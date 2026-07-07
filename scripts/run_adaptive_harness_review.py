#!/usr/bin/env python3
"""Adaptive-harness runner - the rolling-improvement half of the review system.

Division of labor (docs/ai_review_adaptive_harness_integration.md is the
contract): AI-review (scripts/run_ai_review.py) reviews the CURRENT state and
produces structured findings; THIS runner manages how those findings evolve
over time - reading AI-review's latest report + history, linking repeated
findings across runs, detecting resolved ones from commit citations, and
rendering patch proposals for the human. Same shared schemas
(schemas/review_report.schema.yaml + recommendation.schema.yaml), same
writer, same safety posture. This is ONE system with two runners, not two
systems: every collector, validator, and writer here is IMPORTED from
run_ai_review.py (DR-020 single-source), never forked.

Safety invariants (identical to the AI-review runner):
  - never edits harness files; only writes under --output;
  - --dry-run writes nothing;
  - scheduled_harness_review is report-only BY CODE (source=scheduled_runner,
    --ingest rejected, changes_made must be empty);
  - high-risk recommendations only ever become PATCH PROPOSALS (rendered
    markdown for a human), never applied changes.

Run:
    python scripts/run_adaptive_harness_review.py --mode rolling_improvement_review
    python scripts/run_adaptive_harness_review.py --mode harness_inventory --dry-run
    python scripts/run_adaptive_harness_review.py --mode patch_proposal --read-ai-review reports/ai-review/latest.json

Exit codes: same contract as run_ai_review.py (0 report, 1 validation, 2 usage/target).
"""

import argparse
import importlib.util
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("run_ai_review", _HERE / "run_ai_review.py")
rar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rar)

REPO_ROOT = _HERE.parent

# Mode -> deterministic collectors (names resolve in rar.COLLECTORS plus the
# local ROLLING_COLLECTORS below).
MODES = {
    "harness_inventory": ["inventory", "index_integrity", "artifact_check"],
    "harness_cleanup_review": ["inventory", "index_integrity", "artifact_check",
                               "deprecated_markers", "home_telemetry"],
    "code_invocation_review": ["inventory", "home_telemetry"],
    "ai_review_integration": ["integration_wiring", "ai_review_input"],
    "skill_fit_review": ["inventory", "integration_wiring"],
    "diff_only_review": ["diff", "inventory"],
    "scheduled_harness_review": ["inventory", "index_integrity", "artifact_check",
                                 "deprecated_markers", "ai_review_input"],
    "experiment_design": ["experiments"],
    "patch_proposal": ["ai_review_input"],
    "rolling_improvement_review": ["inventory", "index_integrity", "diff",
                                   "ai_review_input", "rolling_state"],
}

MODE_PROMPTS = "prompts/ai-review-modes.md"
INTEGRATION_DOC = "docs/ai_review_adaptive_harness_integration.md"

REQUIRED_WIRING = [
    ".claude/skills/adaptive-harness/SKILL.md",
    "docs/ai_review_adaptive_harness_integration.md",
    "schemas/review_report.schema.yaml",
    "schemas/recommendation.schema.yaml",
    "scripts/run_ai_review.py",
    "prompts/ai-review-modes.md",
    "docs/codex-delegation-policy.md",
    "benchmarks/ai_review_cases.yaml",
    "benchmarks/harness_cases.yaml",
]


def collect_integration_wiring(ctx):
    """Presence of every artifact the AI-review <-> adaptive-harness contract
    depends on; a missing one is a P1 wiring break."""
    target = ctx["target"]
    missing = [p for p in REQUIRED_WIRING if not (target / p).is_file()]
    root_skill = target / "SKILL.md"
    adapter_documented = (root_skill.is_file()
                          and "adaptive-harness" in root_skill.read_text(encoding="utf-8", errors="replace"))
    return {"status": "ok", "missing": missing, "present": len(REQUIRED_WIRING) - len(missing),
            "root_skill_documents_adapter": adapter_documented}


