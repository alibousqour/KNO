# Phase 4: Error Recovery Guide - Understanding Self-Healing

This guide explains how KNO autonomously detects, investigates, and fixes errors using ChatGPT.

---

## How Phase 4 Error Recovery Works

### The Error Recovery Pipeline

```
┌─────────────────────────────────────────────────────────┐
│ 1. ERROR DETECTION                                      │
│    Exception occurs in local LLM or Python code         │
└─────────────────────┬───────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│ 2. ERROR QUEUING                                        │
│    Error details captured: type, message, traceback     │
│    Queued to self_evolution_thread                      │
└─────────────────────┬───────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│ 3. CHATGPT INVESTIGATION                                │
│    "This error means... you should try..."              │
│    ChatGPT generates fix suggestion                     │
└─────────────────────┬───────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│ 4. FIX CLASSIFICATION                                   │
│    [FIX_SHELL] = pip install numpy==1.24.3             │
│    [FIX_CODE] = Python code snippet to patch           │
│    [INFO] = Knowledge only, manual fix needed          │
└─────────────────────┬───────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│ 5. AUTO-FIX APPLICATION                                 │
│    Execute fix command/code with timeout protection    │
│    Verify success                                       │
└─────────────────────┬───────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│ 6. LOGGING & CONTINUATION                               │
│    Log result to evolution.log                          │
│    Resume normal operation                              │
└─────────────────────────────────────────────────────────┘
```

---

## Error Types and Recovery Strategies

### Type 1: Missing Dependencies

**Example Error**:
```
ModuleNotFoundError: No module named 'numpy'
```

**ChatGPT Response**:
```
[FIX_SHELL] pip install numpy
```

**Automatic Recovery**:
- Detects missing module
- Suggests: `pip install numpy`
- Executes: `subprocess.run(['pip', 'install', 'numpy'], timeout=30)`
- Verifies: Imports numpy successfully
- Result: ✅ Logged to evolution.log

---

### Type 2: Version Incompatibility

**Example Error**:
```
AttributeError: module 'numpy' has no attribute 'int'
(numpy 1.24+ removed numpy.int)
```

**ChatGPT Response**:
```
[FIX_SHELL] pip install numpy==1.23.5
```

**Automatic Recovery**:
- Identifies: numpy version too new
- Suggests: Pin to compatible version
- Executes: `pip install numpy==1.23.5`
- Verifies: Code runs without error
- Result: ✅ Logged to evolution.log

---

### Type 3: Code-Level Logic Errors

**Example Error**:
```
IndexError: list index out of range
Position: agent.py line 1234
```

**ChatGPT Response**:
```
[FIX_CODE] 
# Add bounds checking before accessing list
if index < len(my_list):
    value = my_list[index]
else:
    value = default_value
```

**Automatic Recovery**:
- Analyzes error location
- Generates patched code section
- Applies patch (if safe)
- Tests: Does error recur?
- Result: ✅ Fixed or ⚠️ Logged for manual review

---

### Type 4: Network/API Errors

**Example Error**:
```
requests.exceptions.ConnectionError: Failed to connect
```

**ChatGPT Response**:
```
[FIX_SHELL] pip install requests
[INFO] Check internet connectivity
```

**Automatic Recovery**:
- Suggests package update
- Installs
- Logs: Partial fix (network issue may persist)
- Result: ⚠️ Partial - dependency fixed, network problem remains

---

### Type 5: Resource Exhaustion

**Example Error**:
```
MemoryError: Unable to allocate memory
```

**ChatGPT Response**:
```
[INFO] Clear cache to free memory
[FIX_CODE]
import gc
gc.collect()  # Force garbage collection
```

**Automatic Recovery**:
- Executes garbage collection
- Logs suggestion: Monitor memory usage
- Result: ⚠️ Temporary relief - may recur under heavy load

---

## Error Queuing Mechanism

### What Gets Queued?

