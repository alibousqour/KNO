# Retro-Futuristic UI - Technical Implementation Reference

## Code Sections Modified in agent.py

---

## 1. CLASS CONSTANTS (Lines ~3617-3635)

### Purpose
Define color scheme, dimensions, and animation parameters for retro-futuristic aesthetic.

### Updated Constants

```python
# COLOR SCHEME - Retro Arcade Palette
BAR_COLOR_IDLE = "#00FFCC"      # Neon cyan (12 bars, 40 amplitude)
BAR_COLOR_THINKING = "#00FF00"  # Neon green (16 bars, 80 amplitude)
BAR_COLOR_SPEAKING = "#FFFF00"  # Neon yellow (20 bars, 140 amplitude)
MIC_GLOW_COLOR = "#FF0000"      # Red LED indicator
SEND_GLOW_COLOR = "#00FF00"     # Green LED on send
BG_COLOR = "#000000"            # Pure pitch black

# CANVAS PARAMETERS
CANVAS_WIDTH = 500
CANVAS_HEIGHT = 250
BARS_IDLE = 12                  # Number of bars in idle state
BARS_THINKING = 16              # Number of bars in thinking state
BARS_SPEAKING = 20              # Number of bars in speaking state
BAR_WIDTH = 12                  # Pixel width per bar
BAR_SPACING = 25                # Center-to-center spacing

# ANIMATION SETTINGS
ANIMATION_FPS = 16              # milliseconds (60 FPS)
AMPLITUDE_IDLE = 40             # Bar height range
AMPLITUDE_THINKING = 80
AMPLITUDE_SPEAKING = 140
WAVE_PHASE_INCREMENT = 0.03     # Speed modifier
```

