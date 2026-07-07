#!/usr/bin/env python3
"""Tests for scripts/run_adaptive_harness_review.py + check_adaptive_harness.py.

Pins the Phase-2 contract:
  - every mode dry-runs to schema-core-valid JSON; dry-run writes nothing;
  - scheduled_harness_review is report-only (source=scheduled_runner,
    --ingest rejected);
  - --read-ai-review consumes an AI-review latest.json and the rolling loop
    classifies findings new / repeated / resolved-by-commit / carried-open;
  - patch_proposal renders an apply/rollback sheet and applies nothing;
  - the tier-0 validator passes on this repo and catches posture regressions.

Dual-runnable (repo convention):
    python scripts/test_run_adaptive_harness_review.py   (standalone, exit 0/1)
    python -m pytest scripts/test_run_adaptive_harness_review.py
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNNER = REPO_ROOT / "scripts" / "run_adaptive_harness_review.py"
VALIDATOR = REPO_ROOT / "scripts" / "check_adaptive_harness.py"

_spec = importlib.util.spec_from_file_location("run_adaptive_harness_review", RUNNER)
ahr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ahr)


def run_runner(*argv):
    return subprocess.run(
        [sys.executable, str(RUNNER)] + list(argv),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO_ROOT), timeout=300)


def make_ai_review_fixture(tmp, recs):
    """A minimal AI-review latest.json + history the rolling loop can read."""
    out = Path(tmp) / "ai-review"
    (out / "history").mkdir(parents=True)
    report = {
        "review_id": "air-20260706-000000-harness_cleanup_review",
        "review_date": "2026-07-06T00:00:00+00:00",
        "source": "ai_review", "mode": "harness_cleanup_review",
        "files_inspected": [], "components_inspected": {},
        "issues_found": [], "obsolete_scaffolding": [],
        "inefficient_invocations": [], "recommendations": recs,
        "experiments_proposed": [], "changes_made": [],
        "unresolved_questions": [], "metrics": {}, "next_review_trigger": "n/a",
    }
    (out / "latest.json").write_text(json.dumps(report), encoding="utf-8")
    (out / "history" / "review-log.jsonl").write_text(
        json.dumps({"review_id": report["review_id"]}) + "\n", encoding="utf-8")
    return out / "latest.json"


def rec(n, name="component"):
    return {
        "recommendation_id": f"REC-20260706-{n:03d}",
        "component_name": name, "component_type": "rule", "file_path": "X.md",
        "current_purpose": "p", "evidence_it_still_helps": "none found",
        "evidence_it_may_be_obsolete": "e", "recommendation": "Simplify",
        "expected_impact": "i", "risk_if_changed": "low",
        "suggested_test": "t", "confidence": "high", "priority": "P2",
        "source_review_id": "air-20260706-000000-harness_cleanup_review",
    }


# --------------------------------------------------------------------------

def test_help_runs():
    proc = run_runner("--help")
    assert proc.returncode == 0, proc.stderr
    assert "--read-ai-review" in proc.stdout


def test_all_modes_dry_run_valid():
    for mode in sorted(ahr.MODES):
        proc = run_runner("--mode", mode, "--dry-run", "--no-home")
        assert proc.returncode == 0, f"{mode}: {proc.stderr}"
        report = json.loads(proc.stdout)
        assert report["mode"] == mode
        assert report["dry_run"] is True
        expected_source = "scheduled_runner" if mode == "scheduled_harness_review" else "adaptive_harness"
        assert report["source"] == expected_source, mode


def test_dry_run_does_not_mutate_repo():
    before = subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                            text=True, cwd=str(REPO_ROOT), timeout=60).stdout
    proc = run_runner("--mode", "rolling_improvement_review", "--dry-run", "--no-home")
    assert proc.returncode == 0, proc.stderr
    after = subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                           text=True, cwd=str(REPO_ROOT), timeout=60).stdout
    assert before == after


def test_scheduled_rejects_ingest():
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "f.json"
        f.write_text("{}", encoding="utf-8")
        proc = run_runner("--mode", "scheduled_harness_review", "--dry-run",
                          "--no-home", "--ingest", str(f))
        assert proc.returncode == 1
        assert "report-only" in proc.stderr


def test_rolling_loop_reads_ai_review_and_writes_history():
    with tempfile.TemporaryDirectory() as tmp:
        latest = make_ai_review_fixture(tmp, [rec(101, "alpha"), rec(102, "beta")])
        out = Path(tmp) / "harness"
        proc = run_runner("--mode", "rolling_improvement_review", "--no-home",
                          "--read-ai-review", str(latest), "--output", str(out))
        assert proc.returncode == 0, proc.stderr
        report = json.loads((out / "latest.json").read_text(encoding="utf-8"))
        assert report["metrics"]["rolling"]["new_count"] == 2
        assert report["metrics"]["source_reports_read"] == [str(latest)]
        assert len(report["recommendations"]) == 2
        # Second run: both records now exist in the previous harness report -> repeated.
        proc2 = run_runner("--mode", "rolling_improvement_review", "--no-home",
                           "--read-ai-review", str(latest), "--output", str(out))
        assert proc2.returncode == 0, proc2.stderr
        report2 = json.loads((out / "latest.json").read_text(encoding="utf-8"))
        assert report2["metrics"]["rolling"]["repeated_count"] == 2
        assert report2["metrics"]["rolling"]["new_count"] == 0
        assert all(r["status"] == "repeated" for r in report2["recommendations"])
        log = (out / "history" / "review-log.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(log) == 2


def test_rolling_state_survives_other_modes_running_in_between():
    """Phase-2 dogfooding regression: latest.json is overwritten by every
    mode; the rolling loop must key off rolling_state.json instead."""
    with tempfile.TemporaryDirectory() as tmp:
        latest = make_ai_review_fixture(tmp, [rec(110, "delta")])
        out = Path(tmp) / "harness"
        run_runner("--mode", "rolling_improvement_review", "--no-home",
                   "--read-ai-review", str(latest), "--output", str(out))
        # An unrelated mode overwrites latest.json in the same output dir.
        run_runner("--mode", "harness_inventory", "--no-home", "--output", str(out))
        proc = run_runner("--mode", "rolling_improvement_review", "--no-home",
                          "--read-ai-review", str(latest), "--output", str(out))
        assert proc.returncode == 0, proc.stderr
        report = json.loads((out / "latest.json").read_text(encoding="utf-8"))
        assert report["metrics"]["rolling"]["repeated_count"] == 1, \
            "rolling state must not reset when other modes overwrite latest.json"
        assert report["metrics"]["rolling"]["new_count"] == 0


def test_rolling_carries_open_when_finding_disappears_unproven():
    """A finding that stops being reported WITHOUT a citing commit is carried
    open, never silently dropped (DR-011)."""
    with tempfile.TemporaryDirectory() as tmp:
        latest = make_ai_review_fixture(tmp, [rec(103, "gamma")])
        out = Path(tmp) / "harness"
        run_runner("--mode", "rolling_improvement_review", "--no-home",
                   "--read-ai-review", str(latest), "--output", str(out))
        # New AI-review with the finding gone (no commit cites REC-...-103).
        report_obj = json.loads(latest.read_text(encoding="utf-8"))
        report_obj["recommendations"] = []
        latest.write_text(json.dumps(report_obj), encoding="utf-8")
        proc = run_runner("--mode", "rolling_improvement_review", "--no-home",
                          "--read-ai-review", str(latest), "--output", str(out))
        assert proc.returncode == 0, proc.stderr
        report2 = json.loads((out / "latest.json").read_text(encoding="utf-8"))
        rolling = report2["metrics"]["rolling"]
        assert rolling["carried_open_count"] == 1, rolling
        assert rolling["resolved_count"] == 0
        assert any(r.get("recommendation_id") == "REC-20260706-103"
                   for r in report2["recommendations"])


def test_corrupt_rolling_state_refuses_instead_of_resetting():
    """Review finding (2026-07-06 pair): a corrupted rolling_state.json must
    not silently reset the loop's memory."""
    with tempfile.TemporaryDirectory() as tmp:
        latest = make_ai_review_fixture(tmp, [rec(120, "epsilon")])
        out = Path(tmp) / "harness"
        run_runner("--mode", "rolling_improvement_review", "--no-home",
                   "--read-ai-review", str(latest), "--output", str(out))
        state = out / "rolling_state.json"
        assert state.is_file()
        state.write_text("{corrupt", encoding="utf-8")
        proc = run_runner("--mode", "rolling_improvement_review", "--no-home",
                          "--read-ai-review", str(latest), "--output", str(out))
        assert proc.returncode == 0, proc.stderr
        report = json.loads((out / "latest.json").read_text(encoding="utf-8"))
        assert any(i["category"] == "rolling_state" and i["severity"] == "P1"
                   for i in report["issues_found"]), "corrupt state must surface as a P1 issue"
        assert state.read_text(encoding="utf-8") == "{corrupt", \
            "corrupt state file must be preserved for inspection, not overwritten"


