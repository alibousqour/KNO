# Retro-Futuristic UI Testing Checklist

## Quick Reference: Feature Validation

---

## ✅ Visual Elements Checklist

### 1. **Background & Base Colors**
- [ ] Pure pitch black background (#000000) visible on startup
- [ ] No gray gradients or lighter backgrounds
- [ ] Canvas area shows black with dark interior
- [ ] Status bar background is pitch black

### 2. **Neon Color Accents**
- [ ] Canvas has bright cyan border (2px, #00FFCC)
- [ ] Response text is neon cyan (#00FFCC)
- [ ] Idle mode shows cyan bars
- [ ] Thinking mode shows green bars (#00FF00)
- [ ] Speaking mode shows yellow bars (#FFFF00)

### 3. **Monospace Typography**
- [ ] All text uses Courier New font (monospace)
- [ ] Status labels appear in bracket format: `[KNO_CORE::ONLINE]`
- [ ] Control buttons show brackets: `[EXIT]`, `[SYNC_PHONE]`
- [ ] Text entry placeholder shows `[type_command]`
- [ ] Response display prefixed with `>>`

### 4. **LED Glow Effects**
- [ ] Mic button glows red when recording
- [ ] Send button glows green when clicked
- [ ] Pixelated bars have faint glow around edges
- [ ] Center LED indicator visible and glowing
- [ ] No smooth gradients (all LED stipple pattern)

### 5. **Pixelated Audio Bars**
- [ ] Idle state: 12 cyan bars, slow pulsing
- [ ] Thinking state: 16 green bars, medium pulsing
- [ ] Speaking state: 20 yellow bars, fast pulsing
- [ ] Bars have white highlight on top edge (3D)
- [ ] All bars same width (12px per bar)

### 6. **Search Bar Components**
- [ ] Frame has corner_radius=20 (rounded arcade style)
- [ ] 2px neon cyan border around search bar
- [ ] Mic button on left (red LED, #FF0000)
- [ ] Text entry centered with black background
- [ ] Send button on right (gray → green on action)
- [ ] Exit button shows red bracket `[EXIT]`
- [ ] Sync button shows cyan bracket `[SYNC_PHONE]`

---

## 🎮 Functional Tests

### A. **Voice Input (Microphone)**
1. [ ] Click mic button
2. [ ] Verify: Mic button turns bright red (#FF0000)
3. [ ] Verify: Status shows `[RECORDING_VOICE]`
4. [ ] Verify: Equalizer bars turn green and pulse faster
5. [ ] Speak into microphone
6. [ ] Verify: Bars respond to audio input
7. [ ] Wait for response
8. [ ] Verify: Bars turn yellow during speech output
9. [ ] Verify: Status shows `[SPEAKING_OUTPUT]`
10. [ ] Verify: Back to cyan idle after done

### B. **Text Input (Send Button)**
1. [ ] Type text in entry field
2. [ ] Press Enter (or click send button)
3. [ ] Verify: Send button glows green (#00FF00)
4. [ ] Verify: Status shows `[PROCESSING_INPUT]`
5. [ ] Verify: Response appears in terminal format
6. [ ] Verify: Response shows `USER> [your text]`
7. [ ] Verify: Response shows `KNO > >> [result]`
8. [ ] Verify: Bars turn yellow during processing
9. [ ] Verify: Response text is cyan (#00FFCC)
10. [ ] Verify: Back to idle cyan bars (#00FFCC)

### C. **Status Indicator Updates**
1. [ ] On startup: `[KNO_CORE::ONLINE]`
2. [ ] On mic recording: `[RECORDING_VOICE]`
3. [ ] On text send: `[PROCESSING_INPUT]`
4. [ ] During speaking: `[SPEAKING_OUTPUT]`
5. [ ] When ready: `[READY]`
6. [ ] On error: `[ERROR_PROCESS]`

### D. **Control Button Response**
1. [ ] Exit button (`[EXIT]`):
   - [ ] Shows red color
   - [ ] Closes application on click
   - [ ] Or minimizes (verify behavior)

2. [ ] Sync Phone button (`[SYNC_PHONE]`):
   - [ ] Shows cyan color
   - [ ] Has proper functionality

3. [ ] Refresh Audio button:
   - [ ] Shows `[REFRESH]` label
   - [ ] Reloads audio devices

---

## 🎨 Animation Benchmark

### Frame Rate Test
- [ ] Animation runs smooth (60 FPS, no stuttering)
- [ ] Bars update smoothly
- [ ] LED glow effect consistent
- [ ] No lag during processing

### State Transitions
- [ ] IDLE → THINKING: Bars instantly turn green
- [ ] THINKING → SPEAKING: Bars instantly turn yellow
- [ ] SPEAKING → IDLE: Bars return to cyan
- [ ] All transitions happen within <100ms

### Glow Effects
- [ ] Glow is visible but not overpowering
- [ ] Stipple pattern creates semi-transparent effect
- [ ] Center LED indicator glows in all states
- [ ] Red glow appears with mic button recording

---

## 🔊 Audio Visualization

### Response Text Display
1. Type: "Hello KNO"
2. Verify response format:
   ```
   USER> Hello KNO
   KNO > >> Response text here...
   ```
3. Check all responses use this format
4. Verify `>>` prefix present
5. Verify cyan text color (#00FFCC)

### Multiline Responses
- [ ] Long responses display properly
- [ ] Text wrapping works
- [ ] Cyan color maintained
- [ ] Courier New font maintained
- [ ] Terminal format preserved

---

## 🎯 Performance Checks

### Resource Usage
- [ ] CPU usage reasonable while animating
- [ ] Memory stable (no memory leaks)
- [ ] No canvas flickering
- [ ] Smooth scrolling in response area

### Compatibility
- [ ] Works at 1920x1080 resolution
- [ ] Works at 1280x720 resolution
- [ ] Works at ultrawide (3440x1440)
- [ ] Fullscreen mode supported
- [ ] Window resizing works

---

## 🐛 Known Behaviors

### Expected on First Run
- [ ] Takes ~2-3 seconds to initialize TTS/STT
- [ ] First audio test may have latency
- [ ] Bars may not move smoothly if no audio permission

### Audio Device Issues
- [ ] If mic not detected: Use `[REFRESH]` button
- [ ] If audio output quiet: Check speaker volume
- [ ] If no glow visible: Check display brightness

---

## 📋 Detailed State Testing

### State 1: IDLE (Startup)
```
Status: [KNO_CORE::ONLINE]
Bars: 12 cyan (#00FFCC)
Speed: Slow pulse (~0.03 rad/frame)
Animation: Gentle wave at 60 FPS
Mic Button: Red #FF0000
Send Button: Gray #888888
```

Expected Result:
- [ ] Cyan bars pulsing gently
- [ ] No user input yet
- [ ] System ready for voice or text

### State 2: RECORDING (Mic Click)
```
Status: [RECORDING_VOICE]
Bars: 16 green (#00FF00)
Speed: Medium pulse (~0.08 rad/frame)
Mic Button: Bright red glowing
Animation: Responsive to audio input
```

Expected Result:
- [ ] Bars instantly turn green
- [ ] Mic LED glows bright red
- [ ] System listening to audio
- [ ] Bars respond to sound levels

### State 3: PROCESSING (Send Text)
```
Status: [PROCESSING_INPUT]
Bars: 16 green (#00FF00)
Speed: Medium-fast animation
Send Button: Glows green #00FF00
Animation: Active processing
```

Expected Result:
- [ ] Green bars pulsing faster
- [ ] Send button glows bright green
- [ ] Status shows processing
- [ ] LLM generating response

### State 4: SPEAKING (Output)
```
Status: [SPEAKING_OUTPUT]
Bars: 20 yellow (#FFFF00)
Speed: Fast pulse (~0.2 rad/frame)
Animation: High-energy mode
Color: Pure bright yellow
```

Expected Result:
- [ ] Bars turn yellow instantly
- [ ] Fast aggressive pulsing
- [ ] Status updated
- [ ] Audio playing or response showing
- [ ] 20 bars maximum (high energy)

### State 5: READY (Complete)
```
Status: [READY]
Bars: 12 cyan (#00FFCC)
Speed: Slow pulse
Animation: Back to idle
```

Expected Result:
- [ ] Bars return to cyan
- [ ] 12 bars from 20
- [ ] Gentle pulsing resumes
- [ ] System ready for next input

---

## 🎨 Color Reference Card

Print out and compare:
```
PURE BLACK      #000000 ███████ (Background)
NEON CYAN       #00FFCC ███████ (Idle, Borders)
NEON GREEN      #00FF00 ███████ (Thinking)
NEON YELLOW     #FFFF00 ███████ (Speaking)
RED LED         #FF0000 ███████ (Mic Recording)
TEXT GRAY       #888888 ███████ (Buttons)
DARK GRAY       #0a0a0a ███████ (Frames)
```

Verify each color matches exactly on your monitor.

---

## 🔧 Quick Test Script

```python
# Copy into Python console to test individual components:

# Test 1: Color constants
print(BotGUI.BAR_COLOR_IDLE)      # Should print: #00FFCC
print(BotGUI.BAR_COLOR_THINKING)  # Should print: #00FF00
print(BotGUI.BAR_COLOR_SPEAKING)  # Should print: #FFFF00

# Test 2: Status messages
gui.status_var.set("[RECORDING_VOICE]")
print(gui.status_var.get())  # Should show bracket format

# Test 3: Canvas state
print(f"Wave phase: {gui.wave_phase}")
print(f"Is thinking: {gui.is_thinking}")
print(f"Is speaking: {gui.is_speaking}")

# Test 4: Force state changes
gui.is_thinking = True   # Should show green bars
gui.is_speaking = True   # Should show yellow bars
gui.is_thinking = False
gui.is_speaking = False  # Should reset to cyan
```

---

## ✨ Success Criteria

**System is COMPLETE and working correctly when:**

✅ Pure black background visible on startup  
✅ Cyan neon borders clearly visible  
✅ Monospace font (Courier New) used throughout  
✅ Status shows in bracket notation: `[KNO_CORE::ONLINE]`  
✅ Mic button shows red LED glow when recording  
✅ Audio bars transition: cyan → green → yellow  
✅ Send button glows green momentarily on click  
✅ Response text shows terminal format: `USER>` and `KNO >`  
✅ Pixelated bars have LED glow effect (not smooth waves)  
✅ Animation runs smooth at 60 FPS  
✅ All colors match retro-futuristic palette  
✅ 12 bars idle → 16 thinking → 20 speaking  

---

## 🆘 Debugging Tips

If something doesn't look right:

1. **Colors too dim?**
   - Increase monitor brightness
   - Check GPU driver (Intel/NVIDIA/AMD)
   - Verify no color filter active (Windows Accessibility)

2. **Bars not animating?**
   - Check animation_loop() is called via `after(16, ...)`
   - Verify `wave_phase` is incrementing
   - Check canvas.delete("all") happens

3. **Font looks wrong?**
   - Verify Courier New installed on system
   - Check font size in line: `font=("Courier New", 14, "bold")`
   - Try fallback: `font=("Courier", 14, "bold")`

4. **Glow effects missing?**
   - Check `stipple="gray50"` is in glow rectangle
   - Verify glow_color is not None
   - Check canvas configured correctly

5. **Status not updating?**
   - Verify status_var.set() is called
   - Check status_label is bound to status_var
   - Verify label render timing

---

**Last Updated:** Phase 5 - Cloud Native Refactor  
**Status:** Ready for Testing  
**Contact:** KNO Development Team
