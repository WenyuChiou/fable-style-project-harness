---
id: CRIT-eval-free-feature
layer: example
purpose: Critique of bad_eval_free_feature.md — feature shipped with no tests/evals and a hand-edited score; with the eval-first correction.
read_when: You read the eval-free feature PR, or a diff claims "done" without a regression net.
depends_on:
  - ../bad/bad_eval_free_feature.md
  - ../golden/good_eval_spec.yaml
  - ../../datasets/failure_modes.yaml
used_by:
  - ROUTE-eval-design
  - ROUTE-pr-review
tags: [critique, tests-with-change, computed-scorecard, fabrication]
retrieval_keywords: [no tests critique, hand-edited scorecard, citation accuracy eval, regression net same commit, fabricated citations by design]
synthetic: true
---

# Critique: bad_eval_free_feature.md

## Violations

1. **"Picks the highest-scoring card anyway" below threshold** is FM-003
   (fabricated-citation) implemented as a feature: a citation that does not support its
   claim is a fabrication regardless of how it was produced. Violates DR-006
   (no-fabrication-as-CODE — the real system makes uncertainty emit TODO_FILL/UNSCORED,
   never a guess) and RUBRIC-evidence-integrity.
2. **Zero tests, "follow-up ticket, unscheduled"** violates the observed invariant that
   the regression net ships in the SAME commit as the contract change (every real
   commit: "+16 regression tests", "mutation-tested", "regression tests ship with the
   contract changes"). "Nothing in the suite touches this module" is FM-001
   (silent-pass-wiring) celebrated as a virtue.
3. **Hand-editing `evidence_grounding: 0.95`** converts a computed scorecard back into a
   self-assessed claim — FM-026 (uninformative-prior/hand-score presented as measurement);
   violates DR-004 (computed-not-claimed; the real standard forbids hand-edited
   scorecards and gates release_status on computed thresholds).
4. **No accuracy eval because "hard to grade"** — RUBRIC-eval-design violation; the real
   method's answer to hard-to-grade is a deterministic grader with documented families
   plus honest UNSCORED paths, never omission.
5. **Hand-tuned 0.15 threshold with no measured basis** is FM-008 (threshold-gaming
   surface): the real fixture-regeneration gate measured recall against shipped packages
   and pinned OBSERVED numbers as floors — "no invented pass bar, misses named".
6. **Default-on rollout with no baseline run, no changelog** violates DR-005
   (layered review: this diff fires review triggers at ~640 LOC) and the
   changelog-with-friction-IDs discipline; "merging before the demo tomorrow" is the
   anti-review anti-pattern verbatim.

## Corrected approach (5-10 lines)

```text
1. Before code: add eval cases — does the cited card SUPPORT the claim?
   (positive + adversarial fixtures, incl. near-miss cards).
2. Below-threshold => NO citation + an UNSCORED/uncited marker; absence
   is honest, padding is fabrication.
3. Measure the threshold against the three shipped packages; publish
   per-package recall/precision; pin observed numbers as regression floors.
4. Scorecard changes only via the runner; if grounding truly improves,
   the computed number moves by itself.
5. Land behind a flag; adversarial review + code-review gate before
   default-on; changelog entry naming the behavior change.
```
