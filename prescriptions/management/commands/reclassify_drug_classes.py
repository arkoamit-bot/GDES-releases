"""Correct DrugMaster.drug_class values the old name matcher got wrong.

    python manage.py reclassify_drug_classes            # report only
    python manage.py reclassify_drug_classes --apply    # write the changes

`classify_drug` used to match the bare substring "statin" (so nystatin,
somatostatin and cilastatin became STATIN) and put topical / eye / nasal
products and multi-ingredient combinations into the steroid and calcineurin
inhibitor classes. Those classes drive exposure analytics and prescription
rules, so already-imported rows are corrected here.

Deliberately conservative:

* Only rows currently STATIN, STEROID or CNI are considered.
* Only rows whose *name* carries the old false-positive signal are touched -
  a row classed from its MedEx therapeutic class alone is left as it is.
* A row moves only when the corrected name matcher disagrees with it.
* Curated formulary rows (`seed_drugs.DRUGS`) are never changed.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from treatments.models import DrugClass, DrugMaster

from .import_bddrugbank import CURATED_BRANDS, classify_drug, norm

# The name signals the old matcher keyed on, per affected class.
_LEGACY_NAME_SIGNALS = {
    DrugClass.STATIN: ("statin",),
    DrugClass.STEROID: (
        "prednisolone", "prednisone", "methylprednisolone", "dexamethasone",
        "betamethasone", "budesonide", "deflazacort", "hydrocortisone",
        "cortisone", "triamcinolone", "beclomethasone", "fluticasone",
        "corticosteroid", "glucocorticoid"),
    DrugClass.CNI: ("cyclosporine", "ciclosporin", "tacrolimus", "rapamycin",
                    "everolimus", "sirolimus"),
}


def proposed_changes():
    curated = {norm(name) for name in CURATED_BRANDS}
    for drug in DrugMaster.objects.filter(
            drug_class__in=list(_LEGACY_NAME_SIGNALS)).order_by("generic_name"):
        if norm(drug.generic_name) in curated:
            continue
        lowered = drug.generic_name.lower()
        if not any(k in lowered for k in _LEGACY_NAME_SIGNALS[drug.drug_class]):
            continue
        new = classify_drug(drug.generic_name, [])
        if new != drug.drug_class:
            yield drug, new


class Command(BaseCommand):
    requires_system_checks = []
    help = "Fix drug_class values set by the old substring name matcher."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true",
                            help="Write the changes (default: report only)")

    def handle(self, *args, apply, **options):
        changes = list(proposed_changes())
        for drug, new in changes:
            self.stdout.write(f"  {drug.generic_name}: {drug.drug_class} -> {new}")
        if apply and changes:
            with transaction.atomic():
                for drug, new in changes:
                    drug.drug_class = new
                    drug.save(update_fields=["drug_class"])
        self.stdout.write(self.style.SUCCESS(
            f"{'Changed' if apply else 'Would change'} {len(changes)} row(s)."))
