from __future__ import annotations

from pathlib import Path

import pytest
from reportlab.pdfgen import canvas

from ingestion.pipeline import ingest_dataset
from storage.manifest import write_manifest_atomic
from versioning.registry import (
    VersioningError,
    create_embedding_version,
    create_index_version,
    get_active_index,
    list_versions,
    register_dataset_version,
    rollback_active_index,
    set_active_index,
)


def _write_manifest(path: Path, doc_count: int) -> dict:
    manifest = {
        "dataset": "demo",
        "ingestion_version": "0.1.0",
        "documents": [{"doc_id": f"doc-{idx}"} for idx in range(doc_count)],
        "chunks": [{"chunk_id": f"chunk-{idx}"} for idx in range(doc_count * 2)],
    }
    write_manifest_atomic(path, manifest)
    return manifest


def _write_pdf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(path))
    pdf.setFont("Helvetica", 12)
    pdf.drawString(72, 720, text)
    pdf.showPage()
    pdf.save()


def test_dataset_versions_and_retention(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    dataset = "demo"
    manifest_path = out_dir / dataset / "manifest.json"

    for count in range(1, 5):
        manifest = _write_manifest(manifest_path, count)
        register_dataset_version(manifest, manifest_path, out_dir, dataset)

    versions = list_versions("dataset", out_dir, dataset)
    assert len(versions) == 3
    assert all(version.name for version in versions)


def test_switch_and_rollback_active_index(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    dataset = "demo"
    manifest_path = out_dir / dataset / "manifest.json"
    manifest = _write_manifest(manifest_path, 1)

    dataset_entry = register_dataset_version(manifest, manifest_path, out_dir, dataset)
    embedding_entry = create_embedding_version("text-embed-v1", {"dim": 1536}, out_dir, dataset)
    index_entry_one = create_index_version(
        dataset_entry.name, embedding_entry.name, out_dir, dataset
    )
    index_entry_two = create_index_version(
        dataset_entry.name, embedding_entry.name, out_dir, dataset
    )

    set_active_index(index_entry_one.name, out_dir, dataset, is_admin=True)
    active = get_active_index(out_dir, dataset)
    assert active["active_index"] == index_entry_one.name

    set_active_index(index_entry_two.name, out_dir, dataset, is_admin=True)
    active = get_active_index(out_dir, dataset)
    assert active["active_index"] == index_entry_two.name

    rolled_back = rollback_active_index(out_dir, dataset, is_admin=True)
    assert rolled_back["active_index"] == index_entry_one.name


def test_admin_required_for_switch(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    dataset = "demo"
    manifest_path = out_dir / dataset / "manifest.json"
    manifest = _write_manifest(manifest_path, 1)

    dataset_entry = register_dataset_version(manifest, manifest_path, out_dir, dataset)
    embedding_entry = create_embedding_version("text-embed-v1", {"dim": 1536}, out_dir, dataset)
    index_entry = create_index_version(dataset_entry.name, embedding_entry.name, out_dir, dataset)

    with pytest.raises(VersioningError):
        set_active_index(index_entry.name, out_dir, dataset, is_admin=False)


def test_retention_keeps_active_index(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    dataset = "demo"
    manifest_path = out_dir / dataset / "manifest.json"
    manifest = _write_manifest(manifest_path, 1)

    dataset_entry = register_dataset_version(manifest, manifest_path, out_dir, dataset)
    embedding_entry = create_embedding_version("text-embed-v1", {"dim": 1536}, out_dir, dataset)

    index_entries = [
        create_index_version(dataset_entry.name, embedding_entry.name, out_dir, dataset)
        for _ in range(3)
    ]
    set_active_index(index_entries[0].name, out_dir, dataset, is_admin=True)
    index_entries.append(
        create_index_version(dataset_entry.name, embedding_entry.name, out_dir, dataset)
    )

    versions = list_versions("index", out_dir, dataset)
    assert len(versions) == 3
    assert index_entries[0].name in {version.name for version in versions}


def test_ingestion_creates_version_entries(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "out"
    dataset = "demo"

    pdf_path = input_dir / "sample.pdf"
    _write_pdf(pdf_path, "Hello version registry")

    ingest_dataset(input_dir, dataset, output_dir)

    dataset_versions = list_versions("dataset", output_dir, dataset)
    embedding_versions = list_versions("embedding", output_dir, dataset)
    index_versions = list_versions("index", output_dir, dataset)

    assert len(dataset_versions) == 1
    assert len(embedding_versions) == 1
    assert len(index_versions) == 1
