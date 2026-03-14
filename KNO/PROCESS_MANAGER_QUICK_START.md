"""
Process & Task Management - Quick Start Guide

Fast introduction to KNO v6.0 Process Management system.
Get up and running in 5 minutes.
"""

# ============================================================================
# QUICK START - 5 MINUTE SETUP
# ============================================================================

"""
STEP 1: Installing
──────────────────

Dependencies:
  ✓ Python 3.9+
  ✓ asyncio (built-in)
  ✓ subprocess (built-in)
  ✓ threading (built-in)

No additional packages required!


STEP 2: Basic Import
────────────────────

from hardware.processes import (
    TaskScheduler,
    TaskPriority,
    ProcessHealer,
    HealingStrategy,
)


STEP 3: Your First Task (30 seconds)
────────────────────────────────────

import asyncio

async def main():
    # Create scheduler
    scheduler = TaskScheduler()
    await scheduler.start()
    
    # Schedule a task
    task = await scheduler.schedule_task(
        process_id="my_app",
        command="echo 'Hello from KNO Process Manager!'",
        priority=TaskPriority.NORMAL
    )
    
    # Wait for completion
    while task.status.value not in ['completed', 'failed']:
        await asyncio.sleep(0.5)
    
    print(f"Status: {task.status.value}")
    
    # Cleanup
    await scheduler.stop()

asyncio.run(main())


RESULT:
  Status: completed
  ✓ First process task executed!
"""


# ============================================================================
# COMMON USE CASES
# ============================================================================

"""
USE CASE 1: Run an External Application
────────────────────────────────────────

import asyncio
from hardware.processes import TaskScheduler, TaskPriority

async def run_notepad():
    scheduler = TaskScheduler()
    await scheduler.start()
    
    # Launch Notepad (Windows) or gedit (Linux)
    import sys
    cmd = "notepad.exe" if sys.platform == "win32" else "gedit"
    
    task = await scheduler.schedule_task(
        process_id="editor",
        command=cmd,
        name="Text Editor",
        priority=TaskPriority.HIGH
    )
    
    print(f"Editor launched, task ID: {task.task_id}")
    
    # Keep scheduler running
    while True:
        stats = await scheduler.get_stats()
        if stats['concurrent_running'] == 0:
            break
        await asyncio.sleep(1)
    
    await scheduler.stop()

asyncio.run(run_notepad())


USE CASE 2: Auto-Restart on Crash (Self-Healing)
──────────────────────────────────────────────────

import asyncio
from hardware.processes import (
    ProcessManager,
    ProcessHealer,
    HealingStrategy,
    RetryPolicy
)

async def resilient_service():
    # Create process
    manager = ProcessManager()
    process = manager.create_process(
        "my_service",
        "python service.py",
        auto_restart=True,
        max_retries=5  # Restart up to 5 times
    )
    
    # Setup healing
    healer = ProcessHealer(
        healing_strategy=HealingStrategy.EXPONENTIAL_BACKOFF,
        retry_policy=RetryPolicy(
            max_retries=5,
            initial_delay=2.0,
            max_delay=30.0
        )
    )
    
    healer.add_process(process)
    await healer.start_monitoring()
    
    # Start service
    await process.start()
    
    # Monitor
    for _ in range(60):
        running = await process.is_running()
        print(f"Service running: {running}")
        await asyncio.sleep(1)

asyncio.run(resilient_service())


USE CASE 3: Priority-Based Task Queue
──────────────────────────────────────

import asyncio
from hardware.processes import TaskScheduler, TaskPriority

async def priority_workflow():
    scheduler = TaskScheduler(max_concurrent_tasks=3)
    await scheduler.start()
    
    # Critical task
    await scheduler.schedule_task(
        "system_init",
        "setup.py",
        priority=TaskPriority.CRITICAL
    )
    
    # Important tasks
    for i in range(3):
        await scheduler.schedule_task(
            f"service_{i}",
            f"service.py --id {i}",
            priority=TaskPriority.HIGH
        )
    
    # Background tasks
    await scheduler.schedule_task(
        "cleanup",
        "cleanup.py",
        priority=TaskPriority.LOW
    )
    
    # Monitor execution order
    stats = await scheduler.get_stats()
    print(f"Queue size: {stats['queue_size']}")
    print("Tasks will execute in priority order")
    
    # Wait for all
    await asyncio.sleep(30)
    await scheduler.stop()

asyncio.run(priority_workflow())


USE CASE 4: Track Process Health
─────────────────────────────────

import asyncio
from hardware.processes import ProcessRegistry, ProcessManager

async def health_monitoring():
    registry = ProcessRegistry()
    manager = ProcessManager()
    
    # Create and register process
    process = manager.create_process(
        "app",
        "python app.py"
    )
    registry.register_process(process)
    
    # Simulate lifecycle
    registry.update_metrics_on_start(process.process_id)
    await asyncio.sleep(2)
    registry.update_metrics_on_stop(process.process_id, uptime_seconds=2.0)
    
    # Check health
    metrics = registry.get_metrics(process.process_id)
    print(f"Health: {metrics.get_health_status()}")
    print(f"Reliability: {metrics.get_reliability_score():.1f}%")
    
    # Summary
    summary = registry.get_system_summary()
    print(f"Total processes: {summary['total_processes']}")
    print(f"Healthy: {summary['healthy_processes']}")

asyncio.run(health_monitoring())
"""


