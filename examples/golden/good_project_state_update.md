---
id: EXAMPLE-good-project-state-update
layer: example
purpose: Golden example of a development-plan status update — per-phase states with evidence pointers, recorded drift fixes, and honest PARTIAL markers.
read_when: You are updating a plan/status document after a milestone, or reporting project state to the owner.
depends_on:
  - ./good_go_no_go_decision.md
used_by:
  - ROUTE-memory-update
  - ROUTE-repo-maintenance
tags: [status-update, development-plan, drift-fix, partial-status, golden]
retrieval_keywords: [development plan, status DONE PARTIAL, drift fix, stage status, milestone update, honest status line, recorded correction]
source_artifact: docs/development_plan.md (repo method-harness-compiler, updates recorded in commits 510b79f, 91b982b, 7134227)
synthetic: false
---

# Golden: Project State Update (modeled on the real development-plan updates)

The source plan is a living document whose status header is rewritten at every
milestone, with three properties worth copying: statuses carry **evidence**, drift is
**fixed and recorded** (not silently rewritten), and partial completion is **labeled
PARTIAL**, never rounded up to done.

## The status header (condensed real form)

> Status as of 2026-07-02: **Phase 0 done; Milestone 1a (roadmap-inverted, see below)
> DONE; Milestone 1b (second demo, N=2 gate PASSED with zero schema changes) DONE;
> Milestone 1c (grader v2 + `phc` CLI + external audit wedge) DONE; Milestone 1d
> (Category-7 retracted-paper outcome eval) EXECUTED as a pilot; tool-discovery research
> (M2a, run at the start of Phase 2 per B12) DONE.**

Each clause names the milestone, its defining artifact, and its gate result — the header
is skimmable proof, not a mood.

## Per-phase entries (structure)

```
### Milestone 1a: Installable plugin + computed scorecard + transcripts — DONE (2026-07-01)
  [what shipped, which design-review IDs it discharged (B1, B2), suite count]

### Phase 2: Semi-automated builder — research prefix DONE (M2a);
    first-wave builder primitives SHIPPED (M2b, 2026-07-02)

### Phase 5: Runtime export — 🟡 PARTIAL (Claude Code path de facto shipped)
  Status: originally "not started", but the Claude Code export path shipped
  as part of M1a. [the honest reclassification is explained, not hidden]

### Stage 4: Evidence and method — ⬜   [not-started stays visibly empty]
```

## Recorded drift fixes (the distinctive move)

When the M2a update touched the plan, it did not just add its own row — it recorded
**three drift fixes** it found in the existing text, in the commit body:

> docs/development_plan.md Phase 1/Stage 1 DONE + three recorded drift fixes
> (N=2 gate wording now consistent AND honest: blinded full-suite arm still open;
> M1c locale notes; Phase 5 re-marked PARTIAL)

Note the direction of the fixes: one of them **downgraded** a status (Phase 5 re-marked
PARTIAL) and another **narrowed** a gate claim (the blinded full-suite arm of the B3 gate
is still open, and the plan now says so). Status updates in this method are allowed to
make the project look *less* done when that is the truth.

## Companion moves observed elsewhere in the repo

- Status lines are **synced across every surface that repeats them**: when the test count
  moved, the parity agent updated all three README locales and caught two stale "299"
  status lines left over from the previous milestone (commit e7f0fc6).
- Statuses reference the **gate artifact**, not the author's memory: "N=2 gate PASSED"
  links to `docs/n2_gate_report.md`, where the PASS is independently verified.
- New friction discovered during a milestone is **appended** to the standing gate report
  (the N=3 section was appended to the N=2 report rather than replacing it), preserving
  the historical record — corrections append, never overwrite.
- Suite counts appear in nearly every update ("Suite 638 -> 730 passing") — a cheap,
  mechanical, hard-to-fake progress signal.

## Reuse checklist

- [ ] One-paragraph status header naming every milestone + its gate result.
- [ ] Per-phase entries: DONE / 🟡 PARTIAL / ⬜ with dates and evidence pointers.
- [ ] Drift found while updating is fixed AND recorded as a drift fix.
- [ ] Downgrades and narrowed claims are legitimate update outcomes.
- [ ] Numbers (test counts, gate scores) accompany every DONE.
- [ ] History appends; earlier sections stay verbatim with status notes only.
