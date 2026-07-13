"""
Render a finalized prescription to PDF, with multiple engine backends.

1. WeasyPrint (best quality, needs native cairo/pango/GTK).
2. xhtml2pdf (pure-Python fallback, no native deps).
3. HTML download (always works; user opens in browser and prints).

The Bengali font is embedded when available so bilingual instructions print
correctly anywhere.
"""
from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.template.loader import render_to_string


class PDFEngineUnavailable(RuntimeError):
    pass


def _bengali_font_face_css() -> str:
    """@font-face pointing at the bundled Bengali TTF, if present."""
    path = getattr(settings, "BENGALI_FONT_PATH", None)
    if path and path.exists():
        uri = path.as_uri()
        return (
            "@font-face{font-family:'Bn';"
            f"src:url('{uri}') format('truetype');font-weight:normal;}}"
        )
    return ""


def render_prescription_html(prescription) -> str:
    return render_to_string("prescriptions/prescription.html", {
        "rx": prescription,
        "patient": prescription.patient,
        "encounter": prescription.encounter,
        "items": prescription.items.select_related("drug").all(),
        "clinic": settings.CLINIC,
        "bn_font_face": _bengali_font_face_css(),
    })


def render_prescription_pdf(prescription) -> bytes:
    """Try engines in order: WeasyPrint → xhtml2pdf → raise with helpful msg."""
    html = render_prescription_html(prescription)

    # 1. WeasyPrint (best fidelity)
    try:
        from weasyprint import HTML
        return HTML(string=html, base_url=str(settings.BASE_DIR)).write_pdf()
    except Exception:
        pass  # fallback

    # 2. xhtml2pdf (pure-Python, no native deps)
    try:
        from xhtml2pdf import pisa
        from io import BytesIO
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result,
                                encoding="utf-8")
        if not pdf.err:
            return result.getvalue()
    except Exception:
        pass  # fallback

    # 3. Nothing worked — raise with actionable message
    raise PDFEngineUnavailable(
        "No PDF engine is available. Install WeasyPrint + GTK (best quality) "
        "or xhtml2pdf (pure-Python fallback). The HTML preview still works."
    )


def render_prescription_html_download(prescription) -> str:
    """Return an HTML file the user can open in a browser and print.
    Includes a print-friendly stylesheet."""
    html = render_prescription_html(prescription)
    # Inject a print button and auto-print hint
    extra = """
    <script>
    window.addEventListener('load', function(){
      var btn = document.createElement('button');
      btn.textContent = 'Print / Save as PDF';
      btn.style.cssText = 'position:fixed;top:12px;right:12px;padding:8px 14px;'
        + 'font-size:14px;background:#26215C;color:#fff;border:0;border-radius:6px;cursor:pointer;';
      btn.onclick = function(){ window.print(); };
      document.body.appendChild(btn);
    });
    </script>
    <style>@media screen{ body{ margin:20px; } }</style>
    """
    return html.replace("</body>", extra + "\n</body>")


def save_prescription_pdf(prescription, data: bytes) -> Path:
    """Persist a finalized prescription PDF to MEDIA_ROOT/prescriptions/."""
    pdf_dir = getattr(settings, "PRESCRIPTION_PDF_DIR",
                      Path(settings.BASE_DIR) / "media" / "prescriptions")
    pdf_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{prescription.patient.patient_id}_v{prescription.version}_{prescription.pk}.pdf"
    path = pdf_dir / fname
    path.write_bytes(data)
    return path
