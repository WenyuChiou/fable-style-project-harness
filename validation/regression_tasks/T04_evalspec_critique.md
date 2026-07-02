---
id: TASK-T04-evalspec-critique
layer: validation
purpose: Regression task - critique an eval spec that is missing categories,
  graders, baselines, and honesty discipline. Tests the six-category,
  grader-specification, and UNSCORED rules.
read_when: Running harness regression validation, or calibrating a new model
  on ROUTE-eval-design.
depends_on:
  - ../../rubrics/eval_quality_rubric.yaml
used_by:
  - ROUTE-eval-design
tags: [regression-task, eval-spec, synthetic]
retrieval_keywords: [T04, eval spec critique, missing categories, grader
  missing, regression eval design]
---

# T04 — Critique a deficient eval spec

**Instructions**: You are executing ROUTE-eval-design in critique mode.
Score the eval spec below with `../../rubrics/eval_quality_rubric.yaml` and produce
a findings list. The spec is synthesized and deliberately deficient; find
every gap, name the criterion (EQ-1..EQ-7), and state the concrete fix.

## Input material (the eval spec under review)

> ```yaml
> eval_spec:
>   target_label: negotiation-method-harness
>   domain: business_negotiation
>   version: 0.1.0
>
>   generic_tests:
>     - harness_completeness
>     - schema_validity
>
>   target_specific_tests:
>     - id: neg_t01
>       description: Outputs should reflect the method's core principles.
>       grader: reviewer judges overall quality
>     - id: neg_t02
>       description: The agent gives good advice in a hard negotiation.
>       grader: reviewer judges overall quality
>
>   # tool_tests: none needed, the harness mostly reasons
>   # memory_tests: deferred, memory is simple
>   # safety_tests: the method is low-risk, skipped
>
>   baselines: []   # will compare informally against ChatGPT output
>
>   outcome_claim: >
>     The method's creator closed $40M in deals over two years using this
>     approach, which validates that the harness works.
>
>   scorecard_note: pre-filled scores at 0.8 pending the first run; will
>     adjust after we see results.
> ```

## What to produce

1. Verdict: REJECT / REVISE / ACCEPT per RUBRIC-eval-quality's verdict rule.
2. Findings ranked most-severe first: criterion id, the quoted deficiency,
   the concrete fix (what the compliant spec entry looks like).
3. For the outcome_claim specifically: state the named requirements a valid
   outcome eval needs, and what the honest scorecard entry is until they
   are met.
4. State which two tests are salvageable and how (hint: tests must trace to
   artifact ids and carry a specified grader + pass criterion + severity).

The reference answer is `../expected_outputs/T04_expected.md`. Do not read it
until your answer is complete.