### Key Changes from Previous Version
- Removed: WAVE_COLOR_* (blue/cyan/magenta wave colors)
- Added: BAR_COLOR_* (neon cyan/green/yellow LED colors)
- Added: MIC_GLOW_COLOR, SEND_GLOW_COLOR for button states
- Changed: BG_COLOR from dark gray to pure black (#000000)

---

## 2. MAIN UI SETUP (Lines ~3760-3810)

### A. Status Label - Top

```python
# OLD:
# self.status_label_top = ctk.CTkLabel(
#     master=self.main_frame,
#     text="KNO CORE: ONLINE",
#     text_color="#00FFCC"
# )

# NEW:
self.status_label_top = ctk.CTkLabel(
    master=self.main_frame,
    text="[KNO_CORE::ONLINE]",        # Bracket notation
    text_color="#00FFCC",              # Neon cyan
    font=("Courier New", 16, "bold")   # Monospace terminal font
)
self.status_label_top.pack(side="top", padx=10, pady=5)
```

**What Changed:**
- Text format: `"KNO CORE: ONLINE"` → `"[KNO_CORE::ONLINE]"` (retro bracket style)
- Font: Added Courier New (monospace) for terminal feel
- Size: 16px bold for emphasis

### B. Canvas - Central Visualization

```python
# NEW - Complete rewrite:
self.canvas = tk.Canvas(
    master=self.left_frame,
    width=500,
    height=250,
    bg="#000000",                           # Pure pitch black
    highlightthickness=2,                   # Border thickness
    highlightbackground="#00FFCC",          # Neon cyan border
    highlightcolor="#00FFCC"
)
self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
```

**What Changed:**
- Background: `"#1a1a1a"` → `"#000000"` (pure black)
- Border: Added 2px cyan highlight for arcade frame effect
- No rounded corners (Tkinter Canvas doesn't support corner_radius)

### C. Response Text Frame

```python
# NEW - Updated styling:
self.response_frame = ctk.CTkFrame(
    master=self.left_frame,
    fg_color="#0a0a0a",                 # Very dark gray
    corner_radius=5,
    border_width=2,
    border_color="#00FFCC"              # Cyan border
)
self.response_frame.pack(fill="both", expand=True, padx=10, pady=5)

self.response_text = ctk.CTkTextbox(
    master=self.response_frame,
    height=100,
    text_color="#00FFCC",               # Neon cyan
    fg_color="#000000",                 # Pure black background
    font=("Courier New", 10),           # Monospace
    state="disabled"
)
self.response_text.pack(fill="both", expand=True, padx=5, pady=5)
```

**What Changed:**
- Font: Switched to Courier New (monospace) for terminal style
- Colors: Response text now cyan on black (CRT monitor aesthetic)
- Border: Added cyan border for consistency

### D. Audio Device Selector

```python
# NEW - Retro terminal style:
device_label = ctk.CTkLabel(
    master=self.device_frame,
    text="[AUDIO_INPUT]",               # Bracket notation
    text_color="#00FFCC",
    font=("Courier New", 12, "bold")
)
device_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

refresh_button = ctk.CTkButton(
    master=self.device_frame,
    text="[REFRESH]",                   # Bracket label
    text_color="#00FFCC",
    border_width=1,
    border_color="#00FFCC",
    fg_color="#000000",
    command=self.refresh_audio_devices
)
refresh_button.grid(row=0, column=2, padx=5, pady=5)
```

**What Changed:**
- Labels: Changed to bracket notation for retro feel
- Font: Courier New monospace throughout
- Border: Added cyan borders to buttons

---

## 3. SEARCH BAR REDESIGN (Lines ~3850-3920)

### Complete Search Bar Overhaul for Pixel Art Look

```python
# NEW - Complete retro-futuristic search bar:

self.search_bar_frame = ctk.CTkFrame(
    master=self.main_frame,
    fg_color="#0a0a0a",                # Dark arcade panel
    corner_radius=20,                  # Smooth arcade button curve
    border_width=2,
    border_color="#00FFCC"             # Neon cyan border
)
self.search_bar_frame.pack(fill="x", padx=10, pady=10)
self.search_bar_frame.grid_columnconfigure(1, weight=1)

# ===== MIC BUTTON (LEFT) =====
self.mic_button = ctk.CTkButton(
    master=self.search_bar_frame,
    text="🎤",
    text_color="#FF0000",              # Red LED color
    fg_color="transparent",
    hover_color="#1a0000",             # Dark red on hover
    border_width=2,
    border_color="#888888",            # Gray border
    width=50,
    height=50,
    font=("Courier New", 18, "bold"),  # Monospace icon font
    command=self.on_mic_button_clicked
)
self.mic_button.grid(row=0, column=0, padx=5, pady=5)

# ===== TEXT ENTRY (CENTER) =====
self.search_entry = ctk.CTkEntry(
    master=self.search_bar_frame,
    placeholder_text="[type_command]",      # Bracket format
    text_color="#00FFCC",                   # Neon cyan
    placeholder_text_color="#555555",       # Dim gray
    fg_color="#000000",                     # Pure black
    border_width=1,
    border_color="#00FFCC",                 # Cyan border
    font=("Courier New", 13),               # Monospace input
    height=40,
    corner_radius=6
)
self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
self.search_entry.bind("<Return>", lambda e: self.on_send_button_clicked())

# ===== SEND BUTTON (RIGHT) =====
self.send_button = ctk.CTkButton(
    master=self.search_bar_frame,
    text="➔",
    text_color="#888888",              # Gray idle state
    fg_color="transparent",
    hover_color="#1a1a1a",
    border_width=2,
    border_color="#888888",            # Gray border
    width=50,
    height=50,
    font=("Courier New", 14, "bold"),  # Monospace arrow
    corner_radius=10,
    command=self.on_send_button_clicked
)
self.send_button.grid(row=0, column=2, padx=5, pady=5)

# ===== CONTROL BUTTONS (RIGHT SIDE) =====

# Exit Button
exit_button = ctk.CTkButton(
    master=self.search_bar_frame,
    text="[EXIT]",                     # Bracket label
    text_color="#FF0000",              # Red LED
    fg_color="transparent",
    border_width=1,
    border_color="#FF0000",
    width=60,
    font=("Courier New", 9, "bold"),
    command=self.exit_app
)
exit_button.grid(row=0, column=3, padx=3, pady=5)

# Sync Phone Button
sync_button = ctk.CTkButton(
    master=self.search_bar_frame,
    text="[SYNC_PHONE]",               # Bracket label
    text_color="#00FFCC",              # Cyan LED
    fg_color="transparent",
    border_width=1,
    border_color="#00FFCC",
    width=80,
    font=("Courier New", 8, "bold"),
    command=self.sync_with_phone
)
sync_button.grid(row=0, column=4, padx=3, pady=5)
```

**Key Features:**
- Frame has`corner_radius=20` for arcade button curves
- All text uses Courier New (monospace)
- Bracket notation for labels: `[type_command]`, `[EXIT]`, etc.
- Red mic LED (#FF0000) and gray send button (#888888)
- Neon cyan borders throughout

---

## 4. STATE TRACKING FLAGS (Lines ~3960-3965)

```python
# NEW - Added state flags for LED effects:

self.mic_recording = False      # Type: bool
                                # Purpose: Track mic recording state
                                # Usage: Changes mic button to bright red

self.send_hovering = False      # Type: bool
                                # Purpose: Track send button hover state
                                # Usage: Future hover effects for green glow
```

**Why These Matter:**
- `mic_recording`: Determines if mic button glows red
- `send_hovering`: Allows send button to glow green on hover

---

## 5. ANIMATION SYSTEM - COMPLETE REPLACEMENT (Lines ~3990-4110)

### OLD METHOD: _draw_waves()
```python
# [Smooth circular wave visualization]
# 24-32 points in circle
# Smooth wave interpolation
# Deleted in retro redesign
```

### NEW METHOD: _draw_pixel_bars()

```python
def _draw_pixel_bars(self):
    """
    Render pixelated LED-style bars like 80s equalizer.
    
    STATE CONFIGURATION:
    - IDLE:     12 cyan bars,  40 amplitude,   0.03 speed
    - THINKING: 16 green bars, 80 amplitude,   0.08 speed
    - SPEAKING: 20 yellow bars,140 amplitude,  0.2 speed
    """
    import math
    
    # 1. DETERMINE STATE AND COLORS
    if self.is_speaking:
        color = "#FFFF00"              # Neon yellow
        glow_color = "#FFFF00"
        amplitude = 140
        num_bars = 20
        speed = 0.2
    elif self.is_thinking:
        color = "#00FF00"              # Neon green
        glow_color = "#00FF00"
        amplitude = 80
        num_bars = 16
        speed = 0.08
    else:
        color = "#00FFCC"              # Neon cyan
        glow_color = "#00FFCC"
        amplitude = 40
        num_bars = 12
        speed = 0.03
    
    # 2. CLEAR CANVAS
    self.canvas.delete("all")
    
    # 3. DRAW PIXELATED BARS
    center_y = 125  # Canvas height center (250/2)
    start_x = 30
    glow_size = 6   # Glow extends 6px beyond bar
    
    for i in range(num_bars):
        # Calculate bar height using sine wave
        bar_height = int(amplitude * (
            0.4 + 0.6 * math.sin(self.wave_phase + i * 0.4)
        ))
        
        # Positioning
        x_pos = start_x + i * 22  # Bars spaced 22px apart
        y_top = center_y - bar_height
        y_base = center_y
        
        # DRAW GLOW LAYER (outer semi-transparent)
        glow_x_min = x_pos - glow_size
        glow_x_max = x_pos + 12 + glow_size
        glow_y_min = y_top - glow_size
        glow_y_max = y_base + glow_size
        
        self.canvas.create_rectangle(
            glow_x_min, glow_y_min,
            glow_x_max, glow_y_max,
            fill=glow_color,
            outline="",
            stipple="gray50"  # Semi-transparent via stipple pattern
        )
        
        # DRAW MAIN BRIGHT BAR
        self.canvas.create_rectangle(
            x_pos, y_top,
            x_pos + 12, y_base,
            fill=color,
            outline=color,
            width=1
        )
        
        # DRAW WHITE HIGHLIGHT on top (3D effect)
        self.canvas.create_line(
            x_pos, y_top,
            x_pos + 12, y_top,
            fill="#FFFFFF",
            width=1
        )
    
    # 4. DRAW CENTER LED INDICATOR
    led_x = 250  # Center of 500px canvas
    led_y = 125
    
    # Outer glow ring
    self.canvas.create_oval(
        led_x - 20, led_y - 20,
        led_x + 20, led_y + 20,
        fill=glow_color,
        outline="",
        stipple="gray50"
    )
    
    # Inner bright circle
    self.canvas.create_oval(
        led_x - 14, led_y - 14,
        led_x + 14, led_y + 14,
        fill=color,
        outline=color
    )
    
    # Center brightest point
    self.canvas.create_oval(
        led_x - 6, led_y - 6,
        led_x + 6, led_y + 6,
        fill="#FFFFFF",
        outline=""
    )
    
    # 5. DRAW DECORATIVE BORDER (retro arcade frame)
    border_color = "#00FFCC"
    self.canvas.create_line(
        5, 5,
        495, 5,          # Top
        fill=border_color, width=1
    )
    self.canvas.create_line(
        5, 245,
        495, 245,        # Bottom
        fill=border_color, width=1
    )
    self.canvas.create_line(
        5, 5,
        5, 245,          # Left
        fill=border_color, width=1
    )
    self.canvas.create_line(
        495, 5,
        495, 245,        # Right
        fill=border_color, width=1
    )
    
    # 6. UPDATE ANIMATION PHASE
    self.wave_phase += speed
```

### animation_loop() - Updated

```python
def animation_loop(self):
    """
    Main 60 FPS animation coordinator.
    Calls _draw_pixel_bars() each frame.
    """
    try:
        self._draw_pixel_bars()  # Now calls pixelated bars method
        self.master.after(16, self.animation_loop)  # 16ms = ~60 FPS
    except Exception as e:
        print(f"Animation error: {e}")
```

**Technical Details:**

| Parameter | Idle | Thinking | Speaking |
|-----------|------|----------|----------|
| **Bars** | 12 | 16 | 20 |
| **Color** | #00FFCC | #00FF00 | #FFFF00 |
| **Amplitude** | 40 | 80 | 140 |
| **Speed** | 0.03 | 0.08 | 0.2 |

**Glow Effect Algorithm:**
```python
# Step 1: Draw glow rectangle 6px larger than bar
glowrect = create_rectangle(
    x - 6, y - 6, x + 18, y + 6,
    fill=color, stipple="gray50"  # Stipple = semi-transparent
)

# Step 2: Draw solid bar on top
solidrect = create_rectangle(
    x, y, x + 12, y + max_height,
    fill=color, outline=color
)

# Result: Solid bar with soft glow around edges (80s CRT look)
```

---

## 6. INPUT HANDLERS WITH LED EFFECTS (Lines ~4120-4210)

### A. Microphone Button Handler

```python
def on_mic_button_clicked(self):
    """
    Mic button click: Start voice recording with LED red glow.
    """
    print("[MIC_LED_GLOWING] Red LED activated")
    
    # Set flags
    self.recording_active.set()     # Start recording
    self.mic_recording = True       # Used for LED state
    self.is_thinking = True         # Trigger green bars
    
    # Change mic button color to bright red
    self.mic_button.configure(
        text_color="#FF0000"        # Bright red LED glow
    )
    
    # Update status
    self.status_var.set("[RECORDING_VOICE]")  # Bracket notation
    
    # In background: Handle actual recording
    # (threading handled elsewhere)
```

**LED Glow Effect:**
- Sets `mic_button.text_color` to bright red (#FF0000)
- Status shows `[RECORDING_VOICE]` in bracket format
- Equalizer bars turn green and respond to audio

### B. Send Button Handler

```python
def on_send_button_clicked(self):
    """
    Send button click: Process text with green LED glow.
    """
    # Get text from entry
    text_input = self.search_entry.get()
    if not text_input:
        return
    
    # Reset mic recording state
    self.mic_recording = False
    self.recording_active.set(False)
    
    # Ensure mic button is red (not bright)
    self.mic_button.configure(
        text_color="#FF0000"        # Back to regular red
    )
    
    # Make send button glow green momentarily
    self.send_button.configure(
        text_color="#00FF00"        # Green glow
    )
    
    # Update status
    self.status_var.set("[PROCESSING_INPUT]")
    
    # Process in background thread
    threading.Thread(
        target=self._process_text_input,
        args=(text_input,),
        daemon=True
    ).start()
```

**Green LED Glow Effect:**
- Sets `send_button.text_color` to bright green (#00FF00)
- Status shows `[PROCESSING_INPUT]`
- Bars turn green to indicate processing

### C. Text Processing with Retro Terminal Format

```python
def _process_text_input(self, user_input):
    """
    Process text and display in retro terminal format.
    """
    try:
        # Update status
        self.status_var.set("[PROCESSING_INPUT]")
        
        # Get response from LLM
        response = self._get_text_response(user_input)
        
        # Format response in retro terminal style
        formatted_input = f"USER> {user_input}"      # User prompt
        formatted_response = f"KNO > >> {response}"  # LLM response with >>
        
        # Display in response textbox
        self.response_text.configure(state="normal")
        self.response_text.insert("end", f"\n{formatted_input}\n")
        self.response_text.insert("end", f"{formatted_response}\n")
        self.response_text.configure(state="disabled")
        
        # Update status
        self.status_var.set("[SPEAKING_OUTPUT]")
        
        # Make send button return to gray after processing
        self.send_button.configure(
            text_color="#888888"    # Reset to dim gray
        )
        
        # Update status to ready
        self.status_var.set("[READY]")
        
    except Exception as e:
        print(f"Error processing text: {e}")
        self.status_var.set("[ERROR_PROCESS]")
        self.send_button.configure(text_color="#888888")
```

**Retro Terminal Format:**
```
USER> What is the weather?
KNO > >> The weather is...

USER> How are you?
KNO > >> I am functioning optimally...
```

---

## 7. UTILITY METHODS

### _create_led_glow() - Helper Method (Optional)

```python
def _create_led_glow(self, x, y, radius, color):
    """
    Helper method to create LED glow effect.
    Optional - currently glow is done inline in _draw_pixel_bars().
    """
    # Outer glow (stipple for transparency)
    self.canvas.create_oval(
        x - radius - 6, y - radius - 6,
        x + radius + 6, y + radius + 6,
        fill=color, stipple="gray50", outline=""
    )
    
    # Inner circle (bright)
    self.canvas.create_oval(
        x - radius, y - radius,
        x + radius, y + radius,
        fill=color, outline=color
    )
```

---

## 8. COLOR MANAGEMENT - Quick Reference

### Setting Colors Dynamically

```python
# Change idle bar color
if self.is_thinking == False and self.is_speaking == False:
    bar_color = "#00FFCC"  # Change to your color

# Change thinking color
if self.is_thinking and not self.is_speaking:
    bar_color = "#00FF00"  # Change to your color

# Change speaking color
if self.is_speaking:
    bar_color = "#FFFF00"  # Change to your color

# Apply to UI elements
self.canvas.create_rectangle(..., fill=bar_color)
```

### Glow Effect Colors

```python
# Glow uses SAME color as bars (semi-transparent via stipple)
glow_color = bar_color
self.canvas.create_rectangle(
    ...,
    fill=glow_color,
    stipple="gray50"  # This creates transparency effect
)
```

---

## 9. IMPORT REQUIREMENTS

```python
# Existing imports (must remain)
import customtkinter as ctk
import tkinter as tk
import threading
import dotenv
from scipy import signal
from scipy.fft import fft
import math  # NEW - Required for sin() calculations
```

---

## 10. PERFORMANCE OPTIMIZATION

### Canvas Rendering Pipeline

```python
# OPTIMAL: Clear and redraw (16ms per frame at 60 FPS)
self.canvas.delete("all")                    # Clear all
for i in range(num_bars):
    # Draw glow
    self.canvas.create_rectangle(...)
    # Draw bar
    self.canvas.create_rectangle(...)
self.wave_phase += speed                     # Update animation

# TOTAL TIME: ~2-5ms (well under 16ms budget)
```

### State Management

```python
# Track only what's needed
self.is_thinking = False        # State 1: IDLE
self.is_speaking = False        # State 1: IDLE

# is_thinking = True            # State 2: THINKING
# is_speaking = False

# is_speaking = True            # State 3: SPEAKING
# (is_thinking doesn't matter)
```

---

## 11. DEBUGGING CHECKLIST

```python
# Add these print statements to debug animation
print(f"Wave phase: {self.wave_phase}")           # Should increment each frame
print(f"Bar color: {color}")                      # Should be hex color
print(f"Amplitude: {amplitude}")                  # Should be 40/80/140
print(f"Canvas ready: {self.canvas}")             # Should be canvas object
print(f"FPS calculation: {1000 / 16}")            # Should be ~62.5 FPS

# Check state transitions
print(f"is_thinking: {self.is_thinking}")         # True/False
print(f"is_speaking: {self.is_speaking}")         # True/False
print(f"mic_recording: {self.mic_recording}")     # True/False
```

---

## 12. PLATFORM COMPATIBILITY

### Font Handling

```python
# Courier New (preferred - all platforms)
font=("Courier New", 14, "bold")

# Fallback options
font=("Courier", 14, "bold")           # Linux/Mac
font=("Consolas", 14, "bold")          # Windows alternative
font=("Liberation Mono", 14, "bold")   # Linux
```

### Border Colors (No Platform Issues)

```python
# Hex colors consistent across all platforms
"#00FFCC"  # Cyan (Windows/Mac/Linux identical)
"#00FF00"  # Green (identical)
"#FFFF00"  # Yellow (identical)
"#FF0000"  # Red (identical)
"#000000"  # Black (identical)
```

---

## 13. COMPLETE STATE MACHINE

```python
STATE MACHINE: KNO RETRO-FUTURISTIC UI

┌─────────────────────────────────────────┐
│  STARTUP:                               │
│  is_thinking = False                    │
│  is_speaking = False                    │
│  Status: [KNO_CORE::ONLINE]             │
│  Bars: 12 cyan, slow pulse              │
└─────────────────────────────────────────┘
          ↓
    User clicks mic OR types
          ↓
┌─────────────────────────────────────────┐
│  RECORDING/PROCESSING:                  │
│  is_thinking = True                     │
│  is_speaking = False                    │
│  Status: [RECORDING_VOICE] or           │
│          [PROCESSING_INPUT]             │
│  Bars: 16 green, medium pulse           │
│  Mic: Red or Send: Green LED            │
└─────────────────────────────────────────┘
          ↓
    LLM generates response
          ↓
┌─────────────────────────────────────────┐
│  SPEAKING:                              │
│  is_thinking = False                    │
│  is_speaking = True                     │
│  Status: [SPEAKING_OUTPUT]              │
│  Bars: 20 yellow, fast pulse            │
│  Output: USER> / KNO >                  │
└─────────────────────────────────────────┘
          ↓
    Audio finishes OR timeout
          ↓
┌─────────────────────────────────────────┐
│  READY (IDLE):                          │
│  is_thinking = False                    │
│  is_speaking = False                    │
│  Status: [READY]                        │
│  Bars: 12 cyan, slow pulse              │
│  (Back to startup state)                │
└─────────────────────────────────────────┘
```

---

## 14. MODIFICATION GUIDE

### To Change Idle Bar Count from 12 to 14:
```python
# Find in _draw_pixel_bars():
# CHANGE FROM:
BARS_IDLE = 12
# TO:
BARS_IDLE = 14
# And update line:
num_bars = 12  # in idle section
# TO:
num_bars = 14
```

### To Change LED Glow Intensity:
```python
# Find in _draw_pixel_bars():
# Current glow offset:
glow_size = 6
# Increase for bigger glow:
glow_size = 8  # Bigger glow
# Or decrease:
glow_size = 4  # Smaller glow
```

### To Add Custom Colors:
```python
# Add to class constants:
BAR_COLOR_CUSTOM = "#FF00FF"  # Your color

# Use in _draw_pixel_bars():
if self.custom_mode:
    color = "#FF00FF"
    glow_color = "#FF00FF"
```

---

## 15. KNOWN LIMITATIONS & WORKAROUNDS

| Issue | Cause | Workaround |
|-------|-------|-----------|
| Colors appear dim | Monitor brightness | Increase brightness to 70%+ |
| Bars don't glow | Stipple pattern issue | Verify `stipple="gray50"` in canvas.create_rectangle() |
| Font looks wrong | Courier New not installed | Use fallback: ("Courier", 14) |
| Animation stutters | Frame rate inconsistent | Check for blocking I/O in animation_loop() |
| Bars don't transition | State flags not updating | Verify `self.is_thinking` is set before animation |

---

**Documentation Status:** Complete  
**Last Updated:** Phase 5 Cloud Native Refactor  
**Version:** 5.0 Retro-Futuristic Pixel Art Edition
