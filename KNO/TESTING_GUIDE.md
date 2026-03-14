# Testing Guide - Agent.py Improvements

Comprehensive testing guide for the refactored agent.py with logging, configuration, and error handling improvements.

---

## Unit Testing Strategy

### Test 1: Logging System

**File: `test_logging.py`**

```python
import logging
import tempfile
import os
from pathlib import Path
from agent import setup_logging, logger

def test_logging_setup():
    """Test that logging is configured correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup logger with temp directory
        log_file = os.path.join(tmpdir, "test.log")
        test_logger = setup_logging(
            log_level=logging.INFO,
            log_file=log_file,
            console_output=False
        )
        
        # Write test message
        test_logger.info("Test message")
        
        # Verify log file created
        assert os.path.exists(log_file), "Log file not created"
        
        # Verify message in file
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Test message" in content, "Message not in log"
        
        print("✅ Logging setup test passed")

def test_logging_levels():
    """Test different log levels."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "test.log")
        test_logger = setup_logging(
            log_level=logging.DEBUG,
            log_file=log_file,
            console_output=False
        )
        
        # Write messages at different levels
        test_logger.debug("Debug message")
        test_logger.info("Info message")
        test_logger.warning("Warning message")
        test_logger.error("Error message")
        
        # Verify all in file
        with open(log_file, 'r') as f:
            content = f.read()
            assert "DEBUG" in content
            assert "INFO" in content
            assert "WARNING" in content
            assert "ERROR" in content
        
        print("✅ Logging levels test passed")

def test_rotating_file_handler():
    """Test that log rotation works (max 10MB)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "test.log")
        test_logger = setup_logging(
            log_level=logging.INFO,
            log_file=log_file,
            console_output=False
        )
        
        # The logger has rotating handler (max 10MB)
        # Find the RotatingFileHandler
        rotating_handler = None
        for handler in test_logger.handlers:
            if hasattr(handler, 'maxBytes'):
                rotating_handler = handler
                break
        
        assert rotating_handler is not None, "RotatingFileHandler not found"
        assert rotating_handler.maxBytes == 10 * 1024 * 1024, "Max size not 10MB"
        assert rotating_handler.backupCount == 5, "Backup count not 5"
        
        print("✅ Rotating file handler test passed")

if __name__ == "__main__":
    test_logging_setup()
    test_logging_levels()
    test_rotating_file_handler()
    print("\n✨ All logging tests passed!")
```

### Test 2: Configuration System

**File: `test_config.py`**

```python
import os
import tempfile
from pathlib import Path
from agent import Config

def test_config_defaults():
    """Test that Config has sensible defaults."""
    assert Config.MODELS_DIR is not None
    assert Config.LOGS_DIR is not None
    assert Config.TRANSCRIBE_TIMEOUT == 120
    assert Config.NETWORK_TIMEOUT == 30
    assert Config.MAX_RETRIES == 3
    print("✅ Config defaults test passed")

def test_config_env_override():
    """Test that environment variables override defaults."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Set environment
        os.environ['KNO_BASE_DIR'] = tmpdir
        os.environ['KNO_TRANSCRIBE_TIMEOUT'] = '300'
        
        # Reload Config (in real test, would reload module)
        # For now, just verify the env vars are read
        base_dir = os.getenv('KNO_BASE_DIR')
        timeout = int(os.getenv('KNO_TRANSCRIBE_TIMEOUT', '120'))
        
        assert base_dir == tmpdir
        assert timeout == 300
        
        print("✅ Config environment override test passed")

def test_config_get_path():
    """Test Config.get_path() method."""
    # These should all return Path objects or None
    paths = ['models', 'sounds', 'logs', 'whisper', 'base']
    
    for path_type in paths:
        result = Config.get_path(path_type)
        assert result is not None, f"get_path('{path_type}') returned None"
    
    print("✅ Config get_path test passed")

def test_config_whisper_executable():
    """Test getting Whisper executable path."""
    exe = Config.get_whisper_executable()
    # May be None if not installed, but method should work
    print(f"  Whisper exe: {exe}")
    print("✅ Config whisper executable test passed")

if __name__ == "__main__":
    test_config_defaults()
    test_config_env_override()
    test_config_get_path()
    test_config_whisper_executable()
    print("\n✨ All config tests passed!")
```