def collect_ai_review_input(ctx):
    """Read AI-review's latest structured report + run history (read-only)."""
    path = ctx["read_ai_review"]
    if path is None:
        path = ctx["target"] / "reports" / "ai-review" / "latest.json"
    path = Path(path)
    if not path.is_file():
        return {"status": "unavailable",
                "reason": f"no AI-review report at {path} - run scripts/run_ai_review.py first"}
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "unavailable", "reason": f"unreadable report: {exc}"}
    history_rows = []
    skipped_rows = 0
    history = path.parent / "history" / "review-log.jsonl"
    if history.is_file():
        for line in history.read_text(encoding="utf-8").splitlines():
            try:
                history_rows.append(json.loads(line))
            except json.JSONDecodeError:
                skipped_rows += 1  # never drop the run over one bad row; reported below
    return {"status": "ok", "path": str(path),
            "history_rows_skipped": skipped_rows,
            "review_id": report.get("review_id"),
            "mode": report.get("mode"),
            "recommendations": report.get("recommendations", []),
            "inefficient_invocations": report.get("inefficient_invocations", []),
            "issues_found": report.get("issues_found", []),
            "experiments_proposed": report.get("experiments_proposed", []),
            "unresolved_questions": report.get("unresolved_questions", []),
            "history_runs": len(history_rows)}


def _rec_key(rec):
    return rec.get("recommendation_id") or (
        rec.get("component_name", ""), rec.get("file_path", ""), rec.get("recommendation", ""))


def resolved_by_commit(target, rec_id, since_days=180):
    """A recommendation counts as resolved ONLY on application evidence: a
    commit whose message says it applies/resolves the REC id. A bare mention
    (a rejection note, a proposal listing, a revert - reverts say
    'reverts REC-...') must NOT close the loop; the verb is the contract.
    Computed, never guessed (DR-004)."""
    rc, out, _ = rar.git(["log", f"--since={since_days} days ago",
                          "--extended-regexp",
                          "--grep", f"(applies|resolves) {rec_id}",
                          "--format=%h %s"], cwd=target)
    if rc != 0 or not out.strip():
        return None
    return out.strip().splitlines()[0]


def collect_rolling_state(ctx):
    """Link the current AI-review findings against the previous adaptive-harness
    report: new / repeated / resolved-by-commit. The rolling loop's memory."""
    target = ctx["target"]
    ai = collect_ai_review_input(ctx)
    if ai["status"] != "ok":
        return {"status": "unavailable", "reason": ai.get("reason", "no AI-review input")}
    current = {str(_rec_key(r)): r for r in ai["recommendations"]}
    # Rolling state lives in its own file, written ONLY by
    # rolling_improvement_review runs - latest.json is overwritten by every
    # mode, so reading it here would reset the loop whenever another mode ran
    # in between (found in Phase-2 dogfooding).
    prev_path = (Path(ctx["output"]) if ctx["output"] else target / "reports" / "harness") / "rolling_state.json"
    previous = {}
    if prev_path.is_file():
        try:
            prev_state = json.loads(prev_path.read_text(encoding="utf-8"))
            previous = {str(_rec_key(r)): r for r in prev_state.get("recommendations", [])}
        except (OSError, json.JSONDecodeError) as exc:
            # An EXISTING but unreadable state file must not silently reset
            # the loop's memory (2026-07-06 review pair, correctness finding 1):
            # refuse, so the state write guard keeps the corrupt file for a
            # human to inspect instead of overwriting it.
            return {"status": "unavailable",
                    "reason": f"rolling_state.json exists but is unreadable ({exc}) - "
                              f"fix or delete it explicitly; refusing to reset loop memory"}
    new, repeated, resolved, still_open = [], [], [], []
    for key, rec in current.items():
        if key in previous:
            rec = dict(rec)
            rec["status"] = "repeated"
            repeated.append(rec)
        else:
            new.append(rec)
    for key, rec in previous.items():
        if key in current:
            continue
        rec_id = rec.get("recommendation_id", "")
        commit = resolved_by_commit(target, rec_id) if rec_id else None
        if commit:
            resolved.append({"recommendation_id": rec_id,
                             "component_name": rec.get("component_name"),
                             "resolving_commit": commit})
        else:
            rec = dict(rec)
            rec["status"] = "open"
            still_open.append(rec)  # absent from the new review but unproven-resolved: carried, not dropped
    return {"status": "ok", "new_count": len(new), "repeated_count": len(repeated),
            "resolved_count": len(resolved), "carried_open_count": len(still_open),
            "new": new, "repeated": repeated, "resolved": resolved,
            "carried_open": still_open, "source_review_id": ai.get("review_id")}


