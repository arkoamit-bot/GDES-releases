"""GDES WSGI server: waitress on loopback, behind Caddy.

Started at boot by the "GDES Server" scheduled task (run_server.bat).

Why a script and not waitress-serve.exe: this machine also runs the DKD
registry, whose watchdog, when it restarts DKD, kills every process whose
command line contains "waitress". Launched as `python gdes_serve.py`, this
process's command line never matches that filter, so a DKD restart cannot take
GDES down with it. Keep "waitress" out of this file's name and path.

Bind 127.0.0.1, never 0.0.0.0: Caddy is what faces the network.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bgddr.settings_server")

from waitress import serve  # noqa: E402

from bgddr.wsgi import application  # noqa: E402

serve(
    application,
    listen=os.environ.get("GDES_LISTEN", "127.0.0.1:8100"),
    # Threads, not workers: the constraint is how many clinicians save at the
    # same moment, not the CPU. Raise if clinicians report waiting.
    threads=int(os.environ.get("GDES_THREADS", "8")),
    max_request_body_size=31_457_280,      # 30 MB, matches Caddy's limit
    channel_timeout=60,
    ident="GDES",
)
