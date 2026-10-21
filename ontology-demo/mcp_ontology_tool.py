"""
MCP Ontology Tool — Clinical Concept Resolution
================================================
An MCP-compatible tool that resolves plain-English clinical
terms to structured medical codes using a local OWL ontology.

This file demonstrates how a docstring becomes the agent's
reasoning instruction — the agent reads the docstring to
understand WHEN to call this tool and WHAT to pass to it.

To register with your MCP server, import resolve_clinical_term
and register it as a tool in your server's tool list.

Demo context: Women In Data Toronto 2026
Author: Prashanth Soma — psomaus.com
"""

import json
from pathlib import Path

# ── Import the core lookup logic from ontology_lookup.py ────────────────────
import sys
sys.path.insert(0, str(Path(__file__).parent))
from ontology_lookup import load_ontology_raw, resolve_term

# Load ontology once at module level — not on every call
_OWL_PATH = Path(__file__).parent / "clinical_ontology.owl"
_CONCEPTS  = load_ontology_raw(str(_OWL_PATH)) if _OWL_PATH.exists() else []


# ── MCP Tool Definition ──────────────────────────────────────────────────────

def resolve_clinical_term(plain_english_term: str) -> dict:
    """
    Resolve a plain-English clinical term to structured medical codes.

    Use this tool BEFORE generating any SQL query that involves a
    medical condition, disease, diagnosis, or symptom. This ensures
    the query uses the correct ICD-10 codes rather than guessing from
    free-text column values.

    When to call this tool:
    - The user's question mentions a disease, condition, or symptom
      (e.g. "patients with diabetes", "members diagnosed with CHF",
      "beneficiaries with high blood pressure")
    - You need to filter a clinical database by diagnosis or condition
    - You are unsure which ICD-10 code family applies to a term

    Args:
        plain_english_term (str):
            The condition or disease as the user stated it — do not
            translate or normalise before passing. Examples:
            "diabetes", "high blood pressure", "heart failure", "CHF",
            "Type 2 diabetes", "COPD", "depression"

    Returns:
        dict with keys:
            query           (str)  — the original term you passed in
            resolved_label  (str)  — preferred clinical label
            icd10_codes     (list) — ICD-10 code(s) to use in SQL WHERE clause
            icd9_codes      (list) — ICD-9 codes if available
            snomed_codes    (list) — SNOMED CT codes if available
            synonyms        (list) — accepted alternative names
            confidence      (int)  — match confidence 0–100
            parent_concept  (str)  — where this fits in the hierarchy
            not_found       (bool) — True if no match; ask the user to clarify

    Example:
        Input:  "diabetes"
        Output: {
            "query": "diabetes",
            "resolved_label": "Diabetes",
            "icd10_codes": ["E08-E13"],
            "confidence": 100,
            "parent_concept": "ChronicDisease",
            ...
        }

        Input:  "high blood pressure"
        Output: {
            "query": "high blood pressure",
            "resolved_label": "Hypertension",
            "icd10_codes": ["I10"],
            "snomed_codes": ["38341003"],
            "confidence": 90,
            ...
        }

    Important:
        If not_found is True, do NOT guess an ICD-10 code. Instead,
        ask the user to clarify the condition before generating SQL.
        A wrong code silently returns wrong patients — there is no
        error, only a bad answer that sounds correct.
    """
    if not _CONCEPTS:
        return {
            "query":          plain_english_term,
            "error":          "Ontology file not loaded. Check that clinical_ontology.owl exists.",
            "not_found":      True,
        }

    matches = resolve_term(plain_english_term, _CONCEPTS)

    if not matches:
        return {
            "query":          plain_english_term,
            "resolved_label": None,
            "icd10_codes":    [],
            "icd9_codes":     [],
            "snomed_codes":   [],
            "synonyms":       [],
            "confidence":     0,
            "parent_concept": None,
            "not_found":      True,
            "suggestion":     "Term not found in ontology. Ask the user to clarify or provide the ICD-10 code directly.",
        }

    top = matches[0]
    return {
        "query":          plain_english_term,
        "resolved_label": top["label"],
        "icd10_codes":    top["icd10"],
        "icd9_codes":     top["icd9"],
        "snomed_codes":   top["snomed"],
        "synonyms":       top["synonyms"],
        "confidence":     top["_score"],
        "parent_concept": top["parent"],
        "not_found":      False,
        "all_matches":    [
            {"label": m["label"], "icd10": m["icd10"], "confidence": m["_score"]}
            for m in matches
        ],
    }


# ── MCP Tool Registration Schema ─────────────────────────────────────────────
# This is the schema block you register with your MCP server.
# The description here IS the docstring the agent reads at runtime.

MCP_TOOL_SCHEMA = {
    "name": "resolve_clinical_term",
    "description": (
        "Resolve a plain-English clinical term to ICD-10 and SNOMED codes "
        "using a local ontology. Call this BEFORE generating SQL for any "
        "query that involves a medical condition, disease, or diagnosis. "
        "Returns structured codes, synonyms, and confidence score. "
        "If not_found is True, ask the user to clarify before proceeding."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "plain_english_term": {
                "type":        "string",
                "description": (
                    "The medical condition as the user stated it. "
                    "Do not translate before passing. "
                    "Examples: 'diabetes', 'CHF', 'high blood pressure', 'COPD'."
                ),
            }
        },
        "required": ["plain_english_term"],
    },
}


# ── Demo runner ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "═" * 64)
    print("  MCP Ontology Tool — Live Demo")
    print("  Women In Data Toronto 2026 · Prashanth Soma")
    print("═" * 64)

    print("\n  The agent sees this tool description at runtime:")
    print("  " + "─" * 60)
    print(f"  Tool name:  {MCP_TOOL_SCHEMA['name']}")
    print(f"  Description:\n  {MCP_TOOL_SCHEMA['description']}")
    print("  " + "─" * 60)

    print("\n  The agent reasons: 'The user asked about patients with")
    print("  diabetes. I must call resolve_clinical_term BEFORE")
    print("  generating SQL, or I will guess the wrong codes.'")
    print()

    # Simulate three agent tool calls
    demo_queries = [
        "diabetes",
        "high blood pressure",
        "chf",
    ]

    for query in demo_queries:
        print(f"\n  Agent calls: resolve_clinical_term('{query}')")
        result = resolve_clinical_term(query)
        print(f"  → resolved_label: {result['resolved_label']}")
        print(f"  → icd10_codes:    {result['icd10_codes']}")
        print(f"  → confidence:     {result['confidence']}%")
        print(f"  → not_found:      {result['not_found']}")

    print()
    print("  Now the agent generates SQL using I10, I50, E08-E13")
    print("  — not a free-text LIKE '%diabetes%' guess.")
    print()
    print("  This is the discipline the ontology provides.")
    print("  The same discipline the star schema required in 2003.")
    print("  The machinery changed. The discipline didn't.")
    print("\n" + "═" * 64 + "\n")
