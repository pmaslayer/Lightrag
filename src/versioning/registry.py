from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from storage.manifest import load_manifest

ACTIVE_INDEX_FILE = "active_index.json"


class VersioningError(RuntimeError):
    pass


@dataclass(frozen=True)
class VersionEntry:
    name: str
    created_at: str
    metadata: dict[str, Any]


def create_version_name(payload: dict[str, Any]) -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    payload_json = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    digest = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()[:8]
    return f"{timestamp}-{digest}"


def create_registry_entry(payload: dict[str, Any]) -> VersionEntry:
    created_at = datetime.now(UTC).isoformat()
    name = create_version_name({"created_at": created_at, **payload})
    return VersionEntry(name=name, created_at=created_at, metadata=payload)


def list_versions(kind: str, out_dir: Path, dataset: str) -> list[VersionEntry]:
    registry = _load_registry(kind, out_dir, dataset)
    return [VersionEntry(**entry) for entry in registry.get("versions", [])]


def _load_registry(kind: str, out_dir: Path, dataset: str) -> dict[str, Any]:
    path = _registry_path(kind, out_dir, dataset)
    return load_manifest(path) or {"kind": kind, "versions": []}


def _registry_path(kind: str, out_dir: Path, dataset: str) -> Path:
    return _kind_dir(kind, out_dir, dataset) / "registry.json"


def _version_manifest_path(kind: str, name: str, out_dir: Path, dataset: str) -> Path:
    return _version_dir(kind, name, out_dir, dataset) / "manifest.json"


def _version_dir(kind: str, name: str, out_dir: Path, dataset: str) -> Path:
    return _kind_dir(kind, out_dir, dataset) / name


def _kind_dir(kind: str, out_dir: Path, dataset: str) -> Path:
    return _versions_root(out_dir, dataset) / kind


def _versions_root(out_dir: Path, dataset: str) -> Path:
    return out_dir / dataset / "versions"


def _active_index_path(out_dir: Path, dataset: str) -> Path:
    return out_dir / dataset / ACTIVE_INDEX_FILE


def get_active_index(out_dir: Path, dataset: str) -> dict[str, Any]:
    path = _active_index_path(out_dir, dataset)
    return load_manifest(path) or {"active_index": None, "history": [], "updated_at": None}
