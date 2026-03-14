# KNO Configuration Examples

Comprehensive configuration examples for different deployment scenarios.

## Quick Start Configuration

### Windows (Local Development)

**File: `.env`**
```env
# Base directories
KNO_BASE_DIR=C:\Users\YourName\KNO
KNO_MODELS_DIR=C:\Users\YourName\KNO\models
KNO_LOGS_DIR=C:\Users\YourName\KNO\logs

# Audio settings
KNO_SAMPLE_RATE=16000
KNO_AUDIO_CHANNELS=1

# Performance tuning
KNO_TRANSCRIBE_TIMEOUT=120
KNO_NETWORK_TIMEOUT=30
KNO_MAX_RETRIES=3

# Logging
KNO_LOG_LEVEL=INFO
KNO_CONSOLE_OUTPUT=true

# Cleanup
KNO_CLEANUP_TEMP_FILES=true
```

**PowerShell Launch**
```powershell
# Load configuration from .env
& ".\venv\Scripts\Activate.ps1"
python agent.py
```

### Linux/Ubuntu (Server Deployment)

**File: `.env`**
```env
# Base directories
KNO_BASE_DIR=/home/ubuntu/kno
KNO_MODELS_DIR=/home/ubuntu/kno/models
KNO_LOGS_DIR=/home/ubuntu/kno/logs

# Audio settings
KNO_SAMPLE_RATE=16000
KNO_AUDIO_CHANNELS=1

# Performance tuning for server
KNO_TRANSCRIBE_TIMEOUT=180
KNO_NETWORK_TIMEOUT=60
KNO_MAX_RETRIES=5

# Logging to syslog
KNO_LOG_LEVEL=DEBUG
KNO_CONSOLE_OUTPUT=false

# Cleanup
KNO_CLEANUP_TEMP_FILES=true
```

**Bash Launch**
```bash
#!/bin/bash
source /home/ubuntu/kno/.env
cd /home/ubuntu/kno
python3 agent.py >> logs/startup.log 2>&1
```

### macOS (Development)

**File: `~/.bashrc` or `~/.zshrc`**
```bash
export KNO_BASE_DIR="$HOME/Projects/kno"
export KNO_MODELS_DIR="$HOME/Projects/kno/models"
export KNO_SAMPLE_RATE=16000
export KNO_LOG_LEVEL=DEBUG
```

**Launch**
```bash
source ~/.zshrc
cd ~/Projects/kno
python agent.py
```

---

## Scenario-Based Configurations

### Scenario 1: Fast Local Network (Recommended for Development)

**When to use:**
- Local machine with good internet (>100 Mbps)
- Powerful CPU/GPU
- Should be responsive

**Configuration**
```env
KNO_BASE_DIR=./                        # Use current directory

# Tight timeouts - network is fast
KNO_TRANSCRIBE_TIMEOUT=60              # 1 minute
KNO_NETWORK_TIMEOUT=10                 # 10 seconds
KNO_AUDIO_RECORD_TIMEOUT=30            # 30 seconds

# Minimal retries - few transient failures
KNO_MAX_RETRIES=2
KNO_RETRY_DELAY=1
KNO_RETRY_BACKOFF=2

# Aggressive logging
KNO_LOG_LEVEL=DEBUG
KNO_CONSOLE_OUTPUT=true

# Cleanup immediately
KNO_CLEANUP_TEMP_FILES=true
```

### Scenario 2: Slow/Unreliable Network (Production)

**When to use:**
- Deployed to cloud (network variable)
- Unstable WiFi or cellular
- Must be reliable over responsive

**Configuration**
```env
KNO_BASE_DIR=/var/lib/kno

# Generous timeouts - network can be slow
KNO_TRANSCRIBE_TIMEOUT=240             # 4 minutes
KNO_NETWORK_TIMEOUT=60                 # 60 seconds
KNO_AUDIO_RECORD_TIMEOUT=60            # 60 seconds

# aggressive Retries - handle transients
KNO_MAX_RETRIES=5
KNO_RETRY_DELAY=2
KNO_RETRY_BACKOFF=2

# Production logging
KNO_LOG_LEVEL=INFO
KNO_CONSOLE_OUTPUT=false               # Send to syslog instead

# Cleanup after delays
KNO_CLEANUP_TEMP_FILES=true
```

### Scenario 3: High-Performance Server (GPU/TPU)

**When to use:**
- High-end hardware
- Processing many requests
- Need maximum throughput

