---
id: L2-current-phase
layer: context
purpose: The source project's real current phase — what is allowed and forbidden right now
read_when: Start of every task, immediately after L0 — before classifying or acting
depends_on: [context/L0_bootstrap.md]
used_by: [ROUTE-phase-review, ROUTE-tool-discovery, ROUTE-pr-review, ROUTE-eval-design, ROUTE-memory-update, ROUTE-runtime-export, ROUTE-repo-maintenance, ROUTE-ab-test-design]
tags: [phase, current-state, scope, allowed, forbidden]
retrieval_keywords: [current phase, what phase, allowed, forbidden, scope, phase 3, next milestone, paused state]
---

# L2 — Current Phase

> **MAINTENANCE RULE (per `operating_model/project_memory_policy.yaml`):
> this file MUST be updated at every phase transition.** A stale L2 is the harness's worst
> failure mode — every route reads it first. Update it in the same round
> that updates `docs/development_plan.md` in the source repo.

Snapshot as of **2026-07-02, source repo at commit `965c68e`** (verified
against `docs/development_plan.md`).

## Where the project actually is

| Milestone | Status |
|---|---|
| Phase 0 — spec-first package standard | DONE (Day 1, commit `f4c826f`) |
| M1a — installable plugin + computed scorecard + transcripts | DONE (2026-07-01) |
| M1b — second demo, N=2 zero-schema-edit gate | DONE, arm (b) PASS (`docs/n2_gate_report.md`) |
| M1c — grader v2 + `phc` CLI + external audit wedge | DONE |
| M1d — Category-7 retracted-paper outcome eval | EXECUTED AS PILOT (proof-of-instrument, no accuracy claim) |
| N=3 — third demo via `phc new` dogfood, zero schema edits | DONE |
| M2a — tool-discovery research (27 sources scored, metadata-only) | DONE (2026-07-02, commit `510b79f`) |
| M2b — first-wave builder primitives + fixture-regeneration gate | SHIPPED, gate-measured (commit `91b982b`) |
| **Phase 3 — evidence and methodology extraction** | **NOT STARTED = the next phase** |

Phases 0–2 are therefore done *through the first-wave builder primitives at
`91b982b`* (Phase 2 keeps open second-wave items: FindSkills + GitHub
SKILL.md adapters, tool-fit-scorer refinement, model router, routing-policy
runner wiring). The N=2 gate's arm (a) — blinded-grader full §15.5 suite —
remains an honest open item.

## Paused state — allowed vs forbidden

**Allowed while paused (no gate required):**

- Reading, auditing, and re-verifying any shipped artifact (re-run
  `scripts/run_evals.py`, `scripts/generator_gate.py`, pytest).
- Recording friction, corrections, and memory updates (append-only).
- Repo maintenance: locale sync, CI, test-suite upkeep, doc drift fixes —
  with the review gates of ROUTE-pr-review.
- Phase-2 second-wave items already listed in `development_plan.md`
  (they extend a shipped, gate-measured wave).
- Designing (not running) future evals and A/B protocols —
  pre-registration artifacts are welcome; runs are not.

**Forbidden until the Phase-3 entry decision:**

- Starting Phase-3 automation (source discovery, evidence-card builder,
  principle extractor, source-to-principle mapper, attribution classifier)
  without an architect work order pinning IDs and disciplines first.
- Any schema edit outside a logged `CHANGELOG_STANDARD.md` revision with
  friction-ID citations and mutation regression tests.
- Hand-editing any computed scorecard; guessing any UNSCORED value.
- Executing, installing, or signing up for any discovered tool (spec 9.5).
- Fabricating evidence to fill `TODO_FILL` markers.
- Drawing capability/accuracy claims from the n=3 Category-7 pilot.

## Required outputs of the next phase (Phase 3, per `development_plan.md`)

- [ ] Source discovery
- [ ] Evidence card builder
- [ ] Principle extractor
- [ ] Source-to-principle mapper
- [ ] Attribution classifier

Observable entry expectations, from how Phases 1–2 were run: an architect
work order BEFORE execution; a falsifiable gate defined BEFORE automation
(the Phase-2 precedent is the fixture-regeneration gate — deterministic
coverage metrics against the 3 shipped packages, floors pinned as
regression tests); generators emit `.generated.yaml` DRAFTS with
`TODO_FILL`, never fabricated content; every claim about a source cited to
a fetched URL with honest unverified/unreachable ledgers.

## If your task conflicts with this file

Trust the source repo's `docs/development_plan.md` over this snapshot,
report the drift, and update this file in the same round.
