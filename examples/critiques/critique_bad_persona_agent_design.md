---
id: CRIT-persona-agent-design
layer: example
purpose: Critique of bad_persona_agent_design.md — the "You are the expert" pattern, with every violated rule and the harness-shaped correction.
read_when: You read the persona-bot example, or someone requests an agent that "is" a named expert.
depends_on:
  - ../bad/bad_persona_agent_design.md
  - ../../datasets/failure_modes.yaml
used_by:
  - ROUTE-eval-design
  - ROUTE-pr-review
tags: [critique, persona, impersonation, evidence]
retrieval_keywords: [persona critique, impersonation refusal, method emulation only, non-affiliation, citation discipline, stay in character]
synthetic: true
---

# Critique: bad_persona_agent_design.md

## Violations

1. **"You are Duan Yongping… stay in character at all times."** Direct impersonation of
   a living person, plus an instruction to deflect when asked. Violates DR-006
   (no-fabrication-as-code: the identity claim itself is a fabrication) and
   RUBRIC-tool-safety/person-policy: the observed standard's `impersonation_policy:
   method_emulation_only` and the eval `safe_t01_impersonation_refusal` exist precisely
   to catch this (FM-010 persona-drift; the real grader catches 「我是段永平」 in CJK too).
2. **First-person financial verdicts ("buy, hold, or sell… what price").** Violates the
   domain hard line the real package eval-enforces (`dom_t04_no_ratings_or_price_targets`)
   and the risk posture for `risk_level: financial`.
3. **"Your judgment is your evidence; you do not need to cite sources."** Violates DR-006
   and RUBRIC-evidence-integrity — every target claim must resolve to an evidence card
   with an attribution type and a verified flag (FM-003 fabricated-citation is the
   default failure state of citation-free personas; cf. the ai-berkshire audit: 0
   machine-resolvable citations across 2,194 files).
4. **"You cannot unit-test wisdom" — no evals.** FM-001 (silent-pass-wiring) as a design
   philosophy; violates DR-003. The real project publishes 0/3-vs-3/3 transcripts against
   exactly this baseline — persona quality claims are testable, and personas lose.
5. **Track-record marketing as evidence** ("2-year simulated portfolio return") — the
   real evaluation framework explicitly rules this out: unauditable, n too small
   (RUBRIC-eval-design; Category-7 outcome evals with pre-registration are the honest
   substitute).
6. **Prompt-declared memory** ("you remember your past conversations") with no store,
   no update policy — FM-001 again; violates DR-009 (memory is files with append rules,
   not vibes).
7. **Living person's name as product brand** (`duan-yongping-gpt`) — FM-029-adjacent
   legal exposure; the real project renamed to methodology-first
   (`quality-value-investing-harness`) with a mandatory non-affiliation notice.

## Corrected approach (5-10 lines)

```text
- Name the package for the METHOD; the person appears only as cited
  evidence subject, with subject_status declared and a non-affiliation
  + advisory footer machine-appended to every output.
- Replace "you are X" with "an agent harness based on publicly available
  evidence about X's methodology"; refuse impersonation baits (eval-tested,
  including alias/CJK forms).
- Every method claim cites an evidence card (attribution enum + verified
  flag; compilations capped at third_party_interpretation).
- Ship the eval spec WITH the agent: impersonation, no-ratings,
  injection-resistance, citation-fabrication tests; publish the FAILs.
- Memory = package-declared JSONL files with append-only update policy.
```
