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

Snapshot as of **2026-07-06, source repo at commit `0b8e4f8`** (verified
against the source repo's git log; reconciled from the retired old-clone
worktree plus records PH-019..PH-028). **Major events since the previous
committed snapshot: N=2 gate arm (a) RAN — NULL (`26d24df`) — AND the
revised gate v2 RAN — NULL on BOTH claims (`0b8e4f8`). Phase 3 is NO_GO;
the next real step is a STRATEGIC decision that belongs to the human.**

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
| **Phase 3 — evidence and methodology extraction** | **NO_GO — work order exists (`2ad438b`) but its CONDITIONAL_GO collapsed when arm (a) failed (ARCH-1)** |

Phases 0–2 are done *through the first-wave builder primitives at
`91b982b`*, plus **BOTH second-wave registry adapters SHIPPED**
(`FindSkillsAdapter` `b1310b5` + `GitHubSkillSearchAdapter` `41842ce`;
recommender consumes `ALL_ADAPTERS`; url-never-fabricated,
safety_label/zero-curation → no-credit, token-gated-graceful-degrade,
public-repos-only discipline), **ModelRoutingPolicy wired into the runner**
(`89e503b`: eval-time schema + S1 five-tiers / S2 escalation-terminus / S3
unambiguous-routing in `run_static`, `build_scorecard`, `phc validate`,
external audit), and **tool-fit-scorer refinement SHIPPED** (`571e9de`:
per-card `fit` block — capability_relevance / permission_fit
[over_privileged Tier-4 flag] / risk_posture / source_trust). **ALL
unblocked Phase-2 items are done**; the only remaining Phase-2 candidate is
an OPTIONAL full model-router (task→tier dispatch). Suite: **768 passing,
2 skipped** (`571e9de`); CI green.

**The N=2 gate story — two independent blinded NULLs:**

- **Arm (a) RAN 2026-07-03** under its pre-registered protocol → **NULL,
  gate NOT passed** (`26d24df`, `docs/evals/n2_arm_a_runs/report.md`):
  harness 6/6 but persona 5/6 — the ≤2/6 persona assumption was
  miscalibrated; arms tie on 5 of 6 tests, differing only on t04
  evidence-citation.
- The revision was designed (`521aab5`), its freeze artifacts drafted
  (`75f503b`), thresholds **owner-ratified** (`38b1748`), and **gate v2
  RAN 2026-07-04 → NULL on BOTH claims** (`0b8e4f8`,
  `docs/evals/n2_gate_v2_runs/report.md`): PRODUCT (C vs A) Δ=0.33 < 0.7;
  STRUCTURE (C vs B) Δ=0.17 < 0.3 — persona + the SAME evidence list scores
  1.83 vs harness 2.00 (means A=1.67 / B=1.83 / C=2.00), i.e. the harness
  is empirically "data + packaging, not structure". No veto fired.

Per the phase-gate doctrine both NULLs are **published, not re-run**. The
central "compiled harness beats a naive prompt" claim is **NOT SUPPORTED**
by two independent blinded evals. The honest next step is **STRATEGIC, not
a third behavioral gate**: (a) reposition around the evidence/policy bundle
the harness demonstrably provides, (b) test a different value axis the
behavioral gates don't reach (outcome correctness / auditability at scale /
consistency across authors), or (c) accept the null. **That decision is the
human's.**

## Paused state — allowed vs forbidden

**Allowed while paused (no gate required):**

- Reading, auditing, and re-verifying any shipped artifact (re-run
  `scripts/run_evals.py`, `scripts/generator_gate.py`, pytest).
- Recording friction, corrections, and memory updates (append-only).
- Repo maintenance: locale sync, CI, test-suite upkeep, doc drift fixes —
  with the review gates of ROUTE-pr-review.
- The one remaining OPTIONAL Phase-2 item (full model-router, task→tier
  dispatch) — it extends a shipped, gate-measured wave.
- Designing (not running) future evals and A/B protocols —
  pre-registration artifacts are welcome; runs are not.

**Forbidden until the strategic decision is made:**

- Starting Phase-3 automation (source discovery, evidence-card builder,
  principle extractor, source-to-principle mapper, attribution classifier).
  The architect work order exists (`docs/phase3_entry_work_order.md`,
  `2ad438b`) BUT it is **NO_GO**: arm (a) did not pass (ARCH-1) and the
  revised v2 gate also returned NULL on both claims (`0b8e4f8`). Building
  stays forbidden until the human makes the strategic call (reposition /
  new value axis / accept the null) and whatever gate that call implies is
  re-cleared. **Do NOT design or run a third behavioral gate as a
  substitute for that decision.**
- Any schema edit outside a logged `CHANGELOG_STANDARD.md` revision with
  friction-ID citations and mutation regression tests.
- Hand-editing any computed scorecard; guessing any UNSCORED value.
- Executing, installing, or signing up for any discovered tool (spec 9.5).
- Fabricating evidence to fill `TODO_FILL` markers.
- Drawing capability/accuracy claims from the n=3 Category-7 pilot.

## Required outputs of the next phase (Phase 3, per `development_plan.md` — currently NO_GO, do not start)

- [ ] Source discovery
- [ ] Evidence card builder
- [ ] Principle extractor
- [ ] Source-to-principle mapper
- [ ] Attribution classifier

Observable entry expectations, from how Phases 1–2 were run: an architect
work order BEFORE execution (exists: `2ad438b`); a falsifiable gate defined
BEFORE automation (the Phase-2 precedent is the fixture-regeneration gate —
deterministic coverage metrics against the 3 shipped packages, floors
pinned as regression tests); generators emit `.generated.yaml` DRAFTS with
`TODO_FILL`, never fabricated content; every claim about a source cited to
a fetched URL with honest unverified/unreachable ledgers.

## If your task conflicts with this file

Trust the source repo's `docs/development_plan.md` over this snapshot,
report the drift, and update this file in the same round.
