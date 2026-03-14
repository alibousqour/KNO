"""
KNO_V2.py

Unified single-file AI system merging KNO core logic with OpenClaw-style
computer-use capabilities (vision + GUI actions).

Features included:
- Consolidated imports
- ResourceManager that checks/installs dependencies
- HigherIntelligenceBridge (text + image analysis via Gemini 1.5 Flash)
- VisionModule (screenshot capture + image bytes)
- ActionExecutor (pyautogui wrapper)
- SelfEvolutionThread integrating visual recovery
- BotGUI with 'Eye' indicator and Direct Action console

This file is intentionally self-contained and defensive when optional
dependencies are missing.
"""
from __future__ import annotations

import os
import sys
import io
import time
import json
import threading
import queue
import subprocess
import logging
import base64
from pathlib import Path
from typing import Optional, Tuple

try:
    # Prefer requests for HTTP; fall back to urllib if missing
    import requests
    requests_available = True
except Exception:
    requests = None
    requests_available = False

# Optional runtime dependencies
try:
    from PIL import Image, ImageGrab
    pil_available = True
except Exception:
    Image = None
    ImageGrab = None
    pil_available = False

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.3
    pyautogui_available = True
except Exception:
    pyautogui = None
    pyautogui_available = False

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext
    tk_available = True
except Exception:
    tk = None
    ttk = None
    scrolledtext = None
    tk_available = False

# Root directory (absolute path requirement)
ROOT_DIR = r"A:\\KNO"

# Ensure working directory and OpenClaw path are discoverable
try:
    os.chdir(ROOT_DIR)
except Exception:
    # If chdir fails, continue but log later
    pass

# Add openclaw-main to sys.path so any optional imports can be discovered
openclaw_path = os.path.join(ROOT_DIR, 'openclaw-main')
if openclaw_path not in sys.path:
    sys.path.append(openclaw_path)

# Logging: write to A:\KNO\logs/kno_v2.log and console
log_dir = os.path.join(ROOT_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'kno_v2.log')
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("KNO_V2")
try:
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(fh)
except Exception:
    pass

# Load or create config.json in ROOT_DIR
CONFIG_PATH = os.path.join(ROOT_DIR, 'config.json')
default_config = {
    "GOOGLE_API_KEY": "YOUR_KEY_HERE",
    "VISION_ENABLED": True,
    "LOG_LEVEL": "INFO",
    "FAILSAFE_CORNERS": True
}
config = {}
if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as cf:
            config = json.load(cf)
    except Exception:
        config = {}
else:
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as cf:
            json.dump(default_config, cf, indent=2)
        logger.info(f"Created config template at {CONFIG_PATH}. Please add your GOOGLE_API_KEY.")
        config = default_config.copy()
    except Exception as e:
        logger.warning(f"Failed to create config.json template: {e}")

