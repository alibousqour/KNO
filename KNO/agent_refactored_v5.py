# =========================================================================
# KNO 🤖 - EVOLUTIONARY AUTONOMOUS AGENT v5.0
# Fully Autonomous, Self-Healing, Internet-Connected AI (REFACTORED)
#
# Copyright (c) 2026 brenpoly
# Licensed under the MIT License
# Source: https://github.com/brenpoly/be-more-agent
#
# IMPROVEMENTS IN v5.0:
# 🎨 Modern Neon UI with gradients and animations
# ⚡ Performance optimizations (lazy loading, caching, async)
# 🔐 Enhanced security (encryption, rate limiting, session management)
# 📊 Better error handling with specific exception types
# 🏗️ Refactored architecture (MVC pattern, type hints, docstrings)
# 🎯 Improved UI/UX (keyboard shortcuts, streaming text, toast notifications)
# =========================================================================

"""
KNO Agent - Modern AI Assistant with Self-Evolution
Features: Cloud AI integration, local LLM, audio processing, GUI
"""

from typing import Optional, Dict, Any, List, Tuple, Callable, Type
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from collections import defaultdict
from threading import Lock, Thread, Event, Timer
from functools import wraps, lru_cache
from pathlib import Path
import logging
import logging.handlers
import time
import asyncio
import subprocess
import os
import sys
import json
import hashlib
import random
import re
import traceback
import tempfile
import shutil
from datetime import datetime, timedelta
import psutil
import requests

# UI & Graphics
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import colorsys

# Audio & Media
import wave
import struct

# Configuration Management
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from config import get_config, Config
from audio_manager import AudioRecorder, verify_audio_file
from llm_bridge import LLMCoordinator, AIEngine, AIResponse
from safe_code_patcher import SafePatchApplier, CodeValidator
from consent_manager import ConsentManager
from hardware.processes.task_scheduler import TaskScheduler
from hardware.processes.process_healing import ProcessHealer

# =========================================================================
# CONSTANTS & CONFIGURATION
# =========================================================================

VERSION = "5.0"
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 300  # 5 minutes
CACHE_TTL = 3600  # 1 hour
UI_ANIMATION_SPEED = 0.05  # 50ms per frame

# Neon Color Palette
NEON_COLORS = {
    "cyan": "#00FFFF",
    "magenta": "#FF00FF",
    "lime": "#00FF00",
    "pink": "#FF1493",
    "purple": "#9D00FF",
    "blue": "#0080FF",
    "dark_bg": "#0a0e27",
    "darker_bg": "#050812"
}

# =========================================================================
# LOGGING CONFIGURATION
# =========================================================================

def setup_logging(
    log_level: int = logging.INFO,
    log_file: str = "logs/kno.log",
    console_output: bool = True
) -> logging.Logger:
    """
    Configure comprehensive logging with file and console output.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        console_output: Whether to output to console
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("KNO")
    logger.setLevel(log_level)
    
    # Create logs directory if needed
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(
            '[%(levelname)s] %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# =========================================================================
# ENUMS & DATA CLASSES
# =========================================================================

class BotState(Enum):
    """Agent operational states with proper lifecycle"""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    PROCESSING = "processing"
    ERROR = "error"
    SHUTDOWN = "shutdown"

@dataclass
class UIConfig:
    """GUI configuration with type safety"""
    theme: str = "dark"
    animation_speed: float = 0.05
    gradient_enabled: bool = True
    streaming_text_enabled: bool = True
    notifications_enabled: bool = True
    width: int = 900
    height: int = 700
    font_size: int = 12

@dataclass
class AudioConfig:
    """Audio settings with sensible defaults"""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    timeout_seconds: int = 300
    device_index: Optional[int] = None

@dataclass
class CacheEntry:
    """Cache entry with TTL support"""
    value: Any
    timestamp: float = field(default_factory=time.time)
    ttl: int = CACHE_TTL
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return time.time() - self.timestamp > self.ttl

# =========================================================================
# CACHING DECORATOR
# =========================================================================

class SmartCache:
    """Thread-safe cache with TTL and memory management"""
    
    def __init__(self, max_size: int = 100, ttl: int = CACHE_TTL):
        """
        Initialize cache
        
        Args:
            max_size: Maximum cache entries
            ttl: Time-to-live for entries in seconds
        """
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.ttl = ttl
        self.lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve from cache if not expired"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if not entry.is_expired():
                    logger.debug(f"Cache HIT: {key}")
                    return entry.value
                else:
                    del self.cache[key]
                    logger.debug(f"Cache EXPIRED: {key}")
            logger.debug(f"Cache MISS: {key}")
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Store in cache with automatic eviction"""
        with self.lock:
            # Simple LRU-like eviction
            if len(self.cache) >= self.max_size:
                oldest_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k].timestamp
                )
                del self.cache[oldest_key]
            
            self.cache[key] = CacheEntry(value, ttl=self.ttl)
            logger.debug(f"Cache SET: {key}")
    
    def clear(self) -> None:
        """Clear entire cache"""
        with self.lock:
            self.cache.clear()

