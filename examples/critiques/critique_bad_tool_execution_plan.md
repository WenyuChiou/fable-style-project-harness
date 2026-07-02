---
id: CRIT-tool-execution-plan
layer: example
purpose: Critique of bad_tool_execution_plan.md — auto-installing discovered tools during research, with every violated rule and the read-only correction.
read_when: You read the bad tool plan, or a research plan proposes installing/executing candidates.
depends_on:
  - ../bad/bad_tool_execution_plan.md
  - ../golden/good_tool_discovery_report.md
  - ../../datasets/failure_modes.yaml
used_by:
  - ROUTE-tool-discovery
tags: [critique, tool-safety, read-only, trust-boundary]
retrieval_keywords: [auto install critique, read-only discovery, trust boundary, npx install MCP, gut score, unverified ledger]
synthetic: true
---

# Critique: bad_tool_execution_plan.md

## Violations

1. **Auto-installing discovered MCP servers into the live global config** (step 1) is
   FM-025 (auto-install-trust-boundary-crossing) and violates DR-007
   (discovery-without-execution). The real research plan pinned "nothing installed,
   executed, cloned-and-run, or signed up for" BEFORE research began, and the report
   honors it per-source — even download endpoints are named and marked *not used*. The
   real package standard also bans it at runtime
   (`install_or_execute_unknown_tools_or_mcp_servers` is a prohibited_action).
2. **`curl | bash` and OAuth click-through without reading scopes** compound the same
   violation with unauditable execution; RUBRIC-tool-safety requires risk assessed from
   declared metadata, not from surviving the experience.
3. **Signing up and scattering live keys "to be rotated later"** violates the zero-signup
   rule and standard secret hygiene; the real M2a used only existing operator auth and
   said so ("no new signup").
4. **Exercising write paths on real systems during discovery** — the real posture is
   read-only defaults with a single scoped write allowlist even at RUNTIME; at research
   time writes are simply out of scope.
5. **"Trust registry safety labels"** — the real report records safety labels as claims
   with **unverified** scoring methodology; adopting them as ground truth is FM-030-class
   (secondhand data adopted silently).
6. **Gut scores with no claim-to-URL trace** violate DR-006 (no-fabrication-as-code) and
   RUBRIC-evidence-integrity: every dimension in the real `tool_sources.yaml` carries a
   one-line basis, and an independent reviewer re-verified 12 claims live — impossible
   with gut scores (FM-008 threshold-gaming adjacent: unfalsifiable rankings).
7. **Dropping uninvestigable sources from the list** violates the no-fabrication corollary:
   the real dataset keeps 7 uninvestigated sources as visible **unscored stubs**.
8. **Risk assessed by daily-driving with default permissions** inverts DR-007's key
   finding: since registries publish no risk metadata, risk must be **computed from
   conservative proxies** (credentials, hosting, transport), with unknown → medium +
   `read_only ASSUMED UNVERIFIED`.

## Corrected approach (5-10 lines)

```text
1. Pre-register investigation questions + the read-only rule (no install,
   no execute, no signup) before the first fetch.
2. Probe metadata only: public JSON endpoints, GitHub API, docs pages;
   cite the fetched URL on every claim; mark everything else unverified.
3. Keep uninvestigated sources as unscored stubs; record conflicting
   counts as conflicts.
4. Score per-dimension with a written basis; totals mechanically derived;
   have an independent reviewer re-verify claims against the cited URLs.
5. Compute risk from conservative proxies; unknown => medium risk,
   read_only ASSUMED UNVERIFIED.
6. Installation happens later, per-tool, behind ToolCards + human vetting
   (generated cards ship as unverified_auto_draft that FAIL validation
   until vetted).
```
