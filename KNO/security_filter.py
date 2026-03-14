"""
Security Filter and Ignore List System
======================================

نظام الأمان والتصفية المتقدم لـ KNO Semantic Search

Provides:
- Advanced file filtering with customizable ignore lists
- Support for .gitignore patterns
- Protection against sensitive file exposure
- Configurable security policies
- Audit logging for security events

Author: KNO Architecture
License: MIT
"""

import os
import json
import logging
from pathlib import Path
from typing import Set, List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import fnmatch
from datetime import datetime

logger = logging.getLogger('KNO.SecurityFilter')

# ============================================================================
# SECURITY CONFIGURATIONS
# ============================================================================

class SensitivityLevel(Enum):
    """File sensitivity levels"""
    PUBLIC = "public"           # Can be indexed
    INTERNAL = "internal"       # Limited indexing
    CONFIDENTIAL = "confidential"  # Should not be indexed
    RESTRICTED = "restricted"   # Must not be indexed under any circumstances


@dataclass
class IgnoreRule:
    """Single ignore rule with metadata"""
    pattern: str
    sensitivity: SensitivityLevel
    reason: str
    enabled: bool = True
    details: str = ""


# ============================================================================
# BUILT-IN IGNORE RULES
# ============================================================================

class DefaultIgnoreRules:
    """Default security ignore rules for KNO"""
    
    # Sensitive files that should NEVER be indexed
    RESTRICTED_PATTERNS = [
        # Cryptographic keys and secrets
        "*.key", "*.pem", "*.pfx", "*.p12",
        "*private*", "*secret*", "*password*",
        ".aws", ".ssh", ".credentials",
        
        # API keys and tokens
        ".env", ".env.*", ".env.local",
        "*api_key*", "*api_secret*", "*token*",
        "secrets.json", "credentials.json",
        
        # Database credentials
        "*password*", "*passwd*",
        ".db", "*.sqlite3", "*.db-journal",
        
        # Authentication
        "oauth*", "jwt*", "bearer*",
        "*auth_token*", "*refresh_token*",
    ]
    
    # Sensitive directories
    RESTRICTED_DIRECTORIES = [
        ".git", ".github",
        ".ssh", ".aws", ".azure",
        ".env", ".env.*",
        "venv", ".venv", "env",
        "__pycache__", ".pytest_cache",
        "node_modules", ".npm",
        ".vscode", ".idea", ".eclipse",
        "dist", "build", "target",
        ".tox", ".nox",
        "htmlcov", ".coverage",
        ".mypy_cache", ".dmypy.json",
        "*.egg-info", ".eggs",
        "site-packages",
    ]
    
    # System and temporary files
    SYSTEM_FILES = [
        "*.pyc", "*.pyo", "*.pyd",
        "*.so", "*.o", "*.a",
        "*.exe", "*.dll", "*.dylib",
        "*.class", "*.jar",
        "Thumbs.db", ".DS_Store",
        "*~", "*.bak", "*.tmp",
        ".swp", ".swo", "*.swn",
    ]
    
    # Binary and large files
    BINARY_FILES = [
        "*.zip", "*.rar", "*.7z", "*.tar", "*.gz",
        "*.bin", "*.iso", "*.img",
        "*.exe", "*.msi", "*.dmg",
        "*.so", "*.dll", "*.dylib",
        "*.pyc", "*.pyo",
    ]
    
    # IDE and editor files
    EDITOR_FILES = [
        ".vscode/*",
        ".idea/*",
        "*.sublime-*",
        ".eclipse/*",
        "launch.json",
        "settings.json",
        "tasks.json",
    ]
    
    # Documentation cache files
    CACHE_FILES = [
        ".cache/*",
        "*.cache",
        "$RECYCLE.BIN/*",
        ".Trash/*",
    ]
    
    @classmethod
    def get_all_rules(cls) -> List[IgnoreRule]:
        """Get all default ignore rules"""
        rules = []
        
        # Restricted (cryptographic keys, secrets)
        for pattern in cls.RESTRICTED_PATTERNS:
            rules.append(IgnoreRule(
                pattern=pattern,
                sensitivity=SensitivityLevel.RESTRICTED,
                reason="Contains sensitive secrets or credentials",
                details="Cryptographic keys, API credentials, database passwords"
            ))
        
        # Restricted directories
        for pattern in cls.RESTRICTED_DIRECTORIES:
            rules.append(IgnoreRule(
                pattern=f"**/{pattern}",
                sensitivity=SensitivityLevel.RESTRICTED,
                reason="Sensitive directory",
                details=f"System or environment directory: {pattern}"
            ))
        
        # Confidential (system files)
        for pattern in cls.SYSTEM_FILES:
            rules.append(IgnoreRule(
                pattern=pattern,
                sensitivity=SensitivityLevel.CONFIDENTIAL,
                reason="System generated file",
                details="Should not be indexed - not useful for search"
            ))
        
        # Confidential (binary files)
        for pattern in cls.BINARY_FILES:
            rules.append(IgnoreRule(
                pattern=pattern,
                sensitivity=SensitivityLevel.CONFIDENTIAL,
                reason="Binary file",
                details="Cannot be meaningfully indexed"
            ))
        
        # Internal (editor files)
        for pattern in cls.EDITOR_FILES:
            rules.append(IgnoreRule(
                pattern=pattern,
                sensitivity=SensitivityLevel.INTERNAL,
                reason="Editor configuration",
                details="IDE-specific settings, not development code"
            ))
        
        return rules


