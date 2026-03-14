# =========================================================================
# KNO v5.0 Security Refactoring - Migration Guide
# =========================================================================

## 🎯 Overview

This guide explains how to migrate from the old agent.py (8000+ lines, security issues) to the new v5.0 architecture (modular, secure, maintainable).

### What Changed?

**SECURITY IMPROVEMENTS:**
- ❌ **REMOVED**: JSON file storage for API keys (evolution_keys.json)
- ✅ **ADDED**: Environment variables only for sensitive data
- ❌ **REMOVED**: Dangerous exec() calls for code execution
- ✅ **ADDED**: Safe AST-based code patching
- ❌ **REMOVED**: Silent admin escalation without consent
- ✅ **ADDED**: Explicit user opt-in for admin features
- ✅ **ADDED**: Proper exception handling (specific, not bare except:)
- ✅ **ADDED**: Timeout enforcement on all long-running operations
- ✅ **ADDED**: File handle cleanup and verification

**ARCHITECTURE IMPROVEMENTS:**
- ✅ **SPLIT**: 8000-line agent.py → 6 focused modules + small orchestrator
- ✅ **ADDED**: Type hints everywhere
- ✅ **ADDED**: Comprehensive docstrings
- ✅ **ADDED**: Proper logging instead of print()
- ✅ **ADDED**: Configuration validation

---

## 📋 File Structure (NEW)

```
a:\KNO\KNO\
├── agent_refactored.py         ← NEW: Main orchestrator (<300 lines)
├── config.py                   ← NEW: Secure config management
├── llm_bridge.py              ← NEW: Cloud API integration
├── safe_code_patcher.py       ← NEW: Safe code patching (replaces exec())
├── audio_manager.py           ← NEW: Audio with timeouts & cleanup
│
├── .env                        ← IMPORTANT: Create this file
├── agent.py                    ← OLD: Keep as backup initially
│
├── logs/                       ← NEW: Logging directory
│   └── kno.log                ← Log file (created auto)
├── backups/                    ← NEW: Code patch backups
│   └── agent.py.*.bak        ← Backup files
└── patch_history.log          ← NEW: Patch audit trail
```

---

## 🔐 SECURITY FIX #1: API Keys → Environment Variables Only

### BEFORE (INSECURE):
```python
# OLD agent.py reads from JSON and environment
# If evolution_keys.json exists → security risk!

def load_api_key(key_name):
    env_key = os.getenv(key_name)
    if env_key:
        return env_key
    
    # ❌ INSECURE: Falls back to JSON file
    if os.path.exists("evolution_keys.json"):
        with open("evolution_keys.json", "r") as f:
            config = json.load(f)
            return config.get(key_name)
```

### AFTER (SECURE):
```python
# NEW config.py - environment ONLY
api_config = APIConfig(
    gemini_api_key=os.getenv("GEMINI_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    deepseek_api_key=os.getenv("DEEPSEEK_API_KEY")
)
# If key is not in environment → None (no JSON fallback)
```

### Migration Steps:

1. **Create .env file:**
   ```bash
   cp .env.example .env  # Use the template in config.py
   ```

2. **Set your API keys:**
   ```bash
   # .env file
   GEMINI_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   DEEPSEEK_API_KEY=your_key_here
   ```

3. **Delete old JSON file:**
   ```bash
   rm evolution_keys.json  # No longer used or needed
   ```

4. **Verify it works:**
   ```bash
   python config.py  # Should show loaded API keys or warnings
   ```

---

## 🔧 SECURITY FIX #2: No More exec() - Safe Code Patching

### BEFORE (CRITICAL VULNERABILITY):
```python
# OLD agent.py - allows running ANY code from AI!
def apply_fix(fix_suggestion):
    if "[FIX_CODE]" in fix_suggestion:
        code = fix_suggestion.split("[FIX_CODE]")[1]
        # ❌ CRITICAL: Runs arbitrary code!
        exec(code, {"experience_memory": experience_memory})
```

### AFTER (SAFE):
```python
# NEW safe_code_patcher.py - validates code first, patches with regex
def apply_patch(filepath, patch_code, reason=""):
    # 1. Validate code with AST
    is_valid, errors = CodeValidator.validate_patch_code(patch_code)
    if not is_valid:
        raise ValueError(f"Blocked: {errors}")
    
    # 2. Create backup
    backup_path = self._create_backup(filepath)
    
    # 3. Apply safely (regex replace, not execution)
    new_content = self._apply_replace(original, old_code, new_code)
    
    # 4. Write and verify
    with open(filepath, "w") as f:
        f.write(new_content)
```

### Blocked Patterns (Automatically Rejected):
- `eval()`, `exec()`, `compile()`
- `__import__`, `__builtins__`
- `globals()`, `locals()`, `vars()`
- `getattr()`, `setattr()`, `delattr()`
- Double underscore methods (`__`)

### Migration Steps:

