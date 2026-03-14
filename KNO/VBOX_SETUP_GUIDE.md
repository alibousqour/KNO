# KNO V2 VirtualBox Headless Appliance - Setup Guide

## Quick Start: Deploy KNO V2 in VirtualBox

This document provides step-by-step instructions to run KNO V2 as a standalone AI appliance inside VirtualBox with full integration between Windows host and the guest VM.

---

## Prerequisites

- **Windows Host**: Windows 10/11 with VirtualBox 7.0+
- **Guest OS**: Windows 10/11 or Linux (Ubuntu 20.04+)
- **Host Network**: Ethernet or Wi-Fi with internet access
- **Storage**: 50 GB free space on host for VM
- **RAM**: Host with 8 GB+ RAM (4 GB allocated to VM)

---

## Part 1: Create the KNO_V2 Virtual Machine

### Option A: Using VirtualBox GUI

1. **Open VirtualBox** and click "New"
   - Name: `KNO_V2_Appliance`
   - Machine Folder: `C:\VMs\` (or your preferred location)
   - ISO Image: Windows 10/11 or Ubuntu 20.04 ISO
   - Type: Windows or Linux (as chosen)
   - Skip Unattended Install (for now)

2. **Hardware Configuration**
   - Memory: **4096 MB** (4 GB)
   - Processors: **2 cores**
   - Enable 3D Acceleration: ✓

3. **Storage Configuration**
   - Virtual Hard Disk Size: **40 GB**
   - Select "VDI" format
   - Dynamic allocation: ✓ (grows on demand)

4. **Display**
   - Graphics Controller: **VMSVGA** (not VGA)
   - Video Memory: **128 MB**

5. **Network**
   - Adapter 1: **Bridged Adapter**
   - Select your active network (Ethernet or Wi-Fi)

6. **Shared Clipboard & Drag-Drop**
   - General → Shared Clipboard: **Bidirectional**
   - Drag and Drop: **Bidirectional**

7. **Finish** and Boot the VM

### Option B: Using Command Line

```bash
# Create VM
VBoxManage createvm --name "KNO_V2_Appliance" --ostype Windows10 --register

# Configure hardware
VBoxManage modifyvm "KNO_V2_Appliance" ^
  --memory 4096 ^
  --cpus 2 ^
  --graphicscontroller vmsvga ^
  --vram 128 ^
  --clipboard bidirectional ^
  --draganddrop bidirectional

# Create and attach disk
VBoxManage createhd --filename "C:\VMs\KNO_V2.vdi" --size 40960
VBoxManage storagectl "KNO_V2_Appliance" --name "SATA" --add sata
VBoxManage storageattach "KNO_V2_Appliance" --storagectl "SATA" --port 0 --device 0 --type hdd --medium "C:\VMs\KNO_V2.vdi"

# Configure network
VBoxManage modifyvm "KNO_V2_Appliance" --nic1 bridged --bridgeadapter1 "Ethernet"

# Attach ISO
VBoxManage storageattach "KNO_V2_Appliance" --storagectl "SATA" --port 1 --device 0 --type dvddrive --medium "C:\Windows.iso"

# Start VM
VBoxManage startvm "KNO_V2_Appliance"
```

---

## Part 2: Install Guest OS Inside VM

1. **Boot VM** and follow Windows/Linux installation
2. **Complete Installation** with default settings
3. **Restart VM** after OS setup completes

---

## Part 3: Set Up VBoxGuestAdditions

VBoxGuestAdditions enables:
- **Clipboard sharing** (copy from Windows, paste in VM)
- **Shared folders** (access host files)
- **3D acceleration** (smooth Blade Runner UI)
- **Mouse integration** (seamless cursor movement)

### For Windows Guest

1. **Inside VM**, open VirtualBox menu
2. **Devices → Insert Guest Additions CD Image**
3. **Run installer**: `D:\VBoxWindowsAdditions.exe /S`
4. **Reboot VM**

OR use the automated helper:

```cmd
# Copy the helper script to VM
python prepare_vbox_env.py --setup