When an exception occurs in the main LLM inference loop:

```python
try:
    response = llama_model.generate(prompt)
except Exception as e:
    # [PHASE 4] Queue error for investigation
    error_info = {
        'error_type': e.__class__.__name__,
        'error_msg': str(e),
        'traceback': traceback.format_exc(),
        'timestamp': datetime.now(),
        'context': {
            'last_prompt': prompt[:200],
            'model_status': 'loaded',
            'memory_usage': psutil.virtual_memory().percent
        }
    }
    self_evolution_thread.queue_error(error_info)
```

### Queue Processing

Errors are processed asynchronously:

```python
class SelfEvolutionThread(Thread):
    def __init__(self):
        self.error_queue = Queue()
        self.processing = True
    
    def process_error_queue(self):
        while self.processing:
            while not self.error_queue.empty():
                error = self.error_queue.get()
                fix = self.investigate_error(error)
                self.apply_fix(fix)
            time.sleep(1)  # Check every second
```

**Key Feature**: Non-blocking - errors don't halt main agent operation

---

## ChatGPT Error Investigation

### Sample Investigation

**Error Sent to ChatGPT**:
```
Error Type: ModuleNotFoundError
Error Message: No module named 'librosa'
Traceback: File agent.py, line 234
Context: Audio processing pipeline
```

**ChatGPT Response**:
```
This error occurs because the librosa library (audio processing)
is not installed in your Python environment.

SOLUTION (Priority: HIGH, Confidence: 98%):
[FIX_SHELL] pip install librosa

VERIFICATION:
After running this command, librosa will be available
and the audio processing should work.

FALLBACK (if above fails):
[FIX_SHELL] pip install librosa --upgrade
[FIX_SHELL] pip install librosa --force-reinstall
```

---

## Fix Types

### [FIX_SHELL] - System Commands

These are executed in a subprocess:

```bash
pip install package_name
pip install package_name==version
pip install --upgrade package_name
apt-get install system-package
brew install system-package
```

**Safety Features**:
- 30-second timeout (prevents hanging)
- Command logged before execution
- Return code checked (logs if fails)
- stdout/stderr captured for analysis

**Example Execution**:
```python
result = subprocess.run(
    ['pip', 'install', 'numpy==1.24.3'],
    timeout=30,
    capture_output=True,
    text=True
)
if result.returncode == 0:
    print("SUCCESS: numpy 1.24.3 installed")
else:
    print(f"FAILED: {result.stderr}")
```

### [FIX_CODE] - Python Code Patches

These modify Python logic:

```python
# Original (broken):
value = my_list[index]

# Fixed:
if index < len(my_list):
    value = my_list[index]
else:
    value = None
```

**Safety Features**:
- Code reviewed before execution
- `exec()` used carefully with restricted namespace
- Changes logged with before/after comparison
- Easy to revert if needed

**Example Application**:
```python
fix_code = """
import gc
gc.collect()
"""
namespace = {'my_list': my_list}
exec(fix_code, namespace)  # Execute in safe namespace
```

### [INFO] - Knowledge Only

These cannot be auto-fixed:

```
[INFO] This error occurs under specific conditions:
- Heavy CPU load (>95%)
- Low memory (<500MB free)
- Large batch size processing

RECOMMENDATION:
Reduce batch_size parameter from 64 to 32
Monitor system resources during operation

MANUAL STEPS:
1. edit config.json
2. Change batch_size: 32
3. Restart agent
```

**Handling**:
- Logged to evolution.log
- GUI shows suggestion
- User can implement manually
- No remote execution attempted

---

## Real-World Error Recovery Examples

### Example 1: Fresh Installation

**Scenario**: Running agent.py on new machine

**Error Flow**:
```
1. Import scipy → ModuleNotFoundError
2. Queue error → self_evolution_thread
3. ChatGPT: "pip install scipy"
4. Auto-execute: pip install scipy
5. Retry import → SUCCESS
6. Agent continues normally
```

