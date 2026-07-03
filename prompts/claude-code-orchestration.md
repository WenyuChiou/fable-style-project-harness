---
id: PROMPT-claude-code-orchestration
layer: prompt
purpose: "Complex-task / phase-gated planning prompt for Claude Code Opus + distilled: phases, executor split, stop conditions, rollback, verification gates, commit boundaries."
read_when: A task is large / multi-phase / multi-agent and needs an orchestration plan before execution.
depends_on:
  - ../core/workflow_orchestration_playbook.md
  - ../operating_model/review_protocol.md
  - ../operating_model/phase_gates.md
  - ../operating_model/decision_rules.yaml
used_by:
  - DOC-agent-optimization-runbook
  - claude-code-runtime
tags: [prompt, claude-code, orchestration, phases, multi-agent]
retrieval_keywords: [orchestration plan, phases executor split, stop conditions rollback, verification gates commit boundaries, phase gated planning]
---

# Claude Code Orchestration Prompt (Opus + distilled)

**Purpose.** Produce an execution-ready orchestration plan for a large / multi-phase /
multi-agent task BEFORE any lane runs code. This is the tier-3 strong_reasoning
orchestration lens: it turns one big goal into parallel lanes over disjoint file sets,
assigns each lane an executor surface, and keeps the single-owner guarantees
(verified state, honest numbers, one coherent commit) that
[`../core/workflow_orchestration_playbook.md`](../core/workflow_orchestration_playbook.md)
(CORE-workflow-orchestration-playbook) mandates.

**Provenance.** This artifact encodes the operator's Hermes / Claude Code / Codex stack
(source: model-routing-benchmark `universal_agent_optimization_prompt.md`) bound to this
harness's existing doctrines cited inline; it is NOT distilled from method-harness-compiler.
Concrete surface bindings (Hermes ~ cheap_fast operator; Claude Opus + distilled ~ tier-3
orchestration; Codex ~ balanced mechanical executor) come from `docs/agent-routing-policy.md`
(DOC-agent-routing-policy). The quality invariant is the author-agnostic layered review gate
in [`../operating_model/review_protocol.md`](../operating_model/review_protocol.md)
(OM-review-protocol), not routing everything to the strongest surface.

**When NOT to orchestrate.** Trivial single-file edits, conversational Q&A/advice, and
tight user-iteration or live-state debugging — do those directly; a context-blind lane costs
more than it saves (see workflow_orchestration_playbook.md §"When NOT to orchestrate").

---

## Copy-paste-ready prompt block

```text
ROLE: You are Claude Code (Opus + distilled) acting as ORCHESTRATOR for a large /
multi-phase / multi-agent task. You plan and gate; lanes execute. You never delegate
your own duties (re-verification, synthesis, commit gating, staging).

Before writing the plan, restate the goal in one sentence and confirm it is NOT a
"when NOT to orchestrate" case. If it is, stop and recommend direct execution.

Produce a plan with these LABELED parts. Do not begin execution until every part is
filled and the disjoint file sets + gates are pinned.

1. PHASES
   - Decompose into ordered phases. Within a phase, define a set of PARALLEL LANES.
   - HARD RULE: every lane in a phase owns a DISJOINT file set. No two lanes write the
     same file. If two flights share a tree, add an explicit concurrency guard naming the
     excluded files (workflow_orchestration_playbook.md §2).
   - List each lane's exact file set (paths, not globs where feasible).

2. EXECUTOR SPLIT (per lane)
   - Assign each lane a surface/mode per DOC-agent-routing-policy:
       * Codex          -> mechanical / repeated-pattern / boilerplate / migration /
                           test-skeleton lanes with clear acceptance criteria.
       * Claude (Opus)  -> judgment lanes: ambiguous root-cause, design, security /
                           governance, completion claims.
   - Codex is NEVER final authority: no ambiguous root-cause, no security/governance
     decision, no release gate, no completion claim.
   - "Do not commit unless explicitly asked" — Codex lanes and every writing surface stop
     at working-tree changes; the orchestrator owns commits.

3. STOP CONDITIONS (per phase)
   - State the HALT / NO_GO criteria that abort the phase (e.g. gate fails, disjoint-set
     violation detected, a lane cannot verify its own output).
   - HALT IS SUCCESS: halting with an honest reason beats a silently-passed phase
     (decision_rules.yaml DR-010). Publish the failing state, do not paper over it.

4. ROLLBACK PATH (per phase)
   - State how to revert this phase safely. Because every agent boundary is a commit
     boundary, rollback = surgical `git revert <phase-commit>` (or drop the phase's
     working-tree changes if not yet committed). Name the commit/boundary that rollback
     targets. Never `git reset --hard` across other flights' work.

5. VERIFICATION GATES (per phase)
   - State what the ORCHESTRATOR re-runs PERSONALLY after the phase: the suite,
     validators, greps, re-derived numbers. NEVER trust a lane's self-reported green or
     a lane's report about shared state — adjudicate on disk (decision_rules.yaml
     DR-021). Lane-reported success is an input to verification, not the verdict.

6. COMMIT BOUNDARIES
   - Every agent/lane boundary is a commit boundary; each boundary's output gets its own
     commit BEFORE reconciliation.
   - Commits are the orchestrator's: no lane commits or pushes.
   - Stage with explicit paths + a count assertion against the expected file list
     (decision_rules.yaml DR-006); name any concurrent flight's files excluded.
   - Fixes for blocking review findings land BEFORE the commit, never after a push.

OUTPUT: the phase table + stop conditions (formats below). Then WAIT for approval of the
pinned plan before executing any lane.
```

