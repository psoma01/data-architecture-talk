"""
llm.py — LLM calls: SQL generation and judge validation
=========================================================
Single responsibility: talk to Ollama.

  ollama_complete()  — raw completion call
  generate_sql()     — Step 1: plain English → SQL
  judge_validate()   — Step 2: validate SQL before execution
"""

import re
import textwrap

import httpx

from config import OLLAMA_BASE_URL, OLLAMA_MODEL, JUDGE_MODEL, SCHEMA_CONTEXT


def ollama_complete(prompt: str, model: str, system: str = "") -> str:
    """
    Send a prompt to the locally running Ollama instance.
    Raises RuntimeError if Ollama is not reachable.
    """
    payload = {"model": model, "prompt": prompt, "stream": False}
    if system:
        payload["system"] = system

    try:
        r = httpx.post(f"{OLLAMA_BASE_URL}/api/generate",
                       json=payload, timeout=60.0)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except httpx.ConnectError:
        raise RuntimeError(
            f"Cannot reach Ollama at {OLLAMA_BASE_URL}.\n"
            f"Fix: ollama serve && ollama pull {model}"
        )


def preflight_check() -> bool:
    """
    Verify Ollama is reachable and the configured model is available.
    Prints a clear fix message if the check fails.
    Returns True if ready, False otherwise.
    """
    try:
        r = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5.0)
        models = [m["name"] for m in r.json().get("models", [])]
        if any(OLLAMA_MODEL in m for m in models):
            print(f"  ✓ Ollama: {OLLAMA_MODEL} ready")
            return True
        else:
            print(f"  ✗ Ollama: model '{OLLAMA_MODEL}' not found")
            print(f"    Available: {models or 'none pulled yet'}")
            print(f"    Fix: ollama pull {OLLAMA_MODEL}")
            return False
    except Exception:
        print(f"  ✗ Ollama: not reachable at {OLLAMA_BASE_URL}")
        print( "    Fix: ollama serve")
        return False


def generate_sql(question: str) -> tuple[str, bool]:
    """
    Step 1 — SQL Generation.

    Sends the plain-English question and schema context to the local LLM
    and asks for a single PostgreSQL SELECT statement in return.

    The prompt includes:
      - The full schema context from schema_context.txt
      - A strict system instruction to return SQL only — no prose, no markdown
      - The user's question

    In a production system this step first calls an ontology lookup tool
    (see ontology-demo/mcp_ontology_tool.py) when the question involves
    medical conditions, to resolve terms to ICD-10 codes before generating SQL.

    Returns (sql, is_valid_select).
    """
    system = textwrap.dedent("""
        You are a SQL expert. You generate PostgreSQL SELECT statements.
        Respond ONLY with a single SQL query — no explanation, no markdown,
        no backticks. Just raw SQL ending with a semicolon.
        If you cannot generate valid SQL, respond with: ERROR: <reason>
    """).strip()

    prompt = f"Schema:\n{SCHEMA_CONTEXT}\n\nQuestion: {question}\n\nSQL:"

    raw  = ollama_complete(prompt, model=OLLAMA_MODEL, system=system)
    sql  = re.sub(r"```sql|```", "", raw).strip()
    ok   = sql.upper().startswith("SELECT") and not sql.upper().startswith("ERROR")
    return sql, ok


def judge_validate(question: str, sql: str) -> tuple[str, bool]:
    """
    Step 2 — LLM-as-Judge Validation.

    Sends the original question and generated SQL to a second LLM call
    that acts as an independent judge. The judge checks:
      - Does the SQL semantically answer the question?
      - Does it reference columns and tables that exist in the schema?
      - Would it return correct results?

    Style issues (formatting, aliasing preferences) are not grounds for FAIL.
    Only semantic errors or missing schema objects cause a FAIL.

    The agent does not execute SQL that fails this step.
    This is the hallucination mitigation layer.

    Returns (verdict_text, passed).
    """
    system = textwrap.dedent("""
        You are a SQL validator. Decide if the SQL correctly answers the question.
        Be lenient on style — only FAIL if the SQL is semantically wrong,
        references columns or tables that do not exist, or returns wrong results.
        Respond with exactly one of:
            PASS: <one-line reason>
            FAIL: <one-line reason>
        Nothing else.
    """).strip()

    prompt = (
        f"Schema:\n{SCHEMA_CONTEXT}\n\n"
        f"Question: {question}\n\n"
        f"SQL to validate:\n{sql}\n\n"
        f"Verdict:"
    )

    verdict = ollama_complete(prompt, model=JUDGE_MODEL, system=system)
    return verdict, verdict.upper().startswith("PASS")
