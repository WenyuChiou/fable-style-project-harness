---
id: CHECK-tool-discovery
layer: validation
purpose: Binary pre-return checks for tool/registry discovery work and
  boundary audits, drawn from RUBRIC-tool-discovery and RUBRIC-tool-boundary.
read_when: After drafting a discovery report, ToolCard set, or boundary audit,
  before returning it.
depends_on:
  - ../../rubrics/tool_discovery_rubric.yaml
  - ../../rubrics/tool_boundary_rubric.yaml
  - ../../prompts/tool_discovery_prompt.md
used_by:
  - ROUTE-tool-discovery
tags: [checklist, tool-discovery, boundary]
retrieval_keywords: [discovery checklist, boundary checklist, read-only
  checks, toolcard checks]
---

# Tool discovery / boundary self-checklist

Answer each YES/NO. Any NO means the deliverable is not ready to return.

1. [ ] Nothing was installed, executed, cloned-and-run, downloaded-and-opened,
   or signed up for during this work — and the report SAYS so up front.
2. [ ] Fields gated behind signup/auth are recorded as "skipped — requires
   signup", not silently omitted and not obtained.
3. [ ] Every source is answered against the same pre-registered question grid
   (index? formats? fields? maintained? license/security? read-only safe?),
   including explicit NO / unverified answers.
4. [ ] Every factual claim cites the URL or API call it was fetched from,
   with the fetch date.
5. [ ] Live probes ("verified live") are distinguished from documentation
   claims ("per their docs / llms.txt").
6. [ ] Conflicting figures are recorded as unresolved with both values and
   the probe that would settle them — no winner picked without evidence.
7. [ ] The report ends with a could-not-verify / not-investigated honesty
   ledger.
8. [ ] Rate limits, guest caps, and auth tiers are recorded per source.
9. [ ] Any drafted ToolCard carries `verification_status:
   unverified_auto_draft` and a `risk_basis` showing how risk was COMPUTED
   from conservative proxies (ambiguity resolved to the higher tier).
10. [ ] No draft was written to a governed filename — only `.generated.yaml`
    siblings, non-destructive by default.
11. [ ] No shipped/committed tree contains generated drafts (draft count
    verified, not assumed).
12. [ ] Selected tools default to read-only; any write/execute tool is
    flagged for human (Tier 4) review.
13. [ ] ToolCard capability strings resolve to capability-map ids, or the
    unresolved ones are listed as findings.
