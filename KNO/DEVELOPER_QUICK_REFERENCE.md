# KNO v5.0 - Developer Quick Reference

---

## 🚀 Quick Start (2 minutes)

```python
# 1. Create and run agent
from agent_refactored import KNOAgent

agent = KNOAgent()
if not agent.startup():
    print("Failed to start")
    exit(1)

# 2. Record audio
audio_file = agent.record_audio("voice.wav")  # Auto timeout: 5 min

# 3. Query AI
response, engine = agent.query_ai("What is the weather?")
print(f"AI ({engine}): {response}")

# 4. Apply code patch
success = agent.apply_code_patch(
    "config.py",
    "REPLACE|OLD|NEW",
    reason="Update setting"
)

# 5. Shutdown
agent.shutdown()
```

---

## 📦 Module Reference

### config.py - Configuration Management

**Load Configuration:**
```python
from config import get_config

config = get_config()  # Loads .env + environment variables

# Access values
print(config.api.gemini_api_key)
print(config.audio.listen_timeout_seconds)
print(config.system.log_level)
```

**Configuration Structure:**
```python
@dataclass
class Config:
    api: APIConfig              # Cloud API keys
    audio: AudioConfig          # Audio settings
    llm: LLMConfig             # Local LLM settings
    system: SystemConfig        # System settings
```

**Validate Configuration:**
```python
warnings = config.validate()
if warnings:
    for warning in warnings:
        logger.warning(warning)
```

**Get Summary:**
```python
print(config.get_summary())
# Output:
# ════════════════════════════════════════════════════════
# KNO Configuration Summary
# ════════════════════════════════════════════════════════
# API Keys Available: 2 configs
# Audio Device: Default
# Wake Word: 'KNO'
# Listen Timeout: 300s
# ...
```

---

### llm_bridge.py - Cloud AI Integration

**Initialize Coordinator:**
```python
from llm_bridge import LLMCoordinator
import os

coordinator = LLMCoordinator(
    gemini_key=os.getenv("GEMINI_API_KEY"),
    openai_key=os.getenv("OPENAI_API_KEY"),
    deepseek_key=os.getenv("DEEPSEEK_API_KEY")
)
```

**Query with Automatic Fallback:**
```python
# Tries: Gemini → ChatGPT → DeepSeek (first success wins)
response, fallback_chain = coordinator.query_with_fallback(
    prompt="Analyze this error: RuntimeError: connection failed",
    max_tokens=1000
)

print(f"Response: {response.content}")
print(f"Engine: {response.engine.value}")
print(f"Fallback chain: {fallback_chain}")

# Response object:
# - response.content: str (the AI response)
# - response.engine: AIEngine (Gemini/OpenAI/DeepSeek)
# - response.tokens_used: int
# - response.is_valid: bool (check before using)
# - response.error: str (if failed)
```

**Query Specific Engine (Optional):**
```python
from llm_bridge import GeminiBridge

gemini = GeminiBridge(os.getenv("GEMINI_API_KEY"))
if gemini.is_available():
    response = gemini.query("What is AI?")
```

---

### safe_code_patcher.py - Safe Code Patching

**Initialize Patcher:**
```python
from safe_code_patcher import SafePatchApplier, CodeValidator

patcher = SafePatchApplier()
```

**Validate Code:**
```python
code = """
def helper():
    return 42
"""

is_valid, errors = CodeValidator.validate_patch_code(code)
if not is_valid:
    print(f"Blocked: {errors}")
```

**Apply Patch (Safe):**
```python
success, message = patcher.apply_patch(
    filepath="config.py",
    patch_code="REPLACE|old_value=1|old_value=2",
    reason="Fix default configuration"
)

if success:
    print(message)  # "✅ Patch applied. Backup: ..."
else:
    print(message)  # "❌ Error: ..."
```

**Patch Formats:**

1. **REPLACE** - Swap old code for new:
```python
patch = "REPLACE|print('hello')|print('goodbye')"
```

2. **APPEND** - Add code at end:
```python
patch = """APPEND
def new_function():
    return "Hello"
"""
```

