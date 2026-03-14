# 📝 EXACT CODE CHANGES - DETAILED BREAKDOWN

## 1. agent.py - ConsentManager Import (Lines ~155-165)

### Added Code:
```python
# =========================================================================
# CONSENT & AUDIT SYSTEM - User permission and operation logging
# =========================================================================
try:
    from consent_manager import ConsentManager, AuditLogger
    consent_manager = ConsentManager(settings_file="settings.json", main_window=None)
    logger.info("✓ ConsentManager initialized for security-controlled operations")
except Exception as e:
    logger.warning(f"ConsentManager initialization failed, proceeding without consent checks: {e}")
    consent_manager = None  # Fallback: no consent checks if initialization fails
```

**Location**: Right after logger initialization in imports section
**Purpose**: Initialize consent system with error handling for graceful degradation

---

## 2. agent.py - file_move() in SystemActionEngine (Lines ~2619-2643)

### BEFORE:
```python
def file_move(self, source, destination):
    """Move file with approval and path validation."""
    if not self._validate_path(source) or not self._validate_path(destination):
        print(f"[ACTION] Path outside allowed directories", flush=True)
        return False
    
    if not self.request_approval("file_move", f"Move {source} → {destination}"):
        return False
    
    try:
        shutil.move(source, destination)
        print(f"[ACTION] Moved: {source} → {destination}", flush=True)
        return True
    except Exception as e:
        print(f"[ACTION ERROR] Failed to move file: {e}", flush=True)
        return False
```

### AFTER:
```python
def file_move(self, source, destination):
    """Move file with approval and path validation."""
    if not self._validate_path(source) or not self._validate_path(destination):
        print(f"[ACTION] Path outside allowed directories", flush=True)
        return False
    
    if not self.request_approval("file_move", f"Move {source} → {destination}"):
        return False
    
    # Check global consent manager for additional security control
    if consent_manager:
        if not consent_manager.request_approval(
            action=f"Move file {source}",
            permission_type="file_system",
            details=f"Source: {source}\nDestination: {destination}"
        ):
            print(f"[ACTION] File move operation denied by consent manager", flush=True)
            return False
    
    try:
        shutil.move(source, destination)
        print(f"[ACTION] Moved: {source} → {destination}", flush=True)
        return True
    except Exception as e:
        print(f"[ACTION ERROR] Failed to move file: {e}", flush=True)
        return False
```

**Changes**: 
- Added 8-line consent check block before shutil.move()
- Dual approval gates: local callback + global consent_manager
- Logs denial if consent_manager blocks operation

---

## 3. agent.py - file_copy() in SystemActionEngine (Lines ~2645-2671)

### BEFORE:
```python
def file_copy(self, source, destination):
    """Copy file with approval and path validation."""
    if not self._validate_path(source) or not self._validate_path(destination):
        print(f"[ACTION] Path outside allowed directories", flush=True)
        return False
    
    if not self.request_approval("file_copy", f"Copy {source} → {destination}"):
        return False
    
    try:
        if os.path.isdir(source):
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
        print(f"[ACTION] Copied: {source} → {destination}", flush=True)
        return True
    except Exception as e:
        print(f"[ACTION ERROR] Failed to copy: {e}", flush=True)
        return False
```

### AFTER:
```python
def file_copy(self, source, destination):
    """Copy file with approval and path validation."""
    if not self._validate_path(source) or not self._validate_path(destination):
        print(f"[ACTION] Path outside allowed directories", flush=True)
        return False
    
    if not self.request_approval("file_copy", f"Copy {source} → {destination}"):
        return False
    
    # Check global consent manager for additional security control
    if consent_manager:
        if not consent_manager.request_approval(
            action=f"Copy file {source}",
            permission_type="file_system",
            details=f"Source: {source}\nDestination: {destination}"
        ):
            print(f"[ACTION] File copy operation denied by consent manager", flush=True)
            return False
    
    try:
        if os.path.isdir(source):
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
        print(f"[ACTION] Copied: {source} → {destination}", flush=True)
        return True
    except Exception as e:
        print(f"[ACTION ERROR] Failed to copy: {e}", flush=True)
        return False
```

**Changes**: Same consent check block as file_move()

---

## 4. agent.py - file_delete() in SystemActionEngine (Lines ~2673-2695)

### BEFORE:
```python
def file_delete(self, filepath):
    """Delete file with approval."""
    if not self._validate_path(filepath):
        print(f"[ACTION] Path outside allowed directories", flush=True)
        return False
    
    if not self.request_approval("file_delete", f"Delete: {filepath}"):
        return False
    
    try:
        if os.path.isdir(filepath):
            shutil.rmtree(filepath)
        return True
    except Exception as e:
        print(f"[ACTION ERROR] Failed to delete: {e}", flush=True)
        return False
```

### AFTER:
```python
def file_delete(self, filepath):
    """Delete file with approval."""
    if not self._validate_path(filepath):
        print(f"[ACTION] Path outside allowed directories", flush=True)
        return False
    
    if not self.request_approval("file_delete", f"Delete: {filepath}"):
        return False
    
    # Check global consent manager for additional security control
    if consent_manager:
        if not consent_manager.request_approval(
            action=f"Delete file {filepath}",
            permission_type="file_system",
            details=f"File: {filepath}"
        ):
            print(f"[ACTION] File delete operation denied by consent manager", flush=True)
            return False
    
    try:
        if os.path.isdir(filepath):
            shutil.rmtree(filepath)
        return True
    except Exception as e:
        print(f"[ACTION ERROR] Failed to delete: {e}", flush=True)
        return False
```

**Changes**: Similar consent check block adapted for delete operation

---

## Summary of Changes

### Total Lines Modified in agent.py: ~40 lines
- 1 import section: ~10 lines
- 3 methods updated: ~30 lines (8 lines per method consent check + comments)

### Import Pattern Used (Safe):
```python
try:
    from consent_manager import ConsentManager, AuditLogger
    consent_manager = ConsentManager(...)
except Exception:
    consent_manager = None  # Graceful fallback
```

### Consent Check Pattern Used (Consistent):
```python
if consent_manager:
    if not consent_manager.request_approval(
        action="Description of action",
        permission_type="permission_category",
        details="Additional context"
    ):
        print(f"[ACTION] Operation denied by consent manager")
        return False
```

### Design Philosophy:
- ✅ Dual gate system: Local callback + global consent manager
- ✅ Fail-safe: If ConsentManager unavailable, continues without it
- ✅ Consistent: Same pattern applied to all 3 file operations
- ✅ Minimal changes: Only ~40 lines added to 7900+ line file
- ✅ Backward compatible: No breaking changes to existing logic

---

## New Files Created

### consent_manager.py (290 lines)
Core consent and audit system with two main classes:
- AuditLogger: JSONL logging to logs/audit.log
- ConsentManager: Approval dialogs + permission checks

### settings.json (26 lines)
Security configuration file with:
- autonomy_level setting
- 7 permission categories
- Audit logging configuration
- API security settings

---

## Testing Verification

All changes verified:
- ✅ No syntax errors (py_compile pass)
- ✅ Imports working (test_consent.py passes)
- ✅ Integration verified (verify_consent_integration.py confirms)
- ✅ 3 consent checks found in agent.py
- ✅ Backward compatible (fallback to None works)
