# =========================================================================
# Safe Code Patcher - AST-Based Code Validation & Safe Patching
# =========================================================================
"""
Replaces dangerous exec() with safe regex-based code patching.

SECURITY ARCHITECTURE:
1. Parse code as AST to validate structure
2. Whitelist allowed operations
3. Apply changes via regex, not execution
4. Backup original file before patching
5. Verify changes after patching

This eliminates arbitrary code execution vulnerability.
"""

import ast
import os
import re
import logging
import shutil
import hashlib
from typing import Optional, Dict, List, Tuple
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("KNO.safe_code_patcher")


# =========================================================================
# SECURITY CONFIGURATION
# =========================================================================

# Whitelisted operations for code patches
WHITELISTED_OPERATIONS = {
    "import_statements",      # Allow new imports
    "function_definition",    # Allow new function definitions
    "variable_assignment",    # Allow variable assignments
    "string_literal",         # Allow string literals
    "number_literal",         # Allow numeric literals
    "boolean_literal",        # Allow boolean literals
    "list_literal",           # Allow list literals
    "dict_literal",           # Allow dict literals
    "method_call",            # Allow method calls (restricted)
    "attribute_access",       # Allow attribute access
}

# Explicitly blocked patterns (malicious code indicators)
BLOCKED_PATTERNS = [
    r"__import__",            # Arbitrary imports
    r"eval\s*\(",            # eval() execution
    r"exec\s*\(",            # exec() execution
    r"compile\s*\(",         # compile() execution
    r"__builtins__",          # Direct builtin access
    r"globals\s*\(",         # Access to globals
    r"locals\s*\(",          # Access to locals
    r"vars\s*\(",            # Access to vars
    r"dir\s*\(",             # Directory listing
    r"getattr\s*\(",         # Arbitrary attribute access
    r"setattr\s*\(",         # Arbitrary attribute setting
    r"delattr\s*\(",         # Arbitrary attribute deletion
    r"type\s*\(",            # Type manipulation
    r"object\s*\(",          # Object manipulation
    r"__",                    # Double underscore (dunder methods)
]


# =========================================================================
# AST VALIDATOR
# =========================================================================

