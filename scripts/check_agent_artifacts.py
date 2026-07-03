#!/usr/bin/env python3
"""Tier-0 presence + keyword check for the 8 markdown agent-binding overlay artifacts.

This validator confirms that the concrete agent-binding overlay authored on top of
this harness actually exists on disk and contains its load-bearing keywords. It is a
deterministic, offline, standard-library-only check (no network, no LLM) so it can run
in CI or a pre-commit gate as the cheapest layer of the author-agnostic review gate
(operating_model/review_protocol.md). It enforces DR-011 no-silent-pass and DR-021
verify-agent-observations-on-disk: a claim that these files were written is only true
if they read back with their required substrings.

For each of the 8 relative paths in REQUIRED it checks the file exists, is readable, and
(case-insensitively) contains every required substring, then prints a per-file status
line and a summary.

Run:
    python scripts/check_agent_artifacts.py

Exit codes:
    0  all 8 artifacts present and every required keyword found
    1  any artifact missing, unreadable, or missing a required keyword
"""
import sys
from pathlib import Path

# Repo root relative to this script (scripts/ -> repo root); runs from any cwd.
repo_root = Path(__file__).resolve().parent.parent

# Each overlay artifact -> case-insensitive substrings that MUST appear in it.
REQUIRED = {
    "docs/agent-routing-policy.md": [
        "Hermes", "Claude Code", "Codex", "Opus baseline", "Fable",
        "escalat", "anti-pattern", "delegate",
    ],
    "docs/completion-honesty-gate.md": [
        "I cannot honestly claim completion because", "exit code", "stderr",
        "timeout", "background job", "canonical", "derived report",
        "test", "file exist",
    ],
    "docs/agent-optimization-runbook.md": [
        "Telegram", "OAuth", "refactor", "benchmark", "release",
        "Hermes", "Codex",
    ],
    "prompts/hermes-router.md": [
        "classify", "route", "Claude Code", "Codex", "concise", "verify",
    ],
    "prompts/claude-code-debug.md": [
        "observed facts", "assumptions", "root cause",
        "verification commands", "alternative hypotheses", "recommended fix",
    ],
    "prompts/claude-code-orchestration.md": [
        "phases", "executor", "stop condition", "rollback",
        "verification gate", "commit boundar",
    ],
    "prompts/claude-code-completion-integrity.md": [
        "raw process", "artifact laundering", "premature",
        "background job", "canonical", "missing test",
    ],
    "prompts/codex-task-brief-template.md": [
        "Context", "Goal", "In scope", "Out of scope", "Files allowed",
        "Constraints", "Acceptance criteria", "Verification commands",
        "Output contract", "do not commit",
    ],
}


def check_file(rel_path, required_subs):
    """Return (status, missing_subs). status is 'OK', 'FAIL', or 'MISSING'."""
    path = repo_root / rel_path
    try:
        text = path.read_text(encoding="utf-8").lower()
    except (FileNotFoundError, OSError):
        return "MISSING", []
    missing = [sub for sub in required_subs if sub.lower() not in text]
    return ("OK" if not missing else "FAIL"), missing


def main():
    total = len(REQUIRED)
    passed = 0
    for rel_path, required_subs in REQUIRED.items():
        status, missing = check_file(rel_path, required_subs)
        if status == "OK":
            passed += 1
            print("OK {} ({} keywords)".format(rel_path, len(required_subs)))
        elif status == "MISSING":
            print("MISSING FILE {}".format(rel_path))
        else:
            print("FAIL {}: missing {}".format(rel_path, missing))
    print("{}/{} artifacts OK".format(passed, total))
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
