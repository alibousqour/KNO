# Quick Reference Card - Agent.py Improvements

## 🚀 Quick Start

### Initialize at Startup
```python
from agent import Config, logger, setup_logging

# Setup logging
Config.initialize()
Config.print_config()

logger.info("Application started")
```

### Configure Environment
```bash
# Set paths
export KNO_BASE_DIR=/path/to/data
export KNO_MODELS_DIR=/path/to/models
export KNO_LOGS_DIR=/path/to/logs

# Set timeouts
export KNO_TRANSCRIBE_TIMEOUT=240      # 4 minutes
export KNO_NETWORK_TIMEOUT=60          # 1 minute
export KNO_MAX_RETRIES=5               # 5 attempts

# Set logging
export KNO_LOG_LEVEL=DEBUG             # DEBUG/INFO/WARNING/ERROR
export KNO_CONSOLE_OUTPUT=true         # Show in console too

python agent.py
```

---

## 📝 Logging Usage

### Replace Old Print Statements
```python
# OLD ❌
print(f"[TAG] message", flush=True)

# NEW ✅
logger.info("message")
logger.debug("detailed info")
logger.warning("recoverable error")
logger.error("failed operation", exc_info=True)
```

### Log Levels Quick Guide
```python
logger.debug("Internal details")      # Developers only
logger.info("Important milestones")    # Always interesting
logger.warning("Something odd")        # Investigate later
logger.error("Operation failed")       # Fix required
logger.critical("System broken")       # Emergency
```

---

## ⚙️ Configuration Quick Reference

### Get Configuration Values
```python
# Paths
Config.BASE_DIR              # Base directory
Config.MODELS_DIR            # Models location
Config.LOGS_DIR              # Logs location
Config.get_path("models")    # Get any path type

# Timeouts (seconds)
Config.TRANSCRIBE_TIMEOUT    # Default: 120
Config.NETWORK_TIMEOUT       # Default: 30
Config.AUDIO_RECORD_TIMEOUT  # Default: 60
Config.BRAIN_LOOP_INTERVAL   # Default: 60

# Retry
Config.MAX_RETRIES           # Default: 3
Config.RETRY_DELAY           # Default: 1.0
Config.RETRY_BACKOFF         # Default: 2.0

# Audio
Config.SAMPLE_RATE           # Default: 16000
Config.AUDIO_CHANNELS        # Default: 1

# Logging
Config.LOG_LEVEL             # Default: "INFO"
Config.CONSOLE_OUTPUT        # Default: True
```

### Environment Variables List
| Variable | Default | Example |
|----------|---------|---------|
| `KNO_BASE_DIR` | `./` | `/home/user/kno` |
| `KNO_MODELS_DIR` | `BASE/models` | `/data/models` |
| `KNO_LOGS_DIR` | `BASE/logs` | `/var/log/kno` |
| `KNO_TRANSCRIBE_TIMEOUT` | `120` | `240` |
| `KNO_NETWORK_TIMEOUT` | `30` | `60` |
| `KNO_MAX_RETRIES` | `3` | `5` |
| `KNO_LOG_LEVEL` | `INFO` | `DEBUG` |
| `KNO_CONSOLE_OUTPUT` | `true` | `false` |

---

## 🔄 Retry Logic

### Use Retry Decorator
```python
@retry(max_attempts=3, delay=1, backoff=2)
def my_network_operation():
    """Automatically retries on failure."""
    return requests.get(url).json()

# Automatic retry strategy:
# Attempt 1: Fails immediately
# Attempt 2: Waits 1s, tries again
# Attempt 3: Waits 2s, tries again
# If all fail: Raises exception
```

### Built-in Retry
```python
# Already has @retry decorator
path = ResourceManager.download_file(
    url="https://...",
    destination="models",
    filename="model.bin",
    size_mb=500
)
```

---

## 📁 File Operations

### Validate Wave File
```python
from agent import validate_wave_file

is_valid, error = validate_wave_file(
    "audio.wav",
    min_duration=0.1,
    max_duration=600
)

if not is_valid:
    logger.error(f"Invalid audio: {error}")
    # File will be cleaned up
else:
    logger.info("Audio file valid")
```

### Safe File Deletion
```python
from agent import safe_file_delete

# Always succeeds (doesn't crash on missing file)
success = safe_file_delete("temp_audio.wav")

if success:
    logger.info("File deleted")
```

### Audio File Cleanup
```python
from agent import cleanup_temp_files

# Clean all temporary files
count = cleanup_temp_files(dry_run=False)
logger.info(f"Cleaned {count} temp files")
```

