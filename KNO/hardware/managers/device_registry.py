# =========================================================================
# Device Registry - Device Discovery and Management
# =========================================================================
"""Device discovery and registration module"""

import logging
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger("KNO.HAL.DeviceRegistry")


@dataclass
class Device:
    """Representation of a hardware device"""
    device_id: str
    device_type: str  # 'audio_input', 'audio_output', 'network', 'storage', etc.
    name: str
    details: Dict[str, Any]
    discovered_at: datetime
    last_accessed: datetime = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = datetime.now()


class DeviceRegistry:
    """
    Central registry for hardware devices.
    - Discovers new devices
    - Tracks device lifecycle
    - Handles hot-plugging
    - Provides device event callbacks
    """
    
    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.device_callbacks: Dict[str, List[Callable]] = {
            'on_device_added': [],
            'on_device_removed': [],
            'on_device_updated': []
        }
        logger.info("✓ Device Registry initialized")
    
    def register_device(self, device_id: str, device_type: str, 
                       name: str, details: Dict[str, Any]) -> Device:
        """
        Register a new device.
        
        Args:
            device_id: Unique device identifier
            device_type: Type of device
            name: Human-readable name
            details: Additional device details
            
        Returns:
            Device object
        """
        device = Device(
            device_id=device_id,
            device_type=device_type,
            name=name,
            details=details,
            discovered_at=datetime.now()
        )
        
        is_new = device_id not in self.devices
        self.devices[device_id] = device
        
        if is_new:
            logger.info(f"📱 Device registered: {device_type}/{name} ({device_id})")
            self._trigger_callbacks('on_device_added', device)
        else:
            self._trigger_callbacks('on_device_updated', device)
        
        return device
    
    def unregister_device(self, device_id: str) -> bool:
        """
        Unregister a device.
        
        Args:
            device_id: Device identifier
            
        Returns:
            True if device was unregistered, False if not found
        """
        if device_id in self.devices:
            device = self.devices.pop(device_id)
            logger.info(f"📱 Device unregistered: {device.device_type}/{device.name}")
            self._trigger_callbacks('on_device_removed', device)
            return True
        return False
    
    def get_device(self, device_id: str) -> Device | None:
        """Get device by ID"""
        return self.devices.get(device_id)
    
    def get_devices_by_type(self, device_type: str) -> List[Device]:
        """Get all devices of a specific type"""
        return [d for d in self.devices.values() if d.device_type == device_type]
    
    def get_all_devices(self) -> List[Device]:
        """Get all registered devices"""
        return list(self.devices.values())
    
    def register_callback(self, event: str, callback: Callable):
        """
        Register an event callback.
        
        Args:
            event: Event name ('on_device_added', 'on_device_removed', etc.)
            callback: Callback function(device: Device)
        """
        if event in self.device_callbacks:
            self.device_callbacks[event].append(callback)
            logger.debug(f"Callback registered for {event}")
    
    def _trigger_callbacks(self, event: str, device: Device):
        """Trigger callbacks for an event"""
        for callback in self.device_callbacks.get(event, []):
            try:
                callback(device)
            except Exception as e:
                logger.error(f"Error in callback for {event}: {e}")
    
    def __repr__(self) -> str:
        return f"DeviceRegistry({len(self.devices)} devices)"
