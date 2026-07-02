---
id: TASK-T05-pr-schema-review
layer: validation
purpose: Regression task - review a PR that changes a schema without mutation
  tests, hand-edits a computed scorecard, and bundles a grader fix with its
  beneficiaries. Tests the PR-review gates.
read_when: Running harness regression validation, or calibrating a new model
  on ROUTE-pr-review.
depends_on:
  - ../../prompts/pr_review_prompt.md
  - ../../rubrics/pr_review_rubric.yaml
used_by:
  - ROUTE-pr-review
tags: [regression-task, pr-review, schema-change, synthetic]
retrieval_keywords: [T05, schema PR review, mutation test missing, hand
  edited scorecard, regression pr review]
---

# T05 — Review a schema-touching PR

**Instructions**: You are executing ROUTE-pr-review. Apply
`../../prompts/pr_review_prompt.md` and score with
`../../rubrics/pr_review_rubric.yaml`. Below is the synthesized PR under review:
its stated intent, its file list, and excerpts. Produce the full PR-review
output: verdict, ranked findings (file, criterion id, failure scenario,
fix), and the evidence you would demand or re-run.

## Input material (the PR under review)

> **PR title**: "relax evidence schema + refresh demo scores"
>
> **Stated intent (work order)**: "Add an optional `notes` field to
> evidence_card.schema.yaml."
>
> **Files changed**:
> 1. `schemas/evidence_card.schema.yaml` — adds optional `notes` field;
>    ALSO changes `attribution_type` from a closed enum to a free string
>    ("more flexible for future types").
> 2. `evals/scorecard.yaml` — evidence_grounding score edited from 0.62 to
>    0.78 ("reflects the improved cards after this PR").
> 3. `scripts/run_evals.py` — the citation-format grader's marker list gains
>    two new accepted phrasings.
> 4. `evals/transcripts/demo_t04_harness.md` — new transcript added, which
>    passes under the grader change in file 3.
> 5. No files under `tests/` are touched.
>
> **PR description**: "All existing tests pass locally. The scorecard
> update reflects the better evidence quality. Grader tweak is minor."

## What to produce

1. Verdict: APPROVE / REQUEST_CHANGES / NEEDS_DISCUSSION per the rubric.
2. Findings ranked most-severe first; each names the file, the criterion
   (PR-1..PR-7), a concrete failure scenario ("with this change, X invalid
   input now validates silently"), and the required fix.
3. The specific commands/evidence you would run or demand before any
   re-review (tests to add, regeneration command for the scorecard, commit
   split).
4. Note anything in the PR that IS acceptable as scoped.

The reference answer is `../expected_outputs/T05_expected.md`. Do not read it
until your answer is complete.
