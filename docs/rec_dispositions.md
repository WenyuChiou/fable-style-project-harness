---
id: DOC-rec-dispositions
layer: doc
purpose: Append-only operator disposition log for audit recommendations (REC ids) - each line records a human decision; the commit that adds a line carries the closure verb grep_history.py greps for.
read_when: Checking why a REC is closed, or recording a new human disposition (approve-keep, resolve-as-answered, reject).
depends_on:
  - ../scripts/grep_history.py
used_by: [operator-session]
tags: [doc, dispositions, adaptive-harness, append-only]
retrieval_keywords: [rec disposition log, closed recommendations, keep approved, resolved as answered, rejected recommendation]
---

# REC disposition log (append-only)

One line per human disposition. The COMMIT adding a line is the durable
closure record — its subject carries the `applies` / `resolves` verb (or a
`Harness-Outcome:` trailer) that `scripts/grep_history.py` treats as
closure. Bare mentions here close nothing; the log line without its verb
commit is not a closure.

| Date | REC | Disposition | Ground |
|---|---|---|---|
| 2026-07-14 | REC-20260706-034 | RESOLVED (question answered) | The rolling improvement loop's value question was answered by its own suggested test — the round-4 A/B (`benchmarks/harness_cases.yaml` case `ai_review_only_vs_ai_review_plus_adaptive_harness`, executed 2026-07-14, B-loses); the consequence shipped as REC-20260714-001 (linkage machinery retired, grep-history replaces it). Nothing left for this REC to decide. |
| 2026-07-14 | REC-20260706-014 | KEEP APPROVED | Operator affirmed the runner's Keep recommendation for the incident-born gate core (release trigger, scope assertion, stdout-redirect, orphan-pytest, staged-filecount rules in the operator harness). No file changes — approval closes the review question; the rules stay. |