# ============================================================================
# HEALING STRATEGIES EXPLAINED
# ============================================================================

"""
Choose the right healing strategy for your use case:

IMMEDIATE
  └─ Restart instantly
  └─ Use for: Quick utilities, stateless services
  └─ Risk: May thrash if broken

    HealingStrategy.IMMEDIATE


EXPONENTIAL_BACKOFF (Recommended)
  └─ 5s, 10s, 20s, 40s... (doubles each time)
  └─ Use for: Most services, unknown stability
  └─ Benefit: Prevents rapid failure cycles

    HealingStrategy.EXPONENTIAL_BACKOFF


LINEAR_BACKOFF
  └─ 5s, 10s, 15s, 20s... (steady increase)
  └─ Use for: Well-understood services
  └─ Benefit: Predictable restart timing

    HealingStrategy.LINEAR_BACKOFF


ADAPTIVE
  └─ Auto-adjusts based on crash frequency
  └─ Use for: Production systems
  └─ Benefit: Self-optimizing

    HealingStrategy.ADAPTIVE


CIRCUIT_BREAKER
  └─ Stop restarting after threshold
  └─ Use for: Critical systems safety
  └─ Benefit: Prevents resource exhaustion

    HealingStrategy.CIRCUIT_BREAKER
"""


# ============================================================================
# COMMON PATTERNS
# ============================================================================

"""
PATTERN: Sequential Workflow
─────────────────────────────

async def sequential_workflow():
    scheduler = TaskScheduler()
    await scheduler.start()
    
    steps = [
        ("step_1", "python step1.py"),
        ("step_2", "python step2.py"),
        ("step_3", "python step3.py"),
    ]
    
    for proc_id, cmd in steps:
        task = await scheduler.schedule_task(
            proc_id, cmd,
            priority=TaskPriority.CRITICAL
        )
        
        # Wait for completion
        while task.status.value not in ['completed', 'failed']:
            await asyncio.sleep(0.5)
        
        print(f"✓ {proc_id} completed")
    
    await scheduler.stop()


PATTERN: Parallel Batch
──────────────────────

async def parallel_batch():
    scheduler = TaskScheduler(max_concurrent_tasks=10)
    await scheduler.start()
    
    # Schedule 10 tasks in parallel
    tasks = []
    for i in range(10):
        task = await scheduler.schedule_task(
            f"job_{i}",
            f"process.py --id {i}",
            priority=TaskPriority.NORMAL
        )
        tasks.append(task)
    
    print(f"Scheduled {len(tasks)} tasks, max 10 concurrent")
    
    await asyncio.sleep(30)
    await scheduler.stop()


PATTERN: Monitor with HAL
──────────────────────────

async def monitor_with_hardware():
    from hardware import HardwareManager
    
    hw = HardwareManager()
    scheduler = TaskScheduler()
    await scheduler.start()
    
    # Schedule task
    task = await scheduler.schedule_task(
        "heavy_task",
        "analyze_data.py"
    )
    
    # Monitor with HAL
    while task.status.value == 'running':
        cpu = await hw.cpu.get_usage(per_core=False)
        mem = await hw.memory.get_usage()
        
        print(f"CPU: {cpu}%, Memory: {mem}%")
        
        if mem > 80:
            await scheduler.pause_task(task.task_id)
            await asyncio.sleep(5)
            await scheduler.resume_task(task.task_id)
        
        await asyncio.sleep(2)
    
    await scheduler.stop()
"""


