# Roadmap: Graph-RAG на Lightrag (Production)

## Overview

Доставить v1 Graph-RAG пайплайн с ingestion, графовой индексацией, гибридным поиском, наблюдаемостью, безопасностью и UI, разбив работу на 5 фаз с четкими критериями успеха.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [ ] **Phase 1: Ingestion, Versioning & CI/CD Foundation** - ingestion, версионирование и базовый CI/CD
- [ ] **Phase 2: Graph Extraction & Postgres Graph Index** - извлечение графа и хранение в Postgres
- [ ] **Phase 3: Hybrid Retrieval, Caching & UI** - гибридный поиск, кэш и UI
- [ ] **Phase 4: Observability & Evaluation** - наблюдаемость и оценка качества
- [ ] **Phase 5: Security & Resilience** - безопасность и отказоустойчивость

## Phase Details

### Phase 1: Ingestion, Versioning & CI/CD Foundation
**Goal**: Надежный ingestion PDF, версионирование данных/эмбеддингов и базовый CI/CD
**Depends on**: Nothing (first phase)
**Requirements**: ING-01, ING-02, ING-03, VER-01, VER-02, VER-03, CICD-01, CICD-02
**Success Criteria** (what must be TRUE):
  1. Пользователь загружает PDF и получает стабильные чанки/метаданные; повторный запуск даёт идентичные результаты для тех же входных данных.
  2. Пользователь выполняет инкрементальную загрузку и видит, что переобрабатываются только новые/изменённые документы.
  3. Оператор переключает активную версию индекса и видит, что выдача соответствует выбранной версии.
  4. При push в репозиторий автоматически запускаются тесты и линт, и результат виден в CI.
**Plans**: TBD

Plans:
- [ ] 01-01: Ingestion pipeline (PDF parsing, chunking, metadata)
- [ ] 01-02: Version registry for data and embeddings
- [ ] 01-03: CI/CD baseline (tests + lint)

### Phase 2: Graph Extraction & Postgres Graph Index
**Goal**: Извлечение сущностей/отношений, дедупликация и графовые запросы в Postgres
**Depends on**: Phase 1
**Requirements**: GRPH-01, GRPH-02, GRPH-03
**Success Criteria** (what must be TRUE):
  1. Пользователь/оператор видит извлечённые сущности и связи для новых документов в графе.
  2. Дубликаты сущностей объединяются; запрос по каноническому имени возвращает единый узел.
  3. Графовые запросы (траверсы) в Postgres возвращают ожидаемые связи для тестового набора.
**Plans**: TBD

Plans:
- [ ] 02-01: Entity/relationship extraction + canonicalization
- [ ] 02-02: Postgres graph schema + Apache AGE queries

### Phase 3: Hybrid Retrieval, Caching & UI
**Goal**: Гибридный retrieval, режимы локальный/глобальный, кэш и UI с цитатами
**Depends on**: Phase 2
**Requirements**: RET-01, RET-02, RET-03, RET-04, CCH-01, CCH-02, UI-01, UI-02, UI-03
**Success Criteria** (what must be TRUE):
  1. Пользователь задаёт вопрос и получает ответ с цитатами на исходные чанки.
  2. Пользователь переключает локальный/глобальный режим и видит различие в подобранном контексте.
  3. Повторный запрос отдаётся быстрее за счёт кэширования.
  4. UI показывает выбранный режим и цитаты в ответе.
**Plans**: TBD

Plans:
- [ ] 03-01: Hybrid retrieval orchestration
- [ ] 03-02: Cache layer for retrieval + embeddings
- [ ] 03-03: UI for query, mode selection, citations

### Phase 4: Observability & Evaluation
**Goal**: Трассировка и метрики качества через Langfuse SDK и RAGAS
**Depends on**: Phase 3
**Requirements**: OBS-01, OBS-02, OBS-03
**Success Criteria** (what must be TRUE):
  1. Оператор видит трассировку запроса в Langfuse со стадиями retrieval и generation.
  2. Оператор запускает оценку RAGAS и получает метрики качества по набору запросов.
  3. Оператор видит базовые метрики (p95 latency, errors, throughput) для сервиса.
**Plans**: TBD

Plans:
- [ ] 04-01: Langfuse tracing integration
- [ ] 04-02: RAGAS evaluation jobs + metrics dashboard

### Phase 5: Security & Resilience
**Goal**: Контроль доступа и устойчивость к сбоям
**Depends on**: Phase 4
**Requirements**: SEC-01, SEC-02, RES-01, RES-02
**Success Criteria** (what must be TRUE):
  1. Пользователь без доступа не может получить документы/узлы; авторизованный получает доступ к разрешённым данным.
  2. При деградации ingestion система продолжает обслуживать запросы пользователей.
  3. Повторы ingestion при сбоях выполняют retry/backoff без потери состояния.
**Plans**: TBD

Plans:
- [ ] 05-01: ACL enforcement for documents and graph nodes
- [ ] 05-02: Resilience patterns (retry/backoff, degradation handling)

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Ingestion, Versioning & CI/CD Foundation | 0/3 | Not started | - |
| 2. Graph Extraction & Postgres Graph Index | 0/2 | Not started | - |
| 3. Hybrid Retrieval, Caching & UI | 0/3 | Not started | - |
| 4. Observability & Evaluation | 0/2 | Not started | - |
| 5. Security & Resilience | 0/2 | Not started | - |

---
*Roadmap created: 2026-03-04*