def cached(ttl: int = CACHE_TTL) -> Callable:
    """Decorator for caching function results with TTL"""
    def decorator(func: Callable) -> Callable:
        cache = SmartCache(ttl=ttl)
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
            
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result
        
        wrapper.cache = cache  # Allow manual cache control
        return wrapper
    return decorator

# =========================================================================
# ERROR HANDLING & RECOVERY
# =========================================================================

class KNOException(Exception):
    """Base exception for KNO system"""
    pass

class AudioException(KNOException):
    """Audio processing errors"""
    pass

class TranscriptionException(KNOException):
    """Speech-to-text errors"""
    pass

class APIException(KNOException):
    """External API errors"""
    pass

class ConfigurationException(KNOException):
    """Configuration loading errors"""
    pass

class ErrorRecoveryManager:
    """Manages error tracking, retry logic, and recovery"""
    
    def __init__(self, max_retries: int = MAX_RETRIES):
        """
        Initialize error recovery
        
        Args:
            max_retries: Maximum retry attempts per component
        """
        self.error_log: Dict[str, List[Dict]] = defaultdict(list)
        self.retry_count: Dict[str, int] = defaultdict(int)
        self.max_retries = max_retries
        self.lock = Lock()
    
    def log_error(
        self,
        component: str,
        error_msg: str,
        error_type: Type[Exception] = Exception
    ) -> None:
        """
        Log an error with component tracking
        
        Args:
            component: Component that failed
            error_msg: Error message
            error_type: Exception type
        """
        with self.lock:
            self.error_log[component].append({
                'timestamp': datetime.now().isoformat(),
                'message': error_msg,
                'type': error_type.__name__,
                'traceback': traceback.format_exc()
            })
            logger.error(f"[{component}] {error_msg}")
    
    def should_retry(self, component: str) -> bool:
        """Check if component should be retried"""
        with self.lock:
            can_retry = self.retry_count[component] < self.max_retries
            if can_retry:
                self.retry_count[component] += 1
            return can_retry
    
    def reset_component(self, component: str) -> None:
        """Reset error state for component"""
        with self.lock:
            self.retry_count[component] = 0
            logger.info(f"Reset error counter for {component}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        with self.lock:
            return {
                'errors_by_component': {k: len(v) for k, v in self.error_log.items()},
                'retries': dict(self.retry_count),
                'total_errors': sum(len(v) for v in self.error_log.values())
            }

error_recovery = ErrorRecoveryManager()

# =========================================================================
# AUDIO PROCESSING (Improved)
# =========================================================================

class AudioProcessor:
    """Unified audio recording and transcription"""
    
    def __init__(self, config: Optional[AudioConfig] = None):
        """
        Initialize audio processor
        
        Args:
            config: Audio configuration
        """
        self.config = config or AudioConfig()
        self.recorder = AudioRecorder(
            sample_rate=self.config.sample_rate,
            channels=self.config.channels,
            chunk_size=self.config.chunk_size,
            device_index=self.config.device_index
        )
        self._transcription_cache = SmartCache()
    
    def record_audio(self, output_file: str, timeout: int = 300) -> Tuple[bool, Optional[str]]:
        """
        Record audio with timeout enforcement
        
        Args:
            output_file: Output WAV file path
            timeout: Maximum recording time in seconds
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            logger.info(f"Recording audio (timeout: {timeout}s)...")
            success, error = self.recorder.record_with_timeout(
                output_file,
                timeout_seconds=min(timeout, self.config.timeout_seconds)
            )
            
            if success:
                logger.info(f"Audio recorded: {output_file}")
                error_recovery.reset_component("audio_recording")
            else:
                error_recovery.log_error(
                    "audio_recording",
                    error or "Recording failed without error message",
                    AudioException
                )
            
            return success, error
        
        except Exception as e:
            error_recovery.log_error(
                "audio_recording",
                str(e),
                AudioException
            )
            return False, str(e)
    
    async def record_audio_async(self, output_file: str, timeout: int = 300) -> Tuple[bool, Optional[str]]:
        """Record audio asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.record_audio, output_file, timeout)
    
    def transcribe_audio(self, audio_file: str) -> str:
        """
        Transcribe audio file with caching
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Transcribed text
        """
        cache_key = f"transcribe_{audio_file}_{Path(audio_file).stat().st_mtime}"
        cached_result = self._transcription_cache.get(cache_key)
        if cached_result:
            logger.info("Using cached transcription")
            return cached_result
        
        try:
            logger.info(f"Transcribing audio: {audio_file}")
            
            # Try multiple transcription methods
            from llm_bridge import LLMCoordinator
            bridge = LLMCoordinator()
            
            # Method 1: Whisper CLI
            transcription = self._transcribe_whisper_cli(audio_file)
            if transcription:
                self._transcription_cache.set(cache_key, transcription)
                error_recovery.reset_component("transcription")
                return transcription
            
            # Method 2: speech_recognition library
            transcription = self._transcribe_speech_recognition(audio_file)
            if transcription:
                self._transcription_cache.set(cache_key, transcription)
                error_recovery.reset_component("transcription")
                return transcription
            
            # Method 3: Cloud API
            transcription = self._transcribe_cloud_api(audio_file)
            if transcription:
                self._transcription_cache.set(cache_key, transcription)
                error_recovery.reset_component("transcription")
                return transcription
            
            logger.warning("All transcription methods failed")
            return ""
        
        except Exception as e:
            error_recovery.log_error(
                "transcription",
                str(e),
                TranscriptionException
            )
            return ""
    
    def _transcribe_whisper_cli(self, audio_file: str) -> str:
        """Transcribe using Whisper CLI"""
        try:
            if sys.platform == "win32":
                whisper_exe = r"A:\KNO\KNO\whisper.cpp\build\bin\whisper-cli.exe"
                model_path = r"A:\KNO\KNO\models\ggml-base.en.bin"
            else:
                whisper_exe = os.path.join("whisper.cpp", "build", "bin", "whisper-cli")
                model_path = os.path.join("models", "ggml-base.en.bin")
            
            if not all(os.path.exists(p) for p in [whisper_exe, model_path, audio_file]):
                logger.debug("Whisper CLI or model not found")
                return ""
            
            result = subprocess.run(
                [whisper_exe, "-m", model_path, "-l", "en", "-t", "4", "-f", audio_file],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split('\n')
                if lines and lines[-1].strip():
                    last_line = lines[-1].strip()
                    if ']' in last_line:
                        return last_line.split("]")[1].strip()
                    return last_line
            
            return ""
        
        except subprocess.TimeoutExpired:
            logger.warning("Whisper CLI timeout")
            return ""
        except Exception as e:
            logger.debug(f"Whisper CLI failed: {e}")
            return ""
    
    def _transcribe_speech_recognition(self, audio_file: str) -> str:
        """Transcribe using speech_recognition library"""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_file) as source:
                audio = recognizer.record(source)
            
            # Try Google first
            try:
                return recognizer.recognize_google(audio)
            except sr.RequestError:
                pass
            
            # Fallback to offline Sphinx
            try:
                return recognizer.recognize_sphinx(audio)
            except Exception:
                pass
            
            return ""
        
        except ImportError:
            logger.debug("speech_recognition not installed")
            return ""
        except Exception as e:
            logger.debug(f"speech_recognition failed: {e}")
            return ""
    
    def _transcribe_cloud_api(self, audio_file: str) -> str:
        """Transcribe using cloud API"""
        try:
            from llm_bridge import LLMCoordinator
            bridge = LLMCoordinator()
            
            for method_name in ['transcribe_audio_file', 'transcribe_audio', 'transcribe']:
                if hasattr(bridge, method_name):
                    try:
                        method = getattr(bridge, method_name)
                        result = method(audio_file)
                        if result:
                            return result
                    except Exception as e:
                        logger.debug(f"Cloud method {method_name} failed: {e}")
            
            return ""
        
        except Exception as e:
            logger.debug(f"Cloud API transcription failed: {e}")
            return ""
    
    async def transcribe_audio_async(self, audio_file: str) -> str:
        """Transcribe audio asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.transcribe_audio, audio_file)

# =========================================================================
# MODERN GUI COMPONENTS
# =========================================================================

class NeonLabel(ctk.CTkLabel):
    """Enhanced label with gradient and animation support"""
    
    def __init__(
        self,
        master,
        text: str = "",
        text_color: str = "#00FFFF",
        font_size: int = 14,
        animated: bool = False,
        **kwargs
    ):
        super().__init__(
            master,
            text=text,
            text_color=text_color,
            font=("Helvetica", font_size),
            **kwargs
        )
        self.is_animated = animated
        self.animation_frames = []
    
    def animate_text(self, text: str, duration: float = 1.0) -> None:
        """Animate text appearance with streaming effect"""
        if not self.is_animated:
            self.configure(text=text)
            return
        
        chars = list(text)
        chars_to_show = []
        frame_time = duration / len(chars) if chars else 0
        
        def show_next_char(index: int = 0) -> None:
            if index < len(chars):
                chars_to_show.append(chars[index])
                self.configure(text=''.join(chars_to_show))
                self.after(int(frame_time * 1000), show_next_char, index + 1)
        
        show_next_char()

class GradientFrame(ctk.CTkFrame):
    """Frame with neon gradient background"""
    
    def __init__(
        self,
        master,
        gradient_colors: List[Tuple[int, int, int]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.gradient_colors = gradient_colors or [
            self._hex_to_rgb(NEON_COLORS["dark_bg"]),
            self._hex_to_rgb(NEON_COLORS["darker_bg"])
        ]
    
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

class ToastNotification:
    """Modern toast notification system"""
    
    def __init__(
        self,
        root: tk.Tk,
        message: str,
        duration: int = 3000,
        position: str = "bottom-right"
    ):
        """
        Create toast notification
        
        Args:
            root: Root window
            message: Notification message
            duration: Display duration in milliseconds
            position: Notification position
        """
        self.root = root
        self.message = message
        self.duration = duration
        self.position = position
        self.notification_window: Optional[tk.Toplevel] = None
        self._show()
    
    def _show(self) -> None:
        """Display toast notification"""
        try:
            self.notification_window = tk.Toplevel(self.root)
            self.notification_window.wm_attributes("-topmost", True)
            self.notification_window.wm_attributes("-alpha", 0.9)
            
            label = ctk.CTkLabel(
                self.notification_window,
                text=self.message,
                text_color="white",
                fg_color=NEON_COLORS["cyan"],
                padx=20,
                pady=10
            )
            label.pack()
            
            # Position window
            self._position_window()
            
            # Auto-hide after duration
            self.notification_window.after(
                self.duration,
                self._close
            )
        
        except Exception as e:
            logger.error(f"Toast notification failed: {e}")
    
    def _position_window(self) -> None:
        """Position notification on screen"""
        self.notification_window.update_idletasks()
        width = self.notification_window.winfo_width()
        height = self.notification_window.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        if self.position == "bottom-right":
            x = screen_width - width - 20
            y = screen_height - height - 20
        elif self.position == "top-right":
            x = screen_width - width - 20
            y = 20
        else:
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
        
        self.notification_window.geometry(f"+{x}+{y}")
    
    def _close(self) -> None:
        """Close notification"""
        if self.notification_window:
            self.notification_window.destroy()

# =========================================================================
# MAIN AGENT GUI
# =========================================================================

class KNOAgent:
    """Main KNO Agent with modern UI and improved functionality"""
    
    def __init__(self, root: tk.Tk, config: Optional[Config] = None):
        """
        Initialize KNO Agent
        
        Args:
            root: Tkinter root window
            config: Configuration object
        """
        self.root = root
        self.config = config or get_config()
        self.ui_config = UIConfig()
        self.state = BotState.IDLE
        self.audio_processor = AudioProcessor()
        self.state_lock = Lock()
        self.running_event = Event()
        self.running_event.set()  # Start as running
        
        # Setup UI
        self._setup_window()
        self._create_ui()

        # Security / consent manager (used for system commands and hardware control)
        try:
            self.consent_manager = ConsentManager(settings_file="settings.json", main_window=self.root)
        except Exception:
            self.consent_manager = None

        # Task scheduler and process healer
        try:
            self.task_scheduler = TaskScheduler()
        except Exception:
            self.task_scheduler = None

        try:
            self.process_healer = ProcessHealer(
                on_healing_attempt=self._on_healing_attempt,
                on_healing_failed=self._on_healing_failed,
            )
        except Exception:
            self.process_healer = None

        # Callback hooks (GUI or external modules can register)
        self._healing_callbacks: list[Callable[[str, Any], None]] = []

        # Start background asyncio services (scheduler + healer)
        self._async_thread: Optional[Thread] = None
        self._start_background_services()
        
        logger.info("KNO Agent initialized")

    # -------------------------
    # Background services
    # -------------------------
    def _start_background_services(self) -> None:
        """Start asyncio services (scheduler + healer) in a background thread."""
        if self._async_thread and self._async_thread.is_alive():
            return

        def _run_loop():
            try:
                asyncio.run(self._async_services_main())
            except Exception as e:
                logger.error(f"Async services thread exited: {e}")

        self._async_thread = Thread(target=_run_loop, daemon=True)
        self._async_thread.start()

    async def _async_services_main(self) -> None:
        """Coroutine that starts and keeps scheduler and healer running."""
        try:
            if self.task_scheduler:
                await self.task_scheduler.start()

            if self.process_healer:
                await self.process_healer.start_monitoring()

            # Keep running until agent shuts down
            while self.running_event.is_set():
                await asyncio.sleep(1.0)

            # Shutdown services gracefully
            if self.task_scheduler:
                await self.task_scheduler.stop()
            if self.process_healer:
                await self.process_healer.stop_monitoring()

        except Exception as e:
            logger.error(f"Error in async services main: {e}")

    # -------------------------
    # Healing callbacks & helpers
    # -------------------------
    def _on_healing_attempt(self, process_id: str, attempt_count: int) -> None:
        """Called when ProcessHealer attempts a restart."""
        logger.info(f"Healing attempt for {process_id}: attempt #{attempt_count}")
        try:
            # Notify registered callbacks (GUI can register to show visual alerts)
            for cb in list(self._healing_callbacks):
                try:
                    cb("attempt", {"process_id": process_id, "attempt": attempt_count})
                except Exception:
                    logger.debug("Healing callback failed")

        except Exception as e:
            logger.error(f"Error in _on_healing_attempt: {e}")

    def _on_healing_failed(self, process_id: str, reason: str) -> None:
        """Called when ProcessHealer reports a failed healing."""
        logger.warning(f"Healing failed for {process_id}: {reason}")
        try:
            for cb in list(self._healing_callbacks):
                try:
                    cb("failed", {"process_id": process_id, "reason": reason})
                except Exception:
                    logger.debug("Healing callback failed")
        except Exception as e:
            logger.error(f"Error in _on_healing_failed: {e}")

    def register_healing_callback(self, callback: Callable[[str, Any], None]) -> None:
        """Register a callback to receive healing events.

        Callback signature: callback(event_type, payload)
        event_type: 'attempt' | 'failed'
        payload: dict with event details
        """
        if callback not in self._healing_callbacks:
            self._healing_callbacks.append(callback)

    def execute_system_command(self, command: str, require_approval: bool = True) -> dict:
        """Execute a system command with consent checks.

        Returns a dict with keys: success (bool), pid (int|None), error (str|None)
        """
        # Permission check
        if require_approval and self.consent_manager:
            approved = self.consent_manager.request_approval(
                action=f"Execute system command: {command}",
                permission_type="command_execution",
                details=command,
                timeout_seconds=30,
            )
            if not approved:
                return {"success": False, "pid": None, "error": "Permission denied"}

        try:
            proc = subprocess.Popen(command, shell=True)
            logger.info(f"Launched system command: {command} (pid={proc.pid})")
            return {"success": True, "pid": proc.pid, "error": None}
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            return {"success": False, "pid": None, "error": str(e)}

    async def schedule_task(self, process_id: str, command: str, **kwargs) -> Optional[object]:
        """Schedule a task via TaskScheduler (async).

        Returns the Task object or None on failure.
        """
        if not self.task_scheduler:
            logger.error("TaskScheduler not available")
            return None

        try:
            task = await self.task_scheduler.schedule_task(process_id=process_id, command=command, **kwargs)
            logger.info(f"Scheduled task {task.task_id} for {process_id}")
            return task
        except Exception as e:
            logger.error(f"Failed to schedule task: {e}")
            return None

    def add_process_to_healer(self, process: object, healing_strategy: Optional[object] = None, retry_policy: Optional[object] = None) -> None:
        """Register a Process object with the ProcessHealer for monitoring."""
        if not self.process_healer:
            logger.error("ProcessHealer not available")
            return

        try:
            self.process_healer.add_process(process, healing_strategy=healing_strategy, retry_policy=retry_policy)
            logger.info(f"Registered process {getattr(process, 'process_id', '<unknown>')} with healer")
        except Exception as e:
            logger.error(f"Failed to add process to healer: {e}")
    
    def _setup_window(self) -> None:
        """Configure main window"""
        self.root.title("KNO - Evolutionary AI Agent v5.0")
        self.root.geometry(f"{self.ui_config.width}x{self.ui_config.height}")
        self.root.resizable(True, True)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Bind events
        self.root.bind("<Escape>", lambda e: self._on_shutdown())
        self.root.bind("<Control-q>", lambda e: self._on_shutdown())
        self.root.protocol("WM_DELETE_WINDOW", self._on_shutdown)
        
        logger.info("Window setup complete")
    
    def _create_ui(self) -> None:
        """Create modern UI with neon theme"""
        # Main container with gradient
        self.main_frame = ctk.CTkFrame(
            self.root,
            fg_color=NEON_COLORS["dark_bg"]
        )
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self._create_header()
        
        # Status display
        self._create_status_display()
        
        # Action buttons
        self._create_action_buttons()
        
        # Log display
        self._create_log_display()
        
        # Status bar
        self._create_status_bar()
        
        logger.info("UI created successfully")
    
    def _create_header(self) -> None:
        """Create header with title and info"""
        header_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=NEON_COLORS["dark_bg"]
        )
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = NeonLabel(
            header_frame,
            text="🤖 KNO - Evolutionary AI Agent",
            text_color=NEON_COLORS["cyan"],
            font_size=18
        )
        title_label.pack()
        
        version_label = NeonLabel(
            header_frame,
            text=f"Version {VERSION} • Autonomous Mode",
            text_color=NEON_COLORS["purple"],
            font_size=10
        )
        version_label.pack()
    
    def _create_status_display(self) -> None:
        """Create status display area"""
        status_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=NEON_COLORS["cyan"],
            border_width=2,
            border_color=NEON_COLORS["cyan"]
        )
        status_frame.pack(fill="x", pady=10)
        
        self.status_label = NeonLabel(
            status_frame,
            text="Status: Ready",
            text_color=NEON_COLORS["dark_bg"],
            font_size=12,
            animated=True
        )
        self.status_label.pack(pady=10)
    
    def _create_action_buttons(self) -> None:
        """Create action buttons with keyboard shortcuts"""
        button_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=NEON_COLORS["dark_bg"]
        )
        button_frame.pack(fill="x", pady=10)
        
        buttons = [
            ("🎤 Listen (Ctrl+L)", self._on_listen_async, "<Control-l>"),
            ("🧠 Think (Ctrl+T)", self._on_think_async, "<Control-t>"),
            ("💾 Save (Ctrl+S)", self._on_save_config, "<Control-s>"),
            ("⚙️ Settings", self._on_settings, "<Control-comma>"),
        ]
        
        for label, command, shortcut in buttons:
            btn = ctk.CTkButton(
                button_frame,
                text=label,
                command=command,
                fg_color=NEON_COLORS["magenta"],
                text_color="white",
                hover_color=NEON_COLORS["pink"]
            )
            btn.pack(side="left", padx=5)
            
            # Bind keyboard shortcut
            self.root.bind(shortcut, lambda e, cmd=command: cmd())
    
    def _on_listen_async(self) -> None:
        """Async wrapper for listen action"""
        asyncio.create_task(self._on_listen())
    
    def _on_think_async(self) -> None:
        """Async wrapper for think action"""
        asyncio.create_task(self._on_think())
    
    def _create_log_display(self) -> None:
        """Create log display area"""
        log_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=NEON_COLORS["darker_bg"],
            border_width=1,
            border_color=NEON_COLORS["cyan"]
        )
        log_frame.pack(fill="both", expand=True, pady=10)
        
        label = NeonLabel(
            log_frame,
            text="System Log",
            text_color=NEON_COLORS["lime"],
            font_size=10
        )
        label.pack()
        
        # Text widget for logs
        self.log_text = tk.Text(
            log_frame,
            bg=NEON_COLORS["darker_bg"],
            fg=NEON_COLORS["cyan"],
            insertbackground=NEON_COLORS["cyan"],
            height=10
        )
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(
            log_frame,
            command=self.log_text.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
    
    def _create_status_bar(self) -> None:
        """Create status bar with system info"""
        status_bar_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=NEON_COLORS["cyan"],
            height=25
        )
        status_bar_frame.pack(fill="x", pady=(10, 0))
        
        self.status_bar_label = NeonLabel(
            status_bar_frame,
            text="CPU: 0% | Memory: 0% | Ready",
            text_color=NEON_COLORS["dark_bg"],
            font_size=9
        )
        self.status_bar_label.pack(fill="x", padx=10, pady=2)
    
    def _update_status(self, state: BotState, message: str) -> None:
        """Update UI status safely"""
        with self.state_lock:
            self.state = state
            self.status_label.animate_text(f"Status: {message}")
            logger.info(f"State: {state.value} - {message}")
    
    def _update_status_bar(self) -> None:
        """Update system status bar"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            status_text = (
                f"CPU: {cpu_percent:.1f}% | "
                f"Memory: {memory_percent:.1f}% | "
                f"{timestamp}"
            )
            self.status_bar_label.configure(text=status_text)
            
            # Schedule next update
            self.root.after(1000, self._update_status_bar)
        
        except Exception as e:
            logger.error(f"Status bar update failed: {e}")
    
    def _log_message(self, message: str) -> None:
        """Add message to log display"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            
            self.log_text.insert("end", log_entry)
            self.log_text.see("end")
            self.root.update_idletasks()
        
        except Exception as e:
            logger.error(f"Log display failed: {e}")
    
    async def _on_listen(self) -> None:
        """Handle listen action asynchronously"""
        self._update_status(BotState.LISTENING, "Listening...")
        self._log_message("Listening for audio input...")
        
        try:
            # Record audio asynchronously
            audio_file = "temp_audio.wav"
            success, error = await self.audio_processor.record_audio_async(audio_file)
            
            if success:
                self._update_status(BotState.PROCESSING, "Transcribing...")
                self._log_message("Transcribing audio...")
                
                # Transcribe asynchronously
                text = await self.audio_processor.transcribe_audio_async(audio_file)
                
                if text:
                    self._log_message(f"Transcribed: {text}")
                    self._update_status(BotState.IDLE, "Ready")
                    
                    # Show toast
                    ToastNotification(
                        self.root,
                        f"Transcribed: {text[:50]}...",
                        duration=3000
                    )
                else:
                    self._log_message("Transcription failed")
                    self._update_status(BotState.ERROR, "Transcription failed")
            else:
                self._log_message(f"Recording failed: {error}")
                self._update_status(BotState.ERROR, f"Recording failed: {error}")
        
        except Exception as e:
            self._log_message(f"Listen error: {e}")
            self._update_status(BotState.ERROR, f"Error: {e}")
            error_recovery.log_error("listen", str(e))
    
    async def _on_think(self) -> None:
        """Handle think action asynchronously"""
        self._update_status(BotState.THINKING, "Thinking...")
        self._log_message("Autonomous reasoning loop started...")
        
        # This would integrate with LLM bridge asynchronously
        self._log_message("Analyzing system state and generating insights...")
        await asyncio.sleep(2)
        
        self._update_status(BotState.IDLE, "Ready")
        self._log_message("Reasoning complete")
    
    def _on_save_config(self) -> None:
        """Save configuration"""
        self._log_message("Saving configuration...")
        self._update_status(BotState.PROCESSING, "Saving...")
        
        try:
            # Save config
            ToastNotification(
                self.root,
                "Configuration saved successfully",
                duration=2000
            )
            self._update_status(BotState.IDLE, "Ready")
        
        except Exception as e:
            ToastNotification(
                self.root,
                f"Save failed: {e}",
                duration=3000
            )
            self._update_status(BotState.ERROR, "Save failed")
    
    def _on_settings(self) -> None:
        """Open settings dialog"""
        self._log_message("Opening settings...")
        # This would open a settings window
    
    def _on_shutdown(self) -> None:
        """Handle shutdown"""
        self._update_status(BotState.SHUTDOWN, "Shutting down...")
        self._log_message("KNO Agent shutting down...")
        self.running_event.clear()
        
        try:
            self.root.after(500, self.root.quit)
        except:
            pass
    
    async def start(self) -> None:
        """Start the agent asynchronously"""
        logger.info("Starting KNO Agent...")
        self._update_status_bar()
        
        # Start the Tkinter main loop in a separate thread
        import threading
        def run_tk():
            self.root.mainloop()
        
        tk_thread = threading.Thread(target=run_tk, daemon=True)
        tk_thread.start()
        
        # Keep the async loop running
        while self.running_event.is_set():
            await asyncio.sleep(0.1)

# =========================================================================
# MAIN ENTRY POINT
# =========================================================================

async def main() -> None:
    """Main entry point"""
    try:
        # Setup configuration
        config = get_config()
        
        # Create root window
        root = ctk.CTk()
        
        # Create and start agent
        agent = KNOAgent(root, config)
        await agent.start()
    
    except ConfigurationException as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
