# KNO v6.0 - Task Manager Quick Reference Card

## 🎯 What Was Added to BotGUI_new.py

### Four Key Features:

1. **Real-Time Process Monitoring** (1-second updates)
   - Live Treeview showing all processes
   - Status, reliability %, uptime, health, crash count
   - Non-blocking asyncio implementation

2. **Color-Coded Health Status**
   - 🟢 Green: Healthy (≥95% reliability)
   - 🟡 Yellow: Degraded (80-95% reliability)
   - 🔴 Red: Critical (<80% reliability)

3. **Visual Healing Alerts**
   - Toast notifications on process restart
   - Auto-dismiss after 3 seconds
   - Retry count indicator
   - Color progression: Green → Yellow → Red

4. **eDEX-UI JSON Sync** (5-second interval)
   - Auto-export to `edex_status.json`
   - System health calculation
   - Recent healing events
   - Cross-system integration ready

---

## 🚀 Quick Start (30 seconds)

```python
import tkinter as tk
from hardware.processes import ProcessRegistry, ProcessManager
from BotGUI_new import FuturisticBotGUI

# 1. Setup
registry = ProcessRegistry()
manager = ProcessManager(registry)
root = tk.Tk()
gui = FuturisticBotGUI(root)

# 2. Connect monitoring
gui.set_process_registry(registry)

# 3. Use normally - monitoring is automatic!
root.mainloop()
```

---

## 📋 Common Tasks

### Display a Process in Monitoring

```python
from hardware.processes import Process, ProcessConfig

config = ProcessConfig(command="python", args=["agent.py"])
process = Process("my_agent", config)
registry.register_process(process)
manager.start(process)

# Process now appears in Treeview, updates every 1s
```

### Record a Healing Event

```python
# When your process crashes and you restart it:
gui.record_healing_event(
    process_id="my_agent",
    reason="crash_detected",
    retry_count=1  # Which attempt?
)

# Visual alert appears in status bar, auto-dismisses after 3s
```

### Check System Health from JSON

```python
import json
from pathlib import Path

edex = json.loads(Path("edex_status.json").read_text())
print(edex["system_health"])      # "HEALTHY", "DEGRADED", "CRITICAL"
print(edex["average_reliability"])  # 97.5 (%)
print(edex["total_processes"])      # 3
```

---

## 🎨 Display Layout

```
┌─────────────────────────────────────┐
│ KNO                        Ready    │ ← Status bar
├─────────────────────────────────────┤
│                                     │
│      Audio Wave Visualization       │ ← Original GUI (unchanged)
│            (60 FPS)                 │
│                                     │
├─────────────────────────────────────┤
│ Process ID │ Status │ Reliability │  │ ← NEW: Task Monitor
│ my_agent   │ RUNNING│    98.5%   │  │   (1s refresh)
│ web_driver │ RUNNING│    95.2%   │  │
│ audio_proc │ CRASHED│    72.0%   │  │
├─────────────────────────────────────┤
│ Command KNO...                      │ ← Text input (unchanged)
└─────────────────────────────────────┘
```

**Color coding applied to process rows:**
- Green text = healthy process
- Yellow text = degraded process  
- Red text = critical process

---

## ⚙️ Configuration

### Update Interval (default: 1 second)

```python
# In BotGUI_new.py, line ~580
await asyncio.sleep(1.0)  # Change to 2.0 or 0.5
```

### JSON Sync Interval (default: 5 seconds)

```python
# In BotGUI_new.py, line ~553
sync_interval = 5  # Change to 10 or 3
```

### JSON File Path (default: edex_status.json)

```python
gui.task_manager.edex_status_path = "custom/path/edex.json"
```

### Max History Size (default: 100 events)

```python
gui.task_manager.max_history = 50  # Keep fewer events
```

---

## 📊 edex_status.json Structure

**File**: `edex_status.json` (auto-created every 5 seconds)

**Key fields**:
```json
{
  "timestamp": "2024-01-20T15:30:45.123456",
  "system_health": "HEALTHY|DEGRADED|CRITICAL",
  "average_reliability": 97.5,
  "total_processes": 3,
  
  "processes": {
    "process_name": {
      "status": "RUNNING|CRASHED|STOPPED",
      "reliability_score": 98.5,
      "uptime": 3600.5,
      "crashes": 0,
      "restarts": 0,
      "health": "healthy|degraded|critical"
    }
  },
  
  "recent_healing_events": [
    {
      "timestamp": "...",
      "process_id": "...",
      "reason": "crash_detected",
      "retry_count": 1
    }
  ]
}
```

