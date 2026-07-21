"""Exports app — no persistent models.

Data export is a *view-layer* feature: it reads from other apps' models and
writes CSV / Excel / SPSS files to EXPORTS_DIR.  No database tables needed.
"""
