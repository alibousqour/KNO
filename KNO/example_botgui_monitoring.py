#!/usr/bin/env python3
"""
Example: BotGUI Process Monitoring Integration

Demonstrates how to integrate the enhanced FuturisticBotGUI with async
process registry monitoring for real-time process status display.

Features:
- Creates mock processes
- Registers them with ProcessRegistry
- Displays metrics in real-time Treeview
- Simulates process lifecycle events
"""

import tkinter as tk
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from BotGUI_new import FuturisticBotGUI
from hardware.processes.process_registry import ProcessRegistry, ProcessMetrics
from hardware.processes.process_manager import Process, ProcessConfig, ProcessState


class MockProcessSimulator:
    """Simulates process lifecycle for demonstration."""
    
    def __init__(self, registry: ProcessRegistry):
        self.registry = registry
        self.processes = {}
    
    def create_mock_process(
        self,
        process_id: str,
        command: str = "mock_process.py"
    ) -> Process:
        """Create and register a mock process."""
        config = ProcessConfig(
            command=command,
            args=[],
            auto_restart=True,
            restart_delay=5,
            max_restarts=3
        )
        
        process = Process(process_id=process_id, config=config)
        self.registry.register_process(process)
        self.processes[process_id] = process
        
        print(f"[SIMULATOR] Created mock process: {process_id}")
        return process
    
    async def simulate_process_lifecycle(
        self,
        process_id: str,
        duration: float = 30.0,
        crash_at: float = None
    ) -> None:
        """Simulate a process lifecycle with optional crash.
        
        Args:
            process_id: Process to simulate
            duration: How long process runs
            crash_at: Seconds to crash (None = no crash)
        """
        # Start process
        self.registry.update_metrics_on_start(process_id)
        process = self.processes[process_id]
        process.state = ProcessState.RUNNING
        print(f"[SIMULATOR] Started: {process_id}")
        
        start_time = asyncio.get_event_loop().time()
        
        # Run until duration or crash
        while asyncio.get_event_loop().time() - start_time < duration:
            elapsed = asyncio.get_event_loop().time() - start_time
            
            # Check for crash condition
            if crash_at and elapsed >= crash_at:
                self.registry.update_metrics_on_crash(process_id)
                process.state = ProcessState.CRASHED
                print(f"[SIMULATOR] Crashed: {process_id}")
                
                # Auto-restart after delay
                await asyncio.sleep(3)
                self.registry.update_metrics_on_restart(process_id)
                process.state = ProcessState.RUNNING
                print(f"[SIMULATOR] Restarted: {process_id}")
                
                crash_at = None  # Don't crash again
            
            await asyncio.sleep(0.5)
        
        # Graceful stop
        uptime = asyncio.get_event_loop().time() - start_time
        self.registry.update_metrics_on_stop(process_id, uptime)
        process.state = ProcessState.STOPPED
        print(f"[SIMULATOR] Stopped: {process_id} (uptime: {uptime:.1f}s)")


async def run_simulation(registry: ProcessRegistry) -> None:
    """Run a realistic process simulation."""
    simulator = MockProcessSimulator(registry)
    
    # Create several mock processes
    print("\n[EXAMPLE] Creating mock processes...")
    simulator.create_mock_process("worker_1", "worker_process.py")
    simulator.create_mock_process("worker_2", "worker_process.py")
    simulator.create_mock_process("audio_processor", "audio_engine.py")
    simulator.create_mock_process("data_sync", "data_sync.py")
    
    # Simulate their lifecycles
    print("[EXAMPLE] Starting process simulations...\n")
    
    # Worker 1: Normal operation
    task1 = asyncio.create_task(
        simulator.simulate_process_lifecycle("worker_1", duration=45.0)
    )
    
    # Worker 2: Will crash and recover
    task2 = asyncio.create_task(
        simulator.simulate_process_lifecycle("worker_2", duration=50.0, crash_at=15.0)
    )
    
    # Audio processor: Shorter lifetime
    task3 = asyncio.create_task(
        simulator.simulate_process_lifecycle("audio_processor", duration=30.0)
    )
    
    # Data sync: Normal operation
    task4 = asyncio.create_task(
        simulator.simulate_process_lifecycle("data_sync", duration=40.0)
    )
    
    # Run all simulations concurrently
    await asyncio.gather(task1, task2, task3, task4)
    
    print("\n[EXAMPLE] All simulations complete!")


def main():
    """Main entry point."""
    print("=" * 70)
    print("BotGUI Process Monitoring Integration Example")
    print("=" * 70)
    print("\nThis example demonstrates:")
    print("  • Real-time process registry monitoring")
    print("  • Async Treeview updates every 2 seconds")
    print("  • Process lifecycle simulation (start/crash/restart/stop)")
    print("  • Thread-safe Tkinter integration")
    print("\nWatch the Treeview update as processes start, run, crash, and stop.")
    print("Press ESC to exit the GUI.\n")
    print("=" * 70 + "\n")
    
    # Create Tkinter root
    root = tk.Tk()
    
    # Create GUI
    gui = FuturisticBotGUI(root)
    
    # Create process registry
    registry = ProcessRegistry(max_history_size=500)
    
    # Connect registry to GUI
    gui.set_process_registry(registry)
    print("[MAIN] Process monitoring connected to GUI\n")
    
    # Start simulation in background thread
    import threading
    
    def run_simulation_thread():
        """Run simulation in background thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_simulation(registry))
        finally:
            loop.close()
    
    sim_thread = threading.Thread(target=run_simulation_thread, daemon=True)
    sim_thread.start()
    
    # Start GUI (blocking)
    print("[MAIN] Launching GUI...\n")
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n[MAIN] Interrupted by user")
    except Exception as e:
        print(f"\n[MAIN] Error: {e}")
    finally:
        print("[MAIN] Shutting down...")


if __name__ == "__main__":
    main()
