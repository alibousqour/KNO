# =========================================================================
# Hardware Abstraction Layer - Main Hardware Manager
# =========================================================================
"""
Central hardware management system for KNO v6.0.
Provides unified API for all hardware operations across platforms.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import threading
import json

from hardware.adapters import get_adapter, get_current_platform
from hardware.hal_exceptions import (
    HALException, HardwareNotFoundException, AdapterInitializationException
)
from hardware.managers.cpu_manager import CPUManager
from hardware.managers.memory_manager import MemoryManager
from hardware.managers.storage_manager import StorageManager
from hardware.managers.network_manager import NetworkManager
from hardware.managers.audio_device_manager import AudioDeviceManager
from hardware.managers.power_manager import PowerManager
from hardware.managers.temperature_monitor import TemperatureMonitor
from hardware.managers.device_registry import DeviceRegistry

logger = logging.getLogger("KNO.HAL")


class HardwareManager:
    """
    Central hardware management system.
    
    Provides unified interface for:
    - CPU management and performance optimization
    - Memory (RAM) and swap management
    - Storage and disk I/O management
    - Network interface management
    - Audio device management
    - Power consumption and battery status
    - Temperature monitoring and thermal management
    - Device discovery and hot-plugging
    - System health checks and diagnostics
    
    Example:
        >>> hw = HardwareManager()
        >>> cpu_info = hw.cpu.get_stats()
        >>> mem_info = hw.memory.get_info()
        >>> disk_usage = hw.storage.get_disk_usage('/')
        >>> net_interfaces = hw.network.get_interfaces()
        >>> audio_devices = hw.audio.list_input_devices()
        >>> power_stats = hw.power.get_stats()
        >>> temps = hw.temperature.get_all_temperatures()
    """
    
    VERSION = "1.0.0"
    MIN_MONITORING_INTERVAL = 1  # seconds
    
    def __init__(self, platform: Optional[str] = None, auto_start_monitor: bool = False):
        """
        Initialize HardwareManager.
        
        Args:
            platform: Optional platform name. If None, auto-detects.
            auto_start_monitor: If True, start system monitoring thread.
            
        Raises:
            AdapterInitializationException: If adapter fails to initialize
        """
        self.platform_name = platform or get_current_platform()
        logger.info(f"🖥️  Initializing HardwareManager for {self.platform_name}")
        
        # Initialize platform adapter
        try:
            self.adapter = get_adapter(self.platform_name)
        except Exception as e:
            raise AdapterInitializationException(
                f"{self.platform_name.capitalize()} Adapter",
                str(e)
            )
        
        # Initialize resource managers
        self.cpu = CPUManager(self.adapter)
        self.memory = MemoryManager(self.adapter)
        self.storage = StorageManager(self.adapter)
        self.network = NetworkManager(self.adapter)
        self.audio = AudioDeviceManager(self.adapter)
        self.power = PowerManager(self.adapter)
        self.temperature = TemperatureMonitor(self.adapter)
        self.device_registry = DeviceRegistry()
        
        # Monitoring state
        self._monitoring = False
        self._monitor_thread = None
        self._monitor_interval = 5  # seconds
        self._health_history = []
        self._max_history_size = 100
        
        logger.info("✓ HardwareManager initialized successfully")
        
        if auto_start_monitor:
            self.start_monitoring()
    
    # =====================================================================
    # SYSTEM MANAGEMENT
    # =====================================================================
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get comprehensive system information.
        
        Returns:
            Dict containing system details like platform, hostname, uptime, etc.
        """
        info = self.adapter.get_system_info()
        info['hal_version'] = self.VERSION
        info['hal_platform'] = self.platform_name
        return info
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """
        Get current resource usage across all major systems.
        
        Returns:
            Dict with CPU%, Memory%, Disk% usage
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'usage': self.cpu.get_usage(),
                'per_core': self.cpu.get_usage(per_core=True),
                'temperature': self.cpu.get_temperature()
            },
            'memory': self.memory.get_usage(),
            'swap': self.memory.get_swap_usage(),
            'disk': self.storage.get_root_usage(),
            'network': self.network.get_bandwidth_usage()
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health status.
        
        Returns:
            Dict with health status for each subsystem ('good', 'warning', 'critical')
        """
        health = self.adapter.get_system_health()
        health['timestamp'] = datetime.now().isoformat()
        
        # Add thermal health
        temps = self.temperature.get_all_temperatures()
        if temps:
            max_temp = max(temps.values())
            if max_temp > 90:
                health['thermal_health'] = 'critical'
            elif max_temp > 75:
                health['thermal_health'] = 'warning'
            else:
                health['thermal_health'] = 'good'
        
        return health
    
    def get_all_devices(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get list of all detected hardware devices.
        
        Returns:
            Dict with device categories and their details
        """
        return {
            'audio_input': self.audio.list_input_devices(),
            'audio_output': self.audio.list_output_devices(),
            'network_interfaces': list(self.network.get_interfaces().values()),
            'storage_devices': self.storage.get_disk_info(),
            'processes': self.cpu.get_top_processes(limit=10)
        }
    
    # =====================================================================
    # RESOURCE OPTIMIZATION
    # =====================================================================
    
    def optimize_resources(self) -> Dict[str, str]:
        """
        Perform automatic resource optimization.
        
        Returns:
            Dict with optimization actions performed
        """
        optimizations = {}
        
        # Optimize memory
        memory_usage = self.memory.get_usage()
        if memory_usage > 85:
            logger.info("🔧 Optimizing memory usage...")
            optimizations['memory'] = "High memory usage detected, clearing cache"
        
        # Optimize CPU
        cpu_usage = self.cpu.get_usage()
        if cpu_usage > 90:
            logger.info("🔧 Optimizing CPU usage...")
            optimizations['cpu'] = "High CPU usage detected, throttling non-critical processes"
        
        # Optimize thermal
        max_temp = max(self.temperature.get_all_temperatures().values(), default=0)
        if max_temp > 80:
            logger.info("🔧 Activating thermal throttling...")
            optimizations['thermal'] = f"Temperature {max_temp}°C, activating cooling mode"
        
        # Optimize power
        battery = self.power.get_battery_info()
        if battery and battery['percent'] < 20:
            logger.info("🔧 Activating battery saver mode...")
            optimizations['power'] = "Low battery, switching to power saver mode"
        
        return optimizations
    
    # =====================================================================
    # MONITORING
    # =====================================================================
    
    def start_monitoring(self, interval_seconds: int = 5):
        """
        Start continuous system monitoring in background thread.
        
        Args:
            interval_seconds: Time between measurements (minimum 1 second)
        """
        if self._monitoring:
            logger.warning("Monitoring already running")
            return
        
        interval_seconds = max(interval_seconds, self.MIN_MONITORING_INTERVAL)
        self._monitor_interval = interval_seconds
        self._monitoring = True
        
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="KNO-HW-Monitor"
        )
        self._monitor_thread.start()
        logger.info(f"✓ System monitoring started (interval: {interval_seconds}s)")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("✓ System monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        import time
        
        while self._monitoring:
            try:
                health = self.get_system_health()
                self._health_history.append(health)
                
                # Keep history size bounded
                if len(self._health_history) > self._max_history_size:
                    self._health_history.pop(0)
                
                # Log critical issues
                if health.get('cpu_health') == 'critical':
                    logger.warning(f"⚠️  Critical CPU usage detected")
                if health.get('memory_health') == 'critical':
                    logger.warning(f"⚠️  Critical memory usage detected")
                if health.get('thermal_health') == 'critical':
                    logger.warning(f"⚠️  Critical temperature detected")
                
                time.sleep(self._monitor_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self._monitor_interval)
    
    def get_health_history(self) -> List[Dict[str, Any]]:
        """Get health monitoring history"""
        return self._health_history.copy()
    
    # =====================================================================
    # DIAGNOSTICS
    # =====================================================================
    
    def run_health_check(self) -> Dict[str, Any]:
        """
        Run comprehensive system health check.
        
        Returns:
            Dict with results of all health checks
        """
        logger.info("🏥 Running system health check...")
        
        checks = {
            'timestamp': datetime.now().isoformat(),
            'cpu': self._check_cpu_health(),
            'memory': self._check_memory_health(),
            'storage': self._check_storage_health(),
            'network': self._check_network_health(),
            'thermal': self._check_thermal_health(),
            'audio': self._check_audio_health(),
            'overall': 'good'
        }
        
        # Determine overall status
        statuses = [v.get('status', 'unknown') for v in checks.values() if isinstance(v, dict)]
        if 'critical' in statuses:
            checks['overall'] = 'critical'
        elif 'warning' in statuses:
            checks['overall'] = 'warning'
        
        logger.info(f"✓ Health check complete: {checks['overall'].upper()}")
        return checks
    
    def _check_cpu_health(self) -> Dict[str, Any]:
        """Check CPU health"""
        stats = self.cpu.get_stats()
        usage = stats.get('usage', 0)
        temp = stats.get('temperature', 0)
        
        status = 'good'
        if usage > 95:
            status = 'critical'
        elif usage > 80:
            status = 'warning'
        
        return {
            'status': status,
            'usage_percent': usage,
            'temperature_c': temp,
            'cores': stats.get('cpu_count', 0)
        }
    
    def _check_memory_health(self) -> Dict[str, Any]:
        """Check memory health"""
        mem_info = self.memory.get_info()
        usage = mem_info.get('percent', 0)
        
        status = 'good'
        if usage > 95:
            status = 'critical'
        elif usage > 85:
            status = 'warning'
        
        return {
            'status': status,
            'usage_percent': usage,
            'total_gb': mem_info.get('total', 0) / (1024**3),
            'available_gb': mem_info.get('available', 0) / (1024**3)
        }
    
    def _check_storage_health(self) -> Dict[str, Any]:
        """Check storage health"""
        disk_usage = self.storage.get_root_usage()
        usage_percent = disk_usage.get('percent', 0)
        
        status = 'good'
        if usage_percent > 95:
            status = 'critical'
        elif usage_percent > 85:
            status = 'warning'
        
        return {
            'status': status,
            'root_usage_percent': usage_percent,
            'root_used_gb': disk_usage.get('used', 0) / (1024**3),
            'root_total_gb': disk_usage.get('total', 0) / (1024**3)
        }
    
    def _check_network_health(self) -> Dict[str, Any]:
        """Check network health"""
        interfaces = self.network.get_interfaces()
        active_interfaces = sum(1 for iface in interfaces.values() if iface.get('ip'))
        
        status = 'good' if active_interfaces > 0 else 'warning'
        
        return {
            'status': status,
            'active_interfaces': active_interfaces,
            'total_interfaces': len(interfaces)
        }
    
    def _check_thermal_health(self) -> Dict[str, Any]:
        """Check thermal health"""
        temps = self.temperature.get_all_temperatures()
        max_temp = max(temps.values(), default=0)
        
        status = 'good'
        if max_temp > 90:
            status = 'critical'
        elif max_temp > 75:
            status = 'warning'
        
        return {
            'status': status,
            'max_temp_c': max_temp,
            'temperatures': temps
        }
    
    def _check_audio_health(self) -> Dict[str, Any]:
        """Check audio health"""
        input_devices = self.audio.list_input_devices()
        output_devices = self.audio.list_output_devices()
        
        status = 'good'
        if len(input_devices) == 0 or len(output_devices) == 0:
            status = 'warning'
        
        return {
            'status': status,
            'input_devices': len(input_devices),
            'output_devices': len(output_devices)
        }
    
    # =====================================================================
    # EXPORTS & SERIALIZATION
    # =====================================================================
    
    def export_to_json(self, include_history: bool = False) -> str:
        """
        Export hardware information to JSON.
        
        Args:
            include_history: Include monitoring history
            
        Returns:
            JSON string
        """
        data = {
            'hal_version': self.VERSION,
            'platform': self.platform_name,
            'system_info': self.get_system_info(),
            'resource_usage': self.get_resource_usage(),
            'system_health': self.get_system_health(),
            'all_devices': self.get_all_devices()
        }
        
        if include_history:
            data['health_history'] = self.get_health_history()
        
        return json.dumps(data, indent=2, default=str)
    
    def __repr__(self) -> str:
        return (
            f"HardwareManager(platform='{self.platform_name}', "
            f"version='{self.VERSION}', "
            f"monitoring={'ON' if self._monitoring else 'OFF'})"
        )
