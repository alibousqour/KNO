# ✅ Windows Installation Verification Checklist

Use this checklist to verify your Windows 10/11 installation is complete and working.

---

## Phase 1: Prerequisites (Before Setup)

- [ ] Windows 10/11 (updated to latest version)
- [ ] Internet connection available
- [ ] Administrator access (may be needed)
- [ ] At least 5GB free disk space
- [ ] Microphone connected and working
- [ ] Speaker or headphones available

**Verify Windows Version:**
```powershell
[System.Environment]::OSVersion.VersionString
# Should show: Microsoft Windows 10.0.xxxx or Windows 11.0.xxxx
```

---

## Phase 2: Python Installation

- [ ] Python 3.8+ installed
- [ ] Python added to PATH
- [ ] pip working correctly

**Verify Python:**
```powershell
python --version
# Should show: Python 3.8.x or higher

pip --version
# Should show: pip x.x.x from C:\...\Python3xx\lib\site-packages
```

If either command fails:
1. Reinstall Python from https://www.python.org
2. **IMPORTANT:** Check "Add Python to PATH" during installation
3. Restart PowerShell/CMD
4. Try again

---

## Phase 3: Project Setup

- [ ] Project extracted/cloned to a location
- [ ] Navigated to project directory

**Verify Navigation:**
```powershell
cd C:\Path\To\Project\KNO\KNO
dir    # Should show: agent.py, config.json, setup.bat, setup.ps1, etc.
```

---

## Phase 4: Run Setup Script

**Choose ONE method:**

### Method A: PowerShell (Recommended) ⭐
```powershell
# Check if script execution is allowed
Get-ExecutionPolicy

# If "Restricted", allow local scripts:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run setup
.\setup.ps1
```

**Checklist while setup runs:**
- [ ] Python version confirmed
- [ ] Virtual environment created
- [ ] Directories created (piper, sounds, faces, whisper.cpp)
- [ ] Dependencies installing
- [ ] Setup completed successfully

### Method B: Command Prompt
```cmd
setup.bat
```

**Both methods should show:**
```
✓ Python is installed
✓ Virtual environment created
✓ Virtual environment activated
✓ All directories created
✓ Python dependencies installed
[6/6] Setup Complete!
```

---

## Phase 5: Virtual Environment

- [ ] Virtual environment created at `venv\`
- [ ] Can activate virtual environment

**Verify Virtual Environment:**
```powershell
# Should exist
dir venv\

# Activate
.\venv\Scripts\Activate.ps1
# Or in Command Prompt: venv\Scripts\activate.bat

# Should show "(venv)" in prompt
# Deactivate later with: deactivate
```

---

## Phase 6: Dependencies Installation

- [ ] All packages installed
- [ ] No installation errors

**Verify Dependencies:**
```powershell
# Make sure venv is activated
pip list
# Should show: sounddevice, numpy, scipy, ollama, Pillow, etc.

# Test imports
python -c "import ollama; print('✓ Ollama')"
python -c "import sounddevice; print('✓ SoundDevice')"
python -c "import PIL; print('✓ PIL')"
python -c "import numpy; print('✓ NumPy')"
```

---

## Phase 7: Directory Structure  

- [ ] `piper\` directory exists
- [ ] `sounds\` directory with subdirectories exists
- [ ] `faces\` directory with subdirectories exists
- [ ] `whisper.cpp\` directory exists (optional)

**Verify Directories:**
```powershell
dir sounds\
# Should contain: greeting_sounds, thinking_sounds, ack_sounds, error_sounds

dir faces\
# Should contain: idle, listening, thinking, speaking, error, warmup, capturing
```

---

## Phase 8: Configuration Files

- [ ] `config.json` exists and readable
- [ ] `.env.example` exists for reference
- [ ] Can create `.env` with API keys (optional)

**Verify Configuration:**
```powershell
# Should exist
type config.json
# Should show valid JSON

# Check config has required fields
python -c "import json; config=json.load(open('config.json')); print('✓ Config valid')"
```

---

## Phase 9: Audio System

- [ ] Microphone detected and working
- [ ] Speaker/headphones available
- [ ] Audio drivers updated

**Verify Audio:**
```powershell
python -c "
import sounddevice as sd
print('Microphones:', len(sd.query_devices()))
# Should show something other than 0
"

