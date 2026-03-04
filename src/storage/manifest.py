from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

import orjson


def load_manifest(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = path.read_bytes()
    return json.loads(data)


def write_manifest_atomic(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = orjson.dumps(manifest, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS)
    with tempfile.NamedTemporaryFile(
        "wb",
        delete=False,
        dir=path.parent,
        prefix=f".{path.name}.",
    ) as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
        temp_path = Path(handle.name)
    temp_path.replace(path)
