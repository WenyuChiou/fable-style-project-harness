---
id: PROMPT-codex-task-brief-template
layer: prompt
purpose: "Fill-in template for scoped Codex execution: context, goal, in/out of scope, allowed files, constraints, acceptance criteria, verification commands, output contract. Codex must not commit unless explicitly asked."
read_when: Before delegating any mechanical multi-file / boilerplate / migration / test-skeleton task to Codex.
depends_on:
  - ../docs/agent-routing-policy.md
  - ../operating_model/decision_rules.yaml
  - ../operating_model/review_protocol.md
used_by:
  - DOC-agent-routing-policy
  - DOC-agent-optimization-runbook
  - codex-runtime
tags: [prompt, codex, delegation, task-brief, template, scoped]
retrieval_keywords: [codex brief template, scoped codex task, in scope out of scope,
  allowed files, acceptance criteria verification commands, output contract,
  codex do not commit]
---

# Codex task-brief template

**Purpose.** A copy-paste-ready fill-in brief for delegating one **scoped, mechanical**
unit of work to Codex — repeated multi-file edits, boilerplate, migration, test
skeletons, or a clear refactor with objective acceptance criteria.

**Provenance.** This artifact encodes the operator's Hermes / Claude Code / Codex stack
(source: model-routing-benchmark `universal_agent_optimization_prompt.md`) bound to this
harness's existing doctrines cited inline; it is NOT distilled from
method-harness-compiler.

**Codex is a scoped executor, never final authority.** Codex output is never a completion
claim, never the root-cause verdict, and never the release gate. Its diff ships only after
the layered review gate (`../operating_model/review_protocol.md`) run by the orchestrator.
Routing rationale: `../docs/agent-routing-policy.md` (DOC-agent-routing-policy) — Codex maps
to the tier-2 `balanced` mechanical-executor class of `../operating_model/model_routing_policy.yaml`.

## When to use

- The task is mechanical and repetitive with a stable pattern (batch edits, scaffold,
  migration, test skeletons) and has **no security / governance / release surface**.
- Acceptance is objectively checkable (a command passes, a symbol is gone, a count matches).

Do NOT use this template for: ambiguous root-cause debugging, architecture/design,
security or governance decisions, release gates, or any completion claim — those stay on a
Claude Code surface per `../docs/agent-routing-policy.md`.

## The fill-in template (copy-paste-ready)

Fill every bracketed placeholder. Delete no labeled section — if one is empty, write `none`.

```text
# Codex task brief

## Context
[2-4 sentences: what repo/module, what state it is in, why this change. Point to the
plan or ticket. Codex should not have to infer intent.]

## Goal
[One sentence, imperative, objectively checkable. "Rename X to Y across the listed files",
not "clean up the naming".]

## In scope
[Bullet list of the exact transformations to perform. Concrete and enumerable.]

## Out of scope
[Bullet list of things NOT to touch — behavior changes, unrelated refactors, formatting
sweeps, dependency bumps. Anything not listed here AND not in "In scope" is forbidden.]

## Files allowed
[Explicit list of file paths Codex may edit. EVERYTHING NOT LISTED HERE IS FORBIDDEN —
do not create, rename, delete, or edit any other file. If a needed file is missing from
this list, STOP and report instead of editing it.]

## Constraints
- Preserve existing conventions (style, naming, imports, file layout) exactly.
- Deterministic-first (DR-001): no nondeterministic edits; identical input yields identical diff.
- No new dependencies unless explicitly listed here: [list, or "none"].
- On any uncertainty or missing information, STOP and report — do not guess (DR-002).

## Acceptance criteria
[Objectively checkable bullets. Each must be verifiable by a command or a grep, e.g.
"grep -r 'oldName' returns zero hits in the allowed files", "the N call sites now use Y".]

## Verification commands
[Exact commands to run, in order. Codex MUST run each and paste the real output back —
not a description of it. e.g.
  pytest tests/unit/test_foo.py -q
  grep -rn "oldName" src/  # expect: no matches
Paste stdout/stderr verbatim for each.]

## Output contract
Return exactly two things:
1. SUMMARY: 2-4 sentences on what changed and whether every acceptance criterion is met.
2. CHANGED-FILES: a list of every file you modified, one path per line (no others).
Also paste the verification-command output required above.
do not commit unless explicitly requested — and never push. Leave the working tree
staged-or-clean per instruction; the orchestrator reviews the diff and stages it.
```

