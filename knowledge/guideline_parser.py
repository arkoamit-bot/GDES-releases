"""Guideline parser — parse structured guidelines into KB rule candidates.

Supports multiple guideline formats:
- Markdown with structured headings
- Simple JSON rule definitions
- YAML rule definitions
- CSV rule tables
"""

from __future__ import annotations

import json
import re
from typing import Any

from .models import GuidelineDocument, GuidelineSource, KnowledgeBaseEntry

# Pattern for extracting rule candidates from markdown sections
RULE_BLOCK_PATTERN = re.compile(
    r"(?:^|\n)#{1,4}\s+(?:Recommendation|Rule|Criterion)\s*[#:. ]*([^\n]+)\n"
    r"(.*?)(?=\n#{1,4}\s+(?:Recommendation|Rule|Criterion)|\Z)",
    re.DOTALL | re.MULTILINE,
)

# Pattern for extracting recommendation strength indicators
STRENGTH_PATTERN = re.compile(
    r"(Level\s+|Grade\s+)?([12])([A-D]|Strong|Weak|Conditional)?",
    re.IGNORECASE,
)

FIELD_ALIASES = {
    "proteinuria": "proteinuria",
    "urine protein": "proteinuria",
    "spot upcr": "proteinuria",
    "24h protein": "proteinuria",
    "albumin": "albumin",
    "serum albumin": "albumin",
    "egfr": "latest_egfr",
    "gfr": "latest_egfr",
    "creatinine": "latest_egfr",
    "c3": "labs",
    "c4": "labs",
    "ana": "labs",
    "dsdna": "labs",
    "anti-dsdna": "labs",
    "anca": "labs",
    "anti-gbm": "labs",
    "pla2r": "labs",
    "hepatitis": "labs",
    "hbsag": "labs",
    "hcv": "labs",
    "hiv": "labs",
    "edema": "features",
    "hypertension": "features",
    "hematuria": "features",
    "gross hematuria": "features",
    "purpura": "features",
    "arthritis": "features",
    "rash": "features",
}


def parse_markdown_guideline(doc: GuidelineDocument) -> list[dict]:
    """Parse a markdown guideline document into rule candidates.

    Returns a list of candidate dicts::
        {
            "disease_id": str,
            "conditions": [{"field": ..., "operator": ..., "value": ...}],
            "weight": int,
            "explanation": str,
            "evidence_grade": str,
            "guideline_chapter": str,
        }
    """
    content = doc.content
    candidates = []

    for match in RULE_BLOCK_PATTERN.finditer(content):
        title = match.group(1).strip()
        body = match.group(2).strip()
        candidate = _parse_rule_block(title, body, doc)
        if candidate:
            candidates.append(candidate)

    return candidates


def _parse_rule_block(title: str, body: str, doc: GuidelineDocument) -> dict | None:
    """Parse a single rule block from markdown content."""
    candidate: dict[str, Any] = {
        "disease_id": _guess_disease(title),
        "conditions": [],
        "weight": 1,
        "explanation": title,
        "evidence_grade": "NG",
        "guideline_chapter": title,
        "guideline_paragraph": "",
        "guideline_quote": body[:500] if body else title,
    }

    # Extract recommendation strength
    strength_match = STRENGTH_PATTERN.search(body)
    if strength_match:
        grade = strength_match.group(2)
        if grade in ("1", "2"):
            candidate["evidence_grade"] = grade

    # Extract conditions from structured lists
    for line in body.split("\n"):
        line = line.strip()
        condition = _parse_condition_line(line)
        if condition:
            candidate["conditions"].append(condition)

    if not candidate["conditions"]:
        # Fallback: use the title as a simple condition
        candidate["conditions"].append({
            "field": "features",
            "operator": "eq",
            "value": title.lower().replace(" ", "_"),
        })

    return candidate


