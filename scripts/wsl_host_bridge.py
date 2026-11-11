#!/usr/bin/env python3
"""
ULTRON WSL Host Bridge & App Launcher
Runs inside WSL2 (Ubuntu-22.04) and bridges:
1. Port 8001: Proxies incoming Windows traffic (0.0.0.0:8001 -> 127.0.0.1:8000)
2. Port 8009: Receives host execution requests from Docker container (172.17.0.1:8009)
   and launches native Windows apps via cmd.exe / powershell.exe with foreground activation.
"""

import sys
import socket
import threading
import subprocess
import json
import logging
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ULTRON.WSLHostBridge")

CMD_EXE = "/mnt/c/WINDOWS/system32/cmd.exe"
POWERSHELL_EXE = "/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0/powershell.exe"

APP_COMMANDS = {
    "whatsapp": {
        "protocol": "whatsapp:",
        "app_id": "5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
        "fallback_url": "https://web.whatsapp.com"
    },
    "store": {"protocol": "ms-windows-store:", "name": "Microsoft Store"},
    "microsoft store": {"protocol": "ms-windows-store:", "name": "Microsoft Store"},
    "windows store": {"protocol": "ms-windows-store:", "name": "Microsoft Store"},
    "settings": {"protocol": "ms-settings:", "name": "Windows Settings"},
    "spotify": {
        "protocol": "spotify:",
        "fallback_url": "https://open.spotify.com"
    },
    "notepad": {"cmd": "notepad.exe"},
    "calc": {"cmd": "calc.exe"},
    "calculator": {"cmd": "calc.exe"},
    "task manager": {"cmd": "taskmgr.exe"},
    "taskmgr": {"cmd": "taskmgr.exe"},
    "youtube": {"cmd": "start https://www.youtube.com"},
    "github": {"cmd": "start https://github.com"},
    "gmail": {"cmd": "start https://mail.google.com"},
    "chatgpt": {"cmd": "start https://chatgpt.com"},
    "camera": {"protocol": "microsoft.windows.camera:"},
    "photos": {"protocol": "ms-photos:"},
    "paint": {"cmd": "mspaint.exe"},
    "terminal": {"cmd": "wt.exe"},
    "cmd": {"cmd": "cmd.exe"},
    "powershell": {"cmd": "powershell.exe"},
    "chrome": {"cmd": "start chrome"},
    "edge": {"cmd": "start msedge"},
    "browser": {"cmd": "start msedge"},
    "code": {"cmd": "code"},
    "vscode": {"cmd": "code"},
    "explorer": {"cmd": "explorer.exe"},
    "files": {"cmd": "explorer.exe"},
    "downloads": {"cmd": "explorer.exe shell:Downloads"},
    "documents": {"cmd": "explorer.exe shell:Personal"},
    "pictures": {"cmd": "explorer.exe shell:My Pictures"},
    "recycle bin": {"cmd": "explorer.exe shell:RecycleBinFolder"},
    "control panel": {"cmd": "control.exe"},
    "discord": {"protocol": "discord:", "fallback_url": "https://discord.com/app"},
    "telegram": {"protocol": "tg:", "fallback_url": "https://web.telegram.org"},
    "steam": {"protocol": "steam:"},
}


