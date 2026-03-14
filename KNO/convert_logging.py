#!/usr/bin/env python3
"""
Print-to-Logger Conversion Helper

This script helps convert remaining print() statements to logger calls.
Run this in the agent.py directory to perform automated conversions.

Usage:
    python convert_logging.py                 # Dry run (show what would change)
    python convert_logging.py --apply         # Apply changes to agent.py
"""

import re
import os
import sys
import argparse
from pathlib import Path


TAG_TO_LEVEL = {
    # Error levels
    'ERROR': 'error',
    'FATAL': 'error',
    'FAIL': 'error',
    'EXCEPTION': 'error',
    
    # Warning levels
    'WARNING': 'warning',
    'WARN': 'warning',
    'ISSUE': 'warning',
    
    # Info levels
    'INFO': 'info',
    'READY': 'info',
    'RESOURCE': 'info',
    'DOWNLOAD': 'info',
    'AUDIO': 'info',
    'TRANSCRIBE': 'info',
    'PRIVILEGE': 'info',
    'MAIN': 'info',
    'STATE': 'info',
    'OK': 'info',
    
    # Debug levels
    'DEBUG': 'debug',
    'TRACE': 'debug',
}


def detect_log_level(tag, message):
    """
    Detect appropriate log level based on tag and message content.
    
    Args:
        tag: String tag from [TAG]
        message: Message text
        
    Returns:
        str: Log level ('error', 'warning', 'info', 'debug')
    """
    # Check tag first
    level = TAG_TO_LEVEL.get(tag, 'info')
    
    # Check message content
    msg_lower = message.lower()
    if 'error' in msg_lower or 'failed' in msg_lower or 'exception' in msg_lower:
        return 'error'
    elif 'warning' in msg_lower or 'warn' in msg_lower or 'issue' in msg_lower:
        return 'warning'
    elif 'debug' in msg_lower or 'trace' in msg_lower:
        return 'debug'
    
    return level


def convert_tagged_print(match):
    """Convert [TAG] message print to logger call."""
    tag = match.group(1)
    message = match.group(2)
    
    level = detect_log_level(tag, message)
    return f'logger.{level}({message})'


def convert_simple_print(match):
    """Convert simple print message to logger call."""
    message = match.group(1)
    
    # Try to detect level from message
    msg_lower = message.lower()
    if 'error' in msg_lower or 'failed' in msg_lower:
        return f'logger.error({message})'
    elif 'warning' in msg_lower or 'warn' in msg_lower:
        return f'logger.warning({message})'
    else:
        return f'logger.info({message})'


def convert_file(filename, apply=False):
    """
    Convert print() statements to logger calls.
    
    Args:
        filename: Path to file to convert
        apply: If True, write changes; if False, just show diff
        
    Returns:
        tuple: (changes_count, changes_list)
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return 0, []
    
    content = original_content
    changes = []
    
    # Pattern 1: [TAG] style messages
    pattern1 = r'print\(\s*f?"?\s*\[([A-Z_]+)\]\s*(.+?(?:"|$))\s*,\s*flush=True\)'
    
    def replace1(match):
        tag = match.group(1)
        message = match.group(2)
        level = detect_log_level(tag, message)
        replacement = f'logger.{level}({message})'
        changes.append((match.group(0), replacement))
        return replacement
    
    content, count1 = re.subn(pattern1, replace1, content)
    
    # Pattern 2: Simple print statements with flush=True
    pattern2 = r'print\(\s*(.+?)\s*,\s*flush=True\)'
    
    def replace2(match):
        message = match.group(1)
        msg_str = str(message).lower()
        
        # Skip if looks like [TAG]
        if '[' in message and ']' in message:
            return match.group(0)
        
        if 'error' in msg_str or 'failed' in msg_str:
            replacement = f'logger.error({message})'
        elif 'warning' in msg_str or 'warn' in msg_str:
            replacement = f'logger.warning({message})'
        else:
            replacement = f'logger.info({message})'
        
        changes.append((match.group(0), replacement))
        return replacement
    
    content, count2 = re.subn(pattern2, replace2, content)
    
    # Pattern 3: Simple print without flush (less common)
    pattern3 = r'print\(\s*(["\'].*?["\'])\s*\)'
    
    def replace3(match):
        message = match.group(1)
        if 'error' in message.lower():
            replacement = f'logger.error({message})'
        else:
            replacement = f'logger.info({message})'
        changes.append((match.group(0), replacement))
        return replacement
    
    content, count3 = re.subn(pattern3, replace3, content)
    
    total_changes = count1 + count2 + count3
    
    if total_changes > 0:
        if apply:
            # Backup original
            backup_file = f"{filename}.backup_{Path(filename).stat().st_mtime:.0f}"
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write converted content
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Converted {total_changes} print() statements")
            print(f"📁 Backup saved to: {backup_file}")
        else:
            print(f"📊 Would convert {total_changes} print() statements:")
            for i, (old, new) in enumerate(changes[:10], 1):
                print(f"\n  {i}. OLD: {old[:60]}...")
                print(f"     NEW: {new[:60]}...")
            if len(changes) > 10:
                print(f"\n  ... and {len(changes) - 10} more")
    else:
        print("✨ No print() statements found to convert")
    
    return total_changes, changes


def main():
    parser = argparse.ArgumentParser(
        description="Convert print() statements to logger calls"
    )
    parser.add_argument(
        '--apply', 
        action='store_true',
        help='Apply changes to file (default: dry-run only)'
    )
    parser.add_argument(
        '--file',
        default='agent.py',
        help='File to convert (default: agent.py)'
    )
    
    args = parser.parse_args()
    
    filename = args.file
    
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        sys.exit(1)
    
    print(f"🔍 Scanning {filename}...")
    print()
    
    if args.apply:
        print("🔄 Applying changes...")
    else:
        print("📋 DRY RUN MODE - no changes will be made")
    
    print()
    count, changes = convert_file(filename, apply=args.apply)
    
    print()
    print("=" * 60)
    if not args.apply and count > 0:
        print("To apply these changes, run:")
        print(f"  python {__file__} --file {filename} --apply")
    print("=" * 60)


if __name__ == '__main__':
    main()
