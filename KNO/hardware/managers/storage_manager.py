# =========================================================================
# Storage Manager - Disk I/O and Storage Management
# =========================================================================
"""Storage management module"""

import logging
from typing import Dict, Any, List
from hardware.hal_decorators import cached, monitor_performance

logger = logging.getLogger("KNO.HAL.Storage")


class StorageManager:
    """Manage storage operations"""
    
    def __init__(self, adapter):
        self.adapter = adapter
        logger.info("✓ Storage Manager initialized")
    
    def get_disk_info(self) -> List[Dict[str, Any]]:
        """Get list of all disks"""
        return self.adapter.get_disk_info()
    
    @cached(ttl=10)
    def get_disk_usage(self, path: str) -> Dict[str, Any]:
        """Get disk usage for a path"""
        return self.adapter.get_disk_usage(path)
    
    def get_root_usage(self) -> Dict[str, Any]:
        """Get root filesystem usage"""
        return self.get_disk_usage('/')
    
    @cached(ttl=5)
    def get_io_stats(self) -> Dict[str, Any]:
        """Get disk I/O statistics"""
        return self.adapter.get_disk_io_stats()
    
    def mount_volume(self, device: str, mountpoint: str) -> bool:
        """Mount a volume"""
        return self.adapter.mount_volume(device, mountpoint)
    
    def unmount_volume(self, mountpoint: str) -> bool:
        """Unmount a volume"""
        return self.adapter.unmount_volume(mountpoint)
    
    @monitor_performance(log_threshold_ms=500)
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive disk statistics"""
        return self.adapter.get_disk_stats()
