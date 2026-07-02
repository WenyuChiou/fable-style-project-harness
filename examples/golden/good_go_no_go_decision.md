---
id: EXAMPLE-good-go-no-go-decision
layer: example
purpose: Golden example of a falsifiable gate verdict — the N=2 zero-schema-edit gate — where the friction record IS the deliverable and the honesty note narrows the claim.
read_when: You must decide GO / CONDITIONAL_GO / NO_GO at a phase gate, or you are writing up a gate result.
depends_on:
  - ./good_phase_review.md
  - ../../playbooks
used_by:
  - ROUTE-phase-review
tags: [gate, go-no-go, n2-gate, friction-inventory, honesty-note, golden]
retrieval_keywords: [N=2 gate, zero schema changes, friction record, PASS verdict, byte-identical, honesty note, resolutions table, accepted unresolved]
source_artifact: docs/n2_gate_report.md (repo method-harness-compiler, commit bd32614; resolutions f8740f8)
synthetic: false
---

# Golden: GO / NO-GO Gate Verdict (the N=2 gate, condensed from the real report)

The gate was pre-registered in the phase review (design review B3): "the second demo
package must be authored against the EXISTING schemas without modifying them; every point
of friction is recorded — **the friction record IS the deliverable**." This file condenses
the real verdict; the moves to copy are annotated.

## The verdict (lead with it, then immediately narrow it)

> **PASS — the second package was authored with ZERO schema changes.** All ten files in
> `schemas/` are byte-identical to their pre-demo2 state — **independently verified**, not
> asserted by the authors.
>
> **Honesty note:** "zero schema changes" means *zero changes during authoring*. The
> standard did move once before the gate (the target block, v0.6-alpha) because N=2
> preparation showed person-first framing cannot express a methodology-anchored package
> at all — the single authoring-impossible case, resolved by a minimal, **logged,
> pre-gate** schema revision, not a silent edit.

Moves observed:
- The pass condition was fixed BEFORE the work started (pre-registration).
- The check is mechanical (byte-identical `schemas/`) and was re-verified by someone who
  did not author the package.
- The one exception is disclosed in the verdict itself, with the changelog pointer, so
  the claim survives adversarial reading.

## The friction inventory (the actual deliverable)

Thirteen items (F1-F13), each in a fixed shape: **where** (exact schema/field) → what
chafed → workaround used → recommended action. Ordered by how many of the four authoring
agents independently hit it, then severity. Representative entries:

| ID | Friction (condensed) | Hit by | Disposition (v0.6) |
|---|---|---|---|
| F1 | Person-named fields forced to carry non-person values (`target_person` hard-required by 3 schemas) | 4/4 agents | RESOLVED — clean-break renames (`person` → `subject`, `target_person` → `target_label`), not aliases |
| F2 | `person_specific_tests` is a person-named slot for method tests | 2/4 | RESOLVED — `target_specific_tests` rename, git mv in both packages |
| F4 | Fixed memory naming is investment-flavored; JSONL record shapes ungoverned — produced a REAL dangling `review_memory.jsonl` reference caught at integration | 1/4 + corroboration | Accepted, unresolved — convention + NAMING NOTE + tests |
| F9 | Scorecard cannot express recorded-N/A or unscored-ness; honest answer "not measured" had no slot | 2/4 | Accepted, unresolved — recorded-N/A pinned by tests instead |
| F13 | Runner resolves any `step_*` string — a misspelled step id would pass silently; pinned-id review caught it, not the machine | 1/4 | Accepted at schema layer — content tests now pin the nine step ids in order |

## What generalized cleanly (the other half of honesty)

The report also names what needed NO change: the schema architecture, the 4-value
attribution enum, the core package tree, the plugin packaging layer, the read-only tool
model, the invariant-vs-compiled workflow split, and the computed-scorecard runner
("ran on the person-less package with no crash and no silent pass").

## The resolutions table closes the loop

Every friction ID later received an explicit disposition — RESOLVED (with the exact
rename), PARTIALLY RESOLVED, or **"Accepted, unresolved"** with the candidate fix left on
record. Nothing was silently dropped; the standard revision commit maps each change to
its friction ID.

## Why this is the golden form

- **Falsifiable before, mechanical after**: the gate condition existed before the work
  and was checked byte-for-byte after.
- **Friction is data, not complaint**: each item names the exact file/field, the
  workaround actually used, and feeds the next standard revision by ID.
- **A PASS that documents its own boundary** (the honesty note) is worth more than a
  clean PASS that hides a pre-gate edit.
- **"Accepted, unresolved" is a legitimate disposition** — the gate does not force fake
  closure. Halt-or-defer is a success state.

## Reuse checklist

- [ ] Gate condition pre-registered, with a mechanical check.
- [ ] Verdict independently re-verified (different agent/person than the author).
- [ ] Honesty note narrowing the claim where reality is messier than the slogan.
- [ ] Friction items: where → chafe → workaround → recommendation, with hit-counts.
- [ ] "What generalized cleanly" section.
- [ ] Later resolutions table referencing friction IDs; unresolved items say so.
