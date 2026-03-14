# =========================================================================
# Audio Manager - Safe Audio Recording with Timeout & File Handling
# =========================================================================
"""
Audio recording with proper timeout enforcement and file cleanup.

SECURITY FEATURES:
1. Timeout enforcement via threading.Timer
2. Explicit file close() with verification
3. File size validation before processing
4. Exception-specific error handling
5. Resource cleanup in finally blocks
"""

import wave
import pyaudio
import threading
import logging
import os
import time
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger("KNO.audio_manager")


# =========================================================================
# AUDIO RECORDING WITH TIMEOUT
# =========================================================================

class AudioRecorder:
    """Records audio with timeout enforcement and safe file handling"""
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 channels: int = 1,
                 chunk_size: int = 1024,
                 device_index: Optional[int] = None):
        """
        Initialize audio recorder.
        
        Args:
            sample_rate: Sample rate in Hz (default 16000)
            channels: Number of channels (1=mono, 2=stereo)
            chunk_size: Frames per audio buffer
            device_index: Audio device index (None = default)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.device_index = device_index
        
        self._audio_interface = None
        self._stream = None
        self._timeout_timer = None
        self._recording_stop_event = threading.Event()
        self._is_recording = False
    
    def record_with_timeout(self, 
                           output_file: str,
                           timeout_seconds: int = 300) -> Tuple[bool, Optional[str]]:
        """
        Record audio with timeout enforcement.
        
        Args:
            output_file: Path to save WAV file
            timeout_seconds: Maximum recording time (default 5 minutes)
            
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        if not timeout_seconds or timeout_seconds < 5:
            return False, "❌ Timeout must be at least 5 seconds"
        
        logger.info(f"🎤 Recording audio (timeout: {timeout_seconds}s) → {output_file}")
        
        # Reset state
        self._recording_stop_event.clear()
        self._is_recording = False
        frames = []
        
        try:
            # Initialize PyAudio
            self._audio_interface = pyaudio.PyAudio()
            
            # Open audio stream
            try:
                self._stream = self._audio_interface.open(
                    format=pyaudio.paInt16,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    frames_per_buffer=self.chunk_size,
                    input_device_index=self.device_index
                )
            except OSError as e:
                logger.error(f"❌ Audio device error: {e}")
                return False, f"Audio device not available: {e}"
            except Exception as e:
                logger.error(f"❌ Stream initialization failed: {e}")
                return False, f"Stream error: {e}"
            
            logger.info("✅ Stream opened")
            self._is_recording = True
            
            # Set up timeout timer
            self._timeout_timer = threading.Timer(
                timeout_seconds,
                self._on_timeout,
                args=[timeout_seconds]
            )
            self._timeout_timer.daemon = True
            self._timeout_timer.start()
            
            logger.info(f"⏱️  Timeout timer set: {timeout_seconds}s")
            
            # Record audio
            try:
                while self._is_recording and not self._recording_stop_event.is_set():
                    try:
                        chunk = self._stream.read(
                            self.chunk_size,
                            exception_on_overflow=False
                        )
                        frames.append(chunk)
                    except IOError as e:
                        logger.error(f"❌ Read error: {e}")
                        break
                    except Exception as e:
                        logger.error(f"❌ Unexpected recording error: {e}")
                        break
            
            except KeyboardInterrupt:
                logger.info("⏹️  Recording interrupted by user")
                return False, "Recording interrupted"
            except Exception as e:
                logger.error(f"❌ Recording failed: {e}")
                return False, f"Recording error: {e}"
            
            finally:
                # Cancel timeout timer
                if self._timeout_timer:
                    self._timeout_timer.cancel()
                
                self._is_recording = False
            
            # Write audio to file
            if not frames:
                logger.warning("⚠️  No audio data recorded")
                return False, "No audio data captured"
            
            try:
                return self._write_wav_file(output_file, frames)
            except Exception as e:
                logger.error(f"❌ Failed to write audio file: {e}")
                return False, f"Write error: {e}"
        
        except ImportError:
            logger.error("❌ PyAudio not installed")
            return False, "PyAudio not installed"
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False, f"Unexpected error: {e}"
        
        finally:
            # Cleanup resources
            self._cleanup_stream()
    
    def _write_wav_file(self, filepath: str, frames: list) -> Tuple[bool, Optional[str]]:
        """
        Write audio frames to WAV file with proper cleanup.
        
        Args:
            filepath: Output file path
            frames: Audio frames to write
            
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        # Ensure output directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        wave_file = None
        try:
            # Open WAV file for writing
            wave_file = wave.open(filepath, "wb")
            
            # Set WAV properties
            wave_file.setnchannels(self.channels)
            wave_file.setsampwidth(2)  # 16-bit audio
            wave_file.setframerate(self.sample_rate)
            
            # Write frames
            for frame in frames:
                wave_file.writeframes(frame)
            
            # Explicitly close the file
            wave_file.close()
            wave_file = None  # Set to None so finally block doesn't try to close again
            
            # IMPORTANT: Add small delay to ensure file handle is released
            time.sleep(0.1)
            
            # Verify file was created and has content
            if not os.path.exists(filepath):
                return False, f"❌ File was not created: {filepath}"
            
            file_size = os.path.getsize(filepath)
            if file_size == 0:
                return False, f"❌ File is empty: {filepath}"
            
            logger.info(f"✅ Audio saved ({file_size} bytes): {filepath}")
            return True, None
        
        except OSError as e:
            logger.error(f"❌ File I/O error: {e}")
            return False, f"File error: {e}"
        except Exception as e:
            logger.error(f"❌ Write error: {e}")
            return False, f"Error writing WAV: {e}"
        
        finally:
            # Ensure file is closed
            if wave_file is not None:
                try:
                    wave_file.close()
                except Exception:
                    pass
    
    def _on_timeout(self, timeout_seconds: int):
        """Called when timeout expires"""
        logger.warning(f"⏱️  Recording timeout ({timeout_seconds}s) - stopping recording")
        self._is_recording = False
        self._recording_stop_event.set()
    
    def stop_recording(self):
        """Stop recording immediately (user request)"""
        logger.info("⏹️  Stopping recording")
        self._is_recording = False
        self._recording_stop_event.set()
        if self._timeout_timer:
            self._timeout_timer.cancel()
    
    def _cleanup_stream(self):
        """Clean up audio stream and interface"""
        try:
            if self._stream is not None:
                if self._stream.is_active():
                    self._stream.stop_stream()
                self._stream.close()
                self._stream = None
        except Exception as e:
            logger.warning(f"⚠️  Error closing stream: {e}")
        
        try:
            if self._audio_interface is not None:
                self._audio_interface.terminate()
                self._audio_interface = None
        except Exception as e:
            logger.warning(f"⚠️  Error closing audio interface: {e}")
    
    def __del__(self):
        """Ensure cleanup on object destruction"""
        self._cleanup_stream()


# =========================================================================
# AUDIO UTILITIES
# =========================================================================

def verify_audio_file(filepath: str) -> Tuple[bool, str]:
    """
    Verify audio file exists, is readable, and has content.
    
    Args:
        filepath: Path to audio file
        
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    # Check file exists
    if not os.path.exists(filepath):
        return False, f"❌ File not found: {filepath}"
    
    # Check file size
    try:
        file_size = os.path.getsize(filepath)
        if file_size == 0:
            return False, f"❌ File is empty: {filepath}"
    except OSError as e:
        return False, f"❌ Cannot read file: {e}"
    
    # Try to open as WAV file
    try:
        wave_file = wave.open(filepath, "rb")
        channels = wave_file.getnchannels()
        sample_width = wave_file.getsampwidth()
        sample_rate = wave_file.getframerate()
        n_frames = wave_file.getnframes()
        wave_file.close()
        
        logger.info(
            f"✅ Audio file valid: {channels}ch, {sample_rate}Hz, "
            f"{n_frames} frames ({file_size} bytes)"
        )
        return True, "Audio file is valid"
    
    except wave.Error as e:
        return False, f"❌ Invalid WAV file: {e}"
    except Exception as e:
        return False, f"❌ Error reading audio: {e}"


