# Comprehensive Fixes Applied to agent.py

## Summary of Changes

This document details all the fixes applied to make your voice assistant robust for Windows, with proper Whisper.cpp integration, Ollama error handling, and graceful shutdown behavior.

---

## 1. AUDIO PROCESSING FIX: save_audio_buffer()

### Problem
- File handles were not properly closed before Whisper tried to read the audio
- Windows sometimes keeps files locked, causing "file in use" errors

### Solution (Lines 725-745)
```python
# Use explicit file handle management instead of context manager
wf = wave.open(filename, "wb")
try:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(samplerate)
    wf.writeframes(audio_data.tobytes())
    wf.flush()  # Force write to disk immediately
finally:
    wf.close()  # Ensure file is closed before returning

# Small delay to ensure file system finishes writing
time.sleep(0.1)
```

### Why This Matters
- Explicit `close()` ensures file is released before Whisper reads it
- `flush()` forces data to disk immediately
- Small delay allows Windows file system to finalize write
- Prevents "file locked" or "permission denied" errors

---

## 2. OLLAMA INTEGRATION FIX: warm_up_logic()

### Problem
- Slow Ollama connections could hang indefinitely
- No error messages if Ollama server wasn't running
- Connection failures would crash the agent

### Solution (Lines 597-610)
```python
def warm_up_logic(self):
    self.set_state(BotStates.WARMUP, "Warming up brains...")
    try:
        print(f"[OLLAMA] Loading model: {TEXT_MODEL}", flush=True)
        ollama.generate(model=TEXT_MODEL, prompt="", keep_alive=-1)
        print(f"[OLLAMA] Model loaded successfully: {TEXT_MODEL}", flush=True)
    except ConnectionError as e:
        print(f"[OLLAMA ERROR] Cannot connect to Ollama server: {e}", flush=True)
        print(f"[OLLAMA ERROR] Make sure Ollama is running! Start with: ollama serve", flush=True)
    except Exception as e:
        print(f"[OLLAMA ERROR] Failed to load {TEXT_MODEL}: {e}", flush=True)
        print(f"[OLLAMA ERROR] Continuing anyway - will try to use model when needed", flush=True)
```

### Why This Matters
- Catches `ConnectionError` specifically for Ollama connection issues
- Graceful failure - agent continues even if model load fails
- User gets clear instructions on how to fix the problem
- Distinguishes network errors from other exceptions

---

## 3. WHISPER PATHFINDING FIX: transcribe_audio()

### Problem
- Relative paths couldn't find whisper-cli.exe on Windows
- "WinError 2: The system cannot find the file specified" errors
- No pre-flight checks to verify files exist

### Solution (Lines 759-840)
```python
def transcribe_audio(self, filename):
    print("[TRANSCRIBE] Starting transcription...", flush=True)
    try:
        # Windows: Use ABSOLUTE paths with raw strings
        if sys.platform == "win32":
            whisper_exe = r"A:\KNO\KNO\whisper.cpp\build\bin\whisper-cli.exe"
            model_path = r"A:\KNO\KNO\models\ggml-base.en.bin"
        else:
            whisper_exe = os.path.join("whisper.cpp", "build", "bin", "whisper-cli")
            model_path = os.path.join("models", "ggml-base.en.bin")
        
        # PRE-FLIGHT CHECKS
        if not os.path.exists(whisper_exe):
            error_msg = f"""[TRANSCRIBE ERROR] whisper-cli.exe not found!
    Expected: {whisper_exe}
    Fix: Place it at: A:\\KNO\\KNO\\whisper.cpp\\build\\bin\\whisper-cli.exe"""
            print(error_msg, flush=True)
            return ""
        
        # ... more checks ...
        
        # 120-second timeout instead of 60 (Whisper is slow!)
        result = subprocess.run(
            [whisper_exe, "-m", model_path, "-l", "en", "-t", "4", "-f", filename],
            capture_output=True, text=True, timeout=120
        )
```

