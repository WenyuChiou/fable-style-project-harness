---
id: PROMPT-project-state-update
layer: prompt
purpose: Instruction for updating the harness's memory/ files after completing
  work - append-only, friction-fed, changelog-linked - mirroring the repo's
  observable memory discipline.
read_when: After any task that changed project state, produced a decision, hit
  friction, or corrected an earlier record.
depends_on:
  - ../rubrics/maintainability_rubric.yaml
used_by:
  - ROUTE-memory-update
  - ROUTE-repo-maintenance
tags: [memory, state-update, corrections, friction]
retrieval_keywords: [update memory, record decision, log friction, correction
  record, after task, append only]
---

# Project state update prompt

After finishing work, bring `../memory/` up to date. Memory is how the next
session (or a weaker model) starts smart. Follow these rules exactly.

## Rules

1. **Append, never overwrite.** JSONL streams get new lines; a new line that
   changes a conclusion references the record it supersedes
   (`supersedes: <id>`, `change_reason: new_evidence | contradiction |
   correction | revalidation`). YAML state files are read-modify-write as
   documents, but prior conclusions are marked `superseded` / `stale`, not
   deleted.
2. **Corrections are first-class records.** If you (or a review) found
   something the harness previously got wrong, write a correction entry that
   links back to the wrong record. Never edit the wrong record in place —
   correction_traceability is a tested property, not a style preference.
3. **Friction feeds the standard.** If you chafed against a schema, template,
   rubric, or convention while working, record it as a friction entry with a
   stable id (the N2-F* / N3-F* pattern): where it chafed, the workaround
   used, the recommended revision. Do NOT fix the standard inline — friction
   entries are consumed by a later, deliberate revision whose changelog entry
   cites the friction ids it resolves.
4. **No memory sprawl.** Do not invent new memory files, backends, or record
   shapes. New memory types enter through the standard first. If an update
   doesn't fit any existing file, that is itself a friction entry.
5. **Record skips honestly.** If you could not update something (missing
   information, out of scope), record THAT — an explicit "not updated
   because ..." line — rather than leaving silence.

## Procedure

1. List what changed in this session: decisions made, artifacts produced,
   corrections found, friction hit.
2. For each, pick the target memory file per its documented record shape and
   append/update per the rules above.
3. Give every new record a stable id and today's date; link evidence by id or
   repo path (a memory claim with no source artifact is a fabrication risk).
4. Close with a one-line summary in your final answer: which memory files
   changed, how many records appended, any friction ids created.
