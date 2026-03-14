"""
Custom exceptions for Process & Task Management.

This module defines a comprehensive exception hierarchy for process management,
enabling precise error handling and recovery strategies.

Exception Hierarchy:
    ProcessException (base)
    ├── ProcessStartException
    ├── ProcessTimeoutException
    ├── ProcessResourceException
    ├── ProcessStateException
    ├── TaskSchedulerException
    └── TooManyRestartsException
"""

from typing import Optional, Any


class ProcessException(Exception):
    """Base exception for all process management errors."""

    def __init__(
        self,
        message: str,
        process_id: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize ProcessException.

        Args:
            message: Error message describing what went wrong
            process_id: ID of the process involved in the error
            context: Additional context information for debugging
        """
        super().__init__(message)
        self.message = message
        self.process_id = process_id
        self.context = context or {}

    def __str__(self) -> str:
        """Return formatted error message with context."""
        base = self.message
        if self.process_id:
            base = f"[Process: {self.process_id}] {base}"
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            base = f"{base} ({context_str})"
        return base


class ProcessStartException(ProcessException):
    """Raised when a process fails to start.

    Possible causes:
    - Command not found or invalid
    - Insufficient permissions
    - Resource constraints
    - System limitations
    """

    pass


class ProcessTimeoutException(ProcessException):
    """Raised when a process operation times out.

    Possible causes:
    - Process takes too long to start
    - Process hangs during execution
    - Startup timeout exceeded
    """

    pass


class ProcessResourceException(ProcessException):
    """Raised when process encounters resource constraints.

    Possible causes:
    - Insufficient memory
    - Too many open processes
    - Disk space exhausted
    - CPU limits exceeded
    """

    pass


class ProcessStateException(ProcessException):
    """Raised when invalid state transition is attempted.

    Possible causes:
    - Stopping an already stopped process
    - Starting an already running process
    - Restarting process in invalid state
    """

    pass


class TaskSchedulerException(ProcessException):
    """Raised when task scheduling fails.

    Possible causes:
    - Scheduler is full
    - Invalid task configuration
    - Task dependencies not met
    - Scheduler is shutting down
    """

    pass


class TooManyRestartsException(ProcessException):
    """Raised when process exceeds maximum restart attempts.

    This indicates that a process has crashed multiple times
    and the self-healing system has exhausted retry attempts.

    Possible causes:
    - Fundamental process issue
    - Environment misconfiguration
    - Resource constraints preventing stable operation
    """

    pass
