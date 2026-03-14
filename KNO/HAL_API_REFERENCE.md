# KNO v6.0 - Hardware Abstraction Layer (HAL) - API Reference
## خارطة المراجع - Complete API Documentation

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [HardwareManager API](#hardwaremanager-api)
4. [Resource Managers](#resource-managers)
5. [Platform Adapters](#platform-adapters)
6. [Exception Handling](#exception-handling)
7. [Configuration](#configuration)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Examples](#examples)

---

## Quick Start

### Basic Initialization

```python
from hardware import HardwareManager

# Initialize HardwareManager (auto-detects platform)
hw = HardwareManager()

# Get system information
sys_info = hw.get_system_info()

# Get resource usage
usage = hw.get_resource_usage()

# Get system health
health = hw.get_system_health()
```

### Using Individual Managers

```python
# CPU Management
cpu_usage = hw.cpu.get_usage()
cpu_stats = hw.cpu.get_stats()

# Memory Management
mem_info = hw.memory.get_info()
mem_usage = hw.memory.get_usage()

# Storage Management
disk_usage = hw.storage.get_disk_usage('/')

# Network Management
interfaces = hw.network.get_interfaces()

# Audio Management
input_devices = hw.audio.list_input_devices()

# Power Management
battery = hw.power.get_battery_info()

# Temperature Monitoring
temps = hw.temperature.get_all_temperatures()
```

---

## Architecture Overview

### HAL Layer Architecture

```
┌─────────────────────────────────────────────────────┐
│       KNO Application Layer (agent.py)              │
└─────────────────────────────────────────────────────┘
                        ↓ (API calls)
┌─────────────────────────────────────────────────────┐
│       HardwareManager (Orchestrator)                │
│  ├─ CPU Manager                                     │
│  ├─ Memory Manager                                  │
│  ├─ Storage Manager                                 │
│  ├─ Network Manager                                 │
│  ├─ Audio Device Manager                            │
│  ├─ Power Manager                                   │
│  ├─ Temperature Monitor                             │
│  └─ Device Registry                                 │
└─────────────────────────────────────────────────────┘
                        ↓ (Adapter pattern)
┌─────────────────────────────────────────────────────┐
│       Platform Adapters                             │
│  ├─ Windows Adapter                                 │
│  ├─ Linux Adapter                                   │
│  ├─ macOS Adapter (future)                          │
│  └─ Raspberry Pi Adapter (future)                   │
└─────────────────────────────────────────────────────┘
                        ↓ (System calls)
┌─────────────────────────────────────────────────────┐
│       Operating System APIs                         │
│  ├─ WMI (Windows)                                   │
│  ├─ /proc filesystem (Linux)                        │
│  ├─ psutil (Cross-platform)                         │
│  └─ PyAudio, netifaces, etc.                        │
└─────────────────────────────────────────────────────┘
```

---

## HardwareManager API

### Constructor

```python
HardwareManager(platform: Optional[str] = None, 
                auto_start_monitor: bool = False) -> HardwareManager
```

**Parameters:**
- `platform`: Optional platform name. If None, auto-detects ('windows', 'linux', 'raspi')
- `auto_start_monitor`: Start monitoring thread immediately

**Example:**
```python
# Auto-detect platform
hw = HardwareManager()

# Explicit platform
hw = HardwareManager(platform='linux')

# With monitoring
hw = HardwareManager(auto_start_monitor=True)
```

### System Information Methods

#### `get_system_info() → Dict[str, Any]`
Get comprehensive system information.

**Returns:**
```python
{
    'platform': 'windows',
    'system': 'Windows',
    'release': '10',
    'hostname': 'MY-LAPTOP',
    'processor': 'Intel Core i7',
    'cpu_count': 8,
    'memory': 16000000000,  # bytes
    'uptime': 1234567890.0  # seconds
}
```

#### `get_resource_usage() → Dict[str, Any]`
Get current resource usage across all systems.

**Returns:**
```python
{
    'timestamp': '2026-03-10T15:30:45.123456',
    'cpu': {
        'usage': 45.2,  # percentage
        'per_core': [10.5, 15.3, 20.1, ...],
        'temperature': 65.5  # Celsius
    },
    'memory': 65.3,  # percentage
    'swap': 12.1,    # percentage
    'disk': {'percent': 48.5},
    'network': {'bytes_sent': 1000000, 'bytes_recv': 2000000}
}
```

#### `get_system_health() → Dict[str, Any]`
Get overall system health status.

**Returns:**
```python
{
    'timestamp': '2026-03-10T15:30:45.123456',
    'cpu_health': 'good',      # 'good', 'warning', 'critical'
    'memory_health': 'warning',
    'disk_health': 'good',
    'thermal_health': 'good',
    'overall': 'warning'
}
```

### Device Management

#### `get_all_devices() → Dict[str, List[Dict]]`
Get all detected hardware devices.

**Returns:**
```python
{
    'audio_input': [...],
    'audio_output': [...],
    'network_interfaces': [...],
    'storage_devices': [...],
    'processes': [...]
}
```

### Optimization

#### `optimize_resources() → Dict[str, str]`
Perform automatic resource optimization.

**Returns:**
```python
{
    'memory': 'High memory usage detected, clearing cache',
    'cpu': 'High CPU usage detected, throttling non-critical processes',
    'thermal': 'Temperature 82°C, activating cooling mode'
}
```

### Monitoring

#### `start_monitoring(interval_seconds: int = 5) → None`
Start continuous system monitoring in background.

```python
hw.start_monitoring(interval_seconds=2)
```

#### `stop_monitoring() → None`
Stop system monitoring.

```python
hw.stop_monitoring()
```

#### `get_health_history() → List[Dict[str, Any]]`
Get monitoring history.

```python
history = hw.get_health_history()
for snapshot in history:
    print(snapshot['timestamp'], snapshot['cpu_health'])
```

### Diagnostics

#### `run_health_check() → Dict[str, Any]`
Run comprehensive system health check.

**Returns:**
```python
{
    'timestamp': '2026-03-10T15:30:45.123456',
    'cpu': {
        'status': 'good',
        'usage_percent': 45.2,
        'temperature_c': 65.5,
        'cores': 8
    },
    'memory': {
        'status': 'good',
        'usage_percent': 65.3,
        'total_gb': 16.0,
        'available_gb': 5.5
    },
    'storage': {...},
    'network': {...},
    'thermal': {...},
    'overall': 'good'
}
```

### Data Export

#### `export_to_json(include_history: bool = False) → str`
Export hardware information to JSON.

```python
json_data = hw.export_to_json(include_history=True)
print(json_data)
```

---

## Resource Managers

### CPU Manager

#### Properties & Methods

```python
hw.cpu.get_count() → int
hw.cpu.get_frequency() → Dict[str, float]
hw.cpu.get_usage(per_core: bool = False) → float | List[float]
hw.cpu.get_temperature() → Optional[float]
hw.cpu.set_frequency(core_id: int, frequency_mhz: int) → bool
hw.cpu.get_stats() → Dict[str, Any]
hw.cpu.get_top_processes(limit: int = 10) → List[Dict]
```

#### Examples

```python
# Get CPU information
print(f"Cores: {hw.cpu.get_count()}")
print(f"Usage: {hw.cpu.get_usage():.1f}%")

# Per-core usage
per_core = hw.cpu.get_usage(per_core=True)
for i, usage in enumerate(per_core):
    print(f"Core {i}: {usage:.1f}%")

# Temperature
if temp := hw.cpu.get_temperature():
    print(f"Temperature: {temp:.1f}°C")

# Top processes
for proc in hw.cpu.get_top_processes(limit=5):
    print(f"{proc['name']}: {proc['cpu_percent']:.1f}%")
```

### Memory Manager

#### Properties & Methods

```python
hw.memory.get_info() → Dict[str, int]
hw.memory.get_usage() → float
hw.memory.get_swap_info() → Dict[str, int]
hw.memory.get_swap_usage() → float
hw.memory.get_by_process(pid: int) → Dict[str, int]
hw.memory.get_stats() → Dict[str, Any]
```

#### Examples

```python
# Memory information
mem = hw.memory.get_info()
print(f"Total: {mem['total'] / (1024**3):.2f} GB")
print(f"Available: {mem['available'] / (1024**3):.2f} GB")
print(f"Usage: {hw.memory.get_usage():.1f}%")

# Swap information
swap = hw.memory.get_swap_info()
print(f"Swap Total: {swap['total'] / (1024**3):.2f} GB")
print(f"Swap Usage: {hw.memory.get_swap_usage():.1f}%")
```

### Storage Manager

#### Properties & Methods

```python
hw.storage.get_disk_info() → List[Dict]
hw.storage.get_disk_usage(path: str) → Dict
hw.storage.get_root_usage() → Dict
hw.storage.get_io_stats() → Dict
hw.storage.mount_volume(device: str, mountpoint: str) → bool
hw.storage.unmount_volume(mountpoint: str) → bool
hw.storage.get_stats() → Dict[str, Any]
```

#### Examples

```python
# Disk information
for disk in hw.storage.get_disk_info():
    usage = hw.storage.get_disk_usage(disk['mountpoint'])
    print(f"{disk['device']}: {usage['percent']:.1f}% used")

# Root usage
root = hw.storage.get_root_usage()
print(f"Root: {root['used'] / (1024**3):.2f} / {root['total'] / (1024**3):.2f} GB")

# I/O stats
io = hw.storage.get_io_stats()
print(f"Read: {io['read_bytes'] / (1024**3):.2f} GB")
print(f"Written: {io['write_bytes'] / (1024**3):.2f} GB")
```

### Network Manager

#### Properties & Methods

```python
hw.network.get_interfaces() → Dict[str, Dict]
hw.network.get_interface_stats(interface: str) → Dict
hw.network.get_ip_address(interface: str) → Optional[str]
hw.network.get_mac_address(interface: str) → Optional[str]
hw.network.enable_interface(interface: str) → bool
hw.network.disable_interface(interface: str) → bool
hw.network.get_bandwidth_usage() → Dict
hw.network.get_stats() → Dict[str, Any]
```

#### Examples

```python
# List interfaces
for iface_name, iface_info in hw.network.get_interfaces().items():
    print(f"{iface_name}: {iface_info['ip']}")

# Get specific interface info
ip = hw.network.get_ip_address('eth0')
mac = hw.network.get_mac_address('eth0')

# Bandwidth usage
bw = hw.network.get_bandwidth_usage()
print(f"Sent: {bw['bytes_sent'] / (1024**3):.2f} GB")
print(f"Received: {bw['bytes_recv'] / (1024**3):.2f} GB")
```

### Audio Device Manager

#### Properties & Methods

```python
hw.audio.list_input_devices() → List[Dict]
hw.audio.list_output_devices() → List[Dict]
hw.audio.get_device_info(device_id: int, is_input: bool) → Dict
hw.audio.set_default_input(device_id: int) → bool
hw.audio.set_default_output(device_id: int) → bool
hw.audio.get_volume(device_id: Optional[int] = None) → float
hw.audio.set_volume(level: float, device_id: Optional[int] = None) → bool
hw.audio.get_stats() → Dict
```

#### Examples

```python
# List devices
print("Input devices:")
for dev in hw.audio.list_input_devices():
    print(f"  [{dev['id']}] {dev['name']} ({dev['channels']} channels)")

print("Output devices:")
for dev in hw.audio.list_output_devices():
    print(f"  [{dev['id']}] {dev['name']} ({dev['channels']} channels)")

# Volume control
vol = hw.audio.get_volume()
print(f"Volume: {vol * 100:.0f}%")

hw.audio.set_volume(0.75)  # 75%
```

### Power Manager

#### Properties & Methods

```python
hw.power.get_battery_info() → Optional[Dict]
hw.power.get_consumption() → Dict[str, float]
hw.power.set_profile(profile: str) → bool
hw.power.get_stats() → Dict[str, Any]
```

#### Examples

```python
# Battery information
battery = hw.power.get_battery_info()
if battery:
    print(f"Battery: {battery['percent']:.1f}%")
    print(f"Plugged In: {battery['power_plugged']}")

# Power profile
hw.power.set_profile('powersave')  # 'performance', 'balanced', 'powersave'
```

### Temperature Monitor

#### Properties & Methods

```python
hw.temperature.get_all_temperatures() → Dict[str, float]
hw.temperature.get_max_temperature() → float
hw.temperature.is_critical() → bool
hw.temperature.is_warning() → bool
hw.temperature.check_thermal_health() → str
hw.temperature.get_stats() → Dict
```

#### Examples

```python
# Get temperatures
temps = hw.temperature.get_all_temperatures()
for sensor, temp in temps.items():
    print(f"{sensor}: {temp:.1f}°C")

# Check status
status = hw.temperature.check_thermal_health()
if status == 'critical':
    print("⚠️  Critical temperature!")
```

---

## Platform Adapters

### Supported Platforms

| Platform | Support | Dependencies |
|----------|---------|--------------|
| Windows 10/11 | ✅ Full | psutil, pyaudio, optional: wmi |
| Linux (Ubuntu, Debian, etc.) | ✅ Full | psutil, pyaudio, netifaces, optional: GPUtil |
| Raspberry Pi | ⏳ Partial | psutil, pyaudio, optional: RPi.GPIO |
| macOS | ⏳ Partial | psutil, pyaudio (fallback to Linux adapter) |

### Using Specific Adapters

```python
from hardware.adapters import get_adapter

# Get adapter for specific platform
adapter = get_adapter('linux')

# Or auto-detect
adapter = get_adapter()

# Create HardwareManager with specific adapter
from hardware import HardwareManager
hw = HardwareManager(platform='windows')
```

---

## Exception Handling

### Exception Hierarchy

```
HALException (base)
├── PlatformNotSupportedException
├── HardwareNotFoundException
├── HardwareAccessDeniedException
├── DeviceNotReadyException
├── ResourceExhaustedException
├── ThermalThrottlingException
├── AdapterInitializationException
└── Specific Manager Exceptions
    ├── CPUManagerException
    ├── MemoryManagerException
    ├── StorageManagerException
    ├── NetworkManagerException
    ├── AudioManagerException
    ├── PowerManagerException
    └── TemperatureException
```

### Error Handling Examples

```python
from hardware import HardwareManager
from hardware import HALException, HardwareNotFoundException

try:
    hw = HardwareManager()
    cpu_freq = hw.cpu.get_frequency()
except HALException as e:
    print(f"HAL Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")

# Catching specific exceptions
try:
    hw = HardwareManager(platform='unsupported')
except AdapterInitializationException as e:
    print(f"Failed to initialize: {e}")
```

---

## Configuration

### Environment Variables

```bash
# Enable debug logging
export KNO_HAL_DEBUG=1

# Set specific platform (override auto-detection)
export KNO_HAL_PLATFORM=linux

# Monitoring interval (seconds)
export KNO_HAL_MONITOR_INTERVAL=5
```

### Logging Configuration

```python
import logging

# Enable debug logging for HAL
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("KNO.HAL")
logger.setLevel(logging.DEBUG)
```

---

## Best Practices

### 1. Use Context Managers for Long-Running Operations

```python
from hardware.hal_decorators import PerformanceTimer

with PerformanceTimer("System Check") as timer:
    health = hw.run_health_check()
    # Do something with health data
# Time will be logged automatically
```

### 2. Cache Expensive Operations

```python
# HAL automatically caches expensive operations
# but you can manually control it:

# Get fresh data (bypasses cache)
stats = hw.adapter.get_system_info()

# Use cached version
stats = hw.get_system_info()
```

### 3. Handle Long-Running Monitoring

```python
# Start monitoring in background
hw.start_monitoring(interval_seconds=5)

# Do other work...

# Stop before exit
hw.stop_monitoring()
```

### 4. Check Health Before Making Decisions

```python
health = hw.get_system_health()

if health['cpu_health'] == 'critical':
    # Reduce CPU-intensive tasks
    pass

if health['memory_health'] == 'critical':
    # Clear caches, free memory
    pass
```

---

## Troubleshooting

### Issue: "psutil not installed"

**Solution:**
```bash
pip install psutil
```

### Issue: "Permission denied" errors

**Solution (Linux):**
```bash
# Some operations require root:
sudo python your_script.py

# Or use passwordless sudo for specific commands
sudo visudo  # Add: youruser ALL=(ALL) NOPASSWD: /usr/bin/amixer, etc.
```

### Issue: AudioManager returns empty device list

**Solution:**
```bash
# Install PyAudio
pip install pyaudio

# On Linux, you may also need:
sudo apt-get install portaudio19-dev python3-dev
```

### Issue: Network interfaces not detected

**Solution (Linux):**
```bash
pip install netifaces
```

### Issue: Temperature not showing

**Solution (Windows):**
```bash
# CPU temperature requires WMI
pip install pywin32
```

---

## Examples

### Example 1: Complete System Diagnostic Report

```python
from hardware import HardwareManager
import json

hw = HardwareManager()

report = {
    'system': hw.get_system_info(),
    'usage': hw.get_resource_usage(),
    'health': hw.run_health_check(),
    'devices': hw.get_all_devices()
}

print(json.dumps(report, indent=2, default=str))
```

### Example 2: Real-Time Monitoring Dashboard

```python
from hardware import HardwareManager
import time

hw = HardwareManager()
hw.start_monitoring(interval_seconds=1)

try:
    for _ in range(60):
        usage = hw.get_resource_usage()
        print(f"CPU: {usage['cpu']['usage']:.1f}% | "
              f"Mem: {usage['memory']:.1f}% | "
              f"Disk: {usage['disk']['percent']:.1f}%")
        time.sleep(1)
finally:
    hw.stop_monitoring()
```

### Example 3: Alert System

```python
from hardware import HardwareManager

hw = HardwareManager()

def check_alerts():
    health = hw.run_health_check()
    
    if health['cpu']['status'] == 'critical':
        send_alert("🔴 CRITICAL: CPU usage is very high!")
    
    if health['thermal']['status'] == 'critical':
        send_alert("🔴 CRITICAL: System is overheating!")
    
    if health['memory']['status'] == 'warning':
        send_alert("🟡 WARNING: Memory usage is high")

check_alerts()
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-10 | Initial release with Windows and Linux support |

---

## Contributing

To contribute to HAL development:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## License

MIT License - See LICENSE file for details

---

**Last Updated**: 2026-03-10  
**Status**: ✅ Production Ready  
**Support**: GitHub Issues
