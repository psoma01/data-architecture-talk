"""
demo.py — Entry point for the live demo
=========================================
Run this file to start the agent.

    uv run python nl2sql-stub/demo.py
    uv run python nl2sql-stub/demo.py "show me all films rated PG"

Pre-flight checks run first — the demo exits cleanly if
Ollama or Postgres is not ready.
"""

import sys

import llm
import db
from agent import run

# ── Demo questions ────────────────────────────────────────────────────────────
# These are chosen to produce clean, reliable SQL from llama3.2.
# Each maps directly to one view or one simple table query.
# Avoid questions that could tempt the model to re-aggregate a view.

DEMO_QUESTIONS = [
    # Uses active_rentals view — simple WHERE on return_date
    "Which customers currently have films that are not yet returned?",
    # Uses customer_spend view — simple ORDER BY + LIMIT, no aggregation needed
    "Show me the top 3 customers ranked by total spent.",
    # Simple table scan with WHERE
    "Show me all films rated PG.",
    # Uses active_rentals view — filter by category column
    "Which films in the Drama category are currently rented out?",
]

if __name__ == "__main__":
    print("\n" + "═" * 64)
    print("  NL2SQL Agent — Local Demo")
    print("  Plain English → SQL generation → Judge validation → Postgres")
    print("═" * 64)

    # Pre-flight
    print("\n  Pre-flight checks:")
    print("  " + "─" * 40)
    ready = llm.preflight_check() and db.preflight_check()
    if not ready:
        print("\n  Fix the above before running the demo.\n")
        sys.exit(1)
    print()

    # Questions — CLI arg or first two demo questions
    questions = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else DEMO_QUESTIONS[:2]

    for q in questions:
        result = run(q, verbose=True)
        if result.error:
            print(f"\n  Error: {result.error}")
        print()

    print("  Try your own question:")
    print('  uv run python nl2sql-stub/demo.py "show me all films rated PG"\n')