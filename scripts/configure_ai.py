#!/usr/bin/env python3
"""
ULTRON AI Provider Configuration Wizard (scripts/configure_ai.py)
Tests and activates real LLM credentials (Google Gemini, OpenAI, NVIDIA NIM, Ollama)
and synchronizes both .env and the active Docker container.
"""

import os
import sys
import time
import argparse
import subprocess

ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")


def update_env(provider: str, model: str, api_key: str):
    """Update AI settings in .env file."""
    if not os.path.exists(ENV_FILE):
        print(f"[ERROR] .env file not found at: {ENV_FILE}")
        return False

    with open(ENV_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    found_prov = False
    found_model = False
    found_key = False

    for line in lines:
        if line.startswith("AI_PROVIDER="):
            new_lines.append(f"AI_PROVIDER={provider}\n")
            found_prov = True
        elif line.startswith("AI_MODEL_NAME="):
            new_lines.append(f"AI_MODEL_NAME={model}\n")
            found_model = True
        elif line.startswith("AI_API_KEY="):
            new_lines.append(f"AI_API_KEY={api_key}\n")
            found_key = True
        else:
            new_lines.append(line)

    if not found_prov:
        new_lines.append(f"AI_PROVIDER={provider}\n")
    if not found_model:
        new_lines.append(f"AI_MODEL_NAME={model}\n")
    if not found_key:
        new_lines.append(f"AI_API_KEY={api_key}\n")

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    return True


def test_gemini_key(api_key: str, model_name: str) -> bool:
    """Test Gemini API key with a live 1-turn call."""
    print(f"[*] Testing Gemini API key with model '{model_name}'...")
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        t0 = time.time()
        res = client.models.generate_content(
            model=model_name,
            contents="Respond with 'ULTRON_ONLINE' to verify connectivity."
        )
        elapsed = round(time.time() - t0, 2)
        print(f"[PASS] Connection successful! Latency: {elapsed}s")
        print(f"[PASS] Model Response: {res.text.strip()}")
        return True
    except Exception as e:
        print(f"[ERROR] Gemini API verification failed: {e}")
        return False


def test_openai_key(api_key: str, model_name: str, base_url: str = None) -> bool:
    """Test OpenAI/NVIDIA API key with a live call."""
    print(f"[*] Testing API key with model '{model_name}'...")
    try:
        import urllib.request
        import json

        url = f"{base_url.rstrip('/')}/chat/completions" if base_url else "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "model": model_name,
            "messages": [{"role": "user", "content": "Respond with 'ULTRON_ONLINE'"}]
        }).encode()

        req = urllib.request.Request(url, data=data, headers=headers)
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            elapsed = round(time.time() - t0, 2)
            res_json = json.loads(resp.read().decode())
            text = res_json["choices"][0]["message"]["content"]
            print(f"[PASS] Connection successful! Latency: {elapsed}s")
            print(f"[PASS] Model Response: {text.strip()}")
            return True
    except Exception as e:
        print(f"[ERROR] API verification failed: {e}")
        return False


def sync_container():
    """Copy updated .env to running container and restart."""
    print("[*] Synchronizing Docker container...")
    try:
        subprocess.run(["wsl", "docker", "cp", ".env", "ultron_backend:/app/.env"], check=True)
        subprocess.run(["wsl", "docker", "restart", "ultron_backend"], check=True)
        print("[PASS] Docker backend restarted with new credentials.")
        return True
    except Exception as e:
        print(f"[WARN] Could not automatically sync container: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Configure ULTRON AI Provider")
    parser.add_argument("--provider", choices=["gemini", "openai", "nvidia", "ollama", "mock"], default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--key", default=None)
    parser.add_argument("--skip-test", action="store_true", help="Skip live connection test")
    args = parser.parse_args()

    provider = args.provider
    model = args.model
    api_key = args.key

    print("======================================================================")
    print("            ULTRON AI PROVIDER CONFIGURATION WIZARD                   ")
    print("======================================================================")

    if not provider:
        print("Select Provider:")
        print("  [1] Google Gemini (Recommended - Free tier available)")
        print("  [2] OpenAI (GPT-4o / GPT-4o-mini)")
        print("  [3] NVIDIA NIM")
        print("  [4] Ollama (Local ₹0 offline)")
        print("  [5] Mock (Air-gapped development)")
        choice = input("Enter choice [1-5]: ").strip()
        mapping = {"1": "gemini", "2": "openai", "3": "nvidia", "4": "ollama", "5": "mock"}
        provider = mapping.get(choice, "gemini")

    default_models = {
        "gemini": "gemini-2.5-flash",
        "openai": "gpt-4o-mini",
        "nvidia": "meta/llama-3.1-8b-instruct",
        "ollama": "llama3.2",
        "mock": "mock-ultron-v1"
    }

    if not model:
        def_model = default_models.get(provider, "gemini-2.5-flash")
        user_m = input(f"Enter model identifier [Default: {def_model}]: ").strip()
        model = user_m if user_m else def_model

    if not api_key and provider not in ("ollama", "mock"):
        api_key = input(f"Enter API Key for {provider}: ").strip()

    if not api_key:
        api_key = "mock_key"

    # Test key
    valid = True
    if not args.skip_test and provider not in ("ollama", "mock") and api_key != "mock_key":
        if provider == "gemini":
            valid = test_gemini_key(api_key, model)
        elif provider == "openai":
            valid = test_openai_key(api_key, model)
        elif provider == "nvidia":
            valid = test_openai_key(api_key, model, base_url="https://integrate.api.nvidia.com/v1")

    if not valid:
        proceed = input("Live test failed. Save credentials anyway? [y/N]: ").strip().lower()
        if proceed != "y":
            print("[ABORT] Configuration cancelled.")
            sys.exit(1)

    # Save to .env
    if update_env(provider, model, api_key):
        print(f"[PASS] Saved AI_PROVIDER={provider}, AI_MODEL_NAME={model} to .env")
        sync_container()
        print("\n[SUCCESS] AI Provider activation complete!")
    else:
        print("[ERROR] Failed to update .env")


if __name__ == "__main__":
    main()
