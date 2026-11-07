@echo off
setlocal EnableDelayedExpansion

title ULTRON - Remove Tailscale Portproxy
echo ======================================================================
echo           ULTRON AGENTIC OS: REMOVE TAILSCALE PORTPROXY
echo ======================================================================
echo.

pushd "%CD%"
cd /d "%~dp0"

:: 1. Auto-detect Python and stop socket bridge
set "PYTHON_EXE=backend\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    where python >nul 2>&1
    if !errorlevel! equ 0 set "PYTHON_EXE=python"
)

if exist "%PYTHON_EXE%" (
    echo [*] Stopping ULTRON Tailscale Bridge process...
    "%PYTHON_EXE%" scripts\tailscale_bridge.py --stop >nul 2>&1
)

:: Also kill by window title or process name if running
taskkill /FI "WINDOWTITLE eq ULTRON Tailscale Bridge*" /F >nul 2>&1

:: 2. Auto-detect Tailscale IP
set "TS_IP="
for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "(Get-NetIPAddress -InterfaceAlias '*Tailscale*' -AddressFamily IPv4 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty IPAddress -First 1)"`) do set "TS_IP=%%i"
if not defined TS_IP set "TS_IP=100.69.161.16"

:: 3. Remove Windows netsh portproxy rule if Admin
net session >nul 2>&1
if %errorlevel% equ 0 (
    echo [*] Removing Windows netsh portproxy rule for %TS_IP%:8000...
    netsh interface portproxy delete v4tov4 listenaddress=%TS_IP% listenport=8000 >nul 2>&1
    netsh interface portproxy delete v4tov4 listenaddress=100.69.161.16 listenport=8000 >nul 2>&1
    echo [OK] Windows netsh rule removed.
) else (
    echo [NOTE] Standard user mode: Socket bridge stopped. To remove netsh rule run as administrator.
)

echo.
echo ----------------------------------------------------------------------
echo Current Portproxy Configuration:
echo ----------------------------------------------------------------------
netsh interface portproxy show all 2>nul
echo ----------------------------------------------------------------------
echo.
echo Rollback completed successfully.
pause