def test_missing_ai_review_input_preserves_rolling_state():
    """Review finding (2026-07-06 pair, posture lens): rolling run with the
    AI-review input missing must NOT overwrite rolling_state.json with []."""
    with tempfile.TemporaryDirectory() as tmp:
        latest = make_ai_review_fixture(tmp, [rec(121, "zeta")])
        out = Path(tmp) / "harness"
        run_runner("--mode", "rolling_improvement_review", "--no-home",
                   "--read-ai-review", str(latest), "--output", str(out))
        before = (out / "rolling_state.json").read_text(encoding="utf-8")
        assert "REC-20260706-121" in before
        proc = run_runner("--mode", "rolling_improvement_review", "--no-home",
                          "--read-ai-review", str(Path(tmp) / "nonexistent.json"),
                          "--output", str(out))
        assert proc.returncode == 0, proc.stderr
        after = (out / "rolling_state.json").read_text(encoding="utf-8")
        assert after == before, "missing input must preserve prior rolling state"


def test_ingest_deduped_against_rolling_recommendations():
    """Review finding (2026-07-06 pair): the same record ingested into
    AI-review AND passed to --ingest here must appear once, not twice."""
    with tempfile.TemporaryDirectory() as tmp:
        latest = make_ai_review_fixture(tmp, [rec(122, "eta")])
        findings = Path(tmp) / "f.json"
        findings.write_text(json.dumps({"recommendations": [rec(122, "eta")]}),
                            encoding="utf-8")
        out = Path(tmp) / "harness"
        proc = run_runner("--mode", "rolling_improvement_review", "--no-home",
                          "--read-ai-review", str(latest), "--output", str(out),
                          "--ingest", str(findings))
        assert proc.returncode == 0, proc.stderr
        report = json.loads((out / "latest.json").read_text(encoding="utf-8"))
        ids = [r["recommendation_id"] for r in report["recommendations"]]
        assert ids.count("REC-20260706-122") == 1, ids


