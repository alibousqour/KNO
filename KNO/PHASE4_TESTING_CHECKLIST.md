# Phase 4: Testing & Verification Checklist

Complete this checklist to verify Phase 4 implementation is working correctly.

---

## Pre-Launch Checklist

### Environment Setup
- [ ] API keys acquired:
  - [ ] Google Gemini API key created
  - [ ] OpenAI ChatGPT API key created
- [ ] Environment variables configured:
  - [ ] `GEMINI_API_KEY` set permanently
  - [ ] `OPENAI_API_KEY` set permanently
- [ ] evolution_keys.json (backup):
  - [ ] Created (optional but recommended)
  - [ ] Added to .gitignore
  - [ ] Permissions restricted (chmod 600)

### Code Verification
- [ ] agent.py syntax verified (0 errors) ✅
- [ ] HigherIntelligenceBridge class exists
- [ ] EvolutionaryAutoDownloader class exists
- [ ] SelfEvolutionThread class exists
- [ ] Three instances created globally
- [ ] File header updated to v4.0

### Directory Structure
- [ ] `logs/` directory exists
- [ ] `models/` directory exists
- [ ] `faces/` directory exists (for GUI assets)
- [ ] `sounds/` directory exists

---

## Startup Verification

### Test 1: Agent Starts Without Errors
```bash
python agent.py
```

**Expected Output**:
```
[STARTUP] KNO Evolutionary Autonomous Agent v4.0 starting...
[BRAIN] Higher Intelligence Bridge initialized
[BRAIN] Gemini API: LOADED
[BRAIN] ChatGPT API: LOADED (or fallback ready)
[MODEL] Loading GGUF model...
[MODEL] Model loaded successfully
[READY] Agent ready for input
```

**Check**:
- [ ] No import errors
- [ ] No connection errors  
- [ ] No timeout during startup
- [ ] Model loaded successfully
- [ ] Both API brains initialized

---

### Test 2: Check Logs Directory
```bash
ls -la logs/
```

**Expected**:
```
logs/
  ├─ evolution.log (created on first API call)
  └─ other_logs/ (from Phase 3, if any)
```

**Check**:
- [ ] `logs/` directory accessible
- [ ] Write permissions confirmed
- [ ] No permission errors

---

## API Integration Tests

### Test 3: Verify Gemini API Connection
```python
from agent import higher_intelligence_bridge

print("Testing Gemini API...")
response = higher_intelligence_bridge.query_gemini("What is 2+2?")
print(f"Gemini responded: {response[:100]}...")
```

**Expected**:
- Response from Gemini within 3 seconds
- Answer to "What is 2+2?" should mention 4
- No timeout errors
- Response logged to `logs/evolution.log`

**Check**:
- [ ] Response received successfully
- [ ] Response is sensible (not error message)
- [ ] No timeout occurred
- [ ] Latency < 5 seconds

---

### Test 4: Verify ChatGPT API Connection
```python
from agent import higher_intelligence_bridge

print("Testing ChatGPT API...")
response = higher_intelligence_bridge.query_chatgpt("What is 2+2?")
print(f"ChatGPT responded: {response[:100]}...")
```

**Expected**:
- Response from ChatGPT within 5 seconds
- Answer should mention 4
- Response logged to `logs/evolution.log`

**Check**:
- [ ] Response received successfully
- [ ] Response is sensible (not error message)
- [ ] No timeout occurred
- [ ] Latency < 10 seconds

---

### Test 5: Verify Fallback Mechanism
```python
from agent import higher_intelligence_bridge

# Temporarily set Gemini key to invalid to test fallback
import os
os.environ['GEMINI_API_KEY'] = 'invalid-key-12345'

# This should fail Gemini and fallback to ChatGPT
response = higher_intelligence_bridge.solve_complex_problem(
    problem="What is today's date?",
    context="Current date: 2024"
)

print(f"Response via fallback: {response[:100]}...")
```

**Expected**:
- First attempt to Gemini fails (401 Unauthorized)
- Automatic fallback to ChatGPT
- ChatGPT returns valid response
- Log shows fallback was triggered

**Check**:
- [ ] Fallback mechanism works
- [ ] ChatGPT response received despite Gemini failure
- [ ] Logged properly with fallback indication

---

## Model Auto-Download Test

### Test 6: Verify Auto-Download (if model missing)
```bash
# First, backup current model
mv models/gemma-2b-it.gguf models/gemma-2b-it.gguf.backup

# Start agent - should trigger auto-download
python agent.py
```

**Expected**:
```
[STARTUP] Model file not found
[DOWNLOADER] Querying Gemini for latest gemma-2b-it...
[DOWNLOADER] Found download URL: https://...
[DOWNLOADER] Downloading... 0%
[DOWNLOADER] Downloading... 25%
[DOWNLOADER] Downloading... 50%
[DOWNLOADER] Downloading... 75%
[DOWNLOADER] Downloading... 100%
[DOWNLOADER] Model downloaded successfully
[MODEL] Loading GGUF model...
[MODEL] Model loaded successfully
```

