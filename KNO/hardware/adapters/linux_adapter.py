# =========================================================================
# Hardware Abstraction Layer - Linux Adapter
# =========================================================================
"""
Platform adapter for Linux (Ubuntu, Debian, Fedora, etc.).
Uses psutil, netifaces, and /proc filesystem for hardware access.
"""

import logging
import platform
import socket
from typing import Dict, Any, Optional, List
import psutil
import os

logger = logging.getLogger("KNO.HAL.Linux")

try:
    import netifaces
    NETIFACES_AVAILABLE = True
except ImportError:
    NETIFACES_AVAILABLE = False
    logger.warning("netifaces not available - network features limited")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.warning("PyAudio not available - audio features limited")

try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False
    logger.warning("GPUtil not available - GPU features limited")

from hardware.adapters.base_adapter import BaseAdapter
from hardware.hal_decorators import retry, cached


class LinuxAdapter(BaseAdapter):
    """Linux hardware access adapter"""
    
    def get_platform_name(self) -> str:
        return "linux"
    
    def _initialize(self):
        """Initialize Linux adapter"""
        self.distro_name = self._get_distro_name()
        logger.info(f"Initializing Linux adapter on {self.distro_name}")
    
    @staticmethod
    def _get_distro_name() -> str:
        """Get Linux distribution name"""
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME'):
                        return line.split('=')[1].strip().strip('"')
        except FileNotFoundError:
            pass
        
        try:
            return platform.linux_distribution()[0]
        except AttributeError:
            return platform.system()
    
    # =====================================================================
    # CPU MANAGEMENT
    # =====================================================================
    
    def get_cpu_count(self) -> int:
        """Get number of CPU cores (physical)"""
        return psutil.cpu_count(logical=False) or psutil.cpu_count()
    
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
        """Get CPU temperature from /sys or psutil"""
        try:
            # Try psutil first
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if 'coretemp' in name or 'k10temp' in name or 'cpu' in name.lower():
                        for entry in entries:
                            return entry.current
        except Exception as e:
            logger.warning(f"Failed to get CPU temperature: {e}")
        
        # Fallback to /sys/class/thermal
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp_millidegrees = int(f.read().strip())
                return temp_millidegrees / 1000.0
        except FileNotFoundError:
            pass
        
        return None
    
    def set_cpu_frequency(self, core_id: int, frequency_mhz: int) -> bool:
        """
        Set CPU frequency (requires root and cpufreq driver).
        Uses scaling_setspeed in /sys/devices/system/cpu/
        """
        try:
            path = f"/sys/devices/system/cpu/cpu{core_id}/cpufreq/scaling_setspeed"
            if not os.path.exists(path):
                logger.warning(f"CPU frequency control not available for core {core_id}")
                return False
            
            with open(path, 'w') as f:
                f.write(str(frequency_mhz))
            return True
        except PermissionError:
            logger.error("Setting CPU frequency requires root privileges")
            return False
        except Exception as e:
            logger.error(f"Failed to set CPU frequency: {e}")
            return False
    
    def get_cpu_stats(self) -> Dict[str, Any]:
        """Get comprehensive CPU statistics"""
        try:
            load_avg = os.getloadavg()
        except AttributeError:
            load_avg = None
        
        return {
            'cpu_count': self.get_cpu_count(),
            'cpu_count_logical': psutil.cpu_count(),
            'frequency': self.get_cpu_frequency(),
            'usage': self.get_cpu_usage(),
            'per_core_usage': self.get_cpu_usage(per_core=True),
            'temperature': self.get_cpu_temperature(),
            'load_average': load_avg,
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
            'percent': mem.percent,
            'free': mem.free,
            'buffers': mem.buffers,
            'cached': mem.cached
        }
    
    @cached(ttl=2)
    def get_swap_info(self) -> Dict[str, int]:
        """Get swap memory information"""
        swap = psutil.swap_memory()
        return {
            'total': swap.total,
            'used': swap.used,
            'free': swap.free,
            'percent': swap.percent,
            'sin': swap.sin,
            'sout': swap.sout
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
            'swap': self.get_swap_info()
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
        """Mount a filesystem (requires root)"""
        try:
            os.system(f"mount {device} {mountpoint}")
            return True
        except Exception as e:
            logger.error(f"Failed to mount {device}: {e}")
            return False
    
    def unmount_volume(self, mountpoint: str) -> bool:
        """Unmount a filesystem (requires root)"""
        try:
            os.system(f"umount {mountpoint}")
            return True
        except Exception as e:
            logger.error(f"Failed to unmount {mountpoint}: {e}")
            return False
    
    def get_disk_stats(self) -> Dict[str, Any]:
        """Get comprehensive disk statistics"""
        return {
            'disks': self.get_disk_info(),
            'usage': {disk['device']: self.get_disk_usage(disk['mountpoint']) 
                     for disk in self.get_disk_info() if os.path.exists(disk['mountpoint'])},
            'io': self.get_disk_io_stats()
        }
    
    # =====================================================================
    # NETWORK MANAGEMENT
    # =====================================================================
    
    @cached(ttl=10)
    def get_network_interfaces(self) -> Dict[str, Dict[str, Any]]:
        """Get network interfaces"""
        interfaces = {}
        
        if NETIFACES_AVAILABLE:
            try:
                for interface_name in netifaces.interfaces():
                    interfaces[interface_name] = {
                        'ip': None,
                        'mac': None,
                        'addresses': []
                    }
                    
                    for addr_family, addresses in netifaces.ifaddresses(interface_name).items():
                        for addr in addresses:
                            interfaces[interface_name]['addresses'].append({
                                'family': str(addr_family),
                                'address': addr.get('addr', ''),
                                'netmask': addr.get('netmask', '')
                            })
                            
                            # Extract IP and MAC
                            if addr_family == 2:  # AF_INET
                                interfaces[interface_name]['ip'] = addr.get('addr')
                            elif addr_family == 17:  # AF_LINK
                                interfaces[interface_name]['mac'] = addr.get('addr')
            except Exception as e:
                logger.error(f"Error getting network interfaces: {e}")
        else:
            # Fallback using psutil
            for interface_name, interface_addrs in psutil.net_if_addrs().items():
                interfaces[interface_name] = {
                    'ip': None,
                    'mac': None,
                    'addresses': []
                }
                
                for addr in interface_addrs:
                    if addr.family == 2:  # AF_INET
                        interfaces[interface_name]['ip'] = addr.address
                    elif addr.family == 17:  # AF_LINK
                        interfaces[interface_name]['mac'] = addr.address
        
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
        """Enable network interface (requires root)"""
        try:
            os.system(f"ip link set {interface} up")
            return True
        except Exception as e:
            logger.error(f"Failed to enable interface {interface}: {e}")
            return False
    
    def disable_interface(self, interface: str) -> bool:
        """Disable network interface (requires root)"""
        try:
            os.system(f"ip link set {interface} down")
            return True
        except Exception as e:
            logger.error(f"Failed to disable interface {interface}: {e}")
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
                'errors_out': net_io.errout,
                'dropped_in': net_io.dropin,
                'dropped_out': net_io.dropout
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
        """Set default input device (requires alsamixer)"""
        logger.warning("Audio device configuration on Linux is complex")
        return False
    
    def set_default_audio_output(self, device_id: int) -> bool:
        """Set default output device"""
        logger.warning("Audio device configuration on Linux is complex")
        return False
    
    def get_volume(self, device_id: Optional[int] = None) -> float:
        """Get volume level (0.0-1.0) using alsamixer"""
        try:
            # This is a simplified version; real implementation would use alsaaudio
            result = os.popen("amixer get Master | grep -oP '\\d+(?=%)'").read()
            if result:
                return float(result.strip()) / 100.0
        except Exception as e:
            logger.warning(f"Failed to get volume: {e}")
        
        return 0.5
    
    def set_volume(self, level: float, device_id: Optional[int] = None) -> bool:
        """Set volume level (0.0-1.0)"""
        try:
            percent = int(level * 100)
            os.system(f"amixer set Master {percent}%")
            return True
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            return False
    
    def get_audio_stats(self) -> Dict[str, Any]:
        """Get audio statistics"""
        return {
            'input_devices': self.list_audio_input_devices(),
            'output_devices': self.list_audio_output_devices(),
            'volume': self.get_volume()
        }
    
    # =====================================================================
    # POWER MANAGEMENT
    # =====================================================================
    
    def get_battery_info(self) -> Optional[Dict[str, Any]]:
        """Get battery information"""
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
        """Get power consumption from /sys if available"""
        power_stats = {}
        
        try:
            # CPU power
            with open('/sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference', 'r') as f:
                power_stats['cpu_epp'] = f.read().strip()
        except FileNotFoundError:
            pass
        
        return power_stats
    
    def set_power_profile(self, profile: str) -> bool:
        """Set power profile (requires root and cpupower)"""
        profiles = {
            'performance': 'performance',
            'balanced': 'schedutil',
            'powersave': 'powersave'
        }
        
        governor = profiles.get(profile, 'schedutil')
        try:
            os.system(f"echo {governor} | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor")
            return True
        except Exception as e:
            logger.error(f"Failed to set power profile: {e}")
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
        
        # GPU temperature (if available)
        if GPUTIL_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                for i, gpu in enumerate(gpus):
                    temps[f'gpu{i}'] = gpu.temperature
            except Exception as e:
                logger.warning(f"Failed to get GPU temperature: {e}")
        
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
                'create_time': proc.create_time(),
                'num_threads': proc.num_threads()
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
        """Set process priority (-20 to 19)"""
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
            return {
                'platform': self.get_platform_name(),
                'distro': self.distro_name,
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
        disk_info = self.get_disk_usage('/')
        
        return {
            'cpu_health': self._classify_health(cpu_usage, 80, 90),
            'memory_health': self._classify_health(mem_info['percent'], 80, 90),
            'disk_health': self._classify_health(disk_info['percent'], 85, 95),
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