def get_audio_devices() -> list:
    """
    Get list of available audio devices.
    
    Returns:
        list: List of device info dicts
    """
    try:
        audio = pyaudio.PyAudio()
        devices = []
        
        for i in range(audio.get_device_count()):
            try:
                info = audio.get_device_info_by_index(i)
                if info.get("maxInputChannels", 0) > 0:
                    devices.append({
                        "index": i,
                        "name": info.get("name", "Unknown"),
                        "channels": info.get("maxInputChannels", 0),
                        "sample_rate": int(info.get("defaultSampleRate", 0))
                    })
            except Exception as e:
                logger.warning(f"⚠️  Error reading device {i}: {e}")
                continue
        
        audio.terminate()
        return devices
    
    except Exception as e:
        logger.error(f"❌ Error enumerating audio devices: {e}")
        return []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test audio recording
    recorder = AudioRecorder()
    
    print("📋 Available Audio Devices:")
    for device in get_audio_devices():
        print(f"  [{device['index']}] {device['name']} - {device['channels']}ch @ {device['sample_rate']}Hz")
    
    print("\n🎤 Recording 5-second sample...")
    success, error = recorder.record_with_timeout("test_audio.wav", timeout_seconds=5)
    
    if success:
        print("✅ Recording successful")
        is_valid, msg = verify_audio_file("test_audio.wav")
        print(f"{msg}")
    else:
        print(f"❌ Recording failed: {error}")
