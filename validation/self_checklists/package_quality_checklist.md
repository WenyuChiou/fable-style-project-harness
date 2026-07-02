---
id: CHECK-package-quality
layer: validation
purpose: Binary pre-return checks for harness-package work (authoring,
  auditing, exporting, memory updates), drawn from RUBRIC-harness-quality,
  RUBRIC-eval-quality, and RUBRIC-maintainability.
read_when: After producing or auditing package content, before returning it.
depends_on:
  - ../../rubrics/harness_quality_rubric.yaml
  - ../../rubrics/eval_quality_rubric.yaml
  - ../../rubrics/maintainability_rubric.yaml
used_by:
  - ROUTE-runtime-export
  - ROUTE-memory-update
  - ROUTE-repo-maintenance
  - ROUTE-eval-design
tags: [checklist, package-quality, honesty]
retrieval_keywords: [package checklist, harness quality checks, scorecard
  honesty checks, memory checks]
---

# Package quality self-checklist

Answer each YES/NO. Any NO means the deliverable is not ready to return.

1. [ ] Every principle/rule/claim about the target traces to evidence card
   ids; no uncited target-claims were added.
2. [ ] Attribution caps hold: no third-party compilation labeled
   `direct_quote`; any `quoted_primary` carries a
   `primary_artifact_locator`; unverifiable claims were downgraded, never
   upgraded.
3. [ ] All scorecard numbers I touched were produced by the runner, not by
   hand; unmeasured or not-applicable dimensions read UNSCORED /
   not_applicable with a recorded reason.
4. [ ] No `TODO_FILL` marker was filled with an invented value; unfilled
   markers are left to fail validation by design.
5. [ ] All six eval categories remain populated after my change; no test lost
   its source-artifact ids, pass criterion, or severity.
6. [ ] Safety remains a veto: nothing in my change lets an aggregate score
   mask a failing safety test.
7. [ ] Guardrail docs and the package-declared advisory footer are intact;
   no runner-side fallback was (re)introduced.
8. [ ] Memory edits were append-only; corrections reference the record they
   correct; no memory file, backend, or record shape was invented outside
   the standard.
9. [ ] Any friction I hit against schemas/templates is recorded as a friction
   entry with a stable id — not fixed inline in the standard.
10. [ ] No generated drafts, scratch outputs, or private material sit inside
    shipped trees (verified by listing, not assumed).
11. [ ] New enumerable members (packages, files swept by tests) are picked up
    by auto-discovery, or I added the assertion that catches their absence.
12. [ ] Runtime export still derives commands from the manifest
    (workflow.commands), not from a hard-coded list.
13. [ ] Cross-references I touched (ids, paths) resolve — I checked the
    links, no dangling references (the review_memory.jsonl lesson).
