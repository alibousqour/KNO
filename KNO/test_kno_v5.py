# =========================================================================
# KNO Test Suite - Comprehensive Testing for v5.0
# =========================================================================
"""
Comprehensive test suite for KNO v5.0 system
Tests cover: caching, rate limiting, configuration, security, audio
Run with: pytest test_kno_v5.py -v
"""

import pytest
import time
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import modules to test
try:
    from kno_utils import (
        SmartCache, cached, RateLimiter, SessionManager,
        BackupManager, PerformanceMonitor, DataEncryption
    )
    from kno_config_v5 import (
        ConfigManager, APIConfig, AudioConfig, UIConfig,
        LoggingConfig, CacheConfig, SecurityConfig, PerformanceConfig
    )
except ImportError as e:
    print(f"Warning: Could not import test modules: {e}")

# =========================================================================
# CACHE TESTS
# =========================================================================

class TestSmartCache:
    """Test SmartCache functionality"""
    
    def test_cache_set_get(self):
        """Test basic cache operations"""
        cache = SmartCache(max_size=10, ttl=100)
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
    
    def test_cache_miss(self):
        """Test cache miss"""
        cache = SmartCache()
        
        assert cache.get("nonexistent") is None
    
    def test_cache_expiration(self):
        """Test cache TTL expiration"""
        cache = SmartCache(ttl=1)
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        time.sleep(1.1)
        assert cache.get("key1") is None
    
    def test_cache_max_size(self):
        """Test LRU eviction"""
        cache = SmartCache(max_size=2)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # key1 should be evicted
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
    
    def test_cache_stats(self):
        """Test cache statistics"""
        cache = SmartCache()
        
        cache.set("key", "value")
        cache.get("key")  # hit
        cache.get("nonexistent")  # miss
        
        stats = cache.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['size'] == 1
    
    def test_cache_clear(self):
        """Test cache clearing"""
        cache = SmartCache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None

class TestCachedDecorator:
    """Test @cached decorator"""
    
    def test_decorator_caching(self):
        """Test function result caching"""
        call_count = 0
        
        @cached(ttl=100)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = expensive_function(5)
        result2 = expensive_function(5)
        
        assert result1 == 10
        assert result2 == 10
        assert call_count == 1  # Should only be called once

# =========================================================================
# RATE LIMITING TESTS
# =========================================================================

class TestRateLimiter:
    """Test RateLimiter functionality"""
    
    def test_rate_limiter_allow(self):
        """Test rate limiter allows requests"""
        limiter = RateLimiter(requests_per_second=2, burst_size=2)
        
        # Should allow up to burst size
        assert limiter.is_allowed("endpoint") is True
        assert limiter.is_allowed("endpoint") is True
    
    def test_rate_limiter_deny(self):
        """Test rate limiter denies requests after limit"""
        limiter = RateLimiter(requests_per_second=1, burst_size=1)
        
        assert limiter.is_allowed("endpoint") is True
        assert limiter.is_allowed("endpoint") is False
    
    def test_rate_limiter_stats(self):
        """Test rate limiter statistics"""
        limiter = RateLimiter(requests_per_second=10, burst_size=20)
        
        stats = limiter.get_stats("endpoint")
        assert stats['available_tokens'] > 0
        assert stats['max_tokens'] == 20
        assert stats['requests_per_second'] == 10

# =========================================================================
# SESSION MANAGEMENT TESTS
# =========================================================================

class TestSessionManager:
    """Test SessionManager functionality"""
    
    def test_create_session(self):
        """Test session creation"""
        manager = SessionManager()
        
        session_id = manager.create_session("user1", {"role": "admin"})
        assert session_id == "user1"
    
    def test_get_valid_session(self):
        """Test retrieving valid session"""
        manager = SessionManager(timeout_minutes=60)
        
        manager.create_session("user1", {"role": "admin"})
        session_data = manager.get_session("user1")
        
        assert session_data == {"role": "admin"}
    
    def test_session_timeout(self):
        """Test session expiration"""
        manager = SessionManager(timeout_minutes=0)  # Immediate timeout
        
        manager.create_session("user1", {"role": "admin"})
        time.sleep(0.1)
        
        session_data = manager.get_session("user1")
        assert session_data is None
    
    def test_session_update(self):
        """Test session data update"""
        manager = SessionManager()
        
        manager.create_session("user1", {"role": "user"})
        manager.update_session("user1", {"role": "admin"})
        
        session_data = manager.get_session("user1")
        assert session_data["role"] == "admin"
    
    def test_destroy_session(self):
        """Test session destruction"""
        manager = SessionManager()
        
        manager.create_session("user1", {"role": "admin"})
        assert manager.destroy_session("user1") is True
        assert manager.get_session("user1") is None
    
    def test_cleanup_expired(self):
        """Test cleanup of expired sessions"""
        manager = SessionManager(timeout_minutes=0)
        
        manager.create_session("user1", {"data": "value"})
        time.sleep(0.1)
        
        cleaned = manager.cleanup_expired()
        assert cleaned == 1

