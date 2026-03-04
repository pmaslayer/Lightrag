# Architecture Research

**Domain:** Graph-RAG pipeline for corporate PDF search (Lightrag)
**Researched:** 2026-03-04
**Confidence:** MEDIUM

## Standard Architecture

### System Overview

```
+----------------------------------------------------------------------------------+
|                                Presentation Layer                                |
|  +------------------+     +------------------+     +-------------------------+   |
|  |  Web UI (users)  | <-> |  API Gateway     | <-> |  AuthN/AuthZ (SSO)       |   |
|  +------------------+     +------------------+     +-------------------------+   |
+----------------------------------------------------------------------------------+
                  |                            |                            |
                  v                            v                            v
+----------------------------------------------------------------------------------+
|                              Application/Service Layer                           |
|  +------------------+   +------------------+   +------------------+              |
|  | Query Orchestr.  |   | Ingestion Orchestr.|  | Observability   |              |
|  +------------------+   +------------------+   | (RAGAS/LangFuse) |              |
|        |                        |              +------------------+              |
|        v                        v                                                  |
|  +------------------+   +------------------+   +------------------+              |
|  | Retrieval Engine |   | Processing Worker|   | Evaluation Jobs  |              |
|  +------------------+   +------------------+   +------------------+              |
+----------------------------------------------------------------------------------+
                  |                            |                            |
                  v                            v                            v
+----------------------------------------------------------------------------------+
|                                   Data Layer                                     |
|  +------------------+   +------------------+   +------------------+              |
|  | Postgres (graph) |   | Postgres (vector)|   | Object Store     |              |
|  | (nodes/edges)    |   | (embeddings)     |   | (PDF originals)  |              |
|  +------------------+   +------------------+   +------------------+              |
|            ^                    ^                     ^                         |
|            |                    |                     |                         |
|  +------------------+   +------------------+   +------------------+              |
|  | Metadata/Version |   | Cache (query,    |   | Search Index     |              |
|  | Registry         |   | embeddings)      |   | (optional)       |              |
|  +------------------+   +------------------+   +------------------+              |
+----------------------------------------------------------------------------------+
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Web UI | Query input, filters, results view, feedback | SPA + SSR (React/Vue) |
| API Gateway | Request routing, rate limits, auth integration | REST/GraphQL service |
| AuthN/AuthZ | User identity, role-based access, doc ACLs | SSO + policy layer |
| Query Orchestrator | Build retrieval plan, manage caching, call LLM | Service with Lightrag integration |
| Retrieval Engine | Hybrid vector + graph retrieval, rerank | Lightrag adapters + Postgres queries |
| Ingestion Orchestrator | Schedule ingestion, versioning, backfills | Worker queue + scheduler |
| Processing Worker | Parse PDFs, chunk, embed, entity/relationship extraction | Background workers |
| Observability | Traces, metrics, quality eval, prompt logs | RAGAS + LangFuse |
| Evaluation Jobs | Offline eval, drift checks, regression tests | Batch jobs |
| Postgres (graph) | Store entities, relations, document graph | pg + graph extension |
| Postgres (vector) | Store embeddings, ANN search | pgvector |
| Object Store | Store original PDFs and derived artifacts | S3-compatible or filesystem |
| Metadata/Version Registry | Track dataset/embedding versions, lineage | DB tables + migrations |
| Cache | Reuse results and embeddings | Redis or Postgres-based cache |

## Recommended Project Structure

```
src/
|-- api/                 # HTTP layer, request/response, auth middleware
|-- services/            # Orchestration logic (query, ingestion, eval)
|-- retrieval/           # Vector + graph retrieval adapters
|-- ingestion/           # Parsing, chunking, embedding pipelines
|-- graph/               # Graph construction and querying logic
|-- storage/             # DB access, repositories, migrations
|-- observability/       # RAGAS/LangFuse integration, metrics
|-- jobs/                # Background workers, schedulers
|-- cache/               # Cache interfaces and providers
|-- ui/                  # Frontend (if in-repo)
|-- config/              # Runtime configuration
|-- tests/               # Unit/integration/e2e
```

### Structure Rationale

- **`api/`:** Isolates transport concerns from core logic.
- **`services/`:** Centralizes orchestration with explicit use cases.
- **`retrieval/` + `graph/`:** Keeps retrieval strategies and graph logic distinct.
- **`ingestion/`:** Separates data pipeline from query runtime.
- **`storage/`:** Encapsulates Postgres access and schema changes.
- **`observability/`:** Keeps telemetry and eval wiring consistent.

## Architectural Patterns

### Pattern 1: Dual-Path Retrieval (Vector + Graph)

**What:** Combine ANN vector search with graph traversal to expand context.
**When to use:** When entity relationships or document linkage matter.
**Trade-offs:** Better recall; more complex scoring and latency control.

### Pattern 2: Asynchronous Ingestion Pipeline

**What:** Parse/embed/build graph in background workers with versioned outputs.
**When to use:** Large corpora and frequent updates.
**Trade-offs:** Requires job orchestration and replay logic.

### Pattern 3: Observability-First RAG

**What:** Trace each request end-to-end with prompt and retrieval metadata.
**When to use:** Production with quality targets and audit needs.
**Trade-offs:** Overhead in instrumentation and data retention.

## Data Flow

### Request Flow

```
User -> Web UI -> API Gateway -> Query Orchestrator
  -> Cache lookup
  -> Retrieval Engine
     -> Vector search (pgvector)
     -> Graph traversal (graph tables)
     -> Merge + rerank
  -> LLM generation (Lightrag)
  -> Response + citations
  -> Telemetry (RAGAS/LangFuse)
  -> Web UI
