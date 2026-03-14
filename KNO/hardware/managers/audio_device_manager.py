# =========================================================================
# Audio Device Manager - Audio Device Management
# =========================================================================
"""Audio device management module"""

import logging
from typing import Dict, Any, List, Optional
from hardware.hal_decorators import cached

logger = logging.getLogger("KNO.HAL.Audio")


class AudioDeviceManager:
    """Manage audio device operations"""
    
    def __init__(self, adapter):
        self.adapter = adapter
        logger.info("✓ Audio Device Manager initialized")
    
    @cached(ttl=30)
    def list_input_devices(self) -> List[Dict[str, Any]]:
        """List input devices (microphones)"""
        return self.adapter.list_audio_input_devices()
    
    @cached(ttl=30)
    def list_output_devices(self) -> List[Dict[str, Any]]:
        """List output devices (speakers)"""
        return self.adapter.list_audio_output_devices()
    
    def get_device_info(self, device_id: int, is_input: bool) -> Dict[str, Any]:
        """Get audio device info"""
        return self.adapter.get_audio_device_info(device_id, is_input)
    
    def set_default_input(self, device_id: int) -> bool:
        """Set default input device"""
        return self.adapter.set_default_audio_input(device_id)
    
    def set_default_output(self, device_id: int) -> bool:
        """Set default output device"""
        return self.adapter.set_default_audio_output(device_id)
    
    def get_volume(self, device_id: Optional[int] = None) -> float:
        """Get volume level (0.0-1.0)"""
        return self.adapter.get_volume(device_id)
    
    def set_volume(self, level: float, device_id: Optional[int] = None) -> bool:
        """Set volume level (0.0-1.0)"""
        return self.adapter.set_volume(level, device_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get audio statistics"""
        return self.adapter.get_audio_stats()
