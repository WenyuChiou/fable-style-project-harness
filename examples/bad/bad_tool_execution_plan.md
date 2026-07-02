---
id: EXAMPLE-bad-tool-execution-plan
layer: example
purpose: NEGATIVE example — a tool-discovery plan that auto-installs and executes discovered MCP servers during research, crossing the trust boundary.
read_when: Calibrating what NOT to do during tool/registry research; paired critique explains each violation.
depends_on:
  - ../critiques/critique_bad_tool_execution_plan.md
  - ../golden/good_tool_discovery_report.md
used_by:
  - ROUTE-tool-discovery
tags: [negative-example, auto-install, tool-execution, trust-boundary, synthetic]
retrieval_keywords: [auto install MCP, npx install, execute discovered tool, sign up API key, curl pipe bash, tool research shortcut]
source_artifact: synthesized (violates the read-only rule the real plan pinned in docs/tool_discovery_research_plan.md §9.5 and the M2a report honored)
synthetic: true
---

> **NEGATIVE EXAMPLE — do not imitate.** The real M2a research program investigated 27
> sources with zero installs, zero executions, zero signups. This plan does the
> opposite. See `../critiques/critique_bad_tool_execution_plan.md`.

# Tool Discovery Sprint — "hands-on evaluation" plan

## Approach

Reading registry metadata tells you nothing. The only way to evaluate a tool is to run
it. For each of the ~30 candidate registries and their top hits:

1. **Install everything that looks relevant.** For each MCP server found:
   `npx -y <server>@latest` straight into the main development machine's global config
   so all sessions can use it immediately. Where a server ships an install script,
   `curl -s <url> | bash` is fastest.
2. **Register API keys as we go.** Sign up for every data source with the team email and
   drop keys into `.env` so probes are unthrottled. We can rotate them later.
3. **Exercise write paths.** A tool that can only be read-tested is only half-tested —
   for filesystem and database servers, create/update/delete a few records on the dev
   box to confirm write behavior.
4. **Trust registry safety labels.** If the registry marks a skill "safe", skip the
   source read; the moderation pipeline already checked it.
5. **Score from experience.** After a week of daily-driving the installed set, each
   researcher assigns a 1-10 gut score per tool. No need to record which endpoint or
   page a claim came from — the score is the deliverable.

## Efficiency notes

- Run the installed servers with default permissions; sandboxing each one would double
  the sprint.
- If a server needs OAuth, click through with the team's browser session — faster than
  reading its scopes.
- Uninstall at the end "if time permits".

## Deliverable

A ranked list of tools we liked, with the gut scores. Sources that we could not install
are dropped from the list entirely (nothing to say about them).

*(By day two the dev machine is running ~40 unaudited third-party servers with write
access and live credentials, and the final ranking cannot be traced to a single
verifiable observation.)*