def _parse_condition_line(line: str) -> dict | None:
    """Parse a single line into a condition if it matches expected patterns."""
    line_lower = line.lower().strip("-* \t")

    # Pattern: "If/When [field] is [operator] [value]"
    if_match = re.match(
        r"(?:if|when|has|with)\s+(.+?)\s+(?:is|has|are|>|<|>=|<=|contains?)\s+(.+)",
        line_lower,
    )
    if if_match:
        raw_field = if_match.group(1).strip()
        raw_value = if_match.group(2).strip()
        field = FIELD_ALIASES.get(raw_field, raw_field)
        operator = _infer_operator(raw_value)
        value = _infer_value(raw_value)
        return {"field": field, "operator": operator, "value": value}

    # Pattern: "[field] > [value]" or "[field] >= [value]"
    cmp_match = re.match(r"(.+?)\s*(>=\?|<=?|>|<)\s*([\d.]+)", line_lower)
    if cmp_match:
        raw_field = cmp_match.group(1).strip()
        op = cmp_match.group(2)
        val = float(cmp_match.group(3))
        field = FIELD_ALIASES.get(raw_field, raw_field)
        op_map = {">": "gt", ">=": "gte", "<": "lt", "<=": "lte"}
        return {"field": field, "operator": op_map.get(op, "eq"), "value": val}

    return None


def _infer_operator(value_str: str) -> str:
    """Infer the operator from a value string."""
    if value_str.startswith(">="):
        return "gte"
    if value_str.startswith(">"):
        return "gt"
    if value_str.startswith("<="):
        return "lte"
    if value_str.startswith("<"):
        return "lt"
    if value_str in ("present", "positive", "yes", "true"):
        return "exists"
    if value_str in ("absent", "negative", "no", "false", "none"):
        return "not_exists"
    return "eq"


def _infer_value(value_str: str):
    """Parse a value string into an appropriate Python type."""
    cleaned = value_str.strip("<>!= \t")
    try:
        return int(cleaned)
    except ValueError:
        pass
    try:
        return float(cleaned)
    except ValueError:
        pass
    return cleaned.strip('"')


def _guess_disease(title: str) -> str:
    """Guess the disease_id from a rule title."""
    title_lower = title.lower()
    disease_map = {
        "iga": ["iga", "iga nephropathy", "igav", "henoch", "schonlein"],
        "membranous": ["membranous", "mn"],
        "mcd": ["minimal change", "mcd", "lipoid"],
        "fsgs": ["fsgs", "focal segmental"],
        "lupus": ["lupus", "sle", "systemic lupus"],
        "anca": ["anca", "vasculitis", "gpa", "mpa", "granulomatosis"],
        "antiGbm": ["anti-gbm", "goodpasture"],
        "c3": ["c3 glomerulopathy", "c3g", "dd"],
        "diabeticNephropathy": ["diabetic", "dkd"],
        "hypertensiveNephrosclerosis": ["hypertensive", "hns"],
        "acuteInterstitialNephritis": ["interstitial nephritis", "ain"],
        "acuteTubularNecrosis": ["tubular necrosis", "atn", "acute tubular"],
        "thromboticMicroangiopathy": ["tma", "thrombotic microangiopathy", "hus", "ttp"],
        "amyloidosis": ["amyloid", "amyloidosis"],
        "infectionRelated": ["infection", "post-infectious", "postinfectious",
                            "psgn", "infection-related"],
    }
    for disease_id, keywords in disease_map.items():
        for kw in keywords:
            if kw in title_lower:
                return disease_id
    return "unknown"


def parse_json_rules(data: list[dict]) -> list[dict]:
    """Parse a JSON array of rule definitions into KB-ready rule dicts.

    Expected input format per item::
        {
            "disease_id": "iga",
            "entry_id": "KB-IGA-020",
            "conditions": [{"field": "...", "operator": "...", "value": ...}],
            "weight": 2,
            "explanation": "...",
            "evidence_grade": "1",
            "source_abbreviation": "KDIGO",
            "source_year": 2025,
        }
    """
    candidates = []
    for item in data:
        if not isinstance(item, dict):
            continue
        candidate = {
            "disease_id": item.get("disease_id", "unknown"),
            "conditions": item.get("conditions", []),
            "weight": item.get("weight", 1),
            "explanation": item.get("explanation", ""),
            "evidence_grade": item.get("evidence_grade", "NG"),
            "entry_id": item.get("entry_id", ""),
            "source_abbreviation": item.get("source_abbreviation", ""),
            "source_year": item.get("source_year", 0),
            "guideline_chapter": item.get("guideline_chapter", ""),
            "guideline_paragraph": item.get("guideline_paragraph", ""),
            "guideline_quote": item.get("guideline_quote", ""),
        }
        candidates.append(candidate)
    return candidates
