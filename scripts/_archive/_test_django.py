"""Verify Django integration of the exports app."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bgddr.settings")
django.setup()

# Verify app loads
from django.apps import apps
app_config = apps.get_app_config("exports")
print(f"App loaded: {app_config.name} ({app_config.verbose_name})")

# Verify services are importable
from exports.services.dataset import build_dataset
from exports.services.dictionary import column_defs
from exports.services.writers import to_csv, to_xlsx, to_sav
print("All service imports OK")

# Verify URL resolution
from django.urls import reverse
url = reverse("exports:export-index")
print(f"URL resolved: {url}")

# Verify all export URLs
for name in ["export-index", "export-csv", "export-xlsx", "export-sav"]:
    url = reverse(f"exports:{name}")
    print(f"  {name}: {url}")

print("\nAll Django integration checks passed!")
