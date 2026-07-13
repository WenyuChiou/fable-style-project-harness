#!/usr/bin/env python3
"""Hermes compact-router static benchmark and optional live one-shot runner."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import shutil
import signal
import statistics
import subprocess
import tempfile
import time
import unicodedata
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


REPO = Path(__file__).resolve().parent.parent
PROMPT = REPO / "prompts" / "hermes-router.md"
CASES = REPO / "benchmarks" / "hermes_router" / "cases.json"
BASELINE_FALLBACK = REPO / "benchmarks" / "hermes_router" / "baseline_prompt.txt"
FAIR_PREREGISTRATION = REPO / "benchmarks" / "hermes_router" / "fair_ab_preregistration.json"
FAIR_PREREGISTRATION_SHA256 = "595a6384c3e060c98bde46ae366022fea3829ebf594fc3d4ea5abbe2e5595343"
BASELINE_REF = "19c4966"
BASELINE_BYTES = 1402
BASELINE_SHA256 = "9b3aa95feda4e10b3457b9d4818240289ddf3ad91102ff64231d9f917f1406d0"
DEFAULT_LIVE_ROOT = REPO / "evals" / "hermes_router_live"
POST_KILL_TIMEOUT = 10
FAIR_STDERR_LIMIT = 8000
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
    "Class=daily|debug|architecture|completion|mechanical|harness|governance|unclear",
    "release-plan/unclear-root=architecture",
    "mismatch/release-approval=completion",
    "security=governance",
    "bulk=mechanical",
    "deterministic-scan=harness",
    "unclassifiable=unclear",
    "Map class>target,mode",
    "daily>hermes,direct",
    "debug>claude,opus",
    "architecture>claude,opus-distilled",
    "governance>claude,opus-distilled",
    "completion>claude,fable-distilled",
    "mechanical>codex,scoped",
    "harness>harness,runner",
    "unclear>ask-user,clarify",
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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_fair_preregistration() -> dict:
    if sha256_file(FAIR_PREREGISTRATION) != FAIR_PREREGISTRATION_SHA256:
        raise ValueError("Hermes fair A/B preregistration drifted")
    payload = json.loads(FAIR_PREREGISTRATION.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or payload.get("frozen_before_new_live_outputs") is not True:
        raise ValueError("invalid Hermes fair A/B preregistration")
    repo_root = REPO.resolve()
    for relative, expected in payload.get("frozen_input_sha256", {}).items():
        path = (REPO / relative).resolve()
        if repo_root not in path.parents:
            raise ValueError(f"fair preregistration input escaped repository: {relative}")
        if not path.is_file() or sha256_file(path) != expected:
            raise ValueError(f"fair preregistration input drifted: {relative}")
    design = payload.get("design", {})
    if (design.get("cases"), design.get("repetitions"), design.get("calls_per_variant"),
            design.get("total_calls"), design.get("retries")) != (10, 5, 50, 100, 0):
        raise ValueError("fair preregistration design drifted")
    return payload


def _freeze_semantic_value(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze_semantic_value(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_semantic_value(item) for item in value)
    return value


def fair_semantic_config(preregistration: dict) -> Mapping[str, Any]:
    """Return the only frozen data the stdout-only extractor is allowed to observe."""
    grading = preregistration["grading"]
    return _freeze_semantic_value({
        "reference_semantic_extractor": grading["reference_semantic_extractor"],
        "target_aliases": grading["target_aliases"],
        "mode_aliases": grading["mode_aliases"],
    })


def fair_live_prompt(contract: str, task: str, variant: str, preregistration: dict) -> str:
    if variant not in {"A", "B"}:
        raise ValueError("fair prompt variant must be A or B")
    invariant = preregistration["design"]["prompt_invariant"]
    return (
        contract + invariant["common_prefix_exact"]
        + invariant[f"{variant}_output_instruction_exact"]
        + invariant["common_task_prefix_exact"] + task)


FAIR_SEGMENT_DELIMITERS = re.compile(r"[-‐‑‒–—―/_+]+")


def _fair_pre_anchor_text(stdout: str) -> str:
    return unicodedata.normalize("NFKC", stdout).casefold().replace("\r\n", "\n").replace("\r", "\n")


def _fair_segment(text: str) -> str:
    return " ".join(FAIR_SEGMENT_DELIMITERS.sub(" ", text).split())


def _fair_candidates(segments: list[str], aliases: dict[str, list[str]]) -> list[str]:
    candidates: set[str] = set()
    for raw_segment in segments:
        segment = _fair_segment(raw_segment)
        matches: list[tuple[int, int, str]] = []
        for canonical, values in aliases.items():
            for raw_alias in values:
                alias = _fair_segment(raw_alias)
                pattern = re.compile(r"(?<!\w)" + re.escape(alias) + r"(?!\w)")
                matches.extend((match.start(), match.end(), canonical)
                               for match in pattern.finditer(segment))
        for index, match in enumerate(matches):
            start, end, canonical = match
            contained = any(
                other_index != index
                and other_start <= start and end <= other_end
                and (other_start < start or end < other_end)
                for other_index, (other_start, other_end, _other_value) in enumerate(matches))
            if not contained:
                candidates.add(canonical)
    return sorted(candidates)


def extract_fair_semantics(stdout: str, semantic_config: Mapping[str, Any]) -> dict:
    """Extract candidates from stdout only; gold data is deliberately unavailable here."""
    text = _fair_pre_anchor_text(stdout)
    spec = semantic_config["reference_semantic_extractor"]
    target_segments: list[str] = []
    for regex in spec["target_anchor_regexes"]:
        target_segments.extend(match.group(1) for match in re.finditer(regex, text, re.IGNORECASE))
    target_segments.extend(
        match.group(1) for match in re.finditer(
            spec["standalone_target_regex"], text, re.IGNORECASE))
    mode_segments = list(target_segments)
    for regex in spec["mode_anchor_regexes"]:
        mode_segments.extend(match.group(1) for match in re.finditer(regex, text, re.IGNORECASE))
    target_candidates = _fair_candidates(target_segments, semantic_config["target_aliases"])
    mode_candidates = _fair_candidates(mode_segments, semantic_config["mode_aliases"])
    target = target_candidates[0] if len(target_candidates) == 1 else None
    mode = mode_candidates[0] if len(mode_candidates) == 1 else None
    target_reason = (
        "selected" if len(target_candidates) == 1 else
        "unresolved_zero_candidates" if not target_candidates else
        "ambiguous_multiple_candidates")
    mode_reason = (
        "selected" if len(mode_candidates) == 1 else
        "unresolved_zero_candidates" if not mode_candidates else
        "ambiguous_multiple_candidates")
    if len(target_candidates) > 1 or len(mode_candidates) > 1:
        state = "ambiguous"
    elif target is None or mode is None:
        state = "unresolved"
    else:
        state = "selected"
    return {
        "target_segments": [_fair_segment(value) for value in target_segments],
        "mode_segments": [_fair_segment(value) for value in mode_segments],
        "target_candidates": target_candidates,
        "target": target,
        "target_reason": target_reason,
        "mode_candidates": mode_candidates,
        "mode": mode,
        "mode_reason": mode_reason,
        "state": state,
    }


def grade_fair_semantics(stdout: str, case: dict,
                         semantic_config: Mapping[str, Any]) -> dict:
    semantic = extract_fair_semantics(stdout, semantic_config)
    expected = case["expected"]
    target_correct = semantic["target"] == expected["target"]
    exact_correct = target_correct and semantic["mode"] == expected["mode"]
    protected = bool(case["protected"])
    return {
        **semantic,
        "target_correct": target_correct,
        "exact_route_correct": exact_correct,
        "protected_misroute": bool(
            protected and {"hermes", "codex"}.intersection(semantic["target_candidates"])),
        "protected_unresolved": protected and semantic["state"] == "unresolved",
        "protected_ambiguous": protected and semantic["state"] == "ambiguous",
    }


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


def decode_json_object(receipt: str) -> dict:
    payload = json.loads(receipt)
    if not isinstance(payload, dict):
        raise ValueError("Hermes receipt must be a JSON object")
    return payload


def decode_receipt(receipt: str) -> dict:
    payload = decode_json_object(receipt)
    if set(payload) != {"v", "class", "target", "mode"}:
        raise ValueError("invalid Hermes receipt keys")
    if type(payload["v"]) is not int or payload["v"] != 1:  # bool is not an accepted version.
        raise ValueError("invalid Hermes receipt shape or version")
    if any(not isinstance(payload[key], str) for key in ("class", "target", "mode")):
        raise ValueError("Hermes receipt class, target, and mode must be strings")
    return payload


def validate_receipt(payload: dict) -> dict:
    task_class = payload["class"]
    if task_class not in COMBINATIONS:
        raise ValueError("unknown Hermes receipt class")
    if (payload["target"], payload["mode"]) != COMBINATIONS[task_class]:
        raise ValueError("invalid target/mode for Hermes receipt class")
    return payload


def parse_receipt(receipt: str) -> dict:
    return validate_receipt(decode_receipt(receipt))


def is_forbidden_protected_target(payload: dict | None) -> bool:
    if not payload:
        return False
    target = payload.get("target")
    if not isinstance(target, str):
        return False
    target = target.strip().lower()
    return bool(re.match(r"^(hermes|codex)(?:$|[\s/_-])", target))


def route_once(task_class: str, contract: str, variant: str) -> str:
    contract.encode("utf-8")  # Standing-context load proxy; no model inference claim.
    return emit_receipt(decision_for_class(task_class), variant)


def live_prompt(contract: str, task: str, variant: str = "B") -> str:
    output_contract = (
        "Return the JSON receipt only; this evaluation explicitly requests receipt output."
        if variant == "B" else
        "Return exactly three lines: classification: <class>, route: <target>, mode: <mode>."
    )
    return (
        f"{contract}\n\nEVALUATION MODE: Classify only. Do not execute the task or use tools. "
        f"{output_contract}\nTASK: {task}")


def decode_baseline_receipt(receipt: str) -> dict:
    match = re.fullmatch(
        r"\s*classification:\s*([^\r\n]+)\s*[\r\n]+route:\s*([^\r\n]+)\s*"
        r"[\r\n]+mode:\s*([^\r\n]+)\s*", receipt, flags=re.IGNORECASE)
    if not match:
        raise ValueError("invalid baseline free-form receipt")
    payload = {
        "v": 1,
        "class": match.group(1).strip().lower(),
        "target": match.group(2).strip().lower(),
        "mode": match.group(3).strip().lower(),
    }
    return payload


def parse_baseline_receipt(receipt: str) -> dict:
    return validate_receipt(decode_baseline_receipt(receipt))


def as_text(value: str | bytes | None) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value or ""


def run_hermes_process(prompt: str, timeout: int,
                       executable: str = "hermes") -> tuple[str, str, int | None, str, float]:
    """Run one Hermes classification and terminate its process tree on timeout."""
    cmd = [executable, "--ignore-rules", "--oneshot", prompt]
    started = time.perf_counter()
    proc = subprocess.Popen(
        cmd,
        cwd=REPO,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        start_new_session=os.name != "nt",
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return stdout, stderr, proc.returncode, "", time.perf_counter() - started
    except subprocess.TimeoutExpired as exc:
        termination_notes = []

        def kill_direct() -> None:
            try:
                proc.kill()
            except OSError as kill_exc:
                termination_notes.append(f"direct_kill_failed:{type(kill_exc).__name__}")

        if os.name == "nt":
            try:
                killed = subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    capture_output=True, timeout=POST_KILL_TIMEOUT)
                if killed.returncode != 0:
                    termination_notes.append(f"taskkill_exit_{killed.returncode}")
                    kill_direct()
            except (subprocess.TimeoutExpired, OSError) as kill_exc:
                termination_notes.append(f"taskkill_failed:{type(kill_exc).__name__}")
                kill_direct()
        else:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError as kill_exc:
                termination_notes.append(f"killpg_failed:{type(kill_exc).__name__}")
                kill_direct()
        try:
            stdout, stderr = proc.communicate(timeout=POST_KILL_TIMEOUT)
        except subprocess.TimeoutExpired as followup_exc:
            termination_notes.append("post_kill_wait_timeout")
            kill_direct()
            try:
                stdout, stderr = proc.communicate(timeout=POST_KILL_TIMEOUT)
            except subprocess.TimeoutExpired as final_exc:
                termination_notes.append("direct_kill_wait_timeout")
                stdout, stderr = as_text(final_exc.stdout), as_text(final_exc.stderr)
                for stream in (proc.stdout, proc.stderr):
                    if stream is not None:
                        with contextlib.suppress(OSError):
                            stream.close()
        stdout = as_text(stdout) or as_text(exc.stdout)
        stderr = (as_text(stderr) or as_text(exc.stderr)) + f"\nTIMEOUT after {timeout} seconds"
        if termination_notes:
            stderr += "\nTERMINATION: " + ",".join(termination_notes)
        return stdout, stderr, None, f"timeout_{timeout}s", time.perf_counter() - started


def git_output(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=30)


def live_provenance() -> dict:
    runner_path = Path(__file__).resolve()
    prompt_bytes = PROMPT.read_bytes()
    runner_relative = runner_path.relative_to(REPO).as_posix()
    tracked = True
    for path in (runner_relative, PROMPT.relative_to(REPO).as_posix(), CASES.relative_to(REPO).as_posix()):
        if git_output(["diff", "--quiet", "HEAD", "--", path]).returncode != 0:
            tracked = False
        if git_output(["diff", "--cached", "--quiet", "HEAD", "--", path]).returncode != 0:
            tracked = False
    head = git_output(["rev-parse", "HEAD"])
    try:
        version = subprocess.run(
            ["hermes", "--version"], cwd=REPO, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30)
        version_text = (version.stdout or version.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        version_text = f"UNAVAILABLE:{type(exc).__name__}"
    model = provider = "UNAVAILABLE"
    status_sha256 = config_sha256 = "UNAVAILABLE"
    try:
        status = subprocess.run(
            ["hermes", "status"], cwd=REPO, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30)
        status_text = (status.stdout or status.stderr)
        status_sha256 = hashlib.sha256(status_text.encode("utf-8")).hexdigest()
        model_match = re.search(r"^\s*Model:\s*(.+)$", status_text, flags=re.MULTILINE)
        provider_match = re.search(r"^\s*Provider:\s*(.+)$", status_text, flags=re.MULTILINE)
        model = model_match.group(1).strip() if model_match else "UNAVAILABLE"
        provider = provider_match.group(1).strip() if provider_match else "UNAVAILABLE"
        config_path = subprocess.run(
            ["hermes", "config", "path"], cwd=REPO, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30)
        candidate = Path(config_path.stdout.strip())
        if config_path.returncode == 0 and candidate.is_file():
            config_sha256 = hashlib.sha256(candidate.read_bytes()).hexdigest()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return {
        "frozen_sha": head.stdout.strip() if head.returncode == 0 else "UNKNOWN",
        "runner_sha256": hashlib.sha256(runner_path.read_bytes()).hexdigest(),
        "prompt_sha256": hashlib.sha256(prompt_bytes).hexdigest(),
        "inputs_tracked_at_frozen_sha": tracked,
        "hermes_version": version_text,
        "runtime_fingerprint": {
            "model": model,
            "provider": provider,
            "status_sha256": status_sha256,
            "config_sha256": config_sha256,
            "config_hash_scope": "entire config.yaml bytes when available",
            "raw_config_or_secrets_stored": False,
        },
        "live_command_policy": ["hermes", "--ignore-rules", "--oneshot", "<prompt>"],
    }


def provenance_eligible(provenance: dict) -> bool:
    fingerprint = provenance.get("runtime_fingerprint", {})
    required = (
        fingerprint.get("model"), fingerprint.get("provider"),
        fingerprint.get("status_sha256"), fingerprint.get("config_sha256"),
    )
    hashes_valid = all(
        re.fullmatch(r"[0-9a-f]{64}", value or "")
        for value in (fingerprint.get("status_sha256"), fingerprint.get("config_sha256")))
    return bool(
        provenance.get("inputs_tracked_at_frozen_sha") is True
        and not str(provenance.get("hermes_version", "UNAVAILABLE")).startswith("UNAVAILABLE")
        and all(value and value != "UNAVAILABLE" for value in required)
        and hashes_valid)


def fair_runtime_fingerprint() -> dict:
    resolved = shutil.which("hermes")
    executable_path = "UNAVAILABLE"
    executable_sha256 = "UNAVAILABLE"
    if resolved:
        try:
            executable = Path(resolved).resolve(strict=True)
            executable_path = str(executable)
            executable_sha256 = sha256_file(executable)
        except OSError:
            pass

    def probe(*args: str) -> dict:
        if executable_path == "UNAVAILABLE":
            return {"returncode": None, "stdout": "", "stderr": "", "error": "executable_unavailable"}
        try:
            result = subprocess.run(
                [executable_path, *args], cwd=REPO, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=30)
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error": "",
            }
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {
                "returncode": None, "stdout": "", "stderr": "",
                "error": f"{type(exc).__name__}:{exc}",
            }

    version = probe("--version")
    status = probe("status")
    config = probe("config", "path")
    version_text = (version["stdout"] or version["stderr"]).strip()
    status_text = status["stdout"] + "\n--STDERR--\n" + status["stderr"]
    model_match = re.search(r"^\s*Model:\s*(.+)$", status_text, flags=re.MULTILINE)
    provider_match = re.search(r"^\s*Provider:\s*(.+)$", status_text, flags=re.MULTILINE)
    config_path = "UNAVAILABLE"
    config_sha256 = "UNAVAILABLE"
    if config["returncode"] == 0:
        try:
            candidate = Path(config["stdout"].strip()).resolve(strict=True)
            if candidate.is_file():
                config_path = str(candidate)
                config_sha256 = sha256_file(candidate)
        except OSError:
            pass
    return {
        "executable_path": executable_path,
        "executable_sha256": executable_sha256,
        "version_returncode": version["returncode"],
        "version": version_text or "UNAVAILABLE",
        "version_error": version["error"],
        "status_returncode": status["returncode"],
        "status_sha256": hashlib.sha256(status_text.encode("utf-8")).hexdigest()
        if status["returncode"] is not None else "UNAVAILABLE",
        "status_error": status["error"],
        "model": model_match.group(1).strip() if model_match else "UNAVAILABLE",
        "provider": provider_match.group(1).strip() if provider_match else "UNAVAILABLE",
        "config_path_returncode": config["returncode"],
        "config_path": config_path,
        "config_sha256": config_sha256,
        "config_error": config["error"],
        "raw_config_or_secrets_stored": False,
    }


def fair_runtime_fingerprint_eligible(fingerprint: dict) -> bool:
    required_hashes = (
        fingerprint.get("executable_sha256"), fingerprint.get("status_sha256"),
        fingerprint.get("config_sha256"),
    )
    return bool(
        all(fingerprint.get(key) == 0 for key in (
            "version_returncode", "status_returncode", "config_path_returncode"))
        and all(re.fullmatch(r"[0-9a-f]{64}", value or "") for value in required_hashes)
        and all(fingerprint.get(key) not in {None, "", "UNAVAILABLE"} for key in (
            "executable_path", "version", "model", "provider", "config_path")))


def fair_input_provenance(preregistration: dict) -> dict:
    runner = Path(__file__).resolve()
    relative_paths = [
        runner.relative_to(REPO).as_posix(),
        PROMPT.relative_to(REPO).as_posix(),
        CASES.relative_to(REPO).as_posix(),
        BASELINE_FALLBACK.relative_to(REPO).as_posix(),
        FAIR_PREREGISTRATION.relative_to(REPO).as_posix(),
    ]
    tracked_clean = True
    for relative in relative_paths:
        if git_output(["cat-file", "-e", f"HEAD:{relative}"]).returncode != 0:
            tracked_clean = False
        if git_output(["diff", "--quiet", "HEAD", "--", relative]).returncode != 0:
            tracked_clean = False
        if git_output(["diff", "--cached", "--quiet", "HEAD", "--", relative]).returncode != 0:
            tracked_clean = False
    head = git_output(["rev-parse", "HEAD"])
    observed_hashes = {relative: sha256_file(REPO / relative) for relative in relative_paths}
    frozen_match = all(
        observed_hashes.get(relative) == expected
        for relative, expected in preregistration["frozen_input_sha256"].items())
    return {
        "frozen_sha": head.stdout.strip() if head.returncode == 0 else "UNKNOWN",
        "input_sha256": observed_hashes,
        "inputs_tracked_at_frozen_sha": tracked_clean,
        "frozen_input_hashes_match": frozen_match,
        "live_command_policy": ["<resolved-hermes>", "--ignore-rules", "--oneshot", "<prompt>"],
    }


def fair_provenance_eligible(provenance: dict, start: dict, end: dict) -> bool:
    return bool(
        fair_start_provenance_eligible(provenance, start)
        and fair_runtime_fingerprint_eligible(end)
        and start == end)


def fair_start_provenance_eligible(provenance: dict, start: dict) -> bool:
    return bool(
        provenance.get("inputs_tracked_at_frozen_sha") is True
        and provenance.get("frozen_input_hashes_match") is True
        and re.fullmatch(r"[0-9a-f]{40}", provenance.get("frozen_sha", ""))
        and fair_runtime_fingerprint_eligible(start))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def write_fair_json_atomic(path: Path, payload: dict) -> None:
    """Atomically preserve fair-run evidence, including manifest rewrites."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        with contextlib.suppress(OSError):
            temporary.unlink()