# ============================================================================
# IGNORE LIST MANAGER
# ============================================================================

class IgnoreListManager:
    """
    المدير الأساسي لقائمة التجاهل
    
    Manages file filtering with support for .gitignore patterns
    and custom security rules.
    """
    
    def __init__(self, base_directory: str = ".", custom_rules: Optional[List[IgnoreRule]] = None):
        """
        Initialize ignore list manager.
        
        Args:
            base_directory: Base directory for patterns
            custom_rules: Optional custom ignore rules
        """
        self.base_directory = Path(base_directory)
        self.rules: List[IgnoreRule] = DefaultIgnoreRules.get_all_rules()
        
        if custom_rules:
            self.rules.extend(custom_rules)
        
        self.gitignore_patterns: Set[str] = set()
        self.security_audit_log: List[Dict[str, Any]] = []
        
        # Load .gitignore if exists
        self._load_gitignore()
        
        logger.info(f"IgnoreListManager initialized with {len(self.rules)} rules")
    
    def _load_gitignore(self):
        """Load patterns from .gitignore file"""
        gitignore_path = self.base_directory / ".gitignore"
        
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if line and not line.startswith('#'):
                            self.gitignore_patterns.add(line)
                
                logger.info(f"Loaded {len(self.gitignore_patterns)} patterns from .gitignore")
            
            except Exception as e:
                logger.warning(f"Failed to load .gitignore: {e}")
    
    def should_ignore_file(
        self,
        file_path: str,
        reason_output: bool = False
    ) -> bool | Dict[str, Any]:
        """
        يجب تجاهل هذا الملف؟
        
        Check if a file should be ignored.
        
        Args:
            file_path: Path to check
            reason_output: Return reason for ignoring
        
        Returns:
            bool or Dict with ignore status and reason
        """
        path = Path(file_path)
        relative_path = path.relative_to(self.base_directory) if path.is_relative_to(self.base_directory) else path
        
        # Check enabled rules
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            if self._matches_pattern(str(relative_path), rule.pattern):
                result = {
                    'ignored': True,
                    'rule': rule.pattern,
                    'sensitivity': rule.sensitivity.value,
                    'reason': rule.reason,
                    'details': rule.details
                }
                
                # Log restricted access attempts
                if rule.sensitivity == SensitivityLevel.RESTRICTED:
                    self._log_security_event(file_path, rule)
                
                return result if reason_output else True
        
        # Check .gitignore patterns
        for pattern in self.gitignore_patterns:
            if self._matches_pattern(str(relative_path), pattern):
                result = {
                    'ignored': True,
                    'rule': pattern,
                    'sensitivity': SensitivityLevel.INTERNAL.value,
                    'reason': 'Ignored via .gitignore',
                    'details': f'Pattern: {pattern}'
                }
                return result if reason_output else True
        
        return {'ignored': False} if reason_output else False
    
    def should_include_file(self, file_path: str) -> bool:
        """Shorthand: check if file should be included"""
        return not self.should_ignore_file(file_path)
    
    @staticmethod
    def _matches_pattern(path_str: str, pattern: str) -> bool:
        """Check if path matches pattern using fnmatch"""
        # Normalize slashes
        path_str = path_str.replace('\\', '/')
        pattern = pattern.replace('\\', '/')
        
        # Handle directory patterns
        if pattern.startswith('*/'):
            pattern = pattern[2:]
        
        # Check both full path and filename
        if fnmatch.fnmatch(path_str, pattern):
            return True
        
        if fnmatch.fnmatch(path_str, f'*/{pattern}'):
            return True
        
        # Check filename only
        filename = Path(path_str).name
        if fnmatch.fnmatch(filename, pattern):
            return True
        
        return False
    
    def add_custom_rule(
        self,
        pattern: str,
        sensitivity: SensitivityLevel,
        reason: str,
        details: str = ""
    ) -> None:
        """
        أضف قاعدة تجاهل مخصصة
        
        Add a custom ignore rule.
        
        Args:
            pattern: File pattern to ignore
            sensitivity: Sensitivity level
            reason: Reason for ignoring
            details: Additional details
        """
        rule = IgnoreRule(
            pattern=pattern,
            sensitivity=sensitivity,
            reason=reason,
            details=details
        )
        self.rules.append(rule)
        logger.info(f"Added custom rule: {pattern}")
    
    def remove_rule(self, pattern: str) -> bool:
        """Remove rule by pattern"""
        original_count = len(self.rules)
        self.rules = [r for r in self.rules if r.pattern != pattern]
        removed = len(self.rules) < original_count
        
        if removed:
            logger.info(f"Removed rule: {pattern}")
        
        return removed
    
    def enable_rule(self, pattern: str) -> bool:
        """Enable a rule"""
        for rule in self.rules:
            if rule.pattern == pattern:
                rule.enabled = True
                return True
        return False
    
    def disable_rule(self, pattern: str) -> bool:
        """Disable a rule"""
        for rule in self.rules:
            if rule.pattern == pattern:
                rule.enabled = False
                return True
        return False
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """Get summary of all rules"""
        by_sensitivity = {}
        for rule in self.rules:
            key = rule.sensitivity.value
            if key not in by_sensitivity:
                by_sensitivity[key] = []
            by_sensitivity[key].append(rule.pattern)
        
        return {
            'total_rules': len(self.rules),
            'gitignore_patterns': len(self.gitignore_patterns),
            'by_sensitivity': by_sensitivity,
            'enabled_rules': len([r for r in self.rules if r.enabled])
        }
    
    def _log_security_event(self, file_path: str, rule: IgnoreRule) -> None:
        """Log security event for restricted file access attempts"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'file': file_path,
            'rule': rule.pattern,
            'reason': rule.reason,
            'sensitivity': rule.sensitivity.value
        }
        self.security_audit_log.append(event)
        logger.warning(f"SECURITY: Attempt to access restricted file: {file_path}")
    
    def get_security_audit_log(self) -> List[Dict[str, Any]]:
        """Get security audit log"""
        return self.security_audit_log.copy()
    
    def save_audit_log(self, log_file: str = "security_audit.log") -> bool:
        """Save security audit log to file"""
        try:
            with open(log_file, 'w') as f:
                json.dump(self.security_audit_log, f, indent=2)
            logger.info(f"Saved audit log to {log_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save audit log: {e}")
            return False


# ============================================================================
# SECURE FILE ANALYZER
# ============================================================================

class SecureFileAnalyzer:
    """
    محلل ملفات آمن مع فلترة السلامة
    
    File analyzer with integrated security filtering.
    """
    
    def __init__(self, base_directory: str = ".", ignore_manager: Optional[IgnoreListManager] = None):
        """Initialize secure file analyzer"""
        self.base_directory = Path(base_directory)
        self.ignore_manager = ignore_manager or IgnoreListManager(base_directory)
    
    def scan_directory_safely(
        self,
        directory: str = None,
        include_ignored: bool = False
    ) -> Dict[str, Any]:
        """
        مسح آمن للمجلد
        
        Safe directory scan with security filtering.
        
        Args:
            directory: Directory to scan (uses base if None)
            include_ignored: Include ignored files in report
        
        Returns:
            Scan results with statistics
        """
        scan_dir = Path(directory or self.base_directory)
        
        results = {
            'scan_date': datetime.now().isoformat(),
            'directory': str(scan_dir),
            'total_files': 0,
            'indexable_files': 0,
            'ignored_files': 0,
            'restricted_files': 0,
            'files_by_type': {},
            'ignored_summary': {},
            'security_warnings': []
        }
        
        try:
            for root, dirs, files in os.walk(scan_dir):
                # Filter directories first
                dirs[:] = [
                    d for d in dirs
                    if self.ignore_manager.should_include_file(os.path.join(root, d))
                ]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    results['total_files'] += 1
                    
                    # Check if should be ignored
                    ignore_info = self.ignore_manager.should_ignore_file(file_path, reason_output=True)
                    
                    if ignore_info['ignored']:
                        results['ignored_files'] += 1
                        
                        sensitivity = ignore_info.get('sensitivity', 'unknown')
                        if sensitivity not in results['ignored_summary']:
                            results['ignored_summary'][sensitivity] = 0
                        results['ignored_summary'][sensitivity] += 1
                        
                        if sensitivity == 'restricted':
                            results['restricted_files'] += 1
                            results['security_warnings'].append({
                                'file': file_path,
                                'reason': ignore_info.get('reason')
                            })
                    
                    else:
                        results['indexable_files'] += 1
                        
                        # Track file types
                        ext = Path(file).suffix or 'no_ext'
                        if ext not in results['files_by_type']:
                            results['files_by_type'][ext] = 0
                        results['files_by_type'][ext] += 1
        
        except Exception as e:
            logger.error(f"Scan error: {e}")
            results['error'] = str(e)
        
        return results


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def demo_security_filter():
    """Demonstrate security filtering"""
    
    print("\n" + "=" * 70)
    print("KNO Security Filter - Demonstration".center(70))
    print("=" * 70)
    
    # Initialize
    manager = IgnoreListManager(base_directory="./KNO")
    
    # Show stats
    summary = manager.get_rules_summary()
    print(f"\n📋 Rules Summary:")
    print(f"   Total Rules: {summary['total_rules']}")
    print(f"   .gitignore Patterns: {summary['gitignore_patterns']}")
    print(f"   Enabled Rules: {summary['enabled_rules']}")
    
    print(f"\n🔒 Rules by Sensitivity:")
    for sensitivity, patterns in summary['by_sensitivity'].items():
        print(f"   {sensitivity.upper()}: {len(patterns)} rules")
    
    # Test some files
    test_files = [
        "KNO/agent.py",
        "KNO/config.json",
        ".env",
        ".git/config",
        "node_modules/package.json",
        ".ssh/id_rsa",
        "secrets.json",
        "__pycache__/module.pyc"
    ]
    
    print(f"\n🔍 Testing Files:")
    for test_file in test_files:
        ignore_info = manager.should_ignore_file(test_file, reason_output=True)
        status = "❌ IGNORED" if ignore_info['ignored'] else "✓ INCLUDED"
        reason = ignore_info.get('reason', 'OK')
        print(f"   {status:15} {test_file:35} ({reason})")
    
    # Scan directory
    print(f"\n📊 Directory Scan:")
    analyzer = SecureFileAnalyzer(base_directory="./KNO", ignore_manager=manager)
    scan = analyzer.scan_directory_safely()
    
    print(f"   Total Files: {scan['total_files']}")
    print(f"   Indexable Files: {scan['indexable_files']}")
    print(f"   Ignored Files: {scan['ignored_files']}")
    print(f"   Restricted Files: {scan['restricted_files']}")
    
    if scan['security_warnings']:
        print(f"\n⚠️  Security Warnings: {len(scan['security_warnings'])}")
        for warning in scan['security_warnings'][:3]:
            print(f"   - {warning['file']}: {warning['reason']}")


if __name__ == "__main__":
    demo_security_filter()
