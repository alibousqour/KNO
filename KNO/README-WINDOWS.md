# 🤖 Windows 10/11 Setup Guide for Be More Agent

This guide provides complete step-by-step instructions to run the Be More Agent (KNO and BMO projects) on Windows 10/11.

---

## ✅ Prerequisites

- **Windows 10** or **Windows 11** (64-bit recommended)
- **Python 3.8+** (Download from https://www.python.org)
  - ✓ During installation, **check "Add Python to PATH"**
- **Git** (optional, for cloning repository)
- **Internet connection** (for downloading dependencies and AI models)
- **Microphone** (for voice input)
- **Speaker** or headphones (for voice output)
- **Webcam** (optional, for image capture feature)

---

## 📋 Installation Steps

### Step 1: Verify Python Installation

Open **Command Prompt** or **PowerShell** and check Python is installed:

```powershell
python --version
pip --version
```

You should see Python 3.8 or higher. If not, install Python from https://www.python.org

---

### Step 2: Clone or Extract the Project

Navigate to your desired directory and extract/clone the project:

```powershell
cd C:\Users\YourUsername\Documents
# Extract the ZIP file or clone repository
git clone <repository-url>
cd KNO\KNO
```

Or if you have a ZIP file:
- Extract it to a folder like `C:\Users\YourUsername\Documents\KNO`
- Open PowerShell and navigate to the KNO\KNO folder

---

### Step 3: Run the Setup Script

#### Option A: Using PowerShell (Recommended - Colorful Output)

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup.ps1
```

#### Option B: Using Command Prompt (Batch)

```cmd
setup.bat
```

The setup script will:
- ✓ Create a Python virtual environment
- ✓ Create all required directories
- ✓ Install Python dependencies
- ✓ Display next steps

---

### Step 4: Activate Virtual Environment

The setup script does this automatically, but if you need to manually activate:

#### PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

#### Command Prompt:
```cmd
venv\Scripts\activate.bat
```

You should see `(venv)` in your terminal prompt.

---

### Step 5: Install Required AI Models

#### 5a. Install Ollama (Required for LLM)

1. Download Ollama from https://ollama.ai
2. Install and run it
3. In PowerShell/CMD, pull the language model:

```powershell
ollama pull gemma3:1b
```

This downloads a lightweight LLM (~2GB). Other options:
- `gemma2` - Larger, more capable
- `mistral` - Faster, less capable
- `neural-chat` - Good balance

#### 5b. Download Piper TTS (Text-to-Speech)

Piper is optional but recommended for voice output:

1. Go to: https://github.com/rhasspy/piper/releases
2. Download the Windows version: `piper_windows_x86_64.zip`
3. Extract to the `piper\` folder in your project directory
4. The folder should look like:
   ```
   piper\
   ├── piper.exe
   ├── piper.json
   ├── en_GB-semaine-medium.onnx
   └── (other voice model files)
   ```

To download a voice model:
```powershell
cd piper
# Voice model will be downloaded automatically when piper runs the first time
cd ..
```

---

### Step 6: Add Media Files (Sounds & Face Images)

The script created empty directories. Add your media:

#### Sounds:
- `sounds\greeting_sounds\` - Greeting audio files (MP3/WAV)
- `sounds\thinking_sounds\` - Thinking/processing sounds
- `sounds\ack_sounds\` - Acknowledgment/confirmation sounds
- `sounds\error_sounds\` - Error notification sounds

#### Face Images:
- `faces\idle\` - Resting state images (PNG/JPG)
- `faces\listening\` - Listening state images
- `faces\thinking\` - Processing/thinking images
- `faces\speaking\` - Speaking state images
- `faces\error\` - Error state images
- `faces\warmup\` - Startup sequence images
- `faces\capturing\` - Image capture state

**Example:**
```
faces/idle/
  ├── face1.png
  ├── face2.png
  └── face3.png
```

---

### Step 7: Configure the Project

Edit `config.json` to customize behavior:

```json
{
    "text_model": "gemma3:1b",        // Change to other ollama models
    "vision_model": "moondream",       // For image analysis
    "voice_model": "piper/en_GB-semaine-medium.onnx",
    "chat_memory": true,               // Enable conversation history
    "camera_rotation": 0,              // Rotate camera: 0, 90, 180, 270
    "system_prompt_extras": ""         // Add custom instructions here
}
```

---

### Step 8: Set Up Environment Variables (Optional)

For Google Gemini API support, create a `.env` file:

```powershell
# Create .env file in project root
"GEMINI_API_KEY=your-api-key-here" | Out-File -Encoding UTF8 .env
```

Or create it manually:
1. Open Notepad
2. Add: `GEMINI_API_KEY=your-api-key-here`
3. Save as `.env` in the project root folder

---

## 🚀 Running the Project

### Method 1: Using PowerShell

```powershell
# Navigate to project
cd C:\Path\To\KNO\KNO

# Activate virtual environment (if not already active)
.\venv\Scripts\Activate.ps1

# Run the agent
python agent.py
```

### Method 2: Using Command Prompt

```cmd
cd C:\Path\To\KNO\KNO
venv\Scripts\activate.bat
python agent.py
```

### Method 3: Create a Shortcut (Easiest for Future Use)

Create a batch file `run_agent.bat`:

```batch
@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
python agent.py
pause
```

Double-click this file to run the agent.

---

## 🎮 Using the Agent

### Keyboard Controls:
- **ENTER** - Toggle voice recording (Push-to-Talk)
- **SPACE** - Stop current speech/interrupt
- **ESC** - Exit fullscreen mode
- **Click on screen** - Show/hide HUD (text display)
- **"Quit" or "Exit"** - Say this to close gracefully

### Features:
- 🎤 Voice input via microphone
- 🎵 Voice output (requires Piper TTS)
- 🧠 AI responses via Ollama
- 💾 Conversation memory (saves to `memory.json`)
- 🔍 Web search capability
- 📸 Image capture (requires camera)
- 🎭 Emotional responses (mood-based)
- ⚡ Real-time processing

---

## 🔧 Troubleshooting

### Problem: Python not found

**Solution:**
```powershell
# Add Python to PATH manually
$env:Path += ";C:\Users\YourUsername\AppData\Local\Programs\Python\Python311"
python --version
```

Or reinstall Python with "Add Python to PATH" option checked.

---

### Problem: Virtual Environment Won't Activate

**Solution:**
```powershell
# If PS script execution is restricted
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
.\venv\Scripts\Activate.ps1
```

---

### Problem: "No module named 'sounddevice'"

**Solution:**
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Problem: Audio Input No Working

**Solution:**
1. Check Windows sound settings
2. Make sure microphone is not muted
3. Test microphone in Windows Settings:
   - Settings → Sound → Input devices → Test microphone
4. Update audio drivers from device manufacturer's website

---

### Problem: Ollama Connection Error

**Solution:**
1. Ensure Ollama is installed and running:
   ```powershell
   ollama serve
   ```
2. In another terminal, verify model is available:
   ```powershell
   ollama list
   ```
3. Pull the model if missing:
   ```powershell
   ollama pull gemma3:1b
   ```

---

### Problem: Port 11434 Already in Use

**Solution:**
```powershell
# Find and kill the process using port 11434
netstat -ano | findstr :11434

# Kill the process (replace PID with the number shown)
taskkill /PID <PID> /F
```

---

### Problem: Permission Denied on Windows Firewall

**Solution:**
1. Windows Defender Firewall → Allow an app through firewall
2. Find Python in the list and check both Private and Public
3. Restart the application

---

### Problem: Face Images Not Displaying

**Solution:**
1. Verify images are in correct folders:
   ```powershell
   dir faces\
   dir faces\idle\
   ```
2. Image format should be `.png` or `.jpg`
3. Try with larger images (at least 400x300 pixels)
4. Convert Images to PNG:
   - Use Paint or online converter
   - Supported formats: PNG, JPG

---

## 📁 Project Structure (Windows)

```
KNO\KNO\
├── agent.py                 # Main agent program
├── config.json              # Configuration file
├── requirements.txt         # Python dependencies
├── setup.bat               # Batch setup script
├── setup.ps1               # PowerShell setup script
├── memory.json             # Conversation memory (auto-created)
├── input.wav               # Voice input (auto-created)
├── wakeword.onnx           # Wake word model
│
├── venv\                   # Virtual environment (created by setup)
│   ├── Scripts\
│   │   ├── python.exe
│   │   ├── pip.exe
│   │   └── Activate.ps1
│   └── ...
│
├── piper\                  # Text-to-Speech (manual download)
│   ├── piper.exe
│   ├── en_GB-semaine-medium.onnx
│   └── ...
│
├── whisper.cpp\            # Speech recognition (OPTIONAL)
│   ├── build\bin\whisper-cli.exe
│   ├── models\ggml-base.en.bin
│   └── ...
│
├── sounds\                 # Audio files
│   ├── greeting_sounds\    # (add your files)
│   ├── thinking_sounds\    # (add your files)
│   ├── ack_sounds\         # (add your files)
│   └── error_sounds\       # (add your files)
│
├── faces\                  # Face images
│   ├── idle\               # (add your files)
│   ├── listening\          # (add your files)
│   ├── thinking\           # (add your files)
│   ├── speaking\           # (add your files)
│   ├── error\              # (add your files)
│   ├── capturing\          # (add your files)
│   └── warmup\             # (add your files)
│
└── BMO\                    # Optional: Alternative UI project
    ├── main.py
    ├── voice.py
    ├── brain.py
    ├── ui.py
    ├── requirements.txt
    └── ...
```

---

## 🌐 Obtaining Required Keys & Resources

### Ollama (Free, Local AI)
- Website: https://ollama.ai
- Models available: Gemma, Mistral, Llama, etc.
- All runs locally on your computer (privacy-first)

### Google Gemini API (Optional)
- Website: https://aistudio.google.com
- Get API key: https://makersuite.google.com/app/apikey
- Free tier available with rate limits

### OpenAI API (Optional Alternative)
- Website: https://openai.com
- Requires paid API key
- More capable but not free

### Piper TTS (Free, Text-to-Speech)
- GitHub: https://github.com/rhasspy/piper
- Voice models: https://huggingface.co/rhasspy/piper-voices
- Multiple languages and voices supported

---

## 🚀 Advanced Configuration

### Change Language Models

Edit `config.json`:
```json
{
    "text_model": "mistral"    // Faster, try: mistral, neural-chat, tinyllama
}
```

Available models (run `ollama pull <name>`):
- `gemma3:1b` - Small, fast
- `gemma2` - Better quality, slower
- `mistral` - Very fast
- `llama2` - Larger, more capable
- `neural-chat` - Good balance
- `openchat` - Fast and capable

---

### Change Voice

Edit `piper_voice` in `config.json` or download another voice from:
https://huggingface.co/rhasspy/piper-voices/tree/main/en

Available English voices:
- `en_GB-semaine-medium.onnx` - British English
- `en_US-lessac-medium.onnx` - American English
- `en_US-ryan-medium.onnx` - American English (male)

---

## 📊 Performance Tips

### If Agent Runs Slowly:

1. **Use smaller language model:**
   ```json
   "text_model": "mistral"  // Faster than gemma
   ```

2. **Lower animation frame rate** in `agent.py`:
   - Change animation speed values

3. **Close background applications:**
   - Stop unnecessary programs to free RAM

4. **Check system resources:**
   ```powershell
   Get-Process | Sort-Object WS -Descending | Select-Object -First 10
   ```

5. **Upgrade Python:**
   - Use Python 3.11+ for better performance

---

## 📝 Notes & Known Issues

### Limitations on Windows:
- ✓ Piper TTS works well on Windows
- ✓ Ollama runs reliably on Windows
- ⚠️ `rpicam-still` (Raspberry Pi camera) not available - uses OpenCV fallback
- ⚠️ Some Tkinter features may behave different than Linux

### What Works on Windows:
- ✓ Voice input (via microphone)
- ✓ Voice output (via Piper TTS or edge-tts)
- ✓ Web search
- ✓ Conversation memory (JSON)
- ✓ Animation and UI
- ✓ All AI inference (via Ollama)

---

## 🆘 Getting Help

1. **Check the error message** - It often tells you what's wrong
2. **Google the error** - Search "Python error: <message>"
3. **Check Forums:**
   - Stack Overflow
   - Python Discord
   - GitHub Issues

4. **Common Fixes:**
   - Delete `venv` folder and rerun setup
   - Update Python to latest 3.11+
   - Update all dependencies: `pip install --upgrade -r requirements.txt`
   - Restart Windows
   - Check Task Manager → End conflicting processes

---

## ✨ Enjoying the Agent!

Once running, your agent will:
- 🎤 Listen for your voice commands
- 🧠 Process with local AI (Ollama)
- 💬 Generate intelligent responses
- 🎵 Speak back with Piper TTS
- 💾 Remember conversations
- 😊 Change emotions based on mood
- 📸 Capture images (with compatible camera)
- 🌐 Search the web

**Congratulations! You now have a fully functional local AI agent running on Windows!** 🎉

---

**Last Updated:** February 2026
**Tested On:** Windows 10 22H2, Windows 11 23H2
