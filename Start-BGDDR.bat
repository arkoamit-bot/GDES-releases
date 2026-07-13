@echo off
rem ===================================================================
rem  BGDDR Registry - double-click launcher (no console window).
rem  Works immediately from source using the installed Python, before
rem  (or instead of) building BGDDR.exe. Logs go to Logs\bgddr.log.
rem ===================================================================
cd /d "%~dp0"

rem Prefer pythonw (no console). Fall back to python if unavailable.
where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw "%~dp0desktop\launcher.py"
) else (
    start "" python "%~dp0desktop\launcher.py"
)
