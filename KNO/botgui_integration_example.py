"""
BotGUI Task Manager Integration Examples
========================================

This file demonstrates how to integrate the enhanced BotGUI_new.py
with the Process Manager system for real-time monitoring and healing.
"""

import tkinter as tk
import asyncio
import threading
import time
from pathlib import Path
from hardware.processes import (
    ProcessRegistry, ProcessManager, TaskScheduler,
    Process, ProcessConfig, ProcessState
)
from BotGUI_new import FuturisticBotGUI


# ============================================================================
# Example 1: Basic Integration with monitoring
# ============================================================================

def example_1_basic_integration():
    """Basic setup: Create GUI with process registry monitoring."""
    
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Integration")
    print("="*70)
    
    # Initialize process management
    registry = ProcessRegistry(max_history_size=1000)
    manager = ProcessManager(registry)
    
    # Create Tkinter root
    root = tk.Tk()
    gui = FuturisticBotGUI(root)
    
    # Connect registry to GUI for real-time monitoring
    gui.set_process_registry(registry)
    
    print("[SETUP] ProcessRegistry connected to BotGUI")
    print("[FEATURE] Treeview will update every 1 second")
    print("[FEATURE] edex_status.json will sync every 5 seconds")
    
    # Create and register a test process
    config = ProcessConfig(
        command="python",
        args=["-c", "import time; time.sleep(10)"],
        timeout_seconds=15
    )
    
    process = Process("example_process", config)
    registry.register_process(process)
    
    print(f"[PROCESS] Registered: {process.process_id}")
    
    # Start the process (non-blocking)
    threading.Thread(
        target=manager.start,
        args=(process,),
        daemon=True
    ).start()
    
    root.mainloop()


# ============================================================================
# Example 2: Monitoring with healing events
# ============================================================================

def example_2_with_healing_alerts():
    """Setup: Monitor processes and simulate healing events."""
    
    print("\n" + "="*70)
    print("EXAMPLE 2: Healing Events and Alerts")
    print("="*70)
    
    # Initialize components
    registry = ProcessRegistry()
    manager = ProcessManager(registry)
    
    # Create GUI
    root = tk.Tk()
    gui = FuturisticBotGUI(root)
    gui.set_process_registry(registry)
    
    # Enable edex_status.json sync in workspace
    gui.task_manager.edex_status_path = "edex_status.json"
    
    # Create test processes
    processes = []
    for i in range(3):
        config = ProcessConfig(
            command="python",
            args=["-c", f"import time; time.sleep({10 + i*5})"],
            timeout_seconds=30
        )
        process = Process(f"process_{i}", config)
        registry.register_process(process)
        processes.append(process)
    
    print(f"[SETUP] Registered {len(processes)} processes")
    
    # Start processes
    for process in processes:
        threading.Thread(
            target=manager.start,
            args=(process,),
            daemon=True
        ).start()
    
    # Simulate healing events every 10 seconds
    def simulate_healing():
        """Simulate healing events for demonstration."""
        attempt = 1
        while gui.animation_alive:
            time.sleep(10)
            
            if attempt <= 3:
                process = processes[attempt % len(processes)]
                gui.record_healing_event(
                    process_id=process.process_id,
                    reason="simulated_crash",
                    retry_count=attempt
                )
                print(f"[SIM] Healing event recorded for {process.process_id}")
                
            attempt += 1
            
            if attempt > 5:
                break
    
    # Start healing simulation in background
    threading.Thread(target=simulate_healing, daemon=True).start()
    
    print("[FEATURE] Healing alerts will appear in status bar")
    print("[FEATURE] edex_status.json will include healing events")
    print("[INFO] Healing simulation active (5 events total)")
    
    root.mainloop()


# ============================================================================
# Example 3: Custom process with lifecycle management
# ============================================================================

