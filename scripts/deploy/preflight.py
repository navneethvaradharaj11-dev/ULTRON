#!/usr/bin/env python3
"""
PROJECT ULTRON — PRODUCTION ENVIRONMENT PREFLIGHT VALIDATOR
Executes strict pre-flight security and infrastructure checks.
FAILS CLOSED with non-zero exit code if production constraints are violated.
"""

import os
import sys
import shutil

def run_preflight():
    print("==================================================")
    print("🔍 ULTRON PRODUCTION PRE-FLIGHT VALIDATION")
    print("==================================================")

    failures = []
    warnings = []

    # 1. Environment & Mode Check
    env_mode = os.getenv("ENVIRONMENT", "development").lower()
    debug_mode = os.getenv("DEBUG", "true").lower() == "true"
    print(f"📌 Environment Mode: '{env_mode}'")
    print(f"📌 Debug Mode: {debug_mode}")

    if env_mode == "production" and debug_mode:
        failures.append("SECURITY RISK: DEBUG=True is prohibited in production mode.")

    # 2. JWT Secret Validation
    jwt_secret = os.getenv("JWT_SECRET", "")
    if env_mode == "production":
        if not jwt_secret or "change_in_production" in jwt_secret or len(jwt_secret) < 32:
            failures.append("SECURITY RISK: JWT_SECRET must be set and >= 32 characters in production.")
    else:
        if not jwt_secret:
            warnings.append("JWT_SECRET is unset; fallback secret will be used in development.")

    # 3. Database Credentials Check
    mysql_pass = os.getenv("MYSQL_PASSWORD", "")
    if env_mode == "production" and (mysql_pass == "root" or not mysql_pass):
        failures.append("SECURITY RISK: Default or empty MYSQL_PASSWORD is prohibited in production.")

    # 4. CORS Origins Check
    cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "*")
    if env_mode == "production" and cors_origins == "*":
        failures.append("SECURITY RISK: Wildcard CORS_ALLOWED_ORIGINS '*' is prohibited in production.")

    # 5. Required Workspace Directories
    required_dirs = ["/opt/ultron/backups", "/opt/ultron/logs", "sandbox"]
    for d in required_dirs:
        if not os.path.exists(d):
            try:
                os.makedirs(d, exist_ok=True)
                print(f"📁 Created required directory: {d}")
            except Exception as e:
                warnings.append(f"Could not create directory '{d}': {e}")

    # 6. Docker Binary Check
    docker_path = shutil.which("docker")
    if not docker_path:
        warnings.append("Docker executable not found in PATH on current execution node.")
    else:
        print(f"✅ Docker found: {docker_path}")

    # Print Report
    print("\n--- Pre-Flight Audit Report ---")
    if warnings:
        print("⚠️ Warnings:")
        for w in warnings:
            print(f"  - {w}")

    if failures:
        print("\n❌ PRE-FLIGHT VALIDATION FAILED (FAIL-CLOSED):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

    print("\n✅ PRE-FLIGHT VALIDATION PASSED SUCCESSFULLY.")
    sys.exit(0)

if __name__ == "__main__":
    run_preflight()
