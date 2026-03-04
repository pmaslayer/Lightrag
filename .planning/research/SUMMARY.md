# Project Research Summary

**Project:** LightragTest
**Domain:** Production Graph-RAG pipeline for corporate PDF search (LightRAG)
**Researched:** 2026-03-04
**Confidence:** MEDIUM

## Executive Summary

Research converges on a production Graph-RAG system built on LightRAG with Postgres as the single store for both graph and vector data (Apache AGE + pgvector). The core product is an ingestion-heavy pipeline that builds a versioned graph and hybrid retrieval (graph + vector) to serve local and global query modes, with observability (RAGAS + Langfuse) treated as a first-class requirement.

The recommended approach is to prioritize a robust ingestion + graph extraction foundation, then implement hybrid retrieval and query orchestration, and finally harden evaluation and security. Key risks concentrate around entity resolution quality, relation schema drift, and retrieval noise; these must be mitigated through normalization pipelines, explicit ontologies, and calibrated retrieval thresholds with component-level metrics.

## Key Findings

### Recommended Stack

A LightRAG server deployment with Python 3.13, Postgres 17 + pgvector 0.8.2 + Apache AGE 1.6 provides a stable, single-store Graph-RAG foundation. Supporting services (Redis + Celery) enable async ingestion and caching, while RAGAS + Langfuse + OpenTelemetry provide the observability and evaluation backbone needed for production quality control.

**Core technologies:**
- LightRAG Server (`lightrag-hku[api]`): core Graph-RAG engine and API/UI Ч aligned with production deployment goals.
- PostgreSQL 17.9 + pgvector 0.8.2 + Apache AGE 1.6.0: single-store graph + vector retrieval Ч required for constraints and stable upgrades.
- NGINX 1.28.2: TLS termination and ingress on VMs/containers Ч standard, stable.

### Expected Features

**Must have (table stakes):**
- Ќадежный ingestion дл€ PDF Ч users expect stable parsing, chunking, metadata, and repeatable pipelines.
- √рафова€ индексаци€ (entities/relations + дедупликаци€) Ч required for Graph-RAG correctness.
- Ћокальный и глобальный режимы поиска Ч users expect both deep and overview retrieval.
- Observability (tracing + RAG-метрики) Ч required for production stability.
- Ѕазовый UI с выдачей ответов и цитат Ч user-facing value and trust.

**Should have (competitive):**
-  эширование запросов и контекста Ч latency and cost control at scale.
- јвтотюнинг/промпт-тюнинг индексации Ч faster domain adaptation.
- Ёкспериментальный контур качества (A/B, offline eval) Ч regression prevention.

**Defer (v2+):**
- DRIFT-подобный поиск Ч high complexity, later.
- Dynamic community selection Ч after global search stabilizes.
- ћультимодальность Ч only after core PDF pipeline is stable.

### Architecture Approach

Adopt a layered architecture with a query orchestrator, ingestion orchestrator, retrieval engine, and observability stack over a Postgres-based graph + vector data layer. Use async workers for parsing/embedding/extraction and maintain explicit versioning for embeddings and graph snapshots to enable rollbacks and reproducibility.

**Major components:**
1. Query Orchestrator Ч plans retrieval, manages cache, and coordinates LLM calls.
2. Ingestion Orchestrator + Workers Ч parse PDFs, chunk, embed, extract graph, and publish versions.
3. Retrieval Engine Ч hybrid vector + graph retrieval with merge/rerank.
4. Observability + Evaluation Ч tracing, RAGAS metrics, and offline eval jobs.
5. Data Layer Ч Postgres (graph + vector), object store for PDFs, and metadata/version registry.

### Critical Pitfalls

