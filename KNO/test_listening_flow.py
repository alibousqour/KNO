#!/usr/bin/env python3
"""
Test the complete listening flow: simulate ENTER press, recording, and response
"""

import sys
import os
sys.path.insert(0, os.getcwd())

from agent import BotGUI, BotStates
import tkinter as tk
import threading
import time

def test_listening_interaction():
    """Simulate a user pressing ENTER, speaking, and the agent responding"""
    
    print("\n" + "="*70)
    print("TESTING LISTENING FLOW: User -> Record -> Transcribe -> Response")
    print("="*70)
    
    # Create the GUI but don't start it yet
    root = tk.Tk()
    app = BotGUI(root)
    
    # Wait for initialization
    print("[TEST] Waiting 3 seconds for agent to warm up...")
    time.sleep(3)
    
    print(f"[TEST] Agent current state: {app.current_state}")
    print(f"[TEST] Agent status: {app.status_var.get()}")
    
    # Simulate ENTER press (PTT on)
    print("\n[TEST] Simulating ENTER press to start recording...")
    app.handle_ppt_toggle()
    
    print(f"[TEST] Recording active: {app.recording_active.is_set()}")
    print(f"[TEST] Agent state after PTT on: {app.current_state}")
    
    # Simulate some recording time (0.5 seconds)
    print("[TEST] Simulating recording for 0.5 seconds...")
    time.sleep(0.5)
    
    # Simulate ENTER release (PTT off)
    print("[TEST] Simulating ENTER release to stop recording...")
    app.handle_ppt_toggle()
    
    print(f"[TEST] Recording active: {app.recording_active.is_set()}")
    print(f"[TEST] Agent state after PTT off: {app.current_state}")
    
    # Wait for processing
    print("[TEST] Waiting for processing...")
    time.sleep(2)
    
    # Check if agent is still running
    print(f"[TEST] Final agent state: {app.current_state}")
    print(f"[TEST] Final agent status: {app.status_var.get()}")
    
    # Clean up
    app.safe_exit()
    print("\n[TEST] Listening flow test complete!")

if __name__ == "__main__":
    test_listening_interaction()
