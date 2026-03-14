"""
FUTURISTIC BOTGUI - Audio Waves Visualization
A high-tech interface centered around animated audio wave visualization.
This is a complete replacement for the BotGUI class in agent.py.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import math
import json
import os
import asyncio
try:
    import psutil
    HAS_PSUTIL = True
except Exception:
    HAS_PSUTIL = False
from typing import Optional, Dict, List, Any
from pathlib import Path
from datetime import datetime


class KNOTaskManager:
    """Task Manager for monitoring processes and healing events with eDEX-UI sync."""
    
    def __init__(self, edex_status_path: Optional[str] = None):
        """Initialize task manager.
        
        Args:
            edex_status_path: Path to edex_status.json for sync
        """
        self.edex_status_path = edex_status_path or "edex_status.json"
        self.processes: Dict[str, Dict[str, Any]] = {}
        self.healing_events: List[Dict[str, Any]] = []
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.max_history = 100
        self._lock = threading.Lock()
    
    def add_process(self, process_id: str, config: Dict[str, Any]) -> None:
        """Add process to tracking.
        
        Args:
            process_id: Process identifier
            config: Process configuration
        """
        with self._lock:
            self.processes[process_id] = {
                "id": process_id,
                "status": "CREATED",
                "reliability_score": 100.0,
                "uptime": 0.0,
                "crashes": 0,
                "last_update": datetime.now().isoformat(),
                "config": config
            }
    
    def record_healing_event(self, process_id: str, reason: str, retry_count: int) -> None:
        """Record a healing/restart event.
        
        Args:
            process_id: Process that was healed
            reason: Reason for healing
            retry_count: Current retry attempt
        """
        with self._lock:
            event = {
                "timestamp": datetime.now().isoformat(),
                "process_id": process_id,
                "reason": reason,
                "retry_count": retry_count,
                "type": "healing_attempt"
            }
            self.healing_events.append(event)
            
            # Keep only recent events
            if len(self.healing_events) > self.max_history:
                self.healing_events = self.healing_events[-self.max_history:]
    
    def update_process_status(self, process_id: str, status: str, 
                             reliability: float, uptime: float, crashes: int) -> None:
        """Update process status in tracking.
        
        Args:
            process_id: Process identifier
            status: Process state
            reliability: Reliability score (0-100)
            uptime: Uptime in seconds
            crashes: Total crashes
        """
        with self._lock:
            if process_id in self.processes:
                self.processes[process_id].update({
                    "status": status,
                    "reliability_score": reliability,
                    "uptime": uptime,
                    "crashes": crashes,
                    "last_update": datetime.now().isoformat()
                })
    
    def sync_to_edex(self) -> None:
        """Sync current state to edex_status.json for eDEX-UI integration."""
        try:
            with self._lock:
                status_data = {
                    "timestamp": datetime.now().isoformat(),
                    "processes": self.processes,
                    "recent_healing": self.healing_events[-10:] if self.healing_events else [],
                    "total_processes": len(self.processes),
                    "system_health": self._calculate_system_health()
                }
            
            # Write to edex_status.json
            Path(self.edex_status_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.edex_status_path, 'w') as f:
                json.dump(status_data, f, indent=2)
        
        except Exception as e:
            print(f"[TASK_MANAGER] Error syncing to eDEX: {e}", flush=True)
    
    def _calculate_system_health(self) -> str:
        """Calculate overall system health based on processes."""
        if not self.processes:
            return "IDLE"
        
        avg_reliability = sum(p.get("reliability_score", 100) for p in self.processes.values()) / len(self.processes)
        
        if avg_reliability >= 95:
            return "HEALTHY"
        elif avg_reliability >= 80:
            return "DEGRADED"
        else:
            return "CRITICAL"
    
    def get_healing_events_for_display(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent healing events for display.
        
        Args:
            limit: Maximum events to return
            
        Returns:
            List of healing events
        """
        with self._lock:
            return self.healing_events[-limit:] if self.healing_events else []


