from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from ingestion.extract import ExtractedPage


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    text: str
    metadata: dict[str, Any]


def chunk_pages(
    pages: list[ExtractedPage],
    doc_id: str,
    source_path: str,
    doc_metadata: dict[str, Any],
    max_chars: int = 2000,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    for page in pages:
        page_chunks = _split_text(page.text, max_chars=max_chars)
        for index, chunk_text in enumerate(page_chunks):
            chunk_id = _stable_chunk_id(doc_id, page.page_number, index)
            metadata = {
                "source_path": source_path,
                "page_number": page.page_number,
                "chunk_index": index,
                "author": doc_metadata.get("Author"),
                "title": doc_metadata.get("Title"),
                "created_at": doc_metadata.get("CreationDate"),
                "ocr_used": page.ocr_used,
                "ocr_confidence": page.ocr_confidence,
            }
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    text=chunk_text,
                    metadata=metadata,
                )
            )
    return chunks


def _split_text(text: str, max_chars: int) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    return [cleaned[i : i + max_chars] for i in range(0, len(cleaned), max_chars)]


def _stable_chunk_id(doc_id: str, page_number: int, chunk_index: int) -> str:
    base = f"{doc_id}:{page_number}:{chunk_index}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()
