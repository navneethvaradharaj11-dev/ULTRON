@echo off
setlocal EnableDelayedExpansion

title ULTRON - Samsung Galaxy A16 5G Mobile Deployment
echo ==============================================================================
echo        ULTRON AGENTIC OS: MOBILE APK INSTALLER (GALAXY A16 5G)
echo ==============================================================================
echo.

pushd "%CD%"
cd /d "%~dp0.."

set "APK_PATH=frontend\flutter_app\build\app\outputs\flutter-apk\app-debug.apk"
if not exist "%APK_PATH%" (
    echo [*] APK not found. Compiling Flutter APK first...
    cd frontend\flutter_app
    call flutter build apk --debug
    cd ..\..
)

:: Locate ADB
set "ADB_EXE=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"
if not exist "%ADB_EXE%" (
    where adb >nul 2>&1
    if !errorlevel! equ 0 (
        set "ADB_EXE=adb"
    ) else (
        echo [ERROR] ADB not found in %LOCALAPPDATA%\Android\Sdk or PATH.
        echo Please ensure Android SDK platform-tools is installed.
        pause
        exit /b 1
    )
)

echo [*] ADB Runtime : %ADB_EXE%
echo [*] Target APK  : %APK_PATH%
echo.
echo [*] Checking for connected devices...
"%ADB_EXE%" devices -l

:: Count devices
set "DEV_COUNT=0"
for /f "skip=1 tokens=1" %%d in ('"%ADB_EXE%" devices') do (
    if not "%%d"=="" set /a DEV_COUNT+=1
)

if %DEV_COUNT% gtr 0 (
    echo.
    echo [PASS] Android device detected!
    echo [*] Installing ULTRON debug APK...
    "%ADB_EXE%" install -r "%APK_PATH%"
    if !errorlevel! equ 0 (
        echo.
        echo [SUCCESS] ULTRON installed on your phone successfully!
        echo [*] Launching ULTRON on device...
        "%ADB_EXE%" shell monkey -p com.example.flutter_app -c android.intent.category.LAUNCHER 1 >nul 2>&1
    ) else (
        echo [ERROR] Installation failed. Check device screen for permission prompt.
    )
) else (
    echo.
    echo [!] No Android device detected via USB.
    echo.
    echo HOW TO CONNECT YOUR SAMSUNG GALAXY A16 5G:
    echo 1. Connect phone to PC using a USB-C data cable.
    echo 2. On your phone: Go to Settings ^> About phone ^> Software information.
    echo 3. Tap 'Build number' 7 times until Developer mode is enabled.
    echo 4. Go to Settings ^> Developer options ^> Turn ON 'USB debugging'.
    echo 5. When the prompt appears on your phone screen, tap 'Always allow from this computer'.
    echo 6. Re-run this script to automatically install!
    echo.
    echo ALTERNATIVE WIRELESS ADB:
    echo If phone is on same Wi-Fi: Developer options ^> Wireless debugging ^> Pair device.
    echo Then run: adb pair ^<IP:PORT^> and adb connect ^<IP:PORT^>
)

echo.
pause