LOCAL_COLLECTORS = {
    "integration_wiring": collect_integration_wiring,
    "ai_review_input": collect_ai_review_input,
    "rolling_state": collect_rolling_state,
}


def resolve_collector(name):
    if name in LOCAL_COLLECTORS:
        return LOCAL_COLLECTORS[name]
    base = rar.COLLECTORS[name]
    return lambda ctx: base({"target": ctx["target"], "home": ctx["home"],
                             "since_ref": ctx["since_ref"], "scoped_files": ctx["scoped_files"]})


def derive_issues(collected):
    issues = []

    def add(sev, category, description, file_path=""):
        issues.append({"id": f"DET-{len(issues) + 1:03d}", "severity": sev,
                       "category": category, "file_path": file_path,
                       "description": description, "source": "deterministic"})

    wiring = collected.get("integration_wiring", {})
    for p in wiring.get("missing", []):
        add("P1", "integration_wiring", f"Required AI-review/adaptive-harness wiring artifact missing: {p}", p)
    if wiring.get("root_skill_documents_adapter") is False:
        add("P2", "integration_wiring",
            "Root SKILL.md does not document its relationship to .claude/skills/adaptive-harness/", "SKILL.md")
    ai = collected.get("ai_review_input", {})
    if ai.get("status") == "unavailable":
        add("P2", "ai_review_input", f"AI-review input unavailable: {ai.get('reason', '')}")
    if ai.get("history_rows_skipped"):
        add("P3", "ai_review_input",
            f"{ai['history_rows_skipped']} unparseable row(s) skipped in AI-review history JSONL.")
    rolling = collected.get("rolling_state", {})
    if rolling.get("status") == "unavailable":
        add("P1", "rolling_state",
            f"Rolling loop did NOT run: {rolling.get('reason', '')} - state preserved, not reset.")
    for name in ("index_integrity", "artifact_check", "deprecated_markers", "codex_policy"):
        if name in collected:
            issues.extend(_reuse_ai_review_issue_rules(collected, name, len(issues)))
    return issues


def _reuse_ai_review_issue_rules(collected, name, offset):
    """Route the shared collectors through run_ai_review's own issue rules so
    both runners flag identical states identically."""
    sub = {name: collected[name]}
    derived = rar.derive_issues(sub)
    for i, issue in enumerate(derived):
        issue["id"] = f"DET-{offset + i + 1:03d}"
    return derived


