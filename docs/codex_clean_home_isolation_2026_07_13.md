---
id: DOC-codex-clean-home-isolation-2026-07-13
layer: doc
purpose: Commit-bound evidence for Codex per-trial runtime isolation, cleanup, and scored-run recovery
read_when: Checking whether Codex benchmark trials still inherit operator MCP, plugin, or user configuration state
depends_on:
  - ../scripts/run_long_codex_ab.py
  - ../scripts/test_run_long_codex_ab.py
  - ./codex_long_task_ab.md
  - ./evidence.md
used_by: [DOC-evidence, operator-session]
tags: [codex, isolation, benchmark, evidence, cleanup]
retrieval_keywords: [Codex clean home, CODEX_HOME isolation, operator config contamination, scored trial recovery]
---

# Codex Clean-Home Isolation Regression

Status: deterministic isolation gate complete plus one commit-bound live smoke.
This is not a multi-trial reliability or speed comparison.

## Why this change was needed

The 2026-07-10 long-task run executed 80 trials, but 33 were unscored after
operator-level MCP authentication and plugin-cache failures entered every arm.
The same operator-environment failure class appeared in every arm, with
unscored counts A/B/C/D = 7/9/7/10. The randomized schedule supports treating
it as arm-independent infrastructure contamination, but the counts were not
equal and this isolation regression does not revalidate the earlier efficiency
ordering. The failures consumed time and tokens without measuring the task.

The previous runner inherited the operator `CODEX_HOME`. Commit `e950be8`
changed each trial to use a fresh home containing only `auth.json`, with user
config and rules ignored, session persistence disabled, and the execution
policy declared on the command line. Commit `7f3d702` added the frozen
contamination and five-trial leakage gates.

## Unknown unknown found during live validation

Removing operator config also removed the Windows runtime setting that made
workspace writes available. The first isolated smoke was read-only. Adding
`approval_policy=never` alone did not fix it; the second smoke was also
read-only. The passing contract required both `sandbox=workspace-write` and an
explicit `windows.sandbox=elevated` override. The runner uses
`--strict-config`, so an incompatible future Codex CLI rejects the contract
instead of silently changing it.

Independent review then found additional non-happy paths before commit:

- path traversal could move the temporary credential home outside work root;
- a partial auth copy could leave credential material behind;
- Windows timeout termination contained an unbounded follow-up wait;
- a repeated timeout could return byte output and crash diagnostic rendering.

All four paths now have behavioral regression tests.

## Deterministic gates

Re-run: `python scripts/test_run_long_codex_ab.py`.

Result after `7f3d702`: 27/27 pass. Isolation-specific assertions establish:

| Gate | Result |
|---|---|
| Invalid inherited `config.toml` fails the A fixture parser | PASS |
| B copies `auth.json` but no config, plugins, or `AGENTS.md` | PASS |
| Exact CLI vector and isolated `CODEX_HOME` | PASS |
| Auth continuity through the isolated process environment | PASS |
| Cross-trial home or marker leakage | 0/5 |
| Home cleanup after normal completion and timeout | PASS |
| Partial-copy and cleanup-failure diagnostics | PASS |
| Path-traversing run ID rejected before credential copy | PASS |
| Three repeated timeouts with byte output return bounded diagnostics | PASS |

Repository integration remained 53/53.

## Commit-bound live smoke

Raw local run:
`evals/long_codex_ab/codex_clean_home_committed_20260713/` (gitignored).

The manifest binds the run to both Git and runner bytes:

| Field | Value |
|---|---|
| `frozen_sha` | `e950be89266230621fb9192c2f96c2ffd302b1ee` |
| `runner_tracked_at_frozen_sha` | `true` |
| `runner_content_sha256` | `4383d0b03274040ff722db15513bf4d02f9bb9b0d70ed1f79d883f61f61a2fc2` |
| Executed / scored / unscored | 1 / 1 / 0 |
| Primary pass | 1 |
| False done | 0 |
| Canonical evidence checked | 1 |
| Codex home removed | true |
| Exit code | 0 |
| Input / output tokens | 90,427 / 838 |
| Tool calls / wall time | 5 / 69.07 seconds |

The tracked runner hash was recomputed after the run and matched the manifest.

## Supported claim and limit

The shipped runner prevents the tested operator-config contamination class,
preserves authentication, cleans five sequential trial homes without leakage,
and produced one scored live Codex trial from the committed implementation.
This is an engineering reliability improvement over the inherited-home runner.

It does **not** prove that the earlier 41% unscored rate is eliminated, nor a
token, latency, correctness, concurrent-execution, or cross-platform lift. A
multi-trial rerun is required before making any of those claims.