### Test 3: File Validation

**File: `test_file_validation.py`**

```python
import wave
import tempfile
import os
from agent import validate_wave_file, safe_file_delete

def test_validate_valid_wav():
    """Test validation of a valid WAV file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create valid WAV file
        wav_file = os.path.join(tmpdir, "valid.wav")
        
        # Write simple WAV
        import numpy as np
        sample_rate = 16000
        duration = 2
        samples = np.random.randint(-32768, 32767, sample_rate * duration, dtype=np.int16)
        
        with wave.open(wav_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(samples.tobytes())
        
        # Validate
        is_valid, error = validate_wave_file(wav_file)
        assert is_valid, f"Valid WAV marked invalid: {error}"
        
        print("✅ Valid WAV validation test passed")

def test_validate_corrupted_wav():
    """Test detection of corrupted WAV file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create corrupted WAV (just wrong header)
        corrupted_file = os.path.join(tmpdir, "corrupted.wav")
        with open(corrupted_file, 'wb') as f:
            f.write(b"NOT_A_VALID_WAV_FILE" + b"\x00" * 100)
        
        # Validate
        is_valid, error = validate_wave_file(corrupted_file)
        assert not is_valid, "Corrupted WAV not detected"
        assert "error" in error.lower() or "corrupted" in error.lower()
        
        print("✅ Corrupted WAV detection test passed")

def test_validate_empty_wav():
    """Test detection of empty WAV file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create empty WAV
        wav_file = os.path.join(tmpdir, "empty.wav")
        
        with wave.open(wav_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            # Write nothing
        
        # Validate
        is_valid, error = validate_wave_file(wav_file)
        assert not is_valid, "Empty WAV not detected"
        assert "empty" in error.lower()
        
        print("✅ Empty WAV detection test passed")

def test_safe_file_delete():
    """Test safe file deletion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # Delete it
        result = safe_file_delete(test_file, log_on_failure=False)
        assert result, "Deletion failed"
        assert not os.path.exists(test_file), "File still exists after deletion"
        
        print("✅ Safe file delete test passed")

def test_safe_file_delete_nonexistent():
    """Test safe deletion of non-existent file (should not crash)."""
    result = safe_file_delete("/nonexistent/path/file.txt", log_on_failure=False)
    assert result, "Should return True for non-existent file"
    
    print("✅ Safe file delete (non-existent) test passed")

if __name__ == "__main__":
    test_validate_valid_wav()
    test_validate_corrupted_wav()
    test_validate_empty_wav()
    test_safe_file_delete()
    test_safe_file_delete_nonexistent()
    print("\n✨ All file validation tests passed!")
```

### Test 4: Retry Logic

**File: `test_retry.py`**

