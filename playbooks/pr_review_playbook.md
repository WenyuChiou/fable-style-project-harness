---
id: PLAYBOOK-pr-review
layer: playbook
purpose: The layered review protocol as a PR/commit checklist — orthogonal adversarial lenses, independent re-verification by re-running, regression-tests-with-contract-changes, explicit-path staging, and traceable commit trailers.
read_when: Reviewing any diff/PR/commit, or preparing a change for review; before EVERY commit that ships work.
depends_on:
  - ./phase6_evaluation_runner.md
used_by:
  - ROUTE-pr-review
tags: [review, adversarial-reviewers, re-verification, commit-trailers, staging-discipline, regression-tests]
retrieval_keywords: [code review gate, orthogonal lenses, REQUEST_CHANGES, re-derive numbers, grep old value, explicit path staging, Co-Reviewed-By, Executed-By trailer, regression net ships with contract change, P1 fixed before merge]
---

# PR review playbook — the layered review protocol

**Status: REAL — applied on every substantive commit in the repo.** Evidence: every feature commit body carries `Executed-By:` / `Co-Reviewed-By:` / `Co-Authored-By:` trailers naming the reviewers, their verdicts, and what they independently re-verified (see commits `046d0e3`, `bd32614`, `f8740f8`, `9532648`, `e7f0fc6`, `d7603e3`, `7134227`, `510b79f`, `91b982b`).

## Goal

No change ships on the author's word. Every substantive diff passes through layered review: (1) adversarial reviewers with ORTHOGONAL lenses, (2) independent re-verification by re-running scripts/tests/greps/fetches — not by re-reading prose, (3) a code-review gate with an explicit verdict, (4) disciplined staging and a commit message that makes the whole chain auditable later.

## Allowed work

- **Assign 2+ adversarial reviewers with non-overlapping lenses**, matched to the change's risk axis. Observed pairings: plan-compliance + honesty/safety (M1a); N=2-gate audit + evidence/safety (M1b); v0.6-consistency + transcript-authenticity (v0.6); correctness + audit-fairness (CLI/audit); gate-honesty + correctness (M2b); research-integrity (M2a); pre-registration honesty (pilot); fresh-eyes usability + consistency (hardening). Apparent verdict conflict between lenses is usually partition, not contradiction.
- **Independent re-verification, by re-running**: reviewers re-derive rather than trust. Observed forms: "hand re-derived package numbers reproduce byte-for-byte"; "independent old-value grep + byte-identical scorecard re-runs"; "12 claims re-verified live against cited URLs"; "5 URLs live-checked"; "schemas byte-identical to <commit> independently verified"; anti-convenience verification of transcript authenticity; cross-agent observation conflicts "resolved by on-disk verification" (count the artifacts yourself).
- **Verdict gate**: APPROVE → merge; REQUEST_CHANGES → fix the P0/P1s BEFORE merge, in the same round (observed: passive-voice evasion fixture, overwrite-guard P1, transcript-FAILs-into-major_failures P1, "1 P0 + 3 P1 fixed by public correction, not concealment"). NEVER merge-then-fix.
- **Regression tests ship WITH contract changes** in the same commit ("regression net ships with the contract change" — suite growth is reported per commit: 114→135→150→172→299→335→369→392→555→629→730). Renames get mutation tests ("reverting any rename fails the suite").
- **Explicit-path staged commits with count assertions**: stage named paths and assert the staged file count ("Explicit-path staging (6 files asserted)"); when parallel work is in flight, state what is deliberately excluded ("M2a research workflow is concurrently in flight on disjoint files and is excluded from this commit").
- **Commit trailers as the audit trail**: `Executed-By:` (who/what built it), `Co-Reviewed-By:` (each reviewer, lens, verdict, and what was re-verified; REQUEST_CHANGES outcomes recorded, e.g. "correctness REQUEST_CHANGES -> P1 overwrite-guard fixed"), human-gate notes where a human intervened ("Human-gate: zh-TW 語感 review — one full-width punctuation fix").

## Forbidden work

- Single-lens review of a multi-risk change; two reviewers with the same lens.
- Accepting a number, claim, or "verified" flag without a re-derivation path.
- Loosening a grader/gate/test in the change that benefits from it — that fix lands separately (see `./phase6_evaluation_runner.md`).
- `git add .`-style staging; committing files a concurrent workstream owns.
- Concealing a reviewer finding: corrections are published (top-of-file correction notices), findings are named in the trailer, FAILs are wired into the artifacts.
- Skipping review because the change "is small" — reviewers found P1s in rounds the author considered done (the transcript-FAILs P1, the overwrite-guard P1, the passive-verdict gameability P1).

## Required outputs

1. Reviewer assignments with declared lenses (orthogonal by construction).
2. Per-reviewer verdict + the specific artifacts they re-derived/re-ran.
3. Fixes for all P0/P1 findings landed pre-merge.
4. Regression tests covering every contract change in the same diff.
5. A commit message whose body records: what shipped, honest limitations, suite delta, staging discipline, and the full trailer block.

## Acceptance criteria

- A later reader can reconstruct from the commit body alone: who built it, who reviewed with what lens, what was independently re-verified, what was found, and how findings were resolved.
- Every load-bearing number in the diff has been reproduced by someone other than its author (script re-run, grep, live fetch, or byte-comparison).
- The suite passes at a HIGHER count than before for contract changes.
- Nothing merged with an open REQUEST_CHANGES.

## Common failure modes

- **Endorsement stacking**: N reviewers all reading for the same thing; one bug-finder P0 outweighs N approvals. Prevention: assign lenses explicitly.
- **Review by prose-reading**: a reviewer who doesn't re-run finds only style. The protocol's wins (byte-identical re-runs, live URL checks) all came from re-execution.
- **Convenient verification**: checking only evidence that supports the author. The transcript-authenticity review is explicitly "anti-convenience".
- **Fix-forward promises**: merging with a known P1 "to fix later" — observed practice is same-round fixes, every time.
- **Trailer rot**: omitting the REQUEST_CHANGES history makes the review look cleaner than it was; record verdict TRAJECTORIES, not just final states.

## Self-check checklist

- [ ] Do my reviewers cover orthogonal lenses matched to this change's risks?
- [ ] Has every load-bearing number/claim been independently re-derived by re-running something?
- [ ] Are all P0/P1 findings fixed in this round, with regression tests?
- [ ] Do regression tests ship in the SAME commit as the contract change?
- [ ] Is staging explicit-path with an asserted file count, excluding concurrent work?
- [ ] Does the commit body carry Executed-By / Co-Reviewed-By (with lenses, verdicts, and re-verifications)?
