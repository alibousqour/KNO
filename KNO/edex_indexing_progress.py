"""
eDEX-UI Indexing Progress Integration
======================================

Provides real-time progress bar updates to eDEX-UI during file indexing operations.
Integrates seamlessly with agent.py and any indexing process.

Features:
- Real-time progress bar in eDEX-UI interface
- Color-coded progress (red → orange → yellow → green)
- Speed tracking (files/sec, MB/s)
- ETA calculation
- Seamless JSON status file updates
- Thread-safe operations

Author: KNO Architecture
License: MIT
"""

import json
import os
import threading
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger('KNO.IndexingProgress')

# ============================================================================
# PROGRESS TRACKING DATACLASS
# ============================================================================

@dataclass
class IndexingProgress:
    """Track indexing progress for eDEX-UI display"""
    operation: str = "Indexing files..."
    current: int = 0
    total: int = 0
    current_file: str = ""
    processed_bytes: int = 0
    total_bytes: int = 0
    start_time: float = field(default_factory=time.time)
    
    @property
    def percentage(self) -> float:
        """Calculate progress percentage (0-100)"""
        if self.total <= 0:
            return 0.0
        return min(100.0, (self.current / self.total) * 100)
    
    @property
    def elapsed_seconds(self) -> float:
        """Time elapsed since start"""
        return time.time() - self.start_time
    
    @property
    def files_per_second(self) -> float:
        """Calculate indexing speed (files/sec)"""
        elapsed = self.elapsed_seconds
        if elapsed <= 0 or self.current <= 0:
            return 0.0
        return self.current / elapsed
    
    @property
    def mb_per_second(self) -> float:
        """Calculate throughput (MB/sec)"""
        elapsed = self.elapsed_seconds
        if elapsed <= 0 or self.processed_bytes <= 0:
            return 0.0
        return (self.processed_bytes / (1024 * 1024)) / elapsed
    
    @property
    def eta_seconds(self) -> int:
        """Calculate estimated time remaining"""
        speed = self.files_per_second
        if speed <= 0:
            return 0
        remaining = self.total - self.current
        return int(remaining / speed)
    
    @property
    def status_message(self) -> str:
        """Generate status message for display"""
        if self.total <= 0:
            return self.operation
        
        speed = self.files_per_second
        mb_speed = self.mb_per_second
        
        msg = f"{self.operation} "
        msg += f"({self.current}/{self.total}) "
        msg += f"[{self.percentage:.0f}%] "
        msg += f"@ {speed:.1f} files/sec "
        
        if mb_speed > 0:
            msg += f"({mb_speed:.2f} MB/s)"
        
        return msg

# ============================================================================
# EDEX STATUS FILE MANAGER
# ============================================================================

