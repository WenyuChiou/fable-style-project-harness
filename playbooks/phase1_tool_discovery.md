---
id: PLAYBOOK-phase1-tool-discovery
layer: playbook
purpose: Procedure for metadata-only tool/registry discovery research — per-claim fetched-URL citations, per-dimension scored source registry, honest unverified ledgers, zero execution.
read_when: Running any external tool/source discovery or research-survey task, or reviewing one for citation integrity.
depends_on:
  - ./phase0_static_package_standard.md
  - ./pr_review_playbook.md
used_by:
  - ROUTE-tool-discovery
  - ROUTE-phase-review
tags: [tool-discovery, metadata-only, read-only, source-scoring, no-execution, research]
retrieval_keywords: [M2a, tool discovery, registry research, fetched URL citation, unverified ledger, score basis, spec 9.5, no install, dead end recorded]
---

# Phase 1 — Tool-discovery research (metadata-only, citation-per-claim)

**Status: REAL — executed as M2a on 2026-07-02** (commit `510b79f`; artifacts `docs/tool_discovery_report.md`, `docs/mcp_registry_report.md`, `docs/tool_source_comparison.md`, `data/tool_sources.yaml`). Note the scheduling discipline: this research was deliberately DEFERRED from "next after Phase 0" to the start of Phase 2, because its actual consumer (the tool-fit scorer) lives there (design-review decision B12). Research runs when its consumer exists.

## Goal

Investigate and rank external discovery sources (skill indexes, MCP registries, API catalogs) so later automation can consume them — producing a scored, machine-shaped source registry — while **never executing, installing, cloning-and-running, or signing up for anything** (spec 9.5: "tool discovery is allowed; tool execution is not").

## Allowed work

- Read-only web fetches and public API/GitHub metadata reads (repo metadata, contents listings, live JSON stats probes, code-search counts).
- Fixed investigation questions applied per source (the project used Q1–Q6: machine-readable index? formats? extractable fields? maintained? license/security? read-only safe?) — defined in the research PLAN before execution.
- Scoring every investigated source on declared dimensions where **every dimension score carries a one-line basis** and the total is a test-enforced mean (spec-9.4 score blocks; shape pinned by `tests/test_tool_sources.py`).
- Recording rate limits, auth requirements, and pricing changes observed live (e.g., "OpenAlex keyless model is GONE — mandatory key + metered credit").
- A cross-source ranked comparison with an explicit integration order for the consumer phase (ClawHub 0.89 → Official MCP Registry 0.86 → Glama 0.85 first wave).

## Forbidden work

- Executing/installing anything discovered (`npx findskills` was documented but **not run**; FindSkills' full-field API key requires signup — **not exercised**).
- Scoring a source that was not investigated: uninvestigated sources ship as **unscored stubs** (7 of 34), never given invented numbers (no-fabrication rule).
- Omitting dead ends: unreachable-to-fetch sources are recorded in the report as dead ends, not dropped (2 in the MCP registry report).
- Stating a claim without its fetched URL; anything not directly observed is marked *unverified* inline (e.g. "count not independently verified", "scoring methodology unverified").

## Required outputs

1. Per-category research reports answering the fixed questions per source, every factual claim cited to a fetched URL, with an honest unverified/unreachable ledger.
2. A machine-shaped scored registry (`data/tool_sources.yaml` pattern: N investigated entries + score blocks with per-dimension basis lines + unscored stubs).
3. A ranked comparison doc naming the consumer-phase integration order and **deliberate postponements**.
4. Shape tests enforcing the registry contract (total = mean of dimensions; required fields present).
5. Key design findings fed forward explicitly (e.g., "NO registry publishes permission/risk metadata → risk must be COMPUTED from proxies" — this single finding shaped the entire Phase-2 `assess_candidate` design).

## Acceptance criteria

- Zero installs / executions / signups, and the commit message says so ("Read-only throughout: zero installs, zero executions, zero signups").
- An independent research-integrity reviewer re-verifies a sample of claims LIVE against the cited URLs (the M2a review re-verified 12 claims, zero fabrication) — see `./pr_review_playbook.md`.
- Every scored dimension has a basis line; every unscored source is a visible stub.
- Later phases correct the ledger honestly when live probes contradict it (M2b recorded "Two M2a honesty-ledger corrections from live probes: official registry ?search= and Glama ?query= both work").

## Common failure modes

- **Research before its consumer exists** — findings rot. Prevention: schedule discovery at the start of the phase that consumes it (B12).
- **Score inflation for famous sources** — prevented by per-dimension basis lines that a reviewer can re-derive.
- **Silent dead ends** — an unreachable registry omitted from the report makes coverage look better than it is; record the failure.
- **Claim laundering** — repeating a source's self-reported number ("1000+ skills") as fact; mark it "claimed, not independently verified".
- **Discovery drifting into execution** — running a CLI "just to check". The boundary is binding on every adapter built later, not just this phase.

## Self-check checklist

- [ ] Does every factual claim in my report cite the URL it was fetched from?
- [ ] Did I run, install, or sign up for anything? (Must be NO.)
- [ ] Are uninvestigated sources stubs, not scores?
- [ ] Are dead ends and blocked fetches recorded, not omitted?
- [ ] Does every score dimension carry a one-line basis, and is the total a computed mean?
- [ ] Did I name the integration order and postponements for the consuming phase?
- [ ] Has an independent reviewer live-re-verified a claim sample?
