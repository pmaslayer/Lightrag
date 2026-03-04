# Phase 1: Ingestion, Versioning & CI/CD Foundation - Context

**Gathered:** 2026-03-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Доставить надежный ingestion PDF, версионирование данных/эмбеддингов и базовый CI/CD для v1.
</domain>

<decisions>
## Implementation Decisions

### Ingestion Behavior
- Детерминизм не строгий: качество важнее бит‑в‑бит идентичности при обновлениях парсера.
- Метаданные в v1 — минимум (источник, дата, автор/владелец, раздел/страницы).
- Сканированные PDF: OCR best‑effort с пометкой качества.
- При частичном падении ingestion: fail‑fast и подробный отчет об ошибках.

### Incremental Updates
- Обновление по расписанию (батчи).
- Изменение определяется по контенту (хеш/содержимое).
- Удаленные документы: жёсткое удаление из индекса.
- Целевой интервал обновлений: ежедневно.

### Versioning & Rollback
- Имена версий: timestamp + hash (авто‑генерация).
- Переключение активной версии: только админ.
- Rollback: мгновенно на предыдущую версию.
- Храним последние 3 версии.

### CI/CD Gates
- Блокирующие проверки: pytest + ruff.
- main защищён: merge через PR + проверки.
- В CI на каждый PR: полный набор тестов + линт.
- Автодеплой в v1 не нужен (ручной).

### Claude's Discretion
- Нет — все ключевые решения зафиксированы.
</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- Нет — кодовой базы пока нет.

### Established Patterns
- Нет — кодовой базы пока нет.

### Integration Points
- Нет — кодовой базы пока нет.
</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.
</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.
</deferred>

---

*Phase: 01-ingestion-versioning-ci-cd-foundation*
*Context gathered: 2026-03-04*
