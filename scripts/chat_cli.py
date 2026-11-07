#!/usr/bin/env python3
"""
ULTRON Interactive Terminal Console (scripts/chat_cli.py)
Direct, real-time command-line interface to interact with the ULTRON Agentic AI Operating System.
Connects via Tailscale or localhost gateway.
"""

import sys
import json
import urllib.request
import urllib.error
import time

GATEWAY_CANDIDATES = [
    "http://100.69.161.16:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8000"
]

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"


def probe_gateway() -> str:
    """Find active listening ULTRON gateway."""
    for host in GATEWAY_CANDIDATES:
        try:
            req = urllib.request.Request(f"{host}/health", headers={"User-Agent": "ULTRON-CLI"})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                if resp.status == 200:
                    return host
        except Exception:
            continue
    return GATEWAY_CANDIDATES[0]


def authenticate(base_url: str) -> tuple[str, str]:
    """Obtain or generate operator JWT token."""
    user = "operator_cli"
    password = "CliSecurePassword123!"

    # 1. Register if needed
    reg_url = f"{base_url}/api/v1/auth/register"
    reg_payload = json.dumps({"username": user, "email": "operator@ultron.internal", "password": password}).encode()
    try:
        req = urllib.request.Request(reg_url, data=reg_payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=3.0)
    except urllib.error.HTTPError:
        pass  # User already registered

    # 2. Login
    login_url = f"{base_url}/api/v1/auth/login"
    login_payload = json.dumps({"username": user, "password": password}).encode()
    try:
        req = urllib.request.Request(login_url, data=login_payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode())
            return data.get("access_token", ""), user
    except Exception as e:
        print(f"{RED}[ERROR] Authentication failed: {e}{RESET}")
        return "", ""


def send_chat_message(base_url: str, token: str, prompt: str):
    """Send natural language request to ULTRON AI Engine."""
    url = f"{base_url}/api/v1/ai/generate"
    payload = json.dumps({
        "prompt": prompt,
        "system_instruction": "You are ULTRON, the master personal agentic operating system. Provide sharp, intelligent, professional responses."
    }).encode()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    try:
        req = urllib.request.Request(url, data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=15.0) as resp:
            data = json.loads(resp.read().decode())
            return data.get("response", ""), data.get("provider_used", "ai"), data.get("model_used", "model")
    except Exception as e:
        return f"Error contacting AI engine: {e}", "error", "none"


def main():
    print(f"{CYAN}{BOLD}======================================================================{RESET}")
    print(f"{CYAN}{BOLD}           U L T R O N   T E R M I N A L   C O N S O L E              {RESET}")
    print(f"{CYAN}{BOLD}               Personal Agentic AI Operating System                   {RESET}")
    print(f"{CYAN}{BOLD}======================================================================{RESET}")

    print(f"[*] Probing ULTRON Gateways...")
    gateway = probe_gateway()
    print(f"[*] Connected to Gateway: {GREEN}{gateway}{RESET}")

    token, user = authenticate(gateway)
    if not token:
        print(f"{YELLOW}[!] Running in guest mode.{RESET}")
    else:
        print(f"[*] Authenticated as: {GREEN}{user}{RESET}")

    print(f"\n{YELLOW}Type your command or message. Enter '/help' for options, or 'exit' to quit.{RESET}\n")

    while True:
        try:
            user_input = input(f"{BOLD}{GREEN}YOU > {RESET}").strip()
            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", ":q"):
                print(f"{CYAN}ULTRON standing by. Goodbye.{RESET}")
                break

            if user_input.lower() == "/help":
                print(f"\n{BOLD}Commands:{RESET}")
                print("  /status   - Show system capabilities and database health")
                print("  /ai       - Show active AI provider and model diagnostics")
                print("  /clear    - Clear terminal screen")
                print("  exit      - Close console\n")
                continue

            if user_input.lower() == "/status":
                req = urllib.request.Request(f"{gateway}/health")
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    print(json.dumps(json.loads(resp.read().decode()), indent=2))
                continue

            if user_input.lower() == "/ai":
                req = urllib.request.Request(f"{gateway}/api/v1/ai/status")
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    print(json.dumps(json.loads(resp.read().decode()), indent=2))
                continue

            if user_input.lower() == "/clear":
                import os
                os.system("cls" if os.name == "nt" else "clear")
                continue

            # Stream thinking indicator
            print(f"{MAGENTA}ULTRON is thinking...{RESET}", end="\r")
            t0 = time.time()
            reply, provider, model = send_chat_message(gateway, token, user_input)
            latency = int((time.time() - t0) * 1000)

            print(" " * 30, end="\r")  # clear thinking
            print(f"{CYAN}{BOLD}ULTRON [{provider}:{model}] ({latency}ms):{RESET}")
            print(f"{reply}\n")

        except (KeyboardInterrupt, EOFError):
            print(f"\n{CYAN}Session ended.{RESET}")
            break


if __name__ == "__main__":
    main()
