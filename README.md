# The Machinery Changed. The Discipline Didn't.

Demo code for the talk at **Women In Data™ Toronto Chapter**, October 2026.

**Prashanth Soma** · Senior AI Architect · [psomaus.com](https://psomaus.com) · [LinkedIn](https://linkedin.com/in/prashanthsoma)

---

## Talk summary

Data architecture has gone through five distinct eras in thirty years —
OLAP cubes, MPP appliances, data lakes, lakehouses, and agentic AI.
Every era solved a real constraint. Every era created a new one.
And underneath every era, one thing never changed: data has to be
defined, owned, and governed before any machine can reliably answer
a question with it.

**The machinery changed. The discipline didn't.**
> *"The star schema in 2003 required someone to define 'revenue' before the cube could calculate it. The ontology in 2025 requires someone to define 'diabetes' before the agent can query it. Same discipline. Different machinery."*

> **Note:** This repo is a talk companion — shared for reference and learning. It is not actively maintained and issues are not monitored.
---

## Repo structure

```
data-architecture-talk/
├── README.md
├── RUNBOOK.md               ← complete setup and run instructions
├── pyproject.toml           ← uv project (Python 3.11+)
│
├── deck/
│   └── the-machinery-changed.pdf    
│
├── ontology-demo/
│   ├── clinical_ontology.owl        ← open in [Protégé](https://protege.stanford.edu/)
│   ├── ontology_lookup.py           ← standalone term-to-code resolver
│   └── mcp_ontology_tool.py         ← MCP tool with docstring
│
└── nl2sql-stub/
    ├── .env.example                 ← copy to .env, edit if needed
    ├── config.py                    ← loads .env, DB config, schema context
    ├── schema_context.txt           ← data dictionary the LLM reads
    ├── db.py                        ← Postgres connection and execution
    ├── llm.py                       ← SQL generation and judge validation
    ├── agent.py                     ← three-step orchestrator — generation, validation, execution 
    ├── demo.py                      ← entry point: uv run python nl2sql-stub/demo.py
    ├── schema.sql                   ← Pagila schema subset + sample data
    └── sample_queries.md            ← demo questions and talking points
```

---

## Quick start

```bash
git clone https://github.com/psoma01/data-architecture-talk.git
cd data-architecture-talk

# Install dependencies
uv sync

# Copy config (defaults work on macOS without changes)
cp nl2sql-stub/.env.example nl2sql-stub/.env

# Ontology demo — no extra dependencies needed
uv run python ontology-demo/ontology_lookup.py "diabetes"
uv run python ontology-demo/mcp_ontology_tool.py

# NL2SQL agent — requires Ollama + Postgres (see RUNBOOK.md)
uv run python nl2sql-stub/demo.py
```

See **[RUNBOOK.md](RUNBOOK.md)** for full prerequisites and setup.

---

## The ontology demo

Shows how an agent resolves a plain-English clinical term to structured
medical codes before generating SQL — using a local OWL ontology,
zero cloud dependencies, and the same pattern as the MCP tool docstrings.

```bash
uv run python ontology-demo/ontology_lookup.py "high blood pressure"
```

```
  Resolving: "high blood pressure"
  ────────────────────────────────────────────────────────────

  ✓ Hypertension  (confidence: 90%)
    ICD-10:  I10
    SNOMED:  38341003
    Synonyms: HTN, arterial hypertension

  Agent payload:
  { "resolved_label": "Hypertension", "icd10_codes": ["I10"], ... }
```

Open `clinical_ontology.owl` in [Protégé](https://protege.stanford.edu)
to see the full concept hierarchy.

---

## The NL2SQL agent

A modular three-step agent loop running entirely on your local machine:

```
demo.py          ← run this
  └── agent.py   ← orchestrates the three steps
        ├── llm.py → Step 1: generate_sql()    — LLM writes a SELECT
        ├── llm.py → Step 2: judge_validate()  — second LLM checks it
        └── db.py  → Step 3: execute_select()  — runs only if Step 2 passes
```

```bash
uv run python nl2sql-stub/demo.py
uv run python nl2sql-stub/demo.py "show me all films rated PG"
```

**No cloud. No API key. No vendor subscription.**

---

## Key finding this demo is built around

**Spider 2.0** (ICLR 2025): the best AI agent solved only **21.3%** of
real enterprise NL2SQL tasks — vs 91.2% on simple benchmarks.

The gap is not the model. The gap is the data underneath.

→ [arxiv.org/abs/2411.07763](https://arxiv.org/abs/2411.07763)

---

## Tech stack

| Layer | Tool |
|-------|------|
| Local LLM | [Ollama](https://ollama.com) + llama3.2 |
| Database | PostgreSQL + Pagila schema |
| Ontology editor | [Protégé](https://protege.stanford.edu) 5.6 |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| Python | 3.11+ |

---

## License

MIT — use freely, attribution appreciated.