---

## 🔍 Debugging Checklist

- [ ] `set_process_registry(registry)` called?
- [ ] Processes registered in registry before starting?
- [ ] edex_status.json exists in workspace?
- [ ] Terminal shows `[GUI] Process registry monitoring started`?
- [ ] Treeview shows processes after 1 second?
- [ ] JSON updates every 5 seconds (check timestamp)?
- [ ] Healing alerts appear when calling `record_healing_event()`?

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| [BOTGUI_TASK_MANAGER_GUIDE.md](BOTGUI_TASK_MANAGER_GUIDE.md) | Complete integration guide (450+ lines) |
| [BOTGUI_ENHANCEMENTS_SUMMARY.md](BOTGUI_ENHANCEMENTS_SUMMARY.md) | Technical summary of changes |
| [botgui_integration_example.py](botgui_integration_example.py) | 5 working examples |
| [PROCESS_MANAGER_API_REFERENCE.md](PROCESS_MANAGER_API_REFERENCE.md) | ProcessRegistry API |

---

## 🎯 Integration Points

### For agent.py
```python
gui.set_process_registry(your_registry)
gui.record_healing_event(proc_id, "reason", attempt_num)
```

### For audio_manager.py
```python
# Include process in registry
registry.register_process(audio_process)
```

### For config.py
```python
EDEX_STATUS_PATH = "edex_status.json"
gui.task_manager.edex_status_path = config.EDEX_STATUS_PATH
```

---

## ✅ Feature Checklist

- [x] Real-time Treeview (1-second updates)
- [x] Reliability score display per process
- [x] Color-coded health status (green/yellow/red)
- [x] Visual healing alerts with retry count
- [x] Auto-dismiss alerts after 3 seconds
- [x] JSON sync to edex_status.json (5-second interval)
- [x] System health calculation (HEALTHY/DEGRADED/CRITICAL)
- [x] Recent healing events in JSON
- [x] Thread-safe asyncio implementation
- [x] Non-blocking UI updates
- [x] Full backward compatibility
- [x] Comprehensive documentation
- [x] 5 working examples

---

## 🔗 Related Processes

This Task Manager integrates with:
- **ProcessRegistry**: Provides metrics and process list
- **ProcessManager**: Handles process lifecycle
- **ProcessHealer**: Auto-restart on crash
- **TaskScheduler**: Task queue and execution
- **eDEX-UI**: Real-time status display

---

## 💡 Pro Tips

1. **Monitor everything**: Add all important processes to registry for visibility
2. **Color watch**: Glance at Treeview colors for instant health status
3. **JSON bridge**: Use edex_status.json to feed data to monitoring dashboards
4. **History**: Healing alerts auto-expire - check JSON for full history
5. **Performance**: With 100+ processes, increase update interval to 2-3 seconds

---

## 🐛 Troubleshooting

**Treeview empty?**
```python
gui.set_process_registry(registry)  # Must call this!
```

**JSON not updating?**
```python
# Check file exists and has recent timestamp
cat edex_status.json | grep timestamp
```

**Alerts not showing?**
```python
# Must call record_healing_event when process crashes
gui.record_healing_event("proc_id", "crash_detected", 1)
```

**High memory?**
```python
gui.task_manager.max_history = 50  # Reduce from 100
```

---

## 📞 Quick Reference

| Task | Code |
|------|------|
| Enable monitoring | `gui.set_process_registry(registry)` |
| Add process | `registry.register_process(process)` |
| Record healing | `gui.record_healing_event(id, reason, count)` |
| Stop monitoring | `gui.stop_monitoring()` |
| Exit cleanly | `gui.safe_exit()` |
| Check health | `json.load(open("edex_status.json"))["system_health"]` |

---

## 🎓 Learning Path

1. **Start**: Run `botgui_integration_example.py 1` (basic example)
2. **Learn**: Read [BOTGUI_TASK_MANAGER_GUIDE.md](BOTGUI_TASK_MANAGER_GUIDE.md)
3. **Explore**: Try examples 2-5 with your processes
4. **Integrate**: Add to your agent.py following the checklist
5. **Monitor**: Watch the Treeview and edex_status.json updates

---

**Version**: KNO v6.0  
**Date**: 2024-01-20  
**Status**: ✅ Production Ready
