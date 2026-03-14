"""
Process Manager Integration Guide for KNO v6.0

How to integrate the Process & Task Management system
with the Hardware Abstraction Layer (HAL) and KNO agent.
"""

# ============================================================================
# OVERVIEW
# ============================================================================

The Process Manager complements HAL by providing:

1. **Task Scheduling**: Run external applications asynchronously
2. **Process Monitoring**: Track application lifecycle and health
3. **Self-Healing**: Automatic restart on crashes with configurable strategies
4. **Resource Awareness**: Adjust concurrency based on HAL metrics

Integration points:
- KNO agent initialization (agent.py)
- Audio system management (audio_manager.py)
- Resource monitoring (using HAL)
- GUI extensions (BotGUI_new.py)
- Configuration system (config.py)


# ============================================================================
# PHASE 3: KNO CORE INTEGRATION STEPS
# ============================================================================

STEP 1: Update agent.py
─────────────────────────────────────

File: agent.py

Add imports:
```python
from hardware.processes import (
    TaskScheduler,
    ProcessHealer,
    HealingStrategy,
    RetryPolicy,
    ProcessRegistry,
)
import asyncio
```

In Agent.__init__():
```python
self.process_scheduler = TaskScheduler(max_concurrent_tasks=5)
self.process_healer = ProcessHealer(
    healing_strategy=HealingStrategy.EXPONENTIAL_BACKOFF,
    retry_policy=RetryPolicy(max_retries=5)
)
self.process_registry = ProcessRegistry()
```

In Agent.initialize() or startup:
```python
# Start process management systems
await self.process_scheduler.start()
await self.process_healer.start_monitoring()
logger.info("Process management systems initialized")
```

In Agent.shutdown() or cleanup:
```python
# Graceful shutdown
await self.process_scheduler.stop(wait_pending=True)
await self.process_healer.stop_monitoring()
logger.info("Process management systems stopped")
```

In Agent.reasoning_loop() or main loop:
```python
# Every 60 seconds, check resource usage and adjust scheduling
if iteration % 60 == 0:
    memory_usage = await self.hw.memory.get_usage()
    
    # Adjust concurrency based on available memory
    if memory_usage > 85:
        self.process_scheduler.max_concurrent_tasks = 2
    elif memory_usage > 70:
        self.process_scheduler.max_concurrent_tasks = 4
    else:
        self.process_scheduler.max_concurrent_tasks = 5
    
    # Get process health status
    health = await self.process_healer.get_health_report()
    if health["processes"]:
        logger.info(f"Process health: {health}")
```


STEP 2: Add Process Management to Configuration
─────────────────────────────────────────────────

File: config.py

Add configuration class:
```python
@dataclass
class ProcessConfig:
    """Process Management Configuration"""
    
    # Scheduling
    max_concurrent_tasks: int = 5
    default_task_ttl_seconds: int = 300
    
    # Healing
    healing_strategy: str = "exponential_backoff"
    max_restart_attempts: int = 5
    initial_restart_delay: float = 5.0
    max_restart_delay: float = 300.0
    
    # Monitoring
    process_monitoring_enabled: bool = True
    health_check_interval: int = 5
    metrics_history_limit: int = 1000
    
    # Resource awareness
    memory_threshold_warning: float = 80.0
    memory_threshold_critical: float = 90.0
    cpu_threshold_warning: float = 80.0
```

Load from environment:
```python
process_cfg = ProcessConfig(
    max_concurrent_tasks=int(
        os.getenv("KNO_MAX_CONCURRENT_TASKS", "5")
    ),
    healing_strategy=os.getenv(
        "KNO_HEALING_STRATEGY", "exponential_backoff"
    ),
    ...
)
```


STEP 3: Integrate with Audio Manager
──────────────────────────────────────

File: audio_manager.py

Instead of manual device enumeration, use Process Manager for
audio applications that need to be launched:

```python
async def launch_audio_application(self, app_name: str):
    """Launch audio application through Process Manager"""
    
    command_map = {
        "audacity": "audacity.exe",
        "vlc": "vlc.exe",
        "foobar2000": "foobar2000.exe",
        ...
    }
    
    if app_name not in command_map:
        raise ValueError(f"Unknown app: {app_name}")
    
    task = await self.process_scheduler.schedule_task(
        process_id=f"audio_app_{app_name}",
        command=command_map[app_name],
        name=f"Audio: {app_name}",
        priority=TaskPriority.HIGH,
        auto_restart=True,
        max_retries=3
    )
    
    return task.task_id


async def stop_audio_application(self, app_name: str):
    """Stop audio application"""
    
    task = await self.process_registry.get_process(
        f"audio_app_{app_name}"
    )
    
    if task:
        await self.process_scheduler.stop_task(task.task_id)
```


STEP 4: GUI Dashboard Integration
─────────────────────────────────

File: BotGUI_new.py

Add process monitoring frame:

