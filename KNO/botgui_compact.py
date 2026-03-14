# ===== COMPACT BOTGUI REPLACEMENT WITH FUTURISTIC AUDIO WAVES =====
# This is a streamlined version to replace the massive BotGUI class in agent.py

class BotGUI:
    """
    Futuristic BotGUI with Audio Wave Visualization
    High-tech cybernetic interface centered around neon animated waves.
    System Prompt: "You are KNO, a highly advanced cybernetic AI assistant. Be concise, professional, and act as a voice-first system."
    """
    
    # UI Constants
    WAVE_COLOR_IDLE = "#00FFCC"      # Neon cyan
    WAVE_COLOR_THINKING = "#0088FF"  # Neon blue
    WAVE_COLOR_SPEAKING = "#FF00FF"  # Neon magenta
    BG_COLOR = "#0a0a0a"             # Deep black
    BG_WIDTH, BG_HEIGHT = 1200, 800
    
    def __init__(self, master):
        """Initialize futuristic audio waves UI."""
        self.master = master
        self.master.title("KNO - Cybernetic AI Assistant")
        
        # Try fullscreen
        try:
            self.master.attributes('-fullscreen', True)
            print("[GUI] Fullscreen enabled", flush=True)
        except Exception as e:
            print(f"[GUI] Fullscreen failed ({e}), using windowed mode", flush=True)
            self.master.geometry('1200x800')
        
        self.master.bind('<Escape>', self.exit_fullscreen)
        
        # ===== STATE =====
        self.master.configure(bg=self.BG_COLOR)
        self.is_speaking = False
        self.is_thinking = False
        self.wave_phase = 0.0
        self.animation_running = True
        self.status_var = tk.StringVar(value="Ready")
        self.user_input_queue = []
        
        # Cloud mode check
        self.cloud_llm_mode = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY"))
        self.model_file_missing = False
        
        # Simple state for compatibility
        self.current_state = "IDLE"
        self.permanent_memory = self.load_chat_history()
        self.session_memory = []
        self.recording_active = threading.Event()
        self.tts_queue = []
        self.tts_queue_lock = threading.Lock()
        self.tts_active = threading.Event()
        self.current_audio_process = None
        self.phone_connected = False
        
        # ===== BUILD UI =====
        
        # Top frame with title and status
        top_frame = tk.Frame(self.master, bg=self.BG_COLOR, height=60)
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
        
        # Audio wave canvas (main element)
        canvas_frame = tk.Frame(self.master, bg=self.BG_COLOR)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            bg=self.BG_COLOR,
            highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bottom text input
        bottom_frame = tk.Frame(self.master, bg=self.BG_COLOR)
        bottom_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
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
        
        # Bind entry events
        self.text_entry.bind('<FocusIn>', self._on_entry_focus_in)
        self.text_entry.bind('<FocusOut>', self._on_entry_focus_out)
        self.text_entry.bind('<Return>', self._on_enter_pressed)
        
        # Keyboard controls
        self.master.bind('<space>', self._toggle_speaking_state)
        atexit.register(self.safe_exit)
        
        # Start animation thread
        self.animation_alive = True
        self.animation_thread = threading.Thread(target=self._animation_loop, daemon=True)
        self.animation_thread.start()
        
        print("[GUI] Futuristic BotGUI with audio waves initialized", flush=True)
    
    def _animation_loop(self):
        """Background animation loop."""
        frame_rate = 60
        frame_time = 1.0 / frame_rate
        
        while self.animation_alive:
            try:
                self.wave_phase += 0.05 if not self.is_speaking else 0.1
                if self.wave_phase > 2 * 3.14159:
                    self.wave_phase -= 2 * 3.14159
                
                self._draw_waves()
                time.sleep(frame_time)
            except Exception as e:
                print(f"[ANIMATION] Error: {e}", flush=True)
                time.sleep(0.016)
    
    def _draw_waves(self):
        """Draw animated audio waves."""
        try:
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()
            
            if cw < 100 or ch < 100:
                return
            
            self.canvas.delete("all")
            
            if self.is_speaking:
                color = self.WAVE_COLOR_SPEAKING
                amp = 80
                bars = 32
            elif self.is_thinking:
                color = self.WAVE_COLOR_THINKING
                amp = 50
                bars = 24
            else:
                color = self.WAVE_COLOR_IDLE
                amp = 30
                bars = 16
            
            cx, cy = cw / 2, ch / 2
            bar_w = cw / (bars + 1)
            
            # Draw equalizer bars
            for i in range(bars):
                x = (i + 1) * bar_w
                angle = self.wave_phase + (i / bars) * (2 * 3.14159)
                wave_offset = __import__('math').sin(angle)
                height = amp * (1.0 + 0.5 * wave_offset)
                
                y1 = cy - height / 2
                y2 = cy + height / 2
                
                self.canvas.create_line(
                    x, y1, x, y2,
                    fill=color,
                    width=int(bar_w * 0.6)
                )
            
            # Draw center ring
            ring_r = 30 + 20 * __import__('math').sin(self.wave_phase)
            if self.is_speaking:
                ring_r = 50 + 30 * __import__('math').sin(self.wave_phase)
            
            self.canvas.create_oval(
                cx - ring_r, cy - ring_r,
                cx + ring_r, cy + ring_r,
                outline=color,
                width=2
            )
            
            # Center dot
            self.canvas.create_oval(
                cx - 5, cy - 5,
                cx + 5, cy + 5,
                fill=color,
                outline=color
            )
            
            # Status text
            status_text = "SPEAKING" if self.is_speaking else ("THINKING" if self.is_thinking else "IDLE")
            self.canvas.create_text(
                cx, cy + 60,
                text=status_text,
                font=("Arial", 10, "bold"),
                fill=color,
                anchor=tk.N
            )
        except Exception as e:
            pass
    
    def _on_entry_focus_in(self, event):
        """Handle entry focus."""
        if self.text_entry.get() == "Command KNO...":
            self.text_entry.delete(0, tk.END)
            self.text_entry.config(fg=self.WAVE_COLOR_IDLE)
    
    def _on_entry_focus_out(self, event):
        """Handle entry blur."""
        if self.text_entry.get() == "":
            self.text_entry.insert(0, "Command KNO...")
            self.text_entry.config(fg="#666666")
    
    def _on_enter_pressed(self, event):
        """Handle Enter key - send command."""
        user_input = self.text_entry.get().strip()
        
        if user_input and user_input != "Command KNO...":
            print(f"[INPUT] User: {user_input}", flush=True)
            self.user_input_queue.append(user_input)
            self.text_entry.delete(0, tk.END)
            self.is_thinking = True
            self.status_var.set("Thinking...")
            
            threading.Thread(target=self._process_command, args=(user_input,), daemon=True).start()
    
    def _process_command(self, command):
        """Process a command."""
        try:
            time.sleep(1)
            self.is_thinking = False
            self.is_speaking = True
            self.status_var.set("Speaking...")
            time.sleep(2)
            self.is_speaking = False
            self.status_var.set("Ready")
        except Exception as e:
            print(f"[PROCESS] Error: {e}", flush=True)
            self.is_thinking = False
            self.is_speaking = False
            self.status_var.set("Error")
    
    def _toggle_speaking_state(self, event):
        """Toggle speaking state."""
        self.is_speaking = not self.is_speaking
        status = "SPEAKING" if self.is_speaking else "IDLE"
        self.status_var.set(status)
    
    def exit_fullscreen(self, event=None):
        """Exit fullscreen."""
        self.animation_alive = False
        self.master.attributes('-fullscreen', False)
        self.safe_exit()
    
    def safe_exit(self):
        """Safe shutdown."""
        print("[GUI] Shutting down...", flush=True)
        self.animation_alive = False
        self.save_chat_history()
        try:
            self.master.quit()
            self.master.destroy()
        except:
            pass
    
    def request_action_approval(self, action_type, details):
        """Request user approval."""
        try:
            from tkinter import messagebox
            result = messagebox.askyesno("Approval", f"{action_type}\n\n{details}\n\nApprove?")
            print(f"[APPROVAL] {action_type}: {'YES' if result else 'NO'}", flush=True)
            return result
        except:
            return False
    
    def handle_incoming_notification(self, sender, message):
        """Handle notification."""
        print(f"[NOTIFY] {sender}: {message}", flush=True)
    
    def load_chat_history(self):
        """Load chat history."""
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return [{"role": "system", "content": 'You are KNO, a highly advanced cybernetic AI assistant. Be concise, professional, and act as a voice-first system.'}]
    
    def save_chat_history(self):
        """Save chat history."""
        try:
            full = self.permanent_memory + self.session_memory
            conv = full[1:]
            if len(conv) > 10:
                conv = conv[-10:]
            with open(MEMORY_FILE, "w") as f:
                json.dump([full[0]] + conv, f, indent=4)
        except Exception as e:
            print(f"[MEMORY] Save error: {e}", flush=True)
