#!/usr/bin/env python3
"""Tests for scripts/build_harness_graph.py (overlay 04 minimal KG export).

Pins: both frontmatter forms parse; depends_on resolves file-relative with
root-relative fallback (the repo's mixed convention) and counts the fallback;
broken refs exit 1; the graph only sees git-tracked files (gitignore respect);
impact queries compute the transitive reverse closure; --dry-run writes
nothing.

Dual-runnable:
    python scripts/test_build_harness_graph.py   (standalone, exit 0/1)
    python -m pytest scripts/test_build_harness_graph.py
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILDER = REPO_ROOT / "scripts" / "build_harness_graph.py"

_spec = importlib.util.spec_from_file_location("build_harness_graph", BUILDER)
bhg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bhg)


def make_repo(tmp):
    repo = Path(tmp)
    def g(*args):
        return subprocess.run(["git"] + list(args), cwd=str(repo),
                              capture_output=True, text=True, encoding="utf-8")
    g("init"); g("config", "user.email", "t@t"); g("config", "user.name", "t")
    (repo / "docs").mkdir()
    (repo / "core").mkdir()
    (repo / "core" / "base.md").write_text("---\nid: CORE-base\nlayer: core\n---\nx", encoding="utf-8")
    # file-relative depends_on
    (repo / "docs" / "a.md").write_text(
        "---\nid: DOC-a\nlayer: doc\ndepends_on:\n  - ../core/base.md\nused_by: [ROUTE-x]\n---\nx",
        encoding="utf-8")
    # root-relative depends_on (the repo's second convention)
    (repo / "docs" / "b.md").write_text(
        "---\nid: DOC-b\nlayer: doc\ndepends_on: [docs/a.md]\n---\nx", encoding="utf-8")
    # comment-form frontmatter (yaml)
    (repo / "c.yaml").write_text(
        "# ---\n# id: SCHEMA-c\n# layer: schema\n# depends_on: [docs/b.md]\n# ---\nkey: v\n",
        encoding="utf-8")
    # gitignored file with a broken ref - must NOT enter the graph
    (repo / ".gitignore").write_text("ignored/\n", encoding="utf-8")
    (repo / "ignored").mkdir()
    (repo / "ignored" / "z.md").write_text(
        "---\nid: DOC-z\ndepends_on: [nonexistent.md]\n---\nx", encoding="utf-8")
    (repo / "ROUTES.yaml").write_text(
        "routes:\n  - id: ROUTE-x\n    required:\n      - docs/a.md\n", encoding="utf-8")
    g("add", "-A"); g("commit", "-m", "seed")
    return repo


def run_builder(*argv, cwd=REPO_ROOT):
    return subprocess.run([sys.executable, str(BUILDER)] + list(argv),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", cwd=str(cwd), timeout=120)


def test_help_runs():
    proc = run_builder("--help")
    assert proc.returncode == 0 and "--impact" in proc.stdout


def test_fixture_graph_both_conventions_and_ignore():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        proc = run_builder("--target", str(repo), "--dry-run")
        assert proc.returncode == 0, proc.stderr
        g = json.loads(proc.stdout)
        paths = {n["path"] for n in g["nodes"]}
        assert "docs/a.md" in paths and "c.yaml" in paths
        assert "ignored/z.md" not in paths, "gitignored files must not enter the graph"
        assert g["broken_depends_on"] == []
        # docs/b.md's 'docs/a.md' needs the root-relative fallback; c.yaml sits
        # at repo root where both conventions coincide (counts as file-relative).
        assert g["root_relative_depends_on_count"] == 1, g["root_relative_depends_on_count"]
        dep_edges = [e for e in g["edges"] if e["edge_type"] == "depends_on"]
        assert {(e["source"], e["target"]) for e in dep_edges} == {
            ("docs/a.md", "core/base.md"), ("docs/b.md", "docs/a.md"), ("c.yaml", "docs/b.md")}
        route_edges = [e for e in g["edges"] if e["edge_type"] == "routes_to"]
        assert ("docs/a.md", "ROUTE-x") in {(e["source"], e["target"]) for e in route_edges}


def test_broken_depends_on_exits_nonzero():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        (repo / "docs" / "broken.md").write_text(
            "---\nid: DOC-broken\ndepends_on: [missing/file.md]\n---\nx", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=str(repo), capture_output=True)
        subprocess.run(["git", "commit", "-m", "add broken"], cwd=str(repo), capture_output=True)
        proc = run_builder("--target", str(repo), "--dry-run")
        assert proc.returncode == 1
        g = json.loads(proc.stdout)
        assert any("missing/file.md" in b for b in g["broken_depends_on"])


def test_impact_reverse_closure():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        proc = run_builder("--target", str(repo), "--dry-run",
                           "--impact", "core/base.md")
        g = json.loads(proc.stdout)
        imp = g["impact"]
        # a depends on base; b depends on a; c depends on b -> all transitively impacted.
        assert set(imp["impacted_files"]) == {"docs/a.md", "docs/b.md", "c.yaml"}, imp
        assert imp["impacted_routes"] == ["ROUTE-x"]


def test_all_four_frontmatter_conventions_parse():
    """Review finding (2026-07-06 overlay pair, blocking): bare '#' comment
    headers and plain top-level YAML were invisible - 12 real files."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        # Form 3: bare comment header, no '# ---' delimiters, multi-line inline list.
        (repo / "form3.yaml").write_text(
            "# id: OM-form3\n# layer: operating_model\n"
            "# depends_on: [docs/a.md,\n#   docs/b.md]\nrules: []\n", encoding="utf-8")
        # Form 4: plain top-level YAML keys.
        (repo / "form4.yaml").write_text(
            "id: RUBRIC-form4\nlayer: rubric\ndepends_on:\n  - docs/a.md\n"
            "criteria:\n  - id: X-1\n    rule: nested items must not leak\n", encoding="utf-8")
        # BOM-prefixed md frontmatter.
        (repo / "bom.md").write_text(
            "﻿---\nid: DOC-bom\nlayer: doc\ndepends_on: [docs/a.md]\n---\nx", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=str(repo), capture_output=True)
        subprocess.run(["git", "commit", "-m", "forms"], cwd=str(repo), capture_output=True)
        proc = run_builder("--target", str(repo), "--dry-run")
        assert proc.returncode == 0, proc.stderr
        g = json.loads(proc.stdout)
        by_path = {n["path"]: n for n in g["nodes"]}
        assert by_path["form3.yaml"]["id"] == "OM-form3"
        assert by_path["form4.yaml"]["id"] == "RUBRIC-form4"
        assert by_path["bom.md"]["id"] == "DOC-bom"
        deps = {(e["source"], e["target"]) for e in g["edges"] if e["edge_type"] == "depends_on"}
        assert ("form3.yaml", "docs/a.md") in deps and ("form3.yaml", "docs/b.md") in deps, \
            "multi-line inline list must keep all entries"
        assert ("form4.yaml", "docs/a.md") in deps
        assert ("bom.md", "docs/a.md") in deps
        assert not any(s == "form4.yaml" and t == "X-1" for s, t in deps), \
            "nested list items must not leak into depends_on"


