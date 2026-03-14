"""
ConsentManager and Audit Logging System for KNO Agent

Provides:
- Permission checking (file system, process control, registry, command execution)
- User approval dialogs (with timeout)
- Audit logging of all operations and permission decisions
- Configurable security levels via settings.json
"""

import json
import os
import datetime
import threading
from pathlib import Path
from typing import Optional, Dict, Any

# Attempt to import Tkinter for GUI approval dialogs
try:
    import tkinter as tk
    from tkinter import messagebox
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False


class AuditLogger:
    """Log all operations and permission decisions for audit trail."""
    
    def __init__(self, audit_file: str = "logs/audit.log"):
        self.audit_file = audit_file
        Path(os.path.dirname(audit_file) or "logs").mkdir(parents=True, exist_ok=True)
    
    def log(self, operation_type: str, action: str, result: str, details: Optional[Dict[str, Any]] = None):
        """Log an operation with timestamp and details."""
        timestamp = datetime.datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "operation_type": operation_type,
            "action": action,
            "result": result,  # "approved", "denied", "error"
            "details": details or {}
        }
        
        try:
            with open(self.audit_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"[AUDIT] Error writing to audit log: {e}", flush=True)
    
    def get_recent_operations(self, limit: int = 50) -> list:
        """Retrieve recent audit entries."""
        if not os.path.exists(self.audit_file):
            return []
        
        try:
            with open(self.audit_file, "r") as f:
                lines = f.readlines()
            
            entries = []
            for line in reversed(lines[-limit:]):
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
            
            return list(reversed(entries))
        except Exception as e:
            print(f"[AUDIT] Error reading audit log: {e}", flush=True)
            return []


