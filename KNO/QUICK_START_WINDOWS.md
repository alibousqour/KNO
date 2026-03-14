# ⚡ Quick Start Guide - Windows 10/11

**5-Minute Setup for Impatient Users**

---

## 1️⃣ Prerequisites (60 seconds)

```powershell
# Check Python is installed
python --version    # Should show 3.8+
```

If not, install from https://www.python.org (check "Add Python to PATH")

---

## 2️⃣ Run Setup (2 minutes)

```powershell
# Navigate to KNO project
cd C:\Your\Project\Path\KNO\KNO

# Run setup (pick one)
.\setup.ps1          # Recommended
# OR
setup.bat
```

**This will:**
- ✓ Create virtual environment
- ✓ Install dependencies
- ✓ Create directories
- ✓ Show next steps

---

## 3️⃣ Install AI Models (1 minute)

```powershell
# Download Ollama from https://ollama.ai and install

# In PowerShell, download the language model
ollama pull gemma3:1b

# Optional: Text-to-speech
# Download from https://github.com/rhasspy/piper/releases
# Extract Windows version to piper\ folder
```

---

## 4️⃣ Add Your Media (30 seconds)

Create the directory structure:
```
project\sounds\
  ├── greeting_sounds\      (add .wav/.mp3)
  ├── thinking_sounds\      (add .wav/.mp3)
  └── ack_sounds\           (add .wav/.mp3)

project\faces\
  ├── idle\                 (add .png/.jpg)
  ├── listening\            (add .png/.jpg)
  ├── thinking\             (add .png/.jpg)
  └── speaking\             (add .png/.jpg)
```

---

## 5️⃣ Run the Agent (1 minute)

### Option A: PowerShell ⭐
```powershell
.\venv\Scripts\Activate.ps1
python agent.py
```

### Option B: Command Prompt
```cmd
venv\Scripts\activate.bat
python agent.py
```

### Option C: Create Shortcut
Save this as `run.bat` → double-click it:
```batch
@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
python agent.py
pause
```

---

## 🎮 Controls

- **ENTER** - Start/stop listening
- **SPACE** - Interrupt speaking
- **ESC** - Exit fullscreen
- **Click screen** - Show/hide text
- Say **"exit"** - Quit gracefully

---

## ❌ Something Not Working?

### Audio not working?
- Check Windows Settings → Sound
- Update audio drivers
- Try a different microphone

### Ollama not connecting?
```powershell
ollama serve    # Start in separate terminal
ollama list     # Check models
```

### Python not found?
- Reinstall Python with "Add Python to PATH" checked
- Or: `$env:Path += ";C:\Python311"`

### Dependencies missing?
```powershell
pip install -r requirements.txt --upgrade
```

### Still stuck?
- Read: `README-WINDOWS.md` (full guide)
- Read: `WINDOWS-COMPATIBILITY.md` (technical)

---

## 📁 Project Structure

```
KNO\KNO\
├── agent.py          ← Main program
├── config.json       ← Settings
├── setup.ps1         ← Setup script
├── requirements.txt  ← Dependencies
├── venv\             ← Virtual environment (auto-created)
├── sounds\           ← Audio files (auto-created)
├── faces\            ← Face images (auto-created)
└── README-WINDOWS.md ← Full setup guide
```

---

## 🔑 API Keys (Optional)

For advanced features, create `.env`:
```
GEMINI_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```

Get free keys from:
- Google: https://makersuite.google.com/app/apikey
- OpenAI: https://platform.openai.com/account/api-keys

---

## ✨ Pro Tips

1. **Use PowerShell** - Better experience than Command Prompt
2. **Keep Ollama running** - Open separate PowerShell, run `ollama serve`
3. **Close apps** - Free up RAM for better performance
4. **Use SSD** - Faster startup times
5. **Update regularly** - `pip install --upgrade -r requirements.txt`

---

## 📊 Troubleshooting Flowchart

```
Does agent start?
├─ NO
│  ├─ Python error?
│  │  └─ Re-run: pip install -r requirements.txt
│  ├─ Ollama not found?
│  │  └─ Download and run: ollama serve
│  └─ Other error? Check README-WINDOWS.md
│
└─ YES
   ├─ Audio not working?
   │  └─ Check Windows Sound Settings + drivers
   ├─ Responses not generating?
   │  └─ Verify Ollama is running
   └─ Enjoy! 🎉
```

---

## 🚀 Next Steps

1. **After first run:** Read `config.json`, customize settings
2. **Add more sounds:** Put audio in `sounds/` folders
3. **Add face images:** Put PNG/JPG in `faces/` folders
4. **Enable features:** Uncomment sections in `config.json`
5. **Fine-tune:** Adjust models, voices, settings

---

## 📞 Quick Fixes

| Problem | Solution |
|---------|----------|
| "Python not found" | Reinstall with PATH option |
| "No module named X" | `pip install -r requirements.txt` |
| "Ollama connection error" | Run `ollama serve` in another terminal |
| "Permission denied" | Run PowerShell as Administrator |
| "Port 11434 in use" | Another Ollama instance running - close it |
| "Audio choppy/delayed" | Close background apps, restart |
| "Camera not working" | Check Windows camera permissions |

---

## 🎯 What Works

- ✅ Voice input via microphone
- ✅ Voice output via Piper TTS
- ✅ AI responses via Ollama
- ✅ Conversation memory
- ✅ Web search
- ✅ Image capture
- ✅ Emotion detection
- ✅ Customizable personality

---

## ⏱️ Estimated Total Setup Time

| Step | Time |
|------|------|
| Install Python | 2 min |
| Run setup script | 3 min |
| Download Ollama | 5 min |
| Pull model | 5 min |
| Add media (optional) | 5 min |
| **TOTAL** | **20 min** |

---

## 🎓 Key Changes from Original

| What Changed | Why | Impact |
|-------------|-----|--------|
| Paths: `"sounds/..."` → `os.path.join()` | Windows compatibility | Works anywhere |
| Executables: `.exe` detection | Windows uses .exe | Auto-detects OS |
| Setup: Bash → Batch/PowerShell | Windows native | One-click setup |
| Files: Absolute → Relative paths | Portable | Works on any drive |
| Fallback: Pi camera → OpenCV | Windows support | Webcam works |

---

## 📚 Documentation Level

| Need | File |
|------|------|
| "Just tell me what to do" | This file ⭐ |
| "I need step-by-step help" | README-WINDOWS.md |
| "What changed and why?" | WINDOWS-COMPATIBILITY.md |
| "Show me the code changes" | CHANGES_SUMMARY.md |
| "How does this work?" | Code files + comments |

---

## 🎉 Ready to Go!

If you followed all steps and it's working... **Congratulations!** 🚀

Your Be More Agent is now running on Windows 10/11 natively!

Now:
1. Say something to the microphone
2. Watch it respond with AI
3. Customize `config.json` to your liking
4. Add your own sounds and faces
5. Enjoy your local AI assistant!

---

**Need help?** → Read `README-WINDOWS.md`  
**Want details?** → Read `WINDOWS-COMPATIBILITY.md`  
**Done troubleshooting?** → Start using it! 🎮

---

**Last Updated:** February 2026  
**For:** Windows 10/11, Python 3.8+
