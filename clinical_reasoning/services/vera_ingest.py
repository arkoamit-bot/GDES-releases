"""Parse a Vera Health response into structured, plan-ready recommendations.

Why this exists
---------------
"Request Prescription from Vera" asks for `Drug:` / `Dose:` / `Duration:` blocks,
but Vera answers in **markdown** -- `**Drug:** Prednisolone`, `### 1. Tacrolimus`,
`- **Dose:** 1 mg/kg/day`. The original parser only matched a bare `Drug:` at the
start of a line, so almost every real response fell into the "unstructured"
bucket and was stored as one opaque blob of text -- unusable for anything.

This module reads the markdown the way a clinician does: it tracks which section
it is in (first-line / second-line / rescue / contraindicated / monitoring /
counselling ...) and emits records shaped like the entries in
DISEASE_TREATMENT_PROFILES, so a saved recommendation can be merged straight
into a future Personalized Management Plan.

Safety
------
Parsing is deliberately conservative: anything it cannot confidently interpret
is preserved verbatim in `unparsed` rather than guessed at. Nothing here decides
whether a recommendation is *used* -- entries are saved as drafts and only a
clinician-approved (active) entry ever reaches a management plan.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# --- Section detection ----------------------------------------------------- #
# Ordered: the first pattern that matches a heading wins.
SECTION_PATTERNS: list[tuple[str, str]] = [
    ("first_line", r"first[\s-]*line|initial therapy|induction"),
    ("second_line", r"second[\s-]*line|alternative therapy|if refractory"),
    ("rescue", r"rescue|salvage|third[\s-]*line|refractory"),
    ("contraindicated", r"contraindicat|avoid|do not use"),
    ("pre_treatment", r"pre[\s-]*treatment|before starting|baseline (?:work[\s-]*up|checks?)|screening"),
    ("vaccinations", r"vaccin|immuni[sz]ation"),
    ("interactions", r"interaction"),
    ("monitoring", r"monitor|follow[\s-]*up|surveillance"),
    ("counselling", r"counsell?ing|patient education|advice"),
    ("maintenance", r"maintenance"),
]

# Field labels Vera uses, mapped onto the management-plan schema.
FIELD_MAP: dict[str, str] = {
    "drug": "drug", "medication": "drug", "agent": "drug", "name": "drug",
    "dose": "dose", "dosage": "dose", "starting dose": "dose",
    "frequency": "frequency", "freq": "frequency",
    "route": "route",
    "duration": "duration", "treatment duration": "duration",
    "renal adjustment": "renal_adjustment", "renal": "renal_adjustment",
    "renal dosing": "renal_adjustment", "dose adjustment": "renal_adjustment",
    "monitoring": "monitoring", "monitor": "monitoring",
    "evidence": "evidence", "guideline": "evidence", "reference": "evidence",
    "evidence level": "evidence_grade", "grade": "evidence_grade",
    "rationale": "rationale", "reasoning": "rationale", "justification": "rationale",
    "target": "target", "goal": "target",
    "contraindication": "contraindications", "contraindications": "contraindications",
    "precaution": "precautions", "precautions": "precautions",
    "interaction": "interactions", "interactions": "interactions",
    "note": "notes", "notes": "notes", "caution": "notes",
}

# A medication block opens on one of these labels.
DRUG_LABELS = {"drug", "medication", "agent"}

# Lines that are pure formatting.
_RULE_RE = re.compile(r"^[-*=_\s]{3,}$")
_HEADING_RE = re.compile(r"^(#{1,6})\s*(.+?)\s*#*$")
_BULLET_RE = re.compile(r"^\s*(?:[-*+•]|\d+[.)])\s+")
_KV_RE = re.compile(r"^([A-Za-z][A-Za-z /()\-]{0,28}?)\s*:\s*(.+)$")
# "1. **Prednisolone** 1 mg/kg/day PO" -- a drug named by a heading/bullet with
# no explicit "Drug:" label.
_NAMED_DRUG_RE = re.compile(r"^\*\*(?P<name>[^*]{2,60})\*\*\s*[—–-]?\s*(?P<rest>.*)$")

LINE_SECTIONS = {"first_line", "second_line", "rescue", "maintenance"}


def strip_markdown(text: str) -> str:
    """Remove the decorations Vera wraps its labels in."""
    out = text.strip()
    out = re.sub(r"\*\*(.+?)\*\*", r"\1", out)     # bold
    out = re.sub(r"(?<!\w)[*_](\S.*?\S)[*_](?!\w)", r"\1", out)  # italics
    out = re.sub(r"`(.+?)`", r"\1", out)           # inline code
    out = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1", out)  # links -> label
    return out.strip()


def _classify_heading(text: str) -> str | None:
    low = strip_markdown(text).lower()
    for name, pattern in SECTION_PATTERNS:
        if re.search(pattern, low):
            return name
    return None


@dataclass
class VeraPlan:
    """Everything worth keeping from one Vera response."""
    medications: list[dict] = field(default_factory=list)
    contraindicated: list[str] = field(default_factory=list)
    pre_treatment: list[str] = field(default_factory=list)
    vaccinations: list[str] = field(default_factory=list)
    interactions: list[str] = field(default_factory=list)
    monitoring: list[str] = field(default_factory=list)
    counselling: list[str] = field(default_factory=list)
    unparsed: list[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not (self.medications or self.contraindicated or self.pre_treatment
                    or self.vaccinations or self.interactions or self.monitoring
                    or self.counselling)

    def counts(self) -> dict[str, int]:
        return {
            "medications": len(self.medications),
            "contraindicated": len(self.contraindicated),
            "pre_treatment": len(self.pre_treatment),
            "vaccinations": len(self.vaccinations),
            "interactions": len(self.interactions),
            "monitoring": len(self.monitoring),
            "counselling": len(self.counselling),
        }


_NARRATIVE_BUCKETS = {
    "contraindicated": "contraindicated",
    "pre_treatment": "pre_treatment",
    "vaccinations": "vaccinations",
    "interactions": "interactions",
    "monitoring": "monitoring",
    "counselling": "counselling",
}


def parse_vera_response(text: str) -> VeraPlan:
    """Parse Vera's markdown answer into a VeraPlan.

    Handles the three shapes Vera actually produces, in any mix:
      1. `Drug: X` / `Dose: Y` label blocks (what the prompt asks for)
      2. the same labels wrapped in markdown bold / bullets / numbering
      3. a drug named by a bold heading, with details in following bullets
    """
    plan = VeraPlan()
    if not text or not text.strip():
        return plan

    section = ""          # current narrative section
    current: dict | None = None   # medication block being filled

    def close_current():
        nonlocal current
        if current and current.get("drug"):
            plan.medications.append(current)
        current = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or _RULE_RE.match(line.strip()):
            continue

        # --- headings switch section ---
        heading = _HEADING_RE.match(line.strip())
        heading_text = heading.group(2) if heading else None
        # A short bold-only line acts as a heading too ("**Monitoring**").
        if heading_text is None:
            bare = line.strip()
            if bare.startswith("**") and bare.endswith("**") and len(bare) < 70 \
                    and ":" not in bare:
                heading_text = strip_markdown(bare)
        if heading_text is not None:
            found = _classify_heading(heading_text)
            if found:
                close_current()
                section = found
                continue
            # A heading we don't recognise still ends the current drug block.
            close_current()
            continue

        body = _BULLET_RE.sub("", line.strip())
        body = strip_markdown(body)
        if not body:
            continue

        # --- label: value ---
        kv = _KV_RE.match(body)
        if kv:
            key = kv.group(1).strip().lower()
            value = kv.group(2).strip()
            if key in DRUG_LABELS:
                close_current()
                current = {"drug": value, "section": section or "first_line"}
                continue
            mapped = FIELD_MAP.get(key)
            if mapped and current is not None:
                # Append rather than overwrite: Vera sometimes repeats a label.
                if current.get(mapped):
                    current[mapped] = f"{current[mapped]}; {value}"
                else:
                    current[mapped] = value
                continue
            if mapped and current is None and mapped in ("monitoring", "contraindications"):
                bucket = "monitoring" if mapped == "monitoring" else "contraindicated"
                getattr(plan, bucket).append(value)
                continue
            # A labelled line outside any drug block -> keep it in its section.
            if section in _NARRATIVE_BUCKETS:
                getattr(plan, _NARRATIVE_BUCKETS[section]).append(body)
                continue
            plan.unparsed.append(body)
            continue

        # --- a drug named in bold, details to follow ---
        named = _NAMED_DRUG_RE.match(line.strip())
        if named and section in LINE_SECTIONS:
            close_current()
            current = {"drug": strip_markdown(named.group("name")),
                       "section": section}
            rest = strip_markdown(named.group("rest") or "")
            if rest:
                current["dose"] = rest
            continue

        # --- plain prose ---
        if section in _NARRATIVE_BUCKETS:
            getattr(plan, _NARRATIVE_BUCKETS[section]).append(body)
        elif current is not None:
            # Continuation of the current drug's rationale.
            current["rationale"] = (
                f"{current['rationale']} {body}".strip()
                if current.get("rationale") else body
            )
        else:
            plan.unparsed.append(body)

    close_current()
    return plan


# --------------------------------------------------------------------------- #
# Conversion to KnowledgeBaseEntry.rule_data
# --------------------------------------------------------------------------- #

# Vera's section -> the management-plan list it belongs in.
SECTION_TO_PLAN_LINE = {
    "first_line": "first_line",
    "maintenance": "first_line",
    "second_line": "second_line",
    "rescue": "rescue_therapy",
}

PLAN_FIELDS = ("drug", "dose", "frequency", "route", "duration", "target",
               "renal_adjustment", "monitoring", "evidence", "rationale",
               "contraindications", "precautions", "interactions", "notes")


def medication_to_rule_data(med: dict, *, disease_id: str, disease_name: str,
                            patient_id: str, captured_at: str) -> dict:
    """Shape one parsed medication like a DISEASE_TREATMENT_PROFILES entry.

    Provenance is recorded, but the patient's NAME is deliberately not: the
    knowledge base is disease-level knowledge and should not accumulate
    identifiable data. The registry ID is enough to trace the recommendation
    back to the consultation that produced it.
    """
    data = {f: (med.get(f) or "") for f in PLAN_FIELDS}
    data["plan_line"] = SECTION_TO_PLAN_LINE.get(med.get("section", ""), "first_line")
    data["disease_id"] = disease_id
    data["disease_name"] = disease_name
    data["provenance"] = {
        "source": "vera_health_ai",
        "patient_id": patient_id,
        "captured_at": captured_at,
        "section": med.get("section", ""),
    }
    return data
