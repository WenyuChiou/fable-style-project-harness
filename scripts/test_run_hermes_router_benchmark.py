#!/usr/bin/env python3
"""Tests for the deterministic Hermes router benchmark."""

from __future__ import annotations

import importlib.util
import hashlib
import json
import subprocess
import sys
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
    assert len(compact.encode("utf-8")) == 836
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


def test_report_discloses_static_proxy_limits():
    report = runner.run_benchmark(iterations=20)
    assert report["fixtures"]["parsed"] == 10
    assert report["fixtures"]["mapping_correct"] == 10
    assert report["fixtures"]["protected_misroutes"] == 0
    assert "not Hermes/model latency" in report["static_time_proxy"]["definition"]
    assert any("not live Hermes" in line for line in report["limitations"])
    assert any("do not measure whether Hermes classifies" in line for line in report["limitations"])
    assert json.loads(json.dumps(report))["schema_version"] == 1


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
