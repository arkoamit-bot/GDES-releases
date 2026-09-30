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


def render_context(prescription) -> dict:
    """Template context: the frozen issued snapshot for a prescription issued
    with one; the live linked records for a draft (and, flagged, for one
    finalized before snapshots existed)."""
    from .services.issue import view_model
    vm = view_model(prescription)
    return {
        "rx": prescription,
        "s": vm["s"],
        "legacy_live": vm["legacy_live"],
        "has_dose": any(it.get("dose") for it in vm["s"].get("items", [])),
        "bn_font_face": _bengali_font_face_css(),
    }


def render_prescription_html(prescription, *, simple_pdf: bool = False) -> str:
    """`simple_pdf` drops what xhtml2pdf cannot draw (the faded diagonal DRAFT
    watermark); the DRAFT banner still prints."""
    ctx = render_context(prescription)
    ctx["simple_pdf"] = simple_pdf
    return render_to_string("prescriptions/prescription.html", ctx)


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
        simple = render_prescription_html(prescription, simple_pdf=True)
        pdf = pisa.pisaDocument(BytesIO(simple.encode("utf-8")), result,
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
      btn.className = 'no-print';
      btn.style.cssText = 'position:fixed;top:12px;right:12px;padding:8px 14px;'
        + 'font-size:14px;background:#26215C;color:#fff;border:0;border-radius:6px;cursor:pointer;';
      btn.onclick = function(){ window.print(); };
      document.body.appendChild(btn);
    });
    </script>
    <style>@media print{ .no-print{ display:none !important; } }</style>
    """
    return html.replace("</body>", extra + "\n</body>")


def render_prescription_html_print(prescription) -> str:
    """The slip as a stand-alone page that opens the print dialog on load.

    Printing the slip as its own top-level document is the reliable route.
    Printing the preview page (the slip inside an iframe under the app's own
    layout) came out as extra blank pages on real printers, with the slip
    pushed onto a later page.
    """
    html = render_prescription_html(prescription)
    extra = """
    <script>
    window.addEventListener('load', function(){
      setTimeout(function(){ window.print(); }, 400);
    });
    </script>
    """
    return html.replace("</body>", extra + "</body>")


def save_prescription_pdf(prescription, data: bytes) -> Path | None:
    """Archive a FINALIZED prescription's PDF under MEDIA_ROOT/prescriptions/.

    The first archived file is the original and is never overwritten: a later
    download (after a template or font change) is served but not archived over
    it. Drafts are never archived.
    """
    if not prescription.is_final:
        return None
    pdf_dir = getattr(settings, "PRESCRIPTION_PDF_DIR",
                      Path(settings.BASE_DIR) / "media" / "prescriptions")
    pdf_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{prescription.patient.patient_id}_v{prescription.version}_{prescription.pk}.pdf"
    path = pdf_dir / fname
    if path.exists():
        return path
    path.write_bytes(data)
    return path
