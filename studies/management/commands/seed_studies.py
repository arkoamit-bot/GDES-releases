"""
Seed the BGDDR research portfolio as Study records so they can be selected and
enrolled into from the clinic UI (/patients/<id>/enrol/).

Covers: the Phase-A prospective registry, the six flagship first-wave studies,
the GN Master Protocol's illustrative Phase-C interventional sub-studies, and the
distinctive supportive-therapy cohorts. Idempotent — safe to re-run.

    python manage.py seed_studies

Study codes that have a registered eligibility function (ADVANCED-DKD-IGAN,
HCQ-IGAN-ADVANCED) are screened automatically at enrolment.
"""
from django.core.management.base import BaseCommand

from studies.models import Study, StudyArm

OBS, QUASI, RCT = Study.Type.OBSERVATIONAL, Study.Type.QUASI, Study.Type.RCT
SB, NONE = Study.Scheme.STRATIFIED_BLOCK, Study.Scheme.NONE

# code, title, type, scheme, stratify_by, arms[(code,name,ratio,is_control)], consent, endpoint
PORTFOLIO = [
    ("BGDDR-REGISTRY", "BGDDR prospective GN registry (Phase A)", OBS, NONE, [], [],
     False, "composite_kidney_event"),

    # --- Flagship first-wave (Domain I) -------------------------------------
    ("ADVANCED-DKD-IGAN", "Study 25 — HCQ steroid-sparing in IgAN + diabetes, eGFR < 30",
     RCT, SB, ["diabetes"],
     [("hcq", "HCQ + supportive care", 1, False), ("control", "Supportive care", 1, True)],
     True, "complete_remission"),
    ("HCQ-IGAN-ADVANCED", "Study 1 — Hydroxychloroquine in IgAN, eGFR 15–30",
     QUASI, NONE, [], [], False, "egfr_slope"),
    ("MMF-IGAN", "Study 2 — MMF in steroid-resistant / intolerant IgAN",
     QUASI, NONE, [], [], False, "complete_remission"),
    ("MEST-C-PREDICTOR", "Study 4 — Oxford MEST-C as predictor of treatment response",
     OBS, NONE, [], [], False, "complete_remission"),
    ("RTX-MN-DOSE", "Study 7 — Low-dose vs standard rituximab in membranous nephropathy",
     RCT, SB, ["proteinuria_range"],
     [("low", "Low-dose rituximab (500 mg)", 1, False), ("std", "Standard rituximab", 1, True)],
     True, "complete_remission"),
    ("LN-IMPLEMENTATION", "Study 10 — Lupus nephritis implementation (before vs after)",
     OBS, NONE, [], [], False, "complete_remission"),

    # --- Phase-C illustrative interventional sub-studies (protocol §8.2) -----
    ("IGAN-BUDESONIDE", "IgAN — targeted-release budesonide vs optimised RAAS blockade",
     RCT, SB, ["egfr_30", "proteinuria_range"],
     [("budesonide", "Targeted-release budesonide", 1, False), ("raas", "Optimised RAAS blockade", 1, True)],
     True, "complete_remission"),
    ("MN-RTX-CNI", "Membranous nephropathy — rituximab vs tacrolimus",
     RCT, SB, ["proteinuria_range"],
     [("rtx", "Rituximab", 1, False), ("cni", "Tacrolimus", 1, True)],
     True, "complete_remission"),
    ("FSGS-STEROID-CNI", "FSGS — high-dose prednisolone vs calcineurin inhibitor",
     RCT, SB, ["egfr_30"],
     [("steroid", "High-dose prednisolone", 1, False), ("cni", "Calcineurin inhibitor", 1, True)],
     True, "complete_remission"),

    # --- Supportive-therapy / cross-disease cohorts (Domain II) --------------
    ("SGLT2-GN", "Study 3 — SGLT2 inhibitors across histologic GN subtypes (real-world)",
     OBS, NONE, [], [], False, "egfr_slope"),
    ("FINERENONE-GN", "Study 15 — Finerenone in biopsy-proven GN (new-user cohort)",
     OBS, NONE, [], [], False, "egfr_slope"),
]


class Command(BaseCommand):
    help = "Seed the BGDDR research portfolio as selectable studies."

    def handle(self, *args, **options):
        created = updated = n_arms = 0
        for i, (code, title, stype, scheme, strat, arms, consent, endpoint) in enumerate(PORTFOLIO):
            study, was_new = Study.objects.update_or_create(
                code=code,
                defaults=dict(
                    title=title, study_type=stype, status=Study.Status.RECRUITING,
                    randomization_scheme=scheme, stratify_by=strat,
                    block_multipliers=[2] if scheme == SB else [],
                    random_seed=20260100 + i, requires_trial_consent=consent,
                    primary_endpoint=endpoint),
            )
            created += was_new
            updated += not was_new
            for order, (acode, aname, ratio, is_control) in enumerate(arms):
                _, a_new = StudyArm.objects.get_or_create(
                    study=study, code=acode,
                    defaults=dict(name=aname, ratio=ratio, order=order, is_control=is_control))
                n_arms += a_new
        self.stdout.write(self.style.SUCCESS(
            f"Studies seeded: {created} created, {updated} updated, {n_arms} arms added."))
