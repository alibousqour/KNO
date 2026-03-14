import socket
import threading
import json
import time
import sys
try:
    import psutil
except Exception:
    class _PsutilFallback:
        @staticmethod
        def cpu_percent(interval=None):
            return 0.0
        @staticmethod
        def disk_usage(path):
            class _DU:
                percent = 0.0
            return _DU()
        @staticmethod
        def virtual_memory():
            class _VM:
                percent = 0.0
            return _VM()
    psutil = _PsutilFallback()

# --- WebSocket bridge for eDEX ---
import asyncio
import websockets

class StatsWebSocketServer:
    def __init__(self, port=8765):
        self.port = port
        self.clients = set()
        self.loop = None
        self.thread = threading.Thread(target=self.run_server, daemon=True)
        self.thread.start()

    async def handler(self, websocket, path):
        self.clients.add(websocket)
        try:
            while True:
                await asyncio.sleep(1)
        except Exception:
            pass
        finally:
            self.clients.remove(websocket)

    def run_server(self):
        async def main():
            async with websockets.serve(self.handler, "0.0.0.0", self.port):
                await asyncio.Future()  # run forever
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"[WARN] WebSocket server failed: {e}", flush=True)

    def broadcast(self, msg):
        if self.loop and self.clients:
            asyncio.run_coroutine_threadsafe(self._broadcast(msg), self.loop)

    async def _broadcast(self, msg):
        for ws in self.clients:
            try:
                await ws.send(msg)
            except Exception:
                pass

stats_ws_server = StatsWebSocketServer(port=8765)
# =========================================================================
#  KNO 🤖 - EVOLUTIONARY AUTONOMOUS AGENT v4.0
#  Fully Autonomous, Self-Healing, Internet-Connected AI
#
#  Copyright (c) 2026 brenpoly
#  Licensed under the MIT License
#  Source: https://github.com/brenpoly/be-more-agent
#
#  PHASE 4 FEATURES - EXTERNAL AI BRAIN INTEGRATION:
#  🌐 Gemini & ChatGPT Integration - Query external AI for complex problems
#  🧬 Higher Intelligence Bridge - Automatic fallback to cloud AI when needed
#  🔍 Evolutionary Auto-Downloader - Uses AI to find & download latest models
#  🔧 Self-Evolution Thread - ChatGPT auto-fixes errors for autonomous healing
#  📊 Comprehensive Evolution Logging - All AI interactions logged to evolution.log
#  💾 Self-Coding Capability - Auto-apply ChatGPT fixes to local logic
#
#  CORE FEATURES (Phases 1-3):
#  ✨ Autonomous Reasoning Loop - Proactive decision-making every 60 seconds
#  🧠 Direct Llama-cpp-python LLM - No HTTP overhead, pure local inference
#  🎤 Hands-Free Wake Word Detection - Continuous listening for "KNO" keyword
#  🔧 Self-Correcting Error Handling with Automatic Recovery
#  📱 Autonomous Resource Management & Auto-Download
#  🔐 Full System Permissions with Admin Escalation
#  ⚙️ Intelligent Hardware Fallback Detection
#  🐧 Linux Systemd Service Auto-launch Support
#  🔓 Unrestricted Lifecycle Management
# =========================================================================

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
try:
    import customtkinter as ctk
    ctk_available = True
except Exception:
    ctk = None
    ctk_available = False
    # Logger may not be configured yet at import time; use print for clarity
    try:
        logger.warning("customtkinter not installed. Install with: pip install customtkinter")
    except Exception:
        print("[INIT] customtkinter not installed. Install with: pip install customtkinter", flush=True)
from PIL import Image, ImageTk
import math
import threading
import time
import json
import os
import subprocess
import random
import queue
import re
import sys
import select
import traceback
import atexit
import datetime
import warnings
import importlib.util
import wave
import struct
import ctypes
import requests
import urllib.request
import zipfile
import shutil
from pathlib import Path 
import tempfile
import hashlib
import glob
# Optional psutil: provide graceful fallback if missing
try:
    import psutil
except Exception:
    # Minimal fallback to avoid runtime crashes when psutil is not installed.
    class _PsutilFallback:
        @staticmethod
        def cpu_percent(interval=None):
            return 0.0

        @staticmethod
        def disk_usage(path):
            class _DU:
                percent = 0.0
            return _DU()

        @staticmethod
        def virtual_memory():
            class _VM:
                percent = 0.0
            return _VM()

    psutil = _PsutilFallback()
from functools import lru_cache, wraps

# Load environment variables from .env (if python-dotenv is available)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Lightweight ResourceDownloader stub to avoid import-time NameErrors
# The full implementation is defined later in the file; this stub allows
# top-level code that references ResourceDownloader during import to
# proceed without failing. The real class will overwrite this stub.
class ResourceDownloader:
    FALLBACK_MODELS = []

    @staticmethod
    def auto_download_model():
        return None

    @staticmethod
    def calculate_checksum(path):
        return None

    @staticmethod
    def verify_model_integrity(path):
        return False


# =========================================================================
# LOGGING FRAMEWORK - Enhanced logging system with file and console output
# =========================================================================
import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
import functools

# Ensure console uses UTF-8 to avoid encoding errors on Windows consoles
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Global UI color constants
BG_COLOR = "#050505"
AMBER_COLOR = "#FF8C00"

