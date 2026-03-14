# Phase 4: API Integration Guide - Step-by-Step Setup

This guide walks through setting up and using Phase 4's external AI brain integration.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [API Key Acquisition](#api-key-acquisition)
3. [Environment Setup](#environment-setup)
4. [Configuration Verification](#configuration-verification)
5. [Using Phase 4 Features](#using-phase-4-features)
6. [Advanced Configuration](#advanced-configuration)

---

## Prerequisites

- ✅ agent.py v5.0+ (Phase 4 implementation)
- ✅ Python 3.8+ with venv configured
- ✅ `requests` library (auto-installed)
- ✅ Internet connection for API calls
- ✅ Valid Gemini and/or ChatGPT API keys

### Check Prerequisites
```bash
# Verify Python version
python --version  # Should be 3.8+

# Verify requests library
pip list | grep requests

# Verify internet
ping api.google.com
```

---

## API Key Acquisition

### Option 1: Google Gemini API (RECOMMENDED)

**Why Gemini?** Faster responses, free tier available, generally cheaper

#### Step 1: Get API Key
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Click **"Create API Key"** → **"Create API key in new project"**
3. Copy the API key (looks like: `AIzaSyD...`)
4. ⚠️ **Keep this SECRET** - Never share or commit to git

#### Step 2: Test API Key (Optional)
```bash
# Replace YOUR_KEY with actual key
$env:GEMINI_API_KEY = "AIzaSyD..."
python -c "
import requests
headers = {'Content-Type': 'application/json'}
data = {'contents': [{'parts': [{'text': 'Hello'}]}]}
resp = requests.post(
    'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + os.getenv('GEMINI_API_KEY'),
    json=data, headers=headers
)
print('Status:', resp.status_code)
"
```

### Option 2: OpenAI ChatGPT API (FALLBACK)

**Why ChatGPT?** Highly reliable, powerful reasoning, used as automatic fallback

#### Step 1: Get API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in (create account if needed)
3. Click **"Create new secret key"**
4. Copy the key (looks like: `sk-...`)
5. ⚠️ **Keep this SECRET** - Don't share or commit

#### Step 2: Set Up Billing
1. Go to [Billing Settings](https://platform.openai.com/account/billing/overview)
2. Add payment method
3. Set usage limits (recommended: $5/month)
4. Monitor usage in dashboard

#### Step 3: Test API Key (Optional)
```bash
$env:OPENAI_API_KEY = "sk-..."
python -c "
import requests
headers = {
    'Authorization': 'Bearer ' + os.getenv('OPENAI_API_KEY'),
    'Content-Type': 'application/json'
}
data = {
    'model': 'gpt-3.5-turbo',
    'messages': [{'role': 'user', 'content': 'Hello'}]
}
resp = requests.post(
    'https://api.openai.com/v1/chat/completions',
    json=data, headers=headers
)
print('Status:', resp.status_code)
"
```

---

## Environment Setup

### Method 1: Permanent Environment Variables (RECOMMENDED)

**PowerShell** (Windows):
```powershell
# Set persistent environment variables
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "AIzaSyD...", "User")
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")

# Verify they were set
$env:GEMINI_API_KEY
$env:OPENAI_API_KEY

# Restart PowerShell for changes to take effect
```

**Bash** (Linux/Mac):
```bash
# Add to ~/.bashrc or ~/.bash_profile
export GEMINI_API_KEY="AIzaSyD..."
export OPENAI_API_KEY="sk-..."

# Load immediately
source ~/.bashrc
```

### Method 2: Local evolution_keys.json (BACKUP)

Create file: `a:/KNO/KNO/evolution_keys.json`

```json
{
  "gemini_api_key": "AIzaSyD...",
  "openai_api_key": "sk-..."
}
```

**Security**: Restrict file permissions
```bash
# Linux/Mac
chmod 600 evolution_keys.json

# Windows PowerShell
$file = 'evolution_keys.json'
$acl = Get-Acl $file
$acl.SetAccessRuleProtection($true, $true)
Set-Acl -Path $file -AclObject $acl
```

**Add to .gitignore**:
```bash
echo "evolution_keys.json" >> .gitignore
```

### Method 3: Temporary Session (TESTING ONLY)

```bash
# PowerShell (session-only)
$env:GEMINI_API_KEY = "AIzaSyD..."
$env:OPENAI_API_KEY = "sk-..."

# Bash (session-only)
export GEMINI_API_KEY="AIzaSyD..."
export OPENAI_API_KEY="sk-..."
```

---

## Configuration Verification

### Test 1: Verify Environment Variables

```python
import os

gemini = os.getenv('GEMINI_API_KEY')
openai = os.getenv('OPENAI_API_KEY')

print(f"Gemini configured: {bool(gemini)}")
print(f"ChatGPT configured: {bool(openai)}")

if not gemini and not openai:
    print("ERROR: No API keys configured!")
    print("See API_KEYS_SECURITY_README.md for setup")
```

### Test 2: Verify API Connectivity

```python
# Run this in Python
from agent import higher_intelligence_bridge

# Test Gemini
print("Testing Gemini API...")
response = higher_intelligence_bridge.query_gemini("What is 2+2?")
print(f"Gemini response: {response[:100]}...")

# Test ChatGPT fallback
print("\nTesting ChatGPT API...")
response = higher_intelligence_bridge.query_chatgpt("What is 2+2?")
print(f"ChatGPT response: {response[:100]}...")
```

### Test 3: Verify evolution.log Setup

```bash
# Start agent
python agent.py

# In another terminal, monitor logs
tail -f logs/evolution.log

# Within 10 minutes, you should see:
# [2024-01-15 14:32:10] [GEMINI] Query: ...
```

### Test 4: Manual Error Queuing

```python
from agent import self_evolution_thread

# Queue an error for investigation
error_info = {
    'error_type': 'ImportError',
    'error_msg': 'No module named numpy',
    'traceback': 'File agent.py, line 42'
}

self_evolution_thread.queue_error(error_info)
self_evolution_thread.process_error_queue()

# Check logs
# tail -f logs/evolution.log
```

---

## Using Phase 4 Features

### Feature 1: Query External AI for Complex Problems

```python
from agent import higher_intelligence_bridge

# Query Gemini (or ChatGPT on fallback)
problem = "Write Python code to optimize numpy matrix multiplication"
solution = higher_intelligence_bridge.solve_complex_problem(
    problem=problem,
    context="Current system has numpy 1.24.3"
)

print(f"AI Solution:\n{solution}")
```

**Automatic Integration**: When local model is uncertain, `autonomous_brain_loop()` automatically queries this every 10 cycles.

### Feature 2: Auto-Download Latest Models

```python
from agent import evolutionary_downloader

# Automatically finds latest gemma-2b-it and downloads
print("Searching for latest model...")
success = evolutionary_downloader.evolutionary_download_model()

if success:
    print("Model downloaded successfully!")
else:
    print("Model download failed")
```

**Automatic Integration**: If model missing, called at startup to download automatically.

### Feature 3: Autonomous Error Recovery

```python
from agent import self_evolution_thread

# Manually queue error (or it's called automatically on exceptions)
error = {
    'error_type': 'UnboundLocalError',
    'error_msg': 'local variable referenced before assignment',
    'code_location': 'agent.py:1234'
}

# Queue the error
self_evolution_thread.queue_error(error)

# Process errors (runs in background automatically)
self_evolution_thread.process_error_queue()

# Check logs/evolution.log for fix details
```

**Automatic Integration**: `chat_and_respond()` error handler automatically queues errors.

---

## Advanced Configuration

### Custom Timeouts

Edit in [agent.py](agent.py):

```python
class HigherIntelligenceBridge:
    TIMEOUT = 30  # Change to 60 for slower connections
    API_RETRY_ATTEMPTS = 3  # Change to 5 for unreliable networks
```

### Custom Retry Strategy

```python
# Exponential backoff configuration
BASE_DELAY = 1  # Start 1 second
MAX_DELAY = 16  # Cap at 16 seconds
# Backoff: 1s → 2s → 4s → 8s → 16s
```

### Custom Model for ChatGPT Fallback

```python
# Change from gpt-3.5-turbo to gpt-4 (more capable, more expensive)
MODEL = "gpt-4"  # Instead of "gpt-3.5-turbo"
```

### Logging Depth

```python
# In evolution.log, control verbosity:
# VERBOSE: Log full API requests/responses
# NORMAL: Log query type + cost
# MINIMAL: Log only errors
```

### Rate Limiting

```python
# If hitting API rate limits, add delay:
import time
time.sleep(1)  # Wait 1 second between API calls
```

---

## Cost Estimation

### Gemini API (Google)

| Tier | Cost | Requests/month |
|------|------|---------|
| Free | $0 | 60/min |
| Standard | $0.0005/1k tokens | ~10k/month |
| Pro | $20/month | Unmetered |

**Typical Usage**:
- 1 AI query per 10 minutes = 144/day = 4,320/month
- ~500 tokens per query average = 2.16M tokens
- Cost: ~$1.08/month (free tier often sufficient)

### ChatGPT API (OpenAI)

| Model | Cost | Performance |
|-------|------|-------------|
| GPT-3.5-turbo | $0.0015/1k tokens input | Fast, good for fixes |
| GPT-4 | $0.03/1k tokens input | Slower, better reasoning |

**Typical Usage**:
- 1 error per 2 hours = 12/day = 360/month
- ~200 tokens per error analysis
- ~1,000 tokens per response
- Cost: ~$0.54/month (gpt-3.5-turbo)

**Total Estimated Cost**: $1-2/month

---

## Troubleshooting API Setup

### Issue: "API key not found"
```
❌ Error: GEMINI_API_KEY environment variable not set
✅ Solution: 
   1. Set environment variable (see Environment Setup)
   2. Restart Python/terminal
   3. Verify with: echo $env:GEMINI_API_KEY
```

### Issue: "401 Unauthorized"
```
❌ Error: Invalid API key provided
✅ Solution:
   1. Copy API key again (check for extra spaces)
   2. Verify key hasn't expired
   3. Try ChatGPT fallback (might work while Gemini fails)
```

### Issue: "429 Rate Limited"
```
❌ Error: Too many API requests
✅ Solution:
   1. Wait 60 seconds
   2. Reduce query frequency
   3. Upgrade to paid tier for higher limits
```

### Issue: "500 Internal Server Error"
```
❌ Error: API service temporarily unavailable
✅ Solution:
   1. Automatically retried 3x with backoff
   2. Falls back to ChatGPT
   3. Check api.status.google.com or openai.com/status
```

### Issue: "Connection timeout"
```
❌ Error: Network unreachable or API unresponsive
✅ Solution:
   1. Check internet: ping 8.8.8.8
   2. Check firewall allows HTTPS outbound
   3. Retry manually in 30+ seconds
```

---

## Security Best Practices

1. **NEVER commit API keys** to git
   ```bash
   # Add to .gitignore
   echo "evolution_keys.json" >> .gitignore
   ```

2. **Use environment variables** (not config files)
   ```bash
   # DO: Use env var (secure)
   $env:GEMINI_API_KEY = "secret"
   
   # DON'T: Store in file
   gemini_key = "secret"  # In source code
   ```

3. **Rotate keys regularly** (monthly recommended)
   - Regenerate on API dashboard
   - Update environment variable
   - Delete old key

4. **Monitor API usage** monthly
   - Check billing dashboard
   - Set spending alerts
   - Investigate unusual spikes

5. **Enable API key restrictions** (if available)
   - Restrict to specific IP ranges
   - Restrict to specific APIs (Gemini only, etc.)
   - Add expiration dates

See [API_KEYS_SECURITY_README.md](API_KEYS_SECURITY_README.md) for detailed security setup.

---

## Next Steps

1. ✅ Follow [Environment Setup](#environment-setup)
2. ✅ Run [Configuration Verification](#configuration-verification) tests
3. ✅ Start agent: `python agent.py`
4. ✅ Monitor: `tail -f logs/evolution.log`
5. 📚 Read [PHASE4_ERROR_RECOVERY_GUIDE.md](PHASE4_ERROR_RECOVERY_GUIDE.md) for error handling
6. 📚 Read [PHASE4_TROUBLESHOOTING.md](PHASE4_TROUBLESHOOTING.md) for common issues

---

**Questions?** Check [PHASE4_TROUBLESHOOTING.md](PHASE4_TROUBLESHOOTING.md)  
**Security concerns?** Check [API_KEYS_SECURITY_README.md](API_KEYS_SECURITY_README.md)  
**Status overview?** Check [PHASE4_IMPLEMENTATION_COMPLETE.md](PHASE4_IMPLEMENTATION_COMPLETE.md)
