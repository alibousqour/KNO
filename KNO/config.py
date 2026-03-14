# =========================================================================
# KNO Configuration Management - Secure Environment-Based Configuration
# =========================================================================
"""
Secure configuration loader with environment variable support.
NEVER saves to JSON files. All sensitive data from environment only.
Load hierarchy: Environment Variables → .env file → Defaults
"""

import os
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
import json

logger = logging.getLogger("KNO.config")

# SECURITY: Ensure no JSON is used for sensitive config
# All secrets must come from environment variables only


# =========================================================================
# CONFIGURATION MODELS
# =========================================================================

@dataclass
class APIConfig:
    """Cloud API configuration - from environment variables ONLY"""
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    
    def __post_init__(self):
        """Validate that keys are not empty strings"""
        if self.gemini_api_key == "":
            self.gemini_api_key = None
        if self.openai_api_key == "":
            self.openai_api_key = None
        if self.deepseek_api_key == "":
            self.deepseek_api_key = None


@dataclass
class AudioConfig:
    """Audio processing configuration"""
    device: Optional[int] = None  # Audio device index, None = default
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    wake_word: str = "KNO"
    listen_timeout_seconds: int = 300  # 5 minutes max listen time
    ptt_timeout_seconds: int = 60  # 1 minute for PTT


@dataclass
class LLMConfig:
    """Local LLM configuration"""
    model_path: str = "models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
    context_size: int = 2048
    max_tokens: int = 512
    temperature: float = 0.7
    n_gpu_layers: int = -1  # Use GPU if available


@dataclass
class SystemConfig:
    """System-level configuration"""
    request_admin: bool = False  # NEVER auto-escalate without user consent
    enable_self_healing: bool = True
    max_retries_per_component: int = 3
    retry_backoff_multiplier: float = 2.0
    log_file: str = "logs/kno.log"
    log_level: str = "INFO"
    memory_file: str = "memory.json"
    experience_file: str = "experience.json"


@dataclass
class Config:
    """Complete KNO configuration - loaded from env only"""
    api: APIConfig
    audio: AudioConfig
    llm: LLMConfig
    system: SystemConfig
    _env_file_path: Optional[str] = None
    
    @classmethod
    def from_environment(cls, env_file: str = ".env") -> "Config":
        """
        Load configuration from environment variables and .env file.
        
        Load order:
        1. Load .env file (if it exists)
        2. Read environment variables
        3. Apply defaults for missing values
        
        Args:
            env_file: Path to .env file (default ".env")
            
        Returns:
            Config: Loaded configuration object
            
        Raises:
            ValueError: If required API keys are missing and no fallback available
        """
        # Load .env file if it exists
        env_path = Path(env_file)
        if env_path.exists():
            load_dotenv(env_file)
            logger.info(f"✅ Loaded environment from {env_file}")
        else:
            logger.debug(f"No .env file found at {env_file}")
        
        # =====================================================================
        # SECURITY FIX #1: API Keys from Environment Only
        # =====================================================================
        api_config = APIConfig(
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            deepseek_api_key=os.getenv("DEEPSEEK_API_KEY")
        )
        
        # Validate that at least one API key is available
        if not any([api_config.gemini_api_key, api_config.openai_api_key, 
                    api_config.deepseek_api_key]):
            logger.warning(
                "⚠️  No API keys available in environment variables. "
                "Cloud AI features will be disabled. Set: "
                "GEMINI_API_KEY, OPENAI_API_KEY, or DEEPSEEK_API_KEY"
            )
        else:
            available_apis = [
                k.split("_")[0] for k in [
                    "GEMINI" if api_config.gemini_api_key else None,
                    "OPENAI" if api_config.openai_api_key else None,
                    "DEEPSEEK" if api_config.deepseek_api_key else None,
                ] if k
            ]
            logger.info(f"✅ API keys loaded for: {', '.join(available_apis)}")
        
        # Audio configuration
        audio_config = AudioConfig(
            device=cls._get_int_env("AUDIO_DEVICE"),
            sample_rate=cls._get_int_env("AUDIO_SAMPLE_RATE", 16000),
            channels=cls._get_int_env("AUDIO_CHANNELS", 1),
            chunk_size=cls._get_int_env("AUDIO_CHUNK_SIZE", 1024),
            wake_word=os.getenv("WAKE_WORD", "KNO"),
            listen_timeout_seconds=cls._get_int_env("LISTEN_TIMEOUT_SECONDS", 300),
            ptt_timeout_seconds=cls._get_int_env("PTT_TIMEOUT_SECONDS", 60),
        )
        
        # LLM configuration
        llm_config = LLMConfig(
            model_path=os.getenv("MODEL_PATH", "models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"),
            context_size=cls._get_int_env("CONTEXT_SIZE", 2048),
            max_tokens=cls._get_int_env("MAX_TOKENS", 512),
            temperature=cls._get_float_env("TEMPERATURE", 0.7),
            n_gpu_layers=cls._get_int_env("N_GPU_LAYERS", -1),
        )
        
        # System configuration
        # SECURITY FIX #2: Require explicit user opt-in for admin escalation
        request_admin = os.getenv("REQUEST_ADMIN", "false").lower() == "true"
        system_config = SystemConfig(
            request_admin=request_admin,
            enable_self_healing=os.getenv("ENABLE_SELF_HEALING", "true").lower() == "true",
            max_retries_per_component=cls._get_int_env("MAX_RETRIES", 3),
            retry_backoff_multiplier=cls._get_float_env("RETRY_BACKOFF", 2.0),
            log_file=os.getenv("LOG_FILE", "logs/kno.log"),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            memory_file=os.getenv("MEMORY_FILE", "memory.json"),
            experience_file=os.getenv("EXPERIENCE_FILE", "experience.json"),
        )
        
        config = cls(
            api=api_config,
            audio=audio_config,
            llm=llm_config,
            system=system_config,
            _env_file_path=str(env_path.absolute()) if env_path.exists() else None
        )
        
        logger.info("✅ Configuration loaded successfully")
        return config
    
    @staticmethod
    def _get_int_env(key: str, default: Optional[int] = None) -> Optional[int]:
        """Safely get integer from environment"""
        try:
            value = os.getenv(key)
            if value is None:
                return default
            return int(value)
        except (ValueError, TypeError):
            logger.warning(f"Invalid integer value for {key}: {os.getenv(key)}")
            return default
    
    @staticmethod
    def _get_float_env(key: str, default: Optional[float] = None) -> Optional[float]:
        """Safely get float from environment"""
        try:
            value = os.getenv(key)
            if value is None:
                return default
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Invalid float value for {key}: {os.getenv(key)}")
            return default
    
    def validate(self) -> List[str]:
        """
        Validate configuration and return list of warnings.
        
        Returns:
            List[str]: List of validation warnings (empty if valid)
        """
        warnings = []
        
        # Audio configuration
        if self.audio.listen_timeout_seconds < 60:
            warnings.append(
                f"⚠️  Listen timeout too short ({self.audio.listen_timeout_seconds}s). "
                "Minimum recommended: 60s"
            )
        
        if self.audio.listen_timeout_seconds > 1800:  # 30 minutes
            warnings.append(
                f"⚠️  Listen timeout very long ({self.audio.listen_timeout_seconds}s). "
                "May cause high resource usage."
            )
        
        # LLM configuration
        if not Path(self.llm.model_path).exists():
            warnings.append(
                f"⚠️  Model file not found: {self.llm.model_path}. "
                "Local LLM will not be available."
            )
        
        # System configuration
        if self.system.max_retries_per_component < 1:
            warnings.append("⚠️  max_retries_per_component must be at least 1")
        
        return warnings
    
    def get_summary(self) -> str:
        """Get human-readable configuration summary"""
        summary = [
            "═" * 60,
            "KNO Configuration Summary",
            "═" * 60,
            f"API Keys Available: {self._count_api_keys()} configs",
            f"Audio Device: {self.audio.device or 'Default'}",
            f"Wake Word: '{self.audio.wake_word}'",
            f"Listen Timeout: {self.audio.listen_timeout_seconds}s",
            f"Model Path: {self.llm.model_path}",
            f"Auto-Admin Escalation: {'❌ DISABLED' if not self.system.request_admin else '⚠️  ENABLED'}",
            f"Self-Healing: {'✅ ENABLED' if self.system.enable_self_healing else '❌ DISABLED'}",
            f"Log Level: {self.system.log_level}",
            "═" * 60,
        ]
        return "\n".join(summary)
    
    def _count_api_keys(self) -> int:
        """Count available API keys"""
        count = 0
        if self.api.gemini_api_key:
            count += 1
        if self.api.openai_api_key:
            count += 1
        if self.api.deepseek_api_key:
            count += 1
        return count


