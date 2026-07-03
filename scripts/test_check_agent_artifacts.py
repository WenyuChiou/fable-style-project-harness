#!/usr/bin/env python3
"""Regression tests for check_agent_artifacts.py's frontmatter depends_on parser.

Pins the parser behavior the 2026-07-03 depends_on extension relies on, so a future
refactor that silently breaks block-list parsing (and thus quietly stops checking
depends_on resolution) fails loudly instead of passing green. Pure-stdlib asserts,
no pytest / third-party dependency, mirroring the checker it guards.

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

    total = len(CASES) + 2
    print("{} passed, {} failed".format(total - failures, failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
