# =========================================================================
# Hardware Abstraction Layer - Base Adapter
# =========================================================================
"""
Base class for platform adapters (Windows, Linux, macOS, Raspberry Pi).
Defines the interface that all adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
import logging

logger = logging.getLogger("KNO.HAL.Adapters")


# =========================================================================
# PLATFORM DETECTION
# =========================================================================

def get_current_platform() -> str:
    """
    Detect current operating system platform.
    
    Returns:
        One of: 'linux', 'windows', 'macos', 'raspi'
    """
    import platform
    import sys
    
    system = platform.system().lower()
    
    # Check for Raspberry Pi
    if system == 'linux':
        try:
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read().strip().lower()
                if 'raspberry' in model:
                    return 'raspi'
        except (FileNotFoundError, IOError):
            pass
        return 'linux'
    
    if system == 'windows':
        return 'windows'
    
    if system == 'darwin':
        return 'macos'
    
    raise RuntimeError(f"Unknown platform: {system}")


# =========================================================================
# BASE ADAPTER CLASS
# =========================================================================

class BaseAdapter(ABC):
    """
    Abstract base class for platform adapters.
    All platform-specific implementations must inherit from this class.
    """
    
    def __init__(self):
        self.platform_name = self.get_platform_name()
        self.is_available = True
        self._initialize()
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return platform name (e.g., 'linux', 'windows')"""
        pass
    
    @abstractmethod
    def _initialize(self):
        """Initialize the adapter. Called after __init__."""
        pass
    
    # =====================================================================
    # CPU MANAGEMENT
    # =====================================================================
    
    @abstractmethod
    def get_cpu_count(self) -> int:
        """Get number of CPU cores"""
        pass
    
    @abstractmethod
    def get_cpu_frequency(self) -> Dict[str, float]:
        """
        Get CPU frequency information.
        Returns: {'current': float, 'min': float, 'max': float} (MHz)
        """
        pass
    
    @abstractmethod
    def get_cpu_usage(self, per_core: bool = False) -> float:
        """
        Get CPU usage percentage.
        Args:
            per_core: If True, return list of per-core values
        Returns: float (0-100) or list of floats
        """
        pass
    
    @abstractmethod
    def get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature in Celsius (if available)"""
        pass
    
    @abstractmethod
    def set_cpu_frequency(self, core_id: int, frequency_mhz: int) -> bool:
        """Set CPU frequency (requires admin/root)"""
        pass
    
    @abstractmethod
    def get_cpu_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive CPU statistics.
        Returns: dict with cpu_count, frequency, usage, temperature, etc.
        """
        pass
    
    # =====================================================================
    # MEMORY MANAGEMENT
    # =====================================================================
    
    @abstractmethod
    def get_memory_info(self) -> Dict[str, int]:
        """
        Get memory information in bytes.
        Returns: {'total': int, 'available': int, 'used': int, 'percent': float}
        """
        pass
    
    @abstractmethod
    def get_swap_info(self) -> Dict[str, int]:
        """
        Get swap memory information in bytes.
        Returns: {'total': int, 'used': int, 'percent': float}
        """
        pass
    
    @abstractmethod
    def get_memory_by_process(self, pid: int) -> Dict[str, int]:
        """
        Get memory usage for a specific process.
        Returns: {'rss': int, 'vms': int, 'percent': float}
        """
        pass
    
    @abstractmethod
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        pass
    
    # =====================================================================
    # STORAGE MANAGEMENT
    # =====================================================================
    
    @abstractmethod
    def get_disk_info(self) -> List[Dict[str, Any]]:
        """
        Get list of all disks.
        Returns: [{'device': str, 'mountpoint': str, 'fstype': str}, ...]
        """
        pass
    
    @abstractmethod
    def get_disk_usage(self, path: str) -> Dict[str, Any]:
        """
        Get disk usage for a path.
        Returns: {'total': int, 'used': int, 'free': int, 'percent': float}
        """
        pass
    
    @abstractmethod
    def get_disk_io_stats(self) -> Dict[str, Any]:
        """
        Get disk I/O statistics.
        Returns: {'read_bytes': int, 'write_bytes': int, ...}
        """
        pass
    
    @abstractmethod
    def mount_volume(self, device: str, mountpoint: str) -> bool:
        """Mount a filesystem (requires admin/root)"""
        pass
    
    @abstractmethod
    def unmount_volume(self, mountpoint: str) -> bool:
        """Unmount a filesystem (requires admin/root)"""
        pass
    
    @abstractmethod
    def get_disk_stats(self) -> Dict[str, Any]:
        """Get comprehensive disk statistics"""
        pass
    
    # =====================================================================
    # NETWORK MANAGEMENT
    # =====================================================================
    
    @abstractmethod
    def get_network_interfaces(self) -> Dict[str, Dict[str, Any]]:
        """
        Get list of network interfaces.
        Returns: {'eth0': {'ip': str, 'mac': str, ...}, ...}
        """
        pass
    
    @abstractmethod
    def get_interface_stats(self, interface: str) -> Dict[str, Any]:
        """
        Get interface statistics.
        Returns: {'bytes_sent': int, 'bytes_recv': int, ...}
        """
        pass
    
    @abstractmethod
    def get_ip_address(self, interface: str) -> Optional[str]:
        """Get IP address for interface"""
        pass
    
    @abstractmethod
    def get_mac_address(self, interface: str) -> Optional[str]:
        """Get MAC address for interface"""
        pass
    
    @abstractmethod
    def enable_interface(self, interface: str) -> bool:
        """Enable network interface (requires admin/root)"""
        pass
    
    @abstractmethod
    def disable_interface(self, interface: str) -> bool:
        """Disable network interface (requires admin/root)"""
        pass
    
    @abstractmethod
    def get_network_stats(self) -> Dict[str, Any]:
        """Get comprehensive network statistics"""
        pass
    
    # =====================================================================
    # AUDIO DEVICE MANAGEMENT
    # =====================================================================
    
    @abstractmethod
    def list_audio_input_devices(self) -> List[Dict[str, Any]]:
        """
        List all audio input devices (microphones).
        Returns: [{'id': int, 'name': str, 'channels': int, ...}, ...]
        """
        pass
    
    @abstractmethod
    def list_audio_output_devices(self) -> List[Dict[str, Any]]:
        """
        List all audio output devices (speakers).
        Returns: [{'id': int, 'name': str, 'channels': int, ...}, ...]
        """
        pass
    
    @abstractmethod
    def get_audio_device_info(self, device_id: int, is_input: bool) -> Dict[str, Any]:
        """Get detailed information about an audio device"""
        pass
    
    @abstractmethod
    def set_default_audio_input(self, device_id: int) -> bool:
        """Set default input device (requires admin/root)"""
        pass
    
    @abstractmethod
    def set_default_audio_output(self, device_id: int) -> bool:
        """Set default output device (requires admin/root)"""
        pass
    
    @abstractmethod
    def get_volume(self, device_id: Optional[int] = None) -> float:
        """Get volume level (0.0-1.0)"""
        pass
    
    @abstractmethod
    def set_volume(self, level: float, device_id: Optional[int] = None) -> bool:
        """Set volume level (0.0-1.0)"""
        pass
    
    @abstractmethod
    def get_audio_stats(self) -> Dict[str, Any]:
        """Get comprehensive audio statistics"""
        pass
    
    # =====================================================================
    # POWER MANAGEMENT
    # =====================================================================
    
    @abstractmethod
    def get_battery_info(self) -> Optional[Dict[str, Any]]:
        """
        Get battery information (if available).
        Returns: {'percent': float, 'status': str, ...} or None
        """
        pass
    
    @abstractmethod
    def get_power_consumption(self) -> Dict[str, float]:
        """Get power consumption (watts) by component"""
        pass
    
    @abstractmethod
    def set_power_profile(self, profile: str) -> bool:
        """
        Set power profile: 'performance', 'balanced', 'powersave'
        Requires admin/root
        """
        pass
    
    @abstractmethod
    def get_power_stats(self) -> Dict[str, Any]:
        """Get comprehensive power statistics"""
        pass
    
    # =====================================================================
    # TEMPERATURE MONITORING
    # =====================================================================
    
    @abstractmethod
    def get_all_temperatures(self) -> Dict[str, float]:
        """
        Get all available temperatures.
        Returns: {'cpu': float, 'gpu': float, 'disk': float, ...} (Celsius)
        """
        pass
    
    @abstractmethod
    def get_temperature_stats(self) -> Dict[str, Any]:
        """Get comprehensive temperature statistics"""
        pass
    
    # =====================================================================
    # PROCESS MANAGEMENT
    # =====================================================================
    
    @abstractmethod
    def get_process_list(self) -> List[Dict[str, Any]]:
        """
        Get list of all running processes.
        Returns: [{'pid': int, 'name': str, 'status': str, ...}, ...]
        """
        pass
    
    @abstractmethod
    def get_process_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a process"""
        pass
    
    @abstractmethod
    def kill_process(self, pid: int, force: bool = False) -> bool:
        """Kill a process"""
        pass
    
    @abstractmethod
    def set_process_priority(self, pid: int, priority: int) -> bool:
        """Set process priority (-20 to 19, lower = higher priority)"""
        pass
    
    # =====================================================================
    # SYSTEM INFO
    # =====================================================================
    
    @abstractmethod
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get comprehensive system information.
        Returns: {
            'platform': str,
            'hostname': str,
            'kernel': str,
            'uptime': float,
            'boot_time': float,
            ...
        }
        """
        pass
    
    @abstractmethod
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health metrics.
        Returns: {
            'cpu_health': str,  # 'good', 'warning', 'critical'
            'memory_health': str,
            'disk_health': str,
            'thermal_health': str,
            ...
        }
        """
        pass
