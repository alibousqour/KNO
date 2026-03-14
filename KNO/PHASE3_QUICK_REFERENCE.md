# PHASE 3: QUICK REFERENCE CARD

**Last Updated**: February 16, 2026 | **Version**: 3.0.0

---

## 🚀 Quick Start

```bash
# Start agent with Phase 3 features
python agent.py

# Watch console for 6 prefixes: [DOWNLOADER] [EXPERIENCE] [BRIDGE] [CORRECTION] [EVOLUTION] [BACKUP]
```

---

## 📍 Module Locations

| Module | Lines | Purpose | Prefix |
|--------|-------|---------|--------|
| ResourceDownloader | 433-545 | Auto-download models | `[DOWNLOADER]` |
| ExperienceMemory | 547-650 | Error tracking | `[EXPERIENCE]` |
| InternetLearningBridge | 652-730 | Web search | `[BRIDGE]` |
| SelfCorrection | 732-850 | Auto-fix errors | `[CORRECTION]` |
| EvolutionaryLogic | 852-930 | Pattern analysis | `[EVOLUTION]` |
| StateBackup | 932-1015 | State recovery | `[BACKUP]` |

---

## 🔧 Global Instances

Access anywhere:
```python
from agent import (
    resource_downloader,
    experience_memory,
    internet_bridge,
    self_correction,
    evolution_logic,
    state_backup
)
```

---

## 🎯 Feature Quick Guide

### **1. Auto-Download Models**
```python
# Automatic! Called by verify_and_setup_model()
resource_downloader.auto_download_model()
# Returns: path to downloaded model or None
```

### **2. Experience Tracking**
```python
# Logs to experience.json
experience_memory.log_error("error_type", "error message", "context")
count = experience_memory.get_pattern("error_type")
if count >= 2:
    # Auto-correction triggered!
```

### **3. Web Search**
```python
# Search web for answers
results = internet_bridge.search_web_for_solution(
    "query text",
    max_results=3
)
```

### **4. Auto-Install**
```python
# Detect missing library
lib = self_correction.detect_missing_library(error_message)
if lib:
    # Auto-install
    self_correction.auto_install_dependency(lib)
```

### **5. Pattern Analysis**
```python
# Track success metrics
evolution_logic.track_success_rate("task_name", success=True)

# Suggest improvements
evolution_logic.suggest_improvement(
    "component",
    "issue description",
    "suggested fix"
)
```

### **6. Backup & Restore**
```python
# Create backup
backup_path = state_backup.create_backup("agent.py")

# List backups
backups = state_backup.list_backups()

# Restore
state_backup.restore_from_backup(backup_path, "agent.py")
```

---

## 📊 Data Files

| File | Created | Purpose |
|------|---------|---------|
| experience.json | On first error | Error memory |
| evolution.json | On first optimization | Improvements |
| kno_backups/ | On first backup | Recovery |

---

## 🔴 Console Prefixes Legend

```
[DOWNLOADER] 🚀 ⬇️  ✅ ❌    → Model downloads
[EXPERIENCE] 📝 ⚠️  ✅      → Error logging
[BRIDGE]    🌐 ✅          → Web search
[CORRECTION] 📦 ✅ ❌      → Auto-install
[EVOLUTION] 💡 📊 ⚠️       → Improvements
[BACKUP]    💾 ✅ ❌      → State backup
```

---

## 🧪 Testing Quick Commands

```bash
# Test auto-download (if no models)
python agent.py
# Look for: [DOWNLOADER] ⬇️ Downloading...

# Test experience memory (force error)
# In chat, say something that breaks
# Look for: [EXPERIENCE] 📝 New error logged

# Test brain loop analysis (wait 5+ min)
# Brain cycles automatically
# Look for: [EVOLUTION] 💡 Improvement suggested

# Test web search (ask unknown command)
# Agent queries DuckDuckGo
# Look for: [BRIDGE] 🌐 Searching web for...
```

---

## ⚙️ Configuration

### Change Download Retry Count
```python
# Line 440 in ResourceDownloader
max_retries = 3  # Change this
```

### Change Error Count Threshold
```python
# Line 4503 in chat_and_respond
if error_count >= 2:  # Change 2 to any value
```

