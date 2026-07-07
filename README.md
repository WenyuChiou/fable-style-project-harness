---
id: README
layer: doc
purpose: Explain what this adaptive harness system is, what it is not, and how to enter it
read_when: First contact with the repo, or when unsure how the pieces fit
depends_on: [context/L0_bootstrap.md, HARNESS.yaml, docs/publication_status.md]
used_by: [ROUTE-phase-review, ROUTE-tool-discovery, ROUTE-pr-review, ROUTE-eval-design, ROUTE-memory-update, ROUTE-runtime-export, ROUTE-repo-maintenance, ROUTE-ab-test-design]
tags: [entrypoint, overview, publication, adaptive-harness]
retrieval_keywords: [what is this repo, harness overview, how to use, entrypoint, publication status, progressive disclosure, adaptive harness skill system]
---

# fable-style-project-harness

A progressive-disclosure operating harness your AI agent loads a little at a time — it gates every "done" claim, keeps context cost low, and reviews and prunes itself on a cadence.

## Quickstart

```bash
git clone https://github.com/WenyuChiou/fable-style-project-harness
cd fable-style-project-harness
git config core.hooksPath scripts/hooks     # enable the pre-commit gates (recommended)
python validation/integration_check.py      # 51 self-checks; all-PASS = your clone works
```

Or simply tell whatever AI you use — Claude Code, Codex, Cursor, Hermes — *"read `SETUP.md` and set this up"*: one idempotent script wires everything for its own runtime (`python scripts/setup_harness.py`, flags per runtime).

## Two ways to use it

Pick per task — you don't need Mode A for simple work.

**A. Run big tasks the Fable way** — tell Claude Code: *"read `core/GLOBAL_BOOTSTRAP.md` and follow it"* (or add a two-line pointer in your own `~/.claude/CLAUDE.md`). It loads ~5% of this repo per task via `ROUTES.yaml`, works the task loop, and gates every done-claim. Use it for multi-agent / long-horizon / expensive-if-wrong work; skip it for simple tasks (frontier models ace those bare — measured, see `distillation/distillation-log.md`).

**B. Audit and continuously improve your own AI setup** (your CLAUDE.md, hooks, skills):

```bash
python scripts/run_ai_review.py --mode harness_cleanup_review --target <your-repo>
# then in a Claude session: read reports/ai-review/latest.json, answer
# prompts/ai-review-modes.md's checklist, save findings.json, and:
python scripts/run_ai_review.py --mode harness_cleanup_review --ingest findings.json
python scripts/run_adaptive_harness_review.py --mode rolling_improvement_review --target <your-repo>
python scripts/run_adaptive_harness_review.py --mode patch_proposal   # high-risk items -> a sheet YOU approve
```

Findings enter only through schema-validated `--ingest`, and scheduled runs are report-only by design — deterministic scripts compute, LLMs judge, humans approve (the full contract is [`docs/ai_review_adaptive_harness_integration.md`](docs/ai_review_adaptive_harness_integration.md)). Approve a proposal → commit with `applies REC-YYYYMMDD-NNN` in the message → the next rolling run marks it resolved with the commit sha. Non-Claude agents enter via [`AGENTS.md`](AGENTS.md).

## Is it proven useful?

Use this system for discipline, economy (~90-98% less context loaded per task; same gate behavior at ~55% less standing-instruction context), and audit trail — NOT for capability: it does NOT make a frontier model smarter (eight consecutive ceiling experiments hit plain-Opus 88-100%, up to N=120 buried requirements retained with zero drops, harness OFF), so its measured value concentrates only where mistakes are expensive, work is long, or several agents run at once, and its own guidance says to skip the ceremony on simple tasks.

The full tested ledger — including the negative results — is [`docs/evidence.md`](docs/evidence.md).

## What this repo IS

