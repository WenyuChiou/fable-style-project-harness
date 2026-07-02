---
id: PLAYBOOK-phase0-static-package-standard
layer: playbook
purpose: Procedure for the Day-1 "spec-first static standard" phase — schemas and a static demo package before any automation, closed by an adversarial design-review panel.
read_when: Starting a new standard/spec-first project phase, or reviewing whether a Phase-0 build is complete and gate-ready.
depends_on:
  - ./pr_review_playbook.md
used_by:
  - ROUTE-phase-review
tags: [phase0, schemas-first, static-demo, design-review, spec-first]
retrieval_keywords: [day 1 build, static standard, schema first, static demo package, adversarial panel, spec v0.5.1, design review, phase gate]
---

# Phase 0 — Static package standard (schemas-first, static demo, adversarial panel)

**Status: REAL — executed as the Day-1 build** (commit `f4c826f`, spec v0.5.1 baseline) and closed by the 2026-07-01 design review (`docs/design_review_2026-07-01.md`).

## Goal

Define the package standard as machine-checkable schemas plus one hand-authored static demo package that instantiates every schema, BEFORE writing any generator, CLI, or automation. The static demo is the ground-truth fixture all later automation must regenerate (`docs/comparisons/generator_fixture_gate.md` §1 doctrine). Then subject the whole spec to an independent multi-lens adversarial review before first public exposure.

## Allowed work

- Repo skeleton, README, and normative docs (`docs/product_outputs.md`, `docs/evaluation_framework.md`, `docs/memory_strategy.md`, `docs/security_policy.md`, `docs/model_routing_policy.md`).
- The full schema set (the project shipped 10: harness, tool_card, evidence_card, capability_map, memory_policy, eval_spec, scorecard, model_routing_policy, methodology, guardrail_policy).
- ONE static demo package, hand-authored against the schemas, with real evidence and real guardrails — not lorem ipsum.
- Basic validation tests (schema validity, tree completeness) that run in CI-less pytest.
- Research PLANS for later phases (e.g. `docs/tool_discovery_research_plan.md`) — plans, not execution.
- A written acceptance checklist (spec 18.1 style, 10 binary criteria) checked item-by-item in `docs/development_plan.md`.

## Forbidden work

- Any compiler/generator code ("static-standard-before-compiler sequencing" — kept on the design review's all-lens keep list).
- Self-assessed quality numbers presented as measurements (this became design-review finding C2, "evaluation is a silent pass" — the exact fabrication pattern the project exists to prevent).
- Executing or installing anything discovered during research planning.
- Committing before the protective-policy layer exists (quote caps, non-affiliation, person policy — Tier A, commit `388f06e`, landed before first push).

## Required outputs

1. Schemas in `schemas/` with `$id`s and validation tests.
2. Static demo package satisfying the full canonical tree.
3. Development plan with phased checklist and explicit acceptance criteria.
4. A design-review report from an **independent adversarial panel run BEFORE first public exposure**. The project used four orthogonal lenses run independently and synthesized by the orchestrator: end-user journey simulation (×4 personas), positioning/competitive landscape with live web research, ruthless design skeptic, and trust/risk/ethics. Output shape: convergent-findings table with severity, a "what survives unchanged" keep list, a tiered change program (Tier A protective / Tier B structural / Tier C explicitly rejected), and a revised roadmap.
5. Ratification record: which Tier-B items the owner accepted (the project ratified B7 + B10 renames same-day; B1–B12 drove all later milestones).

## Acceptance criteria

- Every schema has at least one instance in the demo package and at least one validation test.
- The Day-1 checklist is fully checked with file-path evidence per item.
- The design review produced findings the builder did NOT already know (the panel found 34; 12 convergent across independent lenses — convergence across lenses is the credibility signal).
- Rejected changes are recorded WITH reasons (Tier C), not silently dropped.
- The demo clearly demonstrates the standard's differentiator (here: "harness package, not persona chatbot"), enforced in files, not only prose.

## Common failure modes

- **Phase order inverted** — proof and installability deferred to the end. The panel's C1 ("not installable anywhere — every persona's journey dies at minute five") forced the roadmap inversion: installability became the *next* milestone's exit criterion, not a Phase-5 deliverable.
- **Declarative eval with no runner** (C2): scorecard numbers nothing computed. Fix ratified as B2: run_evals is "the only Phase-0/1 code that matters".
- **Standard priced for adoption failure** (C7): ~45 mandatory files at N=1. Detection: count files a human actually touches vs. compiler intermediates.
- **Artifact-level legal exposure discovered late** (C4/C5: quote licensing, living-person naming). Prevention: the Tier-A protective sweep before ANY public exposure.
- **Naming that needs five "this is NOT" disclaimers** (C10) — rename while private is cheap (`4437320`), expensive after.

## Self-check checklist

- [ ] Are all schemas instantiated by the static demo, and does pytest prove it?
- [ ] Is there a written phased plan with binary acceptance criteria?
- [ ] Did an adversarial panel with orthogonal lenses review the spec BEFORE first exposure?
- [ ] Is every panel finding dispositioned (accepted-tier / rejected-with-reason)?
- [ ] Are protective/legal policies (quotes, naming, subject policy) in place before the first push?
- [ ] Is anything claiming a quality score that nothing computed? If yes, stop — that is finding C2.
