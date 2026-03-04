# Pitfalls Research

**Domain:** Graph-RAG pipeline (Lightrag, корпоративные PDF, Postgres граф+векторы)
**Researched:** 2026-03-04
**Confidence:** MEDIUM

## Critical Pitfalls

### Pitfall 1: Ошибки entity linking и слияния сущностей

**What goes wrong:**
Граф склеивает разные сущности ("Apple" компания и фрукт) или, наоборот, дублирует одну сущность под разными именами. В результате связи и ответы становятся неверными, а multi-hop рассуждение рушится.

**Why it happens:**
Entity/relationship extraction выполняется автоматически, а дедупликация часто сводится к совпадению названия и типа. Без каноникализации, алиасов и доменной онтологии ошибки на входе масштабируются в графе.

**How to avoid:**
- Ввести слой нормализации: алиасы, синонимы, правила каноникализации по домену.
- Хранить уверенность и источник для каждого утверждения; слияние только при достаточной уверенности.
- Включить ручную валидацию для топ?сущностей (частотные узлы, high-degree).

**Warning signs:**
- Резкий рост количества почти одинаковых узлов.
- Узлы с чрезмерной степенью (generic nodes) и «универсальными» связями.
- Жалобы пользователей на «смешивание» объектов.

**Phase to address:**
Phase 2: Graph Extraction & Entity Resolution.

---

### Pitfall 2: Дрейф схемы отношений (edge?type explosion)

**What goes wrong:**
Граф содержит сотни синонимичных типов связей ("uses", "utilized_by", "depends_on"), из?за чего поиск по связям ломается, а запросы становятся непредсказуемыми.

**Why it happens:**
Открытая экстракция без контролируемой схемы/онтологии порождает хаотичные типы связей, которые не нормализуются в единый словарь.

**How to avoid:**
- Ограничить набор типов связей доменной онтологией.
- Ввести маппинг/нормализацию отношений на этапе экстракции и/или пост?обработки.
- Периодически пересматривать и сжимать редкие типы связей.

**Warning signs:**
- Быстрый рост числа уникальных типов связей.
- Разные формулировки одной и той же связи в отчетах.
- Резкое падение качества при multi-hop запросах.

**Phase to address:**
Phase 2: Graph Extraction & Schema Normalization.

---

### Pitfall 3: Неподходящее chunking для графовой экстракции

**What goes wrong:**
Ключевые связи распадаются между чанками, сущности теряют контекст, а извлеченные триплеты становятся неполными или ошибочными.

**Why it happens:**
Chunking оптимизируют под векторный поиск, а не под извлечение отношений. Длинные PDF и разрывы по границам страниц ломают связь «сущность?контекст».

**How to avoid:**
- Использовать overlap и контекстные окна для длинных документов.
- Учитывать структуру PDF (заголовки, разделы, таблицы).
- Отдельно валидировать качество экстракции сущностей и связей при разных настройках chunking.

**Warning signs:**
- Низкая полнота связей при ручной проверке.
- Сильная деградация качества на длинных документах.

**Phase to address:**
Phase 1: Ingestion & Chunking Strategy.

---

### Pitfall 4: Отсутствие «bridge evidence» для multi-hop вопросов

**What goes wrong:**
Графовое рассуждение обрывается, потому что промежуточные документы/узлы не попадают в топ?K. Ответы становятся неполными или галлюцинируют связи.

**Why it happens:**
Статическое извлечение и одношаговый retrieval не поднимают промежуточные доказательства, особенно для сложных цепочек.

**How to avoid:**
- Итеративный retrieval с контролем шума.
- Реранжирование путей/подграфов по покрытию цепочки.
- Явная оптимизация на «bridge» узлы в ранжировании.

**Warning signs:**
- Хорошая точность на одношаговых вопросах и провалы на сложных.
- Отсутствие ключевых промежуточных документов в трассах.

**Phase to address:**
Phase 3: Retrieval & Reasoning (Graph Traversal + Reranking).

---

### Pitfall 5: Переретрив и шум (retrieval overload)

**What goes wrong:**
Система подает слишком много контекста. Модель теряется, растет латентность, ответы ухудшаются.

**Why it happens:**
Команда повышает recall «на всякий случай», не измеряя деградацию из?за шума и ограничений контекста.

**How to avoid:**
- Калибровать top?K, threshold и длину контекста на реальных вопросах.
- Ввести метрики контекст?точности и шумочувствительности.

**Warning signs:**
- Ухудшение faithfulness при росте K.
- Увеличение латентности без роста качества.

**Phase to address:**
Phase 3: Retrieval & Context Assembly.

---

### Pitfall 6: Отсутствие компонентной оценки качества (retrieval vs generation)

**What goes wrong:**
Команда видит «плохие ответы», но не понимает: проблема в retrieval, в графе или в генерации. Исправления становятся случайными.

**Why it happens:**
Оценка только end?to?end, без метрик контекст?precision/recall и faithfulness.

**How to avoid:**
- Вести метрики retrieval (context precision/recall, entity recall).
- Отдельно измерять faithfulness и answer relevancy.
- Добавить golden set для ключевых сценариев.

**Warning signs:**
- Невозможно объяснить, почему ответ плохой.
- Улучшения не воспроизводятся.

**Phase to address:**
Phase 4: Evaluation & Observability (RAGAS + tracing).

---

### Pitfall 7: Устаревание графа и версий эмбеддингов