# Or manual install (requires Admin):
cd D:\
VBoxWindowsAdditions.exe /S
```

### For Linux Guest (Ubuntu)

```bash
# Inside VM
sudo apt-get update
sudo apt-get install -y virtualbox-guest-additions-iso
sudo reboot
```

---

## Part 4: Configure Network (Bridged Adapter)

### Verify Bridged Network Access

**Inside VM**, open Command Prompt and run:

```cmd
# Check IP address (should be on same subnet as host)
ipconfig

# Test DNS resolution
nslookup generativelanguage.googleapis.com

# Ping gateway (8.8.8.8)
ping 8.8.8.8 -c 4
```

**Expected Output**:
- IP Address: `192.168.x.x` or `10.x.x.x` (same as host)
- DNS resolves Google servers
- Ping returns responses (no timeouts)

If you see "unreachable" or no IP, check:
1. **Host network is active** (Ethernet/Wi-Fi connected)
2. **VM is connected to bridged adapter** (Devices → Network → Bridged Adapter)
3. **Run ipconfig /release && ipconfig /renew** in guest

---

## Part 5: Copy KNO_V2 to Guest VM

### Option A: Using Shared Folder

1. **On Windows Host** → VirtualBox Settings
   - Shared Folders → Add New
   - Folder Path: `A:\KNO`
   - Folder Name: `KNO`
   - Auto-mount: ✓

2. **Inside VM**, mount shared folder:
   ```bash
   # Windows: folder appears as network drive
   # Linux: sudo mount -t vboxsf KNO /mnt/kno
   ```

### Option B: Using SCP or Git Clone

```bash
# If SSH enabled on host:
scp -r A:\KNO guest@<VM_IP>:~/KNO_V2

# Or git clone:
git clone https://github.com/yourusername/KNO.git
cd KNO
```

---

## Part 6: Install KNO Dependencies Inside VM

```bash
# Inside VM
cd ~/KNO_V2  # or your KNO directory

# Install packages
pip install -r requirements.txt

# If packages fail, auto-install via prepare_vbox_env:
python prepare_vbox_env.py --setup
```

---

## Part 7: Configure Google Gemini API Key

1. **Get API Key** from Google Cloud Console
   - https://generativeai.google.com/
   - Create API key for Gemini 1.5 Flash

2. **Add to config.json** inside VM:
   ```json
   {
     "GOOGLE_API_KEY": "YOUR_API_KEY_HERE",
     "VISION_ENABLED": true,
     "LOG_LEVEL": "INFO",
     "FAILSAFE_CORNERS": true
   }
   ```

3. **Verify API Access**:
   ```bash
   python -c "import requests; r = requests.post('https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent', json={'contents':[{'parts':[{'text':'test'}]}]}, headers={'x-goog-api-key': 'YOUR_KEY'}, timeout=10); print('API OK' if r.status_code == 200 else f'Error: {r.status_code}')"
   ```

---

## Part 8: Boot KNO V2

```bash
# Inside VM, in the KNO directory
python KNO_V2.py
```

You should see:
```
[INFO] Starting KNO_V2
[INFO] VirtualBox environment helper found. Running pre-flight check...
[INFO] VirtualBox environment check passed.
[INFO] ResourceManager: Creating directories...
[INFO] Checking dependencies...
[INFO] HigherIntelligenceBridge: API key loaded
[INFO] VisionModule: PIL ImageGrab available
[INFO] ActionExecutor: pyautogui available
[INFO] SelfEvolutionThread: background worker started
[INFO] [SYSTEM] KNO V2 ONLINE. VISION MODULE STANDING BY.
```

GUI Window opens with:
- **Status**: Ready
- **Visual Perception**: Eye indicator (grey = off, amber = on)
- **Direct Action Console**: Shows mouse clicks, keyboard events
- **Toggle Eye**: Enable vision mode (screenshots + Gemini analysis)
- **Press Esc**: Emergency stop (disables vision + actions)

---

## Part 9: Clipboard Integration Test

### Copy Error from Windows, Solve in VM

1. **On Windows Host**:
   - Open any application with an error
   - Copy error message to clipboard (Ctrl+C)

2. **Inside VM (KNO_V2 running)**:
   - ClipboardMonitor detects change
   - Queues error to SelfEvolutionThread
   - Logs: `Error-like content detected in clipboard. Queueing for analysis.`
   - Sends screenshot + clipboard text to Gemini
   - Returns fix: click button, type command, etc.
   - ActionExecutor executes fix

3. **Verify Integration**:
   ```bash
   python prepare_vbox_env.py --clipboard-test
   ```

---

## Part 10: Secure the VM (Optional)

### Windows Firewall in VM

```cmd
# Allow inbound RDP (if you want to remote in)
netsh advfirewall firewall add rule name="RDP" dir=in action=allow protocol=tcp localport=3389

