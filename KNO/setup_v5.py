# =========================================================================
# KNO v5.0 Deployment Setup - Installation & Configuration
# =========================================================================
"""
Automated setup script for KNO v5.0 system
Handles: environment setup, dependency installation, configuration
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from typing import Optional, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =========================================================================
# REQUIREMENTS
# =========================================================================

REQUIREMENTS = [
    "customtkinter>=5.0.0",
    "pillow>=9.0.0",
    "requests>=2.28.0",
    "pydotenv>=0.20.0",
    "numpy>=1.21.0",
    "SpeechRecognition>=3.10.0",
    "pocketsphinx>=0.1.15",
    "pyttsx3>=2.90",
    "pytest>=7.0.0",
    "python-dotenv>=0.20.0",
]

# =========================================================================
# SETUP MANAGER
# =========================================================================

class SetupManager:
    """Manages KNO v5.0 installation and configuration"""
    
    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = Path(workspace_dir)
        self.venv_dir = self.workspace_dir / "venv"
        self.logs_dir = self.workspace_dir / "logs"
        self.backups_dir = self.workspace_dir / "backups"
        self.config_file = self.workspace_dir / "config.json"
        self.env_file = self.workspace_dir / ".env"
    
    def print_banner(self):
        """Print setup banner"""
        banner = """