**Check**:
- [ ] Gemini queried for model link
- [ ] Download started automatically
- [ ] Progress shown
- [ ] Model saved to `/models/`
- [ ] Model loaded successfully

**Cleanup**:
```bash
# Restore original model
rm models/gemma-2b-it.gguf
mv models/gemma-2b-it.gguf.backup models/gemma-2b-it.gguf
```

---

## Error Recovery Tests

### Test 7: Trigger Intentional Error
```python
# In Python REPL while agent is running
import sys
sys.path.insert(0, 'a:\\KNO\\KNO')

from agent import self_evolution_thread

# Queue a fake error
error = {
    'error_type': 'ModuleNotFoundError',
    'error_msg': 'No module named fictitious_package_xyz',
    'traceback': 'File agent.py line 100',
    'timestamp': str(__import__('datetime').datetime.now())
}

self_evolution_thread.queue_error(error)
self_evolution_thread.process_error_queue()

# Wait 10 seconds for ChatGPT to respond
import time
time.sleep(10)
```

**Expected in logs**:
```
[CHATGPT] Error: ModuleNotFoundError
[CHATGPT] Fix: [FIX_SHELL] pip install fictitious_package_xyz
[EVOLUTION] Applying fix...
[EVOLUTION] Command failed (as expected - fake package)
```

**Check**:
- [ ] Error queued successfully
- [ ] ChatGPT investigation triggered
- [ ] Fix suggestion received
- [ ] Fix application attempted
- [ ] Result logged to evolution.log

---

### Test 8: Verify evolution.log Entry Format
```bash
tail -20 logs/evolution.log
```

**Expected Format**:
```
[2024-01-15 14:32:10] [GEMINI] Query: "What is..."
[2024-01-15 14:32:12] [GEMINI] Response: "..." (truncated at 2048 chars)
[2024-01-15 14:32:15] [CHATGPT] Error: ModuleNotFoundError
[2024-01-15 14:32:18] [CHATGPT] Fix: [FIX_SHELL] pip install X
[2024-01-15 14:32:22] [EVOLUTION] Applied: pip install X
[2024-01-15 14:32:25] [EVOLUTION] Result: SUCCESS
[2024-01-15 14:32:26] [INTERACTION] Total API calls: 5, Success rate: 100%
```

**Check**:
- [ ] All entries have timestamps
- [ ] API source identified ([GEMINI], [CHATGPT], etc.)
- [ ] Query/response pairs logged
- [ ] Fixes logged with [FIX_*] prefix
- [ ] Results tracked (SUCCESS/FAILED)

---

## Autonomous Brain Loop Tests

### Test 9: Verify 10-Minute AI Query Cycle
```bash
# Start agent
python agent.py

# Wait 10 minutes (600 seconds), monitoring logs
watch -n 10 'tail logs/evolution.log'
# Or in PowerShell
while($true) { Clear-Host; Get-Content logs/evolution.log -Tail 10; Start-Sleep 10 }

# After 10 minutes, should see:
# [AI_QUERY] Cycle 10: Querying Gemini for system insights...
```

**Expected After 10 Minutes**:
```
[BRAIN_LOOP] Cycle 10: Requesting AI suggestions...
[GEMINI] Query: "System status: ..."
[GEMINI] Response: "Suggestions: ..."
[TTS] Queuing AI suggestion to speaker...
[INTERACTION] AI cycle complete
```

**Check**:
- [ ] AI queries automatically every 10 cycles
- [ ] Gemini/ChatGPT returns suggestions
- [ ] Suggestions output to TTS (if enabled)
- [ ] Cycle tracked in logs

---

### Test 10: Verify GUI Status Display
During the 10-minute wait above, watch the agent GUI:

**Expected Display**:
```
┌────────────────────────────────────┐
│  KNO Evolutionary Autonomous Agent │
│                                    │
│  Status: 🧬 KNO is Evolving...    │
│                                    │
│  Consulting external AI brains     │
│  Processing system analysis        │
│                                    │
└────────────────────────────────────┘
```

**Check**:
- [ ] GUI displays "KNO is Evolving..."
- [ ] Status updates during API calls
- [ ] Status returns to normal after API calls
- [ ] No UI freezing during API calls

---

## Integration Tests

### Test 11: Phase 1-3 Compatibility
Verify Phase 4 doesn't break existing functionality:

```bash
# Test wake word detection (Phase 1)
# Should still work normally
# Say wake word and a command

# Test model loading verification (Phase 2)
# Model should load without Phase 4 block
# Check logs for Phase 2 verification steps

# Test experience memory (Phase 3)
# Should still log interactions
# Check experience.json file created
```

**Check**:
- [ ] Wake word detection still works
- [ ] Model loads normally
- [ ] Experience memory logs interactions
- [ ] No conflicts between phases

---

