---
id: EXAMPLE-bad-overengineered-plan
layer: example
purpose: NEGATIVE example — a development plan that defers proof to the end, prices the standard for adoption failure, and has no falsifiable gates.
read_when: Calibrating what NOT to accept in a plan; paired critique explains each violation.
depends_on:
  - ../critiques/critique_bad_overengineered_plan.md
used_by:
  - ROUTE-phase-review
  - ROUTE-eval-design
tags: [negative-example, overengineering, plan, no-gates, synthetic]
retrieval_keywords: [overengineered plan, big design up front, deferred validation, no gate, phase order inverted, framework first]
source_artifact: synthesized (violations mirror the real anti-patterns named in docs/design_review_2026-07-01.md C1/C2/C7)
synthetic: true
---

> **NEGATIVE EXAMPLE — do not imitate.** This plan is synthesized to violate specific
> decision rules. See `../critiques/critique_bad_overengineered_plan.md`.

# Development Plan: Universal Expert Compiler Platform (v1.0)

## Vision

Build the definitive, fully general platform for compiling any expert's methodology into
any agent runtime. The architecture must be complete before any package ships, so that
nothing has to be reworked later.

## Phase 1 (Months 1-3): Core abstraction layer

- Design 14 core abstractions (ExpertModel, MethodGraph, EvidenceLattice,
  CapabilityMatrix, ToolMesh, MemoryFabric, RoutingKernel, ExportPipeline, ...).
- Author 22 JSON schemas covering every conceivable domain up front.
- Define the 61-file canonical package tree. All files mandatory — partial packages
  would fragment the ecosystem.
- Build the plugin SDK, the theme system, and the multi-tenant registry service.

## Phase 2 (Months 4-6): Compiler internals

- Implement all 30 `src/` modules against the abstraction layer.
- Build the LLM-powered auto-extraction pipeline that reads an expert's collected works
  and generates the full package automatically. Accuracy will be validated in Phase 5.

## Phase 3 (Months 7-8): Integrations

- Adapters for 12 registries, 6 runtimes, 4 vector databases, and a Kubernetes operator
  for horizontal eval scaling.

## Phase 4 (Month 9): First demo package

- Generate the first demo package using the Phase-2 pipeline. Since the pipeline
  implements the schemas, the demo will conform by construction — no separate
  validation pass needed.

## Phase 5 (Month 10): Evaluation & launch

- Write the eval framework. Scores will be filled into the scorecard based on the
  team's assessment of each dimension.
- Public launch with all 12 registry integrations live.

## Success criteria

- Architecture praised as "complete and general".
- The platform supports every future domain we can imagine.
- Launch generates community excitement.

## Risk management

- Risk: scope. Mitigation: the team is experienced.
- Risk: schedule. Mitigation: phases can overlap if needed.

*(No install path exists until Month 10. No package is authored by hand against the
schemas before the compiler generates one. No gate can fail: every phase ends when its
artifacts are "complete", as judged by the authors.)*