def test_impact_fixpoint_beyond_depth_four():
    """Review finding (blocking): depth cap silently truncated real chains
    (repo max depth 7+). Closure must reach fixpoint."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        prev = "core/base.md"
        for i in range(6):  # chain depth 6 > old cap of 4
            name = f"docs/chain{i}.md"
            (repo / name).write_text(
                f"---\nid: DOC-chain{i}\ndepends_on: [{prev}]\n---\nx", encoding="utf-8")
            prev = name
        subprocess.run(["git", "add", "-A"], cwd=str(repo), capture_output=True)
        subprocess.run(["git", "commit", "-m", "chain"], cwd=str(repo), capture_output=True)
        proc = run_builder("--target", str(repo), "--dry-run", "--impact", "core/base.md")
        g = json.loads(proc.stdout)
        impacted = set(g["impact"]["impacted_files"])
        assert "docs/chain5.md" in impacted, f"deep chain end missing: {sorted(impacted)}"


def test_untracked_not_ignored_files_enter_graph():
    """Review finding (should-fix): plain `git ls-files` dropped new files;
    --others --exclude-standard includes them while still honoring .gitignore."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        (repo / "docs" / "new_untracked.md").write_text(
            "---\nid: DOC-new\ndepends_on: [docs/a.md]\n---\nx", encoding="utf-8")
        proc = run_builder("--target", str(repo), "--dry-run")
        g = json.loads(proc.stdout)
        paths = {n["path"] for n in g["nodes"]}
        assert "docs/new_untracked.md" in paths
        assert "ignored/z.md" not in paths, ".gitignore must still be honored"


def test_dry_run_writes_nothing():
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(tmp)
        run_builder("--target", str(repo), "--dry-run")
        assert not (repo / "reports").exists(), "--dry-run must not create reports/"


def test_real_repo_builds_clean():
    proc = run_builder("--dry-run")
    assert proc.returncode == 0, "the real repo graph must have zero broken depends_on"
    g = json.loads(proc.stdout)
    assert g["node_count"] > 100
    assert g["stale_edge_count"] == 0
    assert g["broken_depends_on"] == []


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
        except Exception as exc:  # noqa: BLE001
            print("FAIL {} (error): {!r}".format(fn.__name__, exc))
            failed += 1
    print("{} passed, {} failed".format(passed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
