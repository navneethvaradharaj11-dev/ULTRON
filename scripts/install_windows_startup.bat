@echo off
setlocal EnableDelayedExpansion

title ULTRON - Install Windows Startup Task
echo ======================================================================
echo           ULTRON AGENTIC OS: CONFIGURE AUTO-START ON BOOT
echo ======================================================================
echo.

pushd "%CD%"
cd /d "%~dp0.."

set "PROJECT_ROOT=%CD%"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS_FILE=%STARTUP_FOLDER%\ultron_tailscale_startup.vbs"
set "BAT_FILE=%PROJECT_ROOT%\setup_portproxy.bat"

echo [*] Target Project Path: %PROJECT_ROOT%
echo [*] Startup Folder     : %STARTUP_FOLDER%
echo.

:: Generate silent VBScript background launcher in Startup folder
echo ' ULTRON Auto-Start on Windows Login > "%VBS_FILE%"
echo Set WshShell = CreateObject("WScript.Shell") >> "%VBS_FILE%"
echo WshShell.CurrentDirectory = "%PROJECT_ROOT%" >> "%VBS_FILE%"
echo ' Start WSL keepalive and docker containers silently >> "%VBS_FILE%"
echo WshShell.Run "wsl -d Ubuntu-22.04 docker start ultron_mysql ultron_redis ultron_backend ultron_worker ultron_proxy", 0, True >> "%VBS_FILE%"
echo ' Start Tailscale Bridge in background >> "%VBS_FILE%"
echo WshShell.Run "cmd.exe /c """"%PROJECT_ROOT%\setup_portproxy.bat""""", 0, False >> "%VBS_FILE%"

if exist "%VBS_FILE%" (
    echo [PASS] Windows startup persistence installed successfully!
    echo        File: %VBS_FILE%
    echo.
    echo ULTRON and the Tailscale bridge will now start automatically
    echo in the background whenever Windows boots or you log in.
) else (
    echo [ERROR] Failed to write startup file to %VBS_FILE%
)

echo.
pause

