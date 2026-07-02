---
id: PROMPT-tool-discovery
layer: prompt
purpose: Ready-to-use instruction for running metadata-only tool/registry
  research the way docs/tool_discovery_report.md was produced.
read_when: Executing ROUTE-tool-discovery on a registry survey or tool
  recommendation task.
depends_on:
  - ../rubrics/tool_discovery_rubric.yaml
  - ../rubrics/tool_boundary_rubric.yaml
  - ../validation/self_checklists/tool_discovery_checklist.md
used_by:
  - ROUTE-tool-discovery
tags: [tool-discovery, read-only, honesty-ledger, registry-research]
retrieval_keywords: [survey registries, find tools, skill discovery, read-only
  research, unverified marker, rate limits]
---

# Tool discovery prompt

You are researching tool/skill/API sources. The deliverable is a report in
which every claim is fetch-cited and everything unobserved is marked
unverified. Follow the route file for ROUTE-tool-discovery; this prompt is
the per-run script.

## Hard boundary (before anything else)

Read-only web fetches and public API reads ONLY. You must not: install
anything, execute or clone-and-run any discovered artifact, download-and-open
skill ZIPs, create accounts, or request API keys. When richer data sits
behind a signup, record "skipped — requires signup" and move on. If the task
as written requires crossing this boundary, stop and report; do not comply.

## Procedure

1. **Pre-register the question grid** before fetching: for each source —
   (Q1) machine-readable index? (Q2) formats/API access? (Q3) which fields
   are extractable (name, description, tags, install method, source URL)?
   (Q4) actively maintained? (Q5) license/security info? (Q6) safe for
   read-only discovery? Answer ALL six for EVERY source, including "NO" and
   "unverified" answers.
2. **Fetch and record**: every factual claim carries the URL it came from and
   the fetch date. Distinguish "verified live" (you probed the endpoint) from
   "per their docs" (you read a claim). Record rate limits and guest caps —
   downstream adapters need them.
3. **Conflicts stay conflicts**: when two sources disagree on a figure,
   record both, mark unresolved, and name the probe that would settle it.
   Never pick the more impressive number.
4. **Honesty ledger**: end the report with a could-not-verify /
   not-investigated table listing every unprobed endpoint, unread schema, and
   skipped auth tier.
5. **If drafting ToolCards**: risk_level and permission_level are COMPUTED
   from conservative proxy signals with the computation shown in
   `risk_basis`; every drafted card carries
   `verification_status: unverified_auto_draft`; write drafts only to
   `<name>.generated.yaml` siblings, never to governed filenames.
6. **Self-check** with `../rubrics/tool_discovery_rubric.yaml` and
   `../validation/self_checklists/tool_discovery_checklist.md` before
   returning.