# ============================================================================
# CONFIGURATION REFERENCE
# ============================================================================

"""
TaskScheduler Configuration
───────────────────────────

scheduler = TaskScheduler(
    max_concurrent_tasks=5,      # Concurrent execution limit
    default_ttl_seconds=300      # Default 5-minute timeout
)


Task Configuration
──────────────────

task = await scheduler.schedule_task(
    process_id="unique_id",           # Required: unique ID
    command="command --args",         # Required: shell command
    name="Display Name",              # Optional: user-friendly name
    priority=TaskPriority.NORMAL,    # Optional: execution priority
    ttl_seconds=300,                  # Optional: timeout in seconds
    auto_restart=False,               # Optional: auto-restart on crash
    max_retries=3,                    # Optional: max restart attempts
    # Additional ProcessConfig options
    cwd="/path/to/working/dir",      # Working directory
    shell=False,                       # Use shell interpreter
    timeout=10.0,                      # Start timeout
    capture_output=True,               # Capture stdout/stderr
)


Healing Configuration
─────────────────────

healer = ProcessHealer(
    healing_strategy=HealingStrategy.EXPONENTIAL_BACKOFF,
    retry_policy=RetryPolicy(
        max_retries=5,                # -1 = unlimited
        initial_delay=5.0,            # Seconds
        max_delay=300.0,              # Seconds max
        backoff_multiplier=2.0,       # For exponential
        crash_threshold=3,            # Crashes to trigger
        window_seconds=300,           # 5-minute window
        cooldown_seconds=60.0         # Min delay between retries
    ),
    on_healing_attempt=lambda pid, attempt: 
        print(f"Restart attempt {attempt}"),
    on_healing_failed=lambda pid, reason: 
        print(f"Failed: {reason}")
)
"""


# ============================================================================
# TROUBLESHOOTING QUICK REFERENCE
# ============================================================================

"""
Problem: Task won't start
Solution: Check command exists
  subprocess.run(["which", "python3"])  # Linux/Mac
  where python  # Windows

Problem: Process crashes immediately
Solution: Check for syntax errors
  python script.py  # Run directly

Problem: Healing not working
Solution: Start monitoring
  await healer.start_monitoring()

Problem: High resource usage
Solution: Reduce concurrent tasks
  scheduler.max_concurrent_tasks = 2

Problem: Tasks not executing
Solution: Start scheduler
  await scheduler.start()

Need help?
  → Check process_examples.py for full examples
  → Read PROCESS_MANAGER_API_REFERENCE.md for details
  → Enable logging: logging.basicConfig(level=logging.DEBUG)
"""


# ============================================================================
# NEXT STEPS
# ============================================================================

"""
✓ You've learned the basics!

Next:
  1. Try the examples in process_examples.py
  2. Read PROCESS_MANAGER_API_REFERENCE.md for detailed API
  3. Integrate with HAL system (HardwareManager)
  4. Set up monitoring and metrics
  5. Deploy to production

Key Resources:
  • process_examples.py: 6 complete working examples
  • PROCESS_MANAGER_API_REFERENCE.md: Complete API docs
  • hardware/processes/: Full source code
  
Questions? Check the comments in the source code!
"""
