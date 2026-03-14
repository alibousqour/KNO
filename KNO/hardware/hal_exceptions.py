# =========================================================================
# Hardware Abstraction Layer - Custom Exceptions
# =========================================================================
"""
Custom exception classes for HAL operations.
Provides hierarchical exception handling with context information.
"""

class HALException(Exception):
    """Base exception for all HAL operations"""
    pass


class PlatformNotSupportedException(HALException):
    """Raised when operation is not supported on current platform"""
    def __init__(self, operation: str, platform: str = None):
        self.operation = operation
        self.platform = platform
        super().__init__(
            f"Operation '{operation}' not supported"
            f"{f' on {platform}' if platform else ''}"
        )


class HardwareNotFoundException(HALException):
    """Raised when requested hardware device is not found"""
    def __init__(self, device_type: str, device_id: str = None):
        self.device_type = device_type
        self.device_id = device_id
        super().__init__(
            f"{device_type} device not found"
            f"{f': {device_id}' if device_id else ''}"
        )


class HardwareAccessDeniedException(HALException):
    """Raised when access to hardware is denied (permission issue)"""
    def __init__(self, device: str, reason: str = None):
        self.device = device
        self.reason = reason
        super().__init__(
            f"Access denied to {device}"
            f"{f': {reason}' if reason else ''}"
        )


class DeviceNotReadyException(HALException):
    """Raised when device is not ready"""
    def __init__(self, device: str, reason: str = None):
        self.device = device
        self.reason = reason
        super().__init__(
            f"Device '{device}' is not ready"
            f"{f': {reason}' if reason else ''}"
        )


class ResourceExhaustedException(HALException):
    """Raised when system resources are exhausted"""
    def __init__(self, resource_type: str, required: int, available: int):
        self.resource_type = resource_type
        self.required = required
        self.available = available
        super().__init__(
            f"{resource_type} exhausted: required {required}, "
            f"available {available}"
        )


class ThermalThrottlingException(HALException):
    """Raised when system is thermal throttling"""
    def __init__(self, temperature: float, threshold: float):
        self.temperature = temperature
        self.threshold = threshold
        super().__init__(
            f"Thermal throttling: {temperature}°C > {threshold}°C"
        )


class CPUManagerException(HALException):
    """CPU management specific exception"""
    pass


class MemoryManagerException(HALException):
    """Memory management specific exception"""
    pass


class StorageManagerException(HALException):
    """Storage management specific exception"""
    pass


class NetworkManagerException(HALException):
    """Network management specific exception"""
    pass


class AudioManagerException(HALException):
    """Audio device management specific exception"""
    pass


class PowerManagerException(HALException):
    """Power management specific exception"""
    pass


class TemperatureException(HALException):
    """Temperature monitoring specific exception"""
    pass


class AdapterInitializationException(HALException):
    """Raised when platform adapter fails to initialize"""
    def __init__(self, adapter_name: str, reason: str):
        self.adapter_name = adapter_name
        self.reason = reason
        super().__init__(
            f"Failed to initialize {adapter_name} adapter: {reason}"
        )
