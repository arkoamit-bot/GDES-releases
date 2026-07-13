"""
Create the registry roles (Django Groups) and assign per-model permissions
(protocol §11 role-based access control).

    python manage.py seed_roles

Reads are open to any authenticated user (DjangoModelPermissions); these grants
gate writes. Assign a user to a role with: user.groups.add(Group.objects.get(name="coordinator")).
"""
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

REGISTRY_APPS = [
    "patients", "encounters", "baseline", "labs", "pathology", "treatments",
    "prescriptions", "analytics", "audit", "studies", "safety", "scheduling",
    "biomarkers", "clinical", "knowledge", "decision", "timeline",
]

# role -> {"app_label.model": [actions]} ; "ALL" grants every registry permission,
# "VIEW_ALL" grants view on every registry model.
ROLES = {
    "data_manager": "ALL",
    "statistician": "VIEW_ALL",
    "readonly": "VIEW_ALL",
    "coordinator": {
        "patients.patient": ["add", "change", "view"],
        "encounters.clinicalencounter": ["add", "change", "view"],
        "scheduling.scheduledvisit": ["add", "change", "view"],
        "studies.studyenrollment": ["add", "change", "view"],
        "prescriptions.prescription": ["view"],
    },
    "investigator": {
        "encounters.clinicalencounter": ["add", "change", "view"],
        "encounters.clinicalevent": ["add", "change", "view"],
        "treatments.treatmentexposure": ["add", "change", "view"],
        "prescriptions.prescription": ["add", "change", "view"],
        "safety.adverseevent": ["add", "change", "view"],
        "labs.labresult": ["add", "change", "view"],
    },
    "pathologist": {
        "pathology.biopsy": ["add", "change", "view"],
        "pathology.pathologyreview": ["add", "change", "view"],
        "pathology.gndiagnosis": ["add", "change", "view"],
    },
}


def _perm(app_label, model, action):
    ct = ContentType.objects.get(app_label=app_label, model=model)
    return Permission.objects.get(content_type=ct, codename=f"{action}_{model}")


def _all_registry_perms(view_only=False):
    qs = Permission.objects.filter(content_type__app_label__in=REGISTRY_APPS)
    if view_only:
        qs = qs.filter(codename__startswith="view_")
    return list(qs)


class Command(BaseCommand):
    help = "Create roles (Groups) and assign per-model permissions."

    def handle(self, *args, **options):
        for role, spec in ROLES.items():
            group, _ = Group.objects.get_or_create(name=role)
            if spec == "ALL":
                perms = _all_registry_perms()
            elif spec == "VIEW_ALL":
                perms = _all_registry_perms(view_only=True)
            else:
                perms = []
                for dotted, actions in spec.items():
                    app_label, model = dotted.split(".")
                    for action in actions:
                        perms.append(_perm(app_label, model, action))
            group.permissions.set(perms)
            self.stdout.write(f"  {role}: {len(perms)} permissions")
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(ROLES)} roles."))
