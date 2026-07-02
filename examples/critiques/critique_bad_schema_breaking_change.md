---
id: CRIT-schema-breaking-change
layer: example
purpose: Critique of bad_schema_breaking_change.md — unswept rename of a required field; with the friction-mapped, mutation-tested correction.
read_when: You read the bad schema-change PR, or any diff touches a governed schema.
depends_on:
  - ../bad/bad_schema_breaking_change.md
  - ../golden/good_go_no_go_decision.md
  - ../../datasets/failure_modes.yaml
used_by:
  - ROUTE-pr-review
  - ROUTE-repo-maintenance
tags: [critique, schema-change, mutation-tests, changelog]
retrieval_keywords: [schema rename critique, mutation regression test, changelog standard, instance sweep, friction id, grep old value]
synthetic: true
---

# Critique: bad_schema_breaking_change.md

## Violations

1. **Rename motivated by taste, not recorded friction** ("it just felt off; no recorded
   friction from any package author"). Violates DR-002/DR-009 as practiced: every real
   v0.6/v0.7 standard change maps to a numbered friction item from a gate report
   (F1-F13, N3-F1..; "every item mapped to recorded friction"). No friction ID, no
   standard change.
2. **No instance sweep.** The real v0.6 rename moved schemas, instances, runner, tests,
   and docs **in one revision** across both packages (git mv, all references), with an
   independent reviewer running old-value greps. Leaving shipped packages invalid is
   FM-017 (dangling-cross-reference) at contract scale.
3. **No mutation tests.** The real sweep added tests such that "reverting any rename
   fails the suite"; here NO test pins field names, so the suite stays green while the
   contract breaks — FM-001 (silent-pass-wiring) in its most expensive form.
   RUBRIC-review-quality requires the regression net in the same commit.
4. **No changelog entry** ("pre-1.0, expect churn"). The real standard logs every
   revision in `CHANGELOG_STANDARD.md` with friction IDs — the changelog IS the
   standard's memory (DR-009: corrections/revisions append to an auditable record).
   Skipping it is FM-004 (stale-doc-drift) by construction.
5. **Drive-by semantic change** (confidence number→integer 0-100) smuggled into a
   "rename" PR: silently breaks every downstream threshold comparison; violates DR-005
   (scope-named commits; scope-sensitive files must be named in the commit body) and
   trigger discipline — schema surface = mandatory review.
6. **"Failures will surface naturally when someone next runs the runner"** delegates
   discovery to a future victim — the exact opposite of DR-003's fail-closed posture and
   of the N=2 gate ethic (change the standard deliberately and loggedly, or record
   friction and leave it).

## Corrected approach (5-10 lines)

```text
1. File the naming pain as a friction item in the gate report; let it
   accumulate hit-count/severity evidence.
2. If ratified: one revision moves schema + BOTH packages' instances +
   runner + tests + docs (git mv; grep the old name to zero, excluding
   historical gate/changelog text).
3. Add mutation tests: reverting the rename (or the type change) fails
   the suite.
4. CHANGELOG_STANDARD entry citing the friction ID; version bump.
5. Separate the semantic type change into its own reviewed change with
   its own tests — never ride a rename.
6. Independent reviewer re-greps old values and re-runs the suite before
   commit; explicit-path staging with a file-count assertion.
```