**Configuration**
```env
KNO_BASE_DIR=/mnt/data/kno            # Fast SSD

# Model caching (don't reload)
KNO_MODEL_CACHE_ENABLED=true
KNO_MODEL_CACHE_TTL=3600

# Aggressive processing
KNO_TRANSCRIBE_TIMEOUT=30              # Very fast
KNO_NETWORK_TIMEOUT=5                  # Assume local data
KNO_AUDIO_RECORD_TIMEOUT=10

# Few retries - just skip slow requests
KNO_MAX_RETRIES=1
KNO_RETRY_DELAY=0.5

# Minimal logging overhead
KNO_LOG_LEVEL=WARNING
KNO_CONSOLE_OUTPUT=false

# Batch cleanup
KNO_CLEANUP_TEMP_FILES=true
```

### Scenario 4: Embedded/Edge Device (RPi, NVIDIA Jetson)

**When to use:**
- Resource-constrained device
- Limited memory/CPU
- Temperature concerns

**Configuration**
```env
KNO_BASE_DIR=/home/pi/kno             # Standard location

# Conservative timeouts - slow processor
KNO_TRANSCRIBE_TIMEOUT=360             # 6 minutes
KNO_NETWORK_TIMEOUT=30                 # Standard internet
KNO_AUDIO_RECORD_TIMEOUT=60

# Retry with long backoff - don't thrash
KNO_MAX_RETRIES=3
KNO_RETRY_DELAY=5
KNO_RETRY_BACKOFF=1.5

# Minimal logging - preserve disk
KNO_LOG_LEVEL=WARNING
KNO_CONSOLE_OUTPUT=false

# Aggressive cleanup
KNO_CLEANUP_TEMP_FILES=true
KNO_TEMP_FILES_MAX_AGE=300            # Clean files >5min old
```

### Scenario 5: Docker Container

**When to use:**
- Container-based deployment
- Kubernetes orchestration
- Cloud provider

**Configuration (container environment)**
```bash
# Dockerfile environment
ENV KNO_BASE_DIR=/data
ENV KNO_MODELS_DIR=/data/models
ENV KNO_LOGS_DIR=/var/log/kno
ENV KNO_LOG_LEVEL=INFO
ENV KNO_CONSOLE_OUTPUT=true      # Log goes to stdout
ENV KNO_CLEANUP_TEMP_FILES=true
```

**docker-compose.yml**
```yaml
version: '3.8'
services:
  kno:
    build: .
    environment:
      - KNO_BASE_DIR=/data
      - KNO_TRANSCRIBE_TIMEOUT=180
      - KNO_MAX_RETRIES=5
      - KNO_LOG_LEVEL=DEBUG
    volumes:
      - kno_data:/data
      - kno_logs:/var/log/kno
    ports:
      - "3000:3000"
    healthcheck:
      test: ["CMD", "python3", "-c", "import kno; print('OK')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## Environment Variable Reference

### Directory Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `KNO_BASE_DIR` | Path | `./` | Base directory for all KNO files |
| `KNO_MODELS_DIR` | Path | `BASE_DIR/models` | Where AI models are stored |
| `KNO_SOUNDS_DIR` | Path | `BASE_DIR/sounds` | Where audio files are stored |
| `KNO_LOGS_DIR` | Path | `BASE_DIR/logs` | Where log files are written |
| `KNO_WHISPER_DIR` | Path | `BASE_DIR/whisper.cpp/build/bin` | Where Whisper binary is located |

### Timeout Settings (seconds)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `KNO_TRANSCRIBE_TIMEOUT` | int | `120` | Max time for speech→text |
| `KNO_AUDIO_RECORD_TIMEOUT` | int | `60` | Max duration of audio recording |
| `KNO_NETWORK_TIMEOUT` | int | `30` | Max time for network requests |
| `KNO_BRAIN_LOOP_INTERVAL` | int | `60` | Autonomous brain loop cycle |

### Retry Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `KNO_MAX_RETRIES` | int | `3` | Max retry attempts on failure |
| `KNO_RETRY_DELAY` | float | `1.0` | Initial retry delay (seconds) |
| `KNO_RETRY_BACKOFF` | float | `2.0` | Backoff multiplier per retry |

### Audio Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `KNO_SAMPLE_RATE` | int | `16000` | Audio sample rate (Hz) |
| `KNO_AUDIO_CHANNELS` | int | `1` | Number of channels (mono/stereo) |
| `KNO_AUDIO_DTYPE` | str | `float32` | Audio data type |

### Logging Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `KNO_LOG_LEVEL` | str | `INFO` | Log level (DEBUG/INFO/WARNING/ERROR) |
| `KNO_CONSOLE_OUTPUT` | bool | `true` | Also print to console (vs file only) |

### Cleanup Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `KNO_CLEANUP_TEMP_FILES` | bool | `true` | Auto-delete temporary files |

---

## Configuration Priority

KNO checks settings in this order (first found wins):

1. **Environment Variables** (e.g., `$KNO_BASE_DIR`)
2. **.env File** (in project root)
3. **Hardcoded Defaults** (fallback)

### Example Priority Resolution

```python
# If you have all three:

