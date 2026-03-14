# KNO v6.0 - Hardware Abstraction Layer (HAL) - Quick Start Guide
## دليل البدء السريع

**Last Updated**: 2026-03-10

---

## 📦 Installation

### Step 1: Install Core Dependencies

```bash
# Windows
pip install psutil pyaudio python-dotenv colorlog

# Linux (Ubuntu/Debian)
pip install psutil pyaudio python-dotenv colorlog netifaces
sudo apt-get install portaudio19-dev python3-dev

# Optional: GPU support (Linux)
pip install GPUtil
```

### Step 2: Verify Installation

```python
from hardware import HardwareManager

hw = HardwareManager()
print(hw)  # Should print: HardwareManager(platform='...', ...)
```

---

## 🚀 5-Minute Quick Start

### Basic System Information

```python
from hardware import HardwareManager

# Initialize
hw = HardwareManager()

# Get system info
info = hw.get_system_info()
print(f"Platform: {info['platform']}")
print(f"Hostname: {info['hostname']}")
print(f"CPU Cores: {info['cpu_count']}")
print(f"Total RAM: {info['memory'] / (1024**3):.1f} GB")
```

### Check System Health

```python
# Get health status
health = hw.get_system_health()
print(f"Overall: {health['overall'].upper()}")
print(f"CPU: {health['cpu_health']}")
print(f"Memory: {health['memory_health']}")
print(f"Disk: {health['disk_health']}")
```

### Get Resource Usage

```python
# Current resource usage
usage = hw.get_resource_usage()
print(f"CPU Usage: {usage['cpu']['usage']:.1f}%")
print(f"Memory: {usage['memory']:.1f}%")
print(f"Disk: {usage['disk']['percent']:.1f}%")
```

---

## 🎯 Common Use Cases

### 1. Monitor CPU Usage

```python
hw = HardwareManager()

# Get CPU info
print(f"CPU Cores: {hw.cpu.get_count()}")
print(f"CPU Usage: {hw.cpu.get_usage():.1f}%")
print(f"Temperature: {hw.cpu.get_temperature():.1f}°C")

# Top processes
for proc in hw.cpu.get_top_processes(limit=3):
    print(f"{proc['name']}: {proc['cpu_percent']:.1f}%")
```

### 2. Check Memory Usage

```python
hw = HardwareManager()

mem = hw.memory.get_info()
print(f"Total: {mem['total'] / (1024**3):.1f} GB")
print(f"Used: {mem['used'] / (1024**3):.1f} GB")
print(f"Available: {mem['available'] / (1024**3):.1f} GB")
print(f"Usage: {mem['percent']:.1f}%")
```

### 3. Monitor Storage

```python
hw = HardwareManager()

for disk in hw.storage.get_disk_info():
    usage = hw.storage.get_disk_usage(disk['mountpoint'])
    print(f"{disk['device']}: {usage['percent']:.1f}% used")
```

### 4. List Network Interfaces

```python
hw = HardwareManager()

for ifname, ifdata in hw.network.get_interfaces().items():
    print(f"{ifname}")
    print(f"  IP: {ifdata['ip']}")
    print(f"  MAC: {ifdata['mac']}")
```

### 5. Manage Audio Devices

```python
hw = HardwareManager()

# List devices
print("Microphones:")
for dev in hw.audio.list_input_devices():
    print(f"  [{dev['id']}] {dev['name']}")

print("Speakers:")
for dev in hw.audio.list_output_devices():
    print(f"  [{dev['id']}] {dev['name']}")

# Control volume
print(f"Volume: {hw.audio.get_volume() * 100:.0f}%")
hw.audio.set_volume(0.75)  # 75%
```

### 6. Check Battery Status

```python
hw = HardwareManager()

battery = hw.power.get_battery_info()
if battery:
    print(f"Battery: {battery['percent']:.1f}%")
    print(f"Plugged In: {battery['power_plugged']}")
```

### 7. Monitor Temperature

```python
hw = HardwareManager()

temps = hw.temperature.get_all_temperatures()
for sensor, temp in temps.items():
    print(f"{sensor}: {temp:.1f}°C")

status = hw.temperature.check_thermal_health()
print(f"Thermal Health: {status}")
```

### 8. Run Full Health Check

```python
hw = HardwareManager()

health = hw.run_health_check()

print(f"Overall: {health['overall'].upper()}")
for subsystem, check in health.items():
    if isinstance(check, dict) and 'status' in check:
        print(f"  {subsystem}: {check['status']}")
```

