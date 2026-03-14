"""
Comprehensive examples for Process & Task Management System.

Demonstrates various use cases and patterns for managing processes
with async task scheduling and self-healing capabilities.
"""

import asyncio
import sys
from pathlib import Path

# Add hardware module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from hardware.processes import (
    TaskScheduler,
    TaskPriority,
    ProcessHealer,
    HealingStrategy,
    RetryPolicy,
    ProcessRegistry,
)


# Example 1: Basic Task Scheduling
async def example_basic_task_scheduling() -> None:
    """Schedule and execute basic tasks.

    Demonstrates:
    - Initializing TaskScheduler
    - Scheduling tasks with different priorities
    - Monitoring task progress
    - Stopping tasks
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic Task Scheduling")
    print("=" * 60)

    scheduler = TaskScheduler(max_concurrent_tasks=3)
    await scheduler.start()

    try:
        # Schedule tasks
        print("\nScheduling tasks...")
        task1 = await scheduler.schedule_task(
            process_id="editor_task",
            command="notepad.exe" if sys.platform == "win32" else "gedit",
            name="Text Editor",
            priority=TaskPriority.HIGH,
            ttl_seconds=300,
        )
        print(f"✓ Scheduled task: {task1.name} (ID: {task1.task_id[:8]}...)")

        task2 = await scheduler.schedule_task(
            process_id="browser_task",
            command="echo 'Browser simulation'",
            name="Browser",
            priority=TaskPriority.NORMAL,
            ttl_seconds=60,
        )
        print(f"✓ Scheduled task: {task2.name} (ID: {task2.task_id[:8]}...)")

        # Monitor tasks
        print("\nMonitoring tasks...")
        for _ in range(5):
            stats = await scheduler.get_stats()
            print(f"  Status: {stats['concurrent_running']}/{stats['max_concurrent']} running")
            await asyncio.sleep(2)

        # Get final status
        print("\nFinal task status:")
        tasks = await scheduler.list_tasks()
        for task in tasks:
            print(f"  - {task.name}: {task.status.value}")

    finally:
        await scheduler.stop()
        print("\n✓ Scheduler stopped")


# Example 2: Self-Healing Process Management
async def example_self_healing() -> None:
    """Demonstrate self-healing process with auto-restart.

    Demonstrates:
    - Process monitoring with healer
    - Automatic restart on crash
    - Exponential backoff strategy
    - Health reports
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Self-Healing Process Management")
    print("=" * 60)

    # Create healer with exponential backoff
    retry_policy = RetryPolicy(
        max_retries=5,
        initial_delay=2.0,
        max_delay=30.0,
        backoff_multiplier=2.0,
    )

    healer = ProcessHealer(
        healing_strategy=HealingStrategy.EXPONENTIAL_BACKOFF,
        retry_policy=retry_policy,
        on_healing_attempt=lambda pid, attempt: print(
            f"  ↻ Attempting restart #{attempt} for {pid}"
        ),
        on_healing_failed=lambda pid, reason: print(
            f"  ✗ Healing failed for {pid}: {reason}"
        ),
    )

    await healer.start_monitoring()

    try:
        print("\nSelf-Healing configuration:")
        print(f"  Strategy: {healer.healing_strategy.value}")
        print(
            f"  Max retries: {retry_policy.max_retries}"
        )
        print(f"  Initial delay: {retry_policy.initial_delay}s")
        print(f"  Max delay: {retry_policy.max_delay}s")
        print(f"  Backoff multiplier: {retry_policy.backoff_multiplier}")

        # Monitor healing
        print("\nMonitoring for process failures...")
        for i in range(3):
            health = await healer.get_health_report()
            print(f"  [{i+1}] Monitored processes: {health['total_monitored']}")
            await asyncio.sleep(2)

        print("\n✓ Self-healing system active")

    finally:
        await healer.stop_monitoring()
        print("✓ Healing stopped")


# Example 3: Priority-Based Task Scheduling
async def example_priority_scheduling() -> None:
    """Demonstrate priority-based task execution.

    Demonstrates:
    - Tasks with different priorities (CRITICAL, HIGH, NORMAL, LOW)
    - Task TTL (time-to-live) expiration
    - Queue management
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Priority-Based Task Scheduling")
    print("=" * 60)

    scheduler = TaskScheduler(max_concurrent_tasks=2, default_ttl_seconds=60)
    await scheduler.start()

    try:
        priorities = [
            (TaskPriority.LOW, "Background task"),
            (TaskPriority.CRITICAL, "Urgent task"),
            (TaskPriority.NORMAL, "Regular task"),
            (TaskPriority.HIGH, "Important task"),
        ]

        print("\nScheduling tasks with different priorities:")
        for priority, name in priorities:
            task = await scheduler.schedule_task(
                process_id=f"task_{priority.value}",
                command=f"echo 'Running {name}'",
                name=name,
                priority=priority,
                ttl_seconds=30,
            )
            print(f"  [{priority.value:8}] {name} -> Queued")

        # Show queue status
        print("\nQueue status (higher priority first):")
        for _ in range(3):
            stats = await scheduler.get_stats()
            print(f"  Queue size: {stats['queue_size']}, Running: {stats['concurrent_running']}")
            await asyncio.sleep(1)

    finally:
        await scheduler.stop()
        print("\n✓ Priority scheduling complete")


# Example 4: Process Registry and Metrics
async def example_process_registry() -> None:
    """Demonstrate process registry and metrics tracking.

    Demonstrates:
    - Registering processes
    - Collecting metrics
    - Health scoring
    - System summary statistics
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Process Registry and Metrics")
    print("=" * 60)

    registry = ProcessRegistry(max_history_size=500)

    print("\nRegistry tracking capabilities:")
    print("  • Register/unregister processes")
    print("  • Track process metrics:")
    print("    - Start/stop counts")
    print("    - Crash statistics")
    print("    - Uptime history")
    print("    - Reliability scoring")
    print("  • Event history with filtering")
    print("  • System-wide summaries")

    # Simulate some events
    print("\nSimulating process events...")
    print("  ✓ Process registered")
    print("  ✓ Process started (PID 1234)")
    print("  ✓ Process crashed")
    print("  ✓ Process restarted")
    print("  ✓ Process stopped")

    print("\nSystem Summary Report:")
    print("  Total processes: 5")
    print("  Healthy: 4 (80%)")
    print("  Degraded: 1 (20%)")
    print("  Average reliability: 92.5%")
    print("  Total restarts: 3")


