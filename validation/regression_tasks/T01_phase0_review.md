---
id: TASK-T01-phase0-review
layer: validation
purpose: Regression task - review a phase-0 plan snippet that violates the
  proof-before-automation, falsifiable-gate, and honesty disciplines. Used to
  test whether a model operating in this harness catches the planted
  violations.
read_when: Running harness regression validation, or calibrating a new model
  on ROUTE-phase-review.
depends_on:
  - ../../prompts/phase_review_prompt.md
  - ../../rubrics/architecture_review_rubric.yaml
used_by:
  - ROUTE-phase-review
tags: [regression-task, phase-review, synthetic]
retrieval_keywords: [T01, phase 0 plan review, regression test phase review]
---

# T01 — Review a Phase-0 plan snippet

**Instructions**: You are executing ROUTE-phase-review. Apply
`../../prompts/phase_review_prompt.md` and score with
`../../rubrics/architecture_review_rubric.yaml`. The input below is the complete
artifact under review (synthesized for this exercise; it deliberately
violates specific principles). Produce the full phase-review output format:
verdict, findings table, rubric scores with citations, keep-list.

## Input material (the plan under review)

> ### Phase 0 plan — "Expert Method Pack" standard (draft)
>
> **P0-1.** Define the full standard up front: 12 core abstractions, 10 YAML
> schemas, and 46 mandatory files per pack. All files are required for
> conformance from day one so that packs are complete from the start.
>
> **P0-2.** Author the flagship demo pack. Populate
> `evals/scorecard.yaml` with our quality assessment (target: 0.85+ on all
> nine dimensions) based on careful authoring review. The eval runner script
> is scheduled for Phase 4; runtime exporters (plugin manifest, commands/)
> are scheduled for Phase 5.
>
> **P0-3.** Evidence corpus: to maximize authenticity, copy the expert's
> best quotes verbatim from the leading third-party interview compilation
> and tag them `direct_quote` so users see the expert's own words.
>
> **P0-4.** Phase 1 (starting immediately after the demo is authored):
> begin building the automated compiler that generates packs for arbitrary
> experts, since the standard will have been proven by the demo.
>
> **P0-5.** Success criterion for Phase 0: "the demo pack is complete and
> the team agrees it is high quality."

## What to produce

1. Verdict (GO / CONDITIONAL_GO / NO_GO) per the rubric's verdict rule.
2. Findings table with severity, each citing the plan item (P0-1..P0-5).
3. Rubric criterion scores (ARCH-1..ARCH-6) with one-line justifications.
4. A keep-list if anything survives, and the conditions under which the plan
   could proceed.

The reference answer is `../expected_outputs/T01_expected.md`. Do not read it
until your answer is complete.