# =========================================================================
# Singleton Instance
# =========================================================================

_config_instance: Optional[Config] = None


def get_config() -> Config:
    """
    Get or create the global configuration instance.
    
    Returns:
        Config: The global configuration object
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config.from_environment()
        
        # Log any validation warnings
        warnings = _config_instance.validate()
        for warning in warnings:
            logger.warning(warning)
    
    return _config_instance


# =========================================================================
# Example .env file template
# =========================================================================

ENV_TEMPLATE = """
# KNO Configuration
# Copy this to .env and fill in your values

# =============== API Keys (REQUIRED for cloud features) ===============
# Get these from: 
#   - GEMINI_API_KEY: https://aistudio.google.com/app/apikeys
#   - OPENAI_API_KEY: https://platform.openai.com/api-keys
#   - DEEPSEEK_API_KEY: https://platform.deepseek.com/api/keys

GEMINI_API_KEY=
OPENAI_API_KEY=
DEEPSEEK_API_KEY=

# =============== Audio Configuration ===============
AUDIO_DEVICE=
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
AUDIO_CHUNK_SIZE=1024
WAKE_WORD=KNO
LISTEN_TIMEOUT_SECONDS=300
PTT_TIMEOUT_SECONDS=60

# =============== LLM Configuration ===============
MODEL_PATH=models/mistral-7b-instruct-v0.1.Q4_K_M.gguf
CONTEXT_SIZE=2048
MAX_TOKENS=512
TEMPERATURE=0.7
N_GPU_LAYERS=-1

# =============== System Configuration ===============
REQUEST_ADMIN=false
ENABLE_SELF_HEALING=true
MAX_RETRIES=3
RETRY_BACKOFF=2.0
LOG_FILE=logs/kno.log
LOG_LEVEL=INFO
MEMORY_FILE=memory.json
EXPERIENCE_FILE=experience.json
"""


if __name__ == "__main__":
    # Test configuration
    logging.basicConfig(level=logging.INFO)
    config = get_config()
    logger.info(config.get_summary())
    
    # Check for validation issues
    warnings = config.validate()
    if warnings:
        logger.warning("\n⚠️  Configuration Warnings:")
        for warning in warnings:
            logger.warning(f"  {warning}")
    else:
        logger.info("\n✅ Configuration valid!")

