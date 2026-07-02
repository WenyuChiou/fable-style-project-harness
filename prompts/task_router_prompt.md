---
id: PROMPT-task-router
layer: prompt
purpose: Classify an incoming request into exactly one of the eight routes and
  name the minimal file set to execute it.
read_when: Immediately after bootstrap, whenever a new user request arrives.
depends_on:
  - ./weak_model_bootstrap_prompt.md
used_by:
  - ROUTE-phase-review
  - ROUTE-tool-discovery
  - ROUTE-pr-review
  - ROUTE-eval-design
  - ROUTE-memory-update
  - ROUTE-runtime-export
  - ROUTE-repo-maintenance
  - ROUTE-ab-test-design
tags: [routing, classification, task-type]
retrieval_keywords: [which route, classify task, task type, route table,
  routing decision]
---

# Task router prompt

Classify the request BEFORE working. Output four lines — `restatement:`,
`task_type:`, `route:`, `reading_set:` — then proceed under that route only.

## Procedure

1. **Restate** the request in one sentence (your words, not the user's).
2. **Identify the current phase** of the project if the request is
   phase-sensitive (check the operating model / latest changelog entry).
3. **Match against the route table** below. If two routes seem to apply, the
   request is probably two tasks: split it and route each part. Never blend
   route procedures.
4. **List the reading set**: the route file + its `depends_on` rubric(s) and
   checklist(s). Read nothing else.

## Route table

| If the request is about... | route |
|---|---|
| Reviewing a plan, spec revision, phase gate, or GO/NO_GO decision | ROUTE-phase-review |
| Surveying registries, skills, MCP servers, APIs, or data sources (metadata-only research) | ROUTE-tool-discovery |
| Reviewing a diff, commit range, PR, or delegate output before merge | ROUTE-pr-review |
| Designing or critiquing eval specs, graders, baselines, ablations, outcome evals | ROUTE-eval-design |
| Updating memory files, friction inventories, correction records, changelogs-as-memory | ROUTE-memory-update |
| Exporting a package to a runtime (plugin form, SKILL.md, commands/), install smoke | ROUTE-runtime-export |
| Repo hygiene: test infrastructure, auto-discovery, scratch cleanup, ignore rules, doc structure | ROUTE-repo-maintenance |
| Designing a comparison (harness vs baseline, A/B arms, blinded grading, pre-registration) | ROUTE-ab-test-design |

## Disambiguation rules (learned from the repo's history)

- A **schema edit inside a PR** routes to ROUTE-pr-review, but the reviewer
  must apply `../rubrics/eval_quality_rubric.yaml` EQ-6 and
  `../rubrics/pr_review_rubric.yaml` PR-2 (mutation-test gate) — do not re-route to
  eval-design.
- A **grader fix** is eval work (ROUTE-eval-design) even when it arrives as a
  one-line diff: it needs the divergence-publication + separate-commit
  discipline.
- **"Add a tool" requests** are two routes: discovery (metadata, computed
  risk) then pr-review (the ToolCard diff). Discovery never executes anything.
- If the request cannot be classified, say so and ask; do not pick the
  closest route and improvise.
