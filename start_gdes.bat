@echo off
cd /d "%~dp0"
echo Starting GDES (secure desktop mode)...
set DJANGO_SETTINGS_MODULE=bgddr.settings_desktop
python manage.py runserver 127.0.0.1:8000
pause
