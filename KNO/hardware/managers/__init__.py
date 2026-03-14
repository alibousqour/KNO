# =========================================================================
# hardware/managers/__init__.py
# =========================================================================
"""Resource managers for HAL"""

from .cpu_manager import CPUManager
from .memory_manager import MemoryManager
from .storage_manager import StorageManager
from .network_manager import NetworkManager
from .audio_device_manager import AudioDeviceManager
from .power_manager import PowerManager
from .temperature_monitor import TemperatureMonitor
from .device_registry import DeviceRegistry, Device

__all__ = [
    'CPUManager',
    'MemoryManager',
    'StorageManager',
    'NetworkManager',
    'AudioDeviceManager',
    'PowerManager',
    'TemperatureMonitor',
    'DeviceRegistry',
    'Device'
]
