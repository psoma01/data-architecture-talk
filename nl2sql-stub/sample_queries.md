# Sample Queries — NL2SQL Demo

These plain-English questions work well, for a local machine execution.
Paste any of them at the prompt or pass as a CLI argument.

## Good demo queries (clear, unambiguous)

```
Which customers currently have films that are not yet returned?
```
```
What are the top 3 customers by total amount spent?
```
```
How many films are in each category?
```
```
Show me all active customers from Toronto.
```
```
Which films have never been rented?
```
```
What is the average rental rate by film rating?
```

## Queries that test the judge (may fail validation — good teaching moment)

```
Delete all customers who have never rented anything.
```
> Agent should refuse — not a SELECT statement.

```
Show me the secret films.
```
> Agent should fail validation — "secret" column does not exist.

## Running a specific query

```bash
uv run python nl2sql-stub/demo.py  "show me all films rated PG"
uv run python nl2sql-stub/demo.py  "which customers spent more than 5 dollars"
uv run python nl2sql-stub/demo.py  "how many active customers are there"
```

## What to check out during the execution

1. **Step 1 — SQL generation**: the LLM reads the schema context and
   writes a SELECT. Check the `SCHEMA_CONTEXT` constant in the `generate_sql()` docstring in `llm.py`.
   In production this is dynamically retrieved from a vector store.

2. **Step 2 — Judge validation**: a second LLM call checks the SQL
   before it touches the database. Watch `step_validate_sql()`.
   This is the hallucination mitigation layer.

3. **Step 3 — Execution**: only runs if Step 2 passes.
   The agent cannot mutate data — only SELECT is permitted.

4. **The docstrings**: every function has a docstring that explains
   *when* the agent calls it and *what it expects*. This is the same
   pattern as the ontology MCP tool. The docstring is the instruction.

5. **Query failures**: This is actually a great teaching moment — the judge rejected the SQL, which means the validation layer is working. In production this is where a human reviews and re-prompts.

> **Note:** there’s no guarantee with a local LLM. The model is non-deterministic. The same question can produce different SQL on different runs