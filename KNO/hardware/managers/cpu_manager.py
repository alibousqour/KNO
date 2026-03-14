# =========================================================================
# CPU Manager - CPU and Process Management
# =========================================================================
"""CPU and process management module"""

import logging
from typing import Dict, Any, Optional, List
from hardware.hal_decorators import cached, monitor_performance

logger = logging.getLogger("KNO.HAL.CPU")


class CPUManager:
    """Manage CPU operations and process management"""
    
    def __init__(self, adapter):
        self.adapter = adapter
        logger.info("✓ CPU Manager initialized")
    
    def get_count(self) -> int:
        """Get number of CPU cores"""
        return self.adapter.get_cpu_count()
    
    @cached(ttl=5)
    def get_frequency(self) -> Dict[str, float]:
        """Get CPU frequency info (MHz)"""
        return self.adapter.get_cpu_frequency()
    
    @cached(ttl=2)
    def get_usage(self, per_core: bool = False) -> dict | float:
        """Get CPU usage percentage"""
        return self.adapter.get_cpu_usage(per_core=per_core)
    
    def get_temperature(self) -> Optional[float]:
        """Get CPU temperature in Celsius"""
        return self.adapter.get_cpu_temperature()
    
    def set_frequency(self, core_id: int, frequency_mhz: int) -> bool:
        """Set CPU frequency for a core"""
        return self.adapter.set_cpu_frequency(core_id, frequency_mhz)
    
    @monitor_performance(log_threshold_ms=500)
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive CPU statistics"""
        return self.adapter.get_cpu_stats()
    
    def get_top_processes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top CPU-consuming processes"""
        import psutil
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    processes.append({
                        'pid': proc.pid,
                        'name': proc.name(),
                        'cpu_percent': proc.cpu_percent()
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            logger.error(f"Error getting process list: {e}")
        
        # Sort by CPU usage and return top N
        return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