def render_patch_proposals(recommendations, review_id):
    """Deterministic patch-proposal document: high-risk recommendations become
    a human-consumable apply/rollback sheet. Rendering is the ONLY action -
    nothing is applied."""
    lines = [f"# Patch proposals - {review_id}", "",
             "Every entry is a PROPOSAL. A human applies or rejects it; commits",
             "that apply one MUST cite its recommendation_id so the rolling loop",
             "can mark it resolved.", ""]
    for rec in recommendations:
        lines += [f"## {rec.get('recommendation_id', '?')} - {rec.get('recommendation')} {rec.get('component_name')}",
                  "",
                  f"- **file**: {rec.get('file_path', '')}",
                  f"- **priority / confidence**: {rec.get('priority')} / {rec.get('confidence')}",
                  f"- **evidence (obsolete)**: {rec.get('evidence_it_may_be_obsolete', '')}",
                  f"- **evidence (still helps)**: {rec.get('evidence_it_still_helps', '')}",
                  f"- **risk if changed**: {rec.get('risk_if_changed', '')}",
                  f"- **validation test**: {rec.get('suggested_test', '')}",
                  f"- **requires human approval**: {rec.get('requires_human_approval', False)}",
                  f"- **apply convention**: the applying commit message MUST say "
                  f"'applies {rec.get('recommendation_id', '?')}' (or 'resolves ...') - "
                  f"that exact verb closes the rolling loop; bare mentions do not.",
                  f"- **rollback**: single-commit revert whose message says "
                  f"'reverts {rec.get('recommendation_id', '?')}' (a revert must NOT say applies/resolves).",
                  ""]
    if not recommendations:
        lines += ["No high-risk recommendations pending.", ""]
    return "\n".join(lines)


def high_risk(recs):
    return [r for r in recs
            if r.get("requires_human_approval") is True
            or (r.get("recommendation") in ("Remove", "Replace") and r.get("priority") in ("P0", "P1"))]


def next_trigger_for(mode):
    return {
        "harness_inventory": "monthly, or after adding any new harness component class",
        "harness_cleanup_review": "monthly deep review",
        "code_invocation_review": "monthly, or after rewiring any hook",
        "ai_review_integration": "after any change to either runner or the shared schemas",
        "skill_fit_review": "after adding/renaming skills or changing skill descriptions",
        "diff_only_review": "after each harness-touching commit",
        "scheduled_harness_review": "next scheduled run (report-only); weekly light cadence",
        "experiment_design": "when a recommendation is classified Experiment without a case",
        "patch_proposal": "when rolling review surfaces new high-risk recommendations",
        "rolling_improvement_review": "weekly light; after every AI-review ingest run",
    }[mode]


