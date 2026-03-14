# Microphone Initialization and Audio Recording Fixes

## Summary of Improvements

Your AI agent had several critical audio issues that would cause crashes. All have been fixed with robust fallback strategies and comprehensive error handling.

---

## Issues Fixed

### 1. **Microphone Device Matching Error** ✅
**Problem:**
- Hardcoded `INPUT_DEVICE_NAME = 1` would fail if device index 1 didn't exist
- Error: `Wake Word Stream Error: No input device matching '...'`
- No fallback - agent would crash

**Solution:**
- Created `get_audio_device()` function that:
  - Tries preferred device (index 1) first
  - Falls back to system default device if preferred not available
  - Returns `None` for default device (most compatible)
  - Logs device selection for debugging

```python
# Before: Hardcoded
INPUT_DEVICE_NAME = 1

# After: Dynamic with fallback
INPUT_DEVICE_NAME = None
device = get_audio_device()  # Automatically handles fallback
```

---

### 2. **Immediate Crash After 'LISTENING' State** ✅
**Problem:**
- `print("[STATE] LISTENING: I'm listening!")` would execute
- Then immediately `--- SHUTDOWN SEQUENCE ---` without explanation
- No error messages to debug

**Solution:**
- Added comprehensive error handling in `record_voice_ppt()`:
  - Try-except blocks around audio stream creation
  - Status message checking during callbacks
  - Buffer validation before processing
  - Explicit error logging with `traceback.print_exc()`
  - Gracefully returns `None` instead of crashing

```python
# Added detailed logging
print(f"[AUDIO] PTT recording complete, {len(buffer)} chunks recorded", flush=True)
print(f"[AUDIO] PTT recording error: {e}", flush=True)
traceback.print_exc()  # Full error details
```

---

### 3. **Empty Buffer and Missing Audio Handling** ✅
**Problem:**
- `save_audio_buffer()` would crash if:
  - Buffer was empty
  - Sound files didn't exist in `ack_sounds_dir`
  - Directory for audio file didn't exist

**Solution:**
- Added buffer validation with logging
- Gracefully skip ack sound if not available
- Auto-create directories if needed
- Comprehensive try-except with detailed error messages

```python
def save_audio_buffer(self, buffer, filename, samplerate=16000):
    if not buffer:
        print("[AUDIO] Warning: Empty buffer, cannot save", flush=True)
        return None
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
        
        # ... save audio ...
        
        # Gracefully handle missing ack sound
        ack_sound = self.get_random_sound(ack_sounds_dir)
        if ack_sound:
            try:
                self.play_sound(ack_sound)
            except Exception as e:
                print(f"[AUDIO] Warning: Could not play ack sound: {e}", flush=True)
                # Don't crash - continue anyway
    except Exception as e:
        print(f"[AUDIO] Error saving audio buffer: {e}", flush=True)
        return None
```

---

### 4. **Path Compatibility (Windows vs Linux)** ✅
**Status:**
- ✅ All sound directories use `os.path.join()`
- ✅ All face directories use `os.path.join()`
- ✅ Whisper executable uses `os.path.join()` with Windows `.exe` detection
- ✅ Audio file paths properly constructed

**Example:**
```python
# Correct - Windows compatible
greeting_sounds_dir = os.path.join("sounds", "greeting_sounds")
models_dir = os.path.join("whisper.cpp", "models")

if sys.platform == "win32":
    whisper_exe = os.path.join(whisper_dir, "whisper-cli.exe")
else:
    whisper_exe = os.path.join(whisper_dir, "whisper-cli")
```

---

### 5. **Sound Directory Error Handling** ✅
**Problem:**
- `get_random_sound()` would fail silently
- No feedback if sound directory missing
- No logging for debugging

**Solution:**
- Added explicit error messages for:
  - Missing directories
  - Empty directories (no .wav files)
  - Access errors

```python
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
        print(f"[AUDIO] Error accessing sound directory: {e}", flush=True)
    return None
```

---

### 6. **Audio Stream Error Handling** ✅
**Problem:**
- Recording status flags ignored
- Device errors not logged
- No way to know if recording actually succeeded

**Solution:**
- Check `status` parameter in callbacks
- Log device selection and recording stats
- Validate recorded chunks count

```python
def callback(indata, frames, time_info, status):
    if status:
        print(f"[AUDIO] Recording status: {status}", flush=True)  # NOW LOGGED
    buffer.append(indata.copy())

# After recording
print(f"[AUDIO] PTT recording complete, {len(buffer)} chunks recorded", flush=True)
```

---

## New Logging Output

You'll now see detailed audio diagnostics:

```
[AUDIO] Using device 1: USB Audio Device
[AUDIO] Starting PTT recording...
[AUDIO] Using device 1 for recording
[AUDIO] PTT recording complete, 1024 chunks recorded
[AUDIO] Saving 1024 chunks to input.wav
[AUDIO] Audio saved: input.wav
[AUDIO] Playing sound: sounds/ack_sounds/beep.wav
[AUDIO] Sound playback complete
```

---

## Testing the Fixes

### Test 1: Basic Recording
```bash
1. Run: python agent.py
2. Click Tkinter window
3. Press ENTER to record
4. Speak: "Test message"
5. Press ENTER to stop
6. Check console for [AUDIO] messages showing device, recording stats, save, playback
```

Expected output:
```
[AUDIO] Using device 1: USB Microphone
[AUDIO] Starting PTT recording...
[AUDIO] PTT recording complete, 512 chunks recorded
[AUDIO] Audio saved: input.wav
(No crash - proceeds to transcription)
```

### Test 2: Device Fallback
If your device 1 doesn't exist:
```
[AUDIO] Warning checking device 1: ...
[AUDIO] Falling back to default device: ...
(Agent continues working with default device)
```

### Test 3: Missing Sound Files
If `sounds/ack_sounds/` is missing:
```
[AUDIO] No .wav files found in sounds/ack_sounds
[AUDIO] Audio saved: input.wav
(Skips ack sound gracefully, continues)
```

---

## Stability Improvements

### Before:
- Any audio error → Agent crashes with "--- SHUTDOWN SEQUENCE ---"
- No information about what failed
- User doesn't know if recording worked

### After:
- Audio errors → Logged and caught
- Agent reverts to IDLE state gracefully
- User gets clear feedback in console and GUI
- Recording stats shown (chunks, file size, device)

---

## Configuration

No configuration changes needed! The agent now:
1. Auto-detects best microphone
2. Falls back gracefully if device unavailable
3. Handles missing sound files
4. Works on both Windows and Linux

---

## Files Modified

- `agent.py`: 
  - Added `get_audio_device()` function
  - Updated `record_voice_ppt()` with device selection and error handling
  - Updated `record_voice_adaptive()` with device selection
  - Improved `save_audio_buffer()` with validation and graceful error handling
  - Enhanced `get_random_sound()` with error logging
  - Enhanced `play_sound()` with error logging
  - All `device=INPUT_DEVICE_NAME` replaced with `device=device` or `device=get_audio_device()`

---

## Backwards Compatibility

✅ All changes are backwards compatible
- Existing configuration still works
- No new configuration needed
- Agent auto-configures microphone

## Next Steps

**Test the agent:**
```bash
cd a:\KNO\KNO
python agent.py
```

If you still experience issues, check the console output for `[AUDIO]` messages - they'll tell you exactly what's happening at each step.
