---
id: EXPECT-T01
layer: validation
purpose: Reference answer for T01_phase0_review - the violations that must be
  caught and the acceptable rubric-score range.
read_when: Grading a model's answer to T01, never before attempting it.
depends_on:
  - ../regression_tasks/T01_phase0_review.md
  - ../../rubrics/architecture_review_rubric.yaml
used_by:
  - ROUTE-phase-review
tags: [expected-output, grading-key]
retrieval_keywords: [T01 expected, phase review answer key]
---

# T01 expected output

## Required verdict

**NO_GO.** ARCH-1 and ARCH-2 score 1, which triggers NO_GO mechanically. An
answer of CONDITIONAL_GO is acceptable ONLY if it converts every violation
below into an explicit, falsifiable condition; GO is a fail.

## Violations that MUST be caught (all five)

| # | Plan item | Violation | Principle |
|---|---|---|---|
| 1 | P0-2 (scorecard "based on authoring review", runner in Phase 4, exporters Phase 5) | Self-assigned scorecard numbers nothing computed = the silent-pass fabrication pattern; proof (runner, installability) deferred to the end - the inverted phase order | ARCH-1; computed-not-claimed (design review C1/C2 pattern) |
| 2 | P0-4 (automation "starting immediately", standard "will have been proven by the demo") | Automation before any falsifiable gate; N=1 proves nothing about generality - a second package authored against frozen schemas (the N=2 zero-schema-edit gate) is the minimum evidence | ARCH-2 (design review B3 pattern) |
| 3 | P0-5 ("the team agrees it is high quality") | Success criterion is unfalsifiable; nothing could fail it | ARCH-2 |
| 4 | P0-1 (46 mandatory files, all required from day one, at N=1) | Surface priced for adoption failure; no conformance levels; compiler intermediates mandatory for humans | ARCH-3 (design review C7/B4 pattern) |
| 5 | P0-3 (verbatim quotes from a third-party compilation tagged `direct_quote`) | Attribution-cap violation (third-party compilations never direct_quote; primary-source locator required) AND unaddressed redistribution/licensing exposure | ARCH-5 (design review C4/A1 pattern) |

## Rubric score ranges (grading tolerance +/- 1 except where noted)

- ARCH-1: **1** (must be 1 - proof is last)
- ARCH-2: **1** (must be 1 - no falsifiable gate anywhere)
- ARCH-3: 1-2
- ARCH-4: 2-3 (the plan is silent on state separation; silence is scored
  low-neutral, and noting the silence is worth credit)
- ARCH-5: **1-2** (quote handling is an active violation, not just silence)
- ARCH-6: 1-3 (the plan prescribes no review lenses; an answer may score
  this low or mark it UNSCORED with a reason - both acceptable)

## Also required for full credit

- A keep-list: schemas/standard-first sequencing and the demo-as-fixture
  idea are salvageable; the intent to define evals is right, only its
  execution timing is wrong.
- The failure path: "revise the standard, don't automate it" - the fix is
  reordering (installable demo + computed eval as Phase-0 exit criteria,
  gate before compiler work), not abandonment.
- Findings cite plan items (P0-x), not vibes.

## Automatic fails

- Verdict GO.
- Missing violation #1 or #2 (the two load-bearing gates).
- Inventing violations not present in the text (e.g., claiming the plan
  executes untrusted tools) - precision matters as much as recall.
