---
id: PLAYBOOK-phase7-public-release
layer: playbook
purpose: Prospective procedure for flipping the repo public — content review gates, no-secrets scan, audit-article fairness review, non-affiliation and licensing checks, human sign-off.
read_when: Preparing any public release, publishing an audit of a third party, or reviewing pre-flip readiness.
depends_on:
  - ./phase6_evaluation_runner.md
  - ./repo_maintenance_playbook.md
  - ./pr_review_playbook.md
used_by:
  - ROUTE-phase-review
  - ROUTE-repo-maintenance
tags: [public-release, prospective, secrets-scan, licensing, non-affiliation, human-gate, audit-fairness]
retrieval_keywords: [public flip, release gate, NOTICE file, takedown, non-affiliation notice, no fake badges, tier 4 human review, audit article, license carve-out, secrets scan]
---

# Phase 7 — Public release (PROSPECTIVE)

**Status: PROSPECTIVE — grounded in plan, not yet executed.** `docs/development_plan.md` Phase 6 (public release: GitHub repo public, demo, technical blog, architecture diagram, baseline comparison, evaluation report) is ⬜ NOT STARTED; the repo is private. Everything below extrapolates from protections and gates the project ALREADY built in anticipation (Tier-A commit `388f06e`; release-status gating in `docs/evaluation_framework.md` §6.1; the published-audit fairness protocol of commit `9532648`; the private-harness gitignore of `965c68e`).

## Goal

Flip the repo public only after every content, legal, safety, and honesty gate passes — with human review as the final, non-delegable gate. Public release always requires human sign-off (model routing policy: Tier 4; evaluation framework: `public_demo` requires "Tier 4 human review completed", and high-risk domains require human review at EVERY status promotion, not only the first).

## Allowed work

- **Release-status gating by computed scorecard**: `release_status` is derived, not self-declared; `public_demo` requires every safety test passing (safety is a veto, not a weight), zero unsupported person-claims, ≥1 documented baseline comparison, and human review. Tier-A A3 pins thresholds: ≥90% verified sources, zero unverified direct quotes, URLs resolving. Any confirmed fabricated citation caps status at experimental until resolved. Demotion is automatic on later failures.
- **Licensing/attribution sweep**: NOTICE file excluding quoted evidence text from the MIT grant; verbatim-quote caps honored (≤2 sentences/card); compilation sources cited by locator only; `source_license`/`redistribution_allowed` fields populated.
- **Person/subject protections**: non-affiliation notices in README + SKILL.md ("not affiliated with, endorsed by, or reviewed by …"); `subject_status` declared; published opt-out/takedown process; methodology-first naming (person appears as cited evidence subject, not brand).
- **No-secrets / private-content scan** before flip: the repo already enforces that the private harness distillation "must never ship with the (future-public) repo" (`agent_harness/` gitignored, `965c68e`); extend the same discipline to keys, tokens, personal contact info, and private chat content anywhere in history and tree.
- **Audit-article review before publishing any third-party audit**: the ai-berkshire precedent — pin the audited commit; treat the clone strictly as data (never execute/import); every number copied from runner-emitted YAML that "reproduces byte-for-byte"; an independent fairness reviewer re-derives the claims (12+ re-derived); the tone credits the target's strengths; the honest framing is explicit ("a 0.02 does not mean the pack is 2% good — it means almost none of what makes it good is machine-auditable"). A published audit converts an incumbent into a test subject; unfairness converts the publisher into the story.
- **README honesty pass**: honest status line, no fake badges (the project kept "no badge while private" and replaced the 'no CI' clause only when CI actually existed); locale mirrors synced with parity tests.

## Forbidden work

- Flipping public with any failing safety test, unresolved fabricated citation, or unfilled TODO_FILL anywhere in shipped packages.
- Publishing quality numbers the runner did not compute, or an audit claim not present in the runner-emitted companion YAML.
- Shipping the private distillation, credentials, or personal data — scan tree AND history.
- Self-declared release status; skipping the human gate; treating the flip as reversible ("cheap to do while the repo is private; expensive after" applies to everything public).
- Publishing a third-party audit without pinning the snapshot and offering a reproduce-it-yourself path.

## Required outputs

1. Pre-flip gate report: item-by-item pass/fail against the `public_demo` gate conditions, with file-path evidence.
2. Secrets/private-content scan result (tree + history), recorded.
3. Licensing checklist: NOTICE present, quote caps verified, per-card license fields, non-affiliation notices in every package + locale.
4. For any launch audit article: pinned-commit method section, runner-emitted YAML companion, fairness-review record, reproduce-commands block.
5. Human sign-off record naming who approved and what they reviewed (Tier 4).
6. Post-flip verification: public install path (the GitHub-form marketplace add recorded as NOT VERIFIED while private in `docs/quality/fresh_user_walkthrough.md`) finally exercised and the walkthrough updated.

## Acceptance criteria

- Every gate condition maps to a computed check or an explicit human review — nothing passes by assertion.
- All UNSCORED/unverified items are either resolved or explicitly listed in the release notes (honest-failure publishing extends to launch day).
- A stranger can reproduce the headline claims (install, eval numbers, audit numbers) from the public tree alone.

## Common failure modes

- **Legal exposure discovered post-flip** — design-review C4/C5 (quote licensing, living-person naming) were rated critical precisely because "a publisher takedown is the most likely public failure mode"; the Tier-A layer exists to be verified NOW, not rebuilt at flip time.
- **Marketing numbers outrunning computed numbers** — the README trust section uses real computed-scorecard numbers including the FAILs; keep it that way at launch.
- **Audit article as attack piece** — fairness review + strengths-crediting tone is what makes the wedge artifact publishable.
- **Stale walkthrough claims** — install instructions that were only verified in private form must be re-verified public.
- **History leaks** — a clean tree with dirty history still leaks; scan both.

## Self-check checklist

- [ ] Do all safety tests pass, with zero fabricated-citation incidents open?
- [ ] Secrets/private-content scan clean on tree AND history (agent_harness/ still ignored)?
- [ ] NOTICE, quote caps, non-affiliation, takedown process all present and test-pinned?
- [ ] Every public number computed and reproducible by a stranger?
- [ ] Audit articles: pinned snapshot, byte-reproducing YAML, fairness review done?
- [ ] Human (Tier 4) sign-off recorded?
