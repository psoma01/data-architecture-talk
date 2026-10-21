"""
agent.py — The three-step agent loop
======================================
Orchestrates SQL generation → judge validation → execution.
This is the file to show during the demo — the full chain in 40 lines.
"""

from dataclasses import dataclass, field
from typing import Optional

from llm import generate_sql, judge_validate
from db import execute_select


@dataclass
class AgentResult:
    question:  str
    sql:       str       = ""
    rows:      list[dict] = field(default_factory=list)
    validated: bool      = False
    error:     Optional[str] = None


def run(question: str, verbose: bool = True) -> AgentResult:
    """
    Run the full NL2SQL agent loop for a plain-English question.

      Step 1 — generate_sql()    : LLM writes a SELECT from the question
      Step 2 — judge_validate()  : second LLM call checks it before execution
      Step 3 — execute_select()  : runs against Postgres only if Step 2 passes

    The agent never executes SQL that fails validation.
    That is the discipline. Same discipline as every prior era.
    Different machinery.
    """
    result = AgentResult(question=question)

    if verbose:
        print(f"\n{'═' * 64}")
        print(f"  Question: {question}")
        print(f"{'═' * 64}")

    # ── Step 1: Generate ──────────────────────────────────────────────
    if verbose: print("\n  [1/3] Generating SQL...")
    sql, ok = generate_sql(question)
    result.sql = sql
    if verbose: print(f"  → {sql[:200]}")

    if not ok:
        result.error = f"Generation failed: {sql}"
        if verbose: print(f"\n  ✗ {result.error}")
        return result

    # ── Step 2: Validate ──────────────────────────────────────────────
    if verbose: print("\n  [2/3] Validating with judge model...")
    verdict, passed = judge_validate(question, sql)
    result.validated = passed
    if verbose:
        print(f"  → {'✓ PASS' if passed else '✗ FAIL'}: {verdict}")

    if not passed:
        result.error = f"Validation failed: {verdict}"
        if verbose: print("\n  Agent: SQL did not pass validation. Not executing.")
        return result

    # ── Step 3: Execute ───────────────────────────────────────────────
    if verbose: print("\n  [3/3] Executing against Postgres...")
    rows, err = execute_select(sql)
    result.rows = rows

    if err:
        result.error = err
        if verbose: print(f"\n  ✗ {err}")
        return result

    if verbose:
        print(f"\n  ✓ {len(rows)} row(s) returned")
        _print_table(rows)

    return result


def _print_table(rows: list[dict]) -> None:
    if not rows:
        return
    headers = list(rows[0].keys())
    col_w   = {h: max(len(h), max(len(str(r[h])) for r in rows)) for h in headers}
    bar     = "  │ " + " │ ".join(h.ljust(col_w[h]) for h in headers) + " │"
    sep     = "  ├─" + "─┼─".join("─" * col_w[h] for h in headers) + "─┤"
    print(f"\n  {'─' * (len(bar) - 2)}")
    print(bar)
    print(sep)
    for row in rows:
        print("  │ " + " │ ".join(str(row[h]).ljust(col_w[h]) for h in headers) + " │")
    print(f"  {'─' * (len(bar) - 2)}")
