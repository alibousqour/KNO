# Comprehensive fixes for agent.py
# This script shows the complete updated functions

UPDATED_TRANSCRIBE_AUDIO = '''    def transcribe_audio(self, filename):
        """Transcribe audio file using Whisper.cpp with robust Windows path handling.
        
        WHY THIS MATTERS:
        1. Absolute paths prevent 'WinError 2: system cannot find the file' crashes
        2. Pre-flight checks tell user exactly what's missing
        3. Explicit file checks prevent subprocess from hanging
        4. Exception handling prevents KeyboardInterrupt from crashing main loop
        5. Longer timeout prevents Whisper from timing out on first run
        """
        print("[TRANSCRIBE] Starting transcription...", flush=True)
        try:
            # Windows: Use absolute paths with raw strings (r"...") to prevent backslash escaping
            if sys.platform == "win32":
                # These are the EXACT paths where files must be placed
                whisper_exe = r"A:\\KNO\\KNO\\whisper.cpp\\build\\bin\\whisper-cli.exe"
                model_path = r"A:\\KNO\\KNO\\models\\ggml-base.en.bin"
            else:
                # Linux: Use relative paths from current directory
                whisper_exe = os.path.join("whisper.cpp", "build", "bin", "whisper-cli")
                model_path = os.path.join("models", "ggml-base.en.bin")
            
            # PRE-FLIGHT CHECKS: Verify all required files exist before attempting transcription
            # This prevents cryptic subprocess errors and tells user exactly what is missing
            if not os.path.exists(whisper_exe):
                error_msg = f"""[TRANSCRIBE ERROR] whisper-cli.exe not found!
    Expected location: {whisper_exe}
    
    Fix: Download whisper.cpp and place whisper-cli.exe at:
    A:\\\\KNO\\\\KNO\\\\whisper.cpp\\\\build\\\\bin\\\\whisper-cli.exe"""
                print(error_msg, flush=True)
                return ""
            
            if not os.path.exists(model_path):
                error_msg = f"""[TRANSCRIBE ERROR] Model file not found!
    Expected location: {model_path}
    
    Fix: Download ggml-base.en.bin and place it at:
    A:\\\\KNO\\\\KNO\\\\models\\\\ggml-base.en.bin"""
                print(error_msg, flush=True)
                return ""
            
            if not os.path.exists(filename):
                error_msg = f"[TRANSCRIBE ERROR] Audio file not found: {filename}"
                print(error_msg, flush=True)
                return ""
            
            # Verify audio file is readable (sometimes open handles prevent reading on Windows)
            try:
                with wave.open(filename, 'rb') as test_wav:
                    frames = test_wav.getnframes()
                    if frames == 0:
                        print("[TRANSCRIBE ERROR] Audio file is empty (0 frames)", flush=True)
                        return ""
            except Exception as e:
                print(f"[TRANSCRIBE ERROR] Cannot read audio file: {e}", flush=True)
                return ""
            
            print(f"[TRANSCRIBE] Using executable: {whisper_exe}", flush=True)
            print(f"[TRANSCRIBE] Using model: {model_path}", flush=True)
            print(f"[TRANSCRIBE] Processing audio: {filename}", flush=True)
            
            # Run transcription with proper argument passing (list format handles spaces in paths)
            # Arguments:
            #   -m: model file path
            #   -l: language (en = English)
            #   -t: number of threads (4 = good balance)
            #   -f: input audio file
            result = subprocess.run(
                [whisper_exe, "-m", model_path, "-l", "en", "-t", "4", "-f", filename],
                capture_output=True,
                text=True,
                timeout=120  # Whisper can be slow on first run, allow 2 minutes
            )
            
            # Check if subprocess failed
            if result.returncode != 0:
                error_output = result.stderr if result.stderr else result.stdout
                print(f"[TRANSCRIBE ERROR] Whisper failed with return code {result.returncode}", flush=True)
                print(f"[TRANSCRIBE ERROR] Output: {error_output}", flush=True)
                return ""
            
            # Parse Whisper output (last line contains the transcribed text)
            transcription_lines = result.stdout.strip().split('\\n')
            transcription = ""
            
            if transcription_lines and transcription_lines[-1].strip():
                last_line = transcription_lines[-1].strip()
                # Whisper output format: "[timestamp] text here" or just "text here"
                if ']' in last_line:
                    transcription = last_line.split("]", 1)[1].strip()
                else:
                    transcription = last_line
            
            if not transcription:
                print("[TRANSCRIBE] No speech detected in audio", flush=True)
                return ""
            
            print(f"[TRANSCRIBE] Success! Heard: '{transcription}'", flush=True)
            return transcription.strip()
            
        except subprocess.TimeoutExpired:
            print(f"[TRANSCRIBE ERROR] Transcription timed out (took >120 seconds)", flush=True)
            print(f"[TRANSCRIBE] Tip: Check if whisper-cli.exe and models are on slow network drives", flush=True)
            return ""
        except KeyboardInterrupt:
            # Gracefully handle Ctrl+C without crashing
            print("[TRANSCRIBE] Transcription cancelled by user", flush=True)
            return ""
        except Exception as e:
            print(f"[TRANSCRIBE ERROR] Unexpected error: {e}", flush=True)
            traceback.print_exc()
            return ""
'''

