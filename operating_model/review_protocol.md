---
id: OM-review-protocol
layer: operating_model
purpose: The five-layer review pipeline observed on every shipping commit — adversarial orthogonal-lens review, independent re-verification, code-review verdict gate, explicit-path staging with count assertion, CI watch — with the real catches as evidence.
read_when: Preparing any commit; reviewing a delegate's output; deciding whether a change is ready to ship.
depends_on:
  - ./operating_model.md
  - ./decision_rules.yaml
used_by:
  - ROUTE-pr-review
  - ROUTE-phase-review
  - ROUTE-repo-maintenance
tags: [review, adversarial, verification, staging, ci]
retrieval_keywords: layered review, adversarial reviewer, orthogonal lenses, re-verification, grep old value, code review gate, explicit path staging, count assertion, CI green, real catches
---

# Review Protocol — layered, adversarial, re-verified

Nothing ships on one pair of eyes. Every commit body in this repo records
which layers ran and what they caught (`Co-Reviewed-By:` trailers, all 17
commits). The layers are ordered; later layers assume earlier ones ran.

## Layer 1 — Adversarial reviewers with ORTHOGONAL lenses

Reviewers are framed as adversaries with non-overlapping questions, never as
endorsers:

- Day 1 design review: four-lens panel — end-user journey ×4 personas,
  positioning/competitive (live web research), ruthless design skeptic,
  trust/risk/ethics — "run independently and synthesized by the
  orchestrator", 34 findings (`docs/design_review_2026-07-01.md`).
- Per-round pairs: "gate-honesty" + "correctness" (91b982b); "fresh-eyes
  usability" + "consistency" (7134227); "v0.6 consistency" + "transcript
  authenticity" (f8740f8); "research-integrity" (510b79f);
  "pre-registration honesty" (2917804); "audit fairness" (9532648).
- A REQUEST_CHANGES from one lens outweighs APPROVEs from the others; fixes
  land before the commit, and the catch is named in the commit body.

## Layer 2 — Independent re-verification (never trust the report)

Reviewers re-derive, re-run, and re-grep rather than reading summaries:

- Re-run scripts: "byte-identical scorecard re-runs" (f8740f8); audit YAML
  "reproduces byte-for-byte" (9532648).
- Re-derive numbers by hand: gate-honesty reviewer "hand re-derived package
  numbers reproduce byte-for-byte" (91b982b); fairness reviewer "re-derived
  12+ claims" (9532648).
- Grep-old-value after renames: "independent old-value grep" (f8740f8);
  repo-wide grep + 114/114 pytest after the project rename (4437320).
- Live-check citations: 12 claims re-verified against cited URLs (510b79f);
  5 URLs live-checked (d7603e3); 6 quotes checked verbatim (bd32614).
- Verify on disk, not on agent say-so: the zh-TW mermaid observation conflict
  between agents was "resolved by on-disk verification (0/0/0 mermaid, 6/6/6
  fences)" (490470d).

## Layer 3 — Code-review verdict gate

The code-review skill runs on the diff range; its verdict gates the commit,
and the trigger that fired is recorded in the commit body (e.g. "APPROVE
(triggers 1, 3, 4)" — multi-file, critical-path, delegate-returned). Present
on every shipping commit from f4c826f through 91b982b.

## Layer 4 — Explicit-path staging with count assertion

Files are staged by explicit path and the staged count is asserted against
the expected count before committing: "Explicit-path staging (6 files
asserted)" (510b79f). Concurrent in-flight work on disjoint files is
explicitly excluded and the exclusion is documented in the commit body
(490470d). Never `git add -A` and hope.

## Layer 5 — CI / suite watch to green

The full suite count is stated in every commit body and must be green before
ship (latest: "Suite 638 -> 730 passing", 91b982b). CI runs ubuntu+windows ×
py3.11/3.13 with full pytest plus `phc validate` on all packages (7134227).
Locale-parity and mutation-regression tests are part of the net, not
optional extras.

## The real catches (why the layers exist)

| Catch | Layer | Evidence |
|---|---|---|
| Silent-pass evaluation: self-assigned scorecard numbers with no runner — "the exact fabrication pattern the project exists to prevent" (finding C2, critical) → computed scorecards mandated | 1 | `docs/design_review_2026-07-01.md`; fixed in 046d0e3 |
| Question-echo grader artifact: rp04's "genuine recognition" contamination claim was FALSE — corrected by public notice, results recomputed, case moved to UNSCORED | 1+2 | 2917804; `docs/comparisons/retracted_paper_outcome_pilot.md` |
| In-excerpt leakage identifier: rp04's identifier list violated the pre-registration's own contract ("Hasilpur" appears in its excerpt) — found by post-run audit | 2 | pilot report §2.1 |
| Passive-voice verdict evasion: "acceptance is recommended" slipped past the scope_refusal grader — reviewer-found, confirmed on disk, closed with a pinned evasion fixture | 1+2 | 9532648 |
| recommend-tools bypassed the shared overwrite guard (P1) — correctness reviewer REQUEST_CHANGES; fixed + regression tests before commit | 1 | 91b982b |
| Fresh-eyes P1s: builder-path README missing `pip install -e .`; N=3 audit-output taxonomy stale | 1 | 7134227 |
| Stale status lines: parity agent caught two stale "299" README status lines | 2 | e7f0fc6 |
| Grader false positives/negatives: refused-price-target negation false positive; hyphen-only `non-impersonation` marker missing a genuine disclosure — both closed by documented-list extension + mutation regression tests, transcripts unchanged | 1+2 | bd32614; `CHANGELOG_STANDARD.md` v0.7 DISCLOSURE_MARKERS |

## Non-negotiables

1. Reviewer lenses must be orthogonal; apparent verdict conflict is usually
   partition, and synthesis is the orchestrator's job.
2. Grader/gate fixes land SEPARATELY from the change that benefits
   (f8740f8: grader "deliberately NOT loosened in the change that would
   benefit from it"; v2 landed next round, 9532648).
3. Corrections are published, never concealed: "fixed by public correction,
   not concealment" (2917804).
4. Frozen transcripts are immutable — regrade via the runner; never edit the
   transcript (CHANGELOG v0.7: "the frozen transcripts are unchanged and
   regraded via the runner").
