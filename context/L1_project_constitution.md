---
id: L1-project-constitution
layer: context
purpose: The source project's thesis, non-goals, and stable operating principles
read_when: A decision touches project identity, scope boundaries, or a principle conflict
depends_on: [context/L0_bootstrap.md]
used_by: [ROUTE-phase-review, ROUTE-eval-design, ROUTE-pr-review, ROUTE-tool-discovery, ROUTE-ab-test-design]
tags: [constitution, thesis, non-goals, principles]
retrieval_keywords: [thesis, non-goals, stable principles, no impersonation, no fabrication, evaluation first, discovery without execution, honest failure]
---

# L1 — Project Constitution

Everything below is stated in the source repo's public artifacts
(`README.md`, `docs/development_plan.md`, `docs/design_review_2026-07-01.md`,
`docs/CHANGELOG_STANDARD.md`, commit bodies). It changes rarely; when it
does, the change lands as a logged standard revision, never a silent edit.

## Thesis

**Compile any expert methodology with a public corpus into an
evidence-grounded, testable, auditable agent package.** (README headline.)
The product is the package **standard** plus the **compiler** — the three
shipped example packages are demos, not the product. The counter-thesis it
exists to refute: persona bots are unfalsifiable and nothing they produce
accumulates (measured 0/3 vs 3/3 head-to-head, `docs/comparisons/`).

## Non-goals (the ten, from the source README)

The project must **not** become:

1. A celebrity impersonation system.
2. A prompt collection.
3. A chatbot that only imitates tone.
4. A raw skill marketplace.
5. A raw MCP marketplace.
6. A tool that automatically installs unknown MCP servers.
7. A financial advisor.
8. A medical/legal advisor.
9. A high-risk autonomous decision system.
10. A system that fabricates expert views without evidence.

Any task that drifts toward one of these is out of scope regardless of who
asked. The required framing is always "harness based on publicly available
evidence about the target's methodology" — never a first-person claim to be
the person.

## Stable principles (observable across every shipped milestone)

1. **Evaluation-first.** "Build harness = build agent + build evaluation"
   (spec 15.1, restated in `development_plan.md` guardrails). Scorecards
   are **computed, never hand-edited**; unmeasured dimensions are reported
   UNSCORED, never guessed (Milestone 1a acceptance criteria; N3-F20
   friction shows the discipline even where the schema resists it).

2. **File-based memory first.** YAML for curated state, JSONL for
   append-only event streams; "records are never rewritten in place —
   updates are new lines that reference prior lines"
   (`docs/memory_strategy.md`). Corrections get their own store
   (`correction_memory.jsonl`).

3. **Discovery-before-execution.** Tool research is metadata-only:
   "zero installs, zero executions, zero signups" (commit `510b79f`,
   spec 9.5). Tools are read-only by default; risk is COMPUTED from
   conservative proxies because "NO registry publishes permission/risk
   metadata" (M2a finding). This boundary is "binding on every adapter
   built from it."

4. **Standard-before-compiler.** The static package standard shipped first
   (Phase 0); automation is gated on falsifiable evidence the standard
   generalizes (the N=2/N=3 zero-schema-edit gates,
   `docs/n2_gate_report.md`). "Otherwise revise the standard, don't
   automate it" (design review B3).

5. **No-impersonation.** "You are <person>" framing is forbidden; enforced
   as a machine check (static impersonation ban in `run_evals.py`), a
   guardrail file, and behavioral tests — not just prose.

6. **No-fabrication.** Attribution types (`direct_quote | paraphrase |
   third_party_interpretation | model_inference`, later `quoted_primary`
   with a REQUIRED locator) + confidence + verified flags are mandatory on
   evidence. `TODO_FILL` markers fail validation BY DESIGN — a package
   holding unreviewed drafts cannot validate (`CHANGELOG_STANDARD.md`
   v0.7.1). Third-party compilations are capped: never `direct_quote`
   (Tier A1).

7. **Honest-failure publishing.** The project publishes its own FAILs:
   the defective web-search leakage run was "preserved verbatim +
   reported" (commit `2917804`); the grader-vs-human divergence was
   published before being fixed (Milestone 1c); rp04 was corrected "by
   public correction, not concealment"; the generator gate names its
   misses ("reported not gamed", commit `91b982b`). Grader fixes land
   separately from the changes that benefit from them.

8. **Cost-aware routing.** "Use the cheapest reliable method that passes
   quality thresholds": deterministic tier-0 code first, then cheap →
   mid → strong models, human review last (`docs/model_routing_policy.md`
   priority order 1–5).

9. **Friction is a deliverable.** Authoring pain is recorded, not silently
   absorbed ("the friction record IS the deliverable", N=2 gate); standard
   revisions cite friction IDs (F1–F13, N3-F1–F22) in
   `CHANGELOG_STANDARD.md`, with clean-break renames while pre-release.

10. **Halt-is-a-success.** Scope gates HALT rather than reframe
    (workflow stage 2, "halt beats a reframed answer"); phase gates return
    GO / CONDITIONAL_GO / NO_GO and a NO_GO is a valid, publishable
    outcome.