# 1. Environment variable (highest priority)
export KNO_BASE_DIR="/custom/path"

# 2. .env file
KNO_BASE_DIR=/env/file/path

# 3. Hardcoded default (lowest priority)
BASE_DIR = Path("./")

# Result: /custom/path is used
Config.BASE_DIR  # => /custom/path
```

---

## Using Configuration in Python Code

### Get Configuration Values

```python
# Direct access
models = Config.MODELS_DIR  # Path object
timeout = Config.TRANSCRIBE_TIMEOUT  # int

# Get paths by type
path = Config.get_path("models")
path = Config.get_path("whisper")

# Get platform-appropriate executable
exe = Config.get_whisper_executable()

# Print all settings (useful for debugging)
Config.print_config()
```

### Create Custom Configuration

```python
# Can subclass Config for custom settings
class MyConfig(Config):
    CUSTOM_SETTING = os.getenv("MY_CUSTOM_SETTING", "default_value")
```

---

## Testing Configuration

### Validate Current Configuration

```python
from pathlib import Path
import sys

# Add KNO to path
sys.path.insert(0, str(Path(__file__).parent))

from agent import Config, logger

# Initialize and verify
Config.initialize()
Config.print_config()

# Check specific paths
print(f"Models available: {list(Config.MODELS_DIR.glob('*.gguf'))}")
print(f"Whisper executable: {Config.get_whisper_executable()}")
```

### Environment Variable Test

```bash
# Test different configurations
KNO_BASE_DIR=/tmp/test python -c "from agent import Config; print(Config.BASE_DIR)"
KNO_LOG_LEVEL=DEBUG python agent.py  # Run with debug logging
KNO_MAX_RETRIES=1 python agent.py    # Fewer retries for testing
```

---

## Troubleshooting Configuration

### Issue: Can't Find Models

**Solution:**
```bash
# Check current models directory
python -c "from agent import Config; Config.initialize(); print(Config.MODELS_DIR)"

# Set explicit path
export KNO_MODELS_DIR=/path/to/models
python agent.py
```

### Issue: Slow Transcription

**Solution:**
```bash
# Increase timeout for slow networks
export KNO_TRANSCRIBE_TIMEOUT=240
python agent.py  # 4-minute timeout instead of 2
```

### Issue: Too Many Retries

**Solution:**
```bash
# Reduce retries for development/testing
export KNO_MAX_RETRIES=1
export KNO_RETRY_DELAY=0
python agent.py
```

### Issue: Log File Not Being Written

**Solution:**
```bash
# Check log level and console output
export KNO_LOG_LEVEL=DEBUG
export KNO_CONSOLE_OUTPUT=true
python agent.py

# Verify directory exists
ls -la $(python -c "from agent import Config; print(Config.LOGS_DIR)")
```

---

## Production Deployment Checklist

- [ ] Set `KNO_BASE_DIR` to persistent storage
- [ ] Set `KNO_LOG_LEVEL=INFO` (not DEBUG)
- [ ] Set `KNO_CONSOLE_OUTPUT=false` (reduce overhead)
- [ ] Set `KNO_MAX_RETRIES=5` (handle transients)
- [ ] Set `KNO_TRANSCRIBE_TIMEOUT=240` (generous)
- [ ] Set `KNO_CLEANUP_TEMP_FILES=true`
- [ ] Verify `KNO_MODELS_DIR` points to fast storage
- [ ] Setup log rotation (Config handles this automatically)
- [ ] Test with expected network conditions
- [ ] Monitor log files for errors

---

## Quick Reference

**Development:**
```bash
export KNO_LOG_LEVEL=DEBUG
export KNO_MAX_RETRIES=2
python agent.py
```

**Production:**
```bash
export KNO_BASE_DIR=/var/lib/kno
export KNO_LOG_LEVEL=INFO
export KNO_MAX_RETRIES=5
python agent.py
```

**Docker:**
```bash
docker run -e KNO_LOG_LEVEL=INFO \
           -e KNO_BASE_DIR=/data \
           -v kno_data:/data \
           myapp:latest
```

**Slow Network:**
```bash
export KNO_TRANSCRIBE_TIMEOUT=300
export KNO_NETWORK_TIMEOUT=60
export KNO_MAX_RETRIES=5
python agent.py
```
