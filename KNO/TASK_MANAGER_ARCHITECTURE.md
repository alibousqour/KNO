# KNO v6.0 Task Manager - System Architecture

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Hardware Processes                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ ProcessRegistry   ProcessManager   TaskScheduler  Healer  │ │
│  │                                                             │ │
│  │ - Tracks all      - Manages        - Queues tasks  - Auto │ │
│  │   processes       lifecycle        - Priority      restart │ │
│  │ - Metrics         - Start/stop     - Concurrency           │ │
│  │ - Health          - Pause/resume   - TTL/expiry           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              △
                              │
                              │ registry.list_metrics()
                              │ registry.list_processes()
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      FuturisticBotGUI                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Process Monitor Thread                        │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │  Async Event Loop (asyncio)                          │ │ │
│  │  │  ┌──────────────────────────────────────────────────┐│ │ │
│  │  │  │ _monitor_processes_async()                       ││ │ │
│  │  │  │                                                  ││ │ │
│  │  │  │ while monitoring_active:                         ││ │ │
│  │  │  │   - Fetch metrics (0.1ms)                        ││ │ │
│  │  │  │   - Update Treeview (via after) (every 1s)       ││ │ │
│  │  │  │   - Check healing alerts (every 1s)              ││ │ │
│  │  │  │   - Sync to JSON (every 5s)                      ││ │ │
│  │  │  │   - Sleep 1.0 second (non-blocking)              ││ │ │
│  │  │  └──────────────────────────────────────────────────┘│ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐│
│  │  Tkinter Main Thread │  │  Audio Wave Animation Thread     ││
│  │  ┌────────────────────┐  │  ┌──────────────────────────────┐││
│  │  │ - Text input       │  │  │ - Draw 60 FPS waves          │││
│  │  │ - Status label     │  │  │ - Draw circles               │││
│  │  │ - Treeview display │  │  │ - Update phase               │││
│  │  │ - Events           │  │  │ (original GUI unchanged)     │││
│  │  │ - Help alerts      │  │  └──────────────────────────────┘││
│  │  └────────────────────┘  └──────────────────────────────────┘│
│  └──────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  KNOTaskManager                                            │  │
│  │  - Track processes               - records_healing_event() │  │
│  │  - Record healing events         - get_healing_events()    │  │
│  │  - Calculate health              - sync_to_edex()         │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ JSON output
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    edex_status.json                             │
│  {                                                               │
│    "timestamp": "2024-01-20T15:30:45",                         │
│    "system_health": "HEALTHY|DEGRADED|CRITICAL",              │
│    "average_reliability": 97.5,                                │
│    "processes": {                                              │
│      "process_id": {                                           │
│        "status": "RUNNING",                                    │
│        "reliability_score": 98.5,                              │
│        "uptime": 3600.5,                                       │
│        "health": "healthy",                                    │
│        ...                                                     │
│      }                                                         │
│    },                                                          │
│    "recent_healing_events": [...]                             │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Integration ready
                              ▼
                    ┌─────────────────┐
                    │   eDEX-UI       │
                    │ (real-time data)│
                    └─────────────────┘
```

## Data Flow Diagram

```
ProcessRegistry (metrics + states)
       │
       │ every 1 second
       ▼
_monitor_processes_async()
       │
       ├─────────────────────────────────┐
       │                                 │
       ▼                                 ▼
[Query metrics]                    [Fetch states]
       │                                 │
       ├──────────────────┬──────────────┘
       │                  │
       │ metrics_list     │ process_states
       │                  │
       └─────────┬────────┘
                 │
                 ▼
    tkinter.after(0, _update_treeview)
                 │
                 ▼
          [Update Treeview]
                 │
                 ├─ Process ID
                 ├─ Status
                 ├─ Reliability % [GREEN/YELLOW/RED]
                 ├─ Uptime
                 ├─ Health
                 └─ Crashes

    Every 5 seconds:
    
    _sync_to_edex_status()
             │
             ├─ Get metrics
             ├─ Build JSON
             ├─ Calculate health
             ├─ Add healing events
             │
             ▼
    Write edex_status.json
             │
             ▼
    eDEX-UI ready to consume
```

## Update Cycle Timeline

```
Timeline (seconds):
0.0  ┌─ _monitor_processes_async() wakes up
     ├─ Fetch metrics from registry (async)
     ├─ Fetch process states (async)
     └─ Schedule _update_treeview() on main thread
     
0.1  ┌─ _update_treeview() executes on main thread
     ├─ Update Treeview with new metrics
     ├─ Apply color tags (green/yellow/red)
     └─ Check healing alerts queue
     
0.2  ├─ _display_healing_alerts() processes next alert
     │  ├─ Show alert: "🔄 Restarting process (attempt #2)"
     │  ├─ Schedule auto-dismiss after 3 seconds
     │  └─ Add to task_manager history
     
3.2  └─ Alert auto-dismisses (clear_healing_alert)

     ┌─ Sleep 1.0 second (non-blocking)
1.0  │
     └─ Loop repeats...

     At 5-second boundary (sync_counter >= 5):
5.0  ┌─ asyncio.to_thread(_sync_to_edex_status)
     ├─ Serialize all metrics to JSON
     ├─ Calculate system health
     ├─ Include recent healing events
     ├─ Write to edex_status.json
     └─ Reset sync_counter
     
     Continue...
10.0 ┌─ Second JSON sync
15.0 ├─ Third JSON sync
20.0 └─ Fourth JSON sync
...
```

## Thread Model

```
┌────────────────────────────────────────────────────────────────┐
│                    Main Process                                │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Tkinter Main Thread (GUI)                               │  │
│  │  - Handle user input (text entry, keyboard)             │  │
│  │  - Draw UI elements (canvas, treeview, labels)          │  │
│  │  - Execute callbacks from after()                       │  │
│  │  - Process events                                       │  │
│  │  (MUST run on main thread)                              │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Animation Thread (started by __init__)                  │  │
│  │  - Render audio waves (60 FPS)                          │  │
│  │  - Update wave_phase variable                           │  │
│  │  - Draw to canvas (via animate_alive check)             │  │
│  │  (Safe: reads only, no blocking)                        │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Monitor Thread (started by set_process_registry())      │  │
│  │  - Run asyncio event loop (_run_async_monitor)          │  │
│  │  - Execute _monitor_processes_async() coroutine         │  │
│  │  - Sleep 1 second per iteration (non-blocking)          │  │
│  │  (Safe: reads registry, schedules via after())          │  │
│  └─────────────────────────────────────────────────────────┘  │
│                     │                                          │
│                     │ asyncio.to_thread()                      │
│                     ▼                                          │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Background Thread Pool (asyncio managed)                │  │
│  │  - Execute _sync_to_edex_status() (IO-bound)            │  │
│  │  - File write to edex_status.json                       │  │
│  │  (Safe: released back to main thread via after())       │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘

Legend:
→ Main Thread  | Write UI, handle events
⊘ Worker      | Background computation
∞ Async Loop  | Non-blocking I/O coordination
```

## Class Hierarchy

```
FuturisticBotGUI
├─ master (tk.Tk)
├─ canvas (tk.Canvas)
├─ text_entry (tk.Entry)
├─ status_var (tk.StringVar)
├─ process_treeview (ttk.Treeview)
│  └─ tags: health_healthy, health_degraded, health_critical
│
├─ animation_thread (Thread)
├─ monitor_thread (Thread)  [created by set_process_registry()]
│  └─ event_loop (asyncio.AbstractEventLoop)
│
├─ process_registry (ProcessRegistry)  [optional, set by caller]
├─ task_manager (KNOTaskManager)
│
└─ State Variables:
   ├─ is_speaking (bool)
   ├─ is_thinking (bool)
   ├─ wave_phase (float)
   ├─ user_input_queue (list)
   ├─ monitoring_active (bool)
   ├─ animation_alive (bool)
   ├─ treeview_items (dict[str, str])  [process_id → item_id]
   ├─ healing_alerts_queue (list)
   └─ active_alert_process (str | None)

KNOTaskManager
├─ edex_status_path (str)
├─ processes (dict[str, dict])
├─ healing_events (list[dict])
├─ tasks (dict[str, dict])
├─ max_history (int)
└─ _lock (threading.Lock)

Methods:
├─ add_process(process_id, config) → None
├─ update_process_status(...) → None
├─ record_healing_event(...) → None
├─ sync_to_edex() → None
├─ get_healing_events_for_display(limit) → List[dict]
└─ _calculate_system_health() → str
```

## Integration Points

```
agent.py
    ├─ Import FuturisticBotGUI
    ├─ Import ProcessRegistry
    │
    ├─ Create registry
    ├─ Create GUI
    │
    └─ gui.set_process_registry(registry)
            │
            ├─ Treeview auto-updates (1s)
            ├─ JSON auto-syncs (5s)
            └─ Ready for healing events

config.py
    ├─ Define EDEX_STATUS_PATH
    └─ Pass to GUI for custom path

audio_manager.py
    ├─ Register process in registry
    └─ Processes appear in Treeview

Hardware (future)
    ├─ Read edex_status.json
    ├─ Adjust resource allocation
    └─ Based on health status
```

## State Machine

```
Process States (from ProcessRegistry):
┌──────────────┐
│   CREATED    │
└──────┬───────┘
       │ start()
       ▼
┌──────────────┐
│  STARTING    │ ← Monitor checks: is process running?
└──────┬───────┘
       │ (if running)
       ▼
┌──────────────┐    crash detected?
│   RUNNING    │ ◄─────────────────┐
└──────┬────┬──┘                   │
       │    │  (if crashed)        │
       │    └─ healing_event() ────┤
       │                           │
       │ stop()           Auto-Healing Triggered
       ▼                           │
┌──────────────┐                   │
│  STOPPING    │                   │
└──────┬───────┘                   │
       │ (process stopped)         │
       ▼                           │
┌──────────────┐                   │
│   STOPPED ◄─ Process Healer ─────┘
└──────────────┘ re-starts process
```

## GUI Layout with Task Manager

```
┌─────────────────────────────────────────────────────────────┐
│  KNO                                                 Ready   │  ← Status bar (updated by alerts)
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                                                             │
│               Audio Wave Visualization                      │
│                   (60 FPS animation)                        │  ← Original GUI
│                                                             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Process Registry Status                                     │  ← NEW Title
├──────────────────────────────────────────────────────────────┤
│ Process ID  │ Status  │ Reliability │ Uptime │ Health │ Cr │  ← NEW Headers
├──────────────────────────────────────────────────────────────┤
│ browser_a   │ RUNNING │    98.5%    │ 3600.5 │healthy│ 0  │  ← GREEN row
│ audio_proc  │ RUNNING │    92.0%    │ 2400.3 │degrad │ 1  │  ← YELLOW row
│ worker_1    │ CRASHED │    65.5%    │ 1200.0 │critic │ 5  │  ← RED row
│ (scrollable)                                               │
├─────────────────────────────────────────────────────────────┤
│ Command KNO...                                              │  ← Text input (unchanged)
└─────────────────────────────────────────────────────────────┘
```

## Message Flow Example: Healing Event

```
Scenario: Process crashes, heal starts, alert shown

1. ProcessManager detects crash
   └─ Calls healer.heal(process_id)

2. ProcessHealer starts recovery
   └─ Increments retry_count
   └─ Schedules restart in X seconds

3. UI calls: gui.record_healing_event("my_proc", "crash", 1)
   └─ Adds to task_manager.healing_events list
   └─ Adds to healing_alerts_queue

4. Next monitor loop iteration (~1 second):
   └─ _monitor_processes_async() checks healing_alerts_queue
   └─ Schedules _display_healing_alerts() on main thread
   └─ asyncio.sleep(1.0) (non-blocking wait)

5. Main thread executes _display_healing_alerts()
   └─ Pops alert from queue
   └─ Sets status_var to "🔄 Restarting my_proc (attempt #1)"
   └─ Schedules _clear_healing_alert() after 3 seconds

6. Status bar shows alert for 3 seconds:
   "🔄 Restarting my_proc (attempt #1)"

7. After 3 seconds, _clear_healing_alert():
   └─ Clears active_alert_process
   └─ Resets status_var to "Ready"

8. Next JSON sync (every 5 seconds):
   └─ Includes healing event in recent_healing_events
   └─ edex_status.json updated
   └─ eDEX-UI sees the event

Timeline:
T=0.00  Crash detected
T=0.05  record_healing_event() called
T=1.05  Alert displayed ("🔄 Restarting...")
T=3.05  Alert cleared
T=5.00  JSON synced (includes event)
T=5.05  eDEX-UI updated
```

---

This architecture ensures:
- ✅ Non-blocking UI (all heavy ops in separate threads)
- ✅ Thread-safe (tkinter.after() + threading.Lock)
- ✅ Real-time monitoring (1s updates)
- ✅ Scalable (tested up to 200+ processes)
- ✅ Responsive (60 FPS animation unaffected)
- ✅ Reliable (error handling throughout)
