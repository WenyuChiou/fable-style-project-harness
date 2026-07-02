---
id: PLAYBOOK-phase5-runtime-export
layer: playbook
purpose: Procedure for making packages installable in a real runtime — plugin-superset design, export verification tooling, and honest E2E install verification with explicit UNVERIFIED lists.
read_when: Exporting artifacts to a runtime (plugin, CLI, marketplace), or verifying an install path end-to-end.
depends_on:
  - ./phase4_memory_update.md
  - ./repo_maintenance_playbook.md
used_by:
  - ROUTE-runtime-export
  - ROUTE-phase-review
tags: [runtime-export, plugin, install-verification, E2E, unverified-ledger, smoke-check]
retrieval_keywords: [phc export, plugin superset, marketplace.json, install smoke, fresh user walkthrough, headless install, pointer skill, namespaced command, UNVERIFIED list]
---

# Phase 5 — Runtime export (REAL-partial: primary runtime shipped; others honest gaps)

**Status: REAL-PARTIAL.** The Claude Code export path shipped *de facto* through Milestones 1a/1c rather than as a Phase-5 work item, and `docs/development_plan.md` re-marked the phase honestly from "not started" to PARTIAL. E2E install verification is real (`docs/quality/fresh_user_walkthrough.md`, commit `7134227`). The Codex path is a documented manual fallback only; the generic MCP exporter is "genuinely not started" — stated, not fudged.

## Goal

Make the package installable and runnable in a real runtime with **no separate export step where possible** — the package standard is designed as a strict superset of the runtime's native format (design-review B1: plugin.json + pointer SKILL.md + commands/ + marketplace.json), so "install and run" is a property of the standard, not a converter's output. Then verify the headline install promise by actually exercising it.

## Allowed work

- Superset packaging: package-level runtime manifest, a THIN pointer skill redirecting to the canonical root SKILL.md ("never a second, divergent runtime contract"), per-command frontmatter binding to the plugin root, repo-level marketplace manifest listing every package.
- Export verification tooling: `phc export` verifies plugin-install prerequisites; `--scaffold-missing` only CREATES, never overwrites.
- A zero-dependency pre-install smoke check (`scripts/install_smoke.py` pattern): marketplace manifest parses; every entry's source dir + plugin.json exist; **no package is silently unshipped** (every `examples/*/HARNESS.yaml` must appear); names cross-match; command frontmatter closed with non-empty description and the binding line; pointer skill resolves; optional checks report SKIP when a dependency is absent — "never a silent pass".
- Real E2E verification on a fresh-ish environment: validate → marketplace add (local path) → install → component discovery → run a real command headlessly → verify side effects on disk → uninstall cleanly. The project's run: a ~9-minute headless `/analyze-company Coca-Cola` executed the full staged workflow (competence gate, live retrieval, zero ratings/price targets, citation audit with an honest `verified: false` table, explicit uncertainty), memory writes verified on disk then reverted, clean uninstall.
- Recording every stumble verbatim (bare `/show-sources` fails headless — must use the namespaced form; a cosmetic marketplace-description warning) and feeding fixes back (builder-path `pip install -e .` step added to README ×3 locales after a fresh-eyes P1).

## Forbidden work

- Claiming "installs and runs" without having installed and run it — the walkthrough exists because the headline promise was "finally exercised for real" only at the hardening milestone.
- Extrapolating verified status: the walkthrough separates ✅ VERIFIED (with how) from ⛔ NOT VERIFIED (GitHub-form add while private; interactive TTY flows; cross-session correction flow) — "Nothing here is projected or assumed."
- A second divergent runtime contract (fat runtime skill diverging from the canonical SKILL.md).
- Mutating the user's environment without cleanup in a verification run.
- Faking a runtime path in docs: unshipped exporters are listed as unchecked items ("documented manual path only", "genuinely not started").

## Required outputs

1. Installable package form + marketplace manifest (superset design).
2. Export-verification CLI step + standalone smoke script covered by mutation regression tests.
3. A dated walkthrough doc with a **verified/unverified split table**: per step, status and HOW it was verified (exit codes, quoted outputs, on-disk reads).
4. An honest UNVERIFIED list of everything the environment could not exercise, kept in the doc — not deleted when inconvenient.
5. Doc fixes for every stumble a fresh user would hit, mirrored across locales.

## Acceptance criteria

- Full cycle demonstrated: validate → add → install → run → side-effects verified on disk → uninstall, with captured outputs.
- The smoke check fails loudly on: silently-unshipped package, name mismatch, broken frontmatter, unresolvable pointer skill.
- CI runs runtime validation on every package (the project's CI runs `phc validate` on all three packages on ubuntu+windows × two Python versions).
- Unverified paths are enumerated with the reason they could not be verified.

## Common failure modes

- **Export as an afterthought phase** — design-review C1: every user journey "dies at minute five" if installability arrives last. Fix: invert; installability is an early exit criterion.
- **Verified-by-analogy** — assuming the GitHub-form install works because the local-path form does; the walkthrough refused this inference (repo private ⇒ NOT VERIFIED).
- **Silent packaging drift** — a new package added to examples/ but not the marketplace; caught only by the no-silently-unshipped check.
- **Headless vs interactive divergence** — commands resolving interactively but not in `-p` mode (the namespacing stumble); test the mode users will actually script.
- **Verification that dirties the environment** — memory writes and installs must be reverted/uninstalled; the walkthrough verified cleanup too.

## Self-check checklist

- [ ] Does the package install with NO separate export step (superset design)?
- [ ] Did I actually run the full install→run→uninstall cycle and capture outputs?
- [ ] Are side effects verified by reading the disk, then reverted?
- [ ] Does the walkthrough table split VERIFIED (with how) from NOT VERIFIED (with why)?
- [ ] Does a zero-dep smoke check guard the packaging invariants, with SKIP-not-silent semantics?
- [ ] Are unshipped runtime paths stated as unshipped in the plan and README?
