"""
Clinical Ontology Lookup — Standalone Demo Script
===================================================
Parses clinical_ontology.owl and resolves plain-English
terms to structured medical codes (ICD-10, ICD-9, SNOMED).

Usage:
    python ontology_lookup.py "diabetes"
    python ontology_lookup.py "high blood pressure"
    python ontology_lookup.py "heart failure"

Requirements:
    pip install owlready2
"""

import sys
import json
from pathlib import Path


def load_ontology_raw(owl_path: str) -> list[dict]:
    """
    Parse the OWL file using basic XML parsing (no owlready2 needed for demo).
    Returns a list of concept dicts with all annotations.
    """
    import xml.etree.ElementTree as ET

    NS = {
        "owl":    "http://www.w3.org/2002/07/owl#",
        "rdf":    "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs":   "http://www.w3.org/2000/01/rdf-schema#",
        "skos":   "http://www.w3.org/2004/02/skos/core#",
        "clin":   "http://psomaus.com/ontology/clinical#",
    }

    tree = ET.parse(owl_path)
    root = tree.getroot()
    concepts = []

    for cls in root.findall("owl:Class", NS):
        uri = cls.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", "")
        if not uri:
            continue

        local_name = uri.split("#")[-1]
        label_el = cls.find("rdfs:label", NS)
        label = label_el.text if label_el is not None else local_name
        defn_el = cls.find("skos:definition", NS)
        definition = defn_el.text if defn_el is not None else ""

        parent_el = cls.find("rdfs:subClassOf", NS)
        parent_uri = parent_el.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource", "") if parent_el is not None else ""
        parent = parent_uri.split("#")[-1] if parent_uri else "Thing"

        # Collect all annotation values from the clin: namespace
        CLIN_NS = "http://psomaus.com/ontology/clinical#"
        annotations: dict[str, list[str]] = {}
        for child in cls:
            tag = child.tag
            if tag.startswith(f"{{{CLIN_NS}}}"):
                key = tag[len(f"{{{CLIN_NS}}}"):]
                annotations.setdefault(key, [])
                if child.text:
                    annotations[key].append(child.text.strip())

        concepts.append({
            "id":           local_name,
            "label":        label,
            "definition":   definition,
            "parent":       parent,
            "icd10":        annotations.get("icd10Code", []),
            "icd9":         annotations.get("icd9Code", []),
            "snomed":       annotations.get("snomedCode", []),
            "synonyms":     annotations.get("synonym", []),
            "plain_terms":  annotations.get("plainEnglishTerm", []),
            "clinical_note":annotations.get("clinicalNote", []),
        })

    return concepts


def resolve_term(query: str, concepts: list[dict]) -> list[dict]:
    """
    Match a plain-English query against concepts.
    Checks: preferred label, plain_terms, synonyms (case-insensitive).
    Returns a ranked list of matching concepts.
    """
    query_lower = query.lower().strip()
    matches = []

    for concept in concepts:
        score = 0

        # Exact label match — highest confidence
        if query_lower == concept["label"].lower():
            score = 100
        # Plain-English term match
        elif any(query_lower == t.lower() for t in concept["plain_terms"]):
            score = 90
        # Synonym match
        elif any(query_lower == s.lower() for s in concept["synonyms"]):
            score = 80
        # Partial label match
        elif query_lower in concept["label"].lower():
            score = 60
        # Partial plain-term match
        elif any(query_lower in t.lower() for t in concept["plain_terms"]):
            score = 50
        # Partial synonym match
        elif any(query_lower in s.lower() for s in concept["synonyms"]):
            score = 40

        if score > 0:
            matches.append({**concept, "_score": score})

    # Sort by score descending, then label alphabetically
    matches.sort(key=lambda x: (-x["_score"], x["label"]))
    return matches


def format_result(match: dict) -> str:
    """Format a single concept match for terminal display."""
    lines = [
        f"\n  ✓ {match['label']}  (confidence: {match['_score']}%)",
        f"    Parent: {match['parent']}",
    ]
    if match["icd10"]:
        lines.append(f"    ICD-10:  {', '.join(match['icd10'])}")
    if match["icd9"]:
        lines.append(f"    ICD-9:   {', '.join(match['icd9'])}")
    if match["snomed"]:
        lines.append(f"    SNOMED:  {', '.join(match['snomed'])}")
    if match["synonyms"]:
        lines.append(f"    Synonyms: {', '.join(match['synonyms'])}")
    if match["definition"]:
        lines.append(f"    Definition: {match['definition'][:120]}{'...' if len(match['definition']) > 120 else ''}")
    if match["clinical_note"]:
        lines.append(f"    Clinical note: {match['clinical_note'][0][:120]}")
    return "\n".join(lines)


def main():
    owl_path = Path(__file__).parent / "clinical_ontology.owl"

    if not owl_path.exists():
        print(f"ERROR: OWL file not found at {owl_path}")
        sys.exit(1)

    # Load and parse
    concepts = load_ontology_raw(str(owl_path))
    print(f"\n  Ontology loaded: {len(concepts)} concepts")

    # Get query from args or prompt
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        print("\n  Enter a plain-English clinical term to resolve.")
        print("  Examples: diabetes, high blood pressure, heart failure, copd\n")
        query = input("  > ").strip()

    if not query:
        print("  No query provided.")
        sys.exit(0)

    print(f"\n  Resolving: \"{query}\"")
    print("  " + "─" * 60)

    matches = resolve_term(query, concepts)

    if not matches:
        print(f"\n  No match found for \"{query}\".")
        print("  Try: diabetes, hypertension, heart failure, copd, depression")
    else:
        print(f"\n  Found {len(matches)} match(es):\n")
        for match in matches[:3]:  # Show top 3
            print(format_result(match))

    print("\n  " + "─" * 60)

    # Also output clean JSON for the agent demo
    if matches:
        top = matches[0]
        agent_payload = {
            "query":          query,
            "resolved_label": top["label"],
            "icd10_codes":    top["icd10"],
            "icd9_codes":     top["icd9"],
            "snomed_codes":   top["snomed"],
            "synonyms":       top["synonyms"],
            "confidence":     top["_score"],
            "parent_concept": top["parent"],
        }
        print("\n  Agent payload (JSON):")
        print("  " + json.dumps(agent_payload, indent=4).replace("\n", "\n  "))

    print()


if __name__ == "__main__":
    main()
