#!/usr/bin/env python3
"""Summarize the 2026-07-07 harness-effect pilot from canonical scorecards.

This is a reporting helper, not a grader. It reads the scorecards already
written under evals/harness_ab/pilot_2026-07-07/scorecards and emits computed
aggregate metrics so README/evidence claims can cite numbers generated from
disk artifacts instead of hand-calculated prose.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


REPO = Path(__file__).resolve().parent.parent
DEFAULT_PILOT = REPO / "evals" / "harness_ab" / "pilot_2026-07-07"
HIGH_RISK_SCENARIOS = {"T2", "T3", "T4", "T5"}


def as_bool(value) -> bool:
    return bool(value) if isinstance(value, bool) else False


def load_trials(pilot_dir: Path) -> list[dict]:
    scorecard_dir = pilot_dir / "scorecards"
    trials: list[dict] = []
    for path in sorted(scorecard_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for trial in data.get("trials", []):
            row = dict(trial)
            row["scorecard"] = path.name
            trials.append(row)
    if not trials:
        raise SystemExit(f"no trials found under {scorecard_dir}")
    return trials


def summarize_trials(trials: Iterable[dict]) -> dict:
    rows = list(trials)
    arms = {}
    for arm in sorted({row.get("arm") for row in rows}):
        arm_rows = [row for row in rows if row.get("arm") == arm]
        arms[arm] = {
            "trials": len(arm_rows),
            "primary_pass": sum(1 for row in arm_rows if as_bool(row.get("primary_pass"))),
            "false_done": sum(1 for row in arm_rows if as_bool(row.get("false_done"))),
            "canonical_checked": sum(1 for row in arm_rows if as_bool(row.get("canonical_checked"))),
            "tool_calls": sum(int(row.get("tool_calls_reported_by_delegate") or 0) for row in arm_rows),
            "duration_seconds": round(sum(float(row.get("duration_seconds") or 0) for row in arm_rows), 2),
            "input_tokens": sum(int(row.get("input_tokens") or 0) for row in arm_rows),
            "output_tokens": sum(int(row.get("output_tokens") or 0) for row in arm_rows),
        }
    deltas = {}
    if "A" in arms and "B" in arms:
        a, b = arms["A"], arms["B"]
        for key in ("primary_pass", "false_done", "canonical_checked", "tool_calls",
                    "duration_seconds", "input_tokens", "output_tokens"):
            deltas[f"B_minus_A_{key}"] = round(b[key] - a[key], 2)
        for key in ("tool_calls", "duration_seconds", "input_tokens", "output_tokens"):
            deltas[f"B_over_A_{key}"] = round(b[key] / a[key], 2) if a[key] else None
    return {"arms": arms, "deltas": deltas}


def build_report(pilot_dir: Path) -> dict:
    trials = load_trials(pilot_dir)
    high_risk = [row for row in trials if row.get("scenario") in HIGH_RISK_SCENARIOS]
    return {
        "pilot": pilot_dir.name,
        "source": str((pilot_dir / "scorecards").relative_to(REPO)).replace("\\", "/"),
        "status": "pilot_proxy_not_formal_ab",
        "important_limitation": (
            "Same-environment proxy; Arm A may be contaminated by global verification "
            "discipline. Do not treat this as a formal capability benchmark."
        ),
        "all_trials": summarize_trials(trials),
        "high_risk_trials_T2_T5": summarize_trials(high_risk),
    }


def print_markdown(report: dict) -> None:
    print(f"# Harness A/B pilot summary: {report['pilot']}")
    print()
    print(report["important_limitation"])
    print()
    for section_key, label in (
        ("all_trials", "All trials"),
        ("high_risk_trials_T2_T5", "High-risk trials T2-T5"),
    ):
        section = report[section_key]
        print(f"## {label}")
        print()
        print("| Arm | Trials | Pass | False done | Canonical checked | Tool calls | Input tokens | Output tokens | Seconds |")
        print("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
        for arm, row in section["arms"].items():
            print(
                f"| {arm} | {row['trials']} | {row['primary_pass']} | {row['false_done']} | "
                f"{row['canonical_checked']} | {row['tool_calls']} | {row['input_tokens']} | "
                f"{row['output_tokens']} | {row['duration_seconds']} |"
            )
        print()
        deltas = section["deltas"]
        if deltas:
            print("Deltas: " + ", ".join(f"{k}={v}" for k, v in sorted(deltas.items())))
            print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-dir", type=Path, default=DEFAULT_PILOT)
    parser.add_argument("--markdown", action="store_true", help="emit a Markdown table instead of JSON")
    args = parser.parse_args(argv)

    report = build_report(args.pilot_dir.resolve())
    if args.markdown:
        print_markdown(report)
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())