### Why This Matters
- `r"..."` raw strings prevent `\` from being treated as escape characters
- Absolute paths work regardless of current working directory
- Pre-flight checks prevent cryptic subprocess errors
- 120-second timeout prevents premature timeout on first run
- Returns empty string instead of crashing on errors

---

## 4. ERROR HANDLING FIX: chat_and_respond()

### Problem
- Ollama connection errors crashed the agent
- No way to handle `KeyboardInterrupt` during chat
- Slow responses froze the UI

### Solution (Lines 870-881)
```python
try:
    print(f"[OLLAMA] Sending query to {model_to_use}...", flush=True)
    stream = ollama.chat(...)
    
    for chunk in stream:
        if self.interrupted.is_set():
            print("[OLLAMA] Response interrupted by user", flush=True)
            break
        
        # Extract content safely
        try:
            content = chunk.get('message', {}).get('content', '')
        except:
            content = ""
        full_response_buffer += content

except ConnectionError as e:
    print(f"[OLLAMA ERROR] Connection failed: {e}", flush=True)
    fallback_msg = "I am having trouble thinking..."
    # Send fallback response instead of crashing
    self.append_to_text(f"BOT: {fallback_msg}")
    with self.tts_queue_lock:
        self.tts_queue.append(fallback_msg)
    self.wait_for_tts()
    self.set_state(BotStates.IDLE, "Connection Error")

except KeyboardInterrupt:
    print("[MAIN] Interrupted by user", flush=True)
    self.set_state(BotStates.IDLE, "Interrupted")
```

### Why This Matters
- `ConnectionError` catches Ollama network failures
- `KeyboardInterrupt` allows graceful cancellation with Ctrl+C
- Fallback response sent to user instead of crash
- `chunk.get()` safely extracts data without crashing on format changes

---

## 5. MAIN LOOP ERROR HANDLING: safe_main_execution()

### Problem
- Any error in the main loop would crash the entire agent
- KeyboardInterrupt at wrong time could cause unclean shutdown
- No recovery mechanism for individual operation failures

### Solution (Lines 509-620)
```python
def safe_main_execution(self):
    try:
        # ... initialization ...
        
        while True:
            try:  # Inner loop try-except for per-iteration error handling
                # Recording stage with error handling
                try:
                    if trigger_source == "PTT":
                        audio_file = self.record_voice_ptt()
                    else:
                        audio_file = self.record_voice_adaptive()
                except Exception as e:
                    print(f"[AUDIO ERROR] Recording failed: {e}", flush=True)
                    self.set_state(BotStates.IDLE, "Recording failed.")
                    continue  # Skip to next iteration
                
                # Transcription stage with error handling
                try:
                    user_text = self.transcribe_audio(audio_file)
                except KeyboardInterrupt:
                    print("[MAIN] Transcription cancelled", flush=True)
                    self.set_state(BotStates.IDLE, "Cancelled.")
                    continue
                except Exception as e:
                    print(f"[TRANSCRIBE ERROR] {e}", flush=True)
                    continue
                
                # Chat stage with error handling
                try:
                    self.chat_and_respond(user_text, img_path=None)
                except KeyboardInterrupt:
                    print("[MAIN] Chat interrupted by user", flush=True)
                    continue
                except Exception as e:
                    print(f"[MAIN ERROR] Chat failed: {e}", flush=True)
                    continue
                    
            except KeyboardInterrupt:
                # Inner loop interrupted
                print("[MAIN] Operation cancelled by user", flush=True)
                self.set_state(BotStates.IDLE, "Ready.")
                continue
            except Exception as e:
                # General error recovery
                print(f"[MAIN ERROR] Loop iteration failed: {e}", flush=True)
                self.set_state(BotStates.ERROR, f"Error: {str(e)[:30]}")
                time.sleep(1)  # Wait before retrying
                self.set_state(BotStates.IDLE, "Ready")
                continue
                    
    except KeyboardInterrupt:
        # Top-level interrupt - clean shutdown
        print("\\n[MAIN] Agent shutdown requested by user", flush=True)
        self.safe_exit()
