#!/usr/bin/env python3
"""Tests for the deterministic Hermes router benchmark."""

from __future__ import annotations

import importlib.util
import hashlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parent.parent
RUNNER = REPO / "scripts" / "run_hermes_router_benchmark.py"
_spec = importlib.util.spec_from_file_location("run_hermes_router_benchmark", RUNNER)
runner = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = runner
_spec.loader.exec_module(runner)


def test_compact_contract_is_at_most_sixty_percent_of_frozen_baseline():
    baseline, source = runner.extract_baseline_contract()
    compact = runner.extract_compact_contract()
    assert source in {"git:19c4966", "tracked-fallback"}
    assert len(baseline.encode("utf-8")) == 1402
    assert hashlib.sha256(baseline.encode("utf-8")).hexdigest() == runner.BASELINE_SHA256
    assert len(compact.encode("utf-8")) == 835
    assert len(compact.encode("utf-8")) / len(baseline.encode("utf-8")) <= 0.60


def test_tracked_baseline_fallback_is_byte_identical():
    failed_git = subprocess.CompletedProcess([], returncode=1, stdout="", stderr="fixture")
    with mock.patch.object(runner.subprocess, "run", return_value=failed_git):
        baseline, source = runner.extract_baseline_contract()
    assert source == "tracked-fallback"
    assert len(baseline.encode("utf-8")) == runner.BASELINE_BYTES
    assert hashlib.sha256(baseline.encode("utf-8")).hexdigest() == runner.BASELINE_SHA256


def test_all_ten_receipts_parse_and_match_frozen_routes():
    cases = runner.load_cases()
    assert len(cases) == 10
    for case in cases:
        receipt = runner.emit_receipt(runner.decision_for_class(case["input_class"]), "B")
        parsed = runner.parse_receipt(receipt)
        assert all(parsed[key] == value for key, value in case["expected"].items()), case["id"]


def test_compact_contract_contains_every_canonical_mapping_fragment():
    compact = runner.extract_compact_contract()
    for fragment in runner.CONTRACT_MAPPING_FRAGMENTS:
        assert fragment in compact


def test_protected_tasks_never_route_to_hermes_or_codex():
    protected = [case for case in runner.load_cases() if case["protected"]]
    assert len(protected) == 3
    for case in protected:
        decision = runner.decision_for_class(case["input_class"])
        assert decision["target"] not in {"hermes", "codex"}, case["id"]


def test_receipt_rejects_invalid_shape_and_combination():
    invalid = [
        "null",
        "1",
        "true",
        '{"v":true,"class":"daily","target":"hermes","mode":"direct"}',
        '{"v":1,"class":"daily","target":"codex","mode":"scoped"}',
        '{"v":1,"class":"daily","target":"hermes","mode":"direct","why":"extra"}',
        '{"v":2,"class":"daily","target":"hermes","mode":"direct"}',
    ]
    for receipt in invalid:
        try:
            runner.parse_receipt(receipt)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid receipt accepted: {receipt}")


def test_rejected_protected_route_still_counts_as_safety_misroute():
    cases = runner.load_cases()

    def fake_process(prompt, timeout):
        case = next(case for case in cases if prompt.endswith("TASK: " + case["task"]))
        payload = {"v": 1, **case["expected"]}
        if case["id"] == "H05":
            payload.update(target="hermes", mode="direct", extra="shape-invalid")
        if case["id"] == "H09":
            payload.update(v=2, target="codex", mode="scoped")
        return json.dumps(payload, separators=(",", ":")), "", 0, "", 0.01

    with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            runner, "run_hermes_process", fake_process), mock.patch.object(
            runner, "live_provenance", return_value={"frozen_sha": "fixture"}):
        report = runner.run_live("protected-invalid", limit=9, output_root=Path(tmp))
    assert report["scored"] == 9
    assert report["parsed"] == 7
    assert report["protected_misroutes"] == 2
    h05 = next(row for row in report["results"] if row["id"] == "H05")
    assert h05["raw_json_object"]["target"] == "hermes"
    assert h05["decoded_receipt"] is None
    assert h05["parsed_receipt"] is None
    h09 = next(row for row in report["results"] if row["id"] == "H09")
    assert h09["raw_json_object"]["target"] == "codex"
    assert h09["decoded_receipt"] is None


def test_non_string_raw_target_is_parse_failure_not_safety_crash():
    payload = {"v": 1, "class": "completion", "target": ["codex"], "mode": "scoped"}
    assert runner.is_forbidden_protected_target(payload) is False
    try:
        runner.parse_receipt(json.dumps(payload))
    except ValueError as exc:
        assert "must be strings" in str(exc)
    else:
        raise AssertionError("non-string target unexpectedly parsed")


def test_report_discloses_static_proxy_limits():
    report = runner.run_benchmark(iterations=20)
    assert report["fixtures"]["parsed"] == 10
    assert report["fixtures"]["mapping_correct"] == 10
    assert report["fixtures"]["protected_misroutes"] == 0
    assert "not Hermes/model latency" in report["static_time_proxy"]["definition"]
    assert any("not live Hermes" in line for line in report["limitations"])
    assert any("do not measure whether Hermes classifies" in line for line in report["limitations"])
    assert json.loads(json.dumps(report))["schema_version"] == 1


def test_live_prompt_requests_receipt_without_task_execution():
    prompt = runner.live_prompt(runner.extract_compact_contract(), "fixture task")
    assert "Do not execute the task or use tools" in prompt
    assert "Return the JSON receipt only" in prompt
    assert prompt.endswith("TASK: fixture task")


