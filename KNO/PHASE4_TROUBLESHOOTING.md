# Phase 4: Troubleshooting Guide - Common Issues & Fixes

Quick reference for Phase 4 setup and runtime issues.

---

## Quick Reference

| Issue | Symptom | Solution |
|-------|---------|----------|
| API keys missing | "GEMINI_API_KEY not set" | [Go to: API Key Setup](#api-key-setup-issues) |
| API 401 error | "Invalid API key" | [Go to: Authentication Issues](#authentication-issues) |
| No evolution.log | Logs not created | [Go to: Logging Issues](#logging-issues) |
| Error not fixed | "EVOLUTION: FAILED" | [Go to: Fix Application Issues](#fix-application-issues) |
| Slow API response | 30+ second delays | [Go to: Performance Issues](#performance-issues) |

---

## API Key Setup Issues

### Problem: ❌ "GEMINI_API_KEY environment variable not set"

**What it means**: 
- Gemini API key not configured in environment
- Agent can still use ChatGPT (fallback), but not Gemini

**Solution A: Permanent Setup (Recommended)**

```powershell
# PowerShell - Set permanent environment variable
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "AIzaSyD...", "User")

# Verify
$env:GEMINI_API_KEY

# Restart PowerShell and Python for changes to take effect
```

**Solution B: Session Setup (Temporary)**

```powershell
# Current session only (lost when terminal closes)
$env:GEMINI_API_KEY = "AIzaSyD..."
$env:OPENAI_API_KEY = "sk-..."

python agent.py
```

**Solution C: evolution_keys.json Backup**

Create file: `a:/KNO/KNO/evolution_keys.json`

```json
{
  "gemini_api_key": "AIzaSyD...",
  "openai_api_key": "sk-..."
}
```

Then restart agent.

**Verify the Fix**:
```python
import os
print(f"Gemini: {os.getenv('GEMINI_API_KEY', 'NOT SET')}")
print(f"ChatGPT: {os.getenv('OPENAI_API_KEY', 'NOT SET')}")
```

---

### Problem: ❌ "OPENAI_API_KEY environment variable not set"

**What it means**:
- ChatGPT API not configured
- Error recovery (Phase 4 core feature) won't work
- Gemini queries work, but ChatGPT fallback unavailable

**Solution**:
Follow same steps as Gemini (above), but for OpenAI

```powershell
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")
```

---

### Problem: ❌ "Both API keys failed - No external AI available"

**What it means**:
- Both Gemini AND ChatGPT are not configured
- Higher intelligence bridge disabled
- Error recovery disabled

**Solution**:
Configure at least ONE API key (preferably both):

```powershell
# At minimum, configure Gemini (free tier available)
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your-key", "User")

# Then restart
python agent.py
```

---

## Authentication Issues

### Problem: ❌ API Error 401 - "Unauthorized"

**What it means**:
- API key is invalid or expired
- Key cannot authenticate with API

**Log Example**:
```
[GEMINI] Query: "What is..."
[GEMINI] ERROR 401: Invalid API key
[CHATGPT] Query: "What is..."
[CHATGPT] Response: "..." (fallback succeeded)
```

**Solution A: Verify Key is Correct**

1. Copy key again from [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Check for extra spaces: `"AIzaSyD...xYz "`
3. Set environment variable again
4. Restart terminal and Python

```powershell
# Remove old key
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", $null, "User")

# Set new key
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "AIzaSyDyourfullkeyhere", "User")

# Verify
$env:GEMINI_API_KEY
```

**Solution B: Check Key Expiration**

- Keys don't expire by default
- But API access can be revoked
- Go to [Google Cloud Console](https://console.cloud.google.com)
- Check: API enabled
- Check: Billing enabled

**Solution C: Use ChatGPT While Fixing Gemini**

```python
from agent import higher_intelligence_bridge

# Gemini will fail with 401
# ChatGPT fallback will activate automatically
response = higher_intelligence_bridge.solve_complex_problem("test")
# Works via automatic fallback
```

**Solution D: Regenerate API Key**

If still getting 401:
1. Delete current key on [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Create new key
3. Update environment variable
4. Test: `python test_agent.py`

---

### Problem: ❌ API Error 403 - "Forbidden"

**What it means**:
- API access denied (usually billing issue)
- Account not authorized

**Log Example**:
```
[OPENAI] Query: "..."
[OPENAI] ERROR 403: Billing required
```

**Solution: Set Up Billing**

For OpenAI/ChatGPT:
1. Go to [OpenAI Billing Settings](https://platform.openai.com/account/billing/overview)
2. Add payment method (credit card)
3. Wait 5-10 minutes for activation
4. Try again

For Google/Gemini:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Billing → Link a billing account
3. Or use free tier (default, limited to 60 req/min)

---

### Problem: ❌ API Error 429 - "Rate Limited"

**What it means**:
- Too many requests sent too quickly
- Hit API rate limit (usually 60/min for free tier)

**Log Example**:
```
[GEMINI] ERROR 429: Rate limit exceeded
[CHATGPT] Query fallback...
[CHATGPT] Response: "..."
```

**Solution A: Wait For Rate Limit Reset**

```bash
# Rate limits reset after 1 minute
# Just wait and try again
wait 60 seconds
python agent.py
```

**Solution B: Reduce Query Frequency**

In [agent.py](agent.py), find `autonomous_brain_loop()`:

```python
# Default: Query AI every 10 cycles (10 minutes)
evolution_query_cycle = 0
if evolution_query_cycle % 10 == 0:  # Every 10 cycles
    # Change % 10 to % 30 for every 30 cycles (30 min)
    response = gemini_api.query(...)
```

**Solution C: Upgrade API Tier**

- **Gemini**: Upgrade to [Google AI Studio Pro](https://aistudio.google.com) for higher limits
- **ChatGPT**: Upgrade OpenAI account for higher rate limits

---

## Configuration Issues

### Problem: ❌ "evolution_keys.json not found"

**What it means**:
- Backup credential method unavailable
- Environment variables still used (primary)
- Just a warning, not an error

**Log Example**:
```
[BRAIN] evolution_keys.json NOT found (using env vars)
```

**Solution** (Optional): Create file if you want backup method

```json
{
  "gemini_api_key": "AIzaSyD...",
  "openai_api_key": "sk-..."
}
```

Then:
```bash
echo "evolution_keys.json" >> .gitignore  # Don't commit!
chmod 600 evolution_keys.json  # Restrict permissions
```

---

### Problem: ❌ "Invalid JSON in evolution_keys.json"

**What it means**:
- File exists but is malformed
- Backup method disabled
- Agent falls back to environment variables

**Log Example**:
```
[BRAIN] ERROR: evolution_keys.json is invalid JSON
[BRAIN] Falling back to environment variables...
```

**Solution: Fix JSON Format**

Open `evolution_keys.json` and verify:

```json
{
  "gemini_api_key": "AIzaSyD...",
  "openai_api_key": "sk-..."
}
```

Common mistakes:
- ❌ Missing quotes: `gemini_api_key: "..."`
- ❌ Trailing comma: `"key": "value",}`
- ❌ Single quotes: `'key': '...'`

Use [JSON Validator](https://jsonlint.com) to check

---

## Logging Issues

### Problem: ❌ "logs/evolution.log not created"

**What it means**:
- No API calls made yet (normal if running fresh agent)
- Or: Logging is working but file not visible yet

**Solution A: Wait For First API Query**

Default: Queries AI every 10 cycles (~10 minutes)

```bash
# Run agent, wait 10+ minutes
python agent.py

# In another terminal, check for log file
ls -la logs/evolution.log

# If exists but empty, wait more
tail -f logs/evolution.log
```

**Solution B: Trigger API Query Manually**

```python
from agent import higher_intelligence_bridge

# Force a Gemini query
response = higher_intelligence_bridge.query_gemini("test")

# Log file should appear now
```

**Solution C: Verify logs/ Directory Exists**

```bash
# Check if logs directory exists
ls -la logs/

# If missing, create it
mkdir -p logs

# Restart agent
python agent.py
```

---

### Problem: ❌ "evolution.log not writable"

**What it means**:
- File has wrong permissions
- Agent can't write to it

**Log Example**:
```
[EVOLUTION] ERROR: Cannot write to logs/evolution.log
```

**Solution: Fix Permissions**

```bash
# Linux/Mac
chmod 666 logs/evolution.log

# Windows PowerShell
$acl = Get-Acl 'logs\evolution.log'
$acl.SetAccessRuleProtection($false, $false)
Set-Acl 'logs\evolution.log' -AclObject $acl
```

Or delete and recreate:
```bash
rm logs/evolution.log
python agent.py  # Will create new file
```

---

### Problem: ❌ "evolution.log growing too large"

**What it means**:
- Log file is getting very large (100MB+)
- Might slow down agent

**Solution: Archive Old Logs**

```bash
# Rename current log
mv logs/evolution.log logs/evolution.log.backup

# Start fresh log
touch logs/evolution.log

# Create new Python script to parse old log
python -c "
import gzip
with open('logs/evolution.log.backup', 'rb') as f_in:
    with gzip.open('logs/evolution.log.backup.gz', 'wb') as f_out:
        f_out.writelines(f_in)
"

# Delete original backup
rm logs/evolution.log.backup
```

---

## Model Issues

### Problem: ❌ "GGUF model not found at startup"

**What it means**:
- Model file missing from `/models/`
- Auto-downloader should activate
- If not, download failed

**Log Example**:
```
[STARTUP] LLAMA model not found
[DOWNLOADER] Searching for latest gemma-2b-it...
[DOWNLOADER] Found: https://huggingface.co/...
[DOWNLOADER] Downloading... 50%
[ERROR] Download failed: Connection timeout
```

**Solution A: Manual Download**

Use Gemini API to find link:
```python
from agent import evolutionary_downloader

# This finds and downloads automatically
evolutionary_downloader.evolutionary_download_model()
```

**Solution B: Manual Model Download**

1. Visit [Hugging Face](https://huggingface.co/models?search=gemma)
2. Search: `gemma-2b-it-GGUF`
3. Download `.gguf` file
4. Save to: `a:/KNO/KNO/models/gemma-2b-it.gguf`
5. Restart agent

**Solution C: Verify Download Location**

```bash
# Check if file exists
ls -la models/gemma-2b-it.gguf

# Check file size (should be 1-2 GB)
du -h models/gemma-2b-it.gguf

# If exists but wrong size, delete and redownload
rm models/gemma-2b-it.gguf
python agent.py  # Re-triggers auto-download
```

---

### Problem: ❌ "Model loads but inference slow"

**What it means**:
- Model response takes 30+ seconds
- Could be normal (depends on hardware) or issue

**Solution A: Check System Resources**

```python
import psutil

print(f"CPU Usage: {psutil.cpu_percent()}%")
print(f"Memory: {psutil.virtual_memory()}")
print(f"Disk I/O: {psutil.disk_io_counters()}")
```

**Solution B: Enable GPU Acceleration** (if available)

If you have NVIDIA GPU:
```bash
pip install llama-cpp-python[cuda]
```

Then restart agent for faster inference.

**Solution C: Reduce Model Complexity**

Current: `gemma-2b-it` (2B parameters)
- If too slow: Use `gemma-2b-it-q4_0` (quantized, faster)
- If too accurate needed: Use `gemma-7b-it` (slower, better)

---

## Fix Application Issues

### Problem: ❌ "Fix suggested but not applied"

**What it means**:
- ChatGPT suggested fix
- Auto-application failed
- Error still occurs

**Log Example**:
```
[CHATGPT] Fix: [FIX_SHELL] pip install numpy==1.24.3
[EVOLUTION] Applying: pip install numpy==1.24.3
[EVOLUTION] ERROR: Command timed out after 30 seconds
[EVOLUTION] Fix failed - see logs for details
```

**Solution A: Apply Fix Manually**

```bash
# Apply the exact command suggested in logs
pip install numpy==1.24.3

# Restart agent
python agent.py
```

**Solution B: Increase Timeout**

In [agent.py](agent.py), SelfEvolutionThread class:

```python
# Default: 30 seconds
APPLY_TIMEOUT = 30

# Change to 60 for slow systems
APPLY_TIMEOUT = 60
```

**Solution C: Check Subprocess Permissions**

```bash
# Verify pip works manually
pip --version
pip install requests  # Test install

# If fails, might need admin/sudoedit
sudo pip install numpy
```

---

### Problem: ❌ "Fix applied but error recurs"

**What it means**:
- Fix worked temporarily
- Same error happening again
- Indicates root cause not fixed

**Log Example**:
```
[CHATGPT] Fix: [FIX_SHELL] pip install numpy==1.24.3
[EVOLUTION] Fix applied successfully
[20 minutes later]
[EVOLUTION] ERROR: Same ImportError recurs!
```

**Solution A: Investigate Root Cause**

```python
# Look for pattern in logs
grep "ImportError" logs/evolution.log

# If repeating, suggest to ChatGPT for further analysis
higher_intelligence_bridge.query_chatgpt(
    "numpy ImportError keeps recurring. Root cause?"
)
```

**Solution B: Check for Version Lock**

```bash
# List all numpy versions
pip index versions numpy

# Maybe specific package requires specific numpy
pip show numpy  # Check current
pip show scipy  # Check scipy requirement
```

**Solution C: Fresh Install**

```bash
# Remove package completely
pip uninstall numpy

# Fresh install
pip install numpy
```

---

### Problem: ❌ "[FIX_CODE] applied but modified something unintended"

**What it means**:
- Code fix applied, but changed more than expected
- Side effects or unintended edits

**Solution A: Revert Changes**

```bash
# Restore from git
git checkout agent.py

# Or restart Python (code changes lost)
python agent.py
```

**Solution B: Review ChatGPT Fix**

Look in `logs/evolution.log` for exact fix:
```
[CHATGPT] Fix: [FIX_CODE]
[Code snippet shown]
```

**Solution C: Disable Auto-Apply for That Error Type**

In [agent.py](agent.py), SelfEvolutionThread:

```python
SKIP_AUTOAPPLY = [
    'error_type_to_skip',
    'another_error_type'
]
```

---

## Performance Issues

### Problem: ❌ "API queries taking 30+ seconds"

**What it means**:
- Normal latency is 2-5 seconds
- 30+ seconds indicates timeout or network issue

**Log Example**:
```
[11:32:10] [GEMINI] Query started
[11:32:40] [GEMINI] Timeout after 30 seconds
[11:32:42] [CHATGPT] Query fallback started
[11:32:47] [CHATGPT] Response received
```

**Solution A: Check Network**

```bash
# Test internet speed
ping 8.8.8.8

# Test API endpoint specifically
curl -I https://generativelanguage.googleapis.com
curl -I https://api.openai.com

# Check for firewall blocks
tracert api.openai.com
```

**Solution B: Increase Timeout**

In [agent.py](agent.py), HigherIntelligenceBridge:

```python
TIMEOUT = 30  # Change to 60
```

**Solution C: Check API Status**

- [Google Status Page](https://status.google.com)
- [OpenAI Status Page](https://status.openai.com)

---

### Problem: ❌ "Agent running but very slow overall"

**What it means**:
- Not just APIs, but full agent is sluggish
- Could be memory/CPU issue or model loading

**Solution A: Check System Resources**

```bash
# Windows PowerShell
Get-Process python | Select-Object ProcessName, WorkingSet, CPU

# Linux
ps aux | grep python
top -p $(pgrep python)

# If memory > 5GB or CPU > 80%, issue with agent
```

**Solution B: Reduce Agent Workload**

- Reduce batch size in config.json
- Increase sleep time between brain cycles
- Disable audio processing if not needed
- Run on machine with more RAM

**Solution C: Profile Agent**

```python
import cProfile
import pstats

cProfile.run('agent.main()', 'agent_profile.prof')

stats = pstats.Stats('agent_profile.prof')
stats.sort_stats('cumulative').print_stats(10)
```

---

## Network Issues

### Problem: ❌ "Connection refused" to API

**What it means**:
- Cannot establish connection to API server
- Firewall, network, or API down

**Log Example**:
```
[GEMINI] ConnectionError: Connection refused
[CHATGPT] ConnectionError: Connection refused
```

**Solution A: Check Network Connectivity**

```bash
# Test basic internet
ping google.com

# Test specific API
curl https://api.openai.com/health  # or similar

# If fails, check:
# 1. Internet connection
# 2. Firewall rules
# 3. VPN (if using)
```

**Solution B: Check if API is Down**

- Visit [Google Status](https://status.google.com)
- Visit [OpenAI Status](https://status.openai.com)
- Wait for service restoration

**Solution C: Configure Proxy** (if behind corporate firewall)

```python
# In agent.py, add proxy configuration
import os
os.environ['HTTP_PROXY'] = 'http://proxy.company.com:8080'
os.environ['HTTPS_PROXY'] = 'https://proxy.company.com:8080'
```

---

## Debugging

### Enable Verbose Logging

```bash
# Set environment variable for debug output
$env:DEBUG = "1"
python agent.py

# Or in Python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Full Error Trace

```bash
# Show full stack trace instead of summary
python -u agent.py 2>&1 | tee full_debug.log

# Then analyze
grep ERROR full_debug.log
grep Traceback full_debug.log
```

### Test Individual Components

```python
# Test just Gemini
from agent import higher_intelligence_bridge
print(higher_intelligence_bridge.query_gemini("test"))

# Test just ChatGPT
print(higher_intelligence_bridge.query_chatgpt("test"))

# Test error queuing
from agent import self_evolution_thread
self_evolution_thread.queue_error({'error': 'test'})
```

---

## Getting Help

1. **Check the logs**: `tail -f logs/evolution.log`
2. **Search this guide**: Use Ctrl+F to find your issue
3. **Read related docs**:
   - [PHASE4_IMPLEMENTATION_COMPLETE.md](PHASE4_IMPLEMENTATION_COMPLETE.md) - Overview
   - [PHASE4_API_INTEGRATION_GUIDE.md](PHASE4_API_INTEGRATION_GUIDE.md) - Setup
   - [PHASE4_ERROR_RECOVERY_GUIDE.md](PHASE4_ERROR_RECOVERY_GUIDE.md) - Error handling
4. **Manual fix**: Apply suggestions from ChatGPT in logs manually

---

**Last Updated**: Present  
**Version**: Phase 4.0  
**Status**: Ready for production troubleshooting
