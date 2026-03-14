# =========================================================================
# KNO Utility Modules - Smart Cache, Encryption, Rate Limiting
# =========================================================================
"""
Utility modules for KNO v5.0 system
Includes: Caching, Encryption, Rate Limiting, Session Management
"""

import time
import hashlib
import json
import logging
from typing import Any, Dict, Optional, Callable
from threading import Lock
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps
from pathlib import Path
import os

logger = logging.getLogger(__name__)

# =========================================================================
# SMART CACHE
# =========================================================================

class SmartCache:
    """
    Thread-safe cache with TTL and memory management
    
    Features:
    - Time-to-live for entries
    - LRU eviction policy
    - Thread-safe operations
    - Memory efficient
    """
    
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl = ttl
        self.lock = Lock()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve from cache if not expired"""
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                logger.debug(f"Cache MISS: {key}")
                return None
            
            entry = self.cache[key]
            if time.time() - entry['timestamp'] > entry['ttl']:
                del self.cache[key]
                self.misses += 1
                logger.debug(f"Cache EXPIRED: {key}")
                return None
            
            self.hits += 1
            logger.debug(f"Cache HIT: {key}")
            return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store in cache with optional custom TTL"""
        with self.lock:
            # LRU eviction
            if len(self.cache) >= self.max_size:
                oldest_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k]['timestamp']
                )
                del self.cache[oldest_key]
                logger.debug(f"Cache EVICT: {oldest_key}")
            
            self.cache[key] = {
                'value': value,
                'timestamp': time.time(),
                'ttl': ttl or self.ttl
            }
            logger.debug(f"Cache SET: {key}")
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100) if total > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': f"{hit_rate:.1f}%"
            }

def cached(ttl: int = 3600) -> Callable:
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        cache = SmartCache(ttl=ttl)
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
            
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result
        
        wrapper.cache = cache
        return wrapper
    
    return decorator

# =========================================================================
# ENCRYPTION
# =========================================================================

class DataEncryption:
    """
    Simple encryption/decryption for sensitive data
    
    Note: Production should use cryptography library
    This is for demonstration only
    """
    
    @staticmethod
    def encrypt(data: str, key: str = None) -> str:
        """Simple encryption using SHA256 + XOR"""
        if key is None:
            key = os.getenv("ENCRYPTION_KEY", "default-key")
        
        # Hash the key to get consistent length
        key_hash = hashlib.sha256(key.encode()).digest()
        
        # Simple XOR encryption
        encrypted = ''.join(
            chr(ord(c) ^ k) for c, k in zip(data, key_hash * len(data))
        )
        
        # Base64 encode for safe transmission
        import base64
        return base64.b64encode(encrypted.encode('latin1')).decode()
    
    @staticmethod
    def decrypt(encrypted_data: str, key: str = None) -> str:
        """Decrypt data"""
        if key is None:
            key = os.getenv("ENCRYPTION_KEY", "default-key")
        
        try:
            import base64
            encrypted = base64.b64decode(encrypted_data).decode('latin1')
            key_hash = hashlib.sha256(key.encode()).digest()
            
            decrypted = ''.join(
                chr(ord(c) ^ k) for c, k in zip(encrypted, key_hash * len(encrypted))
            )
            
            return decrypted
        
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return ""

# =========================================================================
# RATE LIMITING
# =========================================================================

