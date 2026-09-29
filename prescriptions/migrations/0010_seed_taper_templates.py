"""Starting taper templates, editable in Admin -> Prescriptions -> Taper templates.

The three counselling texts are the former hard-coded TAPER_PRESETS, word for
word. "Short course - no taper needed" is not carried over: picking it ticked
"Taper this course", so the slip printed "Taper before stopping ... reduce the
dose step by step" above "No taper needed". Leaving the box unticked says that.

The dose ladders are examples in the printed format, to be adjusted to the
patient's dose, indication and tablet strengths. Existing titles are never
overwritten, and reversing this migration leaves the rows alone.
"""
from django.db import migrations

TEMPLATES = [
    ("Prednisolone 60 mg to stop (example ladder)",
     "60 mg once daily (morning) x 4 weeks\n"
     "50 mg daily x 1 week\n"
     "40 mg daily x 1 week\n"
     "30 mg daily x 1 week\n"
     "20 mg daily x 1 week\n"
     "15 mg daily x 1 week\n"
     "10 mg daily x 1 week\n"
     "5 mg daily x 1 week, then stop."),
    ("Prednisolone 40 mg to stop (example ladder)",
     "40 mg once daily (morning) x 2 weeks\n"
     "30 mg daily x 2 weeks\n"
     "20 mg daily x 2 weeks\n"
     "15 mg daily x 1 week\n"
     "10 mg daily x 1 week\n"
     "5 mg daily x 1 week, then stop."),
    ("Prednisolone 20 mg to stop (example ladder)",
     "20 mg once daily (morning) x 1 week\n"
     "15 mg daily x 1 week\n"
     "10 mg daily x 1 week\n"
     "5 mg daily x 1 week, then stop."),
    ("Step down to maintenance (example)",
     "Reduce by 5 mg every 2 weeks down to 10 mg daily, then by 2.5 mg every "
     "4 weeks down to 5 mg daily. Continue 5 mg daily until the next review."),
    ("Standard course — step down to zero",
     "TAPER BEFORE STOPPING. Reduce the dose step by step as advised "
     "(commonly by one tablet every 5–7 days) until the course is "
     "finished. Do not stop this steroid suddenly."),
    ("Long course / previous long steroid use",
     "TAPER SLOWLY. Reduce the dose by about 25% every 1–2 weeks, then "
     "by the smallest tablet every 5–7 days, until it is finished. "
     "Do not stop suddenly — long courses can suppress the adrenal "
     "glands. Carry a steroid card and tell any doctor you are on "
     "long-term steroids."),
    ("Adrenal-suppression counselling",
     "Do not stop this steroid suddenly. Long courses can suppress the "
     "adrenal glands, so the dose must be reduced slowly as advised. "
     "Carry a steroid card and mention it before any surgery, illness "
     "or vomiting."),
]


def seed(apps, schema_editor):
    TaperTemplate = apps.get_model("prescriptions", "TaperTemplate")
    for order, (title, body) in enumerate(TEMPLATES, start=1):
        TaperTemplate.objects.get_or_create(
            title=title, defaults={"body": body, "sort_order": order * 10})


class Migration(migrations.Migration):

    dependencies = [
        ("prescriptions", "0009_tapertemplate"),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
