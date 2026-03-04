from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from storage.manifest import load_manifest, write_manifest_atomic

ACTIVE_INDEX_FILE = "active_index.json"
RETENTION_LIMIT = 3


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


def register_dataset_version(
    manifest: dict[str, Any],
    manifest_path: Path,
    out_dir: Path,
    dataset: str,
) -> VersionEntry:
    payload = {
        "dataset": dataset,
        "manifest_path": str(manifest_path),
        "ingestion_version": manifest.get("ingestion_version"),
        "doc_count": len(manifest.get("documents", [])),
        "chunk_count": len(manifest.get("chunks", [])),
    }
    entry = create_registry_entry(payload)
    _write_version_manifest(
        kind="dataset",
        entry=entry,
        out_dir=out_dir,
        dataset=dataset,
        manifest={"dataset_version": entry.name, **payload, "created_at": entry.created_at},
    )
    _append_registry_entry("dataset", entry, out_dir, dataset)
    apply_retention("dataset", out_dir, dataset)
    return entry


def create_embedding_version(
    model: str,
    parameters: dict[str, Any],
    out_dir: Path,
    dataset: str,
) -> VersionEntry:
    payload = {"model": model, "parameters": parameters}
    entry = create_registry_entry(payload)
    _write_version_manifest(
        kind="embedding",
        entry=entry,
        out_dir=out_dir,
        dataset=dataset,
        manifest={"embedding_version": entry.name, **payload, "created_at": entry.created_at},
    )
    _append_registry_entry("embedding", entry, out_dir, dataset)
    apply_retention("embedding", out_dir, dataset)
    return entry


def create_index_version(
    dataset_version: str,
    embedding_version: str,
    out_dir: Path,
    dataset: str,
) -> VersionEntry:
    payload = {
        "dataset_version": dataset_version,
        "embedding_version": embedding_version,
    }
    entry = create_registry_entry(payload)
    _write_version_manifest(
        kind="index",
        entry=entry,
        out_dir=out_dir,
        dataset=dataset,
        manifest={"index_version": entry.name, **payload, "created_at": entry.created_at},
    )
    _append_registry_entry("index", entry, out_dir, dataset)
    active_index = get_active_index(out_dir, dataset)
    apply_retention("index", out_dir, dataset, active_index=active_index.get("active_index"))
    return entry


def apply_retention(
    kind: str,
    out_dir: Path,
    dataset: str,
    active_index: str | None = None,
) -> None:
    registry = _load_registry(kind, out_dir, dataset)
    versions = registry.get("versions", [])
    if len(versions) <= RETENTION_LIMIT:
        return

    versions_sorted = sorted(versions, key=lambda entry: entry["created_at"])
    keep = versions_sorted[-RETENTION_LIMIT:]
    keep_names = {entry["name"] for entry in keep}

    if active_index and active_index not in keep_names:
        active_entry = next(
            (entry for entry in versions_sorted if entry["name"] == active_index), None
        )
        if active_entry:
            keep = keep[1:] + [active_entry]
            keep_names = {entry["name"] for entry in keep}

    to_remove = [entry for entry in versions_sorted if entry["name"] not in keep_names]
    for entry in to_remove:
        _delete_version(kind, entry["name"], out_dir, dataset)

    registry["versions"] = keep
    write_manifest_atomic(_registry_path(kind, out_dir, dataset), registry)


def _load_registry(kind: str, out_dir: Path, dataset: str) -> dict[str, Any]:
    path = _registry_path(kind, out_dir, dataset)
    return load_manifest(path) or {"kind": kind, "versions": []}


def _write_version_manifest(
    kind: str,
    entry: VersionEntry,
    out_dir: Path,
    dataset: str,
    manifest: dict[str, Any],
) -> None:
    path = _version_manifest_path(kind, entry.name, out_dir, dataset)
    write_manifest_atomic(path, manifest)


def _append_registry_entry(kind: str, entry: VersionEntry, out_dir: Path, dataset: str) -> None:
    registry = _load_registry(kind, out_dir, dataset)
    versions = registry.get("versions", [])
    versions.append(asdict(entry))
    registry["versions"] = versions
    write_manifest_atomic(_registry_path(kind, out_dir, dataset), registry)


def _delete_version(kind: str, name: str, out_dir: Path, dataset: str) -> None:
    version_dir = _version_dir(kind, name, out_dir, dataset)
    if not version_dir.exists():
        return
    for path in version_dir.rglob("*"):
        if path.is_file():
            path.unlink()
    for path in sorted(version_dir.rglob("*"), reverse=True):
        if path.is_dir():
            path.rmdir()
    version_dir.rmdir()


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


def set_active_index(
    index_version: str,
    out_dir: Path,
    dataset: str,
    is_admin: bool,
) -> dict[str, Any]:
    _ensure_admin(is_admin)
    if not _version_exists("index", index_version, out_dir, dataset):
        raise VersioningError(f"Index version '{index_version}' not found.")

    active_index = get_active_index(out_dir, dataset)
    history = list(active_index.get("history", []))
    current = active_index.get("active_index")
    if current and current != index_version:
        history.append(current)

    updated = {
        "active_index": index_version,
        "history": history,
        "updated_at": datetime.now(UTC).isoformat(),
    }
    write_manifest_atomic(_active_index_path(out_dir, dataset), updated)
    return updated


def rollback_active_index(out_dir: Path, dataset: str, is_admin: bool) -> dict[str, Any]:
    _ensure_admin(is_admin)
    active_index = get_active_index(out_dir, dataset)
    history = list(active_index.get("history", []))
    if not history:
        raise VersioningError("No previous index version available for rollback.")
    previous = history.pop()
    updated = {
        "active_index": previous,
        "history": history,
        "updated_at": datetime.now(UTC).isoformat(),
    }
    write_manifest_atomic(_active_index_path(out_dir, dataset), updated)
    return updated


def _version_exists(kind: str, name: str, out_dir: Path, dataset: str) -> bool:
    return _version_manifest_path(kind, name, out_dir, dataset).exists()


def _ensure_admin(is_admin: bool) -> None:
    if not is_admin:
        raise VersioningError("Admin privileges required for version switch/rollback.")
