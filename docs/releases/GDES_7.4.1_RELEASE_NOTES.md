## GDES 7.4.1

A small data release. No database migrations and no change to how the app
looks or behaves for clinicians.

### Drug database
- **`import_dkdr_drugs`** merges the DKDR brand catalogue (MedEx `bd_med` and
  the brand registry) into the drug list. It is additive: brands and strengths
  are added to existing drugs, nothing is deleted or overwritten. Names that
  differ from an existing drug only by a salt or hydrate word (for example
  "Cefixime" and "Cefixime Trihydrate") are filed under the existing drug
  instead of creating a duplicate. `--dry-run` reports without writing.
- **Drug-class fixes.** The importer no longer treats nystatin, somatostatin
  or cilastatin as statins, and no longer classes topical, eye, ear, nasal or
  inhaled products, or combinations of different ingredients, as systemic
  steroids or calcineurin inhibitors. `reclassify_drug_classes` corrects
  existing rows (report first, `--apply` to write).

### Installer
- The installer script's default version now matches the app version.

After updating, run `import_dkdr_drugs` and `reclassify_drug_classes --apply`
(or `sync_medex_drugs`) to bring an existing installation's drug list up to
date; a fresh update alone does not change the drug table.
