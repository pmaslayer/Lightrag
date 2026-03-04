from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ingestion.chunking import Chunk, chunk_pages
from ingestion.constants import INGESTION_VERSION
from ingestion.extract import ExtractedTextResult, extract_text_from_pdf
from storage.manifest import load_manifest, write_manifest_atomic


class IngestionError(RuntimeError):
    def __init__(self, message: str, errors: list[str]) -> None:
        super().__init__(message)
        self.errors = errors


def ingest_dataset(input_path: Path, dataset: str, out_dir: Path) -> dict[str, Any]:
    input_path = input_path.resolve()
    out_dir = out_dir.resolve()
    manifest_path = _manifest_path(out_dir, dataset)

    existing_manifest = load_manifest(manifest_path)
    existing_docs = _index_docs(existing_manifest)
    existing_chunks = _index_chunks(existing_manifest)

    pdf_files = _collect_pdfs(input_path)
    if not pdf_files:
        raise IngestionError("No PDF files found for ingestion.", [])

    errors: list[str] = []
    documents: list[dict[str, Any]] = []
    chunks: list[dict[str, Any]] = []
    changed = False

    for pdf_path in pdf_files:
        doc_id = _doc_id(input_path, pdf_path)
        doc_hash = _hash_file(pdf_path)
        existing_doc = existing_docs.get(doc_id)

        if existing_doc and existing_doc.get("doc_hash") == doc_hash:
            documents.append(existing_doc)
            chunks.extend(existing_chunks.get(doc_id, []))
            continue

        changed = True
        try:
            extracted = extract_text_from_pdf(pdf_path)
            doc_entry, chunk_entries = _build_entries(
                doc_id=doc_id,
                source_path=str(pdf_path),
                doc_hash=doc_hash,
                extracted=extracted,
            )
            documents.append(doc_entry)
            chunks.extend(chunk_entries)
        except Exception as exc:
            errors.append(f"{pdf_path}: {exc}")

    if errors:
        raise IngestionError("Ingestion failed with errors.", errors)

    existing_doc_ids = set(existing_docs.keys())
    current_doc_ids = {doc["doc_id"] for doc in documents}
    removed_doc_ids = existing_doc_ids - current_doc_ids
    if removed_doc_ids:
        changed = True

    if existing_manifest and not changed:
        return existing_manifest

    manifest = {
        "dataset": dataset,
        "doc_hash_source": "pdf_bytes",
        "ingestion_version": INGESTION_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "documents": sorted(documents, key=lambda item: item["doc_id"]),
        "chunks": sorted(chunks, key=lambda item: item["chunk_id"]),
    }

    write_manifest_atomic(manifest_path, manifest)
    return manifest


def _build_entries(
    doc_id: str,
    source_path: str,
    doc_hash: str,
    extracted: ExtractedTextResult,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    ingested_at = datetime.now(UTC).isoformat()
    chunks = chunk_pages(
        pages=extracted.pages,
        doc_id=doc_id,
        source_path=source_path,
        doc_metadata=extracted.metadata,
    )
    doc_entry = {
        "doc_id": doc_id,
        "source_path": source_path,
        "doc_hash": doc_hash,
        "metadata": extracted.metadata,
        "parser_info": extracted.parser_info,
        "ocr_quality": extracted.ocr_quality,
        "chunk_ids": [chunk.chunk_id for chunk in chunks],
        "ingested_at": ingested_at,
    }
    chunk_entries = [_chunk_entry(chunk, ingested_at) for chunk in chunks]
    return doc_entry, chunk_entries


def _chunk_entry(chunk: Chunk, ingested_at: str) -> dict[str, Any]:
    return {
        "chunk_id": chunk.chunk_id,
        "doc_id": chunk.doc_id,
        "text": chunk.text,
        "metadata": chunk.metadata,
        "ingested_at": ingested_at,
    }


def _collect_pdfs(input_path: Path) -> list[Path]:
    if input_path.is_file() and input_path.suffix.lower() == ".pdf":
        return [input_path]
    if input_path.is_dir():
        return sorted(path for path in input_path.rglob("*.pdf") if path.is_file())
    return []


def _doc_id(root: Path, pdf_path: Path) -> str:
    if root.is_dir():
        relative = pdf_path.relative_to(root)
        return relative.as_posix()
    return pdf_path.name


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _index_docs(manifest: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not manifest:
        return {}
    return {doc["doc_id"]: doc for doc in manifest.get("documents", [])}


def _index_chunks(manifest: dict[str, Any] | None) -> dict[str, list[dict[str, Any]]]:
    if not manifest:
        return {}
    chunks_by_doc: dict[str, list[dict[str, Any]]] = {}
    for chunk in manifest.get("chunks", []):
        chunks_by_doc.setdefault(chunk["doc_id"], []).append(chunk)
    return chunks_by_doc


def _manifest_path(out_dir: Path, dataset: str) -> Path:
    return out_dir / dataset / "manifest.json"
