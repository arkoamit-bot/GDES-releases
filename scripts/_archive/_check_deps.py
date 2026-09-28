"""Check available packages for export writers."""
try:
    import openpyxl
    print("openpyxl: OK")
except ImportError:
    print("openpyxl: MISSING")

try:
    import pyreadstat
    print("pyreadstat: OK")
except ImportError:
    print("pyreadstat: MISSING")

try:
    import csv, io, zipfile
    print("stdlib csv/io/zipfile: OK")
except ImportError:
    print("stdlib: MISSING")
