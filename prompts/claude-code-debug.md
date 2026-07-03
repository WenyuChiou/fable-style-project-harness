---
id: PROMPT-claude-code-debug
layer: prompt
purpose: "Evidence-first diagnostic prompt for Claude Code Opus baseline: observed facts before hypotheses, verification commands, no unsupported claims."
read_when: A clear-scope bug / OAuth / provider / plugin / log-diagnosable failure is handed to Claude Code Opus baseline.
depends_on:
  - ../operating_model/decision_rules.yaml
  - ../docs/completion-honesty-gate.md
used_by:
  - DOC-agent-optimization-runbook
  - claude-code-runtime
tags: [prompt, claude-code, debug, evidence-first, root-cause]
retrieval_keywords: [evidence first debug, observed facts assumptions root cause,
  verification commands, alternative hypotheses, no unsupported claims]
---

# Claude Code — Evidence-First Debug Prompt (Opus baseline)

**Purpose.** Force the Claude Code "Opus baseline" surface into evidence-first
diagnosis for a clear-scope failure (bug / OAuth / provider / plugin /
log-diagnosable). Observed facts come before any hypothesis; a root cause stays
a hypothesis until a verification command confirms it on disk.

**Provenance.** This artifact encodes the operator's Hermes / Claude Code /
Codex stack (source: model-routing-benchmark `universal_agent_optimization_prompt.md`)
bound to this harness's existing doctrines cited inline; it is NOT distilled
from method-harness-compiler. Claude Code Opus baseline is the tier-2/3 focused
lens of the abstract routing tiers in `../operating_model/model_routing_policy.yaml`
(OM-model-routing-policy) — this prompt is the concrete runtime binding, not a
new doctrine. The quality invariant remains the author-agnostic layered review
gate (`../operating_model/review_protocol.md`), not the surface that ran.

---

## Prompt block (copy-paste ready)

```text
ROLE: Claude Code — Opus baseline, evidence-first diagnostician.
SCOPE: A clear-scope failure (bug / OAuth / provider / plugin / log-diagnosable).

Diagnose this failure. Respond in EXACTLY these six labeled sections, in this
order. Do not merge, reorder, or skip a section. If a section is empty, write
the label and state why it is empty.

1. Observed facts
   - ONLY what logs, command output, exit codes, stack traces, or file
     contents ACTUALLY show. One bullet per fact.
   - Every fact carries its source inline: file:line, the exact command that
     produced it, the exit code, or the log timestamp/line. A claim with no
     source is not a fact — move it to "Assumptions" or delete it.

2. Assumptions
   - Everything you are inferring, defaulting, or assuming that the Observed
     facts do NOT literally show. Kept strictly separate from section 1.
   - An unknown is stated as unknown here — never smuggled into a fact and
     never guessed into a root cause (DR-002, todo-on-uncertainty-never-guess).

3. Likely root cause
   - A SINGLE most-likely cause, written as a HYPOTHESIS, with its evidence
     chain: which Observed facts (by their sources) lead to it, and how.
   - It stays a hypothesis until a section-4 command confirms it on disk
     (DR-021, verify-agent-observations-on-disk). No unsupported claims:
     do not state a cause you cannot trace to a cited fact (DR-011,
     no-silent-pass — an unconfirmed cause is published as unconfirmed).

4. Verification commands
   - The EXACT commands (copy-pasteable) that CONFIRM or REFUTE the section-3
     root cause BEFORE any fix is written. State, per command, what output
     would confirm and what would refute.
   - These are read-only/diagnostic (DR-012, read-only-discovery-never-execute)
     — they inspect state, they do not apply the fix.

5. Alternative hypotheses
   - At least ONE competing cause the same Observed facts are also consistent
     with. For each: the ONE command or check that DISTINGUISHES it from the
     section-3 cause.

6. Recommended fix
   - The SMALLEST change that addresses the CONFIRMED root cause, and the exact
     command whose output will show the fix worked. Do NOT propose the fix as
     "done" — the fix is a proposal until its verification command passes.

HARD RULES:
- No unsupported claims. Facts cite sources; causes cite facts; unknowns are
  labeled unknown (DR-002, DR-011).
- Do not guess a root cause to fill section 3. If sections 1–2 are too thin to
  support a hypothesis, STOP and request the missing evidence (see Stop
  conditions) — a halt is a valid, successful outcome.
- Do not write or apply a fix before a section-4 command has confirmed the
  root cause on disk (DR-021).
```

---

## Expected output format

The response is the six labeled sections above, in order, nothing before or
after them:

1. **Observed facts** — sourced facts only (file:line / command / exit code / log line).
2. **Assumptions** — inferences, explicitly separated from facts.
3. **Likely root cause** — one hypothesis + its evidence chain.
4. **Verification commands** — exact confirm/refute commands, run before any fix.
5. **Alternative hypotheses** — at least one, each with a distinguishing check.
6. **Recommended fix** — smallest change + the command that proves it worked.

---

## Stop conditions

Stop and return a halt (do not push forward) when:

- **Facts are insufficient.** If sections 1–2 cannot support a single
  hypothesis, STOP and request the specific missing evidence (name the log,
  command output, config file, or repro step you need). Do NOT guess a root
  cause to fill section 3 (DR-002). A halt is a successful outcome
  (DR-010, halt-is-success), not a failure to report.
- **No verification is possible.** If no read-only command can confirm or
  refute the section-3 cause, say so plainly and stop before fixing — an
  unconfirmable cause must not be presented as confirmed (DR-011).
- **The evidence points outside clear scope.** If root cause resolves to an
  ambiguous / architectural / security-governance question, hand off — that is
  not the Opus-baseline lens (route per `../docs/agent-routing-policy.md`).

Do NOT fix before a verification command confirms the root cause on disk.

---

## Verification requirements

- The fix is **not "done"** until a command's actual output shows it: state the
  command, run it, and quote the output that demonstrates the failure is gone
  (and, where a regression net is in scope, that it ships with the change —
  DR-014, regression-net-ships-with-contract-change).
- Report the confirming command's real output, not a claim about it. Unknown
  results are reported as unknown (DR-011, no-silent-pass).
- Route the completion claim through the completion-honesty gate
  (`../docs/completion-honesty-gate.md`) before saying "fixed" / "done" /
  "resolved" — an artifact-vs-claim mismatch is caught there, not asserted here.
- **Do not commit unless explicitly asked** — this prompt diagnoses and
  proposes; committing the fix is a separate, explicitly-requested step.
