# Branch and long-term harness checks

## Branch safety

- [ ] Fable checked `git status`.
- [ ] Fable checked current branch.
- [ ] Fable did not work directly on `main`.
- [ ] Fable created or selected a safe working branch.
- [ ] Dirty working tree, if any, was reported before edits.
- [ ] No unrelated human changes were overwritten.

## Long-term harness qualities

- [ ] Maintainability improved or preserved.
- [ ] Observability improved or preserved.
- [ ] Traceability improved or preserved.
- [ ] Rollback safety improved or preserved.
- [ ] Scheduled mode remains report-only by default.
- [ ] AI-review findings can feed adaptive-harness.
- [ ] adaptive-harness can maintain AI-review over time.
- [ ] Lower-tier model boundaries are explicit.
- [ ] Codebase memory / KG, if used, supports retrieval and impact mapping rather than duplicating memory.

# Phase Execution Checklist

## Before starting

- [ ] Working branch created.
- [ ] Repo clean or current changes intentionally kept.
- [ ] Phase prompt selected.
- [ ] Fable / Fabo set to ultracode.
- [ ] Human understands whether this phase may edit files or only propose patches.

## Phase 1 completion gate

- [ ] AI-review slash command exists or is preserved.
- [ ] AI-review runner exists.
- [ ] CLAUDE.md / Codex delegation policy checked.
- [ ] Tool/code invocation audit exists.
- [ ] AI-review reports can be generated.
- [ ] AI-review history can be appended.
- [ ] Benchmark scaffold exists.
- [ ] Dry-run does not modify repo.
- [ ] High-risk changes are patch proposals only.

## Phase 2 completion gate

- [ ] adaptive-harness skill exists.
- [ ] AI-review integration doc exists.
- [ ] Shared schema exists.
- [ ] Rolling improvement loop exists.
- [ ] Adaptive harness runner exists.
- [ ] Reports/harness scaffold exists.
- [ ] Adaptive-harness can read AI-review latest JSON.
- [ ] Public/private posture conflict resolved.
- [ ] Benchmark scaffold connected to recommendations.
- [ ] Scheduled mode defaults to report-only.

## Phase 3 completion gate

- [ ] AI-review scripts run.
- [ ] Adaptive-harness scripts run.
- [ ] JSON / Markdown / history outputs validated.
- [ ] Skill activation paths validated.
- [ ] Opus/Fable test status recorded.
- [ ] Sonnet test status recorded.
- [ ] Haiku test status recorded.
- [ ] Codex test status recorded.
- [ ] PASS / FAIL / PARTIAL / UNVERIFIED matrix completed.
- [ ] Final verdict: READY / CONDITIONAL_READY / NOT_READY.


## Optional codebase memory / KG overlay gate

- [ ] Existing codebase memory setup identified.
- [ ] Decided `KG_NEEDED` or `NO_KG_NEEDED_NOW`.
- [ ] If KG needed, minimal schema created.
- [ ] If KG not needed, lightweight indexing/query/test plan recorded.
- [ ] AI-review can use retrieval / memory without bulk-reading.
- [ ] adaptive-harness can link repeated/resolved findings.
- [ ] Lower-tier model retrieval path checked.
- [ ] Retrieval / KG smoke tests proposed or added.
- [ ] Scheduled index/KG update defaults to report-only.
- [ ] No secrets/private data/hidden reasoning stored in memory or KG.
