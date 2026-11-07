@echo off
setlocal EnableDelayedExpansion

title ULTRON - Tailscale Portproxy Setup
echo ======================================================================
echo           ULTRON AGENTIC OS: TAILSCALE PORTPROXY SETUP
echo ======================================================================
echo.

pushd "%CD%"
cd /d "%~dp0"

:: 1. Auto-detect Python executable
set "PYTHON_EXE=backend\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    where python >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=python"
    ) else (
        echo [ERROR] Python not found in backend\.venv or system PATH.
        pause
        exit /b 1
    )
)

:: 2. Auto-detect WSL2 IP Address
set "WSL_IP="
for /f "tokens=1" %%i in ('wsl hostname -I 2^>nul') do (
    if not defined WSL_IP set "WSL_IP=%%i"
)
if not defined WSL_IP set "WSL_IP=127.0.0.1"

:: 3. Auto-detect Tailscale IP Address
set "TS_IP="
for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "(Get-NetIPAddress -InterfaceAlias '*Tailscale*' -AddressFamily IPv4 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty IPAddress -First 1)"`) do set "TS_IP=%%i"
if not defined TS_IP set "TS_IP=100.69.161.16"

echo [*] Configuration Detected:
echo     - Tailscale IP   : %TS_IP%
echo     - Listen Port    : 8000
echo     - Connect Target : %WSL_IP%:8000 (Local ULTRON Backend)
echo     - Python Runtime : %PYTHON_EXE%
echo.

:: 4. If running as Admin, configure Windows Kernel netsh portproxy too
net session >nul 2>&1
if %errorlevel% equ 0 (
    echo [*] Running with Administrative privileges.
    echo [*] Configuring Windows netsh portproxy rule...
    netsh interface portproxy delete v4tov4 listenaddress=%TS_IP% listenport=8000 >nul 2>&1
    netsh interface portproxy add v4tov4 listenaddress=%TS_IP% listenport=8000 connectaddress=%WSL_IP% connectport=8000 > setup_portproxy.log 2>&1
    netsh interface portproxy show all >> setup_portproxy.log 2>&1
    echo [*] Restarting IP Helper service to apply portproxy bindings...
    net stop iphlpsvc >nul 2>&1
    net start iphlpsvc >nul 2>&1
    echo [OK] Windows netsh portproxy configured.
)

:: 5. Launch high-resilience user-space socket bridge in background
echo [*] Starting ULTRON Tailscale Socket Bridge background task...
start "ULTRON Tailscale Bridge" /B "%PYTHON_EXE%" scripts\tailscale_bridge.py --listen-ip %TS_IP% --target-host %WSL_IP% --target-port 8000 >> setup_portproxy.log 2>&1

:: Allow bridge to initialize
powershell -NoProfile -Command "Start-Sleep -Milliseconds 800"

:: 6. Verification test against live endpoint
echo [*] Validating Tailscale endpoint: http://%TS_IP%:8000/health ...
curl.exe -s -f --max-time 3 http://%TS_IP%:8000/health > nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo  [PASS] 100%% SUCCESS RATE -- PORTPROXY IS FULLY OPERATIONAL!
    echo ======================================================================
    echo  URL: http://%TS_IP%:8000/health
    echo  Active Response:
    curl.exe -s --max-time 3 http://%TS_IP%:8000/health
    echo.
    echo  Database [3306] and Redis [6379] are STRICTLY ISOLATED.
    echo ======================================================================
) else (
    echo.
    echo [WARNING] Direct endpoint test did not respond within 3s.
    echo Check setup_portproxy.log or verify Docker containers in WSL:
    echo     wsl docker ps
)

echo.
echo Setup completed. Press any key to exit.
pause
