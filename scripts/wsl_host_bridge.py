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


def run_cmd_async(cmd_str: str):
    """Run a Windows command asynchronously without blocking the bridge."""
    try:
        subprocess.Popen(
            [CMD_EXE, "/c", cmd_str],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        logger.warning("Error running cmd '%s': %s", cmd_str, e)


def launch_windows_app(app_name: str, target: str = None) -> dict:
    """Execute Windows command to launch desktop application and restore/focus window."""
    app_lower = app_name.lower().strip()
    config = APP_COMMANDS.get(app_lower, {})

    logger.info("Executing desktop app launch for: '%s' (target: '%s')", app_lower, target)

    # 1. In-App Searches with Target Parameter
    if target:
        if app_lower in ["store", "microsoft store", "windows store"]:
            run_cmd_async(f"start ms-windows-store://search/?query={target}")
            return {"success": True, "app": "Microsoft Store", "target": target, "message": f"Searching Microsoft Store for '{target}'"}

        elif app_lower in ["spotify", "music"]:
            query = "Today's Top Hits" if target.lower().strip() in ["a song", "some music", "music", "song", "songs", "play a song"] else target
            run_cmd_async(f"start https://open.spotify.com/search/{query}")
            run_cmd_async(f"start spotify:search:{query}")
            return {"success": True, "app": "Spotify", "target": query, "message": f"Playing '{query}' on Spotify"}

        elif app_lower in ["youtube"]:
            query = "Trending Music" if target.lower().strip() in ["a song", "some music", "music", "song", "songs", "play a song"] else target
            run_cmd_async(f"start https://www.youtube.com/results?search_query={query}")
            return {"success": True, "app": "YouTube", "target": query, "message": f"Playing '{query}' on YouTube"}

        elif app_lower in ["google", "browser", "chrome", "edge"]:
            run_cmd_async(f"start https://www.google.com/search?q={target}")
            return {"success": True, "app": "Google", "target": target, "message": f"Searching Google for '{target}'"}

    # 2. Protocol or Shell App activation
    if app_lower == "whatsapp":
        run_cmd_async("start explorer.exe shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App")
        run_cmd_async("start whatsapp:")
        return {"success": True, "app": "WhatsApp", "message": "WhatsApp Desktop launched and brought to foreground"}

    elif app_lower in ["spotify", "music"]:
        run_cmd_async("start https://open.spotify.com")
        run_cmd_async("start spotify:")
        return {"success": True, "app": "Spotify", "message": "Spotify launched and brought to foreground"}

    elif app_lower in ["store", "microsoft store", "windows store"]:
        run_cmd_async("start explorer.exe shell:AppsFolder\\Microsoft.WindowsStore_8wekyb3d8bbwe!App")
        run_cmd_async("start ms-windows-store:")
        return {"success": True, "app": "Microsoft Store", "message": "Microsoft Store launched and brought to foreground"}

    elif config.get("protocol"):
        proto = config["protocol"]
        run_cmd_async(f"start {proto}")
        return {"success": True, "app": app_name, "message": f"{app_name} opened via protocol {proto}"}

    elif config.get("cmd"):
        cmd_str = config["cmd"]
        if target:
            cmd_str += f" \"{target}\""
        run_cmd_async(cmd_str)
        return {"success": True, "app": app_name, "message": f"{app_name} opened successfully"}

    else:
        # Generic command launch attempt
        run_cmd_async(f"start {app_name}")
        return {"success": True, "app": app_name, "message": f"{app_name} launched"}


def handle_app_launcher_client(client_sock):
    """Handle connection from Docker backend requesting app launch."""
    try:
        data = client_sock.recv(4096)
        if not data:
            return

        # 1. Forward directly to native Windows bridge on 100.69.161.16:8009 for interactive desktop execution
        try:
            with socket.create_connection(("100.69.161.16", 8009), timeout=2.0) as win_sock:
                win_sock.sendall(data)
                win_resp = win_sock.recv(4096)
                if win_resp:
                    client_sock.sendall(win_resp)
                    return
        except Exception as forward_err:
            logger.debug("Could not forward to Windows native launcher (falling back to local): %s", forward_err)

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

