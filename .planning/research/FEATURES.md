# Feature Research

**Domain:** Production Graph-RAG pipeline for корпоративный поиск по PDF
**Researched:** 2026-03-04
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Надежный ingestion для PDF (парсинг, чанкинг, метаданные, очистка) | Без стабильного ingestion ответы разваливаются | MEDIUM | Нужны пайплайны обработки, backpressure и повторяемость |
| Графовая индексация: извлечение сущностей/отношений + дедупликация | Это база Graph-RAG, иначе нет графа | HIGH | Извлечение сущностей/отношений и слияние дублей |
| Гибридный retrieval: графовая выборка + текстовый/векторный поиск | Ожидается более точный и полный контекст | HIGH | Комбинация subgraph retrieval и традиционного retrieval |
| Режимы запроса: локальный (entity-neighborhood) и глобальный (community summaries) | Пользователи хотят и детали, и обзор | HIGH | Локальный и глобальный режимы в GraphRAG |
| Инкрементальное обновление индекса | Без него обновления слишком дорогие | HIGH | Инкрементальная вставка новых подграфов |
| Observability: трассировка, метрики, оценка качества | Production без этого не поддерживается | MEDIUM | Инструментирование и оценка качества |
| Кэширование запросов и контекста | Ожидание по латентности и стоимости | MEDIUM | Кэш для retrieval и ответа |
| Контроль доступа и фильтрация по ACL | Корпоративные данные требуют защиты | MEDIUM | Политики доступа на уровне документов/узлов |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Dynamic community selection для глобального поиска | Снижает шум и стоимость, повышает релевантность | HIGH | Отбор релевантных сообществ перед map-reduce |
| DRIFT-подобный гибрид глобального+локального поиска | Улучшает точность и полноту на сложных вопросах | HIGH | Генерация follow-up вопросов по community insights |
| Автотюнинг/промпт-тюнинг индексации | Быстрая адаптация под домен без ручных правок | MEDIUM | Автоматическая генерация/настройка промптов |
| Многомасштабное контекстирование (multi-hop + summary layers) | Лучше отвечает на многошаговые вопросы | HIGH | Комбинация subgraph и community summaries |
| Экспериментальный контур качества (A/B, offline eval) | Ускоряет улучшения и снижает регрессии | MEDIUM | Автоматизированные RAG-метрики |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Полная real-time переиндексация всего графа | “Всегда актуально” | Взрывает стоимость и латентность | Инкрементальные обновления + периодический batch |
| Свободный доступ пользователей к raw graph query (Cypher/SQL) | “Гибкость” | Риски безопасности и непредсказуемые нагрузки | Ограниченные шаблоны запросов и фасады |
| Мультимодальность “сразу” | Кажется универсальным | Сложность пайплайна и качества | Сначала PDF-текст, позже расширение |

## Feature Dependencies

```
[Графовая индексация]
    L--requires--> [Надежный ingestion для PDF]

[Локальный/глобальный режимы поиска]
    L--requires--> [Графовая индексация]

[Dynamic community selection]
    L--requires--> [Глобальный режим поиска]

[DRIFT-подобный поиск]
    L--requires--> [Локальный/глобальный режимы поиска]

[Автотюнинг промптов индексации]
    L--enhances--> [Графовая индексация]

[Экспериментальный контур качества]
    L--requires--> [Observability]
```

### Dependency Notes

- **[Графовая индексация] requires [Надежный ingestion для PDF]:** Без стабильного ingestion граф будет неполным и несогласованным.
- **[Локальный/глобальный режимы поиска] requires [Графовая индексация]:** Оба режима опираются на граф и его summaries.
- **[Dynamic community selection] requires [Глобальный режим поиска]:** Нужны community reports для отбора.
- **[DRIFT-подобный поиск] requires [Локальный/глобальный режимы поиска]:** DRIFT комбинирует оба подхода.
- **[Автотюнинг промптов индексации] enhances [Графовая индексация]:** Улучшает качество извлечения сущностей/отношений.
- **[Экспериментальный контур качества] requires [Observability]:** Без трассировки и логов нельзя валидировать метрики.

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [ ] Надежный ingestion для PDF — без этого нет данных
- [ ] Графовая индексация (entities/relations + дедупликация) — ядро Graph-RAG
- [ ] Локальный и глобальный режимы поиска — покрывают детали и обзор
- [ ] Observability (трейсы + базовые RAG-метрики) — контроль качества
- [ ] Базовый UI с выдачей ответов и цитат — пользовательская ценность

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] Кэширование — при росте нагрузки и стоимости
- [ ] Автотюнинг промптов — при появлении доменных данных
- [ ] Экспериментальный контур качества (A/B, offline) — когда есть трафик

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] DRIFT-подобный поиск — высокая сложность, позже
- [ ] Dynamic community selection — после стабилизации глобального поиска
- [ ] Мультимодальность — только при подтвержденной потребности

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Надежный ingestion для PDF | HIGH | MEDIUM | P1 |
| Графовая индексация | HIGH | HIGH | P1 |
| Локальный/глобальный режимы поиска | HIGH | HIGH | P1 |
| Observability | HIGH | MEDIUM | P1 |
| Базовый UI с цитатами | HIGH | MEDIUM | P1 |
| Кэширование | MEDIUM | MEDIUM | P2 |
| Автотюнинг промптов | MEDIUM | MEDIUM | P2 |
| Экспериментальный контур качества | MEDIUM | MEDIUM | P2 |
| Dynamic community selection | MEDIUM | HIGH | P3 |
| DRIFT-подобный поиск | MEDIUM | HIGH | P3 |

## Competitor Feature Analysis

| Feature | Competitor A | Competitor B | Our Approach |
|---------|--------------|--------------|--------------|
| Локальный/глобальный режимы поиска | Microsoft GraphRAG: local/global search | LlamaIndex: KG RAG retriever | Взять как table stakes |
| Dynamic community selection | Microsoft GraphRAG | — | Рассмотреть после v1 |
| DRIFT-подобный поиск | Microsoft Research (DRIFT) | — | Будущее улучшение |
| Инкрементальные обновления графа | LightRAG | — | Обязательная поддержка |
| Observability и оценка качества | RAGAS + Langfuse | — | Стандарт для production |

## Sources

- Microsoft GraphRAG docs and research blogs
- LlamaIndex knowledge graph RAG documentation
- LightRAG project documentation
- RAGAS evaluation metrics documentation
- Langfuse observability documentation

---
*Feature research for: Production Graph-RAG pipeline*
*Researched: 2026-03-04*