class ConsentManager:
    """
    Central permission and consent system for KNO Agent.
    
    Handles:
    - Loading permissions from settings.json
    - Requesting user approval for sensitive operations
    - Logging all permission decisions
    - Configurable security levels
    """
    
    def __init__(self, settings_file: str = "settings.json", main_window=None):
        self.settings_file = settings_file
        self.main_window = main_window
        self.settings = self._load_settings()
        self.audit_logger = AuditLogger(self.settings.get("audit_logging", {}).get("audit_file", "logs/audit.log"))
        self.approval_cache = {}  # Cache user approvals during session
        self.approval_cache_timeout = 3600  # 1 hour
        
        print("[CONSENT] 🔐 ConsentManager initialized", flush=True)
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from settings.json with defaults."""
        defaults = {
            "autonomy_level": "approval_required",
            "permissions": {
                "file_system": "ask",
                "process_control": "ask",
                "registry": "ask",
                "command_execution": "ask",
                "network_operations": "ask",
                "adb_control": "ask",
                "phone_notifications": "ask"
            },
            "antivirus": {
                "enabled": False,
                "real_time_protection": False,
                "quarantine_path": "quarantine"
            },
            "self_evolution": {
                "enabled": False,
                "auto_apply_patches": False,
                "require_approval_for_code_patches": True
            },
            "audit_logging": {
                "enabled": True,
                "audit_file": "logs/audit.log",
                "log_all_operations": True
            }
        }
        
        if not os.path.exists(self.settings_file):
            # Create defaults if file doesn't exist
            try:
                Path("logs").mkdir(exist_ok=True)
                with open(self.settings_file, "w") as f:
                    json.dump(defaults, f, indent=2)
                print(f"[CONSENT] ✅ Created default settings.json", flush=True)
            except Exception as e:
                print(f"[CONSENT] ⚠️  Could not create settings.json: {e}", flush=True)
            return defaults
        
        try:
            with open(self.settings_file, "r") as f:
                user_settings = json.load(f)
            # Merge with defaults (user settings override defaults)
            return {**defaults, **user_settings}
        except Exception as e:
            print(f"[CONSENT] ⚠️  Error loading settings.json, using defaults: {e}", flush=True)
            return defaults
    
    def request_approval(
        self, 
        action: str, 
        permission_type: str, 
        details: Optional[str] = None, 
        timeout_seconds: int = 30
    ) -> bool:
        """
        Request user approval for a sensitive operation.
        
        Args:
            action: Human-readable action description (e.g., "Delete file /path/to/file")
            permission_type: Permission category (e.g., "file_system", "process_control")
            details: Additional context (e.g., file path, process name)
            timeout_seconds: How long to wait for user response
        
        Returns:
            bool: True if approved, False if denied or timed out
        """
        autonomy_level = self.settings.get("autonomy_level", "approval_required")
        perm_setting = self.settings.get("permissions", {}).get(permission_type, "ask")
        
        # Auto-deny if permission is disabled
        if perm_setting == "disabled" or autonomy_level == "restricted":
            self.audit_logger.log(
                operation_type=permission_type,
                action=action,
                result="denied",
                details={"reason": "permission_disabled", "details": details}
            )
            print(f"[CONSENT] ❌ Operation denied (disabled): {action}", flush=True)
            return False
        
        # Auto-approve if permission is fully enabled
        if perm_setting == "allow":
            self.audit_logger.log(
                operation_type=permission_type,
                action=action,
                result="approved",
                details={"reason": "auto_approved", "details": details}
            )
            print(f"[CONSENT] ✅ Operation auto-approved: {action}", flush=True)
            return True
        
        # Otherwise, ask for approval
        approved = self._show_approval_dialog(action, permission_type, details, timeout_seconds)
        
        result_status = "approved" if approved else "denied"
        self.audit_logger.log(
            operation_type=permission_type,
            action=action,
            result=result_status,
            details={"details": details, "timeout_seconds": timeout_seconds}
        )
        
        if approved:
            print(f"[CONSENT] ✅ Operation approved by user: {action}", flush=True)
        else:
            print(f"[CONSENT] ❌ Operation denied by user: {action}", flush=True)
        
        return approved
    
    def _show_approval_dialog(
        self, 
        action: str, 
        permission_type: str, 
        details: Optional[str] = None,
        timeout_seconds: int = 30
    ) -> bool:
        """Show GUI approval dialog if Tkinter available, else console prompt."""
        if TKINTER_AVAILABLE and self.main_window:
            return self._show_tk_dialog(action, details, timeout_seconds)
        else:
            return self._show_console_prompt(action, details)
    
    def _show_tk_dialog(self, action: str, details: Optional[str] = None, timeout_seconds: int = 30) -> bool:
        """Show Tkinter messagebox approval dialog with timeout."""
        try:
            msg = f"KNO Agent is requesting permission:\n\n{action}"
            if details:
                msg += f"\n\nDetails: {details}"
            
            # Create a result holder
            result_holder = {"approved": False}
            
            def show_dialog():
                approved = messagebox.askyesno(
                    "Permission Required",
                    msg,
                    parent=self.main_window
                )
                result_holder["approved"] = approved
            
            # Schedule dialog on GUI thread with timeout
            try:
                self.main_window.after(0, show_dialog)
            except Exception as e:
                print(f"[CONSENT] Could not show dialog: {e}, falling back to console", flush=True)
                return self._show_console_prompt(action, details)
            
            return result_holder.get("approved", False)
        except Exception as e:
            print(f"[CONSENT] Error showing dialog: {e}", flush=True)
            return self._show_console_prompt(action, details)
    
    def _show_console_prompt(self, action: str, details: Optional[str] = None) -> bool:
        """Show console-based approval prompt."""
        print(f"\n{'='*60}", flush=True)
        print("[CONSENT] Permission Required", flush=True)
        print(f"Action: {action}", flush=True)
        if details:
            print(f"Details: {details}", flush=True)
        print("='*60}", flush=True)
        
        try:
            response = input("[CONSENT] Approve? (yes/no): ").strip().lower()
            return response in ("yes", "y")
        except (EOFError, KeyboardInterrupt):
            print("[CONSENT] No response; denying operation", flush=True)
            return False
    
    def check_permission(
        self,
        permission_type: str,
        action: str = "Operation",
        details: Optional[str] = None
    ) -> bool:
        """
        Quick permission check without user interaction (uses settings only).
        
        Returns:
            bool: True if operation is allowed, False if denied/restricted
        """
        perm_setting = self.settings.get("permissions", {}).get(permission_type, "ask")
        autonomy_level = self.settings.get("autonomy_level", "approval_required")
        
        if autonomy_level == "restricted" or perm_setting == "disabled":
            return False
        
        if perm_setting == "allow":
            return True
        
        # "ask" — would require user interaction, so we deny by default in non-interactive context
        return False
    
    def get_audit_trail(self, limit: int = 50) -> list:
        """Retrieve recent audit entries."""
        return self.audit_logger.get_recent_operations(limit)
    
    def is_evolution_enabled(self) -> bool:
        """Check if self-evolution is enabled."""
        return self.settings.get("self_evolution", {}).get("enabled", False)
    
    def requires_patch_approval(self) -> bool:
        """Check if code patches require user approval."""
        return self.settings.get("self_evolution", {}).get("require_approval_for_code_patches", True)
