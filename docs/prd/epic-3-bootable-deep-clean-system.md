# Epic 3 Bootable Deep Clean System

**Epic Goal:** Deliver a bootable ISO with wizard interface for complete system wiping, hardware detection, and certificate generation, using Ubuntu LTS base with nwipe integration and resilient fallback strategies for demo success.

## Implementation Guidelines: Cubic-Based ISO Creation

### Prerequisites & Setup

**Development Environment:**
```bash
# Install Cubic on Ubuntu development machine
sudo add-apt-repository universe
sudo add-apt-repository ppa:cubic-wizard/release
sudo apt update
sudo apt install --no-install-recommends cubic
```

**Base ISO Selection:**
- Ubuntu 22.04 LTS Desktop (ubuntu-22.04.3-desktop-amd64.iso)
- Maintains Microsoft-signed shim for Secure Boot compatibility
- Proven hardware compatibility and driver support

### Step-by-Step ISO Customization Process

**Phase 1: Cubic Project Setup**
1. Launch Cubic: `sudo cubic`
2. Create new project in dedicated workspace folder
3. Select Ubuntu 22.04 LTS Desktop ISO as base
4. Enter chroot environment for customization

**Phase 2: SecureWipe Application Integration**
```bash
# Inside Cubic's chroot terminal
apt update
apt install python3-pip python3-tk nwipe git

# Install Python dependencies
pip3 install cryptography minisign

# Create application directory
mkdir -p /usr/local/securewipe
cp -r /path/to/bootable-iso/src/* /usr/local/securewipe/
chmod +x /usr/local/securewipe/main.py

# Create system integration
ln -s /usr/local/securewipe/main.py /usr/local/bin/securewipe
```

**Phase 3: GUI Auto-Launch Configuration**
```bash
# Create desktop entry for auto-launch
cat > /etc/skel/.config/autostart/SecureWipe.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=SecureWipe Deep Clean
Comment=Complete System Wiping Tool
Exec=/usr/local/securewipe/main.py --fullscreen
Icon=/usr/local/securewipe/assets/icon.png
Terminal=false
Categories=System;Security;
X-GNOME-Autostart-enabled=true
EOF

# Create desktop shortcut
cp /etc/skel/.config/autostart/SecureWipe.desktop /home/ubuntu/Desktop/
chmod +x /home/ubuntu/Desktop/SecureWipe.desktop
```

**Phase 4: System Optimization**
```bash
# Remove unnecessary packages to reduce ISO size
apt remove --purge libreoffice* thunderbird firefox
apt autoremove
apt autoclean

# Configure Plymouth for boot splash
echo 'GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"' >> /etc/default/grub
update-grub
```

### GUI Application Architecture

**Main Interface Design (tkinter-based):**
- **Welcome Screen:** Large "Start Deep Clean" button with SecureWipe branding
- **Device Selection:** Visual device cards with icons (SSD/HDD/USB)
- **Confirmation Dialog:** Red warning with typed confirmation requirement
- **Progress Screen:** Real-time progress bar with nwipe integration
- **Certificate Generation:** Success screen with QR code and USB save option

**Key GUI Components:**
```python
# Example button-driven interface structure
class SecureWipeGUI:
    def create_main_screen(self):
        # Large, prominent action buttons
        start_btn = tk.Button(text="🔥 START DEEP CLEAN", 
                             font=("Arial", 24, "bold"),
                             bg="#d32f2f", fg="white",
                             command=self.show_device_selection)
        
    def create_device_selection(self):
        # Visual device cards with click selection
        for device in detected_devices:
            device_frame = self.create_device_card(device)
            device_frame.bind("<Button-1>", lambda e, d=device: self.select_device(d))
```

### Testing & Validation Framework

**VM Testing Setup:**
```bash
# Create UEFI test environment
qemu-system-x86_64 \
  -enable-kvm -m 4G \
  -drive if=pflash,format=raw,readonly,file=/usr/share/ovmf/OVMF_CODE_4M.fd \
  -drive if=pflash,format=raw,file=test_OVMF_VARS.fd \
  -cdrom securewipe-deep-clean.iso \
  -drive file=test-disk.img,format=raw,if=virtio
```

**Demo Preparation Checklist:**
- [ ] VM snapshot with working ISO saved
- [ ] Test USB devices (8GB, 32GB) prepared
- [ ] GUI launches automatically on boot
- [ ] All buttons respond correctly
- [ ] Certificate generation completes
- [ ] Offline verifier validates certificates

## Story 3.1 Bootable ISO Foundation with Secure Boot Compatibility

As a **user preparing to completely wipe a device for disposal**,  
I want **a bootable ISO that starts reliably with Secure Boot enabled**,  
so that **I can perform complete system wiping on modern hardware without BIOS modifications**.