def assemble_report(mode, args, collected, ingest, started):
    now = datetime.now(timezone.utc)
    source = "scheduled_runner" if mode == "scheduled_harness_review" else "adaptive_harness"
    inventory = collected.get("inventory", {})
    counts = inventory.get("counts", {})
    rolling = collected.get("rolling_state", {})
    recommendations = list(ingest.get("recommendations", []))
    if rolling.get("status") == "ok":
        # The rolling loop's merged view: new + repeated + carried-open records,
        # plus ingest records deduped by key (same semantics as
        # merge_experiments - the same finding must never appear twice).
        rolled = rolling["new"] + rolling["repeated"] + rolling["carried_open"]
        seen = {str(_rec_key(r)) for r in rolled}
        recommendations = rolled + [r for r in recommendations
                                    if str(_rec_key(r)) not in seen]
    ai = collected.get("ai_review_input", {})
    unresolved = list(ingest.get("unresolved_questions", []))
    unresolved += [q for q in ai.get("unresolved_questions", []) if q not in unresolved]
    semantic_keys = ("recommendations", "obsolete_scaffolding",
                     "inefficient_invocations", "codex_delegation_findings")
    empty_semantic = [k for k in semantic_keys if not ingest.get(k)]
    if empty_semantic and mode not in ("patch_proposal",):
        unresolved.append(
            f"Semantic sections not executed/ingested this run for mode '{mode}': "
            f"{', '.join(empty_semantic)}. See {MODE_PROMPTS} - UNSCORED, not passed.")
    files = inventory.get("files", [])
    if "diff" in collected and collected["diff"].get("status") == "ok":
        files = sorted({c["path"] for c in collected["diff"]["changed"]})
    report = {
        "schema": rar.SCHEMA_REF,
        "review_id": f"ahr-{now.strftime('%Y%m%d-%H%M%S')}-{mode}",
        "review_date": now.isoformat(timespec="seconds"),
        "source": source,
        "mode": mode,
        "target": str(args.target),
        "files_inspected": files,
        "components_inspected": counts,
        "issues_found": derive_issues(collected) + list(ingest.get("issues_found", [])),
        "obsolete_scaffolding": list(ingest.get("obsolete_scaffolding", [])),
        "inefficient_invocations": (list(ingest.get("inefficient_invocations", []))
                                    or ai.get("inefficient_invocations", [])),
        "codex_delegation_findings": list(ingest.get("codex_delegation_findings", [])),
        "recommendations": recommendations,
        "experiments_proposed": rar.merge_experiments(
            collected.get("experiments", {}).get("cases", []),
            ingest.get("experiments_proposed", []) or ai.get("experiments_proposed", [])),
        "changes_made": list(ingest.get("changes_made", [])),
        "unresolved_questions": unresolved,
        "metrics": {
            "runtime_sec": round(time.time() - started, 2),
            "collectors": {n: d.get("status", "unknown") for n, d in collected.items()},
            "governance_line_counts": inventory.get("governance_line_counts", {}),
            "total_files_scanned": len(inventory.get("files", [])),
            "total_prompts_detected": counts.get("prompts", 0),
            "total_routes_detected": counts.get("routes", 0),
            "total_scripts_detected": counts.get("scripts", 0),
            "total_subagents_detected": counts.get("subagents", 0),
            "total_code_invocations": counts.get("scripts", 0) + counts.get("hooks", 0),
            "source_reports_read": [p for p in [ai.get("path")] if p],
            "ai_review_history_runs": ai.get("history_runs", 0),
            "rolling": {k: rolling.get(k) for k in
                        ("new_count", "repeated_count", "resolved_count", "carried_open_count")
                        } if rolling.get("status") == "ok" else {"status": rolling.get("status", "not_run")},
            "resolved_issues": rolling.get("resolved", []),
        },
        "next_review_trigger": next_trigger_for(mode),
        "dry_run": bool(args.dry_run),
    }
    return report


def build_arg_parser():
    p = argparse.ArgumentParser(
        prog="run_adaptive_harness_review.py",
        description="Adaptive-harness rolling-review runner. Reads AI-review structured "
                    "output, links findings across runs, renders patch proposals. "
                    "Never edits harness files; scheduled mode is report-only.")
    p.add_argument("--mode", required=True, choices=sorted(MODES))
    p.add_argument("--target", default=str(REPO_ROOT))
    p.add_argument("--output", default=None,
                   help="Output dir (default: <target>/reports/harness). Gitignored by design.")
    p.add_argument("--read-ai-review", default=None, dest="read_ai_review",
                   help="Path to AI-review latest.json (default: <target>/reports/ai-review/latest.json).")
    p.add_argument("--home", default=os.path.expanduser("~/.claude"))
    p.add_argument("--no-home", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="Print report JSON; write NOTHING.")
    p.add_argument("--changed-files-only", action="store_true")
    p.add_argument("--since-ref", default=None)
    p.add_argument("--ingest", default=None,
                   help="LLM findings JSON (validated, same contract as run_ai_review.py).")
    return p


