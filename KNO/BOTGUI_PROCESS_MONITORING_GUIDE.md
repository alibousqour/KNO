# BotGUI Process Monitoring Integration Guide

## Overview

The enhanced `BotGUI_new.py` now includes integrated **async process registry monitoring** with a real-time Treeview widget displaying:
- Process ID
- Current State (RUNNING, STOPPED, etc.)
- Reliability Score (0-100%)
- Average Uptime (seconds)
- Health Status (healthy, degraded, critical)
- Total Crashes

## Key Features

### 1. **Async Process Monitoring**
- Polls ProcessRegistry every 2 seconds using `asyncio`
- Runs in a dedicated background thread with its own event loop
- Non-blocking GUI updates via Tkinter's thread-safe `.after()` method
- Automatically stops on GUI shutdown

### 2. **Real-Time Treeview Display**
- **Integrated Layout**: Audio wave visualization (top) + Process Treeview (bottom)
- **Scrollable**: Up to 8 rows visible with scrollbar for many processes
- **Color Coded**: Neon cyan styling matching the cyberpunk aesthetic
- **Self-updating**: Adds/removes/updates rows as processes start/stop

### 3. **Thread-Safe Integration**
- Uses `asyncio.new_event_loop()` in background thread
- GUI updates marshaled through `master.after()` callback
- No Tkinter race conditions or blocking

## Installation & Usage

### Step 1: Import ProcessRegistry

```python
from hardware.processes.process_registry import ProcessRegistry
```

### Step 2: Initialize GUI and Registry

```python
import tkinter as tk
from BotGUI_new import FuturisticBotGUI
from hardware.processes.process_registry import ProcessRegistry

# Create Tkinter root
root = tk.Tk()

# Create GUI
gui = FuturisticBotGUI(root)

# Create or get your ProcessRegistry instance
registry = ProcessRegistry(max_history_size=1000)

# Connect registry to GUI monitoring
gui.set_process_registry(registry)

# Start main loop
root.mainloop()
```

### Step 3: Register Processes

As you create and manage processes, register them with the registry:

```python
# After creating a Process instance:
process = Process(process_id="main_worker", config=ProcessConfig(...))
registry.register_process(process)

# Update metrics when process lifecycle changes:
registry.update_metrics_on_start(process.process_id)
# ... later:
registry.update_metrics_on_stop(process.process_id, uptime_seconds=45.3)
```

## API Reference

### FuturisticBotGUI Methods

#### `set_process_registry(registry: ProcessRegistry) -> None`
Activates process monitoring in the GUI.

**Parameters:**
- `registry`: ProcessRegistry instance to monitor

**Behavior:**
- Starts background async monitoring thread
- Begins 2-second polling cycle
- Updates Treeview with current metrics

**Example:**
```python
gui.set_process_registry(my_registry)
```

#### `stop_monitoring() -> None`
Stops the process monitoring (called automatically on exit).

**Example:**
```python
gui.stop_monitoring()
```

#### `_monitor_processes_async() -> None` (Async)
Polls registry every 2 seconds. Runs in background thread event loop.

**Behavior:**
- Calls `registry.list_metrics()` for all process metrics
- Calls `registry.list_processes()` for current states
- Marshals updates to Tkinter via `.after()`
- Sleeps for 2 seconds between polls

#### `_update_treeview(metrics_list, process_states) -> None`
Updates Treeview rows with latest metrics (runs on main thread).

**Behavior:**
- Adds new processes to Treeview
- Updates existing process rows
- Removes processes no longer in registry
- Formats reliability, uptime, and health data

## Treeview Display Format

### Columns

| Column | Type | Format | Example |
|--------|------|--------|---------|
| Process ID | Text | String | `worker_1`, `audio_processor` |
| Status | Enum | State name | `RUNNING`, `STOPPED`, `CRASHED` |
| Reliability % | Percentage | Float with % | `98.5%`, `75.0%` |
| Avg Uptime (s) | Seconds | Float with 1 decimal | `125.4`, `45.0` |
| Health | Status | String | `healthy`, `degraded`, `critical` |
| Crashes | Count | Integer | `0`, `5`, `12` |

### Update Interval
- **Default**: 2 seconds
- **Non-blocking**: GUI remains responsive
- **Automatic**: No manual refresh needed

## Integration Example

Here's a complete example integrating the GUI with actual process monitoring:

