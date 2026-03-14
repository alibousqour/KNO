# =========================================================================
# Network Manager - Network Interface Management
# =========================================================================
"""Network management module"""

import logging
from typing import Dict, Any
from hardware.hal_decorators import cached, monitor_performance

logger = logging.getLogger("KNO.HAL.Network")


class NetworkManager:
    """Manage network operations"""
    
    def __init__(self, adapter):
        self.adapter = adapter
        logger.info("✓ Network Manager initialized")
    
    @cached(ttl=10)
    def get_interfaces(self) -> Dict[str, Dict[str, Any]]:
        """Get network interfaces"""
        return self.adapter.get_network_interfaces()
    
    @cached(ttl=5)
    def get_interface_stats(self, interface: str) -> Dict[str, Any]:
        """Get interface statistics"""
        return self.adapter.get_interface_stats(interface)
    
    def get_ip_address(self, interface: str) -> str | None:
        """Get IP address"""
        return self.adapter.get_ip_address(interface)
    
    def get_mac_address(self, interface: str) -> str | None:
        """Get MAC address"""
        return self.adapter.get_mac_address(interface)
    
    def enable_interface(self, interface: str) -> bool:
        """Enable interface"""
        return self.adapter.enable_interface(interface)
    
    def disable_interface(self, interface: str) -> bool:
        """Disable interface"""
        return self.adapter.disable_interface(interface)
    
    def get_bandwidth_usage(self) -> Dict[str, Any]:
        """Get bandwidth usage"""
        stats = self.adapter.get_network_stats()
        return {
            'bytes_sent': stats.get('bytes_sent', 0),
            'bytes_recv': stats.get('bytes_recv', 0),
            'packets_sent': stats.get('packets_sent', 0),
            'packets_recv': stats.get('packets_recv', 0)
        }
    
    @monitor_performance(log_threshold_ms=300)
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive network statistics"""
        return self.adapter.get_network_stats()