```python
class ProcessMonitorFrame(tk.Frame):
    """Monitor running processes in GUI"""
    
    def __init__(self, parent, scheduler, healer):
        super().__init__(parent)
        self.scheduler = scheduler
        self.healer = healer
        
        # Title
        tk.Label(self, text="Process Monitor").pack()
        
        # Task list
        self.task_tree = ttk.Treeview(self, columns=("Name", "Status", "Runtime"))
        self.task_tree.pack(fill=tk.BOTH, expand=True)
        
        # Health status
        self.health_label = tk.Label(self, text="Health: Healthy")
        self.health_label.pack()
        
        # Control buttons
        button_frame = tk.Frame(self)
        button_frame.pack()
        tk.Button(button_frame, text="Pause", command=self.pause_selected).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Resume", command=self.resume_selected).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Stop", command=self.stop_selected).pack(side=tk.LEFT)
        
        self.update_interval = 1000  # 1 second
        self.update_monitor()
    
    async def update_monitor(self):
        """Update process monitor display"""
        
        # Get task list
        stats = await self.scheduler.get_stats()
        tasks = await self.scheduler.list_tasks()
        
        # Update tree
        self.task_tree.delete(*self.task_tree.get_children())
        for task in tasks:
            runtime = await task.get_runtime_seconds()
            self.task_tree.insert("", "end", values=(
                task.name,
                task.status.value,
                f"{runtime:.1f}s"
            ))
        
        # Update health
        health = await self.healer.get_health_report()
        self.health_label.config(
            text=f"Processes: {health['total_monitored']}, "
                 f"Running: {stats['concurrent_running']}"
        )
        
        self.after(self.update_interval, 
                  lambda: asyncio.create_task(self.update_monitor()))
```

In main window:
```python
monitor_frame = ProcessMonitorFrame(root, scheduler, healer)
monitor_frame.pack()
```


STEP 5: Add Process Control Commands to Agent
───────────────────────────────────────────────

File: agent.py (command handling)

Add commands:
```python
async def handle_process_command(self, command: str, args: str):
    """Handle process management commands"""
    
    if command == "list_tasks":
        tasks = await self.process_scheduler.list_tasks()
        return {
            "tasks": [
                {
                    "id": t.task_id,
                    "name": t.name,
                    "status": t.status.value,
                    "priority": t.priority.value
                }
                for t in tasks
            ]
        }
    
    elif command == "run_task":
        # args: {"process_id": "...", "command": "...", "priority": "..."}
        task = await self.process_scheduler.schedule_task(
            process_id=args["process_id"],
            command=args["command"],
            priority=TaskPriority[args.get("priority", "NORMAL")]
        )
        return {"task_id": task.task_id}
    
    elif command == "stop_task":
        # args: {"task_id": "..."}
        success = await self.process_scheduler.stop_task(args["task_id"])
        return {"success": success}
    
    elif command == "pause_task":
        success = await self.process_scheduler.pause_task(args["task_id"])
        return {"success": success}
    
    elif command == "resume_task":
        success = await self.process_scheduler.resume_task(args["task_id"])
        return {"success": success}
    
    elif command == "process_stats":
        stats = await self.process_scheduler.get_stats()
        health = await self.process_healer.get_health_report()
        return {
            "scheduler": stats,
            "health": health
        }
```


# ============================================================================
# INTEGRATION CHECKLIST
# ============================================================================

Phase 3: KNO Core Integration

✓ Import Process Management modules in agent.py
✓ Initialize TaskScheduler, ProcessHealer, ProcessRegistry
✓ Start management systems in initialization
✓ Add resource monitoring to main loop
✓ Implement graceful shutdown
✓ Add process control commands
✓ Update configuration system
✓ Add GUI monitoring frame
✓ Integrate with audio_manager.py
✓ Add logging for process events
✓ Test with simple external application
✓ Verify self-healing with crash simulation
✓ Verify resource scaling


# ============================================================================
# USAGE EXAMPLES AFTER INTEGRATION
# ============================================================================

EXAMPLE 1: Agent Running External Tools
────────────────────────────────────────

async def agent_action():
    # Agent decides to analyze data with external tool
    task = await agent.process_scheduler.schedule_task(
        "data_analysis",
        "python analyze.py --dataset large_data.csv",
        priority=TaskPriority.HIGH,
        ttl_seconds=600
    )
    
    # Monitor execution
    while task.status.value not in ['completed', 'failed']:
        await asyncio.sleep(5)
    
    if task.status.value == 'completed':
        print("Analysis complete, reading results...")


EXAMPLE 2: Agent Managing Services
───────────────────────────────────

async def agent_manages_services():
    # Start multiple services
    services = ["api_server", "database", "cache"]
    
    for service in services:
        task = await agent.process_scheduler.schedule_task(
            service,
            f"python {service}.py",
            priority=TaskPriority.CRITICAL,
            auto_restart=True,
            max_retries=-1  # Unlimited restarts
        )
        
        # Add to healer for auto-recovery
        process = agent.process_manager.get_process(service)
        agent.process_healer.add_process(process)


EXAMPLE 3: Resource-Aware Task Scheduling
──────────────────────────────────────────

async def resource_aware_scheduling():
    memory = await agent.hw.memory.get_usage()
    
    if memory > 85:
        # Defer heavy tasks
        priority = TaskPriority.DEFERRED
    elif memory > 70:
        priority = TaskPriority.LOW
    else:
        priority = TaskPriority.NORMAL
    
    task = await agent.process_scheduler.schedule_task(
        "heavy_computation",
        "compute.py",
        priority=priority
    )
"""