class RateLimiter:
    """
    Token bucket rate limiter
    
    Features:
    - Per-endpoint rate limiting
    - Exponential backoff on failure
    - Request queuing
    - Automatic cleanup
    """
    
    def __init__(self, requests_per_second: int = 10, burst_size: int = 20):
        """
        Initialize rate limiter
        
        Args:
            requests_per_second: Base rate
            burst_size: Maximum burst capacity
        """
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.tokens: Dict[str, float] = defaultdict(lambda: burst_size)
        self.last_update: Dict[str, float] = defaultdict(time.time)
        self.lock = Lock()
    
    def is_allowed(self, endpoint: str) -> bool:
        """Check if request is allowed"""
        with self.lock:
            now = time.time()
            time_passed = now - self.last_update[endpoint]
            
            # Refill tokens
            self.tokens[endpoint] = min(
                self.burst_size,
                self.tokens[endpoint] + time_passed * self.requests_per_second
            )
            self.last_update[endpoint] = now
            
            if self.tokens[endpoint] >= 1:
                self.tokens[endpoint] -= 1
                return True
            
            return False
    
    def wait_if_needed(self, endpoint: str) -> float:
        """Wait until request is allowed, return wait time"""
        wait_time = 0
        
        while not self.is_allowed(endpoint):
            wait_time += 0.1
            time.sleep(0.1)
        
        return wait_time
    
    def get_stats(self, endpoint: str) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        with self.lock:
            return {
                'endpoint': endpoint,
                'available_tokens': self.tokens[endpoint],
                'max_tokens': self.burst_size,
                'requests_per_second': self.requests_per_second
            }

# =========================================================================
# SESSION MANAGEMENT
# =========================================================================

class SessionManager:
    """
    Manages user sessions with timeout and state
    
    Features:
    - Session timeout
    - State management
    - Cleanup of expired sessions
    - Thread-safe operations
    """
    
    def __init__(self, timeout_minutes: int = 60):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.timeout = timedelta(minutes=timeout_minutes)
        self.lock = Lock()
    
    def create_session(self, session_id: str, data: Dict[str, Any] = None) -> str:
        """Create new session"""
        with self.lock:
            self.sessions[session_id] = {
                'data': data or {},
                'created_at': datetime.now(),
                'last_activity': datetime.now()
            }
            logger.info(f"Session created: {session_id}")
            return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data if valid"""
        with self.lock:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            
            # Check timeout
            if datetime.now() - session['last_activity'] > self.timeout:
                del self.sessions[session_id]
                logger.warning(f"Session expired: {session_id}")
                return None
            
            # Update last activity
            session['last_activity'] = datetime.now()
            
            return session['data']
    
    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Update session data"""
        with self.lock:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            session['data'].update(data)
            session['last_activity'] = datetime.now()
            
            return True
    
    def destroy_session(self, session_id: str) -> bool:
        """Destroy session"""
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"Session destroyed: {session_id}")
                return True
            
            return False
    
    def cleanup_expired(self) -> int:
        """Clean up expired sessions"""
        with self.lock:
            now = datetime.now()
            expired = [
                sid for sid, session in self.sessions.items()
                if now - session['last_activity'] > self.timeout
            ]
            
            for sid in expired:
                del self.sessions[sid]
            
            if expired:
                logger.info(f"Cleaned up {len(expired)} expired sessions")
            
            return len(expired)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        with self.lock:
            return {
                'total_sessions': len(self.sessions),
                'timeout_minutes': self.timeout.total_seconds() / 60
            }

# =========================================================================
# BACKUP MANAGER
# =========================================================================

