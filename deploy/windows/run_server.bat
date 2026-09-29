@echo off
REM GDES WSGI server. Started at boot by the "GDES Server" scheduled task
REM (install.ps1). Listens on 127.0.0.1:8100 only; Caddy faces the network.
REM Settings and secrets come from "E:\GDES server\.env".
cd /d "E:\GDES server"
set PYTHONUNBUFFERED=1
set DJANGO_SETTINGS_MODULE=bgddr.settings_server
".venv\Scripts\python.exe" deploy\windows\gdes_serve.py >> "E:\gdes-data\app\Logs\server.out" 2>> "E:\gdes-data\app\Logs\server.err"
