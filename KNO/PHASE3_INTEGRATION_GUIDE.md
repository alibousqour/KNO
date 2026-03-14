# PHASE 3: SELF-EVOLUTION ARCHITECTURE - INTEGRATION GUIDE

**Comprehensive Integration & Feature Activation Manual**

---

## 📋 Table of Contents

1. [Quick Reference](#quick-reference)
2. [Module Locations](#module-locations)
3. [Integration Flow Diagrams](#integration-flow-diagrams)
4. [Feature Activation Guide](#feature-activation-guide)
5. [Console Output Reference](#console-output-reference)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Configuration](#advanced-configuration)

---

## 🚀 Quick Reference

### All 6 Modules at a Glance

| Module | Purpose | Key Feature | Console Prefix |
|--------|---------|------------|-----------------|
| **ResourceDownloader** | Auto-fetch GGUF models | Downloads from Hugging Face | `[DOWNLOADER]` |
| **ExperienceMemory** | Error tracking & learning | Logs patterns to experience.json | `[EXPERIENCE]` |
| **InternetLearningBridge** | Web search for unknowns | DuckDuckGo queries | `[BRIDGE]` |
| **SelfCorrection** | Auto-fix errors | Detects missing libraries | `[CORRECTION]` |
| **EvolutionaryLogic** | Pattern analysis | Suggests improvements | `[EVOLUTION]` |
| **StateBackup** | Safety mechanism | Timestamped backups | `[BACKUP]` |

---

## 📍 Module Locations in agent.py

### **Lines 433-545: ResourceDownloader**
```python
# Auto-downloads GGUF models from Hugging Face
# Methods:
#   - download_model(url, path, name, max_retries=3)
#   - auto_download_model() → path or None

# Fallback models in priority order:
# 1. gemma-2b-it (1600MB)
# 2. tinyllama-1.1b (700MB)  
# 3. phi-2-mini (1600MB)
```

**Triggered By**: `LlamaConnector.verify_and_setup_model()` at line 2766  
**Data Created**: GGUF file in `./models/` directory

---

### **Lines 547-650: ExperienceMemory**
```python
# Persistent error memory system
# Methods:
#   - load() / save() ← interact with experience.json
#   - log_error(type, message, context)
#   - get_pattern(error_type) → count
#   - learn_solution(error_type, solution)

# Persists to: experience.json
```

**Triggered By**: Error handling in `chat_and_respond()` at line 4495  
**Data Created**: `./experience.json` on first error

---

### **Lines 652-730: InternetLearningBridge**
```python
# Web search & external AI integration point
# Methods:
#   - search_web_for_solution(query, max_results=3)
#   - query_external_ai(prompt, api_choice="duckduckgo")

# Uses: DuckDuckGo search (no API key required)
# Future: ChatGPT/Gemini support via API keys
```

**Trigger Points**: 
- Unknown commands during chat
- Error research phase in SelfCorrection

**Data Created**: None (cache only in memory)

---

### **Lines 732-850: SelfCorrection**
```python
# Autonomous error detection & recovery
# Methods:
#   - detect_missing_library(error_message) → lib_name
#   - auto_install_dependency(package_name) → bool
#   - handle_adb_pairing_failure(retry_count=3) → bool

# Pattern detection via regex:
# - ModuleNotFoundError: ...
# - ImportError: ...
# - cannot import name: ...
```

**Triggered By**: Experience memory detection of repeated errors (≥2 occurrences)  
**Subprocess Calls**: `pip install <package>` with 60s timeout  
**Data Created**: correction_history list in memory

---

### **Lines 852-930: EvolutionaryLogic**
```python
# Self-analysis and improvement suggestions
# Methods:
#   - analyze_regex_patterns(name, test_cases)
#   - suggest_improvement(component, issue, fix)
#   - track_success_rate(task_name, success)

# Metrics tracked:
# - task_success_rate (float percentage)
# - regex_patterns_tested (list)
# - improvements_suggested (list)
```

**Triggered By**: Brain loop analysis every 5 cycles (~5 minutes)  
**Data Created**: None persistent yet (future: evolution.json)

---

### **Lines 932-1015: StateBackup**
```python
# Safety mechanism for self-modifications
# Methods:
#   - create_backup(filename="agent.py") → path
#   - restore_from_backup(backup_path, target) → bool
#   - list_backups() → list

# Backup directory: kno_backups/
# Format: agent_backup_YYYYMMDD_HHMMSS.py
```

**Triggered By**: Before any self-modifying code changes  
**Data Created**: `./kno_backups/agent_backup_*.py` files

---

### **Lines 1729-1749: Global Instances**
```python
# Module-level instantiation (available everywhere)
resource_downloader = ResourceDownloader()
experience_memory = ExperienceMemory()
internet_bridge = InternetLearningBridge()
self_correction = SelfCorrection()
evolution_logic = EvolutionaryLogic()
state_backup = StateBackup()
```

**Initialization**: Called once at module import  
**Scope**: Global (accessible from all methods)

---

## 🔄 Integration Flow Diagrams

### **Flow 1: Agent Startup and Model Loading**
```
┌─────────────────────────────────────┐
│   agent.py loaded                   │
│   Module instances created (lines   │
│   1729-1749)                        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│   LlamaConnector.verify_and_        │
│   setup_model() [line 2766]         │
└────────────┬────────────────────────┘
             │
      ┌──────┴──────┐
      ▼             ▼
   Found    Not Found
  Primary     │
      ✅      ▼
         Check for
         Fallback
             │
         ┌───┴───┐
         ▼       ▼
       Found   Not Found
         ✅       │
                  ▼
            [DOWNLOADER]
            ResourceDownloader
            .auto_download_model()
                  │
              ┌───┴───┐
              ▼       ▼
           Success Failed
            ✅      ❌
        (return)  (return None)
                  GUI: "⚠️ Error: 
                   Brain File 
                   Missing"
```

### **Flow 2: Error Detection and Recovery**
```
┌──────────────────────────────┐
│ Error occurs in chat_and_    │
│ respond() [line 4495]        │
└──────────────┬───────────────┘
               │
               ▼
       [EXPERIENCE]
    experience_memory
    .log_error(...)
               │
               ▼
      Get error count:
      experience_memory
      .get_pattern(...)
               │
          ┌────┴─────┐
          ▼          ▼
       Count=1    Count≥2
         ✅      (repeat!)
              │
              ▼
      [CORRECTION]
   self_correction.
   detect_missing_
   library(error)
              │
          ┌───┴────┐
          ▼        ▼
       Found    Not Found
        Lib      │
         │       ▼
         │    Log & Move On
         │
         ▼
    [CORRECTION]
 auto_install_
 dependency()
         │
      ┌──┴──┐
      ▼    ▼
   Success Timeout
    ✅     ❌
```

### **Flow 3: Brain Loop Analysis and Evolution**
```
Autonomous Brain Loop [line 3813]
        │ Every 60s
        ▼
┌─────────────────────┐
│ Cycle N             │
│ - Check health      │
│ - Monitor tasks     │
│ - Track metrics     │
└────────┬────────────┘
         │
    ┌────┴──────────────┐
    │ Cycle % 5 == 0?   │
    │ (every 5 min)     │
    └────┬────────────┐ │
    NO   │            │ YES
         │            ▼
         │    [EVOLUTION]
         │  evolution_logic.
         │  track_success_
         │     rate()
         │       │
         │       ▼
         │   Check error_log
         │   for patterns
         │   (≥3 repeats)
         │       │
         │       ▼
         │   If found:
         │   suggest_
         │   improvement()
         │
    ┌────┴────────────────┐
    ▼
Sleep 60s
```

---

## 🎯 Feature Activation Guide

### **Feature 1: Automatic Model Download**

**Trigger Condition**: No GGUF models found in `./models/` directory

**Sequence**:
1. Agent starts → `LlamaConnector.verify_and_setup_model()` called
2. Primary (gemma-3-1b.gguf) NOT found
3. Fallback search for any .gguf: NOT found
4. `ResourceDownloader.auto_download_model()` triggered
5. Downloads try in order: TinyLlama (700MB) → Gemma-2B (1600MB) → Phi-2 (1600MB)
6. First successful download used
7. Agent continues with downloaded model

**Console Output**:
```
[DOWNLOADER] 🚀 INITIATING AUTO-DOWNLOAD SEQUENCE
[DOWNLOADER] 🛰️  No local GGUF models found. Searching Hugging Face...
[DOWNLOADER] 🔄 Attempting tinyllama-1.1b...
[DOWNLOADER] ⬇️  Downloading tinyllama (Attempt 1/3)...
[DOWNLOADER] 25% - 175MB/700MB
[DOWNLOADER] 50% - 350MB/700MB
[DOWNLOADER] 75% - 525MB/700MB
[DOWNLOADER] ✅ Successfully downloaded: models/tinyllama-1.1b.Q4_K_M.gguf
```

**How to Test**:
```bash
# Backup your models
mv ./models ./models_backup

# Start agent
python agent.py

# Watch for [DOWNLOADER] messages
# After download, verify:
ls -lh ./models/*.gguf
```

---

### **Feature 2: Experience Memory & Error Tracking**

**Trigger Condition**: Any exception in chat_and_respond()

**Sequence**:
1. Error occurs → caught in except block (line 4495)
2. `experience_memory.log_error()` called
3. Error added to experience.json
4. If count ≥ 2 → self_correction activates
5. If missing library detected → auto pip install

**Console Output**:
```
[LLAMA ERROR] Error during chat: No module named 'foobar'
[EXPERIENCE] 📝 New error logged: llama_chat_error
[EXPERIENCE] 📝 Error llama_chat_error logged (occurrence #2)
[SELF-CORRECTION] ⚠️  Repeated error detected (2 occurrences).
[SELF-CORRECTION] 📦 Detected missing library: foobar
[CORRECTION] 📦 Attempting to auto-install: foobar
[CORRECTION] ✅ Successfully installed: foobar
```

**Data Files Created**:
```json
// experience.json
{
  "errors_encountered": 2,
  "error_log": [
    {
      "type": "llama_chat_error",
      "message": "No module named 'foobar'",
      "count": 2,
      "timestamp": "2026-02-16T14:30:45"
    }
  ],
  "solutions_learned": [
    {
      "error_type": "llama_chat_error",
      "solution": "Installed foobar via pip"
    }
  ]
}
```

**How to Test**:
```bash
# Force an error (e.g., make chat_and_respond crash)
# Run agent and trigger error twice
# Check console for [EXPERIENCE] messages
# Verify experience.json created:
cat experience.json

# Trigger same error again (3rd time)
# Should NOT see auto-install (only on repeated ≥2)
```

---

### **Feature 3: Internet Learning Bridge**

**Trigger Conditions**:
1. Unknown command that doesn't match any action handlers
2. Error research needed by self_correction.SelfCorrection

**Sequence**:
1. User says something not recognized
2. `internet_bridge.search_web_for_solution()` called
3. DuckDuckGo search executed with query
4. Top result returned to user
5. Response played via TTS

**Console Output**:
```
[BRIDGE] 🌐 Searching web for: how to fix USB connection issue
[BRIDGE] ✅ Found 3 results
[BRIDGE] 📍 Top result: From USB Support: Troubleshooting USB connection...

[BRIDGE] ℹ️  Using DuckDuckGo web search (no API key required)
```

**How to Test**:
```bash
# Start agent
python agent.py

# Ask an unknown command:
# "What is quantum entanglement?"
# or "Tell me about machine learning"

# Watch for [BRIDGE] messages
# Agent will search web and read result
```

---

### **Feature 4: Self-Correction & Auto-Install**

**Trigger Condition**: Error repeats ≥2 times AND pattern matched by regex

**Patterns Detected**:
- `ModuleNotFoundError: No module named 'X'`
- `ImportError: No module named 'X'`
- `cannot import name 'X'`

**Sequence**:
1. First error: logged to experience_memory
2. Second same error: experience count = 2
3. `self_correction.detect_missing_library()` called
4. Pattern matched → library name extracted
5. `self_correction.auto_install_dependency()` runs pip
6. Success → agent continues
7. Failure → logged but doesn't block

**Console Output**:
```
[CORRECTION] 📦 Attempting to auto-install: requests
[CORRECTION] ✅ Successfully installed: requests
```

**How to Test**:
```bash
# Simulate missing library by editing imports temporarily
# or manually breaking an import statement
# Trigger error twice via chat
# Should see [CORRECTION] auto-install messages
```

---

### **Feature 5: Evolutionary Logic & Suggestions**

**Trigger Condition**: Brain loop runs 5 cycles (~5 minutes)

**Sequence**:
1. Brain loop ticks every 60s
2. Every 5 cycles (cycle % 5 == 0)
3. Check error_log for patterns
4. If any error count ≥ 3 → suggest_improvement()
5. Suggestion logged with timestamp
6. Displayed on console

**Console Output**:
```
[BRAIN] 🔍 Experience analysis: 12 total errors logged
[BRAIN] ⚠️  Recurring error detected: llama_chat_error (3 times)
[EVOLUTION] 💡 Improvement suggested for llama_chat_error
[EVOLUTION] 📝 Issue: Error occurs repeatedly (3 times)
[EVOLUTION] 💡 Fix: Review and optimize error handling for llama_chat_error
```

**How to Test**:
```bash
# Let agent run for 5+ minutes
# Force the same error 3+ times
# Watch brain loop debug output
# Should see [EVOLUTION] suggestions after 5 minutes
```

---

### **Feature 6: State Backup & Restore**

**Trigger Condition**: Before any self-modifying code

**Backup Format**:
- Directory: `./kno_backups/`
- Filename: `agent_backup_YYYYMMDD_HHMMSS.py`
- Example: `agent_backup_20260216_143000.py`

**Methods**:
```python
# Create backup:
backup_path = state_backup.create_backup("agent.py")
# → ./kno_backups/agent_backup_20260216_143000.py

# List backups:
backups = state_backup.list_backups()

# Restore:
state_backup.restore_from_backup(backup_path, "agent.py")
```

**Console Output**:
```
[BACKUP] 💾 Backup created: kno_backups/agent_backup_20260216_143000.py
[BACKUP] 📋 Available backups (3):
[BACKUP]   - agent_backup_20260216_140000.py
[BACKUP]   - agent_backup_20260216_141000.py
[BACKUP]   - agent_backup_20260216_142000.py
```

**How to Test**:
```bash
# Manually call in KNO console:
from agent import state_backup
state_backup.create_backup("agent.py")

# List backups:
state_backup.list_backups()

# Restore:
state_backup.restore_from_backup(
    "kno_backups/agent_backup_20260216_143000.py",
    "agent.py"
)
```

---

## 📊 Console Output Reference

### **All 6 Console Prefixes**

| Prefix | Module | Meaning | Example |
|--------|--------|---------|---------|
| `[DOWNLOADER]` | ResourceDownloader | Model download progress | `[DOWNLOADER] ⬇️  Downloading gemma-2b...` |
| `[EXPERIENCE]` | ExperienceMemory | Error logged to memory | `[EXPERIENCE] 📝 New error logged: llama_chat_error` |
| `[BRIDGE]` | InternetLearningBridge | Web search in progress | `[BRIDGE] 🌐 Searching web for: X` |
| `[CORRECTION]` | SelfCorrection | Auto-fix in progress | `[CORRECTION] ✅ Successfully installed: X` |
| `[EVOLUTION]` | EvolutionaryLogic | Improvement suggestion | `[EVOLUTION] 💡 Improvement suggested for X` |
| `[BACKUP]` | StateBackup | State saved/restored | `[BACKUP] 💾 Backup created: kno_backups/...` |

### **Symbol Legend**
- 🚀 = Initialization/Start
- ⬇️ = Download
- ✅ = Success
- ❌ = Failure
- ⚠️ = Warning
- 🔍 = Searching
- 📝 = Logging
- 💡 = Suggestion
- 💾 = Backup

---

## 🔧 Troubleshooting

### **Issue 1: Download Fails - "No such file or directory: models/"**

**Cause**: Models directory doesn't exist  
**Fix**: The code creates it automatically with `Path(models_dir).mkdir(parents=True, exist_ok=True)`  
**Manual Fix**:
```bash
mkdir -p models
python agent.py
```

---

### **Issue 2: Auto-Install Fails - "pip: command not found"**

**Cause**: pip not in PATH or Python not configured  
**Symptom**: `[CORRECTION] ❌ Failed to install ...`  
**Fix**:
```bash
# Verify pip available:
pip --version

# Or use python -m pip:
python -m pip install <package>
```

---

### **Issue 3: experience.json Not Creating**

**Cause**: No errors yet or permission issue  
**Expected**: Creates on first error  
**Test**:
```bash
# Force error in console:
python agent.py
# Say something that crashes
# Check: ls -la experience.json
```

---

### **Issue 4: Download Hangs/Timeout - Model Takes Forever**

**Cause**: Large model (Gemma-2B ~1.6GB) or slow internet  
**Timeout**: 300 seconds per attempt, 3 retries  
**Solution**:
```bash
# Let it retry (exponential backoff)
# Or manually download and put in ./models/
wget -O models/gemma-2b-it.Q4_K_M.gguf \
  https://huggingface.co/.../gemma-2b-it.Q4_K_M.gguf
```

---

### **Issue 5: kno_backups/ Permission Denied**

**Cause**: Write permission issue  
**Fix**:
```bash
# Change permissions:
chmod 755 kno_backups/

# Or create manually:
mkdir -p kno_backups
python agent.py
```

---

## ⚙️ Advanced Configuration

### **Customize Fallback Models**

Edit lines 440-456 in agent.py:
```python
FALLBACK_MODELS = [
    {
        "name": "your-model-name",
        "url": "https://huggingface.co/.../your-model.gguf",
        "size_mb": 2048,
        "description": "Your model description"
    },
    # ... add more
]
```

---

### **Change Error Count Threshold for Auto-Fix**

Current: Auto-fix triggers at 2+ occurrences  
Edit line 4503 in agent.py:
```python
if error_count >= 2:  # Change 2 to whatever threshold you want
    # Auto-fix logic
```

---

### **Configure Brain Loop Analysis Frequency**

Current: Every 5 cycles (5 minutes)  
Edit line 3868 in autonomous_brain_loop():
```python
if cycle_count % 5 == 0:  # Change 5 to any interval
    # Perform 5-minute analysis
```

---

### **Enable API-Based External AI (Future)**

InternetLearningBridge supports extension:
```python
# In query_external_ai(), add:
if api_choice == "gemini":
    # Call Gemini API (requires GEMINI_API_KEY env var)
    
elif api_choice == "chatgpt":
    # Call ChatGPT API (requires OPENAI_API_KEY env var)
```

---

### **Backup Directory Location**

Default: `./kno_backups/`  
Edit line 1019 in StateBackup:
```python
BACKUP_DIR = "kno_backups"  # Change to any path
```

---

## 📚 Module API Quick Reference

### **ResourceDownloader**
```python
ResourceDownloader.auto_download_model() → str (path) or None
ResourceDownloader.download_model(url, dest, name, max_retries=3) → str or None
```

### **ExperienceMemory**
```python
experience_memory.log_error(type, message, context)
experience_memory.get_pattern(error_type) → int (count)
experience_memory.learn_solution(error_type, solution)
```

### **InternetLearningBridge**
```python
internet_bridge.search_web_for_solution(query, max_results=3) → list
internet_bridge.query_external_ai(prompt, api_choice="duckduckgo") → str or None
```

### **SelfCorrection**
```python
self_correction.detect_missing_library(error_message) → str or None
self_correction.auto_install_dependency(package_name) → bool
self_correction.handle_adb_pairing_failure(retry_count=3) → bool
```

### **EvolutionaryLogic**
```python
evolution_logic.analyze_regex_patterns(name, test_cases) → dict
evolution_logic.suggest_improvement(component, issue, fix)
evolution_logic.track_success_rate(task_name, success)
```

### **StateBackup**
```python
state_backup.create_backup(filename="agent.py") → str (path) or None
state_backup.restore_from_backup(backup_path, target) → bool
state_backup.list_backups() → list
```

---

## ✅ Implementation Verification Checklist

- [ ] Install agent.py and run `python agent.py`
- [ ] No syntax errors in console
- [ ] Models directory created if missing
- [ ] Global instances initialized
- [ ] If no models: [DOWNLOADER] messages appear
- [ ] Generate first error: [EXPERIENCE] message appears
- [ ] Generate same error twice: [CORRECTION] message appears
- [ ] Wait 5 minutes for brain loop analysis: [EVOLUTION] message appears
- [ ] Check files exist: `experience.json`, `kno_backups/`
- [ ] All 6 console prefixes working

---

## 🎉 Summary

Phase 3 Integration is complete with:
- ✅ 6 autonomous modules fully integrated
- ✅ 4 trigger points in existing code
- ✅ 3 persistent data systems
- ✅ 6 unique console prefixes
- ✅ Comprehensive error handling
- ✅ Self-healing capabilities
- ✅ Experience-driven learning
- ✅ Internet-augmented intelligence

**KNO is now a fully autonomous, self-learning agent! 🚀**

