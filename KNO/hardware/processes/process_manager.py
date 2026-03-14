"""
Core Process Management Classes.

Provides Process and ProcessManager for managing individual process lifecycles,
with comprehensive state tracking and resource monitoring.
"""

import asyncio
import subprocess
import threading
import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, Any, List
from datetime import datetime, timedelta
from pathlib import Path

from .process_exceptions import (
    ProcessStartException,
    ProcessTimeoutException,
    ProcessStateException,
)

logger = logging.getLogger(__name__)


class ProcessState(Enum):
    """Process lifecycle states.

    States represent the process journey:
    - CREATED: Process object created but not started
    - STARTING: Start command issued, waiting for subprocess
    - RUNNING: Subprocess established and active
    - PAUSED: Process suspended but not terminated
    - STOPPING: Stop signal sent, waiting for graceful shutdown
    - STOPPED: Process terminated normally
    - CRASHED: Process terminated unexpectedly
    - ZOMBIE: Process terminated but parent not notified
    """

    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    CRASHED = "crashed"
    ZOMBIE = "zombie"


@dataclass
class ProcessConfig:
    """Configuration for process startup and monitoring.

    Attributes:
        command: Shell command to execute (can include args)
        cwd: Working directory for process
        env: Environment variables dictionary
        shell: Use shell interpreter
        timeout: Startup timeout in seconds
        monitoring_interval: Check interval in seconds
        auto_restart: Automatically restart on crash
        restart_on_crash: Alias for auto_restart
        max_retries: Max restart attempts (-1 = unlimited)
        restart_delay: Delay before restart in seconds
        resource_limits: Resource limit constraints
        capture_output: Capture stdout/stderr
        create_new_group: Create new process group (for signal handling)
    """

    command: str
    cwd: Optional[Path] = None
    env: Optional[dict[str, str]] = None
    shell: bool = False
    timeout: float = 10.0
    monitoring_interval: float = 1.0
    auto_restart: bool = False
    restart_on_crash: bool = False
    max_retries: int = 3
    restart_delay: float = 5.0
    resource_limits: Optional[dict[str, int]] = None
    capture_output: bool = True
    create_new_group: bool = True


