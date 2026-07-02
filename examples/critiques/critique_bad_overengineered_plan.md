---
id: CRIT-overengineered-plan
layer: example
purpose: Critique of bad_overengineered_plan.md — names every violated decision rule, failure mode, and rubric criterion, with the corrected approach.
read_when: You read the bad plan example, or you are reviewing a plan that smells framework-first.
depends_on:
  - ../bad/bad_overengineered_plan.md
  - ../../datasets/failure_modes.yaml
used_by:
  - ROUTE-phase-review
tags: [critique, plan-review, overengineering, gates]
retrieval_keywords: [plan critique, big design up front, falsifiable gate missing, adoption failure, phase order inverted]
synthetic: true
---

# Critique: bad_overengineered_plan.md

## Violations

1. **Phase order inverted — proof deferred to the end.** Installability and evaluation
   land in Months 9-10; every earlier phase can only be judged by the authors' taste.
   Violates DR-003 (falsifiable-gates-before-automation) — the observed method inverted
   exactly this ordering on review (design review B1/B3): the demo ships installable
   FIRST, and automation begins only after an N=2 zero-schema-edit gate passes.
2. **No gate can fail.** "Ends when artifacts are complete, as judged by the authors"
   is not a gate. Violates DR-003 and RUBRIC-gate-honesty (a gate needs a pre-registered,
   mechanical pass condition and a NO_GO branch; halt is a success state, DR-010).
3. **Standard priced for adoption failure.** 22 schemas / 61 mandatory files at N=0
   reproduces FM-009 (scope-creep-standard-bloat) — the real review flagged ~45 files at
   N=1 as a critical finding (C7) and demoted compiler intermediates.
4. **"Conform by construction — no separate validation"** is FM-001 (silent-pass-wiring):
   the generator implementing the schema does not evidence conformance; independent
   validation does.
5. **Self-assessed scorecard** ("filled in based on the team's assessment") violates
   DR-004 (honest-failure-publishing) and RUBRIC-eval-design: scores are computed by a
   runner or marked UNSCORED — never hand-assigned (FM-026).
6. **Auto-extraction pipeline before any hand-authored package** violates DR-008
   (deterministic-tier-0-first) and the N=2 discipline: generalize from at least two
   hand-authored instances before automating.
7. **Vibes-based success criteria and risk section** ("community excitement",
   "the team is experienced") violate DR-002 (pin IDs/disciplines before execution) —
   nothing here is checkable.

## Corrected approach (what the real method did)

```text
1. Day 1: hand-author ONE package against a minimal standard; ship its
   regression suite in the same commit.
2. Run a 4-lens adversarial review of the spec BEFORE the next phase;
   emit tiered change program with IDs (A*/B*/C*).
3. Make "installs and runs end-to-end in a stock runtime" the EXIT
   criterion of the first milestone, not the last.
4. Gate automation on falsifiable conditions: harness >=5/6 vs baseline
   <=2/6 under a blinded grader, AND a second domain authored with ZERO
   schema edits. Otherwise revise the standard — halting is a pass.
5. Scores come from a runner; unmeasured dimensions say UNSCORED.
6. Defer every schema/file that two real packages have not yet forced.
```