## How the orchestrator uses this

1. **Brief first.** Write the filled brief before invoking Codex. A vague brief is the
   single largest source of bad delegate output — the "Files allowed" and "Acceptance
   criteria" sections are non-negotiable.
2. **Delegate-returned is a mandatory review trigger.** On return, review the diff under
   the layered gate (`../operating_model/review_protocol.md`) — Codex output does not get a
   pass because it is "just mechanical".
3. **Re-verify on disk (DR-021).** Do not trust Codex's summary or its CHANGED-FILES list;
   confirm the actual on-disk changes match, and re-run the verification commands yourself.
4. **Explicit-path staging (DR-006).** Stage each file by explicit path and assert the
   staged file count against the CHANGED-FILES list before any commit.
5. **Ship only through the gate.** Codex output reaches a commit only after review passes;
   Codex itself never commits, never pushes, never declares the task done.

## Examples

A filled mini-brief — "rename symbol across N files":

```text
# Codex task brief

## Context
The auth module renamed its token helper. `getSessionTok` is the old name; the new name is
`getSessionToken`. The definition is already renamed; the 6 call sites still use the old name.

## Goal
Update all call sites of `getSessionTok` to `getSessionToken` across the listed files, no behavior change.

## In scope
- Replace the identifier `getSessionTok` with `getSessionToken` at every call site.

## Out of scope
- No signature changes, no logic changes, no import reordering, no formatting sweep.
- Do not touch the definition (already renamed) or any test fixtures' recorded data.

## Files allowed
- src/auth/login.ts
- src/auth/refresh.ts
- src/api/middleware.ts
- src/api/handlers/session.ts
- src/pages/account.tsx
- src/pages/settings.tsx
(Nothing else. If a 7th call site exists outside this list, STOP and report it.)

## Constraints
- Preserve existing conventions exactly.
- Deterministic-first (DR-001).
- No new dependencies (none).
- On uncertainty, STOP and report (DR-002).

## Acceptance criteria
- grep -rn "getSessionTok\b" src/ returns zero matches (word-boundary; must not match the new name).
- Each of the 6 files now references `getSessionToken`.
- No file outside "Files allowed" is modified.

## Verification commands
  grep -rn "getSessionTok\b" src/        # expect: no matches
  git status --porcelain                 # expect: only the 6 allowed files, modified
  npm run typecheck                      # expect: exit 0

## Output contract
1. SUMMARY: what changed + all acceptance criteria met?
2. CHANGED-FILES: exact list of modified paths.
Paste the three verification outputs verbatim.
do not commit unless explicitly requested — and never push.
```

## Anti-patterns

| Anti-pattern | Why it fails | Do instead |
|---|---|---|
| Vague scope ("clean up the module") | Codex invents scope; diff sprawls | One imperative Goal + enumerated In scope |
| No "Files allowed" list | Codex edits files you never intended | Explicit allow-list; everything else forbidden |
| Letting Codex `git commit` / `git push` | Bypasses the review gate; unreviewed output ships | "do not commit unless explicitly requested"; orchestrator commits after review |
| Using Codex for root-cause / security / governance / release | Codex is not final authority (DOC-agent-routing-policy) | Keep those on a Claude Code surface |
| Accepting output with no CHANGED-FILES list | Cannot re-verify on disk (DR-021) or count-assert staging (DR-006) | Require the Output contract's CHANGED-FILES list every time |
| Trusting Codex's "done" / summary as verification | Summary is a claim, not evidence (DR-011 no-silent-pass) | Re-run Verification commands yourself before staging |

**Standing rule:** do not commit unless explicitly asked. The orchestrator reviews the diff,
re-verifies on disk, then stages and commits — Codex does neither.
