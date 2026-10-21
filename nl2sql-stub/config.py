"""
config.py — Central configuration
===================================
Loads environment variables from .env and exposes
DB_CONFIG, Ollama settings, and the schema context.

All other modules import from here — nothing reads
os.getenv directly.
"""

import os
from pathlib import Path

# Load .env if python-dotenv is available; silently skip if not.
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

# ── Database ──────────────────────────────────────────────────────────────────
DB_CONFIG = {
    "dbname":   os.getenv("PGDATABASE", "pagila_demo"),
    "user":     os.getenv("PGUSER", ""),        # empty = OS username (macOS default)
    "password": os.getenv("PGPASSWORD", ""),
    "host":     os.getenv("PGHOST", "localhost"),
    "port":     int(os.getenv("PGPORT", "5432")),
}

# ── Ollama ────────────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL",   "phi4-mini:latest")
JUDGE_MODEL     = os.getenv("JUDGE_MODEL",    "llama3.2")

# ── Schema context ────────────────────────────────────────────────────────────
# Loaded once from schema_context.txt and reused across all LLM calls.
_schema_path = Path(__file__).parent / "schema_context.txt"
SCHEMA_CONTEXT = _schema_path.read_text() if _schema_path.exists() else ""
