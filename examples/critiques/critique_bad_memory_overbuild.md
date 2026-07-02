---
id: CRIT-memory-overbuild
layer: example
purpose: Critique of bad_memory_overbuild.md — seven backends on day 1, overwrite-on-contradiction, ungoverned record shapes; with the file-based correction.
read_when: You read the memory overbuild example, or a design proposes retrieval infrastructure before records exist.
depends_on:
  - ../bad/bad_memory_overbuild.md
  - ../../datasets/failure_modes.yaml
used_by:
  - ROUTE-memory-update
  - ROUTE-phase-review
tags: [critique, memory, append-only, premature-infrastructure]
retrieval_keywords: [memory critique, vector db premature, append only correction record, overwrite contradiction, record schema, package state split]
synthetic: true
---

# Critique: bad_memory_overbuild.md

## Violations

1. **Seven backends before the first record** violates DR-008
   (deterministic/cheap-first) and DR-003 (no falsifiable need demonstrated — nothing
   gates the build). The observed method ships `storage_backend: yaml_jsonl` — plain
   files — and its weekly memory loop runs on them; infrastructure is earned by recorded
   friction, not anticipated (the entire v0.6/v0.7 standard evolved ONLY from
   friction-report IDs).
2. **"Newer record overwrites the older one" on contradiction** is the cardinal memory
   violation — DR-009 (corrections append, never overwrite). The real update_policy:
   `contradictory_evidence_must_reduce_confidence_or_create_correction` and
   `major_updates_must_create_versioned_entry`; `mem_t05` tests that correction records
   replay into a gap-free audit chain. Hard-deleting near-duplicates destroys the same
   audit trail (FM-012-adjacent).
3. **No record shapes, "find its shape organically"** — the real N=2 gate flagged
   ungoverned JSONL record shapes as friction F4 even WITH a single backend; seven
   backends multiply FM-017 (dangling/dangling-shape references) with nothing
   machine-checking any of them.
4. **Memory inside the versioned, regenerable package** reproduces FM-012
   (memory-clobber-on-regeneration) — the real review's C8: "regeneration clobbers the
   one feature that brings users back weekly"; the ratified fix splits immutable package
   from mutable per-user state.
5. **"No way to test memory before there are users"** — false by demonstration:
   the real suite tests memory write validity, retrieval faithfulness ("no fabricated
   history"), contradiction handling, staleness flagging, and correction traceability
   (mem_t01..t05) against on-disk fixtures; violates RUBRIC-eval-design and DR-003.
6. **$800/mo idle infra + 6 weeks to first record** — scope creep (FM-009) with the
   moat argument doing the work evidence should do (RUBRIC-scope-discipline).

## Corrected approach (5-10 lines)

```text
1. Day 1: YAML/JSONL files per memory type, declared in the manifest;
   zero servers.
2. Update policy as data: link-or-create, reduce-confidence-or-correct,
   flag-stale, versioned major updates — append-only throughout.
3. Ship mem_t01..t05-style tests WITH the memory feature (write validity,
   faithful retrieval, contradiction => correction record, staleness,
   gap-free replay).
4. Keep mutable state OUT of the regenerable package (per-user state dir);
   memory survives upgrades by rule.
5. Add retrieval infrastructure only when a recorded friction item says
   file scan is failing — and gate it on a measured baseline.
```