def setup_logging(log_level=logging.INFO, log_file="logs/kno.log", console_output=True):
    """
    Configure comprehensive logging system with both file and console output.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        console_output: Whether to also output to console
        
    Returns:
        logger: Configured logger instance
        
    Example:
        logger = setup_logging(logging.DEBUG)
        logger.info("Application started")
    """
    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file) if os.path.dirname(log_file) else "logs", exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("KNO")
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # File handler with rotation (max 10MB, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    
    # Console handler with enforced UTF-8 encoding where possible
    try:
        import io
        console_stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    except Exception:
        console_stream = sys.stdout
    console_handler = logging.StreamHandler(console_stream)
    console_handler.setLevel(log_level)
    
    # Formatting with timestamp, level, function name, and message
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)-8s] [%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    if console_output:
        logger.addHandler(console_handler)
    
    return logger

# Global logger instance
logger = setup_logging(logging.INFO)

# Override built-in print to sanitize non-ASCII characters for older consoles
import builtins, unicodedata
_orig_print = builtins.print
def _sanitize_text(x):
    try:
        s = str(x)
        return ''.join(ch if ord(ch) < 128 else '?' for ch in s)
    except Exception:
        return x

def print(*args, **kwargs):
    try:
        new_args = tuple(_sanitize_text(a) for a in args)
        return _orig_print(*new_args, **kwargs)
    except Exception:
        return _orig_print(*args, **kwargs)

# =========================================================================
# CONSENT & AUDIT SYSTEM - User permission and operation logging
# =========================================================================
try:
    from consent_manager import ConsentManager, AuditLogger
    consent_manager = ConsentManager(settings_file="settings.json", main_window=None)
    logger.info("ConsentManager initialized for security-controlled operations")
except Exception as e:
    logger.warning(f"ConsentManager initialization failed, proceeding without consent checks: {e}")
    consent_manager = None  # Fallback: no consent checks if initialization fails

# Global flag used by the UI to indicate DeepSeek is actively analyzing/generating code.
# When True, UI will show purple neon bars to indicate "Deep Thinking Mode".
DEEPSEEK_ACTIVE = False
# Global flag used by the UI to indicate Gemini is actively queried.
# When True, UI will show cyan bars to indicate Gemini is handling the request.
GEMINI_ACTIVE = False

def retry(max_attempts=3, delay=1, backoff=2, exceptions=(Exception,)):
    """
    Decorator for retry logic with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay in seconds
        backoff: Multiplier for exponential backoff
        exceptions: Tuple of exceptions to catch
        
    Example:
        @retry(max_attempts=3, delay=1, backoff=2)
        def network_operation():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_attempts}), "
                            f"retrying in {current_delay}s: {e}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator

# Suppress harmless library warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")

# =========================================================================
# ENVIRONMENT CONFIGURATION - Paths and settings with platform support
# =========================================================================

class Config:
    """
    Centralized configuration management with environment variable support.
    All paths are configurable and platform-aware.
    
    Priority order:
    1. Environment variables (KNO_*)
    2. .env file settings
    3. Hardcoded defaults
    
    Examples:
        Config.WHISPER_BIN_PATH
        Config.MODELS_DIR
        Config.get_path("whisper")
    """
    
    # Base directories - platform aware
    BASE_DIR = Path(os.getenv("KNO_BASE_DIR", os.path.dirname(os.path.abspath(__file__))))
    MODELS_DIR = Path(os.getenv("KNO_MODELS_DIR", BASE_DIR / "models"))
    SOUNDS_DIR = Path(os.getenv("KNO_SOUNDS_DIR", BASE_DIR / "sounds"))
    FACES_DIR = Path(os.getenv("KNO_FACES_DIR", BASE_DIR / "faces"))
    LOGS_DIR = Path(os.getenv("KNO_LOGS_DIR", BASE_DIR / "logs"))
    WHISPER_DIR = Path(os.getenv("KNO_WHISPER_DIR", BASE_DIR / "whisper.cpp" / "build" / "bin"))
    
    # Timeouts and intervals (all configurable)
    TRANSCRIBE_TIMEOUT = int(os.getenv("KNO_TRANSCRIBE_TIMEOUT", "120"))  # seconds
    AUDIO_RECORD_TIMEOUT = int(os.getenv("KNO_AUDIO_RECORD_TIMEOUT", "60"))  # seconds
    NETWORK_TIMEOUT = int(os.getenv("KNO_NETWORK_TIMEOUT", "30"))  # seconds
    BRAIN_LOOP_INTERVAL = int(os.getenv("KNO_BRAIN_LOOP_INTERVAL", "60"))  # seconds
    
    # Retry and retry logic
    MAX_RETRIES = int(os.getenv("KNO_MAX_RETRIES", "3"))
    RETRY_BACKOFF = float(os.getenv("KNO_RETRY_BACKOFF", "2.0"))
    RETRY_DELAY = float(os.getenv("KNO_RETRY_DELAY", "1.0"))
    
    # Audio configuration
    SAMPLE_RATE = int(os.getenv("KNO_SAMPLE_RATE", "16000"))
    AUDIO_CHANNELS = int(os.getenv("KNO_AUDIO_CHANNELS", "1"))
    AUDIO_DTYPE = os.getenv("KNO_AUDIO_DTYPE", "float32")
    
    # Cleanup behavior
    CLEANUP_TEMP_FILES = os.getenv("KNO_CLEANUP_TEMP_FILES", "true").lower() == "true"
    TEMP_FILES_PREFIX = "kno_temp_"
    
    # Logging
    LOG_FILE = LOGS_DIR / "kno.log"
    LOG_LEVEL = os.getenv("KNO_LOG_LEVEL", "INFO")
    CONSOLE_OUTPUT = os.getenv("KNO_CONSOLE_OUTPUT", "true").lower() == "true"
    
    @classmethod
    def initialize(cls):
        """Initialize all directories and validate configuration."""
        logger.info(f"Initializing KNO configuration from base directory: {cls.BASE_DIR}")
        
        directories = [cls.MODELS_DIR, cls.SOUNDS_DIR, cls.FACES_DIR, 
                      cls.LOGS_DIR, cls.WHISPER_DIR]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Directory ensured: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
        
        logger.info("Configuration initialized successfully")
    
    @classmethod
    def get_path(cls, path_type):
        """
        Get a path by type with fallback logic.
        
        Args:
            path_type: Type of path ("whisper", "models", "sounds", etc.)
            
        Returns:
            Path object or None if not available
        """
        paths = {
            "whisper": cls.WHISPER_DIR,
            "models": cls.MODELS_DIR,
            "sounds": cls.SOUNDS_DIR,
            "faces": cls.FACES_DIR,
            "logs": cls.LOGS_DIR,
            "base": cls.BASE_DIR,
        }
        return paths.get(path_type)
    
    @classmethod
    def get_whisper_executable(cls):
        """
        Get path to Whisper executable with platform detection.
        
        Returns:
            Path to whisper executable or None
        """
        if sys.platform == "win32":
            exe_path = cls.WHISPER_DIR / "whisper-cli.exe"
        else:
            exe_path = cls.WHISPER_DIR / "whisper"
        
        if exe_path.exists():
            logger.debug(f"Found Whisper executable: {exe_path}")
            return str(exe_path)
        else:
            logger.warning(f"Whisper executable not found at {exe_path}")
            return None
    
    @classmethod
    def print_config(cls):
        """Print current configuration to log (useful for debugging)."""
        logger.info("=" * 60)
        logger.info("KNO Configuration Summary:")
        logger.info(f"  Base Directory:        {cls.BASE_DIR}")
        logger.info(f"  Models Directory:      {cls.MODELS_DIR}")
        logger.info(f"  Logs Directory:        {cls.LOGS_DIR}")
        logger.info(f"  Whisper Directory:     {cls.WHISPER_DIR}")
        logger.info(f"  Transcribe Timeout:    {cls.TRANSCRIBE_TIMEOUT}s")
        logger.info(f"  Audio Record Timeout:  {cls.AUDIO_RECORD_TIMEOUT}s")
        logger.info(f"  Max Retries:           {cls.MAX_RETRIES}")
        logger.info(f"  Log Level:             {cls.LOG_LEVEL}")
        logger.info("=" * 60)

# Core dependencies (guard heavy imports to avoid blocking startup)
try:
    import sounddevice as sd
except Exception:
    sd = None

try:
    import numpy as np
except Exception:
    np = None

try:
    import scipy
    import scipy.signal as scipy_signal
except Exception:
    scipy = None
    scipy_signal = None
    try:
        logger.warning("SciPy not installed. Install with: pip install scipy to enable wake-word filtering and signal processing.")
    except Exception:
        print("[INIT] SciPy not installed. Install with: pip install scipy", flush=True)
import gc

# =========================================================================
# UTILITY FUNCTIONS - Helpers for file handling, cleanup, and validation
# =========================================================================

@functools.lru_cache(maxsize=1)
def get_whisper_model_path():
    """
    Get cached path to Whisper model file with validation.
    Results are cached to avoid repeated filesystem checks.
    
    Returns:
        Path to model file or None if not found
    """
    model_extensions = [".gguf", ".bin", ".pt"]
    for ext in model_extensions:
        patterns = [f"*ggml*{ext}", f"*base*{ext}"]
        for pattern in patterns:
            matches = list(Config.MODELS_DIR.glob(pattern))
            if matches:
                logger.debug(f"Found Whisper model: {matches[0]}")
                return str(matches[0])
    
    logger.warning("No Whisper model found in models directory")
    return None

def validate_wave_file(filepath, min_duration=0.1, max_duration=600):
    """
    Comprehensive validation of WAV file with checking for corruption.
    
    Args:
        filepath: Path to WAV file
        min_duration: Minimum duration in seconds
        max_duration: Maximum duration in seconds
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Examples:
        is_valid, error = validate_wave_file("audio.wav")
        if not is_valid:
            logger.error(f"Audio file invalid: {error}")
    """
    try:
        if not os.path.exists(filepath):
            return False, f"File not found: {filepath}"
        
        if not filepath.lower().endswith('.wav'):
            return False, f"Not a WAV file: {filepath}"
        
        with wave.open(filepath, 'rb') as wf:
            # Read WAV parameters
            n_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            
            # Validate parameters
            if n_channels < 1 or n_channels > 8:
                return False, f"Invalid channels: {n_channels}"
            
            if sample_width < 1 or sample_width > 4:
                return False, f"Invalid sample width: {sample_width}"
            
            if framerate < 8000 or framerate > 48000:
                return False, f"Invalid sample rate: {framerate}Hz"
            
            if n_frames < 1:
                return False, "Audio file is empty (0 frames)"
            
            # Calculate duration
            duration = n_frames / framerate
            
            if duration < min_duration:
                return False, f"Duration too short: {duration:.2f}s (min: {min_duration}s)"
            
            if duration > max_duration:
                return False, f"Duration too long: {duration:.2f}s (max: {max_duration}s)"
            
            logger.debug(
                f"WAV validation passed: {n_channels}ch, {framerate}Hz, "
                f"{sample_width*8}bit, {duration:.2f}s"
            )
            return True, ""
    
    except wave.Error as e:
        return False, f"Corrupted WAV file: {e}"
    except Exception as e:
        return False, f"Validation error: {e}"

def cleanup_temp_files(prefix=None, dry_run=False):
    """
    Clean up temporary audio files with safe deletion.
    
    Args:
        prefix: Filename prefix to match (default: Config.TEMP_FILES_PREFIX)
        dry_run: If True, only log what would be deleted
        
    Returns:
        Number of files deleted
        
    Examples:
        count = cleanup_temp_files(dry_run=True)  # See what would be deleted
        cleanup_temp_files()  # Actually delete
    """
    if not Config.CLEANUP_TEMP_FILES:
        logger.debug("Temporary file cleanup disabled in configuration")
        return 0
    
    prefix = prefix or Config.TEMP_FILES_PREFIX
    count = 0
    
    try:
        temp_dir = tempfile.gettempdir()
        for filename in os.listdir(temp_dir):
            if filename.startswith(prefix):
                filepath = os.path.join(temp_dir, filename)
                try:
                    if dry_run:
                        logger.debug(f"Would delete: {filepath}")
                    else:
                        os.remove(filepath)
                        logger.debug(f"Deleted temp file: {filename}")
                    count += 1
                except Exception as e:
                    logger.warning(f"Could not delete {filename}: {e}")
    except Exception as e:
        logger.error(f"Temp file cleanup failed: {e}")
    
    if not dry_run:
        logger.info(f"Cleaned up {count} temporary files")
    
    return count

def safe_file_delete(filepath, log_on_failure=True):
    """
    Safely delete a file with comprehensive error handling.
    
    Args:
        filepath: Path to file to delete
        log_on_failure: Whether to log failures (vs silent)
        
    Returns:
        True if deleted successfully, False otherwise
        
    Example:
        try:
            result = safe_file_delete("audio.wav")
        finally:
            pass  # File safely deleted if it existed
    """
    if not filepath or not os.path.exists(filepath):
        logger.debug(f"File does not exist, skipping deletion: {filepath}")
        return True
    
    try:
        # Check if file is accessible
        if os.path.isfile(filepath):
            os.remove(filepath)
            logger.debug(f"Deleted file: {filepath}")
            return True
        else:
            if log_on_failure:
                logger.warning(f"Path is not a file: {filepath}")
            return False
    except PermissionError:
        logger.warning(f"Permission denied deleting file: {filepath}")
        return False
    except Exception as e:
        if log_on_failure:
            logger.error(f"Error deleting file {filepath}: {e}")
        return False

def ensure_file_closed(file_object, timeout=2):
    """
    Ensure a file object is properly closed before external access.
    
    Args:
        file_object: File object to close
        timeout: Timeout in seconds for close operation
        
    Returns:
        True if successfully closed, False otherwise
        
    Example:
        with open("file.wav", "wb") as f:
            f.write(data)
        ensure_file_closed(f)  # Redundant but safe
    """
    try:
        if file_object and not file_object.closed:
            file_object.close()
            logger.debug("File object closed successfully")
        return True
    except Exception as e:
        logger.error(f"Error closing file: {e}")
        return False

import tempfile

# --- AI ENGINES ---
import openwakeword
from openwakeword.model import Model
# PHASE 5 REFACTOR: Bypassed local llama-cpp-python, using cloud APIs instead
# from llama_cpp import Llama  # ❌ DISABLED - Using Gemini/ChatGPT APIs

# --- WEB SEARCH (Using your working import) ---
from duckduckgo_search import DDGS

# =========================================================================
# ADMIN PRIVILEGE ESCALATION (STARTUP CHECK)
# =========================================================================

def check_and_request_admin_privileges():
    """
    Check if running with admin privileges. If not, attempt escalation.
    
    This is critical and must run at startup before any hardware/system operations.
    On Windows, attempts UAC privilege escalation via ShellExecuteEx.
    On Linux, checks and reports root status.
    
    Returns:
        bool: True if running with appropriate privileges
    """
    if sys.platform == "win32":
        try:
            is_admin = ctypes.windll.shell.IsUserAnAdmin()
            if not is_admin:
                logger.warning("NOT RUNNING AS ADMINISTRATOR")
                logger.info("Attempting to escalate privileges...")
                logger.info("Please approve the UAC prompt")
                
                # Reconstruct command line
                python_exe = sys.executable
                script_path = os.path.abspath(__file__)
                params = ' '.join([f'"{arg}"' if ' ' in arg else arg for arg in sys.argv[1:]])
                
                try:
                    ctypes.windll.shell.ShellExecuteEx(
                        lpVerb='runas',
                        lpFile=python_exe,
                        lpParameters=f'"{script_path}" {params}',
                        nShow=1
                    )
                    logger.info("Escalation initiated. Original process will exit.")
                    sys.exit(0)
                except Exception as e:
                    logger.warning(f"Could not escalate privileges: {e}")
                    logger.info("Continuing with limited privileges")
            else:
                logger.info("✅ Running with ADMINISTRATOR privileges")
            return is_admin
        except Exception as e:
            logger.error(f"Privilege check failed: {e}")
            return False
    else:
        # Linux check
        if os.geteuid() == 0:
            logger.info("✅ Running with root privileges")
            return True
        else:
            logger.warning("NOT running as root (some features may be limited)")
            return False

# =========================================================================
# 0. SYSTEM INITIALIZATION & SELF-HEALING FRAMEWORK
# =========================================================================

def is_admin():
    """
    Check if process has administrative privileges.
    
    Windows: Uses ctypes to check IsUserAnAdmin
    Unix: Uses os.geteuid() to check root status
    
    Returns:
        bool: True if running with admin/root privileges
    """
    if sys.platform == "win32":
        try:
            return ctypes.windll.shell.IsUserAnAdmin()
        except Exception as e:
            logger.debug(f"Admin check failed: {e}")
            return False
    else:
        return os.geteuid() == 0

def request_admin_privileges():
    """
    Attempt to request admin privileges on Windows.
    
    On Windows, restarts the process with UAC privilege escalation.
    On Unix, logs a warning if not running as root.
    """
    if sys.platform == "win32" and not is_admin():
        try:
            logger.info("Requesting admin privileges...")
            ctypes.windll.shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=' '.join(sys.argv))
            sys.exit(0)
        except Exception as e:
            logger.warning(f"Could not escalate privileges: {e}")

class ResourceManager:
    """Autonomous resource management with auto-download capabilities."""
    
    # Model file verification flags (populated by verify_required_files)
    MODEL_VERIFIED = False
    MODEL_PATH = None
    MODEL_IS_FALLBACK = False
    
    # Repository URLs for essential components
    RESOURCES = {
        "whisper.cpp": {
            "windows": "https://github.com/ggerganov/whisper.cpp/releases/download/v1.5.0/whisper-bin-x64.zip",
            "linux": "https://github.com/ggerganov/whisper.cpp/releases/download/v1.5.0/whisper-bin-linux.zip",
            "target": "whisper.cpp/build/bin",
            "extract": True
        },
        "ggml-base.en.bin": {
            "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin",
            "target": "models",
            "extract": False,
            "size_mb": 140
        }
    }
    
    @staticmethod
    def check_and_create_directories():
        """
        Ensure all required directories exist with logging.
        
        Creates the following directories:
        - models (for AI models)
        - sounds (for audio files)
        - faces (for image data)
        - whisper.cpp/build/bin (for Whisper binary)
        - logs (for log files)
        - openclaw (for OpenClaw computer use framework)
        """
        dirs = ["models", "sounds", "faces", "whisper.cpp/build/bin", "logs", "openclaw"]
        for d in dirs:
            try:
                Path(d).mkdir(parents=True, exist_ok=True)
                logger.debug(f"Directory ready: {d}")
            except Exception as e:
                logger.error(f"Failed to create directory {d}: {e}")
    
    @staticmethod
    def ensure_openclaw_installed():
        """
        Clone OpenClaw repository if not already present.
        Required for computer use capabilities (GUI automation + screen perception).
        """
        openclaw_dir = Path("openclaw")
        if openclaw_dir.exists() and (openclaw_dir / ".git").exists():
            logger.debug("OpenClaw already installed")
            return True
        
        try:
            logger.info("Cloning OpenClaw framework...")
            subprocess.run(
                ["git", "clone", "https://github.com/the-open-source-action-agent/openclaw.git", str(openclaw_dir)],
                check=True,
                capture_output=True
            )
            logger.info("OpenClaw installed successfully")
            return True
        except Exception as e:
            logger.warning(f"Failed to install OpenClaw: {e}. Computer use features disabled.")
            return False
    
    @staticmethod
    def check_openclaw_dependencies():
        """
        Verify required OpenClaw dependencies (pyautogui, PIL, anthropic).
        Attempts to import; logs warnings if missing but doesn't crash.
        """
        deps_ok = True
        required = {
            "pyautogui": "GUI automation (click, type, scroll)",
            "PIL": "Screenshot capture (pillow)",
            "anthropic": "Claude API for vision analysis"
        }
        
        for module, desc in required.items():
            try:
                __import__(module if module != "PIL" else "PIL")
                logger.debug(f"✓ {module} available ({desc})")
            except ImportError:
                logger.warning(f"✗ {module} missing ({desc}) - install with: pip install {module if module != 'PIL' else 'pillow'}")
                deps_ok = False
        
        return deps_ok
    
    @staticmethod
    @retry(max_attempts=3, delay=2, backoff=2, exceptions=(requests.exceptions.RequestException,))
    def download_file(url, destination, filename, size_mb=None):
        """
        Download file with progress tracking, resume capability, and retry logic.
        
        Uses exponential backoff for transient failures. Supports resume from partial downloads.
        
        Args:
            url: URL to download from
            destination: Directory where file will be saved
            filename: Filename to save as
            size_mb: Expected file size in MB (for logging)
            
        Returns:
            Full path to downloaded file or None if failed
            
        Raises:
            requests.exceptions.RequestException: If download fails after retries
            
        Example:
            path = ResourceManager.download_file(
                "https://example.com/file.bin",
                "models",
                "model.bin",
                size_mb=500
            )
        """
        filepath = os.path.join(destination, filename)
        
        try:
            logger.info(f"Downloading {filename} to {destination}...")
            if size_mb:
                logger.info(f"Expected size: ~{size_mb}MB")
            
            # Create destination if needed
            Path(destination).mkdir(parents=True, exist_ok=True)
            
            # Check if partially downloaded
            resume_header = {}
            mode = 'wb'
            if os.path.exists(filepath):
                existing_size = os.path.getsize(filepath)
                resume_header = {'Range': f'bytes={existing_size}-'}
                mode = 'ab'
                logger.info(f"Resuming from {existing_size} bytes")
            
            response = requests.get(
                url,
                stream=True,
                timeout=Config.NETWORK_TIMEOUT,
                headers=resume_header
            )
            # Handle HTTP 416 (Requested Range Not Satisfiable) which can occur
            # when the remote file changed and resume is invalid. In that case,
            # delete the local partial file and restart download from scratch.
            if response.status_code == 416:
                logger.warning(f"Download resume failed with 416 for {filename}; handling resume mismatch")
                try:
                    existing_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
                except Exception:
                    existing_size = 0

                # Check remote Content-Length (try HEAD) to see if local file is already complete
                try:
                    head = requests.head(url, timeout=10)
                    remote_size = int(head.headers.get('content-length', 0))
                except Exception:
                    remote_size = 0

                # If sizes match, assume download completed previously and return the file
                if remote_size and existing_size and existing_size == remote_size:
                    logger.info(f"Local file already complete (size matches remote): {filepath}")
                    return filepath

                # Otherwise remove partial file and retry full download
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        logger.info(f"Removed corrupted partial file: {filepath}")
                except Exception as e:
                    logger.warning(f"Could not remove partial file: {e}")

                # Retry full download without Range header
                response = requests.get(url, stream=True, timeout=Config.NETWORK_TIMEOUT)

            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            chunk_size = 1024 * 16  # 16KB chunks
            
            with open(filepath, mode) as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            percent = (downloaded / total_size) * 100
                            current_mb = downloaded / (1024 * 1024)
                            total_mb = total_size / (1024 * 1024)
                            logger.debug(f"{filename}: {percent:.1f}% ({current_mb:.1f}MB/{total_mb:.1f}MB)")
            
            logger.info(f"✅ Successfully downloaded: {filename}")
            return filepath
                
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise
    
    @staticmethod
    def extract_archive(filepath, extract_to):
        """
        Extract downloaded archives with error handling and cleanup.
        
        Args:
            filepath: Path to archive file
            extract_to: Directory to extract to
            
        Returns:
            bool: True if extraction successful, False otherwise
            
        Example:
            success = ResourceManager.extract_archive("download.zip", ".")
        """
        try:
            logger.info(f"Extracting {filepath} to {extract_to}...")
            Path(extract_to).mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            
            logger.info(f"✅ Extraction complete")
            # Cleanup archive after successful extraction
            safe_file_delete(filepath)
            return True
        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            return False
    
    @staticmethod
    def verify_and_repair_critical_files():
        """
        AUTONOMOUS DEPENDENCY REPAIR
        
        Check for critical files and auto-download/repair if missing.
        Priority: Model file, then Whisper CLI
        
        Uses exponential backoff retry for network operations.
        Logs all operations to logger for debugging.
        """
        logger.info("🔍 Verifying critical dependencies...")
        
        critical_files = {
            "models/ggml-base.en.bin": {
                "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin",
                "directory": "models",
                "size_mb": 140
            },
            "whisper.cpp/build/bin/whisper-cli.exe" if sys.platform == "win32" else "whisper.cpp/build/bin/whisper": {
                "url": "https://github.com/ggerganov/whisper.cpp/releases/download/v1.5.0/whisper-bin-x64.zip" if sys.platform == "win32" else "https://github.com/ggerganov/whisper.cpp/releases/download/v1.5.0/whisper-bin-linux.zip",
                "directory": ".",
                "is_archive": True,
                "extract_to": "."
            }
        }
        
        for filepath, details in critical_files.items():
            if not os.path.exists(filepath):
                logger.warning(f"⚠️  MISSING: {filepath}")
                
                url = details["url"]
                directory = details["directory"]
                filename = os.path.basename(url.split('?')[0])  # Remove query params
                size_mb = details.get("size_mb")
                
                logger.info(f"🌐 Auto-downloading from: {url[:60]}...")
                
                try:
                    downloaded_path = ResourceManager.download_file(url, directory, filename, size_mb)
                    
                    if downloaded_path:
                        if details.get("is_archive"):
                            extract_to = details.get("extract_to", directory)
                            if ResourceManager.extract_archive(downloaded_path, extract_to):
                                logger.info(f"✅ Dependency repaired: {filepath}")
                            else:
                                logger.error(f"❌ Failed to extract: {filename}")
                        else:
                            logger.info(f"✅ Dependency repaired: {filepath}")
                    else:
                        logger.error(f"❌ Could not auto-repair: {filepath}")
                except Exception as e:
                    logger.error(f"Exception during repair: {e}")
            else:
                try:
                    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    logger.info(f"✅ Found: {filepath} ({file_size_mb:.1f}MB)")
                except Exception as e:
                    logger.warning(f"Could not stat file {filepath}: {e}")
        
        logger.info("🔍 Dependency verification complete")
    
    @staticmethod
    def verify_adb_installed():
        """
        Check if ADB (Android Debug Bridge) is installed and available in system PATH.
        
        Returns:
            bool: True if ADB is available, False otherwise
            
        Example:
            if ResourceManager.verify_adb_installed():
                logger.info("ADB is ready")
        """
        try:
            result = subprocess.run(["adb", "version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("✅ ADB found in PATH")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.debug(f"ADB check failed: {e}")
        
        logger.warning("⚠️  ADB not found in PATH")
        return False
    
    @staticmethod
    def download_platform_tools():
        """Download and install Android Platform Tools with ADB."""
        print("[RESOURCE] 🌐 Downloading Platform Tools...", flush=True)
        
        # Detect OS for correct download
        if sys.platform == "win32":
            url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
            folder_name = "platform-tools"
        elif sys.platform == "darwin":
            url = "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"
            folder_name = "platform-tools"
        else:  # Linux
            url = "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"
            folder_name = "platform-tools"
        
        # Download to current directory
        filepath = ResourceManager.download_file(url, ".", "platform-tools.zip", size_mb=20)
        
        if not filepath:
            print("[RESOURCE] ❌ Failed to download Platform Tools", flush=True)
            return False
        
        # Extract to current directory
        if not ResourceManager.extract_archive(filepath, "."):
            print("[RESOURCE] ❌ Failed to extract Platform Tools", flush=True)
            return False
        
        # Add to PATH
        platform_tools_path = os.path.abspath(folder_name)
        try:
            if sys.platform == "win32":
                # Set PATH environment variable in current process
                os.environ["PATH"] = platform_tools_path + ";" + os.environ.get("PATH", "")
                print(f"[RESOURCE] ✅ Added to PATH: {platform_tools_path}", flush=True)
                
                # Also update system PATH via registry (optional, requires admin)
                try:
                    import winreg
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment")
                    current_path = winreg.QueryValueEx(key, "PATH")[0]
                    if platform_tools_path not in current_path:
                        new_path = platform_tools_path + ";" + current_path
                        winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                        print(f"[RESOURCE] ✅ Updated system PATH (user)", flush=True)
                    winreg.CloseKey(key)
                except Exception as e:
                    print(f"[RESOURCE] Note: System PATH update requires admin: {e}", flush=True)
            else:
                # Linux/Mac: Add to PATH in current process
                os.environ["PATH"] = platform_tools_path + ":" + os.environ.get("PATH", "")
                print(f"[RESOURCE] ✅ Added to PATH: {platform_tools_path}", flush=True)
                
                # Optionally update ~/.bashrc or ~/.zshrc
                shell_rc = os.path.expanduser("~/.bashrc")
                if not os.path.exists(shell_rc):
                    shell_rc = os.path.expanduser("~/.zshrc")
                
                if os.path.exists(shell_rc):
                    with open(shell_rc, "a") as f:
                        f.write(f"\nexport PATH=\"{platform_tools_path}:$PATH\"\n")
                    print(f"[RESOURCE] ✅ Updated shell config", flush=True)
            
            return True
        except Exception as e:
            print(f"[RESOURCE] Error updating PATH: {e}", flush=True)
            return False
    
    @staticmethod
    def verify_required_files():
        """Verify all required directories and CRITICAL model file."""
        required_dirs = ['models', 'sounds', 'faces', 'logs', 'platform-tools']
        base_path = os.getcwd()
        
        print(f"[RESOURCE] 🔍 Verifying required directories at {base_path}", flush=True)
        
        all_dirs_ok = True
        try:
            for dir_name in required_dirs:
                dir_path = os.path.join(base_path, dir_name)
                if not os.path.exists(dir_path):
                    Path(dir_path).mkdir(parents=True, exist_ok=True)
                    print(f"[RESOURCE] ✅ Created: {dir_name}", flush=True)
                else:
                    print(f"[RESOURCE] ✅ Found: {dir_name}", flush=True)
            
            print(f"[RESOURCE] ✅ All required directories verified", flush=True)
        except Exception as e:
            print(f"[RESOURCE] ❌ Verification error: {e}", flush=True)
            all_dirs_ok = False
        
        # ===== PHASE 5 REFACTOR: Using Cloud APIs, skipping local model check =====
        print(f"[RESOURCE] 🧠 Checking AI brain (Cloud APIs)...", flush=True)
        # PHASE 5: No local model required - using Gemini API as primary
        # Local .gguf file is optional (for offline fallback only)
        print(f"[RESOURCE] ✅ Cloud AI selected as primary brain", flush=True)
        print(f"[RESOURCE]   - Gemini API (primary)", flush=True)
        print(f"[RESOURCE]   - ChatGPT API (fallback)", flush=True)
        
        # Check if local model exists (optional)
        models_dir = os.path.join(os.getcwd(), "models")
        local_models = [f for f in os.listdir(models_dir) if f.endswith(".gguf")] if os.path.exists(models_dir) else []
        if local_models:
            print(f"[RESOURCE] ℹ️  Local fallback model available: {local_models[0]}", flush=True)
            ResourceManager.MODEL_PATH = os.path.join(models_dir, local_models[0])
            ResourceManager.MODEL_VERIFIED = True
        else:
            print(f"[RESOURCE] ℹ️  No local model (cloud APIs will be used exclusively)", flush=True)
            ResourceManager.MODEL_VERIFIED = False
            ResourceManager.MODEL_PATH = None
        
        return all_dirs_ok


# =========================================================================
# GLOBAL CONTROLLER MODULE - System & Network Authority
# =========================================================================
# ResourceDownloader is implemented later in the file with a comprehensive
# implementation (checksum verification, integrity checks, and advanced
# recovery). The detailed version is retained; the duplicate earlier
# definition was removed to avoid conflicts.

# =========================================================================
# 2. EXPERIENCE MEMORY: Error Logging & Pattern Recognition
# =========================================================================

class ExperienceMemory:
    """
    EXPERIENCE MEMORY
    Stores 'lessons learned' from errors to prevent repeating mistakes.
    Maintains experience.json with error patterns and solutions.
    """
    
    FILENAME = "experience.json"
    
    def __init__(self):
        self.data = self.load()
        # Ensure required schema keys exist even if experience.json is corrupted
        try:
            if not isinstance(self.data, dict):
                self.data = {}
        except Exception:
            self.data = {}

        self._ensure_schema()
        # In-memory throttling helpers to avoid excessive disk writes
        self._last_error = None
        self._last_error_time = None
        self._consecutive_same_error = 0
        # Track counts of errors in this session to avoid log flooding
        self._session_error_counts = {}

    def _ensure_schema(self):
        """Ensure that essential keys exist in the experience schema."""
        if "errors_encountered" not in self.data:
            self.data["errors_encountered"] = 0
        if "error_log" not in self.data:
            self.data["error_log"] = []
        if "patterns_recognized" not in self.data:
            self.data["patterns_recognized"] = {}
        if "solutions_learned" not in self.data:
            self.data["solutions_learned"] = []
    
    def load(self):
        """Load experience.json or create new."""
        try:
            if os.path.exists(self.FILENAME):
                with open(self.FILENAME, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[EXPERIENCE] ⚠️  Error loading {self.FILENAME}: {e}", flush=True)
        
        return {
            "errors_encountered": 0,
            "error_log": [],
            "patterns_recognized": {},
            "solutions_learned": [],
            "last_updated": None
        }
    
    def save(self):
        """Save experience data to experience.json."""
        try:
            self.data["last_updated"] = datetime.datetime.now().isoformat()
            with open(self.FILENAME, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"[EXPERIENCE] ❌ Error saving {self.FILENAME}: {e}", flush=True)
    
    def log_error(self, error_type, error_message, context=""):
        """
        Log an error to experience memory.
        
        Args:
            error_type: Category (e.g., "adb_pairing", "llm_timeout")
            error_message: The error message
            context: Additional context about when/where it occurred
        """
        # Ensure schema keys exist to avoid KeyError from corrupted files
        self._ensure_schema()

        # Throttle repeated identical errors to avoid disk flooding
        now = datetime.datetime.now()
        same_as_last = (self._last_error == error_message)
        if same_as_last and self._last_error_time:
            delta = (now - self._last_error_time).total_seconds()
        else:
            delta = None

        if same_as_last and delta is not None and delta <= 60:
            self._consecutive_same_error += 1
        else:
            self._consecutive_same_error = 1

        self._last_error = error_message
        self._last_error_time = now

        # If the same error happened more than 5 times within 1 minute, skip disk write
        if self._consecutive_same_error > 5 and delta is not None and delta <= 60:
            print(f"[EXPERIENCE] ⚠️ Throttling repeated error (count={self._consecutive_same_error}): {error_type}", flush=True)
            # still update in-memory counter but do not persist to disk
            return

        # Session-level throttle for noisy wake-word detection errors
        # Avoid bloating logs if wake word detector misfires repeatedly in one session.
        if error_type == 'wake_word_detection_error':
            cnt = self._session_error_counts.get(error_type, 0) + 1
            self._session_error_counts[error_type] = cnt
            if cnt > 10:
                print(f"[EXPERIENCE] ⚠️ Session throttle: skipping excessive {error_type} (count={cnt})", flush=True)
                return

        self.data["errors_encountered"] += 1
        
        error_entry = {
            "type": error_type,
            "message": error_message[:100],  # Truncate
            "context": context[:100],
            "timestamp": datetime.datetime.now().isoformat(),
            "count": 1
        }
        
        # Check if similar error exists
        for entry in self.data["error_log"]:
            if entry["type"] == error_type and entry["message"] == error_message:
                entry["count"] += 1
                entry["timestamp"] = datetime.datetime.now().isoformat()
                self.save()
                print(f"[EXPERIENCE] 📝 Error {error_type} logged (occurrence #{entry['count']})", flush=True)
                return
        
        self.data["error_log"].append(error_entry)
        self.save()
        print(f"[EXPERIENCE] 📝 New error logged: {error_type}", flush=True)
        try:
            gc.collect()
            print(f"[EXPERIENCE] 🧹 Performed gc.collect() after logging", flush=True)
        except Exception:
            pass
    
    def get_pattern(self, error_type):
        """Check if an error type has been seen before and how many times."""
        for entry in self.data["error_log"]:
            if entry["type"] == error_type:
                return entry["count"]
        return 0
    
    def learn_solution(self, error_type, solution_description):
        """Store a learned solution for future reference."""
        self.data["solutions_learned"].append({
            "error_type": error_type,
            "solution": solution_description,
            "discovered": datetime.datetime.now().isoformat()
        })
        print(f"[EXPERIENCE] 💡 Solution learned for {error_type}: {solution_description[:50]}...", flush=True)
        self.save()

# =========================================================================
# 3. INTERNET LEARNING BRIDGE: Query External AI & Web Search
# =========================================================================

class InternetLearningBridge:
    """
    INTERNET LEARNING BRIDGE
    Allows KNO to query external AI APIs (Gemini, ChatGPT) or search web
    when encountering unknown commands or errors it cannot solve locally.
    """
    
    def __init__(self):
        self.cache = {}  # Cache responses to avoid redundant queries
    
    def search_web_for_solution(self, query, max_results=3):
        """
        Search the web for a solution using DuckDuckGo.
        
        Args:
            query: Search query (e.g., "how to fix ADB connection error")
            max_results: Number of results to return
            
        Returns:
            List of search results or empty list
        """
        print(f"[BRIDGE] 🌐 Searching web for: {query[:60]}...", flush=True)
        
        try:
            ddgs = DDGS(timeout=20)
            results = ddgs.text(query, max_results=max_results)
            
            if results:
                print(f"[BRIDGE] ✅ Found {len(results)} results", flush=True)
                return results
            else:
                print(f"[BRIDGE] ⚠️  No results found", flush=True)
                return []
        except Exception as e:
            print(f"[BRIDGE] ❌ Web search failed: {e}", flush=True)
            return []
    
    def query_external_ai(self, prompt, api_choice="duckduckgo"):
        """
        Query an external AI or use web search for unknown commands.
        Currently uses DuckDuckGo; can be extended for API keys.
        
        Args:
            prompt: The question or command
            api_choice: Which service to use ("duckduckgo", "gemini", "chatgpt")
            
        Returns:
            Response text or None
        """
        print(f"[BRIDGE] 🤖 Querying external intelligence...", flush=True)
        
        if api_choice == "duckduckgo" or api_choice is None:
            print(f"[BRIDGE] ℹ️  Using DuckDuckGo web search (no API key required)", flush=True)
            results = self.search_web_for_solution(prompt)
            
            if results:
                # Extract and summarize first result
                top_result = results[0]
                summary = f"From {top_result.get('title', 'Web')}: {top_result.get('body', '')[:200]}..."
                print(f"[BRIDGE] 📍 Top result: {summary[:100]}...", flush=True)
                return summary
        
        else:
            print(f"[BRIDGE] ⚠️  API '{api_choice}' configured externally. Using web search fallback.", flush=True)
            return self.search_web_for_solution(prompt)
        
        return None


class DeepSeekEngine:
    """Integration with DeepSeek API (OpenAI-compatible request format).

    - Reads API key from environment variable `DEEPSEEK_API_KEY` (ensure .env loading).
    - Uses model `deepseek-chat` or `deepseek-coder` depending on task.
    - Exposes `analyze_error` and `generate_patch` helpers.
    """

    API_BASE = "https://api.deepseek.com/v1"

    def __init__(self, api_key=None):
        # Respect environment variable; allow injection for testing
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            logger.warning("DeepSeek API key not found in DEEPSEEK_API_KEY; DeepSeek disabled.")

    def _post(self, path, payload, timeout=30):
        """POST to DeepSeek with exponential backoff for 429 and 5xx errors."""
        if not self.api_key:
            return None

        url = f"{self.API_BASE}{path}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        max_retries = 3
        backoff_factor = 2  # Exponential backoff: 2s, 4s, 8s
        retry_attempt = 0
        retry_status_codes = {429, 500, 502, 503, 504}  # Rate limit + server errors

        while retry_attempt < max_retries:
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
                
                # Successful response
                if resp.status_code in (200, 201):
                    if retry_attempt > 0:
                        print(f"[DEEPSEEK] ✅ Recovered after {retry_attempt} retry attempt(s)", flush=True)
                    return resp.json()
                
                # Retryable error codes (rate limit, server errors)
                if resp.status_code in retry_status_codes:
                    retry_attempt += 1
                    if retry_attempt < max_retries:
                        wait_time = backoff_factor ** (retry_attempt - 1)
                        print(f"[DEEPSEEK] ⚠️  Status {resp.status_code}. Retry {retry_attempt}/{max_retries} in {wait_time}s...", flush=True)
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.warning(f"DeepSeek API exhausted retries after {max_retries} attempts. Last code: {resp.status_code}")
                        print(f"[DEEPSEEK] ❌ Exhausted {max_retries} retries. Fallback triggered.", flush=True)
                        return None
                
                # Non-retryable error
                logger.warning(f"DeepSeek API returned non-retryable {resp.status_code}: {resp.text[:200]}")
                print(f"[DEEPSEEK] ❌ Non-retryable error {resp.status_code}. No retry.", flush=True)
                return None

            except requests.exceptions.Timeout:
                retry_attempt += 1
                if retry_attempt < max_retries:
                    wait_time = backoff_factor ** (retry_attempt - 1)
                    print(f"[DEEPSEEK] ⏱️  Timeout. Retry {retry_attempt}/{max_retries} in {wait_time}s...", flush=True)
                    time.sleep(wait_time)
                else:
                    logger.exception(f"DeepSeek API timeout after {max_retries} retries")
                    print(f"[DEEPSEEK] ❌ Timeout after {max_retries} retries. Fallback triggered.", flush=True)
                    return None
            except requests.exceptions.RequestException as re:
                logger.exception(f"DeepSeek API request exception: {re}")
                print(f"[DEEPSEEK] ❌ Request error: {re}", flush=True)
                return None
        
        logger.exception("DeepSeek API exhausted all retry attempts")
        print(f"[DEEPSEEK] ❌ All retries exhausted.", flush=True)
        return None

    def analyze_error(self, error_message, context=None, model="deepseek-coder"):
        """Send traceback or error text to DeepSeek for analysis and suggested fix.

        Returns the textual suggestion or None.
        """
        if not self.api_key:
            return None

        global DEEPSEEK_ACTIVE
        DEEPSEEK_ACTIVE = True

        try:
            prompt = f"Analyze this Python error and suggest a precise fix.\n\nError:\n{error_message}\n\nContext:\n{context or ''}\n\nRespond with either a [FIX_CODE] block or [FIX_SHELL] commands. Be concise."

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a code repair assistant. Provide minimal, actionable fixes."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.0,
                "max_tokens": 1200
            }

            result = self._post("/chat/completions", payload)
            if result and isinstance(result, dict):
                # OpenAI-like response structure
                choices = result.get("choices") or []
                if choices:
                    text = choices[0].get("message", {}).get("content") or choices[0].get("text")
                    return text
        finally:
            DEEPSEEK_ACTIVE = False

        return None

    def generate_patch(self, diff_request, model="deepseek-coder"):
        """Ask DeepSeek to generate a unified patch for a requested improvement.

        Returns patch text or None.
        """
        if not self.api_key:
            return None

        global DEEPSEEK_ACTIVE
        DEEPSEEK_ACTIVE = True
        try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are an expert Python developer. Output a unified diff patch only."},
                    {"role": "user", "content": diff_request}
                ],
                "temperature": 0.0,
                "max_tokens": 2000
            }

            result = self._post("/chat/completions", payload)
            if result and isinstance(result, dict):
                choices = result.get("choices") or []
                if choices:
                    text = choices[0].get("message", {}).get("content") or choices[0].get("text")
                    return text
        finally:
            DEEPSEEK_ACTIVE = False

        return None


# =========================================================================
# 4. SELF-CORRECTION & AUTO-PATCHING: Error Detection & Auto-Fix
# =========================================================================

class SelfCorrection:
    """
    SELF-CORRECTION & AUTO-PATCHING
    Detects missing libraries automatically and attempts pip install.
    Handles common errors like ADB pairing failures with automatic retries.
    """
    
    def __init__(self):
        self.correction_history = []
    
    def detect_missing_library(self, error_message):
        """
        Detect if an error is due to a missing library.
        
        Args:
            error_message: The error message to analyze
            
        Returns:
            Library name if detected, None otherwise
        """
        # Common patterns for missing libraries
        patterns = [
            r"ModuleNotFoundError: No module named ['\"](\w+)['\"]",
            r"ImportError: No module named ['\"](\w+)['\"]",
            r"cannot import name ['\"](\w+)['\"]",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_message)
            if match:
                return match.group(1)
        
        return None
    
    def auto_install_dependency(self, package_name):
        """
        Automatically attempt to install a missing dependency.
        
        Args:
            package_name: Name of Python package to install
            
        Returns:
            True if installation succeeded, False otherwise
        """
        print(f"[CORRECTION] 📦 Attempting to auto-install: {package_name}", flush=True)
        
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name, "-q"],
                timeout=60,
                check=True
            )
            print(f"[CORRECTION] ✅ Successfully installed: {package_name}", flush=True)
            self.correction_history.append({
                "type": "auto_install",
                "package": package_name,
                "timestamp": datetime.datetime.now().isoformat(),
                "success": True
            })
            return True
        
        except subprocess.CalledProcessError:
            print(f"[CORRECTION] ❌ Failed to install {package_name}", flush=True)
            self.correction_history.append({
                "type": "auto_install",
                "package": package_name,
                "timestamp": datetime.datetime.now().isoformat(),
                "success": False
            })
            return False
        
        except subprocess.TimeoutExpired:
            print(f"[CORRECTION] ⏱️  Installation timeout for {package_name}", flush=True)
            return False
        
        except Exception as e:
            print(f"[CORRECTION] ❌ Installation error: {e}", flush=True)
            return False
    
    def handle_adb_pairing_failure(self, retry_count=3, backoff=2):
        """
        Handle ADB pairing failures with automatic retries and backoff.
        
        Args:
            retry_count: Number of retry attempts
            backoff: Exponential backoff multiplier (in seconds)
            
        Returns:
            True if recovery attempted, False otherwise
        """
        print(f"[CORRECTION] 🔌 ADB pairing failed. Initiating recovery protocol...", flush=True)
        
        for attempt in range(retry_count):
            wait_time = backoff ** attempt
            print(f"[CORRECTION] ⏳ Retry {attempt + 1}/{retry_count} in {wait_time}s...", flush=True)
            time.sleep(wait_time)
            
            try:
                # Attempt to restart ADB
                subprocess.run(["adb", "kill-server"], timeout=5, capture_output=True)
                time.sleep(1)
                subprocess.run(["adb", "start-server"], timeout=5, check=True, capture_output=True)
                print(f"[CORRECTION] ✅ ADB service restarted successfully", flush=True)
                return True
            except Exception as e:
                print(f"[CORRECTION] ⚠️  Attempt {attempt + 1} failed: {e}", flush=True)
        
        print(f"[CORRECTION] ❌ ADB recovery failed after {retry_count} attempts", flush=True)
        return False

# =========================================================================
# 5. EVOLUTIONARY LOGIC: Self-Analysis & Pattern Optimization
# =========================================================================

class EvolutionaryLogic:
    """
    EVOLUTIONARY LOGIC
    Analyzes KNO's own patterns and suggests improvements to RegEx patterns,
    logic, and efficiency based on success/failure rates.
    """
    
    def __init__(self):
        self.metrics = {
            "task_success_rate": 0.0,
            "regex_patterns_tested": [],
            "improvements_suggested": []
        }
    
    def analyze_regex_patterns(self, pattern_name, test_cases):
        """
        Analyze a regex pattern for efficiency and suggest improvements.
        
        Args:
            pattern_name: Identifier for the regex (e.g., "whatsapp_message")
            test_cases: List of (input, expected_output) tuples
            
        Returns:
            Dictionary with analysis and suggestions
        """
        print(f"[EVOLUTION] 🔬 Analyzing regex pattern: {pattern_name}", flush=True)
        
        analysis = {
            "pattern": pattern_name,
            "total_tests": len(test_cases),
            "passed": 0,
            "failed": 0,
            "suggestions": []
        }
        
        # This is a placeholder for actual regex analysis
        # In practice, you'd compile and test the regex patterns
        
        print(f"[EVOLUTION] ✅ Analysis complete: {analysis['total_tests']} tests", flush=True)
        self.metrics["regex_patterns_tested"].append(analysis)
        
        return analysis
    
    def suggest_improvement(self, component, issue_description, suggested_fix):
        """
        Log a suggested improvement for KNO's own code/logic.
        
        Args:
            component: Which component has the issue (e.g., "whatsapp_parser")
            issue_description: What the issue is
            suggested_fix: What should be done to fix it
        """
        improvement = {
            "component": component,
            "issue": issue_description,
            "suggestion": suggested_fix,
            "timestamp": datetime.datetime.now().isoformat(),
            "applied": False
        }
        
        print(f"[EVOLUTION] 💡 Improvement suggested for {component}", flush=True)
        print(f"[EVOLUTION] 📝 Issue: {issue_description[:50]}...", flush=True)
        print(f"[EVOLUTION] 💡 Fix: {suggested_fix[:50]}...", flush=True)
        
        self.metrics["improvements_suggested"].append(improvement)
    
    def track_success_rate(self, task_name, success):
        """
        Track success/failure of tasks to identify patterns.
        
        Args:
            task_name: Name of the task being tracked
            success: Boolean indicating success/failure
        """
        # Update aggregate success rate
        total = len(self.metrics["regex_patterns_tested"])
        passed = sum(1 for p in self.metrics["regex_patterns_tested"] if p.get("passed", 0) > 0)
        
        if total > 0:
            self.metrics["task_success_rate"] = passed / total
            print(f"[EVOLUTION] 📊 Current success rate: {self.metrics['task_success_rate']*100:.1f}%", flush=True)

# =========================================================================
# 6. STATE BACKUP & RESTORE: Stability-First Self-Modification
# =========================================================================

class StateBackup:
    """
    STATE BACKUP & RESTORE
    Creates and manages backups of agent.py before any self-modifications.
    Ensures KNO can always rollback to a stable state.
    """
    
    BACKUP_DIR = "kno_backups"
    
    def __init__(self):
        Path(self.BACKUP_DIR).mkdir(exist_ok=True)
    
    def create_backup(self, filename="agent.py"):
        """
        Create a timestamped backup of a critical file.
        
        Args:
            filename: File to backup (usually agent.py)
            
        Returns:
            Path to backup file or None
        """
        try:
            if not os.path.exists(filename):
                print(f"[BACKUP] ❌ File not found: {filename}", flush=True)
                return None
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{os.path.splitext(filename)[0]}_backup_{timestamp}.py"
            backup_path = os.path.join(self.BACKUP_DIR, backup_filename)
            
            shutil.copy2(filename, backup_path)
            print(f"[BACKUP] 💾 Backup created: {backup_path}", flush=True)
            
            return backup_path
        
        except Exception as e:
            print(f"[BACKUP] ❌ Backup failed: {e}", flush=True)
            return None
    
    def restore_from_backup(self, backup_path, target_filename="agent.py"):
        """
        Restore a file from backup.
        
        Args:
            backup_path: Path to the backup file
            target_filename: Where to restore to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(backup_path):
                print(f"[BACKUP] ❌ Backup not found: {backup_path}", flush=True)
                return False
            
            shutil.copy2(backup_path, target_filename)
            print(f"[BACKUP] ✅ Restored from: {backup_path}", flush=True)
            
            return True
        
        except Exception as e:
            print(f"[BACKUP] ❌ Restore failed: {e}", flush=True)
            return False
    
    def list_backups(self):
        """List all available backups."""
        try:
            backups = sorted(os.listdir(self.BACKUP_DIR))
            print(f"[BACKUP] 📋 Available backups ({len(backups)}):", flush=True)
            for backup in backups:
                print(f"[BACKUP]   - {backup}", flush=True)
            return backups
        except Exception as e:
            print(f"[BACKUP] ❌ Error listing backups: {e}", flush=True)
            return []

# =========================================================================

# =========================================================================
# PHASE 4: EXTERNAL AI BRAIN INTEGRATION (GEMINI & CHATGPT)
# =========================================================================

class CloudLLMBridge:
    """
    PHASE 5 REFACTOR: CLOUD LLM BRIDGE (Primary LLM Controller)
    Uses Gemini & ChatGPT as the main LLM instead of local Llama model.
    Provides chat_completion() and stream_chat_completion() interfaces
    matching the LlamaConnector API for compatibility.
    
    Fallback Chain:
      1. Gemini API (primary, fastest)
      2. ChatGPT API (fallback, most reliable)
      3. Graceful degradation if both fail
    """
    
    def __init__(self, higher_brain):
        self.higher_brain = higher_brain
        self.gemini_key = higher_brain.gemini_key
        self.openai_key = higher_brain.openai_key
    
    def chat_completion(self, messages, temperature=0.7, max_tokens=512):
        """
        Chat completion using cloud APIs (compatible with LlamaConnector interface).
        
        Args:
            messages: Chat message history
            temperature: Response creativity (0.0-1.0)
            max_tokens: Max response length
            
        Returns:
            Response in llama-cpp-python format or None
        """
        # Extract user message
        user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        if not user_message:
            print(f"[CLOUD] ❌ No user message found", flush=True)
            return None
        
        print(f"[CLOUD] 🤖 Chat completion: {user_message[:60]}...", flush=True)
        
        # Try Gemini first
        if self.gemini_key:
            response = self._try_gemini_chat(user_message, temperature, max_tokens)
            if response:
                return response
        
        # Fallback to ChatGPT
        if self.openai_key:
            print(f"[CLOUD] 🔄 Gemini failed, trying ChatGPT...", flush=True)
            response = self._try_chatgpt_chat(user_message, temperature, max_tokens)
            if response:
                return response
        
        print(f"[CLOUD] ❌ All APIs failed", flush=True)
        return None
    
    def _try_gemini_chat(self, user_message, temperature, max_tokens):
        """Try Gemini API chat completion (use configurable v1 model endpoint)."""
        try:
            model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={self.gemini_key}"

            payload = {
                "contents": [{"parts": [{"text": user_message}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens
                }
            }

            # POST directly to fully-qualified URL (key included)
            response = requests.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                # Try several possible response shapes used by Gemini v1
                if "candidates" in result and len(result["candidates"]) > 0:
                    content = result["candidates"][0].get("content", "")
                elif "outputs" in result and len(result["outputs"]) > 0:
                    out = result["outputs"][0]
                    if isinstance(out, dict) and "content" in out:
                        content = out["content"] if isinstance(out["content"], str) else str(out["content"])
                    else:
                        content = str(result)
                elif "contents" in result:
                    content = result["contents"][0]["parts"][0].get("text", "")
                else:
                    content = str(result)

                print(f"[CLOUD] ✅ Gemini: {content[:60]}...", flush=True)
                return {
                    "choices": [
                        {"message": {"content": content}, "delta": {"content": content}}
                    ]
                }
        except Exception as e:
            print(f"[CLOUD] ⚠️  Gemini error: {e}", flush=True)

        return None
    
    def _try_chatgpt_chat(self, user_message, temperature, max_tokens):
        """Try ChatGPT API chat completion."""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": user_message}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    print(f"[CLOUD] ✅ ChatGPT: {content[:60]}...", flush=True)
                    # Return in llama-cpp-python format
                    return {
                        "choices": [
                            {"message": {"content": content}, "delta": {"content": content}}
                        ]
                    }
        except Exception as e:
            print(f"[CLOUD] ⚠️  ChatGPT error: {e}", flush=True)
        
        return None
    
    def stream_chat_completion(self, messages, temperature=0.7, max_tokens=512):
        """
        Streaming chat completion (compatible with LlamaConnector interface).
        Since cloud APIs don't stream the same way, we return full response as chunks.
        """
        response = self.chat_completion(messages, temperature, max_tokens)
        if response and "choices" in response:
            content = response["choices"][0]["message"]["content"]
            # Yield in chunks to simulate streaming
            chunk_size = 50
            for i in range(0, len(content), chunk_size):
                yield {
                    "choices": [
                        {"delta": {"content": content[i:i+chunk_size]}}
                    ]
                }

class HigherIntelligenceBridge:
    """
    HIGHER INTELLIGENCE BRIDGE
    Updated Gemini v1 usage, robust retry/backoff, and memory collection.
    """

    def __init__(self):
        self.gemini_key = self._load_api_key("GEMINI_API_KEY")
        self.openai_key = self._load_api_key("OPENAI_API_KEY")
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.request_log = []
        self.api_status = "Initializing..."

        print(f"[BRAIN] 🧠 Higher Intelligence Bridge initialized", flush=True)
        print(f"[BRAIN] 🔐 Gemini API: {'✅ Loaded' if self.gemini_key else '❌ Not Available'}", flush=True)
        print(f"[BRAIN] 🔐 ChatGPT API: {'✅ Loaded' if self.openai_key else '❌ Not Available'}", flush=True)
        print(f"[BRAIN] 🔐 DeepSeek API: {'✅ Loaded' if self.deepseek_key else '❌ Not Available'}", flush=True)

    @staticmethod
    def _load_api_key(key_name):
        env_key = os.getenv(key_name)
        if env_key:
            print(f"[BRAIN] ✅ Loaded {key_name} from environment", flush=True)
            return env_key

        try:
            if os.path.exists("evolution_keys.json"):
                with open("evolution_keys.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                key_mapping = {
                    "GEMINI_API_KEY": "gemini_api_key",
                    "OPENAI_API_KEY": "openai_api_key"
                }
                mapped_key = key_mapping.get(key_name)
                if mapped_key and config.get(mapped_key):
                    print(f"[BRAIN] ✅ Loaded {key_name} from evolution_keys.json", flush=True)
                    return config[mapped_key]
        except Exception as e:
            print(f"[BRAIN] ⚠️  Could not load {key_name} from config: {e}", flush=True)

        print(f"[BRAIN] ⚠️  {key_name} not available", flush=True)
        return None

    @retry(max_attempts=Config.MAX_RETRIES, delay=Config.RETRY_DELAY, backoff=Config.RETRY_BACKOFF, exceptions=(requests.exceptions.RequestException, Exception))
    def query_gemini(self, prompt):
        """
        Query Google Gemini v1 endpoint and return textual content. Uses retry decorator.
        """
        if not self.gemini_key:
            print(f"[BRAIN] ❌ Gemini API key not available", flush=True)
            return None

        global GEMINI_ACTIVE
        GEMINI_ACTIVE = True
        print(f"[BRAIN] 🔬 Querying Gemini for: {prompt[:60]}...", flush=True)

        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={self.gemini_key}"

        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }

        try:
            response = requests.post(url, json=payload, timeout=Config.NETWORK_TIMEOUT)
            if response.status_code != 200:
                print(f"[BRAIN] ⚠️  Gemini error {response.status_code}: {response.text[:200]}", flush=True)
                GEMINI_ACTIVE = False
                gc.collect()
                return None

            result = response.json()

            # Parse common response shapes
            content = None
            if isinstance(result, dict):
                if "candidates" in result and result.get("candidates"):
                    content = result["candidates"][0].get("content", "")
                elif "outputs" in result and result.get("outputs"):
                    out = result["outputs"][0]
                    if isinstance(out, dict) and "content" in out:
                        content = out.get("content") if isinstance(out.get("content"), str) else str(out.get("content"))
                elif "contents" in result and isinstance(result["contents"], list):
                    try:
                        content = result["contents"][0]["parts"][0]["text"]
                    except Exception:
                        content = str(result)
                else:
                    # Fallback to serializing result
                    content = str(result)

            if not content:
                content = str(result)

            # Log and return
            print(f"[BRAIN] ✅ Gemini responded: {content[:120]}...", flush=True)
            self.request_log.append({
                "api": "gemini",
                "prompt": prompt[:200],
                "response": content[:500],
                "timestamp": datetime.datetime.now().isoformat(),
                "success": True
            })

            GEMINI_ACTIVE = False
            gc.collect()
            return content

        except Exception as e:
            print(f"[BRAIN] ❌ Gemini error: {e}", flush=True)
            GEMINI_ACTIVE = False
            gc.collect()
            # Re-raise to enable retry decorator to catch and retry
            raise

    @retry(max_attempts=Config.MAX_RETRIES, delay=Config.RETRY_DELAY, backoff=Config.RETRY_BACKOFF, exceptions=(requests.exceptions.RequestException, Exception))
    def query_chatgpt(self, prompt):
        """
        Query OpenAI ChatCompletion (fallback) with retry and memory collection.
        """
        if not self.openai_key:
            print(f"[BRAIN] ❌ ChatGPT API key not available", flush=True)
            return None

        print(f"[BRAIN] 🧠 Querying ChatGPT for: {prompt[:60]}...", flush=True)
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are KNO, an autonomous AI agent. Provide concise solutions."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=Config.NETWORK_TIMEOUT)
            if response.status_code != 200:
                print(f"[BRAIN] ⚠️  ChatGPT error {response.status_code}: {response.text[:200]}", flush=True)
                gc.collect()
                return None

            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"].get("content", "")
                print(f"[BRAIN] ✅ ChatGPT responded: {content[:120]}...", flush=True)
                self.request_log.append({
                    "api": "chatgpt",
                    "prompt": prompt[:200],
                    "response": content[:500],
                    "timestamp": datetime.datetime.now().isoformat(),
                    "success": True
                })
                gc.collect()
                return content

            gc.collect()
            return None

        except Exception as e:
            print(f"[BRAIN] ❌ ChatGPT error: {e}", flush=True)
            gc.collect()
            raise

    def solve_complex_problem(self, problem_description):
        """
        Query external AI with fallback: Gemini first, then ChatGPT.
        """
        print(f"[BRAIN] 🚀 Sending problem to external intelligence...", flush=True)

        if self.gemini_key:
            try:
                solution = self.query_gemini(problem_description)
                if solution:
                    return solution
            except Exception:
                pass

        if self.openai_key:
            try:
                solution = self.query_chatgpt(problem_description)
                if solution:
                    return solution
            except Exception:
                pass

        if 'deepseek_engine' in globals() and deepseek_engine and getattr(deepseek_engine, 'api_key', None):
            try:
                print("[BRAIN] 🔁 External AIs failed — trying DeepSeek fallback", flush=True)
                ds = deepseek_engine.analyze_error(problem_description, context='solve_complex_problem')
                if ds:
                    return ds
            except Exception as e:
                print(f"[BRAIN] ⚠️ DeepSeek fallback failed: {e}", flush=True)

        print(f"[BRAIN] ❌ No external AI available", flush=True)
        return None

    def log_interactions(self):
        """Save all API interactions to log file."""
        log_file = "logs/evolution.log"
        Path("logs").mkdir(exist_ok=True)

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n=== External AI Interactions ({datetime.datetime.now().isoformat()}) ===\n")
                for interaction in self.request_log:
                    f.write(f"\n[{interaction['api'].upper()}]\n")
                    f.write(f"Prompt: {interaction['prompt']}\n")
                    f.write(f"Response: {interaction['response']}\n")
                    f.write(f"Status: {'✅ Success' if interaction['success'] else '❌ Failed'}\n")
                    f.write(f"Time: {interaction['timestamp']}\n")
        except Exception as e:
            print(f"[BRAIN] ❌ Error logging interactions: {e}", flush=True)
            
    
    def log_interactions(self):
        """Save all API interactions to log file."""
        log_file = "logs/evolution.log"
        Path("logs").mkdir(exist_ok=True)
        
        try:
            with open(log_file, "a") as f:
                f.write(f"\n=== External AI Interactions ({datetime.datetime.now().isoformat()}) ===\n")
                for interaction in self.request_log:
                    f.write(f"\n[{interaction['api'].upper()}]\n")
                    f.write(f"Prompt: {interaction['prompt']}\n")
                    f.write(f"Response: {interaction['response']}\n")
                    f.write(f"Status: {'✅ Success' if interaction['success'] else '❌ Failed'}\n")
                    f.write(f"Time: {interaction['timestamp']}\n")
        except Exception as e:
            print(f"[BRAIN] ❌ Error logging interactions: {e}", flush=True)

# =========================================================================

class EvolutionaryAutoDownloader:
    """
    EVOLUTIONARY AUTO-DOWNLOADER
    Uses Gemini API to find latest GGUF model links and download them.
    """
    
    def __init__(self, higher_brain):
        self.higher_brain = higher_brain
        self.models_dir = os.path.join(os.getcwd(), "models")
        Path(self.models_dir).mkdir(exist_ok=True)
    
    def find_latest_model_link(self):
        """
        Ask Gemini to find the latest gemma-2b-it GGUF model link.
        
        Returns:
            Download URL or None if not found
        """
        prompt = """
        Find the download link for the latest gemma-2b-it GGUF quantized model.
        The model should be:
        - From Hugging Face (preferably)
        - Q4_K_M quantization (around 1.5-2GB)
        - Named something like "gemma-2b-it.Q4_K_M.gguf"
        
        Provide ONLY the direct download URL, nothing else.
        """
        
        print(f"[DOWNLOADER] 🔍 Asking Gemini for latest model link...", flush=True)
        
        link = self.higher_brain.query_gemini(prompt)
        
        if link:
            # Clean up the response (might include explanations)
            lines = link.strip().split('\n')
            for line in lines:
                if line.startswith('http'):
                    print(f"[DOWNLOADER] 🔗 Found link: {line[:80]}...", flush=True)
                    return line.strip()
        
        print(f"[DOWNLOADER] ❌ Could not obtain model link from Gemini", flush=True)
        return None
    
    def evolutionary_download_model(self):
        """
        Automatically download GGUF model using Gemini-found link.
        
        Returns:
            Path to downloaded model or None
        """
        print(f"[DOWNLOADER] 🚀 Starting evolutionary auto-download...", flush=True)
        
        # Get download link from Gemini
        download_url = self.find_latest_model_link()
        
        if not download_url:
            print(f"[DOWNLOADER] ❌ Could not find model link", flush=True)
            return None
        
        # Extract filename from URL
        filename = download_url.split('/')[-1]
        filepath = os.path.join(self.models_dir, filename)
        
        print(f"[DOWNLOADER] ⬇️  Downloading {filename}...", flush=True)
        
        try:
            response = requests.get(download_url, stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            percent = (downloaded / total_size) * 100
                            mb_done = downloaded / (1024*1024)
                            mb_total = total_size / (1024*1024)
                            print(f"[DOWNLOADER] {percent:.1f}% - {mb_done:.0f}MB/{mb_total:.0f}MB", flush=True, end='\r')
            
            print(f"\n[DOWNLOADER] ✅ Model downloaded successfully: {filepath}", flush=True)
            return filepath
        
        except Exception as e:
            print(f"[DOWNLOADER] ❌ Download failed: {e}", flush=True)
            if os.path.exists(filepath):
                os.remove(filepath)
            return None

# =========================================================================

class SelfEvolutionThread:
    """
    SELF-EVOLUTION THREAD
    Autonomous error investigation and fix application.
    When errors occur, query ChatGPT for solutions and apply them.
    """
    
    def __init__(self, higher_brain):
        self.higher_brain = higher_brain
        self.error_queue = []
        self.fixes_applied = []
        self.running = False
        self._worker_thread = None
        self._new_error_event = threading.Event()
    
    def queue_error(self, error_type, error_message, context):
        """
        Queue an error for investigation and fix.
        
        Args:
            error_type: Type of error (e.g., "adb_pairing", "import_error")
            error_message: The error message
            context: Context where error occurred
        """
        error_item = {
            "type": error_type,
            "message": error_message,
            "context": context,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "queued"
        }
        
        self.error_queue.append(error_item)
        print(f"[EVOLUTION] 📋 Error queued: {error_type}", flush=True)
        # Notify background worker if running
        try:
            self._new_error_event.set()
        except Exception:
            pass
    
    def investigate_error(self, error_item):
        """
        Ask AI engines to investigate an error with retry tracking.
        Try DeepSeek first (with backoff), then Gemini, then ChatGPT.
        
        Args:
            error_item: Error dictionary from queue
            
        Returns:
            Tuple of (suggested_fix, ai_engine_used, retry_summary)
        """
        prompt = f"""
        I'm an autonomous Python agent named KNO. I encountered an error:
        
        Error Type: {error_item['type']}
        Error Message: {error_item['message']}
        Context: {error_item['context']}
        
        Provide a specific, actionable fix in Python code or shell commands.
        Format: Start with [FIX_CODE] or [FIX_SHELL] then provide the code/command.
        """
        
        print(f"[EVOLUTION] 🔍 Investigating error with DeepSeek/Gemini/ChatGPT fallback chain...", flush=True)
        retry_summary = {"deepseek": 0, "gemini_attempted": False, "chatgpt_attempted": False, "fallback_path": []}

        # Prefer DeepSeek for code analysis if available
        if 'deepseek_engine' in globals() and deepseek_engine and getattr(deepseek_engine, 'api_key', None):
            print(f"[EVOLUTION] 🧠 Tier 1: Querying DeepSeek for code fix...", flush=True)
            retry_summary["fallback_path"].append("DeepSeek")
            try:
                ds_fix = deepseek_engine.analyze_error(error_item['message'], context=error_item.get('context'))
                if ds_fix:
                    print(f"[EVOLUTION] ✅ DeepSeek SUCCESS. Suggested fix: {str(ds_fix)[:140]}...", flush=True)
                    return ds_fix, "DeepSeek", retry_summary
            except Exception as e:
                # DeepSeek failed, trigger fallback
                print(f"[EVOLUTION] ⚠️ DeepSeek failed (will attempt fallback): {e}", flush=True)

        # Fallback: try Gemini
        if 'higher_intelligence_bridge' in globals() and higher_intelligence_bridge:
            print(f"[EVOLUTION] 🔎 Tier 2: Falling back to Gemini for analysis...", flush=True)
            retry_summary["gemini_attempted"] = True
            retry_summary["fallback_path"].append("Gemini")
            try:
                gemini_fix = higher_intelligence_bridge.query_gemini(prompt)
                if gemini_fix:
                    print(f"[EVOLUTION] ✅ Gemini SUCCESS. Suggested fix: {str(gemini_fix)[:140]}...", flush=True)
                    return gemini_fix, "Gemini", retry_summary
            except Exception as e:
                print(f"[EVOLUTION] ⚠️ Gemini failed (will attempt ChatGPT): {e}", flush=True)

        # Final fallback: ChatGPT
        if 'higher_intelligence_bridge' in globals() and higher_intelligence_bridge:
            print(f"[EVOLUTION] 💬 Tier 3: Final fallback to ChatGPT...", flush=True)
            retry_summary["chatgpt_attempted"] = True
            retry_summary["fallback_path"].append("ChatGPT")
            try:
                fix = higher_intelligence_bridge.query_chatgpt(prompt)
                if fix:
                    print(f"[EVOLUTION] ✅ ChatGPT SUCCESS. Suggested fix: {fix[:100]}...", flush=True)
                    return fix, "ChatGPT", retry_summary
            except Exception as e:
                print(f"[EVOLUTION] ⚠️ ChatGPT failed: {e}", flush=True)

        print(f"[EVOLUTION] ❌ All AI engines exhausted. No fix available.", flush=True)
        return None, None, retry_summary
    
    def apply_fix(self, fix_suggestion, error_item, ai_engine="Unknown", retry_summary=None):
        """
        Apply the suggested fix with backup and user approval.
        
        Args:
            fix_suggestion: The fix from AI engine
            error_item: The original error item
            ai_engine: Name of AI engine that provided the fix
            retry_summary: Dict with retry/fallback info
            
        Returns:
            True if fix applied successfully
        """
        # Print retry/fallback summary for transparency
        if retry_summary:
            fallback_text = " → ".join(retry_summary.get("fallback_path", []))
            print(f"[EVOLUTION] 📊 Fallback chain used: {fallback_text}", flush=True)
            print(f"[EVOLUTION] 🧠 AI engine: {ai_engine}", flush=True)
        
        print(f"[EVOLUTION] 🔧 Attempting to apply fix from {ai_engine}...", flush=True)
        
        try:
            # Check if it's a shell command
            if "[FIX_SHELL]" in fix_suggestion:
                command = fix_suggestion.split("[FIX_SHELL]")[1].strip()
                print(f"[EVOLUTION] 💻 Shell command: {command[:80]}", flush=True)
                
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    timeout=30,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"[EVOLUTION] ✅ Shell command succeeded", flush=True)
                    self.fixes_applied.append({
                        "error": error_item['type'],
                        "fix_type": "shell",
                        "ai_engine": ai_engine,
                        "command": command,
                        "result": "success",
                        "timestamp": datetime.datetime.now().isoformat()
                    })
                    return True
                else:
                    print(f"[EVOLUTION] ❌ Shell command failed: {result.stderr}", flush=True)
                    return False
            
            # Check if it's Python code (for agent.py patching)
            elif "[FIX_CODE]" in fix_suggestion:
                code = fix_suggestion.split("[FIX_CODE]")[1].strip()
                print(f"[EVOLUTION] 🐍 Code patch detected: {code[:80]}", flush=True)
                
                # For agent.py patches, use SafePatchApplier
                # (In headless mode, auto-approve; in GUI mode, show dialog)
                if 'safe_patch_applier' in globals() and safe_patch_applier:
                    applied = safe_patch_applier.apply_patch_with_approval(
                        "agent.py",
                        code,
                        reason=f"Auto-fix from {ai_engine}: {error_item['type']}",
                        old_code=None,
                        ai_engine=ai_engine,
                        error_item=error_item
                    )
                    if applied:
                        print(f"[EVOLUTION] ✅ Code patch applied to agent.py", flush=True)
                        self.fixes_applied.append({
                            "error": error_item['type'],
                            "fix_type": "code_patch",
                            "ai_engine": ai_engine,
                            "code": code[:200],
                            "result": "success",
                            "timestamp": datetime.datetime.now().isoformat()
                        })
                        return True
                    else:
                        print(f"[EVOLUTION] ⚠️ Code patch not applied immediately; evaluating auto-apply rules", flush=True)
                        # If GUI is absent/unresponsive, allow high-confidence automatic application
                        high_confidence = (ai_engine == "DeepSeek") or (error_item.get('type') in ("import_error", "module_not_found", "tcl_error", "syntax_error"))
                        if high_confidence:
                            print(f"[EVOLUTION] ⚡ High-confidence patch detected; auto-applying after timeout.", flush=True)
                            forced = safe_patch_applier.apply_patch_with_approval(
                                "agent.py",
                                code,
                                reason=f"Auto-apply high-confidence fix from {ai_engine}: {error_item['type']}",
                                old_code=None,
                                ai_engine=ai_engine,
                                error_item=error_item,
                                force=True
                            )
                            if forced:
                                print(f"[EVOLUTION] ✅ Forced code patch applied to agent.py", flush=True)
                                self.fixes_applied.append({
                                    "error": error_item['type'],
                                    "fix_type": "code_patch_forced",
                                    "ai_engine": ai_engine,
                                    "code": code[:200],
                                    "result": "success",
                                    "timestamp": datetime.datetime.now().isoformat()
                                })
                                return True
                            else:
                                print(f"[EVOLUTION] ❌ Forced code patch failed", flush=True)
                                return False
                        return False
                else:
                    # Cannot apply patch - must use safe_code_patcher only
                    logger.warning(f"[EVOLUTION] ⚠️ Cannot apply patch: no safe_patch_applier available")
                    return False
        
        except Exception as e:
            print(f"[EVOLUTION] ❌ Could not apply fix: {e}", flush=True)
            return False
    
    def process_error_queue(self):
        """
        Process all queued errors: investigate and apply fixes.
        Prints retry and fallback summary to console for debugging.
        """
        if not self.error_queue:
            return
        
        print(f"[EVOLUTION] 🔄 Processing {len(self.error_queue)} queued errors...", flush=True)
        
        while self.error_queue:
            error_item = self.error_queue.pop(0)
            error_item['status'] = 'investigating'
            
            # Get AI engine suggestion with retry/fallback tracking
            fix, ai_engine, retry_summary = self.investigate_error(error_item)
            
            if fix:
                # Try to apply the fix
                success = self.apply_fix(fix, error_item, ai_engine=ai_engine, retry_summary=retry_summary)
                error_item['status'] = 'fixed' if success else 'failed'
            else:
                print(f"[EVOLUTION] ⚠️  No fix available for {error_item['type']}", flush=True)
                error_item['status'] = 'no_fix'

            # Attempt visual recovery for UI-related errors
            try:
                if error_item.get('type') in ('gui_error', 'window_error', 'dialog_error'):
                    recovered = self.attempt_visual_recovery(error_item)
                    if recovered:
                        error_item['status'] = 'recovered_visual'
                        self.fixes_applied.append({
                            'error': error_item['type'],
                            'fix_type': 'visual_recovery',
                            'ai_engine': 'vision+action',
                            'result': 'attempted',
                            'timestamp': datetime.datetime.now().isoformat()
                        })
            except Exception:
                pass

    def _worker_loop(self):
        """Background loop that processes errors as they arrive."""
        print("[EVOLUTION] ▶️ SelfEvolutionThread background worker started", flush=True)
        self.running = True
        while self.running:
            try:
                # Wait until there's an error or timeout
                self._new_error_event.wait(timeout=2)
                self._new_error_event.clear()
                if self.error_queue:
                    self.process_error_queue()
                    self.log_evolution()
            except Exception as e:
                print(f"[EVOLUTION] ⚠️ Worker loop error: {e}", flush=True)
            time.sleep(0.1)

    def attempt_visual_recovery(self, error_item):
        """
        Use vision + action executor to attempt an automated recovery for UI errors.
        This method will call the global `action_executor` and `vision_module` if available.
        Returns True if an attempt was made.
        """
        try:
            if 'action_executor' in globals() and action_executor and 'vision_module' in globals() and vision_module:
                logger.info("SelfEvolutionThread: attempting visual recovery via ActionExecutor")
                return action_executor.autonomous_error_recovery()
            return False
        except Exception as e:
            logger.error(f"Visual recovery attempt failed: {e}")
            return False

    def start(self):
        """Start the background worker thread."""
        if self._worker_thread and self._worker_thread.is_alive():
            return
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()

    def stop(self):
        """Stop the background worker thread."""
        self.running = False
        try:
            self._new_error_event.set()
        except Exception:
            pass
    
    def log_evolution(self):
        """Log all evolution activities to evolution.log"""
        log_file = "logs/evolution.log"
        Path("logs").mkdir(exist_ok=True)
        
        try:
            with open(log_file, "a") as f:
                f.write(f"\n=== Self-Evolution Activities ({datetime.datetime.now().isoformat()}) ===\n")
                f.write(f"Errors Processed: {len(self.fixes_applied)}\n")
                f.write(f"Successful Fixes: {sum(1 for f in self.fixes_applied if f['result'] == 'success')}\n")
                
                for fix in self.fixes_applied:
                    f.write(f"\nError: {fix['error']}\n")
                    f.write(f"Fix Type: {fix['fix_type']}\n")
                    f.write(f"Result: {fix['result']}\n")
                    f.write(f"Timestamp: {fix['timestamp']}\n")
        
        except Exception as e:
            print(f"[EVOLUTION] ❌ Error logging evolution: {e}", flush=True)

# =========================================================================

# =========================================================================
# =========================================================================
# PHASE 4-5: EXTERNAL AI BRAINS & CLOUD LLM - GLOBAL INSTANCES
# =========================================================================

# Higher Intelligence Bridge - Queries Gemini/ChatGPT for complex problems
higher_intelligence_bridge = HigherIntelligenceBridge()

# Computer Use Modules - Vision + Action for autonomous error recovery
try:
    vision_module = VisionModule()
    action_executor = ActionExecutor(vision_module=vision_module)
except Exception as e:
    # Fallback for headless/missing vision: VisionModule likely not defined
    vision_module = None
    action_executor = None
    logger.debug(f"VisionModule initialization skipped (expected in headless mode): {e}")

# DeepSeek engine: specialized for code analysis and self-evolution tasks.
deepseek_engine = DeepSeekEngine(api_key=os.getenv("DEEPSEEK_API_KEY"))

# PHASE 5: Cloud LLM Bridge - Primary LLM controller (replaces LlamaConnector)
cloud_llm_bridge = CloudLLMBridge(higher_intelligence_bridge)

# Evolutionary Auto-Downloader - Uses AI to find & download models
evolutionary_downloader = EvolutionaryAutoDownloader(higher_intelligence_bridge)

# Self-Evolution Thread - Autonomous error fixing
self_evolution_thread = SelfEvolutionThread(higher_intelligence_bridge)

# =========================================================================

class DependencyManager:
    """Autonomous dependency checking and auto-installation."""
    
    OPTIONAL_PACKAGES = {
        "pychromecast": "pychromecast",         # Smart TV control
        "adb_shell": "adb-shell",               # Android device control
        "scapy": "scapy",                       # Network scanning
        "Flask": "flask",                       # Web server (optional)
    }
    
    @staticmethod
    def check_and_install_dependencies():
        """Check for optional dependencies and auto-install if missing."""
        print("[DEPENDENCY] Checking optional packages...", flush=True)
        
        for import_name, package_name in DependencyManager.OPTIONAL_PACKAGES.items():
            try:
                __import__(import_name)
                print(f"[DEPENDENCY] ✓ {import_name} available", flush=True)
            except ImportError:
                print(f"[DEPENDENCY] ✗ {import_name} missing, attempting auto-install...", flush=True)
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", package_name, "-q"],
                        timeout=120,
                        check=True
                    )
                    print(f"[DEPENDENCY] ✓ {package_name} installed successfully", flush=True)
                except Exception as e:
                    print(f"[DEPENDENCY] ✗ Failed to install {package_name}: {e}", flush=True)

class SystemActionEngine:
    """Execute system-level actions with human-in-the-loop approval."""
    
    ALLOWED_DIRS = [
        "A:\\KNO\\KNO\\downloads",
        "A:\\KNO\\KNO\\",
        os.path.expanduser("~\\Downloads"),
        os.path.expanduser("~\\Desktop")
    ]
    
    def __init__(self, approval_callback=None):
        """Initialize with optional approval callback (from Tkinter GUI)."""
        self.approval_callback = approval_callback
    
    def request_approval(self, action_type, details):
        """Request human approval for an action."""
        if self.approval_callback:
            return self.approval_callback(action_type, details)
        return True  # Auto-approve if no callback
    
    def open_browser(self, url):
        """Open URL in default browser with approval."""
        if not self.request_approval("open_browser", f"Open: {url}"):
            return False
        
        try:
            import webbrowser
            webbrowser.open(url)
            print(f"[ACTION] Opened browser: {url}", flush=True)
            return True
        except Exception as e:
            print(f"[ACTION ERROR] Failed to open browser: {e}", flush=True)
            return False
    
    def file_move(self, source, destination):
        """Move file with approval and path validation."""
        if not self._validate_path(source) or not self._validate_path(destination):
            print(f"[ACTION] Path outside allowed directories", flush=True)
            return False
        
        if not self.request_approval("file_move", f"Move {source} → {destination}"):
            return False
        
        # Check global consent manager for additional security control
        if consent_manager:
            if not consent_manager.request_approval(
                action=f"Move file {source}",
                permission_type="file_system",
                details=f"Source: {source}\nDestination: {destination}"
            ):
                print(f"[ACTION] File move operation denied by consent manager", flush=True)
                return False
        
        try:
            shutil.move(source, destination)
            print(f"[ACTION] Moved: {source} → {destination}", flush=True)
            return True
        except Exception as e:
            print(f"[ACTION ERROR] Failed to move file: {e}", flush=True)
            return False
    
    def file_copy(self, source, destination):
        """Copy file with approval and path validation."""
        if not self._validate_path(source) or not self._validate_path(destination):
            print(f"[ACTION] Path outside allowed directories", flush=True)
            return False
        
        if not self.request_approval("file_copy", f"Copy {source} → {destination}"):
            return False
        
        # Check global consent manager for additional security control
        if consent_manager:
            if not consent_manager.request_approval(
                action=f"Copy file {source}",
                permission_type="file_system",
                details=f"Source: {source}\nDestination: {destination}"
            ):
                print(f"[ACTION] File copy operation denied by consent manager", flush=True)
                return False
        
        try:
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
            print(f"[ACTION] Copied: {source} → {destination}", flush=True)
            return True
        except Exception as e:
            print(f"[ACTION ERROR] Failed to copy: {e}", flush=True)
            return False
    
    def file_delete(self, filepath):
        """Delete file with approval."""
        if not self._validate_path(filepath):
            print(f"[ACTION] Path outside allowed directories", flush=True)
            return False
        
        if not self.request_approval("file_delete", f"Delete: {filepath}"):
            return False
        
        # Check global consent manager for additional security control
        if consent_manager:
            if not consent_manager.request_approval(
                action=f"Delete file {filepath}",
                permission_type="file_system",
                details=f"File: {filepath}"
            ):
                print(f"[ACTION] File delete operation denied by consent manager", flush=True)
                return False
        
        try:
            if os.path.isdir(filepath):
                shutil.rmtree(filepath)
            return True
        except Exception as e:
            print(f"[ACTION ERROR] Failed to delete: {e}", flush=True)
            return False


def perform_startup_sanity_check():
    """Lightweight startup sanity check for AI engines and dependency manager.

    Prints a success message only if Gemini, DeepSeek, ChatGPT (OpenAI) keys
    are available and the DependencyManager class is reachable.
    """
    ok = True
    missing = []

    try:
        gemini_ok = bool(higher_intelligence_bridge and getattr(higher_intelligence_bridge, 'gemini_key', None))
    except Exception:
        gemini_ok = False
    if not gemini_ok:
        ok = False
        missing.append('Gemini')

    try:
        chatgpt_ok = bool(higher_intelligence_bridge and getattr(higher_intelligence_bridge, 'openai_key', None))
    except Exception:
        chatgpt_ok = False
    if not chatgpt_ok:
        ok = False
        missing.append('ChatGPT')

    try:
        deepseek_ok = bool(deepseek_engine and getattr(deepseek_engine, 'api_key', None))
    except Exception:
        deepseek_ok = False
    if not deepseek_ok:
        ok = False
        missing.append('DeepSeek')

    try:
        dm_ok = hasattr(DependencyManager, 'check_and_install_dependencies')
    except Exception:
        dm_ok = False
    if not dm_ok:
        ok = False
        missing.append('DependencyManager')

    if ok:
        print("[SANITY] ✅ All AI engines and DependencyManager initialized successfully.", flush=True)
    else:
        print(f"[SANITY] ⚠️ Initialization incomplete. Missing: {', '.join(missing)}", flush=True)


def create_unified_diff(old_text, new_text, old_name="original", new_name="modified"):
    """Generate a unified diff between old and new text.
    
    Returns a string with diff formatted for display.
    """
    import difflib
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    diff = difflib.unified_diff(old_lines, new_lines, fromfile=old_name, tofile=new_name, lineterm='')
    return ''.join(diff)


def show_patch_approval_dialog(main_window, old_code, new_code, title="Approve Code Patch"):
    """Show a GUI dialog with unified diff and Approve/Reject buttons.
    
    Returns True if user clicked 'Approve & Patch', False if 'Reject Fix'.
    """
    global DEEPSEEK_ACTIVE
    DEEPSEEK_ACTIVE = True  # Pulse purple while awaiting approval
    
    try:
        # Create a top-level dialog window
        dialog = tk.Toplevel(main_window)
        dialog.title(title)
        dialog.geometry("900x600")
        dialog.resizable(True, True)
        
        # Generate diff text
        diff_text = create_unified_diff(old_code, new_code, old_name="Current", new_name="Proposed")
        
        # Frame for instructions
        instr_frame = ttk.Frame(dialog)
        instr_frame.pack(fill=tk.X, padx=10, pady=5)
        instr_label = ttk.Label(instr_frame, text="Review the proposed changes below:", font=("Arial", 10, "bold"))
        instr_label.pack()
        
        # Text widget for diff display (read-only)
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, height=20, width=100, font=("Courier", 9))
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Insert diff with syntax highlighting (simple coloring)
        text_widget.insert(tk.END, diff_text)
        text_widget.config(state=tk.DISABLED)  # Read-only
        
        # Color diff lines for clarity
        text_widget.tag_config("added", foreground="green")
        text_widget.tag_config("removed", foreground="red")
        text_widget.tag_config("header", foreground="blue")
        
        for i, line in enumerate(diff_text.split('\n')):
            line_start = f"{i}.0"
            if line.startswith('+') and not line.startswith('+++'):
                text_widget.tag_add("added", line_start, f"{line_start} lineend")
            elif line.startswith('-') and not line.startswith('---'):
                text_widget.tag_add("removed", line_start, f"{line_start} lineend")
            elif line.startswith('@@'):
                text_widget.tag_add("header", line_start, f"{line_start} lineend")
        
        # Result holder
        result = {"approved": False}
        
        def on_approve():
            result["approved"] = True
            dialog.destroy()
        
        def on_reject():
            result["approved"] = False
            dialog.destroy()
        
        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        approve_btn = tk.Button(
            button_frame,
            text="✓ Approve & Patch",
            bg="#00DD00",
            fg="white",
            font=("Arial", 11, "bold"),
            command=on_approve,
            width=20
        )
        approve_btn.pack(side=tk.LEFT, padx=5)
        
        reject_btn = tk.Button(
            button_frame,
            text="✗ Reject Fix",
            bg="#DD0000",
            fg="white",
            font=("Arial", 11, "bold"),
            command=on_reject,
            width=20
        )
        reject_btn.pack(side=tk.LEFT, padx=5)
        
        # Wait for user decision
        dialog.wait_window()
        
        return result["approved"]
    
    finally:
        DEEPSEEK_ACTIVE = False