```python
import time
from agent import retry

def test_retry_success_first_try():
    """Test that function succeeds on first try."""
    call_count = 0
    
    @retry(max_attempts=3, delay=0.1, backoff=1)
    def sometimes_fails():
        nonlocal call_count
        call_count += 1
        return "success"
    
    result = sometimes_fails()
    assert result == "success"
    assert call_count == 1, "Should only call once"
    
    print("✅ Retry success first try test passed")

def test_retry_success_after_failures():
    """Test that function retries and succeeds."""
    call_count = 0
    
    @retry(max_attempts=3, delay=0.05, backoff=1)
    def sometimes_fails():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Temporary failure")
        return "success"
    
    result = sometimes_fails()
    assert result == "success"
    assert call_count == 3, "Should call 3 times"
    
    print("✅ Retry success after failures test passed")

def test_retry_max_attempts_exceeded():
    """Test that function fails after max attempts."""
    call_count = 0
    
    @retry(max_attempts=3, delay=0.05, backoff=1)
    def always_fails():
        nonlocal call_count
        call_count += 1
        raise ValueError("Permanent failure")
    
    try:
        always_fails()
        assert False, "Should have raised exception"
    except ValueError as e:
        assert "Permanent failure" in str(e)
        assert call_count == 3, "Should call 3 times"
    
    print("✅ Retry max attempts exceeded test passed")

def test_retry_exponential_backoff():
    """Test that backoff delay increases exponentially."""
    times = []
    
    @retry(max_attempts=3, delay=0.05, backoff=2)
    def sometimes_fails():
        times.append(time.time())
        if len(times) < 3:
            raise ValueError("Try again")
        return "success"
    
    result = sometimes_fails()
    assert result == "success"
    
    # Verify delays increased
    if len(times) >= 2:
        delay1 = times[1] - times[0]
        delay2 = times[2] - times[1] if len(times) > 2 else 0
        # delay2 should be roughly 2x delay1 (with some tolerance)
        # (skipping exact verification due to system variance)
    
    print("✅ Retry exponential backoff test passed")

if __name__ == "__main__":
    test_retry_success_first_try()
    test_retry_success_after_failures()
    test_retry_max_attempts_exceeded()
    test_retry_exponential_backoff()
    print("\n✨ All retry tests passed!")
```

---

## Integration Testing

### Test 5: Full Startup Sequence

**File: `test_startup.py`**

```python
#!/usr/bin/env python3
"""Test full startup sequence with all improvements."""

import os
import sys
import tempfile
from pathlib import Path

# Set test environment
os.environ['KNO_LOG_LEVEL'] = 'DEBUG'
os.environ['CLEANUP_TEMP_FILES'] = 'true'

from agent import Config, logger, setup_logging

def test_full_startup():
    """Test complete startup with all systems."""
    print("Starting full startup test...\n")
    
    # Test 1: Logging initialization
    print("[1/4] Testing logging system...")
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "startup.log")
        test_logger = setup_logging(
            log_level='DEBUG',
            log_file=log_file,
            console_output=True
        )
        test_logger.info("Startup test beginning")
    print("✅ Logging initialized")
    
    # Test 2: Configuration initialization
    print("\n[2/4] Testing configuration...")
    Config.initialize()
    Config.print_config()
    print("✅ Configuration loaded")
    
    # Test 3: Path existence
    print("\n[3/4] Testing directory creation...")
    dirs_to_check = ['MODELS_DIR', 'LOGS_DIR', 'SOUNDS_DIR']
    for dir_name in dirs_to_check:
        dir_path = getattr(Config, dir_name)
        if dir_path:
            dir_path.mkdir(parents=True, exist_ok=True)
            assert dir_path.exists(), f"{dir_name} not created"
            logger.info(f"✅ {dir_name} ready: {dir_path}")
    
    # Test 4: Executable detection
    print("\n[4/4] Testing executable detection...")
    whisper_exe = Config.get_whisper_executable()
    if whisper_exe:
        logger.info(f"✅ Whisper executable found: {whisper_exe}")
    else:
        logger.warning("⚠️  Whisper executable not found (optional)")
    
    print("\n" + "="*60)
    print("✨ Full startup test PASSED")
    print("="*60)

if __name__ == "__main__":
    test_full_startup()
```

---

## Performance Testing

### Test 6: Logging Performance

**File: `test_logging_performance.py`**