3. **REMOVE** - Delete code:
```python
patch = """REMOVE
def unwanted_function():
    pass
"""
```

4. **INSERT_FUNCTION** - Add function:
```python
patch = """INSERT_FUNCTION
def helper(x, y):
    \"\"\"Adds two numbers\"\"\"
    return x + y
"""
```

**Backups and Audit Trail:**
```bash
# View backup files
ls -la backups/

# View patch history
cat patch_history.log
```

---

### audio_manager.py - Audio Recording with Timeout

**Initialize Recorder:**
```python
from audio_manager import AudioRecorder

recorder = AudioRecorder(
    sample_rate=16000,
    channels=1,
    chunk_size=1024,
    device_index=None  # Use default device
)
```

**Record with Timeout:**
```python
# Record for maximum 5 minutes (auto timeout)
success, error = recorder.record_with_timeout(
    output_file="voice.wav",
    timeout_seconds=300
)

if success:
    print("✅ Recording saved")
else:
    print(f"❌ Error: {error}")
```

**Verify Audio File:**
```python
from audio_manager import verify_audio_file

is_valid, message = verify_audio_file("voice.wav")
print(message)
# ✅ Audio file valid: 1ch, 16000Hz, 48000 frames (192000 bytes)
```

**List Audio Devices:**
```python
from audio_manager import get_audio_devices

devices = get_audio_devices()
for device in devices:
    print(f"[{device['index']}] {device['name']} - {device['channels']}ch")
    
# Usage: Set AUDIO_DEVICE in .env to index
```

---

### agent_refactored.py - Main Orchestrator

**Minimal Setup:**
```python
from agent_refactored import KNOAgent

agent = KNOAgent()
agent.startup()  # Loads config, initializes modules
agent.shutdown()
```

**Full API:**

```python
# ============ Audio ============
audio_file = agent.record_audio(output_file="voice.wav")
# Returns: str (path to file) or None

# ============ AI Queries ============
response, engine = agent.query_ai(
    prompt="What is 2+2?",
    context="Math problem"
)
# Returns: (str or None, engine_name)

# ============ Code Patching ============
success = agent.apply_code_patch(
    filepath="some_file.py",
    patch_code="REPLACE|old|new",
    reason="Fix issue"
)
# Returns: bool

# ============ Lifecycle ============
agent.startup()   # Initialize everything
agent.shutdown()  # Clean shutdown
```

---

## 🔒 Security Best Practices

### API Keys
```python
# ✅ CORRECT - From environment
key = os.getenv("API_KEY")

# ❌ WRONG - Hardcoded in code
key = "sk-12345..."

# ❌ WRONG - Loaded from JSON file
with open("keys.json") as f:
    key = json.load(f)["api_key"]
```

### Code Validation
```python
# ✅ CORRECT - Validate before using
is_valid, errors = CodeValidator.validate_patch_code(code)
if is_valid:
    patcher.apply_patch(...)

# ❌ WRONG - Run code directly
exec(code)  # NEVER!
```

### Exception Handling
```python
# ✅ CORRECT - Specific exceptions
try:
    stream.read(1024)
except OSError as e:
    logger.error(f"Device error: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")

# ❌ WRONG - Too generic
except Exception:
    pass  # Swallows all errors
```

### Administrative Operations
```python
# ✅ CORRECT - Explicit opt-in
if config.system.request_admin:
    escalate_privileges()

# ❌ WRONG - Silent escalation
if not is_admin():
    escalate_privileges()  # User doesn't expect this!
```

---

## 🐛 Debugging Tips

### Enable Debug Logging
```python
from config import get_config
import logging

config = get_config()
# Change in .env: LOG_LEVEL=DEBUG

logger = logging.getLogger("KNO")
logger.setLevel(logging.DEBUG)
```

### View Logs
```bash
# Real-time monitoring
tail -f logs/kno.log

# Filter by level
grep "ERROR" logs/kno.log
grep "WARNING" logs/kno.log

# Filter by module
grep "KNO.audio" logs/kno.log
grep "KNO.llm" logs/kno.log
```

### Check Configuration
```bash
python config.py
```

