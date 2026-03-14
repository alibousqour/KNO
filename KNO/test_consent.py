#!/usr/bin/env python3
"""Test ConsentManager initialization and basic operations."""

import sys
import os

# Test 1: Import ConsentManager
print("[TEST 1] Importing ConsentManager...", flush=True)
try:
    from consent_manager import ConsentManager, AuditLogger
    print("✓ ConsentManager imported successfully", flush=True)
except Exception as e:
    print(f"✗ Failed to import ConsentManager: {e}", flush=True)
    sys.exit(1)

# Test 2: Initialize ConsentManager
print("[TEST 2] Initializing ConsentManager...", flush=True)
try:
    cm = ConsentManager(settings_file="settings.json", main_window=None)
    print("✓ ConsentManager initialized successfully", flush=True)
except Exception as e:
    print(f"✗ Failed to initialize ConsentManager: {e}", flush=True)
    sys.exit(1)

# Test 3: Check permission (non-interactive)
print("[TEST 3] Checking 'file_system' permission...", flush=True)
try:
    has_permission = cm.check_permission("file_system")
    print(f"✓ check_permission returned: {has_permission}", flush=True)
except Exception as e:
    print(f"✗ Failed to check permission: {e}", flush=True)
    sys.exit(1)

# Test 4: Check evolution status
print("[TEST 4] Checking evolution status...", flush=True)
try:
    is_enabled = cm.is_evolution_enabled()
    print(f"✓ is_evolution_enabled returned: {is_enabled}", flush=True)
except Exception as e:
    print(f"✗ Failed to check evolution status: {e}", flush=True)
    sys.exit(1)

# Test 5: Verify audit logger
print("[TEST 5] Testing audit logger...", flush=True)
try:
    audit_entries = cm.get_audit_trail(limit=5)
    print(f"✓ get_audit_trail returned {len(audit_entries)} entries", flush=True)
except Exception as e:
    print(f"✗ Failed to get audit trail: {e}", flush=True)
    sys.exit(1)

print("\n" + "="*50)
print("✓ All ConsentManager tests passed!")
print("="*50)
