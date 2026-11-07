@echo off
setlocal EnableDelayedExpansion

title ULTRON - Personal Agentic Operating System
cd /d "%~dp0"

:MENU
cls
echo ==============================================================================
echo   UU   UU  LL      TTTTTTT  RRRRRR    OOOOO   NN   NN
echo   UU   UU  LL        TTT    RR   RR  OO   OO  NNN  NN   PROJECT ULTRON
echo   UU   UU  LL        TTT    RRRRRR   OO   OO  NN N NN   Agentic AI Operating System
echo   UU   UU  LL        TTT    RR  RR   OO   OO  NN  NNN   Phases 1-18 Production Ready
echo    UUUUU   LLLLLLL   TTT    RR   RR   OOOOO   NN   NN   [Zero Cloud Budget Mesh]
echo ==============================================================================
echo.

:: Detect Python
set "PYTHON_EXE=backend\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    where python >nul 2>&1
    if !errorlevel! equ 0 set "PYTHON_EXE=python"
)

:: Detect Tailscale IP
set "TS_IP="
for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "(Get-NetIPAddress -InterfaceAlias '*Tailscale*' -AddressFamily IPv4 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty IPAddress -First 1)"`) do set "TS_IP=%%i"
if not defined TS_IP set "TS_IP=100.69.161.16"

echo [*] Target Gateway : http://%TS_IP%:8000
echo [*] Python Runtime : %PYTHON_EXE%
echo.
echo ==============================================================================
echo   CONTROL COMMANDS:
echo ==============================================================================
echo   [1] Start ULTRON (WSL Docker Stack + Tailscale Bridge)
echo   [2] Check System Health Probes & AI Diagnostics
echo   [3] Launch Interactive Terminal Chat with ULTRON
echo   [4] Run Full Test Battery (276 Pytest + 12 Flutter Tests)
echo   [5] Build Android Mobile APK (with Auto-Gateway Configuration)
echo   [6] Host Wireless APK Download Portal (One-Tap for Galaxy A16 5G)
echo   [7] Install APK via USB Cable (ADB Auto-Installer)
echo   [8] Configure AI Credentials (NVIDIA NIM / Gemini / OpenAI)
echo   [9] Configure Windows Boot Auto-Start (Silent Persistence)
echo   [10] Stop ULTRON Services Safely
echo   [11] Open Documentation / Runbooks
echo   [12] Exit
echo ==============================================================================
set /p "CHOICE=Select an option [1-12]: "

if "%CHOICE%"=="1" goto START_SYSTEM
if "%CHOICE%"=="2" goto HEALTH_CHECK
if "%CHOICE%"=="3" goto CHAT_CLI
if "%CHOICE%"=="4" goto RUN_TESTS
if "%CHOICE%"=="5" goto BUILD_APK
if "%CHOICE%"=="6" goto SERVE_APK
if "%CHOICE%"=="7" goto INSTALL_PHONE
if "%CHOICE%"=="8" goto CONFIGURE_AI
if "%CHOICE%"=="9" goto AUTO_START
if "%CHOICE%"=="10" goto STOP_SYSTEM
if "%CHOICE%"=="11" goto OPEN_DOCS
if "%CHOICE%"=="12" goto EXIT_APP
goto MENU

:START_SYSTEM
echo.
echo [*] Booting WSL Docker Containers...
wsl docker start ultron_mysql ultron_redis ultron_backend ultron_worker ultron_proxy
echo [*] Starting Tailscale Bridge...
start /min "ULTRON Tailscale Bridge" "%PYTHON_EXE%" scripts\tailscale_bridge.py
timeout /t 2 >nul
echo.
echo [PASS] ULTRON is online and listening on http://%TS_IP%:8000
pause
goto MENU

:HEALTH_CHECK
echo.
echo [*] Querying System Health on http://%TS_IP%:8000/health...
curl.exe -s http://%TS_IP%:8000/health
echo.
echo.
echo [*] Querying AI Engine Status on http://%TS_IP%:8000/api/v1/ai/status...
curl.exe -s http://%TS_IP%:8000/api/v1/ai/status
echo.
echo.
pause
goto MENU

:CHAT_CLI
echo.
echo [*] Launching ULTRON Interactive Chat Console...
"%PYTHON_EXE%" scripts\chat_cli.py
pause
goto MENU

:RUN_TESTS
echo.
echo [*] Executing Full 276-Test Backend Regression Battery...
"%PYTHON_EXE%" -m pytest tests
echo.
echo [*] Executing Flutter Mobile Test Battery...
cd frontend\flutter_app
call flutter test
cd ..\..
echo.
echo [PASS] Test Battery Finished.
pause
goto MENU

:BUILD_APK
echo.
echo [*] Compiling Production-Ready Android Debug APK...
cd frontend\flutter_app
call flutter build apk --debug
cd ..\..
echo.
echo [PASS] Binary generated at: frontend\flutter_app\build\app\outputs\flutter-apk\app-debug.apk
pause
goto MENU

:SERVE_APK
echo.
echo [*] Starting Wireless APK Download Portal for phone...
"%PYTHON_EXE%" scripts\serve_apk.py
goto MENU

:INSTALL_PHONE
echo.
call scripts\install_apk_phone.bat
goto MENU

:CONFIGURE_AI
echo.
"%PYTHON_EXE%" scripts\configure_ai.py
pause
goto MENU

:AUTO_START
echo.
echo [1] Install Auto-Start on Windows Login
echo [2] Remove Auto-Start
set /p "AS_CHOICE=Select [1-2]: "
if "%AS_CHOICE%"=="1" call scripts\install_windows_startup.bat
if "%AS_CHOICE%"=="2" call scripts\uninstall_windows_startup.bat
goto MENU

:STOP_SYSTEM
echo.
echo [*] Stopping Tailscale Bridge...
call remove_portproxy.bat
echo [*] Halting Docker Containers...
wsl docker stop ultron_backend ultron_worker ultron_proxy
echo.
echo [OK] ULTRON Services stopped.
pause
goto MENU

:OPEN_DOCS
echo.
echo Opening Roadmap Completion Report...
start "" "docs\ROADMAP_COMPLETION_REPORT.md"
goto MENU

:EXIT_APP
echo Exiting ULTRON console.
exit /b 0

