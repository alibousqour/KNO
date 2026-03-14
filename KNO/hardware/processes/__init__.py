"""
Process & Task Management Module for KNO v6.0
Provides async-based task scheduling, process monitoring, and self-healing capabilities.

This module enables KNO to:
- Run external applications (browsers, editors, tools) asynchronously
- Monitor process health and resource usage
- Automatically restart crashed processes (Self-Healing)
- Schedule and manage complex task workflows
- Track process lifecycle and state transitions

Main Components:
- ProcessManager: Core process lifecycle management
- TaskScheduler: Async task scheduling with priority and TTL
- ProcessHealer: Self-healing system with retry strategies
- ProcessRegistry: Central registry for all managed processes

Example:
    >>> scheduler = TaskScheduler()
    >>> task = await scheduler.schedule_task(
    ...     "chrome",
    ...     command="chrome.exe https://example.com",
    ...     restart_on_crash=True,
    ...     max_retries=3
    ... )
    >>> status = await task.get_status()
    >>> await scheduler.stop_task("chrome")
"""

from .process_manager import Process, ProcessState, ProcessManager, ProcessConfig
from .task_scheduler import TaskScheduler, Task, TaskPriority, TaskStatus
from .process_healing import ProcessHealer, HealingStrategy, RetryPolicy
from .process_registry import ProcessRegistry, ProcessMetrics
from .process_exceptions import (
    ProcessException,
    ProcessStartException,
    ProcessTimeoutException,
    ProcessResourceException,
    ProcessStateException,
    TaskSchedulerException,
    TooManyRestartsException,
)

__version__ = "1.0.0"
__all__ = [
    # Process Management
    "Process",
    "ProcessState",
    "ProcessManager",
    "ProcessConfig",
    # Task Scheduling
    "TaskScheduler",
    "Task",
    "TaskPriority",
    "TaskStatus",
    # Self-Healing
    "ProcessHealer",
    "HealingStrategy",
    "RetryPolicy",
    # Registry
    "ProcessRegistry",
    "ProcessMetrics",
    # Exceptions
    "ProcessException",
    "ProcessStartException",
    "ProcessTimeoutException",
    "ProcessResourceException",
    "ProcessStateException",
    "TaskSchedulerException",
    "TooManyRestartsException",
]