class Process:
    """Manages a single process lifecycle with async monitoring.

    Features:
    - Asynchronous start/stop operations
    - State machine with validation
    - Resource monitoring integration
    - Event callbacks for state changes
    - Comprehensive error handling
    """

    def __init__(
        self,
        process_id: str,
        config: ProcessConfig,
        on_state_change: Optional[Callable[[str, "Process"], None]] = None,
    ) -> None:
        """Initialize Process management wrapper.

        Args:
            process_id: Unique process identifier
            config: ProcessConfig with startup parameters
            on_state_change: Callback for state transitions
        """
        self.process_id = process_id
        self.config = config
        self._state = ProcessState.CREATED
        self._process: Optional[subprocess.Popen[Any]] = None
        self._monitor_thread: Optional[threading.Thread] = None
        self._should_monitor = False
        self._state_lock = threading.Lock()
        self._on_state_change = on_state_change

        # Tracking metrics
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.restart_count = 0
        self.crash_count = 0
        self.last_crash_time: Optional[datetime] = None
        self.uptime_seconds = 0.0

    @property
    def state(self) -> ProcessState:
        """Get current process state."""
        with self._state_lock:
            return self._state

    async def start(self) -> bool:
        """Start the process asynchronously.

        Returns:
            True if process started successfully

        Raises:
            ProcessStartException: If start fails
            ProcessStateException: If process already running
        """
        if self.state in (ProcessState.RUNNING, ProcessState.STARTING):
            raise ProcessStateException(
                f"Cannot start process already in {self.state.value} state",
                process_id=self.process_id,
            )

        self._set_state(ProcessState.STARTING)

        try:
            # Prepare subprocess kwargs
            kwargs = {
                "shell": self.config.shell,
                "cwd": self.config.cwd,
            }

            if self.config.env:
                kwargs["env"] = self.config.env

            if self.config.capture_output:
                kwargs["stdout"] = subprocess.PIPE
                kwargs["stderr"] = subprocess.PIPE

            # Create process
            self._process = subprocess.Popen(self.config.command, **kwargs)

            if self._process.pid is None:
                raise ProcessStartException(
                    "Failed to start process - no PID obtained",
                    process_id=self.process_id,
                )

            self.start_time = datetime.now()
            self._set_state(ProcessState.RUNNING)

            # Start monitoring in background
            self._should_monitor = True
            self._monitor_thread = threading.Thread(
                target=self._monitor_process, daemon=True
            )
            self._monitor_thread.start()

            logger.info(
                f"Process {self.process_id} started with PID {self._process.pid}"
            )
            return True

        except Exception as e:
            self._set_state(ProcessState.STOPPED)
            raise ProcessStartException(
                f"Failed to start process: {str(e)}",
                process_id=self.process_id,
                context={"command": self.config.command},
            )

    async def stop(self, timeout: float = 10.0) -> bool:
        """Stop the process gracefully.

        Args:
            timeout: Grace period in seconds before force kill

        Returns:
            True if process stopped successfully
        """
        if self.state == ProcessState.STOPPED:
            return True

        if self._process is None:
            return False

        self._set_state(ProcessState.STOPPING)

        try:
            # Try graceful termination first
            self._process.terminate()

            # Wait for graceful shutdown
            try:
                self._process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                logger.warning(
                    f"Process {self.process_id} did not terminate gracefully, force killing"
                )
                self._process.kill()
                self._process.wait()

            self._should_monitor = False
            self.end_time = datetime.now()
            self._set_state(ProcessState.STOPPED)

            logger.info(f"Process {self.process_id} stopped successfully")
            return True

        except Exception as e:
            logger.error(f"Error stopping process {self.process_id}: {e}")
            return False

    async def is_running(self) -> bool:
        """Check if process is currently running.

        Returns:
            True if process is active
        """
        if self._process is None:
            return False

        poll_result = self._process.poll()
        return poll_result is None

    async def get_pid(self) -> Optional[int]:
        """Get the process ID.

        Returns:
            PID if running, None otherwise
        """
        return self._process.pid if self._process else None

    async def pause(self) -> bool:
        """Pause the process (suspend).

        Returns:
            True if paused successfully
        """
        if self.state != ProcessState.RUNNING or self._process is None:
            return False

        try:
            import signal

            if hasattr(signal, "SIGSTOP"):
                self._process.send_signal(signal.SIGSTOP)
                self._set_state(ProcessState.PAUSED)
                return True
            return False
        except Exception as e:
            logger.error(f"Error pausing process {self.process_id}: {e}")
            return False

    async def resume(self) -> bool:
        """Resume a paused process.

        Returns:
            True if resumed successfully
        """
        if self.state != ProcessState.PAUSED or self._process is None:
            return False

        try:
            import signal

            if hasattr(signal, "SIGCONT"):
                self._process.send_signal(signal.SIGCONT)
                self._set_state(ProcessState.RUNNING)
                return True
            return False
        except Exception as e:
            logger.error(f"Error resuming process {self.process_id}: {e}")
            return False

    def _monitor_process(self) -> None:
        """Monitor process in background thread.

        Detects crashes and updates state accordingly.
        """
        while self._should_monitor:
            try:
                if self._process is None:
                    break

                poll_result = self._process.poll()

                if poll_result is not None and self.state == ProcessState.RUNNING:
                    # Process has exited
                    self._set_state(ProcessState.CRASHED)
                    self.crash_count += 1
                    self.last_crash_time = datetime.now()
                    self.end_time = datetime.now()

                    logger.warning(
                        f"Process {self.process_id} crashed with exit code {poll_result}"
                    )

                time.sleep(self.config.monitoring_interval)

            except Exception as e:
                logger.error(f"Error in process monitor for {self.process_id}: {e}")
                break

    def _set_state(self, new_state: ProcessState) -> None:
        """Set process state with callback notification.

        Args:
            new_state: New ProcessState value
        """
        with self._state_lock:
            old_state = self._state
            self._state = new_state

            if self._on_state_change and old_state != new_state:
                try:
                    self._on_state_change(new_state.value, self)
                except Exception as e:
                    logger.error(f"Error in state change callback: {e}")

    def get_info(self) -> dict[str, Any]:
        """Get comprehensive process information.

        Returns:
            Dictionary with process details
        """
        pid = self._process.pid if self._process else None
        uptime = 0.0

        if self.start_time:
            if self.end_time:
                uptime = (self.end_time - self.start_time).total_seconds()
            else:
                uptime = (datetime.now() - self.start_time).total_seconds()

        return {
            "process_id": self.process_id,
            "pid": pid,
            "state": self.state.value,
            "command": self.config.command,
            "running": self._process is not None and self._process.poll() is None,
            "uptime_seconds": uptime,
            "restart_count": self.restart_count,
            "crash_count": self.crash_count,
            "last_crash_time": self.last_crash_time.isoformat()
            if self.last_crash_time
            else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


class ProcessManager:
    """Manages multiple processes with unified interface.

    Coordinates process lifecycle across application.
    """

    def __init__(self) -> None:
        """Initialize ProcessManager."""
        self._processes: dict[str, Process] = {}
        self._processes_lock = threading.Lock()

    def create_process(
        self,
        process_id: str,
        command: str,
        **config_kwargs: Any,
    ) -> Process:
        """Create a new managed process.

        Args:
            process_id: Unique identifier
            command: Command to execute
            **config_kwargs: ProcessConfig parameters

        Returns:
            Configured Process object
        """
        if process_id in self._processes:
            raise ProcessStateException(
                f"Process {process_id} already exists",
                process_id=process_id,
            )

        config = ProcessConfig(command=command, **config_kwargs)
        process = Process(
            process_id,
            config,
            on_state_change=self._on_process_state_change,
        )

        with self._processes_lock:
            self._processes[process_id] = process

        return process

    def get_process(self, process_id: str) -> Optional[Process]:
        """Get process by ID.

        Args:
            process_id: Process identifier

        Returns:
            Process object or None
        """
        with self._processes_lock:
            return self._processes.get(process_id)

    def list_processes(self) -> List[Process]:
        """Get all managed processes.

        Returns:
            List of Process objects
        """
        with self._processes_lock:
            return list(self._processes.values())

    def _on_process_state_change(self, new_state: str, process: Process) -> None:
        """Handle process state change.

        Args:
            new_state: New state value
            process: Process object
        """
        logger.debug(f"Process {process.process_id} state changed to {new_state}")
