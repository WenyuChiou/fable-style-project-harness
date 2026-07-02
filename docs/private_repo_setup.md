---
id: DOC-private-repo-setup
layer: doc
purpose: Privacy posture — private remote, never-include list, public-flip review checklist, gitignore
read_when: Setting up the remote, before any push, and MANDATORY before any consideration of making this repo public
depends_on: [HARNESS.yaml, README.md]
used_by: [ROUTE-repo-maintenance, ROUTE-pr-review]
tags: [privacy, security, review-checklist, gitignore, private-remote]
retrieval_keywords: [private repo, make public, review checklist, secrets, gitignore, publish, privacy policy]
---

# Private Repo Setup and Publication Policy

This repo's `HARNESS.yaml` constraints are binding:
`private_until_reviewed`, `no_secrets`, `no_hidden_reasoning`. The parent
project enforces the same boundary from its side — commit `965c68e`
gitignores `agent_harness/` with the message "private harness distillation
must never ship with the (future-public) repo."

## 1. Remote policy

- **A private remote is REQUIRED.** If this repo gets a remote at all, it
  must be private from the first push. No public remote, no public mirror,
  no gist excerpts.
- **Never public without a human content review.** An agent may propose
  the flip; only a human completes the checklist below and executes it.
  This mirrors the source project's own posture (private during
  development; public flip is an explicit, human-gated event).

## 2. Never-include list (checked on EVERY commit, not just at the flip)

The following must never appear in this repo, in any file, at any commit:

- Secrets: API keys, tokens, credentials, `.env` contents, auth cookies.
- Personal contact info: phone numbers, personal emails, addresses,
  messaging handles.
- Private chat exports or session transcripts of private conversations.
- Proprietary or private system prompts, and any "hidden internals" of any
  model or agent product.
- Hidden reasoning traces (chain-of-thought) — invented OR captured.
  Everything here must be reconstructable by an observer of the source
  repo's public artifacts; if it isn't, it doesn't belong.

## 3. Public-flip review checklist

A human reviewer walks every item, on the actual file tree at the actual
candidate commit (not from memory):

- [ ] **Secret scan clean** — run an automated secret scanner over the full
      history, not just HEAD; rewrite history if anything ever landed.
- [ ] **Never-include sweep** — grep for keys/tokens/emails/phones/chat
      markers; open every hit; zero tolerated.
- [ ] **Provenance audit** — every claim, example, and dataset record
      traces to a `source_artifact` (repo path or commit) or is explicitly
      marked `synthetic`/`synthesized`. Nothing implies access to
      non-public material.
- [ ] **No hidden-reasoning content** — prompts/ contains only fragments
      reconstructable from observable work orders and command frontmatter.
- [ ] **Third-party content check** — no verbatim quoted material beyond
      what the source repo itself publishes under its NOTICE carve-out.
- [ ] **People check** — no names, handles, or identifying details of
      uninvolved private individuals.
- [ ] **License decided** — a deliberate license file exists (the source
      repo uses MIT with a quoted-material carve-out; choose consciously,
      don't copy blindly).
- [ ] **`.gitignore` intact** — the required ignore set below is present
      and has not been weakened.
- [ ] **Retrieval smoke test passes** (`docs/retrieval_smoke_test.md`) —
      you are not publishing a broken harness.
- [ ] **Human sign-off recorded** — the flip commit message names the
      reviewer and the checklist date.

Any unchecked box = the repo stays private. Halt is a success.

## 4. Required `.gitignore`

The repo-root `.gitignore` must contain at least the following classes
(see the actual file for the exact patterns):

- Secrets and credentials: `.env`, `.env.*`, `*.key`, `*.pem`,
  `secrets/`, `credentials*`, `*token*`
- Language/tool caches: `__pycache__/`, `*.pyc`, `.pytest_cache/`,
  `node_modules/`, `.venv/`
- OS junk: `.DS_Store`, `Thumbs.db`, `desktop.ini`
- Local scratch and logs: `scratch/`, `tmp/`, `*.log`
- Private local state: `local/`, `*.local.md`, `private/`

Additions are welcome; removals require the same human review as a public
flip.
