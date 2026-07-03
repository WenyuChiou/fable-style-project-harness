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

**Snapshot date:** 2026-07-02 · **HEAD:** `801ce17` (chore: gitignore CLAUDE.local.md) · **Standard version:** v0.7.1 · **Visibility:** private
(open-source-ready; MIT + NOTICE carve-out; no badges while private)

## Health

- **Test suite:** 730 passing (last stated in 91b982b; growth: 98 → 114 →
  299 → 335 → 369 → 392 → 555 → 629 → 638 → 730)
- **CI:** `.github/workflows/ci.yml` — ubuntu + windows × py3.11/3.13, full
  pytest + `phc validate` on all three packages (added in 7134227)
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
  adapters, fixture-regeneration gate with pinned floors)
- **Phases 3, 4, 6** not started · **Phase 5** PARTIAL (Claude Code export de
  facto shipped; Codex = documented manual path; MCP config export not started)

## Honestly-still-open gate arms / obligations

- N=2 gate **arm (a)**: blinded-grader full §15.5 suite — never attempted
- Pre-registration **commit-before-runs** protocol: declared (5d96fd6), not
  yet exercised on a new round
- `outcome_tests` eval-spec group (N3-F2) and outcome subtree completeness
  gate (N3-F3) — open while Category 7 is a pilot
- Accepted-unresolved friction backlog: N=2 F4-F7/F9-F13 remainder + N=3
  N3-F5..F9, F16-F22 (see `docs/n2_gate_report.md` resolution tables)

## Next candidates (from development_plan.md open boxes)

1. Second-wave adapters: FindSkills + GitHub SKILL.md search
2. Tool-fit scorer refinement (beyond `rank_score`) + model router;
   ModelRoutingPolicy semantic validation wired into the runner
3. Phase 3: evidence-card builder / principle extractor / attribution
   classifier
4. Phase 4: memory tooling (contradiction update, stale-claim detection)
5. N=2 arm (a) blinded full-suite behavioral eval
6. Full (non-pilot) Category-7 run per pilot report §6
7. Phase 6 public release (repo flip, technical article, audit wedge launch)

## Standing constraints

Never commit `agent_harness/` (gitignored, 965c68e). No fabricated evidence;
TODO_FILL fails validation. Discovered tools are never executed. Repo goes
public only on the owner's word.

## Session-close note (2026-07-02, Fable -> Opus handoff)

- This harness itself shipped and was wired GLOBALLY this session: thin
  pointer skill `~/.claude/skills/fable-harness/`, global CLAUDE.md section
  (user-authorized), `CLAUDE.local.md` in the main repo, codebase-memory
  index live. First real consumer expected: an Opus session continuing the
  main project.
- Main-project state is UNCHANGED since `91b982b` (the two commits after it
  are gitignore guards only). Next candidates: M2c Phase 3 evidence
  extraction (fabrication risk -> code gates), B3 blinded full-suite arm,
  Phase 4 longitudinal memory exercise, ai-berkshire article (user review
  first), public flip (user's word).
