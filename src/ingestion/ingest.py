from __future__ import annotations

from hashlib import sha256
from pathlib import Path


def ingest_pdf(path: str | Path) -> dict[str, str | int]:
    file_path = Path(path)
    data = file_path.read_bytes()
    return {
        "filename": file_path.name,
        "size_bytes": len(data),
        "sha256": sha256(data).hexdigest(),
    }