def example_3_custom_process_lifecycle():
    """Setup: Manage process lifecycle with detailed logging."""
    
    print("\n" + "="*70)
    print("EXAMPLE 3: Custom Process Lifecycle")
    print("="*70)
    
    # Initialize
    registry = ProcessRegistry()
    manager = ProcessManager(registry)
    
    # Create GUI
    root = tk.Tk()
    gui = FuturisticBotGUI(root)
    gui.set_process_registry(registry)
    
    # Create custom process with monitoring
    class MonitoredProcess:
        def __init__(self, name, registry, gui):
            self.name = name
            self.registry = registry
            self.gui = gui
            self.running = False
            self.crash_count = 0
            self.max_crashes = 3
        
        def create(self):
            """Create and register process."""
            config = ProcessConfig(
                command="python",
                args=["-c", "import time; time.sleep(5)"],
                timeout_seconds=10
            )
            process = Process(self.name, config)
            self.registry.register_process(process)
            return process
        
        def start(self, process):
            """Start process and monitor."""
            self.running = True
            manager.start(process)
            print(f"[LIFECYCLE] {self.name} started")
        
        def simulate_crash(self):
            """Simulate crash and recovery."""
            if self.crash_count < self.max_crashes:
                self.crash_count += 1
                self.gui.record_healing_event(
                    process_id=self.name,
                    reason="simulated_crash",
                    retry_count=self.crash_count
                )
                print(f"[LIFECYCLE] {self.name} crashed (attempt {self.crash_count})")
        
        def stop(self):
            """Stop process."""
            self.running = False
            print(f"[LIFECYCLE] {self.name} stopped")
    
    # Create monitored process
    monitored = MonitoredProcess("lifecycle_process", registry, gui)
    process = monitored.create()
    monitored.start(process)
    
    # Simulate crash after delay
    def delayed_crash():
        time.sleep(3)
        monitored.simulate_crash()
    
    threading.Thread(target=delayed_crash, daemon=True).start()
    
    print("[FEATURE] Process lifecycle displayed in Treeview")
    print("[FEATURE] Crash simulation triggered after 3 seconds")
    
    root.mainloop()


# ============================================================================
# Example 4: Multiple processes with task scheduler
# ============================================================================

def example_4_task_scheduler_integration():
    """Setup: Integrate TaskScheduler with process monitoring."""
    
    print("\n" + "="*70)
    print("EXAMPLE 4: Task Scheduler Integration")
    print("="*70)
    
    # Initialize all components
    registry = ProcessRegistry()
    manager = ProcessManager(registry)
    scheduler = TaskScheduler(max_concurrent_tasks=3)
    
    # Create GUI
    root = tk.Tk()
    gui = FuturisticBotGUI(root)
    gui.set_process_registry(registry)
    
    print("[SETUP] TaskScheduler + ProcessRegistry + BotGUI integrated")
    
    # Create multiple processes
    processes_config = [
        ("web_browser", ["python", "-c", "import time; time.sleep(20)"]),
        ("audio_agent", ["python", "-c", "import time; time.sleep(20)"]),
        ("compute_worker", ["python", "-c", "import time; time.sleep(20)"]),
    ]
    
    async def scheduled_tasks():
        """Schedule and monitor tasks."""
        
        # Schedule each process as a task
        for proc_name, args in processes_config:
            config = ProcessConfig(command=args[0], args=args[1:], timeout_seconds=30)
            process = Process(proc_name, config)
            registry.register_process(process)
            
            # Start process in scheduler
            await scheduler.schedule_task(
                task_id=f"task_{proc_name}",
                coro=asyncio.to_thread(manager.start, process),
                priority="HIGH"
            )
            print(f"[SCHEDULER] Scheduled task for {proc_name}")
            
            await asyncio.sleep(0.5)
        
        # Monitor scheduler stats
        while gui.animation_alive:
            stats = await scheduler.get_stats()
            print(f"[SCHEDULER] Active: {stats['active']}, Queued: {stats['queued']}")
            await asyncio.sleep(5)
    
    # Run scheduler in background
    def run_scheduler_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(scheduled_tasks())
        except Exception as e:
            print(f"[SCHEDULER] Error: {e}")
        finally:
            asyncio.set_event_loop(None)
    
    threading.Thread(target=run_scheduler_loop, daemon=True).start()
    
    print("[FEATURE] Treeview shows all scheduled processes")
    print("[FEATURE] Monitor reliability and health status")
    print("[INFO] 3 concurrent tasks managed by scheduler")
    
    root.mainloop()