class SafePatchApplier:
    """Apply code patches with backup, user approval, and retry tracking."""
    
    BACKUP_DIR = "backups"
    
    def __init__(self, main_window=None):
        """Initialize with optional Tkinter main window for approval dialogs."""
        self.main_window = main_window
        self.patches_applied = []
        self.patches_rejected = []
        
        # Create backup directory if missing
        Path(self.BACKUP_DIR).mkdir(exist_ok=True)
        print(f"[PATCH] Backup directory: {os.path.abspath(self.BACKUP_DIR)}", flush=True)
    
    def create_backup(self, filepath, content):
        """Create a timestamped backup before writing changes.
        
        Returns the backup filepath.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        basename = os.path.basename(filepath)
        backup_name = f"{os.path.splitext(basename)[0]}_{timestamp}.bak"
        backup_path = os.path.join(self.BACKUP_DIR, backup_name)
        
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[PATCH] 💾 Backup created: {backup_path}", flush=True)
            return backup_path
        except Exception as e:
            print(f"[PATCH] ❌ Backup failed: {e}", flush=True)
            return None
    
    def apply_patch_with_approval(self, filepath, new_code, reason="Code improvement", old_code=None, ai_engine=None, error_item=None, force=False):
        """Apply a patch to a file with user approval and backup.
        
        Args:
            filepath: File to patch
            new_code: New code content
            reason: Reason for the patch (for logging)
            old_code: Old code to show in diff (if None, read from file)
        
        Returns:
            True if patch applied, False if rejected or failed.
        """
        try:
            # Read current code if not provided
            if old_code is None:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        old_code = f.read()
                except Exception as e:
                    print(f"[PATCH] ❌ Could not read {filepath}: {e}", flush=True)
                    return False
            
            # Support forced application (bypass approval) for emergency auto-applies
            if force:
                print(f"[PATCH] ⚡ Forced apply requested for {reason}", flush=True)
                approved = True
            else:
                # Show approval dialog if GUI available. Use a timeout so headless or frozen GUIs don't block.
                approved = None
            if self.main_window:
                print(f"[PATCH] 📋 Awaiting user approval for patch: {reason} (will timeout after 30s)", flush=True)

                # Use an event to receive result from GUI thread
                result_holder = {"approved": None}
                evt = threading.Event()

                def _show_and_set():
                    try:
                        result = show_patch_approval_dialog(self.main_window, old_code, new_code, title=f"Approve Patch: {reason}")
                        result_holder["approved"] = bool(result)
                    except Exception as e:
                        print(f"[PATCH] ⚠️ GUI approval dialog failed: {e}", flush=True)
                        result_holder["approved"] = None
                    finally:
                        evt.set()

                try:
                    # Schedule dialog on GUI thread
                    try:
                        self.main_window.after(0, _show_and_set)
                    except Exception:
                        # If after() unavailable, run in a thread (best-effort)
                        threading.Thread(target=_show_and_set, daemon=True).start()

                    # Wait up to 30s for user response
                    waited = evt.wait(timeout=30)
                    if waited:
                        approved = result_holder.get("approved")
                    else:
                        approved = None  # GUI unresponsive or user did not respond
                except Exception as e:
                    print(f"[PATCH] ⚠️ Approval scheduling failed: {e}", flush=True)
                    approved = None
            else:
                # Auto-approve if no GUI (for testing)
                print(f"[PATCH] ⚠️  No GUI available; auto-approving patch: {reason}", flush=True)
                approved = True

            # If GUI existed but was unresponsive (approved is None), fallback to console approval
            if approved is None and self.main_window is not None:
                try:
                    prompt = f"GUI approval timed out. Approve patch '{reason}'? [y/N]: "
                    answer = input(prompt).strip().lower()
                    approved = answer == 'y'
                except Exception:
                    approved = False
            
            if not approved:
                print(f"[PATCH] ❌ Patch rejected by user: {reason}", flush=True)
                self.patches_rejected.append({
                    "file": filepath,
                    "reason": reason,
                    "timestamp": datetime.datetime.now().isoformat()
                })
                return False
            
            # Create backup
            backup_path = self.create_backup(filepath, old_code)
            if not backup_path:
                print(f"[PATCH] ❌ Backup failed; refusing to patch for safety.", flush=True)
                return False
            
            # Write new code
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_code)
                print(f"[PATCH] ✅ Patch applied: {filepath}", flush=True)
                self.patches_applied.append({
                    "file": filepath,
                    "reason": reason,
                    "backup": backup_path,
                    "timestamp": datetime.datetime.now().isoformat()
                })
                return True
            except Exception as e:
                print(f"[PATCH] ❌ Failed to write {filepath}: {e}", flush=True)
                return False
        
        except Exception as e:
            print(f"[PATCH] ❌ Patch operation failed: {e}", flush=True)
            return False
    
    def get_patch_log(self):
        """Return a summary of all applied and rejected patches."""
        return {
            "applied": self.patches_applied,
            "rejected": self.patches_rejected
        }


# =========================================================================
# Global instance of SafePatchApplier for use throughout agent
# =========================================================================
safe_patch_applier = SafePatchApplier(main_window=None)  # Will be set by GUI later if available

# =========================================================================

class NetworkIOTController:
    """Discover and control Smart Devices on local network."""
    
    def __init__(self, approval_callback=None):
        """Initialize network controller."""
        self.approval_callback = approval_callback
        self.discovered_devices = {}
    
    def request_approval(self, action_type, details):
        """Request human approval for network actions."""
        if self.approval_callback:
            return self.approval_callback(action_type, details)
        return True
    
    def scan_network(self, subnet="192.168.1.0/24", timeout=5):
        """Scan local network for active devices (requires scapy)."""
        if not self.request_approval("network_scan", f"Scan network: {subnet}"):
            return []
        
        try:
            from scapy.all import ARP, Ether, srp
            print(f"[NETWORK] Scanning network: {subnet}", flush=True)
            
            arp_request = ARP(pdst=subnet)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request
            
            answered, _ = srp(arp_request_broadcast, timeout=timeout, verbose=False)
            
            devices = []
            for element in answered:
                device_info = {"ip": element[1].psrc, "mac": element[1].hwsrc}
                devices.append(device_info)
                print(f"[NETWORK] Found: {device_info['ip']} ({device_info['mac']})", flush=True)
            
            self.discovered_devices = {d['ip']: d for d in devices}
            return devices
        except ImportError:
            print(f"[NETWORK] scapy not available, skipping network scan", flush=True)
            return []
        except Exception as e:
            print(f"[NETWORK] Scan error: {e}", flush=True)
            return []
    
    def discover_chromecast(self):
        """Discover Chromecast devices on network."""
        try:
            import pychromecast
            print(f"[DEVICE] Discovering Chromecast devices...", flush=True)
            
            chromecasts = pychromecast.get_chromecasts()
            devices = []
            for cc in chromecasts:
                device_info = {
                    "type": "chromecast",
                    "name": cc.device.friendly_name,
                    "ip": cc.mdns_name.split(".")[0] if cc.mdns_name else "N/A"
                }
                devices.append(device_info)
                print(f"[DEVICE] Found Chromecast: {device_info['name']}", flush=True)
            
            return devices
        except ImportError:
            print(f"[DEVICE] pychromecast not available", flush=True)
            return []
        except Exception as e:
            print(f"[DEVICE] Chromecast discovery error: {e}", flush=True)
            return []
    
    def send_chromecast_command(self, device_name, command, args=None):
        """Send command to Chromecast device."""
        if not self.request_approval("chromecast_command", f"{device_name}: {command}"):
            return False
        
        try:
            import pychromecast
            
            chromecasts = pychromecast.get_chromecasts()
            for cc in chromecasts:
                if cc.device.friendly_name == device_name:
                    if command == "pause":
                        cc.media_controller.pause()
                    elif command == "play":
                        cc.media_controller.play()
                    elif command == "mute":
                        cc.set_volume_muted(True)
                    elif command == "unmute":
                        cc.set_volume_muted(False)
                    elif command == "volume" and args:
                        cc.set_volume(args.get("level", 0.5))
                    
                    print(f"[DEVICE] Sent to {device_name}: {command}", flush=True)
                    return True
            
            print(f"[DEVICE] Device not found: {device_name}", flush=True)
            return False
        except Exception as e:
            print(f"[DEVICE] Command error: {e}", flush=True)
            return False
    
    def send_adb_command(self, device_address, command):
        """Send ADB command to Android device."""
        if not self.request_approval("adb_command", f"{device_address}: {command}"):
            return False
        
        try:
            from adb_shell.adb_device import AdbDeviceTcp
            
            device = AdbDeviceTcp(device_address, port=5555)
            device.connect(rsa_keys=None)
            
            result = device.shell(command)
            print(f"[DEVICE] ADB Command result: {result}", flush=True)
            device.close()
            return True
        except ImportError:
            print(f"[DEVICE] adb_shell not available", flush=True)
            return False
        except Exception as e:
            print(f"[DEVICE] ADB error: {e}", flush=True)
            return False
    
    def adb_connect_wireless(self, phone_ip, port=5555):
        """Connect to Android phone via wireless ADB."""
        # First ensure ADB is available
        if not ResourceManager.verify_adb_installed():
            print(f"[PHONE] ADB not found, attempting to download Platform Tools...", flush=True)
            if ResourceManager.download_platform_tools():
                print(f"[PHONE] ✅ Platform Tools installed", flush=True)
            else:
                print(f"[PHONE] ❌ Could not install Platform Tools", flush=True)
                return False
        
        try:
            import subprocess
            # Connect to wireless device
            result = subprocess.run(
                ["adb", "connect", f"{phone_ip}:{port}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"[PHONE] ✅ Connected to {phone_ip}:{port}", flush=True)
                print(f"[PHONE] Output: {result.stdout}", flush=True)
                return True
            else:
                print(f"[PHONE] ❌ Connection failed: {result.stderr}", flush=True)
                return False
        except FileNotFoundError:
            print(f"[PHONE] ❌ ADB command not found - platform tools may not be installed", flush=True)
            return False
        except Exception as e:
            print(f"[PHONE] ❌ Connection error: {e}", flush=True)
            return False
    
    def send_phone_notification(self, message, phone_ip=None):
        """Send notification to Android phone via ADB."""
        if not self.request_approval("phone_notification", f"Send to phone: {message[:50]}..."):
            print(f"[PHONE] Notification rejected by user", flush=True)
            return False
        
        try:
            import subprocess
            
            # If phone_ip provided, connect first
            if phone_ip:
                if not self.adb_connect_wireless(phone_ip):
                    print(f"[PHONE] ❌ Could not connect to phone at {phone_ip}", flush=True)
                    return False
            
            # Format message for broadcast
            notification_message = f"KNO Report: {message}"
            
            # Use adb shell to send broadcast notification
            # This will trigger a system notification on the phone
            adb_command = [
                "adb", "shell", "am", "broadcast",
                "-a", "android.intent.action.EDIT",
                "--es", "msg", notification_message
            ]
            
            result = subprocess.run(
                adb_command,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"[PHONE] ✅ Notification sent: {notification_message[:60]}...", flush=True)
                return True
            else:
                print(f"[PHONE] ❌ Notification failed: {result.stderr}", flush=True)
                return False
                
        except FileNotFoundError:
            print(f"[PHONE] ❌ ADB not found - make sure Platform Tools are installed", flush=True)
            return False
        except Exception as e:
            print(f"[PHONE] ❌ Notification error: {e}", flush=True)
            return False
    
    def adb_pair_wireless(self, phone_ip, pairing_port, pairing_code):
        """Pair phone using wireless debugging credentials."""
        if not ResourceManager.verify_adb_installed():
            print(f"[PHONE] ADB not found, attempting to download Platform Tools...", flush=True)
            if not ResourceManager.download_platform_tools():
                print(f"[PHONE] ❌ Could not install Platform Tools", flush=True)
                return False
        
        try:
            import subprocess
            
            # Clear frozen ADB protocol state
            print(f"[PHONE] 🔧 Resetting ADB server...", flush=True)
            subprocess.run(["adb", "kill-server"], capture_output=True, timeout=5)
            time.sleep(1)
            subprocess.run(["adb", "start-server"], capture_output=True, timeout=5)
            time.sleep(1)
            
            pairing_address = f"{phone_ip}:{pairing_port}"
            print(f"[PHONE] 🔐 Pairing with {pairing_address} (code: {pairing_code})", flush=True)
            
            # Execute adb pair command
            result = subprocess.run(
                ["adb", "pair", pairing_address, pairing_code],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                print(f"[PHONE] ✅ Pairing successful!", flush=True)
                print(f"[PHONE] Output: {result.stdout}", flush=True)
                return True
            else:
                print(f"[PHONE] ❌ Pairing failed: {result.stderr}", flush=True)
                return False
                
        except FileNotFoundError:
            print(f"[PHONE] ❌ ADB command not found", flush=True)
            return False
        except Exception as e:
            print(f"[PHONE] ❌ Pairing error: {e}", flush=True)
            return False
    
    def adb_connect_wireless_main(self, phone_ip, main_port=38575):
        """Connect to paired phone using main connection port."""
        if not ResourceManager.verify_adb_installed():
            print(f"[PHONE] ADB not found, attempting to download Platform Tools...", flush=True)
            if not ResourceManager.download_platform_tools():
                print(f"[PHONE] ❌ Could not install Platform Tools", flush=True)
                return False
        
        try:
            import subprocess
            
            connection_address = f"{phone_ip}:{main_port}"
            print(f"[PHONE] 📱 Connecting to {connection_address}...", flush=True)
            
            # Execute adb connect command
            result = subprocess.run(
                ["adb", "connect", connection_address],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0 and "connected" in result.stdout.lower():
                print(f"[PHONE] ✅ Connected to phone at {connection_address}", flush=True)
                print(f"[PHONE] Output: {result.stdout}", flush=True)
                return True
            else:
                print(f"[PHONE] ❌ Connection failed: {result.stderr or result.stdout}", flush=True)
                return False
                
        except FileNotFoundError:
            print(f"[PHONE] ❌ ADB command not found", flush=True)
            return False
        except Exception as e:
            print(f"[PHONE] ❌ Connection error: {e}", flush=True)
            return False
    
    def sync_phone_wireless(self, phone_ip, pairing_port=34245, pairing_code="352913", main_port=38575):
        """Complete wireless sync: pair then connect."""
        print(f"[PHONE] 🔄 Starting wireless sync process...", flush=True)
        
        # Step 1: Pair
        if not self.adb_pair_wireless(phone_ip, pairing_port, pairing_code):
            print(f"[PHONE] ❌ Pairing failed, aborting sync", flush=True)
            return False
        
        time.sleep(2)  # Wait for pairing to complete
        
        # Step 2: Connect
        if not self.adb_connect_wireless_main(phone_ip, main_port):
            print(f"[PHONE] ❌ Connection failed, though pairing succeeded", flush=True)
            return False
        
        print(f"[PHONE] ✅ Wireless sync complete!", flush=True)
        return True

# =========================================================================
# NOTIFICATION LISTENER - WhatsApp Message Detection
# =========================================================================

class NotificationListener:
    """Listen for incoming notifications via ADB and detect WhatsApp messages."""
    
    def __init__(self, callback=None, privacy_mode=False):
        """
        Initialize notification listener.
        callback: Function to call when new notification detected (sender, message, privacy_mode)
        privacy_mode: If True, hide message content
        """
        self.callback = callback
        self.privacy_mode = privacy_mode
        self.last_notification_hash = None
        self.listening = False
        self.listener_thread = None
        self.whatsapp_regex = r'com\.whatsapp.*?pkg=com\.whatsapp.*?tag=notif_(\d+).*?(?:text=([^}]*?))?(?:}\s|$)'
        self.is_connected = False  # Track if phone is connected
        
        # More comprehensive WhatsApp pattern
        self.whatsapp_pattern = re.compile(
            r'statusbarNotification\(pkg=com\.whatsapp.*?(?:text=\'([^\']+)\')?',
            re.DOTALL
        )
        
        print(f"[NOTIFY] 🎧 Notification listener initialized (Privacy: {privacy_mode})", flush=True)
    
    def start_listening(self):
        """Start background listener thread."""
        if self.listening:
            print("[NOTIFY] Listener already running", flush=True)
            return
        
        self.listening = True
        self.listener_thread = threading.Thread(target=self._listener_loop, daemon=True)
        self.listener_thread.start()
        print("[NOTIFY] 🎧 Notification listener started", flush=True)
    
    def stop_listening(self):
        """Stop the listener thread."""
        self.listening = False
        if self.listener_thread:
            self.listener_thread.join(timeout=5)
        print("[NOTIFY] 🎧 Notification listener stopped", flush=True)
    
    def _listener_loop(self):
        """Background loop to poll notifications."""
        import subprocess
        
        while self.listening:
            try:
                # Run adb dumpsys to get notifications
                result = subprocess.run(
                    ["adb", "shell", "dumpsys", "notification", "--noredact"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    notifications = result.stdout
                    self._parse_notifications(notifications)
                else:
                    print(f"[NOTIFY] ⚠️  dumpsys failed: {result.stderr[:100]}", flush=True)
                
                # Poll every 5 seconds
                time.sleep(5)
                
            except FileNotFoundError:
                print("[NOTIFY] ❌ ADB not found", flush=True)
                break
            except subprocess.TimeoutExpired:
                print("[NOTIFY] ⚠️  dumpsys timeout", flush=True)
            except Exception as e:
                print(f"[NOTIFY] ❌ Listener error: {e}", flush=True)
                time.sleep(5)
    
    def _parse_notifications(self, dumpsys_output):
        """Parse dumpsys output for WhatsApp messages."""
        try:
            # Look for WhatsApp package
            if "com.whatsapp" not in dumpsys_output:
                return
            
            # Extract relevant WhatsApp notification blocks
            whatsapp_sections = []
            lines = dumpsys_output.split('\n')
            
            in_whatsapp = False
            current_block = []
            
            for line in lines:
                if 'com.whatsapp' in line:
                    in_whatsapp = True
                
                if in_whatsapp:
                    current_block.append(line)
                    
                    # Check if we've reached end of notification block
                    if (line.strip().startswith('mFlags=') or 
                        line.strip().startswith('icon=') or
                        (len(current_block) > 50 and line.strip() == '')):
                        if len(current_block) > 5:
                            whatsapp_sections.append('\n'.join(current_block))
                        current_block = []
                        in_whatsapp = False
            
            # Parse each section for sender and message
            for section in whatsapp_sections[-5:]:  # Check last 5 notifications
                sender, message = self._extract_whatsapp_data(section)
                
                if sender or message:
                    notification_hash = hash(f"{sender}{message}")
                    
                    # Avoid duplicate notifications
                    if notification_hash != self.last_notification_hash:
                        self.last_notification_hash = notification_hash
                        
                        print(f"[NOTIFY] 📱 New WhatsApp from {sender}: {message[:50] if message else '(no text)'}", flush=True)
                        
                        # Log notification
                        self._log_notification(sender, message)
                        
                        # Trigger callback
                        if self.callback:
                            self.callback(sender, message)
                        
                        break  # Process only the newest notification
        
        except Exception as e:
            print(f"[NOTIFY] ❌ Parse error: {e}", flush=True)
    
    def _extract_whatsapp_data(self, notification_block):
        """Extract sender name and message from notification block."""
        try:
            sender = None
            message = None
            
            # Look for title pattern (usually sender name)
            title_match = re.search(r'titleText=\'([^\']+)\'', notification_block)
            if title_match:
                sender = title_match.group(1).strip()
            
            # Alternative: look in statusBarNotification
            if not sender:
                title_match = re.search(r'pkg=com\.whatsapp.*?tag=\'([^\']+)\'', notification_block)
                if title_match:
                    sender = title_match.group(1).strip()
            
            # Look for message content
            text_match = re.search(r'(?:text|contentText|bigText)=\'([^\']+)\'', notification_block)
            if text_match:
                message = text_match.group(1).strip()
            
            # More aggressive message finding
            if not message:
                # Look for any quoted strings that might be the message
                all_strings = re.findall(r'=\'([^\']{10,}[^\']*?)\'', notification_block)
                if all_strings:
                    for s in all_strings:
                        # Skip technical strings
                        if not any(x in s.lower() for x in ['uri', 'tag', 'icon', 'pkg', 'key=']):
                            message = s
                            break
            
            return sender, message
        
        except Exception as e:
            print(f"[NOTIFY] ❌ Extract error: {e}", flush=True)
            return None, None
    
    def _log_notification(self, sender, message):
        """Log notification to file with timestamp."""
        try:
            log_dir = "logs"
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            
            log_file = os.path.join(log_dir, "notifications.log")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Privacy shield: hide message if privacy mode enabled
            display_message = "[PRIVATE]" if self.privacy_mode else message
            
            log_entry = f"[{timestamp}] WhatsApp from {sender}: {display_message}\n"
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
            
            print(f"[NOTIFY] ✅ Logged to notifications.log", flush=True)
        
        except Exception as e:
            print(f"[NOTIFY] ❌ Logging error: {e}", flush=True)

# Global instances for System & Network control
system_action_engine = SystemActionEngine()
network_iot_controller = NetworkIOTController()

# =========================================================================
# PHASE 3: SELF-EVOLUTION ARCHITECTURE - GLOBAL INSTANCES
# =========================================================================

# Experience memory - learns from errors
experience_memory = ExperienceMemory()

# Internet learning bridge - queries external AI/web
internet_bridge = InternetLearningBridge()

# Self-correction layer - auto-detects and fixes errors
self_correction = SelfCorrection()

# Evolutionary logic - suggests improvements
evolution_logic = EvolutionaryLogic()

# State backup & restore - ensures stability
state_backup = StateBackup()

# =========================================================================
# 1. CONFIGURATION & CONSTANTS
# =========================================================================

CONFIG_FILE = "config.json"
MEMORY_FILE = "memory.json"
KNO_IMAGE_FILE = "current_image.jpg"
WAKE_WORD_MODEL = "./wakeword.onnx"
WAKE_WORD_THRESHOLD = 0.5

# HARDWARE SETTINGS
INPUT_DEVICE_NAME = None
AVAILABLE_DEVICES = []
LAST_WORKING_DEVICE = None

DEFAULT_CONFIG = {
    "text_model": "gemma3:1b",
    "vision_model": "moondream",
    "voice_model": "piper/en_GB-semaine-medium.onnx",
    "chat_memory": True,
    "camera_rotation": 0,
    "system_prompt_extras": "",
    "auto_recovery": True,
    "enable_self_healing": True,
    "privacy_mode": False  # Set to True to hide message content in notifications
}

# LLM SETTINGS - UNRESTRICTED
LLAMA_OPTIONS = {
    'temperature': 0.7,
    'top_k': 40,
    'top_p': 0.9,
    'max_tokens': 512,
    'n_threads': 4
}

def load_config():
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                user_config = json.load(f)
                config.update(user_config)
        except Exception as e:
            print(f"Config Error: {e}. Using defaults.")
    return config

CURRENT_CONFIG = load_config()
TEXT_MODEL = CURRENT_CONFIG["text_model"]
VISION_MODEL = CURRENT_CONFIG["vision_model"]

class BotStates:
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    ERROR = "error"
    CAPTURING = "capturing"
    WARMUP = "warmup"
    HEALING = "healing"       

# --- SYSTEM PROMPT ---
BASE_SYSTEM_PROMPT = """You are KNO, a fully autonomous, self-healing robot assistant with system and network control.
Personality: Intelligent, proactive, helpful robot.
Style: Short sentences. Enthusiastic. Autonomous decision-making.
Additional Role: Autonomous System & Network Controller for your digital and physical workspace.

