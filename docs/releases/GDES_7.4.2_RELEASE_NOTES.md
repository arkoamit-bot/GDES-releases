## GDES 7.4.2

A small data release. No database migrations and no visible change for
clinicians.

### Drug database
- **`import_dkdr_drugs` now reads every DKDR drug source**: MedEx `bd_med`,
  the brand registry, and the BDDrugBank subset (which also supplies a
  therapeutic class per brand). With `--create-generics --fold-salts` a server
  that only has the 60 curated drugs ends with about 2,470 generics and
  27,000+ brands.
- **Insulin products are imported too** (Lispro, Aspart, Glulisine, Detemir,
  Degludec and mixes), classed as insulin like the existing insulin rows.
- **Fix:** the drug importer no longer stops with a duplicate-name error on a
  database that does not yet hold a generic when two spellings of it
  ("Losartan potassium" / "Losartan Potassium") arrive in one run.

See 7.4.1 for the drug-class corrections and `reclassify_drug_classes`.
