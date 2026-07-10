#!/usr/bin/env python3
"""Tier-0 presence + keyword + depends_on check for the agent-binding overlay.

This validator confirms that the concrete agent-binding overlay authored on top of
this harness (a) exists on disk, (b) contains its load-bearing keywords, and (c) has
every ``depends_on:`` frontmatter path resolving to a real file. It is a deterministic,
offline, standard-library-only check (no network, no LLM, no third-party imports) so it
can run in CI or a pre-commit gate as the cheapest layer of the author-agnostic review
gate (operating_model/review_protocol.md). It enforces DR-011 no-silent-pass and DR-021
verify-agent-observations-on-disk: a claim that these files are wired up correctly is
only true if they read back with their required substrings AND every declared dependency
exists on disk.

For each of the 8 markdown overlay artifacts it checks:
    1. the file exists and is readable;
    2. it contains (case-insensitively) every required substring in REQUIRED;
    3. every path in its ``depends_on:`` frontmatter list resolves on disk, relative to
       the file's own directory.

Run:
    python scripts/check_agent_artifacts.py

Exit codes:
    0  all artifacts present, every keyword found, every depends_on path resolves
    1  any artifact missing/unreadable, any keyword missing, or any depends_on broken
"""
import re
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


def read_text(rel_path):
    """Return the file's text, or None if it is missing/unreadable."""
    try:
        return (repo_root / rel_path).read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None


def missing_keywords(text, required_subs):
    """Return the required substrings (case-insensitive) absent from text."""
    low = text.lower()
    return [sub for sub in required_subs if sub.lower() not in low]


def parse_depends_on(text):
    """Extract the depends_on list from a `---`-delimited YAML frontmatter block.

    Pure string parsing (no yaml dependency, keeping this check standard-library
    only). Handles the block-list style used across this repo
    (``depends_on:`` then ``  - path`` lines) plus an inline ``[a, b]`` fallback.
    """
    if not text.startswith("---"):
        return []
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
    deps = []
    in_block = False
    for line in parts[1].splitlines():
        if not in_block:
            stripped = line.strip()
            if stripped == "depends_on:" or stripped.startswith("depends_on:"):
                after = stripped[len("depends_on:"):].strip()
                if after.startswith("["):  # inline list: depends_on: [a, b]
                    inner = after.strip("[]")
                    return [x.strip().strip("\"'") for x in inner.split(",") if x.strip()]
                in_block = True
            continue
        if re.match(r"^\s+-\s+", line):
            deps.append(re.sub(r"^\s+-\s+", "", line).strip().strip("\"'"))
        elif line.strip() == "":
            continue
        else:  # a new top-level key ends the depends_on block
            break
    return deps


def unresolved_depends_on(rel_path, text):
    """Return depends_on entries that do NOT resolve on disk (relative to the file)."""
    base = (repo_root / rel_path).parent
    return [dep for dep in parse_depends_on(text) if not (base / dep).resolve().exists()]


# Bare `- <path>.<ext>` list items (start/required/optional). Matches ANY file
# extension, not a hardcoded allowlist, so a broken .jsonl/.json/... route
# reference cannot slip past this drift check (quoted self_check items and `#`
# comments do not start with a bare word, so they are not matched).
_ROUTE_PATH_RE = re.compile(r"^\s+-\s+([\w./-]+\.[A-Za-z0-9]+)\s*$", re.MULTILINE)


def route_path_refs(text):
    """Return the sorted, de-duped path-like list items in a ROUTES.yaml text."""
    return sorted({m.group(1) for m in _ROUTE_PATH_RE.finditer(text)})


def check_route_paths():
    """Wiring-drift catch: every path-like list item in ROUTES.yaml resolves on disk."""
    text = read_text("ROUTES.yaml") or ""
    return sorted(p for p in route_path_refs(text) if not (repo_root / p).exists())


def main():
    # --quiet: suppress OK lines (success noise re-enters agent context on
    # every hook run); FAIL/MISSING lines and the summary print verbatim.
    quiet = "--quiet" in sys.argv[1:]
    total = len(REQUIRED)
    passed = 0
    for rel_path, required_subs in REQUIRED.items():
        text = read_text(rel_path)
        if text is None:
            print("MISSING FILE {}".format(rel_path))
            continue
        missing = missing_keywords(text, required_subs)
        broken = unresolved_depends_on(rel_path, text)
        if not missing and not broken:
            passed += 1
            if not quiet:
                print("OK {} ({} keywords, depends_on resolves)".format(rel_path, len(required_subs)))
            continue
        if missing:
            print("FAIL {}: missing keywords {}".format(rel_path, missing))
        if broken:
            print("FAIL {}: unresolved depends_on {}".format(rel_path, broken))
    print("{}/{} artifacts OK".format(passed, total))

    # Lightweight wiring-drift + protocol coverage (added 2026-07-03).
    broken_routes = check_route_paths()
    proto = "docs/ab_skill_effect_protocol.md"
    proto_ok = (repo_root / proto).exists()
    if broken_routes:
        print("FAIL ROUTES.yaml references missing paths: {}".format(broken_routes))
    elif not quiet:
        print("OK ROUTES.yaml path references all resolve")
    if not proto_ok:
        print("MISSING FILE " + proto)
    elif not quiet:
        print("OK " + proto)

    return 0 if (passed == total and not broken_routes and proto_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
