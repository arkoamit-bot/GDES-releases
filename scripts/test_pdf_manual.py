"""
Quick test of the PDF fallback chain (WeasyPrint -> xhtml2pdf -> HTML).
Run this to verify prescription printing works without GTK3.
"""
from pathlib import Path

from django.conf import settings
import django

# Minimal Django setup for testing
if not settings.configured:
    django.setup()

from prescriptions.models import Prescription

# Test with the most recent prescription
rx = Prescription.objects.order_by("-id").first()
if not rx:
    print("No prescriptions in database. Create one first via the UI.")
    exit(1)

print(f"Testing PDF generation for prescription {rx.id} ({rx.patient.patient_id})")

# 1. Try WeasyPrint
print("\n1. WeasyPrint...")
try:
    from prescriptions.pdf import render_prescription_pdf
    data = render_prescription_pdf(rx)
    out = Path("media/prescriptions/test_weasyprint.pdf")
    out.write_bytes(data)
    print(f"   OK -> {out} ({len(data)} bytes)")
except Exception as exc:
    print(f"   FAIL: {exc}")

# 2. Try xhtml2pdf
print("\n2. xhtml2pdf...")
try:
    from prescriptions.pdf import render_prescription_html
    from xhtml2pdf import pisa
    from io import BytesIO
    html = render_prescription_html(rx)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result, encoding="utf-8")
    if not pdf.err:
        out = Path("media/prescriptions/test_xhtml2pdf.pdf")
        out.write_bytes(result.getvalue())
        print(f"   OK -> {out} ({len(result.getvalue())} bytes)")
    else:
        print(f"   FAIL: {pdf.err}")
except Exception as exc:
    print(f"   FAIL: {exc}")

# 3. HTML fallback
print("\n3. HTML download...")
try:
    from prescriptions.pdf import render_prescription_html_download
    html = render_prescription_html_download(rx)
    out = Path("media/prescriptions/test_fallback.html")
    out.write_text(html, encoding="utf-8")
    print(f"   OK -> {out} ({len(html)} chars)")
except Exception as exc:
    print(f"   FAIL: {exc}")

print("\nDone. Check media/prescriptions/ for output files.")
