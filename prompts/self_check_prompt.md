---
id: PROMPT-self-check
layer: prompt
purpose: Instruction for scoring your OWN output with the relevant rubric and
  failure-mode list before returning it - the harness's local form of the
  author-agnostic review gate.
read_when: After producing any deliverable, before returning it.
depends_on:
  - ../rubrics/architecture_review_rubric.yaml
  - ../rubrics/harness_quality_rubric.yaml
  - ../rubrics/tool_discovery_rubric.yaml
  - ../rubrics/tool_boundary_rubric.yaml
  - ../rubrics/eval_quality_rubric.yaml
  - ../rubrics/maintainability_rubric.yaml
  - ../rubrics/pr_review_rubric.yaml
  - ../rubrics/progressive_disclosure_rubric.yaml
used_by:
  - ROUTE-phase-review
  - ROUTE-tool-discovery
  - ROUTE-pr-review
  - ROUTE-eval-design
  - ROUTE-memory-update
  - ROUTE-runtime-export
  - ROUTE-repo-maintenance
  - ROUTE-ab-test-design
tags: [self-check, quality-gate, rubric-scoring]
retrieval_keywords: [check my own output, self review, score my work, failure
  modes checked, before returning]
---

# Self-check prompt

Before returning a deliverable, review it as if it were someone else's work.
Nothing ships ungated — the gate is author-agnostic, and that includes you.

## Procedure

1. **Pick the rubric** your route names (phase review ->
   `../rubrics/architecture_review_rubric.yaml`; discovery ->
   `tool_discovery_rubric.yaml` + `tool_boundary_rubric.yaml`; diff review ->
   `pr_review_rubric.yaml`; eval work -> `eval_quality_rubric.yaml`; memory/maintenance ->
   `maintainability_rubric.yaml`; export/layout -> `progressive_disclosure_rubric.yaml`;
   package work -> `harness_quality_rubric.yaml`).
2. **Score every criterion 1-5** against your own output, with a one-line
   justification each. Scoring yourself 5 across the board is a red flag —
   re-read the anchors; the anchor text, not your intention, decides the
   score.
3. **Walk the failure-mode dataset**: open the failure-mode records
   (`FM-###` in `../datasets/`) whose category matches your task type, and
   state for each either "not applicable because ..." or "checked: not
   present because ...". A bare list of FM ids without the because-clauses
   does not count.
4. **Honesty pass**: list everything in your deliverable that is UNSCORED,
   unverified, synthesized, or out of scope. If that list is empty, check
   again — most real deliverables have at least one honest gap.
5. **Apply the rubric's verdict rule to yourself.** If your own output lands
   at REVISE / REQUEST_CHANGES, fix it and re-run this check; if it lands at
   a blocking verdict you cannot fix (missing information, forbidden scope),
   return the deliverable WITH the failing verdict stated — an honestly
   published FAIL beats a silently passed one.

## Output appendix (attach to your deliverable)

```text
self_check:
  rubric: <RUBRIC-id>
  scores: {<criterion-id>: <1-5>, ...}
  verdict: <per rubric verdict rule>
  failure_modes_checked: [<FM-### with because-clauses>]
  unscored_or_unverified: [<items, or an explicit reason the list is empty>]
```
