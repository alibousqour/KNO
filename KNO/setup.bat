@echo off
REM =========================================================================
REM  Be More Agent Setup Script for Windows 10/11
REM  Replaces setup.sh with Windows-native commands
REM =========================================================================

echo.
echo ======================================================
echo   🤖 Be More Agent Setup Script for Windows
echo ======================================================
echo.

REM 1. Check Python is installed
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)
echo ✓ Python is installed

REM 2. Create virtual environment
echo.
echo [2/6] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo ✓ Virtual environment created
)

REM 3. Activate virtual environment and upgrade pip
echo.
echo [3/6] Activating virtual environment and upgrading pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
echo ✓ Virtual environment activated and pip upgraded

REM 4. Create necessary directories
echo.
echo [4/6] Creating project directories...
if not exist piper mkdir piper
if not exist sounds\greeting_sounds mkdir sounds\greeting_sounds
if not exist sounds\thinking_sounds mkdir sounds\thinking_sounds
if not exist sounds\ack_sounds mkdir sounds\ack_sounds
if not exist sounds\error_sounds mkdir sounds\error_sounds
if not exist faces\idle mkdir faces\idle
if not exist faces\listening mkdir faces\listening
if not exist faces\thinking mkdir faces\thinking
if not exist faces\speaking mkdir faces\speaking
if not exist faces\error mkdir faces\error
if not exist faces\warmup mkdir faces\warmup
if not exist whisper.cpp mkdir whisper.cpp
echo ✓ All directories created

REM 5. Install Python requirements
echo.
echo [5/6] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Python dependencies installed

REM 6. Download Piper TTS (optional - commented out; users can download manually)
echo.
echo [6/6] Setup Complete!
echo.
echo ======================================================
echo   ✓ Setup Completed Successfully!
echo ======================================================
echo.
echo NEXT STEPS:
echo.
echo 1. Add sound files:
echo    - Place greeting sounds in: sounds\greeting_sounds\
echo    - Place thinking sounds in: sounds\thinking_sounds\
echo    - Place ack sounds in: sounds\ack_sounds\
echo    - Place error sounds in: sounds\error_sounds\
echo.
echo 2. Add face images:
echo    - Place idle faces in: faces\idle\
echo    - Place listening faces in: faces\listening\
echo    - Place thinking faces in: faces\thinking\
echo    - Place speaking faces in: faces\speaking\
echo    - Place error faces in: faces\error\
echo    - Place warmup faces in: faces\warmup\
echo.
echo 3. Download Piper TTS (optional):
echo    - Download from: https://github.com/rhasspy/piper/releases
echo    - Extract to: piper\ folder
echo.
echo 4. Update config.json with your settings:
echo    - Change models (text_model, vision_model)
echo    - Adjust camera rotation if needed
echo.
echo 5. To run the agent:
echo    - First activate venv: venv\Scripts\activate.bat
echo    - Then run: python agent.py
echo.
echo 6. Set up Ollama (required for LLM):
echo    - Download from: https://ollama.ai
echo    - Install and run: ollama pull gemma3:1b
echo.
pause
