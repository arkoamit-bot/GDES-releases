@echo off
REM GDES reverse proxy on port 8080. Started at boot by the "GDES Caddy" task.
REM
REM The binary is a COPY of DKD's caddy.exe named gdes-caddy.exe. The DKD
REM watchdog restarts its proxy with "Get-Process caddy | Stop-Process", which
REM would kill this one too if it were called caddy.exe.
REM
REM XDG_* keeps this Caddy's state apart from DKD's (E:\dkdr-data\caddy).
cd /d "E:\GDES server"
set XDG_DATA_HOME=E:\gdes-data\caddy
set XDG_CONFIG_HOME=E:\gdes-data\caddy
"E:\gdes-data\bin\gdes-caddy.exe" run --config "E:\GDES server\deploy\windows\Caddyfile" >> "E:\gdes-data\app\Logs\caddy.out" 2>> "E:\gdes-data\app\Logs\caddy.err"
