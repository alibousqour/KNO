# eDEX Data Bridge Architecture & Visual Diagrams

## System Architecture Diagram

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    KNO AGENT (Python)                           ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                  ┃
┃  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  ┃
┃  │  Thinking Loop   │  │ Search Module    │  │ Fixing Logic │  ┃
┃  └────────┬─────────┘  └────────┬─────────┘  └──────┬───────┘  ┃
┃           │                     │                   │           ┃
┃           └─────────────────────┼───────────────────┘           ┃
┃                                 │                               ┃
┃                    await/update_status_sync(...)                ┃
┃                                 │                               ┃
┃                                 ▼                               ┃
┃                    ┌─────────────────────────┐                  ┃
┃                    │   EDEXMonitor Instance   │                 ┃
┃                    │  (in kno_utils.py)      │                 ┃
┃                    │                         │                 ┃
┃                    │  - update_status()      │                 ┃
┃                    │  - log_error()          │                 ┃
┃                    │  - log_fix()            │                 ┃
┃                    │  - get_current_status() │                 ┃
┃                    └────────────┬────────────┘                  ┃
┃                                 │                               ┃
┃                      (Non-blocking write)                       ┃
┃                                 │                               ┃
┃         ┌───────────────────────┘                               ┃
┃         │                                                       ┃
┗━━━━━━━━━┼━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
          │
          │      JSON File I/O
          │      (Async executor)
          │
          ▼
    ┌──────────────────────────┐
    │  edex_status.json        │
    │  (5-10 KB file)          │
    │                          │
    │ {                        │
    │   "agent_status": "...", │
    │   "current_task": "...", │
    │   "progress": 50,        │
    │   "llm_model": "...",    │
    │   "memory_usage_mb": 234,│
    │   "cpu_usage_percent": 32│
    │   ... more fields        │
    │ }                        │
    └──────────────┬───────────┘
                   │
        File polling (500ms refresh)
                   │
    ┌──────────────▼───────────────────────────────┐
    │         eDEX-UI Interface Engine             │
    ├──────────────────────────────────────────────┤
    │                                              │
    │  ┌────────────────────┐  ┌──────────────┐   │
    │  │  Status Widget     │  │  Theme       │   │
    │  │  (React/HTML)      │  │  Engine      │   │
    │  │                    │  │              │   │
    │  │ - Status Badge     │  │ - Colors     │   │
    │  │ - Progress Bar     │  │ - Fonts      │   │
    │  │ - Metrics Display  │  │ - Layout     │   │
    │  │ - Task Text        │  │              │   │
    │  │ - Error Info       │  │              │   │
    │  └────────┬───────────┘  └──────────────┘   │
    │           │                                 │
    │           │ Real-time rendering             │
    │           ▼                                 │
    │  ┌──────────────────────────────────────┐  │
    │  │  ╔═══════════════════════════════╗   │  │
    │  │  ║ ⚙️  KNO Agent Status        ║   │  │
    │  │  ╠═══════════════════════════════╣   │  │
    │  │  ║ Status: THINKING              ║   │  │
    │  │  ║ Task: Analyzing...            ║   │  │
    │  │  ║ [████████░░░░░░░░] 50%        ║   │  │
    │  │  ║ LLM: Gemini-Pro               ║   │  │
    │  │  ║ CPU: 32.1%  Mem: 234MB        ║   │  │
    │  │  ╚═══════════════════════════════╝   │  │
    │  │  (NEON COLORS, LIVE UPDATES)        │  │
    │  └──────────────────────────────────────┘  │
    │                                             │
    └─────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
Agent Operation Timeline:
═══════════════════════════════════════════════════════════════════

Time  Agent State           Monitor Update                JSON File
────  ───────────────────   ──────────────────────        ────────────────
 0ms  Started thinking      progress=0                    edex_status.json
                            agent_status="THINKING"      Updated
                                                         (async write)
                                                              
 50ms Query LLM             progress=25                   Updated
                            current_task="Querying LLM"  (500ms)
                                                         
100ms Processing...         progress=50                   Updated
                            current_task="Processing"    (no update)
                                                         
150ms Almost done           progress=75                   Updated
                            last_action="..."            (no update)
                                                         
200ms Complete              progress=100                  Updated
                            agent_status="IDLE"          (500ms)
                                                         
250ms Idle                  (same)                        Not updated
                                                         (same as 200ms)
