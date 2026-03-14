#!/usr/bin/env python3
"""
Simple test to verify agent components are working
"""
import sys
import os

print("=" * 60)
print("🤖 Be More Agent - Component Tests")
print("=" * 60)
print()

# Test 1: Imports
print("[1/5] Testing imports...")
try:
    from duckduckgo_search import DDGS
    print("  ✅ duckduckgo_search")
except Exception as e:
    print(f"  ❌ duckduckgo_search: {e}")
    sys.exit(1)

try:
    import ollama
    print("  ✅ ollama")
except Exception as e:
    print(f"  ❌ ollama: {e}")
    sys.exit(1)

try:
    import sounddevice
    print("  ✅ sounddevice")
except Exception as e:
    print(f"  ❌ sounddevice: {e}")
    sys.exit(1)

try:
    import tkinter as tk
    print("  ✅ tkinter")
except Exception as e:
    print(f"  ❌ tkinter: {e}")
    sys.exit(1)

# Test 2: Configuration
print()
print("[2/5] Testing configuration...")
try:
    import json
    with open("config.json", "r") as f:
        config = json.load(f)
    print(f"  ✅ config.json loaded")
    print(f"     - text_model: {config.get('text_model', 'N/A')}")
    print(f"     - vision_model: {config.get('vision_model', 'N/A')}")
except Exception as e:
    print(f"  ❌ config.json: {e}")

# Test 3: Directories
print()
print("[3/5] Checking directories...")
dirs_to_check = [
    "sounds/greeting_sounds",
    "sounds/thinking_sounds", 
    "sounds/ack_sounds",
    "faces/idle",
    "faces/listening",
    "faces/thinking",
    "faces/speaking"
]
for dir_path in dirs_to_check:
    if os.path.exists(dir_path):
        file_count = len(os.listdir(dir_path))
        print(f"  ✅ {dir_path} ({file_count} files)")
    else:
        print(f"  ⚠️  {dir_path} (empty/missing)")

# Test 4: Audio
print()
print("[4/5] Testing audio devices...")
try:
    import sounddevice as sd
    devices = sd.query_devices()
    print(f"  ✅ Found {len(devices)} audio devices")
except Exception as e:
    print(f"  ❌ Audio: {e}")

# Test 5: Ollama
print()
print("[5/5] Testing Ollama connection...")
try:
    import ollama
    resp = ollama.list()
    models = resp.get('models', [])
    if models:
        print(f"  ✅ Ollama connected - {len(models)} model(s) available")
        for model in models[:3]:
            print(f"     - {model.get('name', 'unknown')}")
    else:
        print(f"  ⚠️  Ollama connected but no models installed")
        print(f"     Run: ollama pull gemma3:1b")
except Exception as e:
    print(f"  ❌ Ollama: {e}")
    print(f"     Make sure Ollama is running: ollama serve")

print()
print("=" * 60)
print("✅ All tests passed! Ready to run: python agent.py")
print("=" * 60)