class EDEXStatusManager:
    """Manages edex_status.json file updates for progress display"""
    
    def __init__(self, status_file: str = "edex_status.json"):
        """
        Initialize eDEX status manager.
        
        Args:
            status_file: Path to edex_status.json
        """
        self.status_file = status_file
        self.lock = threading.RLock()
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Ensure status file directory exists"""
        status_dir = os.path.dirname(self.status_file)
        if status_dir:
            os.makedirs(status_dir, exist_ok=True)
    
    @staticmethod
    def _get_progress_color(percentage: float) -> str:
        """
        Get RGB color based on progress percentage.
        
        Args:
            percentage: Progress from 0-100
        
        Returns:
            Hex color code (#RRGGBB)
        """
        if percentage < 25:
            return "#FF3333"  # Bright red
        elif percentage < 50:
            return "#FF8833"  # Orange
        elif percentage < 75:
            return "#FFDD33"  # Yellow
        elif percentage < 90:
            return "#88DD33"  # Yellow-green
        else:
            return "#33DD33"  # Bright green
    
    def update_progress(self, progress: IndexingProgress) -> bool:
        """
        Update edex_status.json with current progress.
        
        Args:
            progress: IndexingProgress object
        
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            try:
                status_data = {
                    "version": "2.0",
                    "timestamp": datetime.now().isoformat(),
                    "semantic_search": {
                        "active": True,
                        "operation": progress.operation,
                        "progress": {
                            "current": progress.current,
                            "total": progress.total,
                            "percentage": round(progress.percentage, 1),
                            "current_file": progress.current_file
                        },
                        "performance": {
                            "elapsed_seconds": round(progress.elapsed_seconds, 2),
                            "files_per_second": round(progress.files_per_second, 2),
                            "mb_per_second": round(progress.mb_per_second, 2),
                            "processed_bytes": progress.processed_bytes,
                            "total_bytes": progress.total_bytes,
                            "eta_seconds": progress.eta_seconds
                        }
                    },
                    "ui_elements": {
                        "progress_bar": {
                            "visible": True,
                            "percentage": round(progress.percentage, 1),
                            "color": self._get_progress_color(progress.percentage),
                            "label": f"{progress.percentage:.0f}%"
                        },
                        "status_text": {
                            "primary": progress.operation,
                            "secondary": progress.status_message,
                            "tertiary": f"ETA: {progress.eta_seconds}s | "
                                        f"{progress.files_per_second:.1f} files/s"
                        }
                    }
                }
                
                # Atomic write: write to temp file then rename
                temp_file = self.status_file + ".tmp"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(status_data, f, indent=2, ensure_ascii=False)
                
                # Replace original atomically
                if os.path.exists(self.status_file):
                    os.remove(self.status_file)
                os.rename(temp_file, self.status_file)
                
                logger.debug(f"Updated eDEX status: {progress.percentage:.0f}% "
                           f"({progress.current}/{progress.total})")
                return True
            
            except Exception as e:
                logger.error(f"Failed to update eDEX status: {e}")
                # Clean up temp file if it exists
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                return False
    
    def clear_progress(self) -> bool:
        """
        Clear progress from eDEX-UI.
        
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            try:
                status_data = {
                    "version": "2.0",
                    "timestamp": datetime.now().isoformat(),
                    "semantic_search": {
                        "active": False,
                        "progress": None
                    },
                    "ui_elements": {
                        "progress_bar": {
                            "visible": False
                        }
                    }
                }
                
                temp_file = self.status_file + ".tmp"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(status_data, f, indent=2, ensure_ascii=False)
                
                if os.path.exists(self.status_file):
                    os.remove(self.status_file)
                os.rename(temp_file, self.status_file)
                
                logger.info("Cleared eDEX progress display")
                return True
            
            except Exception as e:
                logger.error(f"Failed to clear eDEX status: {e}")
                return False
    
    def get_current_status(self) -> Optional[Dict[str, Any]]:
        """
        Read current status from edex_status.json.
        
        Returns:
            Current status dict or None if file doesn't exist
        """
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read eDEX status: {e}")
        return None

# ============================================================================
# INDEXING PROGRESS TRACKER
# ============================================================================

class IndexingProgressTracker:
    """
    High-level tracker for indexing operations with eDEX-UI updates.
    
    Usage:
        tracker = IndexingProgressTracker(total_files=1000)
        
        for file in files:
            tracker.start_file(file)
            process_file(file)
            tracker.complete_file(file_size)
            
        tracker.finish()
    """
    
    def __init__(
        self,
        total_files: int = 0,
        total_bytes: int = 0,
        operation: str = "Indexing files...",
        status_file: str = "edex_status.json",
        update_callback: Optional[Callable] = None
    ):
        """
        Initialize progress tracker.
        
        Args:
            total_files: Total number of files to process
            total_bytes: Total bytes to process
            operation: Description of operation
            status_file: Path to edex_status.json
            update_callback: Optional callback after each update
        """
        self.total_files = total_files
        self.total_bytes = total_bytes
        self.operation = operation
        self.status_manager = EDEXStatusManager(status_file)
        self.update_callback = update_callback
        
        self.progress = IndexingProgress(
            operation=operation,
            total=total_files,
            total_bytes=total_bytes
        )
        
        self.lock = threading.RLock()
        self.last_update_time = time.time()
        self.update_interval = 0.5  # Update every 500ms
    
    def start_file(self, filename: str):
        """Mark the start of processing a file"""
        with self.lock:
            self.progress.current_file = filename
    
    def complete_file(self, file_size: int = 0):
        """Mark completion of processing a file"""
        with self.lock:
            self.progress.current += 1
            self.progress.processed_bytes += file_size
            self._maybe_update_display()
    
    def set_operation(self, operation: str):
        """Update operation description"""
        with self.lock:
            self.progress.operation = operation
            self._force_update_display()
    
    def _maybe_update_display(self):
        """Update display if enough time has passed"""
        now = time.time()
        if now - self.last_update_time >= self.update_interval:
            self._force_update_display()
    
    def _force_update_display(self):
        """Force update display immediately"""
        self.status_manager.update_progress(self.progress)
        self.last_update_time = time.time()
        
        if self.update_callback:
            try:
                self.update_callback(self.progress)
            except Exception as e:
                logger.error(f"Update callback failed: {e}")
    
    def finish(self):
        """Mark operation as complete"""
        with self.lock:
            self.progress.current = self.total_files
            self.progress.percentage = 100.0
            self._force_update_display()
            
            # Clear progress display after a short delay
            def clear_after_delay():
                time.sleep(2)
                self.status_manager.clear_progress()
            
            clear_thread = threading.Thread(target=clear_after_delay, daemon=True)
            clear_thread.start()
    
    def set_total(self, total_files: int, total_bytes: int = 0):
        """Update total items to process"""
        with self.lock:
            self.progress.total = total_files
            self.progress.total_bytes = total_bytes
    
    def get_progress(self) -> IndexingProgress:
        """Get current progress snapshot"""
        with self.lock:
            return self.progress

# ============================================================================
# CONVENIENCE FUNCTIONS FOR AGENT INTEGRATION
# ============================================================================

def create_indexing_tracker(
    total_files: int,
    operation: str = "Indexing files...",
    status_file: str = "edex_status.json"
) -> IndexingProgressTracker:
    """
    Create an indexing progress tracker with eDEX integration.
    
    Args:
        total_files: Number of files to index
        operation: Description of operation
        status_file: Path to edex_status.json
    
    Returns:
        IndexingProgressTracker instance
    
    Example:
        tracker = create_indexing_tracker(100, "Indexing Python files...")
        for file in files:
            tracker.start_file(file)
            index_file(file)
            tracker.complete_file(file_size)
        tracker.finish()
    """
    return IndexingProgressTracker(
        total_files=total_files,
        operation=operation,
        status_file=status_file
    )

def update_edex_progress(
    current: int,
    total: int,
    operation: str = "Indexing files...",
    current_file: str = "",
    processed_bytes: int = 0,
    total_bytes: int = 0,
    status_file: str = "edex_status.json"
) -> bool:
    """
    Quick function to update eDEX progress without tracker.
    
    Args:
        current: Current item count
        total: Total items
        operation: Operation description
        current_file: Currently processing file
        processed_bytes: Bytes processed so far
        total_bytes: Total bytes to process
        status_file: Path to edex_status.json
    
    Returns:
        True if successful
    
    Example:
        update_edex_progress(50, 100, "Indexing...", current_file="file.py")
    """
    progress = IndexingProgress(
        operation=operation,
        current=current,
        total=total,
        current_file=current_file,
        processed_bytes=processed_bytes,
        total_bytes=total_bytes
    )
    
    manager = EDEXStatusManager(status_file)
    return manager.update_progress(progress)

def clear_edex_progress(status_file: str = "edex_status.json") -> bool:
    """
    Clear progress display from eDEX-UI.
    
    Args:
        status_file: Path to edex_status.json
    
    Returns:
        True if successful
    """
    manager = EDEXStatusManager(status_file)
    return manager.clear_progress()

# ============================================================================
# STANDALONE DEMO/TEST
# ============================================================================

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
    )
    
    print("🎬 eDEX-UI Indexing Progress Demo")
    print("=" * 50)
    
    # Demo 1: Using IndexingProgressTracker
    print("\n📊 Demo 1: Progress Tracker")
    print("-" * 50)
    
    tracker = create_indexing_tracker(
        total_files=100,
        operation="📂 Indexing Python files..."
    )
    
    for i in range(1, 101):
        tracker.start_file(f"file_{i:03d}.py")
        time.sleep(0.01)  # Simulate work
        tracker.complete_file(file_size=1024 * (i % 50))  # Simulate file sizes
        
        if i % 10 == 0:
            print(f"  Progress: {tracker.progress.percentage:.0f}% "
                  f"({tracker.progress.files_per_second:.1f} files/s)")
    
    tracker.finish()
    print("\n✅ Demo 1 complete!")
    
    # Demo 2: Using quick update function
    print("\n📊 Demo 2: Quick Update Function")
    print("-" * 50)
    
    for i in range(0, 101, 10):
        success = update_edex_progress(
            current=i,
            total=100,
            operation="🔍 Scanning files...",
            current_file=f"file_{i:03d}.py",
            processed_bytes=i * 102400,
            total_bytes=100 * 102400
        )
        print(f"  Update {i}%: {'✓' if success else '✗'}")
        time.sleep(0.5)
    
    clear_edex_progress()
    print("\n✅ Demo 2 complete!")
    
    print("\n🎉 All demos completed successfully!")
