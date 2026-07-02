---
id: PLAYBOOK-phase3-evidence-method-extraction
layer: playbook
purpose: Prospective procedure for automating evidence-card and principle extraction from sources — the highest-fabrication-risk phase; no-fabrication must be CODE gates, not prose.
read_when: Planning or building source-discovery, evidence-card, principle-extraction, or attribution-classification automation.
depends_on:
  - ./phase2_builder_primitives.md
  - ./phase6_evaluation_runner.md
used_by:
  - ROUTE-phase-review
tags: [evidence-extraction, attribution, no-fabrication, prospective, primary-source, verified-flag]
retrieval_keywords: [evidence card builder, principle extractor, attribution classifier, direct quote cap, third party interpretation, quoted_primary, verified false, source to principle map, fabrication gate]
---

# Phase 3 — Evidence and methodology extraction (PROSPECTIVE)

**Status: PROSPECTIVE — grounded in plan, not yet executed.** `docs/development_plan.md` Phase 3 / Stage 4 list: source discovery, evidence card builder, principle extractor, source-to-principle mapper, attribution classifier — all ⬜. Everything below extrapolates ONLY from disciplines the project already enforces on hand-authored evidence (guardrail commits `388f06e`, `d7603e3`; friction items N3-F4/F6 and their v0.7 resolutions in `docs/n2_gate_report.md` / `docs/CHANGELOG_STANDARD.md`).

## Goal

Automate extraction of evidence cards and methodology principles from public sources WITHOUT ever fabricating a citation, quote, URL, date, or attribution. This is the highest-fabrication-risk phase in the roadmap: the extractor produces exactly the artifact class (person-claims with sources) whose fabrication the whole standard exists to prevent.

## Allowed work

- Source discovery limited to metadata + read-only fetches (same boundary as `./phase1_tool_discovery.md`).
- Draft evidence cards emitted as `.generated.yaml` with `TODO_FILL` in every judgment-bearing field (claim wording, confidence, attribution), following the M2b non-destructive draft convention (standard v0.7.1) — validation fails on unfilled markers by design, so unvetted extractions cannot enter a shipping package.
- Attribution classification with **caps enforced as code**, mirroring the hand-authoring rules already in `guardrails/citation_policy.md` and the schemas:
  - `direct_quote` requires a primary-source locator; **third-party compilations are ALWAYS capped at `third_party_interpretation`** (the 问答录-compilation rule) — an extractor must never emit `direct_quote` from a compilation.
  - `quoted_primary` (v0.7) is claimable only when a FETCHED secondary source reproduces the primary artifact's text identically, and `primary_artifact_locator` is REQUIRED (schema `allOf/if/then`). The precedent: of all candidate cards at N=3, exactly ONE (`fpe_ev007`) genuinely qualified; unfetched carriers and talk transcriptions stayed capped.
  - Verbatim quotes capped at ≤2 sentences per card (Tier-A licensing rule); paraphrase + locator is the default.
- `verified` flags computed from actual fetch results only: fetched-and-matched ⇒ `verified: true`; everything else ⇒ `verified: false`, honestly (demo2 shipped "1 honest verified:false"; N=3 shipped 12/13 verified with the gap stated).
- Cross-reference wiring: every principle/rule must link to evidence ids that resolve (the runner's cross-reference layer is the enforcement arm), and `source_id` links must be checked — N3-F6 recorded that dangling `source_id` currently validates silently; the extractor phase is where that gate must be added, not worsened.

## Forbidden work

- Emitting any citation, quote, URL, date, or attribution the pipeline did not actually observe in a fetch (security rule 10: "no invented sources, quotes, URLs, dates, or attributions — ever").
- Upgrading attribution beyond what the fetch evidence supports (attribution is capped by evidence class, never by how confident the text sounds).
- Presenting `model_inference` with the confidence of a `direct_quote` (security rule 11).
- Writing directly into governed evidence files, or auto-promoting drafts.
- Trusting an LLM extraction step without a deterministic post-gate (quote-substring check against the fetched text; locator resolution; enum/cap validation).

## Required outputs

1. Extractor(s) emitting draft cards with computed `verified` flags, capped attribution, and TODO_FILL on judgment fields.
2. **Code gates, not prose**: schema-level caps (enum + conditional requirements), a verbatim-substring check for anything claiming quote status, a `source_id`/locator resolution check, and validation failure on unfilled TODO_FILL.
3. A fixture-regeneration gate against the 3 shipped hand-authored evidence sets (same falsifiable-gate pattern as `./phase2_builder_primitives.md`): how many shipped cards does the extractor recover, with named misses and no invented pass bar.
4. An unverified ledger for sources that could not be fetched (paywalls, 403s, dead links) — disclosed, never guessed around (the COPE-mirror precedent: substitution disclosed in `archived_url` notes).
5. Friction report appended to the gate report if the schemas chafe — recorded, not silently patched (the N=2/N=3 discipline).

## Acceptance criteria

- Zero fabricated citations demonstrable by construction: every quote in extractor output is a byte-substring of a fetched document, machine-checked.
- Every card the extractor could not ground is a draft with TODO_FILL or `verified: false` — never a confident card.
- An adversarial evidence reviewer live-checks a sample of URLs and quotes verbatim (the N=2 review live-checked 6 quotes; N=3 live-checked 5 URLs).
- Attribution caps survive mutation tests (revert-the-cap fails the suite, per the v0.6/v0.7 mutation-regression pattern).

## Common failure modes

- **Compilation-as-primary**: quoting a third-party compilation as `direct_quote` — the exact case the citation policy was written against.
- **Confidence laundering**: an extractor upgrading `third_party_interpretation` to `quoted_primary` because two secondary sources agree; identical-reproduction-by-a-fetched-source is the bar, not agreement.
- **Fetch-blocked ⇒ silently skipped**: blocked fetches must enter the unverified ledger (N3-F5: "fetch attempted and blocked" vs "never attempted" must not be conflated).
- **Prose gates**: a rule that lives only in a policy .md is invisible to `validate` (N3-F22 precedent) — every extraction rule needs a schema/test/runner enforcement point.
- **Grader/extractor fixed in the same change that benefits** — inherit the separation rule from `./phase6_evaluation_runner.md`.

## Self-check checklist

- [ ] Is every quote a machine-verified substring of a fetched source?
- [ ] Is every attribution capped by evidence class, with caps in schema/code?
- [ ] Do unfetchable sources appear in an unverified ledger?
- [ ] Are outputs non-destructive drafts that cannot validate until a human fills TODO_FILL?
- [ ] Is there a falsifiable recovery gate against hand-authored fixtures?
- [ ] Did I record schema friction instead of silently editing the standard?
