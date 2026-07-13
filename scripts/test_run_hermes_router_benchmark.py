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
    baseline = runner.live_prompt("baseline", "fixture task", "A")
    assert "Return exactly three lines" in baseline
    assert "JSON receipt" not in baseline


def test_baseline_freeform_receipt_parser():
    parsed = runner.parse_baseline_receipt(
        "classification: debug\nroute: claude\nmode: opus\n")
    assert parsed == {"v": 1, "class": "debug", "target": "claude", "mode": "opus"}


def test_baseline_protected_misroute_cannot_false_pass():
    case = next(case for case in runner.load_cases() if case["id"] == "H05")
    response = "classification: daily\nroute: hermes\nmode: direct\n"
    with mock.patch.object(
            runner, "run_hermes_process", return_value=(response, "", 0, "", 0.01)):
        result, _raw = runner.execute_live_case(case, "baseline", "A", 30)
    assert result["parsed_receipt"]["target"] == "hermes"
    assert result["correct"] is False
    assert result["protected_misroute"] is True


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


def test_paired_live_runner_alternates_and_gates_case_paired_time():
    cases = runner.load_cases()

    def fake_process(prompt, timeout):
        case = next(case for case in cases if prompt.endswith("TASK: " + case["task"]))
        expected = case["expected"]
        if "Return the JSON receipt only" in prompt:
            output = json.dumps({"v": 1, **expected}, separators=(",", ":"))
            duration = 1.05
        else:
            output = (
                f"classification: {expected['class']}\nroute: {expected['target']}\n"
                f"mode: {expected['mode']}\n")
            duration = 1.0
        return output, "", 0, "", duration

    provenance = {
        "frozen_sha": "paired-fixture", "runner_sha256": "a" * 64,
        "prompt_sha256": "b" * 64, "inputs_tracked_at_frozen_sha": True,
        "hermes_version": "Hermes fixture",
        "runtime_fingerprint": {
            "model": "fixture", "provider": "fixture",
            "status_sha256": "d" * 64, "config_sha256": "c" * 64},
        "live_command_policy": [],
    }
    with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            runner, "run_hermes_process", fake_process), mock.patch.object(
            runner, "live_provenance", return_value=provenance):
        root = Path(tmp)
        report = runner.run_paired_live("paired-unit", repetitions=2, output_root=root)
        manifest = json.loads((root / "paired-unit" / "manifest.json").read_text(encoding="utf-8"))
    assert report["variant_summaries"]["A"]["scored"] == 20
    assert report["variant_summaries"]["B"]["scored"] == 20
    assert report["both_fully_scored_and_parseable"] is True
    assert report["pair_count"] == 20
    assert report["median_case_paired_B_over_A_time"] == 1.05
    assert report["provenance_eligible"] is True
    assert report["passed"] is True
    assert manifest["repetitions"] == 2
    assert manifest["runtime_fingerprint"]["model"] == "fixture"
    first_orders = [
        (row["variant"], row["position"]) for row in manifest["schedule"]
        if row["case_id"] == "H01"]
    assert first_orders == [("A", 1), ("B", 2), ("B", 1), ("A", 2)]


def test_paired_live_runner_fails_closed_on_ineligible_provenance():
    cases = runner.load_cases()

    def fake_process(prompt, timeout):
        case = next(case for case in cases if prompt.endswith("TASK: " + case["task"]))
        expected = case["expected"]
        if "Return the JSON receipt only" in prompt:
            output = json.dumps({"v": 1, **expected}, separators=(",", ":"))
        else:
            output = (
                f"classification: {expected['class']}\nroute: {expected['target']}\n"
                f"mode: {expected['mode']}\n")
        return output, "", 0, "", 1.0

    ineligible = {
        "frozen_sha": "dirty", "runner_sha256": "a" * 64,
        "prompt_sha256": "b" * 64, "inputs_tracked_at_frozen_sha": False,
        "hermes_version": "UNAVAILABLE:TimeoutExpired",
        "runtime_fingerprint": {
            "model": "UNAVAILABLE", "provider": "UNAVAILABLE",
            "status_sha256": "UNAVAILABLE", "config_sha256": "UNAVAILABLE"},
        "live_command_policy": [],
    }
    with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            runner, "run_hermes_process", fake_process), mock.patch.object(
            runner, "live_provenance", return_value=ineligible):
        report = runner.run_paired_live(
            "paired-ineligible", repetitions=1, output_root=Path(tmp))
    assert report["both_fully_scored_and_parseable"] is True
    assert report["provenance_eligible"] is False
    assert report["passed"] is False


