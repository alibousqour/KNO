"""
Self-Healing System for Process Management.

Provides automatic process recovery with configurable healing strategies
and retry policies. Detects crashes and attempts intelligent recovery.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable, Any, List
from datetime import datetime, timedelta

from .process_manager import Process, ProcessState
from .process_exceptions import TooManyRestartsException, ProcessException

logger = logging.getLogger(__name__)


class HealingStrategy(Enum):
    """Strategies for healing crashed processes.

    - IMMEDIATE: Restart immediately
    - EXPONENTIAL_BACKOFF: Exponential delay between restarts
    - LINEAR_BACKOFF: Linear delay increase
    - ADAPTIVE: Adjust strategy based on crash frequency
    - CIRCUIT_BREAKER: Stop restarting after threshold
    """

    IMMEDIATE = "immediate"
    EXPONENTIAL_BACKOFF = "exponential"
    LINEAR_BACKOFF = "linear"
    ADAPTIVE = "adaptive"
    CIRCUIT_BREAKER = "circuit_breaker"


@dataclass
class RetryPolicy:
    """Configures retry behavior.

    Attributes:
        max_retries: Maximum restart attempts (-1 = infinite)
        initial_delay: Initial delay before first retry (seconds)
        max_delay: Maximum delay between retries (seconds)
        backoff_multiplier: Delay multiplier for exponential backoff
        crash_threshold: Crashes in window to trigger strategy change
        window_seconds: Time window for crash threshold
        cooldown_seconds: Cooldown before trying again after failures
    """

    max_retries: int = 5
    initial_delay: float = 5.0
    max_delay: float = 300.0
    backoff_multiplier: float = 2.0
    crash_threshold: int = 3
    window_seconds: int = 300
    cooldown_seconds: float = 60.0


class ProcessHealer:
    """Monitors and heals crashed processes.

    Tracks process health and automatically restarts crashed processes
    using configurable healing strategies and retry policies.
    """

    def __init__(
        self,
        healing_strategy: HealingStrategy = HealingStrategy.EXPONENTIAL_BACKOFF,
        retry_policy: Optional[RetryPolicy] = None,
        on_healing_attempt: Optional[Callable[[str, int], None]] = None,
        on_healing_failed: Optional[Callable[[str, str], None]] = None,
    ) -> None:
        """Initialize ProcessHealer.

        Args:
            healing_strategy: Strategy for process recovery
            retry_policy: Retry configuration
            on_healing_attempt: Callback on restart attempt
            on_healing_failed: Callback on failed healing
        """
        self.healing_strategy = healing_strategy
        self.retry_policy = retry_policy or RetryPolicy()
        self._on_healing_attempt = on_healing_attempt
        self._on_healing_failed = on_healing_failed

        self._monitored_processes: dict[str, _ProcessHealingState] = {}
        self._monitoring_task: Optional[asyncio.Task[None]] = None
        self._is_monitoring = False

    async def start_monitoring(self) -> None:
        """Start monitoring processes for crashes."""
        if self._is_monitoring:
            return

        self._is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitor_loop())
        logger.info("ProcessHealer monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop monitoring processes."""
        self._is_monitoring = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
        logger.info("ProcessHealer monitoring stopped")

    def add_process(
        self,
        process: Process,
        healing_strategy: Optional[HealingStrategy] = None,
        retry_policy: Optional[RetryPolicy] = None,
    ) -> None:
        """Add process to healing monitor.

        Args:
            process: Process to monitor
            healing_strategy: Override default strategy
            retry_policy: Override default retry policy
        """
        state = _ProcessHealingState(
            process=process,
            strategy=healing_strategy or self.healing_strategy,
            policy=retry_policy or self.retry_policy,
        )

        self._monitored_processes[process.process_id] = state
        logger.info(f"Process {process.process_id} added to healing monitor")

    def remove_process(self, process_id: str) -> None:
        """Remove process from healing monitor.

        Args:
            process_id: Process identifier
        """
        if process_id in self._monitored_processes:
            del self._monitored_processes[process_id]
            logger.info(f"Process {process_id} removed from healing monitor")

    async def get_health_report(self) -> dict[str, Any]:
        """Get comprehensive health report for all processes.

        Returns:
            Dictionary with health information
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_monitored": len(self._monitored_processes),
            "processes": {},
        }

        for process_id, state in self._monitored_processes.items():
            process = state.process

            report["processes"][process_id] = {
                "state": process.state.value,
                "restart_attempts": state.restart_count,
                "last_restart": state.last_restart_time.isoformat()
                if state.last_restart_time
                else None,
                "recent_crashes": state.get_recent_crash_count(),
                "is_in_cooldown": state.is_in_cooldown(),
                "circuit_breaker_open": state.circuit_breaker_open,
                "strategy": state.strategy.value,
            }

        return report

    async def _monitor_loop(self) -> None:
        """Main monitoring loop checking for crashed processes."""
        while self._is_monitoring:
            try:
                now = datetime.now()

                for process_id, state in list(self._monitored_processes.items()):
                    process = state.process

                    # Check if process has crashed
                    if process.state == ProcessState.CRASHED:
                        await self._handle_crash(process, state, now)

                await asyncio.sleep(2.0)

            except Exception as e:
                logger.error(f"Error in healing monitor loop: {e}")
                await asyncio.sleep(5.0)

    async def _handle_crash(
        self,
        process: Process,
        state: "_ProcessHealingState",
        crash_time: datetime,
    ) -> None:
        """Handle process crash with healing strategy.

        Args:
            process: Crashed process
            state: Process healing state
            crash_time: Time of crash
        """
        state.add_crash(crash_time)
        state.restart_count += 1

        # Log crash
        logger.warning(
            f"Process {process.process_id} crashed (crash #{state.restart_count})"
        )

        # Check circuit breaker
        if state.circuit_breaker_open:
            self._invoke_callback(
                self._on_healing_failed,
                process.process_id,
                "Circuit breaker is open",
            )
            logger.error(
                f"Circuit breaker open for {process.process_id}, no healing attempted"
            )
            return

        # Check max retries
        if (
            state.policy.max_retries != -1
            and state.restart_count > state.policy.max_retries
        ):
            state.circuit_breaker_open = True
            self._invoke_callback(
                self._on_healing_failed,
                process.process_id,
                "Max retries exceeded",
            )
            logger.error(
                f"Max retries exceeded for {process.process_id}, opening circuit breaker"
            )
            return

        # Check cooldown
        if state.is_in_cooldown():
            logger.debug(
                f"Process {process.process_id} is in cooldown, waiting before restart"
            )
            return

        # Calculate delay before restart
        delay = self._calculate_restart_delay(state)

        logger.info(
            f"Scheduling restart of {process.process_id} in {delay:.1f} seconds"
        )

        # Schedule restart
        await asyncio.sleep(delay)

        try:
            state.last_restart_time = datetime.now()
            self._invoke_callback(self._on_healing_attempt, process.process_id, state.restart_count)

            success = await process.start()
            if success:
                logger.info(f"Process {process.process_id} restarted successfully")
                # Reset restart count on success
                state.restart_count = 0
            else:
                logger.error(f"Failed to restart process {process.process_id}")

        except Exception as e:
            logger.error(f"Error restarting process {process.process_id}: {e}")

    def _calculate_restart_delay(self, state: "_ProcessHealingState") -> float:
        """Calculate delay before next restart attempt.

        Args:
            state: Process healing state

        Returns:
            Delay in seconds
        """
        strategy = state.strategy
        policy = state.policy

        if strategy == HealingStrategy.IMMEDIATE:
            return 0.0

        elif strategy == HealingStrategy.EXPONENTIAL_BACKOFF:
            delay = policy.initial_delay * (policy.backoff_multiplier ** (state.restart_count - 1))
            return min(delay, policy.max_delay)

        elif strategy == HealingStrategy.LINEAR_BACKOFF:
            delay = policy.initial_delay + (policy.initial_delay * (state.restart_count - 1))
            return min(delay, policy.max_delay)

        elif strategy == HealingStrategy.ADAPTIVE:
            recent_crashes = state.get_recent_crash_count()
            if recent_crashes >= policy.crash_threshold:
                # Many crashes, use conservative backoff
                delay = policy.initial_delay * (policy.backoff_multiplier ** state.restart_count)
            else:
                delay = policy.initial_delay
            return min(delay, policy.max_delay)

        elif strategy == HealingStrategy.CIRCUIT_BREAKER:
            crash_rate = state.get_crash_rate()
            if crash_rate > 0.5:  # More than 50% crashes
                state.circuit_breaker_open = True
                return 0.0
            return policy.initial_delay

        return policy.initial_delay

    def _invoke_callback(
        self,
        callback: Optional[Callable[..., Any]],
        process_id: str,
        *args: Any,
    ) -> None:
        """Safely invoke callback.

        Args:
            callback: Callback function
            process_id: Process identifier
            *args: Additional arguments
        """
        if callback:
            try:
                callback(process_id, *args)
            except Exception as e:
                logger.error(f"Error in healing callback: {e}")


class _ProcessHealingState:
    """Internal state tracking for per-process healing.

    Tracks restart attempts, crash history, and state-specific metrics.
    """

    def __init__(
        self,
        process: Process,
        strategy: HealingStrategy,
        policy: RetryPolicy,
    ) -> None:
        """Initialize healing state.

        Args:
            process: Process being monitored
            strategy: Healing strategy
            policy: Retry policy
        """
        self.process = process
        self.strategy = strategy
        self.policy = policy

        self.restart_count = 0
        self.last_restart_time: Optional[datetime] = None
        self.circuit_breaker_open = False
        self._crash_history: List[datetime] = []
        self._cooldown_until: Optional[datetime] = None

    def add_crash(self, crash_time: datetime) -> None:
        """Record a crash occurrence.

        Args:
            crash_time: Time of crash
        """
        self._crash_history.append(crash_time)
        self._cooldown_until = crash_time + timedelta(
            seconds=self.policy.cooldown_seconds
        )

    def get_recent_crash_count(self) -> int:
        """Get crash count in current window.

        Returns:
            Number of crashes in window
        """
        now = datetime.now()
        window_start = now - timedelta(seconds=self.policy.window_seconds)

        return sum(1 for crash_time in self._crash_history if crash_time > window_start)

    def get_crash_rate(self) -> float:
        """Get crash rate.

        Returns:
            Fraction of recent operations that crashed
        """
        if not self._crash_history:
            return 0.0

        recent = self.get_recent_crash_count()
        if recent == 0:
            return 0.0

        return recent / max(self.restart_count, 1)

    def is_in_cooldown(self) -> bool:
        """Check if process is in cooldown period.

        Returns:
            True if still in cooldown
        """
        if self._cooldown_until is None:
            return False

        return datetime.now() < self._cooldown_until
