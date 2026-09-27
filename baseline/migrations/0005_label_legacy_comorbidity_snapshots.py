"""Label pre-existing baseline comorbidity columns as a legacy mirror.

Before this release the columns were rewritten from the patient record on every
baseline save, so their values are not a dated enrollment snapshot. Only the
label is set here -- no clinical value is changed, and no snapshot date is
invented (comorbidity_snapshot_at stays empty). reconcile_linked_facts reports
disagreements between these legacy values and the patient record for review.
"""
from django.db import migrations


def label_legacy(apps, schema_editor):
    Baseline = apps.get_model("baseline", "BaselineAssessment")
    Baseline.objects.filter(comorbidity_snapshot_source="").update(
        comorbidity_snapshot_source="legacy_mirror")


class Migration(migrations.Migration):

    dependencies = [
        ("baseline", "0004_baselineassessment_baseline_encounter_and_more"),
    ]

    operations = [
        migrations.RunPython(label_legacy, migrations.RunPython.noop),
    ]
