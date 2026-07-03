---
id: DOC-completion-honesty-gate
layer: doc
purpose: The checklist any surface must pass before claiming done / fixed / tests pass / benchmark succeeded / ready to commit / ready to release. Distinguishes raw process evidence from derived reports.
read_when: Before emitting any completion or success claim; before commit or release; when a report and the raw artifacts might disagree.
depends_on:
  - ../prompts/self_check_prompt.md
  - ../operating_model/review_protocol.md
  - ../operating_model/decision_rules.yaml
  - ../core/portable_operating_model.md
used_by:
  - PROMPT-claude-code-completion-integrity
  - DOC-agent-routing-policy
  - DOC-agent-optimization-runbook
  - operator-session
tags: [completion-honesty, verification, no-silent-pass, raw-vs-derived, gate]
retrieval_keywords: [can we say done, completion checklist, raw vs derived, exit code stderr timeout, background job, canonical artifact, honest failure wording, before commit before release]
---

# Completion-honesty gate

This artifact encodes the operator's Hermes / Claude Code / Codex stack (source:
model-routing-benchmark `universal_agent_optimization_prompt.md`) bound to this harness's
existing doctrines cited inline; it is NOT distilled from method-harness-compiler.

## Purpose

This is the operational checklist form of `../prompts/self_check_prompt.md`
(PROMPT-self-check) and the honest-failure doctrine in
`../core/portable_operating_model.md` (CORE-portable-operating-model). Any surface —
Hermes, Claude Code (any mode), or Codex — passes this gate before it emits a
completion or success claim ("done", "fixed", "tests pass", "benchmark succeeded",
"ready to commit", "ready to release"). The gate is author-agnostic (see the layered
review gate in `../operating_model/review_protocol.md`, OM-review-protocol): who wrote
the work does not exempt it.

**Core rule — a derived Markdown report is NOT proof.** A `derived report` is a
convenience summary a surface writes about what it did; it can be optimistic, stale,
or fabricated. Stronger evidence, in order, is: the raw process **exit code**, raw
logs including **stderr**, the `canonical` JSON/CSV/log artifact a runner produced,
`test` runner output with counts, and the on-disk listing proving required output
files exist. When a report and the raw artifacts might disagree, the raw artifact
wins. Cited decision rules (do NOT restate their detail — see
`../operating_model/decision_rules.yaml`, OM-decision-rules):

| Rule | Why it applies here |
|---|---|
| DR-004 computed-artifacts-only-via-runners | Numbers must come from a runner, never hand-asserted; the canonical artifact is the runner's output. |
| DR-011 no-silent-pass | A truncated / timed-out / unread run is not a pass; absence of a failure signal is not success. |
| DR-009 publish-own-failures | If evidence is missing or the run failed, publish that — do not paper over it. |
| DR-010 halt-is-success | Correctly halting on missing evidence (rather than guessing done) IS a successful outcome, not a defeat. |

## The checklist

Do NOT emit a completion claim until every box is checked. If any box cannot be
checked, use a failure-wording template below and publish the gap (DR-009).

- [ ] **1. Process exit code checked.** Read the process **exit code**. Nonzero =
      not done. Do not infer success from stdout looking plausible.
- [ ] **2. stderr read, not just stdout.** Inspect **stderr** separately. Warnings,
      partial errors, and swallowed exceptions land there while stdout still prints a
      "done" line.
- [ ] **3. No silent timeout / truncated run.** Confirm the run reached its natural
      end. A `timeout`, a killed process, or truncated output is DR-011 no-silent-pass —
      treat it as NOT done.
- [ ] **4. No background job still running or unjoined.** No `background job` is
      still executing or was launched and never awaited. Check: on Windows, `Get-Job` /
      `tasklist` for the PID you spawned; on POSIX, `jobs` / `ps` for the child. An
      unjoined `background job` means results are not in yet — you cannot claim done.
- [ ] **5. Canonical raw artifact exists AND was inspected.** The `canonical` raw
      artifact (JSON/CSV/log the runner wrote) exists on disk and you opened it — not
      merely its `derived report`. Reading only the summary is artifact laundering.
- [ ] **6. Derived report reconciled against canonical.** The `derived report`
      agrees with the `canonical` artifact, OR the divergence is published (DR-009). If
      you have not compared them, you have not reconciled them.
- [ ] **7. Tests actually ran and passed — count stated.** The `test` suite ran in
      THIS environment and passed; state the count (e.g. "142 passed, 0 failed"), never
      "should pass" or "tests look fine".