1. **ќшибки entity linking и сли€ни€ сущностей** Ч avoid with canonicalization, confidence thresholds, and targeted manual validation.
2. **ƒрейф схемы отношений** Ч avoid with a controlled ontology, normalization, and periodic type compression.
3. **Ќеподход€щий chunking дл€ графовой экстракции** Ч avoid with overlap, structure-aware chunking, and extraction-specific validation.
4. **Ќет bridge evidence дл€ multi-hop вопросов** Ч avoid with iterative retrieval and path-aware reranking.
5. **Retrieval overload и шум** Ч avoid with calibrated K/thresholds and context-quality metrics.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Data Foundation & Ingestion
**Rationale:** Reliable ingestion and versioning are prerequisites for all Graph-RAG features and prevent early-quality collapse.
**Delivers:** PDF parsing/chunking, embeddings, version registry, object storage, initial Postgres schema.
**Addresses:** Ќадежный ingestion дл€ PDF, инкрементальные обновлени€.
**Avoids:** Ќеподход€щий chunking, устаревание графа/эмбеддингов.

### Phase 2: Graph Extraction & Entity Resolution
**Rationale:** Graph correctness underpins local/global query quality; must be stabilized before retrieval logic.
**Delivers:** Entity/relationship extraction, canonicalization, schema normalization, deduplication.
**Uses:** Apache AGE + Postgres graph schema.
**Implements:** Graph construction component.
**Avoids:** Entity linking errors, relation schema drift.

### Phase 3: Hybrid Retrieval & Query Orchestration
**Rationale:** Core user value comes from hybrid retrieval and coherent answers with citations.
**Delivers:** Vector + graph retrieval, reranking, local/global modes, query orchestration.
**Addresses:** Ћокальный/глобальный режимы поиска.
**Avoids:** Bridge-evidence gaps, retrieval overload.

### Phase 4: Observability & Evaluation
**Rationale:** Production reliability requires component-level metrics and traceability.
**Delivers:** RAGAS metrics, Langfuse tracing, offline eval jobs, golden set.
**Addresses:** Observability requirements.
**Avoids:** No component-level evaluation pitfall.

### Phase 5: Security & Access Control
**Rationale:** Corporate data demands ACLs and protection against graph exfiltration.
**Delivers:** AuthN/AuthZ, ACL enforcement, rate limiting, query constraints.
**Avoids:** Subgraph extraction and ACL leakage risks.

### Phase Ordering Rationale

- Ingestion and versioning are dependencies for graph quality and retrieval stability.
- Graph extraction quality gates must precede local/global retrieval to avoid propagating errors.
- Observability needs working end-to-end flows but should be established before scaling.
- Security hardening is essential before broad rollout, after core functionality is stable.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** Entity resolution strategies and domain ontology design are high-risk.
- **Phase 3:** Hybrid retrieval/reranking tuning requires domain-specific evaluation.
- **Phase 5:** Abuse prevention and ACL strategy need policy alignment.

Phases with standard patterns (skip research-phase):
- **Phase 1:** Standard ingestion + Postgres schema/versioning patterns.
- **Phase 4:** RAGAS + Langfuse integration patterns are well documented.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Version choices are current but depend on vendor release cadence. |
| Features | MEDIUM | Based on common Graph-RAG patterns and LightRAG capabilities. |
| Architecture | MEDIUM | Standard layered architecture; details depend on implementation constraints. |
| Pitfalls | MEDIUM | Common failure modes are consistent across Graph-RAG systems. |

**Overall confidence:** MEDIUM

### Gaps to Address

- Entity resolution tuning and ontology definition need domain-specific validation.
- Retrieval calibration (top-K, rerank thresholds) needs real query sets.
- Security policy (ACL granularity, query constraints) needs stakeholder alignment.

## Sources

### Primary (HIGH confidence)
- LightRAG official package and docs Ч core server and API approach.
- PostgreSQL + pgvector + Apache AGE release notes Ч version compatibility.
- RAGAS and Langfuse documentation Ч evaluation and tracing patterns.

### Secondary (MEDIUM confidence)
- Microsoft GraphRAG research and architecture notes Ч local/global search patterns.
- LlamaIndex KG-RAG examples Ч hybrid retrieval practices.

### Tertiary (LOW confidence)
- Blog posts and single-source lessons learned on Graph-RAG pitfalls.

---
*Research completed: 2026-03-04*
*Ready for roadmap: yes*