# Apply log level from config if present
try:
    lvl = config.get('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(getattr(logging, lvl, logging.INFO))
    fh.setLevel(getattr(logging, lvl, logging.INFO))
except Exception:
    pass


class ResourceManager:
    """Check and install required dependencies for KNO_V2."""

    REQUIRED_PYPI = {
        "pillow": "Pillow (PIL) for screenshots and image handling",
        "pyautogui": "pyautogui for GUI automation",
        "requests": "requests for HTTP calls",
    }

    @staticmethod
    def check_and_create_directories():
        dirs = [os.path.join(ROOT_DIR, "logs"), os.path.join(ROOT_DIR, "screenshots"), os.path.join(ROOT_DIR, "temp_vision")]
        for d in dirs:
            try:
                Path(d).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(f"Failed to create directory {d}: {e}")

    @staticmethod
    def check_dependencies() -> dict:
        status = {}
        status['requests'] = requests_available
        status['pillow'] = pil_available
        status['pyautogui'] = pyautogui_available
        return status

    @staticmethod
    def try_install(package: str) -> bool:
        """Attempt `pip install package` in current Python environment."""
        try:
            logger.info(f"Attempting to install {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            logger.info(f"Installed {package}")
            return True
        except Exception as e:
            logger.warning(f"Auto-install failed for {package}: {e}")
            return False

    @classmethod
    def ensure_dependencies(cls):
        status = cls.check_dependencies()
        for pkg, desc in cls.REQUIRED_PYPI.items():
            key = 'pillow' if pkg == 'pillow' else pkg
            if not status.get(key, False):
                installed = cls.try_install(pkg)
                if installed:
                    # best-effort import refresh
                    try:
                        if pkg == 'pillow':
                            from PIL import Image, ImageGrab  # type: ignore
                            globals()['Image'] = Image
                            globals()['ImageGrab'] = ImageGrab
                        elif pkg == 'pyautogui':
                            import pyautogui as _pg  # type: ignore
                            _pg.FAILSAFE = True
                            globals()['pyautogui'] = _pg
                        elif pkg == 'requests':
                            import requests as _req  # type: ignore
                            globals()['requests'] = _req
                    except Exception:
                        pass
    @classmethod
    def scan_local_models(cls, base_path: Optional[str] = None) -> dict:
        """Scan for local LLM models and config files (best-effort). Scans ROOT_DIR by default."""
        base = base_path or ROOT_DIR
        found = {"models": [], "configs": []}
        try:
            for root, dirs, files in os.walk(base):
                for f in files:
                    if f.lower().endswith(('.bin', '.pt', '.ckpt', '.safetensors')):
                        found['models'].append(os.path.join(root, f))
                    if f.lower() in ('config.json', 'model.yml', 'settings.json'):
                        found['configs'].append(os.path.join(root, f))
        except Exception as e:
            logger.warning(f"Model scan failed: {e}")
        return found


class HigherIntelligenceBridge:
    """Handles text and image queries to Gemini 1.5 Flash via REST.

    Requires env var `GOOGLE_API_KEY` configured for the project.
    This class is defensive when `requests` is missing.
    """

    def __init__(self, api_key: Optional[str] = None):
        # Prefer explicit parameter, then environment variable, then config file in ROOT_DIR/config.json
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            cfg_path = os.path.join(ROOT_DIR, 'config.json')
            try:
                if os.path.exists(cfg_path):
                    with open(cfg_path, 'r', encoding='utf-8') as fh:
                        cfg = json.load(fh)
                    # Common key names
                    self.api_key = cfg.get('GOOGLE_API_KEY') or cfg.get('google_api_key')
                    # Also allow nested structure
                    if not self.api_key and isinstance(cfg.get('ai'), dict):
                        self.api_key = cfg['ai'].get('google_api_key')
            except Exception as e:
                logger.debug(f"Failed to read config.json for API key: {e}")

        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not set — Gemini queries will fail")
        else:
            logger.info("HigherIntelligenceBridge: API key loaded")

    def query_text(self, prompt: str, timeout: int = 15) -> Optional[str]:
        if not requests_available or not self.api_key:
            logger.debug("query_text unavailable: requests or api_key missing")
            return None
        try:
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            headers = {"Content-Type": "application/json", "x-goog-api-key": self.api_key}
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            r = requests.post(url, json=payload, headers=headers, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            if "candidates" in data and data["candidates"]:
                return data["candidates"][0].get("content", {}).get("parts", [{}])[0].get("text", "")
            return None
        except Exception as e:
            logger.warning(f"Gemini text query failed: {e}")
            return None

    def query_image(self, image_bytes: bytes, prompt: str, timeout: int = 20) -> Optional[str]:
        if not requests_available or not self.api_key:
            logger.debug("query_image unavailable: requests or api_key missing")
            return None
        try:
            b64 = base64.standard_b64encode(image_bytes).decode()
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/png", "data": b64}}
                    ]
                }]
            }
            headers = {"Content-Type": "application/json", "x-goog-api-key": self.api_key}
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            r = requests.post(url, json=payload, headers=headers, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            if "candidates" in data and data["candidates"]:
                return data["candidates"][0].get("content", {}).get("parts", [{}])[0].get("text", "")
            return None
        except Exception as e:
            logger.warning(f"Gemini image query failed: {e}")
            return None


class VisionModule:
    """Capture screenshots and provide bytes for analysis."""

    def __init__(self):
        self.enabled = pil_available and ImageGrab is not None
        if self.enabled:
            logger.info("VisionModule: PIL ImageGrab available")
        else:
            logger.warning("VisionModule disabled: pillow not available")

    def capture_screenshot(self, save_path: Optional[Path] = None) -> Optional[bytes]:
        if not self.enabled:
            return None
        try:
            img = ImageGrab.grab()
            bio = io.BytesIO()
            img.save(bio, format='PNG')
            data = bio.getvalue()
            # Default: save to ROOT_DIR/temp_vision with timestamp
            if not save_path:
                timestamp = int(time.time() * 1000)
                save_path = os.path.join(ROOT_DIR, 'temp_vision', f'shot_{timestamp}.png')
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(data)
            return data
        except Exception as e:
            logger.error(f"capture_screenshot failed: {e}")
            return None


class ActionExecutor:
    """Wrap pyautogui to perform actions and report back to GUI/log.

    Provide a callback `on_action` that will receive tuples like
    (action_type, details_dict) for GUI display.
    """

    def __init__(self, on_action=None):
        self.enabled = pyautogui_available and pyautogui is not None
        self.on_action = on_action
        if self.enabled:
            logger.info("ActionExecutor: pyautogui available")
        else:
            logger.warning("ActionExecutor disabled: pyautogui not available")

    def stop(self):
        """Disable action execution immediately."""
        try:
            self.enabled = False
            logger.info("ActionExecutor stopped (actions disabled)")
        except Exception:
            pass

    def _report(self, action_type: str, details: dict):
        try:
            if callable(self.on_action):
                self.on_action(action_type, details)
        except Exception:
            pass

    def click(self, x: int, y: int, button: str = 'left') -> bool:
        if not self.enabled:
            return False
        try:
            pyautogui.click(x, y, button=button)
            self._report('click', {'x': x, 'y': y, 'button': button})
            return True
        except Exception as e:
            logger.error(f"click failed: {e}")
            return False

    def type_text(self, text: str) -> bool:
        if not self.enabled:
            return False
        try:
            pyautogui.typewrite(text, interval=0.02)
            self._report('type', {'text': text})
            return True
        except Exception as e:
            logger.error(f"type_text failed: {e}")
            return False

    def press_key(self, key: str) -> bool:
        if not self.enabled:
            return False
        try:
            pyautogui.press(key)
            self._report('press', {'key': key})
            return True
        except Exception as e:
            logger.error(f"press_key failed: {e}")
            return False


class SelfEvolutionThread:
    """Core autonomous error investigation and recovery thread."""

    def __init__(self, hib: HigherIntelligenceBridge, vision: VisionModule, action: ActionExecutor):
        self.hib = hib
        self.vision = vision
        self.action = action
        self.error_queue = queue.Queue()
        self.running = False
        self._thread = None

    def queue_error(self, error_type: str, message: str, context: Optional[str] = None):
        self.error_queue.put({'type': error_type, 'message': message, 'context': context})

    def investigate_error(self, error_item: dict) -> Optional[str]:
        prompt = f"Autonomous agent encountered an error:\nType: {error_item['type']}\nMessage: {error_item['message']}\nContext: {error_item.get('context')}\nProvide a concise fix or steps."
        return self.hib.query_text(prompt)

    def apply_fix(self, fix_text: str) -> bool:
        # Very small emulation: if fix contains [FIX_SHELL] run shell, if [FIX_CODE] skip
        try:
            if not fix_text:
                return False
            if "[FIX_SHELL]" in fix_text:
                cmd = fix_text.split("[FIX_SHELL]")[1].strip()
                subprocess.run(cmd, shell=True)
                return True
            if "[FIX_CODE]" in fix_text:
                # For single-file script, we decline to auto-modify in this simplified merge
                logger.info("Received code patch suggestion; skipping automatic apply in KNO_V2")
                return False
            # If fix_text suggests a UI action, we'll treat that as failed to apply and fall back to visual recovery
            return False
        except Exception as e:
            logger.error(f"apply_fix error: {e}")
            return False

    def visual_recovery(self, error_item: dict) -> bool:
        # Capture screenshot and ask HIB for coordinates or advice
        try:
            data = self.vision.capture_screenshot()
            if not data:
                return False
            prompt = (
                "Is there an error dialog visible in this screenshot? If yes, respond EXACTLY with: "
                "ERROR_FOUND at X,Y (integer coords of primary button). If no, respond: NO_ERROR"
            )
            analysis = self.hib.query_image(data, prompt)
            if not analysis:
                return False
            if "ERROR_FOUND" in analysis:
                # Attempt to parse coords
                try:
                    tail = analysis.split('ERROR_FOUND', 1)[1]
                    if 'at' in tail:
                        coords = tail.split('at', 1)[1].strip()
                        x_str, y_str = coords.split(',')
                        x, y = int(x_str.strip()), int(y_str.strip())
                        logger.info(f"Visual recovery: clicking at {x},{y}")
                        return self.action.click(x, y)
                except Exception as e:
                    logger.warning(f"Failed to parse coordinates: {e}")
                    # Fallback: try center click
                    screen_w, screen_h = (pyautogui.size() if pyautogui_available else (800, 600))
                    return self.action.click(screen_w // 2, screen_h // 2)
            return False
        except Exception as e:
            logger.error(f"visual_recovery failed: {e}")
            return False

    def _loop(self):
        self.running = True
        while self.running:
            try:
                item = self.error_queue.get(timeout=1)
            except Exception:
                time.sleep(0.1)
                continue
            try:
                logger.info(f"Investigating error: {item['type']}")
                fix = self.investigate_error(item)
                applied = self.apply_fix(fix)
                if not applied:
                    logger.info("Apply fix failed or not applicable — attempting visual recovery")
                    recovered = self.visual_recovery(item)
                    if recovered:
                        logger.info("Visual recovery attempted")
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Error in evolution loop: {e}")

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False



class BotGUI:
    """Minimal GUI showing status, Eye indicator, and Direct Action console."""

    def __init__(self, vision: VisionModule, action: ActionExecutor, evo: SelfEvolutionThread):
        self.vision = vision
        self.action = action
        self.evo = evo
        self.root = None
        self.eye_on = False
        self.typewriter = None

    def _on_action(self, action_type: str, details: dict):
        # Append to direct action console
        text = f"{action_type.upper()}: {json.dumps(details)}\n"
        try:
            self.console.insert(tk.END, text)
            self.console.see(tk.END)
        except Exception:
            logger.info(text.strip())

    def toggle_eye(self):
        self.eye_on = not self.eye_on
        color = '#FF8C00' if self.eye_on else '#555555'
        try:
            self.eye_label.config(background=color)
        except Exception:
            pass
        # If enabling vision, ensure modules are enabled
        if self.eye_on:
            logger.info('Visual Perception enabled')
        else:
            logger.info('Visual Perception disabled')

    def _handle_emergency_stop(self, event=None):
        """Emergency Esc handler: disable vision and stop actions immediately."""
        try:
            # Turn off vision flag
            self.vision.enabled = False
            # Stop action executor
            try:
                self.action.stop()
            except Exception:
                pass
            # Stop evolution thread
            try:
                self.evo.stop()
            except Exception:
                pass
            # Update GUI indicator
            try:
                self.eye_on = False
                self.eye_label.config(background='#555555')
            except Exception:
                pass
            # Persist config change
            try:
                cfg = {}
                if os.path.exists(CONFIG_PATH):
                    with open(CONFIG_PATH, 'r', encoding='utf-8') as cf:
                        cfg = json.load(cf)
                cfg['VISION_ENABLED'] = False
                with open(CONFIG_PATH, 'w', encoding='utf-8') as cf:
                    json.dump(cfg, cf, indent=2)
            except Exception:
                pass
            logger.warning('Emergency stop: Vision disabled and actions halted')
        except Exception:
            pass

    def build(self):
        if not tk_available:
            logger.warning('Tkinter not available — GUI will not start')
            return
        self.root = tk.Tk()
        self.root.title('KNO_V2 — Unified AI-OS')

        # Bind Escape to emergency stop
        try:
            self.root.bind('<Escape>', self._handle_emergency_stop)
        except Exception:
            pass

        top = ttk.Frame(self.root)
        top.pack(fill='x', padx=8, pady=6)

        ttk.Label(top, text='Status:').pack(side='left')
        self.status_var = tk.StringVar(value='Ready')
        ttk.Label(top, textvariable=self.status_var).pack(side='left', padx=(4, 12))

        ttk.Label(top, text='Visual Perception:').pack(side='left')
        self.eye_label = tk.Label(top, text=' ', width=2, background='#555555')
        self.eye_label.pack(side='left', padx=(4, 12))

        ttk.Button(top, text='Toggle Eye', command=self.toggle_eye).pack(side='left')

        # Direct Action console
        ttk.Label(self.root, text='Direct Action Console').pack(anchor='w', padx=8)
        self.console = scrolledtext.ScrolledText(self.root, width=80, height=10)
        self.console.pack(padx=8, pady=(0, 8))

        # Wire action callback
        self.action.on_action = self._on_action

        # Create Typewriter that writes to console
        try:
            self.typewriter = Typewriter(self.console)
        except Exception:
            self.typewriter = None

        # Start mainloop in separate thread to keep this process responsive
        threading.Thread(target=self.root.mainloop, daemon=True).start()


class Typewriter:
    """Simple typewriter that writes amber text to the GUI console or stdout."""
    def __init__(self, console_widget=None):
        self.console = console_widget

    def type(self, text: str):
        try:
            if self.console is not None:
                # Configure amber tag
                try:
                    self.console.tag_config('amber', foreground='#FF8C00')
                except Exception:
                    pass
                self.console.insert(tk.END, text + '\n', 'amber')
                self.console.see(tk.END)
            else:
                print(text)
        except Exception:
            print(text)


def main():
    logger.info('Starting KNO_V2')
    
    # Check if running in VirtualBox and prepare environment
    try:
        vbox_helper = Path(ROOT_DIR) / 'prepare_vbox_env.py'
        if vbox_helper.exists():
            logger.info("VirtualBox environment helper found. Running pre-flight check...")
            try:
                result = subprocess.run(
                    [sys.executable, str(vbox_helper), '--check'],
                    capture_output=True,
                    timeout=30
                )
                if result.returncode == 0:
                    logger.info("VirtualBox environment check passed.")
            except Exception as e:
                logger.debug(f"VBox check skipped: {e}")
    except Exception:
        pass
    
    # Verify ROOT_DIR exists
    if not os.path.exists(ROOT_DIR):
        logger.error(f"Required root directory not found: {ROOT_DIR}")
        return

    # Ensure dependencies early (auto-install on first run)
    ResourceManager.check_and_create_directories()
    ResourceManager.ensure_dependencies()

    # Scan local models/configs in ROOT_DIR
    local_assets = ResourceManager.scan_local_models(ROOT_DIR)
    logger.info(f"Local models found: {len(local_assets.get('models', []))}, configs: {len(local_assets.get('configs', []))}")

    hib = HigherIntelligenceBridge()
    vision = VisionModule()
    action = ActionExecutor()
    evo = SelfEvolutionThread(hib, vision, action)
    evo.start()

    gui = BotGUI(vision, action, evo)
    gui.build()

    # Welcome message via Typewriter (amber)
    try:
        if gui.typewriter:
            gui.typewriter.type('[SYSTEM] KNO V2 ONLINE. VISION MODULE STANDING BY.')
        else:
            logger.info('[SYSTEM] KNO V2 ONLINE. VISION MODULE STANDING BY.')
    except Exception:
        logger.info('[SYSTEM] KNO V2 ONLINE. VISION MODULE STANDING BY.')

    # Integrate clipboard bridge (Windows error → KNO analysis)
    try:
        from clipboard_bridge import integrate_clipboard_with_evolution
        integrate_clipboard_with_evolution(gui, evo)
    except ImportError:
        logger.debug("clipboard_bridge module not available; clipboard integration skipped")
    except Exception as e:
        logger.warning(f"Failed to integrate clipboard bridge: {e}")

    # Example: create a synthetic error to exercise visual recovery path
    # In practice errors are queued by other parts of the system
    time.sleep(1.0)
    evo.queue_error('gui_error', 'Sample error to trigger recovery', 'startup')

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Shutting down KNO_V2')
        evo.stop()


if __name__ == '__main__':
    main()
