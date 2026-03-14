# =========================================================================
# hardware/__init__.py - Hardware Abstraction Layer (HAL)
# =========================================================================
"""
KNO v6.0 Hardware Abstraction Layer (HAL)

Provides unified hardware management across Windows, Linux, and Raspberry Pi.

Quick Start:
    from hardware import HardwareManager
    
    hw = HardwareManager()
    
    # CPU management
    cpu_stats = hw.cpu.get_stats()
    cpu_usage = hw.cpu.get_usage()
    
    # Memory management
    mem_info = hw.memory.get_info()
    mem_usage = hw.memory.get_usage()
    
    # Disk management
    disk_usage = hw.storage.get_root_usage()
    
    # Network management
    interfaces = hw.network.get_interfaces()
    
    # Audio management
    input_devices = hw.audio.list_input_devices()
    output_devices = hw.audio.list_output_devices()
    
    # Power management
    battery = hw.power.get_battery_info()
    
    # Temperature monitoring
    temps = hw.temperature.get_all_temperatures()
    
    # System diagnostics
    health = hw.run_health_check()
    
    # Start monitoring
    hw.start_monitoring(interval_seconds=5)
"""

from .hardware_manager import HardwareManager
from .adapters import get_adapter, get_current_platform
from .hal_exceptions import (
    HALException,
    PlatformNotSupportedException,
    HardwareNotFoundException,
    HardwareAccessDeniedException,
    DeviceNotReadyException,
    ResourceExhaustedException,
    ThermalThrottlingException,
    AdapterInitializationException
)
from .managers import (
    CPUManager,
    MemoryManager,
    StorageManager,
    NetworkManager,
    AudioDeviceManager,
    PowerManager,
    TemperatureMonitor,
    DeviceRegistry,
    Device
)

__version__ = "1.0.0"
__author__ = "KNO Development Team"
__license__ = "MIT"

__all__ = [
    # Main classes
    'HardwareManager',
    
    # Managers
    'CPUManager',
    'MemoryManager',
    'StorageManager',
    'NetworkManager',
    'AudioDeviceManager',
    'PowerManager',
    'TemperatureMonitor',
    'DeviceRegistry',
    'Device',
    
    # Adapters
    'get_adapter',
    'get_current_platform',
    
    # Exceptions
    'HALException',
    'PlatformNotSupportedException',
    'HardwareNotFoundException',
    'HardwareAccessDeniedException',
    'DeviceNotReadyException',
    'ResourceExhaustedException',
    'ThermalThrottlingException',
    'AdapterInitializationException'
]
