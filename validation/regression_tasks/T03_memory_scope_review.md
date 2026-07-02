---
id: TASK-T03-memory-scope-review
layer: validation
purpose: Regression task - spot memory overbuild and destructive-update
  violations in a proposed memory upgrade. Tests the append-only,
  five-file-contract, and standard-first disciplines.
read_when: Running harness regression validation, or calibrating a new model
  on ROUTE-memory-update.
depends_on:
  - ../../prompts/project_state_update_prompt.md
  - ../../rubrics/maintainability_rubric.yaml
used_by:
  - ROUTE-memory-update
tags: [regression-task, memory, overbuild, synthetic]
retrieval_keywords: [T03, memory overbuild, append only violation, memory
  scope regression]
---

# T03 — Spot the memory overbuild

**Instructions**: You are reviewing a proposed memory-layer upgrade under
ROUTE-memory-update. Apply the memory rules in
`../../prompts/project_state_update_prompt.md` and score with
`../../rubrics/maintainability_rubric.yaml` (MT-4, MT-6 are load-bearing). The
input below is a synthesized proposal containing planted violations.
Identify each, quote it, and give the compliant alternative.

## Input material (the proposal under review)

> ### Memory layer upgrade proposal (Phase 0 package)
>
> **M-1.** Add `memory/insights.sqlite` plus a
> `memory/embeddings/` vector store so the harness can do semantic recall
> over past analyses. Ship both inside the package so users get recall out
> of the box.
>
> **M-2.** Housekeeping: `correction_memory.jsonl` has accumulated entries
> whose underlying mistakes are now fixed — rewrite those lines in place to
> reflect the corrected understanding, and delete entries older than 90
> days to keep the file lean.
>
> **M-3.** Weekly consolidation job: fold `observation_log.jsonl` into
> `method_memory.yaml` by regenerating `method_memory.yaml` from scratch
> each week (drop the old entries; the regenerated file is the single
> source of truth).
>
> **M-4.** When a thesis changes, update the existing thesis line's
> `summary` and bump its `version` field in place — one line per subject
> keeps the file small.
>
> **M-5.** Add a new `memory/user_quirks.jsonl` file to track per-user
> preferences the package didn't anticipate; document its record shape in a
> comment at the top of the file.

## What to produce

1. Verdict: BLOCK / REVISE / PASS per RUBRIC-maintainability's verdict rule.
2. One finding per violation: proposal item, quoted phrase, the rule it
   breaks, the compliant alternative.
3. Identify anything in the proposal that expresses a legitimate need — and
   the correct channel for it (hint: friction entry feeding a standard
   revision, not a package-local invention).

The reference answer is `../expected_outputs/T03_expected.md`. Do not read it
until your answer is complete.