# ============================================================================
# Example 5: Full workflow with eDEX-UI sync
# ============================================================================

def example_5_full_workflow_with_edex():
    """Complete workflow: Process management with eDEX-UI synchronization."""
    
    print("\n" + "="*70)
    print("EXAMPLE 5: Full Workflow with eDEX-UI Sync")
    print("="*70)
    
    # Setup all components
    registry = ProcessRegistry(max_history_size=500)
    manager = ProcessManager(registry)
    scheduler = TaskScheduler(max_concurrent_tasks=5)
    
    # Create GUI with eDEX integration
    root = tk.Tk()
    gui = FuturisticBotGUI(root)
    gui.set_process_registry(registry)
    
    # Configure eDEX sync path
    edex_path = Path("edex_status.json")
    gui.task_manager.edex_status_path = str(edex_path)
    
    print(f"[EDEX] Syncing to: {edex_path.absolute()}")
    print(f"[EDEX] Sync interval: 5 seconds")
    print(f"[MONITORING] Treeview updates: 1 second")
    
    # Create realistic processes
    apps = [
        ("kno_main_agent", "python agent.py"),
        ("web_driver", "python web_driver.py"),
        ("audio_processor", "python audio_manager.py"),
    ]
    
    processes = []
    for name, cmd in apps:
        config = ProcessConfig(
            command="python",
            args=["-c", f"import time; time.sleep(30)"],
            timeout_seconds=45
        )
        process = Process(name, config)
        registry.register_process(process)
        processes.append(process)
    
    print(f"[PROCESSES] Created {len(processes)} processes")
    
    # Start all processes
    def start_all_processes():
        for process in processes:
            manager.start(process)
            time.sleep(0.5)
    
    threading.Thread(target=start_all_processes, daemon=True).start()
    
    # Monitor and report
    def monitor_workflow():
        """Monitor workflow and report status."""
        interval = 5
        while gui.animation_alive:
            time.sleep(interval)
            
            # Get current metrics
            metrics = registry.list_metrics()
            procs = registry.list_processes()
            
            print("\n[WORKFLOW] Current Status:")
            for metric in metrics:
                proc = next((p for p in procs if p.process_id == metric.process_id), None)
                state = proc.state.value if proc else "UNKNOWN"
                print(f"  {metric.process_id}:")
                print(f"    State: {state}")
                print(f"    Reliability: {metric.get_reliability_score():.1f}%")
                print(f"    Health: {metric.get_health_status()}")
                print(f"    Uptime: {metric.average_uptime:.1f}s")
                print(f"    Crashes: {metric.total_crashes}")
            
            # Check if edex_status.json exists
            if edex_path.exists():
                print(f"  [EDEX] JSON file synced ({edex_path.stat().st_size} bytes)")
    
    threading.Thread(target=monitor_workflow, daemon=True).start()
    
    print("\n[WORKFLOW] Start GUI to see:")
    print("  - Real-time process list (updated every 1s)")
    print("  - Reliability scores with color coding")
    print("  - Health status and crash tracking")
    print("  - eDEX-UI JSON sync (every 5s)")
    
    root.mainloop()


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("BotGUI Task Manager Integration Examples")
    print("="*70)
    print("\nUsage: python botgui_integration_example.py [1|2|3|4|5]")
    print("\nExamples:")
    print("  1 - Basic integration (recommended first)")
    print("  2 - Healing events and alerts")
    print("  3 - Custom process lifecycle")
    print("  4 - Task scheduler integration")
    print("  5 - Full workflow with eDEX sync")
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        
        if example_num == "1":
            example_1_basic_integration()
        elif example_num == "2":
            example_2_with_healing_alerts()
        elif example_num == "3":
            example_3_custom_process_lifecycle()
        elif example_num == "4":
            example_4_task_scheduler_integration()
        elif example_num == "5":
            example_5_full_workflow_with_edex()
        else:
            print(f"\nUnknown example: {example_num}")
            print("Use 1, 2, 3, 4, or 5")
    else:
        print("\nRunning Example 5 (Full Workflow) by default...")
        print("Press Ctrl+C to stop\n")
        example_5_full_workflow_with_edex()
