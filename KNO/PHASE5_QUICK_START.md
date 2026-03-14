# PHASE 5: QUICK START GUIDE - Cloud-Native LLM (Gemini + ChatGPT)

## What's New?

KNO is now **cloud-native** - uses Google Gemini and OpenAI ChatGPT instead of local GGUF models.

**Benefits**:
- ✅ Instant startup (<5 seconds, no model loading)
- ✅ No local GGUF compilation issues
- ✅ Better quality responses (Gemini + ChatGPT)
- ✅ Automatic failover (Gemini → ChatGPT)
- ✅ Minimal cost ($1-2/month)

---

## 3-Minute Setup

### 1. Get API Keys

**Google Gemini API**:
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Click "Create API Key"
3. Copy the key

**OpenAI ChatGPT API**:
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Copy the key

### 2. Set Environment Variables

**PowerShell** (Windows):
```powershell
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "AIzaSyD...", "User")
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")

# Restart PowerShell for changes to take effect
exit
```

**Bash** (Linux/Mac):
```bash
export GEMINI_API_KEY="AIzaSyD..."
export OPENAI_API_KEY="sk-..."

# Or add to ~/.bashrc for permanent setup
```

### 3. Start Agent

```bash
python agent.py
```

**Expected output**:
```
[LLAMA] Initializing Cloud LLM Bridge (Gemini + ChatGPT)
[LLAMA] Cloud LLM ready (Gemini primary, ChatGPT fallback)
[AGENT] Ready
```

---

## That's It!

Your agent is now running with:
- 🧠 Gemini as primary brain (fast, capable)
- 🔄 ChatGPT as automatic fallback (reliable)
- 💾 All Phase 1-4 features intact
- 🚀 Zero startup delay

---

## How It Works

### Request Flow
```
User: "What is quantum computing?"
    ↓
Agent queries Gemini API
    ↓ (if Gemini available)
Gemini returns answer
    ↓
User hears response via TTS

    ↓ (if Gemini fails)
Auto-fallback to ChatGPT API
    ↓
ChatGPT returns answer
    ↓
User hears response
```

### Error Recovery (Self-Evolution)
```
Error occurs during chat
    ↓
ChatGPT analyzes: "What went wrong?"
    ↓
ChatGPT suggests fix: "pip install X" or "fix code Y"
    ↓
Agent auto-applies fix
    ↓
Chat resumes
```

---

## Monitoring

### In another terminal:

```bash
# Watch all API interactions
tail -f logs/evolution.log

# See example output:
# [CLOUD] Gemini Query: "What is..."
# [CLOUD] Gemini Response: "..."
# [EVOLUTION] Error fixed successfully
```

---

## Troubleshooting

### "GEMINI_API_KEY not set"
```powershell
# Windows: Check if env var is set
$env:GEMINI_API_KEY

# If blank, set it:
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your-key", "User")

# Restart PowerShell for changes to apply
```

### "Connection refused"
- ✅ Check internet: `ping 8.8.8.8`
- ✅ Check API keys in environment
- ✅ Check if APIs are up: [Google Status](https://status.google.com), [OpenAI Status](https://status.openai.com)

### Agent takes >30 seconds
- Usually temporary network issue
- Check `logs/evolution.log` for details
- Auto-fallback to ChatGPT if Gemini slow

---

## Features Preserved from Earlier Phases

| Feature | Status | Notes |
|---------|--------|-------|
| Wake word detection | ✅ Works | No changes |
| Experience memory | ✅ Works | Logs to memory.json |
| Error recovery | ✅ Works | ChatGPT-powered |
| Self-evolution | ✅ Works | ChatGPT fixes bugs |
| Audio I/O | ✅ Works | No changes |
| GUI display | ✅ Works | No changes |

---

## Missing Local Model?

If you had a local GGUF model before, don't worry:
- **v5.0 doesn't need it** - Cloud APIs take over
- **If found**, the local model is noted but not used
- **Preferred order**: Gemini → ChatGPT → (local fallback if both fail)

---

## Costs (Realistic)

| Usage Level | Gemini | ChatGPT | Total |
|-------------|--------|---------|-------|
| Light (1x/day) | $0 free tier | $0 | ~$0 |
| Medium (10x/day) | $0 free tier | ~$0.5 | ~$0.50 |
| Heavy (100x/day) | $1-2 | $1-2 | ~$2-4 |
| Extreme (1000x/day) | $5+ | $5+ | ~$10+ |

**Most users**: $0-1/month (free tier)

---

## Next: Explore Features

Now that agent is running:

1. **Test natural conversation**: "Hey KNO, what's the weather?"
2. **Ask complex questions**: "Explain quantum computing"
3. **Use actions**: "Search for latest news about AI"
4. **Watch self-healing**: Trigger an error, watch it auto-fix

---

## Documentation

For more details, see:
- [PHASE5_CLOUD_NATIVE_REFACTOR.md](PHASE5_CLOUD_NATIVE_REFACTOR.md) - Technical details
- [PHASE4_ERROR_RECOVERY_GUIDE.md](PHASE4_ERROR_RECOVERY_GUIDE.md) - Error handling
- [PHASE4_TROUBLESHOOTING.md](PHASE4_TROUBLESHOOTING.md) - Issues & solutions
- [API_KEYS_SECURITY_README.md](API_KEYS_SECURITY_README.md) - API key setup

---

## Version Info

**KNO v5.0** - Cloud-Native LLM Architecture
- Primary: Gemini API
- Fallback: ChatGPT API
- Startup: <5 seconds
- Compatibility: 100% with v1-v4

---

**Ready? Start here**:
```bash
python agent.py
```

Your cloud-powered AI is waiting! 🚀
