# =========================================================================
# hardware/adapters/__init__.py
# =========================================================================
"""Platform adapters for HAL"""

from .base_adapter import BaseAdapter, get_current_platform

__all__ = ['BaseAdapter', 'get_current_platform', 'get_adapter']


def get_adapter(platform_name: str = None) -> BaseAdapter:
    """
    Get the appropriate adapter for the current platform.
    
    Args:
        platform_name: Optional platform name. If not provided, auto-detected.
        
    Returns:
        Initialized adapter for the platform
        
    Raises:
        RuntimeError: If adapter cannot be initialized
    """
    if platform_name is None:
        platform_name = get_current_platform()
    
    platform_name = platform_name.lower()
    
    if platform_name in ('windows', 'w32'):
        from .windows_adapter import WindowsAdapter
        return WindowsAdapter()
    
    elif platform_name in ('linux', 'raspi'):
        from .linux_adapter import LinuxAdapter
        return LinuxAdapter()
    
    elif platform_name == 'macos':
        # macOS adapter (future implementation)
        from .linux_adapter import LinuxAdapter  # Fallback to Linux for now
        return LinuxAdapter()
    
    else:
        raise RuntimeError(f"Unsupported platform: {platform_name}")
