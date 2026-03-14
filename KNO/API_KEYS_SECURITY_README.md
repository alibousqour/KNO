# 🔐 SECURITY WARNING: API KEY MANAGEMENT

## ⚠️ CRITICAL SECURITY CONSIDERATIONS

The API keys you provided are SENSITIVE credentials. They should NEVER be:
- ❌ Hardcoded in source files
- ❌ Committed to version control
- ❌ Shared in emails or messages
- ❌ Stored in plain text accessible to others

## ✅ SECURE IMPLEMENTATION

This implementation uses **environment variables** (recommended) instead of hardcoded keys.

### **Step 1: Set Environment Variables (SAFE)**

**On Windows PowerShell**:
```powershell
# GEMINI API
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "AIzaSyBCvhLB1rsPhuZsSrSjIUfcHX8kO9azPws", "User")

# CHATGPT API
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "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", "User")
```

**Why Environment Variables?**
✅ Secure - not stored in code  
✅ Reusable - works across projects  
✅ Easy - no code changes needed  
✅ Safe - excluded from version control  

### **Step 2: Create evolution_keys.json (BACKUP)**

If environment variables fail, create: `a:\KNO\KNO\evolution_keys.json`

```json
{
  "gemini_api_key": "YOUR_GEMINI_KEY_HERE",
  "openai_api_key": "YOUR_CHATGPT_KEY_HERE",
  "retry_policy": "gemini_first",
  "timeout_seconds": 30,
  "max_retries": 3
}
```

### **Step 3: Add to .gitignore**

Create/update `a:\KNO\KNO\.gitignore`:
```
# API Keys - NEVER COMMIT
evolution_keys.json
.env
*.key
*.secret
logs/evolution.log
```

## 🔄 Key Rotation

Periodically rotate your API keys:
1. Generate new keys in Google Cloud Console and OpenAI Dashboard
2. Update environment variables
3. Delete old keys
4. Monitor logs for any old key usage

## 📊 Monitoring

Track API usage:
- Check `logs/evolution.log` for all API calls
- Monitor API quotas in Google Cloud and OpenAI dashboards
- Alert on unusual activity
- Log all errors and attempts

## ✅ When Ready

Once you've set environment variables OR created evolution_keys.json, run:
```bash
python agent.py
```

The agent will:
1. Load keys securely
2. Test API connectivity
3. Enable external AI brains
4. Log all interactions
5. Display status in GUI

---

**Implementation Status**: Ready to proceed with external AI integration using secure credential loading. ✅
