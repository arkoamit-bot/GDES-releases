"""Check pyreadstat.write_sav column_labels param."""
import pyreadstat
import inspect
sig = inspect.signature(pyreadstat.write_sav)
for name, param in sig.parameters.items():
    print(f"  {name}: {param.annotation} = {param.default!r}")
