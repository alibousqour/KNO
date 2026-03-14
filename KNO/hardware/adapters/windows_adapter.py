# =========================================================================
# Hardware Abstraction Layer - Windows Adapter
# =========================================================================
"""
Platform adapter for Windows 10/11.
Uses psutil, pyaudio, and WMI for hardware access.
"""

import logging
import platform
from typing import Dict, Any, Optional, List
import psutil

logger = logging.getLogger("KNO.HAL.Windows")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.warning("PyAudio not available - audio features limited")

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    logger.warning("WMI not available - some features limited")

from hardware.adapters.base_adapter import BaseAdapter
from hardware.hal_decorators import retry, cached


class WindowsAdapter(BaseAdapter):
    """Windows 10/11 hardware access adapter"""
    
    def get_platform_name(self) -> str:
        return "windows"
    
    def _initialize(self):
        """Initialize Windows adapter"""
        logger.info(f"Initializing Windows adapter on {platform.release()}")
        self.system_name = platform.system()
        self.release = platform.release()
        self.version = platform.version()
        
        if WMI_AVAILABLE:
            try:
                self.wmi = wmi.WMI()
            except Exception as e:
                logger.error(f"Failed to initialize WMI: {e}")
                self.wmi = None
        else:
            self.wmi = None
    
    # =====================================================================
    # CPU MANAGEMENT
    # =====================================================================
    
    def get_cpu_count(self) -> int:
        return psutil.cpu_count(logical=False)
    
    @cached(ttl=5)
    def get_cpu_frequency(self) -> Dict[str, float]:
        """Get CPU frequency information"""
        try:
            freq = psutil.cpu_freq()
            if freq:
                return {
                    'current': freq.current,
                    'min': freq.min,
                    'max': freq.max
                }
        except Exception as e:
            logger.warning(f"Failed to get CPU frequency: {e}")
        
        return {'current': 0.0, 'min': 0.0, 'max': 0.0}
    
    @cached(ttl=2)
    def get_cpu_usage(self, per_core: bool = False) -> float:
        """Get CPU usage percentage"""
        try:
            if per_core:
                return psutil.cpu_percent(interval=0.1, percpu=True)
            else:
                return psutil.cpu_percent(interval=0.1)
        except Exception as e:
            logger.error(f"Error getting CPU usage: {e}")
            return 0.0
    
    def get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature (Windows requires third-party tools)"""
        if not self.wmi:
            return None
        
        try:
            temps = self.wmi.query("SELECT CurrentTemperature FROM Win32_TemperatureProbe")
            if temps:
                # Convert from Kelvin to Celsius
                kelvin = int(temps[0].CurrentTemperature)
                return kelvin - 273.15
        except Exception as e:
            logger.warning(f"Failed to get CPU temperature: {e}")
        
        return None
    
    def set_cpu_frequency(self, core_id: int, frequency_mhz: int) -> bool:
        """
        Set CPU frequency (requires admin and specific tools).
        Windows doesn't provide direct CPU frequency control without special drivers.
        """
        logger.warning("CPU frequency control not directly available on Windows")
        return False
    
    def get_cpu_stats(self) -> Dict[str, Any]:
        """Get comprehensive CPU statistics"""
        return {
            'cpu_count': self.get_cpu_count(),
            'frequency': self.get_cpu_frequency(),
            'usage': self.get_cpu_usage(),
            'per_core_usage': self.get_cpu_usage(per_core=True),
            'temperature': self.get_cpu_temperature(),
            'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
            'ctx_switches': psutil.cpu_stats().ctx_switches,
            'interrupts': psutil.cpu_stats().interrupts
        }
    
    # =====================================================================
    # MEMORY MANAGEMENT
    # =====================================================================
    
    @cached(ttl=2)
    def get_memory_info(self) -> Dict[str, int]:
        """Get memory information"""
        mem = psutil.virtual_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent
        }
    
    @cached(ttl=2)
    def get_swap_info(self) -> Dict[str, int]:
        """Get swap memory information"""
        swap = psutil.swap_memory()
        return {
            'total': swap.total,
            'used': swap.used,
            'percent': swap.percent
        }
    
    def get_memory_by_process(self, pid: int) -> Dict[str, int]:
        """Get memory usage for a specific process"""
        try:
            proc = psutil.Process(pid)
            mem_info = proc.memory_info()
            return {
                'rss': mem_info.rss,
                'vms': mem_info.vms,
                'percent': proc.memory_percent()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning(f"Failed to get memory info for PID {pid}: {e}")
            return {'rss': 0, 'vms': 0, 'percent': 0.0}
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        return {
            'memory': self.get_memory_info(),
            'swap': self.get_swap_info(),
            'by_process': {
                proc.pid: self.get_memory_by_process(proc.pid)
                for proc in psutil.process_iter(['pid']) if proc.pid != 0
            }
        }
    
    # =====================================================================
    # STORAGE MANAGEMENT
    # =====================================================================
    
    def get_disk_info(self) -> List[Dict[str, Any]]:
        """Get list of all disks"""
        disks = []
        try:
            for partition in psutil.disk_partitions():
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'opts': partition.opts
                })
        except Exception as e:
            logger.error(f"Error getting disk info: {e}")
        
        return disks
    
    @cached(ttl=10)
    def get_disk_usage(self, path: str) -> Dict[str, Any]:
        """Get disk usage for a path"""
        try:
            usage = psutil.disk_usage(path)
            return {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            }
        except Exception as e:
            logger.error(f"Error getting disk usage for {path}: {e}")
            return {'total': 0, 'used': 0, 'free': 0, 'percent': 0.0}
    
    @cached(ttl=5)
    def get_disk_io_stats(self) -> Dict[str, Any]:
        """Get disk I/O statistics"""
        try:
            io = psutil.disk_io_counters()
            return {
                'read_bytes': io.read_bytes,
                'write_bytes': io.write_bytes,
                'read_count': io.read_count,
                'write_count': io.write_count,
                'read_time': io.read_time,
                'write_time': io.write_time
            }
        except Exception as e:
            logger.warning(f"Failed to get disk I/O stats: {e}")
            return {}
    
    def mount_volume(self, device: str, mountpoint: str) -> bool:
        """Mount volume (requires admin on Windows)"""
        logger.warning("Volume mounting not directly available on Windows")
        return False
    
    def unmount_volume(self, mountpoint: str) -> bool:
        """Unmount volume (requires admin)"""
        logger.warning("Volume unmounting not directly available on Windows")
        return False
    
    def get_disk_stats(self) -> Dict[str, Any]:
        """Get comprehensive disk statistics"""
        return {
            'disks': self.get_disk_info(),
            'usage': {disk['device']: self.get_disk_usage(disk['mountpoint']) 
                     for disk in self.get_disk_info()},
            'io': self.get_disk_io_stats()
        }
    
    # =====================================================================
    # NETWORK MANAGEMENT
    # =====================================================================
    
    @cached(ttl=10)
    def get_network_interfaces(self) -> Dict[str, Dict[str, Any]]:
        """Get network interfaces"""
        interfaces = {}
        try:
            for interface_name, interface_addrs in psutil.net_if_addrs().items():
                interfaces[interface_name] = {
                    'ip': None,
                    'mac': None,
                    'addresses': []
                }
                
                for addr in interface_addrs:
                    interfaces[interface_name]['addresses'].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
                    
                    if addr.family == 2:  # AF_INET
                        interfaces[interface_name]['ip'] = addr.address
                    elif addr.family == 17:  # AF_LINK (MAC)
                        interfaces[interface_name]['mac'] = addr.address
        except Exception as e:
            logger.error(f"Error getting network interfaces: {e}")
        
        return interfaces
    
    @cached(ttl=5)
    def get_interface_stats(self, interface: str) -> Dict[str, Any]:
        """Get interface statistics"""
        try:
            stats = psutil.net_if_stats()[interface]
            return {
                'is_up': stats.isup,
                'speed': stats.speed,
                'mtu': stats.mtu,
                'errors': stats.errin + stats.errout,
                'dropped': stats.dropin + stats.dropout
            }
        except (KeyError, Exception) as e:
            logger.warning(f"Failed to get stats for {interface}: {e}")
            return {}
    
    def get_ip_address(self, interface: str) -> Optional[str]:
        """Get IP address for interface"""
        interfaces = self.get_network_interfaces()
        return interfaces.get(interface, {}).get('ip')
    
    def get_mac_address(self, interface: str) -> Optional[str]:
        """Get MAC address for interface"""
        interfaces = self.get_network_interfaces()
        return interfaces.get(interface, {}).get('mac')
    
    def enable_interface(self, interface: str) -> bool:
        """Enable interface (requires admin)"""
        logger.warning("Interface control requires administrator privileges")
        return False
    
    def disable_interface(self, interface: str) -> bool:
        """Disable interface (requires admin)"""
        logger.warning("Interface control requires administrator privileges")
        return False
    
    @cached(ttl=5)
    def get_network_stats(self) -> Dict[str, Any]:
        """Get comprehensive network statistics"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'interfaces': self.get_network_interfaces(),
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errors_in': net_io.errin,
                'errors_out': net_io.errout
            }
        except Exception as e:
            logger.error(f"Error getting network stats: {e}")
            return {}
    
    # =====================================================================
    # AUDIO DEVICE MANAGEMENT
    # =====================================================================
    
    def list_audio_input_devices(self) -> List[Dict[str, Any]]:
        """List audio input devices"""
        if not PYAUDIO_AVAILABLE:
            return []
        
        devices = []
        try:
            pa = pyaudio.PyAudio()
            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    devices.append({
                        'id': i,
                        'name': info['name'],
                        'channels': info['maxInputChannels'],
                        'sample_rate': int(info['defaultSampleRate']),
                        'latency': info['defaultInputLatency']
                    })
            pa.terminate()
        except Exception as e:
            logger.error(f"Error listing audio input devices: {e}")
        
        return devices
    
    def list_audio_output_devices(self) -> List[Dict[str, Any]]:
        """List audio output devices"""
        if not PYAUDIO_AVAILABLE:
            return []
        
        devices = []
        try:
            pa = pyaudio.PyAudio()
            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                if info['maxOutputChannels'] > 0:
                    devices.append({
                        'id': i,
                        'name': info['name'],
                        'channels': info['maxOutputChannels'],
                        'sample_rate': int(info['defaultSampleRate']),
                        'latency': info['defaultOutputLatency']
                    })
            pa.terminate()
        except Exception as e:
            logger.error(f"Error listing audio output devices: {e}")
        
        return devices
    
    def get_audio_device_info(self, device_id: int, is_input: bool) -> Dict[str, Any]:
        """Get audio device info"""
        if not PYAUDIO_AVAILABLE:
            return {}
        
        try:
            pa = pyaudio.PyAudio()
            info = pa.get_device_info_by_index(device_id)
            pa.terminate()
            return dict(info)
        except Exception as e:
            logger.error(f"Error getting audio device info: {e}")
            return {}
    
    def set_default_audio_input(self, device_id: int) -> bool:
        """Set default input device (requires admin)"""
        logger.warning("Audio device configuration requires administrator privileges")
        return False
    
    def set_default_audio_output(self, device_id: int) -> bool:
        """Set default output device (requires admin)"""
        logger.warning("Audio device configuration requires administrator privileges")
        return False
    
    def get_volume(self, device_id: Optional[int] = None) -> float:
        """Get volume level (0.0-1.0)"""
        logger.warning("Volume control not available on Windows via HAL")
        return 0.5
    
    def set_volume(self, level: float, device_id: Optional[int] = None) -> bool:
        """Set volume level (requires admin)"""
        logger.warning("Volume control requires administrator privileges")
        return False
    
    def get_audio_stats(self) -> Dict[str, Any]:
        """Get audio statistics"""
        return {
            'input_devices': self.list_audio_input_devices(),
            'output_devices': self.list_audio_output_devices()
        }
    
    # =====================================================================
    # POWER MANAGEMENT
    # =====================================================================
    
    def get_battery_info(self) -> Optional[Dict[str, Any]]:
        """Get battery information (laptop only)"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'secsleft': battery.secsleft,
                    'power_plugged': battery.power_plugged
                }
        except Exception as e:
            logger.warning(f"Failed to get battery info: {e}")
        
        return None
    
    def get_power_consumption(self) -> Dict[str, float]:
        """Get power consumption (Windows doesn't provide direct measurement)"""
        return {}
    
    def set_power_profile(self, profile: str) -> bool:
        """Set power profile (requires admin)"""
        logger.warning("Power profile control requires administrator privileges")
        return False
    
    def get_power_stats(self) -> Dict[str, Any]:
        """Get power statistics"""
        return {
            'battery': self.get_battery_info(),
            'power_consumption': self.get_power_consumption()
        }
    
    # =====================================================================
    # TEMPERATURE MONITORING
    # =====================================================================
    
    def get_all_temperatures(self) -> Dict[str, float]:
        """Get all available temperatures"""
        temps = {}
        
        # CPU temperature
        cpu_temp = self.get_cpu_temperature()
        if cpu_temp:
            temps['cpu'] = cpu_temp
        
        return temps
    
    def get_temperature_stats(self) -> Dict[str, Any]:
        """Get temperature statistics"""
        return {'temperatures': self.get_all_temperatures()}
    
    # =====================================================================
    # PROCESS MANAGEMENT
    # =====================================================================
    
    @cached(ttl=5)
    def get_process_list(self) -> List[Dict[str, Any]]:
        """Get list of running processes"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                processes.append({
                    'pid': proc.pid,
                    'name': proc.name(),
                    'status': str(proc.status())
                })
        except Exception as e:
            logger.error(f"Error getting process list: {e}")
        
        return processes
    
    def get_process_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """Get detailed process information"""
        try:
            proc = psutil.Process(pid)
            return {
                'pid': pid,
                'name': proc.name(),
                'status': str(proc.status()),
                'cpu_percent': proc.cpu_percent(),
                'memory_percent': proc.memory_percent(),
                'create_time': proc.create_time()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning(f"Failed to get process info for PID {pid}: {e}")
            return None
    
    def kill_process(self, pid: int, force: bool = False) -> bool:
        """Kill a process"""
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Failed to kill process {pid}: {e}")
            return False
    
    def set_process_priority(self, pid: int, priority: int) -> bool:
        """Set process priority"""
        try:
            proc = psutil.Process(pid)
            proc.nice(priority)
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Failed to set priority for {pid}: {e}")
            return False
    
    # =====================================================================
    # SYSTEM INFO
    # =====================================================================
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            import socket
            return {
                'platform': self.get_platform_name(),
                'system': self.system_name,
                'release': self.release,
                'version': self.version,
                'hostname': socket.gethostname(),
                'processor': platform.processor(),
                'uptime': psutil.boot_time(),
                'cpu_count': self.get_cpu_count(),
                'memory': self.get_memory_info()['total']
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        cpu_usage = self.get_cpu_usage()
        mem_info = self.get_memory_info()
        
        return {
            'cpu_health': self._classify_health(cpu_usage, 80, 90),
            'memory_health': self._classify_health(mem_info['percent'], 80, 90),
            'overall': 'good'
        }
    
    @staticmethod
    def _classify_health(value: float, warning_threshold: float, critical_threshold: float) -> str:
        """Classify health status"""
        if value >= critical_threshold:
            return 'critical'
        elif value >= warning_threshold:
            return 'warning'
        else:
            return 'good'
