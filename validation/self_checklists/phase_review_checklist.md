---
id: CHECK-phase-review
layer: validation
purpose: Binary pre-return checks for a phase/plan/design review, drawn from
  RUBRIC-architecture-review and the observed gate discipline (design review
  2026-07-01, N=2/N=3 gates).
read_when: After drafting a phase review, before returning it.
depends_on:
  - ../../rubrics/architecture_review_rubric.yaml
  - ../../prompts/phase_review_prompt.md
used_by:
  - ROUTE-phase-review
tags: [checklist, phase-review, gate]
retrieval_keywords: [phase review checklist, gate checklist, GO NO_GO checks]
---

# Phase review self-checklist

Answer each YES/NO. Any NO means the review is not ready to return.

1. [ ] I restated the artifact under review, the current phase, and the
   allowed/forbidden scope in my own words.
2. [ ] The gate condition being evaluated was stated BEFORE the work under
   review was done (or I flagged that it was not, as a finding).
3. [ ] Every gate condition in my verdict is falsifiable — a reader can tell
   exactly what outcome would fail it.
4. [ ] I applied at least three orthogonal lenses (journey / positioning /
   skeptic / trust) and labeled each finding with its lens(es).
5. [ ] Convergent findings (2+ lenses agreeing independently) are ranked
   above single-lens findings.
6. [ ] I checked that runnable proof (installability, computed eval) comes
   BEFORE automation in the plan, and cited the plan's own phase ordering.
7. [ ] I checked for a pre-stated FAIL path ("revise the standard, don't
   automate it") and treated halt-is-a-success as an admissible outcome.
8. [ ] I checked protective/trust items (quote licensing, person policy,
   degraded-mode honesty, scorecard honesty) are scheduled before public
   exposure — or recorded their absence as a finding.
9. [ ] Every rubric criterion score cites specific text (section/line) in the
   reviewed artifact; no score is justified by general impression.
10. [ ] My review includes a keep-list (what survives unchanged) and a
    rejected-changes list with reasons.
11. [ ] The verdict follows RUBRIC-architecture-review's verdict rule
    mechanically — I did not override a computed NO_GO to be agreeable.
12. [ ] If CONDITIONAL_GO: each condition is concrete, falsifiable, and
    assigned to an artifact that will evidence it.
13. [ ] Anything I could not assess is listed as UNSCORED with a reason, not
    scored 3 by default.
