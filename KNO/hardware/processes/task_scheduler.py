"""
Async Task Scheduling System.

Provides TaskScheduler for managing async task execution with:
- Priority-based scheduling
- Task TTL and expiration
- Concurrent execution with limits
- Status tracking and monitoring
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, Any, List, Coroutine
from datetime import datetime, timedelta

from .process_manager import ProcessManager, ProcessConfig
from .process_exceptions import TaskSchedulerException

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task execution priority levels."""

    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    DEFERRED = 4


class TaskStatus(Enum):
    """Task execution status."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAUSED = "paused"


@dataclass
class Task:
    """Represents a manageable task in the scheduler.

    Attributes:
        task_id: Unique task identifier
        process_id: Associated process identifier
        name: Human-readable task name
        status: Current execution status
        priority: Task priority level
        created_at: Task creation timestamp
        started_at: Execution start time
        completed_at: Execution completion time
        ttl_seconds: Time-to-live in seconds
        max_retries: Maximum retry attempts
        current_retry: Current retry count
        error: Error message if failed
        result: Task result data
        metadata: Custom metadata
    """

    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    process_id: str = ""
    name: str = ""
    status: TaskStatus = TaskStatus.QUEUED
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    ttl_seconds: Optional[int] = None
    max_retries: int = 3
    current_retry: int = 0
    error: Optional[str] = None
    result: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

    async def get_status(self) -> str:
        """Get task status.

        Returns:
            Status value string
        """
        return self.status.value

    async def get_age_seconds(self) -> float:
        """Get task age in seconds.

        Returns:
            Age since creation
        """
        return (datetime.now() - self.created_at).total_seconds()

    async def is_expired(self) -> bool:
        """Check if task has expired.

        Returns:
            True if TTL exceeded
        """
        if self.ttl_seconds is None:
            return False

        age = await self.get_age_seconds()
        return age > self.ttl_seconds

    async def get_runtime_seconds(self) -> float:
        """Get execution runtime.

        Returns:
            Runtime in seconds
        """
        if self.started_at is None:
            return 0.0

        end = self.completed_at or datetime.now()
        return (end - self.started_at).total_seconds()


class TaskScheduler:
    """Async task scheduler with priority and resource management.

    Features:
    - Priority-based task execution
    - Concurrent execution limits
    - Task TTL and expiration
    - Automatic retry on failure
    - Comprehensive monitoring
    """

    def __init__(
        self,
        max_concurrent_tasks: int = 10,
        default_ttl_seconds: Optional[int] = None,
    ) -> None:
        """Initialize TaskScheduler.

        Args:
            max_concurrent_tasks: Maximum concurrent task execution
            default_ttl_seconds: Default task TTL
        """
        self.max_concurrent_tasks = max_concurrent_tasks
        self.default_ttl_seconds = default_ttl_seconds

        self._tasks: dict[str, Task] = {}
        self._queue: asyncio.PriorityQueue[tuple[int, Task]] = asyncio.PriorityQueue()
        self._running_tasks: set[asyncio.Task[Any]] = set()
        self._process_manager = ProcessManager()
        self._is_running = False
        self._worker_task: Optional[asyncio.Task[None]] = None
        self._expiration_task: Optional[asyncio.Task[None]] = None

    async def start(self) -> None:
        """Start the scheduler worker threads."""
        if self._is_running:
            return

        self._is_running = True
        self._worker_task = asyncio.create_task(self._run_worker())
        self._expiration_task = asyncio.create_task(self._check_expirations())

        logger.info("TaskScheduler started")

    async def stop(self, wait_pending: bool = True) -> None:
        """Stop the scheduler.

        Args:
            wait_pending: Wait for pending tasks to complete
        """
        self._is_running = False

        if wait_pending:
            # Wait for all running tasks
            if self._running_tasks:
                await asyncio.wait(self._running_tasks, timeout=30.0)

        # Cancel worker tasks
        if self._worker_task:
            self._worker_task.cancel()
        if self._expiration_task:
            self._expiration_task.cancel()

        logger.info("TaskScheduler stopped")

    async def schedule_task(
        self,
        process_id: str,
        command: str,
        name: Optional[str] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        ttl_seconds: Optional[int] = None,
        auto_restart: bool = False,
        max_retries: int = 3,
        **process_config_kwargs: Any,
    ) -> Task:
        """Schedule a new task.

        Args:
            process_id: Unique process identifier
            command: Command to execute
            name: Task display name
            priority: Task priority level
            ttl_seconds: Task time-to-live
            auto_restart: Restart on crash
            max_retries: Maximum retry attempts
            **process_config_kwargs: ProcessConfig parameters

        Returns:
            Scheduled Task object

        Raises:
            TaskSchedulerException: If scheduling fails
        """
        if not self._is_running:
            raise TaskSchedulerException(
                "Scheduler is not running",
                process_id=process_id,
            )

        if process_id in self._tasks:
            raise TaskSchedulerException(
                f"Task with process_id {process_id} already scheduled",
                process_id=process_id,
            )

        # Create process
        process = self._process_manager.create_process(
            process_id,
            command,
            restart_on_crash=auto_restart,
            max_retries=max_retries,
            **process_config_kwargs,
        )

        # Create task
        task = Task(
            process_id=process_id,
            name=name or process_id,
            priority=priority,
            ttl_seconds=ttl_seconds or self.default_ttl_seconds,
            max_retries=max_retries,
        )

        with self._get_lock():
            self._tasks[task.task_id] = task
            await self._queue.put((priority.value, task))

        logger.info(f"Task {task.task_id} scheduled for {process_id}")
        return task

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task object or None
        """
        with self._get_lock():
            return self._tasks.get(task_id)

    async def list_tasks(
        self, status: Optional[TaskStatus] = None
    ) -> List[Task]:
        """List all tasks, optionally filtered by status.

        Args:
            status: Filter by status

        Returns:
            List of Task objects
        """
        with self._get_lock():
            tasks = list(self._tasks.values())

        if status:
            tasks = [t for t in tasks if t.status == status]

        return tasks

    async def stop_task(self, task_id: str) -> bool:
        """Stop a running task.

        Args:
            task_id: Task identifier

        Returns:
            True if stopped successfully
        """
        task = await self.get_task(task_id)
        if not task:
            return False

        process = self._process_manager.get_process(task.process_id)
        if not process:
            return False

        success = await process.stop()
        if success:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()

        return success

    async def pause_task(self, task_id: str) -> bool:
        """Pause a running task.

        Args:
            task_id: Task identifier

        Returns:
            True if paused successfully
        """
        task = await self.get_task(task_id)
        if not task:
            return False

        process = self._process_manager.get_process(task.process_id)
        if not process:
            return False

        success = await process.pause()
        if success:
            task.status = TaskStatus.PAUSED

        return success

    async def resume_task(self, task_id: str) -> bool:
        """Resume a paused task.

        Args:
            task_id: Task identifier

        Returns:
            True if resumed successfully
        """
        task = await self.get_task(task_id)
        if not task:
            return False

        process = self._process_manager.get_process(task.process_id)
        if not process:
            return False

        success = await process.resume()
        if success:
            task.status = TaskStatus.RUNNING

        return success

    async def get_stats(self) -> dict[str, Any]:
        """Get scheduler statistics.

        Returns:
            Dictionary with scheduler metrics
        """
        with self._get_lock():
            tasks = list(self._tasks.values())

        total = len(tasks)
        by_status = {}

        for status in TaskStatus:
            count = sum(1 for t in tasks if t.status == status)
            if count > 0:
                by_status[status.value] = count

        return {
            "total_tasks": total,
            "concurrent_running": len(self._running_tasks),
            "max_concurrent": self.max_concurrent_tasks,
            "queue_size": self._queue.qsize(),
            "by_status": by_status,
        }

    async def _run_worker(self) -> None:
        """Worker coroutine for task processing."""
        while self._is_running:
            try:
                # Wait for queue item or timeout
                if self._queue.empty():
                    await asyncio.sleep(0.5)
                    continue

                try:
                    _, task = self._queue.get_nowait()
                except asyncio.QueueEmpty:
                    await asyncio.sleep(0.5)
                    continue

                # Check if we can run more tasks
                while len(self._running_tasks) >= self.max_concurrent_tasks:
                    await asyncio.sleep(0.1)

                # Check expiration
                if await task.is_expired():
                    task.status = TaskStatus.EXPIRED
                    task.completed_at = datetime.now()
                    logger.warning(f"Task {task.task_id} expired")
                    continue

                # Start task execution
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()

                process = self._process_manager.get_process(task.process_id)
                if not process:
                    task.status = TaskStatus.FAILED
                    task.error = "Process not found"
                    task.completed_at = datetime.now()
                    continue

                # Execute process
                worker = asyncio.create_task(self._execute_task(task, process))
                self._running_tasks.add(worker)
                worker.add_done_callback(self._running_tasks.discard)

            except Exception as e:
                logger.error(f"Error in scheduler worker: {e}")
                await asyncio.sleep(1.0)

    async def _execute_task(self, task: Task, process: Any) -> None:
        """Execute a task with retry logic.

        Args:
            task: Task to execute
            process: Associated process
        """
        try:
            # Attempt to start process with retries
            for attempt in range(task.max_retries):
                try:
                    success = await process.start()
                    if success:
                        # Wait for process to complete
                        while await process.is_running():
                            await asyncio.sleep(task.metadata.get("monitor_interval", 1.0))

                        task.status = TaskStatus.COMPLETED
                        task.completed_at = datetime.now()
                        logger.info(f"Task {task.task_id} completed successfully")
                        return

                except Exception as start_error:
                    task.current_retry = attempt + 1
                    if attempt < task.max_retries - 1:
                        await asyncio.sleep(
                            task.metadata.get("retry_delay", 5.0) * (2 ** attempt)
                        )
                        continue
                    else:
                        raise start_error

            # All retries exhausted
            task.status = TaskStatus.FAILED
            task.error = "Max retries exceeded"
            task.completed_at = datetime.now()

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            logger.error(f"Task {task.task_id} failed: {e}")

    async def _check_expirations(self) -> None:
        """Check and mark expired tasks."""
        while self._is_running:
            try:
                tasks = await self.list_tasks()
                for task in tasks:
                    if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                        continue

                    if await task.is_expired():
                        task.status = TaskStatus.EXPIRED
                        task.completed_at = datetime.now()

                await asyncio.sleep(5.0)

            except Exception as e:
                logger.error(f"Error checking expirations: {e}")
                await asyncio.sleep(5.0)

    def _get_lock(self) -> asyncio.Lock:
        """Get or create async lock for task access.

        Returns:
            AsyncIO lock
        """
        if not hasattr(self, "_task_lock"):
            self._task_lock = asyncio.Lock()
        return self._task_lock
