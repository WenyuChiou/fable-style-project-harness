---
id: EXAMPLE-good-pr-review
layer: example
purpose: Golden example of a pre-commit code review — findings table with evidence, independent re-verification, verdict that gates the commit, and grader-benefit separation.
read_when: You are reviewing a diff before commit, or acting as an adversarial reviewer on another agent's output.
depends_on:
  - ../../rubrics
  - ../../playbooks
used_by:
  - ROUTE-pr-review
tags: [code-review, findings-table, request-changes, re-verification, golden]
retrieval_keywords: [code review verdict, REQUEST_CHANGES, APPROVE, P1 finding, re-run tests, byte-for-byte, independent verification, review trigger, findings table]
source_artifact: git log of method-harness-compiler — review trailers on commits 91b982b (M2b), 9532648 (M1c), f8740f8 (v0.6), f4c826f (Day 1)
synthetic: false
---

# Golden: PR / Diff Review (modeled on the recorded review verdicts)

Every substantive commit in the source repo carries `Co-Reviewed-By:` trailers recording
which reviewers ran, what they found, and how findings were resolved BEFORE the commit
landed. This example reconstructs the M2b review round (commit 91b982b) in the canonical
form, with structure notes.

## Review header

- **Range under review**: M2b builder-primitives diff (generators, registry adapters,
  fixture-regeneration gate; ~90 files).
- **Triggers fired**: #1 (>=50 LOC / >=3 files), #3 (file I/O + network-adjacent code),
  #4 (delegate subagents returned).
- **Reviewers**: two adversarial lenses with orthogonal charters —
  `gate-honesty` (are the published gate numbers real?) and `correctness`
  (does the code do what the doc claims?). Plus the mechanical code-review pass.

## Findings table

| # | Sev | Lens | Finding | Evidence (how verified) | Resolution |
|---|-----|------|---------|--------------------------|------------|
| 1 | P1 | correctness | `recommend-tools` writes output WITHOUT the shared overwrite guard — a re-run silently clobbers a hand-vetted file | Reproduced: ran the command twice against a fixture package; second run overwrote without `--force` | FIXED before commit: routed through shared `write_generated` guard + `--force` flag + regression tests. Verdict flipped REQUEST_CHANGES → APPROVE on re-review |
| 2 | — | gate-honesty | Gate report claims capability link_recall 0.69 / 0.88 / 0.50 across the three shipped packages | **Hand re-derived the package numbers independently; they reproduce byte-for-byte** | APPROVE — numbers pinned as regression floors in `tests/test_generator_gate.py` |
| 3 | P2 | gate-honesty | Grader agreement reported as 0/1 for one package — looks bad | Checked: the 0/1 is an honest manual-grader divergence, reported not gamed; the stronger property (no generated key CONFLICTS with a shipped one) holds 3/3 | ACCEPT AS-IS — do not tune the number; the miss is named in the comparison doc |

## What the reviewers actually did (not just read)

- Re-ran the generator against all three shipped packages and diffed outputs against the
  committed fixtures.
- Hand re-derived the recall/agreement numbers from raw package files — no trust in the
  report's arithmetic.
- Grepped for other write paths that bypass the overwrite guard (found none besides the
  P1).
- Confirmed the e2e tests monkeypatch HTTP **to RAISE**, so CI can never silently hit
  the network.

## Verdict

**REQUEST_CHANGES → (fix applied) → APPROVE.** The P1 fix landed IN this commit with its
regression tests; the verdict, the trigger numbers, and both reviewer outcomes were
recorded in the commit message trailer:

> Co-Reviewed-By: gate-honesty reviewer APPROVE (hand re-derived package numbers
> reproduce byte-for-byte); correctness reviewer REQUEST_CHANGES -> P1 overwrite-guard
> fixed; code-review skill APPROVE (triggers 1, 3, 4)

## Companion patterns observed in other recorded reviews

- **Grader-benefit separation** (commit f8740f8): a grader whose loosening would flip a
  FAIL to PASS in the same change was **deliberately not loosened**; grader fixes land in
  a separate change from the transcripts they affect.
- **Adversarial iteration inside one round** (commit 9532648): reviewer found a
  passive-voice evasion ("acceptance is recommended") that slipped past the verdict
  grader; the evasion was confirmed on disk and closed with a pinned evasion fixture.
- **Reviewer findings are re-verified, not blindly applied** (commit 490470d): two agents
  reported contradictory observations about a mermaid block; resolved by counting on disk
  (0/0/0 mermaid, 6/6/6 fences), not by trusting either agent.
- **Day-1 panel** (commit f4c826f): spec-compliance reviewer REQUEST_CHANGES → 4 P1s
  fixed + 3 regression tests added before the very first commit.

## Reuse checklist

- [ ] Name the triggers that made review mandatory.
- [ ] Orthogonal reviewer lenses; findings carry severity + evidence + resolution.
- [ ] Reviewers re-run / re-derive / re-grep — verification, not vibes.
- [ ] Fixes land with regression tests, in the same commit, before push.
- [ ] Honest-but-ugly numbers are kept and named, never tuned.
- [ ] Verdict + trigger + reviewer outcomes recorded in the commit trailer.
