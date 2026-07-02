---
id: EXAMPLE-bad-memory-overbuild
layer: example
purpose: NEGATIVE example — a day-1 memory architecture with a vector DB and seven backends before a single record exists or a single retrieval need is demonstrated.
read_when: Calibrating what NOT to build for agent memory on day 1; paired critique explains each violation.
depends_on:
  - ../critiques/critique_bad_memory_overbuild.md
used_by:
  - ROUTE-memory-update
  - ROUTE-phase-review
tags: [negative-example, memory-overbuild, vector-db, premature-infrastructure, synthetic]
retrieval_keywords: [vector database day one, embeddings memory, seven backends, memory architecture, RAG stack, hybrid retrieval, knowledge graph memory]
source_artifact: synthesized (contrast with the real repo's yaml_jsonl file-based memory + append-only update_policy, examples/*/HARNESS.yaml)
synthetic: true
---

> **NEGATIVE EXAMPLE — do not imitate.** The observed method ships file-based YAML/JSONL
> memory with append-only rules and machine-checkable update policies. This design is
> the opposite. See `../critiques/critique_bad_memory_overbuild.md`.

# Memory Architecture RFC — v1 (Day 1)

## Goal

Memory is the moat, so we build the full memory platform before the first package ships.

## The seven-backend stack

| # | Backend | Purpose |
|---|---------|---------|
| 1 | Pinecone (vector) | semantic recall over all past analyses |
| 2 | Neo4j (graph) | entity-relationship memory between companies, people, theses |
| 3 | PostgreSQL | structured thesis records |
| 4 | Redis | hot working memory + session cache |
| 5 | S3 | cold archival of raw transcripts |
| 6 | Elasticsearch | keyword + BM25 hybrid retrieval layer |
| 7 | SQLite (edge) | offline replica for laptop use |

A `MemoryFabric` abstraction unifies all seven behind one interface; a nightly
`MemorySync` DAG (Airflow) reconciles them. Embeddings are re-computed on every write
(ada-3, batched). A learned reranker fuses vector, graph, and keyword results.

## Update semantics

- Writes go to whichever backend the router scores highest for the record type.
- On contradiction between stored records, **the newer record overwrites the older one**
  — keeping both would bloat the index and confuse retrieval.
- Deduplication runs weekly and hard-deletes near-duplicates (cosine > 0.93).
- No schema for record shapes yet — each memory type will "find its shape organically";
  the fabric stores whatever JSON arrives.

## Migration & ops

- Kubernetes helm charts for the five server backends.
- Estimated infra cost: ~$800/mo idle. Worth it — memory is the moat.
- The first actual memory record will be written after the retrieval platform is up
  (ETA: 6 weeks).

## Evaluation

Retrieval quality will be assessed qualitatively once users report problems. There is
no way to test memory before there are users anyway.

*(Six weeks of infrastructure precede the first record. Contradictions silently
overwrite history. Nothing validates a record's shape. No test can fail. And the whole
stack sits inside the versioned package, so regenerating the package clobbers it.)*