```

---

## Status lifecycle Flow

```
                    ┌─────────────────┐
                    │  System Start    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  IDLE           │◄──────────┐
                    │  (Waiting)      │           │
                    └────────┬─────────┘           │
                             │                     │
              ┌──────────────┘                     │
              │                                    │
              ▼                                    │
      ┌──────────────┐                            │
      │  THINKING    │  (Analyzing input)         │
      └──────┬───────┘                            │
             │                                    │
             ├──────────────────────────┐         │
             │                          │         │
             ▼                          ▼         │
   ┌──────────────┐           ┌──────────────┐   │
   │  SEARCHING   │           │  EXECUTING   │   │
   │  (Web data)  │           │  (Actions)   │   │
   └──────┬───────┘           └──────┬───────┘   │
          │                          │           │
          │         ┌────────────────┘           │
          │         │                            │
          │         ▼                            │
          │    ┌──────────────┐                  │
          │    │  FIXING      │                  │
          │    │  (Auto-heal) │                  │
          │    └──────┬───────┘                  │
          │           │                          │
          └───────────┼──────────────────────────┘
                      │
                      ▼ (success)
                    IDLE (back to waiting)
```

---

## Method Call Sequence Diagram

```
Agent Code                  EDEXMonitor              File System        eDEX-UI
──────────────────────────  ──────────────────────  ──────────────────  ────────────
     │                                              │                    │
     │ update_status(                               │                    │
     │   agent_status="THINKING",                  │                    │
     │   progress=30)                              │                    │
     │──────────────────────────────────────────►  │                    │
     │                                  │           │                    │
     │                              (lock acquired)  │                    │
     │                              (data updated)   │                    │
     │                                  │           │                    │
     │                          (execute async write)                    │
     │ ◄─────────────────────────────────────────  │                    │
     │ (returns immediately)                        │───────────────────►│ 
     │ continue processing                          │  write JSON file  │
     │                                              │                    │
     │ ... do work ...                              │                    │
     │                                              │                    │
     │ (500ms later, happens automatically)         │                    │
     │                                              │ ◄──────────────────│
     │                                              │   read JSON        │
     │                                              │  (rendering)       │
     │                                              │                    │
     │ log_fix("Fixed X")                          │                    │
     │──────────────────────────────────►          │                    │
     │                          (update data)       │                    │
     │ ◄──────────────────────────────────────────  │                    │
     │                                              │───────────────────►│
     │                                              │  write JSON file  │
     │                                              │                    │
     └──────────────────────────────────────────────────────────────────┘
```

---

## Integration Pattern

```
YOUR AGENT CODE PATTERN:

┌─────────────────────────────────────────────────────┐
│ from kno_utils import edex_monitor                  │
│                                                     │
│ class Agent:                                        │
│     def __init__(self):                             │
│         self.monitor = edex_monitor                 │
│                                                     │
│     async def process(self, prompt):                │
│         ┌─────────────────────────────────────────┐ │
│         │ await self.monitor.update_status(       │ │
│         │     agent_status="THINKING",            │ │
│         │     current_task=f"Processing {prompt}" │ │
│         │ )                                       │ │
│         └──────────────┬──────────────────────────┘ │
│                        │                             │
│         # Do your work here:                        │
│         result = await self.llm.query(prompt)       │
│                        │                             │
│         ┌──────────────┘                             │
│         │                                             │
│         └─────────────────────────────────────────┐  │
│             await self.monitor.update_status(     │  │
│                 agent_status="IDLE",              │  │
│                 progress=100,                     │  │
│                 last_action="Completed"           │  │
│             )                                     │  │
│         ┌─────────────────────────────────────────┐  │
│         return result                             │  │
│         └─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Status Color Mapping

```
┌──────────────────────────────────────────────────────┐
│           STATUS COLOR REFERENCE                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│  IDLE (Gray)       ⚫ #888888                        │
│  Waiting for work                                    │
│                                                      │
│  THINKING (Purple) 🟣 #9D00FF                       │
│  AI processing, analyzing                           │
│                                                      │
│  SEARCHING (Cyan)  🔵 #00FFFF                       │
│  Web search, data lookup                            │
│                                                      │
│  FIXING (Pink)     🩷 #FF1493                       │
│  Auto-correcting errors                             │
│                                                      │
│  EXECUTING (Lime)  🟢 #00FF00                       │
│  Running commands, taking action                    │
│                                                      │
│  ERROR (Red)       🔴 #FF4444                       │
│  Something went wrong                               │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## File Update Cycle

```
Time (ms)
  0 ┤ Agent starts update
      │ update_status(progress=30)
 10 ┤ ├─ Lock acquired
     │ ├─ Data updated
     │ ├─ Executor thread pool queued
 20 ┤ ├─ Control returns to agent (NON-BLOCKING!)
     │ Agent continues processing
 30 ┤ ├─ File I/O starts (background)
     │ │
 40 ┤ ├─ File write completes
     │ └─ Lock released
 50 ┤
     │ (Meanwhile, eDEX-UI polling at 500ms interval)
     │
