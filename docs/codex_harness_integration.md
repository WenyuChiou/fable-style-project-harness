---
id: DOC-codex-harness-integration
layer: doc
purpose: Full Codex and AGENTS.md integration path so future Codex work can use this harness before planning
read_when: Wiring this harness into Codex, OpenCode, Cursor, Hermes, or any AGENTS.md-convention runtime; preparing future work to use the harness globally
depends_on:
  - ../core/GLOBAL_BOOTSTRAP.md
  - ../AGENTS.md
  - ../SETUP.md
  - ./agent-routing-policy.md
  - ./codex-delegation-policy.md
  - ./codebase_memory_indexing.md
used_by: [README, SETUP, operator-session]
tags: [codex, opencode, hermes, agents-md, integration, global-pointer]
retrieval_keywords: [Codex harness integration, AGENTS.md pointer, OpenCode, Hermes, future Codex work, global bootstrap]
---

# Codex Harness Integration

## Goal

Make the harness available before future Codex work starts, especially for long, multi-step, multi-agent, completion-sensitive, or governance-sensitive tasks.

This integration is intentionally a pointer, not a prompt dump. Codex should read the routed files from this repo and follow the current bytes on disk.

## Minimal Pointer

Run `python scripts/setup_harness.py --print-wiring` and paste the emitted absolute-path pointer into a repo-level or global `AGENTS.md` used by Codex and other AGENTS.md-convention agents. The generic form is:

```text
For large, multi-agent, high-risk, phase-gated, or completion-sensitive tasks, read <harness-root>/core/GLOBAL_BOOTSTRAP.md and follow its routing. For AI-harness maintenance, README/evidence work, AGENTS.md/CLAUDE.md/hooks/skills/settings review, read <harness-root>/.claude/skills/adaptive-harness/SKILL.md. Load routed files only; do not bulk-read the harness repo.
```

Use the generated absolute path for real sessions; keep `<harness-root>` only in portable documentation.

## Runtime Matrix

| Runtime | How it enters | What is verified |
|---|---|---|
| Codex | Reads `AGENTS.md`; use the pointer above for other repos. | Codex scoped mechanical edit and no-commit compliance executed in mc08/mc09, n=1. |
| OpenCode | Uses the AGENTS.md convention; place the same pointer in the project or global rules file. | Instruction path documented; live OpenCode harness execution is not yet scored. |
| Cursor | Uses project instructions / AGENTS.md-style repo context. | Same pointer path; live Cursor harness execution is not yet scored. |
| Hermes | Router surface; add the routing row from `--print-wiring`. | Hermes can run deterministic scans and route semantic judgment upward. |
| Claude Code | `SKILL.md` and optional global stub via `--wire-skill --wire-claude`. | Skill-aware path is the primary harness runtime. |

## Codex Operating Rules After Activation

1. Classify the task before editing.
2. Read only the files named by the route.
3. For completion claims, load the completion-integrity route and verify raw artifacts over derived reports.
4. For settings, permissions, hooks, cron, routing, or destructive command allowlists, split safe mechanical edits from governance decisions and stop for explicit approval or patch proposal.
5. For codebase discovery, prefer codebase-memory MCP when available; otherwise fall back to `rg` and then open the canonical file.
6. Do not treat Codex as final authority on its own output. Review and verification stay author-agnostic.

## Verification

Run these after wiring:

```bash
python validation/integration_check.py
python scripts/setup_harness.py --print-wiring
python scripts/summarize_harness_ab_pilot.py --markdown
```

Manual check for another repo:

1. Start a fresh Codex session in that repo.
2. Ask for a high-risk or multi-step task.
3. Confirm the session reads `core/GLOBAL_BOOTSTRAP.md` before planning.
4. Confirm the final answer lists skipped checks or unknowns instead of silently passing.

## Known Gaps

- OpenCode and Cursor are documented through the AGENTS.md-compatible entry path, but live scored runs are not yet in `benchmarks/model_compatibility_cases.yaml`.
- The GPT-5.5 forced-activation pilot did not show quality lift; use the harness for discipline and evidence, not as a blanket capability upgrade.
- Governance-sensitive permission changes need stronger stop behavior; T5 in the pilot exposed this gap.
