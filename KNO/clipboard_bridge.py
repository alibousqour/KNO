"""
clipboard_bridge.py

Windows ↔ KNO Clipboard Synchronization Module

Enables KNO to read from Windows clipboard (via VBox shared clipboard)
and use the content as input for error diagnosis and troubleshooting.

Example Workflow:
1. User copies error message from Windows application
2. KNO detects clipboard change event
3. Reads clipboard content
4. Sends to Gemini for analysis alongside screenshot
5. Executes ActionExecutor commands to fix issue
"""

import threading
import logging
import tkinter as tk
from typing import Optional, Callable

logger = logging.getLogger("ClipboardBridge")


class ClipboardMonitor:
    """Monitor Windows clipboard for changes (via VBox shared clipboard)."""

    def __init__(self, on_clipboard_change: Optional[Callable[[str], None]] = None):
        """
        Initialize clipboard monitor.
        
        Args:
            on_clipboard_change: Callback function(clipboard_text) when content changes
        """
        self.on_clipboard_change = on_clipboard_change
        self.running = False
        self._thread = None
        self._last_content = ""
        self._root = None

    def start(self):
        """Start monitoring clipboard in background thread."""
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("ClipboardMonitor started")

    def stop(self):
        """Stop clipboard monitoring."""
        self.running = False
        try:
            if self._root:
                self._root.quit()
        except Exception:
            pass
        logger.info("ClipboardMonitor stopped")

    def get_clipboard_text(self) -> Optional[str]:
        """
        Read current clipboard content.
        
        Returns:
            Clipboard text or None if unavailable
        """
        try:
            root = tk.Tk()
            root.withdraw()
            text = root.clipboard_get()
            root.destroy()
            return text
        except Exception as e:
            logger.debug(f"Clipboard read failed: {e}")
            return None

    def set_clipboard_text(self, text: str) -> bool:
        """
        Write text to clipboard.
        
        Args:
            text: Text to copy to clipboard
            
        Returns:
            True if successful
        """
        try:
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()  # Required to make change persistent
            root.destroy()
            logger.info(f"Clipboard write: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Clipboard write failed: {e}")
            return False

    def _monitor_loop(self):
        """Background thread loop to monitor clipboard changes."""
        self.running = True
        while self.running:
            try:
                current = self.get_clipboard_text()
                if current and current != self._last_content:
                    self._last_content = current
                    logger.info(f"Clipboard change detected: {current[:80]}...")
                    if callable(self.on_clipboard_change):
                        try:
                            self.on_clipboard_change(current)
                        except Exception as e:
                            logger.error(f"Clipboard callback error: {e}")
                threading.Event().wait(1.0)  # Poll every 1 second
            except Exception as e:
                logger.debug(f"Monitor loop error: {e}")
                threading.Event().wait(1.0)


class ErrorFromClipboardHandler:
    """
    Handle errors copied from Windows and solve them in KNO.
    
    Workflow:
    1. User copies error text from Windows
    2. ClipboardMonitor detects change
    3. This handler extracts error info
    4. Queues error to SelfEvolutionThread
    5. AI analyzes + fixes
    """

    def __init__(self, evolution_thread=None):
        """Initialize handler with link to evolution thread."""
        self.evolution_thread = evolution_thread

    def on_clipboard_change(self, text: str):
        """Called when clipboard content changes."""
        # Heuristic: if text contains error keywords, queue for analysis
        error_keywords = [
            'error', 'exception', 'failed', 'fatal', 'crash',
            'traceback', 'errno', 'fault', 'panic', 'abort'
        ]
        
        if any(keyword in text.lower() for keyword in error_keywords):
            logger.info(f"Error-like content detected in clipboard. Queueing for analysis.")
            if self.evolution_thread:
                self.evolution_thread.queue_error(
                    'clipboard_error',
                    text,
                    'User copied error from Windows application'
                )
            else:
                logger.warning("SelfEvolutionThread not available to process clipboard error")
        else:
            logger.debug(f"Clipboard content is not error-related. Ignoring: {text[:50]}...")


def integrate_clipboard_with_evolution(gui_obj, evolution_thread):
    """
    Wire clipboard monitor to BotGUI and SelfEvolutionThread.
    
    Args:
        gui_obj: BotGUI instance
        evolution_thread: SelfEvolutionThread instance
    """
    try:
        handler = ErrorFromClipboardHandler(evolution_thread)
        clipboard_monitor = ClipboardMonitor(on_clipboard_change=handler.on_clipboard_change)
        
        # Store reference in GUI for later control
        gui_obj.clipboard_monitor = clipboard_monitor
        
        # Start monitoring in background
        clipboard_monitor.start()
        
        logger.info("Clipboard integration enabled: Windows errors → KNO analysis")
        return clipboard_monitor
    except Exception as e:
        logger.warning(f"Clipboard integration failed: {e}")
        return None