# =========================================================================
# BACKUP MANAGER TESTS
# =========================================================================

class TestBackupManager:
    """Test BackupManager functionality"""
    
    def test_backup_creation(self):
        """Test backup file creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source file
            source_file = Path(tmpdir) / "source.txt"
            source_file.write_text("test data")
            
            # Create backup
            manager = BackupManager(backup_dir=Path(tmpdir) / "backups")
            backup_path = manager.backup(str(source_file))
            
            assert backup_path is not None
            assert Path(backup_path).exists()
    
    def test_restore_backup(self):
        """Test backup restoration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and backup file
            source_file = Path(tmpdir) / "source.txt"
            source_file.write_text("original data")
            
            manager = BackupManager(backup_dir=Path(tmpdir) / "backups")
            backup_path = manager.backup(str(source_file))
            
            # Modify original
            source_file.write_text("modified data")
            
            # Restore
            assert manager.restore(backup_path, str(source_file)) is True
            assert source_file.read_text() == "original data"

# =========================================================================
# CONFIGURATION TESTS
# =========================================================================

class TestAPIConfig:
    """Test APIConfig validation"""
    
    def test_api_config_valid(self):
        """Test valid API configuration"""
        config = APIConfig(gemini_key="test_key")
        assert config.validate() is True
    
    def test_api_config_invalid(self):
        """Test invalid API configuration"""
        config = APIConfig()
        assert config.validate() is False

class TestAudioConfig:
    """Test AudioConfig validation"""
    
    def test_audio_config_valid(self):
        """Test valid audio configuration"""
        config = AudioConfig()
        assert config.validate() is True
    
    def test_audio_config_invalid_sample_rate(self):
        """Test invalid sample rate"""
        config = AudioConfig(sample_rate=100)
        assert config.validate() is False
    
    def test_audio_config_invalid_duration(self):
        """Test invalid max duration"""
        config = AudioConfig(max_duration=5)
        assert config.validate() is False

class TestConfigManager:
    """Test ConfigManager"""
    
    def test_config_manager_init(self):
        """Test configuration manager initialization"""
        manager = ConfigManager()
        
        assert manager.api is not None
        assert manager.audio is not None
        assert manager.ui is not None
    
    def test_config_validation(self):
        """Test configuration validation"""
        with patch.object(APIConfig, 'validate', return_value=True):
            with patch.object(AudioConfig, 'validate', return_value=True):
                manager = ConfigManager()
                # Should complete without error
                assert manager.api is not None
    
    def test_config_save_load(self):
        """Test save and load configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test_config.json"
            
            manager = ConfigManager(str(config_file))
            manager.save_config(str(config_file))
            
            assert config_file.exists()
            
            # Load and verify
            loaded = json.loads(config_file.read_text())
            assert "api" in loaded
            assert "audio" in loaded
    
    def test_update_section(self):
        """Test updating configuration section"""
        manager = ConfigManager()
        
        assert manager.update_section("api", default_model="test-model") is True
        assert manager.api.default_model == "test-model"

# =========================================================================
# ENCRYPTION TESTS
# =========================================================================

class TestDataEncryption:
    """Test DataEncryption"""
    
    def test_encrypt_decrypt(self):
        """Test encryption and decryption"""
        original = "sensitive data"
        
        encrypted = DataEncryption.encrypt(original, key="test_key")
        decrypted = DataEncryption.decrypt(encrypted, key="test_key")
        
        assert decrypted == original
    
    def test_wrong_key_fails(self):
        """Test decryption with wrong key fails"""
        original = "sensitive data"
        
        encrypted = DataEncryption.encrypt(original, key="key1")
        decrypted = DataEncryption.decrypt(encrypted, key="key2")
        
        assert decrypted != original

# =========================================================================
# PERFORMANCE MONITOR TESTS
# =========================================================================

class TestPerformanceMonitor:
    """Test PerformanceMonitor"""
    
    def test_record_metric(self):
        """Test recording metrics"""
        monitor = PerformanceMonitor()
        
        monitor.record("response_time", 0.5)
        monitor.record("response_time", 0.7)
        
        stats = monitor.get_stats("response_time")
        assert stats['count'] == 2
        assert stats['min'] == 0.5
        assert stats['max'] == 0.7
    
    def test_performance_report(self):
        """Test performance report generation"""
        monitor = PerformanceMonitor()
        
        monitor.record("latency", 100)
        monitor.record("latency", 150)
        
        report = monitor.report()
        assert "latency" in report
        assert "Min:" in report
        assert "Max:" in report

# =========================================================================
# RUN TESTS
# =========================================================================

if __name__ == "__main__":
    # Run with: python -m pytest test_kno_v5.py -v
    pytest.main([__file__, "-v", "--tb=short"])
