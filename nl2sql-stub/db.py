"""
db.py — Database connection and execution
==========================================
Single responsibility: talk to Postgres.

  preflight_check() — verify the database is reachable at startup
  execute_select()  — run a validated SELECT and return rows
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional

from config import DB_CONFIG


def preflight_check() -> bool:
    """
    Verify Postgres is reachable and the pagila_demo schema is loaded.
    Prints a clear fix message if the check fails.
    Returns True if ready, False otherwise.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM customer;")
            count = cur.fetchone()[0]
        conn.close()
        print(f"  ✓ Postgres: pagila_demo ready ({count} customers)")
        return True
    except psycopg2.OperationalError as e:
        print(f"  ✗ Postgres: {e}")
        print( "    Fix: createdb pagila_demo && psql pagila_demo < nl2sql-stub/schema.sql")
        return False


def execute_select(sql: str) -> tuple[list[dict], Optional[str]]:
    """
    Execute a validated SELECT statement against Postgres.
    Returns (rows, error) — error is None on success.

    Only SELECT statements are accepted.
    The agent cannot mutate data through this function.
    """
    if not sql.strip().upper().startswith("SELECT"):
        return [], "Only SELECT statements are permitted."

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            rows = [dict(row) for row in cur.fetchmany(20)]
        conn.close()
        return rows, None
    except psycopg2.Error as e:
        return [], f"SQL error: {e}"