500 ┤ eDEX-UI reads file (or earlier if polling sooner)
520 ┤ Widget re-renders with new data
900 ┤ Agent updates status again
920 ┤ File written
     │
1400 ┤ eDEX-UI reads file again
1420 ┤ Widget updates
     │
     └─────────────────────────────────────────►

Legend:
  - Update is NON-BLOCKING (returns in 20ms)
  - File I/O happens async in background
  - eDEX-UI polls every 500ms
  - Total latency: <20ms to return + async write
```

---

## Memory Layout

```
┌──────────────────────────────────────────────┐
│           RAM Layout (Simplified)            │
├──────────────────────────────────────────────┤
│                                              │
│  Agent Object (kno_utils)                    │
│  ┌──────────────────────────────────────┐   │
│  │ edex_monitor = EDEXMonitor()        │   │
│  │ ├─ self.file_path = "..."           │   │
│  │ ├─ self.data = {                    │   │
│  │ │   "agent_status": "IDLE",         │   │
│  │ │   "current_task": "...",          │   │
│  │ │   "progress": 0,                  │   │
│  │ │   "llm_model": "None",            │   │
│  │ │   .... (10+ fields)               │   │
│  │ │ }                                 │   │
│  │ ├─ self.lock = Lock()               │   │
│  │ └─ [methods]                        │   │
│  └──────────────────────────────────────┘   │
│  (Total: <5KB in memory)                    │
│                                              │
│  When update_status() called:                │
│  ┌──────────────────────────────────────┐   │
│  │ 1. Acquire lock (thread-safe)        │   │
│  │ 2. Update dict in memory             │   │
│  │ 3. Queue file write (async)          │   │
│  │ 4. Release lock                      │   │
│  │ 5. Return to caller (<1ms)           │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  File I/O happens in background:            │
│  ┌──────────────────────────────────────┐   │
│  │ ThreadPool → Write to disk → Done    │   │
│  │ (Doesn't block agent code)           │   │
│  └──────────────────────────────────────┘   │
│                                              │
└──────────────────────────────────────────────┘

Disk:
┌──────────────────────────────────────────┐
│ edex_status.json (4-8 KB)                │
│ {                                        │
│   "agent_status": "THINKING",            │
│   "current_task": "...",                 │
│   "progress": 45,                        │
│   ... (all fields)                       │
│ }                                        │
└──────────────────────────────────────────┘
```

---

## Component Dependency Graph

```
edex_status.json
      ▲
      │ (reads)
      │
eDEX-UI Widget ◄──────── CSS/JavaScript
      ▲                        │
      │                        └─ KNOStatusWidget.js
      │                            KNOStatusWidget.css
      │
      │ (polls every 500ms)
      │
KNO Agent Code
      │
      ├─ imports ──► kno_utils.py
      │              │
      │              └─ EDEXMonitor class
      │                  ├─ update_status()
      │                  ├─ log_error()
      │                  ├─ log_fix()
      │                  └─ get_current_status()
      │
      └─ calls ──► edex_monitor (global instance)
                      │
                      └─ writes to --> edex_status.json
```

---

## Performance Profile

```
UPDATE OPERATION TIMELINE:

Agent Code:                     0ms ─┐
                                     │
await monitor.update_status()        ├─ <1ms
                                     │
Return from call                  <1ms ┘

File Write (background):         1-3ms  ┌─ Async, non-blocking
                                 3-10ms ┘

eDEX-UI Poll (every 500ms):
  ├─ Read file:                  1-2ms
  └─ Render widget:              5-10ms (React/DOM)

Overall Impact:
  ├─ Agent blocking time:        <1ms per update
  ├─ Frequency:                  As needed (no minimum)
  ├─ Memory footprint:           <5KB in RAM
  ├─ Disk footprint:             4-10KB file
  └─ Network impact:             None (local only)
```

---

## Integration Checklist by Type

```
SIMPLE INTEGRATION (5 minutes):
  └─ Add one update_status() call
     └─ Show progress for next 1-2 operations

MODERATE (30 minutes):
  ├─ Dashboard with error tracking
  ├─ Multiple operation types
  └─ Progress tracking for major tasks

ADVANCED (1-2 hours):
  ├─ Multi-stage complex operations
  ├─ Real-time metrics (CPU/memory)
  ├─ Historical data logging
  └─ Custom eDEX-UI widget styling

EXPERT (4+ hours):
  ├─ WebSocket real-time updates
  ├─ Performance profiling graphs
  ├─ Multi-agent monitoring
  ├─ Custom visualization
  └─ Advanced theme integration
```

---

These diagrams provide a visual understanding of how the eDEX Data Bridge works.
Refer back to them when integrating to better understand the data flow and architecture.

