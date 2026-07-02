---
id: PROMPT-boundary-review
layer: prompt
purpose: Ready-to-use instruction for auditing a tool plan, recommender
  output, or ToolCard set for execution-boundary violations.
read_when: Executing the boundary-audit leg of ROUTE-tool-discovery or
  ROUTE-pr-review on anything that selects or configures tools.
depends_on:
  - ../rubrics/tool_boundary_rubric.yaml
  - ../validation/self_checklists/tool_discovery_checklist.md
used_by:
  - ROUTE-tool-discovery
  - ROUTE-pr-review
tags: [boundary, permissions, risk, audit]
retrieval_keywords: [execution violation, permission audit, risk_basis check,
  tool plan review, unvetted card]
---

# Boundary review prompt

You are auditing a tool plan / ToolCard diff / recommender output for
violations of the execution boundary. Score with
`../rubrics/tool_boundary_rubric.yaml`. A single confirmed TB-1 violation
(something discovered gets installed, executed, or signed up for) ends the
audit with verdict VIOLATION — do not keep scoring as if it were severable.

## What to hunt for, in order

1. **Execution smuggled into discovery.** Words like "install to test",
   "run it in a sandbox to observe", "npx ... to check output", "sign up for
   the free tier". Discovery is metadata-only; behavior is learned from
   documentation and registry metadata, never by running the candidate.
2. **Risk asserted, not computed.** `risk_level: low` justified by vendor
   self-description, popularity, or nothing. Correct form: risk computed
   from conservative proxy signals with the computation recorded in
   `risk_basis`; ambiguity resolves to the HIGHER tier.
3. **Trust laundering.** Auto-drafted cards missing
   `verification_status: unverified_auto_draft`, or a draft promoted to
   `tools/tool_cards.yaml` with no named human vetting step.
4. **Governed-file writes.** A generator or script writing
   `capability_map.yaml` / `eval_spec.yaml` / `tool_cards.yaml` directly
   instead of a `.generated.yaml` sibling; overwrites without `--force`;
   drafts left inside shipped packages.
5. **Permission creep.** Tools defaulting to write / execute /
   external_action without an explicit Tier-4 (human review) escalation;
   permission_level absent from cards so nothing can check it.
6. **Unresolvable capabilities.** ToolCard capability strings that don't
   resolve to capability_map ids — a typo would validate silently.

## Output format

- Verdict: `VIOLATION | REVISE | PASS` (per the rubric's verdict rule).
- For each finding: the exact quoted line from the artifact, the criterion id
  (TB-1..TB-6), and the corrected form.
- If VIOLATION: state what must be rolled back or quarantined (e.g., an
  installed artifact removed, credentials revoked) before work may resume.
