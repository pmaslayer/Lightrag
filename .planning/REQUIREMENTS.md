# Requirements: Graph-RAG на Lightrag (Production)

**Defined:** 2026-03-04
**Core Value:** Пользователь получает точные и воспроизводимые ответы через Graph-RAG поверх корпоративных данных при контролируемой наблюдаемости и качестве.

## v1 Requirements

### Ingestion

- [ ] **ING-01**: User can ingest PDF documents with deterministic parsing, chunking, and metadata extraction
- [ ] **ING-02**: User can re-run ingestion with reproducible outputs for the same input
- [ ] **ING-03**: System supports incremental ingestion updates without full re-index

### Graph Indexing

- [ ] **GRPH-01**: System extracts entities and relationships from ingested text
- [ ] **GRPH-02**: System performs entity deduplication and canonicalization
- [ ] **GRPH-03**: Graph is stored in Postgres with Apache AGE and is queryable by graph traversal

### Retrieval

- [ ] **RET-01**: System performs hybrid retrieval (graph + vector) for user queries
- [ ] **RET-02**: System supports local (entity-neighborhood) retrieval mode
- [ ] **RET-03**: System supports global (community summary) retrieval mode
- [ ] **RET-04**: System returns answers with citations to source chunks

### Observability

- [ ] **OBS-01**: System traces retrieval and generation steps via Langfuse SDK
- [ ] **OBS-02**: System computes RAGAS metrics for query quality evaluation
- [ ] **OBS-03**: System exposes basic operational metrics (latency, errors, throughput)

### Versioning

- [ ] **VER-01**: System versions datasets used for indexing
- [ ] **VER-02**: System versions embedding models and embedding outputs
- [ ] **VER-03**: System supports rollback to a prior indexed version

### Caching

- [ ] **CCH-01**: System caches retrieval results for repeated queries
- [ ] **CCH-02**: System caches embeddings for identical inputs

### Security & Resilience

- [ ] **SEC-01**: System enforces access control on documents and graph nodes
- [ ] **SEC-02**: System isolates user queries to authorized data only
- [ ] **RES-01**: System continues query service when ingestion pipeline is degraded
- [ ] **RES-02**: System supports retry and backoff for ingestion failures

### CI/CD & Testing

- [ ] **CICD-01**: System has automated tests covering ingestion, indexing, and retrieval
- [ ] **CICD-02**: System has CI pipeline that runs tests and lint checks on push

### UI

- [ ] **UI-01**: User can query via a web UI
- [ ] **UI-02**: UI shows answer with citations and retrieval mode used
- [ ] **UI-03**: UI allows selecting local vs global retrieval mode

## v2 Requirements

### Retrieval

- **RET-05**: System supports DRIFT-like hybrid global+local retrieval
- **RET-06**: System supports dynamic community selection for global search

### Quality

- **QAL-01**: System provides A/B evaluation and offline experiment runner

### Multimodal

- **MM-01**: System supports image or multimodal ingestion in addition to PDF

## Out of Scope

| Feature | Reason |
|---------|--------|
| OpenTelemetry integration | Using Langfuse SDK directly for tracing |
| Full real-time reindex of entire graph | Cost/latency; incremental updates preferred |
| Raw user access to graph queries (Cypher/SQL) | Security and load risks |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ING-01 | Phase 1 | Pending |
| ING-02 | Phase 1 | Pending |
| ING-03 | Phase 1 | Pending |
| GRPH-01 | Phase 2 | Pending |
| GRPH-02 | Phase 2 | Pending |
| GRPH-03 | Phase 2 | Pending |
| RET-01 | Phase 3 | Pending |
| RET-02 | Phase 3 | Pending |
| RET-03 | Phase 3 | Pending |
| RET-04 | Phase 3 | Pending |
| OBS-01 | Phase 4 | Pending |
| OBS-02 | Phase 4 | Pending |
| OBS-03 | Phase 4 | Pending |
| VER-01 | Phase 1 | Pending |
| VER-02 | Phase 1 | Pending |
| VER-03 | Phase 1 | Pending |
| CCH-01 | Phase 3 | Pending |
| CCH-02 | Phase 3 | Pending |
| SEC-01 | Phase 5 | Pending |
| SEC-02 | Phase 5 | Pending |
| RES-01 | Phase 5 | Pending |
| RES-02 | Phase 5 | Pending |
| CICD-01 | Phase 1 | Pending |
| CICD-02 | Phase 1 | Pending |
| UI-01 | Phase 3 | Pending |
| UI-02 | Phase 3 | Pending |
| UI-03 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 25 total
- Mapped to phases: 25
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-04*
*Last updated: 2026-03-04 after initial definition*
