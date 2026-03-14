# =========================================================================
# Hardware Abstraction Layer - Decorators & Utilities
# =========================================================================
"""
Decorators and utilities for HAL operations.
- Retry logic for transient failures
- Caching for expensive operations
- Error handling and logging
- Performance monitoring
"""

import functools
import logging
import time
from typing import Callable, Any, Optional, Type, Tuple
from datetime import datetime, timedelta
import threading

logger = logging.getLogger("KNO.HAL")


# =========================================================================
# RETRY DECORATOR
# =========================================================================

def retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff_multiplier: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts
        delay_seconds: Initial delay between retries (seconds)
        backoff_multiplier: Multiply delay by this after each retry
        exceptions: Tuple of exceptions to catch and retry on
        on_retry: Optional callback function(attempt, delay, exception)
        
    Example:
        @retry(max_attempts=3, delay_seconds=0.5)
        def flaky_operation():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay_seconds
            last_exception = None
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    last_exception = e
                    
                    if attempt < max_attempts:
                        if on_retry:
                            on_retry(attempt, current_delay, e)
                        else:
                            logger.warning(
                                f"⚠️  {func.__name__} failed (attempt {attempt}/{max_attempts}), "
                                f"retrying in {current_delay:.1f}s: {e}"
                            )
                        time.sleep(current_delay)
                        current_delay *= backoff_multiplier
                    else:
                        logger.error(
                            f"❌ {func.__name__} failed after {max_attempts} attempts: {e}"
                        )
            
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


# =========================================================================
# CACHING DECORATOR
# =========================================================================

class CachedValue:
    """Cached value with TTL"""
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.created_at = datetime.now()
        self.ttl = timedelta(seconds=ttl)
    
    def is_expired(self) -> bool:
        return datetime.now() - self.created_at > self.ttl


def cached(ttl: int = 3600, key: Optional[str] = None):
    """
    Cache function results with TTL (Time To Live).
    
    Args:
        ttl: Time to live in seconds (default 1 hour)
        key: Optional custom cache key function
        
    Example:
        @cached(ttl=300)  # Cache for 5 minutes
        def expensive_operation(data):
            ...
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_lock = threading.Lock()
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key:
                cache_key = key(args, kwargs)
            else:
                cache_key = (func.__name__, args, tuple(sorted(kwargs.items())))
            
            with cache_lock:
                # Check cache
                if cache_key in cache:
                    cached_val = cache[cache_key]
                    if not cached_val.is_expired():
                        logger.debug(f"✓ Cache hit: {func.__name__}")
                        return cached_val.value
                    else:
                        del cache[cache_key]
                
                # Cache miss - call function
                result = func(*args, **kwargs)
                cache[cache_key] = CachedValue(result, ttl)
                return result
        
        # Add cache management methods
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_size = lambda: len(cache)
        wrapper.get_cache = lambda: cache.copy()
        
        return wrapper
    
    return decorator


# =========================================================================
# PERFORMANCE MONITOR DECORATOR
# =========================================================================

def monitor_performance(log_threshold_ms: float = 100.0):
    """
    Monitor function execution time and log if it exceeds threshold.
    
    Args:
        log_threshold_ms: Log if execution time exceeds this (milliseconds)
        
    Example:
        @monitor_performance(log_threshold_ms=50)
        def critical_operation():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                if elapsed_ms > log_threshold_ms:
                    logger.warning(
                        f"⏱️  {func.__name__} took {elapsed_ms:.2f}ms "
                        f"(threshold: {log_threshold_ms}ms)"
                    )
        
        return wrapper
    
    return decorator


# =========================================================================
# REQUIRE PLATFORM DECORATOR
# =========================================================================

def requires_platform(*platforms: str):
    """
    Ensure function only runs on specified platform(s).
    
    Args:
        *platforms: Platform names ('linux', 'windows', 'macos', 'raspi')
        
    Example:
        @requires_platform('linux', 'raspi')
        def linux_only_operation():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from hardware.adapters.base_adapter import get_current_platform
            current = get_current_platform()
            
            if current not in platforms:
                raise PlatformNotSupportedException(
                    func.__name__, current
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


# =========================================================================
# UTILITY FUNCTIONS
# =========================================================================

def safe_get(obj: dict, key: str, default: Any = None) -> Any:
    """Safely get dictionary value"""
    try:
        return obj.get(key, default)
    except (AttributeError, TypeError):
        return default


def format_bytes(bytes_val: int) -> str:
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"


def format_duration(seconds: float) -> str:
    """Convert seconds to human-readable duration"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def percentage_bar(value: float, width: int = 20) -> str:
    """Create a text-based percentage bar"""
    filled = int(width * value / 100)
    empty = width - filled
    return f"[{'█' * filled}{'░' * empty}] {value:.1f}%"


def try_import(module_name: str, alternative_message: str = None) -> Optional[Any]:
    """Safely import module and log if not available"""
    try:
        return __import__(module_name)
    except ImportError:
        msg = f"⚠️  Module '{module_name}' not available"
        if alternative_message:
            msg += f". {alternative_message}"
        logger.warning(msg)
        return None


# =========================================================================
# CONTEXT MANAGERS
# =========================================================================

class SuppressExceptions:
    """Context manager to suppress specified exceptions"""
    def __init__(self, *exceptions: Type[Exception], default_return: Any = None):
        self.exceptions = exceptions
        self.default_return = default_return
        self.exception_caught = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and issubclass(exc_type, self.exceptions):
            self.exception_caught = exc_val
            return True  # Suppress the exception
        return False


class PerformanceTimer:
    """Context manager for timing operations"""
    def __init__(self, name: str = "Operation", log_func=None):
        self.name = name
        self.log_func = log_func or logger.info
        self.start_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self.start_time
        self.log_func(f"⏱️  {self.name} completed in {self.elapsed*1000:.2f}ms")
        return False


# =========================================================================
# IMPORT GUARD
# =========================================================================

# Import after defining utils to avoid circular imports
from hardware.hal_exceptions import PlatformNotSupportedException
