# 🧬 Self-Evolving Architecture - Developer Quick Reference

## Module Overview & API Reference

### 1. ResourceDownloader
**Location**: Lines 1449-1645  
**Purpose**: Auto-download missing GGUF models

```python
# Public API
ResourceDownloader.auto_download_model()
  → Returns filepath or None
  → Auto-tries models in priority order
  → Verifies GGUF integrity

# Example
model_path = ResourceDownloader.auto_download_model()
if model_path:
    print(f"Downloaded: {model_path}")
```

**Internal Methods**:
```python
ResourceDownloader.calculate_checksum(filepath, algorithm='md5')
  → Returns MD5 hash string

ResourceDownloader.verify_model_integrity(filepath)
  → Returns True/False

ResourceDownloader.download_and_verify_model(model_info, destination)
  → Returns filepath or None
  → Handles retries with exponential backoff

ResourceDownloader._clear_cache()
  → Clears temporary download files
  → Used for recovery
```

---

### 2. ExperienceManager
**Location**: Lines 1647-1722  
**Purpose**: Error logging, pattern detection, solution learning

```python
# Global instance
experience_manager = ExperienceManager()

# API
experience_manager.log_error(error_type, error_message, context="")
  → Logs to experience.json
  → Updates error_patterns count
  → Tracks timestamp & context

experience_manager.get_repeated_errors(threshold=2)
  → Returns dict of errors with count >= threshold
  → Useful for finding patterns

experience_manager.log_solution(error_type, solution)
  → Stores learned solution
  → Persists to experience.json

experience_manager.was_error_seen_before(error_type)
  → Returns (bool, pattern_dict)
  → Checks if similar error occurred
```

**Data Access**:
```python
# View all logged errors
errors = experience_manager.experiences["error_patterns"]

# View learned solutions
solutions = experience_manager.experiences["learned_solutions"]

# View total errors
total = experience_manager.experiences["total_errors"]
```

---

### 3. SelfCorrectionLayer
**Location**: Lines 1724-1790  
**Purpose**: Detect failures, research solutions, apply corrections

```python
# Global instance
self_correction_layer = SelfCorrectionLayer()

# API
self_correction_layer.detect_failure(component, error, context="")
  → Returns (needs_learning, research_required)
  → Logs to experience_manager
  → Checks if error pattern known

self_correction_layer.research_solution_online(error_type, component)
  → Returns list of solution dicts or None
  → Uses DuckDuckGo web search
  → Each result has: title, body, url

self_correction_layer.apply_correction(correction_action, parameters=None)
  → Returns True/False
  → Executes correction from corrections_map
  → Logs results
```

**Available Corrections**:
```python
corrections_map = {
    "restart_llama": LlamaConnector.reload_model,
    "reload_config": load_config,
    "restart_audio": audio_device_manager.scan_and_cache_devices,
    "clear_cache": ResourceDownloader._clear_cache,
}
```

---

### 4. KNO_Evolution
**Location**: Lines 1792-1920  
**Purpose**: Auto-improvement, dependency management, code optimization

```python
# Global instance
kno_evolution = KNO_Evolution()

# API
kno_evolution.create_restore_point(component_name)
  → Creates timestamped backup
  → Returns backup_filepath or None
  → Always do this before code changes!

kno_evolution.auto_install_dependency(package_name, pip_name=None)
  → Auto-runs: pip install package
  → Returns True/False
  → Logs to evolution.json

kno_evolution.detect_missing_imports(filepath)
  → Scans filepath for import statements
  → Tests if each module exists
  → Returns list of (import_name, pip_name) tuples

kno_evolution.optimize_regex_patterns()
  → Analyzes error patterns for regex issues
  → Generates optimization suggestions
  → Returns list of optimization dicts

kno_evolution.suggest_patch(component, improvement_suggestion)
  → Logs patch suggestion
  → Marks status as "suggested"
  → Persists to evolution.json
```

**Example Usage**:
```python
# Create restore point before changes
backup = kno_evolution.create_restore_point("agent")
assert backup, "Backup failed!"

# Install missing dependency
success = kno_evolution.auto_install_dependency("aiohttp")
if success:
    # Now import and use it
    import aiohttp
```

---

### 5. IdleOptimizer
**Location**: Lines 1922-2005  
**Purpose**: Background self-study during idle time

```python
# Global instance
idle_optimizer = IdleOptimizer()

# API
idle_optimizer.perform_self_study()
  → Analyzes error patterns
  → Suggests regex optimizations
  → Checks imports
  → Analyzes logs
  → No return value

idle_optimizer.should_perform_idle_optimization()
  → Returns True if optimization_interval has passed
  → Used to throttle self-study

idle_optimizer.start_idle_monitor_thread()
  → Starts background daemon thread
  → Monitors for 5+ min inactivity
  → Calls perform_self_study() periodically
  → Already called in BotGUI.__init__()
```

**Configuration**:
```python
idle_optimizer.optimization_interval = 3600  # 1 hour (in seconds)
idle_optimizer.last_optimization_time  # Last run timestamp
```

---

### 6. LlamaConnector (Enhancements)
**Location**: Lines 2111-2307  
**Purpose**: Direct GGUF loading with auto-download & reload

```python
# Enhanced methods
LlamaConnector.verify_and_setup_model()
  → Check primary model
  → Search for fallbacks
  → TRIGGER AUTO-DOWNLOAD if none found
  → Returns (model_path, is_fallback)

LlamaConnector.reload_model()
  → Unloads current instance
  → Reloads fresh copy
  → Used for error recovery
  → Returns True/False
  → Logs solution to experience_manager
```