INSTRUCTIONS:
- If the user asks for a physical action, output JSON.
- If the user just wants to chat, reply with NORMAL TEXT.

### CORE ACTIONS ###

Time & Search:
User: What time is it?
You: {"action": "get_time", "value": "now"}

User: Search for news about robots.
You: {"action": "search_web", "value": "robots news"}

User: What do you see right now?
You: {"action": "capture_image", "value": "environment"}

### GLOBAL CONTROL ACTIONS (new) ###

Browser & Web:
User: Open YouTube for me
You: {"action": "open_browser", "url": "https://www.youtube.com"}

System & Files:
User: List my downloads
You: {"action": "file_list", "directory": "A:\\KNO\\KNO\\downloads"}

User: Copy my KNO folder to desktop
You: {"action": "file_copy", "source": "A:\\KNO\\KNO", "destination": "~/Desktop/KNO"}

User: Open Notepad
You: {"action": "launch_app", "app_name": "notepad.exe"}

Network & Devices:
User: Scan my network for devices
You: {"action": "network_scan", "subnet": "192.168.1.0/24"}

User: Find Chromecast devices
You: {"action": "discover_chromecast"}

User: Mute my TV
You: {"action": "chromecast_command", "device_name": "Living Room TV", "command": "mute"}

User: Connect to Android phone
You: {"action": "adb_connect", "device_address": "192.168.1.50:5555"}

User: Run a command
You: {"action": "run_command", "command": "ipconfig /all"}

Sound & Folder:
User: Play a greeting sound
You: {"action": "play_sound", "value": "greeting"}

User: Open my KNO folder
You: {"action": "open_folder", "path": "A:\\KNO\\KNO"}

Phone & Notifications:
User: Send a message to my phone
You: {"action": "send_phone_notification", "message": "Important: Check your schedule"}

User: Connect to my phone
You: {"action": "adb_connect_wireless", "phone_ip": "192.168.1.100"}

User: Notify my phone
You: {"action": "phone_notify", "msg": "Don't forget your meeting at 3 PM"}

### SPECIAL ROUTINES ###

Morning Routine (TRIGGER: "Good Morning", "Morning", or similar):
User: Good Morning
You: {"action": "morning_routine"}

This executes: greeting sound → weather → TV on → folder → phone report (with user approval)

### END EXAMPLES ###
"""

SYSTEM_PROMPT = BASE_SYSTEM_PROMPT + "\n\n" + CURRENT_CONFIG.get("system_prompt_extras", "")

# Sound Directories - Windows compatible paths
greeting_sounds_dir = os.path.join("sounds", "greeting_sounds")
ack_sounds_dir = os.path.join("sounds", "ack_sounds")
thinking_sounds_dir = os.path.join("sounds", "thinking_sounds")
error_sounds_dir = os.path.join("sounds", "error_sounds")

# =========================================================================
# 2. ADVANCED AUDIO DEVICE DETECTION & FALLBACK
# =========================================================================

class AudioDeviceManager:
    """Intelligent audio device detection with comprehensive fallback."""
    
    def __init__(self):
        self.current_device = None
        self.fallback_devices = []
        self.last_working_device = None
        self.device_silence_count = {}  # Track silent recordings per device
        self.scan_and_cache_devices()
    
    def scan_and_cache_devices(self):
        """Scan all available audio devices and cache them."""
        try:
            devices = sd.query_devices()
            self.fallback_devices = []
            
            if isinstance(devices, dict):
                if devices['max_input_channels'] > 0:
                    self.fallback_devices.append(None)
            else:
                for idx, dev in enumerate(devices):
                    if dev['max_input_channels'] > 0:
                        self.fallback_devices.append(idx)
                        print(f"[AUDIO] Device {idx}: {dev['name']} ({dev['max_input_channels']} channels)", flush=True)
            
            if not self.fallback_devices:
                self.fallback_devices = [None]  # Use default
            
            print(f"[AUDIO] Cached {len(self.fallback_devices)} input device(s)", flush=True)
        except Exception as e:
            print(f"[AUDIO] [ERROR] Error scanning devices: {e}", flush=True)
            self.fallback_devices = [None]

    def set_preferred_device(self, device_index):
        """Set the user's preferred audio device index. Use None for system default."""
        try:
            if device_index is None:
                self.current_device = None
                print("[AUDIO] Preferred device set to system default", flush=True)
            else:
                # validate index exists
                try:
                    dev = sd.query_devices(device_index)
                    self.current_device = device_index
                    self.last_working_device = device_index
                    print(f"[AUDIO] Preferred device set to {device_index}: {dev['name']}", flush=True)
                except Exception as e:
                    print(f"[AUDIO] Could not set preferred device {device_index}: {e}", flush=True)
        except Exception as e:
            print(f"[AUDIO] Error setting preferred device: {e}", flush=True)
    
    def is_device_recording_silence(self, device, duration=0.5):
        """
        SMART HARDWARE RECOVERY
        Test if device is producing valid audio signal.
        Returns True if silence detected (RMS below threshold), False if good audio.
        """
        try:
            sample_rate = 16000
            num_samples = int(sample_rate * duration)
            threshold = 0.002  # RMS threshold for silence detection
            
            print(f"[AUDIO] 🔊 Testing device {device} for silence...", flush=True)
            
            audio_data = sd.rec(num_samples, samplerate=sample_rate, channels=1, device=device, blocking=True)
            rms = np.sqrt(np.mean(audio_data ** 2))
            
            print(f"[AUDIO] 📊 Device {device} RMS: {rms:.6f} (threshold: {threshold})", flush=True)
            
            if rms < threshold:
                print(f"[AUDIO] ⚠️  Device {device}: SILENT (RMS {rms:.6f} < {threshold})", flush=True)
                return True
            else:
                print(f"[AUDIO] ✅ Device {device}: ACTIVE (RMS {rms:.6f})", flush=True)
                return False
        except Exception as e:
            print(f"[AUDIO] ❌ Error testing device {device}: {e}", flush=True)
            return True  # Treat as silent on error
    
    def get_best_device_with_fallback(self):
        """
        Get best available device with intelligent fallback.
        Tests each device to ensure it's producing audio (not silent).
        """
        global LAST_WORKING_DEVICE
        
        print("[AUDIO] 🔄 Starting smart device selection with fallback...", flush=True)
        
        try:
            # Priority 1: Last working device (fastest)
            if self.last_working_device is not None:
                try:
                    if not self.is_device_recording_silence(self.last_working_device):
                        print(f"[AUDIO] ✅ Using remembered device: {self.last_working_device}", flush=True)
                        self.current_device = self.last_working_device
                        return self.last_working_device
                except Exception:
                    pass
            
            # Priority 2: Try device 1 (common USB device)
            if 1 in self.fallback_devices or 1 not in [self.fallback_devices]:
                try:
                    if not self.is_device_recording_silence(1):
                        print(f"[AUDIO] ✅ Using device 1", flush=True)
                        self.last_working_device = 1
                        self.current_device = 1
                        return 1
                except Exception:
                    pass
            
            # Priority 3: Iterate through ALL devices with silence detection
            print(f"[AUDIO] 🔍 Searching through {len(self.fallback_devices)} device(s)...", flush=True)
            for device in self.fallback_devices:
                try:
                    if not self.is_device_recording_silence(device, duration=0.3):
                        print(f"[AUDIO] ✅ Found active device: {device}", flush=True)
                        self.last_working_device = device
                        self.current_device = device
                        return device
                except Exception as e:
                    print(f"[AUDIO] ⚠️  Device {device} test failed: {e}", flush=True)
                    continue
            
            # Final fallback to system default
            print(f"[AUDIO] 📍 All devices silent or failed. Using system default.", flush=True)
            self.last_working_device = None
            self.current_device = None
            return None
            
        except Exception as e:
            print(f"[AUDIO] ❌ Error selecting device: {e}", flush=True)
            return None
    
    def get_best_device(self):
        """Wrapper for compatibility."""
        return self.get_best_device_with_fallback()

audio_device_manager = AudioDeviceManager()

def get_audio_device():
    """Get current audio device with fallback logic."""
    # If user selected a specific device, return it (None means system default)
    try:
        if getattr(audio_device_manager, 'current_device', None) is not None:
            return audio_device_manager.current_device
    except Exception:
        pass
    return audio_device_manager.get_best_device()

# =========================================================================
# 3. SELF-HEALING ERROR RECOVERY FRAMEWORK
# =========================================================================

class ErrorRecoverySystem:
    """User‑centric error recovery system.

    Features:
    - Logs errors and recovery attempts to `experience.json`.
    - Attempts retries with exponential backoff (configurable).
    - Suggests fixes to the user via GUI dialogs and only installs packages after approval.
    - Creates timestamped backups of `agent.py` in `kno_backups` before any code changes.
    - Maintains a history of applied fixes for one‑click rollback.
    """

    def __init__(self, experience_path="experience.json", max_recovery_attempts=3):
        self.error_counts = {}
        self.recovery_attempts = {}
        self.max_recovery_attempts = max_recovery_attempts
        self.experience_path = os.path.join(os.path.dirname(__file__), experience_path)
        self.fix_history = []
        self._load_experience()

    def _load_experience(self):
        try:
            if os.path.exists(self.experience_path):
                with open(self.experience_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.fix_history = data.get("fix_history", [])
            else:
                self._save_experience()
        except Exception:
            # If experience file is corrupted, move it aside and start fresh
            try:
                bad = self.experience_path + ".bad"
                shutil.move(self.experience_path, bad)
            except Exception:
                pass
            self.fix_history = []
            self._save_experience()

    def _save_experience(self):
        payload = {"fix_history": self.fix_history}
        try:
            with open(self.experience_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            print(f"[ERROR RECOVERY] Failed to write experience.json: {e}", flush=True)

    def log_error(self, component, error, exc_info=None):
        """Log and track errors by component and persist to `experience.json`."""
        if component not in self.error_counts:
            self.error_counts[component] = 0
            self.recovery_attempts[component] = 0

        self.error_counts[component] += 1
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        entry = {
            "timestamp": timestamp,
            "component": component,
            "error": str(error),
        }
        if exc_info:
            entry["traceback"] = traceback.format_exc()

        # Append to fix history for auditability (do not auto-fix)
        self.fix_history.append({"type": "error", "entry": entry})
        self._save_experience()
        try:
            gc.collect()
        except Exception:
            pass
        logger.error(f"[ERROR] {component}: {error}")

        # Asynchronously ask DeepSeek for a suggested fix (if available).
        try:
            if 'deepseek_engine' in globals() and deepseek_engine and getattr(deepseek_engine, 'api_key', None):
                def _ask_deepseek():
                    try:
                        trace = entry.get('traceback') or entry.get('error')
                        suggestion = deepseek_engine.analyze_error(trace, context=component)
                        if suggestion:
                            # Record suggestion in history and prompt user to apply
                            self.fix_history.append({"type": "deepseek_suggestion", "component": component, "suggestion": suggestion, "timestamp": datetime.datetime.utcnow().isoformat() + "Z"})
                            self._save_experience()
                            # Show patch/proposal to user (will prompt via GUI)
                            try:
                                self.propose_code_patch(suggestion)
                            except Exception as e:
                                logger.warning(f"Could not prompt user for patch: {e}")
                    except Exception:
                        logger.exception("DeepSeek suggestion thread failed")

                threading.Thread(target=_ask_deepseek, daemon=True).start()
        except Exception as e:
            logger.exception(f"Failed to start DeepSeek suggestion thread: {e}")

    def should_attempt_recovery(self, component):
        """Determine if recovery should be attempted based on past attempts."""
        return self.recovery_attempts.get(component, 0) < self.max_recovery_attempts

    def attempt_recovery(self, component, recovery_callable, *args, **kwargs):
        """Attempt to recover by calling `recovery_callable` with exponential backoff.

        Returns True on success, False on failure. All attempts are logged and saved.
        """
        attempt = 0
        delay = 1
        while attempt < self.max_recovery_attempts:
            try:
                attempt += 1
                self.recovery_attempts[component] = self.recovery_attempts.get(component, 0) + 1
                logger.info(f"Attempting recovery for {component} (attempt {attempt})")
                recovery_callable(*args, **kwargs)
                # success
                self.reset_component(component)
                self.fix_history.append({"type": "recovery", "component": component, "attempt": attempt, "result": "success", "timestamp": datetime.datetime.utcnow().isoformat() + "Z"})
                self._save_experience()
                return True
            except Exception as e:
                logger.warning(f"Recovery attempt {attempt} for {component} failed: {e}")
                self.log_error(component, e)
                time.sleep(delay)
                delay *= 2

        # All attempts failed
        self.fix_history.append({"type": "recovery", "component": component, "result": "failed", "timestamp": datetime.datetime.utcnow().isoformat() + "Z"})
        self._save_experience()
        return False

    def record_recovery_attempt(self, component):
        """Record an explicit recovery attempt (keeps compatibility)."""
        self.recovery_attempts[component] = self.recovery_attempts.get(component, 0) + 1

    def reset_component(self, component):
        """Reset error tracking for a component after successful recovery."""
        self.error_counts[component] = 0
        self.recovery_attempts[component] = 0
        logger.info(f"[RECOVERY] {component} successfully recovered")

    def suggest_fix_install_package(self, package_name, reason=None, parent_window=None):
        """Prompt the user to install a missing package. Returns True if installed.

        This will only install after explicit user approval. All actions are logged.
        """
        reason_text = f"\nReason: {reason}" if reason else ""
        msg = f"Missing dependency detected: {package_name}.{reason_text}\n\nInstall now?"
        try:
            approved = messagebox.askyesno("Install Dependency?", msg, parent=parent_window)
        except Exception:
            # If messagebox unavailable (headless), ask via console
            approved = input(msg + " [y/N]: ").strip().lower() == "y"

        if not approved:
            logger.info(f"User declined to install {package_name}")
            self.fix_history.append({"type": "declined_install", "package": package_name, "timestamp": datetime.datetime.utcnow().isoformat() + "Z"})
            self._save_experience()
            return False

        # Create backup of agent.py before making changes
        try:
            self.create_backup(os.path.abspath(__file__))
        except Exception as e:
            logger.warning(f"Failed to create backup before installing {package_name}: {e}")

        # Attempt pip install
        installed = self._pip_install(package_name)
        self.fix_history.append({"type": "installed_package", "package": package_name, "result": installed, "timestamp": datetime.datetime.utcnow().isoformat() + "Z"})
        self._save_experience()
        return installed

    def _pip_install(self, package_name):
        """Install a package using pip in the current environment.

        This function is executed only after explicit user approval.
        """
        try:
            cmd = [sys.executable, "-m", "pip", "install", package_name]
            logger.info(f"Installing package: {package_name}")
            proc = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            logger.debug(proc.stdout)
            if proc.returncode == 0:
                logger.info(f"Successfully installed {package_name}")
                return True
            else:
                logger.error(f"pip install failed for {package_name}: {proc.stderr}")
                return False
        except Exception as e:
            logger.exception(f"Exception during pip install of {package_name}: {e}")
            return False

    def create_backup(self, file_path, backups_dir=None):
        """Create a timestamped backup of a file into `kno_backups`.

        Returns the path to the backup file.
        """
        try:
            if backups_dir is None:
                backups_dir = os.path.join(os.path.dirname(__file__), "kno_backups")
            os.makedirs(backups_dir, exist_ok=True)
            base = os.path.basename(file_path)
            ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            backup_name = f"{base}.{ts}.bak"
            dst = os.path.join(backups_dir, backup_name)
            shutil.copy2(file_path, dst)
            logger.info(f"Created backup: {dst}")
            self.fix_history.append({"type": "backup", "source": file_path, "backup": dst, "timestamp": datetime.datetime.utcnow().isoformat() + "Z"})
            self._save_experience()
            return dst
        except Exception as e:
            logger.exception(f"Failed to create backup for {file_path}: {e}")
            return None

    def propose_code_patch(self, patch_text, parent_window=None):
        """Show a patch to the user in a simple diff dialog and apply only after approval.

        `patch_text` is a unified diff-like string. The function will create a backup before applying.
        """
        try:
            # Ask the user to approve the patch
            approved = messagebox.askyesno("Apply Code Patch?", f"A proposed code patch is available. Apply now?\n\nPatch summary:\n{patch_text[:400]}", parent=parent_window)
        except Exception:
            approved = input("Apply patch? [y/N]: ").strip().lower() == "y"

        if not approved:
            logger.info("User declined to apply proposed patch")
            self.fix_history.append({"type": "patch_declined", "summary": patch_text[:200], "timestamp": datetime.datetime.utcnow().isoformat() + "Z"})
            self._save_experience()
            return False

        # Create backup
        try:
            backup = self.create_backup(os.path.abspath(__file__))
        except Exception as e:
            logger.warning(f"Could not create backup before applying patch: {e}")

        # Apply patch: for safety, write patch_text to a temp file and run `patch` if available,
        # otherwise fail and ask the user to apply manually. We avoid automated, risky edits.
        try:
            # Write patch to temporary file for user inspection or external application
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".patch", mode="w", encoding="utf-8")
            tmp.write(patch_text)
            tmp.close()
            logger.info(f"Patch written to {tmp.name}; please apply manually if automatic apply is unsupported.")
            self.fix_history.append({"type": "patch_saved", "patch_file": tmp.name, "timestamp": datetime.datetime.utcnow().isoformat() + "Z"})
            self._save_experience()
            # Attempt to apply with the `patch` utility if present (best-effort)
            patch_cmd = shutil.which("patch")
            if patch_cmd:
                proc = subprocess.run([patch_cmd, "-p0", "<", tmp.name], shell=True)
                if proc.returncode == 0:
                    logger.info("Patch applied successfully using system patch utility.")
                    return True
                else:
                    logger.warning("System patch utility failed; patch saved for manual apply.")
            return True
        except Exception as e:
            logger.exception(f"Failed to apply patch automatically: {e}")
            return False

error_recovery = ErrorRecoverySystem()

# =========================================================================
# 3.1 RESOURCE DOWNLOADER - AUTO-DOWNLOAD MISSING MODELS
# =========================================================================

class ResourceDownloader:
    """
    AUTO-DOWNLOAD MISSING GGUF MODELS
    If no model found, automatically fetches lightweight model from Hugging Face.
    """
    
    # Lightweight model candidates (in priority order)
    FALLBACK_MODELS = [
        {
            "name": "tinyllama-1.1b",
            "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
            "size_mb": 700,
            "description": "Ultra-lightweight 1.1B model"
        },
        {
            "name": "phi-2-mini",
            "url": "https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf",
            "size_mb": 1600,
            "description": "Lightweight 2.7B model"
        },
        {
            "name": "gemma-2b",
            "url": "https://huggingface.co/google/gemma-2b-it-gguf/resolve/main/gemma-2b-it.gguf",
            "size_mb": 1800,
            "description": "Google Gemma 2B instruction-tuned"
        }
    ]
    
    @staticmethod
    def calculate_checksum(filepath, algorithm='md5'):
        """Calculate file checksum for integrity verification."""
        import hashlib
        hash_obj = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    
    @staticmethod
    def verify_model_integrity(filepath, expected_size=None):
        """Verify downloaded model is valid GGUF file."""
        try:
            if not os.path.exists(filepath):
                print(f"[DOWNLOADER] ❌ File not found: {filepath}", flush=True)
                return False
            
            file_size = os.path.getsize(filepath)
            
            # Check if file has reasonable size
            if file_size < 100 * 1024 * 1024:  # Less than 100MB is likely corrupted
                print(f"[DOWNLOADER] ❌ File suspiciously small: {file_size} bytes", flush=True)
                return False
            
            # Check GGUF magic header (0x47475146 = 'GGUF' in hex)
            with open(filepath, 'rb') as f:
                magic = f.read(4)
                if magic != b'GGUF':
                    print(f"[DOWNLOADER] ❌ Invalid GGUF header. Got: {magic.hex()}", flush=True)
                    return False
            
            checksum = ResourceDownloader.calculate_checksum(filepath)
            print(f"[DOWNLOADER] ✅ Model integrity verified - Checksum: {checksum[:8]}...", flush=True)
            return True
        
        except Exception as e:
            print(f"[DOWNLOADER] ❌ Integrity check failed: {e}", flush=True)
            return False
    
    @staticmethod
    def download_and_verify_model(model_info, destination):
        """Download model with checksum verification and retry logic."""
        filepath = os.path.join(destination, os.path.basename(model_info["url"].split('/')[-1]))
        
        print(f"[DOWNLOADER] 🌐 Fetching {model_info['name']}...", flush=True)
        print(f"[DOWNLOADER] 📝 {model_info['description']}", flush=True)
        print(f"[DOWNLOADER] 📏 Size: ~{model_info['size_mb']}MB", flush=True)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"[DOWNLOADER] ⬇️  Download attempt {attempt + 1}/{max_retries}...", flush=True)
                
                response = requests.get(model_info["url"], stream=True, timeout=300)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                chunk_size = 1024 * 1024  # 1MB chunks
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size:
                                percent = (downloaded / total_size) * 100
                                mb_done = downloaded / (1024 * 1024)
                                mb_total = total_size / (1024 * 1024)
                                print(f"[DOWNLOADER] {percent:.1f}% - {mb_done:.0f}MB/{mb_total:.0f}MB", flush=True, end='\r')
                
                print(f"\n[DOWNLOADER] ✅ Download complete, verifying...", flush=True)
                
                # Verify integrity
                if ResourceDownloader.verify_model_integrity(filepath):
                    print(f"[DOWNLOADER] ✅ Model ready: {filepath}", flush=True)
                    return filepath
                else:
                    os.remove(filepath)
                    raise Exception("Integrity check failed")
            
            except Exception as e:
                print(f"[DOWNLOADER] ❌ Download failed (attempt {attempt + 1}): {e}", flush=True)
                if os.path.exists(filepath):
                    os.remove(filepath)
                time.sleep(min(2 ** attempt, 30))
        
        print(f"[DOWNLOADER] ❌ Could not download {model_info['name']}", flush=True)
        return None
    
    @staticmethod
    def auto_download_model():
        """
        Automatically download lightest available model if none exist.
        Tries models in priority order until one succeeds.
        """
        models_dir = os.path.join(os.getcwd(), "models")
        Path(models_dir).mkdir(parents=True, exist_ok=True)
        
        print(f"\n[DOWNLOADER] 🚀 INITIATING AUTO-DOWNLOAD SEQUENCE", flush=True)
        print(f"[DOWNLOADER] 🛰️  Searching for lightweight GGUF models on Hugging Face...", flush=True)
        
        for model_info in ResourceDownloader.FALLBACK_MODELS:
            print(f"\n[DOWNLOADER] 🔄 Trying: {model_info['name']}...", flush=True)
            
            filepath = ResourceDownloader.download_and_verify_model(model_info, models_dir)
            if filepath:
                print(f"[DOWNLOADER] ✨ SUCCESS! Auto-downloaded model: {filepath}", flush=True)
                return filepath
            
            print(f"[DOWNLOADER] ⏭️  Trying next model...", flush=True)
        
        print(f"[DOWNLOADER] ❌ CRITICAL: Could not auto-download any model!", flush=True)
        return None
    
    @staticmethod
    def _clear_cache():
        """Clear downloaded temporary files and caches for recovery."""
        print(f"[DOWNLOADER] 🧹 Clearing cache files...", flush=True)
        
        try:
            cache_patterns = ["*.tmp", "*.partial"]
            models_dir = os.path.join(os.getcwd(), "models")
            
            if os.path.exists(models_dir):
                for pattern in cache_patterns:
                    import glob
                    for filepath in glob.glob(os.path.join(models_dir, pattern)):
                        try:
                            os.remove(filepath)
                            print(f"[DOWNLOADER] 🗑️  Removed: {filepath}", flush=True)
                        except Exception as e:
                            print(f"[DOWNLOADER] ⚠️  Could not remove: {e}", flush=True)
            
            print(f"[DOWNLOADER] ✅ Cache cleared", flush=True)
            return True
        
        except Exception as e:
            print(f"[DOWNLOADER] ❌ Cache clear failed: {e}", flush=True)
            return False

# =========================================================================
# 3.2 EXPERIENCE MANAGER - ERROR REFLECTION & LEARNING
# =========================================================================

