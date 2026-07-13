#!/usr/bin/env python3
"""Deterministic Hermes compact-router contract benchmark (no model calls)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import subprocess
import time
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
PROMPT = REPO / "prompts" / "hermes-router.md"
CASES = REPO / "benchmarks" / "hermes_router" / "cases.json"
BASELINE_FALLBACK = REPO / "benchmarks" / "hermes_router" / "baseline_prompt.txt"
BASELINE_REF = "19c4966"
BASELINE_BYTES = 1402
BASELINE_SHA256 = "9b3aa95feda4e10b3457b9d4818240289ddf3ad91102ff64231d9f917f1406d0"
CONTRACT_RE = re.compile(
    r"<!-- standing-contract:start -->\s*```\s*([\s\S]*?)\s*```\s*<!-- standing-contract:end -->")
BASELINE_RE = re.compile(
    r"## Prompt block \(copy-paste-ready\)\s*```\s*([\s\S]*?)\s*```")

COMBINATIONS = {
    "daily": ("hermes", "direct"),
    "debug": ("claude", "opus"),
    "architecture": ("claude", "opus-distilled"),
    "completion": ("claude", "fable-distilled"),
    "mechanical": ("codex", "scoped"),
    "harness": ("harness", "runner"),
    "governance": ("claude", "opus-distilled"),
    "unclear": ("ask-user", "clarify"),
}
CONTRACT_MAPPING_FRAGMENTS = (
    "daily>hermes/direct",
    "clear debug>claude/opus",
    "architecture (incl release planning/unclear root cause)>claude/opus-distilled",
    "governance/security>claude/opus-distilled",
    "completion/artifact mismatch/release approval>claude/fable-distilled",
    "stable mechanical bulk>codex/scoped",
    "deterministic harness scan>harness/runner",
    "unclassifiable>ask-user/clarify",
)


def extract_compact_contract() -> str:
    match = CONTRACT_RE.search(PROMPT.read_text(encoding="utf-8"))
    if not match:
        raise ValueError("Hermes standing contract markers are missing")
    return match.group(1)


def extract_baseline_contract() -> tuple[str, str]:
    """Load the exact pre-change Git blob, with a tracked offline fallback."""
    proc = subprocess.run(
        ["git", "show", f"{BASELINE_REF}:prompts/hermes-router.md"],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode == 0:
        match = BASELINE_RE.search(proc.stdout)
        if match:
            baseline, source = match.group(1), f"git:{BASELINE_REF}"
        else:
            baseline, source = "", ""
    else:
        baseline, source = "", ""
    if not baseline:
        baseline = BASELINE_FALLBACK.read_text(encoding="utf-8").rstrip("\r\n")
        source = "tracked-fallback"
    encoded = baseline.encode("utf-8")
    if len(encoded) != BASELINE_BYTES or hashlib.sha256(encoded).hexdigest() != BASELINE_SHA256:
        raise ValueError(f"Hermes baseline drifted: {source}")
    return baseline, source


def load_cases() -> list[dict]:
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or len(payload.get("cases", [])) != 10:
        raise ValueError("Hermes fixture must contain exactly ten schema-v1 cases")
    cases = payload["cases"]
    for case in cases:
        task_class = case.get("input_class")
        if task_class not in COMBINATIONS or case.get("expected", {}).get("class") != task_class:
            raise ValueError(f"invalid Hermes fixture class: {case.get('id')}")
    return cases


def decision_for_class(task_class: str) -> dict:
    if task_class not in COMBINATIONS:
        raise ValueError(f"unknown Hermes fixture class: {task_class}")
    target, mode = COMBINATIONS[task_class]
    return {"class": task_class, "target": target, "mode": mode}


def emit_receipt(decision: dict, variant: str) -> str:
    if variant == "B":
        return (
            f'{{"v":1,"class":"{decision["class"]}",'
            f'"target":"{decision["target"]}","mode":"{decision["mode"]}"}}')
    return (
        f'classification: {decision["class"]}\n'
        f'route: {decision["target"]}\nmode: {decision["mode"]}')


def parse_receipt(receipt: str) -> dict:
    payload = json.loads(receipt)
    if set(payload) != {"v", "class", "target", "mode"} or payload["v"] != 1:
        raise ValueError("invalid Hermes receipt shape or version")
    task_class = payload["class"]
    if task_class not in COMBINATIONS:
        raise ValueError("unknown Hermes receipt class")
    if (payload["target"], payload["mode"]) != COMBINATIONS[task_class]:
        raise ValueError("invalid target/mode for Hermes receipt class")
    return payload


def route_once(task_class: str, contract: str, variant: str) -> str:
    contract.encode("utf-8")  # Standing-context load proxy; no model inference claim.
    return emit_receipt(decision_for_class(task_class), variant)


def paired_route_times(cases: list[dict], baseline: str, compact: str,
                       iterations: int) -> tuple[int, int]:
    """Measure interleaved A/B samples to reduce order and clock-drift bias."""
    contracts = {"A": baseline, "B": compact}
    samples = {"A": [], "B": []}
    for case in cases:  # Warm both paths before collecting samples.
        route_once(case["input_class"], baseline, "A")
        route_once(case["input_class"], compact, "B")
    for sample_index in range(9):
        order = ("A", "B") if sample_index % 2 == 0 else ("B", "A")
        for variant in order:
            started = time.perf_counter_ns()
            for _repeat in range(iterations):
                for case in cases:
                    route_once(case["input_class"], contracts[variant], variant)
            samples[variant].append(time.perf_counter_ns() - started)
    return int(statistics.median(samples["A"])), int(statistics.median(samples["B"]))


def run_benchmark(iterations: int = 1000) -> dict:
    cases = load_cases()
    baseline, baseline_source = extract_baseline_contract()
    compact = extract_compact_contract()
    results = []
    parse_count = mapping_correct = protected_misroutes = 0
    for case in cases:
        decision = decision_for_class(case["input_class"])
        receipt = emit_receipt(decision, "B")
        parsed = parse_receipt(receipt)
        parse_count += 1
        correct = all(parsed[key] == value for key, value in case["expected"].items())
        mapping_correct += int(correct)
        protected_misroute = case["protected"] and parsed["target"] in {"hermes", "codex"}
        protected_misroutes += int(protected_misroute)
        results.append({
            "id": case["id"],
            "receipt": parsed,
            "correct": correct,
            "protected_misroute": protected_misroute,
        })

    baseline_bytes = len(baseline.encode("utf-8"))
    compact_bytes = len(compact.encode("utf-8"))
    a_ns, b_ns = paired_route_times(cases, baseline, compact, iterations)
    byte_ratio = compact_bytes / baseline_bytes
    latency_ratio = b_ns / a_ns
    gates = {
        "standing_bytes_le_60pct": byte_ratio <= 0.60,
        "contract_mapping_fragments_complete": all(
            fragment in compact for fragment in CONTRACT_MAPPING_FRAGMENTS),
        "receipts_parse_10_of_10": parse_count == 10,
        "mapping_coverage_10_of_10": mapping_correct == 10,
        "protected_misroutes_zero": protected_misroutes == 0,
        "static_median_time_ratio_le_1_10": latency_ratio <= 1.10,
    }
    return {
        "schema_version": 1,
        "baseline_source": baseline_source,
        "prompt": {
            "baseline_bytes": baseline_bytes,
            "compact_bytes": compact_bytes,
            "byte_ratio": round(byte_ratio, 4),
            "estimated_tokens_bytes_div_4": {
                "baseline": (baseline_bytes + 3) // 4,
                "compact": (compact_bytes + 3) // 4,
            },
        },
        "fixtures": {
            "total": len(cases),
            "parsed": parse_count,
            "mapping_correct": mapping_correct,
            "protected_misroutes": protected_misroutes,
            "results": results,
        },
        "static_time_proxy": {
            "definition": "UTF-8 contract load + deterministic mapping lookup + receipt emission; not Hermes/model latency",
            "sampling": "9 interleaved paired samples with alternating A/B order after warmup",
            "iterations_per_case_per_sample": iterations,
            "samples_per_variant": 9,
            "baseline_median_ns": a_ns,
            "compact_median_ns": b_ns,
            "ratio": round(latency_ratio, 4),
        },
        "gates": gates,
        "passed": all(gates.values()),
        "limitations": [
            "Static fixtures prove contract economy and schema/policy mapping coverage only.",
            "They do not measure whether Hermes classifies the natural-language tasks correctly.",
            "Token counts are bytes/4 estimates, not live Hermes usage telemetry.",
            "The time proxy is host-side and does not prove live Hermes latency or quality.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=1000)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.iterations < 1:
        parser.error("--iterations must be positive")
    report = run_benchmark(args.iterations)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        prompt = report["prompt"]
        fixtures = report["fixtures"]
        timing = report["static_time_proxy"]
        print(
            f"prompt bytes: {prompt['compact_bytes']}/{prompt['baseline_bytes']} "
            f"({prompt['byte_ratio']:.1%}); receipts: {fixtures['parsed']}/10; "
            f"mapping coverage: {fixtures['mapping_correct']}/10; protected misroutes: "
            f"{fixtures['protected_misroutes']}; static time ratio: {timing['ratio']:.3f}; "
            f"passed: {report['passed']}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
