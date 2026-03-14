# eDEX-UI Data Bridge Integration Guide

## Overview

The EDEXMonitor class creates a real-time "data bridge" between your Python KNO agent and the eDEX-UI cinematic interface. This allows eDEX-UI to display live agent status, think processes, LLM operations, and system metrics.

## Architecture

```
┌─────────────────────┐
│   KNO Agent (Python)│
│  - Thinking Logic   │
│  - LLM Calls        │
│  - Error Fixes      │
└──────────┬──────────┘
           │
           │ Updates JSON via EDEXMonitor
           │
           ▼
┌─────────────────────┐
│ edex_status.json    │
│  (JSON File)        │
└──────────┬──────────┘
           │
           │ Reads JSON every 500ms
           │
           ▼
┌─────────────────────┐
│   eDEX-UI Interface │
│  - Display Status   │
│  - Show Progress    │
│  - Live Metrics     │
└─────────────────────┘
```

## Quick Start

### Step 1: Import and Initialize

```python
from kno_utils import edex_monitor
import asyncio

class YourAgent:
    def __init__(self):
        self.monitor = edex_monitor  # Already initialized globally
        
        # Or create a custom instance:
        # from kno_utils import EDEXMonitor
        # self.monitor = EDEXMonitor("path/to/edex_status.json")
```

### Step 2: Update Status During Operations

#### Method A: Async (Recommended)
```python
async def think(self, prompt):
    """Thinking operation with async status updates"""
    await self.monitor.update_status(
        agent_status="THINKING",
        current_task=f"Analyzing: {prompt[:50]}...",
        llm_model="Gemini-Pro",
        progress=0
    )
    
    # Do your thinking here
    response = await self.llm_coordinator.query(prompt)
    
    await self.monitor.update_status(
        agent_status="IDLE",
        current_task="Thought complete",
        progress=100,
        last_action="Completed analysis"
    )
    
    return response
```

#### Method B: Sync (Non-blocking alternative)
```python
def on_search_start(self, query):
    """Search operation with sync status update"""
    self.monitor.update_status_sync(
        agent_status="SEARCHING",
        current_task=f"Searching: {query}",
        progress=20
    )
    
    # Do search
    results = self.search_engine.find(query)
    
    self.monitor.update_status_sync(
        agent_status="IDLE",
        progress=100,
        last_action=f"Found {len(results)} results"
    )
```

## Status Field Reference

### Core Fields
| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `agent_status` | string | `IDLE`, `THINKING`, `SEARCHING`, `FIXING`, `EXECUTING`, `ERROR` | Current agent state |
| `current_task` | string | Any | Human-readable activity description |
| `progress` | int | 0-100 | Task completion percentage |
| `llm_model` | string | Model name | Currently active LLM |

### System Fields
| Field | Type | Description |
|-------|------|-------------|
| `memory_usage_mb` | float | RAM consumption in MB |
| `cpu_usage_percent` | float | CPU usage percentage |
| `tasks_completed` | int | Total tasks since session start |
| `uptime_seconds` | int | Session duration in seconds |

### Activity Fields
| Field | Type | Description |
|-------|------|-------------|
| `last_action` | string | Most recent operation completed |
| `last_fix` | string | Last code/error fix applied |
| `last_error` | string | Last error encountered |
| `last_update` | string | ISO timestamp of last update |

## Integration Examples

### Example 1: LLM Query with Progress

```python
async def query_llm_with_progress(self, prompt):
    """Query LLM while showing progress"""
    
    await self.monitor.update_status(
        agent_status="THINKING",
        current_task="Sending to Gemini...",
        llm_model="Gemini-Pro",
        progress=10
    )
    
    try:
        await self.monitor.update_status(progress=30)
        response = await self.llm_coordinator.query(prompt)
        
        await self.monitor.update_status(
            progress=80,
            last_action="Model responded"
        )
        
        await self.monitor.update_status(
            agent_status="IDLE",
            progress=100,
            last_action="Response processed",
            tasks_completed=self.monitor.data["tasks_completed"] + 1
        )
        self.monitor.add_task_completed()
        
        return response
        
    except Exception as e:
        self.monitor.log_error(str(e))
        raise
```

### Example 2: Error Detection & Fix

```python
def apply_auto_fix(self, error_msg, code_fix):
    """Auto-fix error and update monitor"""
    
    self.monitor.update_status_sync(
        agent_status="FIXING",
        current_task="Applying automatic fix...",
        progress=50
    )
    
    try:
        # Apply the fix
        self.code_patcher.apply(code_fix)
        
        # Log the fix
        self.monitor.log_fix(f"Fixed: {error_msg[:60]}...")
        
        self.monitor.update_status_sync(
            agent_status="IDLE",
            current_task="Fix applied successfully",
            progress=100
        )
        
    except Exception as e:
        self.monitor.log_error(f"Fix failed: {str(e)}")
```

### Example 3: Search & Data Processing

