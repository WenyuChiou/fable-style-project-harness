---
id: EXAMPLE-good-tool-discovery-report
layer: example
purpose: Golden example of read-only tool/registry discovery — fixed investigation questions, per-claim citations, explicit unverified ledger, zero installs or signups.
read_when: You are researching external tools, registries, MCP servers, or data sources before any integration decision.
depends_on:
  - ../../playbooks
used_by:
  - ROUTE-tool-discovery
tags: [tool-discovery, read-only, registry-research, unverified-ledger, golden]
retrieval_keywords: [tool discovery, MCP registry, read-only fetch, no install, investigation questions, unverified, rate limits, machine-readable index, scoring basis]
source_artifact: docs/tool_discovery_report.md + data/tool_sources.yaml (repo method-harness-compiler, commit 510b79f)
synthetic: false
---

# Golden: Tool Discovery Report (condensed from the real M2a report, 27 sources)

The real report investigated 27 sources across three categories with a hard rule from the
research plan: **nothing was installed, executed, cloned-and-run, or signed up for**.
Every factual claim cites the URL it was fetched from; anything not directly observed is
marked *unverified*. Two source entries are condensed below with the discipline markers
annotated.

## Fixed investigation questions (declared before fetching)

Per source: (Q1) machine-readable index? (Q2) JSON / markdown / `llms.txt` / API access?
(Q3) can we extract name, description, tags, install method, source URL? (Q4) actively
maintained? (Q5) license/security info? (Q6) safe for read-only discovery?

The same six questions for every source make the entries comparable and make gaps
visible — an unanswered question stays visibly unanswered.

## Entry 1 (strongest source; note what "YES" requires)

**A6. ClawHub (clawhub.ai)** — fetched: docs page, HTTP-API page, GitHub repo API.

- **Q1/Q2: YES — strongest public API in category (verified live).** Public no-auth JSON
  endpoints listed by exact path (`GET /api/v1/search`, `/skills/{slug}`, `/packages`);
  the download endpoint is named and marked **not used**.
- **Q3: rich fields** — the extractable field list is enumerated verbatim from the
  response shape, not summarized.
- **Q4: YES** — backing repo pushed 2026-07-01, 9,083 stars. But the total skill count has
  **conflicting secondhand figures** (13,000 vs 71,006) and the report says so:
  "**neither verified against ClawHub's own API**".
- **Q5: best-in-category** — automated security scans, moderation workflow (cited to the
  docs page, not assumed).
- **Q6: YES** — anonymous rate limits quoted with numbers (read 3,000/min per IP).

## Entry 2 (weak source; note that weakness is stated, not padded)

**A7. skills.sh** — fetched: homepage only.

- **Q1/Q2: no API advertised on the homepage.** No JSON index or `llms.txt` visible.
  "(**Unverified whether an undocumented endpoint exists** — only the landing page was
  fetched.)"

The report does not guess. A landing-page-only fetch produces a landing-page-only claim.

## Cross-source findings that fed design (observable downstream)

- **NO registry publishes permission/risk metadata** → ToolCard `permission_level` /
  `risk_level` must be **computed from conservative proxies** (isSecret credential flags,
  hosting attributes, transports, provenance-with-documented-semantics); unknown maps to
  `medium` risk + `read_only ASSUMED UNVERIFIED`, and every rule emits a basis string.
- Sources that could not be investigated became **unscored stubs** in
  `data/tool_sources.yaml` (7 of them) — present, named, and unscored, rather than
  absent or guessed (the no-fabrication rule applied to research, not just evidence).
- Every score block carries a one-line **basis** per dimension, and the total is the
  test-enforced mean of the dimensions — the ranking is recomputable.
- Two earlier claims were later corrected by live probes and recorded as
  **honesty-ledger corrections** (both registries' search parameters do work) — the
  original text stayed; the correction was appended.

## Why this is the golden form

- **Discovery without execution**: the trust boundary is never crossed during research;
  probes are metadata-only, and the one authenticated probe reuses existing operator
  auth with "no new signup" stated.
- **Claim-to-URL discipline**: an independent research-integrity reviewer re-verified 12
  claims live against the cited URLs before the commit merged — possible only because
  every claim carries its URL.
- **Unverified is a first-class answer**: the report's value comes as much from its
  unverified/unreachable ledger as from its findings.
- The report ends in a **ranked, recomputable comparison** and a first-wave integration
  order — research that terminates in a decision, not a reading list.

## Reuse checklist

- [ ] Investigation questions fixed and numbered before the first fetch.
- [ ] Read-only rule stated at the top; any credentialed access disclosed.
- [ ] Every factual claim cites its fetched URL; conflicts between sources surfaced.
- [ ] Unverified / unreachable / not-exercised markers inline, plus a stub entry for
      every uninvestigated source.
- [ ] Per-dimension scoring basis; totals mechanically derivable.
- [ ] Ends with a ranked table and an integration order (or an explicit no-integration
      verdict).
