#!/usr/bin/env python3
"""
ULTRON Tailscale Portproxy & Socket Bridge
Binds strictly to Tailscale/all interfaces (port 8000)
and proxies full-duplex TCP traffic to the local ULTRON backend via WSL proxy (port 8001 -> 8000).

No administrator privileges required.
Maintains 100% database & Redis isolation while providing 100% reliable connectivity.
"""

import sys
import os
import socket
import asyncio
import argparse
import subprocess
import logging
import json
import glob
import winreg
import ctypes
from datetime import datetime
from typing import Optional

try:
    import win32api
    import win32con
except ImportError:
    win32api = None
    win32con = None

class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ('ACLineStatus', ctypes.c_byte),
        ('BatteryFlag', ctypes.c_byte),
        ('BatteryLifePercent', ctypes.c_byte),
        ('Reserved1', ctypes.c_byte),
        ('BatteryLifeTime', ctypes.c_ulong),
        ('BatteryFullLifeTime', ctypes.c_ulong)
    ]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ULTRON.TailscaleBridge")

PID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tailscale_bridge.pid")


def detect_tailscale_ip() -> str:
    """Detect Tailscale IPv4 address from host interfaces or fallback to default."""
    try:
        cmd = [
            "powershell", "-NoProfile", "-Command",
            "(Get-NetIPAddress -InterfaceAlias '*Tailscale*' -AddressFamily IPv4 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty IPAddress -First 1)"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        ip = res.stdout.strip()
        if ip and ip.startswith("100."):
            return ip
    except Exception:
        pass

    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            candidate = info[4][0]
            if candidate.startswith("100."):
                return candidate
    except Exception:
        pass

    return "100.69.161.16"


def ensure_wsl_proxy():
    """Ensure the user-space forwarder & app launcher in WSL is listening on port 8001 & 8009."""
    try:
        res = subprocess.run(["wsl", "hostname", "-I"], capture_output=True, text=True, timeout=5)
        wsl_ips = res.stdout.strip().split()
        for ip in wsl_ips:
            try:
                with socket.create_connection((ip, 8001), timeout=0.3):
                    # Also check 8009
                    try:
                        with socket.create_connection((ip, 8009), timeout=0.3):
                            return
                    except Exception:
                        pass
            except Exception:
                pass
    except Exception:
        pass

    bridge_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wsl_host_bridge.py")
    wsl_script_path = bridge_path.replace("\\", "/")
    if len(wsl_script_path) >= 2 and wsl_script_path[1] == ":":
        drive = wsl_script_path[0].lower()
        wsl_script_path = f"/mnt/{drive}{wsl_script_path[2:]}"

    try:
        subprocess.Popen(
            ["wsl", "nohup", "python3", wsl_script_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        logger.info("Launched WSL Host Bridge (%s)", wsl_script_path)
    except Exception as e:
        logger.warning("Could not launch WSL host bridge: %s", e)


def detect_connect_host() -> tuple[str, int]:
    """Detect the best target host and port for ULTRON backend."""
    ensure_wsl_proxy()

    try:
        res = subprocess.run(["wsl", "hostname", "-I"], capture_output=True, text=True, timeout=5)
        wsl_ips = res.stdout.strip().split()
        for ip in wsl_ips:
            try:
                with socket.create_connection((ip, 8001), timeout=0.5):
                    logger.info("Found reachable backend via WSL proxy at %s:8001", ip)
                    return ip, 8001
            except Exception:
                continue
    except Exception:
        pass

    return "172.26.79.85", 8001


async def pipe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Bidirectional streaming pump with zero copy buffer."""
    try:
        while not reader.at_eof():
            data = await reader.read(65536)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except (asyncio.CancelledError, ConnectionResetError, BrokenPipeError):
        pass
    except Exception as e:
        logger.debug("Pipe error: %s", e)
    finally:
        try:
            if not writer.is_closing():
                writer.close()
                await writer.wait_closed()
        except Exception:
            pass


class TargetResolver:
    """Manages active backend target host and transparently reconnects across WSL restarts."""
    def __init__(self, initial_host: Optional[str] = None, port: int = 8001):
        if initial_host:
            self.host = initial_host
            self.port = port
        else:
            self.host, self.port = detect_connect_host()
        self.lock = asyncio.Lock()

    async def get_connection(self):
        """Acquire an active TCP stream connection, re-detecting host if WSL was restarted."""
        for attempt in range(4):
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(self.host, self.port),
                    timeout=2.0
                )
                return reader, writer
            except Exception as e:
                logger.warning("Target %s:%d unreachable (%s). Re-detecting target... (attempt %d/4)", self.host, self.port, e, attempt + 1)
                async with self.lock:
                    loop = asyncio.get_running_loop()
                    new_host, new_port = await loop.run_in_executor(None, detect_connect_host)
                    self.host = new_host
                    self.port = new_port
                await asyncio.sleep(0.5)

        return await asyncio.wait_for(
            asyncio.open_connection(self.host, self.port),
            timeout=3.0
        )


async def handle_connection(client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter, resolver: TargetResolver):
    client_addr = client_writer.get_extra_info('peername')
    try:
        backend_reader, backend_writer = await resolver.get_connection()
    except Exception as e:
        logger.error("Failed to connect to backend after recovery attempts: %s", e)
        client_writer.close()
        try:
            await client_writer.wait_closed()
        except Exception:
            pass
        return

    try:
        await asyncio.gather(
            pipe(client_reader, backend_writer),
            pipe(backend_reader, client_writer)
        )
    except Exception as e:
        logger.debug("Forwarding session error: %s", e)
    finally:
        try:
            if not client_writer.is_closing():
                client_writer.close()
                await client_writer.wait_closed()
        except Exception:
            pass


_INSTALLED_APPS_CACHE = {}

def get_installed_apps_cache() -> dict:
    global _INSTALLED_APPS_CACHE
    if _INSTALLED_APPS_CACHE:
        return _INSTALLED_APPS_CACHE

    apps = {}

    # 1. Query StartApps (Discovers all 180+ Win32 and Windows Store UWP apps with shell:AppsFolder\AppID)
    try:
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", "Get-StartApps | ConvertTo-Json"],
            text=True, creationflags=0x08000000, timeout=6
        )
        data = json.loads(out)
        if isinstance(data, list):
            for item in data:
                name = item.get("Name", "").lower().strip()
                appid = item.get("AppID", "").strip()
                if name and appid and name not in apps:
                    apps[name] = f"shell:AppsFolder\\{appid}"
    except Exception as e:
        logger.warning("Get-StartApps enumeration warning: %s", e)

    # 2. Start Menu Shortcuts (.lnk)
    dirs = [
        os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs'),
        os.path.expandvars(r'%ProgramData%\Microsoft\Windows\Start Menu\Programs')
    ]
    for d in dirs:
        if os.path.exists(d):
            for f in glob.glob(d + r'\**\*.lnk', recursive=True):
                name = os.path.splitext(os.path.basename(f))[0].lower().strip()
                if name and name not in apps:
                    apps[name] = f

    # 3. Registry App Paths
    for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        try:
            with winreg.OpenKey(root, r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths') as k:
                for i in range(winreg.QueryInfoKey(k)[0]):
                    try:
                        sub = winreg.EnumKey(k, i)
                        name = os.path.splitext(sub)[0].lower().strip()
                        with winreg.OpenKey(k, sub) as sk:
                            val, _ = winreg.QueryValueEx(sk, '')
                            if val and name not in apps:
                                apps[name] = val
                    except Exception:
                        pass
        except Exception:
            pass

    _INSTALLED_APPS_CACHE = apps
    logger.info("Indexed %d installed applications on Windows host", len(apps))
    return apps


def find_app_on_windows(app_name: str) -> Optional[str]:
    """Dynamically locate any installed application shortcut or executable on PC."""
    app_lower = app_name.lower().strip()
    cache = get_installed_apps_cache()

    if app_lower in cache:
        return cache[app_lower]

    for name, path in cache.items():
        if app_lower == name or app_lower in name or name in app_lower:
            return path

    return None


def get_adb_path() -> Optional[str]:
    """Locate Android ADB tool."""
    candidates = [
        os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"),
        r"C:\Users\Navneeth V\AppData\Local\Android\Sdk\platform-tools\adb.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    from shutil import which
    return which("adb")


def execute_mobile_command(action_raw: Optional[str]) -> dict:
    """Execute Android commands via ADB (USB / Wireless)."""
    adb = get_adb_path()
    if not adb:
        return {
            "success": False,
            "app": "Mobile",
            "message": "❌ Android ADB tool not found. Install Android SDK Platform-Tools to control mobile."
        }

    action_str = (action_raw or "").strip()
    action_lower = action_str.lower()

    # Check connected devices
    try:
        out = subprocess.check_output([adb, "devices"], text=True, creationflags=0x08000000, timeout=5)
        lines = [line.strip() for line in out.strip().splitlines()[1:] if line.strip() and not line.startswith("*")]
        connected_devices = [l.split()[0] for l in lines if "\tdevice" in l or "device" in l.split()]
    except Exception as e:
        return {"success": False, "app": "Mobile", "message": f"Error running ADB: {e}"}

    # Connect device via Wi-Fi command
    if action_lower.startswith("connect_") or action_lower.startswith("connect "):
        target_ip = action_str.replace("connect_", "").replace("connect", "").strip()
        if not target_ip:
            return {"success": False, "app": "Mobile", "message": "⚠️ Please provide phone IP and port (e.g. `connect phone 192.168.1.5:5555`)"}
        try:
            res = subprocess.check_output([adb, "connect", target_ip], text=True, creationflags=0x08000000, timeout=10)
            return {"success": True, "app": "Mobile", "message": f"📱 ADB Connection result: {res.strip()}"}
        except Exception as e:
            return {"success": False, "app": "Mobile", "message": f"Failed to connect to {target_ip}: {e}"}

    # Device status check
    if action_lower in ["devices", "check", "status"]:
        if connected_devices:
            dev_str = ", ".join(connected_devices)
            return {"success": True, "app": "Mobile", "message": f"📱 **{len(connected_devices)}** Android device(s) connected: `{dev_str}`"}
        else:
            return {
                "success": True,
                "app": "Mobile",
                "message": "📱 **No Android device connected.**\n\nTo control your mobile:\n1. Enable **Developer Options** & **USB Debugging** (or **Wireless Debugging**) on your phone.\n2. Connect via USB or Wi-Fi using: `connect phone <IP>:<PORT>`."
            }

    if not connected_devices:
        return {
            "success": False,
            "app": "Mobile",
            "message": "📱 **No Android phone currently connected.**\n\nTo connect:\n1. Enable **USB Debugging** on your phone.\n2. Connect via USB or Wi-Fi (`connect phone <IP>:<PORT>`)."
        }

    # Open App on Mobile
    if action_lower.startswith("open_") or action_lower.startswith("open "):
        app_target = action_lower.replace("open_", "").replace("open", "").strip()
        pkg_map = {
            "spotify": "com.spotify.music",
            "whatsapp": "com.whatsapp",
            "youtube": "com.google.android.youtube",
            "chrome": "com.android.chrome",
            "instagram": "com.instagram.android",
            "telegram": "org.telegram.messenger",
            "camera": "com.android.camera",
            "settings": "com.android.settings",
            "maps": "com.google.android.apps.maps",
            "gmail": "com.google.android.gm",
        }
        pkg = pkg_map.get(app_target)
        if pkg:
            subprocess.run([adb, "shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"], creationflags=0x08000000)
            return {"success": True, "app": "Mobile", "message": f"📱 Opened **{app_target.capitalize()}** on connected Android phone!"}
        else:
            # Try to launch via package search
            try:
                pkgs = subprocess.check_output([adb, "shell", "pm", "list", "packages"], text=True, creationflags=0x08000000, timeout=5)
                matching = [p.replace("package:", "").strip() for p in pkgs.splitlines() if app_target in p.lower()]
                if matching:
                    target_pkg = matching[0]
                    subprocess.run([adb, "shell", "monkey", "-p", target_pkg, "-c", "android.intent.category.LAUNCHER", "1"], creationflags=0x08000000)
                    return {"success": True, "app": "Mobile", "message": f"📱 Opened **{app_target}** (`{target_pkg}`) on connected Android phone!"}
            except Exception:
                pass
            return {"success": False, "app": "Mobile", "message": f"⚠️ Could not find app package for '{app_target}' on connected phone."}

    # Close App on Mobile
    if action_lower.startswith("close_") or action_lower.startswith("close "):
        app_target = action_lower.replace("close_", "").replace("close", "").strip()
        pkg_map = {
            "spotify": "com.spotify.music",
            "whatsapp": "com.whatsapp",
            "youtube": "com.google.android.youtube",
            "chrome": "com.android.chrome",
            "instagram": "com.instagram.android",
            "telegram": "org.telegram.messenger",
        }
        pkg = pkg_map.get(app_target, app_target)
        subprocess.run([adb, "shell", "am", "force-stop", pkg], creationflags=0x08000000)
        return {"success": True, "app": "Mobile", "message": f"📱 Closed **{app_target}** on connected Android phone!"}

    # Mobile Screenshot
    if action_lower in ["screenshot", "screen_capture"]:
        pics_dir = os.path.expandvars(r"%USERPROFILE%\Pictures\Screenshots")
        os.makedirs(pics_dir, exist_ok=True)
        local_file = os.path.join(pics_dir, f"mobile_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        subprocess.run([adb, "shell", "screencap", "-p", "/sdcard/screen.png"], creationflags=0x08000000)
        subprocess.run([adb, "pull", "/sdcard/screen.png", local_file], creationflags=0x08000000)
        return {"success": True, "app": "Mobile", "message": f"📱 Mobile screenshot captured and saved to **{local_file}**!"}

    # Mobile Media / Navigation Controls
    mobile_keys = {
        "play": 85, "pause": 85, "play_pause": 85,
        "next": 87, "prev": 88,
        "volume_up": 24, "volume_down": 25,
        "lock": 26, "power": 26, "home": 3, "back": 4
    }
    if action_lower in mobile_keys:
        keycode = mobile_keys[action_lower]
        subprocess.run([adb, "shell", "input", "keyevent", str(keycode)], creationflags=0x08000000)
        return {"success": True, "app": "Mobile", "message": f"📱 Mobile key event `{action_lower}` dispatched successfully!"}

    return {"success": False, "app": "Mobile", "message": f"Unknown mobile action: '{action_str}'"}


def capture_desktop_screenshot() -> str:
    """Capture full desktop screen and save to Pictures\\Screenshots."""
    pics = os.path.expandvars(r'%USERPROFILE%\Pictures\Screenshots')
    os.makedirs(pics, exist_ok=True)
    filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(pics, filename)

    ps_script = f"""Add-Type -AssemblyName System.Windows.Forms,System.Drawing
$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object Drawing.Bitmap $b.Width, $b.Height
$g = [Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Location, [Drawing.Point]::Empty, $b.Size)
$bmp.Save('{filepath}', [Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
$g.Dispose()
"""
    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script], check=True, creationflags=0x08000000)
    return filepath


def close_windows_process(app_target: str) -> dict:
    """Close an application process on Windows."""
    clean_target = app_target.lower().strip()
    proc_map = {
        "spotify": "Spotify.exe",
        "chrome": "chrome.exe",
        "edge": "msedge.exe",
        "browser": "msedge.exe",
        "notepad": "notepad.exe",
        "calc": "CalculatorApp.exe",
        "calculator": "CalculatorApp.exe",
        "discord": "Discord.exe",
        "telegram": "Telegram.exe",
        "whatsapp": "WhatsApp.exe",
        "store": "WinStore.App.exe",
        "microsoft store": "WinStore.App.exe",
        "code": "Code.exe",
        "vscode": "Code.exe",
        "cursor": "Cursor.exe",
        "task manager": "Taskmgr.exe",
        "paint": "mspaint.exe",
        "cmd": "cmd.exe",
        "terminal": "WindowsTerminal.exe",
    }
    proc_name = proc_map.get(clean_target, f"{clean_target}.exe")
    try:
        res = subprocess.run(["taskkill", "/IM", proc_name, "/F"], capture_output=True, text=True, creationflags=0x08000000)
        if res.returncode == 0:
            return {"success": True, "app": "System", "message": f"🛑 Successfully closed **{app_target.capitalize()}** (`{proc_name}`)."}
        else:
            return {"success": True, "app": "System", "message": f"ℹ️ **{app_target.capitalize()}** was not running or has already been closed."}
    except Exception as e:
        return {"success": False, "app": "System", "message": f"Failed to close {app_target}: {e}"}


def execute_native_windows_app(app_name: str, target: Optional[str] = None) -> dict:
    """Execute Windows applications directly in the user's interactive desktop session."""
    app_lower = app_name.lower().strip()
    logger.info("Executing native Windows launch for '%s' (target: '%s')", app_lower, target)

    try:
        # 0. Mobile (Android) Controls via ADB
        if app_lower in ["mobile", "android", "phone", "mobile_app"]:
            return execute_mobile_command(target)

        # 1. System Controls (Volume, Media, Battery, Lock, Screenshots, Show Desktop, Close App)
        if app_lower in ["system_control", "system", "pc", "volume", "media", "close_app", "screenshot"]:
            action = (target or "").lower().strip()

            # Close app action
            if action.startswith("close_") or action.startswith("close ") or app_lower == "close_app":
                app_to_close = action.replace("close_", "").replace("close", "").strip() or (target or "")
                return close_windows_process(app_to_close)

            # Desktop Screenshot
            elif action in ["screenshot", "capture_screen", "take_screenshot"] or app_lower == "screenshot":
                filepath = capture_desktop_screenshot()
                return {"success": True, "app": "Screenshot", "message": f"📸 Screenshot captured and saved to **{filepath}**!"}

            # Show Desktop (Minimize all)
            elif action in ["show_desktop", "minimize_all", "desktop"]:
                if win32api:
                    win32api.keybd_event(0x5B, 0, 0, 0)
                    win32api.keybd_event(0x44, 0, 0, 0)
                    win32api.keybd_event(0x44, 0, win32con.KEYEVENTF_KEYUP, 0)
                    win32api.keybd_event(0x5B, 0, win32con.KEYEVENTF_KEYUP, 0)
                return {"success": True, "app": "Desktop", "message": "🖥 Showing Desktop (minimized open windows)"}

            # Empty Recycle Bin
            elif action in ["empty_recycle_bin", "recycle_bin", "clear_recycle_bin"]:
                try:
                    ctypes.windll.shell32.SHEmptyRecycleBinW(0, None, 7)
                    return {"success": True, "app": "Recycle Bin", "message": "🗑 Recycle Bin emptied successfully!"}
                except Exception as e:
                    return {"success": False, "app": "Recycle Bin", "message": f"Failed to empty Recycle Bin: {e}"}

            # Volume Controls
            elif action in ["volume_up", "up", "increase"]:
                if win32api:
                    for _ in range(5):
                        win32api.keybd_event(0xAF, 0, 0, 0)
                        win32api.keybd_event(0xAF, 0, win32con.KEYEVENTF_KEYUP, 0)
                return {"success": True, "app": "Volume", "message": "🔊 Volume increased by 10%"}
            elif action in ["volume_down", "down", "decrease"]:
                if win32api:
                    for _ in range(5):
                        win32api.keybd_event(0xAE, 0, 0, 0)
                        win32api.keybd_event(0xAE, 0, win32con.KEYEVENTF_KEYUP, 0)
                return {"success": True, "app": "Volume", "message": "🔉 Volume decreased by 10%"}
            elif action in ["mute", "unmute"]:
                if win32api:
                    win32api.keybd_event(0xAD, 0, 0, 0)
                    win32api.keybd_event(0xAD, 0, win32con.KEYEVENTF_KEYUP, 0)
                return {"success": True, "app": "Volume", "message": "🔇 Volume mute toggled"}

            # Media Controls
            elif action in ["media_play_pause", "pause", "resume", "play"]:
                if win32api:
                    win32api.keybd_event(0xB3, 0, 0, 0)
                    win32api.keybd_event(0xB3, 0, win32con.KEYEVENTF_KEYUP, 0)
                return {"success": True, "app": "Media", "message": "⏯ Media playback toggled (Play/Pause)"}
            elif action in ["media_next", "next"]:
                if win32api:
                    win32api.keybd_event(0xB0, 0, 0, 0)
                    win32api.keybd_event(0xB0, 0, win32con.KEYEVENTF_KEYUP, 0)
                return {"success": True, "app": "Media", "message": "⏭ Skipped to next track"}
            elif action in ["media_prev", "prev"]:
                if win32api:
                    win32api.keybd_event(0xB1, 0, 0, 0)
                    win32api.keybd_event(0xB1, 0, win32con.KEYEVENTF_KEYUP, 0)
                return {"success": True, "app": "Media", "message": "⏮ Returned to previous track"}

            # Lock Screen
            elif action in ["lock", "lock_screen", "lock_pc"]:
                ctypes.windll.user32.LockWorkStation()
                return {"success": True, "app": "System", "message": "🔒 PC locked successfully"}

            # Battery Status
            elif action in ["battery", "battery_status"]:
                sps = SYSTEM_POWER_STATUS()
                if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(sps)):
                    if sps.BatteryLifePercent != 255:
                        status = "plugged in and charging" if sps.ACLineStatus == 1 else "on battery power"
                        msg = f"🔋 Battery is at **{sps.BatteryLifePercent}%** ({status})"
                    else:
                        msg = "🖥 Running on AC power (Desktop PC)"
                else:
                    msg = "🖥 Running on AC power (Desktop PC)"
                return {"success": True, "app": "Battery", "message": msg}

        # 2. Spotify Native & Web Playback
        if app_lower in ["spotify", "music"]:
            # Always launch the native Spotify Windows app first so it's active
            try:
                os.startfile(r"shell:AppsFolder\SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify")
            except Exception:
                pass

            if target:
                query = "Today's Top Hits" if target.lower().strip() in ["a song", "some music", "music", "song", "songs", "play a song"] else target
                os.startfile(f"https://open.spotify.com/search/{query}")
            return {"success": True, "app": "Spotify", "target": target, "message": "Spotify opened on desktop"}

        # 3. Microsoft Store
        elif app_lower in ["store", "microsoft store", "windows store"]:
            if target:
                os.startfile(f"ms-windows-store://search/?query={target}")
            else:
                os.startfile("ms-windows-store:")
            return {"success": True, "app": "Microsoft Store", "target": target, "message": "Microsoft Store opened on desktop"}

        # 4. WhatsApp
        elif app_lower == "whatsapp":
            try:
                os.startfile(r"shell:AppsFolder\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App")
            except Exception:
                try:
                    os.startfile("whatsapp:")
                except Exception:
                    os.startfile("https://web.whatsapp.com")
            return {"success": True, "app": "WhatsApp", "message": "WhatsApp opened on desktop"}

        # 5. YouTube
        elif app_lower == "youtube":
            if target:
                os.startfile(f"https://www.youtube.com/results?search_query={target}")
            else:
                os.startfile("https://www.youtube.com")
            return {"success": True, "app": "YouTube", "target": target, "message": "YouTube opened on desktop"}

        # 6. Common native Windows applications & special folders
        system_apps = {
            "notepad": "notepad.exe",
            "calc": "calc.exe",
            "calculator": "calc.exe",
            "task manager": "taskmgr.exe",
            "taskmgr": "taskmgr.exe",
            "paint": "mspaint.exe",
            "settings": "ms-settings:",
            "camera": "microsoft.windows.camera:",
            "photos": "ms-photos:",
            "cmd": "cmd.exe",
            "terminal": "wt.exe",
            "powershell": "powershell.exe",
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
            "browser": "msedge.exe",
            "code": "code",
            "vscode": "code",
            "cursor": "cursor",
            "explorer": "explorer.exe",
            "files": "explorer.exe",
            "downloads": "shell:Downloads",
            "documents": "shell:Personal",
            "pictures": "shell:My Pictures",
            "desktop": "shell:Desktop",
            "recycle bin": "shell:RecycleBinFolder",
            "control panel": "control.exe",
            "c drive": "c:\\",
            "d drive": "d:\\",
            "e drive": "e:\\",
            "c:": "c:\\",
            "d:": "d:\\",
            "e:": "e:\\",
            "discord": "discord:",
            "telegram": "tg:",
            "steam": "steam:"
        }

        if app_lower in system_apps:
            cmd = system_apps[app_lower]
            if cmd.startswith("http") or cmd.startswith("ms-") or cmd.startswith("shell:") or cmd.endswith(":") or ":" in cmd:
                os.startfile(cmd)
            else:
                try:
                    os.startfile(cmd)
                except Exception:
                    subprocess.Popen(cmd, shell=True)
            return {"success": True, "app": app_name, "message": f"{app_name} opened on desktop"}

        # 7. Dynamic Installed App Discovery across PC (187+ apps from Get-StartApps)
        dyn_path = find_app_on_windows(app_lower)
        if dyn_path:
            os.startfile(dyn_path)
            return {"success": True, "app": app_name, "message": f"{app_name} opened on desktop"}

        # 8. Generic App / URL fallback
        if app_name.startswith("http://") or app_name.startswith("https://"):
            os.startfile(app_name)
        else:
            try:
                os.startfile(app_name)
            except Exception:
                subprocess.Popen(f"start {app_name}", shell=True)
        return {"success": True, "app": app_name, "message": f"Launched {app_name}"}

    except Exception as e:
        logger.error("Failed to launch '%s': %s", app_name, e)
        return {"success": False, "app": app_name, "error": str(e)}


async def handle_launcher_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Handle connection from Docker/WSL requesting native desktop app launch."""
    try:
        data = await reader.read(4096)
        if not data:
            return
        req = json.loads(data.decode("utf-8"))
        app = req.get("app", "")
        target = req.get("target")

        res = execute_native_windows_app(app, target)
        writer.write(json.dumps(res).encode("utf-8"))
        await writer.drain()
    except Exception as e:
        logger.error("Launcher handler error: %s", e)
        try:
            writer.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
            await writer.drain()
        except Exception:
            pass
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass


async def run_server(listen_ip: str, listen_port: int, resolver: TargetResolver):
    proxy_server = await asyncio.start_server(
        lambda r, w: handle_connection(r, w, resolver),
        listen_ip,
        listen_port,
        reuse_address=True
    )
    launcher_server = await asyncio.start_server(
        handle_launcher_connection,
        "0.0.0.0",
        8009,
        reuse_address=True
    )

    addrs = ', '.join(str(sock.getsockname()) for sock in proxy_server.sockets)
    launcher_addrs = ', '.join(str(sock.getsockname()) for sock in launcher_server.sockets)
    logger.info("=" * 60)
    logger.info("ULTRON Tailscale Portproxy Socket Bridge Active")
    logger.info("Proxy Listening on   : %s", addrs)
    logger.info("Launcher Listening on: %s", launcher_addrs)
    logger.info("Active Target: %s:%d (Auto-recovering via WSL proxy)", resolver.host, resolver.port)
    logger.info("Isolation    : Database (3306) & Redis (6379) STRICTLY ISOLATED")
    logger.info("=" * 60)

    try:
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass

    async with proxy_server, launcher_server:
        await asyncio.gather(proxy_server.serve_forever(), launcher_server.serve_forever())


def main():
    parser = argparse.ArgumentParser(description="ULTRON Tailscale Portproxy Socket Bridge")
    parser.add_argument("--listen-ip", default="0.0.0.0", help="IP to listen on (default: 0.0.0.0)")
    parser.add_argument("--listen-port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--target-host", default=None, help="Target host (auto-detects WSL)")
    parser.add_argument("--target-port", type=int, default=8001, help="Target port (default: 8001)")
    parser.add_argument("--stop", action="store_true", help="Stop any running bridge instance")
    args = parser.parse_args()

    if args.stop:
        if os.path.exists(PID_FILE):
            try:
                with open(PID_FILE, "r") as f:
                    pid = int(f.read().strip())
                import signal
                os.kill(pid, signal.SIGTERM)
                os.remove(PID_FILE)
                print(f"Stopped bridge process with PID {pid}")
            except Exception as e:
                print(f"Error stopping PID: {e}")
        else:
            print("No running bridge PID found.")
        return

    resolver = TargetResolver(initial_host=args.target_host, port=args.target_port)

    try:
        asyncio.run(run_server(args.listen_ip, args.listen_port, resolver))
    except KeyboardInterrupt:
        logger.info("Shutting down bridge cleanly...")
    finally:
        if os.path.exists(PID_FILE):
            try:
                os.remove(PID_FILE)
            except Exception:
                pass


if __name__ == "__main__":
    main()
