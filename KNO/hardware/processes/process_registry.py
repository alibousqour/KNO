"""
Process Registry and Metrics Tracking.

Provides centralized registry for all managed processes with
comprehensive metrics collection and historical tracking.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, List, Any, Callable
from datetime import datetime, timedelta
from collections import defaultdict

from .process_manager import Process, ProcessState

logger = logging.getLogger(__name__)


@dataclass
class ProcessMetrics:
    """Metrics for a single process.

    Attributes:
        process_id: Process identifier
        total_starts: Number of times started
        total_crashes: Number of crashes
        total_restarts: Number of auto-restarts
        average_uptime: Average runtime in seconds
        peak_memory: Peak memory usage
        peak_cpu: Peak CPU usage
        first_seen: First start time
        last_seen: Last recorded time
        success_count: Successful completions
        failure_count: Failed executions
    """

    process_id: str
    total_starts: int = 0
    total_crashes: int = 0
    total_restarts: int = 0
    average_uptime: float = 0.0
    peak_memory: Optional[float] = None
    peak_cpu: Optional[float] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    uptime_history: List[float] = field(default_factory=list)
    state_transitions: int = 0

    def get_reliability_score(self) -> float:
        """Calculate process reliability score (0-100).

        Returns:
            Reliability percentage
        """
        total_runs = self.success_count + self.failure_count
        if total_runs == 0:
            return 100.0

        return (self.success_count / total_runs) * 100.0

    def get_crash_frequency(self) -> float:
        """Get crashes per hour of operation.

        Returns:
            Crash frequency metric
        """
        total_uptime_hours = sum(self.uptime_history) / 3600.0 if self.uptime_history else 0.001
        return self.total_crashes / total_uptime_hours if total_uptime_hours > 0 else 0.0

    def get_health_status(self) -> str:
        """Get simple health status.

        Returns:
            'healthy', 'degraded', or 'critical'
        """
        reliability = self.get_reliability_score()

        if reliability >= 95.0:
            return "healthy"
        elif reliability >= 80.0:
            return "degraded"
        else:
            return "critical"


class ProcessRegistry:
    """Central registry for all managed processes.

    Tracks process information, collects metrics, and maintains
    historical data for analysis and optimization.
    """

    def __init__(self, max_history_size: int = 1000) -> None:
        """Initialize ProcessRegistry.

        Args:
            max_history_size: Maximum events to keep in history
        """
        self.max_history_size = max_history_size

        self._processes: dict[str, Process] = {}
        self._metrics: dict[str, ProcessMetrics] = {}
        self._event_history: List[dict[str, Any]] = []
        self._state_transitions: dict[str, int] = defaultdict(int)

    def register_process(self, process: Process) -> None:
        """Register a new process.

        Args:
            process: Process to register
        """
        self._processes[process.process_id] = process

        if process.process_id not in self._metrics:
            self._metrics[process.process_id] = ProcessMetrics(
                process_id=process.process_id,
                first_seen=datetime.now(),
            )

        self._record_event(
            "process_registered",
            process.process_id,
            {"command": process.config.command},
        )

        logger.info(f"Process {process.process_id} registered in registry")

    def unregister_process(self, process_id: str) -> None:
        """Unregister a process.

        Args:
            process_id: Process identifier
        """
        if process_id in self._processes:
            del self._processes[process_id]

        self._record_event("process_unregistered", process_id)
        logger.info(f"Process {process_id} unregistered from registry")

    def get_process(self, process_id: str) -> Optional[Process]:
        """Get registered process.

        Args:
            process_id: Process identifier

        Returns:
            Process or None if not found
        """
        return self._processes.get(process_id)

    def get_metrics(self, process_id: str) -> Optional[ProcessMetrics]:
        """Get metrics for a process.

        Args:
            process_id: Process identifier

        Returns:
            ProcessMetrics or None
        """
        return self._metrics.get(process_id)

    def list_processes(
        self, state: Optional[ProcessState] = None
    ) -> List[Process]:
        """List all or filtered processes.

        Args:
            state: Filter by process state

        Returns:
            List of Process objects
        """
        processes = list(self._processes.values())

        if state:
            processes = [p for p in processes if p.state == state]

        return processes

    def list_metrics(self) -> List[ProcessMetrics]:
        """Get metrics for all processes.

        Returns:
            List of ProcessMetrics
        """
        return list(self._metrics.values())

    def update_metrics_on_start(self, process_id: str) -> None:
        """Update metrics when process starts.

        Args:
            process_id: Process identifier
        """
        metrics = self._metrics.get(process_id)
        if metrics:
            metrics.total_starts += 1
            metrics.last_seen = datetime.now()

        self._record_event("process_started", process_id)

    def update_metrics_on_crash(self, process_id: str) -> None:
        """Update metrics when process crashes.

        Args:
            process_id: Process identifier
        """
        metrics = self._metrics.get(process_id)
        if metrics:
            metrics.total_crashes += 1
            metrics.failure_count += 1
            metrics.last_seen = datetime.now()

        self._record_event("process_crashed", process_id)

    def update_metrics_on_restart(self, process_id: str) -> None:
        """Update metrics when process is restarted.

        Args:
            process_id: Process identifier
        """
        metrics = self._metrics.get(process_id)
        if metrics:
            metrics.total_restarts += 1
            metrics.last_seen = datetime.now()

        self._record_event("process_restarted", process_id)

    def update_metrics_on_stop(self, process_id: str, uptime_seconds: float) -> None:
        """Update metrics when process stops.

        Args:
            process_id: Process identifier
            uptime_seconds: Runtime duration
        """
        metrics = self._metrics.get(process_id)
        if metrics:
            metrics.uptime_history.append(uptime_seconds)
            metrics.success_count += 1
            metrics.last_seen = datetime.now()

            # Update average uptime
            if metrics.uptime_history:
                metrics.average_uptime = sum(metrics.uptime_history) / len(
                    metrics.uptime_history
                )

        self._record_event(
            "process_stopped",
            process_id,
            {"uptime_seconds": uptime_seconds},
        )

    def record_state_transition(
        self,
        process_id: str,
        from_state: ProcessState,
        to_state: ProcessState,
    ) -> None:
        """Record a state transition.

        Args:
            process_id: Process identifier
            from_state: Previous state
            to_state: New state
        """
        transition_key = f"{from_state.value}->{to_state.value}"
        self._state_transitions[transition_key] += 1

        metrics = self._metrics.get(process_id)
        if metrics:
            metrics.state_transitions += 1

        self._record_event(
            "state_transition",
            process_id,
            {"from": from_state.value, "to": to_state.value},
        )

    def get_system_summary(self) -> dict[str, Any]:
        """Get summary statistics for all processes.

        Returns:
            Dictionary with system-wide metrics
        """
        all_metrics = list(self._metrics.values())

        if not all_metrics:
            return {
                "total_processes": 0,
                "timestamp": datetime.now().isoformat(),
            }

        total_starts = sum(m.total_starts for m in all_metrics)
        total_crashes = sum(m.total_crashes for m in all_metrics)
        total_restarts = sum(m.total_restarts for m in all_metrics)
        healthy_count = sum(1 for m in all_metrics if m.get_health_status() == "healthy")
        degraded_count = sum(1 for m in all_metrics if m.get_health_status() == "degraded")
        critical_count = sum(1 for m in all_metrics if m.get_health_status() == "critical")

        avg_reliability = (
            sum(m.get_reliability_score() for m in all_metrics) / len(all_metrics)
            if all_metrics
            else 0.0
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "total_processes": len(all_metrics),
            "total_starts": total_starts,
            "total_crashes": total_crashes,
            "total_restarts": total_restarts,
            "average_reliability": avg_reliability,
            "healthy_processes": healthy_count,
            "degraded_processes": degraded_count,
            "critical_processes": critical_count,
            "state_transitions": dict(self._state_transitions),
        }

    def get_event_history(
        self,
        limit: int = 100,
        process_id: Optional[str] = None,
    ) -> List[dict[str, Any]]:
        """Get event history.

        Args:
            limit: Maximum events to return
            process_id: Filter by process ID

        Returns:
            List of event records
        """
        events = self._event_history[-limit:]

        if process_id:
            events = [e for e in events if e.get("process_id") == process_id]

        return events

    def _record_event(
        self,
        event_type: str,
        process_id: str,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Record an event.

        Args:
            event_type: Type of event
            process_id: Process identifier
            details: Additional event details
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "process_id": process_id,
            "details": details or {},
        }

        self._event_history.append(event)

        # Keep history size bounded
        if len(self._event_history) > self.max_history_size:
            self._event_history = self._event_history[-self.max_history_size :]
