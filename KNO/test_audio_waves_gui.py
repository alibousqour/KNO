#!/usr/bin/env python3
"""
Quick test of the futuristic BotGUI with audio waves.
This standalone script demonstrates the new UI.
"""

import tkinter as tk
import threading
import time
import math


class FuturisticBotGUI:
    """High-tech audio waves visualization GUI."""
    
    WAVE_COLOR_IDLE = "#00FFCC"
    WAVE_COLOR_THINKING = "#0088FF"
    WAVE_COLOR_SPEAKING = "#FF00FF"
    BG_COLOR = "#0a0a0a"
    
    def __init__(self, master):
        self.master = master
        self.master.title("KNO - Cybernetic AI Assistant")
        self.master.geometry('1200x800')
        self.master.configure(bg=self.BG_COLOR)
        
        self.is_speaking = False
        self.is_thinking = False
        self.wave_phase = 0.0
        self.animation_alive = True
        self.status_var = tk.StringVar(value="Ready")
        
        self.master.bind('<Escape>', lambda e: self.safe_exit())
        self.master.bind('<space>', self._toggle_speaking)
        
        # Top frame
        top = tk.Frame(self.master, bg=self.BG_COLOR)
        top.pack(fill=tk.X, padx=20, pady=(20, 10))
        tk.Label(top, text="KNO", font=("Arial", 32, "bold"), bg=self.BG_COLOR, fg=self.WAVE_COLOR_IDLE).pack(side=tk.LEFT)
        tk.Label(top, textvariable=self.status_var, font=("Arial", 12), bg=self.BG_COLOR, fg="#888888").pack(side=tk.RIGHT)
        
        # Canvas
        cf = tk.Frame(self.master, bg=self.BG_COLOR)
        cf.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.canvas = tk.Canvas(cf, bg=self.BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Input
        bf = tk.Frame(self.master, bg=self.BG_COLOR)
        bf.pack(fill=tk.X, padx=20, pady=(10, 20))
        self.text_entry = tk.Entry(bf, font=("Arial", 14), bg="#1a1a1a", fg=self.WAVE_COLOR_IDLE, insertbackground=self.WAVE_COLOR_IDLE, borderwidth=0)
        self.text_entry.insert(0, "Command KNO...")
        self.text_entry.pack(fill=tk.X, ipady=8)
        self.text_entry.bind('<FocusIn>', self._on_focus_in)
        self.text_entry.bind('<FocusOut>', self._on_focus_out)
        self.text_entry.bind('<Return>', self._on_enter)
        
        threading.Thread(target=self._animation_loop, daemon=True).start()
        print("[GUI] Futuristic BotGUI initialized", flush=True)
    
    def _animation_loop(self):
        while self.animation_alive:
            try:
                self.wave_phase += 0.05 if not self.is_speaking else 0.1
                if self.wave_phase > 2 * math.pi:
                    self.wave_phase -= 2 * math.pi
                self._draw_waves()
                time.sleep(1 / 60)
            except Exception as e:
                print(f"[ANIMATION] Error: {e}", flush=True)
    
    def _draw_waves(self):
        try:
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()
            if cw < 100 or ch < 100:
                return
            
            self.canvas.delete("all")
            
            if self.is_speaking:
                color, amp, bars = self.WAVE_COLOR_SPEAKING, 80, 32
            elif self.is_thinking:
                color, amp, bars = self.WAVE_COLOR_THINKING, 50, 24
            else:
                color, amp, bars = self.WAVE_COLOR_IDLE, 30, 16
            
            cx, cy = cw / 2, ch / 2
            bar_w = cw / (bars + 1)
            
            for i in range(bars):
                x = (i + 1) * bar_w
                angle = self.wave_phase + (i / bars) * (2 * math.pi)
                height = amp * (1.0 + 0.5 * math.sin(angle))
                y1, y2 = cy - height / 2, cy + height / 2
                self.canvas.create_line(x, y1, x, y2, fill=color, width=int(bar_w * 0.6))
            
            ring_r = 30 + 20 * math.sin(self.wave_phase) if not self.is_speaking else 50 + 30 * math.sin(self.wave_phase)
            self.canvas.create_oval(cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r, outline=color, width=2)
            self.canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill=color, outline=color)
            
            status_text = "SPEAKING" if self.is_speaking else ("THINKING" if self.is_thinking else "IDLE")
            self.canvas.create_text(cx, cy + 60, text=status_text, font=("Arial", 10, "bold"), fill=color, anchor=tk.N)
        except Exception:
            pass
    
    def _on_focus_in(self, e):
        if self.text_entry.get() == "Command KNO...":
            self.text_entry.delete(0, tk.END)
    
    def _on_focus_out(self, e):
        if self.text_entry.get() == "":
            self.text_entry.insert(0, "Command KNO...")
    
    def _on_enter(self, e):
        text = self.text_entry.get().strip()
        if text and text != "Command KNO...":
            print(f"[INPUT] {text}", flush=True)
            self.text_entry.delete(0, tk.END)
            self.is_thinking = True
            self.status_var.set("Thinking...")
            threading.Thread(target=self._process, daemon=True).start()
    
    def _process(self):
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
            self.status_var.set("Error")
    
    def _toggle_speaking(self, e):
        self.is_speaking = not self.is_speaking
        self.status_var.set("SPEAKING" if self.is_speaking else "IDLE")
    
    def safe_exit(self):
        self.animation_alive = False
        self.master.quit()


if __name__ == "__main__":
    root = tk.Tk()
    gui = FuturisticBotGUI(root)
    root.mainloop()