---

## 🔄 Start Monitoring

### Simple Monitoring

```python
from hardware import HardwareManager
import time

hw = HardwareManager()

# Start monitoring
hw.start_monitoring(interval_seconds=2)

for i in range(10):
    usage = hw.get_resource_usage()
    print(f"CPU: {usage['cpu']['usage']:.1f}%, "
          f"Memory: {usage['memory']:.1f}%")
    time.sleep(1)

hw.stop_monitoring()
```

### Monitoring with Alerts

```python
from hardware import HardwareManager
import time

hw = HardwareManager()
hw.start_monitoring(interval_seconds=2)

for _ in range(30):
    health = hw.run_health_check()
    
    if health['cpu']['status'] == 'critical':
        print("🔴 ALERT: CPU usage is critical!")
    elif health['memory']['status'] == 'warning':
        print("🟡 WARNING: Memory usage is high")
    
    time.sleep(1)

hw.stop_monitoring()
```

---

## 💾 Export Data

### Export to JSON

```python
from hardware import HardwareManager
import json

hw = HardwareManager()

# Export system snapshot
data = {
    'system': hw.get_system_info(),
    'usage': hw.get_resource_usage(),
    'health': hw.run_health_check(),
    'devices': hw.get_all_devices()
}

# Save to file
with open('system_info.json', 'w') as f:
    json.dump(data, f, indent=2, default=str)

# Or use HAL's built-in export
json_str = hw.export_to_json(include_history=False)
```

### Create Report

```python
from hardware import HardwareManager
import json
from datetime import datetime

hw = HardwareManager()

report = {
    'timestamp': datetime.now().isoformat(),
    'system': hw.get_system_info(),
    'diagnostics': hw.run_health_check(),
    'resource_usage': hw.get_resource_usage(),
    'audio_devices': hw.audio.get_stats(),
    'network_stats': hw.network.get_stats()
}

print(json.dumps(report, indent=2, default=str))
```

---

## 🔧 Configuration

### Using Environment Variables

```bash
# Enable debug logging
export KNO_HAL_DEBUG=1

# Set specific platform
export KNO_HAL_PLATFORM=linux

# Set monitoring interval
export KNO_HAL_MONITOR_INTERVAL=5
```

### Logging Configuration

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("KNO.HAL")
logger.setLevel(logging.DEBUG)

# Now use HAL normally
from hardware import HardwareManager
hw = HardwareManager()
```

---

## ❌ Troubleshooting

### Issue: "No module named 'hardware'"

**Solution**: Make sure you're in the KNO directory and the hardware folder exists.

```bash
# Check directory structure
ls -la hardware/
# Should show: __init__.py, hardware_manager.py, adapters/, managers/

# Try importing
python -c "from hardware import HardwareManager; print('OK')"
```

### Issue: "psutil is not installed"

**Solution**: Install psutil

```bash
pip install psutil
# Verify
python -c "import psutil; print(psutil.__version__)"
```

### Issue: "No audio devices found"

**Solution**: Install PyAudio

```bash
# Windows
pip install pyaudio

# Linux
sudo apt-get install portaudio19-dev python3-dev
pip install pyaudio

# Verify
python -c "import pyaudio; print('OK')"
```

### Issue: "ImportError: cannot import name 'Device'"

**Solution**: Make sure all HAL files are created properly

```bash
# Check file exists
ls -la hardware/managers/device_registry.py

# Check import
python -c "from hardware.managers import Device; print('OK')"
```

### Issue: "Permission Denied" on Linux

**Solution**: Some operations require root or specific permissions

```bash
# Run with sudo if needed
sudo python your_script.py

# Or set up passwordless sudo
sudo visudo
# Add: youruser ALL=(ALL) NOPASSWD: /usr/bin/amixer
```

---

## 📚 Next Steps

### Learn More

1. **Full API Reference**: See `HAL_API_REFERENCE.md`
2. **Usage Examples**: See `hardware_examples.py`
3. **Technical Details**: See `AINATIVE_OS_ROADMAP_v5.md`

### Integration with KNO

```python
# In agent.py, add HAL monitoring:
from hardware import HardwareManager

class KNOAgent:
    def __init__(self):
        self.hw = HardwareManager()
        self.hw.start_monitoring()
    
    def check_resources(self):
        health = self.hw.get_system_health()
        if health['memory_health'] == 'critical':
            # Take action
            pass
