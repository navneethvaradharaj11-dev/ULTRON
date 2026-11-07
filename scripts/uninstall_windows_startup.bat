@echo off
setlocal EnableDelayedExpansion

title ULTRON - Remove Windows Startup Task
echo ======================================================================
echo           ULTRON AGENTIC OS: REMOVE AUTO-START
echo ======================================================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS_FILE=%STARTUP_FOLDER%\ultron_tailscale_startup.vbs"

if exist "%VBS_FILE%" (
    del "%VBS_FILE%"
    echo [PASS] Windows startup persistence removed successfully.
) else (
    echo [*] No startup persistence script was active.
)

echo.
pause

