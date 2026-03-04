from __future__ import annotations

import argparse
import json
from pathlib import Path

from versioning.registry import (
    VersioningError,
    get_active_index,
    list_versions,
    rollback_active_index,
    set_active_index,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="versioning",
        description="Manage dataset/index versions.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List versions by kind.")
    list_parser.add_argument("--dataset", required=True)
    list_parser.add_argument("--out", required=True)
    list_parser.add_argument("--kind", required=True, choices=["dataset", "embedding", "index"])

    switch_parser = subparsers.add_parser("switch", help="Switch active index version.")
    switch_parser.add_argument("--dataset", required=True)
    switch_parser.add_argument("--out", required=True)
    switch_parser.add_argument("--version", required=True)
    switch_parser.add_argument("--admin", action="store_true")

    rollback_parser = subparsers.add_parser("rollback", help="Rollback to previous index version.")
    rollback_parser.add_argument("--dataset", required=True)
    rollback_parser.add_argument("--out", required=True)
    rollback_parser.add_argument("--admin", action="store_true")

    args = parser.parse_args()
    out_dir = Path(args.out)

    try:
        if args.command == "list":
            entries = list_versions(args.kind, out_dir, args.dataset)
            payload = [entry.__dict__ for entry in entries]
            print(json.dumps(payload, indent=2))
            return
        if args.command == "switch":
            updated = set_active_index(
                index_version=args.version,
                out_dir=out_dir,
                dataset=args.dataset,
                is_admin=args.admin,
            )
            print(json.dumps(updated, indent=2))
            return
        if args.command == "rollback":
            updated = rollback_active_index(
                out_dir=out_dir,
                dataset=args.dataset,
                is_admin=args.admin,
            )
            print(json.dumps(updated, indent=2))
            return
    except VersioningError as exc:
        raise SystemExit(str(exc)) from exc

    active = get_active_index(out_dir, args.dataset)
    print(json.dumps(active, indent=2))


if __name__ == "__main__":
    main()