**Result**: ✅ Self-healed, no manual intervention needed

**Log Entry**:
```
[2024-01-15 10:02:33] [CHATGPT] Error: ModuleNotFoundError scipy
[2024-01-15 10:02:35] [CHATGPT] Fix: [FIX_SHELL] pip install scipy
[2024-01-15 10:02:38] [EVOLUTION] Applied: pip install scipy
[2024-01-15 10:02:45] [EVOLUTION] Verification: SUCCESS
```

---

### Example 2: Numpy Version Conflict

**Scenario**: Old numpy broke by new code

**Error Flow**:
```
1. numpy.int used (removed in 1.24+)
2. AttributeError → Queue error
3. ChatGPT detects numpy version issue
4. Fix: "pip install numpy==1.23.5"
5. Auto-execute → Install specific version
6. Retry → SUCCESS
```

**Result**: ✅ Downgraded to compatible version

**Log Entry**:
```
[2024-01-15 11:45:22] [CHATGPT] Error: AttributeError (numpy.int)
[2024-01-15 11:45:24] [CHATGPT] Root cause: numpy version too new
[2024-01-15 11:45:25] [CHATGPT] Fix: [FIX_SHELL] pip install numpy==1.23.5
[2024-01-15 11:45:35] [EVOLUTION] Downgrade complete
[2024-01-15 11:45:38] [EVOLUTION] Verification: SUCCESS
```

---

### Example 3: Memory Management

**Scenario**: Agent runs out of memory under load

**Error Flow**:
```
1. MemoryError on large batch
2. Queue error → self_evolution_thread
3. ChatGPT: [FIX_CODE] gc.collect()
4. Auto-execute → Release memory
5. Might retry batch size → adjust batch config
```

**Result**: ⚠️ Partial recovery - memory freed, may recur

**Log Entry**:
```
[2024-01-15 14:12:10] [CHATGPT] Error: MemoryError
[2024-01-15 14:12:12] [CHATGPT] Analysis: Out of memory during inference
[2024-01-15 14:12:13] [CHATGPT] Fix: [FIX_CODE] gc.collect()
[2024-01-15 14:12:15] [EVOLUTION] Memory freed: 312MB
[2024-01-15 14:12:16] [EVOLUTION] Status: Partial recovery
[2024-01-15 14:12:17] [INFO] Recommendation: Reduce batch_size in config
```

---

## Monitoring Error Recovery

### View Evolution Log

```bash
# Real-time monitoring
tail -f logs/evolution.log

# Filter by error type
grep "ERROR" logs/evolution.log

# Filter by fix type
grep "FIX_" logs/evolution.log

# Count fixes applied
grep "EVOLUTION" logs/evolution.log | wc -l

# Show only ChatGPT fixes
grep "CHATGPT.*Fix" logs/evolution.log
```

### Parse Log for Statistics

```python
import json
from datetime import datetime

fixes = {
    'total': 0,
    'shell': 0,
    'code': 0,
    'info': 0,
    'success': 0,
    'failed': 0
}

with open('logs/evolution.log', 'r') as f:
    for line in f:
        if '[FIX_' in line:
            fixes['total'] += 1
            if '[FIX_SHELL]' in line:
                fixes['shell'] += 1
            elif '[FIX_CODE]' in line:
                fixes['code'] += 1
            elif '[INFO]' in line:
                fixes['info'] += 1
        if 'SUCCESS' in line:
            fixes['success'] += 1
        elif 'FAILED' in line:
            fixes['failed'] += 1

print(f"Total fixes: {fixes['total']}")
print(f"  Shell: {fixes['shell']}")
print(f"  Code: {fixes['code']}")
print(f"  Info: {fixes['info']}")
print(f"  Success rate: {fixes['success'] / fixes['total'] * 100:.1f}%")
```

