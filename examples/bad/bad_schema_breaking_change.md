---
id: EXAMPLE-bad-schema-breaking-change
layer: example
purpose: NEGATIVE example — renaming a required schema field with no mutation tests, no changelog entry, no instance sweep, and no friction record.
read_when: Calibrating what NOT to do when a schema/contract must change; paired critique explains each violation.
depends_on:
  - ../critiques/critique_bad_schema_breaking_change.md
  - ../golden/good_go_no_go_decision.md
used_by:
  - ROUTE-pr-review
  - ROUTE-repo-maintenance
tags: [negative-example, schema-change, breaking-change, no-changelog, synthetic]
retrieval_keywords: [rename required field, breaking schema change, no migration, no changelog, silent rename, additionalProperties, mutation test missing]
source_artifact: synthesized (contrast with the real v0.6 rename sweep in commit f8740f8 — friction-mapped renames, mutation regression tests, changelog, both packages swept)
synthetic: true
---

> **NEGATIVE EXAMPLE — do not imitate.** The real v0.6 revision renamed fields too — but
> every rename mapped to a recorded friction ID, landed with mutation tests ("reverting
> any rename fails the suite"), swept every instance in both packages, and was logged in
> `CHANGELOG_STANDARD.md`. This PR is the careless version. See
> `../critiques/critique_bad_schema_breaking_change.md`.

# PR #52: refactor: cleaner field names in evidence schema

## Description

While reading `evidence_card.schema.yaml` I noticed `subject` is vague. Renamed it to
`about_entity`, which reads better. One-line schema diff:

```diff
   required:
-    - subject
+    - about_entity
```

Also took the opportunity to tighten `confidence` from `number` to `integer` (0-100
scale is more intuitive than 0.0-1.0) since I was in the file anyway.

## Scope

- `schemas/evidence_card.schema.yaml` — the only file touched. Small diff, quick merge.

## What about existing packages?

The three shipped packages still use `subject` and decimal confidence, but the schemas
have `additionalProperties: true`, so their files still *parse*. Validation failures
will surface naturally when someone next runs the runner, and whoever hits them can fix
the instances then. Filing a ticket felt like overkill for a rename.

## Changelog

None — the standard is pre-1.0, so field names aren't a stable API yet. People should
expect churn.

## Tests

The schema metaschema test still passes (it only checks the schema is valid JSON
Schema). No test asserts field names, so nothing went red. That's a green suite —
merging.

## Motivation

No recorded friction from any package author about `subject`; it just felt off.
Renaming now avoids a bigger rename later, probably.

*(Every shipped evidence card is now invalid against the schema it claims to validate
against; the runner's grounding checks now look for a field no instance has; the 0-100
confidence silently breaks every downstream threshold comparison; and since no test pins
the field names, the suite stays green while the contract is broken. Discovery is
deferred to whoever runs validation next — with no changelog line to explain what
happened.)*