### Guaranteed Cleanup Pattern
```python
audio_file = None
try:
    audio_file = record_voice()
    text = transcribe(audio_file)
    return text
except Exception as e:
    logger.error(f"Failed: {e}")
    raise
finally:
    # Always runs
    if audio_file:
        safe_file_delete(audio_file)
```

---

## 🔧 Directory Structure

After `Config.initialize()`:

```
├── logs/                                   # Log files
│   └── kno.log                            # Main log (rotated)
├── models/                                 # AI models
│   ├── model.gguf                        # Local model (optional)
│   └── model.bin                         # Model file
├── sounds/                                 # Audio files
├── faces/                                  # Image data
├── whisper.cpp/
│   └── build/bin/
│       ├── whisper-cli.exe               # Windows
│       └── whisper                       # Linux/macOS
└── .env                                    # Configuration
```

---

## 🧪 Testing

### Quick Test
```bash
# Test logging
python -c "from agent import logger; logger.info('Test')"

# Test config
python -c "from agent import Config; Config.print_config()"

# Test file cleanup
python -c "from agent import cleanup_temp_files; cleanup_temp_files()"

# Run all tests
python tests/run_all_tests.py
```

### Convert Remaining Print Statements
```bash
# Dry run (see what would change)
python convert_logging.py --file agent.py

# Apply changes
python convert_logging.py --file agent.py --apply

# Verify
python agent.py
```

---

## 🐛 Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| Log file not created | Run `Config.initialize()` to create dirs |
| Can't find models | Check `KNO_MODELS_DIR` is set correctly |
| Timeout too short | `export KNO_TRANSCRIBE_TIMEOUT=300` |
| Too many retries | `export KNO_MAX_RETRIES=1` |
| Wrong paths | Verify `.env` file or env vars |
| Missing executable | Check `Config.get_whisper_executable()` |

---

## 📊 Scenarios

### Development (Fast Computer, Good Internet)
```bash
export KNO_LOG_LEVEL=DEBUG
export KNO_TRANSCRIBE_TIMEOUT=60
export KNO_MAX_RETRIES=2
python agent.py
```

### Production (Unreliable Network)
```bash
export KNO_BASE_DIR=/var/lib/kno
export KNO_LOG_LEVEL=INFO
export KNO_TRANSCRIBE_TIMEOUT=240
export KNO_MAX_RETRIES=5
python agent.py
```

### Docker Container
```bash
docker run \
  -e KNO_BASE_DIR=/data \
  -e KNO_LOG_LEVEL=INFO \
  -e KNO_CONSOLE_OUTPUT=true \
  -v kno_data:/data \
  myapp:latest
```

### Slow Hardware (RPi, Jetson)
```bash
export KNO_TRANSCRIBE_TIMEOUT=360
export KNO_NETWORK_TIMEOUT=60
export KNO_MAX_RETRIES=3
export KNO_RETRY_DELAY=5
python agent.py
```

---

## 🎯 Key Functions to Know

| Function | Purpose | Example |
|----------|---------|---------|
| `setup_logging()` | Setup logger | `setup_logging(log_level=DEBUG)` |
| `Config.initialize()` | Initialize directories | `Config.initialize()` |
| `Config.print_config()` | Print current config | `Config.print_config()` |
| `validate_wave_file()` | Check audio file | `validate_wave_file("audio.wav")` |
| `safe_file_delete()` | Delete safely | `safe_file_delete("temp.wav")` |
| `cleanup_temp_files()` | Clean temp files | `cleanup_temp_files()` |
| `@retry` | Retry decorator | `@retry(max_attempts=3)` |
| `Config.get_whisper_executable()` | Get Whisper path | `exe = Config.get_whisper_executable()` |

---

## 📚 Documentation Files

- **[REFACTORING_IMPROVEMENTS.md](REFACTORING_IMPROVEMENTS.md)** - Detailed guide
- **[CONFIGURATION_EXAMPLES.md](CONFIGURATION_EXAMPLES.md)** - Configuration samples
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - How to test
- **[REFACTORING_COMPLETE_SUMMARY.md](REFACTORING_COMPLETE_SUMMARY.md)** - Full summary

---

## ✅ Checklist for Production

- [ ] `Config.initialize()` called at startup
- [ ] Logging verified (check `logs/kno.log`)
- [ ] Environment variables set correctly
- [ ] File cleanup working
- [ ] Timeouts appropriate for your network
- [ ] Tests passing
- [ ] Error handling tested
- [ ] Documentation reviewed

---

**Version:** 5.1  
**Last Updated:** February 16, 2026  
**Status:** Production Ready ✅