---

## Error Recovery Configuration

### Adjust Timeout

**Default**: 30 seconds per API call

```python
# In agent.py, SelfEvolutionThread class
INVESTIGATE_TIMEOUT = 30  # Change to 60 for slower systems
APPLY_TIMEOUT = 30        # Change to 60 for large pip installs
```

### Adjust Queue Processing

**Default**: Check every 1 second

```python
# In agent.py, SelfEvolutionThread.process_error_queue()
time.sleep(1)  # Change to 0.5 for faster processing
```

### Adjust Error Context

**Default**: Log last 200 chars of prompt

```python
# In agent.py, chat_and_respond() error handler
'last_prompt': prompt[:200]  # Change to [:500] for more context
```

---

## Limitations & Manual Override

### When Fixes Cannot Auto-Apply

1. **Network errors** - Can't fix internet connectivity
2. **Hardware errors** - Can't replace broken hardware
3. **API errors** - Can't fix if Gemini/ChatGPT APIs down
4. **Data corruption** - Can't auto-repair corrupted files
5. **Permission errors** - Can't bypass system permissions

### Manual Override

Disable auto-fix for specific errors:

```python
# In self_evolution_thread.apply_fix()
SKIP_AUTOAPPLY = [
    'PermissionError',
    'OSError',
    'FileNotFoundError',
    'NetworkError'
]

if error_type in SKIP_AUTOAPPLY:
    # Log but don't apply
    print(f"Skipping auto-apply for {error_type}")
    return False
```

---

## Troubleshooting Error Recovery

### Issue: Fixes not being applied

```
Check 1: Is ChatGPT API key configured?
$ echo $env:OPENAI_API_KEY

Check 2: Is error_queue processing running?
$ grep "EVOLUTION" logs/evolution.log

Check 3: Are timeouts too short?
Edit: INVESTIGATE_TIMEOUT = 60

Check 4: Is subprocess failing?
$ manually run pip install package
```

### Issue: Same error repeating

```
Check 1: Did apply actually work?
$ verify manually: pip list | grep package

Check 2: Is fix incorrect?
Search logs for exact error and proposed fix

Check 3: Is there a root cause?
Additional investigation may be needed

Workaround: Manually implement fix then restart
```

### Issue: ChatGPT investigation taking too long

```
Check 1: Is internet slow?
$ ping -c 5 api.openai.com

Check 2: Is ChatGPT API responding?
Check: https://openai.com/status

Check 3: Increase timeout
Edit: INVESTIGATE_TIMEOUT = 120

Check 4: Use Gemini fallback
(Currently ChatGPT-only for error analysis)
```

---

## Best Practices

✅ **DO**:
- Monitor evolution.log regularly
- Set up email alerts for repeated errors
- Review ChatGPT fixes before committing
- Test fixes manually first
- Keep API keys secure

❌ **DON'T**:
- Let auto-fixes run on production without review
- Ignore repeated errors (indicates root cause)
- Share evolution.log with API keys exposed
- Disable error recovery without backup
- Trust auto-fixes for critical operations

---

## Next Steps

1. Set up [API integration](PHASE4_API_INTEGRATION_GUIDE.md)
2. Monitor `logs/evolution.log` during operation
3. Review ChatGPT fixes in log periodically
4. Report any fixes that fail to [PHASE4_TROUBLESHOOTING.md](PHASE4_TROUBLESHOOTING.md)
5. Contribute improvements to error recovery pipeline

---

**Questions?** See [PHASE4_TROUBLESHOOTING.md](PHASE4_TROUBLESHOOTING.md)  
**Setup help?** See [PHASE4_API_INTEGRATION_GUIDE.md](PHASE4_API_INTEGRATION_GUIDE.md)  
**Overall status?** See [PHASE4_IMPLEMENTATION_COMPLETE.md](PHASE4_IMPLEMENTATION_COMPLETE.md)