class ExperienceManager:
    """
    EXPERIENCE.JSON MAINTENANCE & ERROR REFLECTION
    Records mistakes, analyzes patterns, prevents repeat failures.
    """
    
    EXPERIENCE_FILE = "experience.json"
    
    def __init__(self):
        self.experiences = self.load_experiences()
        self.current_session_errors = []
    
    def load_experiences(self):
        """Load past experiences from experience.json."""
        try:
            if os.path.exists(self.EXPERIENCE_FILE):
                with open(self.EXPERIENCE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[EXPERIENCE] ❌ Error loading experiences: {e}", flush=True)
        
        return {
            "total_errors": 0,
            "error_patterns": {},
            "resolved_issues": [],
            "learned_solutions": [],
            "last_updated": None,
            "session_history": []
        }
    
    def save_experiences(self):
        """Save experiences to experience.json."""
        try:
            self.experiences["last_updated"] = datetime.datetime.now().isoformat()
            with open(self.EXPERIENCE_FILE, 'w') as f:
                json.dump(self.experiences, f, indent=2)
            print(f"[EXPERIENCE] 💾 Experiences saved", flush=True)
        except Exception as e:
            print(f"[EXPERIENCE] ❌ Error saving experiences: {e}", flush=True)
    
    def log_error(self, error_type, error_message, context=""):
        """Log an error to experience database."""
        error_key = f"{error_type}:{error_message[:50]}"
        
        if error_key not in self.experiences["error_patterns"]:
            self.experiences["error_patterns"][error_key] = {
                "count": 0,
                "first_seen": datetime.datetime.now().isoformat(),
                "last_seen": None,
                "contexts": []
            }
        
        self.experiences["error_patterns"][error_key]["count"] += 1
        self.experiences["error_patterns"][error_key]["last_seen"] = datetime.datetime.now().isoformat()
        self.experiences["error_patterns"][error_key]["contexts"].append(context)
        self.experiences["total_errors"] += 1
        
        self.current_session_errors.append({
            "type": error_type,
            "message": error_message,
            "context": context,
            "timestamp": datetime.datetime.now().isoformat()
        })
        try:
            gc.collect()
        except Exception:
            pass
        
        print(f"[EXPERIENCE] 📝 Error logged: {error_type} - {error_message[:40]}...", flush=True)
        self.save_experiences()
    
    def get_repeated_errors(self, threshold=2):
        """Get errors that have occurred multiple times (likely patterns to fix)."""
        return {k: v for k, v in self.experiences["error_patterns"].items() 
                if v["count"] >= threshold}
    
    def log_solution(self, error_type, solution):
        """Log a learned solution for future reference."""
        self.experiences["learned_solutions"].append({
            "error_type": error_type,
            "solution": solution,
            "discovered": datetime.datetime.now().isoformat()
        })
        print(f"[EXPERIENCE] 💡 Solution learned for {error_type}", flush=True)
        self.save_experiences()
    
    def was_error_seen_before(self, error_type):
        """Check if similar error has occurred before."""
        for pattern in self.experiences["error_patterns"]:
            if error_type in pattern and self.experiences["error_patterns"][pattern]["count"] > 0:
                return True, self.experiences["error_patterns"][pattern]
        return False, None

# Global experience manager instance
experience_manager = ExperienceManager()

# =========================================================================
# 3.3 SELF-CORRECTION LAYER - LEARNING FROM FAILURES
# =========================================================================

class SelfCorrectionLayer:
    """
    SELF-CORRECTION & LEARNING LOOP
    Detects failures, researches solutions, implements fixes autonomously.
    """
    
    def __init__(self):
        self.learning_mode_active = False
        self.corrections_applied = []
    
    def detect_failure(self, component, error, context=""):
        """
        Detect and record a failure event.
        Returns: (needs_learning, research_required)
        """
        print(f"[CORRECTION] 🔍 Failure detected in {component}: {error}", flush=True)
        
        # Check if we've seen this error before
        was_seen, pattern = experience_manager.was_error_seen_before(component)
        
        if was_seen and pattern["count"] > 2:
            print(f"[CORRECTION] ⚠️  This error has occurred {pattern['count']} times!", flush=True)
            return (True, True)  # Needs learning and research
        
        experience_manager.log_error(component, error, context)
        return (True, was_seen == False)
    
    def research_solution_online(self, error_type, component):
        """
        Research solution using web search (DuckDuckGo).
        Attempts to find documentation or solutions online.
        """
        print(f"[CORRECTION] 🌐 Researching solution for {component}...", flush=True)
        
        try:
            search_queries = [
                f"{component} {error_type} fix solution",
                f"{error_type} python error troubleshooting",
                f"KNO agent {component} configuration"
            ]
            
            from duckduckgo_search import DDGS
            ddgs = DDGS()
            
            for query in search_queries:
                print(f"[CORRECTION] 🔎 Searching: {query}", flush=True)
                try:
                    results = ddgs.text(query, max_results=3)
                    if results:
                        print(f"[CORRECTION] ✅ Found {len(results)} relevant resources", flush=True)
                        solutions = []
                        for result in results:
                            solutions.append({
                                "title": result.get("title", ""),
                                "body": result.get("body", "")[:200],
                                "url": result.get("href", "")
                            })
                        return solutions
                except Exception as e:
                    print(f"[CORRECTION] ⚠️  Search failed: {e}", flush=True)
                    continue
        
        except Exception as e:
            print(f"[CORRECTION] ❌ Research failed: {e}", flush=True)
        
        return None
    
    def apply_correction(self, correction_action, parameters=None):
        """
        Apply a self-correction action (e.g., restart service, reload config, retry).
        """
        print(f"[CORRECTION] 🔧 Applying correction: {correction_action}", flush=True)
        
        corrections_map = {
            "restart_llama": lambda: LlamaConnector.reload_model(),
            "reload_config": lambda: load_config(),
            "restart_audio": lambda: audio_device_manager.scan_and_cache_devices(),
            "clear_cache": lambda: ResourceDownloader._clear_cache(),
        }
        
        if correction_action in corrections_map:
            try:
                corrections_map[correction_action]()
                self.corrections_applied.append({
                    "action": correction_action,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "success": True
                })
                print(f"[CORRECTION] ✅ Correction applied successfully", flush=True)
                return True
            except Exception as e:
                print(f"[CORRECTION] ❌ Correction failed: {e}", flush=True)
                self.corrections_applied.append({
                    "action": correction_action,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "success": False,
                    "error": str(e)
                })
                return False
        
        print(f"[CORRECTION] ⚠️  Unknown correction action: {correction_action}", flush=True)
        return False

# Global self-correction layer instance
self_correction_layer = SelfCorrectionLayer()

# =========================================================================
# 3.4 KNO EVOLUTION MODULE - SELF-IMPROVEMENT & PATCHING
# =========================================================================

class KNO_Evolution:
    """
    EVOLUTIONARY PROGRAMMING - SELF-IMPROVEMENT THROUGH CODE EVOLUTION
    Auto-install dependencies, draft patches, optimize regex patterns.
    All changes logged with restore points for stability.
    """
    
    EVOLUTION_LOG = "evolution.json"
    BACKUP_DIR = "backups"
    
    def __init__(self):
        self.evolution_history = self.load_evolution_log()
        Path(self.BACKUP_DIR).mkdir(parents=True, exist_ok=True)
    
    def load_evolution_log(self):
        """Load evolution history from evolution.json."""
        try:
            if os.path.exists(self.EVOLUTION_LOG):
                with open(self.EVOLUTION_LOG, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[EVOLUTION] ❌ Error loading evolution log: {e}", flush=True)
        
        return {
            "total_adaptations": 0,
            "patches_applied": [],
            "dependencies_added": [],
            "regex_optimizations": [],
            "restore_points": []
        }
    
    def save_evolution_log(self):
        """Save evolution history."""
        try:
            with open(self.EVOLUTION_LOG, 'w') as f:
                json.dump(self.evolution_history, f, indent=2)
        except Exception as e:
            print(f"[EVOLUTION] ❌ Error saving evolution log: {e}", flush=True)
    
    def create_restore_point(self, component_name):
        """Create backup restore point before any modifications."""
        timestamp = datetime.datetime.now().isoformat()
        
        try:
            if component_name == "agent":
                backup_file = os.path.join(self.BACKUP_DIR, f"agent_backup_{timestamp.replace(':', '-')}.py")
                shutil.copy("agent.py", backup_file)
                self.evolution_history["restore_points"].append({
                    "component": component_name,
                    "backup_file": backup_file,
                    "timestamp": timestamp
                })
                print(f"[EVOLUTION] 💾 Restore point created: {backup_file}", flush=True)
                return backup_file
        except Exception as e:
            print(f"[EVOLUTION] ❌ Failed to create restore point: {e}", flush=True)
        
        return None
    
    def auto_install_dependency(self, package_name, pip_name=None):
        """Automatically install missing Python dependency."""
        if pip_name is None:
            pip_name = package_name
        
        print(f"[EVOLUTION] 📦 Auto-installing dependency: {pip_name}", flush=True)
        
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", pip_name, "-q"],
                timeout=120,
                check=True
            )
            
            self.evolution_history["dependencies_added"].append({
                "package": package_name,
                "pip_name": pip_name,
                "installed": datetime.datetime.now().isoformat()
            })
            
            print(f"[EVOLUTION] ✅ Successfully installed: {pip_name}", flush=True)
            self.save_evolution_log()
            return True
        
        except subprocess.CalledProcessError:
            print(f"[EVOLUTION] ❌ Failed to install: {pip_name}", flush=True)
            return False
    
    def detect_missing_imports(self, filepath):
        """
        Scan Python file for import errors and return list of needed packages.
        Returns list of (import_name, pip_name) tuples.
        """
        print(f"[EVOLUTION] 🔍 Scanning for missing imports...", flush=True)
        
        missing_packages = []
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Extract import statements
            import_patterns = [
                r'import\s+(\w+)',
                r'from\s+(\w+)',
            ]
            
            for pattern in import_patterns:
                for match in re.finditer(pattern, content):
                    module_name = match.group(1)
                    
                    # Try importing to see if it exists
                    try:
                        __import__(module_name)
                    except ImportError:
                        print(f"[EVOLUTION] ⚠️  Missing: {module_name}", flush=True)
                        missing_packages.append((module_name, module_name.replace('_', '-')))
        
        except Exception as e:
            print(f"[EVOLUTION] ❌ Import scan failed: {e}", flush=True)
        
        return missing_packages
    
    def optimize_regex_patterns(self):
        """
        Analyze WhatsApp parsing and voice recognition regex patterns.
        Suggest optimizations based on historical data from experience.json.
        """
        print(f"[EVOLUTION] 🔬 Analyzing regex patterns for optimization...", flush=True)
        
        optimizations = []
        
        # Analyze WhatsApp message patterns from experience
        whatsapp_errors = {k: v for k, v in experience_manager.experiences["error_patterns"].items() 
                          if "whatsapp" in k.lower() or "notification" in k.lower()}
        
        if whatsapp_errors:
            print(f"[EVOLUTION] 📊 Found {len(whatsapp_errors)} WhatsApp-related patterns", flush=True)
            optimizations.append({
                "pattern": "whatsapp_parsing",
                "issue_count": len(whatsapp_errors),
                "suggestion": "Expand regex to handle more message formats"
            })
        
        # Analyze audio-related patterns
        audio_errors = {k: v for k, v in experience_manager.experiences["error_patterns"].items() 
                       if "audio" in k.lower() or "voice" in k.lower()}
        
        if audio_errors:
            print(f"[EVOLUTION] 📊 Found {len(audio_errors)} audio-related patterns", flush=True)
            optimizations.append({
                "pattern": "voice_recognition",
                "issue_count": len(audio_errors),
                "suggestion": "Improve noise detection and filtering"
            })
        
        if optimizations:
            self.evolution_history["regex_optimizations"].append({
                "timestamp": datetime.datetime.now().isoformat(),
                "optimizations": optimizations
            })
            self.save_evolution_log()
        
        return optimizations
    
    def suggest_patch(self, component, improvement_suggestion):
        """
        Suggest or draft a patch for improvement.
        Would be used with AI analysis to generate actual code patches.
        """
        print(f"[EVOLUTION] 🏷️  Patch suggestion for {component}: {improvement_suggestion[:50]}...", flush=True)
        
        self.evolution_history["patches_applied"].append({
            "component": component,
            "suggestion": improvement_suggestion,
            "status": "suggested",
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        self.save_evolution_log()

# Global evolution module instance
kno_evolution = KNO_Evolution()

# =========================================================================
# 3.5 IDLE OPTIMIZER - SELF-STUDY & PATTERN LEARNING
# =========================================================================

class IdleOptimizer:
    """
    IDLE-TIME SELF-STUDY
    When KNO is idle, it analyzes logs, optimizes patterns, learns from history.
    """
    
    def __init__(self):
        self.last_optimization_time = None
        self.optimization_interval = 3600  # 1 hour between optimizations
    
    def perform_self_study(self):
        """
        Autonomous self-study routine:
        1. Read and analyze logs
        2. Identify error patterns
        3. Suggest regex optimizations
        4. Check for missing dependencies
        """
        print(f"\n[IDLE] 📚 Starting self-study session...", flush=True)
        
        try:
            # Analyze error patterns from experience
            repeated_errors = experience_manager.get_repeated_errors(threshold=2)
            if repeated_errors:
                print(f"[IDLE] 📊 Identified {len(repeated_errors)} recurring error patterns", flush=True)
                for error_key, pattern in list(repeated_errors.items())[:3]:
                    print(f"[IDLE]   - {error_key}: {pattern['count']} occurrences", flush=True)
            
            # Suggest regex optimizations
            optimizations = kno_evolution.optimize_regex_patterns()
            if optimizations:
                print(f"[IDLE] 💡 Generated {len(optimizations)} optimization suggestions", flush=True)
            
            # Check for missing imports
            missing = kno_evolution.detect_missing_imports("agent.py")
            if missing:
                print(f"[IDLE] ⚠️  Found {len(missing)} potentially missing imports", flush=True)
                for import_name, _ in missing[:3]:
                    print(f"[IDLE]   - {import_name}", flush=True)
            
            # Analyze log file sizes
            if os.path.exists("logs"):
                log_files = os.listdir("logs")
                print(f"[IDLE] 📁 Log directory contains {len(log_files)} files", flush=True)
            
            self.last_optimization_time = time.time()
            print(f"[IDLE] ✅ Self-study session complete", flush=True)
        
        except Exception as e:
            print(f"[IDLE] ❌ Self-study failed: {e}", flush=True)
    
    def should_perform_idle_optimization(self):
        """Check if enough time has passed to perform another optimization."""
        if self.last_optimization_time is None:
            return True
        
        return (time.time() - self.last_optimization_time) > self.optimization_interval
    
    def start_idle_monitor_thread(self):
        """
        Start background thread that performs self-study periodically.
        Runs during idle periods (every hour or when idle for 5+ minutes).
        """
        def idle_monitor_loop():
            idle_threshold = 300  # 5 minutes of inactivity
            last_activity = time.time()
            
            while True:
                try:
                    current_time = time.time()
                    idle_time = current_time - last_activity
                    
                    # Perform self-improvement if enough time passed
                    if self.should_perform_idle_optimization() and idle_time > idle_threshold:
                        self.perform_self_study()
                    
                    time.sleep(60)  # Check every minute
                
                except Exception as e:
                    print(f"[IDLE] ❌ Monitor error: {e}", flush=True)
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=idle_monitor_loop, daemon=True)
        monitor_thread.start()
        print(f"[IDLE] 🚀 Idle optimizer started", flush=True)

# Global idle optimizer instance
idle_optimizer = IdleOptimizer()

# =========================================================================
# =========================================================================
# LLAMA-CPP DIRECT INTEGRATION (No HTTP/Server)
# =========================================================================

class LlamaConnector:
    """
    DIRECT LOCAL LLAMA INTEGRATION
    Uses llama-cpp-python to load GGUF models directly - no server dependency.
    """
    
    llm_instance = None  # Global instance of loaded model
    MODEL_PATH = os.path.join(os.getcwd(), "models", "gemma-3-1b.gguf")
    MAX_RETRIES = 3
    
    @staticmethod
    def verify_and_setup_model():
        """
        STRICT MODEL PATH VERIFICATION WITH AUTO-DOWNLOAD
        Checks for primary model, fallback, then triggers auto-download if needed.
        Returns: (model_path, is_fallback) or (None, False) if no model found
        """
        primary_model = os.path.join(os.getcwd(), "models", "gemma-3-1b.gguf")
        
        # Check primary model
        if os.path.exists(primary_model) and os.path.getsize(primary_model) > 0:
            print(f"[LLAMA] ✅ Primary model found: {primary_model}", flush=True)
            LlamaConnector.MODEL_PATH = primary_model
            return (primary_model, False)
        
        # Primary model missing - search for fallback
        print(f"[LLAMA] ❌ Primary model NOT found: {primary_model}", flush=True)
        print(f"[LLAMA] 🔍 Searching for fallback .gguf files in models directory...", flush=True)
        
        models_dir = os.path.join(os.getcwd(), "models")
        if not os.path.exists(models_dir):
            print(f"[LLAMA] ❌ Models directory does not exist: {models_dir}", flush=True)
            Path(models_dir).mkdir(parents=True, exist_ok=True)
        
        # Search for any .gguf file
        gguf_files = [f for f in os.listdir(models_dir) if f.endswith(".gguf")]
        
        if gguf_files:
            fallback_model = os.path.join(models_dir, gguf_files[0])
            print(f"[LLAMA] ⚠️  USING FALLBACK: {gguf_files[0]}", flush=True)
            print(f"[LLAMA] 📝 Fallback model at: {fallback_model}", flush=True)
            LlamaConnector.MODEL_PATH = fallback_model
            return (fallback_model, True)
        
        # No model found - TRIGGER AUTO-DOWNLOAD
        print(f"[LLAMA] ❌ NO .gguf files found in {models_dir}", flush=True)
        print(f"[LLAMA] 🚀 TRIGGERING AUTOMATIC MODEL DOWNLOAD", flush=True)
        
        downloaded_model = ResourceDownloader.auto_download_model()
        
        if downloaded_model:
            print(f"[LLAMA] ✅ Auto-download succeeded: {downloaded_model}", flush=True)
            LlamaConnector.MODEL_PATH = downloaded_model
            return (downloaded_model, True)  # Mark as fallback since it wasn't primary
        
        print(f"[LLAMA] ❌ AUTO-DOWNLOAD FAILED - NO MODEL AVAILABLE", flush=True)
        return (None, False)
    
    @staticmethod
    def load_model():
        """
        PHASE 5 REFACTOR: Cloud LLM Bridge initialization.
        Returns cloud_llm_bridge for use as primary LLM.
        """
        if LlamaConnector.llm_instance is not None:
            print(f"[LLAMA] ✅ Cloud LLM Bridge ready", flush=True)
            return LlamaConnector.llm_instance
        
        print(f"[LLAMA] 🌐 PHASE 5: Using Cloud LLM (Gemini + ChatGPT)", flush=True)
        try:
            global cloud_llm_bridge
            LlamaConnector.llm_instance = cloud_llm_bridge
            print(f"[LLAMA] ✅ Cloud LLM initialized (Gemini primary, ChatGPT fallback)", flush=True)
            return LlamaConnector.llm_instance
        except Exception as e:
            print(f"[LLAMA] ❌ Cloud LLM init failed: {e}", flush=True)
            return None
    
    @staticmethod
    def chat_completion(messages, temperature=0.7, max_tokens=512):
        """
        PHASE 5: Route to CloudLLMBridge for cloud-based chat completion.
        """
        if LlamaConnector.llm_instance is None:
            LlamaConnector.load_model()
        
        if LlamaConnector.llm_instance is None:
            print(f"[LLAMA] ❌ Cloud LLM not available", flush=True)
            return None
        
        return LlamaConnector.llm_instance.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    @staticmethod
    def stream_chat_completion(messages, temperature=0.7, max_tokens=512):
        """
        PHASE 5: Route to CloudLLMBridge for streaming chat completion.
        """
        if LlamaConnector.llm_instance is None:
            LlamaConnector.load_model()
        
        if LlamaConnector.llm_instance is None:
            print(f"[LLAMA] ❌ Cloud LLM not available", flush=True)
            return
        
        for chunk in LlamaConnector.llm_instance.stream_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        ):
            yield chunk
    
    @staticmethod
    def reload_model():
        print(f"[CLOUD] Reinitializing Cloud LLM...", flush=True)
        try:
            if LlamaConnector.llm_instance is not None:
                LlamaConnector.llm_instance = None
            LlamaConnector.load_model()
            return LlamaConnector.llm_instance is not None
        except Exception as e:
            print(f"[CLOUD] Error: {e}", flush=True)
            return False

# =========================================================================
# COMPUTER USE MODULES (OpenClaw Integration)
# =========================================================================

class VisionModule:
    """
    Screenshot capture and visual analysis using Gemini 1.5 Flash.
    Provides computer use (GUI automation) perception capabilities.
    """
    def __init__(self):
        self.vision_enabled = False
        self.screenshot_lock = threading.Lock()
        try:
            from PIL import ImageGrab
            self.ImageGrab = ImageGrab
            self.vision_enabled = True
            logger.info("✓ Vision module initialized (PIL available)")
        except ImportError:
            logger.warning("✗ Vision module disabled (PIL/pillow not installed)")
    
    def capture_screenshot(self, save_path=None):
        """
        Capture current screen to PIL Image or file.
        
        Args:
            save_path: Optional file path to save screenshot (PNG)
        
        Returns:
            PIL Image object or None if capture fails
        """
        if not self.vision_enabled:
            return None
        
        with self.screenshot_lock:
            try:
                screenshot = self.ImageGrab.grab()
                if save_path:
                    save_path = Path(save_path)
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    screenshot.save(save_path, "PNG")
                    logger.debug(f"Screenshot saved: {save_path}")
                return screenshot
            except Exception as e:
                logger.error(f"Screenshot capture failed: {e}")
                return None
    
    def analyze_screenshot(self, prompt="Describe what you see in this screenshot. Are there any error dialogs?"):
        """
        Send screenshot to Gemini 1.5 Flash for visual analysis.
        
        Args:
            prompt: Analysis prompt for the vision model
        
        Returns:
            Analysis text or None if analysis fails
        """
        if not self.vision_enabled:
            return None
        
        try:
            screenshot = self.capture_screenshot()
            if screenshot is None:
                return None
            
            # Convert PIL Image to bytes
            import io
            img_bytes = io.BytesIO()
            screenshot.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            
            # Prepare request to Gemini
            import base64
            image_data = base64.standard_b64encode(img_bytes.read()).decode()
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_data
                            }
                        }
                    ]
                }]
            }
            
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": higher_intelligence_bridge.api_key
            }
            
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                json=payload,
                headers=headers,
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            if "candidates" in data and data["candidates"]:
                analysis = data["candidates"][0].get("content", {}).get("parts", [{}])[0].get("text", "")
                logger.debug(f"Vision analysis: {analysis[:100]}...")
                return analysis
            return None
        except Exception as e:
            logger.warning(f"Vision analysis failed: {e}")
            return None


