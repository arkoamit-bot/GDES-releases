"""Scaffold the glomerular diseases from the V8 development order that are not yet
in the knowledge base.

Adds each as a Disease record (accurate name/category/definition) plus ONE
skeletal DRAFT diagnostic rule so it enters the expert review queue. The rules
are created with status=DRAFT and are NEVER activated by this command — a
nephrologist must author and approve them via the knowledge lifecycle before
they can influence recommendations (clinical governance).

    python manage.py seed_missing_diseases
"""
from datetime import date

from django.core.management.base import BaseCommand


# (id, name, category, definition)
DISEASES = [
    ("irgn", "Infection-Related Glomerulonephritis", "secondary",
     "GN triggered by active or recent infection (post-streptococcal or "
     "staphylococcus-associated); immune-complex mediated."),
    ("mgrs", "Monoclonal Gammopathy of Renal Significance (MGRS)", "secondary",
     "Kidney disease caused by a nephrotoxic monoclonal immunoglobulin from a "
     "B-cell or plasma-cell clone that does not meet criteria for overt malignancy."),
    ("amyloidosis", "Renal Amyloidosis", "secondary",
     "Extracellular deposition of misfolded fibrillar protein (AL, AA and others) "
     "causing nephrotic-range proteinuria and progressive CKD."),
    ("immunotactoid", "Immunotactoid Glomerulopathy", "primary",
     "Organised microtubular immunoglobulin deposits (>30 nm); frequently "
     "associated with lymphoproliferative disorders."),
    ("cfhr", "CFHR-Related C3 Glomerulopathy", "primary",
     "Complement dysregulation arising from CFHR gene rearrangements, producing "
     "a C3 glomerulopathy phenotype."),
    ("fabry", "Fabry Disease (renal involvement)", "hereditary",
     "X-linked alpha-galactosidase A deficiency causing glycosphingolipid "
     "accumulation, podocyte injury and progressive CKD."),
    ("hbvGn", "HBV-Associated Glomerulonephritis", "secondary",
     "Hepatitis B virus-related glomerulonephritis, most often a membranous or "
     "membranoproliferative pattern."),
    ("hcvGn", "HCV-Associated Glomerulonephritis", "secondary",
     "Hepatitis C virus-related glomerulonephritis, commonly cryoglobulinaemic "
     "membranoproliferative GN."),
    ("igg4", "IgG4-Related Kidney Disease", "tubulointerstitial",
     "IgG4-related disease manifesting as tubulointerstitial nephritis, sometimes "
     "with a membranous pattern; storiform fibrosis and IgG4+ plasma cells."),
    ("paraneoplastic", "Paraneoplastic Glomerular Disease", "secondary",
     "Glomerular disease associated with an underlying malignancy (frequently "
     "membranous nephropathy or minimal change disease)."),
    ("sarcoidosis", "Sarcoidosis-Associated Kidney Disease", "tubulointerstitial",
     "Granulomatous interstitial nephritis and hypercalcaemia-related injury in "
     "systemic sarcoidosis."),
    ("recurrentIga", "Recurrent IgA Nephropathy (allograft)", "transplant",
     "Recurrence of IgA nephropathy in the kidney allograft."),
    ("recurrentFsgs", "Recurrent FSGS (allograft)", "transplant",
     "Early recurrence of focal segmental glomerulosclerosis after "
     "transplantation, often driven by a circulating permeability factor."),
    ("recurrentMembranous", "Recurrent Membranous Nephropathy (allograft)", "transplant",
     "Recurrence of (usually PLA2R-associated) membranous nephropathy in the "
     "kidney allograft."),
]


class Command(BaseCommand):
    help = "Scaffold missing diseases + DRAFT rules (for expert authoring)."

    def handle(self, *args, **options):
        from knowledge.models import Disease, KnowledgeBaseEntry, GuidelineSource

        source = (GuidelineSource.objects.filter(abbreviation__icontains="KDIGO").first()
                  or GuidelineSource.objects.first())

        created_dx = updated_dx = created_rules = 0
        for did, name, category, definition in DISEASES:
            _, was_created = Disease.objects.update_or_create(
                id=did,
                defaults={"name": name, "category": category, "definition": definition},
            )
            created_dx += int(was_created)
            updated_dx += int(not was_created)

            entry_id = f"SCAFFOLD-{did.upper()}-DIAG-001"
            _, rule_created = KnowledgeBaseEntry.objects.get_or_create(
                entry_id=entry_id,
                defaults={
                    "disease_id": did,
                    "rule_data": {
                        "conditions": [],
                        "weight": 0,
                        "base_score": 0,
                        "explanation": (
                            f"SCAFFOLD placeholder for {name}. Requires nephrologist "
                            "authoring of diagnostic criteria before activation."),
                    },
                    "source": source,
                    "evidence_grade": "NG",
                    "rule_type": KnowledgeBaseEntry.RuleType.DIAGNOSTIC,
                    "status": KnowledgeBaseEntry.Status.DRAFT,
                    "effective_date": date.today(),
                    "review_notes": "Auto-scaffolded; needs expert authoring + approval.",
                },
            )
            created_rules += int(rule_created)

        self.stdout.write(self.style.SUCCESS(
            f"Diseases: {created_dx} created, {updated_dx} updated. "
            f"DRAFT scaffold rules created: {created_rules}. "
            f"({Disease.objects.count()} diseases total; scaffold rules are DRAFT — "
            "author and approve them before they affect recommendations.)"
        ))
