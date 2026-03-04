from __future__ import annotations

import json
from pathlib import Path

from reportlab.pdfgen import canvas

from ingestion.pipeline import ingest_dataset


def _write_pdf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(path))
    pdf.setFont("Helvetica", 12)
    pdf.drawString(72, 720, text)
    pdf.showPage()
    pdf.save()


def _load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_ingestion_determinism(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "out"
    dataset = "demo"

    pdf_path = input_dir / "sample.pdf"
    _write_pdf(pdf_path, "Hello deterministic ingestion")

    manifest_first = ingest_dataset(input_dir, dataset, output_dir)
    manifest_second = ingest_dataset(input_dir, dataset, output_dir)

    assert manifest_first == manifest_second
    manifest_file = output_dir / dataset / "manifest.json"
    assert _load_manifest(manifest_file) == manifest_first


def test_ingestion_incremental_updates(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "out"
    dataset = "demo"

    pdf_path_one = input_dir / "one.pdf"
    pdf_path_two = input_dir / "two.pdf"
    _write_pdf(pdf_path_one, "First doc")
    _write_pdf(pdf_path_two, "Second doc")

    manifest_initial = ingest_dataset(input_dir, dataset, output_dir)
    initial_doc_ids = {doc["doc_id"] for doc in manifest_initial["documents"]}
    assert initial_doc_ids == {"one.pdf", "two.pdf"}

    pdf_path_two.unlink()
    pdf_path_three = input_dir / "three.pdf"
    _write_pdf(pdf_path_one, "First doc updated")
    _write_pdf(pdf_path_three, "Third doc")

    manifest_updated = ingest_dataset(input_dir, dataset, output_dir)
    updated_doc_ids = {doc["doc_id"] for doc in manifest_updated["documents"]}

    assert updated_doc_ids == {"one.pdf", "three.pdf"}
    initial_hashes = {doc["doc_id"]: doc["doc_hash"] for doc in manifest_initial["documents"]}
    updated_hashes = {doc["doc_id"]: doc["doc_hash"] for doc in manifest_updated["documents"]}
    assert updated_hashes["one.pdf"] != initial_hashes["one.pdf"]
