# Safety & Resilience - Code Locations & API Reference

## Quick Navigation

### 1. DeepSeek Exponential Backoff
**File:** `agent.py` lines 1163–1225  
**Class:** `DeepSeekEngine`  
**Method:** `_post(self, path, payload, timeout=30)`

**Key variables:**
- `max_retries = 3` (configurable)
- `backoff_factor = 2` (exponential: 2s, 4s, 8s)
- `retry_status_codes = {429, 500, 502, 503, 504}`

**Terminal output markers:**
```
[DEEPSEEK] ⚠️  Status {code}. Retry N/3 in Xs...
[DEEPSEEK] ✅ Recovered after N retry attempt(s)
[DEEPSEEK] ❌ Exhausted 3 retries. Fallback triggered.
[DEEPSEEK] ⏱️  Timeout. Retry N/3 in Xs...
```

---

### 2. GUI Diff Preview Dialog
**File:** `agent.py` lines 2463–2565  
**Function:** `show_patch_approval_dialog(main_window, old_code, new_code, title="Approve Code Patch")`

**Returns:** `bool` (True = approved, False = rejected)

**Dialog features:**
- Size: 900×600 pixels, resizable
- Diff format: Unified (3-way context)
- Colors: Green (+), Red (-), Blue (headers)
- Buttons: Green "approve" + Red "reject"
- Purple bars pulse while dialog is open

**Terminal output markers:**
```
[PATCH] 📋 Awaiting user approval for patch: {reason}
[PATCH] ⚠️  No GUI available; auto-approving patch: {reason}
```

---

### 3. Safe Patch Applier
**File:** `agent.py` lines 2597–2726  
**Class:** `SafePatchApplier`

**Key attributes:**
- `BACKUP_DIR = "backups"` (created automatically)
- `patches_applied = []` (history of successful patches)
- `patches_rejected = []` (history of rejected patches)

**Methods:**

#### `create_backup(filepath, content) → str`
Creates timestamped backup before any write.
```python
backup_path = safe_patch_applier.create_backup("agent.py", old_code)
# Returns: "backups/agent_20260216_191005.bak"
```

#### `apply_patch_with_approval(filepath, new_code, reason, old_code=None) → bool`
- Reads old code from file if not provided
- Shows GUI dialog for approval (if main_window set)
- Creates backup on approval
- Writes new code if backup succeeds
- Logs to patch history

**Terminal output markers:**
```
[PATCH] 💾 Backup created: backups/agent_{YYYYMMDD}_{HHMMSS}.bak
[PATCH] 📋 Awaiting user approval for patch: {reason}
[PATCH] ✅ Patch applied: {filepath}
[PATCH] ❌ Patch rejected by user: {reason}
[PATCH] ❌ Backup failed; refusing to patch for safety.
```

#### `get_patch_log() → dict`
Returns summary of all applied and rejected patches.

---

### 4. Enhanced Error Investigation
**File:** `agent.py` lines 2094–2159  
**Class:** `SelfEvolutionThread`  
**Method:** `investigate_error(error_item) → (fix, ai_engine, retry_summary)`

**Returns tuple:**
```python
(
    fix_text: str or None,
    ai_engine: str ("DeepSeek", "Gemini", "ChatGPT", or None),
    retry_summary: {
        "deepseek": 0,
        "gemini_attempted": bool,
        "chatgpt_attempted": bool,
        "fallback_path": ["DeepSeek", "Gemini", ...]  # Engines tried
    }
)
```

**Fallback order:**
1. Tier 1: DeepSeek (with exponential backoff)
2. Tier 2: Gemini (if DeepSeek fails)
3. Tier 3: ChatGPT (final fallback)

**Terminal output markers:**
```
[EVOLUTION] 🔍 Investigating error with DeepSeek/Gemini/ChatGPT fallback chain...
[EVOLUTION] 🧠 Tier 1: Querying DeepSeek for code fix...
[EVOLUTION] 🔎 Tier 2: Falling back to Gemini for analysis...
[EVOLUTION] 💬 Tier 3: Final fallback to ChatGPT...
[EVOLUTION] ✅ DeepSeek SUCCESS. Suggested fix: ...
[EVOLUTION] ❌ All AI engines exhausted. No fix available.
```

---

### 5. Enhanced Patch Application
**File:** `agent.py` lines 2162–2238  
**Class:** `SelfEvolutionThread`  
**Method:** `apply_fix(fix_suggestion, error_item, ai_engine="Unknown", retry_summary=None) → bool`

**Signature:**
```python
applied = self_evolution_thread.apply_fix(
    fix_suggestion="[FIX_CODE] ...",
    error_item={"type": "AttributeError", ...},
    ai_engine="DeepSeek",
    retry_summary={"fallback_path": ["DeepSeek"], ...}
)
```

**Behavior:**
- Prints fallback chain summary
- Checks for `[FIX_SHELL]` or `[FIX_CODE]` markers
- For code patches: uses SafePatchApplier (auto-approves if no GUI)
- For shell commands: runs with subprocess, max 30s timeout
- Logs all applied fixes to history

