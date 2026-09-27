@echo off
REM Run a Django management command against the SERVER database.
REM
REM   "E:\GDES server\deploy\windows\gdes-manage.bat" createsuperuser
REM   "E:\GDES server\deploy\windows\gdes-manage.bat" changepassword <user>
REM
REM Plain "python manage.py" uses the development settings and a different
REM (SQLite) database, so an account created that way would not exist here.
cd /d "E:\GDES server"
set DJANGO_SETTINGS_MODULE=bgddr.settings_server
set CELERY_BROKER_URL=
".venv\Scripts\python.exe" manage.py %*