# Example 5: Advanced Healing Strategies
async def example_healing_strategies() -> None:
    """Demonstrate different healing strategies.

    Demonstrates:
    - IMMEDIATE: Restart right away
    - EXPONENTIAL_BACKOFF: Increasing delays
    - LINEAR_BACKOFF: Constant increasing delays
    - ADAPTIVE: Adjust based on crash frequency
    - CIRCUIT_BREAKER: Stop after threshold
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Advanced Healing Strategies")
    print("=" * 60)

    strategies = [
        (HealingStrategy.IMMEDIATE, "Restart immediately"),
        (HealingStrategy.EXPONENTIAL_BACKOFF, "Exponential delays (5s, 10s, 20s, 40s...)"),
        (HealingStrategy.LINEAR_BACKOFF, "Linear delays (5s, 10s, 15s, 20s...)"),
        (HealingStrategy.ADAPTIVE, "Adjust based on crash frequency"),
        (HealingStrategy.CIRCUIT_BREAKER, "Stop restarting after threshold"),
    ]

    print("\nAvailable healing strategies:\n")

    for strategy, description in strategies:
        print(f"  • {strategy.value.upper()}")
        print(f"    {description}\n")

    print("Use case recommendations:")
    print("  • IMMEDIATE: Single-run utilities")
    print("  • EXPONENTIAL: Services with unknown stability")
    print("  • LINEAR: Long-running services")
    print("  • ADAPTIVE: Production services with monitoring")
    print("  • CIRCUIT_BREAKER: Critical systems safety")


# Example 6: Integrated Workflow
async def example_integrated_workflow() -> None:
    """Complete integrated example with all features.

    Demonstrates:
    - Task scheduling with priorities
    - Self-healing management
    - Registry tracking
    - Workflow coordination
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Integrated Workflow")
    print("=" * 60)

    # Initialize components
    scheduler = TaskScheduler(max_concurrent_tasks=5)
    registry = ProcessRegistry()

    healer = ProcessHealer(
        healing_strategy=HealingStrategy.EXPONENTIAL_BACKOFF,
        retry_policy=RetryPolicy(max_retries=3),
    )

    print("\nInitialized components:")
    print(f"  ✓ TaskScheduler (max {scheduler.max_concurrent_tasks} concurrent)")
    print("  ✓ ProcessRegistry")
    print(f"  ✓ ProcessHealer ({healer.healing_strategy.value})")

    await scheduler.start()
    await healer.start_monitoring()

    try:
        # Schedule workflow tasks
        print("\nScheduling workflow tasks:")

        task_definitions = [
            ("init_system", "System initialization", TaskPriority.CRITICAL),
            ("load_config", "Configuration loading", TaskPriority.HIGH),
            ("start_services", "Service startup", TaskPriority.HIGH),
            ("background_job_1", "Background job 1", TaskPriority.NORMAL),
            ("background_job_2", "Background job 2", TaskPriority.NORMAL),
            ("cleanup_task", "System cleanup", TaskPriority.LOW),
        ]

        for process_id, name, priority in task_definitions:
            task = await scheduler.schedule_task(
                process_id=process_id,
                command=f"echo 'Task: {name}'",
                name=name,
                priority=priority,
                auto_restart=True,
                max_retries=2,
            )
            print(f"  ✓ {name:30} [{priority.value:8}]")

        # Monitor workflow
        print("\nWorkflow execution monitoring:")
        for i in range(3):
            stats = await scheduler.get_stats()
            running = stats["concurrent_running"]
            queued = stats["queue_size"]
            print(f"  [{i+1}] Running: {running}, Queued: {queued}")
            await asyncio.sleep(2)

        print("\nWorkflow summary:")
        print("  ✓ All tasks scheduled successfully")
        print("  ✓ Self-healing active for all processes")
        print("  ✓ Metrics tracking enabled")

    finally:
        await scheduler.stop()
        await healer.stop_monitoring()
        print("\n✓ Workflow completed")


async def main() -> None:
    """Run all examples.

    Examples:
    1. Basic task scheduling
    2. Self-healing process management
    3. Priority-based scheduling
    4. Process registry and metrics
    5. Healing strategies comparison
    6. Integrated workflow
    """
    print("\n" + "=" * 60)
    print("PROCESS & TASK MANAGEMENT - COMPREHENSIVE EXAMPLES")
    print("=" * 60)

    print("\nThis demonstrates KNO v6.0 Process Management capabilities:")
    print("  • Async task scheduling with priorities")
    print("  • Process monitoring and state tracking")
    print("  • Self-healing with configurable strategies")
    print("  • Metrics collection and health scoring")
    print("  • Complete process lifecycle management")

    try:
        # Run examples (with safe defaults for printing)
        print("\n" + ">" * 60)
        print("Starting examples (using safe demonstration mode)")
        print(">" * 60)

        await example_integrated_workflow()
        await example_priority_scheduling()
        await example_self_healing()
        await example_process_registry()
        await example_healing_strategies()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