```python
async def search_and_process(self, query):
    """Multi-step operation with stage updates"""
    
    # Stage 1: Search
    await self.monitor.update_status(
        agent_status="SEARCHING",
        current_task=f"Searching for: {query}",
        progress=20,
        llm_model="Search Engine"
    )
    
    results = await self.search_engine.find_async(query)
    
    # Stage 2: Process
    await self.monitor.update_status(
        agent_status="THINKING",
        current_task="Processing search results...",
        progress=50,
        llm_model="Gemini-Pro"
    )
    
    processed = await self.process_results(results)
    
    # Stage 3: Complete
    await self.monitor.update_status(
        agent_status="IDLE",
        current_task="Search complete",
        progress=100,
        last_action=f"Processed {len(results)} results"
    )
    self.monitor.add_task_completed()
    
    return processed
```

## Configuring eDEX-UI to Display Data

### Option 1: Direct JSON Reading (Recommended)

1. **Create a custom widget in eDEX-UI** that reads the JSON file periodically:

```javascript
// In eDEX-UI widgets configuration
// Add to: eDEX-ui/src/components/widgets/customWidget.js

class KNOStatusWidget {
    async readStatusFile() {
        try {
            const response = await fetch('file:///full/path/to/edex_status.json');
            const status = await response.json();
            this.displayStatus(status);
        } catch (e) {
            console.error('Failed to read status:', e);
        }
    }
    
    displayStatus(status) {
        // Update UI with status data
        document.getElementById('agent-status').textContent = status.agent_status;
        document.getElementById('current-task').textContent = status.current_task;
        document.getElementById('progress-bar').value = status.progress;
        document.getElementById('llm-model').textContent = status.llm_model;
    }
    
    startPolling() {
        setInterval(() => this.readStatusFile(), 500);  // Update every 500ms
    }
}
```

2. **Add to your eDEX theme configuration** (in `settings.json`):

```json
{
    "widgets": {
        "kno_status": {
            "type": "status",
            "file_path": "../edex_status.json",
            "refresh_interval_ms": 500,
            "display": {
                "position": "top-left",
                "size": "small",
                "show_fields": [
                    "agent_status",
                    "current_task",
                    "progress",
                    "llm_model",
                    "cpu_usage_percent",
                    "memory_usage_mb"
                ]
            }
        }
    }
}
```

### Option 2: WebSocket Real-Time Updates

If you want live updates without polling:

```python
# In your agent initialization
async def broadcast_status_websocket(self):
    """Send status updates via WebSocket"""
    import websockets
    import json
    
    async def send_updates():
        while True:
            status = self.monitor.get_current_status()
            message = json.dumps(status)
            
            if self.ws:
                await self.ws.send(message)
            
            await asyncio.sleep(0.5)  # Update every 500ms
    
    # Start the task
    asyncio.create_task(send_updates())
```

## Performance Monitoring

The monitor also tracks system metrics:

```python
import psutil

async def update_system_metrics(self):
    """Update system performance metrics"""
    
    process = psutil.Process()
    
    await self.monitor.update_status(
        memory_usage_mb=process.memory_info().rss / 1024 / 1024,
        cpu_usage_percent=process.cpu_percent(interval=0.1)
    )
```

## Lifecycle Management

### Reset at Session Start
```python
def __init__(self):
    self.monitor = edex_monitor
    self.monitor.reset()  # Clear previous session
```

### Log Session Events
```python
def on_error(self, error):
    self.monitor.log_error(str(error))

def on_fix_applied(self, fix_description):
    self.monitor.log_fix(fix_description)
```

## File Location

The `edex_status.json` file is created at the path you specify:

```python
# Default location (project root)
monitor = EDEXMonitor("edex_status.json")

# Custom location
monitor = EDEXMonitor("data/edex_status.json")

# Absolute path
monitor = EDEXMonitor("/full/path/to/edex_status.json")
```

## Troubleshooting

### File Not Updating
1. Check file permissions
2. Verify path is correct
3. Ensure async/sync method is called
4. Check logs for errors: `logger.error()`

### eDEX-UI Not Reading File
1. Verify file path in widget configuration
2. Check file exists: `ls -la edex_status.json`
3. Verify JSON is valid: `python -m json.tool edex_status.json`
4. Check file refresh interval (should be 500ms)

### Performance Impact
- JSON file write is non-blocking (uses executor)
- Typically < 1ms per update
- File size stays small (< 5KB)
- No polling overhead on agent

## Example Status File Output

```json
{
    "agent_status": "THINKING",
    "current_task": "Analyzing user prompt about Python optimization...",
    "progress": 45,
    "llm_model": "Gemini-Pro",
    "memory_usage_mb": 234.5,
    "cpu_usage_percent": 32.1,
    "last_action": "Sent query to LLM",
    "last_fix": "Fixed import statement in module",
    "last_error": null,
    "tasks_completed": 7,
    "session_start": "2026-03-09T14:22:31.456789",
    "last_update": "2026-03-09T14:22:45.123456",
    "uptime_seconds": 13
}
```

## Next Steps

1. ✅ EDEXMonitor class is already in `kno_utils.py`
2. Import it in your agent: `from kno_utils import edex_monitor`
3. Call `update_status()` during agent operations
4. Configure eDEX-UI to read the JSON file
5. Watch the cinematic interface update in real-time!

## Advanced Features Coming Next

- WebSocket streaming for true real-time updates
- Audio/visual alerts on status changes
- Multi-agent status aggregation
- Historical data logging
- Performance graphs in eDEX-UI

---

**Questions?** Check the example integrations above or review the EDEXMonitor source in `kno_utils.py`.