1. **Never use exec():**
   ```python
   # ❌ OLD - DON'T DO THIS
   exec(ai_generated_code)
   
   # ✅ NEW - Use this instead
   success = agent.apply_code_patch(
       filepath="agent.py",
       patch_code="REPLACE|old_code|new_code",
       reason="Fix security issue"
   )
   ```

2. **Patch Format Examples:**
   ```python
   # REPLACE patch
   patch = "REPLACE|print('old')|print('new')"
   
   # APPEND patch
   patch = """APPEND
def new_function():
    return 42
"""
   
   # REMOVE patch
   patch = """REMOVE
def unwanted_function():
    pass
"""
   
   # INSERT_FUNCTION patch
   patch = """INSERT_FUNCTION
def helper():
    return "useful"
"""
   ```

---

## ⏱️ SECURITY FIX #3: Timeouts on All Long-Running Operations

### BEFORE (CAN HANG FOREVER):
```python
# OLD agent.py - infinite loop, no timeout!
def detect_wake_word_or_ptt(self):
    while True:  # ❌ No timeout!
        try:
            chunk = stream.read(chunk_size)
            # Process...
        except:
            continue  # ❌ Bare except - swallows all errors
```

### AFTER (ENFORCED TIMEOUT):
```python
# NEW audio_manager.py - 5-min timeout by default
success, error = audio_recorder.record_with_timeout(
    output_file="voice.wav",
    timeout_seconds=300  # 5 minutes max
)

# Timeout automatically stops recording and closes file
# No infinite loops ever possible
```

### Configuration (in .env):
```bash
LISTEN_TIMEOUT_SECONDS=300      # Max listen time
PTT_TIMEOUT_SECONDS=60          # Max push-to-talk time
```

### Migration Steps:

1. **Add timeouts to your config:**
   ```bash
   # .env
   LISTEN_TIMEOUT_SECONDS=300
   PTT_TIMEOUT_SECONDS=60
   ```

2. **Use the new timeout-safe functions:**
   ```python
   # ❌ OLD - potential infinite loop
   # audio_file = recorder.record_voice()
   
   # ✅ NEW - guaranteed timeout
   audio_file = agent.record_audio(output_file="voice.wav")
   ```

---

## 👤 SECURITY FIX #4: Admin Escalation Requires Consent

### BEFORE (SILENT PRIVILEGE ESCALATION):
```python
# OLD agent.py - auto-restarts with UAC without clear warning!
def check_and_request_admin_privileges():
    if not is_admin():
        # ❌ Silently restarts with UAC!
        ShellExecuteEx(lpVerb='runas', ...)
        sys.exit(0)
```

### AFTER (EXPLICIT OPT-IN):
```python
# NEW - only escalates if user explicitly sets REQUEST_ADMIN=true

if config.system.request_admin:  # ✅ Requires explicit config
    self._handle_admin_escalation()
else:
    logger.warning("Admin features disabled. Set REQUEST_ADMIN=true to enable.")
```

### Migration Steps:

1. **To enable admin escalation:**
   ```bash
   # .env
   REQUEST_ADMIN=true
   ```

2. **To disable (recommended for most users):**
   ```bash
   # .env
   REQUEST_ADMIN=false  # Or omit entirely (default)
   ```

3. **What happens:**
   - If `REQUEST_ADMIN=false`: Runs normally, logs warning about limited features
   - If `REQUEST_ADMIN=true`: Requests UAC escalation on Windows

---

## 🛠️ Specific Exception Handling

### BEFORE (TOO BROAD):
```python
# ❌ OLD - ignores important errors
try:
    audio_file = stream.read(chunk_size)
except Exception:  # Catches EVERYTHING silently
    continue
```

### AFTER (SPECIFIC HANDLING):
```python
# ✅ NEW - handles each error type properly
try:
    chunk = stream.read(chunk_size, exception_on_overflow=False)
except IOError as e:
    logger.error(f"Audio read error: {e}")
    break
except OSError as e:
    logger.error(f"Device error: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected audio error: {e}")
    break
```

### Common Exception Types to Use:
```python
OSError                 # File/device/network errors
IOError                 # I/O operation errors
TimeoutError            # Timeout expiration
ImportError             # Module not found
ValueError              # Invalid argument
TypeError               # Wrong type
KeyError                # Missing dictionary key
AttributeError          # Missing attribute
```

---

## 📝 Logging Instead of print()

### BEFORE (NO CONTEXT):
```python
# ❌ OLD - just prints, hard to find later
print(f"[BRAIN] ✅ Loaded {key_name} from environment")
```

### AFTER (STRUCTURED LOGGING):
```python
# ✅ NEW - includes timestamp, level, context
logger.info(f"✅ Loaded {key_name} from environment")
# Output: 2026-02-17 14:23:45,123 - KNO.config - INFO - ✅ Loaded...
```

### Log Levels:
```python
logger.debug("Detailed diagnostic info")      # Development
logger.info("Important status messages")      # Normal operation
logger.warning("Something unexpected")        # User attention needed
logger.error("Operation failed")              # Error occurred
logger.critical("System failure")             # Critical issue
```

