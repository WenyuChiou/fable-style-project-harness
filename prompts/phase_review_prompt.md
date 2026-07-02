---
id: PROMPT-phase-review
layer: prompt
purpose: Ready-to-use instruction for running a phase/plan/design review the
  way the 2026-07-01 design review and the N=2/N=3 gates were run.
read_when: Executing ROUTE-phase-review on a plan, spec revision, or gate
  decision.
depends_on:
  - ../rubrics/architecture_review_rubric.yaml
  - ../validation/self_checklists/phase_review_checklist.md
used_by:
  - ROUTE-phase-review
tags: [phase-review, gate, GO NO_GO, adversarial-lenses]
retrieval_keywords: [review this plan, phase gate, design review procedure,
  GO CONDITIONAL_GO NO_GO, friction record]
---

# Phase review prompt

You are reviewing a plan, spec revision, or phase-gate artifact. Your output
is a verdict — `GO`, `CONDITIONAL_GO`, or `NO_GO` — computed with
`../rubrics/architecture_review_rubric.yaml`, plus a findings table. Follow the
route file for ROUTE-phase-review; this prompt is the per-run script.

## Procedure

1. **Restate** what is under review, which phase the project is in, and what
   the artifact is allowed / forbidden to change. If the gate condition was
   not stated BEFORE the work under review was done, that is itself a
   finding (a gate written after the result is not falsifiable).
2. **Apply orthogonal lenses, one at a time**: (a) end-user journey — walk a
   concrete persona through the plan minute by minute and record where the
   journey dies; (b) positioning/competition — what incumbent or prior work
   does this collide with; (c) ruthless skeptic — which claims have no
   runnable proof; (d) trust/risk — legal, safety, honesty exposure. Do not
   let one lens's optimism cancel another's finding: convergent findings
   (two or more lenses independently agreeing) carry the highest severity.
3. **Check the method skeleton**: proof before automation; falsifiable gates
   with pre-stated FAIL behavior; adoption-priced surface; immutable/mutable
   separation; protective (Tier-A-style) fixes scheduled before any public
   exposure.
4. **Score** every criterion in RUBRIC-architecture-review with a one-line
   justification citing the plan's own text (section/line). No criterion may
   be scored without a citation.
5. **Also record what SURVIVES** review unchanged (a keep-list) and what
   changes you considered and rejected, with reasons — a review that only
   lists faults is incomplete.
6. **Run** `../validation/self_checklists/phase_review_checklist.md` on your
   own review before returning it.

## Output format

- Verdict line: `GO | CONDITIONAL_GO | NO_GO` + one-sentence reason.
- Findings table: `# | finding | lens(es) | severity (critical/major/minor)`.
- Rubric scores: criterion id, score, citation.
- Keep-list and rejected-changes list.
- If CONDITIONAL_GO: the exact conditions, each falsifiable.
- Remember: recommending a halt or a scope cut is a success outcome of this
  review, not a failure. Never soften a NO_GO to be agreeable.
