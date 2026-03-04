# Graph-RAG на Lightrag (Production)

## What This Is

Масштабируемый production-ready Graph-RAG пайплайн на базе Lightrag для внутреннего поиска по корпоративным PDF. Система должна обеспечивать модульную архитектуру, распределённую обработку, графовую индексацию и полный observability с UI для работы пользователей.

## Core Value

Пользователь получает точные и воспроизводимые ответы через Graph-RAG поверх корпоративных данных при контролируемой наблюдаемости и качестве.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Production-grade Graph-RAG пайплайн на Lightrag
- [ ] Полный observability (логирование/метрики/трейсинг) через RAGAS и LangFuse
- [ ] Модульная архитектура и распределённая обработка
- [ ] Графовое хранилище/индексация на Postgres с расширениями
- [ ] Версионирование данных и эмбеддингов
- [ ] Кэширование
- [ ] Безопасность и отказоустойчивость
- [ ] CI/CD и тестирование
- [ ] Полноценный UI для пользователей

### Out of Scope

- Подбор конкретных LLM/эмбеддинговых моделей сейчас — будет решено позже
- Точные частоты обновления данных — определить после запуска

## Context

- Основной источник данных: PDF
- Масштаб: средний (ориентир 10^6–10^7 документов, p95 2–5с)
- Деплой: VM/containers (без Kubernetes)
- Хранилище: Postgres с расширениями для векторов и графов
- Пользователи: внутренние

## Constraints

- **Platform**: VM/containers — без Kubernetes
- **Storage**: Postgres как единое хранилище (векторы + граф)
- **Observability**: использовать RAGAS и LangFuse
- **Framework**: Lightrag как основной фреймворк

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Lightrag как основной фреймворк | Требуется Graph-RAG и модульность | — Pending |
| Postgres для векторов и графа | Единое хранилище и простота эксплуатации | — Pending |
| RAGAS + LangFuse для observability | Нужна полная трассировка и оценка качества | — Pending |
| Деплой без Kubernetes | Ограничение окружения | — Pending |

---
*Last updated: 2026-03-04 after initialization*
