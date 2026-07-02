---
id: PLAYBOOK-phase2-builder-primitives
layer: playbook
purpose: Procedure for building the first automation over a hand-authored standard — deterministic-first generators, TODO-on-uncertainty, non-destructive drafts, offline-fixture adapters, and a falsifiable fixture-regeneration gate.
read_when: Building generators/adapters that automate any part of a previously hand-authored artifact, or reviewing generator coverage claims.
depends_on:
  - ./phase1_tool_discovery.md
  - ./phase6_evaluation_runner.md
  - ./pr_review_playbook.md
used_by:
  - ROUTE-phase-review
  - ROUTE-eval-design
tags: [generators, deterministic-first, TODO_FILL, fixture-gate, offline-fixtures, regression-floors]
retrieval_keywords: [M2b, builder primitives, generated.yaml, fixture regeneration gate, link_recall, TODO_FILL stub, offline fixture, monkeypatch network, regression floor, never guess]
---

# Phase 2 — Builder primitives (deterministic generators + fixture-regeneration gate)

**Status: REAL — executed as M2b on 2026-07-02** (commit `91b982b`; `docs/comparisons/generator_fixture_gate.md`; convention ratified as standard v0.7.1 in `docs/CHANGELOG_STANDARD.md`).

## Goal

Ship the first automation (generators + registry adapters) over the hand-authored standard, and **measure it against the shipped hand-authored packages with deterministic metrics before trusting it** — the fixtures-regeneration gate. Automation must never fabricate judgment: structure is generated; judgment is handed to the human as an explicit stub.

## Allowed work

- **Deterministic-first (tier-0) generators**: no LLM, no network inside any generator. Heuristics are DOCUMENTED and numbered (H1–H5 capability classes; G1–G6 grader inference, action-text-only because condition text quotes banned artifacts and misleads).
- **TODO-on-uncertainty**: anything unclassifiable emits an explicit `TODO_FILL` stub (e.g. `cap_TODO_FILL_unclassified`), never a guess. An unclassifiable grader key becomes an honest `manual`, never an invented key.
- **Non-destructive output**: generators write sibling `<name>.generated.yaml` DRAFTS, never a governed filename; refuse to overwrite without `--force`; promotion from draft to governed file is a HUMAN act (review, fill every TODO_FILL, rename). Validation fails on unfilled markers BY DESIGN, so a package holding unpromoted drafts cannot validate.
- **Registry adapters with offline fixture mode**: one live probe per adapter recorded as a fixture; e2e tests monkeypatch HTTP to RAISE so CI can never hit the network.
- **Computed risk from conservative proxies**: no registry publishes permission/risk taxonomy, so `permission_level`/`risk_level` are computed from documented proxy signals (isSecret credentials, hosting attrs, transports, provenance-with-documented-semantics only); unknown ⇒ conservative `medium` + `read_only ASSUMED UNVERIFIED`; every rule emits a `risk_basis` line. All drafted cards carry `verification_status: unverified_auto_draft`.
- **The falsifiable gate**: a reproducible script (`scripts/generator_gate.py`) that IMPORTS the generators' own coverage functions (no forked scoring logic) and measures recovery against every shipped package; a report stating numbers with named misses; regression floors pinned in tests at measured − tolerance.

## Forbidden work

- LLM calls or network access inside generators or their tests.
- Overwriting governed files, or shipping `.generated.yaml` drafts inside shipped packages (gate drafts go to scratch and are deleted after measurement; verified count 0).
- Inventing a pass threshold for the gate ("no pass threshold is invented here: the numbers are stated and the maintainer sets the bar").
- Gaming a metric the heuristics legitimately can't reach: the domain-core capability of each package systematically lands in the TODO bucket because naming it IS human judgment — "reportable result, not something to game".
- Installing or executing anything an adapter discovers (spec 9.5 remains binding).

## Required outputs

1. Generators + adapters with documented, numbered heuristics.
2. Gate report with per-package deterministic metrics (the project's headline: link_recall 0.69/0.88/0.50, link_presence 1.0×3, rule_skeleton_coverage and rule_test_recall 1.0×3, grader_agreement 0/1 · 3/3 · 1/1 where the 0/1 is an honest manual, not a conflicting key) — every miss NAMED, with the pattern explained.
3. Regression-floor tests so future changes cannot silently regress below measured values.
4. A stronger safety property tested where possible (e.g., "a generated grader key never CONFLICTS with a shipped one").
5. Changelog entry ratifying any new conventions at the standard level (v0.7.1 `.generated.yaml` convention).

## Acceptance criteria

- Gate numbers reproduce byte-for-byte when a reviewer re-derives them by hand (the M2b gate-honesty reviewer did exactly this).
- Coverage misses are enumerated by id, and the miss pattern is diagnosed (here: every named miss was a domain-core-capability link — the human-judgment core).
- The report states its own validity limit: measured on fixtures the heuristics were debugged against ⇒ "regression floors, not validated generalization; the honest next falsification is an N+1 package authored blind to the heuristics".
- Reviewer findings fixed before merge (the correctness reviewer's P1 — recommend-tools bypassing the shared overwrite guard — was fixed in the same round).

## Common failure modes

- **Reaching for an LLM where a deterministic heuristic + honest TODO would do** — destroys reproducibility and auditability of the gate.
- **Generator silently overwrites human work** — the P1 actually caught in review; route ALL writers through one shared overwrite guard.
- **Coverage metric defined post hoc to look good** — prevented by importing the shipped coverage functions and publishing metric definitions in the report.
- **Fixture leakage into shipped artifacts** — enforce "shipped packages carry no drafts" with a test.
- **Treating debugged-against-fixtures numbers as generalization** — always schedule the blind N+1 falsification.

## Self-check checklist

- [ ] Zero LLM / zero network in generators and tests (network monkeypatched to RAISE)?
- [ ] Does every uncertain classification emit TODO_FILL / honest-manual instead of a guess?
- [ ] Are outputs non-destructive drafts requiring human promotion?
- [ ] Is risk computed from documented conservative proxies with a per-rule basis?
- [ ] Does the gate report name every miss and state numbers without an invented bar?
- [ ] Are the measured numbers pinned as regression floors in tests?
- [ ] Did I state what these numbers do NOT prove?
