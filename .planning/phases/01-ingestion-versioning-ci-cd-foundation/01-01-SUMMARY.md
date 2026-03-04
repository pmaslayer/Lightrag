---
phase: 01-ingestion-versioning-ci-cd-foundation
plan: 01
subsystem: ingestion
tags: [pdf, ocr, manifest, chunking, cli, incremental]

# Dependency graph
requires: []
provides:
  - deterministic PDF ingestion pipeline
  - OCR best-effort extraction with quality signals
  - stable chunking and metadata schema
  - incremental manifest updates with atomic writes
  - ingestion CLI entrypoint
affects: [indexing, retrieval, ci-cd]

# Tech tracking
tech-stack:
  added: [pypdf, pdf2image, pytesseract, orjson, reportlab]
  patterns: [content-hash incremental updates, atomic manifest write, stable chunk ids]

key-files:
  created:
    - src/ingestion/constants.py
    - src/ingestion/chunking.py
    - src/ingestion/pipeline.py
    - src/storage/manifest.py
    - src/cli/ingest.py
    - tests/ingestion/test_ingestion_pipeline.py
  modified:
    - pyproject.toml
    - src/ingestion/extract.py

key-decisions:
  - "doc_hash рассчитывается по байтам PDF (pdf_bytes) для инкрементальности"
  - "chunk_id строится из doc_id + page + chunk_index для стабильности границ"
  - "manifest пишется атомарно (temp + rename) и не перезаписывается без изменений"

patterns-established:
  - "Stable chunk IDs: sha256(doc_id:page:chunk_index)"
  - "Incremental ingestion: reuse unchanged docs by content-hash"

requirements-completed: [ING-01, ING-02, ING-03]

# Metrics
duration: 14min
completed: 2026-03-04
---

# Phase 01: Ingestion Pipeline Summary

**Deterministic PDF ingestion with OCR best-effort, stable chunk IDs, and incremental manifest updates via CLI**

## Performance

- **Duration:** 14 min
- **Started:** 2026-03-04T17:59:12Z
- **Completed:** 2026-03-04T18:12:44Z
- **Tasks:** 6
- **Files modified:** 11

## Accomplishments
- Реализовано извлечение текста из PDF с OCR best-effort и метками качества.
- Добавлены стабильные chunk_id и минимальная схема метаданных чанка.
- Собран инкрементальный manifest с атомарной записью и CLI входом.

## Task Commits

Each task was committed atomically:

1. **Task 1: Зафиксировать базовый стек и структуру проекта** - `adb89f4` (feat)
2. **Task 2: Реализовать извлечение текста из PDF с OCR best-effort** - `33100f6` (feat)
3. **Task 3: Стабильный chunking и metadata schema** - `ff00054` (feat)
4. **Task 4: Manifest и инкрементальная логика** - `a510813` (feat)
5. **Task 5: CLI для ingestion** - `d6d2d1f` (feat)
6. **Task 6: Тесты: детерминизм и инкрементальность** - `b16d298` (test)

## Files Created/Modified
- `C:\Users\mearbye\Documents\MyProject\LightragTest\pyproject.toml` - зависимости ingestion и CLI entrypoint
- `C:\Users\mearbye\Documents\MyProject\LightragTest\src\ingestion\constants.py` - решения по окружению и системным зависимостям
- `C:\Users\mearbye\Documents\MyProject\LightragTest\src\ingestion\extract.py` - извлечение текста и OCR best-effort
- `C:\Users\mearbye\Documents\MyProject\LightragTest\src\ingestion\chunking.py` - стабильный chunking и schema
- `C:\Users\mearbye\Documents\MyProject\LightragTest\src\ingestion\pipeline.py` - инкрементальный manifest и orchestration
- `C:\Users\mearbye\Documents\MyProject\LightragTest\src\storage\manifest.py` - атомарная запись manifest
- `C:\Users\mearbye\Documents\MyProject\LightragTest\src\cli\ingest.py` - CLI команда `ingest`
- `C:\Users\mearbye\Documents\MyProject\LightragTest\tests\ingestion\test_ingestion_pipeline.py` - тесты детерминизма и инкрементальности

## Decisions Made
- doc_hash рассчитывается по байтам PDF, а не по нормализованному тексту, чтобы избежать ложных совпадений.
- chunk_id зависит только от doc_id и стабильных границ чанков (page + index).
- manifest не перезаписывается при отсутствии изменений (детерминизм повторных запусков).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Исправлено использование `datetime.UTC` для совместимости с Python 3.12**
- **Found during:** Task 4 (Manifest и инкрементальная логика)
- **Issue:** `datetime.UTC` недоступен при импорте класса `datetime`, вызывал ошибку выполнения.
- **Fix:** Перешли на `from datetime import UTC` и `datetime.now(UTC)`.
- **Files modified:** `C:\Users\mearbye\Documents\MyProject\LightragTest\src\ingestion\extract.py`, `C:\Users\mearbye\Documents\MyProject\LightragTest\src\ingestion\pipeline.py`
- **Verification:** `pytest` + `ruff check`
- **Committed in:** `a510813` (part of task commit)

---

**Total deviations:** 1 auto-fixed (Rule 1)
**Impact on plan:** Исправление требовалось для корректного выполнения, без изменения объёма работ.

## Issues Encountered
- Локально отсутствовали зависимости (pypdf/pdf2image/reportlab) для тестов; установлены перед запуском тестов.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Ingestion пайплайн и manifest готовы для следующего шага индексации.
- Блокеров нет.

---
*Phase: 01-ingestion-versioning-ci-cd-foundation*
*Completed: 2026-03-04*

## Self-Check: PASSED