### View Logs:
```bash
# Real-time
tail -f logs/kno.log

# Filtered by level
grep "ERROR" logs/kno.log
grep "WARNING" logs/kno.log
```

---

## 🚀 Migration Checklist

- [ ] **Create .env file** with API keys
  ```bash
  GEMINI_API_KEY=sk-...
  OPENAI_API_KEY=sk-...
  DEEPSEEK_API_KEY=...
  ```

- [ ] **Delete evolution_keys.json**
  ```bash
  rm evolution_keys.json
  ```

- [ ] **Test new config system**
  ```bash
  python config.py
  ```

- [ ] **Install new dependencies** (if needed)
  ```bash
  pip install python-dotenv requests pyaudio
  ```

- [ ] **Test audio recording**
  ```bash
  python audio_manager.py
  ```

- [ ] **Test safe code patching**
  ```python
  # Create test file
  with open("test.py", "w") as f:
      f.write("x = 1")
  
  # Apply patch
  patcher = SafePatchApplier()
  patcher.apply_patch("test.py", "REPLACE|x = 1|x = 2")
  ```

- [ ] **Update your scripts** to use new modules
  ```python
  from agent_refactored import KNOAgent
  agent = KNOAgent()
  agent.startup()
  ```

- [ ] **Backup old agent.py** for reference
  ```bash
  mv agent.py agent_v4_old.py
  ```

- [ ] **Test full startup**
  ```bash
  python agent_refactored.py
  ```

- [ ] **Review logs**
  ```bash
  tail logs/kno.log
  ```

---

## 🔍 Troubleshooting

### API Keys Not Loading

**Problem:** `⚠️ No API keys available in environment variables`

**Solution:**
```bash
# 1. Verify .env file exists
ls -la .env

# 2. Verify keys are set
echo $GEMINI_API_KEY

# 3. Check .env format (no spaces around =)
# CORRECT: GEMINI_API_KEY=sk-...
# WRONG:   GEMINI_API_KEY = sk-...
```

### Audio Device Not Found

**Problem:** `❌ Audio device error: [Errno -9996]`

**Solution:**
```bash
# 1. List available devices
python audio_manager.py

# 2. Set explicit device index in .env
AUDIO_DEVICE=1  # Use device 1 instead of default

# 3. Restart
```

### Code Patches Being Rejected

**Problem:** `❌ Blocked pattern found`

**Solution:**
```python
# ❌ WRONG: Uses eval (blocked)
patch = "REPLACE|code|eval(something)"

# ✅ RIGHT: Direct function call
patch = "REPLACE|code|result = calculate()"
```

---

## 📚 Module Documentation Quick Reference

### config.py
```python
from config import get_config
config = get_config()
print(config.api.gemini_api_key)      # Get API key
print(config.audio.listen_timeout_seconds)  # Get timeout
```

### llm_bridge.py
```python
from llm_bridge import LLMCoordinator
coordinator = LLMCoordinator(
    gemini_key=os.getenv("GEMINI_API_KEY"),
    openai_key=os.getenv("OPENAI_API_KEY"),
    deepseek_key=os.getenv("DEEPSEEK_API_KEY")
)
response, fallback_chain = coordinator.query_with_fallback("What is 2+2?")
```

### audio_manager.py
```python
from audio_manager import AudioRecorder, verify_audio_file
recorder = AudioRecorder()
success, error = recorder.record_with_timeout("voice.wav", timeout_seconds=300)
is_valid, msg = verify_audio_file("voice.wav")
```

### safe_code_patcher.py
```python
from safe_code_patcher import SafePatchApplier, CodeValidator
patcher = SafePatchApplier()
success, msg = patcher.apply_patch("file.py", "REPLACE|old|new", reason="Fix")
```

### agent_refactored.py
```python
from agent_refactored import KNOAgent
agent = KNOAgent()
agent.startup()
audio = agent.record_audio()
response, engine = agent.query_ai("What is AI?")
```

---

## ✅ Security Validation Checklist

**Before (v4.0) Issues:**
- [x] API keys in JSON files → **FIXED**: Env vars only
- [x] exec() arbitrary code → **FIXED**: Safe patching
- [x] Silent admin escalation → **FIXED**: Requires opt-in
- [x] Infinite loops → **FIXED**: Timeout enforced
- [x] File handle leaks → **FIXED**: Explicit close()
- [x] Bare except: clauses → **FIXED**: Specific handling
- [x] No type hints → **FIXED**: Full type hints
- [x] No docstrings → **FIXED**: Complete docstrings
- [x] print() logging → **FIXED**: Proper logging
- [x] 8000-line monolith → **FIXED**: 6 focused modules

---

## 📞 Support

For issues with the refactored code:

1. Check logs: `tail logs/kno.log`
2. Check config: `python config.py`
3. Review migration guide above
4. Check module docstrings: `python -c "import audio_manager; help(audio_manager)"`

---

**Migration Status: Ready for Production v5.0**