```

### Create Dashboard

```python
# Simple monitoring display
from hardware import HardwareManager
import time
import os

hw = HardwareManager()

while True:
    os.system('clear' if os.name == 'posix' else 'cls')
    
    usage = hw.get_resource_usage()
    health = hw.get_system_health()
    
    print(f"╔═══════════════════════════════════════╗")
    print(f"║     SYSTEM MONITORING DASHBOARD     ║")
    print(f"╠═══════════════════════════════════════╣")
    print(f"║ CPU:    {usage['cpu']['usage']:5.1f}%  Health: {health['cpu_health']:8s} ║")
    print(f"║ Memory: {usage['memory']:5.1f}%  Health: {health['memory_health']:8s} ║")
    print(f"║ Disk:   {usage['disk']['percent']:5.1f}%  Health: {health['disk_health']:8s} ║")
    print(f"╚═══════════════════════════════════════╝")
    
    time.sleep(2)
```

---

## 📞 Getting Help

### Common Questions

**Q: How do I list all audio devices?**
```python
hw = HardwareManager()
for dev in hw.audio.list_input_devices():
    print(dev)
```

**Q: How do I check if the system is overheating?**
```python
if hw.temperature.is_critical():
    print("System is overheating!")
```

**Q: How do I optimize resources?**
```python
optimizations = hw.optimize_resources()
for optimization in optimizations.values():
    print(optimization)
```

**Q: How do I export system information?**
```python
json_str = hw.export_to_json()
```

---

## ✨ Tips & Tricks

### Tip 1: Use Caching Efficiently
```python
# First call - queries hardware
cpu_freq = hw.cpu.get_frequency()  # ~50ms

# Second call within TTL - uses cache
cpu_freq = hw.cpu.get_frequency()  # <5ms
```

### Tip 2: Batch Queries
```python
# Good: Query once, use results
health = hw.run_health_check()
print(health['cpu'])
print(health['memory'])

# Bad: Multiple queries (slower)
cpu_health = hw.cpu.get_stats()
mem_health = hw.memory.get_stats()
```

### Tip 3: Use Context Managers
```python
from hardware.hal_decorators import PerformanceTimer

with PerformanceTimer("Full check"):
    health = hw.run_health_check()
    # Time automatically logged
```

### Tip 4: Monitor in Background
```python
# Start monitoring once
hw.start_monitoring(interval_seconds=5)

# Keep running in background
# Do other work...

# Check anytime
history = hw.get_health_history()
```

---

## 🎓 Learning Path

1. **Beginner**: Run basic examples (5 min)
   - Get system info
   - Check resource usage
   - View devices

2. **Intermediate**: Use individual managers (15 min)
   - CPU monitoring
   - Memory management
   - Storage monitoring

3. **Advanced**: Create dashboards (30 min)
   - Real-time monitoring
   - Health checks
   - Alerts and notifications

4. **Expert**: Integrate with KNO (60+ min)
   - Update agent.py
   - Create custom adapters
   - Build monitoring UI

---

## 🚀 You're All Set!

You now have the KNO Hardware Abstraction Layer ready to use. 

**Next Steps:**
1. ✅ Install dependencies
2. ✅ Run some examples
3. ✅ Integrate with your code
4. ✅ Create monitors/dashboards

**Happy Coding! 🎉**

---

## 📖 Quick Reference

```python
# Initialize
hw = HardwareManager()

# System Info
hw.get_system_info()
hw.get_resource_usage()
hw.get_system_health()
hw.run_health_check()

# CPU
hw.cpu.get_count()
hw.cpu.get_usage()
hw.cpu.get_temperature()
hw.cpu.get_top_processes()

# Memory
hw.memory.get_info()
hw.memory.get_usage()
hw.memory.get_swap_info()

# Storage
hw.storage.get_disk_info()
hw.storage.get_disk_usage('/')
hw.storage.get_io_stats()

# Network
hw.network.get_interfaces()
hw.network.get_ip_address('eth0')
hw.network.get_bandwidth_usage()

# Audio
hw.audio.list_input_devices()
hw.audio.list_output_devices()
hw.audio.get_volume()
hw.audio.set_volume(0.75)

# Power
hw.power.get_battery_info()
hw.power.set_profile('powersave')

# Temperature
hw.temperature.get_all_temperatures()
hw.temperature.check_thermal_health()

# Monitoring
hw.start_monitoring()
hw.stop_monitoring()
hw.get_health_history()

# Export
hw.export_to_json()
```

---

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: 2026-03-10
