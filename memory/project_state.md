---
id: MEM-project-state
layer: memory
purpose: Current-state snapshot of method-harness-compiler — HEAD, suite, packages, phase statuses, open gate arms, next candidates. Rewritten at every session close.
read_when: At session start, before planning any work; before quoting any status number.
depends_on:
  - ./phase_history.jsonl
  - ./accepted_decisions.jsonl
used_by:
  - ROUTE-phase-review
  - ROUTE-memory-update
  - ROUTE-repo-maintenance
tags: [state, snapshot, status]
retrieval_keywords: current state, HEAD, test count, packages shipped, phase status, open items, next candidates
---

# Project State — method-harness-compiler

**Snapshot date:** 2026-07-06 · **HEAD:** `0b8e4f8` (eval: N=2 gate v2 RUN → NULL on both claims) · **Standard version:** v0.7.1 · **Visibility:** private
(open-source-ready; MIT + NOTICE carve-out; no badges while private)

## Health

- **Test suite:** 768 passing, 2 skipped (571e9de; growth: 98 → … → 747 →
  759 → 768)
- **CI:** green — `.github/workflows/ci.yml` — ubuntu + windows × py3.11/3.13,
  full pytest + `phc validate` on all three packages (added in 7134227)
- **E2E:** fresh-user plugin install + headless `/analyze-company` verified
  end-to-end (`docs/quality/fresh_user_walkthrough.md`); honest UNVERIFIED
  list kept (interactive flow, GitHub-form add while private)

## Shipped packages (3)

| Package | Anchor | Notes |
|---|---|---|
| `examples/quality_value_investing_harness` | person-anchored (Duan Yongping as cited evidence subject, methodology-first name) | first demo; CJK aliases governed |
| `examples/manuscript_review_harness` | methodology-anchored (no person; `institutional_corpus`) | N=2 gate package; Category-7 outcome pilot lives here |
| `examples/first_principles_engineering_harness` | person-anchored, attribution-stress corpus | N=3 package, built via `phc new` dogfood |

## Phase status (per docs/development_plan.md)

- **Phase 0** DONE · **M1a / M1b / M1c** DONE · **M1d** executed as PILOT
  (proof-of-instrument, no accuracy claim) · **N=3** SHIPPED
- **Phase 1 (as M2a)** DONE — 27 sources scored metadata-only, 7 honest
  unscored stubs
- **Phase 2** research prefix DONE; **M2b first-wave builder primitives
  SHIPPED** (generate capability-map / eval-spec, recommend-tools, 3 registry
  adapters, fixture-regeneration gate with pinned floors); **BOTH second-wave
  registry adapters SHIPPED (FindSkills b1310b5 + GitHub SKILL.md search
  41842ce)** — recommender consumes ALL_ADAPTERS (5 adapters);
  **ModelRoutingPolicy runner wiring SHIPPED (89e503b)**; **tool-fit-scorer
  refinement SHIPPED (571e9de)**. ALL unblocked Phase-2 items DONE; only
  OPTIONAL leftover: a full model-router (task→tier dispatch)
- **Phase 3 NO_GO** (entry work order `2ad438b` exists; ARCH-1 condition
  failed — see gate arms below) · **Phases 4, 6** not started · **Phase 5**
  PARTIAL (Claude Code export de facto shipped; Codex = documented manual
  path; MCP config export not started)

## Honestly-still-open gate arms / obligations

- N=2 gate — **BOTH the original (arm a) and the revised (v2) gate RAN and
  returned NULL**. arm (a) (`26d24df`): harness 6/6 vs persona 5/6, the ≤2/6
  persona assumption miscalibrated. **gate v2 (`0b8e4f8`, thresholds
  owner-ratified `38b1748` before the run)**: three-arm groundedness —
  PRODUCT (C vs A) NULL Δ=0.33 < 0.7; **STRUCTURE (C vs B) NULL Δ=0.17 <
  0.3 — the harness is empirically "data + packaging, not structure"**
  (persona + same evidence list 1.83 ≈ harness 2.00; means A=1.67 / B=1.83 /
  C=2.00; no veto). **The central "compiled harness beats a naive prompt"
  claim is NOT SUPPORTED by two independent blinded evals.** This is now a
  STRATEGIC finding, not a "try a third gate" item.
  (`docs/evals/n2_gate_v2_runs/report.md`)
- Pre-registration **commit-before-runs** protocol: declared (5d96fd6),
  exercised on both gate runs (prompts frozen 795b381 before arm (a);
  v2 thresholds frozen 75f503b + ratified 38b1748 before the v2 run)
- `outcome_tests` eval-spec group (N3-F2) and outcome subtree completeness
  gate (N3-F3) — open while Category 7 is a pilot
- Accepted-unresolved friction backlog: N=2 F4-F7/F9-F13 remainder + N=3
  N3-F5..F9, F16-F22 (see `docs/n2_gate_report.md` resolution tables)

## Next candidates (from development_plan.md open boxes)

1. **TOP PRIORITY — STRATEGIC DECISION (human).** Both gates ran NULL; gate
   v2 (`0b8e4f8`) showed harness ≈ persona + evidence list, so the "compiled
   harness beats a naive prompt" claim is NOT supported. The honest fork
   (from `n2_gate_v2_runs/report.md` §What-this-feeds): (a) reposition the
   product around the evidence/policy BUNDLE it demonstrably provides + drop
   the structure claim; (b) test a DIFFERENT value axis the behavioral gates
   don't reach (outcome correctness — does grounding improve accuracy?;
   auditability at scale; consistency across many authors); or (c) accept
   the null. Do NOT build a third behavioral gate. **Pending the human.**
2. Phase 3 (evidence extraction): entry work order at `2ad438b` — **NO_GO**
   (ARCH-1). M3a–M3e stay BLOCKED until the strategic decision + whatever
   re-cleared gate it implies, then §8 resolution
3. OPTIONAL Phase-2 leftover: full model-router (task→tier dispatch)
4. Phase 4: memory tooling (contradiction update, stale-claim detection)
5. Full (non-pilot) Category-7 run per pilot report §6
6. Phase 6 public release (repo flip, technical article, audit wedge launch)

## Standing constraints

Never commit `agent_harness/` in the source repo (gitignored, 965c68e — the
old nested harness clone there is retired; this standalone repo is the
harness's home). No fabricated evidence; TODO_FILL fails validation.
Discovered tools are never executed. Repo goes public only on the owner's
word.

## Session-close note (2026-07-06, memory reconciliation)

- PH-019..PH-028 were ported VERBATIM from the retired old clone's
  uncommitted worktree
  (`method-harness-compiler/agent_harness/fable_style_project_harness`)
  into this repo's `phase_history.jsonl` (18 → 28 records, all
  JSON-verified). This file and L2 were rewritten past even the old
  worktree's snapshot to the verified state at source HEAD `0b8e4f8`.
- The old clone's dirty state is now fully captured here; it is safe for
  the orchestrator to retire that clone.