### Test Individual Modules
```bash
# Test audio
python audio_manager.py

# Test config (also displays summary)
python config.py

# Test code validator
python safe_code_patcher.py

# Test LLM bridge
python llm_bridge.py
```

---

## 🔧 Common Tasks

### Record Audio for Transcription
```python
from audio_manager import AudioRecorder, verify_audio_file

recorder = AudioRecorder()
success, error = recorder.record_with_timeout(
    output_file="transcript_input.wav",
    timeout_seconds=60  # Up to 1 minute
)

if success:
    is_valid, msg = verify_audio_file("transcript_input.wav")
    print(msg)  # e.g., "✅ Audio file valid: 1ch, 16000Hz..."
```

### Query AI for Error Recovery
```python
error_context = """
Error Type: FileNotFoundError
Message: Model file not found at /path/to/model.gguf
Stack: [frame 1, frame 2, ...]
System: Windows 10
"""

solution, engine = agent.query_ai(
    prompt="How can I fix this error?",
    context=error_context
)

print(f"Solution from {engine}:\n{solution}")
```

### Apply Code Fixes via AI
```python
# Get fix suggestion from AI
suggestion, engine = agent.query_ai(
    prompt="Provide a patch to fix the audio recording timeout"
)

# Extract and apply patch
# Note: AI should return format: "REPLACE|old|new"
try:
    success = agent.apply_code_patch(
        filepath="audio_manager.py",
        patch_code=suggestion,
        reason=f"Auto-fix from {engine}"
    )
except ValueError as e:
    print(f"Patch rejected for security: {e}")
```

### Handle Configuration Errors
```python
try:
    config = get_config()
    warnings = config.validate()
    
    if warnings:
        logger.warning("Configuration issues found:")
        for w in warnings:
            logger.warning(f"  - {w}")
    
    if not config.api.gemini_api_key:
        logger.warning("Gemini API key not set - cloud AI queries will fail")
        
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    exit(1)
```

---

## 📊 Type Hints Reference

**Common Type Annotations:**
```python
from typing import Optional, List, Dict, Tuple, Union

# Optional types (can be None)
Optional[str]       # str or None
Optional[int]       # int or None

# Collections
List[str]          # List of strings
Dict[str, int]     # Dict with str keys, int values
Tuple[str, int]    # Tuple of (string, integer)

# Union types (one of several)
Union[str, int]    # Either str or int

# Function signatures
def process(data: Optional[str]) -> Tuple[bool, str]:
    \"\"\"Process data, return (success, message)\"\"\"
    pass

# Generic collections
from collections.abc import Sequence
def iterate(items: Sequence[int]) -> int:
    \"\"\"Iterate and sum\"\"\"
    return sum(items)
```

---

## 📋 Docstring Template

```python
def function_name(arg1: str, arg2: Optional[int] = None) -> bool:
    \"\"\"
    Brief one-line summary.
    
    Longer description can span multiple lines explaining
    what the function does and why.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2 (optional)
        
    Returns:
        bool: Description of return value
        
    Raises:
        ValueError: If arg1 is invalid
        OSError: If file operations fail
        
    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    \"\"\"
    pass
```

---

## 🔗 Related Files

- `SECURITY_REFACTORING_SUMMARY.md` - Detailed refactoring overview
- `MIGRATION_v5_SECURITY_REFACTOR.md` - Migration guide
- `.env.example` - Configuration template
- `backups/` - Automatic code patch backups
- `logs/kno.log` - Application logs

---

## 💡 Tips & Tricks

1. **Auto-reload config**: Call `get_config()` again to reload from .env
2. **Thread-safe logging**: Use `logger.info()` instead of `print()` in threads
3. **Fallback chains**: LLM coordinator tries multiple AI engines automatically
4. **Audit trail**: Every patch is logged to `patch_history.log` with timestamp
5. **Timeout safety**: All functions have built-in timeouts, can't hang
6. **Type checking**: Use `mypy` to check types in your code
7. **AST validation**: Leverage `CodeValidator` before applying untrusted code

---

**v5.0 Reference Ready - Happy Coding! 🚀**
