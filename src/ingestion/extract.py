from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pypdf
from pypdf import PdfReader

from ingestion.constants import INGESTION_VERSION


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    text: str
    ocr_used: bool
    ocr_confidence: float | None


@dataclass(frozen=True)
class ExtractedTextResult:
    text: str
    pages: list[ExtractedPage]
    ocr_used: bool
    ocr_quality: str
    parser_info: dict[str, Any]
    metadata: dict[str, Any]
    warnings: list[str]


def extract_text_from_pdf(path: Path) -> ExtractedTextResult:
    reader = PdfReader(str(path))
    page_texts: list[str] = []
    pages: list[ExtractedPage] = []
    warnings: list[str] = []

    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = _normalize_text(text)
        page_texts.append(text)
        pages.append(
            ExtractedPage(
                page_number=index,
                text=text,
                ocr_used=False,
                ocr_confidence=None,
            )
        )

    base_text = _normalize_text("\n".join(page_texts))
    ocr_used = False
    ocr_quality = "none"

    if _should_attempt_ocr(page_texts):
        ocr_pages, ocr_warning = _run_ocr(path, len(page_texts))
        if ocr_warning:
            warnings.append(ocr_warning)
        if ocr_pages:
            merged_pages: list[ExtractedPage] = []
            merged_texts: list[str] = []
            for base_page, ocr_page in zip(pages, ocr_pages, strict=False):
                if len(base_page.text.strip()) < 20 and ocr_page.text.strip():
                    merged_pages.append(ocr_page)
                    merged_texts.append(ocr_page.text)
                    ocr_used = True
                else:
                    merged_pages.append(base_page)
                    merged_texts.append(base_page.text)
            pages = merged_pages
            base_text = _normalize_text("\n".join(merged_texts))
            ocr_quality = _derive_ocr_quality(ocr_pages)
        elif ocr_warning:
            ocr_quality = "unavailable"

    metadata = _extract_pdf_metadata(reader)
    parser_info = {
        "ingestion_version": INGESTION_VERSION,
        "parser": "pypdf",
        "parser_version": pypdf.__version__,
        "ocr": "pytesseract",
        "ocr_attempted": _should_attempt_ocr(page_texts),
        "extracted_at": datetime.now(datetime.UTC).isoformat(),
    }

    return ExtractedTextResult(
        text=base_text,
        pages=pages,
        ocr_used=ocr_used,
        ocr_quality=ocr_quality,
        parser_info=parser_info,
        metadata=metadata,
        warnings=warnings,
    )


def _normalize_text(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n")).strip()


def _should_attempt_ocr(page_texts: list[str]) -> bool:
    if not page_texts:
        return False
    empty_pages = sum(1 for text in page_texts if len(text.strip()) < 20)
    return empty_pages / len(page_texts) >= 0.5


def _run_ocr(path: Path, page_count: int) -> tuple[list[ExtractedPage], str | None]:
    try:
        import pytesseract
        from pdf2image import convert_from_path
    except Exception as exc:  # pragma: no cover - missing optional dependencies
        return [], f"OCR dependencies unavailable: {exc}"

    try:
        images = convert_from_path(str(path), fmt="png")
    except Exception as exc:  # pragma: no cover - system dependency missing
        return [], f"OCR conversion failed: {exc}"

    pages: list[ExtractedPage] = []
    for index, image in enumerate(images, start=1):
        text = _normalize_text(pytesseract.image_to_string(image))
        confidence = _ocr_confidence(pytesseract, image)
        pages.append(
            ExtractedPage(
                page_number=index,
                text=text,
                ocr_used=True,
                ocr_confidence=confidence,
            )
        )

    if len(pages) < page_count:
        return pages, "OCR returned fewer pages than PDF page count."

    return pages, None


def _ocr_confidence(pytesseract_module: Any, image: Any) -> float | None:
    try:
        data = pytesseract_module.image_to_data(image, output_type=pytesseract_module.Output.DICT)
    except Exception:
        return None
    confidences = [
        float(conf)
        for conf in data.get("conf", [])
        if isinstance(conf, (int, float, str)) and str(conf).strip() != "-1"
    ]
    if not confidences:
        return None
    return sum(confidences) / len(confidences)


def _derive_ocr_quality(pages: list[ExtractedPage]) -> str:
    confidences = [page.ocr_confidence for page in pages if page.ocr_confidence is not None]
    if not confidences:
        return "unknown"
    average = sum(confidences) / len(confidences)
    if average >= 80:
        return "high"
    if average >= 60:
        return "medium"
    if average >= 40:
        return "low"
    return "poor"


def _extract_pdf_metadata(reader: PdfReader) -> dict[str, Any]:
    info = reader.metadata or {}
    metadata: dict[str, Any] = {}
    for key, value in info.items():
        clean_key = str(key).lstrip("/")
        metadata[clean_key] = value
    return metadata
