"""Render synthetic prescription print samples for visual QA (not a test).

    $env:PRINT_SAMPLES_OUT = "<dir>"
    python -m pytest docs/reviews/2026-09-27-entry-linkage/print_samples.py -q -s

Writes, per scenario, the standalone HTML (the in-app print / HTML download
content) and, when a PDF engine is importable, the PDF from each available
backend. Only synthetic patients are used. Outside normal test discovery.
"""
import os
from datetime import date
from pathlib import Path

import pytest

pytestmark = pytest.mark.django_db
DAY = date(2026, 9, 1)

LONG_NAME = "Mohammad Abdur Rahman Chowdhury Talukder Bhuiyan (Synthetic Long Name)"
ADVICE = ("Low-salt diet. Check blood pressure daily.\n"
          "Bring all reports to the next visit.")
TAPER = ("40 mg daily x 2 weeks\n30 mg daily x 2 weeks\n20 mg daily x 2 weeks\n"
         "15 mg daily x 2 weeks\n10 mg daily x 4 weeks\n5 mg daily x 4 weeks, then stop")
COMBO_GENERIC = "Calcium Lactate Gluconate + Calcium Carbonate + Vitamin C + Vitamin D3"
COMBO_STRENGTH = "1000 mg+327 mg (Conventional calcium)+500 mg+400 IU"


@pytest.fixture(autouse=True)
def quiet(monkeypatch):
    monkeypatch.setattr("events.signal_handlers.dispatch", lambda *a, **k: None)
    monkeypatch.setattr("events.dispatcher.dispatch", lambda *a, **k: None)


def _drugs():
    from treatments.models import DrugMaster
    names = ["Prednisolone", "Ramipril", "Mycophenolate mofetil", "Empagliflozin",
             "Atorvastatin", "Furosemide", "Hydroxychloroquine", "Tacrolimus",
             "Omeprazole", "Amlodipine", "Metformin", "Losartan", "Cotrimoxazole",
             "Alendronate", COMBO_GENERIC]
    return [DrugMaster.objects.get_or_create(
        generic_name=n, defaults={"drug_class": "other", "default_route": "PO"})[0]
        for n in names]


def _rx(n_items, *, name="Rahima Begum (Synthetic)", final=False, dose_rows=True,
        taper=True, advice=True, stopped=True):
    from encounters.models import ClinicalEncounter
    from patients.models import Patient
    from prescriptions.models import Prescription, PrescriptionItem
    from prescriptions.services.finalize import finalize_prescription
    p = Patient.objects.create(name=name, sex="F", dob=date(1978, 3, 3),
                               hospital_id="SYN-000123", diabetes_status="t2")
    enc = ClinicalEncounter.objects.create(patient=p, encounter_date=DAY,
                                           next_due_date=date(2026, 9, 29),
                                           systolic_bp=138, diastolic_bp=86, weight_kg=64.5,
                                           advice="Visit note: oedema improving." if advice else "")
    rx = Prescription.objects.create(
        encounter=enc, diagnosis_text="Lupus nephritis class IV",
        comorbidities="Hypertension, Diabetes mellitus (Type 2), Bronchial asthma",
        investigations_advised="CBC, Serum creatinine, UPCR, Urine R/M/E, Lipid profile",
        advice=ADVICE if advice else "",
        stop_notes=("Losartan — replaced by ramipril (duplicate RAAS blockade)\n"
                    "Metformin — eGFR below threshold" if stopped else ""))
    drugs = _drugs()
    for i in range(n_items):
        d = drugs[i % len(drugs)]
        is_combo = d.generic_name == COMBO_GENERIC
        PrescriptionItem.objects.create(
            prescription=rx, drug=d, sort_order=i,
            brand=("Calbo-D Forte Plus" if is_combo else f"Brand{i + 1}"),
            strength=(COMBO_STRENGTH if is_combo else ["5 mg", "10 mg", "500 mg", "25 mg"][i % 4]),
            dose=("2" if dose_rows and i == 0 else ""), dose_unit=("tab" if dose_rows and i == 0 else ""),
            frequency=["1+0+0", "1+0+1", "1+1+1", "0+0+1"][i % 4],
            duration=["continue", "4 weeks", "12 weeks", "6 months"][i % 4],
            instruction_bn=("Take after meals" if i % 3 == 0 else ""),
            taper_notes=(TAPER if taper and i == 0 else ""))
    if final:
        finalize_prescription(rx, override_blocks=True)
        rx.refresh_from_db()
    return rx


SCENARIOS = {
    "01_one_item_final": dict(n_items=1, final=True, taper=False, stopped=False),
    "05_items_draft": dict(n_items=5),
    "10_items_final": dict(n_items=10, final=True),
    "15_items_long_name_final": dict(n_items=15, final=True, name=LONG_NAME),
}


def test_render_samples():
    from prescriptions.pdf import render_prescription_html, render_prescription_html_download
    out = Path(os.environ.get("PRINT_SAMPLES_OUT") or "print_samples")
    out.mkdir(parents=True, exist_ok=True)
    engines = []
    try:
        from weasyprint import HTML  # noqa: F401
        engines.append("weasyprint")
    except Exception:
        pass
    try:
        from xhtml2pdf import pisa  # noqa: F401
        engines.append("xhtml2pdf")
    except Exception:
        pass
    report = [f"engines available: {engines or 'none'}"]
    for key, spec in SCENARIOS.items():
        rx = _rx(**spec)
        html = render_prescription_html(rx)
        (out / f"{key}.html").write_text(html, encoding="utf-8")
        (out / f"{key}_download.html").write_text(
            render_prescription_html_download(rx), encoding="utf-8")
        for engine in engines:
            try:
                if engine == "weasyprint":
                    from weasyprint import HTML
                    data = HTML(string=html).write_pdf()
                else:
                    from io import BytesIO
                    from xhtml2pdf import pisa
                    buf = BytesIO()
                    status = pisa.pisaDocument(BytesIO(html.encode("utf-8")), buf,
                                               encoding="utf-8")
                    data = buf.getvalue() if not status.err else b""
                (out / f"{key}_{engine}.pdf").write_bytes(data)
                report.append(f"{key}: {engine} {len(data)} bytes")
            except Exception as exc:  # recorded, not hidden
                report.append(f"{key}: {engine} FAILED {exc!r}")
    (out / "render_report.txt").write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report))