def execute_fair_live_case(case: dict, contract: str, variant: str, timeout: int,
                           executable: str, preregistration: dict,
                           semantic_config: Mapping[str, Any]) -> tuple[dict, dict]:
    prompt = fair_live_prompt(contract, case["task"], variant, preregistration)
    spawn_error = ""
    try:
        stdout, stderr, exit_code, timeout_reason, duration = run_hermes_process(
            prompt, timeout, executable)
    except OSError as exc:
        stdout, stderr, exit_code, timeout_reason, duration = "", str(exc), None, "", 0.0
        spawn_error = f"hermes_spawn_{type(exc).__name__}"
    unscored_reason = (
        timeout_reason or spawn_error or (f"hermes_exit_{exit_code}" if exit_code != 0 else ""))
    native_receipt = None
    native_error = ""
    if not unscored_reason:
        try:
            native_receipt = (
                parse_receipt(stdout.strip()) if variant == "B" else parse_baseline_receipt(stdout))
        except (json.JSONDecodeError, ValueError) as exc:
            native_error = f"{type(exc).__name__}:{exc}"
    semantic = grade_fair_semantics(stdout, case, semantic_config)
    result = {
        "id": case["id"],
        "variant": variant,
        "expected": case["expected"],
        "protected": case["protected"],
        "exit_code": exit_code,
        "timeout_reason": timeout_reason,
        "spawn_error": spawn_error,
        "duration_seconds": duration,
        "duration_seconds_display": round(duration, 3),
        "native_parsed_receipt": native_receipt,
        "native_parse_error": native_error,
        "semantic": semantic,
        "unscored_reason": unscored_reason,
    }
    stderr_bounded = stderr[:FAIR_STDERR_LIMIT]
    raw = {
        **result,
        "prompt": prompt,
        "stdout": stdout,
        "stderr": stderr_bounded,
        "stderr_sha256": hashlib.sha256(stderr.encode("utf-8")).hexdigest(),
        "stderr_truncated": len(stderr) > FAIR_STDERR_LIMIT,
        "stderr_original_characters": len(stderr),
    }
    return result, raw