### Acceptance Criteria
1. **Cubic-based Ubuntu 22.04 LTS customization** with preserved Microsoft signatures
2. **Auto-launching GUI application** with fullscreen wizard interface
3. **Click-driven navigation** - no command-line interaction required
4. **UEFI/Secure Boot compatibility** tested in OVMF VM environment
5. **Professional boot experience** with custom Plymouth splash screen
6. **Optimized ISO size** under 1.5GB through package removal
7. **VM snapshot fallback** saved for guaranteed demo success
8. **Hardware compatibility** validated on Intel/AMD platforms

### Technical Implementation
- **Base:** Ubuntu 22.04.3 Desktop ISO (proven Secure Boot support)
- **Customization Tool:** Cubic for chroot-based modification
- **GUI Framework:** tkinter for zero-dependency interface
- **Auto-launch:** XDG autostart integration for immediate GUI presentation
- **Boot Configuration:** GRUB with quiet splash for professional appearance

## Story 3.2 Hardware Detection with nwipe Integration

As a **user about to perform complete system wiping**,  
I want **reliable storage device detection and selection through visual interface**,  
so that **I can safely identify and wipe the correct devices using simple clicks**.

### Acceptance Criteria
1. **Visual device cards** showing device type icons (SSD/HDD/USB)
2. **Click-to-select interface** with highlighted selection feedback
3. **Device information display** - size, model, connection type
4. **Smart device categorization** using nwipe's hardware detection
5. **Multi-step click confirmations** with prominent warning dialogs
6. **Typed confirmation requirement** - user must type "DELETE" to proceed
7. **Encrypted drive detection** with clear limitation warnings
8. **Emergency stop button** always visible during operations

### GUI Design Specifications
- **Device Cards:** 200x150px cards with device icons and key info
- **Selection Feedback:** Blue border highlight on selected devices
- **Confirmation Dialog:** Red-themed modal with large warning text
- **Progress Integration:** Real-time nwipe progress in GUI progress bar
- **Safety Features:** Confirmation dialogs require explicit user action

## Story 3.3 Beautiful Wizard Interface with Resilient Fallback

As a **non-technical user performing complete device wiping**,  
I want **an intuitive, beautiful interface with automatic fallback capabilities**,  
so that **I can complete the operation with confidence regardless of hardware issues**.

### Acceptance Criteria
1. **Modern GUI wizard** with professional styling and large, clear buttons
2. **Step-by-step navigation** with progress indicators and back/next buttons
3. **Automatic GUI health check** on startup with fallback detection
4. **Graceful TUI fallback** using nwipe's interface if GUI fails
5. **Consistent user experience** - same safety checks in both modes
6. **Visual feedback** - button hover effects, loading animations
7. **Accessibility features** - high contrast mode, large text options
8. **Touch-friendly design** for tablet/touchscreen compatibility

### Interface Design Elements
- **Color Scheme:** Professional blue/white with red warning accents
- **Typography:** Large, readable fonts (minimum 14pt)
- **Button Design:** Rounded corners, clear labels, hover effects
- **Layout:** Centered content with generous whitespace
- **Icons:** Intuitive device and action icons throughout interface

## Story 3.4 Complete System Wiping with Certificate Generation

As a **user completing device disposal preparation**,  
I want **reliable wiping with beautiful certificate generation interface**,  
so that **I have professional verification documents with simple click-to-save functionality**.

### Acceptance Criteria
1. **Real-time progress display** with nwipe integration and visual progress bar
2. **Demo-optimized timing** - 5-10 minute wipe cycles on small test devices
3. **Beautiful certificate display** with QR code and professional formatting
4. **One-click USB save** - "Save Certificate to USB" button
5. **Dual cryptography support** - pyca/cryptography primary, minisign fallback
6. **Success celebration screen** with checkmarks and completion summary
7. **Offline verification demo** - separate verifier app with green/red validation
8. **Emergency demo fallback** - pre-recorded wipe sequence if hardware fails

### Certificate Interface Design
- **Success Screen:** Large green checkmark with "Wipe Complete" message
- **Certificate Preview:** Professional document layout with SecureWipe branding
- **QR Code Display:** Large, scannable QR code for mobile verification
- **Save Options:** Prominent "Save to USB" and "Print Certificate" buttons
- **Verification Demo:** Separate screen showing offline verifier in action

### Demo Preparation Strategy
- **Primary Demo:** Live wipe of 8GB USB drive (estimated 3-5 minutes)
- **Backup Demo:** Pre-recorded wipe sequence with certificate generation
- **Verification Demo:** Offline verifier showing green validation checkmark
- **Fallback Assets:** Screenshots and video of complete process