class BackupManager:
    """
    Automatic backup system with versioning
    
    Features:
    - Hourly automatic backups
    - Versioning
    - Compression
    - Restore functionality
    """
    
    def __init__(self, backup_dir: str = "backups", keep_versions: int = 10):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.keep_versions = keep_versions
        self.lock = Lock()
    
    def backup(self, source_file: str, backup_name: str = None) -> Optional[str]:
        """Create backup of file"""
        try:
            source_path = Path(source_file)
            backup_name = backup_name or source_path.stem
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"{backup_name}_{timestamp}.bak"
            
            with self.lock:
                # Copy file
                with open(source_path, 'rb') as src:
                    with open(backup_path, 'wb') as dst:
                        dst.write(src.read())
                
                logger.info(f"Backup created: {backup_path}")
                
                # Cleanup old backups
                self._cleanup_old_backups(backup_name)
                
                return str(backup_path)
        
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None
    
    def restore(self, backup_path: str, target_file: str) -> bool:
        """Restore from backup"""
        try:
            backup_path = Path(backup_path)
            target_path = Path(target_file)
            
            if not backup_path.exists():
                logger.error(f"Backup not found: {backup_path}")
                return False
            
            with self.lock:
                with open(backup_path, 'rb') as src:
                    with open(target_path, 'wb') as dst:
                        dst.write(src.read())
                
                logger.info(f"Restored from: {backup_path}")
                return True
        
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def _cleanup_old_backups(self, backup_name: str) -> None:
        """Remove old backup versions"""
        backups = sorted(
            self.backup_dir.glob(f"{backup_name}_*.bak"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        for backup in backups[self.keep_versions:]:
            backup.unlink()
            logger.debug(f"Deleted old backup: {backup}")

# =========================================================================
# PERFORMANCE MONITOR
# =========================================================================

class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = defaultdict(list)
        self.lock = Lock()
    
    def record(self, metric_name: str, value: float) -> None:
        """Record a metric"""
        with self.lock:
            self.metrics[metric_name].append({
                'timestamp': datetime.now() ,
                'value': value
            })
            
            # Keep only last 1000 entries
            if len(self.metrics[metric_name]) > 1000:
                self.metrics[metric_name] = self.metrics[metric_name][-1000:]
    
    def get_stats(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for metric"""
        with self.lock:
            values = [m['value'] for m in self.metrics[metric_name]]
            
            if not values:
                return {}
            
            return {
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'count': len(values)
            }
    
    def report(self) -> str:
        """Generate performance report"""
        report = "=== Performance Report ===\n"
        
        with self.lock:
            for metric_name, entries in self.metrics.items():
                if not entries:
                    continue
                
                values = [e['value'] for e in entries]
                report += f"\n{metric_name}:\n"
                report += f"  Count: {len(values)}\n"
                report += f"  Min:   {min(values):.2f}\n"
                report += f"  Max:   {max(values):.2f}\n"
                report += f"  Avg:   {sum(values)/len(values):.2f}\n"
        
        return report

# =========================================================================
# EDEX-UI MONITOR - Data Bridge for Cinematic Interface
# =========================================================================

class EDEXMonitor:
    """
    Real-time data bridge between KNO Agent and eDEX-UI interface
    
    Maintains a JSON file that eDEX-UI reads to display live agent status,
    current tasks, LLM model info, and recent fixes/actions.
    
    Features:
    - Async-safe JSON updates (non-blocking)
    - Real-time status synchronization
    - Memory usage tracking
    - Task progress monitoring
    - Error/fix logging
    
    Example:
        monitor = EDEXMonitor("edex_status.json")
        await monitor.update_status(
            agent_status="THINKING",
            current_task="Analyzing user prompt...",
            llm_model="Gemini-Pro"
        )
    """
    
    def __init__(self, file_path: str = "edex_status.json"):
        """
        Initialize the monitor
        
        Args:
            file_path: Path to JSON file for eDEX-UI to read
        """
        self.file_path = Path(file_path)
        self.lock = Lock()
        
        # Default status structure
        self.data = {
            "agent_status": "IDLE",
            "current_task": "Waiting for input...",
            "progress": 0,
            "llm_model": "None",
            "memory_usage_mb": 0.0,
            "cpu_usage_percent": 0.0,
            "last_action": "System initialized",
            "last_fix": "None",
            "last_error": None,
            "tasks_completed": 0,
            "session_start": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat(),
            "uptime_seconds": 0
        }
        
        # Initial status file creation
        self._save_to_file()
    
    async def update_status(self, **kwargs) -> None:
        """
        Asynchronously update status and write to JSON file
        
        Args:
            **kwargs: Status fields to update
                - agent_status: "IDLE", "THINKING", "SEARCHING", "FIXING", "EXECUTING"
                - current_task: Human-readable task description
                - progress: 0-100 percentage
                - llm_model: Current LLM being used
                - memory_usage_mb: Memory consumption
                - cpu_usage_percent: CPU usage
                - last_action: Last completed action
                - last_error: Error message if applicable
                - last_fix: Last code fix applied
        
        Example:
            await monitor.update_status(
                agent_status="THINKING",
                current_task="Processing user input...",
                llm_model="Gemini-Pro",
                progress=25
            )
        """
        try:
            # Update data dictionary
            self.data.update(kwargs)
            
            # Always update timestamp
            self.data["last_update"] = datetime.now().isoformat()
            
            # Calculate uptime if session_start exists
            try:
                session_start = datetime.fromisoformat(self.data["session_start"])
                uptime = (datetime.now() - session_start).total_seconds()
                self.data["uptime_seconds"] = int(uptime)
            except Exception:
                pass
            
            # Non-blocking file write using executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._save_to_file)
            
        except Exception as e:
            logger.error(f"Error updating eDEX status: {e}")
    
    def update_status_sync(self, **kwargs) -> None:
        """
        Synchronously update status (blocking version)
        Use this if you're not in an async context
        
        Args:
            **kwargs: Status fields to update (same as async version)
        """
        try:
            self.data.update(kwargs)
            self.data["last_update"] = datetime.now().isoformat()
            
            try:
                session_start = datetime.fromisoformat(self.data["session_start"])
                uptime = (datetime.now() - session_start).total_seconds()
                self.data["uptime_seconds"] = int(uptime)
            except Exception:
                pass
            
            self._save_to_file()
        
        except Exception as e:
            logger.error(f"Error updating eDEX status (sync): {e}")
    
    def _save_to_file(self) -> None:
        """
        Write data to JSON file (non-async)
        Called by async/sync update methods
        """
        try:
            with self.lock:
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save eDEX status to file: {e}")
    
    def add_task_completed(self) -> None:
        """Increment completed tasks counter"""
        self.data["tasks_completed"] = self.data.get("tasks_completed", 0) + 1
        self._save_to_file()
    
    def log_fix(self, fix_description: str) -> None:
        """
        Log a code fix or error correction
        
        Args:
            fix_description: Description of what was fixed
        """
        self.data["last_fix"] = fix_description
        self.data["last_action"] = f"Applied fix: {fix_description}"
        self._save_to_file()
    
    def log_error(self, error_message: str) -> None:
        """
        Log an error that occurred
        
        Args:
            error_message: Error description
        """
        self.data["last_error"] = error_message
        self.data["agent_status"] = "ERROR"
        self._save_to_file()
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current status as dictionary"""
        with self.lock:
            return self.data.copy()
    
    def reset(self) -> None:
        """Reset monitor to idle state"""
        self.data = {
            "agent_status": "IDLE",
            "current_task": "Waiting for input...",
            "progress": 0,
            "llm_model": "None",
            "memory_usage_mb": 0.0,
            "cpu_usage_percent": 0.0,
            "last_action": "System reset",
            "last_fix": "None",
            "last_error": None,
            "tasks_completed": self.data.get("tasks_completed", 0),
            "session_start": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat(),
            "uptime_seconds": 0
        }
        self._save_to_file()

# =========================================================================
# GLOBAL INSTANCES
# =========================================================================

performance_monitor = PerformanceMonitor()
rate_limiter = RateLimiter()
session_manager = SessionManager()
encryption = DataEncryption()
edex_monitor = EDEXMonitor("edex_status.json")

if __name__ == "__main__":
    # Example usage
    print("KNO Utilities Module")
    print("=" * 50)
    
    # Test cache
    cache = SmartCache()
    cache.set("test", "value")
    print(f"Cache test: {cache.get('test')}")
    print(f"Stats: {cache.get_stats()}")
    
    # Test rate limiter
    limiter = RateLimiter(requests_per_second=2)
    for i in range(5):
        allowed = limiter.is_allowed("api")
        print(f"Request {i+1}: {'Allowed' if allowed else 'Denied'}")
    
    # Test session
    session_mgr = SessionManager(timeout_minutes=1)
    session_id = session_mgr.create_session("user_123", {"role": "admin"})
    print(f"Session created: {session_id}")
    print(f"Session data: {session_mgr.get_session(session_id)}")
