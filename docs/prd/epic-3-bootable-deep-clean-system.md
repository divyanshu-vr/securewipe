# Epic 3 Bootable Deep Clean System

**Epic Goal:** Deliver a bootable ISO with wizard interface for complete system wiping, hardware detection, and certificate generation, using Ubuntu LTS base with nwipe integration and resilient fallback strategies for demo success.

## Story 3.1 Bootable ISO Foundation with Secure Boot Compatibility

As a **user preparing to completely wipe a device for disposal**,  
I want **a bootable ISO that starts reliably with Secure Boot enabled**,  
so that **I can perform complete system wiping on modern hardware without BIOS modifications**.

### Acceptance Criteria
1. Ubuntu LTS live ISO base with Microsoft-signed shim for Secure Boot compatibility
2. Minimal customization approach - add SecureWipe app and dependencies only
3. ISO boots successfully in UEFI VM with OVMF/EDK2 firmware
4. VM snapshot saved as guaranteed demo fallback
5. Tested on Intel iGPU and AMD/NVMe platforms by day 3
6. Fallback BIOS compatibility maintained for older hardware
7. ISO size under 2GB for standard USB drive compatibility

## Story 3.2 Hardware Detection with nwipe Integration

As a **user about to perform complete system wiping**,  
I want **reliable storage device detection and selection**,  
so that **I can safely identify and wipe the correct devices without accidents**.

### Acceptance Criteria
1. nwipe integration for disk-level operations and device listing
2. Manual device selection with clear device IDs and confirmation
3. Multi-step confirmations with device name echo and typed "DELETE" confirmation
4. SSD vs HDD detection using nwipe's hardware identification
5. Encrypted drive warnings with clear limitation explanations
6. Conservative defaults - show warnings rather than guessing capabilities
7. Device verification working on VM and two test platforms by day 5

## Story 3.3 Resilient Wizard Interface with TUI Fallback

As a **non-technical user performing complete device wiping**,  
I want **a simple interface that works even if graphics fail**,  
so that **I can complete the operation regardless of hardware issues**.

### Acceptance Criteria
1. GUI wizard interface tested early in live environment
2. TUI fallback using nwipe's ncurses interface for constrained environments
3. Automatic fallback to text mode if GUI fails to render
4. Same confirmation flow and safety checks in both GUI and TUI modes
5. Clear navigation and progress indicators in both interfaces
6. Plain-language explanations and device identification
7. Emergency stop functionality available throughout process

## Story 3.4 Complete System Wiping with Dual Cryptography Support

As a **user completing device disposal preparation**,  
I want **reliable wiping with cryptographic proof using fallback signing methods**,  
so that **I have verifiable evidence regardless of library compatibility issues**.

### Acceptance Criteria
1. nwipe integration for NIST-compliant wiping methods with progress display
2. Demonstration on small USB/NVMe devices (5-10 minute demo window)
3. JSON certificate generation using shared schema with schemaVersion field
4. Primary: pyca/cryptography for RSA signing when wheels available
5. Fallback: minisign (Ed25519) for portable signing if OpenSSL issues occur
6. Certificate saved to external USB with offline verification capability
7. Pre-recorded wipe sequence as ultimate demo fallback
8. Success validation: signed JSON + offline verifier green check by day 10