def test_paired_live_runner_rejects_invalid_args_before_writes():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bad = [
            ("../../escape", 2, 30),
            ("bad-reps-zero", 0, 30),
            ("bad-reps-high", 6, 30),
            ("bad-timeout", 2, 0),
        ]
        for run_id, repetitions, timeout in bad:
            try:
                runner.run_paired_live(run_id, repetitions, timeout, root)
            except ValueError:
                pass
            else:
                raise AssertionError(f"invalid paired args accepted: {run_id}")
        assert list(root.iterdir()) == []


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


def fair_fixture_fingerprint(provider="fixture-provider"):
    return {
        "executable_path": "C:/fixture/hermes.exe",
        "executable_sha256": "a" * 64,
        "version_returncode": 0,
        "version": "Hermes fixture 1.0",
        "version_error": "",
        "status_returncode": 0,
        "status_sha256": "b" * 64,
        "status_error": "",
        "model": "fixture-model",
        "provider": provider,
        "config_path_returncode": 0,
        "config_path": "C:/fixture/config.yaml",
        "config_sha256": "c" * 64,
        "config_error": "",
        "raw_config_or_secrets_stored": False,
    }


def fair_fixture_provenance():
    return {
        "frozen_sha": "d" * 40,
        "input_sha256": {},
        "inputs_tracked_at_frozen_sha": True,
        "frozen_input_hashes_match": True,
        "live_command_policy": [],
    }


def test_fair_preregistration_schedule_and_prompt_are_frozen():
    preregistration = runner.load_fair_preregistration()
    assert runner.sha256_file(runner.FAIR_PREREGISTRATION) == runner.FAIR_PREREGISTRATION_SHA256
    cases = runner.load_cases()
    schedule = runner.build_fair_schedule(cases, 5)
    assert len(schedule) == 100
    assert sum(row["variant"] == "A" for row in schedule) == 50
    assert sum(row["variant"] == "B" for row in schedule) == 50
    assert sum(row["variant"] == "A" and row["position"] == 1 for row in schedule) == 25
    assert sum(row["variant"] == "B" and row["position"] == 1 for row in schedule) == 25
    for variant in ("A", "B"):
        contract = runner.extract_baseline_contract()[0] if variant == "A" else runner.extract_compact_contract()
        assert runner.fair_live_prompt(contract, "fixture", variant, preregistration) == runner.live_prompt(
            contract, "fixture", variant)


