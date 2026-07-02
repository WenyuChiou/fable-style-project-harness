---
id: EXAMPLE-good-phase-review
layer: example
purpose: Golden example of a multi-lens adversarial phase review that produced a tiered, ratifiable change program instead of a vague thumbs-up.
read_when: You are about to review a completed phase, spec, or milestone before committing to the next one.
depends_on:
  - ../../playbooks
  - ../../rubrics
used_by:
  - ROUTE-phase-review
tags: [phase-review, adversarial-panel, design-review, tiered-changes, golden]
retrieval_keywords: [design review, four-lens panel, convergent findings, tier A tier B, keep list, rejected changes, change program, GO conditional]
source_artifact: docs/design_review_2026-07-01.md (repo method-harness-compiler, commit f4c826f)
synthetic: false
---

# Golden: Phase Review (Day-1 spec review, condensed from the real artifact)

This is a condensed rendering of the project's post-Day-1 design review. Everything below
is observable in `docs/design_review_2026-07-01.md`. Note the structural moves, not the
domain content — they are what make this review reusable.

## Method observed

1. **Orthogonal lenses, run independently.** Four adversarial reviewers with
   non-overlapping questions: end-user journey simulation (4 personas), positioning and
   competitive landscape (with live web research), ruthless design skeptic, and
   trust/risk/ethics. The orchestrator synthesized; the lenses never negotiated with
   each other.
2. **Convergence is the severity signal.** Findings agreed on by 2-3 independent lenses
   were promoted to `critical` (12 convergent findings, C1-C12). One-lens findings stayed
   in the per-lens appendix.
3. **Explicit keep-list.** The review names what SURVIVES unchanged (evidence attribution
   taxonomy, non-impersonation framing, read-only tool posture, file-based memory format)
   so later phases cannot "fix" what was working.
4. **Tiered change program, not a punch list.** Tier A = protective fixes appliable
   without strategy change (quote-licensing NOTICE, non-affiliation notice, scorecard
   honesty, person policy). Tier B = structural redesign requiring owner ratification
   (invert phase order, falsifiable N=2 gate, CLI-before-internals, demo rename).
   Tier C = **explicitly rejected changes with reasons** (e.g. "swap the living person for
   a historical figure: rejected — living-person/CJK/financial is precisely the stress
   test").
5. **Every critical finding is falsifiable.** C1 "not installable anywhere" cites the
   exact spec section that over-promises; C2 "evaluation is a silent pass" names the
   self-assigned scorecard numbers; C3 quantifies the incumbent (~7.2k stars, ships the
   same target, zero citations/tests/memory).

## Representative excerpt (structure preserved, prose condensed)

> **Overall verdict**: core ideas validated — the anti-persona critique matches market
> evidence, and evidence-attribution + eval-included packaging are unoccupied territory.
> But v0.5.1 has the **phase order inverted** (proof and installability deferred to the
> end), a **standard priced for adoption failure** (~45 mandatory files at N=1), a
> **flagship demo in an incumbent's shadow**, and **unaddressed artifact-level legal
> exposure**. All fixable, most cheaply now.

| # | Convergent finding | Lenses | Severity |
|---|---|---|---|
| C1 | Not installable anywhere — every persona's journey dies at minute five | journey, positioning, skeptic | critical |
| C2 | Evaluation is a silent pass — scorecard scores are self-assigned numbers nothing computed | journey, skeptic, trust | critical |
| C7 | Standard priced for adoption failure — 12 abstractions / ~45 mandatory files at N=1 | journey, positioning, skeptic | major |
| C12 | Degraded-mode dishonesty — with no tools configured the command silently becomes a persona prompt in harness costume | journey | major |

> **Tier B3 (the falsifiable gate).** Phase 2 automation begins only if (a) harness
> >=5/6 vs persona-prompt <=2/6 on the behavioral tests under a blinded grader, AND
> (b) a second harness in a different domain can be authored **without schema changes**.
> Otherwise revise the standard, don't automate it.

## Why this is the golden form

- The verdict leads; evidence follows; every claim cites a spec section, a number, or a
  live-fetched competitor fact.
- Severity is earned by independent convergence, not by reviewer mood.
- The output is a **decision instrument**: the owner ratified B7/B10 by name, and each
  later commit traces back to a review ID (B1, B2, B3, B6, B12 all appear in subsequent
  commit messages).
- Rejected changes are recorded with reasons — the review protects the project from
  re-litigating settled questions.
- The review happened BEFORE the commit that shipped the phase (post-Day-1, pre-commit),
  so its findings became next-phase work orders, not regrets.

## Reuse checklist

- [ ] 3-4 reviewers with orthogonal, written lens charters; no shared drafts.
- [ ] Convergence table with lens attribution per finding.
- [ ] Keep-list of what must NOT change.
- [ ] Tier A (protective, apply now) / Tier B (structural, needs ratification) /
      Tier C (rejected, with reasons).
- [ ] At least one falsifiable gate for the next phase, with numeric pass conditions.
- [ ] Findings carry stable IDs so future commits can cite them.
