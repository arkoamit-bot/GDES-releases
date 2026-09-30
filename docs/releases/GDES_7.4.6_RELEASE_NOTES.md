## GDES 7.4.6

Two fixes on the prescription. No database migrations.

### The preview showed nothing
The prescription preview page embedded the slip in a way the browser cut off
after the first few characters, so the box was empty. The whole slip now
shows. This was also the reason printing that page came out blank.

### An injection was offered, and printed, as oral
A drug's route was only picked up when it appeared inside the drug's name, so
a drug sold only as an injection kept the default route "oral": meropenem was
offered as PO in the prescription form and printed **PO** on the slip.

The route now comes from the product's dosage form, and only when the form
names a route outright. A bare "Injection" still claims nothing, because it
may be IV, IM or SC.

The first start after updating applies this to the drug list already on the
PC, which takes a few seconds:

- meropenem: PO → **IV**; ceftriaxone: PO → **IV** (IM also offered)
- paracetamol: IV → **PO** (IV and PR also offered)
- no drug that has an oral form loses "oral", and no drug in the curated
  nephrology formulary changes its route

**Prescriptions already issued keep the route recorded at the time** — they are
immutable records. Re-issue any prescription that shows a wrong route.