```

### Why This Matters
- Nested try-except blocks catch errors at each stage
- Errors don't cascade - agent recovers and waits for next input
- KeyboardInterrupt handled at multiple levels
- `continue` allows loop to retry instead of exiting
- Top-level exception handler prevents zombie processes

---

## 6. ENTRY POINT FIX: __main__

### Problem
- KeyboardInterrupt at startup could leave processes running
- No cleanup if initialization fails

### Solution (Lines 1141-1162)
```python
if __name__ == "__main__":
    print("--- SYSTEM STARTING ---", flush=True)
    app = None
    try:
        print("[INIT] Creating GUI...", flush=True)
        root = tk.Tk()
        app = BotGUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("\\n[MAIN] Keyboard interrupt - shutting down gracefully", flush=True)
        if app:
            app.safe_exit()
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Failed to start agent: {e}", flush=True)
        traceback.print_exc()
        if app:
            try:
                app.safe_exit()
            except:
                pass
        sys.exit(1)
```

### Why This Matters
- Tracks `app` variable to ensure cleanup happens
- Catches `KeyboardInterrupt` separately for graceful shutdown
- Calls `safe_exit()` to properly clean up Ollama, audio, and threads
- Prevents zombie Python processes lingering after crash

---

## Testing Checklist

After applying these fixes, test the following:

✅ **Recording Works**
```
Press ENTER - should print "[AUDIO] Starting PTT recording..."
Speak into mic
Press ENTER - should print "[AUDIO] PTT recording complete, XXX chunks recorded"
"input.wav" file should exist and be playable
```

✅ **Transcription Works**
```
Agent should print "[TRANSCRIBE] Using executable: A:\KNO\KNO\whisper.cpp\build\bin\whisper-cli.exe"
"[TRANSCRIBE] Using model: A:\KNO\KNO\models\ggml-base.en.bin"
Should see "[TRANSCRIBE] Heard: 'your text here'"
```

✅ **Ollama Works**
```
Agent should print "[OLLAMA] Sending query to ..."
Agent should print "[STATE] THINKING: Thinking..."
Agent should respond with text in about 5-10 seconds
```

✅ **Error Recovery Works**
```
Press Ctrl+C during recording - should print "[MAIN] Interrupted by user"
Pressing ENTER again should work normally
Try Ctrl+C during transcription - should recover gracefully
Try Ctrl+C during Ollama response - should allow retry
```

✅ **Missing Files Handled**
```
If ggml-base.en.bin is missing, should print clear error with path
If whisper-cli.exe is missing, should print exact error message
Agent should not crash, but should continue running
```

---

## Key Improvements Summary

| Issue | Before | After |
|-------|--------|-------|
| Whisper path errors | WinError 2 - file not found | Clear error message with fix suggestion |
| Ollama connection fails | Crash | Graceful fallback response |
| Slow transcription | Timeout at 60s | 120s timeout, no premature exit |
| Audio file locked | Whisper can't read file | Explicit close() + flush() + delay |
| Ctrl+C during chat | Crash/hangs | Clean recovery, ready for next input |
| FileNotFoundError | No recovery | Pre-flight checks prevent it |

---

## Deployment Instructions

1. **Replace transcribe_audio()** function (around line 759)
2. **Replace safe_main_execution()** function (around line 509)
3. **Replace warm_up_logic()** function (already done in first batch)
4. **Error handling in chat_and_respond()** (already done)
5. Test with: `python agent.py`

---

## Questions or Issues?

If you encounter any errors:

1. Check terminal output for `[TRANSCRIBE ERROR]`, `[OLLAMA ERROR]`, `[AUDIO ERROR]` tags
2. Read the error message - it should tell you exactly what's wrong
3. Verify file paths:
   - `A:\KNO\KNO\whisper.cpp\build\bin\whisper-cli.exe`
   - `A:\KNO\KNO\models\ggml-base.en.bin`
   - `A:\KNO\KNO\sounds\` directories