- [ ] **8. Required output files exist on disk.** Every required file was verified to
      `file exist` on disk (list it / stat it). Do not assume a write succeeded because
      the code path "should have" written it.
- [ ] **9. Numbers were computed by a runner (DR-004).** Every reported metric came
      from a runner's output, not typed in by hand or eyeballed from a log.
- [ ] **10. Nothing fabricated or guessed.** Unknowns are marked UNSCORED / TODO
      (DR-002 todo-on-uncertainty-never-guess). No number, path, or status was invented
      to make the claim land.

## Raw vs derived

| Evidence type | Strength | Failure it prevents |
|---|---|---|
| Process **exit code** + **stderr** | strong | "stdout said done" while the process actually errored (DR-011). |
| `canonical` JSON/CSV the runner wrote | strong | Hand-asserted numbers; report drift from real results (DR-004). |
| `test` runner output with pass/fail counts | strong | "tests should pass" claims; silent regressions. |
| On-disk file listing (`file exist` verified) | strong | Assuming a write happened; missing artifacts. |
| Hand-written summary / "I ran it and it worked" | weak | Nothing — this is the claim, not the evidence. |
| A `derived report` (Markdown) with no linked artifact | weak | Nothing — "artifact laundering": a green report standing in for proof. |

Rule of thumb: if the only thing you can point to is prose YOU wrote, you have a
weak claim. Point to the runner's `canonical` output instead.

## Failure-wording templates

When the gate cannot be fully passed, say so with one of these literal lines. Copy
verbatim; fill in the specifics.

```text
I cannot honestly claim completion because the process exited nonzero (code N).
I cannot honestly claim completion because I have not inspected the canonical artifact, only its derived report.
I cannot honestly claim completion because a background job is still running.
I cannot honestly claim completion because the tests were not run in this environment.
```

More generally: **"I cannot honestly claim completion because"** ... then the specific
missing evidence (stderr unread, run timed out, required file did not `file exist`,
numbers not computed by a runner).

**HALT-is-success note (DR-010):** stopping here and publishing the gap is the
correct, successful outcome — not a failure to hide. A published HALT beats a
silently passed claim every time (DR-011, and the honest-failure doctrine in
CORE-portable-operating-model).

## Examples

**Bad — laundered report claim:**

> "Done. The benchmark run is complete — see `report.md`, all cases green."
> (No exit code checked, `report.md` is a `derived report`, the `canonical`
> `results.json` was never opened, and the runner was still finishing in a
> `background job`.)

**Good — honest partial with the template:**

> "I cannot honestly claim completion because I have not inspected the canonical
> artifact, only its derived report. `report.md` shows all-green, but `results.json`
> (the runner's `canonical` output) is not yet on disk and a `background job`
> (PID 8123) is still running. Halting here per DR-010; will reconcile once the job
> joins and `results.json` exists. Verified so far: 3 of 5 config files `file exist`;
> the `test` suite has not been run in this environment yet."

## Anti-patterns

- **Treating a green `derived report` as proof.** A report is a claim, not evidence;
  reconcile it against the `canonical` artifact (checklist #5–#6).
- **"Tests should pass."** Either the `test` suite ran with a stated count, or it did
  not run — there is no "should" (checklist #7, DR-011).
- **Declaring done with a `background job` unjoined.** Results are not in until the
  job joins (checklist #4).
- **Hand-edited numbers.** Any metric not produced by a runner violates DR-004
  (checklist #9).
- **Concealing a correction instead of publishing it.** If you found and fixed a
  wrong earlier claim, publish the correction (DR-007 corrections-append-never-overwrite, in
  `../operating_model/decision_rules.yaml`); a quietly overwritten number is a silent
  pass (DR-011).

---

**Decision:** GO to emit a completion / success claim only when all 10 checklist
boxes are checked. Otherwise NO_GO — use a failure-wording template and publish the
gap.

**Risks:** the dominant risk is artifact laundering — a green `derived report`
substituting for the `canonical` runner output; secondary risk is an unjoined
`background job` whose results silently never arrive.

**Required changes (before any commit/release):** reconcile every `derived report`
against its `canonical` artifact; confirm the `test` suite ran with a stated count;
verify required outputs `file exist` on disk. "Do not commit unless explicitly asked"
is a standing rule — this gate authorizes the CLAIM, not the commit.

**Next actions:** if GO, proceed to the phase-gate ladder in
`../operating_model/phase_gates.md` and the layered review gate in
`../operating_model/review_protocol.md` (OM-review-protocol) before shipping; if
NO_GO, publish the gap (DR-009) and HALT (DR-010).
