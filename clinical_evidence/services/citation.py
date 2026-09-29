"""Citation manager — generates citations in multiple formats."""

import re
from datetime import date

from clinical_evidence.constants import CitationFormat


def _clean_authors(authors: str) -> list[str]:
    if not authors:
        return []
    return [a.strip() for a in re.split(r"[;,\,]+", authors) if a.strip()]


def _format_authors_apa(authors: list[str], max_authors: int = 6) -> str:
    if not authors:
        return ""
    parsed = []
    for a in authors:
        parts = a.rsplit(" ", 1)
        if len(parts) == 2:
            parsed.append(f"{parts[1]}, {parts[0][0]}.")
        else:
            parsed.append(a)
    if len(parsed) == 1:
        return parsed[0]
    if len(parsed) <= max_authors:
        return ", ".join(parsed[:-1]) + ", & " + parsed[-1]
    return ", ".join(parsed[:max_authors]) + ", ..."


def _format_authors_vancouver(authors: list[str]) -> str:
    if not authors:
        return ""
    parts = []
    for a in authors:
        name_parts = a.rsplit(" ", 1)
        if len(name_parts) == 2:
            initials = "".join(w[0].upper() for w in name_parts[0].split() if w)
            parts.append(f"{name_parts[1]} {initials}")
        else:
            parts.append(a)
    return ", ".join(parts)


def generate_apa(
    authors: str,
    publication_date: date | str | None,
    title: str,
    journal: str,
    volume: str = "",
    issue: str = "",
    pages: str = "",
    doi: str = "",
) -> str:
    author_list = _clean_authors(authors)
    author_part = _format_authors_apa(author_list)
    year = ""
    if publication_date:
        if isinstance(publication_date, date):
            year = str(publication_date.year)
        else:
            try:
                year = str(int(str(publication_date)[:4]))
            except (ValueError, TypeError):
                year = ""
    parts = [author_part, f"({year})", f"{title}."]
    journal_part = journal
    if volume:
        journal_part += f", {volume}"
        if issue:
            journal_part += f"({issue})"
    if pages:
        journal_part += f", {pages}"
    parts.append(f"{journal_part}.")
    if doi:
        parts.append(f"https://doi.org/{doi}")
    return " ".join(parts)


def generate_vancouver(
    authors: str,
    publication_date: date | str | None,
    title: str,
    journal: str,
    volume: str = "",
    issue: str = "",
    pages: str = "",
    pmid: str = "",
) -> str:
    author_list = _clean_authors(authors)
    author_part = _format_authors_vancouver(author_list)
    year = ""
    if publication_date:
        if isinstance(publication_date, date):
            year = str(publication_date.year)
        else:
            try:
                year = str(int(str(publication_date)[:4]))
            except (ValueError, TypeError):
                year = ""
    parts = [f"{author_part}.", f"{title}.", f"{journal}"]
    if year:
        parts[-1] += f" {year}"
    if volume:
        parts[-1] += f";{volume}"
        if issue:
            parts[-1] += f"({issue})"
    if pages:
        parts[-1] += f":{pages}"
    parts.append("")
    if pmid:
        parts.append(f"PMID: {pmid}")
    return " ".join(parts)


def generate_bibtex(
    authors: str,
    publication_date: date | str | None,
    title: str,
    journal: str,
    doi: str = "",
    pmid: str = "",
    volume: str = "",
    issue: str = "",
    pages: str = "",
) -> str:
    year = ""
    if publication_date:
        if isinstance(publication_date, date):
            year = str(publication_date.year)
        else:
            try:
                year = str(int(str(publication_date)[:4]))
            except (ValueError, TypeError):
                year = ""
    first_author = _clean_authors(authors)[0].split()[-1] if authors else "Unknown"
    cite_key = f"{first_author}{year}"
    fields = [
        f"  title = {{{title}}}",
        f"  author = {{{authors}}}",
        f"  journal = {{{journal}}}",
    ]
    if year:
        fields.append(f"  year = {{{year}}}")
    if volume:
        fields.append(f"  volume = {{{volume}}}")
    if issue:
        fields.append(f"  number = {{{issue}}}")
    if pages:
        fields.append(f"  pages = {{{pages}}}")
    if doi:
        fields.append(f"  doi = {{{doi}}}")
    if pmid:
        fields.append(f"  pmid = {{{pmid}}}")
    return f"@article{{{cite_key},\n" + ",\n".join(fields) + "\n}"


def generate_ris(
    authors: str,
    publication_date: date | str | None,
    title: str,
    journal: str,
    doi: str = "",
    pmid: str = "",
    volume: str = "",
    issue: str = "",
    pages: str = "",
    abstract: str = "",
) -> str:
    lines = ["TY  - JOUR"]
    for author in _clean_authors(authors):
        lines.append(f"AU  - {author}")
    lines.append(f"TI  - {title}")
    lines.append(f"JO  - {journal}")
    if publication_date:
        if isinstance(publication_date, date):
            lines.append(f"PY  - {publication_date.year}")
        else:
            try:
                lines.append(f"PY  - {str(publication_date)[:4]}")
            except (ValueError, TypeError):
                pass
    if volume:
        lines.append(f"VL  - {volume}")
    if issue:
        lines.append(f"IS  - {issue}")
    if pages:
        lines.append(f"SP  - {pages.split('-')[0]}")
        if "-" in pages:
            lines.append(f"EP  - {pages.split('-')[1]}")
    if doi:
        lines.append(f"DO  - {doi}")
    if pmid:
        lines.append(f"SN  - {pmid}")
    if abstract:
        lines.append(f"AB  - {abstract}")
    lines.append("ER  - ")
    return "\r\n".join(lines)


def generate_all(
    authors: str = "",
    publication_date: date | str | None = None,
    title: str = "",
    journal: str = "",
    doi: str = "",
    pmid: str = "",
    pmcid: str = "",
    volume: str = "",
    issue: str = "",
    pages: str = "",
    abstract: str = "",
) -> dict[str, str]:
    kwargs = {
        "authors": authors,
        "publication_date": publication_date,
        "title": title,
        "journal": journal,
        "volume": volume,
        "issue": issue,
        "pages": pages,
        "doi": doi,
        "pmid": pmid,
    }
    return {
        "apa": generate_apa(**kwargs),
        "vancouver": generate_vancouver(**kwargs),
        "bibtex": generate_bibtex(**kwargs),
        "ris": generate_ris(**kwargs, abstract=abstract),
    }


def generate(results) -> dict:
    """Generate all citation formats for a list of EvidenceResult objects."""
    citations = {}
    for r in results:
        try:
            c = generate_all(
                authors=r.authors,
                publication_date=r.publication_date,
                title=r.title,
                journal=r.journal,
                doi=r.doi,
                pmid=r.pmid,
                abstract=r.abstract,
            )
            citations[r.pk] = c
        except Exception:
            citations[r.pk] = {
                "apa": r.title,
                "vancouver": r.title,
                "bibtex": "",
                "ris": "",
            }
    return citations