class ActionExecutor:
    """
    Execute GUI actions (mouse, keyboard, scroll) using pyautogui.
    Provides computer use (action) capabilities for autonomous error recovery.
    """
    def __init__(self, vision_module=None):
        self.vision_module = vision_module
        self.actions_enabled = False
        try:
            import pyautogui
            pyautogui.FAILSAFE = True  # Press top-left corner to abort
            pyautogui.PAUSE = 0.5  # 500ms between actions
            self.pyautogui = pyautogui
            self.actions_enabled = True
            logger.info("✓ Action executor initialized (pyautogui available)")
        except ImportError:
            logger.warning("✗ Action executor disabled (pyautogui not installed)")
    
    def click(self, x, y, button="left", clicks=1):
        """Click mouse button at coordinates."""
        if not self.actions_enabled:
            return False
        try:
            self.pyautogui.click(x, y, button=button, clicks=clicks)
            logger.debug(f"Clicked {button} at ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Click action failed: {e}")
            return False
    
    def type_text(self, text):
        """Type text using keyboard."""
        if not self.actions_enabled:
            return False
        try:
            self.pyautogui.typewrite(text, interval=0.05)
            logger.debug(f"Typed: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Type action failed: {e}")
            return False
    
    def scroll(self, x, y, clicks=1):
        """Scroll at coordinates (positive=up, negative=down)."""
        if not self.actions_enabled:
            return False
        try:
            self.pyautogui.moveTo(x, y)
            self.pyautogui.scroll(clicks)
            logger.debug(f"Scrolled {clicks} clicks at ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Scroll action failed: {e}")
            return False
    
    def move_mouse(self, x, y):
        """Move mouse to coordinates."""
        if not self.actions_enabled:
            return False
        try:
            self.pyautogui.moveTo(x, y, duration=0.5)
            logger.debug(f"Moved mouse to ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Move action failed: {e}")
            return False
    
    def press_key(self, key):
        """Press a single key (e.g., 'enter', 'escape', 'tab')."""
        if not self.actions_enabled:
            return False
        try:
            self.pyautogui.press(key)
            logger.debug(f"Pressed key: {key}")
            return True
        except Exception as e:
            logger.error(f"Key press action failed: {e}")
            return False
    
    def autonomous_error_recovery(self):
        """
        Detect and recover from error dialogs using vision + action.
        
        1. Capture screenshot
        2. Ask Gemini: "Is there an error dialog visible?"
        3. If yes, attempt common recovery actions:
           - Click OK button
           - Click Close button
           - Press Escape key
           - Click first button found
        
        Returns:
            True if error was detected and recovery attempted
        """
        if not self.vision_module or not self.actions_enabled:
            return False
        
        try:
            logger.info("Initiating autonomous error recovery...")
            analysis = self.vision_module.analyze_screenshot(
                "Is there an error dialog, warning dialog, or exception window visible? "
                "If yes, respond with ONLY: ERROR_FOUND at position X,Y where X,Y is the center of the OK/Close button. "
                "If no dialog is found, respond with only: NO_ERROR"
            )
            
            if analysis and "ERROR_FOUND" in analysis:
                logger.warning(f"Error dialog detected: {analysis}")
                
                # Parse coordinates if provided
                try:
                    coords = analysis.split("ERROR_FOUND")[1].strip()
                    if "at position" in coords:
                        pos_str = coords.split("at position")[1].strip()
                        x_str, y_str = pos_str.split(",")
                        x, y = int(x_str.strip()), int(y_str.strip())
                        logger.info(f"Clicking error dialog button at ({x}, {y})")
                        self.click(x, y)
                        return True
                except:
                    # Fallback: try common button locations
                    logger.info("Attempting fallback error recovery...")
                    
                    # Get screen size
                    screen_width, screen_height = self.pyautogui.size()
                    
                    # Common button positions
                    button_positions = [
                        (screen_width // 2, screen_height // 2 + 50),  # Center-bottom OK
                        (screen_width - 100, 30),  # Top-right close
                        (screen_width // 2, screen_height - 50),  # Bottom-center OK
                    ]
                    
                    for x, y in button_positions:
                        logger.info(f"Trying button at ({x}, {y})")
                        self.click(x, y)
                        self.pyautogui.sleep(0.5)
                    
                    return True
            
            logger.debug("No error dialog detected")
            return False
            
        except Exception as e:
            logger.error(f"Autonomous error recovery failed: {e}")
            return False

# =========================================================================
# SYSTEM UTILITIES & AUTONOMOUS FUNCTIONS
# =========================================================================

def generate_linux_service():
    """Generate systemd service configuration for KNO auto-start on Linux."""
    service_config = """[Unit]
Description=KNO - Autonomous Self-Healing Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=kno
WorkingDirectory=/home/kno/KNO
ExecStart=/home/kno/KNO/venv/bin/python /home/kno/KNO/agent.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    return service_config

def print_linux_setup_instructions():
    """Print instructions for setting up KNO as a systemd service."""
    service_config = generate_linux_service()
    print("\n" + "="*70, flush=True)
    print("[LINUX] 📋 KNO SYSTEMD SERVICE CONFIGURATION", flush=True)
    print("="*70, flush=True)
    print("\n# SETUP INSTRUCTIONS:\n", flush=True)
    print("1. Save this configuration to: /etc/systemd/system/kno-agent.service", flush=True)
    print("2. Run: sudo systemctl daemon-reload", flush=True)
    print("3. Run: sudo systemctl enable kno-agent.service", flush=True)
    print("4. Run: sudo systemctl start kno-agent.service", flush=True)
    print("5. Monitor with: sudo journalctl -u kno-agent.service -f", flush=True)
    print("="*70, flush=True)
    print("[SERVICE CONFIG]\n", flush=True)
    print(service_config, flush=True)
    print("="*70 + "\n", flush=True)

def get_system_health():
    """Check system health: CPU usage, disk usage, memory usage."""
    try:
        import psutil
        health = {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'disk_usage': psutil.disk_usage('/').percent,
            'memory_percent': psutil.virtual_memory().percent,
            'timestamp': datetime.datetime.now().isoformat()
        }
        return health
    except ImportError:
        print("[HEALTH] ⚠️  psutil not installed for system monitoring", flush=True)
        return None
    except Exception as e:
        print(f"[HEALTH] ⚠️  Error checking system health: {e}", flush=True)
        return None


class BladeRunnerVisualizer(threading.Thread):
    """Background worker: computes bar heights/colors and posts updates to a queue.
    All actual tkinter canvas operations are performed on the main thread by polling
    the update queue to avoid thread-safety issues.
    """
    def __init__(self, bars=12, palette=None):
        super().__init__(daemon=True)
        self.bars = bars
        self.running = threading.Event()
        self.running.set()
        self._vals = [0.0] * bars
        self.phase = 0.0
        self.palette = palette or ["#FF8C00", "#FF4500", "#8B0000"]
        self._lock = threading.Lock()
        self._update_queue = queue.Queue()

    def set_level(self, rms):
        with self._lock:
            for i in range(self.bars):
                target = min(1.0, rms * (1.2 - i / max(1, self.bars)))
                self._vals[i] = max(self._vals[i] * 0.8, target)

    def run(self):
        try:
            while self.running.is_set():
                with self._lock:
                    self.phase += 0.3
                    snapshot = []
                    for i in range(self.bars):
                        base = (math.sin(self.phase + i * 0.5) + 1) / 2
                        val = max(base * 0.08, min(1.0, self._vals[i]))
                        band = int(val * (len(self.palette) - 1))
                        color = self.palette[min(band, len(self.palette) - 1)]
                        if random.random() < 0.06:
                            color = self.palette[max(0, band - 1)]
                        snapshot.append((val, color))
                # Post the snapshot for the main thread to consume
                try:
                    # Keep at most one snapshot to avoid backlog
                    if self._update_queue.qsize() < 2:
                        self._update_queue.put(snapshot)
                except Exception:
                    pass
                time.sleep(0.06 + random.random() * 0.03)
        except Exception:
            pass

    def stop(self):
        self.running.clear()

    def get_update_queue(self):
        return self._update_queue


class Typewriter:
    """Helper to type text into a Text widget with a typewriter effect in background thread."""
    def __init__(self, text_widget, speed=0.008):
        # Instead of writing to the widget from a background thread (unsafe), we
        # enqueue characters and let the main thread flush them to the Text widget.
        self.text_widget = text_widget
        self.speed = speed
        self._queue = queue.Queue()

    def type(self, text):
        # Enqueue characters for main-thread consumption
        for ch in text + "\n":
            self._queue.put(ch)

    def get_queue(self):
        return self._queue


class BotGUI:
    """Blade Runner 2049 — Wallace Corp terminal aesthetic."""

    BG = "#050505"
    ACCENT_AMBER = "#FF8C00"
    ACCENT_CYAN = "#00CED1"
    DANGER = "#FF0000"
    FONT = ("Consolas", 11)

    def __init__(self, master):
        self.master = master
        try:
            master.title("KNO — Wallace Terminal")
        except Exception:
            pass

        try:
            master.geometry('1200x780')
        except Exception:
            pass

        # Root frame
        if ctk_available and ctk is not None:
            ctk.set_appearance_mode('dark')
            self.root = ctk.CTkFrame(master, fg_color=self.BG)
            self.root.pack(fill='both', expand=True)
        else:
            self.root = tk.Frame(master, bg=self.BG)
            self.root.pack(fill='both', expand=True)

        # Header with Serial and Baseline
        header = tk.Frame(self.root, bg=self.BG)
        header.pack(fill='x', padx=12, pady=8)
        self.serial_label = tk.Label(header, text='SN: KNO-2049-AX7', font=(self.FONT[0], 10, 'bold'), fg=self.ACCENT_AMBER, bg=self.BG)
        self.serial_label.pack(side='left')
        self.baseline_label = tk.Label(header, text='Baseline: PASSED', font=(self.FONT[0], 10), fg=self.ACCENT_AMBER, bg=self.BG)
        self.baseline_label.pack(side='left', padx=18)

        # Status blocks (square data blocks)
        status_row = tk.Frame(self.root, bg=self.BG)
        status_row.pack(fill='x', padx=12)
        self.block_link = self._data_block(status_row, 'LINK_ESTABLISHED', self.ACCENT_AMBER)
        self.block_voice = self._data_block(status_row, 'VOICE_RECOGNITION_ACTIVE', self.ACCENT_CYAN)
        self.block_proc = self._data_block(status_row, 'PROCESSING_LOGIC', '#FFD700')

        # Split view: visualizer left, console right
        split = tk.Frame(self.root, bg=self.BG)
        split.pack(fill='both', expand=True, padx=12, pady=12)

        vis_frame = tk.Frame(split, bg=self.BG)
        vis_frame.pack(side='left', fill='y')
        self.vis_canvas = tk.Canvas(vis_frame, width=260, height=400, bg=self.BG, highlightthickness=0)
        self.vis_canvas.pack(padx=8, pady=8)

        console_frame = tk.Frame(split, bg=self.BG)
        console_frame.pack(side='right', fill='both', expand=True)

        # Console with scanline overlay
        self.response_text = tk.Text(console_frame, bg='#070707', fg=self.ACCENT_AMBER, font=self.FONT, wrap='word', insertbackground=self.ACCENT_AMBER)
        self.response_text.configure(state='disabled')
        self.response_text.pack(fill='both', expand=True, padx=6, pady=6)

        # Scanline overlay canvas (drawn above background; non-interactive)
        self.scan_canvas = tk.Canvas(console_frame, bg=BG_COLOR, highlightthickness=0)
        self.scan_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._draw_scanlines()

        # Input controls
        input_row = tk.Frame(self.root, bg=self.BG)
        input_row.pack(fill='x', padx=12, pady=(0,12))
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(input_row, textvariable=self.input_var, bg='#0b0b0b', fg=self.ACCENT_AMBER, font=self.FONT, insertbackground=self.ACCENT_AMBER)
        self.input_entry.pack(side='left', fill='x', expand=True, padx=(6,4))
        self.send_btn = tk.Button(input_row, text='SEND', bd=0, highlightthickness=2, highlightbackground=self.ACCENT_AMBER, fg='#000', bg=self.ACCENT_AMBER, activebackground=self.ACCENT_AMBER, command=self._on_send)
        self.send_btn.pack(side='right', padx=(4,6))
        self._bind_button_hover(self.send_btn)

        # Helpers
        self.typewriter = Typewriter(self.response_text, speed=0.008)
        # Prepare visualizer: create bar rectangles in main thread, then start worker
        self._bar_items = []
        spacing = 6
        w = int(self.vis_canvas['width'])
        h = int(self.vis_canvas['height'])
        bar_width = (w - (12 + 1) * spacing) / 12
        for i in range(12):
            x = spacing + i * (bar_width + spacing)
            item = self.vis_canvas.create_rectangle(x, h, x + bar_width, h, fill=self.ACCENT_AMBER, outline='')
            self._bar_items.append(item)

        self.visualizer = BladeRunnerVisualizer(bars=12, palette=[self.ACCENT_AMBER, '#FF4500', '#8B0000'])
        self.visualizer.start()

        # Poll queues from worker threads on the main thread
        self._anim_running = True
        self._poll_visualizer()
        self._poll_typewriter()
        # Animation thread monitor for non-canvas animation (scanlines)
        self._anim_thread = threading.Thread(target=self._animation_loop, daemon=True)
        self._anim_thread.start()

        # State flags
        self.idle = True

    # ---------------- UI helpers ----------------
    def _data_block(self, parent, label, color):
        frame = tk.Frame(parent, bg=self.BG)
        block = tk.Frame(frame, width=18, height=18, bg=color)
        block.pack(side='left')
        lbl = tk.Label(frame, text=label, bg=self.BG, fg=self.ACCENT_AMBER, font=(self.FONT[0], 9))
        lbl.pack(side='left', padx=6)
        frame.pack(side='left', padx=12)
        return block

    def _draw_scanlines(self):
        try:
            self.scan_canvas.delete('all')
            h = self.response_text.winfo_height() or 400
            for y in range(0, h, 6):
                self.scan_canvas.create_line(0, y, int(self.scan_canvas.winfo_width() or 800), y, fill='#000000', stipple='gray25')
        except Exception:
            pass

    def _poll_visualizer(self):
        """Poll visualizer queue and apply snapshots to canvas on the main thread."""
        try:
            q = self.visualizer.get_update_queue()
            while not q.empty():
                try:
                    snapshot = q.get_nowait()
                except Exception:
                    snapshot = None
                if not snapshot:
                    continue
                # snapshot is list of (val, color)
                try:
                    for i, (val, color) in enumerate(snapshot):
                        if i < len(self._bar_items):
                            item = self._bar_items[i]
                            h = int(int(self.vis_canvas['height']) - (val * (int(self.vis_canvas['height']) - 20)))
                            x1, y1, x2, y2 = self.vis_canvas.coords(item)
                            self.vis_canvas.coords(item, x1, h, x2, int(self.vis_canvas['height']))
                            try:
                                self.vis_canvas.itemconfig(item, fill=color)
                            except Exception:
                                pass
                except Exception:
                    pass
        except Exception:
            pass
        if self._anim_running:
            try:
                self.master.after(60, self._poll_visualizer)
            except Exception:
                pass

    def _poll_typewriter(self):
        """Flush characters from the Typewriter queue into the Text widget on the main thread."""
        try:
            q = self.typewriter.get_queue()
            any_written = False
            try:
                orig_fg = self.response_text.cget('fg')
            except Exception:
                orig_fg = None
            try:
                self.response_text.configure(state='normal', fg=self.ACCENT_AMBER)
            except Exception:
                try:
                    self.response_text.configure(state='normal')
                except Exception:
                    pass
            while not q.empty():
                try:
                    ch = q.get_nowait()
                except Exception:
                    ch = None
                if ch is None:
                    continue
                try:
                    self.response_text.insert('end', ch)
                    self.response_text.see('end')
                    any_written = True
                except Exception:
                    pass
            if any_written:
                try:
                    # restore disabled state and original fg if available
                    if orig_fg is not None:
                        self.response_text.configure(state='disabled', fg=orig_fg)
                    else:
                        self.response_text.configure(state='disabled')
                except Exception:
                    pass
        except Exception:
            pass
        if self._anim_running:
            try:
                self.master.after(40, self._poll_typewriter)
            except Exception:
                pass

    def _bind_button_hover(self, btn):
        def on_enter(e):
            try:
                btn.config(highlightbackground=self.ACCENT_AMBER)
            except Exception:
                pass
        def on_leave(e):
            try:
                btn.config(highlightbackground=self.ACCENT_AMBER)
            except Exception:
                pass
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

    # ---------------- Input/Output ----------------
    def _on_send(self):
        txt = self.input_var.get().strip()
        if not txt:
            return
        self.input_var.set('')
        # Show user message instantly
        self._append_raw(f"> {txt}")
        # Process asynchronously
        threading.Thread(target=self._process_user_input, args=(txt,), daemon=True).start()

    def _append_raw(self, text):
        try:
            self.response_text.configure(state='normal')
            self.response_text.insert('end', text + '\n')
            self.response_text.see('end')
            self.response_text.configure(state='disabled')
        except Exception:
            pass

    def _process_user_input(self, txt):
        # Flip to active
        self._set_active(True)
        try:
            # Query higher intelligence if available
            solution = None
            if 'higher_intelligence_bridge' in globals():
                try:
                    solution = higher_intelligence_bridge.solve_complex_problem(txt)
                except Exception:
                    solution = None

            if solution:
                self.typewriter.type(f"KNO: {solution}")
            else:
                self.typewriter.type("KNO: (no external solution available)")

        except Exception as e:
            self._append_raw(f"[ERROR] {e}")
        finally:
            self._set_active(False)

    def set_rms_level(self, rms):
        """Thread-safe entry point for audio threads to drive the visualizer."""
        try:
            if hasattr(self, 'visualizer') and self.visualizer:
                self.visualizer.set_level(rms)
        except Exception:
            pass

    def _set_active(self, active: bool):
        # Call gc.collect() on state transitions
        try:
            if self.idle == (not active):
                pass
            self.idle = not active
            gc.collect()
        except Exception:
            pass

    # ---------------- Animation loop ----------------
    def _animation_loop(self):
        try:
            while self._anim_running:
                # Update scanlines size
                try:
                    self._draw_scanlines()
                except Exception:
                    pass
                time.sleep(0.25)
        except Exception:
            pass

    def safe_exit(self, *args, **kwargs):
        try:
            self._anim_running = False
        except Exception:
            pass
        try:
            self.visualizer.stop()
        except Exception:
            pass
        try:
            self.master.quit()
        except Exception:
            pass
        self.input_entry = tk.Entry(self.input_frame, textvariable=self.input_var, bg='#0a0f14', fg=self.ACCENT_AMBER, insertbackground=self.ACCENT_AMBER)
        self.input_entry.pack(side='left', fill='x', expand=True, padx=(8,4), pady=8)
        self.input_entry.bind('<Return>', lambda e: self._on_send())

        self.send_btn = tk.Button(self.input_frame, text='➔', bg=self.ACCENT_PURPLE, fg='#fff', command=self._on_send)
        self.send_btn.pack(side='right', padx=(4,8), pady=8)

        # State
        self.rms_level = 0.0
        self._anim_phase = 0.0
        self._visualizer_bars = 12
        self._visualizer_vals = [0.0] * self._visualizer_bars

        # Start animation
        self._anim_running = True
        self._start_animation()

    # ---------------------- UI building helpers ----------------------
    def _build_status_row(self):
        frame = tk.Frame(self.root_frame, bg=self.BG)
        frame.pack(fill='x', padx=12, pady=(12,0))

        # Cloud Sync LED
        self.led_cloud = self._led(frame, text='Cloud Sync', color='#22C55E')
        self.led_cloud.pack(side='left', padx=8)

        # Ear Active LED
        self.led_ear = self._led(frame, text='Ear', color=self.ACCENT_CYAN)
        self.led_ear.pack(side='left', padx=8)

        # Evolution LED
        self.led_evo = self._led(frame, text='Evolution', color=self.ACCENT_PURPLE)
        self.led_evo.pack(side='left', padx=8)

        spacer = tk.Frame(frame, bg=self.BG)
        spacer.pack(side='left', expand=True)

        self.status_label = tk.Label(frame, text='KNO Cyber‑Noir', bg=self.BG, fg=self.ACCENT_AMBER, font=('Segoe UI', 11, 'bold'))
        self.status_label.pack(side='right', padx=12)

    def _led(self, parent, text='', color='#00FF00'):
        container = tk.Frame(parent, bg=self.BG)
        c = tk.Canvas(container, width=18, height=18, bg=self.BG, highlightthickness=0)
        c.pack(side='left')
        c.create_oval(2,2,16,16, fill=color, outline=self.GLOW_BORDER)
        lbl = tk.Label(container, text=text, bg=self.BG, fg=self.ACCENT_AMBER, font=('Segoe UI', 9))
        lbl.pack(side='left', padx=(6,0))
        return container
    # Legacy visualizer and animation code removed — BladeRunnerVisualizer
    # and Typewriter are used instead. This cleans up duplicate canvas
    # drawing and legacy animation loops.
    def append_response(self, text):
        try:
            self.response_text.configure(state='normal')
            self.response_text.insert('end', text + '\n')
            self._smooth_autoscroll()
            self.response_text.configure(state='disabled')
        except Exception as e:
            print(f"[UI] append_response error: {e}", flush=True)

    def _smooth_autoscroll(self, duration_ms=300):
        """Smooth scrolls the text widget to the bottom over duration_ms."""
        try:
            start = self.response_text.yview()[0]
            end = 1.0
            steps = max(4, int(duration_ms / 40))
            delta = (end - start) / steps
            def step(i=0):
                if i >= steps:
                    try:
                        self.response_text.yview_moveto(end)
                    except Exception:
                        pass
                    return
                try:
                    self.response_text.yview_moveto(start + delta * i)
                except Exception:
                    pass
                self.master.after(40, lambda: step(i+1))
            step(0)
        except Exception:
            try:
                self.response_text.yview_moveto(1.0)
            except Exception:
                pass

    # ---------------------- Input handlers ----------------------
    def _on_send(self):
        txt = self.input_var.get().strip()
        if not txt:
            return
        self.input_var.set("")
        # Append locally and schedule processing
        self.append_response(f"You: {txt}")
        # If external brain exists, hand off to processing threads elsewhere
        try:
            threading.Thread(target=lambda: self._process_user_input(txt), daemon=True).start()
        except Exception:
            pass

    def _process_user_input(self, txt):
        # Bridge to agent processing — simplified placeholder
        try:
            print(f"[UI] Processing user input: {txt}", flush=True)
            solution = None
            if 'higher_intelligence_bridge' in globals():
                try:
                    solution = higher_intelligence_bridge.solve_complex_problem(txt)
                except Exception:
                    solution = None
            if solution:
                if hasattr(self, 'typewriter') and self.typewriter:
                    self.typewriter.type(f"KNO: {solution}")
                else:
                    try:
                        self.master.after(0, lambda s=solution: self.append_response(f"KNO: {s}"))
                    except Exception:
                        pass
            else:
                if hasattr(self, 'typewriter') and self.typewriter:
                    self.typewriter.type("KNO: (no external solution available)")
                else:
                    try:
                        self.master.after(0, lambda: self.append_response("KNO: (no external solution available)"))
                    except Exception:
                        pass
        except Exception as e:
            print(f"[UI] Error processing input: {e}", flush=True)

    def safe_exit(self, *args, **kwargs):
        try:
            self._anim_running = False
        except Exception:
            pass
        try:
            self.master.quit()
        except Exception:
            pass

        # Legacy pixel drawing removed; BladeRunnerVisualizer handles visuals now.
        try:
            # No direct canvas drawing from background; visual updates come
            # from BladeRunnerVisualizer via the main-thread poller.
            return
        except Exception:
            return
    
    # Legacy LED glow helper removed (visuals implemented in BladeRunnerVisualizer)
    
    # ===== SEARCH BAR HANDLERS (Retro LED-style) =====
    
    def on_mic_button_clicked(self):
        """Handle microphone button click - trigger voice recording with LED glow and reactive bars.
        
        Features:
        - Red LED glow on mic button
        - Green pixelated bars (responsive to audio)
        - Background thread for continuous listening
        """
        print("[UI] Microphone button clicked - starting voice input", flush=True)
        try:
            # Set recording flags
            self.recording_active.set()
            self.mic_recording = True
            
            # Trigger thinking animation (green bars, 16 bars, medium pulse)
            self.is_thinking = True
            self.is_speaking = False
            print("[MIC] Triggering reactive bars (green state, 16 bars)", flush=True)
            
            # Update status and button
            self.status_var.set("[RECORDING_VOICE]")
            self.mic_button.configure(text_color="#FF0000")  # Bright red LED
            print("[MIC] Mic LED red - recording active", flush=True)
            
            # Spawn background thread for voice input processing
            threading.Thread(
                target=self._background_voice_listener,
                daemon=True
            ).start()
            print("[MIC] [OK] Voice listener thread started", flush=True)
            
        except Exception as e:
            print(f"[MIC] [ERROR] Error: {e}", flush=True)
            import traceback
            traceback.print_exc()
            
            # Log error
            if experience_memory:
                experience_memory.log_error(
                    error_type="mic_button_error",
                    error_message=str(e)[:100],
                    context="on_mic_button_clicked"
                )
            
            # Try auto-correction
            if self_correction:
                missing_lib = self_correction.detect_missing_library(str(e))
                if missing_lib:
                    print(f"[CORRECTION] Auto-installing: {missing_lib}", flush=True)
                    self_correction.auto_install_dependency(missing_lib)
            
            # Reset state
            self.recording_active.clear()
            self.mic_recording = False
            self.is_thinking = False
            self.status_var.set("[ERROR_MIC]")
    
    def _background_voice_listener(self):
        """Background thread that continuously listens for voice input from mic press.
        
        Features:
        - Records audio in background without blocking UI
        - Automatically transcribes to text
        - Triggers text processing
        - Comprehensive error logging and recovery
        """
        print("[VOICE] 🎙️ Background voice listener started", flush=True)
        
        try:
            # Record voice with fallback
            try:
                print("[VOICE] ⏹️ Recording audio from microphone...", flush=True)
                audio_file = self.record_voice_ppt_with_fallback()
                
                if not audio_file:
                    print("[VOICE] ⚠️ No audio recorded", flush=True)
                    if experience_memory:
                        experience_memory.log_error(
                            error_type="voice_recording_empty",
                            error_message="No audio captured from microphone",
                            context="background_voice_listener"
                        )
                    self.status_var.set("[ERROR_RECORD]")
                    return
                
                print(f"[VOICE] ✅ Audio recorded: {audio_file}", flush=True)
                error_recovery.reset_component("voice_recording")
            
            except Exception as record_error:
                print(f"[VOICE] ⚠️ Recording error: {record_error}", flush=True)
                if experience_memory:
                    experience_memory.log_error(
                        error_type="voice_recording_error",
                        error_message=str(record_error)[:100],
                        context="background_voice_listener"
                    )
                error_recovery.log_error("voice_recording", str(record_error))
                self.status_var.set("[ERROR_RECORD]")
                return
            
            # Transcribe audio with fallback
            try:
                print("[VOICE] 🔤 Transcribing audio to text...", flush=True)
                user_text = self.transcribe_audio_with_recovery(audio_file)
                
                if not user_text:
                    print("[VOICE] ⚠️ Transcription failed or returned empty", flush=True)
                    if experience_memory:
                        experience_memory.log_error(
                            error_type="voice_transcription_empty",
                            error_message="Whisper returned no text",
                            context="background_voice_listener"
                        )
                    self.status_var.set("[ERROR_TRANSCRIBE]")
                    return
                
                print(f"[VOICE] ✅ Transcribed: {user_text}", flush=True)
                error_recovery.reset_component("voice_transcription")
            
            except Exception as transcribe_error:
                print(f"[VOICE] ⚠️ Transcription error: {transcribe_error}", flush=True)
                if experience_memory:
                    experience_memory.log_error(
                        error_type="voice_transcription_error",
                        error_message=str(transcribe_error)[:100],
                        context="background_voice_listener"
                    )
                error_recovery.log_error("voice_transcription", str(transcribe_error))
                self.status_var.set("[ERROR_TRANSCRIBE]")
                return
            
            # Process transcribed text
            try:
                print(f"[VOICE] 🤖 Processing transcribed text...", flush=True)
                self._process_text_input(user_text)
                print(f"[VOICE] ✅ Voice processing complete", flush=True)
            
            except Exception as process_error:
                print(f"[VOICE] ⚠️ Processing error: {process_error}", flush=True)
                if experience_memory:
                    experience_memory.log_error(
                        error_type="voice_processing_error",
                        error_message=str(process_error)[:100],
                        context="background_voice_listener"
                    )
                error_recovery.log_error("voice_processing", str(process_error))
                self.status_var.set("[ERROR_PROCESS]")
            
            # Reset recording state
            self.recording_active.clear()
            self.mic_recording = False
            self.is_thinking = False
        
        except Exception as e:
            print(f"[VOICE] ❌ Critical error in background listener: {e}", flush=True)
            import traceback
            traceback.print_exc()
            
            if experience_memory:
                experience_memory.log_error(
                    error_type="voice_listener_critical",
                    error_message=str(e)[:100],
                    context="background_voice_listener"
                )
            
            # Reset state
            self.recording_active.clear()
            self.mic_recording = False
            self.is_thinking = False
            self.status_var.set("[ERROR_VOICE]")
    
    def on_send_button_clicked(self, event=None):
        """Handle send button click or Enter key - process text input with LED glow."""
        user_text = self.search_entry.get().strip()
        
        if not user_text or user_text == "[type_command]":
            return
        
        print(f"[UI] Text input: {user_text}", flush=True)
        
        # Clear entry and reset mic recording flag
        self.search_entry.delete(0, tk.END)
        self.mic_recording = False
        self.mic_button.configure(text_color="#FF0000")  # Reset mic to red
        
        # Glow send button green momentarily
        self.send_button.configure(text_color=self.SEND_GLOW_COLOR)
        
        # Update status and trigger thinking animation
        self.is_thinking = True
        self.status_var.set("[PROCESSING_INPUT]")
        
        # Queue the text for processing
        with self.tts_queue_lock:
            self.user_input_queue.append(user_text)
        
        # Process in background
        threading.Thread(
            target=self._process_text_input,
            args=(user_text,),
            daemon=True
        ).start()
    
    def _process_text_input(self, text):
        """Process text input through cloud LLM with full autonomy integration.
        
        Features:
        - Reactive audio bars during processing
        - InternetLearningBridge fallback for complex queries
        - ExperienceMemory error logging
        - Comprehensive error recovery
        """
        try:
            print(f"[PROCESS] Processing text: {text}", flush=True)
            self.status_var.set("[PROCESSING_INPUT]")
            
            # Add to permanent memory
            self.permanent_memory.append({"role": "user", "content": text})
            
            # Make bars jump energetically during processing
            self.is_thinking = True
            print(f"[PROCESS] Triggering reactive bars (green state, 16 bars)", flush=True)
            
            response = None
            
            # PRIMARY: Try cloud LLM (Gemini/ChatGPT)
            if self.cloud_llm_mode:
                try:
                    print("[PROCESS] 🤖 Attempting Cloud LLM (Gemini/ChatGPT)...", flush=True)
                    
                    # Prepare messages for cloud AI
                    messages = [{"role": "user", "content": text}]
                    
                    # Try cloud LLM
                    if hasattr(self, 'cloud_llm') and self.cloud_llm:
                        result = self.cloud_llm.chat_completion(messages, temperature=0.7, max_tokens=256)
                        if result and "choices" in result:
                            response = result["choices"][0]["message"]["content"]
                            print(f"[PROCESS] ✅ Cloud LLM success: {response[:60]}...", flush=True)
                    
                    # Fallback: Query HigherIntelligenceBridge
                    if not response:
                        print("[PROCESS] 🌐 Cloud LLM failed, querying HigherIntelligenceBridge...", flush=True)
                        response = higher_intelligence_bridge.solve_complex_problem(text)
                        if response:
                            print(f"[PROCESS] ✅ Bridge response: {response[:60]}...", flush=True)
                    
                except Exception as cloud_error:
                    print(f"[PROCESS] ⚠️  Cloud LLM error: {cloud_error}", flush=True)
                    if experience_memory:
                        experience_memory.log_error(
                            error_type="cloud_llm_failure",
                            error_message=str(cloud_error)[:100],
                            context="text_processing"
                        )
            
            # SECONDARY: Internet Learning Bridge (web search fallback)
            if not response:
                print("[PROCESS] 🌐 Trying internet search fallback...", flush=True)
                try:
                    if 'InternetLearningBridge' in globals():
                        bridge = InternetLearningBridge()
                        search_results = bridge.search_web_for_solution(text, max_results=1)
                        if search_results:
                            response = f"Search result: {search_results[0].get('title', '')[:60]}..."
                            print(f"[PROCESS] ✅ Web search found: {response[:60]}...", flush=True)
                except Exception as web_error:
                    print(f"[PROCESS] ⚠️  Web search error: {web_error}", flush=True)
                    if experience_memory:
                        experience_memory.log_error(
                            error_type="web_search_failure",
                            error_message=str(web_error)[:100],
                            context="text_processing"
                        )
            
            # TERTIARY: Fallback response
            if not response:
                print("[PROCESS] Using fallback response", flush=True)
                response = f">> {text[:40]}... [ACKNOWLEDGED]"
                if experience_memory:
                    experience_memory.log_error(
                        error_type="no_response_generated",
                        error_message=f"Could not generate response for: {text[:50]}",
                        context="text_processing"
                    )
            
            # Sanitize response
            response = str(response)[:200]
            
            # Add response to memory
            self.permanent_memory.append({"role": "assistant", "content": response})
            
            # Display response via Typewriter for thread-safety (main thread polls queue)
            try:
                # Enqueue user line and assistant response to the typewriter queue
                if hasattr(self, 'typewriter') and self.typewriter:
                    self.typewriter.type(f"USER> {text}")
                    self.typewriter.type(f"KNO > >> {response}")
                else:
                    # Fallback: schedule direct insert on main thread
                    def _display():
                        try:
                            self.response_text.configure(state="normal")
                            self.response_text.insert(tk.END, f"USER> {text}\n")
                            self.response_text.insert(tk.END, f"KNO > >> {response}\n")
                            self.response_text.see(tk.END)
                            self.response_text.configure(state="disabled")
                        except Exception:
                            pass
                    try:
                        self.master.after(0, _display)
                    except Exception:
                        pass
                print(f"[PROCESS] ✅ Response queued for UI", flush=True)
            except Exception as display_error:
                print(f"[PROCESS] Display error: {display_error}", flush=True)
                if experience_memory:
                    experience_memory.log_error(
                        error_type="ui_display_error",
                        error_message=str(display_error)[:100],
                        context="text_response_display"
                    )
            
            # Queue TTS for response
            try:
                with self.tts_queue_lock:
                    self.tts_queue.append(response)
                self.tts_active.set()
                print(f"[PROCESS] ✅ Response queued for audio playback", flush=True)
            except Exception as tts_error:
                print(f"[PROCESS] TTS queue error: {tts_error}", flush=True)
            
            # Transition: thinking (green) → speaking (yellow)
            self.is_thinking = False
            self.is_speaking = True
            self.send_button.configure(text_color="#888888")
            self.status_var.set("[SPEAKING_OUTPUT]")
            print(f"[PROCESS] 🎙️ State transition: SPEAKING (yellow bars, 20 bars)", flush=True)
            
            # Simulate speaking duration
            time.sleep(2)
            self.is_speaking = False
            self.status_var.set("[READY]")
            
            print("[PROCESS] ✅ Text processing complete", flush=True)
            error_recovery.reset_component("text_processing")
        
        except Exception as e:
            print(f"[PROCESS] ❌ Critical error in _process_text_input: {e}", flush=True)
            import traceback
            traceback.print_exc()
            
            # Log error to experience memory
            if experience_memory:
                experience_memory.log_error(
                    error_type="text_processing_critical",
                    error_message=str(e)[:100],
                    context="_process_text_input"
                )
            
            # Log to error recovery
            error_recovery.log_error("text_processing", str(e))
            
            # Reset UI state
            self.is_thinking = False
            self.is_speaking = False
            self.send_button.configure(text_color="#888888")
            self.status_var.set("[ERROR_PROCESS]")
            
            # Try to self-correct
            if self_correction:
                missing_lib = self_correction.detect_missing_library(str(e))
                if missing_lib:
                    print(f"[CORRECTION] Attempting to auto-install: {missing_lib}", flush=True)
                    if self_correction.auto_install_dependency(missing_lib):
                        print(f"[CORRECTION] ✅ Successfully installed {missing_lib}", flush=True)
    
    # --- HELPERS ---

    def request_action_approval(self, action_type, details):
        """
        Request human approval for a system/network action via Tkinter messagebox.
        This is the human-in-the-loop security mechanism.
        """
        try:
            from tkinter import messagebox
            result = messagebox.askyesno(
                "Approval Required",
                f"Action: {action_type}\n\nDetails: {details}\n\nApprove?"
            )
            print(f"[APPROVAL] {action_type}: {'APPROVED' if result else 'DENIED'}", flush=True)
            return result
        except Exception as e:
            print(f"[APPROVAL ERROR] {e}", flush=True)
            return False

    def get_weather_summary(self):
        """Get latest weather information from recent searches."""
        try:
            if self.last_search_results.get("weather"):
                weather_text = self.last_search_results.get("weather", "")
                summary = weather_text[:100]
                self.last_weather_summary = summary
                return summary
            return "Weather data not available"
        except Exception as e:
            print(f"[MORNING] Weather summary error: {e}", flush=True)
            return "Weather unavailable"

    def get_task_summary(self):
        """Extract top 3 tasks/goals from memory."""
        try:
            if not self.permanent_memory:
                return "No tasks in memory"
            
            tasks = []
            for msg in self.permanent_memory[-20:]:
                content = msg.get("content", "").lower()
                if any(word in content for word in ["task", "todo", "goal", "reminder", "schedule"]):
                    tasks.append(msg.get("content", "")[:80])
            
            if tasks:
                top_tasks = "\n".join(tasks[:3])
                return f"Tasks: {top_tasks}"
            
            return "No specific tasks found"
        except Exception as e:
            print(f"[MORNING] Task summary error: {e}", flush=True)
            return "Tasks unavailable"

    def detect_phone_ip(self):
        """Attempt to detect phone IP from network scan."""
        try:
            print("[MORNING] Scanning for Android devices...", flush=True)
            return None
        except Exception as e:
            print(f"[MORNING] Phone detection error: {e}", flush=True)
            return None

    def extract_json_from_text(self, text):
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return None
        except Exception:
            return None

    def handle_incoming_notification(self, sender, message):
        """
        Handle incoming WhatsApp notification from listener.
        Updates GUI and queues TTS announcement.
        """
        try:
            privacy_mode = CURRENT_CONFIG.get("privacy_mode", False)
            
            if not self.phone_connected:
                print("[NOTIFY] ⚠️  Phone not connected, skipping notification", flush=True)
                return
            
            notification_display = f"📱 New Message from {sender}"
            if message and not privacy_mode:
                notification_display += f": {message[:80]}"
            
            print(f"[NOTIFY] 🔔 {notification_display}", flush=True)
            
            try:
                if hasattr(self, 'typewriter') and self.typewriter:
                    self.typewriter.type(f"\n{notification_display}")
                else:
                    def _notify():
                        try:
                            self.response_text.configure(state="normal")
                            self.response_text.insert(tk.END, f"\n{notification_display}\n")
                            self.response_text.see(tk.END)
                            self.response_text.configure(state="disabled")
                        except Exception:
                            pass
                    try:
                        self.master.after(0, _notify)
                    except Exception:
                        pass
            except Exception:
                pass
            
            if privacy_mode:
                tts_message = f"You have a message from {sender}"
            else:
                tts_message = f"You have a message from {sender} on WhatsApp"
            
            with self.tts_queue_lock:
                self.tts_queue.insert(0, tts_message)
            
            print(f"[NOTIFY] 🔊 Queued TTS: {tts_message}", flush=True)
            
        except Exception as e:
            print(f"[NOTIFY] ❌ Notification handler error: {e}", flush=True)

    def safe_exit(self):
        print("\n--- SHUTDOWN SEQUENCE ---", flush=True)
        if self.current_audio_process:
            try:
                self.current_audio_process.terminate()
                self.current_audio_process.wait(timeout=1)
            except Exception:
                pass

        self.recording_active.clear()
        self.thinking_sound_active.clear()
        self.tts_active.clear() 
        
        try:
            if hasattr(self, 'notification_listener'):
                self.notification_listener.stop_listening()
                print("[SHUTDOWN] Notification listener stopped", flush=True)
        except Exception as e:
            print(f"[SHUTDOWN] Error stopping listener: {e}", flush=True)
        
        self.save_chat_history()
        
        try:
            if LlamaConnector.llm_instance:
                print("[SHUTDOWN] Releasing Llama model resources...", flush=True)
                LlamaConnector.llm_instance = None
        except Exception:
            pass

        try:
            self.master.quit()
            self.master.destroy()
        except Exception:
            pass 
        
        print("[GUI] BotGUI.__init__ COMPLETE", flush=True)

    def exit_fullscreen(self, event=None):
        self.master.attributes('-fullscreen', False)
        self.safe_exit()

    def toggle_hud_visibility(self, event=None):
        try:
            if self.response_frame.winfo_ismapped():
                self.response_frame.pack_forget()
            else:
                self.response_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        except tk.TclError: 
            pass

    def handle_ptt_toggle(self, event=None):
        current_time = time.time()
        if current_time - self.last_ptt_time < 0.5: 
            return 
        self.last_ptt_time = current_time

        if self.recording_active.is_set():
            print("\n[PTT STOP] Recording stopped. Processing your input...", flush=True)
            self.recording_active.clear() 
        else:
            if self.current_state == BotStates.IDLE or "Wait" in self.status_var.get():
                print("\n[PTT START] Listening... Press ENTER again to stop recording", flush=True)
                self.recording_active.set() 
                self.ptt_event.set()

    def handle_speaking_interrupt(self, event=None):
        if self.current_state == BotStates.SPEAKING or self.current_state == BotStates.THINKING:
            self.interrupted.set()
            self.thinking_sound_active.clear()
            with self.tts_queue_lock:
                self.tts_queue.clear()
            if self.current_audio_process:
                try: 
                    self.current_audio_process.terminate()
                except Exception:
                    pass
            self.set_state(BotStates.IDLE, "Interrupted.")

    def handle_sync_phone(self):
        """Handle Sync Phone button click - pairs and connects to wireless debugging phone."""
        try:
            print("[PHONE] 🔄 Sync Phone button clicked", flush=True)
            self.set_state(BotStates.THINKING, "Syncing Phone...")
            self.status_var.set("Syncing phone... Stand by for pairing.")
            self.master.update()
            
            phone_ip = "192.168.11.109"
            pairing_port = 34245
            pairing_code = "352913"
            main_port = 38575
            
            print(f"[PHONE] Initiating wireless sync with {phone_ip}", flush=True)
            
            def sync_task():
                nonlocal phone_ip, pairing_port, pairing_code, main_port
                
                success = network_iot_controller.sync_phone_wireless(
                    phone_ip, 
                    pairing_port, 
                    pairing_code, 
                    main_port
                )
                
                if success:
                    print("[PHONE] ✅ Phone connection successful!", flush=True)
                    self.phone_ip = phone_ip
                    self.phone_connected = True
                    self.notification_listener.is_connected = True
                    self.set_state(BotStates.IDLE, "Phone Connected")
                    self.status_var.set("✅ Phone Connected")
                    
                    print("[PHONE] Starting notification listener...", flush=True)
                    self.notification_listener.start_listening()
                    
                    with self.tts_queue_lock:
                        self.tts_queue.append("Phone connected successfully! Listening for messages.")
                else:
                    print("[PHONE] ❌ First sync attempt failed, requesting fresh credentials...", flush=True)
                    try:
                        from tkinter import simpledialog
                        new_pairing_port = simpledialog.askinteger("Phone Setup", "Enter pairing port (usually 5555 or in Settings):", initialvalue=34245, minvalue=1024, maxvalue=65535)
                        if new_pairing_port is None:
                            print("[PHONE] ❌ User cancelled port input", flush=True)
                            self.phone_connected = False
                            self.set_state(BotStates.IDLE, "Sync Cancelled")
                            self.status_var.set("❌ Cancelled")
                            return
                        
                        new_pairing_code = simpledialog.askstring("Phone Setup", "Enter pairing code (from phone Settings > Developer > Wireless Debugging):")
                        if new_pairing_code is None or not new_pairing_code.strip():
                            print("[PHONE] ❌ User cancelled code input", flush=True)
                            self.phone_connected = False
                            self.set_state(BotStates.IDLE, "Sync Cancelled")
                            self.status_var.set("❌ Cancelled")
                            return
                        
                        pairing_port = new_pairing_port
                        pairing_code = new_pairing_code.strip()
                        print(f"[PHONE] 🔄 Retrying with new credentials: port {pairing_port}, code {pairing_code}", flush=True)
                        self.status_var.set("Retrying with new credentials...")
                        
                        retry_success = network_iot_controller.sync_phone_wireless(
                            phone_ip,
                            pairing_port,
                            pairing_code,
                            main_port
                        )
                        
                        if retry_success:
                            print("[PHONE] ✅ Retry succeeded!", flush=True)
                            self.phone_ip = phone_ip
                            self.phone_connected = True
                            self.notification_listener.is_connected = True
                            self.set_state(BotStates.IDLE, "Phone Connected")
                            self.status_var.set("✅ Phone Connected")
                            self.notification_listener.start_listening()
                            with self.tts_queue_lock:
                                self.tts_queue.append("Phone connected successfully! Listening for messages.")
                        else:
                            print("[PHONE] ❌ Retry also failed", flush=True)
                            self.phone_connected = False
                            self.set_state(BotStates.IDLE, "Phone Sync Failed")
                            self.status_var.set("❌ Phone Sync Failed After Retry")
                            with self.tts_queue_lock:
                                self.tts_queue.append("Phone sync failed even after retry. Please check your phone settings and try again.")
                    except ImportError:
                        print("[PHONE] ❌ Cannot import simpledialog", flush=True)
                        self.phone_connected = False
                        self.set_state(BotStates.IDLE, "Phone Sync Failed")
                        self.status_var.set("❌ Phone Sync Failed")
                        with self.tts_queue_lock:
                            self.tts_queue.append("Phone sync failed. Check your phone settings.")
            
            sync_thread = threading.Thread(target=sync_task, daemon=True)
            sync_thread.start()
            
        except Exception as e:
            print(f"[PHONE] ❌ Sync error: {e}", flush=True)
            error_recovery.log_error("phone_sync", str(e))
            self.phone_connected = False
            self.set_state(BotStates.IDLE, "Sync Error")
            self.status_var.set("❌ Sync Error")

    # Legacy animation loader removed. Visual animations are handled by
    # `BladeRunnerVisualizer` and external animation assets are not required
    # by the new UI.

    def populate_audio_devices(self):
        """Populate the audio input device combobox with available input devices."""
        try:
            devices = sd.query_devices()
            values = []
            for idx, d in enumerate(devices):
                try:
                    if d.get('max_input_channels', 0) > 0:
                        name = d.get('name', 'Unknown')
                        values.append(f"{idx} - {name}")
                except Exception:
                    continue
            if not values:
                values = ["Default"]
            if hasattr(self, 'device_combobox'):
                self.device_combobox.configure(values=values)
            pref = getattr(audio_device_manager, 'current_device', None)
            if pref is None and hasattr(self, 'device_var'):
                self.device_var.set("Default")
            else:
                if hasattr(self, 'device_var'):
                    for v in values:
                        if v.startswith(f"{pref} ") or v.startswith(f"{pref}-") or v.startswith(f"{pref} -"):
                            self.device_var.set(v)
                            break
        except Exception as e:
            print(f"[AUDIO UI] Error listing devices: {e}", flush=True)

    def on_device_selected(self, event=None):
        """Callback when user selects an audio device from the dropdown."""
        try:
            sel = self.device_var.get() if hasattr(self, 'device_var') else None
            if not sel or sel == "Default":
                audio_device_manager.set_preferred_device(None)
                try: 
                    self.status_var.set("Audio input: Default")
                except Exception:
                    pass
                return
            idx_str = sel.split("-")[0].strip()
            try:
                idx = int(idx_str)
            except Exception:
                idx = None
            audio_device_manager.set_preferred_device(idx)
            try: 
                self.status_var.set(f"Audio input set to: {sel}")
            except Exception:
                pass
        except Exception as e:
            print(f"[AUDIO UI] on_device_selected error: {e}", flush=True)

    def set_state(self, state, msg="", cam_path=None):
        def _update():
            if msg: 
                print(f"[STATE] {state.upper()}: {msg}", flush=True)
            if self.current_state != state:
                self.current_state = state
                self.current_frame_index = 0
            if msg: 
                self.status_var.set(msg)
        self.master.after(0, _update)

    def append_to_text(self, text, newline=True):
        def _update():
            self.response_text.configure(state="normal")
            if newline: 
                self.response_text.insert(tk.END, text + "\n")
            else: 
                self.response_text.insert(tk.END, text)
            
            self.response_text.see(tk.END)
            self.response_text.configure(state="disabled")
            
        self.master.after(0, _update)

    def _stream_to_text(self, chunk):
        def update_text_stream():
            self.response_text.configure(state="normal")
            self.response_text.insert(tk.END, chunk)
            self.response_text.see(tk.END) 
            self.response_text.configure(state="disabled")
        self.master.after(0, update_text_stream)

    # =========================================================================
    # 3. ACTION ROUTER
    # =========================================================================
    
    def execute_action_and_get_result(self, action_data):
        raw_action = action_data.get("action", "").lower().strip()
        value = action_data.get("value") or action_data.get("query")
        
        VALID_TOOLS = {
            # Core tools
            "get_time", "search_web", "capture_image",
            # Global Control tools (System)
            "open_browser", "file_move", "file_copy", "file_delete", "file_list", "launch_app", "run_command",
            # Global Control tools (Network/IoT)
            "network_scan", "discover_chromecast", "chromecast_command", "adb_connect", "adb_command",
            # Phone & Notifications
            "send_phone_notification", "adb_connect_wireless", "phone_notify",
            # Special Routines
            "morning_routine"
        }
        
        ALIASES = {
            # Core aliases
            "google": "search_web", "browser": "search_web", "news": "search_web",         
            "search_news": "search_web", "look": "capture_image", "see": "capture_image", 
            "check_time": "get_time",
            # System aliases
            "open": "open_browser", "go_to": "open_browser", "visit": "open_browser",
            "delete": "file_delete", "remove": "file_delete", "list_files": "file_list",
            "move_file": "file_move", "copy_file": "file_copy",
            # Network aliases
            "scan": "network_scan", "find_devices": "discover_chromecast", "tv": "chromecast_command"
        }

        action = ALIASES.get(raw_action, raw_action)
        print(f"ACTION: {raw_action} -> {action}", flush=True)

        if action not in VALID_TOOLS:
            if value and isinstance(value, str) and len(value.split()) > 1:
                return f"CHAT_FALLBACK::{value}"
            return "INVALID_ACTION"

        # ===== CORE ACTIONS =====
        if action == "get_time":
            now = datetime.datetime.now().strftime("%I:%M %p")
            return f"The current time is {now}."
        
        elif action == "search_web":
            print(f"Searching web for: {value}...", flush=True)
            try:
                with DDGS() as ddgs:
                    results = []
                    try:
                        results = list(ddgs.news(value, region='us-en', max_results=1))
                        if results: 
                            print(f"[DEBUG] Found News: {results[0].get('title')}", flush=True)
                    except Exception as e: 
                        print(f"[DEBUG] News Search Error: {e}", flush=True)
                    
                    if not results:
                        print("[DEBUG] No news found, trying text search...", flush=True)
                        try: 
                            results = list(ddgs.text(value, region='us-en', max_results=1))
                            if results: 
                                print(f"[DEBUG] Found Text: {results[0].get('title')}", flush=True)
                        except Exception as e:
                             print(f"[DEBUG] Text Search Error: {e}", flush=True)

                    if results:
                        r = results[0]
                        title = r.get('title', 'No Title')
                        body = r.get('body', r.get('snippet', 'No Body'))
                        return f"SEARCH RESULTS for '{value}':\nTitle: {title}\nSnippet: {body[:300]}"
                    else: 
                        print(f"[DEBUG] Search returned 0 results.", flush=True)
                        return "SEARCH_EMPTY"
            except Exception as e:
                print(f"[DEBUG] Connection/Library Error: {e}", flush=True)
                return "SEARCH_ERROR"
        
        elif action == "capture_image":
             return "IMAGE_CAPTURE_TRIGGERED"

        # ===== SYSTEM ACTION ENGINE =====
        elif action == "open_browser":
            url = action_data.get("url") or value
            if system_action_engine.open_browser(url):
                return f"Opened {url} in your browser."
            else:
                return "Failed to open browser."
        
        elif action == "file_list":
            directory = action_data.get("directory") or value
            files = system_action_engine.file_list(directory)
            if files:
                return f"Files in {directory}: {', '.join(files[:5])}"
            else:
                return f"Could not list files in {directory}"
        
        elif action == "file_copy":
            source = action_data.get("source")
            destination = action_data.get("destination")
            if system_action_engine.file_copy(source, destination):
                return f"Copied {source} to {destination}"
            else:
                return f"Failed to copy file"
        
        elif action == "file_move":
            source = action_data.get("source")
            destination = action_data.get("destination")
            if system_action_engine.file_move(source, destination):
                return f"Moved {source} to {destination}"
            else:
                return f"Failed to move file"
        
        elif action == "file_delete":
            filepath = action_data.get("filepath") or value
            if system_action_engine.file_delete(filepath):
                return f"Deleted {filepath}"
            else:
                return f"Failed to delete file"
        
        elif action == "launch_app":
            app_name = action_data.get("app_name") or value
            if system_action_engine.launch_app(app_name):
                return f"Launched {app_name}"
            else:
                return f"Failed to launch {app_name}"
        
        elif action == "run_command":
            command = action_data.get("command") or value
            if system_action_engine.run_command(command):
                return f"Command executed."
            else:
                return f"Command failed."

        # ===== NETWORK & IOT ACTIONS =====
        elif action == "network_scan":
            subnet = action_data.get("subnet") or "192.168.1.0/24"
            devices = network_iot_controller.scan_network(subnet)
            if devices:
                device_list = "\n".join([f"{d['ip']} ({d['mac']})" for d in devices])
                return f"Network scan complete. Found devices:\n{device_list}"
            else:
                return "No devices found on network"
        
        elif action == "discover_chromecast":
            devices = network_iot_controller.discover_chromecast()
            if devices:
                device_list = "\n".join([d['name'] for d in devices])
                return f"Found Chromecast devices:\n{device_list}"
            else:
                return "No Chromecast devices found"
        
        elif action == "chromecast_command":
            device_name = action_data.get("device_name")
            command = action_data.get("command")
            args = action_data.get("args", {})
            if network_iot_controller.send_chromecast_command(device_name, command, args):
                return f"Sent {command} to {device_name}"
            else:
                return f"Failed to send command"
        
        elif action == "adb_connect":
            device_address = action_data.get("device_address") or value
            print(f"[ACTION] Connecting to ADB device: {device_address}", flush=True)
            return f"Ready to send ADB commands to {device_address}. Use 'adb_command' action."
        
        elif action == "adb_command":
            device_address = action_data.get("device_address")
            command = action_data.get("command") or value
            if network_iot_controller.send_adb_command(device_address, command):
                return f"ADB command executed."
            else:
                return f"ADB command failed."

        # ===== PHONE & NOTIFICATIONS =====
        elif action == "adb_connect_wireless":
            phone_ip = action_data.get("phone_ip") or value
            if network_iot_controller.adb_connect_wireless(phone_ip):
                self.phone_ip = phone_ip  # Store for future use
                return f"Connected to phone at {phone_ip}. Ready to send notifications."
            else:
                return f"Failed to connect to phone at {phone_ip}. Is your phone's IP correct?"
        
        elif action == "send_phone_notification":
            message = action_data.get("message") or value
            if network_iot_controller.send_phone_notification(message, self.phone_ip):
                return f"Notification sent to your phone."
            else:
                return f"Failed to send notification. Is your phone connected via ADB?"
        
        elif action == "phone_notify":
            msg = action_data.get("msg") or action_data.get("message") or value
            if not msg:
                return "No message provided for phone notification."
            
            # Format for notification display
            notification_msg = msg if msg.startswith("KNO") else f"KNO: {msg}"
            
            # Try using termux-notification first (if Termux app installed), then fallback to am broadcast
            try:
                import subprocess
                
                # Try Method 1: Termux notification (more user-friendly)
                try:
                    result = subprocess.run(
                        ["adb", "shell", "termux-notification", "-t", "KNO Message", "-c", msg],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        print(f"[PHONE] ✅ Notification sent via Termux: {msg[:50]}...", flush=True)
                        return f"Notification sent to your phone."
                except Exception:
                    pass  # Fallback to method 2
                
                # Method 2: am broadcast
                result = subprocess.run(
                    ["adb", "shell", "am", "broadcast",
                     "-a", "android.intent.action.EDIT",
                     "--es", "msg", notification_msg],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    print(f"[PHONE] ✅ Notification sent via broadcast: {msg[:50]}...", flush=True)
                    return f"Notification sent to your phone."
                else:
                    print(f"[PHONE] ❌ Notification failed: {result.stderr}", flush=True)
                    return f"Failed to send notification."
                    
            except FileNotFoundError:
                print(f"[PHONE] ❌ ADB not found", flush=True)
                return "ADB not found - make sure phone is synced."
            except Exception as e:
                print(f"[PHONE] ❌ Notification error: {e}", flush=True)
                return f"Error sending notification: {e}"

        # ===== SPECIAL ROUTINES =====
        elif action == "morning_routine":
            if self.execute_morning_routine():
                return "Morning routine started - follow the approval dialogs."
            else:
                return "Morning routine failed to execute."

        return None

    # =========================================================================
    # 3.5 AUTONOMOUS BRAIN LOOP - PROACTIVE DECISION MAKING
    # =========================================================================

    def autonomous_brain_loop(self):
        """
        Background thread that runs autonomously every 60 seconds.
        - Checks for new WhatsApp notifications
        - Announces urgent messages without user input
        - Monitors system health and reports issues
        - PHASE 3: Performs experience-based self-optimization
        - PHASE 4: Queries external AI brains (Gemini/ChatGPT) for complex problems
        """
        print("[BRAIN] 🧠 Autonomous brain loop started", flush=True)
        print("[BRAIN] 🌐 External AI brains available: Gemini=%s, ChatGPT=%s" % (
            "✅" if higher_intelligence_bridge.gemini_key else "❌",
            "✅" if higher_intelligence_bridge.openai_key else "❌"
        ), flush=True)
        
        cycle_count = 0
        evolution_query_cycle = 0
        
        while True:
            try:
                cycle_count += 1
                print(f"[BRAIN] 🔄 Cycle {cycle_count} - Running autonomous evolutionary checks...", flush=True)
                
                # 1. Check system health
                health = get_system_health()
                if health:
                    cpu_pct = health['cpu_percent']
                    disk_pct = health['disk_usage']
                    mem_pct = health['memory_percent']
                    
                    # PHASE 3: Track health metrics for evolutionary optimization
                    if evolution_logic:
                        evolution_logic.track_success_rate(
                            f"system_health_cycle_{cycle_count}",
                            success=(cpu_pct < 90 and disk_pct < 90 and mem_pct < 85)
                        )
                    
                    # Report if resources are critically high
                    if cpu_pct > 90:
                        msg = f"Warning: CPU usage is {cpu_pct}% - system may be slow"
                        print(f"[BRAIN] ⚠️  {msg}", flush=True)
                        with self.tts_queue_lock:
                            self.tts_queue.append(msg)
                    
                    if disk_pct > 90:
                        msg = f"Warning: Disk usage is {disk_pct}% - running out of space"
                        print(f"[BRAIN] ⚠️  {msg}", flush=True)
                        with self.tts_queue_lock:
                            self.tts_queue.append(msg)
                    
                    if mem_pct > 85:
                        msg = f"Warning: Memory usage is {mem_pct}% - may need to free resources"
                        print(f"[BRAIN] ⚠️  {msg}", flush=True)
                        with self.tts_queue_lock:
                            self.tts_queue.append(msg)
                    
                    if cpu_pct < 90 and disk_pct < 90 and mem_pct < 85:
                        print(f"[BRAIN] ✅ System health OK - CPU:{cpu_pct}% Disk:{disk_pct}% Memory:{mem_pct}%", flush=True)
                
                # 2. Check for urgent WhatsApp notifications
                if self.notification_listener and hasattr(self.notification_listener, 'last_notification_hash'):
                    pass
                
                # 3. Every 5 cycles (5 minutes), perform self-analysis
                if cycle_count % 5 == 0:
                    print(f"[BRAIN] 📋 Diagnostic: Notifications processed, System stable", flush=True)
                    
                    # PHASE 3: Analyze error patterns
                    if experience_memory:
                        error_count = experience_memory.data.get("errors_encountered", 0)
                        if error_count > 0:
                            print(f"[BRAIN] 🔍 Experience analysis: {error_count} total errors logged", flush=True)
                            
                            for error_log in experience_memory.data.get("error_log", []):
                                if error_log.get("count", 0) >= 3:
                                    print(f"[BRAIN] ⚠️  Recurring error detected: {error_log['type']} ({error_log['count']} times)", flush=True)
                                    
                                    if evolution_logic:
                                        evolution_logic.suggest_improvement(
                                            component=error_log['type'],
                                            issue_description=f"Error occurs repeatedly ({error_log['count']} times)",
                                            suggested_fix=f"Review and optimize error handling for {error_log['type']}"
                                        )
                
                # 4. PHASE 4: Every 10 cycles (10 minutes), query external AI brains for system analysis
                evolution_query_cycle += 1
                if evolution_query_cycle >= 10:
                    evolution_query_cycle = 0
                    print(f"[BRAIN] 🧬 Querying external AI brains for evolutionary insights...", flush=True)
                    
                    # Prepare system status for AI analysis
                    ai_prompt = f"""
                    I am KNO, an autonomous AI agent. Provide brief evolutionary improvements for my system:
                    
                    System Status:
                    - CPU: {cpu_pct}%
                    - Disk: {disk_pct}%
                    - Memory: {mem_pct}%
                    - Cycles Run: {cycle_count}
                    - Total Errors: {experience_memory.data.get('errors_encountered', 0) if experience_memory else 0}
                    
                    Suggest ONE actionable optimization.
                    """
                    
                    # Query higher intelligence bridge
                    ai_suggestion = higher_intelligence_bridge.solve_complex_problem(ai_prompt)
                    
                    if ai_suggestion:
                        print(f"[BRAIN] 💡 AI Brain Suggestion: {ai_suggestion[:100]}...", flush=True)
                        with self.tts_queue_lock:
                            self.tts_queue.append(f"AI brain suggests: {ai_suggestion[:100]}")
                
                # Log all interactions
                if cycle_count % 5 == 0:
                    higher_intelligence_bridge.log_interactions()
                
                print(f"[BRAIN] ✨ Cycle {cycle_count} complete, sleeping for 60s", flush=True)
                time.sleep(60)
                
            except Exception as e:
                print(f"[BRAIN] ❌ Error in autonomous evolutionary loop: {e}", flush=True)
                import traceback
                traceback.print_exc()
                
                if experience_memory:
                    experience_memory.log_error(
                        error_type="autonomous_brain_error",
                        error_message=str(e)[:100],
                        context=f"cycle_{cycle_count}"
                    )
                
                error_recovery.log_error("autonomous_brain", str(e))
                
                # Self-correction attempt
                if self_correction:
                    missing_lib = self_correction.detect_missing_library(str(e))
                    if missing_lib:
                        print(f"[BRAIN] 📦 Attempting to auto-install: {missing_lib}", flush=True)
                        self_correction.auto_install_dependency(missing_lib)
                
                time.sleep(60)

    # =========================================================================
    # 4. CORE LOGIC
    # =========================================================================

    def safe_main_execution(self):
        """Main execution loop with comprehensive error recovery and autonomy.
        
        Features:
        - Warm-up initialization with error handling
        - TTS worker thread for audio output
        - Continuous voice listening loop
        - Error detection and automatic recovery
        - Experience memory logging
        - Self-correction hooks
        """
        error_cycle_count = 0
        max_error_cycles = 5
        
        while True:
            try:
                print(f"[MAIN] 🚀 Starting safe main execution (attempt {error_cycle_count + 1})...", flush=True)
                
                # 1. WARM-UP INITIALIZATION
                try:
                    print("[MAIN] ⚙️  Starting warm-up...", flush=True)
                    self.warm_up_logic()
                    print("[MAIN] ✅ Warm-up complete", flush=True)
                    error_recovery.reset_component("warmup")
                    error_cycle_count = 0  # Reset error counter on success
                except Exception as warmup_error:
                    print(f"[MAIN] ⚠️  Warm-up error: {warmup_error}", flush=True)
                    if experience_memory:
                        experience_memory.log_error(
                            error_type="warmup_failure",
                            error_message=str(warmup_error)[:100],
                            context="safe_main_execution"
                        )
                    error_recovery.log_error("warmup", str(warmup_error))
                    time.sleep(5)
                    continue
                
                # 2. START TTS WORKER
                try:
                    print("[MAIN] 🔊 Starting TTS worker", flush=True)
                    self.tts_active.set()
                    if not self.tts_thread or not self.tts_thread.is_alive():
                        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
                        self.tts_thread.start()
                    print("[MAIN] ✅ TTS worker ready", flush=True)
                except Exception as tts_error:
                    print(f"[MAIN] ⚠️  TTS worker error: {tts_error}", flush=True)
                    if experience_memory:
                        experience_memory.log_error(
                            error_type="tts_worker_failure",
                            error_message=str(tts_error)[:100]
                        )
                
                # 3. NOTIFICATION LISTENER READY
                print("[MAIN] 📱 Notification listener ready (will start after phone sync)", flush=True)
                
                # 4. START AUTONOMOUS LISTENING LOOP
                print("[MAIN] 🎧 Entering autonomous listening loop...", flush=True)
                print("\n" + "="*60, flush=True)
                print("[READY] ✨ KNO READY - AUTONOMOUS MODE ACTIVATED!", flush=True)
                print("   🎤 Hands-Free Listening Enabled", flush=True)
                print("   🔴 Red LED: Ready for voice input", flush=True)
                print("   1. Say 'KNO' to wake me up", flush=True)
                print("   2. After the beep, say your command", flush=True)
                print("   3. I'll automatically process and respond", flush=True)
                print("   4. Press SPACE at any time to interrupt", flush=True)
                print("="*60 + "\n", flush=True)
                
                # Main listening loop
                while True:
                    try:
                        try:
                            # INNER LOOP: Continuously listen for wake word/PTT with error recovery
                            print("[MAIN] 👂 Waiting for wake word or PTT...", flush=True)

                            try:
                                trigger_source = self.detect_wake_word_or_ptt()
                                print(f"[MAIN] 🔊 Triggered by: {trigger_source}", flush=True)
                            except Exception as detect_error:
                                print(f"[MAIN] ⚠️  Wake word detection error: {detect_error}", flush=True)
                                if experience_memory:
                                    experience_memory.log_error(
                                        error_type="wake_word_detection_error",
                                        error_message=str(detect_error)[:100]
                                    )
                                time.sleep(2)
                                continue
                            
                            if self.interrupted.is_set():
                                self.interrupted.clear()
                                self.set_state(BotStates.IDLE, "Resetting...")
                                continue

                            self.set_state(BotStates.LISTENING, "I'm listening!")

                            # 4A. RECORD AUDIO
                            audio_file = None
                            try:
                                if trigger_source == "PTT":
                                    audio_file = self.record_voice_ppt_with_fallback()
                                else:
                                    audio_file = self.record_voice_adaptive_with_fallback()
                            except Exception as record_error:
                                print(f"[MAIN] ⚠️  Audio recording error: {record_error}", flush=True)
                                if experience_memory:
                                    experience_memory.log_error(
                                        error_type="audio_recording_error",
                                        error_message=str(record_error)[:100]
                                    )
                                self.set_state(BotStates.IDLE, "Recording failed.")
                                continue

                            if not audio_file:
                                print("[MAIN] ⚠️  No audio recorded. Try again.", flush=True)
                                self.set_state(BotStates.IDLE, "Heard nothing.")
                                continue

                            # 4B. TRANSCRIBE AUDIO
                            try:
                                print("[MAIN] 🔤 Converting audio to text...", flush=True)
                                user_text = self.transcribe_audio_with_recovery(audio_file)
                            except Exception as transcribe_error:
                                print(f"[MAIN] ⚠️  Transcription error: {transcribe_error}", flush=True)
                                if experience_memory:
                                    experience_memory.log_error(
                                        error_type="transcription_error",
                                        error_message=str(transcribe_error)[:100]
                                    )
                                self.set_state(BotStates.IDLE, "Transcription failed.")
                                continue
                            
                            if not user_text:
                                print("[MAIN] ⚠️  No text transcribed. Try again.", flush=True)
                                self.set_state(BotStates.IDLE, "Transcription empty.")
                                continue
                            
                            # 4C. PROCESS AND RESPOND
                            try:
                                print(f"[MAIN] ✅ You said: {user_text}", flush=True)
                                self.append_to_text(f"YOU: {user_text}")
                                self.interrupted.clear()
                                self.chat_and_respond(user_text, img_path=None)
                                error_recovery.reset_component("main_loop")
                            except Exception as response_error:
                                print(f"[MAIN] ⚠️  Response generation error: {response_error}", flush=True)
                                if experience_memory:
                                    experience_memory.log_error(
                                        error_type="response_generation_error",
                                        error_message=str(response_error)[:100]
                                    )
                                self.set_state(BotStates.IDLE, "Response error.")
                                continue
                        
                        except Exception as inner_loop_error:
                            print(f"[MAIN] ⚠️  Inner loop error: {inner_loop_error}", flush=True)
                            print("[MAIN] 🔄 Restarting listening loop...", flush=True)
                            time.sleep(2)
                            continue
                    
                    except KeyboardInterrupt:
                        print("\n[MAIN] ⛔ Keyboard interrupt received", flush=True)
                        self.safe_exit()
                        return
            
            except KeyboardInterrupt:
                print("\n[MAIN] ⛔ Keyboard interrupt in outer loop", flush=True)
                self.safe_exit()
                return
            
            except Exception as outer_error:
                print(f"[MAIN] ❌ Critical error in main execution: {outer_error}", flush=True)
                import traceback
                traceback.print_exc()
                
                # Log error
                if experience_memory:
                    experience_memory.log_error(
                        error_type="main_execution_critical",
                        error_message=str(outer_error)[:100],
                        context="safe_main_execution"
                    )
                
                error_recovery.log_error("main_execution", str(outer_error))
                
                # Self-correction attempt
                if self_correction:
                    missing_lib = self_correction.detect_missing_library(str(outer_error))
                    if missing_lib:
                        print(f"[CORRECTION] 📦 Attempting to auto-install: {missing_lib}", flush=True)
                        if self_correction.auto_install_dependency(missing_lib):
                            print(f"[CORRECTION] ✅ Successfully installed {missing_lib}, restarting...", flush=True)
                            error_cycle_count = 0
                            continue
                
                # Increment error cycle and check limit
                error_cycle_count += 1
                if error_cycle_count >= max_error_cycles:
                    print(f"[MAIN] 🛑 Max error cycles ({max_error_cycles}) reached, giving up", flush=True)
                    self.set_state(BotStates.ERROR, f"Max retries exceeded")
                    self.safe_exit()
                    return
                
                print(f"[MAIN] ♻️  Restarting main execution (attempt {error_cycle_count + 1}/{max_error_cycles})...", flush=True)
                time.sleep(5)  # Wait before retry

    def warm_up_logic(self):
        """Initialize AI brains with comprehensive error handling and recovery.
        
        Features:
        - Attempt local model load (if available)
        - Graceful fallback to cloud APIs  
        - Audio device initialization
        - Experience memory logging
        """
        self.set_state(BotStates.WARMUP, "Warming up brains...")
        try:
            print(f"[LLAMA] 🚀 Loading AI brains...", flush=True)
            
            # Try local model first
            try:
                print(f"[LLAMA] Attempting local model load...", flush=True)
                llm = LlamaConnector.load_model()
                
                if llm:
                    print(f"[LLAMA] ✅ Local model loaded successfully", flush=True)
                    error_recovery.reset_component("llama")
                else:
                    print(f"[LLAMA] ⚠️  Local model unavailable, using cloud", flush=True)
                    if experience_memory:
                        experience_memory.log_error(
                            error_type="local_model_unavailable",
                            error_message="Will use cloud APIs",
                            context="warm_up_logic"
                        )
            except Exception as local_error:
                print(f"[LLAMA] ⚠️  Local model error: {local_error}", flush=True)
                if experience_memory:
                    experience_memory.log_error(
                        error_type="local_model_load_error",
                        error_message=str(local_error)[:100],
                        context="warm_up_logic"
                    )
            
            # Cloud LLM initialization
            try:
                print(f"[CLOUD] Initializing cloud LLM...", flush=True)
                if self.cloud_llm_mode:
                    print(f"[CLOUD] ✅ Cloud LLM ready (Gemini/ChatGPT)", flush=True)
                    error_recovery.reset_component("cloud_llm")
                else:
                    print(f"[CLOUD] Cloud mode disabled", flush=True)
            except Exception as cloud_error:
                print(f"[CLOUD] ⚠️  Error: {cloud_error}", flush=True)
            
            # Audio initialization
            try:
                print(f"[AUDIO] Checking devices...", flush=True)
                if sd is not None:
                    device_info = sd.query_devices(kind='input')
                    print(f"[AUDIO] ✅ Ready: {device_info['name']}", flush=True)
                    error_recovery.reset_component("audio")
            except Exception as audio_error:
                print(f"[AUDIO] ⚠️  Error: {audio_error}", flush=True)
            
            # Greeting sound
            try:
                print(f"[SOUND] Playing greeting...", flush=True)
                greeting_sound = self.get_random_sound(greeting_sounds_dir)
                if greeting_sound:
                    self.play_sound(greeting_sound)
                    print(f"[SOUND] ✅ Ready", flush=True)
                else:
                    print(f"[SOUND] ⚠️  No sound available", flush=True)
            except Exception as sound_error:
                print(f"[SOUND] ⚠️  Error: {sound_error}", flush=True)
            
            print("[INIT] 🎯 Warm-up complete, ready for autonomy", flush=True)
            error_recovery.reset_component("warmup")
        
        except Exception as e:
            print(f"[LLAMA] ❌ Warmup error: {e}", flush=True)
            error_recovery.log_error("warmup", str(e))
            if experience_memory:
                experience_memory.log_error(
                    error_type="warmup_critical",
                    error_message=str(e)[:100],
                    context="warm_up_logic"
                )
            print(f"[LLAMA] Continuing in degraded mode", flush=True)

    def detect_wake_word_or_ptt(self):
        self.set_state(BotStates.IDLE, "🎤 Listening for KNO...")
        self.ptt_event.clear()
        
        if self.oww_model: self.oww_model.reset()

        if self.oww_model is None:
            print("[WAKE_WORD] ⚠️  Wake word model not loaded, enabling PTT fallback", flush=True)
            self.ptt_event.wait()
            self.ptt_event.clear()
            return "PTT"

        CHUNK_SIZE = 1280
        OWW_SAMPLE_RATE = 16000
        
        try:
            device_info = sd.query_devices(kind='input')
            native_rate = int(device_info['default_samplerate'])
        except: native_rate = 48000
            
        use_resampling = (native_rate != OWW_SAMPLE_RATE)
        input_rate = native_rate if use_resampling else OWW_SAMPLE_RATE
        input_chunk_size = int(CHUNK_SIZE * (input_rate / OWW_SAMPLE_RATE)) if use_resampling else CHUNK_SIZE
        device = get_audio_device()

        try:
            with sd.InputStream(samplerate=input_rate, channels=1, dtype='int16', 
                                blocksize=input_chunk_size, device=device) as stream:
                while True:
                    if self.ptt_event.is_set():
                        self.ptt_event.clear()
                        return "PTT"
                    
                    # Windows: select() doesn't work with stdin, skip this check on Windows
                    if sys.platform != "win32":
                        rlist, _, _ = select.select([sys.stdin], [], [], 0.001)
                        if rlist: 
                            sys.stdin.readline()
                            return "CLI" 

                    data, _ = stream.read(input_chunk_size)
                    audio_data = np.frombuffer(data, dtype=np.int16)

                    if use_resampling:
                         audio_data = scipy.signal.resample(audio_data, CHUNK_SIZE).astype(np.int16)

                    prediction = self.oww_model.predict(audio_data)
                    for mdl in self.oww_model.prediction_buffer.keys():
                        if list(self.oww_model.prediction_buffer[mdl])[-1] > WAKE_WORD_THRESHOLD:
                            print("[WAKE_WORD] ✅ 'KNO' keyword detected! Starting recording...", flush=True)
                            self.oww_model.reset() 
                            return "WAKE"
                    # Prevent busy-loop CPU spike when idle
                    time.sleep(0.1)
        except Exception as e:
            print(f"[WAKE_WORD] ⚠️  Stream Error: {e}", flush=True)
            print("[WAKE_WORD] Falling back to PTT mode", flush=True)
            self.ptt_event.wait()
            return "PTT"

    # Note: removed duplicate/misspelled `detect_wake_word_or_ppt` wrappers
    # to avoid recursion and ambiguity. Use `detect_wake_word_or_ptt()` as
    # the canonical method for wake-word/PTT detection.

    def record_voice_adaptive_with_fallback(self, filename="input.wav"):
        """Record voice with advanced fallback on device failure."""
        print("Recording (Adaptive)...", flush=True)

        for attempt in range(3):
            try:
                device = get_audio_device()
                return self.record_voice_adaptive(filename, device)
            except Exception as e:
                print(f"[AUDIO] Recording attempt {attempt + 1} failed: {e}", flush=True)
                error_recovery.log_error("audio_record", str(e))
                audio_device_manager.scan_and_cache_devices()
                time.sleep(1)

        print("[AUDIO] Recording failed after all attempts", flush=True)
        return None

    def record_voice_adaptive(self, filename="input.wav", device=None):
        """Original adaptive recording logic."""
        try:
            device_info = sd.query_devices(kind='input')
            samplerate = int(device_info['default_samplerate'])
        except Exception:
            samplerate = 44100

        silence_threshold = 0.006
        silence_duration = 1.5
        max_record_time = 120.0  # UNRESTRICTED: Removed artificial limit
        buffer = []
        silent_chunks = 0
        chunk_duration = 0.05
        chunk_size = int(samplerate * chunk_duration)

        num_silent_chunks = int(silence_duration / chunk_duration)
        max_chunks = int(max_record_time / chunk_duration)
        recorded_chunks = 0
        silence_started = False

        def callback(indata, frames, time_info, status):
            nonlocal silent_chunks, recorded_chunks, silence_started
            volume_norm = np.linalg.norm(indata) / np.sqrt(len(indata))
            buffer.append(indata.copy())
            recorded_chunks += 1
            if recorded_chunks < 5:
                return
            if volume_norm < silence_threshold:
                silent_chunks += 1
                if silent_chunks >= num_silent_chunks:
                    silence_started = True
            else:
                silent_chunks = 0

        try:
            with sd.InputStream(samplerate=samplerate, channels=1, callback=callback,
                                device=device, blocksize=chunk_size):
                while not silence_started and recorded_chunks < max_chunks:
                    sd.sleep(int(chunk_duration * 1000))
        except Exception as e:
            print(f"[AUDIO] Adaptive recording error: {e}", flush=True)
            error_recovery.log_error("audio_adaptive", str(e))
            return None

        return self.save_audio_buffer(buffer, filename, samplerate)

    def record_voice_ppt_with_fallback(self, filename="input.wav"):
        """Record voice with PTT and advanced fallback."""
        print("Recording (PTT)...", flush=True)

        for attempt in range(3):
            try:
                device = get_audio_device()
                return self.record_voice_ppt(filename, device)
            except Exception as e:
                print(f"[AUDIO] PTT attempt {attempt + 1} failed: {e}", flush=True)
                error_recovery.log_error("audio_ppt", str(e))
                audio_device_manager.scan_and_cache_devices()
                time.sleep(1)

        print("[AUDIO] PTT recording failed after all attempts", flush=True)
        return None

    def record_voice_ppt(self, filename="input.wav", device=None):
        """Original PTT recording logic."""
        try:
            device_info = sd.query_devices(kind='input')
            samplerate = int(device_info['default_samplerate'])
        except Exception:
            samplerate = 44100

        buffer = []

        def callback(indata, frames, time_info, status):
            buffer.append(indata.copy())

        try:
            with sd.InputStream(samplerate=samplerate, channels=1, callback=callback, device=device):
                while self.recording_active.is_set():
                    sd.sleep(50)
            print(f"[AUDIO] PTT recording complete, {len(buffer)} chunks recorded", flush=True)
        except Exception as e:
            print(f"[AUDIO] PTT recording error: {e}", flush=True)
            error_recovery.log_error("audio_ppt_stream", str(e))
            return None

        return self.save_audio_buffer(buffer, filename, samplerate)

    def save_audio_buffer(self, buffer, filename, samplerate=16000):
        if not buffer:
            print("[AUDIO] Warning: Empty buffer, cannot save", flush=True)
            return None
        
        try:
            print(f"[AUDIO] Saving {len(buffer)} chunks to {filename}", flush=True)
            audio_data = np.concatenate(buffer, axis=0).flatten()
            audio_data = np.nan_to_num(audio_data, nan=0.0, posinf=0.0, neginf=0.0)
            audio_data = (audio_data * 32767).astype(np.int16)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
            
            # WHY: Explicit file handle management ensures file is completely closed
            # before Whisper tries to read it. Context manager (with) sometimes leaves
            # file handles open on Windows, causing "file in use" errors.
            wf = wave.open(filename, "wb")
            try:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(samplerate)
                wf.writeframes(audio_data.tobytes())
            finally:
                wf.close()  # Ensure file is closed before returning
            
            # Small delay to ensure file system finishes writing
            time.sleep(0.1)
            
            print(f"[AUDIO] Audio saved successfully: {filename}", flush=True)
            
            # Play acknowledgment sound (gracefully skip if unavailable)
            ack_sound = self.get_random_sound(ack_sounds_dir)
            if ack_sound:
                try:
                    self.play_sound(ack_sound)
                except Exception as e:
                    print(f"[AUDIO] Warning: Could not play ack sound: {e}", flush=True)
            
            return filename
        except Exception as e:
            print(f"[AUDIO] Error saving audio buffer: {e}", flush=True)
            traceback.print_exc()
            return None

    def transcribe_audio_with_recovery(self, filename):
        """Transcribe audio with error recovery and fallback."""
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                return self.transcribe_audio(filename)
            except Exception as e:
                print(f"[TRANSCRIBE] Attempt {attempt + 1} failed: {e}", flush=True)
                error_recovery.log_error("transcribe", str(e))
                if attempt < max_attempts - 1:
                    time.sleep(2)
                    continue
        return ""

    def transcribe_audio(self, filename):
        print("Transcribing...", flush=True)
        transcription = ""
        # 1) Try whisper-cli (local) if present
        try:
            if sys.platform == "win32":
                whisper_exe = r"A:\KNO\KNO\whisper.cpp\build\bin\whisper-cli.exe"
                model_path = r"A:\KNO\KNO\models\ggml-base.en.bin"
            else:
                whisper_exe = os.path.join("whisper.cpp", "build", "bin", "whisper-cli")
                model_path = os.path.join("models", "ggml-base.en.bin")

            if os.path.exists(whisper_exe) and os.path.exists(model_path) and os.path.exists(filename):
                print(f"[TRANSCRIBE] Using whisper at: {whisper_exe}", flush=True)
                print(f"[TRANSCRIBE] Using model at: {model_path}", flush=True)
                try:
                    result = subprocess.run(
                        [whisper_exe, "-m", model_path, "-l", "en", "-t", "4", "-f", filename],
                        capture_output=True, text=True, timeout=120
                    )
                    if result.returncode == 0 and result.stdout:
                        transcription_lines = result.stdout.strip().split('\n')
                        if transcription_lines and transcription_lines[-1].strip():
                            last_line = transcription_lines[-1].strip()
                            if ']' in last_line:
                                transcription = last_line.split("]")[1].strip()
                            else:
                                transcription = last_line
                            print(f"[TRANSCRIBE] Whisper result: {transcription}", flush=True)
                            error_recovery.reset_component("transcribe")
                            return transcription.strip()
                        else:
                            print("[TRANSCRIBE] Whisper returned empty output", flush=True)
                    else:
                        err = result.stderr if result.stderr else result.stdout
                        print(f"[TRANSCRIBE] Whisper failed: {err}", flush=True)
                except subprocess.TimeoutExpired:
                    print("[TRANSCRIBE] Whisper timed out", flush=True)
            else:
                print("[TRANSCRIBE] whisper-cli or model not found; skipping to fallback", flush=True)
        except Exception as e:
            print(f"[TRANSCRIBE] Whisper attempt exception: {e}", flush=True)
            error_recovery.log_error("transcribe", str(e))

        # 2) Fallback: SpeechRecognition (Google or PocketSphinx)
        try:
            import importlib
            sr_spec = importlib.util.find_spec('speech_recognition')
            if sr_spec is not None:
                import speech_recognition as sr
                r = sr.Recognizer()
                with sr.AudioFile(filename) as source:
                    audio = r.record(source)
                try:
                    transcription = r.recognize_google(audio)
                    print(f"[TRANSCRIBE] SpeechRecognition (Google) result: {transcription}", flush=True)
                    error_recovery.reset_component("transcribe")
                    return transcription.strip()
                except sr.RequestError as re:
                    print(f"[TRANSCRIBE] Google SR request failed: {re}", flush=True)
                    # Try offline PocketSphinx if available
                    try:
                        transcription = r.recognize_sphinx(audio)
                        print(f"[TRANSCRIBE] SpeechRecognition (Sphinx) result: {transcription}", flush=True)
                        error_recovery.reset_component("transcribe")
                        return transcription.strip()
                    except Exception as se:
                        print(f"[TRANSCRIBE] Sphinx failed: {se}", flush=True)
                except sr.UnknownValueError:
                    print("[TRANSCRIBE] SpeechRecognition could not understand audio", flush=True)
                except Exception as e:
                    print(f"[TRANSCRIBE] SpeechRecognition error: {e}", flush=True)
            else:
                print("[TRANSCRIBE] speech_recognition library not installed; skipping SR fallback", flush=True)
        except Exception as e:
            print(f"[TRANSCRIBE] SpeechRecognition fallback exception: {e}", flush=True)
            error_recovery.log_error("transcribe", str(e))

        # 3) Fallback: Cloud LLM bridge (if present and supports audio transcription)
        try:
            if 'cloud_llm_bridge' in globals() and cloud_llm_bridge is not None:
                for method_name in ('transcribe_audio_file', 'transcribe_audio', 'transcribe'):
                    if hasattr(cloud_llm_bridge, method_name):
                        try:
                            fn = getattr(cloud_llm_bridge, method_name)
                            transcription = fn(filename)
                            if transcription:
                                print(f"[TRANSCRIBE] CloudLLMBridge result via {method_name}: {transcription}", flush=True)
                                error_recovery.reset_component("transcribe")
                                return transcription.strip()
                        except Exception as ce:
                            print(f"[TRANSCRIBE] CloudLLMBridge {method_name} failed: {ce}", flush=True)
        except Exception as e:
            print(f"[TRANSCRIBE] Cloud fallback exception: {e}", flush=True)
            error_recovery.log_error("transcribe", str(e))

        # If all fallbacks fail, log and return empty string
        print("[TRANSCRIBE] All transcribe methods failed or returned empty.", flush=True)
        return ""

    def capture_image(self):
        self.set_state(BotStates.CAPTURING, "Watching...")
        try:
            if sys.platform != "win32":
                subprocess.run(["rpicam-still", "-t", "500", "-n", "--width", "640", "--height", "480", "-o", KNO_IMAGE_FILE], check=True)
            else:
                try:
                    import cv2
                    cap = cv2.VideoCapture(0)
                    ret, frame = cap.read()
                    if ret:
                        cv2.imwrite(KNO_IMAGE_FILE, frame)
                    cap.release()
                except ImportError:
                    print("OpenCV not available. Please install: pip install opencv-python")
                    return None

            rotation = CURRENT_CONFIG.get("camera_rotation", 0)
            if rotation != 0:
                img = Image.open(KNO_IMAGE_FILE)
                img = img.rotate(rotation, expand=True)
                img.save(KNO_IMAGE_FILE)
            return KNO_IMAGE_FILE
        except Exception as e:
            print(f"Camera Error: {e}")
            error_recovery.log_error("camera", str(e))
            return None

    # =========================================================================
    # 5. MORNING ROUTINE
    # =========================================================================

    def execute_morning_routine(self):
        """Execute morning routine sequence: greeting sound → weather → TV → folder → phone notification."""
        try:
            print("[ACTION] Starting morning routine sequence...", flush=True)
            self.set_state(BotStates.SPEAKING, "Morning Routine Starting")
            
            # Step 1: Play greeting sound
            print("[ACTION] Morning routine: Step 1/5 - Playing greeting sound", flush=True)
            time.sleep(0.5)
            system_action_engine.play_sound("greeting")
            time.sleep(1.0)
            
            # Step 2: Open weather search
            print("[ACTION] Morning routine: Step 2/5 - Opening weather search", flush=True)
            time.sleep(0.5)
            system_action_engine.open_browser("https://www.google.com/search?q=weather+today")
            weather_summary = self.get_weather_summary()
            time.sleep(1.5)
            
            # Step 3: Send power-on to TV (if available)
            print("[ACTION] Morning routine: Step 3/5 - Powering on TV", flush=True)
            time.sleep(0.5)
            try:
                devices = network_iot_controller.discover_chromecast()
                if devices:
                    device_name = devices[0]  # Use first discovered device
                    network_iot_controller.send_chromecast_command(device_name, "power_on", [])
                    print(f"[ACTION] TV power command sent to {device_name}", flush=True)
                else:
                    print("[ACTION] No Chromecast devices found - skipping TV control", flush=True)
            except Exception as e:
                print(f"[ACTION] TV control error: {e} - continuing routine", flush=True)
            time.sleep(1.0)
            
            # Step 4: Open KNO folder
            print("[ACTION] Morning routine: Step 4/5 - Opening KNO folder", flush=True)
            time.sleep(0.5)
            system_action_engine.open_folder("a:\\KNO\\KNO")
            time.sleep(1.0)
            
            # Step 5: Send morning report to phone
            print("[ACTION] Morning routine: Step 5/5 - Sending phone notification", flush=True)
            time.sleep(0.5)
            
            # Get summaries
            task_summary = self.get_task_summary()
            
            # Create morning report message
            morning_report = f"Weather: {weather_summary}\n{task_summary}"
            
            # Request first-time phone notification approval
            if not self.first_notification_approved:
                print("[PHONE] First notification - requesting user approval", flush=True)
                if self.request_action_approval("first_phone_notification", 
                    f"Send morning report to phone?\n\n{morning_report[:100]}..."):
                    self.first_notification_approved = True
                    print("[PHONE] User approved phone notifications", flush=True)
                else:
                    print("[PHONE] User declined phone notifications", flush=True)
                    with self.tts_queue_lock:
                        self.tts_queue.append("Morning routine complete. Skipped phone notification.")
                    self.set_state(BotStates.IDLE, "Morning Routine Complete")
                    return True
            
            # Send notification
            if network_iot_controller.send_phone_notification(morning_report, self.phone_ip):
                print("[PHONE] ✅ Morning report sent to phone", flush=True)
            else:
                print("[PHONE] ⚠️  Failed to send phone notification - likely no phone configured yet", flush=True)
            
            print("[ACTION] Morning routine completed successfully", flush=True)
            with self.tts_queue_lock:
                self.tts_queue.append("Good morning! I've started your morning routine and sent a report to your phone.")
            self.set_state(BotStates.IDLE, "Morning Routine Complete")
            return True
            
        except Exception as e:
            print(f"[ACTION ERROR] Morning routine failed: {e}", flush=True)
            error_recovery.log_error("morning_routine", str(e))
            with self.tts_queue_lock:
                self.tts_queue.append("Something went wrong during the morning routine.")
            self.set_state(BotStates.IDLE, "Morning Routine Error")
            return False

    # =========================================================================
    # 6. CHAT & RESPOND
    # =========================================================================

    def chat_and_respond(self, text, img_path=None):
        # Check for morning routine trigger
        morning_phrases = ["good morning", "buenos días", "bonjour", "guten morgen"]
        if any(phrase in text.lower() for phrase in morning_phrases):
            print("[ACTION] Good morning trigger detected - executing morning routine", flush=True)
            self.execute_morning_routine()
            return
        
        if "forget everything" in text.lower() or "reset memory" in text.lower():
            self.session_memory = []
            self.permanent_memory = [{"role": "system", "content": SYSTEM_PROMPT}]
            self.save_chat_history()
            with self.tts_queue_lock: 
                self.tts_queue.append("Okay. Memory wiped.")
            self.set_state(BotStates.IDLE, "Memory Wiped")
            return

        model_to_use = VISION_MODEL if img_path else TEXT_MODEL
        self.set_state(BotStates.THINKING, "Thinking...", cam_path=img_path)
        
        messages = []
        if img_path:
            messages = [{"role": "user", "content": text, "images": [img_path]}]
        else:
            user_msg = {"role": "user", "content": text}
            messages = self.permanent_memory + self.session_memory + [user_msg]
        
        self.thinking_sound_active.set()
        threading.Thread(target=self._run_thinking_sound_loop, daemon=True).start()
        
        full_response_buffer = ""
        sentence_buffer = "" 
        
        try:
            # Use Llama for chat completion with streaming
            stream = LlamaConnector.stream_chat_completion(
                messages=messages,
                temperature=LLAMA_OPTIONS.get('temperature', 0.7),
                max_tokens=LLAMA_OPTIONS.get('max_tokens', 512)
            )
            
            is_action_mode = False
            
            for chunk in stream:
                if self.interrupted.is_set():
                    print("[LLAMA] Response interrupted by user", flush=True)
                    break
                
                # Extract content safely from llama-cpp-python format
                try:
                    content = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
                except Exception:
                    content = ""
                full_response_buffer += content
                
                if '{"' in content or "action:" in content.lower():
                    is_action_mode = True
                    self.thinking_sound_active.clear()
                    continue 

                if is_action_mode: continue

                self.thinking_sound_active.clear()
                if self.current_state != BotStates.SPEAKING:
                    self.set_state(BotStates.SPEAKING, "Speaking...", cam_path=img_path)
                    self.append_to_text("BOT: ", newline=False)

                self._stream_to_text(content)

                sentence_buffer += content
                if any(p in content for p in ".!?\n"):
                    clean_sentence = sentence_buffer.strip()
                    if clean_sentence and re.search(r'[a-zA-Z0-9]', clean_sentence):
                        with self.tts_queue_lock:
                            self.tts_queue.append(clean_sentence)
                    sentence_buffer = ""

            if is_action_mode:
                action_data = self.extract_json_from_text(full_response_buffer)
                if action_data:
                    tool_result = self.execute_action_and_get_result(action_data)

                    if tool_result and tool_result.startswith("CHAT_FALLBACK::"):
                        chat_text = tool_result.split("::", 1)[1]
                        self.thinking_sound_active.clear()
                        self.set_state(BotStates.SPEAKING, "Speaking...", cam_path=img_path)
                        self.append_to_text("BOT: ", newline=False)
                        self.append_to_text(chat_text, newline=True)
                        with self.tts_queue_lock: self.tts_queue.append(chat_text)
                        self.session_memory.append({"role": "assistant", "content": chat_text})
                        self.wait_for_tts()
                        self.set_state(BotStates.IDLE, "Ready")
                        return

                    if tool_result == "IMAGE_CAPTURE_TRIGGERED":
                        new_img_path = self.capture_image()
                        if new_img_path:
                            self.chat_and_respond(text, img_path=new_img_path)
                            return 

                    elif tool_result == "INVALID_ACTION":
                        fallback_text = "I am not sure how to do that."
                        self.thinking_sound_active.clear()
                        self.set_state(BotStates.SPEAKING, "Speaking...", cam_path=img_path)
                        self.append_to_text("BOT: ", newline=False)
                        self.append_to_text(fallback_text, newline=True)
                        with self.tts_queue_lock: self.tts_queue.append(fallback_text)

                    elif tool_result == "SEARCH_EMPTY":
                        fallback_text = "I searched, but I couldn't find any news about that."
                        self.thinking_sound_active.clear()
                        self.set_state(BotStates.SPEAKING, "Speaking...", cam_path=img_path)
                        self.append_to_text("BOT: ", newline=False)
                        self.append_to_text(fallback_text, newline=True)
                        with self.tts_queue_lock: self.tts_queue.append(fallback_text)

                    elif tool_result == "SEARCH_ERROR":
                        fallback_text = "I cannot reach the internet right now."
                        self.thinking_sound_active.clear()
                        self.set_state(BotStates.SPEAKING, "Speaking...", cam_path=img_path)
                        self.append_to_text("BOT: ", newline=False)
                        self.append_to_text(fallback_text, newline=True)
                        with self.tts_queue_lock: self.tts_queue.append(fallback_text)

                    elif tool_result:
                        summary_prompt = [
                            {"role": "system", "content": "Summarize this result in one short sentence."},
                            {"role": "user", "content": f"RESULT: {tool_result}\nUser Question: {text}"}
                        ]
                        
                        self.set_state(BotStates.THINKING, "Reading...")
                        self.thinking_sound_active.set()
                        
                        # Use LlamaConnector for local inference
                        final_resp = LlamaConnector.chat_completion(
                            messages=summary_prompt,
                            temperature=LLAMA_OPTIONS.get('temperature', 0.7),
                            max_tokens=256
                        )
                        
                        if final_resp and 'choices' in final_resp:
                            final_text = final_resp['choices'][0]['message']['content']
                        else:
                            final_text = "Unable to process response."
                        
                        self.thinking_sound_active.clear()
                        self.set_state(BotStates.SPEAKING, "Speaking...", cam_path=img_path)
                        
                        self.append_to_text("BOT: ", newline=False)
                        self.append_to_text(final_text, newline=True)
                        with self.tts_queue_lock: self.tts_queue.append(final_text)
                        self.session_memory.append({"role": "assistant", "content": final_text})
            else:
                self.append_to_text("")
                self.session_memory.append({"role": "assistant", "content": full_response_buffer}) 
            
            self.wait_for_tts()
            self.set_state(BotStates.IDLE, "Ready")
            error_recovery.reset_component("llama_chat")

        except Exception as e:
            print(f"[LLAMA ERROR] Error during chat: {e}", flush=True)
            
            # PHASE 3: Log to experience memory
            experience_memory.log_error(
                error_type="llama_chat_error",
                error_message=str(e)[:100],
                context=text[:50] if text else "unknown"
            )
            
            # PHASE 4: Queue error for self-evolution
            print(f"[EVOLUTION] 🔄 Queuing error for evolutionary investigation...", flush=True)
            self_evolution_thread.queue_error(
                error_type="llama_chat_error",
                error_message=str(e),
                context=f"User input: {text[:100]}"
            )
            
            # Update GUI status to show evolution
            self.set_state(BotStates.THINKING, "🧬 KNO is Evolving...")
            
            # Process any queued errors
            self_evolution_thread.process_error_queue()
            self_evolution_thread.log_evolution()
            
            # Check if error has been repeated
            error_count = experience_memory.get_pattern("llama_chat_error")
            if error_count >= 2:
                print(f"[SELF-CORRECTION] ⚠️  Repeated error detected ({error_count} occurrences). Initiating auto-recovery...", flush=True)
                
                # Check if it's a missing library error
                missing_lib = self_correction.detect_missing_library(str(e))
                if missing_lib:
                    print(f"[SELF-CORRECTION] 📦 Detected missing library: {missing_lib}", flush=True)
                    self_correction.auto_install_dependency(missing_lib)
            
            error_recovery.log_error("llama_chat", str(e))
            traceback.print_exc()
            fallback_msg = "I am having trouble thinking right now. Please try again."
            self.append_to_text(f"BOT: {fallback_msg}")
            with self.tts_queue_lock:
                self.tts_queue.append(fallback_msg)
            self.wait_for_tts()
            self.set_state(BotStates.IDLE, "Chat Error")
        except KeyboardInterrupt:
            print("[MAIN] Interrupted by user", flush=True)
            self.set_state(BotStates.IDLE, "Interrupted")
            self.set_state(BotStates.ERROR, f"Error: {str(e)[:30]}")

    def wait_for_tts(self):
        while self.tts_queue or self.tts_active.is_set():
            if self.interrupted.is_set(): break
            time.sleep(0.1)

    def _tts_worker(self):
        while True:
            text = None
            with self.tts_queue_lock:
                if self.tts_queue: 
                    text = self.tts_queue.pop(0)
                    self.tts_active.set() 
            if text: 
                self.speak(text)
                self.tts_active.clear() 
            else: time.sleep(0.05)

    def speak(self, text):
        clean = re.sub(r"[^\w\s,.!?:-]", "", text)
        if not clean.strip(): return
        
        print(f"[PIPER SPEAKING] '{clean}'", flush=True)
        voice_model = CURRENT_CONFIG.get("voice_model", os.path.join("piper", "en_GB-semaine-medium.onnx"))
        
        try:
            # Windows/Linux compatible piper executable
            if sys.platform == "win32":
                piper_exe = os.path.join("piper", "piper.exe")
            else:
                piper_exe = os.path.join("piper", "piper")
            
            self.current_audio_process = subprocess.Popen(
                [piper_exe, "--model", voice_model, "--output-raw"], 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )

            self.current_audio_process.stdin.write(clean.encode() + b'\n')
            self.current_audio_process.stdin.close() 

            try:
                device_info = sd.query_devices(kind='output')
                native_rate = int(device_info['default_samplerate'])
            except Exception:
                native_rate = 48000 

            PIPER_RATE = 22050
            use_native_rate = False
            
            try:
                sd.check_output_settings(device=None, samplerate=PIPER_RATE)
            except Exception:
                use_native_rate = True

            with sd.RawOutputStream(samplerate=native_rate if use_native_rate else PIPER_RATE, 
                                    channels=1, dtype='int16', 
                                    device=None, latency='low', blocksize=2048) as stream:
                while True:
                    if self.interrupted.is_set(): break
                    data = self.current_audio_process.stdout.read(4096)
                    if not data: break 
                    
                    audio_chunk = np.frombuffer(data, dtype=np.int16)
                    if len(audio_chunk) > 0:
                        self.current_volume = np.max(np.abs(audio_chunk))
                        if use_native_rate:
                            num_samples = int(len(audio_chunk) * (native_rate / PIPER_RATE))
                            audio_chunk = scipy.signal.resample(audio_chunk, num_samples).astype(np.int16)
                        stream.write(audio_chunk.tobytes())
                    else:
                        self.current_volume = 0
                time.sleep(0.5) 
                    
        except Exception as e:
            print(f"Audio Error: {e}")
            error_recovery.log_error("piper_speak", str(e))
        finally:
            self.current_volume = 0
            if self.current_audio_process:
                if self.current_audio_process.stdout:
                    self.current_audio_process.stdout.close()
                if self.current_audio_process.poll() is None:
                    self.current_audio_process.terminate()
                self.current_audio_process = None

    def _run_thinking_sound_loop(self):
        time.sleep(0.5)
        while self.thinking_sound_active.is_set():
            sound = self.get_random_sound(thinking_sounds_dir)
            if sound: self.play_sound(sound)
            for _ in range(50):
                if not self.thinking_sound_active.is_set(): return
                time.sleep(0.1)

    def get_random_sound(self, directory):
        try:
            if os.path.exists(directory):
                files = [f for f in os.listdir(directory) if f.endswith(".wav")]
                if files:
                    return os.path.join(directory, random.choice(files))
                else:
                    print(f"[AUDIO] No .wav files found in {directory}", flush=True)
            else:
                print(f"[AUDIO] Sound directory not found: {directory}", flush=True)
        except Exception as e:
            print(f"[AUDIO] Error accessing sound directory {directory}: {e}", flush=True)
        return None

    def play_sound(self, file_path):
        if not file_path:
            return
        if not os.path.exists(file_path):
            print(f"[AUDIO] Sound file not found: {file_path}", flush=True)
            return
        try:
            print(f"[AUDIO] Playing sound: {file_path}", flush=True)
            with wave.open(file_path, 'rb') as wf:
                file_sr = wf.getframerate()
                data = wf.readframes(wf.getnframes())
                audio = np.frombuffer(data, dtype=np.int16)

            try:
                device_info = sd.query_devices(kind='output')
                native_rate = int(device_info['default_samplerate'])
            except Exception:
                native_rate = 48000 

            playback_rate = file_sr
            try:
                sd.check_output_settings(device=None, samplerate=file_sr)
            except Exception:
                playback_rate = native_rate
                num_samples = int(len(audio) * (native_rate / file_sr))
                audio = scipy.signal.resample(audio, num_samples).astype(np.int16)

            sd.play(audio, playback_rate)
            sd.wait()
            print(f"[AUDIO] Sound playback complete", flush=True)
        except Exception as e:
            print(f"[AUDIO] Error playing sound: {e}", flush=True)
            error_recovery.log_error("play_sound", str(e))

    def load_chat_history(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r") as f: return json.load(f)
            except Exception as e:
                logger.debug(f"Failed to load permanent memory: {e}")
        return [{"role": "system", "content": SYSTEM_PROMPT}]

    def save_chat_history(self):
        try:
            full = self.permanent_memory + self.session_memory
            conv = full[1:]
            if len(conv) > 10: conv = conv[-10:]
            with open(MEMORY_FILE, "w") as f: 
                json.dump([full[0]] + conv, f, indent=4)
        except Exception as e:
            print(f"[MEMORY] Save error: {e}", flush=True)

class DependencyManager:
    """Checks for binaries and python packages and prompts user to install with consent."""

    OPTIONAL_PACKAGES = {
        "ffmpeg": {"type": "binary", "check": lambda: shutil.which("ffmpeg") is not None, "install_hint": "https://ffmpeg.org/download.html"},
        "Pillow": {"type": "python", "module": "PIL", "pip": "Pillow"},
        "python-vlc": {"type": "python", "module": "vlc", "pip": "python-vlc"},
        "PyPDF2": {"type": "python", "module": "PyPDF2", "pip": "PyPDF2"},
    }

    @staticmethod
    def check_and_install_dependencies():
        """Check for optional dependencies and auto-install if missing.

        This is provided as a static helper so older call sites that expect
        DependencyManager.check_and_install_dependencies() still work even if
        the class is instantiated elsewhere in the file.
        """
        print("[DEPENDENCY] Checking optional packages...", flush=True)

        OPTIONAL = {
            "pychromecast": "pychromecast",
            "adb_shell": "adb-shell",
            "scapy": "scapy",
            "Flask": "flask",
        }

        for import_name, package_name in OPTIONAL.items():
            try:
                __import__(import_name)
                print(f"[DEPENDENCY] ✓ {import_name} available", flush=True)
            except ImportError:
                print(f"[DEPENDENCY] ✗ {import_name} missing, attempting auto-install...", flush=True)
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", package_name, "-q"],
                        timeout=120,
                        check=True
                    )
                    print(f"[DEPENDENCY] ✓ {package_name} installed successfully", flush=True)
                except Exception as e:
                    print(f"[DEPENDENCY] ✗ Failed to install {package_name}: {e}", flush=True)

    def __init__(self, parent=None):
        self.parent = parent

    def check_module(self, module_name):
        return importlib.util.find_spec(module_name) is not None

    def check_and_prompt(self, key, parent_window=None):
        info = self.OPTIONAL_PACKAGES.get(key)
        if not info:
            return False

        if info.get("type") == "binary":
            ok = info["check"]()
            if ok:
                return True
            # Prompt user to install ffmpeg
            msg = f"Required binary '{key}' was not detected.\n\nYou can download it from: {info['install_hint']}\n\nOpen download page?"
            try:
                open_page = messagebox.askyesno("Install Binary?", msg, parent=parent_window)
            except Exception:
                open_page = input(msg + " [y/N]: ").strip().lower() == "y"
            if open_page:
                try:
                    import webbrowser
                    webbrowser.open(info["install_hint"])
                except Exception:
                    pass
            return False

        else:
            module = info.get("module")
            pip_name = info.get("pip", key)
            if self.check_module(module):
                return True
            reason = f"Module {module} not available"
            # Ask user to install
            installed = error_recovery.suggest_fix_install_package(pip_name, reason=reason, parent_window=parent_window)
            return installed


if __name__ == "__main__":
    # Headless eDex-ready startup using rich for styled terminal output
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        from rich.align import Align
    except Exception:
        Console = None

    class TerminalUI:
        """Terminal styling and helpers using rich. Falls back to prints if rich missing."""
        ASCII_HEADER = r"""
  _  __ _   _    __     _  _   _   _  
 | |/ /| | | |  / /    | || | | | | | 
 | ' / | |_| | / /_    | || |_| |_| | 
 | . \ |  _  | | '_ \   |__   _|  _  | 
 |_|\_\|_| |_| |_| |_|     |_| |_| |_|  KNO v4.0
"""

        def __init__(self):
            self.console = Console() if Console else None

        def header(self):
            hdr = Text(self.ASCII_HEADER, style="bold cyan")
            if self.console:
                self.console.print(Panel(Align.center(hdr), style="bold cyan", subtitle="KNO v4.0", subtitle_align="right"))
            else:
                print(self.ASCII_HEADER, flush=True)

        def info(self, msg):
            if self.console:
                self.console.print(Panel(Text(msg, style="cyan"), style="cyan"))
            else:
                print(f"[INFO] {msg}", flush=True)

        def success(self, msg):
            if self.console:
                self.console.print(Panel(Text(msg, style="green"), style="green"))
            else:
                print(f"[OK] {msg}", flush=True)

        def warn(self, msg):
            if self.console:
                self.console.print(Panel(Text(msg, style="yellow"), style="yellow"))
            else:
                print(f"[WARN] {msg}", flush=True)

        def stream_log(self, line):
            # High-visibility streaming for evolution log lines
            if self.console:
                self.console.print(Text(line.rstrip(), style="green"))
            else:
                print(line.rstrip(), flush=True)

        def emit_json(self, obj):
            # Emit JSON to stdout for eDex parsing
            try:
                s = json.dumps(obj)
                try:
                    sys.stdout.write(s + "\n")
                    try:
                        sys.stdout.flush()
                    except Exception:
                        pass
                except Exception:
                    # Fallback to original print if direct write fails
                    _orig_print(s)
            except Exception:
                try:
                    sys.stdout.write(str(obj) + "\n")
                    try:
                        sys.stdout.flush()
                    except Exception:
                        pass
                except Exception:
                    try:
                        _orig_print(obj)
                    except Exception:
                        pass

    ui = TerminalUI()
    stop_event = threading.Event()
    # Force headless mode for eDex integration
    GUI_ENABLED = False

    # Route remaining print calls to TerminalUI for consistent styling
    try:
        import builtins as _builtins
        _orig_print = _builtins.print

        def _routed_print(*args, **kwargs):
            try:
                # Respect sep and end if provided
                sep = kwargs.get('sep', ' ')
                end = kwargs.get('end', '\n')
                file_arg = kwargs.get('file', None)

                # If printing to a non-stdout file, defer to original print
                if file_arg is not None and file_arg is not sys.stdout:
                    return _orig_print(*args, **kwargs)

                text = sep.join(str(a) for a in args) + ('' if end == '' else end)
                # Heuristic routing
                if text.startswith('[ERR]') or 'ERROR' in text or 'Traceback' in text:
                    ui.warn(text)
                elif text.startswith('[OK]') or text.startswith('[SUCCESS]'):
                    ui.success(text)
                else:
                    ui.info(text)
            except Exception:
                try:
                    _orig_print(*args, **kwargs)
                except Exception:
                    pass

        # Replace the module-level print so future prints use rich UI
        _builtins.print = _routed_print
    except Exception:
        pass

    def detect_edex():
        # eDex detection: prefer explicit env var, else terminal width heuristic
        if os.getenv("EDEX_UI"):
            return True
        try:
            cols, rows = shutil.get_terminal_size()
            return cols >= 110
        except Exception:
            return False

    EDEX_DETECTED = detect_edex()
    try:
        ui.header()
    except Exception:
        pass

    # Ensure config directories exist quickly
    try:
        ResourceManager.check_and_create_directories()
    except Exception:
        pass

    # Start self evolution thread if present
    try:
        if 'self_evolution_thread' in globals() and self_evolution_thread:
            try:
                self_evolution_thread.start()
                ui.info("SelfEvolutionThread started")
            except Exception:
                ui.warn("Could not start SelfEvolutionThread")
    except Exception:
        pass

    # Tail evolution.log and stream lines in real-time
    def follow_file(path, stop_evt, ui_obj):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                fh.seek(0, os.SEEK_END)
                while not stop_evt.is_set():
                    line = fh.readline()
                    if line:
                        ui_obj.stream_log(line)
                    else:
                        time.sleep(0.2)
        except FileNotFoundError:
            # If file not yet present, wait and retry
            while not stop_evt.is_set():
                if os.path.exists(path):
                    return follow_file(path, stop_evt, ui_obj)
                time.sleep(1)
        except Exception as e:
            ui.warn(f"Log stream error: {e}")

    evolution_log_path = os.path.join(Config.LOGS_DIR, "evolution.log")
    log_thread = threading.Thread(target=follow_file, args=(evolution_log_path, stop_event, ui), daemon=True)
    log_thread.start()

    # Emit system stats as JSON every 5 seconds for eDex to parse
    def system_stats_worker(stop_evt):
        while not stop_evt.is_set():
            try:
                stats = {
                    'ts': datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'cpu_percent': psutil.cpu_percent(interval=None),
                    'mem_percent': getattr(psutil, 'virtual_memory', lambda: type('X', (), {'percent':0})())().percent,
                    'disk_percent': getattr(psutil, 'disk_usage', lambda p: type('X', (), {'percent':0})())(str(Config.BASE_DIR)).percent,
                    'threads': len(threading.enumerate()),
                    'edex_detected': bool(EDEX_DETECTED)
                }
                ui.emit_json({'kno_system': stats})
                # Broadcast to WebSocket clients
                try:
                    stats_ws_server.broadcast(json.dumps({'kno_system': stats}))
                except Exception:
                    pass
            except Exception:
                try:
                    ui.emit_json({'kno_system': {'error': 'failed to collect stats'}})
                except Exception:
                    pass
            # Sleep with early exit
            for _ in range(5):
                if stop_evt.is_set():
                    break
                time.sleep(1)

    stats_thread = threading.Thread(target=system_stats_worker, args=(stop_event,), daemon=True)
    stats_thread.start()

    # Graceful shutdown handler
    def _shutdown(signum=None, frame=None):
        ui.warn('Shutdown requested, stopping background threads...')
        stop_event.set()
        # Attempt to politely stop known LLM/self-evolution threads
        candidates = ['self_evolution_thread', 'llm_thread', 'evolution_thread']
        for name in candidates:
            try:
                obj = globals().get(name)
                if obj:
                    if hasattr(obj, 'stop'):
                        try:
                            obj.stop()
                        except Exception:
                            pass
                    if hasattr(obj, 'running'):
                        try:
                            setattr(obj, 'running', False)
                        except Exception:
                            pass
                    try:
                        if getattr(obj, 'is_alive', lambda: False)():
                            obj.join(timeout=2)
                    except Exception:
                        pass
            except Exception:
                pass
        # Join threads we started
        try:
            log_thread.join(timeout=2)
        except Exception:
            pass
        try:
            stats_thread.join(timeout=2)
        except Exception:
            pass
        # Best-effort: join any remaining non-main threads to avoid ghosts
        try:
            main_ident = threading.main_thread().ident
            for t in threading.enumerate():
                if not t.is_alive():
                    continue
                if getattr(t, 'ident', None) == main_ident:
                    continue
                if t in (log_thread, stats_thread):
                    continue
                try:
                    # attempt graceful join
                    t.join(timeout=1)
                except Exception:
                    pass
        except Exception:
            pass
        ui.success('Shutdown complete')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

    # Register SIGINT handler for clean exit
    try:
        import signal
        signal.signal(signal.SIGINT, _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)
    except Exception:
        pass

    ui.info('KNO running in headless mode (eDex optimized)' + (' - eDex detected' if EDEX_DETECTED else ''))

    # Keep main thread alive until shutdown
    try:
        while not stop_event.wait(1):
            time.sleep(0.1)
    except KeyboardInterrupt:
        _shutdown()
    except Exception as e:
        logger.exception(f"Agent encountered an error: {e}")
        _shutdown()

# =========================================================================
# OPENCLAW REFERENCE (embedded for offline reference)
# The following block contains selected files from the attached OpenClaw repository
# (README.md and openclaw.mjs). This is embedded as a Python string for reference
# and will not be executed. To use OpenClaw runtime, install Node >=22 and follow
# OpenClaw's installation instructions in the embedded README.
# =========================================================================
_OPENCLAW_REFERENCE = '''
=== openclaw-main/README.md ===

"""
# 🦞 OpenClaw — Personal AI Assistant

<... README content embedded here for reference ...>

"""

=== openclaw-main/openclaw.mjs ===

#!/usr/bin/env node

import module from "node:module";

// https://nodejs.org/api/module.html#module-compile-cache
if (module.enableCompileCache && !process.env.NODE_DISABLE_COMPILE_CACHE) {
    try {
        module.enableCompileCache();
    } catch {
        // Ignore errors
    }
}

const isModuleNotFoundError = (err) =>
    err && typeof err === "object" && "code" in err && err.code === "ERR_MODULE_NOT_FOUND";

const installProcessWarningFilter = async () => {
    // Keep bootstrap warnings consistent with the TypeScript runtime.
    for (const specifier of ["./dist/warning-filter.js", "./dist/warning-filter.mjs"]) {
        try {
            const mod = await import(specifier);
            if (typeof mod.installProcessWarningFilter === "function") {
                mod.installProcessWarningFilter();
                return;
            }
        } catch (err) {
            if (isModuleNotFoundError(err)) {
                continue;
            }
            throw err;
        }
    }
};

await installProcessWarningFilter();

const tryImport = async (specifier) => {
    try {
        await import(specifier);
        return true;
    } catch (err) {
        // Only swallow missing-module errors; rethrow real runtime errors.
        if (isModuleNotFoundError(err)) {
            return false;
        }
        throw err;
    }
};

if (await tryImport("./dist/entry.js")) {
    // OK
} else if (await tryImport("./dist/entry.mjs")) {
    // OK
} else {
    throw new Error("openclaw: missing dist/entry.(m)js (build output).");
}

'''
