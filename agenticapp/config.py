"""Shared configuration for the logging-guidelines RAG project."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(
    os.getenv("LOGGING_GUIDELINES_DATA_DIR", str(PROJECT_ROOT / "data"))
).expanduser()

FINAL_RESULT_XLSX = DATA_DIR / "5.Final Result.xlsx"
CONSOLIDATED_48_XLSX = (
    DATA_DIR / "4.8.logging_guidelines_consolidated_with_codebook_corrected_VALIDATION.xlsx"
)
LITERATURE_XLSX = DATA_DIR / "1.LiteraturePhase1.1.xlsx"
# Source-level occurrences, superseded by the consolidated catalogue above.
OCCURRENCES_XLSX = (
    DATA_DIR
    / "4.9.logging_guidelines_with_themes_and_inductive_review_VALIDATION_VALIDATION.xlsx"
)

CHROMA_PATH = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "logging_guidelines"

# Override with OLLAMA_MODEL when switching between locally installed models.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:1b")
OLLAMA_THINK = os.getenv("OLLAMA_THINK", "false").lower() == "true"
# num_predict covers thinking + answer tokens, so it needs generous headroom.
OLLAMA_OPTIONS = {"temperature": 0.2, "num_predict": 6144}

DEFAULT_N_RESULTS = 8

API_HOST = "127.0.0.1"
API_PORT = 8000