# Allow inbound SSH (if SSH installed)
netsh advfirewall firewall add rule name="SSH" dir=in action=allow protocol=tcp localport=22
```

### Linux Ubuntu in VM

```bash
# Install UFW and configure
sudo apt-get install -y ufw
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 3389/tcp # RDP if using rdesktop
sudo ufw enable
```

---

## Troubleshooting

### "Clipboard not syncing"
- **Fix**: Reboot VM after VBoxGuestAdditions install
- Verify: VM Settings → General → Clipboard = Bidirectional
- Check: `prepare_vbox_env.py --clipboard-test`

### "No network bridge available"
- **Fix**: Check VirtualBox → Settings → Network → Adapter Type = "Bridged"
- Select correct host interface (Ethernet or Wi-Fi)
- Run in guest: `ipconfig` → should show IP on same subnet as host

### "KNO_V2.py won't start"
- **Fix**: Verify all dependencies installed: `pip install -r requirements.txt`
- Run: `python prepare_vbox_env.py --setup`
- Check logs: `tail -f logs/kno_v2.log`

### "Gemini API returns 401 Unauthorized"
- **Fix**: Verify API key in `config.json`
- Confirm API key is valid at https://generativeai.google.com/
- Check network access: `ping generativelanguage.googleapis.com`

### "GUI is slow or laggy"
- **Fix**: Increase VM CPUs (Settings → System → CPU)
- Enable 3D Acceleration (Settings → Display)
- Increase VRAM to 256 MB (Settings → Display → Video Memory)

---

## Advanced: Snapshots & Recovery

### Create a Snapshot Before First Boot

```bash
VBoxManage snapshot "KNO_V2_Appliance" take "baseline" --description "Clean OS install before KNO_V2"
```

### Restore from Snapshot if Issues Occur

```bash
VBoxManage snapshot "KNO_V2_Appliance" restore "baseline"
```

---

## Next Steps

1. **Test Vision Module**: Toggle Eye in GUI → screenshots appear in `A:\KNO\temp_vision\`
2. **Test Actions**: Click GUI button → ActionExecutor logs coordinates
3. **Test Error Recovery**: Cause Python error → See SelfEvolutionThread investigate
4. **Test Clipboard**: Copy Windows error → Query Gemini for fix
5. **Test Emergency Stop**: Press Esc → Vision + Actions disabled

---

## Performance Baseline

With recommended spec (4GB RAM, 2 CPU, VMSVGA):
- **Boot time**: ~30 seconds
- **KNO_V2 startup**: ~5 seconds
- **First screenshot**: ~2 seconds
- **Gemini query**: ~3-5 seconds
- **Direct actions** (click, type): <100ms

---

## Support & Logs

KNO_V2 logs to:
- **Console**: Real-time output (INFO level)
- **File**: `A:\KNO\logs\kno_v2.log` (detailed timestamps)
- **Screenshots**: `A:\KNO\temp_vision\shot_*.png` (timestamped)
- **Evolution**: `A:\KNO\logs\evolution.log` (AI changes)

Check logs for debugging:
```bash
tail -f A:\KNO\logs\kno_v2.log
```

---

**Generated**: 2026-02-18  
**For**: KNO V2 Headless Appliance in VirtualBox  
**Last Updated**: February 2026