def build_fair_schedule(cases: list[dict], repetitions: int) -> list[dict]:
    schedule = []
    for repetition in range(1, repetitions + 1):
        for case_index, case in enumerate(cases):
            order = ("A", "B") if (repetition + case_index) % 2 else ("B", "A")
            for position, variant in enumerate(order, start=1):
                schedule.append({
                    "repetition": repetition,
                    "case_index": case_index,
                    "case_id": case["id"],
                    "variant": variant,
                    "position": position,
                })
    return schedule


def median_of_fifty(values: list[float]) -> float:
    if len(values) != 50:
        raise ValueError("fair median requires exactly 50 values")
    ordered = sorted(values)
    return (ordered[24] + ordered[25]) / 2.0


def fair_bootstrap(pair_ratios: list[float], preregistration: dict) -> dict:
    if len(pair_ratios) != 50 or any(value <= 0 for value in pair_ratios):
        return {"pair_median": None, "upper_95": None, "resamples": 0}
    latency = preregistration["latency"]
    state = int(latency["bootstrap_seed"])
    multiplier = 6364136223846793005
    increment = 1442695040888963407
    mask = (1 << 64) - 1
    statistics_ = []
    for _ in range(int(latency["bootstrap_resamples"])):
        sample = []
        for _draw in range(50):
            state = (multiplier * state + increment) & mask
            sample.append(pair_ratios[state % 50])
        statistics_.append(median_of_fifty(sample))
    statistics_.sort()
    upper_index = ((95 * len(statistics_) + 99) // 100) - 1
    return {
        "pair_median": median_of_fifty(pair_ratios),
        "upper_95": statistics_[upper_index],
        "upper_index_zero_based": upper_index,
        "resamples": len(statistics_),
        "final_lcg_state": state,
    }


def execute_live_case(case: dict, contract: str, variant: str, timeout: int) -> tuple[dict, dict]:
    prompt = live_prompt(contract, case["task"], variant)
    spawn_error = ""
    try:
        stdout, stderr, exit_code, timeout_reason, duration = run_hermes_process(prompt, timeout)
    except OSError as exc:
        stdout, stderr, exit_code, timeout_reason, duration = "", str(exc), None, "", 0.0
        spawn_error = f"hermes_spawn_{type(exc).__name__}"
    raw_object = None
    decoded = None
    parsed = None
    parse_error = ""
    if not timeout_reason and not spawn_error and exit_code == 0:
        try:
            if variant == "B":
                raw_object = decode_json_object(stdout.strip())
                decoded = decode_receipt(stdout.strip())
            else:
                raw_object = decode_baseline_receipt(stdout)
                decoded = raw_object
            parsed = validate_receipt(decoded)
        except (json.JSONDecodeError, ValueError) as exc:
            parse_error = f"{type(exc).__name__}:{exc}"
    correct = bool(parsed) and all(
        parsed[key] == value for key, value in case["expected"].items())
    protected_misroute = bool(case["protected"] and is_forbidden_protected_target(raw_object))
    unscored_reason = (
        timeout_reason or spawn_error or (f"hermes_exit_{exit_code}" if exit_code != 0 else ""))
    result = {
        "id": case["id"],
        "variant": variant,
        "expected": case["expected"],
        "protected": case["protected"],
        "exit_code": exit_code,
        "duration_seconds": round(duration, 3),
        "raw_json_object": raw_object,
        "decoded_receipt": decoded,
        "parsed_receipt": parsed,
        "parse_error": parse_error,
        "correct": correct,
        "protected_misroute": protected_misroute,
        "unscored_reason": unscored_reason,
    }
    raw = {**result, "prompt": prompt, "stdout": stdout, "stderr": stderr}
    return result, raw


def run_live(run_id: str, timeout: int = 180, limit: int | None = None,
             output_root: Path = DEFAULT_LIVE_ROOT, variant: str = "B") -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", run_id) or run_id in {".", ".."}:
        raise ValueError(f"invalid live run_id: {run_id!r}")
    if timeout < 1:
        raise ValueError("live timeout must be positive")
    if limit is not None and not 1 <= limit <= 10:
        raise ValueError("live limit must be between 1 and 10")
    if variant not in {"A", "B"}:
        raise ValueError("live variant must be A or B")
    run_dir = (output_root.resolve() / run_id).resolve()
    if run_dir.parent != output_root.resolve():
        raise ValueError("live run directory escaped output root")
    run_dir.mkdir(parents=True, exist_ok=False)
    cases = load_cases()[:limit] if limit is not None else load_cases()
    if variant == "B":
        contract, contract_source = extract_compact_contract(), "current-compact"
    else:
        contract, contract_source = extract_baseline_contract()
    manifest = {
        "run_id": run_id,
        "variant": variant,
        "contract_source": contract_source,
        "contract_sha256": hashlib.sha256(contract.encode("utf-8")).hexdigest(),
        "status": "pre_registered_not_complete",
        "case_ids": [case["id"] for case in cases],
        "timeout_seconds": timeout,
        "strict_receipt": True,
        "model_usage_available": False,
        "limitations": "Hermes one-shot exposes final text and wall time, not token usage.",
        **live_provenance(),
    }
    write_json(run_dir / "manifest.json", manifest)
    results = []
    for case in cases:
        result, raw = execute_live_case(case, contract, variant, timeout)
        write_json(run_dir / "trials" / f"{case['id']}.json", raw)
        results.append(result)
    scored = [row for row in results if not row["unscored_reason"]]
    durations = [row["duration_seconds"] for row in scored]
    scorecard = {
        "run_id": run_id,
        "variant": variant,
        "frozen_sha": manifest["frozen_sha"],
        "status": "complete" if len(results) == 10 else "partial",
        "executed": len(results),
        "scored": len(scored),
        "unscored": len(results) - len(scored),
        "parsed": sum(bool(row["parsed_receipt"]) for row in scored),
        "correct": sum(row["correct"] for row in scored),
        "protected_misroutes": sum(row["protected_misroute"] for row in scored),
        "median_seconds": round(statistics.median(durations), 3) if durations else None,
        "partial_pass": (
            len(results) > 0 and len(scored) == len(results)
            and sum(bool(row["parsed_receipt"]) for row in scored) == len(results)
            and sum(row["correct"] for row in scored) == len(results)
            and sum(row["protected_misroute"] for row in scored) == 0),
        "passed": (
            len(results) == 10 and len(scored) == 10
            and sum(bool(row["parsed_receipt"]) for row in scored) == 10
            and sum(row["correct"] for row in scored) >= 9
            and sum(row["protected_misroute"] for row in scored) == 0),
        "results": results,
    }
    manifest["status"] = "complete" if len(results) == 10 else "partial"
    write_json(run_dir / "manifest.json", manifest)
    write_json(run_dir / "scorecard.json", scorecard)
    return scorecard


def run_paired_live(run_id: str, repetitions: int = 2, timeout: int = 180,
                    output_root: Path = DEFAULT_LIVE_ROOT) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", run_id) or run_id in {".", ".."}:
        raise ValueError(f"invalid paired live run_id: {run_id!r}")
    if not 1 <= repetitions <= 5:
        raise ValueError("paired repetitions must be between 1 and 5")
    if timeout < 1:
        raise ValueError("paired timeout must be positive")
    run_dir = (output_root.resolve() / run_id).resolve()
    if run_dir.parent != output_root.resolve():
        raise ValueError("paired live run directory escaped output root")
    run_dir.mkdir(parents=True, exist_ok=False)
    cases = load_cases()
    baseline, baseline_source = extract_baseline_contract()
    compact = extract_compact_contract()
    contracts = {"A": baseline, "B": compact}
    schedule = []
    for repetition in range(1, repetitions + 1):
        for case_index, case in enumerate(cases):
            order = ("A", "B") if (repetition + case_index) % 2 else ("B", "A")
            for position, variant in enumerate(order, start=1):
                schedule.append({
                    "repetition": repetition, "case_id": case["id"],
                    "variant": variant, "position": position})
    provenance = live_provenance()
    eligible_provenance = provenance_eligible(provenance)
    manifest = {
        "run_id": run_id,
        "status": "pre_registered_not_complete",
        "design": "case-paired A/B with alternating order",
        "repetitions": repetitions,
        "timeout_seconds": timeout,
        "baseline_source": baseline_source,
        "contract_sha256": {
            "A": hashlib.sha256(baseline.encode("utf-8")).hexdigest(),
            "B": hashlib.sha256(compact.encode("utf-8")).hexdigest(),
        },
        "schedule": schedule,
        "success_thresholds": {
            "both_fully_scored_and_parseable": True,
            "B_route_accuracy": 0.90,
            "B_protected_misroutes": 0,
            "median_case_paired_B_over_A_time": 1.10,
        },
        "model_usage_available": False,
        "limitations": "Wall time is live and paired; Hermes one-shot does not expose token usage.",
        "provenance_eligible": eligible_provenance,
        **provenance,
    }
    write_json(run_dir / "manifest.json", manifest)
    case_by_id = {case["id"]: case for case in cases}
    results = []
    for item in schedule:
        case = case_by_id[item["case_id"]]
        result, raw = execute_live_case(
            case, contracts[item["variant"]], item["variant"], timeout)
        result.update(repetition=item["repetition"], position=item["position"])
        raw.update(repetition=item["repetition"], position=item["position"])
        filename = (
            f"R{item['repetition']:02d}_{case['id']}_{item['variant']}_P{item['position']}.json")
        write_json(run_dir / "trials" / filename, raw)
        results.append(result)
    summaries = {}
    for variant in ("A", "B"):
        rows = [row for row in results if row["variant"] == variant]
        scored = [row for row in rows if not row["unscored_reason"]]
        summaries[variant] = {
            "executed": len(rows),
            "scored": len(scored),
            "parsed": sum(bool(row["parsed_receipt"]) for row in scored),
            "correct": sum(row["correct"] for row in scored),
            "protected_misroutes": sum(row["protected_misroute"] for row in scored),
            "median_seconds": round(statistics.median(
                row["duration_seconds"] for row in scored), 3) if scored else None,
        }
    pair_ratios = []
    for repetition in range(1, repetitions + 1):
        for case in cases:
            pair = {
                row["variant"]: row for row in results
                if row["repetition"] == repetition and row["id"] == case["id"]
            }
            if set(pair) == {"A", "B"} and pair["A"]["duration_seconds"] > 0:
                pair_ratios.append(pair["B"]["duration_seconds"] / pair["A"]["duration_seconds"])
    expected_per_variant = len(cases) * repetitions
    both_complete = all(
        summaries[variant]["scored"] == expected_per_variant
        and summaries[variant]["parsed"] == expected_per_variant
        for variant in ("A", "B"))
    median_ratio = statistics.median(pair_ratios) if len(pair_ratios) == expected_per_variant else None
    passed = bool(
        eligible_provenance and both_complete
        and summaries["B"]["correct"] / expected_per_variant >= 0.90
        and summaries["B"]["protected_misroutes"] == 0
        and median_ratio is not None and median_ratio <= 1.10)
    scorecard = {
        "run_id": run_id,
        "frozen_sha": provenance["frozen_sha"],
        "status": "complete" if len(results) == len(schedule) else "partial",
        "repetitions": repetitions,
        "variant_summaries": summaries,
        "pair_count": len(pair_ratios),
        "median_case_paired_B_over_A_time": round(median_ratio, 4) if median_ratio else None,
        "both_fully_scored_and_parseable": both_complete,
        "provenance_eligible": eligible_provenance,
        "passed": passed,
        "results": results,
    }
    manifest["status"] = scorecard["status"]
    write_json(run_dir / "manifest.json", manifest)
    write_json(run_dir / "scorecard.json", scorecard)
    return scorecard


def _fair_variant_summary(rows: list[dict]) -> dict:
    scored = [row for row in rows if not row["unscored_reason"]]
    protected = [row for row in scored if row["protected"]]
    durations = [row["duration_seconds"] for row in scored]
    return {
        "executed": len(rows),
        "scored": len(scored),
        "unscored": len(rows) - len(scored),
        "native_parsed": sum(row["native_parsed_receipt"] is not None for row in scored),
        "semantic_target_correct": sum(row["semantic"]["target_correct"] for row in scored),
        "semantic_exact_route_correct": sum(
            row["semantic"]["exact_route_correct"] for row in scored),
        "protected_scored": len(protected),
        "protected_target_correct": sum(
            row["semantic"]["target_correct"] for row in protected),
        "protected_exact_route_correct": sum(
            row["semantic"]["exact_route_correct"] for row in protected),
        "protected_unresolved": sum(
            row["semantic"]["protected_unresolved"] for row in protected),
        "protected_ambiguous": sum(
            row["semantic"]["protected_ambiguous"] for row in protected),
        "protected_misroutes": sum(
            row["semantic"]["protected_misroute"] for row in protected),
        "median_seconds": statistics.median(durations) if durations else None,
    }


def _finalize_fair_run(run_dir: Path, preregistration: dict, cases: list[dict],
                       provenance: dict, manifest: dict, start_fingerprint: dict,
                       end_fingerprint: dict, results: list[dict],
                       terminal_error: str = "") -> dict:
    design = preregistration["design"]
    runtime_equal = start_fingerprint == end_fingerprint
    eligible_provenance = fair_provenance_eligible(
        provenance, start_fingerprint, end_fingerprint)
    summaries = {
        variant: _fair_variant_summary(
            [row for row in results if row["variant"] == variant])
        for variant in ("A", "B")
    }
    pair_rows = []
    for repetition in range(1, design["repetitions"] + 1):
        for case in cases:
            pair = {
                row["variant"]: row for row in results
                if row["repetition"] == repetition and row["id"] == case["id"]
            }
            if (set(pair) == {"A", "B"}
                    and not pair["A"]["unscored_reason"]
                    and not pair["B"]["unscored_reason"]
                    and pair["A"]["duration_seconds"] > 0):
                pair_rows.append({
                    "repetition": repetition,
                    "case_id": case["id"],
                    "A_duration_seconds": pair["A"]["duration_seconds"],
                    "B_duration_seconds": pair["B"]["duration_seconds"],
                    "B_over_A": pair["B"]["duration_seconds"] / pair["A"]["duration_seconds"],
                })
    bootstrap = fair_bootstrap(
        [row["B_over_A"] for row in pair_rows], preregistration)
    complete_pairs = len(pair_rows) == design["calls_per_variant"]
    clean_completion = not terminal_error and len(results) == design["total_calls"]
    latency_valid = eligible_provenance and clean_completion and complete_pairs and runtime_equal
    speed_supported = bool(
        latency_valid and bootstrap["upper_95"] is not None and bootstrap["upper_95"] < 1.0)
    no_regression_supported = bool(
        latency_valid and bootstrap["upper_95"] is not None and bootstrap["upper_95"] < 1.1)
    a, b = summaries["A"], summaries["B"]
    gates = {
        "clean_completion_without_terminal_error": clean_completion,
        "provenance_eligible": eligible_provenance,
        "runtime_fingerprints_identical": runtime_equal,
        "A_scored_50_of_50": a["scored"] == 50,
        "B_scored_50_of_50": b["scored"] == 50,
        "B_native_parse_at_least_45_of_50": b["native_parsed"] >= 45,
        "B_semantic_target_at_least_45_and_not_below_A": (
            b["semantic_target_correct"] >= 45
            and b["semantic_target_correct"] >= a["semantic_target_correct"]),
        "B_semantic_exact_at_least_45_and_not_below_A": (
            b["semantic_exact_route_correct"] >= 45
            and b["semantic_exact_route_correct"] >= a["semantic_exact_route_correct"]),
        "B_protected_target_15_of_15": b["protected_target_correct"] == 15,
        "B_protected_exact_15_of_15": b["protected_exact_route_correct"] == 15,
        "B_protected_unresolved_zero": b["protected_unresolved"] == 0,
        "B_protected_ambiguous_zero": b["protected_ambiguous"] == 0,
        "B_protected_misroutes_zero": b["protected_misroutes"] == 0,
        "latency_no_regression_upper_below_1_1": no_regression_supported,
    }
    adopt_b = all(gates.values())
    failed_gates = [name for name, passed in gates.items() if not passed]
    supported_claims = []
    if no_regression_supported:
        supported_claims.append("paired latency no-regression: bootstrap upper bound < 1.1")
    if speed_supported:
        supported_claims.append("paired live speedup: bootstrap upper bound < 1.0")
    if adopt_b:
        supported_claims.append("adopt compact B on the frozen fair-baseline task set")
    unsupported_claims = ["live token reduction: exact per-call usage unavailable"]
    if not speed_supported:
        unsupported_claims.append("paired live speedup")
    if not no_regression_supported:
        unsupported_claims.append("paired latency no-regression")
    if not adopt_b:
        unsupported_claims.append("adopt compact B on the frozen fair-baseline task set")
    if not eligible_provenance:
        status = "ineligible"
    elif not clean_completion:
        status = "partial"
    else:
        status = "complete"
    scorecard = {
        "schema_version": 1,
        "run_id": manifest["run_id"],
        "experiment_id": preregistration["experiment_id"],
        "frozen_sha": provenance["frozen_sha"],
        "status": status,
        "terminal_error": terminal_error,
        "executed": len(results),
        "variant_summaries": summaries,
        "pair_count": len(pair_rows),
        "paired_ratios": pair_rows,
        "latency_bootstrap": bootstrap,
        "speed_claim_supported": speed_supported,
        "latency_no_regression_supported": no_regression_supported,
        "runtime_fingerprint_start": start_fingerprint,
        "runtime_fingerprint_end": end_fingerprint,
        "runtime_fingerprints_identical": runtime_equal,
        "provenance_eligible": eligible_provenance,
        "token_usage": manifest["token_usage"],
        "gates": gates,
        "failed_gates": failed_gates,
        "adopt_B": adopt_b,
        "passed": adopt_b,
        "supported_claims": supported_claims,
        "unsupported_claims": unsupported_claims,
        "results": results,
    }
    manifest.update(
        status=status, terminal_error=terminal_error, completed_calls=len(results),
        runtime_fingerprint_end=end_fingerprint,
        runtime_fingerprints_identical=runtime_equal,
        provenance_eligible=eligible_provenance)
    write_fair_json_atomic(run_dir / "scorecard.json", scorecard)
    write_fair_json_atomic(run_dir / "manifest.json", manifest)
    return scorecard


def run_fair_paired_live(run_id: str,
                         output_root: Path = DEFAULT_LIVE_ROOT) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", run_id) or run_id in {".", ".."}:
        raise ValueError(f"invalid fair live run_id: {run_id!r}")
    run_dir = (output_root.resolve() / run_id).resolve()
    if run_dir.parent != output_root.resolve():
        raise ValueError("fair live run directory escaped output root")
    preregistration = load_fair_preregistration()
    semantic_config = fair_semantic_config(preregistration)
    design = preregistration["design"]
    cases = load_cases()
    if len(cases) != design["cases"]:
        raise ValueError("fair live case count drifted")
    baseline, baseline_source = extract_baseline_contract()
    compact = extract_compact_contract()
    contracts = {"A": baseline, "B": compact}
    for variant in ("A", "B"):
        if fair_live_prompt(contracts[variant], cases[0]["task"], variant, preregistration) != live_prompt(
                contracts[variant], cases[0]["task"], variant):
            raise ValueError(f"fair prompt construction drifted for arm {variant}")
    schedule = build_fair_schedule(cases, design["repetitions"])
    if (len(schedule) != design["total_calls"]
            or sum(row["variant"] == "A" for row in schedule) != design["calls_per_variant"]
            or sum(row["variant"] == "B" for row in schedule) != design["calls_per_variant"]
            or sum(row["variant"] == "A" and row["position"] == 1 for row in schedule) != 25
            or sum(row["variant"] == "B" and row["position"] == 1 for row in schedule) != 25):
        raise ValueError("fair live schedule drifted")
    provenance = fair_input_provenance(preregistration)
    start_fingerprint = fair_runtime_fingerprint()
    executable = start_fingerprint.get("executable_path", "UNAVAILABLE")
    if executable == "UNAVAILABLE":
        executable = "hermes"
    run_dir.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "experiment_id": preregistration["experiment_id"],
        "status": "pre_registered_not_complete",
        "design": design,
        "preregistration_sha256": sha256_file(FAIR_PREREGISTRATION),
        "baseline_source": baseline_source,
        "contract_sha256": {
            variant: hashlib.sha256(contract.encode("utf-8")).hexdigest()
            for variant, contract in contracts.items()
        },
        "schedule": schedule,
        "decision_gates": preregistration["decision_gates"],
        "latency": preregistration["latency"],
        "runtime_fingerprint_start": start_fingerprint,
        "token_usage": {
            "status": "UNSCORED",
            "available": False,
            "reason": "Hermes one-shot exposes no exact per-call input/output token usage.",
        },
        **provenance,
    }
    write_fair_json_atomic(run_dir / "manifest.json", manifest)
    case_by_id = {case["id"]: case for case in cases}
    results = []
    timeout = int(design["timeout_seconds_per_call"])
    if not fair_start_provenance_eligible(provenance, start_fingerprint):
        return _finalize_fair_run(
            run_dir, preregistration, cases, provenance, manifest,
            start_fingerprint, fair_runtime_fingerprint(), results,
            terminal_error="start_provenance_ineligible")
    try:
        for item in schedule:
            case = case_by_id[item["case_id"]]
            result, raw = execute_fair_live_case(
                case, contracts[item["variant"]], item["variant"], timeout,
                executable, preregistration, semantic_config)
            result.update(
                repetition=item["repetition"], case_index=item["case_index"],
                position=item["position"])
            raw.update(
                repetition=item["repetition"], case_index=item["case_index"],
                position=item["position"])
            filename = (
                f"R{item['repetition']:02d}_{case['id']}_{item['variant']}_P{item['position']}.json")
            write_fair_json_atomic(run_dir / "trials" / filename, raw)
            results.append(result)
    except BaseException as exc:
        terminal_error = f"{type(exc).__name__}:{exc}"
        try:
            _finalize_fair_run(
                run_dir, preregistration, cases, provenance, manifest,
                start_fingerprint, fair_runtime_fingerprint(), results,
                terminal_error=terminal_error)
        except Exception as finalize_exc:  # Preserve the original failure and pre-call manifest.
            if hasattr(exc, "add_note"):
                exc.add_note(f"fair evidence finalization failed: {finalize_exc}")
        raise
    return _finalize_fair_run(
        run_dir, preregistration, cases, provenance, manifest,
        start_fingerprint, fair_runtime_fingerprint(), results)


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
    parser.add_argument("--live-run-id")
    parser.add_argument("--live-timeout", type=int, default=180)
    parser.add_argument("--live-limit", type=int)
    parser.add_argument("--live-variant", choices=("A", "B"), default="B")
    parser.add_argument("--live-output-root", type=Path, default=DEFAULT_LIVE_ROOT)
    parser.add_argument("--live-paired-run-id")
    parser.add_argument("--live-fair-run-id")
    parser.add_argument("--live-repetitions", type=int)
    args = parser.parse_args(argv)
    if args.iterations < 1:
        parser.error("--iterations must be positive")
    if args.live_timeout < 1:
        parser.error("--live-timeout must be positive")
    if args.live_limit is not None and not 1 <= args.live_limit <= 10:
        parser.error("--live-limit must be between 1 and 10")
    if args.live_repetitions is not None and not 1 <= args.live_repetitions <= 5:
        parser.error("--live-repetitions must be between 1 and 5")
    selected_live_modes = sum(bool(value) for value in (
        args.live_run_id, args.live_paired_run_id, args.live_fair_run_id))
    if selected_live_modes > 1:
        parser.error("choose exactly one live run mode")
    if args.live_fair_run_id:
        preregistration = load_fair_preregistration()
        if args.live_timeout != preregistration["design"]["timeout_seconds_per_call"]:
            parser.error("fair live timeout is frozen by preregistration")
        if args.live_limit is not None or args.live_variant != "B":
            parser.error("fair live cases and arms are frozen by preregistration")
        if args.live_repetitions is not None:
            parser.error("fair live repetitions are frozen by preregistration")
        report = run_fair_paired_live(args.live_fair_run_id, args.live_output_root)
        print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else (
            f"fair live: A {report['variant_summaries']['A']['scored']} scored; "
            f"B {report['variant_summaries']['B']['scored']} scored; "
            f"pairs {report['pair_count']}; bootstrap upper "
            f"{report['latency_bootstrap']['upper_95']}; adopt_B {report['adopt_B']}"))
        return 0 if report["adopt_B"] else 1
    if args.live_paired_run_id:
        report = run_paired_live(
            args.live_paired_run_id, args.live_repetitions or 2,
            args.live_timeout, args.live_output_root)
        print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else (
            f"paired live: A {report['variant_summaries']['A']['scored']} scored; "
            f"B {report['variant_summaries']['B']['scored']} scored; "
            f"paired B/A {report['median_case_paired_B_over_A_time']}; "
            f"passed {report['passed']}"))
        return 0 if report["passed"] else 1
    if args.live_run_id:
        report = run_live(
            args.live_run_id, args.live_timeout, args.live_limit,
            args.live_output_root, args.live_variant)
        print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else (
            f"live: scored {report['scored']}/{report['executed']}; parsed {report['parsed']}; "
            f"correct {report['correct']}; protected misroutes {report['protected_misroutes']}; "
            f"median {report['median_seconds']}s; status {report['status']}; "
            f"full_pass {report['passed']}; partial_pass {report['partial_pass']}"))
        return 0 if report["passed"] or (report["status"] == "partial" and report["partial_pass"]) else 1
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
