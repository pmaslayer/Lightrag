# Stack Research

**Domain:** Production Graph-RAG pipeline on LightRAG (VM/containers, no Kubernetes)
**Researched:** 2026-03-04
**Confidence:** MEDIUM

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| LightRAG Server (`lightrag-hku[api]`) | 1.4.10 | Core Graph-RAG engine + API/Web UI | Official LightRAG server package; includes Graph-RAG pipeline, API, and UI needed for production deployments. | HIGH |
| Python | 3.13.12 | Runtime | Latest stable maintenance release in the 3.13 line; balances maturity with latest fixes. | MEDIUM |
| PostgreSQL | 17.9 | Primary data store (graph + vector + metadata) | Current minor in the 17.x line; stable and widely supported; required by project constraint. | HIGH |
| pgvector | 0.8.2 | Vector index inside Postgres | Latest release fixes a critical HNSW buffer overflow; required for safe vector search. | HIGH |
| Apache AGE | 1.6.0 | Property-graph extension in Postgres | Provides Cypher-style graph queries inside Postgres; aligns with single-store constraint. | MEDIUM |
| NGINX | 1.28.2 (stable) | Reverse proxy, TLS termination | Stable branch with latest security fixes; standard for VM/container ingress without Kubernetes. | HIGH |

### Supporting Libraries

| Library | Version | Purpose | When to Use | Confidence |
|---------|---------|---------|-------------|------------|
| FastAPI | 0.129.0 | API layer for custom endpoints | If you extend LightRAG with custom endpoints or gateways. | HIGH |
| Uvicorn | 0.41.0 | ASGI server | Run FastAPI or LightRAG-compatible API services. | HIGH |
| Gunicorn | 25.1.0 | Process manager | Use with `uvicorn` workers for multi-process serving. | HIGH |
| SQLAlchemy | 2.0.46 | DB access layer | If you need custom DB models beyond LightRAG’s built-ins. | HIGH |
| Alembic | 1.18.4 | DB migrations | For controlled schema evolution in Postgres. | HIGH |
| psycopg | 3.3.2 | Postgres driver | Modern, supported driver for Python; preferred over psycopg2 for new projects. | HIGH |
| Redis (server) | 8.4.1 | Cache + job broker | Latest stable Redis OSS; standard for caching and lightweight queues in VM/container deployments. | HIGH |
| redis-py | 7.1.1 | Redis client | Standard Python client for cache and queues. | HIGH |
| Celery | 5.6.2 | Background tasks | Use for PDF ingestion, embedding, graph extraction, and reindexing jobs. | HIGH |
| RAGAS | 0.4.1 | RAG quality evaluation | Required by project constraint for evaluation and metrics. | HIGH |
| Langfuse (server) | 3.140.0 | Tracing/observability backend | Required by project constraint; official server releases are frequent. | MEDIUM |
| Langfuse Python SDK | 3.14.1 | Tracing client | Standard SDK to emit traces/metrics from Python services. | HIGH |
| OpenTelemetry SDK | 1.39.1 | Unified traces/metrics | Use to export service telemetry and integrate with Langfuse/Prometheus. | HIGH |
| prometheus-client | 0.24.1 | Metrics endpoint | Standard Prometheus metrics exporter for Python services. | HIGH |
| structlog | 25.5.0 | Structured logging | JSON logs with stable processors; integrates well with OTel and log backends. | HIGH |
| httpx | 0.28.1 | HTTP client | Needed for LightRAG API integrations and external LLM providers. | HIGH |
| pydantic | 2.12.5 | Data validation | Standard for FastAPI and request/response schemas. | HIGH |
| pypdf | 6.7.0 | PDF parsing | Baseline PDF extraction for ingestion pipeline. | HIGH |
| orjson | 3.11.7 | Fast JSON | Use for high-throughput JSON serialization in API and pipeline. | HIGH |
| tenacity | 9.1.4 | Retry logic | Robust retries for LLM calls, DB retries, and external APIs. | HIGH |

### Development Tools

| Tool | Purpose | Notes | Confidence |
|------|---------|-------|------------|
| uv | 0.10.2 | Python package manager | LightRAG recommends uv; faster and reliable dependency resolution. | HIGH |
| PgBouncer | 1.24.1 | Connection pooling | Reduce Postgres connection pressure in async workloads. | HIGH |

## Installation

