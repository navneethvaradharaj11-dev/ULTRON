#!/usr/bin/env python3
"""
ULTRON One-Tap APK Download Server (scripts/serve_apk.py)
Hosts a local HTTP download portal so physical Android devices (e.g. Samsung Galaxy A16 5G)
can download and install the pre-configured ULTRON APK over Wi-Fi or Tailscale with zero cables.
"""

import os
import sys
import http.server
import socketserver
import urllib.request

PORT = 8080
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APK_DIR = os.path.join(PROJECT_ROOT, "frontend", "flutter_app", "build", "app", "outputs", "flutter-apk")
APK_FILE = os.path.join(APK_DIR, "app-debug.apk")


def get_tailscale_ip() -> str:
    try:
        import subprocess
        cmd = ["powershell", "-NoProfile", "-Command", "(Get-NetIPAddress -InterfaceAlias '*Tailscale*' -AddressFamily IPv4 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty IPAddress -First 1)"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        ip = res.stdout.strip()
        if ip:
            return ip
    except Exception:
        pass
    return "100.69.161.16"


def main():
    if not os.path.exists(APK_FILE):
        print(f"[!] APK not found at: {APK_FILE}")
        print("[*] Compiling Flutter debug APK first...")
        import subprocess
        subprocess.run(["flutter", "build", "apk", "--debug"], cwd=os.path.join(PROJECT_ROOT, "frontend", "flutter_app"), check=True)

    size_mb = round(os.path.getsize(APK_FILE) / (1024 * 1024), 1)
    ts_ip = get_tailscale_ip()

    print("======================================================================")
    print("      ULTRON ONE-TAP MOBILE INSTALLER (SAMSUNG GALAXY A16 5G)        ")
    print("======================================================================")
    print(f"[*] Binary Size   : {size_mb} MB")
    print(f"[*] APK File      : {APK_FILE}")
    print(f"[*] Private IP    : {ts_ip}")
    print(f"[*] Port          : {PORT}")
    print("----------------------------------------------------------------------")
    print(f"  STEP 1: Make sure Tailscale is connected on your Galaxy A16 5G.")
    print(f"  STEP 2: Open Chrome on your phone and visit:")
    print(f"\n      >>> http://{ts_ip}:{PORT}/app-debug.apk <<<\n")
    print(f"  STEP 3: Tap 'Download anyway' and then 'Install'.")
    print("----------------------------------------------------------------------")
    print("[*] Download server active. Press Ctrl+C when finished.")

    os.chdir(APK_DIR)
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Download server stopped.")


if __name__ == "__main__":
    main()