UPDATED_SAFE_MAIN = '''    def safe_main_execution(self):
        """Main agent loop with comprehensive error handling.
        
        WHY THIS MATTERS:
        - Wraps entire main loop to catch and handle KeyboardInterrupt gracefully
        - Individual try-except blocks in whisper pipeline prevent cascade failures
        - Slow Ollama responses don't freeze the UI
        - Agent can recover from network errors and continue running
        """
        try:
            print("[MAIN] Starting warm-up...", flush=True)
            self.warm_up_logic()
            print("[MAIN] Warm-up complete, starting TTS worker...", flush=True)
            self.tts_active.set()
            self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
            self.tts_thread.start()
            
            print("[MAIN] Entering main loop...", flush=True)
            print("\\n" + "="*60, flush=True)
            print("[READY] AGENT READY! Instructions:", flush=True)
            print("   1. Click on the Tkinter window to give it focus", flush=True)
            print("   2. Press ENTER to start recording your voice command", flush=True)
            print("   3. Press ENTER again to stop recording", flush=True)
            print("   4. I'll process and respond to your command", flush=True)
            print("   5. Press Ctrl+C in terminal to quit gracefully", flush=True)
            print("="*60 + "\\n", flush=True)
            
            while True:
                try:
                    print("[MAIN] Waiting for wake word or PTT...", flush=True)
                    trigger_source = self.detect_wake_word_or_ppt()
                    print(f"[MAIN] Triggered by: {trigger_source}", flush=True)
                    if self.interrupted.is_set():
                        self.interrupted.clear()
                        self.set_state(BotStates.IDLE, "Resetting...")
                        continue

                    self.set_state(BotStates.LISTENING, "I'm listening!")
                    
                    # AUDIO RECORDING: Record until user stops (PTT) or silence detected (Adaptive)
                    audio_file = None
                    try:
                        if trigger_source == "PTT":
                            audio_file = self.record_voice_ppt()
                        else:
                            audio_file = self.record_voice_adaptive()
                    except Exception as e:
                        print(f"[AUDIO ERROR] Recording failed: {e}", flush=True)
                        self.set_state(BotStates.IDLE, "Recording failed.")
                        continue
                    
                    if not audio_file: 
                        print("[AUDIO] No audio recorded. Try again.", flush=True)
                        self.set_state(BotStates.IDLE, "Heard nothing.")
                        continue
                    
                    # TRANSCRIPTION: Convert audio to text using Whisper
                    print("[MAIN] Starting transcription...", flush=True)
                    user_text = ""
                    try:
                        user_text = self.transcribe_audio(audio_file)
                    except KeyboardInterrupt:
                        print("[MAIN] Transcription cancelled", flush=True)
                        self.set_state(BotStates.IDLE, "Cancelled.")
                        continue
                    except Exception as e:
                        print(f"[TRANSCRIBE ERROR] {e}", flush=True)
                        self.set_state(BotStates.IDLE, "Transcription error.")
                        continue
                    
                    if not user_text:
                        print("[MAIN] No text transcribed. Try again.", flush=True)
                        self.set_state(BotStates.IDLE, "Transcription empty.")
                        continue
                    
                    # PROCESSING: Send to Ollama and get response
                    print(f"[MAIN] You said: {user_text}", flush=True)
                    self.append_to_text(f"YOU: {user_text}")
                    self.interrupted.clear()
                    
                    try:
                        self.chat_and_respond(user_text, img_path=None)
                    except KeyboardInterrupt:
                        print("[MAIN] Chat interrupted by user", flush=True)
                        self.set_state(BotStates.IDLE, "Interrupted.")
                        continue
                    except Exception as e:
                        print(f"[MAIN ERROR] Chat processing failed: {e}", flush=True)
                        self.set_state(BotStates.IDLE, "Processing error.")
                        continue
                        
                except KeyboardInterrupt:
                    # Inner loop interrupted - reset and continue
                    print("[MAIN] Operation cancelled by user", flush=True)
                    self.interrupted.set()
                    self.set_state(BotStates.IDLE, "Ready.")
                    continue
                except Exception as e:
                    print(f"[MAIN ERROR] Loop iteration failed: {e}", flush=True)
                    traceback.print_exc()
                    self.set_state(BotStates.ERROR, f"Error: {str(e)[:30]}")
                    # Don't exit - let the loop continue
                    time.sleep(1)
                    self.set_state(BotStates.IDLE, "Ready")
                    continue
                    
        except KeyboardInterrupt:
            print("\\n[MAIN] Agent shutdown requested by user", flush=True)
            self.safe_exit()
        except Exception as e:
            print(f"[FATAL] Fatal error in main execution: {e}", flush=True)
            traceback.print_exc()
            self.set_state(BotStates.ERROR, f"Fatal: {str(e)[:30]}")
'''

print("[OK] Updated function definitions created")
print("\nTo apply these changes, copy the functions above into agent.py:")
print(f"1. Replace transcribe_audio function (starting around line 759)")
print(f"2. Replace safe_main_execution function (starting around line 509)")
print(f"3. Compile and test!")
