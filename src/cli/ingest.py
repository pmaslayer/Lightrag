from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ingestion.constants import CLI_COMMAND, EXECUTION_ENVIRONMENT, SYSTEM_DEPENDENCIES
from ingestion.pipeline import IngestionError, ingest_dataset


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ingest",
        description="Ingest PDF files into a deterministic manifest.",
        epilog=_build_epilog(),
    )
    parser.add_argument("--input", required=True, help="Path to a PDF file or directory.")
    parser.add_argument("--dataset", required=True, help="Dataset name.")
    parser.add_argument("--out", required=True, help="Output directory for manifests.")
    args = parser.parse_args()

    input_path = Path(args.input)
    out_dir = Path(args.out)

    try:
        ingest_dataset(input_path=input_path, dataset=args.dataset, out_dir=out_dir)
    except IngestionError as exc:
        _print_error(str(exc), exc.errors)
        sys.exit(2)
    except Exception as exc:  # pragma: no cover - safety net
        _print_error("Unexpected ingestion error.", [str(exc)])
        sys.exit(2)


def _print_error(message: str, details: list[str]) -> None:
    sys.stderr.write(f"{message}\n")
    if details:
        sys.stderr.write("Details:\n")
        for item in details:
            sys.stderr.write(f"- {item}\n")


def _build_epilog() -> str:
    deps = "; ".join(f"{key}: {value}" for key, value in SYSTEM_DEPENDENCIES.items())
    return (
        f"Environment: {EXECUTION_ENVIRONMENT}. "
        f"System deps: {deps}. "
        f"Command: {CLI_COMMAND}."
    )