**What goes wrong:**
Ответы опираются на устаревшие сведения или несовместимые версии эмбеддингов/графа. Результаты становятся непоследовательными.

**Why it happens:**
Граф строится «разово», а обновления данных и эмбеддингов не имеют версии/инкрементального процесса.

**How to avoid:**
- Ввести версионирование данных, графа и эмбеддингов.
- Планировать инкрементальные переиндексации и бэкауты.
- Отдельно хранить «активные» и «архивные» версии.

**Warning signs:**
- Появляются ответы на основе устаревших документов.
- Несовместимые результаты после обновления модели эмбеддингов.

**Phase to address:**
Phase 1: Data Lifecycle & Versioning.

---

### Pitfall 8: Экстракция подграфов (data exfiltration) через запросы

**What goes wrong:**
Атакующий может реконструировать части графа, извлекая чувствительные связи через серию запросов.

**Why it happens:**
Graph?RAG раскрывает структурированные связи, а на уровне API отсутствуют ограничения на типы запросов, rate limits и мониторинг.

**How to avoid:**
- Ограничить типы запросов и объем выдачи.
- Лимиты и аномал?детект для частых/структурных запросов.
- Фильтры чувствительных узлов и edge?redaction.

**Warning signs:**
- Повторяющиеся шаблонные запросы с малой вариативностью.
- Систематические запросы на «соседей» и «связи».

**Phase to address:**
Phase 5: Security & Abuse Prevention.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Сливать сущности по совпадению названия | Быстрое построение графа | Высокий уровень коллизий и ложных связей | Только прототип |
| Один тип «generic relation» | Простая схема | Потеря семантики, плохой поиск | Никогда |
| Хранить только итоговые summaries узлов | Экономия места | Потеря трассируемости до источников | Только для demo |
| Отсутствие версий эмбеддингов | Быстрые обновления | Несовместимость результатов | Никогда |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Postgres (graph+vector) | Один индекс для разных embedding?версий | Версионировать индексы и хранить активный alias |
| RAGAS | Оценка без набора эталонных вопросов | Создать golden set и валидировать метрики |
| Langfuse | Логирование только финального ответа | Трассировать retrieval, граф?проход, rerank, prompt |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Полный rebuild графа при каждом обновлении | Простои и скачки стоимости | Инкрементальная индексация | При росте частоты обновлений |
| Линейный обход графа для каждого запроса | Латентность растет нелинейно | Кеширование подграфов и путей | 10^6+ узлов |
| Большой top?K для всех запросов | Рост latency и cost | Адаптивный K по сложности запроса | p95 > 2–5с |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Доступ к «соседям» без фильтров | Утечка чувствительных связей | RBAC/ABAC на узлы и связи |
| Отсутствие rate?limit на граф?запросы | Реконструкция подграфов | Квоты, детект шаблонов |
| Логи без маскирования | Утечка PII из PDF | Маскирование и ретеншн?политики |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Нет объяснения «почему этот ответ» | Потеря доверия | Показывать ключевые узлы/источники |
| Смешение локального и глобального поиска | Непредсказуемые ответы | Разделить режимы и UI?подсказки |
| Нет контроля свежести | Пользователь использует устаревшие данные | Отображать дату источника |

## "Looks Done But Isn't" Checklist

- [ ] **Graph Extraction:** часто отсутствует валидация entity?resolution — проверить ручной выборкой
- [ ] **Retrieval:** нет тестов на multi-hop вопросы — проверить bridge evidence
- [ ] **Evaluation:** метрики только end?to?end — добавить component?level
- [ ] **Security:** нет политики выдачи связей — проверить RBAC/ABAC

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Entity linking ошибки | HIGH | Откат версии графа, переиндексация с нормализацией |
| Дрейф схемы | MEDIUM | Нормализовать типы, пересобрать edge?таблицы |
| Retrieval overload | LOW | Снизить K, включить rerank и threshold |
| Subgraph extraction | HIGH | Ввести фильтры, блокировать шаблоны запросов, аудит |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Ошибки entity linking | Phase 2 | Ручная проверка топ?сущностей, precision/recall |
| Дрейф схемы отношений | Phase 2 | Отчет по типам связей и их сжатию |
| Неподходящий chunking | Phase 1 | A/B качество экстракции на длинных PDF |
| Нет bridge evidence | Phase 3 | Тест?набор multi-hop, анализ трасс |
| Retrieval overload | Phase 3 | Графики качества vs K |
| Нет компонентной оценки | Phase 4 | Набор метрик retrieval+faithfulness |
| Устаревание графа | Phase 1 | Регулярные контрольные запросы по свежести |
| Subgraph extraction | Phase 5 | Аномал?детект и аудит запросов |

## Sources

- https://www.microsoft.com/en-us/research/project/graphrag/
- https://microsoft.github.io/graphrag/index/default_dataflow/
- https://www.ideasthesia.org/microsoft-graphrag-architecture-and-lessons-learned/
- https://arxiv.org/abs/2509.25530
- https://arxiv.org/abs/2511.05549
- https://arxiv.org/abs/2602.06495
- https://docs.ragas.io/en/stable/concepts/metrics/
- https://docs.ragas.io/en/v0.1.21/concepts/metrics/
- https://randeepbhatia.com/reference/why-rag-fails
- https://docs.llamaindex.ai/en/stable/examples/node_parsers/slide_parser/

---
*Pitfalls research for: Graph-RAG on Lightrag (production)*
*Researched: 2026-03-04*
