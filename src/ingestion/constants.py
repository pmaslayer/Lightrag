"""Project-wide ingestion constants and environment decisions."""

INGESTION_VERSION = "0.1.0"

# System dependencies required for OCR best-effort flow.
SYSTEM_DEPENDENCIES = {
    "tesseract": "Tesseract OCR >= 5 (required for OCR of scanned PDFs)",
    "poppler": "Poppler utils (pdftoppm) for PDF to image conversion",
}

# Execution environment decision for this plan: local or server execution with
# system dependencies available on the host.
EXECUTION_ENVIRONMENT = "host-installed-deps"

# Canonical CLI command used in tests/CI.
CLI_COMMAND = "ingest --input <path> --dataset <name> --out <dir>"

# Placeholder embedding metadata captured during ingestion until embedding pipeline is implemented.
DEFAULT_EMBEDDING_MODEL = "pending"
DEFAULT_EMBEDDING_PARAMS = {"status": "not-configured"}