```python
import tkinter as tk
import asyncio
from BotGUI_new import FuturisticBotGUI
from hardware.processes.process_registry import ProcessRegistry
from hardware.processes.process_manager import Process, ProcessConfig, ProcessState

# Initialize
root = tk.Tk()
gui = FuturisticBotGUI(root)
registry = ProcessRegistry()

# Create and register processes
config1 = ProcessConfig(
    command="my_worker_script.py",
    auto_restart=True,
    restart_delay=5
)
process1 = Process(process_id="worker_1", config=config1)
registry.register_process(process1)

config2 = ProcessConfig(
    command="audio_processor.py",
    auto_restart=False,
    restart_delay=0
)
process2 = Process(process_id="audio_processor", config=config2)
registry.register_process(process2)

# Connect monitoring to GUI
gui.set_process_registry(registry)

# Simulate process lifecycle
async def simulate_processes():
    """Simulate process activity for testing."""
    registry.update_metrics_on_start("worker_1")
    await asyncio.sleep(3)
    registry.update_metrics_on_start("audio_processor")
    await asyncio.sleep(5)
    
    # Simulate crash
    registry.update_metrics_on_crash("worker_1")
    
    await asyncio.sleep(2)
    
    # Simulate recovery
    registry.update_metrics_on_restart("worker_1")
    await asyncio.sleep(10)
    
    # Simulate graceful stop
    registry.update_metrics_on_stop("audio_processor", uptime_seconds=15.5)

# Run simulation in background thread
import threading
sim_thread = threading.Thread(
    target=lambda: asyncio.run(simulate_processes()),
    daemon=True
)
sim_thread.start()

# Start GUI
root.mainloop()
```

## ProcessRegistry Metrics API

### Available Metrics Properties

From `ProcessMetrics` class (returned by `registry.list_metrics()`):

```python
metrics = registry.get_metrics(process_id)

# Direct attributes
metrics.process_id          # String
metrics.total_starts        # Integer
metrics.total_crashes       # Integer
metrics.total_restarts      # Integer
metrics.average_uptime      # Float (seconds)
metrics.peak_memory         # Float or None
metrics.peak_cpu            # Float or None
metrics.first_seen          # datetime or None
metrics.last_seen           # datetime or None
metrics.success_count       # Integer
metrics.failure_count       # Integer
metrics.uptime_history      # List[float]
metrics.state_transitions   # Integer

# Computed methods
reliability = metrics.get_reliability_score()  # 0.0-100.0
crash_freq = metrics.get_crash_frequency()   # crashes/hour
health = metrics.get_health_status()          # 'healthy'/'degraded'/'critical'
```

### Health Status Rules

The Treeview displays health status based on reliability score:

- **healthy**: Reliability >= 95%
- **degraded**: Reliability >= 80% and < 95%
- **critical**: Reliability < 80%

## Thread Safety

The implementation is fully thread-safe:

1. **Background Polling**: Async monitoring runs in dedicated thread
2. **Event Loop**: `asyncio.new_event_loop()` prevents conflicts
3. **GUI Updates**: `.after(0, callback)` marshals to main thread
4. **Treeview Access**: Only updated from main thread

No locks required—Tkinter's event loop handles synchronization.

## Performance Considerations

### Polling Impact
- **2-second interval**: Minimal CPU overhead
- **Per-process cost**: O(1) metric retrieval
- **GUI update cost**: O(n) where n = number of processes

### Memory Usage
- **Treeview items**: ~100 bytes per process
- **Items dictionary**: Track for efficient updates
- **Background thread**: Minimal (single asyncio loop)

## Stopping Monitoring

Monitoring automatically stops when:
- GUI window is closed
- `exit_fullscreen()` is called
- `safe_exit()` is called
- `stop_monitoring()` is explicitly called

Example explicit stop:
```python
gui.stop_monitoring()
# Treeview stops updating but remains visible
```

## Troubleshooting

### Treeview Not Updating

**Problem**: Process metrics not appearing in Treeview

**Solutions**:
1. Ensure `gui.set_process_registry(registry)` was called
2. Verify processes are registered: `registry.register_process(process)`
3. Check that `registry.list_metrics()` returns non-empty list
4. Verify `process.state` is a valid `ProcessState`

### Missing Columns

**Problem**: Reliability or other columns are blank

**Solutions**:
1. Ensure `ProcessMetrics` object has complete data
2. Check that `get_reliability_score()` doesn't raise exception
3. Verify `average_uptime` is properly calculated

### High CPU Usage

**Problem**: Background monitoring using too much CPU

**Solutions**:
1. Verify 2-second sleep is working (check logs)
2. Ensure no exceptions in `_monitor_processes_async()`
3. Check network/disk I/O during metric retrieval

## Customization

### Change Update Interval

Edit line in `_monitor_processes_async()`:
```python
await asyncio.sleep(2.0)  # Change to desired seconds
```

### Customize Treeview Columns

Modify column configuration in `__init__()`:
```python
self.process_treeview.column("#0", width=200, anchor=tk.W)  # Process ID width
self.process_treeview.column("Reliability", width=100)      # Reliability width
```

### Add Custom Metrics

Override `_update_treeview()` to include additional columns:
```python
# Add to ProcessMetrics properties in values tuple:
values=(state_str, reliability_str, uptime_str, health, crashes_str, custom_metric)
```

## Summary

The enhanced BotGUI provides real-time process monitoring with:
- ✅ Async 2-second polling
- ✅ Thread-safe Tkinter integration
- ✅ Automatic metric updates
- ✅ Scrollable display
- ✅ No performance impact on main GUI
- ✅ Clean cyberpunk aesthetic

Just call `gui.set_process_registry(registry)` and monitoring starts immediately!
