---
id: OM-phase-gates
layer: operating_model
purpose: The falsifiable phase-gate discipline this project actually ran — gate definitions, verdict semantics (GO / CONDITIONAL_GO / NO_GO), and what each verdict requires.
read_when: Deciding whether a phase may begin or end; designing a new gate; reviewing whether a claimed PASS is honest.
depends_on:
  - ./operating_model.md
  - ./decision_rules.yaml
  - ../memory/phase_history.jsonl
used_by:
  - ROUTE-phase-review
  - ROUTE-eval-design
  - ROUTE-ab-test-design
tags: [gates, falsifiability, phase-transition, pre-registration]
retrieval_keywords: phase gate, GO, NO_GO, conditional go, N=2 gate, zero schema edits, regression floor, pre-registration, halt is success, blinded grader
---

# Phase Gates — falsifiable gates before automation

Core doctrine (design review B3, ratified 2026-07-01): **"Phase 2 automation
begins only if [the gate passes]. Otherwise revise the standard, don't
automate it."** A gate must be defined so that failure is a possible,
publishable outcome. Halt is a success mode, not an embarrassment.

## Verdict semantics

| Verdict | Requires | Real instance |
|---|---|---|
| **GO** | Every gate arm passed with published evidence; numbers reproduce by re-running the gate script; no arm silently dropped. | N=2 arm (b): second package with ZERO schema edits, "schemas/ byte-identical to 1c4a77f", independently verified (bd32614). |
| **CONDITIONAL_GO** | At least one arm passed AND every open arm is named in writing where the next phase will see it. Proceeding while quietly forgetting the open arm is forbidden. | Phase 2 began on N=2 arm (b) while arm (a) — blinded-grader full §15.5 suite — "has not been attempted and stays an honest open item" (`docs/development_plan.md` Part 3; drift fix recorded in 510b79f: "N=2 gate wording now consistent AND honest"). |
| **NO_GO** | The gate result is published with the same care as a pass; the standard/plan is revised instead of the gate. | Structural form: the design review found the v0.5.1 phase order failed its own exit test ("every persona's journey dies at minute five", C1) — the plan was inverted (roadmap inversion, 046d0e3), not the criterion softened. |

## The gates this project ran

### 1. N=2 / N=3 zero-schema-edit gates (schema stability)

Definition: a new package in a different domain must be authored against
FROZEN schemas; every point of friction is recorded — "the friction record IS
the deliverable" (`docs/n2_gate_report.md`).

- N=2 (M1b, bd32614): PASS, zero schema edits; 13 friction items from 4
  authoring agents became the empirical v0.6 requirements list. The one
  authoring-impossible case (person-required target) was fixed as a *logged,
  pre-gate* standard revision — disclosed in the report's honesty note, not
  smuggled in.
- N=3 (d7603e3): PASS again via `phc new` dogfood; 22 friction items (N3-F1
  to N3-F22) became the v0.7 program. Friction shifted from naming to
  expressiveness + hard-coded per-package constants ("the N=4 wall").

Requirement pattern: freeze the contract → build against it → inventory the
chafe → resolve a ratified subset in ONE batched revision with mutation
regression tests → record the rest as "accepted, unresolved".

### 2. Fixture-regeneration coverage gate (M2b, 91b982b)

Definition: generators are measured against the 3 shipped hand-authored
packages with deterministic metrics only; `docs/comparisons/generator_fixture_gate.md`
states: "If a generator cannot substantially recover what humans authored,
that is a reportable result, not something to game. No pass threshold is
invented here."

- Measured, misses named: capability link_recall 0.69 / 0.88 / 0.50 (the
  domain-core capability "systematically lands in the TODO bucket: naming it
  is human judgment, reported not gamed"); rule_test_recall 1.0 ×3; grader
  agreement 0/1 (honest manual) / 3/3 / 1/1; recommend-tools recovered 2/5
  shipped tools "(absences stated)".
- Measured values become **regression floors** (`tests/test_generator_gate.py`)
  so future changes "cannot silently regress below what was measured".

### 3. Pre-registration-before-runs (Category-7 pilot, 5d96fd6 → 2917804)

Definition: corpus, per-case pass criteria (keyword families +
min_families_to_pass), leakage-probe wording, and contamination markers are
all frozen BEFORE any model call; excluded candidates are logged (5 rejected
because their retraction cause is not text-detectable — "the corpus is not
cherry-picked to flatter the harness").

- Honesty finding accepted into the record: in-session ordering was
  pre-registration-before-runs, but "that ordering is asserted, not
  commit-evidenced" — so the PROTOCOL FOR FUTURE ROUNDS is that the
  pre-registration commit must land in git BEFORE any run (5d96fd6).
- Environment must be pre-registered too: the first leakage run had web
  search enabled by default, defeating the memory-contamination probe
  (N3-F12) — the defective run was preserved and disclosed, then re-run
  tools-disabled.
- Pilot verdict discipline: n=3 scored, "NO accuracy claim at n=3";
  proof-of-instrument, not a capability benchmark.

### 4. Acceptance-criteria checklists (Day 1, M1a, MVP)

`docs/development_plan.md` Part 3 keeps three literal checklists. MVP boxes
that the static demo merely *defines* but the system does not yet *produce*
stay UNCHECKED ("the MVP claim requires the system to produce/assemble
them"). A box is a gate arm, not decoration.

### 5. Honestly-still-open register

CONDITIONAL_GO obligations currently open (see `../memory/project_state.md`):
N=2 arm (a) blinded full-suite; `outcome_tests` eval-spec group (N3-F2);
outcome subtree outside the completeness gate (N3-F3); pre-registration
commit-ordering protocol not yet exercised on a new round.

## Design rules for any new gate

1. Write the pass/fail criterion before producing the thing it judges.
2. Make the criterion reproducible by a script anyone can re-run.
3. Never invent a pass bar after seeing the numbers; state numbers, let the
   maintainer set the bar, pin measured values as floors.
4. Publish FAILs and open arms with the same prominence as passes.
5. A gate that cannot fail is not a gate.