def test_fair_semantic_extractor_matches_all_frozen_adversarial_vectors():
    preregistration = runner.load_fair_preregistration()
    semantic_config = runner.fair_semantic_config(preregistration)
    assert set(semantic_config) == {
        "reference_semantic_extractor", "target_aliases", "mode_aliases"}
    try:
        semantic_config["target_aliases"]["leak"] = ("gold",)
    except TypeError:
        pass
    else:
        raise AssertionError("semantic extractor config is mutable")
    for vector in preregistration["grading"]["adversarial_vectors"]:
        semantic = runner.extract_fair_semantics(vector["stdout"], semantic_config)
        assert semantic["target_candidates"] == vector["target_candidates"], vector["stdout"]
        assert semantic["target"] == vector["target"], vector["stdout"]
        assert semantic["mode_candidates"] == vector["mode_candidates"], vector["stdout"]
        assert semantic["mode"] == vector["mode"], vector["stdout"]
        assert semantic["target_reason"] == (
            "selected" if len(vector["target_candidates"]) == 1 else
            "unresolved_zero_candidates" if not vector["target_candidates"] else
            "ambiguous_multiple_candidates")
        assert semantic["mode_reason"] == (
            "selected" if len(vector["mode_candidates"]) == 1 else
            "unresolved_zero_candidates" if not vector["mode_candidates"] else
            "ambiguous_multiple_candidates")
        protected_misroute = bool(
            {"hermes", "codex"}.intersection(semantic["target_candidates"]))
        assert protected_misroute == vector["protected_misroute"], vector["stdout"]
    assert runner._fair_segment("opus-‐‑‒–—―/_+distilled") == "opus distilled"


def test_fair_bootstrap_uses_frozen_lcg_median_and_nearest_rank():
    result = runner.fair_bootstrap(
        [(index + 1) / 50 for index in range(50)], runner.load_fair_preregistration())
    assert result == {
        "pair_median": 0.51,
        "upper_95": 0.62,
        "upper_index_zero_based": 9499,
        "resamples": 10000,
        "final_lcg_state": 2047826744685214089,
    }


def test_fair_runtime_fingerprint_hashes_resolved_executable_and_probes():
    with tempfile.TemporaryDirectory() as tmp:
        executable = Path(tmp) / "hermes.exe"
        config = Path(tmp) / "config.yaml"
        executable.write_bytes(b"fixture executable")
        config.write_bytes(b"model: fixture\n")

        def fake_run(cmd, **_kwargs):
            if cmd[-1] == "--version":
                return subprocess.CompletedProcess(cmd, 0, "Hermes fixture\n", "")
            if cmd[-1] == "status":
                return subprocess.CompletedProcess(
                    cmd, 0, "Model: fixture-model\nProvider: fixture-provider\n", "")
            if cmd[-2:] == ["config", "path"]:
                return subprocess.CompletedProcess(cmd, 0, str(config) + "\n", "")
            raise AssertionError(cmd)

        with mock.patch.object(runner.shutil, "which", return_value=str(executable)), mock.patch.object(
                runner.subprocess, "run", side_effect=fake_run):
            fingerprint = runner.fair_runtime_fingerprint()
        executable_resolved = str(executable.resolve())
    assert fingerprint["executable_path"] == executable_resolved
    assert fingerprint["executable_sha256"] == hashlib.sha256(b"fixture executable").hexdigest()
    assert fingerprint["config_sha256"] == hashlib.sha256(b"model: fixture\n").hexdigest()
    assert fingerprint["version_returncode"] == fingerprint["status_returncode"] == 0
    assert fingerprint["config_path_returncode"] == 0
    assert runner.fair_runtime_fingerprint_eligible(fingerprint) is True


def _fair_fake_process_factory(cases, unresolved_protected_case=None, manifest_path=None):
    calls = []

    def fake_process(prompt, timeout, executable):
        if manifest_path is not None:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            assert manifest["status"] == "pre_registered_not_complete"
            assert len(manifest["schedule"]) == 100
        case = next(case for case in cases if prompt.endswith("TASK: " + case["task"]))
        variant = "B" if "Return the JSON receipt only" in prompt else "A"
        expected = case["expected"]
        if variant == "B" and case["id"] == unresolved_protected_case:
            output = "route: execute locally\nmode: direct"
        elif variant == "B":
            output = json.dumps({"v": 1, **expected}, separators=(",", ":"))
        else:
            output = (
                f"classification: {expected['class']}\nroute: {expected['target']}\n"
                f"mode: {expected['mode']}\n")
        calls.append((case["id"], variant, timeout, executable))
        return output, "", 0, "", 0.8 if variant == "B" else 1.0

    return fake_process, calls