╔════════════════════════════════════════════════════════╗
║       KNO v5.0 System - Automated Setup Wizard          ║
║                                                        ║
║  Modern AI Agent with Advanced Features:               ║
║  • Real-time audio processing                          ║
║  • Multi-model LLM support                             ║
║  • Intelligent caching system                          ║
║  • Advanced error recovery                             ║
║  • Professional UI/UX                                  ║
╚════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_python_version(self) -> bool:
        """Check if Python version is compatible"""
        logger.info("Checking Python version...")
        
        if sys.version_info >= (3, 9):
            logger.info(f"✓ Python {sys.version.split()[0]} detected")
            return True
        else:
            logger.error(f"✗ Python 3.9+ required (found {sys.version.split()[0]})")
            return False
    
    def create_directories(self) -> bool:
        """Create necessary directories"""
        logger.info("Creating directory structure...")
        
        try:
            self.logs_dir.mkdir(exist_ok=True)
            self.backups_dir.mkdir(exist_ok=True)
            
            logger.info(f"✓ Created directories:")
            logger.info(f"  - {self.logs_dir}")
            logger.info(f"  - {self.backups_dir}")
            
            return True
        
        except Exception as e:
            logger.error(f"✗ Failed to create directories: {e}")
            return False
    
    def setup_virtual_environment(self) -> bool:
        """Create and activate virtual environment"""
        logger.info("Setting up virtual environment...")
        
        if self.venv_dir.exists():
            logger.info("✓ Virtual environment already exists")
            return True
        
        try:
            subprocess.check_call([sys.executable, "-m", "venv", str(self.venv_dir)])
            logger.info(f"✓ Created virtual environment at {self.venv_dir}")
            return True
        
        except Exception as e:
            logger.error(f"✗ Failed to create virtual environment: {e}")
            return False
    
    def install_requirements(self) -> bool:
        """Install Python dependencies"""
        logger.info("Installing dependencies...")
        
        try:
            # Get pip executable
            if sys.platform == "win32":
                pip_exe = self.venv_dir / "Scripts" / "pip.exe"
            else:
                pip_exe = self.venv_dir / "bin" / "pip"
            
            # Upgrade pip
            logger.info("Upgrading pip...")
            subprocess.check_call([str(pip_exe), "install", "--upgrade", "pip"])
            
            # Install requirements
            for requirement in REQUIREMENTS:
                logger.info(f"Installing {requirement}...")
                subprocess.check_call([str(pip_exe), "install", requirement])
            
            logger.info("✓ All dependencies installed")
            return True
        
        except Exception as e:
            logger.error(f"✗ Failed to install dependencies: {e}")
            return False
    
    def create_env_file(self) -> bool:
        """Create .env configuration file"""
        logger.info("Creating environment configuration...")
        
        if self.env_file.exists():
            logger.info("✓ .env file already exists")
            return True
        
        try:
            env_template = """# ============================================
# KNO v5.0 Environment Configuration
# ============================================

# API Keys (required for LLM functionality)
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here

# Security
ENCRYPTION_KEY=your_encryption_key_here
SECRET_KEY=your_secret_key_here

# Audio Configuration
AUDIO_SAMPLE_RATE=16000
AUDIO_MAX_DURATION=300

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/kno.log

# Performance
ASYNC_ENABLED=true
THREAD_POOL_SIZE=4
LAZY_LOAD_MODULES=true

# Security
API_RATE_LIMIT=60
SESSION_TIMEOUT_MINUTES=60
AUTO_BACKUP_ENABLED=true
REQUIRE_AUTH=false
"""
            
            self.env_file.write_text(env_template)
            logger.info(f"✓ Created .env file at {self.env_file}")
            logger.warning("⚠ Please update .env with your API keys")
            
            return True
        
        except Exception as e:
            logger.error(f"✗ Failed to create .env file: {e}")
            return False
    
    def create_config_file(self) -> bool:
        """Create configuration JSON file"""
        logger.info("Creating configuration file...")
        
        if self.config_file.exists():
            logger.info("✓ Config file already exists")
            return True
        
        try:
            config = {
                "api": {
                    "default_model": "gemini-pro",
                    "timeout_seconds": 30,
                    "max_retries": 3,
                    "retry_delay": 1.0
                },
                "audio": {
                    "sample_rate": 16000,
                    "channels": 1,
                    "chunk_size": 1024,
                    "format": "wav",
                    "max_duration": 300,
                    "use_whisper": True,
                    "use_google_speech": True
                },
                "ui": {
                    "theme": "dark",
                    "accent_color": "#00D9FF",
                    "font_family": "Segoe UI",
                    "font_size": 10,
                    "window_width": 900,
                    "window_height": 700,
                    "animation_enabled": True
                },
                "logging": {
                    "log_level": "INFO",
                    "log_file": "logs/kno.log",
                    "max_file_size": 10485760,
                    "backup_count": 5
                },
                "cache": {
                    "enabled": True,
                    "max_size": 100,
                    "ttl_seconds": 3600,
                    "eviction_policy": "lru"
                },
                "security": {
                    "enable_encryption": True,
                    "api_rate_limit": 60,
                    "session_timeout_minutes": 60,
                    "auto_backup_enabled": True
                },
                "performance": {
                    "async_enabled": True,
                    "thread_pool_size": 4,
                    "lazy_load_modules": True
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"✓ Created config.json")
            return True
        
        except Exception as e:
            logger.error(f"✗ Failed to create config file: {e}")
            return False
    
    def verify_installation(self) -> bool:
        """Verify installation is complete"""
        logger.info("Verifying installation...")
        
        checks = [
            ("Python version", self.check_python_version()),
            ("Directories", self.logs_dir.exists() and self.backups_dir.exists()),
            ("Virtual environment", self.venv_dir.exists()),
            (".env file", self.env_file.exists()),
            ("Config file", self.config_file.exists()),
        ]
        
        all_valid = True
        
        for check_name, result in checks:
            status = "✓" if result else "✗"
            logger.info(f"{status} {check_name}")
            all_valid = all_valid and result
        
        return all_valid
    
    def run_setup(self) -> bool:
        """Run complete setup"""
        self.print_banner()
        
        steps = [
            ("Checking Python version", self.check_python_version()),
            ("Creating directories", self.create_directories()),
            ("Setting up virtual environment", self.setup_virtual_environment()),
            ("Installing dependencies", self.install_requirements()),
            ("Creating .env file", self.create_env_file()),
            ("Creating config file", self.create_config_file()),
        ]
        
        for step_name, result in steps:
            if not result:
                logger.error(f"Setup failed at: {step_name}")
                return False
        
        # Final verification
        if self.verify_installation():
            print("\n" + "="*60)
            logger.info("✓ Setup completed successfully!")
            logger.info("\nNext steps:")
            logger.info("1. Update .env file with your API keys")
            logger.info("2. Run: python agent_refactored_v5.py")
            logger.info("="*60)
            return True
        else:
            logger.error("✗ Installation verification failed")
            return False

# =========================================================================
# HELPER FUNCTIONS
# =========================================================================

def get_python_executable() -> str:
    """Get path to Python executable in venv"""
    if sys.platform == "win32":
        return "venv\\Scripts\\python.exe"
    else:
        return "venv/bin/python"

def run_tests() -> bool:
    """Run test suite"""
    logger.info("Running tests...")
    
    try:
        import pytest
        exit_code = pytest.main([
            "test_kno_v5.py",
            "-v",
            "--tb=short",
            "-x"  # Stop on first failure
        ])
        
        return exit_code == 0
    
    except ImportError:
        logger.warning("pytest not installed, skipping tests")
        return False

def start_application():
    """Start KNO application"""
    logger.info("Starting KNO v5.0 application...")
    
    try:
        import subprocess
        python_exe = get_python_executable()
        subprocess.Popen([python_exe, "agent_refactored_v5.py"])
        logger.info("✓ Application started")
    
    except Exception as e:
        logger.error(f"Failed to start application: {e}")

# =========================================================================
# MAIN
# =========================================================================

def main():
    """Main setup entry point"""
    manager = SetupManager(os.getcwd())
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            success = manager.run_setup()
            sys.exit(0 if success else 1)
        
        elif command == "verify":
            success = manager.verify_installation()
            sys.exit(0 if success else 1)
        
        elif command == "test":
            success = run_tests()
            sys.exit(0 if success else 1)
        
        elif command == "start":
            start_application()
        
        else:
            print("""
Usage: python setup_v5.py [command]

Commands:
  setup  - Complete setup and installation
  verify - Verify installation is complete
  test   - Run test suite
  start  - Start KNO application

Example: python setup_v5.py setup
            """)
    else:
        # Interactive setup
        manager.run_setup()

if __name__ == "__main__":
    main()