```

### Ingestion Flow

```
Source PDFs -> Ingestion Orchestrator -> Processing Workers
  -> Parse/clean -> Chunk -> Embed -> Store embeddings
  -> Entity/relationship extraction -> Graph build -> Store nodes/edges
  -> Version registry update -> Index refresh -> Telemetry
```

### Key Data Flows

1. **Query execution:** User request -> retrieval (vector + graph) -> LLM -> response + trace.
2. **Data refresh:** New/updated PDFs -> pipeline -> embeddings + graph updates -> versioned publish.
3. **Evaluation loop:** Sampled queries -> offline eval -> quality metrics -> prompt/retrieval tuning.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| <=1k users | Single deployment, basic cache, batch ingestion at night |
| 1k-100k users | Separate worker pool, stronger caching, read replicas |
| 100k+ users | Split query/ingestion services, shard vector index |

### Scaling Priorities

1. **First bottleneck:** Retrieval latency (vector + graph). Add caching, tune ANN, precompute expansions.
2. **Second bottleneck:** Ingestion throughput. Add workers and incremental updates.

## Anti-Patterns

### Anti-Pattern 1: Unversioned Embeddings

**What people do:** Overwrite embeddings and graph in place.
**Why it's wrong:** Breaks reproducibility and makes rollback impossible.
**Do this instead:** Keep dataset + embedding versions and publish a stable snapshot.

### Anti-Pattern 2: Graph-Only Retrieval

**What people do:** Rely solely on graph traversal.
**Why it's wrong:** Low recall for new/unlinked content.
**Do this instead:** Always combine with vector search and rerank.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| LLM Provider | RPC/SDK with retries and timeouts | Keep prompts versioned |
| RAGAS | Batch + online metrics | Store eval results by version |
| LangFuse | Trace + prompt logs | Control PII and retention |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| API -> Query Orchestrator | Internal RPC | Enforce auth + rate limits |
| Query -> Retrieval Engine | Direct module call | Keep pure, testable interfaces |
| Ingestion Orchestrator -> Workers | Queue | Enables backpressure and retries |
| Retrieval -> Storage | Repository layer | Centralize SQL and schema changes |

## Suggested Build Order

1. **Data layer foundation:** Postgres schema (graph + vector), object storage, version registry.
2. **Ingestion pipeline:** Parsing, chunking, embeddings, graph construction, indexing.
3. **Retrieval engine:** Vector search + graph traversal + merge/rerank.
4. **Query orchestration:** Lightrag integration, caching, response formatting.
5. **API + Auth:** Gateway, ACLs, rate limiting, user management.
6. **Observability:** RAGAS + LangFuse instrumentation, dashboards.
7. **UI:** Search, filters, citations, feedback loop.
8. **Evaluation + CI/CD:** Regression tests, quality gates, deployment.

## Sources

- General industry patterns for production RAG/Graph-RAG systems

---
*Architecture research for: Graph-RAG pipeline (Lightrag)*
*Researched: 2026-03-04*
