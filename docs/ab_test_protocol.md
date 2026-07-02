---
id: DOC-ab-test-protocol
layer: doc
purpose: Pre-registered design for testing whether this harness improves agent performance — FUTURE WORK, not to be run in this milestone
read_when: Designing the harness-effectiveness experiment, or asked whether the harness "works"
depends_on: [context/L1_project_constitution.md, context/L2_current_phase.md, docs/retrieval_smoke_test.md]
used_by: [ROUTE-ab-test-design]
tags: [ab-test, evaluation, future-work, pre-registration, baseline]
retrieval_keywords: [A/B test, arms, research question, baseline comparison, harness effectiveness, experiment design, future work]
---

# A/B Test Protocol — Harness Effectiveness (FUTURE WORK)

> **STATUS: EXPLICITLY FUTURE WORK. This protocol is a design record only
> and MUST NOT be run in this milestone.** Running it before the harness
> content lanes are complete and the retrieval smoke test passes would
> measure an unfinished artifact. The source project's own discipline
> applies: pre-registration BEFORE any run, and the design published
> before results exist (the Category-7 precedent, commits `5d96fd6` →
> `2917804`).

## Research question

Does an agent operating on `method-harness-compiler` tasks with this
progressive-disclosure harness produce measurably better outcomes —
method adherence, correctness, honesty behaviors, and token cost — than
the same agent with (a) no harness at all, or (b) the same distilled
content delivered as a flat full-context dump?

Secondary question: does index-backed retrieval (codebase-memory MCP) add
anything over grep-based retrieval of the same files?

## Arms

| Arm | Condition | What it isolates |
|---|---|---|
| **A — baseline** | No harness. The agent gets the task and raw access to the source repo only. | The floor: unaided model + repo. |
| **B — flat dump** | The FULL harness content concatenated into context up front (no routing, no progressive disclosure). | Content value without the disclosure discipline — is layering doing work, or just the words? |
| **C — progressive-disclosure harness** | This repo as designed: L0 entry, L2 phase check, L3 routing, route-scoped loading. | The product under test. |
| **D — optional** | Arm C plus a codebase-memory index of this repo (per `docs/codebase_memory_indexing.md`). | Marginal value of semantic retrieval over grep-by-ID. |

Same model, same task set, same tool access (minus the index in A–C),
fixed temperature/config across arms. Arm order randomized per task.

## Task set (to be pinned at pre-registration time)

Representative tasks drawn from the 8 routes — at minimum one per route,
grounded in real source-repo episodes with known-correct behavior (e.g.
"a schema edit is proposed mid-N-gate: what do you do?" — the observable
correct answer is record-friction-don't-edit). The task set, per-task pass
criteria, and grader keys must be **pre-registered before any model call**
and never altered after runs begin (pass criteria fixed; grader BUG fixes
allowed with documentation — the Category-7 precedent distinguishes the
two).

## Metrics

1. **Method adherence** — did the agent restate/classify/check phase
   before acting; did it halt where L2 forbids; did it route correctly
   (gradeable against `RE-###` routing examples)?
2. **Outcome correctness** — deterministic per-task graders where
   possible; blinded human grading where not (the still-open N=2 arm (a)
   teaches: deterministic-subset grading is honest but must be labeled as
   a subset).
3. **Honesty behaviors** — UNSCORED-instead-of-guessed, published
   failures, no fabricated citations.
4. **Cost** — tokens read (context loaded) and tokens generated, per arm.
   The core progressive-disclosure claim is C ≈ B on quality at a
   fraction of B's read cost, both > A.

## Reporting rules (inherited verbatim from the source method)

- Results are a **computed artifact** emitted by a script, never
  hand-edited numbers.
- Every unmeasured cell is UNSCORED with a reason; defective runs are
  preserved and reported alongside operative runs, never discarded.
- A null or negative result is publishable — if C does not beat B, that
  finding feeds a harness revision (via `ROUTE-memory-update` +
  changelog-with-friction-IDs), not a quiet re-run.
- No capability claims from pilot-sized n; the first run is a
  proof-of-instrument.

## Preconditions before this may run

1. All harness lanes complete; `docs/retrieval_smoke_test.md` passes
   (no CONDITIONAL absences in probes the tasks depend on).
2. Task set + pass criteria + grader pre-registered and committed.
3. A human ratifies the run (same gate class as a phase transition).
