# BotGUI Task Manager Integration Guide

## Overview

The enhanced **BotGUI_new.py** now includes a built-in **KNO Task Manager** with real-time process monitoring, reliability scoring, visual healing alerts, and automatic eDEX-UI synchronization.

## Features Added

### 1. Real-Time Process Monitoring Tab
- **Update Interval**: 1 second (non-blocking asyncio)
- **Display Columns**:
  - **Process ID**: Process identifier
  - **Status**: Current process state (CREATED, STARTING, RUNNING, STOPPING, STOPPED, CRASHED)
  - **Reliability %**: Reliability score (0-100% based on success/failure ratio)
  - **Avg Uptime (s)**: Average runtime in seconds
  - **Health**: Health status (healthy/degraded/critical)
  - **Crashes**: Total crash count

### 2. Health Status Color Coding
Visual indicators for process health using color-coded rows in the Treeview:
- **🟢 Green** (`health_healthy`): Reliability ≥ 95% - Process running smoothly
- **🟡 Yellow** (`health_degraded`): Reliability 80-95% - Process has issues
- **🔴 Red** (`health_critical`): Reliability < 80% - Process degraded

### 3. Visual Healing Alerts
Toast notifications when self-healing system attempts to recover a crashed process:
- **Attempt 1-3** (Green): Initial restart attempts
- **Attempt 4-5** (Yellow): Multiple retries in progress
- **Attempt ≥6** (Red): Healing failed, manual intervention needed
- **Auto-dismiss**: Alerts disappear after 3 seconds
- **Message Format**: `🔄 Restarting [process_name] (attempt #2)`

Example status display during healing:
```
GUI Status: "🔄 Restarting browser_agent (attempt #2)"
```

### 4. eDEX-UI Synchronization
Automatic JSON export to `edex_status.json` every 5 seconds:

**File Location**: `edex_status.json` (in workspace root or configured path)

**JSON Schema**:
```json
{
  "timestamp": "2024-01-20T15:30:45.123456",
  "system_health": "HEALTHY",
  "average_reliability": 97.5,
  "total_processes": 3,
  "processes": {
    "browser_agent": {
      "status": "RUNNING",
      "reliability_score": 98.5,
      "uptime": 3600.5,
      "crashes": 0,
      "restarts": 0,
      "health": "healthy",
      "success_count": 10,
      "failure_count": 0
    },
    "audio_agent": {
      "status": "RUNNING",
      "reliability_score": 96.0,
      "uptime": 2500.2,
      "crashes": 1,
      "restarts": 1,
      "health": "healthy",
      "success_count": 25,
      "failure_count": 1
    }
  },
  "recent_healing_events": [
    {
      "timestamp": "2024-01-20T15:30:30.123456",
      "process_id": "audio_agent",
      "reason": "crash_detected",
      "retry_count": 1
    }
  ]
}
```

## Integration with Process Manager

### Setting Up the ProcessRegistry

```python
from hardware.processes import ProcessRegistry, ProcessManager, TaskScheduler

# Initialize components
registry = ProcessRegistry(max_history_size=1000)
manager = ProcessManager(registry)
scheduler = TaskScheduler(max_concurrent_tasks=5)

# Create GUI
root = tk.Tk()
gui = FuturisticBotGUI(root)

# Connect registry to GUI for monitoring
gui.set_process_registry(registry)

# Configure edex_status.json path (optional)
gui.task_manager.edex_status_path = "/path/to/edex_status.json"

root.mainloop()
```

### Recording Healing Events

When your healing/restart logic detects a process needs recovery:

```python
# Record healing event in GUI
gui.record_healing_event(
    process_id="browser_agent",
    reason="crash_detected",
    retry_count=1
)

# This will:
# 1. Display visual alert: "🔄 Restarting browser_agent (attempt #1)"
# 2. Add event to task manager history
# 3. Include in next edex_status.json sync
```

## API Reference

### KNOTaskManager Class

```python
# Initialize task manager
task_manager = KNOTaskManager(edex_status_path="edex_status.json")

# Add process to tracking
task_manager.add_process(
    process_id="web_browser",
    config={"command": "chrome", "args": ["--remote-debugging-port=9222"]}
)

# Update process status
task_manager.update_process_status(
    process_id="web_browser",
    status="RUNNING",
    reliability=98.5,
    uptime=3600.0,
    crashes=0
)

# Record healing event
task_manager.record_healing_event(
    process_id="web_browser",
    reason="crash_detected",
    retry_count=1
)

# Sync to edex_status.json
task_manager.sync_to_edex()

# Get recent healing events
events = task_manager.get_healing_events_for_display(limit=5)
```