class FuturisticBotGUI:
    """
    High-tech futuristic interface with audio waves visualization.
    Features a large central canvas with animated neon cyan waves.
    """
    
    # Constants
    WAVE_COLOR_IDLE = "#00FFCC"      # Neon cyan
    WAVE_COLOR_THINKING = "#0088FF"  # Neon blue
    WAVE_COLOR_SPEAKING = "#FF00FF"  # Neon magenta
    BG_COLOR = "#0a0a0a"             # Deep black
    
    def __init__(self, master):
        """Initialize the futuristic UI with audio waves."""
        self.master = master
        self.master.title("KNO - Cybernetic AI Assistant")
        
        # Try fullscreen, fallback to windowed
        try:
            self.master.attributes('-fullscreen', True)
            print("[GUI] Fullscreen enabled", flush=True)
        except Exception as e:
            print(f"[GUI] Fullscreen failed ({e}), using windowed mode", flush=True)
            self.master.geometry('1200x800')
        # Make the window act like an overlay (always on top, slight transparency)
        try:
            self.master.attributes('-topmost', True)
            self.master.attributes('-alpha', 0.95)
        except Exception:
            pass
        
        # Bind escape key to exit fullscreen
        self.master.bind('<Escape>', self.exit_fullscreen)
        
        # ===== STATE INITIALIZATION =====
        self.is_speaking = False
        self.is_thinking = False
        self.wave_phase = 0.0  # Animation phase
        self.animation_running = True
        self.user_input_queue = []
        
        # Process registry monitoring state
        self.process_registry: Optional[object] = None
        self.monitoring_active = False
        self.treeview_items = {}  # Track item IDs for updates
        
        # Task Manager and healing alerts
        self.task_manager = KNOTaskManager()
        self.healing_alerts_queue: List[Dict[str, Any]] = []
        self.active_alert_process: Optional[str] = None
        self.last_alert_color = self.BG_COLOR

        # Resource monitoring state
        self.resource_usage: Dict[str, Any] = {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_percent": 0.0,
            "net_bytes_sent": 0,
            "net_bytes_recv": 0
        }
        
        # Initialize status
        self.status_var = tk.StringVar(value="Ready")
        
        # ===== BUILD UI =====
        
        # Set background to deep black
        self.master.configure(bg=self.BG_COLOR)
        
        # Create main frame
        main_frame = tk.Frame(self.master, bg=self.BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- TOP SECTION: Status and Title ---
        top_frame = tk.Frame(main_frame, bg=self.BG_COLOR, height=60)
        top_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        title_label = tk.Label(
            top_frame, 
            text="KNO", 
            font=("Arial", 32, "bold"),
            bg=self.BG_COLOR,
            fg=self.WAVE_COLOR_IDLE
        )
        title_label.pack(side=tk.LEFT)
        
        status_label = tk.Label(
            top_frame,
            textvariable=self.status_var,
            font=("Arial", 12),
            bg=self.BG_COLOR,
            fg="#888888"
        )
        status_label.pack(side=tk.RIGHT)
        
        # --- MIDDLE SECTION: Audio Wave Canvas ---
        canvas_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Canvas for waves (top)
        canvas_container = tk.Frame(canvas_frame, bg=self.BG_COLOR)
        canvas_container.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        
        self.canvas = tk.Canvas(
            canvas_container,
            bg=self.BG_COLOR,
            highlightthickness=0,
            cursor="crosshair",
            height=250
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for process monitoring (bottom)
        treeview_label = tk.Label(
            canvas_frame,
            text="Process Registry Status",
            font=("Arial", 10, "bold"),
            bg=self.BG_COLOR,
            fg="#888888"
        )
        treeview_label.pack(fill=tk.X, pady=(15, 5))
        
        # Create Treeview with scrollbar
        treeview_container = tk.Frame(canvas_frame, bg=self.BG_COLOR)
        treeview_container.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM)
        
        scrollbar = ttk.Scrollbar(treeview_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.process_treeview = ttk.Treeview(
            treeview_container,
            columns=("Status", "Reliability", "Uptime", "Health", "Crashes"),
            height=8,
            yscrollcommand=scrollbar.set,
            show="headings"
        )
        scrollbar.config(command=self.process_treeview.yview)
        
        # Configure column headings and widths
        self.process_treeview.column("#0", width=150, anchor=tk.W)
        self.process_treeview.column("Status", width=80, anchor=tk.CENTER)
        self.process_treeview.column("Reliability", width=90, anchor=tk.CENTER)
        self.process_treeview.column("Uptime", width=100, anchor=tk.CENTER)
        self.process_treeview.column("Health", width=80, anchor=tk.CENTER)
        self.process_treeview.column("Crashes", width=70, anchor=tk.CENTER)
        
        self.process_treeview.heading("#0", text="Process ID")
        self.process_treeview.heading("Status", text="Status")
        self.process_treeview.heading("Reliability", text="Reliability %")
        self.process_treeview.heading("Uptime", text="Avg Uptime (s)")
        self.process_treeview.heading("Health", text="Health")
        self.process_treeview.heading("Crashes", text="Crashes")
        
        self.process_treeview.pack(fill=tk.BOTH, expand=True)
        
        # Configure Treeview styling
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Treeview', 
                       background='#1a1a1a',
                       foreground='#00FFCC',
                       fieldbackground='#1a1a1a',
                       font=('Arial', 9))
        style.configure('Treeview.Heading',
                       background='#0a0a0a',
                       foreground='#00FFCC',
                       font=('Arial', 9, 'bold'))
        style.map('Treeview', background=[('selected', '#0088FF')])
        
        # Add tag colors for health status indicators
        self.process_treeview.tag_configure('health_healthy', foreground='#00FF00')  # Green
        self.process_treeview.tag_configure('health_degraded', foreground='#FFFF00')  # Yellow
        self.process_treeview.tag_configure('health_critical', foreground='#FF0000')  # Red
        
        # Get canvas dimensions after packing
        self.master.update_idletasks()
        
        # --- BOTTOM SECTION: Text Input ---
        bottom_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        bottom_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        # Minimalist text entry with no border
        self.text_entry = tk.Entry(
            bottom_frame,
            font=("Arial", 14),
            bg="#1a1a1a",
            fg=self.WAVE_COLOR_IDLE,
            insertbackground=self.WAVE_COLOR_IDLE,
            borderwidth=0,
            relief=tk.FLAT
        )
        self.text_entry.insert(0, "Command KNO...")
        self.text_entry.pack(fill=tk.X, ipady=8)
        
        # Bind events
        self.text_entry.bind('<FocusIn>', self._on_entry_focus_in)
        self.text_entry.bind('<FocusOut>', self._on_entry_focus_out)
        self.text_entry.bind('<Return>', self._on_enter_pressed)

        # --- OVERLAY PANEL: Resource usage and healing logs (top-right) ---
        overlay_frame = tk.Frame(self.master, bg='#0f0f0f', bd=1, relief=tk.RIDGE)
        overlay_frame.place(relx=0.74, rely=0.02, relwidth=0.245, relheight=0.28)

        overlay_title = tk.Label(overlay_frame, text="System Overlay", bg='#0f0f0f', fg='#00FFCC', font=("Arial", 10, 'bold'))
        overlay_title.pack(fill=tk.X, pady=(4,2))

        # Resource labels
        self.cpu_label = tk.Label(overlay_frame, text="CPU: 0%", bg='#0f0f0f', fg='#FFFFFF')
        self.cpu_label.pack(anchor='w', padx=6)
        self.mem_label = tk.Label(overlay_frame, text="MEM: 0%", bg='#0f0f0f', fg='#FFFFFF')
        self.mem_label.pack(anchor='w', padx=6)
        self.disk_label = tk.Label(overlay_frame, text="DISK: 0%", bg='#0f0f0f', fg='#FFFFFF')
        self.disk_label.pack(anchor='w', padx=6)

        # Healing logs listbox
        logs_label = tk.Label(overlay_frame, text="Self-Healing Logs", bg='#0f0f0f', fg='#00FFCC', font=("Arial", 9, 'bold'))
        logs_label.pack(fill=tk.X, pady=(6,0))

        self.healing_listbox = tk.Listbox(overlay_frame, bg='#121212', fg='#FFFFFF', height=6)
        self.healing_listbox.pack(fill=tk.BOTH, expand=True, padx=6, pady=(2,6))
        
        # --- CONTROLS (hidden, accessible via keyboard shortcuts) ---
        # ESC = exit, SPACE = toggle speaking state (for testing)
        self.master.bind('<space>', self._toggle_speaking_state)
        
        # ===== START ANIMATION THREAD =====
        self.animation_alive = True
        self.animation_thread = threading.Thread(target=self._animation_loop, daemon=True)
        self.animation_thread.start()
        # Start a small resource update timer on the main thread
        self.master.after(1000, self._update_resource_ui)
        
        print("[GUI] Futuristic BotGUI initialized with audio waves visualization", flush=True)
    
    def _animation_loop(self):
        """Background thread for smooth wave animation."""
        frame_rate = 60  # 60 FPS
        frame_time = 1.0 / frame_rate
        
        while self.animation_alive:
            try:
                # Update wave phase
                self.wave_phase += 0.05 if not self.is_speaking else 0.1
                if self.wave_phase > 2 * math.pi:
                    self.wave_phase -= 2 * math.pi
                
                # Redraw canvas
                self._draw_waves()
                
                time.sleep(frame_time)
            except Exception as e:
                print(f"[ANIMATION] Error: {e}", flush=True)
                time.sleep(0.016)
    
    def _draw_waves(self):
        """Draw animated audio waves on the canvas."""
        try:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width < 100 or canvas_height < 100:
                return
            
            # Clear canvas
            self.canvas.delete("all")
            
            # Determine wave color and intensity based on state
            if self.is_speaking:
                wave_color = self.WAVE_COLOR_SPEAKING
                base_amplitude = 80
                num_bars = 32
            elif self.is_thinking:
                wave_color = self.WAVE_COLOR_THINKING
                base_amplitude = 50
                num_bars = 24
            else:
                wave_color = self.WAVE_COLOR_IDLE
                base_amplitude = 30
                num_bars = 16
            
            # Calculate center
            center_x = canvas_width / 2
            center_y = canvas_height / 2
            
            # Draw vertical bars (equalizer-style waves)
            bar_width = canvas_width / (num_bars + 1)
            
            for i in range(num_bars):
                x = (i + 1) * bar_width
                
                # Calculate wave offset using sine function
                angle = self.wave_phase + (i / num_bars) * (2 * math.pi)
                wave_offset = math.sin(angle)
                
                # Calculate bar height
                height = base_amplitude * (1.0 + 0.5 * wave_offset)
                
                # Draw bar (vertical rectangle)
                y1 = center_y - height / 2
                y2 = center_y + height / 2
                
                self.canvas.create_line(
                    x, y1, x, y2,
                    fill=wave_color,
                    width=int(bar_width * 0.6)
                )
            
            # Draw animated circle/ring in center
            ring_radius = 30 + 20 * math.sin(self.wave_phase)
            if self.is_speaking:
                ring_radius = 50 + 30 * math.sin(self.wave_phase)
            
            # Draw circle outline
            x1 = center_x - ring_radius
            y1 = center_y - ring_radius
            x2 = center_x + ring_radius
            y2 = center_y + ring_radius
            
            self.canvas.create_oval(
                x1, y1, x2, y2,
                outline=wave_color,
                width=2
            )
            
            # Draw center dot
            dot_radius = 5
            self.canvas.create_oval(
                center_x - dot_radius, center_y - dot_radius,
                center_x + dot_radius, center_y + dot_radius,
                fill=wave_color,
                outline=wave_color
            )
            
            # Draw status text in center
            status_text = "SPEAKING" if self.is_speaking else ("THINKING" if self.is_thinking else "IDLE")
            self.canvas.create_text(
                center_x, center_y + 60,
                text=status_text,
                font=("Arial", 10, "bold"),
                fill=wave_color,
                anchor=tk.N
            )
            
        except Exception as e:
            print(f"[DRAW] Error: {e}", flush=True)
    
    def _on_entry_focus_in(self, event):
        """Handle focus in on text entry."""
        if self.text_entry.get() == "Command KNO...":
            self.text_entry.delete(0, tk.END)
            self.text_entry.config(fg=self.WAVE_COLOR_IDLE)
    
    def _on_entry_focus_out(self, event):
        """Handle focus out from text entry."""
        if self.text_entry.get() == "":
            self.text_entry.insert(0, "Command KNO...")
            self.text_entry.config(fg="#666666")
    
    def _on_enter_pressed(self, event):
        """Handle Enter key press - send command to KNO."""
        user_input = self.text_entry.get().strip()
        
        if user_input and user_input != "Command KNO...":
            print(f"[INPUT] User command: {user_input}", flush=True)
            
            # Queue the input
            self.user_input_queue.append(user_input)
            
            # Clear entry
            self.text_entry.delete(0, tk.END)
            
            # Set thinking state and trigger animation
            self.is_thinking = True
            self.status_var.set("Thinking...")
            
            # Simulate processing (in real app, this would call controller)
            threading.Thread(target=self._process_command, args=(user_input,), daemon=True).start()
    
    def _process_command(self, command):
        """Simulate processing a command."""
        try:
            time.sleep(1)  # Simulate thinking
            self.is_thinking = False
            self.is_speaking = True
            self.status_var.set("Speaking...")
            
            # Simulate speaking
            time.sleep(2)
            self.is_speaking = False
            self.status_var.set("Ready")
        except Exception as e:
            print(f"[PROCESS] Error: {e}", flush=True)
            self.is_thinking = False
            self.is_speaking = False
            self.status_var.set("Error")
    
    def _toggle_speaking_state(self, event):
        """Toggle speaking state for testing (SPACE key)."""
        self.is_speaking = not self.is_speaking
        status = "SPEAKING" if self.is_speaking else "IDLE"
        self.status_var.set(status)
        print(f"[DEV] Speaking state toggled: {status}", flush=True)
    
    def set_process_registry(self, registry: object) -> None:
        """Set the process registry instance for monitoring.
        
        Args:
            registry: ProcessRegistry instance to monitor
        """
        self.process_registry = registry
        self.monitoring_active = True
        
        # Start async monitoring in a background thread
        monitor_thread = threading.Thread(
            target=self._run_async_monitor,
            daemon=True
        )
        monitor_thread.start()
        print("[GUI] Process registry monitoring started", flush=True)
    
    def _run_async_monitor(self) -> None:
        """Run the async process monitor in a new event loop."""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the async monitor coroutine
            loop.run_until_complete(self._monitor_processes_async())
        except Exception as e:
            print(f"[MONITOR] Error in async loop: {e}", flush=True)
        finally:
            asyncio.set_event_loop(None)
    
    async def _monitor_processes_async(self) -> None:
        """Async function to monitor process registry every 1 second.
        
        Updates the Treeview widget with current process status, reliability scores,
        and uptime information from the ProcessRegistry. Also syncs to edex_status.json
        every 5 seconds and processes healing alerts.
        """
        if not self.process_registry:
            print("[MONITOR] No registry available", flush=True)
            return
        
        sync_counter = 0
        sync_interval = 5  # Sync to JSON every 5 seconds (5 x 1-second updates)
        
        while self.monitoring_active and self.animation_alive:
            try:
                # Get all process metrics from registry
                metrics_list = self.process_registry.list_metrics()
                
                # Get list of processes for status
                processes = self.process_registry.list_processes()
                process_states = {p.process_id: p.state for p in processes}
                
                # Update GUI from main thread
                self.master.after(0, self._update_treeview, metrics_list, process_states)
                # Update resource usage on each loop
                if HAS_PSUTIL:
                    # gather resource usage in thread-safe way
                    cpu = psutil.cpu_percent(interval=None)
                    mem = psutil.virtual_memory().percent
                    disk = psutil.disk_usage('/').percent
                    net = psutil.net_io_counters()
                    self.resource_usage.update({
                        "cpu_percent": cpu,
                        "memory_percent": mem,
                        "disk_percent": disk,
                        "net_bytes_sent": net.bytes_sent,
                        "net_bytes_recv": net.bytes_recv
                    })

                # update healing listbox display
                self.master.after(0, self._refresh_healing_listbox)
                
                # Periodically sync to edex_status.json
                sync_counter += 1
                if sync_counter >= sync_interval:
                    await asyncio.to_thread(self._sync_to_edex_status)
                    sync_counter = 0
                
                # Process any pending healing alerts
                self.master.after(0, self._display_healing_alerts)
                
                # Sleep for 1 second between updates (non-blocking)
                await asyncio.sleep(1.0)
                
            except Exception as e:
                print(f"[MONITOR] Error updating metrics: {e}", flush=True)
                await asyncio.sleep(1.0)
    
    def _sync_to_edex_status(self) -> None:
        """Sync process monitoring data to edex_status.json for eDEX-UI integration.
        
        This runs in a background thread to avoid blocking the UI.
        Serializes process metrics, healing events, and system health to JSON.
        """
        try:
            if not self.process_registry:
                return
            
            # Gather all process metrics
            metrics_list = self.process_registry.list_metrics()
            processes = self.process_registry.list_processes()
            
            # Build process data for JSON
            processes_data = {}
            for metrics in metrics_list:
                process = next((p for p in processes if p.process_id == metrics.process_id), None)
                processes_data[metrics.process_id] = {
                    "status": process.state.value if process else "UNKNOWN",
                    "reliability_score": round(metrics.get_reliability_score(), 2),
                    "uptime": round(metrics.average_uptime, 2),
                    "crashes": metrics.total_crashes,
                    "restarts": metrics.total_restarts,
                    "health": metrics.get_health_status(),
                    "success_count": metrics.success_count,
                    "failure_count": metrics.failure_count
                }
            
            # Calculate system health
            if processes_data:
                avg_reliability = sum(p["reliability_score"] for p in processes_data.values()) / len(processes_data)
                if avg_reliability >= 95:
                    system_health = "HEALTHY"
                elif avg_reliability >= 80:
                    system_health = "DEGRADED"
                else:
                    system_health = "CRITICAL"
            else:
                avg_reliability = 100.0
                system_health = "IDLE"
            
            # Build status data
            status_data = {
                "timestamp": datetime.now().isoformat(),
                "system_health": system_health,
                "average_reliability": round(avg_reliability, 2),
                "total_processes": len(processes_data),
                "processes": processes_data,
                "resource_usage": {
                    "cpu_percent": round(self.resource_usage.get("cpu_percent", 0.0), 2),
                    "memory_percent": round(self.resource_usage.get("memory_percent", 0.0), 2),
                    "disk_percent": round(self.resource_usage.get("disk_percent", 0.0), 2),
                    "net_bytes_sent": int(self.resource_usage.get("net_bytes_sent", 0)),
                    "net_bytes_recv": int(self.resource_usage.get("net_bytes_recv", 0))
                },
                "recent_healing_events": [
                    {
                        "timestamp": event["timestamp"],
                        "process_id": event["process_id"],
                        "reason": event["reason"],
                        "retry_count": event.get("retry_count", 0)
                    }
                    for event in self.task_manager.get_healing_events_for_display(limit=10)
                ]
            }
            
            # Write to edex_status.json
            edex_path = Path(self.task_manager.edex_status_path)
            edex_path.parent.mkdir(parents=True, exist_ok=True)
            with open(edex_path, 'w') as f:
                json.dump(status_data, f, indent=2)
            
            print(f"[EDEX_SYNC] Synced {len(processes_data)} processes to {edex_path}", flush=True)
        
        except Exception as e:
            print(f"[EDEX_SYNC] Error syncing to edex_status.json: {e}", flush=True)
    
    def record_healing_event(self, process_id: str, reason: str = "crash_detected", retry_count: int = 1) -> None:
        """Record a process healing/restart event.
        
        Args:
            process_id: Process that was healed
            reason: Reason for healing (default: crash_detected)
            retry_count: Current retry attempt
        """
        self.task_manager.record_healing_event(process_id, reason, retry_count)
        self.healing_alerts_queue.append({
            "process_id": process_id,
            "reason": reason,
            "retry_count": retry_count,
            "timestamp": datetime.now()
        })
        # Add to overlay logs immediately
        try:
            display = f"{datetime.now().strftime('%H:%M:%S')} {process_id}: {reason} (#{retry_count})"
            self.healing_listbox.insert(tk.END, display)
            # Keep listbox to max history
            if self.healing_listbox.size() > self.task_manager.max_history:
                self.healing_listbox.delete(0, 0)
        except Exception:
            pass
        print(f"[HEALING_ALERT] {process_id} being healed (attempt #{retry_count}): {reason}", flush=True)

    def _refresh_healing_listbox(self):
        """Refresh healing listbox from task manager recent events."""
        try:
            recent = self.task_manager.get_healing_events_for_display(limit=50)
            # Clear and repopulate
            self.healing_listbox.delete(0, tk.END)
            for ev in recent:
                ts = ev.get('timestamp', '')
                pid = ev.get('process_id', '')
                reason = ev.get('reason', '')
                retry = ev.get('retry_count', 0)
                self.healing_listbox.insert(tk.END, f"{ts} {pid}: {reason} (#{retry})")
        except Exception:
            pass

    def _update_resource_ui(self):
        """Update the overlay resource labels on the main thread periodically."""
        try:
            ru = self.resource_usage
            self.cpu_label.config(text=f"CPU: {ru.get('cpu_percent', 0.0):.1f}%")
            self.mem_label.config(text=f"MEM: {ru.get('memory_percent', 0.0):.1f}%")
            self.disk_label.config(text=f"DISK: {ru.get('disk_percent', 0.0):.1f}%")
        except Exception:
            pass
        # schedule next update
        self.master.after(1000, self._update_resource_ui)

    def attach_to_agent(self, agent: object) -> None:
        """Attach GUI to a running KNOAgent instance to receive healing events.

        Registers a callback on the agent so self.record_healing_event is called
        for healing notifications.
        """
        try:
            self._attached_agent = agent
            # register adapter callback
            def _adapter(event_type, payload):
                try:
                    if event_type in ("attempt", "failed"):
                        process_id = payload.get('process_id')
                        if event_type == 'attempt':
                            retry = payload.get('attempt', 1)
                            reason = 'restart_attempt'
                        else:
                            retry = payload.get('attempt', 0)
                            reason = payload.get('reason', 'healing_failed')
                        # call GUI recording
                        self.record_healing_event(process_id, reason, retry)
                except Exception:
                    pass

            if hasattr(agent, 'register_healing_callback'):
                agent.register_healing_callback(_adapter)
        except Exception as e:
            print(f"[GUI_ATTACH] Failed to attach to agent: {e}", flush=True)
    
    def _display_healing_alerts(self) -> None:
        """Display visual notifications for healing events.
        
        Processes the healing alerts queue and displays toast notifications
        with appropriate colors and auto-dismiss timing.
        """
        if not self.healing_alerts_queue:
            return
        
        try:
            # Get the next healing event (FIFO)
            event = self.healing_alerts_queue.pop(0)
            
            # Determine alert color and message
            retry_count = event.get("retry_count", 1)
            process_id = event.get("process_id", "unknown")
            reason = event.get("reason", "crashed")
            
            if retry_count <= 3:
                alert_color = "#00FF00"  # Green - healing attempt
                alert_msg = f"🔄 Restarting {process_id} (attempt #{retry_count})"
            elif retry_count <= 5:
                alert_color = "#FFFF00"  # Yellow - multiple retries
                alert_msg = f"⚠ Retry {retry_count} for {process_id}"
            else:
                alert_color = "#FF0000"  # Red - failure
                alert_msg = f"❌ Failed to heal {process_id}"
            
            # Update status label with healing message
            self.status_var.set(alert_msg)
            self.active_alert_process = process_id
            
            # Schedule alert to expire after 3 seconds
            self.master.after(3000, self._clear_healing_alert)
            
            print(f"[ALERT_DISPLAY] {alert_msg} with color {alert_color}", flush=True)
        
        except Exception as e:
            print(f"[ALERT_DISPLAY] Error displaying alert: {e}", flush=True)
    
    def _clear_healing_alert(self) -> None:
        """Clear the current healing alert and reset status."""
        self.active_alert_process = None
        self.status_var.set("Ready")
    
    def _update_treeview(self, metrics_list: list, process_states: dict) -> None:
        """Update Treeview widget with process metrics (thread-safe).
        
        This runs on the main Tkinter thread via .after() callback.
        Displays process status, reliability scores, uptime, health status, and crash count.
        Uses color coding for health status (green=healthy, yellow=degraded, red=critical).
        
        Args:
            metrics_list: List of ProcessMetrics objects from registry
            process_states: Dictionary mapping process_id to ProcessState
        """
        try:
            # Get current item IDs in treeview
            existing_ids = set(self.process_treeview.get_children())
            
            # Track which process IDs we've seen in this update
            seen_process_ids = set()
            
            # Update or create entries for each process
            for metrics in metrics_list:
                process_id = metrics.process_id
                seen_process_ids.add(process_id)
                
                # Get process state if available
                state = process_states.get(process_id)
                state_str = state.value if state else "UNKNOWN"
                
                # Calculate formatted uptime (average in seconds)
                uptime_str = f"{metrics.average_uptime:.1f}"
                
                # Get reliability score (0-100 percentage)
                reliability = metrics.get_reliability_score()
                reliability_str = f"{reliability:.1f}%"
                
                # Get health status
                health = metrics.get_health_status()
                
                # Format crashes count
                crashes_str = str(metrics.total_crashes)
                
                # Determine tag color based on health status
                if health == "healthy":
                    tag = "health_healthy"
                elif health == "degraded":
                    tag = "health_degraded"
                else:  # critical
                    tag = "health_critical"
                
                # Create or update treeview item
                if process_id in self.treeview_items:
                    # Update existing item
                    item_id = self.treeview_items[process_id]
                    self.process_treeview.item(
                        item_id,
                        values=(state_str, reliability_str, uptime_str, health, crashes_str),
                        tags=(tag,)
                    )
                else:
                    # Create new item
                    item_id = self.process_treeview.insert(
                        "",
                        "end",
                        text=process_id,
                        values=(state_str, reliability_str, uptime_str, health, crashes_str),
                        tags=(tag,)
                    )
                    self.treeview_items[process_id] = item_id
            
            # Remove items for processes that no longer exist
            for process_id in list(self.treeview_items.keys()):
                if process_id not in seen_process_ids:
                    item_id = self.treeview_items[process_id]
                    self.process_treeview.delete(item_id)
                    del self.treeview_items[process_id]
        
        except Exception as e:
            print(f"[TREEVIEW] Error updating display: {e}", flush=True)
    
    def stop_monitoring(self) -> None:
        """Stop the process registry monitoring."""
        self.monitoring_active = False
        print("[GUI] Process registry monitoring stopped", flush=True)

    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode and close."""
        self.animation_alive = False
        self.stop_monitoring()
        self.master.attributes('-fullscreen', False)
        self.master.quit()
        self.master.destroy()
    
    def safe_exit(self):
        """Safe shutdown."""
        print("[GUI] Shutting down...", flush=True)
        self.animation_alive = False
        self.stop_monitoring()
        try:
            self.master.quit()
            self.master.destroy()
        except Exception as e:
            print(f"[GUI] Exit error: {e}", flush=True)


# Test/demo code
if __name__ == "__main__":
    root = tk.Tk()
    gui = FuturisticBotGUI(root)
    root.mainloop()
