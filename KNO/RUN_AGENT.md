# 🚀 Running the Be More Agent - Windows 10/11 Setup

## Quick Start

### Step 1: Activate Virtual Environment

```powershell
cd a:\KNO\KNO
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try again.

### Step 2: Run the Agent

```powershell
python agent.py
```

## Alternative: Using Batch File

If PowerShell activation fails, use Command Prompt:

```cmd
cd a:\KNO\KNO
venv\Scripts\activate.bat
python agent.py
```

## What You Need

1. **Ollama**: Download and install from https://ollama.ai
   - Then run: `ollama pull gemma3:1b`

2. **Piper TTS** (Optional): Download from https://github.com/rhasspy/piper/releases
   - Extract to `piper\` folder

3. **Sound & Face Files**: Add to respective folders:
   - `sounds\greeting_sounds\`
   - `sounds\thinking_sounds\`
   - `sounds\ack_sounds\`
   - `faces\idle\`
   - `faces\listening\`
   - `faces\thinking\`
   - `faces\speaking\`

## Dependencies Installed

✅ duckduckgo-search  - Web search
✅ ollama             - Local LLM
✅ sounddevice        - Audio input/output
✅ numpy              - Numerical computing
✅ scipy              - Signal processing
✅ openwakeword       - Wake word detection
✅ onnxruntime        - Model inference
✅ Pillow             - Image processing
✅ python-dotenv      - Environment variables
✅ opencv-python      - Camera support

## Troubleshooting

**Issue**: "No module named X"  
**Solution**: Run `pip install -r requirements.txt`

**Issue**: Ollama connection error  
**Solution**: Make sure Ollama is running:
```powershell
ollama serve
```
(in a separate terminal)

**Issue**: PowerShell execution policy  
**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Ready to Go!

Your environment is now set up. You can run the agent with:
```powershell
python agent.py
```

Enjoy! 🤖