def test_resolved_requires_application_verb():
    """Review finding (2026-07-06 pair): bare mentions / rejection notes /
    reverts must not mark a recommendation resolved."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        def g(*args):
            return subprocess.run(["git"] + list(args), cwd=str(repo),
                                  capture_output=True, text=True, encoding="utf-8")
        if g("init").returncode != 0:
            print("ok (skipped: git init unavailable)")
            return
        g("config", "user.email", "t@t"); g("config", "user.name", "t")
        (repo / "a.md").write_text("x", encoding="utf-8")
        g("add", "-A"); g("commit", "-m", "docs: record decision to REJECT REC-20260706-501 as wontfix")
        (repo / "b.md").write_text("y", encoding="utf-8")
        g("add", "-A"); g("commit", "-m", "fix: applies REC-20260706-502 (merge dispatcher)")
        (repo / "c.md").write_text("z", encoding="utf-8")
        g("add", "-A"); g("commit", "-m", "revert: reverts REC-20260706-503")
        assert ahr.resolved_by_commit(repo, "REC-20260706-501") is None, "rejection note must not resolve"
        assert ahr.resolved_by_commit(repo, "REC-20260706-503") is None, "revert must not resolve"
        assert ahr.resolved_by_commit(repo, "REC-20260706-502") is not None, "applies-verb must resolve"


def test_history_stem_no_same_second_collision():
    """Review finding (2026-07-06 pair): two same-second runs of different
    modes must not overwrite each other's dated history files."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "harness"
        for mode in ("harness_inventory", "skill_fit_review", "experiment_design"):
            proc = run_runner("--mode", mode, "--no-home", "--output", str(out))
            assert proc.returncode == 0, proc.stderr
        history_json = list((out / "history").glob("*.json"))
        log_lines = (out / "history" / "review-log.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(history_json) == len(log_lines) == 3, \
            f"every run must keep its own history file: {len(history_json)} files vs {len(log_lines)} log rows"


def test_patch_proposal_renders_high_risk_only():
    with tempfile.TemporaryDirectory() as tmp:
        high = rec(104, "dangerous-hook")
        high.update({"recommendation": "Remove", "component_type": "hook",
                     "priority": "P0", "requires_human_approval": True})
        low = rec(105, "minor-wording")
        latest = make_ai_review_fixture(tmp, [high, low])
        out = Path(tmp) / "harness"
        proc = run_runner("--mode", "patch_proposal", "--no-home",
                          "--read-ai-review", str(latest), "--output", str(out))
        assert proc.returncode == 0, proc.stderr
        proposals = list((out / "proposals").glob("PATCH-PROPOSALS-*.md"))
        assert len(proposals) == 1
        text = proposals[0].read_text(encoding="utf-8")
        assert "REC-20260706-104" in text and "rollback" in text
        assert "REC-20260706-105" not in text, "low-risk items do not become patch proposals"


def test_render_patch_proposals_empty():
    md = ahr.render_patch_proposals([], "ahr-test")
    assert "No high-risk recommendations pending" in md


def test_integration_wiring_collector_all_present():
    result = ahr.collect_integration_wiring({"target": REPO_ROOT})
    assert result["missing"] == [], result
    assert result["root_skill_documents_adapter"] is True


def test_validator_passes_on_repo():
    proc = subprocess.run([sys.executable, str(VALIDATOR)], capture_output=True,
                          text=True, encoding="utf-8", cwd=str(REPO_ROOT), timeout=120)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_validator_catches_posture_regression():
    spec = importlib.util.spec_from_file_location("check_adaptive_harness", VALIDATOR)
    cah = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cah)
    assert "stays private" in cah.FORBIDDEN_POSTURE
    assert any("publication_status" in p for p in cah.REQUIRED)


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_")]


def main():
    passed = failed = 0
    for fn in TESTS:
        try:
            fn()
            print("ok {}".format(fn.__name__))
            passed += 1
        except AssertionError as exc:
            print("FAIL {}: {}".format(fn.__name__, exc))
            failed += 1
        except Exception as exc:  # noqa: BLE001 - a crash is a failure, reported not raised
            print("FAIL {} (error): {!r}".format(fn.__name__, exc))
            failed += 1
    print("{} passed, {} failed".format(passed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
