## GDES 7.4.4

The full drug list now ships with the app. No database migrations.

### Drug list
- **About 2,470 drugs and 27,000 brand names**, from the DKDR catalogue
  (MedEx `bd_med`, the brand registry and the BDDrugBank subset), are applied
  automatically the first time the updated app starts. It usually takes a few
  seconds. Later starts skip it.
- **Additive.** Brands and strengths are added to the drugs already on the PC.
  Nothing is deleted, and curated formulary entries keep their brand order.
  PCs that already have the weekly MedEx list end with fewer new rows, because
  most names match drugs they already hold.
- **Drug classes are corrected** on the same start (nystatin, somatostatin and
  cilastatin are not statins; topical/eye/ear/nasal/inhaled products and
  combinations are not systemic steroids or calcineurin inhibitors). This can
  change how existing exposures to those products are classed in analytics.
- If the step fails, the app still starts and retries on the next launch.

Servers apply the same list during `server_init`.
