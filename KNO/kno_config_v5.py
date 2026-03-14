# =========================================================================
# KNO Configuration v5.0 - Advanced Settings Management
# =========================================================================
"""
Advanced configuration management for KNO v5.0
Supports dynamic reloading, validation, and environment-based configuration
"""

import json
import logging
from typing import Any, Dict, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# =========================================================================
# CONFIGURATION DATACLASSES
# =========================================================================

@dataclass
class APIConfig:
    """API Configuration"""
    gemini_key: str = os.getenv("GEMINI_API_KEY", "")
    openai_key: str = os.getenv("OPENAI_API_KEY", "")
    deepseek_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    default_model: str = "gemini-pro"
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def validate(self) -> bool:
        """Validate API configuration"""
        if not any([self.gemini_key, self.openai_key, self.deepseek_key]):
            logger.warning("No API keys configured")
            return False
        
        return True

@dataclass
class AudioConfig:
    """Audio Configuration"""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    format: str = "wav"
    max_duration: int = 300  # 5 minutes
    silence_threshold: float = 0.01
    use_whisper: bool = True
    use_google_speech: bool = True
    use_pocket_sphinx: bool = False
    
    def validate(self) -> bool:
        """Validate audio configuration"""
        if self.sample_rate < 8000 or self.sample_rate > 48000:
            logger.error("Invalid sample rate")
            return False
        
        if self.max_duration < 10:
            logger.error("Max duration too short")
            return False
        
        return True

@dataclass
class UIConfig:
    """UI Configuration"""
    theme: str = "dark"
    accent_color: str = "#00D9FF"  # Neon cyan
    font_family: str = "Segoe UI"
    font_size: int = 10
    window_width: int = 900
    window_height: int = 700
    animation_enabled: bool = True
    animation_speed: int = 200  # milliseconds
    toast_duration: int = 3000
    notification_position: str = "bottom-right"
    
    def validate(self) -> bool:
        """Validate UI configuration"""
        valid_themes = ["dark", "light", "system"]
        if self.theme not in valid_themes:
            logger.error(f"Invalid theme: {self.theme}")
            return False
        
        if self.window_width < 400 or self.window_height < 300:
            logger.error("Window size too small")
            return False
        
        return True

