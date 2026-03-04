from __future__ import annotations

from pathlib import Path

from ingestion.ingest import ingest_pdf


def test_ingest_pdf_smoke() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "sample.pdf"
    result = ingest_pdf(fixture_path)

    assert result["filename"] == "sample.pdf"
    assert result["size_bytes"] > 0
    assert len(result["sha256"]) == 64