### FuturisticBotGUI Methods

```python
# Set ProcessRegistry for monitoring
gui.set_process_registry(registry)

# Record healing event and display alert
gui.record_healing_event(
    process_id="process_name",
    reason="crash_detected",
    retry_count=1
)

# Stop monitoring
gui.stop_monitoring()

# Safe shutdown
gui.safe_exit()
```

## Configuration

### Update Intervals

Modify in `_monitor_processes_async()`:
```python
# Update Treeview every N seconds (default: 1)
await asyncio.sleep(1.0)  # Change to 2.0 for 2-second updates

# Sync to JSON every N seconds (default: 5)
sync_interval = 5  # Change to 10 for 10-second syncs
```

### eDEX-UI Path

Set custom path for edex_status.json:
```python
gui.task_manager.edex_status_path = "/custom/path/edex_status.json"
```

### History Size

Limit healing events stored:
```python
gui.task_manager.max_history = 50  # Keep only 50 most recent events
```

### Color Customization

Modify Treeview tag colors:
```python
gui.process_treeview.tag_configure('health_healthy', foreground='#00FF00')
gui.process_treeview.tag_configure('health_degraded', foreground='#FFFF00')
gui.process_treeview.tag_configure('health_critical', foreground='#FF0000')
```

## Workflow Example

### Complete Integration Example

```python
import tkinter as tk
from hardware.processes import (
    ProcessRegistry, ProcessManager, TaskScheduler, 
    Process, ProcessConfig, ProcessState
)
from BotGUI_new import FuturisticBotGUI

# Initialize process management system
registry = ProcessRegistry()
manager = ProcessManager(registry)
scheduler = TaskScheduler(max_concurrent_tasks=3)

# Create GUI
root = tk.Tk()
gui = FuturisticBotGUI(root)
gui.set_process_registry(registry)

# Simulate adding a process
config = ProcessConfig(command="python", args=["agent.py"])
process = Process("main_agent", config)
registry.register_process(process)

# Start the process
manager.start(process)

# If process crashes, record healing
def on_crash_detected(process_id):
    gui.record_healing_event(
        process_id=process_id,
        reason="crash_detected",
        retry_count=1
    )
    # Restart the process
    manager.start(next(p for p in registry.list_processes() if p.process_id == process_id))

# In event loop: edex_status.json auto-syncs every 5 seconds
# Task list updates every 1 second (visible in GUI)
# Alerts display with 3-second auto-dismiss

root.mainloop()
```

## Debugging Tips

### Check edex_status.json

Verify JSON sync is working:
```bash
# Windows
type edex_status.json

# Linux/Mac
cat edex_status.json
```

### Monitor Process List

Treeview automatically updates every 1 second. Watch for:
- Green rows: Healthy processes
- Yellow rows: Degraded performance
- Red rows: Critical issues

### Healing Events

Healing alerts appear as status updates. If not visible:
1. Check `task_manager.healing_events_queue` has events
2. Verify `record_healing_event()` is being called
3. Check terminal for `[HEALING_ALERT]` logs

### Performance

Monitor CPU/Memory with large process counts:
- **100+ processes**: Consider increasing update interval to 2-3 seconds
- **1000+ processes**: Use filtering or pagination in Treeview

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Treeview not updating | Check `set_process_registry()` was called |
| edex_status.json not created | Verify write permissions to workspace |
| Healing alerts not showing | Check `record_healing_event()` calls and timestamp cache |
| High CPU usage | Increase `asyncio.sleep()` interval (slower updates) |
| Color tags not working | Verify both tag and registry are set up |

## Thread Safety

All GUI updates run on the main Tkinter thread via `after()` callbacks:
- Async monitor runs in separate thread with asyncio event loop
- JSON sync uses `asyncio.to_thread()` to avoid blocking
- Thread-safe: ProcessRegistry uses internal locks

## Next Steps

1. **Connect to Agent.py**: Pass registry to your main agent loop
2. **Custom Alerts**: Modify alert colors/messages in `_display_healing_alerts()`
3. **eDEX Integration**: Add listeners to edex_status.json changes in eDEX-UI
4. **Metrics Dashboard**: Extend Treeview with charts/graphs using matplotlib
