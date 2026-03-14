# =========================================================================
# Power Manager - Power and Battery Management
# =========================================================================
"""Power management module"""

import logging
from typing import Dict, Any, Optional
from hardware.hal_decorators import cached

logger = logging.getLogger("KNO.HAL.Power")


class PowerManager:
    """Manage power operations"""
    
    def __init__(self, adapter):
        self.adapter = adapter
        logger.info("✓ Power Manager initialized")
    
    @cached(ttl=10)
    def get_battery_info(self) -> Optional[Dict[str, Any]]:
        """Get battery information"""
        return self.adapter.get_battery_info()
    
    @cached(ttl=15)
    def get_consumption(self) -> Dict[str, float]:
        """Get power consumption"""
        return self.adapter.get_power_consumption()
    
    def set_profile(self, profile: str) -> bool:
        """Set power profile (performance/balanced/powersave)"""
        return self.adapter.set_power_profile(profile)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get power statistics"""
        return self.adapter.get_power_stats()