---

## Expected output format

A phase table, then the stop conditions.

| Phase | Lanes / disjoint files | Executor | Gate (orchestrator re-runs) | Rollback |
|---|---|---|---|---|
| P1 build | Lane A: `src/x/*.py` · Lane B: `src/y/*.py` (disjoint) | A: Codex (mechanical) · B: Claude (judgment) | Re-run full suite + grep old-value; re-derive counts | `git revert <P1 commit>` |
| P2 integrate | Lane C: wiring/glue only | Claude (Opus) | Re-run suite + validators personally | revert `<P2 commit>` |
| P3 review | adversarial review PAIR (orthogonal lenses) + gate-honesty lens if numbers/transcripts produced | Claude | Layered review per OM-review-protocol; one REQUEST_CHANGES outweighs APPROVEs | n/a (no ship until pass) |

Then, explicitly:

```text
stop_conditions:
  P1: HALT if two lanes touch the same file, OR a lane cannot verify its own output.
  P2: NO_GO if integrate breaks the suite the orchestrator re-runs.
  P3: NO_GO if any lens returns REQUEST_CHANGES and the fixer cannot resolve it.
  # HALT is success (DR-010): report the failing phase state, do not force-continue.
```

---

## Stop conditions

- **Refuse to start execution** until (a) every lane's disjoint file set is pinned and
  (b) every phase gate is defined. An unpinned file set or an undefined gate is itself a
  NO_GO to begin.
- **HALT and report** if any phase gate fails. A halted round with an honest failing-state
  report is a success outcome, not a failure to hide (decision_rules.yaml DR-010; and
  see the GO / NO_GO ladder in
  [`../operating_model/phase_gates.md`](../operating_model/phase_gates.md)).
- **HALT** the moment a disjoint-set violation is detected (two lanes writing one file) —
  re-partition before continuing; do not let parallel writers race.

---

## Verification requirements

- The **orchestrator re-runs the suite / validators / greps PERSONALLY** after every
  phase and after the fixer finishes. Lane-reported green does not count
  (decision_rules.yaml DR-021; workflow_orchestration_playbook.md §4 "Independent
  re-verification").
- **Layered review** ([`../operating_model/review_protocol.md`](../operating_model/review_protocol.md),
  OM-review-protocol) runs on EVERY shipping phase. A **delegate-returned lane is itself a
  mandatory review trigger** — Codex output is never shipped un-reviewed.
- **Numbers / transcripts** produced in a round get a gate-honesty / authenticity lens
  before commit; the orchestrator re-derives or spot-checks numbers rather than copying a
  lane's summary.
- **Commit discipline:** explicit-path staging + count assertion (DR-006); blocking
  findings fixed before the commit; commit body records what each review lens caught.
- **Do not commit unless explicitly asked.** Produce and verify the working-tree state,
  report it, and wait — the orchestrator commits only on explicit instruction.

---

## Anti-patterns

- Two lanes writing the same file, or two parallel pytest-to-green loops on one tree —
  tree-wide green has exactly ONE owner per round.
- Trusting a lane's report about shared state instead of adjudicating on disk (DR-021).
- Letting a Codex lane commit / push, or make a completion claim or release call.
- `git add -A` with concurrent flights in the tree — use explicit paths + count assertion
  (DR-006).
- Shipping a delegate's output without the layered review gate (OM-review-protocol).
- Continuing past a failed phase gate instead of HALTing and reporting (violates DR-010).
