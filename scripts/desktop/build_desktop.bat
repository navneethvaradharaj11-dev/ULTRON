@echo off
setlocal EnableDelayedExpansion

title ULTRON - Build Native Windows Executable
echo ======================================================================
echo           ULTRON AGENTIC OS: NATIVE DESKTOP BUILDER
echo ======================================================================
echo.

pushd "%CD%"
cd /d "%~dp0"

:: 1. Find Visual Studio
set "VS_PATH=C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"
if not exist "%VS_PATH%" (
    for /f "usebackq tokens=*" %%i in (`"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property installationPath`) do (
        set "VS_PATH=%%i\VC\Auxiliary\Build\vcvars64.bat"
    )
)

if not exist "%VS_PATH%" (
    echo [ERROR] Visual Studio C++ toolchain not found.
    pause
    exit /b 1
)

echo [*] Initializing Visual Studio toolchain: %VS_PATH%
call "%VS_PATH%" >nul 2>&1

:: 2. Compile Windows Resource
echo [*] Compiling resource script (app icon ^& version metadata)...
rc.exe ultron_res.rc

:: 3. Compile native C++ launcher
echo [*] Compiling ULTRON.exe native Windows executable...
cl.exe /O2 /W4 /EHsc /Fe:ULTRON.exe ultron_launcher.cpp ultron_res.res /link /SUBSYSTEM:WINDOWS wininet.lib shell32.lib >nul 2>&1

if exist "ULTRON.exe" (
    echo [PASS] ULTRON.exe successfully built!
    copy /Y "ULTRON.exe" "..\..\ULTRON.exe" >nul
    
    :: Copy to Desktop
    powershell -NoProfile -Command "$d = [Environment]::GetFolderPath('Desktop'); Copy-Item 'ULTRON.exe' $d\ULTRON.exe -Force; Write-Host '[OK] Copied to Desktop:' $d\ULTRON.exe"
) else (
    echo [ERROR] Compilation failed.
)

echo.
pause