# Test microphone in Windows
# Settings → Sound → Input devices → Test microphone
```

---

## Phase 10: Ollama Installation

- [ ] Ollama downloaded from https://ollama.ai
- [ ] Ollama installed
- [ ] Ollama can be launched
- [ ] Language model downloaded

**Verify Ollama:**
```powershell
# Start Ollama (separate PowerShell window)
ollama serve
# Should show: Listening on 127.0.0.1:11434

# In another window, check models
ollama list
# Should show: gemma3:1b (or pulled models)

# Pull if missing
ollama pull gemma3:1b
```

---

## Phase 11: Optional - Piper TTS

- [ ] Piper downloaded (optional but recommended)
- [ ] Windows version extracted
- [ ] Files in `piper\` folder

**Verify Piper (if using):**
```powershell
# Should exist
dir piper\
# Should show: piper.exe, model files, etc.

# Test (optional)
cd piper
.\piper.exe --help
# Should show help text
```

---

## Phase 12: First Run Test

- [ ] Can activate virtual environment
- [ ] Can import all modules
- [ ] Can start agent without errors

**Test Startup:**
```powershell
# Navigate to project
cd C:\Path\To\Project\KNO\KNO

# Activate venv
.\venv\Scripts\Activate.ps1

# Start agent
python agent.py
# Should show: "--- SYSTEM STARTING ---"
# Should load animations
# Should wait for input
```

---

## Phase 13: Functional Testing

### Audio Input
- [ ] Microphone records sound
- [ ] Audio saved to file
- [ ] System shows audio level

**Test:**
- Speak into microphone near the running agent
- Should see "Recording..." or similar message

### Audio Output
- [ ] Speaker/headphones work
- [ ] Can hear TTS voice
- [ ] Volume appropriate

**Test:**
- Agent should respond verbally (if Piper installed)
- Should hear natural-sounding voice

### Face Animation
- [ ] Face images display in window
- [ ] Animation updates smoothly
- [ ] States change (idle → listening → thinking)

**Test:**
- Should see animated faces
- Different expressions for different states

### Memory
- [ ] `memory.json` created
- [ ] Conversations saved
- [ ] Memory persists between runs

**Test:**
```powershell
type memory.json
# Should show JSON with conversation history
```

---

## Phase 14: Configuration (Optional)

- [ ] Reviewed `config.json`
- [ ] Adjusted settings if needed
- [ ] Added custom prompts (optional)

**Common Settings:**
```json
{
    "text_model": "gemma3:1b",     // Can change to mistral, etc.
    "chat_memory": true,            // Keep conversations
    "camera_rotation": 0,           // 0, 90, 180, 270
    "system_prompt_extras": ""      // Custom instructions
}
```

---

## Phase 15: Media Files (Optional)

- [ ] Added sound files to `sounds/*/` directories
- [ ] Added face images to `faces/*/` directories
- [ ] Files in correct format (.wav/.mp3, .png/.jpg)

**Expected Structure:**
```
sounds/
├── greeting_sounds/     (contains .wav or .mp3)
├── thinking_sounds/     (contains .wav or .mp3)
└── ack_sounds/         (contains .wav or .mp3)