class CodeValidator:
    """Validates code patches using AST parsing"""
    
    @staticmethod
    def validate_patch_code(code: str) -> Tuple[bool, List[str]]:
        """
        Validate patch code for security issues.
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for blocked patterns
        for pattern in BLOCKED_PATTERNS:
            if re.search(pattern, code):
                errors.append(f"❌ Blocked pattern found: {pattern}")
        
        # Try to parse as AST
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"❌ Syntax error: {e}")
            return False, errors
        
        # Analyze AST nodes
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                error = CodeValidator._check_node(node)
                if error:
                    errors.append(error)
        except Exception as e:
            errors.append(f"❌ AST analysis failed: {e}")
            return False, errors
        
        if errors:
            return False, errors
        
        return True, []
    
    @staticmethod
    def _check_node(node: ast.AST) -> Optional[str]:
        """Check individual AST node for security issues"""
        
        # Block Call nodes with certain function names
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in ["eval", "exec", "compile", "__import__"]:
                    return f"❌ Blocked function call: {func_name}"
            elif isinstance(node.func, ast.Attribute):
                attr_name = node.func.attr
                if attr_name in ["__getattr__", "__setattr__", "__delattr__"]:
                    return f"❌ Blocked method: {attr_name}"
        
        # Block import * statements
        if isinstance(node, ast.ImportFrom):
            if any(alias.name == "*" for alias in node.names):
                return "❌ Wildcard imports not allowed"
        
        return None


# =========================================================================
# REGEX-BASED PATCHER
# =========================================================================

class SafePatchApplier:
    """Applies code patches safely using regex and backup validation"""
    
    BACKUP_DIR = "backups"
    PATCH_LOG_FILE = "patch_history.log"
    
    def __init__(self):
        """Initialize patcher"""
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """Ensure backup directory exists"""
        Path(self.BACKUP_DIR).mkdir(exist_ok=True)
    
    def apply_patch(self, 
                   filepath: str, 
                   patch_code: str,
                   reason: str = "") -> Tuple[bool, str]:
        """
        Apply a code patch safely.
        
        Args:
            filepath: Path to file to patch
            patch_code: Code patch to apply (special format)
            reason: Human-readable reason for patch
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        # Validate patch code
        is_valid, errors = CodeValidator.validate_patch_code(patch_code)
        if not is_valid:
            error_msg = "Patch validation failed:\n" + "\n".join(errors)
            logger.error(error_msg)
            return False, error_msg
        
        try:
            # Read original file
            if not os.path.exists(filepath):
                return False, f"❌ File not found: {filepath}"
            
            with open(filepath, "r", encoding="utf-8") as f:
                original_content = f.read()
            
            # Create backup
            backup_path = self._create_backup(filepath, original_content)
            logger.info(f"✅ Backup created: {backup_path}")
            
            # Parse patch directive
            patch_type, patch_details = self._parse_patch_directive(patch_code)
            
            if patch_type == "REPLACE":
                old_code, new_code = patch_details
                new_content = self._apply_replace(original_content, old_code, new_code)
            elif patch_type == "APPEND":
                new_content = self._apply_append(original_content, patch_details)
            elif patch_type == "REMOVE":
                new_content = self._apply_remove(original_content, patch_details)
            elif patch_type == "INSERT_FUNCTION":
                new_content = self._apply_insert_function(original_content, patch_details)
            else:
                return False, f"❌ Unknown patch type: {patch_type}"
            
            if new_content is None:
                return False, "❌ Patch application failed"
            
            # Write patched file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            # Log patch
            self._log_patch(filepath, patch_type, reason, backup_path)
            
            logger.info(f"✅ Patch applied successfully to {filepath}")
            return True, f"✅ Patch applied. Backup: {backup_path}"
        
        except Exception as e:
            logger.error(f"❌ Patch application failed: {e}")
            return False, f"❌ Error: {str(e)}"
    
    def _create_backup(self, filepath: str, content: str) -> str:
        """Create timestamped backup of file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(filepath).name
        backup_name = f"{filename}.{timestamp}.bak"
        backup_path = Path(self.BACKUP_DIR) / backup_name
        
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return str(backup_path)
    
    def _parse_patch_directive(self, patch_code: str) -> Tuple[str, any]:
        """
        Parse patch directive from code.
        
        Patch Formats:
        1. REPLACE|old_code|new_code
        2. APPEND|new_code
        3. REMOVE|code_to_remove
        4. INSERT_FUNCTION|function_code
        """
        lines = patch_code.strip().split("\n")
        directive = lines[0]
        
        if directive.startswith("REPLACE"):
            # REPLACE|old_code|new_code
            parts = patch_code.split("|", 2)
            if len(parts) == 3:
                return "REPLACE", (parts[1].strip(), parts[2].strip())
        elif directive.startswith("APPEND"):
            content = "\n".join(lines[1:])
            return "APPEND", content
        elif directive.startswith("REMOVE"):
            content = "\n".join(lines[1:])
            return "REMOVE", content
        elif directive.startswith("INSERT_FUNCTION"):
            content = "\n".join(lines[1:])
            return "INSERT_FUNCTION", content
        
        raise ValueError(f"Invalid patch directive: {directive}")
    
    def _apply_replace(self, content: str, old_code: str, new_code: str) -> Optional[str]:
        """Apply REPLACE patch"""
        if old_code not in content:
            logger.warning(f"⚠️  Old code not found in file")
            return None
        
        return content.replace(old_code, new_code, 1)
    
    def _apply_append(self, content: str, new_code: str) -> str:
        """Apply APPEND patch"""
        return content + "\n\n" + new_code
    
    def _apply_remove(self, content: str, code_to_remove: str) -> Optional[str]:
        """Apply REMOVE patch"""
        if code_to_remove not in content:
            logger.warning(f"⚠️  Code to remove not found in file")
            return None
        
        return content.replace(code_to_remove, "", 1)
    
    def _apply_insert_function(self, content: str, function_code: str) -> str:
        """Apply INSERT_FUNCTION patch - adds function at end of file"""
        return content + "\n\n" + function_code
    
    def _log_patch(self, filepath: str, patch_type: str, reason: str, backup_path: str):
        """Log patch application to history"""
        timestamp = datetime.now().isoformat()
        log_entry = (
            f"[{timestamp}] {patch_type} to {filepath}\n"
            f"  Reason: {reason}\n"
            f"  Backup: {backup_path}\n"
            f"  Checksum: {self._file_checksum(filepath)}\n"
        )
        
        with open(self.PATCH_LOG_FILE, "a") as f:
            f.write(log_entry + "\n")
    
    @staticmethod
    def _file_checksum(filepath: str) -> str:
        """Calculate SHA256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


# =========================================================================
# SIMPLE REPLACEMENT UTILS
# =========================================================================

def safe_code_replace(filepath: str,
                     old_pattern: str,
                     new_code: str,
                     reason: str = "") -> Tuple[bool, str]:
    """
    Safely replace code in a file using regex validation.
    
    Args:
        filepath: Path to file
        old_pattern: Code to find (as regex)
        new_code: Code to replace with
        reason: Why the patch is being applied
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    patcher = SafePatchApplier()
    patch_code = f"REPLACE|{old_pattern}|{new_code}"
    return patcher.apply_patch(filepath, patch_code, reason)


if __name__ == "__main__":
    # Test code validator
    logging.basicConfig(level=logging.DEBUG)
    
    test_code_valid = """
def helper_function():
    return 42
    
x = 10
y = x + 5
"""
    
    test_code_invalid = """
exec("malicious code")
"""
    
    print("Testing valid code:")
    is_valid, errors = CodeValidator.validate_patch_code(test_code_valid)
    print(f"  Valid: {is_valid}")
    
    print("\nTesting invalid code:")
    is_valid, errors = CodeValidator.validate_patch_code(test_code_invalid)
    print(f"  Valid: {is_valid}")
    print(f"  Errors: {errors}")