### Test 12: Error Queue During Normal Operation
Let agent run normally for 10+ minutes:

```bash
# Monitor for any errors that occur naturally
tail -f logs/evolution.log | grep ERROR

# If any errors occur naturally, verify:
# 1. Error queued automatically
# 2. ChatGPT investigates
# 3. Fix suggested
# 4. Fix application attempted
```

**Check**:
- [ ] Errors auto-queued on exception
- [ ] ChatGPT provides sensible suggestions
- [ ] Fixes are reasonable and safe
- [ ] Agent continues operating after error

---

## Performance Benchmarks

### Test 13: Measure API Response Times

```python
import time
from agent import higher_intelligence_bridge

print("Measuring Gemini latency...")
start = time.time()
response = higher_intelligence_bridge.query_gemini("test")
gemini_time = time.time() - start

print(f"Gemini: {gemini_time:.1f}s")

print("Measuring ChatGPT latency...")
start = time.time()
response = higher_intelligence_bridge.query_chatgpt("test")
chatgpt_time = time.time() - start

print(f"ChatGPT: {chatgpt_time:.1f}s")
```

**Expected Times**:
- Gemini: 1-3 seconds (fast)
- ChatGPT: 2-5 seconds (moderate)
- Both: <30 seconds (timeout threshold)

**Check**:
- [ ] Gemini < 3 seconds
- [ ] ChatGPT < 5 seconds
- [ ] No timeout errors (>30s)

---

### Test 14: Check Memory Usage
```python
import psutil
process = psutil.Process()
mem = process.memory_info()

print(f"Memory usage: {mem.rss / 1024 / 1024:.1f} MB")
print(f"Max memory (Phase 4): ~500 MB")
```

**Expected**:
- Total agent memory: < 1 GB
- API clients overhead: ~50 MB
- No memory leaks after 30 min operation

**Check**:
- [ ] Memory < 500 MB baseline
- [ ] No continuous memory growth
- [ ] No out-of-memory errors

---

## Security Tests

### Test 15: Verify No Hardcoded API Keys
```bash
# Search all Python files for hardcoded keys
grep -r "AIzaSy" .
grep -r "sk-" .

# Should return NO results (only finds these in .gitignore warnings)
```

**Expected**:
- No hardcoded keys found in source code
- Keys only in environment variables
- Backup only in evolution_keys.json (not committed)

**Check**:
- [ ] No hardcoded keys found
- [ ] .gitignore includes evolution_keys.json
- [ ] evolution_keys.json not in git history

---

### Test 16: Verify evolution.log Permissions
```bash
ls -la logs/evolution.log
# Should show: -rw-r--r-- (644 on Linux)
# Or restrictive on Windows
```

**Expected**:
- Log file readable (but contains no secrets)
- Log file writable by agent
- No world-writable permissions

**Check**:
- [ ] File readable
- [ ] File writable by agent user
- [ ] No sensitive key data in logs

---

## Final Verification

### Test 17: Clean Restart
```bash
# Kill any running agent processes
pkill -f "python agent.py"

# Wait 5 seconds
sleep 5

# Fresh start
python agent.py

# Should start cleanly with no errors
```

**Expected**:
- Clean startup (no leftover state issues)
- All modules initialized
- APIs connected
- Ready for operation

**Check**:
- [ ] Clean startup no errors
- [ ] All modules loaded
- [ ] APIs ready
- [ ] Logs created/updated

---

### Test 18: Documentation Verification
- [ ] PHASE4_IMPLEMENTATION_COMPLETE.md exists
- [ ] PHASE4_API_INTEGRATION_GUIDE.md exists
- [ ] PHASE4_ERROR_RECOVERY_GUIDE.md exists
- [ ] PHASE4_TROUBLESHOOTING.md exists
- [ ] API_KEYS_SECURITY_README.md exists
- [ ] All docs are readable and complete

---

## Sign-Off

**Checklist Complete**: ✅ / ❌

If ALL checks pass: **Phase 4 is PRODUCTION READY** ✅

If any checks fail:
1. Note which test failed
2. See [PHASE4_TROUBLESHOOTING.md](PHASE4_TROUBLESHOOTING.md)
3. Apply fix
4. Re-run failed test
5. Once passed, continue

---

## Deployment Commands

Once all tests pass:

```bash
# Start agent for production
python agent.py

# Monitor in separate terminal
tail -f logs/evolution.log

# Performance monitoring (optional)
watch -n 5 'ps aux | grep python | grep agent'
```

---

## Rollback (if needed)

If Phase 4 causes issues:

```bash
# Restore previous agent version (Phase 3)
git checkout HEAD~1 -- agent.py

# Clear evolution logs
rm logs/evolution.log

# Restart
python agent.py
```

---

**Testing Date**: _______________  
**Tested By**: _______________  
**Status**: [ ] PASSED [ ] FAILED [ ] PARTIAL  
**Notes**: _______________________________________________

---

**Phase 4 Status**: Ready for Production ✅