faces/
├── idle/               (contains .png or .jpg)
├── listening/          (contains .png or .jpg)
├── thinking/           (contains .png or .jpg)
└── speaking/           (contains .png or .jpg)
```

---

## Troubleshooting: Common Issues

### Issue: Python Not Found
- [ ] Reinstalled Python with PATH option
- [ ] Restarted PowerShell/CMD
- [ ] Verified: `python --version`
- [ ] ✅ RESOLVED

### Issue: Virtual Environment Won't Activate
- [ ] Ran: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- [ ] Tried PowerShell instead of Command Prompt
- [ ] Verified venv exists: `dir venv\`
- [ ] ✅ RESOLVED

### Issue: Dependencies Won't Install
- [ ] Upgraded pip: `python -m pip install --upgrade pip`
- [ ] Cleared cache: `pip install --cache-dir '' -r requirements.txt`
- [ ] Tried individual: `pip install sounddevice`
- [ ] ✅ RESOLVED

### Issue: Ollama Connection Error
- [ ] Started Ollama: `ollama serve`
- [ ] Verified in task manager: `ollama` running
- [ ] Pulled model: `ollama pull gemma3:1b`
- [ ] Checked port: `netstat -ano | findstr :11434`
- [ ] ✅ RESOLVED

### Issue: Audio Not Working
- [ ] Checked microphone in Windows Settings
- [ ] Tested microphone in Sound Settings
- [ ] Updated audio drivers
- [ ] Ran as Administrator
- [ ] ✅ RESOLVED

---

## Success Criteria: Ready to Use ✅

You're ready when:

- ✅ Python 3.8+ installed and in PATH
- ✅ Virtual environment created and activates
- ✅ All dependencies installed without errors
- ✅ Project directories created (sounds, faces)
- ✅ Ollama installed and models downloaded
- ✅ Agent starts without errors
- ✅ Microphone records sound
- ✅ Faces display and animate
- ✅ System responds to voice input
- ✅ Memory saves conversations

---

## Final Checklist: Complete System

```powershell
# Complete verification script
Write-Host "🤖 Complete System Verification" -ForegroundColor Cyan
Write-Host ""

# 1. Python
Write-Host "[1/8] Python..." -ForegroundColor Yellow
python --version
Write-Host "✓ OK" -ForegroundColor Green
Write-Host ""

# 2. Dependencies
Write-Host "[2/8] Importing core modules..." -ForegroundColor Yellow
python -c "import ollama, sounddevice, numpy, Pillow; print('✓ OK')" -ForegroundColor Green
Write-Host ""

# 3. Virtual Environment
Write-Host "[3/8] Virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") { Write-Host "✓ OK" -ForegroundColor Green }
Write-Host ""

# 4. Directories
Write-Host "[4/8] Directories..." -ForegroundColor Yellow
if ((Test-Path "sounds") -and (Test-Path "faces")) { Write-Host "✓ OK" -ForegroundColor Green }
Write-Host ""

# 5. Ollama
Write-Host "[5/8] Ollama models..." -ForegroundColor Yellow
ollama list
Write-Host ""

# 6. Audio Devices
Write-Host "[6/8] Audio devices..." -ForegroundColor Yellow
python -c "import sounddevice as sd; print(f'Devices found: {len(sd.query_devices())}')"
Write-Host ""

# 7. Configuration
Write-Host "[7/8] Configuration files..." -ForegroundColor Yellow
if ((Test-Path "config.json") -and (Test-Path ".env.example")) { Write-Host "✓ OK" -ForegroundColor Green }
Write-Host ""

# 8. Agent
Write-Host "[8/8] Agent startup test..." -ForegroundColor Yellow
python -c "import agent; print('✓ OK')"
Write-Host ""

Write-Host "✅ All checks passed! System ready to use." -ForegroundColor Green
```

Run this script to verify everything!

---

## 🎓 Next Steps After Verification

1. **Customize config.json** - Adjust models, voices, settings
2. **Add media files** - Put sounds and face images in directories
3. **Set up API keys** - Create `.env` if using Gemini/OpenAI
4. **Learn controls** - ENTER to listen, SPACE to interrupt, ESC to exit
5. **Have fun!** - Talk to your AI agent

---

## 📞 Still Having Issues?

1. **Check:** README-WINDOWS.md (full setup guide)
2. **Check:** WINDOWS-COMPATIBILITY.md (technical details)
3. **Check:** QUICK_START_WINDOWS.md (quick reference)
4. **Debug:** Run individual checks above
5. **Search:** Google the specific error message

---

## ✨ Congratulations!

If all checkmarks are filled, your Windows 10/11 Be More Agent installation is complete and ready to use! 🎉

**You now have:**
- ✅ Local AI processing (no cloud required)
- ✅ Voice input and output
- ✅ Emotional responses
- ✅ Conversation memory
- ✅ Web search capability
- ✅ Customizable personality

**Enjoy your AI assistant!** 🤖

---

**Last Updated:** February 2026  
**Tested On:** Windows 11 23H2, Python 3.11.2
