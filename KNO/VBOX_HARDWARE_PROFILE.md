# VIRTUALBOX HARDWARE PROFILE FOR KNO V2

## Recommended VM Specification

### CPU & Memory
```
RAM:          4 GB (4096 MB minimum)
CPU Cores:    2 cores
CPU Cap:      100% (no limit)
Execution Cap: Disabled (full speed VM)
```

### Storage
```
Disk Size:    40 GB (sparse, grows on demand for logs/models)
Bus Type:     SATA Controller
```

### Display & Graphics
```
Graphics Controller: VMSVGA (supports 3D acceleration for Blade Runner UI)
Video Memory:       128 MB
Display Resolution: 1920x1080 (or host resolution)
3D Acceleration:    Enabled
Clipboard Sharing:  Bidirectional (Windows ↔ KNO-OS)
Drag & Drop:        Bidirectional
```

### Network
```
Network Type:       Bridged Adapter
Adapter:            Intel PRO/1000 MT Desktop (PCnet-PCI II also compatible)
Promiscuous Mode:   Allow VMs
Bridged Interface:  (Select host's primary network adapter:
                     - Ethernet: for wired connection
                     - Wi-Fi: for wireless connection)
```

### I/O Devices
```
USB:                USB 3.0 Controller (for potential hardware integration)
Audio:              Intel HD Audio (disable if running headless)
Serial Port:        Disabled
Parallel Port:      Disabled
```

### System Features
```
Chipset:            PIIX3
ACPI:               Enabled
EFI:                Disabled (BIOS mode for stability)
TPM:                Optional (disabled by default)
Secure Boot:        Disabled
```

## VirtualBox Configuration Steps

### 1. **Create the VM**
```bash
VBoxManage createvm \
  --name "KNO_V2_Appliance" \
  --ostype "Windows" \
  --basefolder "$VBOX_VMS" \
  --register
```

### 2. **Configure Hardware**
```bash
VBoxManage modifyvm "KNO_V2_Appliance" \
  --memory 4096 \
  --cpus 2 \
  --graphicscontroller vmsvga \
  --vram 128 \
  --clipboard bidirectional \
  --draganddrop bidirectional

VBoxManage createhd \
  --filename "KNO_V2_Appliance.vdi" \
  --size 40960

VBoxManage storagectl "KNO_V2_Appliance" \
  --name "SATA Controller" \
  --add sata

VBoxManage storageattach "KNO_V2_Appliance" \
  --storagectl "SATA Controller" \
  --port 0 \
  --device 0 \
  --type hdd \
  --medium "KNO_V2_Appliance.vdi"
```

### 3. **Configure Network (Bridged)**
```bash
VBoxManage modifyvm "KNO_V2_Appliance" \
  --nic1 bridged \
  --bridgeadapter1 "{Ethernet Adapter Name or Wi-Fi Name}"
```

### 4. **Attach Installation Media (Windows ISO)**
```bash
VBoxManage storageattach "KNO_V2_Appliance" \
  --storagectl "SATA Controller" \
  --port 1 \
  --device 0 \
  --type dvddrive \
  --medium "/path/to/Windows.iso"
```

### 5. **Start the VM**
```bash
VBoxManage startvm "KNO_V2_Appliance" --type gui
# Or headless:
VBoxManage startvm "KNO_V2_Appliance" --type headless
```

## Post-Installation Setup

After Windows (or Linux guest) is installed on the VM:

### 1. **Install VBoxGuestAdditions**
```bash
# Copy and run the helper script inside the VM:
python prepare_vbox_env.py --setup
```

This will:
- Detect VirtualBox environment
- Install VBoxGuestAdditions (enables clipboard, shared folders, 3D)
- Verify bridged networking
- Test internet connectivity to Gemini

### 2. **Configure Shared Folders (Optional)**
In VirtualBox GUI:
- VM Settings → Shared Folders
- Add folder pointing to `A:\KNO` (or guest mount point)
- Enable Auto-mount
- Enable Make Permanent

### 3. **Clipboard Bridge Test**
```bash
python prepare_vbox_env.py --clipboard-test
```

This will:
- Test Windows clipboard read
- Verify bidirectional sync works
- Enable KNO to read errors from host and solve them inside VM

## Network Gateway Details

### Bridged Networking Benefits
- **Direct Internet Access**: KNO can reach Gemini API without port forwarding
- **Windows Firewall Transparent**: Guest VM appears as separate device on network
- **Peer-to-Peer**: Host can SSH/RDP into guest VM directly (if enabled)
- **Shared Network Resources**: Access Windows network shares, printers, etc.