def launch_windows_app(app_name: str, target: str = None) -> dict:
    """Execute Windows command to launch desktop application and restore/focus window."""
    app_lower = app_name.lower().strip()
    config = APP_COMMANDS.get(app_lower, {})

    logger.info("Executing desktop app launch for: '%s'", app_lower)

    # 1. In-App Searches with Target Parameter
    if target:
        if app_lower in ["store", "microsoft store", "windows store"]:
            try:
                subprocess.run([CMD_EXE, "/c", "start", f"ms-windows-store://search/?query={target}"], capture_output=True, timeout=5)
            except Exception as e:
                logger.warning("Store search error: %s", e)
            return {"success": True, "app": "Microsoft Store", "target": target, "message": f"Searching Microsoft Store for '{target}'"}

        elif app_lower in ["spotify", "music"]:
            try:
                # Open Spotify search in web player and protocol
                subprocess.run([CMD_EXE, "/c", "start", f"https://open.spotify.com/search/{target}"], capture_output=True, timeout=5)
                subprocess.run([CMD_EXE, "/c", "start", f"spotify:search:{target}"], capture_output=True, timeout=5)
            except Exception as e:
                logger.warning("Spotify search error: %s", e)
            return {"success": True, "app": "Spotify", "target": target, "message": f"Searching Spotify for '{target}'"}

        elif app_lower in ["youtube"]:
            try:
                subprocess.run([CMD_EXE, "/c", "start", f"https://www.youtube.com/results?search_query={target}"], capture_output=True, timeout=5)
            except Exception as e:
                logger.warning("YouTube search error: %s", e)
            return {"success": True, "app": "YouTube", "target": target, "message": f"Searching YouTube for '{target}'"}

        elif app_lower in ["google", "browser", "chrome", "edge"]:
            try:
                subprocess.run([CMD_EXE, "/c", "start", f"https://www.google.com/search?q={target}"], capture_output=True, timeout=5)
            except Exception as e:
                logger.warning("Google search error: %s", e)
            return {"success": True, "app": "Google", "target": target, "message": f"Searching Google for '{target}'"}

    # 2. Protocol or Shell App activation
    if app_lower == "whatsapp":
        try:
            subprocess.run([CMD_EXE, "/c", "start explorer.exe shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App"], capture_output=True, timeout=5)
            subprocess.run([CMD_EXE, "/c", "start", "whatsapp:"], capture_output=True, timeout=5)
        except Exception as e:
            logger.warning("WhatsApp launch error: %s", e)
        return {"success": True, "app": "WhatsApp", "message": "WhatsApp Desktop launched and brought to foreground"}

    elif app_lower in ["spotify", "music"]:
        try:
            # 1. Launch Chrome PWA shortcut which the user has installed
            spotify_pwa = "C:\\Users\\Navneeth V\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Chrome Apps\\Spotify.lnk"
            subprocess.run([CMD_EXE, "/c", "start", "", spotify_pwa], capture_output=True, timeout=5)
            # 2. Also try protocol and web fallback
            subprocess.run([CMD_EXE, "/c", "start", "spotify:"], capture_output=True, timeout=5)
        except Exception as e:
            logger.warning("Spotify launch error: %s", e)
        return {"success": True, "app": "Spotify", "message": "Spotify launched and brought to foreground"}

    elif app_lower in ["store", "microsoft store", "windows store"]:
        try:
            subprocess.run([CMD_EXE, "/c", "start explorer.exe shell:AppsFolder\\Microsoft.WindowsStore_8wekyb3d8bbwe!App"], capture_output=True, timeout=5)
            subprocess.run([CMD_EXE, "/c", "start", "ms-windows-store:"], capture_output=True, timeout=5)
        except Exception as e:
            logger.warning("Store launch error: %s", e)
        return {"success": True, "app": "Microsoft Store", "message": "Microsoft Store launched and brought to foreground"}

    elif config.get("protocol"):
        proto = config["protocol"]
        subprocess.run([CMD_EXE, "/c", "start", proto], capture_output=True, timeout=5)
        return {"success": True, "app": app_name, "message": f"{app_name} opened via protocol {proto}"}

    elif config.get("cmd"):
        cmd_str = config["cmd"]
        if target:
            cmd_str += f" \"{target}\""
        subprocess.run([CMD_EXE, "/c", cmd_str], capture_output=True, timeout=5)
        return {"success": True, "app": app_name, "message": f"{app_name} opened successfully"}

    else:
        # Generic command launch attempt
        try:
            subprocess.run([CMD_EXE, "/c", "start", app_name], capture_output=True, timeout=5)
            return {"success": True, "app": app_name, "message": f"{app_name} launched"}
        except Exception as e:
            return {"success": False, "error": str(e)}


def handle_app_launcher_client(client_sock):
    """Handle connection from Docker backend requesting app launch."""
    try:
        data = client_sock.recv(4096)
        if not data:
            return
        req = json.loads(data.decode("utf-8"))
        app = req.get("app", "")
        target = req.get("target")

        res = launch_windows_app(app, target)
        client_sock.sendall(json.dumps(res).encode("utf-8"))
    except Exception as e:
        logger.error("Error handling app launch request: %s", e)
        try:
            client_sock.sendall(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
        except Exception:
            pass
    finally:
        try:
            client_sock.close()
        except Exception:
            pass


def run_app_launcher_server():
    """Server on port 8009 listening for container app launch requests."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("0.0.0.0", 8009))
        s.listen(32)
        logger.info("WSL Host App Launcher listening on 0.0.0.0:8009")
    except Exception as e:
        logger.error("Could not bind port 8009: %s", e)
        return

    while True:
        try:
            client, _ = s.accept()
            threading.Thread(target=handle_app_launcher_client, args=(client,), daemon=True).start()
        except Exception:
            break


def run_tcp_forwarder():
    """Forwarder on port 8001 -> 127.0.0.1:8000 (backend)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("0.0.0.0", 8001))
        s.listen(128)
        logger.info("WSL TCP Forwarder listening on 0.0.0.0:8001 -> 127.0.0.1:8000")
    except Exception as e:
        logger.error("Could not bind port 8001: %s", e)
        return

    while True:
        try:
            client, _ = s.accept()
            target = socket.create_connection(("127.0.0.1", 8000))
            def pipe(c, t):
                try:
                    while True:
                        d = c.recv(65536)
                        if not d: break
                        t.sendall(d)
                except Exception: pass
                finally:
                    try: t.close()
                    except Exception: pass
            threading.Thread(target=pipe, args=(client, target), daemon=True).start()
            threading.Thread(target=pipe, args=(target, client), daemon=True).start()
        except Exception:
            break


def main():
    t1 = threading.Thread(target=run_tcp_forwarder, daemon=True)
    t2 = threading.Thread(target=run_app_launcher_server, daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


if __name__ == "__main__":
    main()