```bash
# Core
uv pip install "lightrag-hku[api]==1.4.10"

# Supporting
uv pip install \
  fastapi==0.129.0 \
  uvicorn==0.41.0 \
  gunicorn==25.1.0 \
  sqlalchemy==2.0.46 \
  alembic==1.18.4 \
  psycopg[binary,pool]==3.3.2 \
  redis==7.1.1 \
  celery==5.6.2 \
  ragas==0.4.1 \
  langfuse==3.14.1 \
  opentelemetry-sdk==1.39.1 \
  prometheus-client==0.24.1 \
  structlog==25.5.0 \
  httpx==0.28.1 \
  pydantic==2.12.5 \
  pypdf==6.7.0 \
  orjson==3.11.7 \
  tenacity==9.1.4

# Dev dependencies
uv pip install \
  pytest \
  pytest-asyncio \
  mypy \
  ruff
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| PostgreSQL 17.9 | PostgreSQL 18.3 | If you need the newest major features and can validate AGE compatibility on PG18. | 
| Apache AGE 1.6.0 | Apache AGE 1.7.0 | If you standardize on PostgreSQL 18 and accept newer AGE feature set. |
| NGINX 1.28.2 | Apache HTTPD 2.4.66 | If you need legacy Apache modules or existing ops familiarity. |
| Celery 5.6.2 | No queue (sync jobs) | Only for very small datasets or single-node prototypes. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| pgvector < 0.8.2 | Known CVE in HNSW parallel builds; risk of data leakage or crashes. | pgvector 0.8.2 |
| Python 3.12.x | 3.12 is in security-fixes-only mode with no regular bugfix installers. | Python 3.13.12 |
| psycopg2 | Legacy driver; psycopg3 is the current implementation. | psycopg 3.3.2 |
| Redis Stack 7.x | Redis Stack is being merged into Redis OSS; new users are advised to use Redis OSS. | Redis OSS 8.4.1 |
| External graph DB (Neo4j, etc.) | Violates single-store constraint and adds operational complexity. | Apache AGE in Postgres |

## Stack Patterns by Variant

**If you must stay on PostgreSQL 17 for compatibility:**
- Use Apache AGE 1.6.0
- Because AGE 1.6.0 provides PG17 support while avoiding the newest PG18-only changes.

**If you are willing to adopt PostgreSQL 18:**
- Use Apache AGE 1.7.0 + PostgreSQL 18.3
- Because AGE 1.7.0 includes PG18 support and newer fixes.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| PostgreSQL 17.9 | Apache AGE 1.6.0 | AGE release notes list PG17 builds. |
| PostgreSQL 17.9 | pgvector 0.8.2 | pgvector ships against supported PG majors; upgrade minor safely. |
| LightRAG 1.4.10 | Python >= 3.10 | LightRAG requires Python 3.10+ (use 3.13.12). |

## Sources

- https://pypi.org/project/lightrag-hku/ — LightRAG server version 1.4.10
- https://www.python.org/downloads/latest/python3.13/ — Python 3.13.12
- https://www.postgresql.org/support/versioning/ — Current minor releases (PG 17.9, 18.3)
- https://www.postgresql.org/about/news/pgvector-082-released-3245/ — pgvector 0.8.2 + CVE fix
- https://age.apache.org/release-notes/ — Apache AGE 1.6.0 / 1.7.0 release info
- https://nginx.org/ — nginx 1.28.2 stable
- https://pypi.org/project/fastapi/ — FastAPI 0.129.0
- https://pypi.org/project/uvicorn/ — Uvicorn 0.41.0
- https://pypi.org/pypi/gunicorn — Gunicorn 25.1.0
- https://pypi.org/project/SQLAlchemy/ — SQLAlchemy 2.0.46
- https://pypi.org/project/alembic/ — Alembic 1.18.4
- https://pypi.org/project/psycopg/ — psycopg 3.3.2
- https://download.redis.io/releases/ — Redis OSS 8.4.1
- https://pypi.org/project/redis/ — redis-py 7.1.1
- https://pypi.org/pypi/celery/ — Celery 5.6.2
- https://pypi.org/project/ragas/ — RAGAS 0.4.1
- https://github.com/langfuse/langfuse — Langfuse server releases (v3.140.0)
- https://pypi.org/project/langfuse/ — Langfuse Python SDK 3.14.1
- https://pypi.org/project/opentelemetry-sdk/ — OpenTelemetry SDK 1.39.1
- https://pypi.org/project/prometheus-client/ — prometheus-client 0.24.1
- https://pypi.org/project/structlog/ — structlog 25.5.0
- https://pypi.org/pypi/httpx/ — httpx 0.28.1
- https://pypi.org/pypi/pydantic — pydantic 2.12.5
- https://pypi.org/project/pypdf/ — pypdf 6.7.0
- https://pypi.org/project/orjson/ — orjson 3.11.7
- https://pypi.org/project/tenacity/ — tenacity 9.1.4
- https://pypi.org/pypi/uv — uv 0.10.2
- https://www.pgbouncer.org/downloads/ — PgBouncer 1.24.1
- https://archive.apache.org/dist/httpd/Announcement2.4.html — Apache HTTPD 2.4.66
- https://www.python.org/downloads/release/python-31213/ — Python 3.12 security-only status reference
- https://redis.io/docs/latest/operate/oss_and_stack/stack-with-custom-image/ — Redis Stack deprecation notice

---
*Stack research for: Production Graph-RAG on LightRAG*
*Researched: 2026-03-04*
