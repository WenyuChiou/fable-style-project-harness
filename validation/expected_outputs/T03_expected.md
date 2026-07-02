---
id: EXPECT-T03
layer: validation
purpose: Reference answer for T03_memory_scope_review - the overbuild and
  destructive-update violations that must be caught, and the legitimate needs
  that must be re-channeled.
read_when: Grading a model's answer to T03, never before attempting it.
depends_on:
  - ../regression_tasks/T03_memory_scope_review.md
  - ../../rubrics/maintainability_rubric.yaml
used_by:
  - ROUTE-memory-update
tags: [expected-output, grading-key]
retrieval_keywords: [T03 expected, memory review answer key]
---

# T03 expected output

## Required verdict

**BLOCK.** M-2 and M-4 are destructive memory edits (MT-6 at 1), which
triggers BLOCK mechanically. REVISE is a partial credit answer only if every
destructive item is individually blocked; PASS is an automatic fail.

## Violations that MUST be caught (all five items are violations)

| # | Item | Quoted offense | Rule broken | Compliant alternative |
|---|---|---|---|---|
| 1 | M-1 | "insights.sqlite ... vector store ... ship both inside the package" | Overbuild: MVP memory is file-based YAML+JSONL, "memory-ready, not a memory system"; new backends enter through the standard first; mutable state inside the versioned package self-destructs on regeneration | File a friction entry proposing the capability; keep Phase-0 memory as the five declared files; live state belongs outside the regenerable package |
| 2 | M-2 | "rewrite those lines in place ... delete entries older than 90 days" | Corrections append, never overwrite; correction_traceability requires the historical record to survive | Append new correction records referencing the old ones; staleness is a status flag, not a deletion |
| 3 | M-3 | "regenerating method_memory.yaml from scratch each week (drop the old entries)" | Destroys longitudinal state; prior conclusions are marked superseded/stale, not deleted | Consolidation may ADD entries and change status fields; version bumps with notes on why confidence changed |
| 4 | M-4 | "update the existing thesis line's summary ... in place" | Thesis records are never edited; a thesis is superseded by a NEW line with `supersedes` + `change_reason` | New JSONL line per version; old line's status becomes superseded |
| 5 | M-5 | "Add a new memory/user_quirks.jsonl ... shape in a comment" | "A conforming package must not silently invent extra memory files - new memory types enter through the standard first" (user_preference_memory is declared-but-deferred in the standard) | Friction entry proposing the memory type + record shape for a standard revision; until then, out of scope |

## Legitimate needs to re-channel (required for full credit)

- Semantic recall (M-1) and user preferences (M-5) are real needs; the
  correct channel is a friction entry with a stable id feeding a deliberate
  standard revision whose changelog cites it - not package-local invention.
- File-size hygiene (M-2/M-4's motive) is legitimate; the compliant
  mechanism is status flags and, if the standard later allows it, archival
  segments - never in-place rewrites.

## Automatic fails

- Verdict PASS.
- Missing #2 or #4 (the in-place rewrites - the core append-only rule).
- Endorsing the sqlite/vector store as a Phase-0 package addition.
