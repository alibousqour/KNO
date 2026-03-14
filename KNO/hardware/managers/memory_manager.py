# =========================================================================
# Memory Manager - RAM and Swap Memory Management
# =========================================================================
"""Memory management module"""

import logging
from typing import Dict, Any, Optional
from hardware.hal_decorators import cached, monitor_performance

logger = logging.getLogger("KNO.HAL.Memory")


class MemoryManager:
    """Manage memory operations"""
    
    def __init__(self, adapter):
        self.adapter = adapter
        logger.info("✓ Memory Manager initialized")
    
    @cached(ttl=2)
    def get_info(self) -> Dict[str, int]:
        """Get memory information"""
        return self.adapter.get_memory_info()
    
    def get_usage(self) -> float:
        """Get memory usage percentage"""
        info = self.get_info()
        return info.get('percent', 0)
    
    @cached(ttl=2)
    def get_swap_info(self) -> Dict[str, int]:
        """Get swap memory information"""
        return self.adapter.get_swap_info()
    
    def get_swap_usage(self) -> float:
        """Get swap usage percentage"""
        info = self.get_swap_info()
        return info.get('percent', 0)
    
    def get_by_process(self, pid: int) -> Dict[str, int]:
        """Get memory usage for a process"""
        return self.adapter.get_memory_by_process(pid)
    
    @monitor_performance(log_threshold_ms=300)
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        return self.adapter.get_memory_stats()