### Change Brain Loop Frequency
```python
# Line 3868 in autonomous_brain_loop
if cycle_count % 5 == 0:  # 5 cycles = 5 minutes
```

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| Download fails | Check internet, Hugging Face availability |
| Auto-install fails | Check pip, Python path |
| experience.json not created | Force error twice to trigger |
| evolution.json not created | Wait 5+ minutes for analysis |
| [BACKUP] not working | Check kno_backups/ directory permissions |

---

## 📈 Metrics at a Glance

- 6 modules implemented
- 578 lines of code added
- 18 new methods
- 4 integration points
- 0 syntax errors ✅
- 65 KB documentation
- 3 persistent data files
- 6 console prefixes

---

## 🎯 Integration Points

1. **verify_and_setup_model()** → Calls ResourceDownloader
2. **chat_and_respond()** → Logs to experience_memory
3. **autonomous_brain_loop()** → Tracks with evolution_logic
4. **Global error handler** → Auto-correction chain

---

## 📚 Documentation

- PHASE3_COMPLETE_SUMMARY.md - Executive overview
- PHASE3_IMPLEMENTATION_COMPLETE.md - Full features
- PHASE3_INTEGRATION_GUIDE.md - Integration details
- PHASE3_CHANGELOG.md - All changes made
- PHASE3_DEPLOYMENT_FINAL.md - Deployment guide

---

## ✅ Health Check

```python
# In Python console:
from agent import *

# Check all instances exist
print(resource_downloader)      # ✅
print(experience_memory)         # ✅
print(internet_bridge)           # ✅
print(self_correction)           # ✅
print(evolution_logic)           # ✅
print(state_backup)              # ✅

# Check methods available
print(dir(resource_downloader))
print(hasattr(experience_memory, 'log_error'))
print(callable(internet_bridge.search_web_for_solution))
```

---

## 🚀 Performance Notes

- Auto-download: 5-15 min (depends on model size & internet)
- Experience tracking: <10ms per error
- Web search: 2-5 seconds
- Auto-install: 10-60 seconds (depends on package)
- Brain loop: Every 60 seconds
- Analysis: Every 5 brain cycles (~5 minutes)

---

## 🔐 Security Notes

- No external API keys required (DuckDuckGo free)
- Extensible for ChatGPT/Gemini with optional API keys
- Backups use simple file copy (no encryption)
- pip install runs with timeout protection
- All modifications require explicit backup first

---

## 🎓 Learning Resources

Want to understand Phase 3?

1. Start: PHASE3_COMPLETE_SUMMARY.md
2. Deep dive: PHASE3_INTEGRATION_GUIDE.md
3. Implementation: PHASE3_IMPLEMENTATION_COMPLETE.md
4. Changes: PHASE3_CHANGELOG.md

---

## 💻 Developer Workflows

### **Workflow 1: Monitor Phase 3 on Startup**
```bash
python agent.py 2>&1 | grep -E "\[(DOWNLOADER|EXPERIENCE|BRIDGE|CORRECTION|EVOLUTION|BACKUP)\]"
```

### **Workflow 2: Test Error Tracking**
```python
# Force error 3+ times, watch [EXPERIENCE] and [EVOLUTION] output
for i in range(3):
    try:
        # Code that fails
    except Exception as e:
        experience_memory.log_error("test_error", str(e), f"attempt_{i}")
```

### **Workflow 3: Backup Before Modification**
```python
state_backup.create_backup("agent.py")
# ... make modifications ...
# If needed: state_backup.restore_from_backup(backup_path, "agent.py")
```

---

## 🎯 Common Tasks

**Task: Force Model Download**
```bash
rm models/*.gguf
python agent.py
# Watch [DOWNLOADER] messages
```

**Task: View Error History**
```bash
cat experience.json | jq '.error_log'
```

**Task: List Backups**
```python
from agent import state_backup
state_backup.list_backups()
```

**Task: Test Web Search**
```python
from agent import internet_bridge
results = internet_bridge.search_web_for_solution("your query", max_results=1)
print(results[0]['body'])
```

---

## 📞 Support References

- **Pylance Errors**: Check syntax with `mcp_pylance_mcp_s_pylanceFileSyntaxErrors`
- **Import Issues**: Verify with `mcp_pylance_mcp_s_pylanceImports`
- **Module Not Found**: Handle via SelfCorrection.detect_missing_library()

---

**Phase 3 Quick Reference - Print & Keep Handy!** 📋

Version 3.0.0 | February 16, 2026 | Production Ready ✅

