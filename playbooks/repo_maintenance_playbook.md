---
id: PLAYBOOK-repo-maintenance
layer: playbook
purpose: Procedure for keeping repo docs/status truthful over time — docs-accuracy sweeps, grep-old-value after renames, status-line sync, locale parity tests, CI-green discipline, honest re-marking of stale plan statuses.
read_when: After any rename, doc update, locale edit, status change, or when auditing the repo for drift between docs and reality.
depends_on:
  - ./pr_review_playbook.md
used_by:
  - ROUTE-repo-maintenance
tags: [maintenance, docs-drift, rename-sweep, locale-parity, status-sync, CI]
retrieval_keywords: [grep old value, zero leftover audit, locale parity tests, status line synced, stale doc drift, re-marked honestly, mirror sync, CI pipeline, gitattributes LF, test count sync]
---

# Repo maintenance playbook — docs stay true or the tests go red

**Status: REAL** — practiced across commits `4437320` (rename sweep), `1c4a77f` (locale-parity tests), `e7f0fc6`/`490470d` (status-line sync + asset hygiene), `510b79f` (recorded drift fixes), `7134227` (CI + honest README clause replacement).

## Goal

Prevent the slow rot where docs describe a repo that no longer exists. Mechanize truthfulness: renames end with zero-leftover greps, human-visible status lines are synced by tests, locale mirrors are parity-tested, plan statuses are re-marked honestly (including DOWNGRADES), and CI green is the shipping condition.

## Allowed work

- **Rename sweeps with zero-leftover audits**: partition the sweep across workers, then independently re-verify with a repo-wide grep for the OLD value plus a full test run (the project rename: "partitioned sweep + zero-leftover audit; independently re-verified (114/114 pytest, repo-wide grep)"; git renames verified detected at 96–99% similarity so history survives). The v0.6 field renames added the same discipline as review ("independent old-value grep") plus mutation tests so reverting any rename fails the suite.
- **Status-line synchronization**: human-facing status lines (test counts, package counts) must match reality across ALL locations; sync them in the same commit that changes the underlying number, and let a parity agent/test catch strays (real catch: "the parity agent … caught two stale 299 status lines"; "status lines synced 555").
- **Locale parity as regression tests, not vigilance**: mirrors (EN / zh-TW / zh-CN) keep commands, paths, numbers, and code-block counts byte-identical, with per-locale notices faithfully translated; codified in `tests/test_readme_locales.py` (22 tests at introduction, grown to 53). Locale edits are a mandatory-review category; cross-agent disagreement about a mirror is resolved by on-disk verification (counting fences), not by argument.
- **Docs-accuracy sweeps with honest re-marking**: when reality moved, fix the plan — including in the unflattering direction. Real instances (commit `510b79f`, "three recorded drift fixes"): N=2 gate wording made "consistent AND honest: blinded full-suite arm still open"; Phase 5 re-marked from not-started to PARTIAL because the path shipped de facto; stale locale notes resolved. A previously-true claim ("no CI") is REPLACED, not deleted, when it stops being true.
- **Prose trims that preserve facts**: the README trim cut 22% of prose with "every number and all 15 links verified surviving; only prose cut, zero facts dropped" — trimming requires a survival audit.
- **Repo hygiene invariants**: `.gitattributes` LF normalization (line-ending drift is a real cross-OS diff-noise source on Windows); asset-hygiene tests for embedded SVGs (XML-valid, script-free, size-bounded); private material (`agent_harness/`) gitignored so it can never ship.
- **CI as the floor**: matrix CI (ubuntu+windows × two Python versions) running the full suite plus conformance validation on every package; local green is necessary, CI green is the shipping condition; no CI badge claimed while none can be shown.

## Forbidden work

- Declaring a rename done without a repo-wide old-value grep and full test pass.
- Editing one locale of a mirrored file without the others (or without the parity tests passing).
- Leaving a plan status flattering-but-stale; "DONE" claims without file-path evidence.
- Deleting inconvenient history instead of re-marking it (friction inventories stay "historical and unchanged"; resolutions are appended, never rewritten into the record).
- Doc trims that silently drop numbers, links, or caveats.
- Committing maintenance changes mixed into unrelated feature commits without naming them.

## Required outputs

1. For renames: the sweep, the zero-leftover grep result, mutation tests pinning the new names, and history-preserving git mv.
2. For status changes: every affected status line updated in the same commit, with locale mirrors.
3. For doc sweeps: a recorded list of drift fixes in the commit body (what was stale, what it now says).
4. Parity/hygiene tests extended whenever a new mirrored or embedded artifact class appears.
5. CI configuration that exercises the real support matrix, and README claims that match what CI actually proves.

## Acceptance criteria

- `grep -r <old-value>` returns zero hits outside deliberately-preserved historical docs (which carry status notes instead of edits).
- All locale mirrors pass parity tests; all status lines agree with computed reality (test counts, package lists).
- Plan/docs statuses match the tree — verified by walking claims to file paths.
- CI green on the full matrix before any push that claims a working state.

## Common failure modes

- **The half-rename**: code renamed, docs/tests/schemas still carry the old name — why sweeps end with an independent grep, not a checklist.
- **Status-line drift**: test counts hardcoded in prose go stale the moment the suite grows; sync-by-test beats sync-by-memory.
- **Mirror decay**: one locale updated, two rot; parity tests turn vigilance into regression.
- **Flattering staleness**: plans that only get updated when the news is good; the observed norm re-marks in BOTH directions (a "not started" became PARTIAL; a "done"-sounding gate claim was narrowed to "one arm still open").
- **Historical revisionism**: editing old friction/finding text instead of appending resolutions — destroys the audit trail the standard depends on.

## Self-check checklist

- [ ] After a rename: repo-wide old-value grep clean? Full suite green? Mutation tests pinned?
- [ ] Are all status lines (counts, package lists) synced across every file and locale in this commit?
- [ ] Do locale mirrors pass parity tests?
- [ ] Did I re-mark any stale plan status I touched — including downgrades?
- [ ] Did any trim drop a number, link, or caveat? (Audit survival.)
- [ ] Is CI green on the full matrix, and do README claims match what CI proves?
