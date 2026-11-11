import logging
import socket
import json
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger("ULTRON.DesktopAppTools")

# Default gateway in WSL2 Docker containers to reach WSL host
DEFAULT_HOST_BRIDGE_IP = "172.17.0.1"
DEFAULT_HOST_BRIDGE_PORT = 8009

APP_PROTOCOL_MAP = {
    "whatsapp": {"protocol": "whatsapp:", "fallback_url": "https://web.whatsapp.com", "name": "WhatsApp Desktop"},
    "store": {"protocol": "ms-windows-store:", "name": "Microsoft Store"},
    "microsoft store": {"protocol": "ms-windows-store:", "name": "Microsoft Store"},
    "windows store": {"protocol": "ms-windows-store:", "name": "Microsoft Store"},
    "settings": {"protocol": "ms-settings:", "name": "Windows Settings"},
    "spotify": {"protocol": "spotify:", "fallback_url": "https://open.spotify.com", "name": "Spotify"},
    "notepad": {"command": "notepad", "name": "Notepad"},
    "calculator": {"command": "calc", "name": "Calculator"},
    "calc": {"command": "calc", "name": "Calculator"},
    "camera": {"protocol": "microsoft.windows.camera:", "name": "Camera"},
    "photos": {"protocol": "ms-photos:", "name": "Photos"},
    "paint": {"command": "mspaint", "name": "Paint"},
    "terminal": {"command": "wt", "name": "Windows Terminal"},
    "cmd": {"command": "cmd", "name": "Command Prompt"},
    "chrome": {"command": "start chrome", "fallback_url": "https://google.com", "name": "Google Chrome"},
    "browser": {"command": "start msedge", "name": "Default Web Browser"},
    "edge": {"command": "start msedge", "name": "Microsoft Edge"},
    "vscode": {"command": "code", "name": "Visual Studio Code"},
    "code": {"command": "code", "name": "Visual Studio Code"},
    "explorer": {"command": "explorer", "name": "File Explorer"},
    "files": {"command": "explorer", "name": "File Explorer"},
    "task manager": {"command": "taskmgr", "name": "Task Manager"},
    "taskmgr": {"command": "taskmgr", "name": "Task Manager"},
    "youtube": {"command": "start https://www.youtube.com", "name": "YouTube"},
    "github": {"command": "start https://github.com", "name": "GitHub"},
    "gmail": {"command": "start https://mail.google.com", "name": "Gmail"},
    "chatgpt": {"command": "start https://chatgpt.com", "name": "ChatGPT"},
    "downloads": {"command": "explorer shell:Downloads", "name": "Downloads"},
    "documents": {"command": "explorer shell:Personal", "name": "Documents"},
    "pictures": {"command": "explorer shell:My Pictures", "name": "Pictures"},
    "recycle bin": {"command": "explorer shell:RecycleBinFolder", "name": "Recycle Bin"},
    "control panel": {"command": "control", "name": "Control Panel"},
    "discord": {"protocol": "discord:", "fallback_url": "https://discord.com/app", "name": "Discord"},
    "telegram": {"protocol": "tg:", "fallback_url": "https://web.telegram.org", "name": "Telegram"},
    "steam": {"protocol": "steam:", "name": "Steam"},
}


async def launch_desktop_app(app_name: str, target: Optional[str] = None) -> Dict[str, Any]:
    """Launch a native Windows desktop application and bring its window to the foreground."""
    cleaned_name = app_name.lower().strip()
    
    app_info = APP_PROTOCOL_MAP.get(cleaned_name, {
        "command": cleaned_name,
        "name": app_name
    })

    payload = {
        "action": "launch",
        "app": cleaned_name,
        "protocol": app_info.get("protocol"),
        "command": app_info.get("command"),
        "fallback_url": app_info.get("fallback_url"),
        "target": target
    }

    loop = asyncio.get_running_loop()

    def _send_to_bridge():
        try:
            with socket.create_connection((DEFAULT_HOST_BRIDGE_IP, DEFAULT_HOST_BRIDGE_PORT), timeout=8.0) as s:
                s.sendall(json.dumps(payload).encode("utf-8"))
                raw_resp = s.recv(4096)
                if raw_resp:
                    return json.loads(raw_resp.decode("utf-8"))
                return {"success": False, "error": "Empty response from host bridge"}
        except Exception as e:
            logger.error("Failed to communicate with desktop host bridge: %s", e)
            return {"success": False, "error": str(e)}

    res = await loop.run_in_executor(None, _send_to_bridge)

    if res.get("success"):
        disp_name = app_info.get("name", app_name)
        if target:
            if cleaned_name in ["spotify", "youtube"]:
                msg = f"🎶 **{disp_name}** has been opened and is playing **{target}** on your desktop!"
            else:
                msg = f"🔍 **{disp_name}** has been opened searching for **{target}** on your desktop!"
        else:
            msg = f"✅ **{disp_name}** has been opened on your desktop!"
        return {
            "success": True,
            "app": disp_name,
            "target": target,
            "result": msg,
            "details": res
        }
    else:
        # If native bridge wasn't reachable or app failed, describe fallback
        error_msg = res.get("error", "Unknown error")
        return {
            "success": False,
            "app": app_name,
            "error": f"Could not launch {app_name} on host ({error_msg}).",
            "fallback_url": app_info.get("fallback_url")
        }