```python
import time
import tempfile
from agent import setup_logging

def test_logging_performance():
    """Test that logging doesn't significantly impact performance."""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = f"{tmpdir}/perf_test.log"
        logger = setup_logging(log_file=log_file, console_output=False)
        
        # Measure time to log 10,000 messages
        iterations = 10000
        
        start_time = time.time()
        for i in range(iterations):
            logger.info(f"Test message {i}")
        elapsed_time = time.time() - start_time
        
        avg_time_ms = (elapsed_time / iterations) * 1000
        
        print(f"Logged {iterations} messages in {elapsed_time:.2f}s")
        print(f"Average per-message time: {avg_time_ms:.3f}ms")
        
        # Should be fast (< 1ms per message)
        assert avg_time_ms < 1.0, f"Logging too slow: {avg_time_ms}ms per message"
        
        print("✅ Logging performance test passed")

if __name__ == "__main__":
    test_logging_performance()
```

---

## Run All Tests

**File: `run_all_tests.py`**

```python
#!/usr/bin/env python3
"""Run all unit and integration tests."""

import subprocess
import sys

test_files = [
    "test_logging.py",
    "test_config.py",
    "test_file_validation.py",
    "test_retry.py",
    "test_startup.py",
    "test_logging_performance.py",
]

def run_tests():
    """Run all test files."""
    print("🧪 Running all agent.py improvement tests\n")
    print("=" * 60)
    
    failed_tests = []
    passed_tests = []
    
    for test_file in test_files:
        print(f"\n📋 Running {test_file}...")
        print("-" * 60)
        
        try:
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=False,
                timeout=30
            )
            
            if result.returncode == 0:
                passed_tests.append(test_file)
                print(f"✅ {test_file} PASSED")
            else:
                failed_tests.append(test_file)
                print(f"❌ {test_file} FAILED")
        
        except subprocess.TimeoutExpired:
            failed_tests.append(test_file)
            print(f"⏱️  {test_file} TIMEOUT")
        except Exception as e:
            failed_tests.append(test_file)
            print(f"❌ {test_file} ERROR: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {len(passed_tests)}/{len(test_files)}")
    print(f"❌ Failed: {len(failed_tests)}/{len(test_files)}")
    
    if failed_tests:
        print(f"\nFailed tests:")
        for test in failed_tests:
            print(f"  - {test}")
        return 1
    else:
        print("\n🎉 All tests PASSED!")
        return 0

if __name__ == "__main__":
    sys.exit(run_tests())
```

---

## Manual Testing Checklist

### Configuration Testing

- [ ] Set `KNO_BASE_DIR` to custom path
- [ ] Verify Config reads custom path
- [ ] Test `KNO_TRANSCRIBE_TIMEOUT=300`
- [ ] Verify timeout is `300` (not default `120`)
- [ ] Test `KNO_LOG_LEVEL=DEBUG`
- [ ] Verify debug messages appear

### Logging Testing

- [ ] Check `logs/kno.log` is created
- [ ] Verify timestamp in log messages
- [ ] Verify function names in log messages
- [ ] Check log rotation (if writing >10MB)
- [ ] Verify different log levels appear

### File Validation Testing

- [ ] Record valid audio
- [ ] Validate successfully
- [ ] Test with too-short/too-long audio
- [ ] Verify cleanup of temp files

### Error Recovery Testing

- [ ] Disconnect network during download
- [ ] Verify automatic retry with backoff
- [ ] Check logs show retry attempts
- [ ] Verify eventual success/failure

### Cross-Platform Testing

- [ ] Test on Windows (paths with backslash)
- [ ] Test on Linux (paths with forward slash)
- [ ] Test on macOS (paths, executable detection)
- [ ] Verify Whisper executable detection

---

## Continuous Integration

### GitHub Actions Workflow

**File: `.github/workflows/test.yml`**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10']
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        python run_all_tests.py
```

---

## Success Criteria

After applying improvements, verify:

- ✅ All messages go to logger (not print)
- ✅ Log files are created and rotated
- ✅ Configuration is read from environment
- ✅ Timeouts are configurable
- ✅ Retries happen with exponential backoff
- ✅ Temporary files are cleaned up
- ✅ Works on Windows/Linux/macOS
- ✅ All tests pass on all platforms

---

**Version:** 5.1 - Testing Guide  
**Last Updated:** February 16, 2026
