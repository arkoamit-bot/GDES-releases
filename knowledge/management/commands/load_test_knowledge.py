"""
Load a deterministic test knowledge base for integration testing.

This is NOT production knowledge. It is a curated, deterministic fixture
with small, independent, version-controlled rules for every supported disease.

Usage:
    python manage.py load_test_knowledge          # loads if not already loaded
    python manage.py load_test_knowledge --force   # reload even if loaded
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from knowledge.models import GuidelineSource, KnowledgeBaseEntry

TEST_RULES: list[dict] = [
    # ---- IgA Nephropathy (IgAN) ----
    {
        "entry_id": "TEST-IGA-001",
        "disease_id": "iga",
        "disease_name": "IgA nephropathy (IgAN)",
        "rule_data": {
            "conditions": [{"field": "biopsy", "operator": "contains", "value": "mesangialIga"}],
            "weight": 10, "base_score": 0,
            "explanation": "Mesangial IgA deposits on biopsy are diagnostic of IgAN",
        },
        "evidence_grade": "1", "rule_type": "diagnostic",
    },
    {
        "entry_id": "TEST-IGA-002",
        "disease_id": "iga",
        "disease_name": "IgA nephropathy (IgAN)",
        "rule_data": {
            "conditions": [{"field": "proteinuria", "operator": "eq", "value": "subnephrotic"}],
            "weight": 3, "base_score": 0,
            "explanation": "Subnephrotic proteinuria is common in IgAN",
        },
        "evidence_grade": "2", "rule_type": "diagnostic",
    },
    # ---- Membranous nephropathy ----
    {
        "entry_id": "TEST-MN-001",
        "disease_id": "membranous",
        "disease_name": "Membranous nephropathy",
        "rule_data": {
            "conditions": [
                {"field": "biopsy", "operator": "contains", "value": "subepithelial"},
                {"field": "proteinuria", "operator": "eq", "value": "nephrotic"},
            ],
            "weight": 10, "base_score": 0,
            "explanation": "Subepithelial deposits with nephrotic proteinuria suggest membranous nephropathy",
        },
        "evidence_grade": "1", "rule_type": "diagnostic",
    },
    # ---- FSGS ----
    {
        "entry_id": "TEST-FSGS-001",
        "disease_id": "fsgs",
        "disease_name": "FSGS",
        "rule_data": {
            "conditions": [{"field": "biopsy", "operator": "contains", "value": "segmentalSclerosis"}],
            "weight": 10, "base_score": 0,
            "explanation": "Segmental sclerosis on biopsy is characteristic of FSGS",
        },
        "evidence_grade": "1", "rule_type": "diagnostic",
    },
    # ---- Minimal change disease ----
    {
        "entry_id": "TEST-MCD-001",
        "disease_id": "mcd",
        "disease_name": "Minimal change disease",
        "rule_data": {
            "conditions": [
                {"field": "biopsy", "operator": "contains", "value": "podocyteEffacement"},
                {"field": "proteinuria", "operator": "eq", "value": "nephrotic"},
            ],
            "weight": 10, "base_score": 0,
            "explanation": "Podocyte effacement with nephrotic proteinuria suggests MCD",
        },
        "evidence_grade": "2", "rule_type": "diagnostic",
    },
    # ---- Lupus nephritis ----
    {
        "entry_id": "TEST-LN-001",
        "disease_id": "lupus",
        "disease_name": "Lupus nephritis",
        "rule_data": {
            "conditions": [
                {"field": "biopsy", "operator": "contains", "value": "fullHouse"},
                {"field": "labs", "operator": "contains", "value": "lowC3"},
            ],
            "weight": 10, "base_score": 0,
            "explanation": "Full-house immunofluorescence with low C3 is diagnostic of lupus nephritis",
        },
        "evidence_grade": "1", "rule_type": "diagnostic",
    },
    # ---- ANCA vasculitis ----
    {
        "entry_id": "TEST-ANCA-001",
        "disease_id": "anca",
        "disease_name": "ANCA vasculitis",
        "rule_data": {
            "conditions": [
                {"field": "biopsy", "operator": "contains", "value": "crescents"},
                {"field": "labs", "operator": "contains", "value": "anca"},
            ],
            "weight": 10, "base_score": 0,
            "explanation": "Crescentic GN with ANCA positivity is diagnostic of ANCA vasculitis",
        },
        "evidence_grade": "1", "rule_type": "diagnostic",
    },
    # ---- Anti-GBM disease ----
    {
        "entry_id": "TEST-GBM-001",
        "disease_id": "antiGbm",
        "disease_name": "Anti-GBM disease",
        "rule_data": {
            "conditions": [
                {"field": "biopsy", "operator": "contains", "value": "crescents"},
                {"field": "labs", "operator": "contains", "value": "antiGbm"},
            ],
            "weight": 10, "base_score": 0,
            "explanation": "Crescentic GN with anti-GBM antibodies is diagnostic of anti-GBM disease",
        },
        "evidence_grade": "1", "rule_type": "diagnostic",
    },
    # ---- C3 glomerulopathy ----
    {
        "entry_id": "TEST-C3-001",
        "disease_id": "c3",
        "disease_name": "C3 glomerulopathy",
        "rule_data": {
            "conditions": [
                {"field": "biopsy", "operator": "contains", "value": "c3Dominant"},
                {"field": "labs", "operator": "contains", "value": "lowC3"},
            ],
            "weight": 10, "base_score": 0,
            "explanation": "C3-dominant immunofluorescence with low C3 suggests C3 glomerulopathy",
        },
        "evidence_grade": "2", "rule_type": "diagnostic",
    },
    # ---- Diabetic kidney disease ----
    {
        "entry_id": "TEST-DKD-001",
        "disease_id": "diabeticNephropathy",
        "disease_name": "Diabetic kidney disease",
        "rule_data": {
            "conditions": [
                {"field": "features", "operator": "contains", "value": "diabetes"},
                {"field": "egfrTrend", "operator": "in", "value": ["reduced", "rapidDecline"]},
            ],
            "weight": 8, "base_score": 0,
            "explanation": "Diabetes with reduced eGFR suggests diabetic kidney disease",
        },
        "evidence_grade": "1", "rule_type": "diagnostic",
    },
]

TEST_SOURCE_DATA = {
    "title": "Test Knowledge Base",
    "abbreviation": "TEST",
    "version_year": 2026,
    "url": "",
    "effective_date": date.today(),
}


class Command(BaseCommand):
    help = "Load deterministic test knowledge base for integration testing"

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Reload even if already loaded")

    def handle(self, *args, **options):
        if KnowledgeBaseEntry.objects.filter(entry_id__startswith="TEST-").exists() and not options["force"]:
            self.stdout.write(self.style.WARNING("Test knowledge base already loaded. Use --force to reload."))
            return

        if options["force"]:
            KnowledgeBaseEntry.objects.filter(entry_id__startswith="TEST-").delete()

        source, _ = GuidelineSource.objects.get_or_create(
            abbreviation="TEST", version_year=2026, defaults=TEST_SOURCE_DATA,
        )

        with transaction.atomic():
            for rule in TEST_RULES:
                KnowledgeBaseEntry.objects.update_or_create(
                    entry_id=rule["entry_id"],
                    defaults={
                        "disease_id": rule["disease_id"],
                        "rule_data": rule["rule_data"],
                        "source": source,
                        "evidence_grade": rule["evidence_grade"],
                        "rule_type": rule["rule_type"],
                        "status": KnowledgeBaseEntry.Status.ACTIVE,
                        "effective_date": date.today(),
                        "tags": ["test", rule["disease_id"]],
                    },
                )

        count = KnowledgeBaseEntry.objects.filter(entry_id__startswith="TEST-").count()
        self.stdout.write(self.style.SUCCESS(f"Loaded {count} deterministic test rules."))
