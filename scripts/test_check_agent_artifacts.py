#!/usr/bin/env python3
"""Regression tests for check_agent_artifacts.py's parsers.

Pins two behaviors so a future refactor that silently breaks them fails loudly
instead of passing green: (1) the frontmatter depends_on block-list parser the
2026-07-03 depends_on extension relies on; (2) route_path_refs, whose extension
match must stay broad enough to catch a broken .jsonl/.json route reference (the
old md|yaml|py-only regex silently skipped memory/phase_history.jsonl). Pure-stdlib
asserts, no pytest / third-party dependency, mirroring the checker it guards.

Run:
    python scripts/test_check_agent_artifacts.py

Exit codes:
    0  all parser cases pass
    1  a regression (a case returned the wrong result)
"""
import importlib.util
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("chk", _here / "check_agent_artifacts.py")
chk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(chk)

# (name, frontmatter_text, expected parse_depends_on result)
CASES = [
    ("block list stops at used_by",
     "---\nid: X\ndepends_on:\n  - ../a/one.md\n  - ./two.yaml\nused_by:\n  - some-runtime\n---\nbody",
     ["../a/one.md", "./two.yaml"]),
    ("inline list fallback",
     "---\ndepends_on: [../a/one.md, ./two.yaml]\n---\n",
     ["../a/one.md", "./two.yaml"]),
    ("no frontmatter -> empty",
     "no frontmatter here\ndepends_on:\n  - x.md\n",
     []),
    ("no depends_on key -> empty",
     "---\nid: X\nused_by:\n  - r\n---\nbody",
     []),
    ("depends_on is last frontmatter key -> collects all",
     "---\nid: X\ndepends_on:\n  - ../a/one.md\n---\nbody",
     ["../a/one.md"]),
    ("empty depends_on then next key -> empty",
     "---\nid: X\ndepends_on:\nused_by:\n  - r\n---\n",
     []),
    ("unterminated frontmatter -> empty",
     "---\nid: X\ndepends_on:\n  - x.md\n",
     []),
    ("blank line inside block does not terminate it",
     "---\ndepends_on:\n  - ../a/one.md\n\n  - ./two.yaml\nused_by:\n  - r\n---\n",
     ["../a/one.md", "./two.yaml"]),
]

# (name, ROUTES.yaml snippet, expected route_path_refs) — pins the broadened
# extension match: a .jsonl path MUST be captured (the exact false-negative the
# old md|yaml|py regex produced), while quoted self_check items and # comments
# must NOT be matched (no false positives that would trip on non-paths).
ROUTE_PATH_CASES = [
    ("captures .jsonl (the extension the old md|yaml|py regex missed)",
     "    required:\n      - memory/phase_history.jsonl\n      - docs/x.md\n",
     ["docs/x.md", "memory/phase_history.jsonl"]),
    ("captures md/yaml/py; ignores quoted self_check items and # comments",
     "  self_check:\n    - \"cite DR-004 not a.file\"\n  # used_by: foo.md\n"
     "    start:\n      - core/GLOBAL_BOOTSTRAP.md\n    required:\n      - a/b.yaml\n      - c/d.py\n",
     ["a/b.yaml", "c/d.py", "core/GLOBAL_BOOTSTRAP.md"]),
    ("prose expected_output with a period -> no path-like items",
     "  expected_output: >-\n    a sentence with a period. no list items here\n",
     []),
]


def main():
    failures = 0

    for name, text, expected in CASES:
        got = chk.parse_depends_on(text)
        if got != expected:
            failures += 1
            print("FAIL parse_depends_on [{}]: expected {} got {}".format(name, expected, got))
        else:
            print("ok   parse_depends_on [{}]".format(name))

    # unresolved_depends_on flags only the non-existent path, not the real one
    # (proves it is not a blanket "any depends_on present" trip-wire).
    mixed = ("---\ndepends_on:\n  - ./NOPE_does_not_exist.md\n"
             "  - ../operating_model/decision_rules.yaml\n---\n")
    broken = chk.unresolved_depends_on("docs/agent-routing-policy.md", mixed)
    if broken != ["./NOPE_does_not_exist.md"]:
        failures += 1
        print("FAIL unresolved_depends_on mixed: expected ['./NOPE_does_not_exist.md'] got {}".format(broken))
    else:
        print("ok   unresolved_depends_on flags only the broken path")

    # A real overlay file's declared deps all resolve -> zero unresolved.
    real_rel = "docs/agent-optimization-runbook.md"
    real = (_here.parent / real_rel).read_text(encoding="utf-8")
    real_broken = chk.unresolved_depends_on(real_rel, real)
    if real_broken != []:
        failures += 1
        print("FAIL unresolved_depends_on on real file: expected [] got {}".format(real_broken))
    else:
        print("ok   unresolved_depends_on clean on a real overlay file")

    for name, text, expected in ROUTE_PATH_CASES:
        got = chk.route_path_refs(text)
        if got != expected:
            failures += 1
            print("FAIL route_path_refs [{}]: expected {} got {}".format(name, expected, got))
        else:
            print("ok   route_path_refs [{}]".format(name))

    # Live coverage: the real ROUTES.yaml's .jsonl route path is now captured
    # (regression guard for issue #2 of the 2026-07-03 review).
    routes_text = (_here.parent / "ROUTES.yaml").read_text(encoding="utf-8")
    if "memory/phase_history.jsonl" not in chk.route_path_refs(routes_text):
        failures += 1
        print("FAIL route_path_refs misses memory/phase_history.jsonl on real ROUTES.yaml")
    else:
        print("ok   route_path_refs captures the real .jsonl route path")

    # And the real file has zero broken route paths (matches check_route_paths()).
    if chk.check_route_paths() != []:
        failures += 1
        print("FAIL check_route_paths reports broken paths on real ROUTES.yaml")
    else:
        print("ok   check_route_paths clean on real ROUTES.yaml")

    total = len(CASES) + 2 + len(ROUTE_PATH_CASES) + 2
    print("{} passed, {} failed".format(total - failures, failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