def main(argv=None):
    rar.utf8_stdout()
    args = build_arg_parser().parse_args(argv)
    args.target = Path(args.target).resolve()
    if not args.target.is_dir():
        print(f"ERROR: target not found: {args.target}", file=sys.stderr)
        return 2
    if args.ingest and args.mode == "scheduled_harness_review":
        print("ERROR: --ingest is not allowed with --mode scheduled_harness_review "
              "(scheduled runs are deterministic report-only by doctrine)", file=sys.stderr)
        return 1
    ingest = {}
    if args.ingest:
        try:
            ingest = json.loads(Path(args.ingest).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: cannot read ingest file: {exc}", file=sys.stderr)
            return 1
        errors = rar.validate_ingest(ingest)
        if errors:
            print("ERROR: ingest findings failed validation:", file=sys.stderr)
            for e in errors:
                print(f"  - {e}", file=sys.stderr)
            return 1
    scoped_files = None
    if args.changed_files_only:
        diff = rar.collect_diff(args.target, args.since_ref)
        if diff["status"] != "ok":
            print(f"ERROR: --changed-files-only needs a working git diff: {diff.get('reason')}",
                  file=sys.stderr)
            return 1
        scoped_files = {c["path"] for c in diff["changed"]} | set(diff["untracked"])

    started = time.time()
    ctx = {"target": args.target, "home": None if args.no_home else args.home,
           "since_ref": args.since_ref, "scoped_files": scoped_files,
           "read_ai_review": args.read_ai_review, "output": args.output}
    collected = {}
    for name in MODES[args.mode]:
        collected[name] = resolve_collector(name)(ctx)

    report = assemble_report(args.mode, args, collected, ingest, started)
    errors = rar.validate_report(report, known_modes=MODES)
    if errors:
        print("ERROR: assembled report failed schema core validation:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    proposals_md = None
    if args.mode == "patch_proposal":
        # Union of every pending source, deduped by key - a non-empty ingest
        # must not mask high-risk items sitting in the rolling state
        # (2026-07-06 review pair, correctness nit).
        pool = list(report["recommendations"])
        pool += collected.get("ai_review_input", {}).get("recommendations", [])
        state_path = (Path(args.output) if args.output
                      else args.target / "reports" / "harness") / "rolling_state.json"
        if state_path.is_file():
            try:
                pool += json.loads(state_path.read_text(encoding="utf-8")).get("recommendations", [])
            except (OSError, json.JSONDecodeError):
                report["unresolved_questions"].append(
                    "rolling_state.json unreadable during patch_proposal - its pending items are NOT in this sheet.")
        seen, unique_pool = set(), []
        for r in pool:
            key = str(_rec_key(r))
            if key not in seen:
                seen.add(key)
                unique_pool.append(r)
        candidates = high_risk(unique_pool)
        proposals_md = render_patch_proposals(candidates, report["review_id"])
        report["metrics"]["patch_proposals_rendered"] = len(candidates)

    if args.dry_run:
        out = dict(report)
        if proposals_md is not None:
            out["patch_proposals_preview"] = proposals_md
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    out_dir = Path(args.output) if args.output else args.target / "reports" / "harness"
    latest = rar.write_outputs(report, out_dir, stem_suffix="harness-review")
    if (args.mode == "rolling_improvement_review"
            and collected.get("rolling_state", {}).get("status") == "ok"):
        # Guarded write: when the rolling collector could not run (AI-review
        # input missing, corrupt prior state), the previous state file is
        # PRESERVED - overwriting it with an empty list would silently drop
        # every carried-open finding (2026-07-06 review pair, posture finding 1).
        (out_dir / "rolling_state.json").write_text(json.dumps({
            "review_id": report["review_id"],
            "review_date": report["review_date"],
            "recommendations": report["recommendations"],
        }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    if proposals_md is not None:
        pdir = out_dir / "proposals"
        pdir.mkdir(parents=True, exist_ok=True)
        pfile = pdir / f"PATCH-PROPOSALS-{report['review_date'][:10]}.md"
        pfile.write_text(proposals_md, encoding="utf-8")
        print(f"   patch proposals: {pfile}")
    print(f"OK {report['review_id']}: wrote {latest} (+ latest.md, history/)")
    rolling = report["metrics"].get("rolling", {})
    if rolling and "new_count" in rolling:
        print(f"   rolling: new={rolling['new_count']} repeated={rolling['repeated_count']} "
              f"resolved={rolling['resolved_count']} carried_open={rolling['carried_open_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
