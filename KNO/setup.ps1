# =========================================================================
#  Be More Agent Setup Script for Windows 10/11 (PowerShell)
#  Modern approach using PowerShell instead of batch files
# =========================================================================

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "   🤖 Be More Agent Setup Script for Windows (PowerShell)" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python is installed
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python is installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org" -ForegroundColor Red
    exit 1
}

# 2. Create virtual environment
Write-Host ""
Write-Host "[2/6] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists, skipping..." -ForegroundColor White
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# 3. Activate virtual environment and upgrade pip
Write-Host ""
Write-Host "[3/6] Activating virtual environment and upgrading pip..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip --quiet
Write-Host "✓ Virtual environment activated and pip upgraded" -ForegroundColor Green

# 4. Create necessary directories
Write-Host ""
Write-Host "[4/6] Creating project directories..." -ForegroundColor Yellow
$directories = @(
    "piper",
    "sounds\greeting_sounds",
    "sounds\thinking_sounds",
    "sounds\ack_sounds",
    "sounds\error_sounds",
    "faces\idle",
    "faces\listening",
    "faces\thinking",
    "faces\speaking",
    "faces\error",
    "faces\warmup",
    "whisper.cpp"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✓ All directories created" -ForegroundColor Green

# 5. Install Python requirements
Write-Host ""
Write-Host "[5/6] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Python dependencies installed" -ForegroundColor Green

# 6. Display next steps
Write-Host ""
Write-Host "[6/6] Setup Complete!" -ForegroundColor Yellow
Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "   ✓ Setup Completed Successfully!" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Add sound files:" -ForegroundColor White
Write-Host "   - Place greeting sounds in: sounds\greeting_sounds\" -ForegroundColor White
Write-Host "   - Place thinking sounds in: sounds\thinking_sounds\" -ForegroundColor White
Write-Host "   - Place ack sounds in: sounds\ack_sounds\" -ForegroundColor White
Write-Host "   - Place error sounds in: sounds\error_sounds\" -ForegroundColor White
Write-Host ""
Write-Host "2. Add face images:" -ForegroundColor White
Write-Host "   - Place idle faces in: faces\idle\" -ForegroundColor White
Write-Host "   - Place listening faces in: faces\listening\" -ForegroundColor White
Write-Host "   - Place thinking faces in: faces\thinking\" -ForegroundColor White
Write-Host "   - Place speaking faces in: faces\speaking\" -ForegroundColor White
Write-Host "   - Place error faces in: faces\error\" -ForegroundColor White
Write-Host "   - Place warmup faces in: faces\warmup\" -ForegroundColor White
Write-Host ""
Write-Host "3. Download Piper TTS (optional):" -ForegroundColor White
Write-Host "   - Download from: https://github.com/rhasspy/piper/releases" -ForegroundColor White
Write-Host "   - Extract Windows build to: piper\ folder" -ForegroundColor White
Write-Host ""
Write-Host "4. Update config.json with your settings:" -ForegroundColor White
Write-Host "   - Change models (text_model, vision_model)" -ForegroundColor White
Write-Host "   - Adjust camera rotation if needed" -ForegroundColor White
Write-Host ""
Write-Host "5. To run the agent:" -ForegroundColor White
Write-Host '   - First activate venv: .\venv\Scripts\Activate.ps1' -ForegroundColor Cyan
Write-Host "   - Then run: python agent.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "6. Set up Ollama (required for LLM):" -ForegroundColor White
Write-Host "   - Download from: https://ollama.ai" -ForegroundColor White
Write-Host "   - Install and run: ollama pull gemma3:1b" -ForegroundColor White
Write-Host ""
Write-Host "7. Environment variables (set in .env or PowerShell):" -ForegroundColor White
Write-Host '   $env:GEMINI_API_KEY = "your-api-key-here"' -ForegroundColor Cyan
Write-Host ""
