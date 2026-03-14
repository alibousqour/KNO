# =========================================================================
# Temperature Monitor - Thermal Management
# =========================================================================
"""Temperature monitoring module"""

import logging
from typing import Dict, Any, Optional
from hardware.hal_decorators import cached
from hardware.hal_exceptions import ThermalThrottlingException

logger = logging.getLogger("KNO.HAL.Temperature")


class TemperatureMonitor:
    """Monitor system temperatures"""
    
    CRITICAL_TEMP = 95.0
    WARNING_TEMP = 80.0
    
    def __init__(self, adapter):
        self.adapter = adapter
        logger.info("✓ Temperature Monitor initialized")
    
    @cached(ttl=5)
    def get_all_temperatures(self) -> Dict[str, float]:
        """Get all available temperatures"""
        return self.adapter.get_all_temperatures()
    
    def get_max_temperature(self) -> float:
        """Get maximum temperature across all sensors"""
        temps = self.get_all_temperatures()
        return max(temps.values(), default=0.0)
    
    def is_critical(self) -> bool:
        """Check if temperature is critical"""
        return self.get_max_temperature() > self.CRITICAL_TEMP
    
    def is_warning(self) -> bool:
        """Check if temperature is in warning range"""
        max_temp = self.get_max_temperature()
        return self.WARNING_TEMP < max_temp <= self.CRITICAL_TEMP
    
    def check_thermal_health(self) -> str:
        """
        Check thermal health status.
        Returns: 'good', 'warning', or 'critical'
        """
        max_temp = self.get_max_temperature()
        if max_temp >= self.CRITICAL_TEMP:
            return 'critical'
        elif max_temp >= self.WARNING_TEMP:
            return 'warning'
        else:
            return 'good'
    
    def get_stats(self) -> Dict[str, Any]:
        """Get temperature statistics"""
        return self.adapter.get_temperature_stats()