def test_fair_live_runner_executes_frozen_design_and_supports_speed_claim():
    cases = runner.load_cases()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        manifest_path = root / "fair-unit" / "manifest.json"
        fake_process, calls = _fair_fake_process_factory(cases, manifest_path=manifest_path)
        fingerprint = fair_fixture_fingerprint()
        with mock.patch.object(runner, "run_hermes_process", fake_process), mock.patch.object(
                runner, "fair_runtime_fingerprint", return_value=fingerprint), mock.patch.object(
                runner, "fair_input_provenance", return_value=fair_fixture_provenance()):
            report = runner.run_fair_paired_live("fair-unit", root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        first_orders = [
            (row["variant"], row["position"]) for row in manifest["schedule"]
            if row["case_id"] == "H01"]
    assert len(calls) == 100
    assert first_orders == [
        ("A", 1), ("B", 2), ("B", 1), ("A", 2), ("A", 1),
        ("B", 2), ("B", 1), ("A", 2), ("A", 1), ("B", 2)]
    for variant in ("A", "B"):
        summary = report["variant_summaries"][variant]
        assert summary["scored"] == summary["native_parsed"] == 50
        assert summary["semantic_target_correct"] == 50
        assert summary["semantic_exact_route_correct"] == 50
        assert summary["protected_target_correct"] == 15
        assert summary["protected_exact_route_correct"] == 15
    assert report["pair_count"] == 50
    assert report["latency_bootstrap"]["pair_median"] == 0.8
    assert report["latency_bootstrap"]["upper_95"] == 0.8
    assert report["speed_claim_supported"] is True
    assert report["latency_no_regression_supported"] is True
    assert report["token_usage"]["status"] == "UNSCORED"
    assert report["adopt_B"] is True


def test_fair_live_protected_unresolved_blocks_adoption_at_45_of_50():
    cases = runner.load_cases()
    with tempfile.TemporaryDirectory() as tmp:
        fake_process, _calls = _fair_fake_process_factory(cases, unresolved_protected_case="H05")
        fingerprint = fair_fixture_fingerprint()
        with mock.patch.object(runner, "run_hermes_process", fake_process), mock.patch.object(
                runner, "fair_runtime_fingerprint", return_value=fingerprint), mock.patch.object(
                runner, "fair_input_provenance", return_value=fair_fixture_provenance()):
            report = runner.run_fair_paired_live("fair-protected-gap", Path(tmp))
    b = report["variant_summaries"]["B"]
    assert b["native_parsed"] == 45
    assert b["semantic_target_correct"] == b["semantic_exact_route_correct"] == 45
    assert b["protected_target_correct"] == b["protected_exact_route_correct"] == 10
    assert b["protected_unresolved"] == 5
    assert b["protected_misroutes"] == 0
    assert report["gates"]["B_native_parse_at_least_45_of_50"] is True
    assert report["gates"]["B_protected_target_15_of_15"] is False
    assert report["gates"]["B_protected_unresolved_zero"] is False
    assert report["adopt_B"] is False


def test_fair_runtime_drift_and_path_traversal_fail_closed():
    start = fair_fixture_fingerprint()
    end = fair_fixture_fingerprint(provider="changed-provider")
    assert runner.fair_provenance_eligible(fair_fixture_provenance(), start, end) is False
    with tempfile.TemporaryDirectory() as tmp:
        try:
            runner.run_fair_paired_live("../../escape", Path(tmp))
        except ValueError as exc:
            assert "invalid fair live run_id" in str(exc)
        else:
            raise AssertionError("path-traversing fair run id accepted")


def test_fair_invalid_start_provenance_fails_before_one_shot_and_writes_ineligible():
    invalid = fair_fixture_provenance()
    invalid["inputs_tracked_at_frozen_sha"] = False
    fingerprint = fair_fixture_fingerprint()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        with mock.patch.object(
                runner, "run_hermes_process", side_effect=AssertionError("one-shot must not run")), \
                mock.patch.object(runner, "fair_runtime_fingerprint", return_value=fingerprint), \
                mock.patch.object(runner, "fair_input_provenance", return_value=invalid):
            report = runner.run_fair_paired_live("fair-invalid-start", root)
        manifest = json.loads(
            (root / "fair-invalid-start" / "manifest.json").read_text(encoding="utf-8"))
        scorecard = json.loads(
            (root / "fair-invalid-start" / "scorecard.json").read_text(encoding="utf-8"))
    assert report["status"] == scorecard["status"] == manifest["status"] == "ineligible"
    assert report["executed"] == manifest["completed_calls"] == 0
    assert report["terminal_error"] == "start_provenance_ineligible"
    assert report["supported_claims"] == []
    assert report["adopt_B"] is False


def test_fair_mid_run_exception_writes_atomic_partial_scorecard_then_reraises():
    cases = runner.load_cases()
    normal_process, calls = _fair_fake_process_factory(cases)

    def fail_second(prompt, timeout, executable):
        if len(calls) == 1:
            raise RuntimeError("fixture interruption")
        return normal_process(prompt, timeout, executable)

    fingerprint = fair_fixture_fingerprint()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        with mock.patch.object(runner, "run_hermes_process", fail_second), mock.patch.object(
                runner, "fair_runtime_fingerprint", return_value=fingerprint), mock.patch.object(
                runner, "fair_input_provenance", return_value=fair_fixture_provenance()):
            try:
                runner.run_fair_paired_live("fair-partial", root)
            except RuntimeError as exc:
                assert str(exc) == "fixture interruption"
            else:
                raise AssertionError("mid-run exception was swallowed")
        run_dir = root / "fair-partial"
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        scorecard = json.loads((run_dir / "scorecard.json").read_text(encoding="utf-8"))
        trials = list((run_dir / "trials").glob("*.json"))
        temporary_files = list(run_dir.rglob("*.tmp"))
    assert len(calls) == 1
    assert len(trials) == 1
    assert temporary_files == []
    assert manifest["status"] == scorecard["status"] == "partial"
    assert manifest["completed_calls"] == scorecard["executed"] == 1
    assert scorecard["terminal_error"] == "RuntimeError:fixture interruption"
    assert scorecard["supported_claims"] == []
    assert scorecard["adopt_B"] is False


def test_fair_atomic_writer_ignores_precreated_predictable_hardlink():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / "outside-target.txt"
        target.write_text("do not truncate", encoding="utf-8")
        destination = root / "manifest.json"
        predictable = destination.with_name(f".{destination.name}.{runner.os.getpid()}.tmp")
        runner.os.link(target, predictable)
        runner.write_fair_json_atomic(destination, {"safe": True})
        assert target.read_text(encoding="utf-8") == "do not truncate"
        assert predictable.read_text(encoding="utf-8") == "do not truncate"
        assert json.loads(destination.read_text(encoding="utf-8")) == {"safe": True}


def test_fair_terminal_error_invalidates_one_hundred_otherwise_happy_rows():
    cases = runner.load_cases()
    fake_process, calls = _fair_fake_process_factory(cases)
    fingerprint = fair_fixture_fingerprint()
    provenance = fair_fixture_provenance()
    preregistration = runner.load_fair_preregistration()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        run_dir = root / "fair-terminal-after-100"
        with mock.patch.object(runner, "run_hermes_process", fake_process), mock.patch.object(
                runner, "fair_runtime_fingerprint", return_value=fingerprint), mock.patch.object(
                runner, "fair_input_provenance", return_value=provenance):
            complete = runner.run_fair_paired_live("fair-terminal-after-100", root)
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        invalidated = runner._finalize_fair_run(
            run_dir, preregistration, cases, provenance, manifest,
            fingerprint, fingerprint, complete["results"],
            terminal_error="RuntimeError:after_final_result")
    assert len(calls) == invalidated["executed"] == 100
    assert invalidated["status"] == "partial"
    assert invalidated["gates"]["clean_completion_without_terminal_error"] is False
    assert invalidated["supported_claims"] == []
    assert invalidated["speed_claim_supported"] is False
    assert invalidated["latency_no_regression_supported"] is False
    assert invalidated["adopt_B"] is False


def test_fair_end_runtime_drift_is_ineligible_and_suppresses_all_claims():
    cases = runner.load_cases()
    fake_process, calls = _fair_fake_process_factory(cases)
    start = fair_fixture_fingerprint()
    end = fair_fixture_fingerprint(provider="changed-provider")
    with tempfile.TemporaryDirectory() as tmp:
        with mock.patch.object(runner, "run_hermes_process", fake_process), mock.patch.object(
                runner, "fair_runtime_fingerprint", side_effect=[start, end]), mock.patch.object(
                runner, "fair_input_provenance", return_value=fair_fixture_provenance()):
            report = runner.run_fair_paired_live("fair-end-drift", Path(tmp))
    assert len(calls) == 100
    assert report["status"] == "ineligible"
    assert report["provenance_eligible"] is False
    assert report["runtime_fingerprints_identical"] is False
    assert report["supported_claims"] == []
    assert report["speed_claim_supported"] is False
    assert report["latency_no_regression_supported"] is False
    assert "paired latency no-regression" in report["unsupported_claims"]
    assert "adopt compact B on the frozen fair-baseline task set" in report["unsupported_claims"]


def test_fair_unscored_call_suppresses_performance_and_adoption_claims():
    cases = runner.load_cases()
    normal_process, calls = _fair_fake_process_factory(cases)

    def one_unscored(prompt, timeout, executable):
        if not calls:
            calls.append(("unscored", "A", timeout, executable))
            return "", "fixture failure", 7, "", 0.25
        return normal_process(prompt, timeout, executable)

    fingerprint = fair_fixture_fingerprint()
    with tempfile.TemporaryDirectory() as tmp:
        with mock.patch.object(runner, "run_hermes_process", one_unscored), mock.patch.object(
                runner, "fair_runtime_fingerprint", return_value=fingerprint), mock.patch.object(
                runner, "fair_input_provenance", return_value=fair_fixture_provenance()):
            report = runner.run_fair_paired_live("fair-unscored", Path(tmp))
    assert len(calls) == 100
    assert report["status"] == "complete"
    assert report["pair_count"] == 49
    assert report["supported_claims"] == []
    assert report["speed_claim_supported"] is False
    assert report["latency_no_regression_supported"] is False
    assert report["adopt_B"] is False


def test_fair_cli_rejects_frozen_overrides_and_legacy_pair_default_stays_two():
    invalid_argvs = [
        ["--live-fair-run-id", "fair-cli", "--live-timeout", "179"],
        ["--live-fair-run-id", "fair-cli", "--live-limit", "1"],
        ["--live-fair-run-id", "fair-cli", "--live-variant", "A"],
        ["--live-fair-run-id", "fair-cli", "--live-repetitions", "1"],
    ]
    with mock.patch.object(runner, "run_fair_paired_live") as fair_run:
        for argv in invalid_argvs:
            with mock.patch.object(sys, "stderr", new=io.StringIO()):
                try:
                    runner.main(argv)
                except SystemExit as exc:
                    assert exc.code == 2
                else:
                    raise AssertionError(f"fair CLI override accepted: {argv}")
        fair_run.assert_not_called()
    legacy_report = {"passed": True}
    with mock.patch.object(runner, "run_paired_live", return_value=legacy_report) as legacy_run, \
            mock.patch.object(sys, "stdout", new=io.StringIO()):
        assert runner.main(["--live-paired-run-id", "legacy-cli", "--json"]) == 0
    assert legacy_run.call_args.args[1] == 2


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
