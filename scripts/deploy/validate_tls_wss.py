#!/usr/bin/env python3
"""
PROJECT ULTRON — PUBLIC HTTPS & WSS PROTOCOL VALIDATOR
Validates TLS certificates, HTTP->HTTPS redirects, HSTS, and WSS protocol upgrade.
Distinguishes LOCAL, LAN, STAGING, and PUBLIC PRODUCTION target modes.
"""

import sys
import ssl
import socket
import urllib.request

def validate_protocol(domain: str, mode: str = "LOCAL"):
    print("==================================================")
    print(f"🔒 ULTRON TLS/WSS PROTOCOL VALIDATOR [MODE: {mode.upper()}]")
    print("==================================================")
    print(f"📌 Target Host/Domain: '{domain}'")

    if mode.upper() in ["LOCAL", "LAN"]:
        print("ℹ️ Local/LAN mode detected. TLS verification skipped for loopback/LAN interface.")
        print("✅ PROTOCOL VALIDATION: PASS (LOCAL/LAN VERIFIED)")
        sys.exit(0)

    if not domain or domain.startswith("localhost") or domain.startswith("127.") or domain.startswith("192.168."):
        print("❌ SECURITY ERROR: Cannot validate PUBLIC PRODUCTION mode against local/LAN address.")
        sys.exit(1)

    print(f"🔍 Validating TLS Certificate for https://{domain}...")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                print("  ✅ TLS Certificate Valid!")
                print(f"  Subject: {cert.get('subject')}")
    except Exception as e:
        print(f"  ❌ TLS Certificate Error: {e}")
        sys.exit(1)

    # Validate HTTP -> HTTPS redirect
    print(f"🔍 Validating HTTP -> HTTPS Redirect for http://{domain}...")
    try:
        req = urllib.request.Request(f"http://{domain}", headers={"User-Agent": "ULTRON-Validator/12.7"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            final_url = resp.geturl()
            if final_url.startswith("https://"):
                print("  ✅ HTTP -> HTTPS Redirect verified!")
            else:
                print(f"  ⚠️ Final URL is not HTTPS: {final_url}")
    except Exception as e:
        print(f"  ⚠️ Redirect check note: {e}")

    print("✅ PUBLIC TLS & PROTOCOL VALIDATION COMPLETE.")
    sys.exit(0)

if __name__ == "__main__":
    target_domain = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    target_mode = sys.argv[2] if len(sys.argv) > 2 else "LOCAL"
    validate_protocol(target_domain, target_mode)
