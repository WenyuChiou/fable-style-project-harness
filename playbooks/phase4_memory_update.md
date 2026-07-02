---
id: PLAYBOOK-phase4-memory-update
layer: playbook
purpose: Procedure for file-based longitudinal memory — append-only JSONL, contradiction/staleness/correction semantics, and on-disk verification of memory writes.
read_when: Designing, implementing, or verifying memory-update behavior; handling contradictions or corrections in any longitudinal store.
depends_on:
  - ./phase6_evaluation_runner.md
used_by:
  - ROUTE-memory-update
  - ROUTE-phase-review
tags: [memory, append-only, jsonl, contradiction, staleness, correction, on-disk-verification]
retrieval_keywords: [memory policy, thesis memory, correction memory, append only, supersedes, contradiction update, stale claim, freshness window, memory write verified on disk]
---

# Phase 4 — Memory and longitudinal updates (policy REAL; automation prospective)

**Status: MIXED.** The memory *policy layer* and record contracts are real and shipped (`docs/memory_strategy.md`; five memory files in every package), and a real end-to-end memory-write verification episode exists (`docs/quality/fresh_user_walkthrough.md` §5, commit `7134227`). The Phase-4 *automation* items (programmatic JSONL store, memory update command, contradiction/stale-detection code) are ⬜ NOT STARTED per `docs/development_plan.md` — those parts below are prospective, grounded in the shipped policy.

## Goal

Give the system longitudinal memory that is human-readable, versionable, testable, and auditable: YAML for slowly-changing curated state, append-only JSONL for event streams. Corrections and contradictions are first-class records, never silent edits — "this is what makes error handling testable".

## Allowed work

- Appending new records: a thesis revision is a NEW line with incremented `version` and a `supersedes` pointer; exactly one version per subject has `status: active`.
- Contradiction handling in the required order: (1) log the incoming item in the observation log with `triggers_update: true` and `relates_to` pointing at the contradicted record; (2) choose exactly one of reduce-confidence (new version, `change_reason: contradiction`) or create-correction (if the prior record was *wrong*, not merely weakened); (3) leave the contradicted record in history as `superseded`.
- Staleness flagging: when `last_validated`/`last_checked` exceeds the freshness window, set `status: stale` (never delete); outputs relying on a stale claim must surface the staleness or trigger revalidation.
- Correction records: append to `correction_memory.jsonl` with `corrects`, `error_type`, `detected_by`, and `resulting_record_ids`; a later change of mind about a correction is itself a NEW correction.
- Cross-reference integrity: every id referenced in a memory record must resolve to a real record — deterministically checkable (tier 0).

## Forbidden work

- Editing or deleting existing JSONL lines — ever. History is never rewritten; state changes are new lines.
- Orphan evidence: a new observation must attach to an existing claim or spawn a new one ("no orphan evidence").
- Inventing extra memory files ad hoc: "new memory types enter through the standard first", not through a single package.
- Storing mutable memory where regeneration clobbers it (design-review C8: mutable state inside the versioned regenerable package self-destructs; B5 ratified splitting immutable package from per-user state).
- Making a memory service (MCP, vector DB) a REQUIRED dependency: files remain the source of truth for audit; richer backends must round-trip the file shapes.

## Required outputs

1. `memory_policy.yaml` declaring backend + the four update-policy rules (link-or-create; contradiction⇒reduce-or-correct; stale⇒flag; major-update⇒versioned entry).
2. Record shapes for the five files (method_memory, source_memory, thesis_memory, observation_log, correction_memory) — the stable contract any future backend must honor.
3. Memory tests covering: write, retrieval, contradiction_update, stale_claim_revalidation, correction_traceability.
4. **On-disk verification of real writes** — the real episode to replicate: after a full headless workflow run, the appended JSONL records were read back from disk and matched the run's self-report exactly (+1 thesis version, +5 observations, seed records preserved, append-only confirmed), then the test writes were reverted to restore the pristine seed state. A memory feature is not "verified" by the agent's claim that it wrote; it is verified by reading the files.
5. (Prospective, Phase-4 proper) code that enforces the invariants instead of convention — same shapes, no schema change.

## Acceptance criteria

- Every memory mutation in a test scenario is observable as appended lines; diffing the files shows appends only.
- From any current claim, one can walk back through versions and corrections to the original assertion (correction_traceability).
- Contradiction is never silently ignored and never silently overwritten.
- Eval runs never mutate live memory except in an isolated scratch area; verification episodes revert their writes.
- Package regeneration/upgrade does not destroy accumulated memory (the C8/B5 requirement).

## Common failure modes

- **Silent overwrite of a contradicted thesis** — the exact anti-pattern the append-only invariant exists for; caught by the contradiction_update test.
- **Deletion as staleness handling** — staleness changes `status`, never deletes; deletion destroys the audit trail.
- **Memory claims verified only by self-report** — the walkthrough discipline is read-the-disk; an agent's "I updated memory" is a claim, not evidence.
- **Naming drift across domains producing dangling references** — real N=2 incident: the standard's `thesis_memory.jsonl` vs the domain-natural `review_memory.jsonl` produced a dangling reference in HARNESS.yaml/SKILL.md, caught at integration (friction F4). Prevention: pin memory file names against the manifest with tests.
- **Ungoverned record shapes diverging across packages** (F4's second half: `company` vs `manuscript` fields with nothing machine-checking either) — record shapes need a contract, or at minimum a NAMING NOTE plus pinning tests.

## Self-check checklist

- [ ] Are all JSONL changes appends (no edits, no deletions)?
- [ ] Does every update follow one of the four policy rules, recorded with `change_reason`?
- [ ] Is exactly one thesis version per subject `active`?
- [ ] Did I verify writes by reading the files on disk, and revert test writes?
- [ ] Do all referenced ids resolve?
- [ ] Would a package upgrade preserve this memory?