### Bridged Networking Configuration
1. **Windows Host**: Ensure primary network is active (Ethernet or Wi-Fi)
2. **VBox Settings**: Set Adapter Type to "Bridged"
3. **Select Bridge Interface**: Choose the active host adapter (usually auto-detected)
4. **Guest IP Assignment**: DHCP or static IP on same subnet as host
5. **Firewall**: Windows Firewall on guest can be enabled/disabled independently

### Test Bridged Network
Inside VM:
```bash
# Check IP address (should be same subnet as host)
ipconfig

# Ping host gateway
ping 8.8.8.8

# Test DNS
nslookup generativelanguage.googleapis.com
```

## Clipboard Integration Details

### How It Works
1. **VBoxGuestAdditions** enables clipboard daemon in guest OS
2. **VirtualBox Host Service** syncs clipboard between Windows and guest
3. **KNO_V2 Listener** (via tkinter) reads from guest clipboard
4. **Error Workflow**: User copies Windows error → KNO reads it → Solves autonomously

### Example: Copy Error from Windows, Solve in VM
```
Windows:
  1. Copy error dialog text from application
  2. Ctrl+C

VM (KNO_V2):
  1. SelfEvolutionThread detects error event (Python exception)
  2. Calls VisionModule.capture_screenshot()
  3. Calls Clipboard.get_windows_text()
  4. Sends both to Gemini for analysis
  5. Returns ActionExecutor.click() commands to fix UI
```

## Hardware Acceleration (VMSVGA)

### Benefits
- **3D Graphics**: Blade Runner UI renders with transparency/shadows
- **Hardware Acceleration**: Offloads to host GPU
- **Better Performance**: Smoother animations and visual effects

### Enabling 3D Acceleration
- VirtualBox GUI → VM Settings → Display → Enable 3D Acceleration ✓
- Video RAM: Set to 128 MB or higher
- Requires VMSVGA controller (not VGA or QXL)

## Troubleshooting

### Clipboard Not Syncing
```
Solution:
1. Ensure VBoxGuestAdditions is installed
2. Restart clipboard daemon: services.msc → VBox guest device
3. Verify VM Settings → General → Clipboard = Bidirectional
```

### Network Bridged But No IP
```
Solution:
1. Enable DHCP on guest or set static IP on same subnet as host
2. Disable Windows Firewall temporarily to test
3. Check host network adapter is active (Ethernet/Wi-Fi)
4. Run: ipconfig /release && ipconfig /renew
```

### Slow Graphics Performance
```
Solution:
1. Increase Allocated Video RAM (Settings → Display)
2. Enable 3D Acceleration (Settings → Display → Enable 3D Acceleration)
3. Set Graphics Controller to VMSVGA (not VGA)
4. Allocate more CPU cores to VM (Settings → System → CPU)
```

### VBoxGuestAdditions Installation Hangs
```
Solution:
1. Insert VBoxGuestAdditions CD (Devices → Insert Guest Additions CD)
2. Run installer manually: D:\VBoxWindowsAdditions.exe /S
3. Or use prepare_vbox_env.py --setup (requires Admin)
4. Reboot after installation completes
```

## Security Notes

### Bridged Networking Considerations
- VM is directly on host network (like a second computer)
- Both host and guest are exposed to each other's traffic
- Use Windows Firewall on guest to restrict inbound connections
- Configure Strong passwords for any guest services (SSH, RDP)

### Clipboard Sharing Risks
- Windows clipboard passes to VM unencrypted over VBox channel
- Avoid copying sensitive credentials to clipboard when KNO is watching
- KNO logs clipboard content to `logs/kno_v2.log` for debugging

### Shared Folders Permissions
- If using shared folders, files inherit host permissions
- Guest process runs with guest OS security context
- Set restrictive NTFS permissions on shared folders if sensitive data

## Performance Tuning

### For Optimal AI Workloads
```
Recommended Settings:
- RAM:             8 GB (if host has >12 GB available)
- CPU Cores:       4 cores (if host has 6+ cores)
- Disk:            SSD with 50+ GB free space
- Network:         1 Gbps bridged connection (auto-detected)
```

### Monitoring Performance
Inside VM:
```bash
# CPU/Memory usage
tasklist /v

# Disk I/O
perfmon  # (Performance Monitor)

# Network throughput
netsh interface tcp show stats
```

## Next Steps

1. **Create VM** using commands in Section 2
2. **Install Windows/Linux** guest OS
3. **Copy KNO_V2.py** and dependencies to guest
4. **Run prepare_vbox_env.py --setup**
5. **Launch KNO_V2.py** to start the AI appliance

---

**Generated**: 2026-02-18  
**KNO Version**: V2  
**VirtualBox Version**: 7.0+ recommended
