# Runbook — Data Architecture Talk Demo

Complete setup and run instructions using `uv`.

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.11+ | python.org |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Ollama | latest | ollama.com |
| PostgreSQL | 14+ | postgresql.org or `brew install postgresql` |
| Protégé | 5.6+ | protege.stanford.edu (needs Java 11+) |

---

## 1. Clone the repo

```bash
git clone https://github.com/psoma01/data-architecture-talk.git
cd data-architecture-talk
```

---

## 2. Set up Python environment with uv

```bash
uv sync

# Verify
uv run python --version
```

---

## 3. Configure environment

```bash
# Copy the example and edit if needed
cp nl2sql-stub/.env.example nl2sql-stub/.env
```

The defaults work on macOS without changes — `PGUSER` is empty, which
tells psycopg2 to use your OS username. Edit `.env` only if your
Postgres setup uses a different user or port.

---

## 4. Set up Ollama (local LLM)

```bash
# Install (macOS/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Pull 2 small language models for generation and LLM-as-Judge
ollama pull llama3.2 && ollama pull phi4-mini

# Start the server — keep this running in a separate terminal
ollama serve

# Verify
curl http://localhost:11434/api/tags
```

> Any model works. `llama3.2` is recommended for SQL generation quality
> on a laptop. `mistral` or `phi4` are good alternatives — update
> `OLLAMA_MODEL` in `.env` to match.

---

## 5. Set up PostgreSQL + Pagila schema

> Assumes PostgreSQL is already installed and running locally.
> Verify with: `psql --version`

```bash
# Connect to confirm access
psql -d postgres -c "\conninfo"

# Create the demo database
createdb pagila_demo

# Load schema and sample data
psql pagila_demo < nl2sql-stub/schema.sql

# Verify
psql pagila_demo -c "SELECT COUNT(*) FROM customer;"
# Should return 10
```

---

## 6. Run the NL2SQL agent

```bash
# Run the default demo (2 questions, pre-flight checks run first)
uv run python nl2sql-stub/demo.py

# Custom question
uv run python nl2sql-stub/demo.py "which customers have not returned their films?"
```

Expected pre-flight output:
```
  Pre-flight checks:
  ────────────────────────────────────────
  ✓ Ollama: llama3.2 ready
  ✓ Postgres: pagila_demo ready (10 customers)
```

More demo questions in `nl2sql-stub/sample_queries.md`.

---

## 7. Run the ontology demo

```bash
# Standalone lookup — no extra dependencies needed
uv run python ontology-demo/ontology_lookup.py "diabetes"
uv run python ontology-demo/ontology_lookup.py "high blood pressure"
uv run python ontology-demo/ontology_lookup.py "chf"

# MCP tool demo — shows docstring as agent instruction
uv run python ontology-demo/mcp_ontology_tool.py
```

---

## 8. Open the ontology in Protégé

1. Download Protégé from https://protege.stanford.edu
2. Open Protégé → **File → Open** → select `ontology-demo/clinical_ontology.owl`
3. Click the **Classes** tab
4. Navigate: `Thing → Disease → ChronicDisease → DiabetesType2`
5. In the **Annotations** panel show `icd10Code: E11`, `synonym: T2DM`

---

## 9. Troubleshooting

**Ollama not reachable**
```bash
curl http://localhost:11434/api/tags   # check if running
ollama serve                            # start if not
```

**Model not found**
```bash
ollama list                 # see what is pulled
ollama pull llama3.2        # pull if missing
ollama pull phi4-mini:latest
```

**Postgres role does not exist**
```bash
# macOS — use your OS username, not "postgres"
# Leave PGUSER empty in .env (the default)
psql pagila_demo -c "\conninfo"   # verify which user connects
```

**pagila_demo database not found**
```bash
createdb pagila_demo
psql pagila_demo < nl2sql-stub/schema.sql
```

**uv not found**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc   # or restart terminal
```

---

## Demo sequence (50 minutes)

| Time | What | File / Tool |
|------|------|-------------|
| 0–3 min | Thesis and agenda | Deck |
| 3–15 min | Five eras walk | Deck |
| 15–17 min | Parquet in DBeaver | DBeaver + any .parquet file |
| 17–21 min | MCP docstrings | `llm.py` — point to `generate_sql()` docstring |
| 21–25 min | Ontology — Protégé + lookup | Protégé + terminal |
| 25–33 min | NL2SQL agent | `agent.py` open in editor, `demo.py` in terminal |
| 33–38 min | Thesis and close | Deck |
| 38–50 min | Q&A | References slide on screen |

### Files to have open before you go on stage

```
editor tab 1  →  nl2sql-stub/agent.py          (the chain — show this first)
editor tab 2  →  nl2sql-stub/llm.py            (docstrings — MCP moment)
editor tab 3  →  nl2sql-stub/schema_context.txt (the data dictionary)
editor tab 4  →  ontology-demo/mcp_ontology_tool.py
terminal 1    →  ollama serve
terminal 2    →  ready for: uv run python nl2sql-stub/demo.py
Protégé       →  clinical_ontology.owl loaded, DiabetesType2 selected
```