**Example**:
```python
# At startup
model_path, is_fallback = LlamaConnector.verify_and_setup_model()
if is_fallback:
    print("Using fallback model")

# On error recovery
success = LlamaConnector.reload_model()
if not success:
    print("Reload failed, need manual intervention")
```

---

## Integration Points in agent.py

### BotGUI.__init__() Integrations

```python
# Line 1747: Model file check
if ResourceManager.MODEL_VERIFIED:
    print("Model ready")

# Line 2535: Start idle optimizer
idle_optimizer.start_idle_monitor_thread()

# Line 2274: Error logging in chat_and_respond()
experience_manager.log_error("llm", str(e), context)
```

### error Handling Pattern

```python
try:
    # Attempt operation
    result = risky_operation()
except Exception as e:
    # Log error
    experience_manager.log_error("component", str(e), "context")
    
    # Check if pattern
    needs_learning, research = self_correction_layer.detect_failure(
        "component", str(e), "context"
    )
    
    # If pattern, research & fix
    if research:
        solutions = self_correction_layer.research_solution_online(
            "component", str(e)
        )
        self_correction_layer.apply_correction("restart_component")
```

---

## File Structure

```
A:\KNO\KNO\
├── agent.py                         # Main file (+1200 lines)
├── experience.json                  # Error patterns & solutions
├── evolution.json                   # Code changes & patches
├── backups/                         # Restore points
│   ├── agent_backup_2026-02-16T14-30-45.py
│   └── agent_backup_2026-02-16T15-00-22.py
└── logs/                            # Historical logs for analysis
```

---

## Key Constants & Flags

```python
# ResourceManager flags (set by verify_and_setup_model)
ResourceManager.MODEL_VERIFIED       # bool: Model found?
ResourceManager.MODEL_PATH           # str: Path to model file
ResourceManager.MODEL_IS_FALLBACK    # bool: Using fallback?

# Evolution file
EVOLUTION_LOG = "evolution.json"
BACKUP_DIR = "backups"

# Experience file
EXPERIENCE_FILE = "experience.json"

# Idle timing
optimization_interval = 3600         # seconds (1 hour)
idle_threshold = 300                 # seconds (5 minutes)
```

---

## Extending the System

### Add a New Correction Action

```python
# In SelfCorrectionLayer.apply_correction()
corrections_map = {
    # ... existing corrections ...
    "my_new_action": my_correction_function,
}

# Define the function
def my_correction_function():
    print("[CORRECTION] Executing my fix...")
    # Do something
    return True
```

### Add a New Self-Study Analysis

```python
# In IdleOptimizer.perform_self_study()
def perform_self_study(self):
    print(f"[IDLE] 📚 Starting self-study session...")
    
    # Existing analyses...
    repeated_errors = experience_manager.get_repeated_errors()
    
    # NEW: Your custom analysis
    my_analysis_results = self.analyze_custom_metric()
    if my_analysis_results:
        print(f"[IDLE] 🔍 Custom analysis: {my_analysis_results}")
```

### Add a New Error Pattern Detector

```python
# In ExperienceManager.log_error()
def log_error(self, error_type, error_message, context=""):
    # Existing code...
    
    # NEW: Custom detection
    if "timeout" in error_message.lower():
        self.experiences["error_patterns"][error_key]["category"] = "performance"
    elif "connection" in error_message.lower():
        self.experiences["error_patterns"][error_key]["category"] = "network"
```

---

## Debugging Tips

### Check if Auto-Download Triggered
```python
# Look for in logs
grep "AUTO-DOWNLOAD" output.log
grep "DOWNLOADER" output.log
```

### View Current Error Patterns
```python
import json
with open("experience.json") as f:
    data = json.load(f)
    for error, info in data["error_patterns"].items():
        print(f"{error}: {info['count']} times")
```

### Manually Trigger Self-Study
```python
# In Python REPL or test script
from agent import idle_optimizer
idle_optimizer.perform_self_study()
```

### Check Restore Points
```bash
# PowerShell
ls backups/ | Sort-Object LastWriteTime -Descending

# Shows most recent backup first
```

---

## Performance Notes

- **Auto-Download**: 300 MB/min typical (internet dependent)
- **Model Reload**: 2-5 seconds (model size dependent)
- **Self-Study**: <500ms (local analysis only)
- **Error Logging**: <10ms (file I/O)

---

## Thread Safety

All global instances use:
- `threading.Lock()` for tts_queue
- JSON file reading/writing is atomic
- No race conditions expected

---

## Testing

```python
# Test auto-download
rm A:\KNO\KNO\models\*.gguf  # Delete all models
python agent.py  # Should auto-download

# Test error logging
experience_manager.log_error("test", "Test error", "Unit test")
# Check experience.json for new entry

# Test self-study
idle_optimizer.optimization_interval = 1  # Force immediate
time.sleep(310)  # Wait 5+ min idle
idle_optimizer.perform_self_study()  # Should run
```

---

## Common Tasks

### Get Error Statistics
```python
errors = experience_manager.get_repeated_errors(threshold=3)
print(f"Top recurring errors: {len(errors)}")
```

### Prevent Auto-Download
```python
# Just place a valid model in models/ before startup
# ResourceDownloader won't trigger if models exist
```

### Force Self-Study Now
```python
idle_optimizer.last_optimization_time = None
# Next idle check will run self-study
```

### Check Evolution Log
```python
with open("evolution.json") as f:
    data = json.load(f)
    print(f"Total adaptations: {data['total_adaptations']}")
    print(f"Restore points: {len(data['restore_points'])}")
```

---

*Quick Reference v1.0 - February 16, 2026*