- **Method summaries, procedures, rubrics, examples, and decision records** that any observer of the `method-harness-compiler` repo could reconstruct from its docs, schemas, scripts, tests, example packages, and git log (17+ commits with rich trailers).
- **A progressive-disclosure context package**: small layered files (`context/L0`–`L5`), a task router (`ROUTES.yaml`), per-route file lists, and datasets keyed by stable IDs (`TE-###`, `FM-###`, `EC-###`, `RE-###`, `ROUTE-*`, `RUBRIC-*`, `PLAYBOOK-*`).
- **Its own git repo**, deliberately gitignored by the parent project (parent commit `965c68e`: "private harness distillation must never ship with the (future-public) repo").

## What this repo is NOT

- **Not a prompt dump.** Nothing here is a private system prompt, hidden chain-of-thought, or internal model instruction. Everything is reconstructed from published artifacts.
- **Not hidden internals.** No API keys, tokens, personal contact info, or private chat content — see [`docs/publication_status.md`](docs/publication_status.md).
- **Not a static skill package.** The adaptive layer exists precisely so the harness gets reviewed and pruned on a cadence; a growing pile of unreviewed rules is a defect the system itself must flag.
- **Not the method-harness-compiler itself.** The source project compiles expert-methodology packages; this repo distills *how that project is operated* so the same working method can be applied elsewhere.

## Entry points (Skill-like activation)

Thin entry files let different runtimes *discover and launch* the harness on their own, instead of a human explaining it each time:

| File | Convention it serves | When it fires |
|---|---|---|
| [`BOOTSTRAP.md`](BOOTSTRAP.md) | Universal shortest entry | Paste-a-pointer for any model: "read BOOTSTRAP.md and follow it" |
| [`AGENTS.md`](AGENTS.md) | Repository agent instructions | Auto-read at session start by convention-following coding agents (Codex, Cursor, and similar) |
| [`SKILL.md`](SKILL.md) | Skill discovery (`name`/`description` frontmatter) | Skill-aware runtimes (Claude Code and similar) surface it as an invocable capability |
| [`core/GLOBAL_BOOTSTRAP.md`](core/GLOBAL_BOOTSTRAP.md) | Portable path for work on any OTHER project | Loads only the `core/` discipline layer and never the project-bound files (L1/L2, phase playbooks, `memory/`) |

The first three converge on the same startup ladder below — they are launchers, not rule stores, so the entry layer stays short and stable. `core/GLOBAL_BOOTSTRAP.md` is the portable path for applying the discipline to any other project.

## How to use it (the reading order)

1. **`context/L0_bootstrap.md`** — the minimal first read, under 300 words.
2. **`context/L2_current_phase.md`** — what phase the source project is in, what is allowed and forbidden right now.
3. **`context/L3_task_router.md`** — classify your task into one of the 8 pinned routes.
4. **`ROUTES.yaml`** — get the exact file list for your route.
5. **Route files only.** Open the rubrics / playbooks / examples the route lists — nothing else, per [`context/L4_progressive_disclosure_policy.md`](context/L4_progressive_disclosure_policy.md).

`context/L1_project_constitution.md` (thesis, non-goals, stable principles) and `context/L5_full_context_map.md` (one-line directory map) are reference layers: load them when a route file points to them or when ambiguity survives the routed files.

## Publication status

**PUBLIC** (visibility verified 2026-07-06). Public-safe posture: no secrets, no hidden reasoning, no private chat exports, no credentials, no local telemetry; generated review reports stay gitignored. The repeatable public-safety review checklist and the honest outstanding-items ledger (license: MIT, decided 2026-07-06) live in [`docs/publication_status.md`](docs/publication_status.md). The `HARNESS.yaml` constraints block (`public_safe_after_human_review`, `no_secrets`, `no_hidden_reasoning`) is binding on every future edit.

## Provenance discipline

Every claim traces to an observable artifact: a file path in `method-harness-compiler` (docs/, schemas/, scripts/, tests/, the three example packages) or a commit hash in its git log. Dataset records carry a `source_artifact` field and a `synthetic` flag; grounded (`synthetic: false`) records are preferred. If you cannot cite an artifact, do not write the claim — the source project's no-fabrication rule (`TODO_FILL`-fails-validation, UNSCORED-never-guessed) applies here too.
