## GDES 7.4.3

A data-tool patch. No database migrations and no visible change for
clinicians.

- `import_dkdr_drugs --fold-salts` no longer files a bare ion name ("Calcium",
  "Sodium", "Magnesium") under a salt row such as "Calcium Carbonate". Such a
  name is now imported as its own drug, and a second run of the import finds
  nothing left to add.
