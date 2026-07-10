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

    # --quiet no-swallow invariant (2026-07-09, validator_verbose_vs_quiet):
    # quiet mode must NEVER suppress a FAIL/MISSING/POSTURE line or change an
    # exit code — a swallowed failure silently disables the commit gate. Each
    # case seeds a real violation into the tree, runs BOTH modes via
    # subprocess, asserts exit parity + byte-identical failure lines, and
    # restores the file in a finally block. Covers the posture-conflict path
    # (check_posture's distinct print branch) that the executed A/B's seed
    # set missed.
    import re
    import subprocess

    def _run(script, quiet):
        args = [sys.executable, str(_here / script)] + (["--quiet"] if quiet else [])
        r = subprocess.run(args, capture_output=True, text=True,
                           encoding="utf-8", cwd=str(_here.parent))
        return r.returncode, sorted(
            l for l in (r.stdout or "").splitlines()
            if l.startswith(("FAIL", "MISSING", "POSTURE")))

    def quiet_parity(name, script, rel_path, mutate):
        nonlocal failures
        p = _here.parent / rel_path
        orig = p.read_text(encoding="utf-8")
        try:
            p.write_text(mutate(orig), encoding="utf-8")
            cv, fv = _run(script, False)
            cq, fq = _run(script, True)
            ok = cv == cq == 1 and fv == fq and len(fv) > 0
            if not ok:
                failures += 1
                print("FAIL quiet-parity [{}]: verbose exit {} fails {} | quiet exit {} fails {}".format(
                    name, cv, len(fv), cq, len(fq)))
            else:
                print("ok   quiet-parity [{}] ({} failure line(s) identical in both modes)".format(
                    name, len(fv)))
        finally:
            p.write_text(orig, encoding="utf-8")

    quiet_parity("keyword removed (case-insensitive)", "check_agent_artifacts.py",
                 "docs/agent-routing-policy.md",
                 lambda t: re.sub("hermes", "h_e_r_m_e_s", t, flags=re.I))
    quiet_parity("broken depends_on", "check_agent_artifacts.py",
                 "docs/completion-honesty-gate.md",
                 lambda t: t.replace("depends_on:", "depends_on:\n  - ./NO_SUCH_FILE.md", 1))
    quiet_parity("posture conflict (check_posture print path)", "check_adaptive_harness.py",
                 "docs/codex-delegation-policy.md",
                 lambda t: t + "\n<!-- seeded: this repo stays private -->\n")

    # Clean tree: both modes exit 0, quiet emits zero failure lines.
    for script in ("check_agent_artifacts.py", "check_adaptive_harness.py"):
        cv, fv = _run(script, False)
        cq, fq = _run(script, True)
        if not (cv == cq == 0 and fv == fq == []):
            failures += 1
            print("FAIL quiet-clean [{}]: verbose exit {} quiet exit {}".format(script, cv, cq))
        else:
            print("ok   quiet-clean [{}] (both modes exit 0, no failure lines)".format(script))

    total = len(CASES) + 2 + len(ROUTE_PATH_CASES) + 2 + 3 + 2
    print("{} passed, {} failed".format(total - failures, failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