@dataclass
class LoggingConfig:
    """Logging Configuration"""
    log_level: str = "INFO"
    log_file: str = "logs/kno.log"
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console_output: bool = True
    file_output: bool = True
    
    def validate(self) -> bool:
        """Validate logging configuration"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_levels:
            logger.error(f"Invalid log level: {self.log_level}")
            return False
        
        return True

@dataclass
class CacheConfig:
    """Cache Configuration"""
    enabled: bool = True
    max_size: int = 100
    ttl_seconds: int = 3600  # 1 hour
    eviction_policy: str = "lru"  # lru, lfu, fifo
    
    def validate(self) -> bool:
        """Validate cache configuration"""
        if self.max_size < 10:
            logger.error("Cache size too small")
            return False
        
        if self.ttl_seconds < 60:
            logger.error("TTL too short")
            return False
        
        valid_policies = ["lru", "lfu", "fifo"]
        if self.eviction_policy not in valid_policies:
            logger.error(f"Invalid eviction policy: {self.eviction_policy}")
            return False
        
        return True

@dataclass
class SecurityConfig:
    """Security Configuration"""
    enable_encryption: bool = True
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "default-key")
    api_rate_limit: int = 60  # requests per minute
    session_timeout_minutes: int = 60
    auto_backup_enabled: bool = True
    backup_interval_hours: int = 1
    require_auth: bool = False
    
    def validate(self) -> bool:
        """Validate security configuration"""
        if self.api_rate_limit < 1:
            logger.error("Rate limit too low")
            return False
        
        if self.session_timeout_minutes < 5:
            logger.error("Session timeout too short")
            return False
        
        return True

@dataclass
class PerformanceConfig:
    """Performance Configuration"""
    async_enabled: bool = True
    thread_pool_size: int = 4
    lazy_load_modules: bool = True
    worker_timeout: int = 300
    max_queue_size: int = 1000
    memory_limit_mb: int = 512
    
    def validate(self) -> bool:
        """Validate performance configuration"""
        if self.thread_pool_size < 1 or self.thread_pool_size > 16:
            logger.error("Invalid thread pool size")
            return False
        
        if self.memory_limit_mb < 128:
            logger.error("Memory limit too low")
            return False
        
        return True

# =========================================================================
# CONFIGURATION MANAGER
# =========================================================================

class ConfigManager:
    """
    Manages all KNO v5.0 configuration
    
    Features:
    - Dynamic configuration loading
    - Validation
    - Hot reloading
    - Environment variable support
    - JSON/Python dict support
    """
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.api = APIConfig()
        self.audio = AudioConfig()
        self.ui = UIConfig()
        self.logging = LoggingConfig()
        self.cache = CacheConfig()
        self.security = SecurityConfig()
        self.performance = PerformanceConfig()
        
        self.load_config()
    
    def load_config(self) -> bool:
        """Load configuration from file or environment"""
        # Try JSON file first
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                self._update_from_dict(data)
                logger.info(f"Configuration loaded from {self.config_file}")
                return self.validate()
            
            except Exception as e:
                logger.error(f"Failed to load config file: {e}")
        
        # Fall back to environment variables
        logger.info("Using environment-based configuration")
        return self.validate()
    
    def _update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update configuration from dictionary"""
        if "api" in data:
            self.api = APIConfig(**data["api"])
        
        if "audio" in data:
            self.audio = AudioConfig(**data["audio"])
        
        if "ui" in data:
            self.ui = UIConfig(**data["ui"])
        
        if "logging" in data:
            self.logging = LoggingConfig(**data["logging"])
        
        if "cache" in data:
            self.cache = CacheConfig(**data["cache"])
        
        if "security" in data:
            self.security = SecurityConfig(**data["security"])
        
        if "performance" in data:
            self.performance = PerformanceConfig(**data["performance"])
    
    def validate(self) -> bool:
        """Validate all configuration sections"""
        sections = [
            ("API", self.api),
            ("Audio", self.audio),
            ("UI", self.ui),
            ("Logging", self.logging),
            ("Cache", self.cache),
            ("Security", self.security),
            ("Performance", self.performance)
        ]
        
        all_valid = True
        
        for name, section in sections:
            if section.validate():
                logger.info(f"✓ {name} configuration valid")
            else:
                logger.error(f"✗ {name} configuration invalid")
                all_valid = False
        
        return all_valid
    
    def save_config(self, filepath: str = None) -> bool:
        """Save current configuration to file"""
        try:
            filepath = filepath or str(self.config_file)
            
            config_data = {
                "api": asdict(self.api),
                "audio": asdict(self.audio),
                "ui": asdict(self.ui),
                "logging": asdict(self.logging),
                "cache": asdict(self.cache),
                "security": asdict(self.security),
                "performance": asdict(self.performance)
            }
            
            with open(filepath, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Configuration saved to {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def reload_config(self) -> bool:
        """Reload configuration from file"""
        logger.info("Reloading configuration...")
        return self.load_config()
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get entire configuration as dictionary"""
        return {
            "api": asdict(self.api),
            "audio": asdict(self.audio),
            "ui": asdict(self.ui),
            "logging": asdict(self.logging),
            "cache": asdict(self.cache),
            "security": asdict(self.security),
            "performance": asdict(self.performance)
        }
    
    def update_section(self, section_name: str, **kwargs) -> bool:
        """Update specific configuration section"""
        try:
            if section_name == "api":
                self.api = APIConfig(**{**asdict(self.api), **kwargs})
            elif section_name == "audio":
                self.audio = AudioConfig(**{**asdict(self.audio), **kwargs})
            elif section_name == "ui":
                self.ui = UIConfig(**{**asdict(self.ui), **kwargs})
            elif section_name == "logging":
                self.logging = LoggingConfig(**{**asdict(self.logging), **kwargs})
            elif section_name == "cache":
                self.cache = CacheConfig(**{**asdict(self.cache), **kwargs})
            elif section_name == "security":
                self.security = SecurityConfig(**{**asdict(self.security), **kwargs})
            elif section_name == "performance":
                self.performance = PerformanceConfig(**{**asdict(self.performance), **kwargs})
            else:
                logger.error(f"Unknown section: {section_name}")
                return False
            
            logger.info(f"Updated {section_name} configuration")
            return True
        
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False
    
    def print_summary(self) -> str:
        """Print configuration summary"""
        summary = "=== Configuration Summary ===\n"
        summary += f"API Model: {self.api.default_model}\n"
        summary += f"Audio Sample Rate: {self.audio.sample_rate}Hz\n"
        summary += f"UI Theme: {self.ui.theme}\n"
        summary += f"Log Level: {self.logging.log_level}\n"
        summary += f"Cache Enabled: {self.cache.enabled}\n"
        summary += f"Async Enabled: {self.performance.async_enabled}\n"
        
        return summary

# =========================================================================
# GLOBAL CONFIGURATION INSTANCE
# =========================================================================

config = ConfigManager()

if __name__ == "__main__":
    print("KNO Configuration Manager v5.0")
    print("=" * 50)
    
    # Print current configuration
    print(config.print_summary())
    
    # Validate
    if config.validate():
        print("\n✓ All configurations valid")
    else:
        print("\n✗ Some configurations invalid")
    
    # Save example
    print("\nSaving example configuration...")
    config.save_config("config_example.json")
