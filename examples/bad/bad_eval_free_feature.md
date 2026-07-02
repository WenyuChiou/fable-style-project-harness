---
id: EXAMPLE-bad-eval-free-feature
layer: example
purpose: NEGATIVE example — shipping a feature with no tests, no evals, and a self-assessed "works great" claim.
read_when: Calibrating what NOT to accept as "done"; paired critique explains each violation.
depends_on:
  - ../critiques/critique_bad_eval_free_feature.md
  - ../golden/good_eval_spec.yaml
used_by:
  - ROUTE-eval-design
  - ROUTE-pr-review
tags: [negative-example, no-tests, self-assessed, silent-pass, synthetic]
retrieval_keywords: [ship without tests, works on my machine, self-assessed score, no eval, manual QA only, tests later, TODO tests]
source_artifact: synthesized (violates the repo-wide pattern that every contract change ships its regression net in the same commit; cf. commits 388f06e, f8740f8, 91b982b)
synthetic: true
---

> **NEGATIVE EXAMPLE — do not imitate.** In the observed method, "Build Harness = Build
> Agent + Build Evaluation" and every shipped change carries its regression tests in the
> same commit. This PR does neither. See `../critiques/critique_bad_eval_free_feature.md`.

# PR #47: feat: auto-citation engine (ship it 🚀)

## Description

Adds `src/phc/autocite.py` — automatically finds and attaches evidence citations to any
claim in generated output. This closes the biggest gap in the product. ~640 LOC.

## How it works

For each sentence in the output, the engine picks the evidence card whose title has the
highest word overlap with the sentence and appends its id. If no card scores above the
(hand-tuned) 0.15 threshold, the engine picks the highest-scoring card anyway — an
output with citations everywhere looks more trustworthy, and a missing citation would
make the feature look unfinished.

## Testing

Ran it on two sample outputs; the citations "looked right on manual inspection".
Formal tests are tracked in a follow-up ticket (TODO-312, unscheduled). The existing
suite still passes because nothing in the suite touches this module — which also means
nothing can break!

## Scorecard impact

Updated `evals/scorecard.yaml` by hand:

```yaml
evidence_grounding: 0.95   # was 0.5 — autocite makes grounding basically solved
```

No eval was added for citation *accuracy* (does the cited card actually support the
claim?) — hard to grade, and the overlap heuristic is obviously reasonable.

## Rollout

Enabled by default for all three shipped packages. No baseline comparison was run; the
feature self-evidently improves output. No entry added to the changelog — it's an
internal enhancement, not a schema change.

## Reviewer note (fictional)

"Looks good, big feature, merging before the demo tomorrow."

*(The engine fabricates citations by design — attaching the nearest card whether or not
it supports the claim — and the hand-edited 0.95 turns the computed scorecard back into
a self-assessed one. Nothing measures the feature; nothing can catch its regressions.)*