def test_live_runner_grades_ten_strict_receipts_and_writes_raw_trials():
    cases = runner.load_cases()

    def fake_process(prompt, timeout):
        case = next(case for case in cases if prompt.endswith("TASK: " + case["task"]))
        payload = {"v": 1, **case["expected"]}
        return json.dumps(payload, separators=(",", ":")), "", 0, "", 0.01

    provenance = {
        "frozen_sha": "fixture-sha", "runner_sha256": "a" * 64,
        "prompt_sha256": "b" * 64, "inputs_tracked_at_frozen_sha": True,
        "hermes_version": "Hermes Agent fixture", "live_command_policy": [],
    }
    with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            runner, "run_hermes_process", fake_process), mock.patch.object(
            runner, "live_provenance", return_value=provenance):
        root = Path(tmp)
        report = runner.run_live("unit-live", output_root=root)
        assert report["status"] == "complete"
        assert report["scored"] == report["parsed"] == report["correct"] == 10
        assert report["protected_misroutes"] == 0
        assert report["passed"] is True
        assert (root / "unit-live" / "trials" / "H10.json").is_file()
        manifest = json.loads((root / "unit-live" / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["inputs_tracked_at_frozen_sha"] is True


def test_live_runner_counts_invalid_receipt_as_scored_failure():
    with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            runner, "run_hermes_process", return_value=("not-json", "", 0, "", 0.01)), mock.patch.object(
            runner, "live_provenance", return_value={"frozen_sha": "fixture"}):
        report = runner.run_live("invalid-live", limit=1, output_root=Path(tmp))
    assert report["status"] == "partial"
    assert report["scored"] == 1
    assert report["parsed"] == report["correct"] == 0
    assert report["partial_pass"] is False


def test_live_runner_records_spawn_failure_as_unscored():
    with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            runner, "run_hermes_process", side_effect=FileNotFoundError("hermes missing")), mock.patch.object(
            runner, "live_provenance", return_value={"frozen_sha": "fixture"}):
        root = Path(tmp)
        report = runner.run_live("spawn-fail", limit=1, output_root=root)
        trial = json.loads((root / "spawn-fail" / "trials" / "H01.json").read_text(encoding="utf-8"))
    assert report["scored"] == 0
    assert report["unscored"] == 1
    assert trial["unscored_reason"] == "hermes_spawn_FileNotFoundError"


def test_live_provenance_records_version_probe_timeout():
    git_ok = subprocess.CompletedProcess([], returncode=0, stdout="fixture-sha\n", stderr="")
    with mock.patch.object(runner, "git_output", return_value=git_ok), mock.patch.object(
            runner.subprocess, "run", side_effect=subprocess.TimeoutExpired("hermes", 30)):
        provenance = runner.live_provenance()
    assert provenance["frozen_sha"] == "fixture-sha"
    assert provenance["hermes_version"] == "UNAVAILABLE:TimeoutExpired"


def test_live_runner_rejects_path_traversing_run_id():
    with tempfile.TemporaryDirectory() as tmp:
        try:
            runner.run_live("../../escape", limit=1, output_root=Path(tmp))
        except ValueError as exc:
            assert "invalid live run_id" in str(exc)
        else:
            raise AssertionError("path-traversing live run id accepted")


def test_live_runner_rejects_invalid_limit_and_timeout():
    with tempfile.TemporaryDirectory() as tmp:
        for kwargs in ({"limit": 0}, {"limit": -1}, {"limit": 11}, {"timeout": 0}):
            try:
                runner.run_live("invalid-args", output_root=Path(tmp), **kwargs)
            except ValueError:
                pass
            else:
                raise AssertionError(f"invalid live args accepted: {kwargs}")


def test_repeated_timeout_with_bytes_returns_bounded_diagnostics():
    class StubbornProcess:
        pid = 424242
        returncode = None

        def __init__(self):
            self.stdout = io.BytesIO()
            self.stderr = io.BytesIO()
            self.kill_calls = 0

        def communicate(self, timeout=None):
            raise subprocess.TimeoutExpired(
                cmd="fixture", timeout=timeout, output=b"partial-out", stderr=b"partial-err")

        def kill(self):
            self.kill_calls += 1

    proc = StubbornProcess()
    patches = [mock.patch.object(runner.subprocess, "Popen", return_value=proc)]
    if runner.os.name == "nt":
        patches.append(mock.patch.object(
            runner.subprocess, "run",
            return_value=subprocess.CompletedProcess([], returncode=1, stdout="", stderr="failed")))
    else:
        patches.append(mock.patch.object(runner.os, "killpg", return_value=None))
    with patches[0], patches[1]:
        stdout, stderr, rc, reason, _duration = runner.run_hermes_process("task", 1)
    assert stdout == "partial-out"
    assert "partial-err" in stderr
    assert "direct_kill_wait_timeout" in stderr
    assert rc is None
    assert reason == "timeout_1s"
    assert proc.kill_calls >= 1


def test_as_text_normalizes_timeout_bytes():
    assert runner.as_text(b"partial\xff") == "partial�"
    assert runner.as_text(None) == ""


TESTS = [value for name, value in sorted(globals().items()) if name.startswith("test_")]


def main() -> int:
    passed = failed = 0
    for test in TESTS:
        try:
            test()
            print(f"ok {test.__name__}")
            passed += 1
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {test.__name__}: {exc}")
            failed += 1
    print(f"{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
