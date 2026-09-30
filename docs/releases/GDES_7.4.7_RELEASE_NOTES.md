## GDES 7.4.7

An injection is no longer offered, or printed, as oral. No database migrations.

### Injections
7.4.6 took each drug's route from its dosage form. For 154 drugs the catalogue
says only "Injection" or "Infusion", which does not say whether the product is
IV, IM or SC, so those still fell back to "oral" — adrenaline, bleomycin,
snake antivenom and two premixed insulins among them.

The route now comes from a clinical table built from published labels and the
standard immunisation reference, with the source recorded for each group:

- vaccines and toxoids **IM**, yellow fever **SC**
- vincristine **IV only** (fatal by any other route)
- heparin **IV or deep SC, never IM**; premixed insulin **SC only**
- procaine penicillin and streptomycin **IM only, never IV**
- epoetin and Mircera **IV or SC**; iron dextran **IV or IM**
- intravenous fluids, nutrition and contrast media **IV**
- depot testosterone and nandrolone **IM**

Where the route depends on the procedure rather than the product, the route is
recorded as **"INJ — Injection (route not specified)"** instead of a guess.
That is 11 drugs, nearly all local anaesthetics given by infiltration or
spinally. The slip prints INJ and the prescriber chooses the route.

Spinal, intravitreal, intra-articular and intracameral products can now be
recorded as what they are, rather than being forced into a systemic route.

The first start after updating applies this to the drug list already on the
PC, which takes a few seconds.

**Prescriptions already issued keep the route recorded at the time** — they are
immutable records. Re-issue any prescription that shows a wrong route.
