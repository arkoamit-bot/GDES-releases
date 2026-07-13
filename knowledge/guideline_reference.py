"""Import a guideline (e.g. a KDIGO PDF) as a CITABLE REFERENCE document.

This does NOT create clinical rules — turning guideline prose into executable
rules requires clinical authoring and cannot be done safely by an automated
parser. Instead it downloads/extracts the guideline text and stores it as a
``GuidelineDocument`` under a ``GuidelineSource`` so that knowledge-base rules
can cite it (via evidence_url / guideline_quote / guideline_chapter) and a
clinician can read the source text inside the app.

Text extraction uses ``pypdf`` (PDFs) and falls back to plain-text decoding.
"""
from __future__ import annotations

import io
from datetime import date

from .models import GuidelineDocument, GuidelineSource


def _extract_pdf_text(raw: bytes) -> tuple[str, int]:
    """Return (text, page_count) from PDF bytes using pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise ValueError("pypdf is required to read PDF guidelines.") from exc

    reader = PdfReader(io.BytesIO(raw))
    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:  # noqa: BLE001 — skip unreadable page, keep going
            pages.append("")
    return "\n\n".join(pages).strip(), len(reader.pages)


def _extract_html_text(raw: bytes) -> tuple[str, int]:
    """Extract readable text from an HTML page (drops nav/script/style boilerplate)."""
    from lxml import html as lxml_html

    try:
        doc = lxml_html.fromstring(raw)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Could not parse the HTML page: {exc}") from exc

    for bad in doc.xpath("//script | //style | //noscript | //nav | //header | //footer"):
        parent = bad.getparent()
        if parent is not None:
            parent.remove(bad)

    # Prefer the main article body if the page marks one; else fall back to <body>.
    nodes = doc.xpath("//article") or doc.xpath("//main")
    if not nodes:
        body = doc.find("body")
        nodes = [body] if body is not None else [doc]

    text = "\n".join(n.text_content() for n in nodes)
    lines = [ln.strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln).strip(), 1


def _looks_like_html(raw: bytes, filename: str, content_type: str) -> bool:
    head = raw[:512].lstrip().lower()
    return (
        "html" in (content_type or "").lower()
        or filename.lower().endswith((".html", ".htm"))
        or head.startswith(b"<!doctype html")
        or head.startswith(b"<html")
    )


def _extract_text(raw: bytes, filename: str = "", content_type: str = "") -> tuple[str, int]:
    is_pdf = (
        raw[:5] == b"%PDF-"
        or filename.lower().endswith(".pdf")
        or "pdf" in (content_type or "").lower()
    )
    if is_pdf:
        return _extract_pdf_text(raw)
    if _looks_like_html(raw, filename, content_type):
        return _extract_html_text(raw)
    # Plain text / markdown fallback.
    try:
        return raw.decode("utf-8").strip(), 1
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace").strip(), 1


def import_guideline_reference(
    *,
    raw: bytes,
    abbreviation: str,
    version_year: int,
    title: str = "",
    filename: str = "",
    source_url: str = "",
    content_type: str = "",
) -> dict:
    """Store a guideline as a citable reference. Returns a summary dict."""
    abbreviation = (abbreviation or "").strip()
    if not abbreviation:
        raise ValueError("A source abbreviation (e.g. 'KDIGO') is required.")
    if not version_year:
        raise ValueError("A source year (e.g. 2025) is required.")

    text, pages = _extract_text(raw, filename=filename, content_type=content_type)
    if not text:
        raise ValueError(
            "No text could be extracted from the file. If this is a scanned "
            "(image-only) PDF, it needs OCR before it can be stored as text."
        )

    # Publisher article pages (Elsevier, etc.) commonly return a cookie/bot
    # challenge or a paywall stub instead of the article. Refuse to store a
    # near-empty or challenge page as if it were the guideline.
    lowered = text[:600].lower()
    bot_wall = any(s in lowered for s in (
        "requires cookies", "enable cookies", "cookies to be enabled",
        "are you a robot", "verify you are human", "access denied",
        "please enable javascript", "subscribe to", "sign in to",
    ))
    if len(text) < 400 or bot_wall:
        raise ValueError(
            "The link did not return readable article text (it looks like a "
            "cookie/bot check or a paywall — common on journal 'fulltext' pages). "
            "Download the article PDF and upload it here, or use a direct PDF link."
        )

    doc_title = (title or "").strip() or filename or f"{abbreviation} {version_year} guideline"

    source, created_source = GuidelineSource.objects.get_or_create(
        abbreviation=abbreviation,
        version_year=version_year,
        defaults={
            "title": doc_title,
            "effective_date": date(int(version_year), 1, 1),
            "url": source_url or "",
        },
    )
    # Backfill the source URL if it was missing.
    if source_url and not source.url:
        source.url = source_url
        source.save(update_fields=["url"])

    doc = GuidelineDocument.objects.create(
        title=doc_title,
        source=source,
        document_type=GuidelineDocument.DocType.TEXT,
        content=text,
        import_status=GuidelineDocument.ImportStatus.COMPLETE,
        import_log=(
            f"Reference import: {pages} page(s), {len(text)} chars"
            + (f", from {source_url}" if source_url else "")
        ),
    )

    return {
        "source": str(source),
        "source_created": created_source,
        "document_id": doc.id,
        "document_title": doc_title,
        "pages": pages,
        "chars": len(text),
    }


def import_guideline_reference_from_url(
    url: str, *, abbreviation: str, version_year: int, title: str = "",
) -> dict:
    from .kb_update import download_bytes

    raw = download_bytes(url)
    return import_guideline_reference(
        raw=raw, abbreviation=abbreviation, version_year=version_year,
        title=title, filename=url.rsplit("/", 1)[-1], source_url=url,
    )