**Terminal output markers:**
```
[EVOLUTION] 📊 Fallback chain used: DeepSeek → Gemini
[EVOLUTION] 🧠 AI engine: DeepSeek
[EVOLUTION] 🔧 Attempting to apply fix from DeepSeek...
[EVOLUTION] ✅ Shell command succeeded
[EVOLUTION] ✅ Code patch applied to agent.py
[EVOLUTION] ❌ Code patch rejected or failed
```

---

### 6. Error Queue Processing
**File:** `agent.py` lines 2241–2259  
**Class:** `SelfEvolutionThread`  
**Method:** `process_error_queue()`

**Flow:**
```
1. Pop error from queue
2. investigate_error() → (fix, engine, summary)
3. apply_fix() with AI engine info
4. Set status: 'fixed' | 'failed' | 'no_fix'
5. Repeat for all queued errors
```

---

### 7. Utility Functions
**File:** `agent.py` lines 2425–2440

#### `create_unified_diff(old_text, new_text, old_name="original", new_name="modified") → str`
Generates unified diff format (like `git diff`) for display in dialog.

---

### 8. Global Instances
**File:** `agent.py` lines 2311–2325

```python
higher_intelligence_bridge = HigherIntelligenceBridge()  # Gemini + ChatGPT
deepseek_engine = DeepSeekEngine(api_key=os.getenv("DEEPSEEK_API_KEY"))
safe_patch_applier = SafePatchApplier(main_window=None)  # Set by GUI later
self_evolution_thread = SelfEvolutionThread(higher_intelligence_bridge)
```

---

### 9. Global Flags for UI Sync
**File:** `agent.py` lines 137–141

```python
DEEPSEEK_ACTIVE = False  # True when DeepSeek analyzing (purple bars)
GEMINI_ACTIVE = False    # True when Gemini analyzing (cyan bars)
```

**Set by:**
- `DeepSeekEngine.analyze_error()` / `.generate_patch()`
- `HigherIntelligenceBridge.query_gemini()`

---

### 10. Startup Sanity Check
**File:** `agent.py` lines 2423–2470  
**Function:** `perform_startup_sanity_check()`

**Checks:**
- Gemini API key present
- ChatGPT (OpenAI) API key present
- DeepSeek API key present
- DependencyManager class reachable

**Runs on:** Module import (auto-called at line 2469)

**Output:**
```
[SANITY] ✅ All AI engines and DependencyManager initialized successfully.
[SANITY] ⚠️ Initialization incomplete. Missing: DeepSeek, Gemini
```

---

## Integration Example

Here's how the full resilience flow works:

```python
# 1. Error occurs in bot
# 2. ErrorRecoverySystem catches it
error_item = {
    "type": "ModuleNotFoundError",
    "message": "No module named 'numpy'",
    "context": "During model loading",
    "status": "queued"
}

# 3. Self-evolution thread investigates (with backoff & fallback)
fix, engine, summary = self_evolution_thread.investigate_error(error_item)
# → Returns ("pip install numpy", "DeepSeek", {"fallback_path": ["DeepSeek"]})

# 4. Apply fix with backup & approval
applied = self_evolution_thread.apply_fix(
    fix,
    error_item,
    ai_engine=engine,
    retry_summary=summary
)
# → Creates: backups/agent_20260216_191005.bak
# → Shows GUI dialog if available
# → Writes patch if approved
# → Prints: [EVOLUTION] 📊 Fallback chain used: DeepSeek
```

---

## Environment Variables

Set in `.env` file (loaded on module import):

```dotenv
GEMINI_API_KEY=AIzaSy...
OPENAI_API_KEY=sk-proj-...
DEEPSEEK_API_KEY=sk-1b8d75...
```

All three are optional (graceful fallback if any missing).

---

## Customization Points

### Adjust backoff parameters:
Edit `DeepSeekEngine._post()`:
```python
max_retries = 5  # Increase from 3
backoff_factor = 3  # 3s, 9s, 27s (steeper backoff)
```

### Change backup location:
Edit `SafePatchApplier`:
```python
BACKUP_DIR = "my_custom_backups"  # Instead of "backups"
```

### Auto-approve patches (headless):
```python
# SafePatchApplier detects missing main_window automatically
# Set it explicitly for GUI:
safe_patch_applier.main_window = my_tkinter_root
```

---

## Debugging Tips

1. **Watch retry attempts:** Look for `[DEEPSEEK]` console lines
2. **Check backup created:** Check `ls backups/` before/after patch
3. **Inspect diff:** Stop before approval, examine dialog text
4. **Verify fallback:** Terminal shows every tier tried
5. **Review patch log:** Call `safe_patch_applier.get_patch_log()`

---

## Test Checklist

- [ ] Syntax validates: `python -m py_compile agent.py`
- [ ] Imports succeed: `python -c "import agent"`
- [ ] SafePatchApplier available: `hasattr(agent, 'SafePatchApplier')`
- [ ] GUI diff works: Run agent, trigger error, approve fix
- [ ] Backup created: Check `backups/` folder has .bak files
- [ ] Retry feedback visible: Check console for `[DEEPSEEK]` lines
- [ ] Fallback logs: Console shows AI engine chain used

---

**Status:** ✅ All resilience components integrated and documented.
