"""Serialise the research dataset to CSV (stdlib) or Excel (openpyxl, optional)."""
from __future__ import annotations

import csv
import io


def _cell(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return 1 if v else 0          # 0/1 is friendlier for stats packages
    return v


def to_csv(columns, rows) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(columns)
    for r in rows:
        writer.writerow([_cell(r.get(c)) for c in columns])
    return buf.getvalue()


class ExcelUnavailable(RuntimeError):
    pass


def to_xlsx(columns, rows, *, dictionary=None, dictionary_columns=None) -> bytes:
    """Research dataset as XLSX. When ``dictionary`` is given, it is written as a
    second 'data_dictionary' sheet so the codebook travels with the data."""
    try:
        from openpyxl import Workbook
        from openpyxl.utils import get_column_letter
    except Exception as exc:
        raise ExcelUnavailable(
            "openpyxl is not installed — use the CSV export, or `pip install openpyxl`."
        ) from exc

    def _sheet(ws, cols, data):
        ws.append(cols)
        for r in data:
            ws.append([_cell(r.get(c)) for c in cols])
        ws.freeze_panes = "A2"
        for i, c in enumerate(cols, start=1):
            ws.column_dimensions[get_column_letter(i)].width = max(12, min(len(c) + 2, 40))

    wb = Workbook()
    ws = wb.active
    ws.title = "research_dataset"
    _sheet(ws, columns, rows)
    if dictionary:
        _sheet(wb.create_sheet("data_dictionary"),
               dictionary_columns or ["column", "type", "units_or_values", "description"],
               dictionary)
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


class SavUnavailable(RuntimeError):
    pass


# Dictionary "type" values that should become SPSS numeric variables.
_SAV_NUMERIC = {"integer", "float", "boolean", "ordinal"}


def _sav_num(v):
    """Coerce a cell to something numeric (or None) for an SPSS numeric column."""
    if v is None or v == "":
        return None
    if isinstance(v, bool):
        return 1 if v else 0
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def to_sav(columns, rows, *, defs=None) -> bytes:
    """Research dataset as an SPSS ``.sav`` file (pyreadstat).

    ``defs`` is a ``{column: (type, units_or_values, description)}`` map (from
    ``exports.services.dictionary.column_defs``). It drives, per variable:
      * the variable LABEL (the human description),
      * the measurement level (scale / ordinal / nominal), and
      * value labels for 0/1 boolean flags (0=No, 1=Yes).
    Numeric dictionary types become SPSS numeric variables; everything else is
    written as an SPSS string variable. Missing values become SPSS system-missing.
    """
    try:
        import pandas as pd
        import pyreadstat
    except Exception as exc:  # pragma: no cover - exercised only when uninstalled
        raise SavUnavailable(
            "pyreadstat/pandas are not installed — use the CSV or Excel export, "
            "or `pip install pyreadstat pandas`."
        ) from exc

    import os
    import tempfile

    defs = defs or {}
    columns = list(columns)

    data, column_labels, measure, value_labels = {}, [], {}, {}
    for c in columns:
        t, _units, desc = defs.get(c, ("", "", ""))
        column_labels.append((desc or c)[:255])  # SPSS label limit
        if t in _SAV_NUMERIC:
            data[c] = [_sav_num(r.get(c)) for r in rows]
            if t == "boolean":
                measure[c] = "nominal"
                value_labels[c] = {0.0: "No", 1.0: "Yes"}
            elif t == "ordinal":
                measure[c] = "ordinal"
            else:
                measure[c] = "scale"
        else:
            data[c] = [None if r.get(c) is None else str(r.get(c)) for r in rows]
            measure[c] = "nominal"

    df = pd.DataFrame(data, columns=columns)

    tmp = tempfile.NamedTemporaryFile(suffix=".sav", delete=False)
    tmp.close()
    try:
        pyreadstat.write_sav(
            df, tmp.name,
            column_labels=column_labels,
            variable_measure=measure,
            variable_value_labels=value_labels,
        )
        with open(tmp.name, "rb") as f:
            return f.read()
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
