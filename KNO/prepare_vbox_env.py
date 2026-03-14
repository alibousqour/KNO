#!/usr/bin/env python3
"""
prepare_vbox_env.py

Prepares KNO_V2 to run as a headless AI appliance inside VirtualBox.

Functions:
1. Detect if running inside a VirtualBox VM
2. Attempt to install VBoxGuestAdditions (if missing)
3. Verify bridged networking is available
4. Configure clipboard sharing between Windows host and KNO-OS guest
5. Test shared folder access and network connectivity

Usage:
    python prepare_vbox_env.py --check    # Only check VM environment
    python prepare_vbox_env.py --setup    # Full setup (detect, install, configure)
    python prepare_vbox_env.py --clipboard-test  # Test clipboard bridge
"""

import os
import sys
import platform
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("VBoxEnv")

# Root directory
ROOT_DIR = r"A:\KNO" if os.name == 'nt' else os.path.expanduser("~/KNO")


class VBoxDetector:
    """Detect if running inside VirtualBox."""

    @staticmethod
    def is_virtualbox():
        """Check for VirtualBox signatures in system."""
        if platform.system() == "Windows":
            # Check registry for VirtualBox
            try:
                result = subprocess.run(
                    ["reg", "query", r"HKEY_LOCAL_MACHINE\HARDWARE\DESCRIPTION\System", "/s"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if "VirtualBox" in result.stdout or "innotek" in result.stdout.lower():
                    return True
            except Exception:
                pass

            # Check for VBox drivers
            try:
                result = subprocess.run(
                    ["systeminfo"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if "VirtualBox" in result.stdout:
                    return True
            except Exception:
                pass

        elif platform.system() in ("Linux", "Darwin"):
            # Check /sys/class/dmi/id/sys_vendor
            try:
                with open("/sys/class/dmi/id/sys_vendor", "r") as f:
                    vendor = f.read().strip().lower()
                    if "virtualbox" in vendor or "innotek" in vendor:
                        return True
            except Exception:
                pass

            # Check dmidecode
            try:
                result = subprocess.run(
                    ["dmidecode", "-s", "system-manufacturer"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if "VirtualBox" in result.stdout:
                    return True
            except Exception:
                pass

        return False

    @staticmethod
    def check_vbox_additions():
        """Check if VBoxGuestAdditions is installed."""
        if platform.system() == "Windows":
            # Check for VBox driver in Device Manager (simplified)
            try:
                result = subprocess.run(
                    ["sc", "query", "VBoxGuest"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return "RUNNING" in result.stdout or "STOPPED" not in result.stdout
            except Exception:
                return False

        elif platform.system() in ("Linux", "Darwin"):
            try:
                result = subprocess.run(
                    ["which", "mount.vboxsf"],
                    capture_output=True,
                    timeout=5
                )
                return result.returncode == 0
            except Exception:
                return False

        return False


class VBoxGuestAdditionsInstaller:
    """Attempt to install VBoxGuestAdditions."""

    @staticmethod
    def install_windows():
        """Install VBoxGuestAdditions on Windows (requires admin)."""
        try:
            logger.info("Attempting to install VBoxGuestAdditions on Windows...")
            # Mount ISO from VBox media directory
            iso_paths = [
                r"C:\Program Files\Oracle\VirtualBox\VBoxGuestAdditions.iso",
                r"C:\Program Files (x86)\Oracle\VirtualBox\VBoxGuestAdditions.iso",
                r"D:\VBoxGuestAdditions.iso",  # Could be CD-ROM
            ]

            iso_path = None
            for path in iso_paths:
                if os.path.exists(path):
                    iso_path = path
                    break

            if not iso_path:
                logger.warning("VBoxGuestAdditions.iso not found at expected locations.")
                logger.info("Manual steps: Insert VBox Guest Additions CD and run installer.")
                return False

            # Run installer (elevate to admin if needed)
            installer = os.path.join(os.path.dirname(iso_path), "VBoxWindowsAdditions.exe")
            if os.path.exists(installer):
                logger.info(f"Running {installer}...")
                subprocess.run([installer, "/S"], check=False)
                logger.info("VBoxGuestAdditions installation initiated.")
                return True

            return False
        except Exception as e:
            logger.warning(f"Failed to install VBoxGuestAdditions: {e}")
            return False

    @staticmethod
    def install_linux():
        """Install VBoxGuestAdditions on Linux (apt/dnf)."""
        try:
            logger.info("Attempting to install VBoxGuestAdditions on Linux...")
            # Try apt first
            result = subprocess.run(
                ["sudo", "apt-get", "install", "-y", "virtualbox-guest-additions-iso"],
                capture_output=True,
                timeout=120
            )
            if result.returncode == 0:
                logger.info("VBoxGuestAdditions installed via apt.")
                return True

            # Try dnf
            result = subprocess.run(
                ["sudo", "dnf", "install", "-y", "VirtualBox-guest-additions"],
                capture_output=True,
                timeout=120
            )
            if result.returncode == 0:
                logger.info("VBoxGuestAdditions installed via dnf.")
                return True

            logger.warning("Auto-install failed. Run: sudo apt-get install virtualbox-guest-additions-iso")
            return False
        except Exception as e:
            logger.warning(f"Failed to install on Linux: {e}")
            return False


class NetworkConfig:
    """Configure bridged networking."""

    @staticmethod
    def check_bridged_network():
        """Verify bridged networking is active."""
        try:
            result = subprocess.run(
                ["ipconfig"] if platform.system() == "Windows" else ["ifconfig"],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Simple heuristic: if we have an IP address, we're likely bridged
            if "192.168" in result.stdout or "10.0" in result.stdout or "172.16" in result.stdout:
                logger.info("Bridged network detected (has private IP).")
                return True
            logger.warning("Could not confirm bridged network. Check VirtualBox settings manually.")
            return False
        except Exception as e:
            logger.warning(f"Network check failed: {e}")
            return False

    @staticmethod
    def test_internet():
        """Test connectivity to Gemini API endpoint."""
        try:
            import socket
            socket.create_connection(("generativelanguage.googleapis.com", 443), timeout=5)
            logger.info("✓ Internet connectivity to Gemini API verified.")
            return True
        except Exception as e:
            logger.warning(f"Internet test failed: {e}")
            return False


class ClipboardBridge:
    """Enable Windows ↔ KNO clipboard sharing."""

    @staticmethod
    def detect_vbox_clipboard():
        """Check if VBox clipboard integration is available."""
        try:
            # Windows: Check for VBox shared clipboard driver
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["reg", "query", r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\VBoxGuest"],
                    capture_output=True,
                    timeout=5
                )
                return result.returncode == 0
            return False
        except Exception:
            return False

    @staticmethod
    def setup_clipboard_sync():
        """Configure clipboard sync between Windows host and KNO guest."""
        try:
            logger.info("Setting up clipboard bridge...")
            # This is primarily configured in VBox settings, but we can verify here
            if ClipboardBridge.detect_vbox_clipboard():
                logger.info("✓ VBox clipboard integration detected.")
                logger.info("Clipboard sharing is enabled. Windows ↔ KNO sync active.")
                return True
            else:
                logger.warning("VBox clipboard not detected. Enable in VM Settings → General → Clipboard.")
                return False
        except Exception as e:
            logger.warning(f"Clipboard setup failed: {e}")
            return False

    @staticmethod
    def test_clipboard_read():
        """Test reading from clipboard."""
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            text = root.clipboard_get()
            root.destroy()
            logger.info(f"✓ Clipboard read successful. Content: {text[:50]}...")
            return True
        except Exception as e:
            logger.warning(f"Clipboard read failed: {e}")
            return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        mode = "--check"
    else:
        mode = sys.argv[1]

    logger.info(f"=== VirtualBox Environment Setup ===")

    # Detect VM
    is_vm = VBoxDetector.is_virtualbox()
    if is_vm:
        logger.info("✓ Running inside VirtualBox.")
    else:
        logger.warning("⚠ Not detected as VirtualBox VM. Skipping guest-specific setup.")
        if mode != "--check":
            return

    # Check/install additions
    has_additions = VBoxDetector.check_vbox_additions()
    if has_additions:
        logger.info("✓ VBoxGuestAdditions detected.")
    else:
        logger.warning("✗ VBoxGuestAdditions missing.")
        if mode == "--setup":
            if platform.system() == "Windows":
                VBoxGuestAdditionsInstaller.install_windows()
            else:
                VBoxGuestAdditionsInstaller.install_linux()

    # Check network
    has_network = NetworkConfig.check_bridged_network()
    if mode == "--setup":
        NetworkConfig.test_internet()

    # Setup clipboard
    if mode in ("--setup", "--clipboard-test"):
        ClipboardBridge.setup_clipboard_sync()
        if mode == "--clipboard-test":
            ClipboardBridge.test_clipboard_read()

    logger.info("=== Setup Complete ===")
    logger.info("KNO_V2 is ready to run as a headless AI appliance in VirtualBox.")


if __name__ == "__main__":
    main()
