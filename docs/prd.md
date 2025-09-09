# SecureWipe Product Requirements Document (PRD)

## Goals and Background Context

### Goals

• Win SIH Hackathon through compelling demo showcasing both Quick Clean and Deep Clean modes
• Enable confident device disposal for individual users without data security fears  
• Provide verifiable proof of complete data erasure through cryptographically signed certificates
• Address India's ₹50,000 crore IT asset hoarding problem with user-friendly solution
• Demonstrate successful parallel team development (3+3 split) with integrated final product
• Achieve 95%+ user completion rate with anxiety-reducing UX and safe defaults

### Background Context

SecureWipe addresses a critical barrier preventing safe IT asset recycling in India. With over 1.75 million tonnes of annual e-waste and ₹50,000+ crore worth of IT assets hoarded due to data security fears, existing solutions create more problems than they solve. Current tools like DBAN require technical expertise, while simple solutions like CCleaner lack verification capabilities. This creates a trust deficit where millions of functional devices remain unused rather than entering the circular economy.

The solution transforms data wiping from a technical nightmare into a trustworthy experience through dual-mode approach: desktop "Quick Clean" for user folders and bootable "Deep Clean" for complete system preparation. Unlike existing tools that prioritize either simplicity OR security, SecureWipe provides both through intelligent defaults, offline certificate verification, and progressive disclosure that serves both casual cleaning and complete disposal scenarios.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2024-12-19 | 1.0 | Initial PRD creation from Project Brief | Product Manager John |

## Requirements

### Functional

**FR1:** Desktop application scans user directories (Documents, Downloads, Desktop, temp folders) and displays files with size/count summaries  
**FR2:** System categorizes files using rule-based logic (extension, path, access time) into "Safe to Delete/Less Important/Important" categories  
**FR3:** AI suggestions appear in separate tab as advisory-only recommendations with confidence scoring  
**FR4:** Secure file deletion uses OS-native tools (sdelete on Windows, shred on Linux) with real-time progress visualization  
**FR5:** System generates JSON certificates with device ID, timestamp, file paths, and cryptographic signatures using local self-signed keys  
**FR6:** Standalone verifier application validates certificate signatures against embedded public keys without internet dependency  
**FR7:** Bootable ISO provides simple wizard interface for complete system wiping with hardware detection  
**FR8:** System gracefully handles edge cases including locked files, encrypted drives, and non-English filenames with clear user messaging  
**FR9:** Double confirmation prevents accidental deletion of critical system files through safe defaults  
**FR10:** Certificate verification demonstrates tamper-proof nature through QR codes and local verification tools

### Non Functional

**NFR1:** Complete user folder scan completes in under 2 minutes for typical user data volumes  
**NFR2:** File deletion progress displays in real-time with plain-language status messages  
**NFR3:** Complete wipe process from scan to certificate takes under 10 minutes  
**NFR4:** Bootable ISO boots successfully in VM environment with UEFI/Secure Boot compatibility  
**NFR5:** Cross-platform compatibility supports Windows 10/11 (primary) and Linux Ubuntu/Debian (secondary)  
**NFR6:** Offline-first architecture operates without internet dependencies or cloud services  
**NFR7:** NIST SP 800-88 compliant deletion methods for demonstration purposes  
**NFR8:** Certificate verification achieves 100% accuracy using offline cryptographic validation  
**NFR9:** System handles 90%+ of common edge cases without crashes or data loss  
**NFR10:** Modular codebase enables parallel team development with shared JSON certificate format

## User Interface Design Goals

### Overall UX Vision

SecureWipe transforms data wiping from a technical nightmare into a trustworthy, anxiety-reducing experience. The interface borrows familiar patterns from gaming (progress bars, checkpoints) and antivirus rescue disks to create comfort through recognition. The dual-mode approach serves both "spring cleaning" users and "complete disposal" scenarios without overwhelming either group through progressive disclosure and intelligent defaults.

### Key Interaction Paradigms

- **Safe Defaults with Manual Override**: AI suggestions appear in separate advisory tab while rule-based categorization drives the main interface
- **Double Confirmation for Risky Operations**: Critical actions require explicit confirmation to prevent accidental deletion
- **Real-time Progress Visualization**: Gaming-inspired progress indicators with plain-language status messages
- **Graceful Edge Case Handling**: Clear messaging for encrypted drives, locked files, and non-English filenames
- **Offline-First Trust Building**: Certificate verification and QR codes work without internet dependency

### Core Screens and Views

- **Desktop Quick Clean Dashboard**: File scanning results with categorized lists and selection controls
- **AI Suggestions Tab**: Optional advisory recommendations with confidence scoring
- **Progress Visualization Screen**: Real-time deletion progress with checkpoint-style indicators  
- **Certificate Generation View**: Cryptographic proof display with QR codes and verification options
- **Bootable ISO Wizard Interface**: Simple step-by-step system wiping with hardware detection warnings
- **Offline Verification Tool**: Standalone certificate validator with embedded public key validation

### Accessibility: WCAG AA

Target WCAG AA compliance to ensure usability for users with disabilities, particularly important given the anxiety-inducing nature of data deletion tasks.

### Branding

Clean, trustworthy design emphasizing security and simplicity. Avoid technical intimidation through plain-language explanations and familiar UI patterns. Color scheme should convey safety and reliability rather than urgency or alarm.

### Target Device and Platforms: Cross-Platform

Desktop applications for Windows 10/11 (primary) and Linux Ubuntu/Debian (secondary). Bootable ISO provides hardware-independent interface. No mobile platforms for MVP.

## Technical Assumptions

### Repository Structure: Monorepo

Single repository with desktop-app/, bootable-iso/, and shared/ folders containing schema.json to enable the 3+3 team split while maintaining shared certificate format compatibility.

### Service Architecture

**Dual-Mode Standalone Applications**: Desktop application as single-process Python application with tkinter/Electron UI, bootable ISO as separate Ubuntu LTS live distribution. Both generate compatible JSON certificates using shared schema for seamless integration.

### Testing Requirements

**Unit + Integration Testing**: Python unittest for desktop components, automated ISO build validation, certificate format compatibility tests, and VM boot verification. Manual testing convenience methods for demo preparation and edge case validation.

### Additional Technical Assumptions and Requests

- **Programming Languages**: Python 3.8+ primary for cross-platform compatibility and rapid development
- **Desktop UI Framework**: Python tkinter for simplicity or Electron for richer UI, decision based on team expertise
- **Cryptography**: pyca/cryptography library primary, minisign as fallback for certificate signing/verification
- **Secure Deletion Tools**: OS-native tools (sdelete on Windows, shred on Linux) for file-level deletion, nwipe for bootable mode
- **Bootable Base**: Ubuntu LTS live ISO with Microsoft-signed shim for Secure Boot compatibility
- **Certificate Format**: Versioned JSON schema with semantic versioning, additive-only changes during hackathon
- **AI Integration**: Optional toggle with rule-based defaults (path/extension/size/access time patterns)
- **Database**: Local JSON files for configuration and logs, no database server dependencies
- **Deployment**: Standalone executables with no cloud dependencies, VM-compatible for demo environment
- **Development Tools**: Free and open-source only due to budget constraints
- **Build System**: Automated CI/CD for certificate schema validation and ISO build verification

## Epic List

**Epic 1: Foundation & Core Infrastructure**  
Establish project setup, shared certificate schema, and basic desktop file scanning with rule-based categorization.

**Epic 2: Desktop Quick Clean & Certificate Generation**  
Complete desktop application with secure deletion, progress visualization, and cryptographically signed certificate generation.

**Epic 3: Bootable Deep Clean System**  
Bootable ISO with wizard interface, hardware detection, complete system wiping, and certificate generation.

**Epic 4: Certificate Verification & AI Enhancement**  
Offline certificate verification tools, QR code generation, and optional AI-powered file categorization suggestions.

## Epic 1 Foundation & Core Infrastructure

**Epic Goal:** Establish project foundation with shared certificate schema, basic desktop file scanning, and rule-based categorization while delivering initial functional value through a working file scanner that demonstrates the core concept.

### Story 1.1 Project Setup and Shared Certificate Schema

As a **development team member**,  
I want **a properly configured monorepo with shared certificate schema**,  
so that **both desktop and bootable teams can develop in parallel with guaranteed certificate compatibility**.

#### Acceptance Criteria
1. Monorepo structure created with desktop-app/, bootable-iso/, and shared/ folders
2. JSON Schema v1.0.0 defined in shared/schema.json with required fields (deviceId, timestamp, files, signature)
3. Python validation script validates certificate format compatibility
4. Git repository initialized with lightweight validation scripts (not full CI/CD)
5. Development environment setup documentation created for both teams
6. Shared cryptography library integration (pyca/cryptography) with basic key generation
7. Schema designed for additive-only changes with version compatibility

### Story 1.2 Desktop Application Foundation

As a **desktop application user**,  
I want **a basic desktop application that launches successfully on Windows**,  
so that **I can begin the file scanning process with confidence**.

#### Acceptance Criteria
1. Python desktop application launches without errors on Windows 10/11
2. UI framework choice finalized by day 2 (tkinter for simplicity or Electron for richer UX)
3. Basic UI displays main window with SecureWipe branding and clear navigation
4. Application detects current user directories (Documents, Downloads, Desktop, temp folders)
5. Application gracefully handles missing directories or permission issues with clear messaging
6. Basic logging framework integrated for debugging and audit trail
7. Linux compatibility as stretch goal, not blocking requirement

### Story 1.3 File System Scanner with Progressive Display

As a **user preparing to dispose of my device**,  
I want **to see files being discovered in real-time with size and count information**,  
so that **I understand what data exists and can see progress even on slower systems**.

#### Acceptance Criteria
1. Scanner traverses user directories and catalogs files with metadata (path, size, modified date)
2. Progressive display shows files as they're discovered, not waiting for complete scan
3. File count and total size updated in real-time for each directory category
4. Progress indicator shows scanning status with plain-language messages and estimated completion
5. Scanner handles edge cases gracefully: locked files (skip with notification), non-English filenames, symbolic links
6. Results displayed in organized list view with expandable directory trees
7. Scanning performance optimized for I/O efficiency, with fallback messaging for slow systems

### Story 1.4 Rule-Based File Categorization

As a **non-technical user**,  
I want **files automatically categorized by safety level with clear explanations**,  
so that **I can make informed decisions without technical expertise**.

#### Acceptance Criteria
1. Files categorized into "Safe to Delete", "Less Important", and "Important" based on documented rules
2. Categorization rules consider file extension, path location, and last access time
3. System files and critical directories automatically marked as "Important" with explanations
4. Temporary files, cache, and downloads marked as "Safe to Delete" with rationale
5. User documents and media files marked as "Less Important" by default
6. Category assignment displayed with clear visual indicators and plain-language explanations
7. Manual override allows users to change category assignments with confirmation dialogs
8. Category rules documented and easily modifiable for future enhancements
9. Bulk operations available for changing multiple file categories efficiently

## Epic 2 Desktop Quick Clean & Certificate Generation

**Epic Goal:** Complete the desktop Quick Clean mode with secure file deletion, real-time progress visualization, and cryptographically signed certificate generation, delivering a fully functional desktop application that users can trust for safe file removal.

### Story 2.1 Secure File Deletion Engine

As a **user who wants to permanently remove sensitive files**,  
I want **selected files securely overwritten using industry-standard methods**,  
so that **I can be confident the data cannot be recovered by unauthorized parties**.

#### Acceptance Criteria
1. Integration with OS-native secure deletion tools (sdelete on Windows, shred on Linux)
2. NIST SP 800-88 compliant deletion methods implemented for demonstration purposes
3. Secure deletion process handles locked files by skipping with clear user notification
4. Deletion engine respects user category selections and manual overrides
5. Pre-deletion validation prevents accidental system file deletion
6. Deletion process can be paused and resumed for large file sets
7. Error handling provides clear messaging for permission issues or hardware failures

### Story 2.2 Real-Time Progress Visualization

As a **user performing file deletion**,  
I want **to see real-time progress with clear status messages**,  
so that **I understand what's happening and feel confident the process is working**.

#### Acceptance Criteria
1. Gaming-inspired progress indicators show overall completion percentage
2. Current file being processed displayed with plain-language status
3. Estimated time remaining calculated and updated dynamically
4. Checkpoint-style indicators show major milestones (scanning complete, deletion started, etc.)
5. Progress can be monitored without blocking the UI (non-blocking operations)
6. Clear differentiation between scanning, categorizing, and deletion phases
7. Success/failure status for each file with summary statistics
8. Option to view detailed log of all operations performed

### Story 2.3 Certificate Generation and Cryptographic Signing

As a **user who needs proof of data deletion**,  
I want **a cryptographically signed certificate documenting what was deleted**,  
so that **I have verifiable evidence for compliance or peace of mind**.

#### Acceptance Criteria
1. JSON certificate generated using shared schema from Epic 1
2. Certificate includes device ID, timestamp, complete file list, and deletion method used
3. Cryptographic signature created using pyca/cryptography with local self-signed keys
4. Certificate saved to user-specified location with clear filename convention
5. QR code generated linking to certificate file for easy sharing/verification
6. Certificate includes human-readable summary of deletion operation
7. Before/after disk space comparison included in certificate
8. Certificate generation completes within 30 seconds of deletion completion

### Story 2.4 User Confirmation and Safety Controls

As a **non-technical user concerned about accidental deletion**,  
I want **clear confirmation dialogs and safety controls**,  
so that **I can proceed with confidence and avoid costly mistakes**.

#### Acceptance Criteria
1. Double confirmation required before starting deletion process
2. Clear summary of what will be deleted with file counts and total size
3. Final "point of no return" warning with explicit user acknowledgment
4. Option to create backup of "Important" files before deletion
5. Safety controls prevent deletion of critical system directories
6. User can review and modify selections up until final confirmation
7. Clear explanation of what "secure deletion" means in plain language
8. Emergency stop button available during deletion process

## Epic 3 Bootable Deep Clean System

**Epic Goal:** Deliver a bootable ISO with wizard interface for complete system wiping, hardware detection, and certificate generation, using Ubuntu LTS base with nwipe integration and resilient fallback strategies for demo success.

### Story 3.1 Bootable ISO Foundation with Secure Boot Compatibility

As a **user preparing to completely wipe a device for disposal**,  
I want **a bootable ISO that starts reliably with Secure Boot enabled**,  
so that **I can perform complete system wiping on modern hardware without BIOS modifications**.

#### Acceptance Criteria
1. Ubuntu LTS live ISO base with Microsoft-signed shim for Secure Boot compatibility
2. Minimal customization approach - add SecureWipe app and dependencies only
3. ISO boots successfully in UEFI VM with OVMF/EDK2 firmware
4. VM snapshot saved as guaranteed demo fallback
5. Tested on Intel iGPU and AMD/NVMe platforms by day 3
6. Fallback BIOS compatibility maintained for older hardware
7. ISO size under 2GB for standard USB drive compatibility

### Story 3.2 Hardware Detection with nwipe Integration

As a **user about to perform complete system wiping**,  
I want **reliable storage device detection and selection**,  
so that **I can safely identify and wipe the correct devices without accidents**.

#### Acceptance Criteria
1. nwipe integration for disk-level operations and device listing
2. Manual device selection with clear device IDs and confirmation
3. Multi-step confirmations with device name echo and typed "DELETE" confirmation
4. SSD vs HDD detection using nwipe's hardware identification
5. Encrypted drive warnings with clear limitation explanations
6. Conservative defaults - show warnings rather than guessing capabilities
7. Device verification working on VM and two test platforms by day 5

### Story 3.3 Resilient Wizard Interface with TUI Fallback

As a **non-technical user performing complete device wiping**,  
I want **a simple interface that works even if graphics fail**,  
so that **I can complete the operation regardless of hardware issues**.

#### Acceptance Criteria
1. GUI wizard interface tested early in live environment
2. TUI fallback using nwipe's ncurses interface for constrained environments
3. Automatic fallback to text mode if GUI fails to render
4. Same confirmation flow and safety checks in both GUI and TUI modes
5. Clear navigation and progress indicators in both interfaces
6. Plain-language explanations and device identification
7. Emergency stop functionality available throughout process

### Story 3.4 Complete System Wiping with Dual Cryptography Support

As a **user completing device disposal preparation**,  
I want **reliable wiping with cryptographic proof using fallback signing methods**,  
so that **I have verifiable evidence regardless of library compatibility issues**.

#### Acceptance Criteria
1. nwipe integration for NIST-compliant wiping methods with progress display
2. Demonstration on small USB/NVMe devices (5-10 minute demo window)
3. JSON certificate generation using shared schema with schemaVersion field
4. Primary: pyca/cryptography for RSA signing when wheels available
5. Fallback: minisign (Ed25519) for portable signing if OpenSSL issues occur
6. Certificate saved to external USB with offline verification capability
7. Pre-recorded wipe sequence as ultimate demo fallback
8. Success validation: signed JSON + offline verifier green check by day 10

## Epic 4 Certificate Verification & AI Enhancement

**Epic Goal:** Complete the trust verification loop with offline certificate validation tools and add optional AI-powered file categorization suggestions that appeal to judges while maintaining rule-based defaults for reliability.

### Story 4.1 Offline Certificate Verifier Application

As a **user who received a SecureWipe certificate**,  
I want **a standalone tool that validates certificate authenticity without internet**,  
so that **I can verify deletion proof independently and share verification with others**.

#### Acceptance Criteria
1. Standalone verifier application with embedded public keys
2. Supports both desktop and bootable ISO certificate formats
3. Drag-and-drop certificate file loading with clear validation results
4. QR code scanning capability for easy certificate sharing
5. Detailed verification report showing certificate contents and signature status
6. Clear VALID/INVALID/TAMPERED status with plain-language explanations
7. Cross-platform compatibility (Windows/Linux) with portable executable

### Story 4.2 AI-Powered File Categorization Suggestions

As a **user scanning files for deletion**,  
I want **intelligent suggestions about file importance**,  
so that **I can make better decisions while maintaining control over the process**.

#### Acceptance Criteria
1. AI suggestions displayed in separate advisory tab (not main interface)
2. Rule-based categorization remains primary with manual override capability
3. AI analyzes file content patterns, naming conventions, and usage frequency
4. Confidence scoring for AI suggestions with clear uncertainty indicators
5. Optional toggle to enable/disable AI features entirely
6. Graceful handling of non-English filenames and non-standard file types
7. AI processing completes within file scanning timeframe without blocking UI

### Story 4.3 QR Code Generation and Certificate Sharing

As a **user who needs to share deletion proof**,  
I want **easy certificate sharing through QR codes**,  
so that **I can provide verification to buyers, auditors, or compliance officers**.

#### Acceptance Criteria
1. QR code generation for certificate file path and verification instructions
2. QR codes link to local verification tools (no internet dependency)
3. Printable certificate summary with QR code for physical documentation
4. Certificate export options (JSON, PDF summary, QR code image)
5. Clear instructions for recipients on how to verify certificates offline
6. QR code scanning works with standard smartphone camera apps
7. Certificate sharing workflow tested with non-technical users

### Story 4.4 Integration Testing and Demo Polish

As a **hackathon judge evaluating SecureWipe**,  
I want **a polished demonstration showing complete workflows**,  
so that **I can understand the technical innovation and practical value**.

#### Acceptance Criteria
1. End-to-end integration testing: Desktop scan → wipe → certificate → verify
2. Bootable ISO integration testing: Boot → detect → wipe → certificate → verify
3. Certificate compatibility verified between desktop and bootable modes
4. Demo script with timing and fallback procedures documented
5. Error handling and edge cases demonstrate gracefully with clear messaging
6. Performance optimization for demo environment (small test datasets)
7. Team can articulate post-MVP roadmap and technical architecture decisions

## Checklist Results Report

### PM Checklist Validation Results

**Overall PRD Completeness:** 92% - Comprehensive and well-structured  
**MVP Scope Appropriateness:** Just Right - Properly balanced for 2-week hackathon  
**Readiness for Architecture Phase:** Ready - Clear technical guidance and constraints provided  

### Category Analysis Table

| Category                         | Status  | Critical Issues |
| -------------------------------- | ------- | --------------- |
| 1. Problem Definition & Context  | PASS    | None - Excellent problem articulation with quantified impact |
| 2. MVP Scope Definition          | PASS    | None - Clear boundaries with strong rationale |
| 3. User Experience Requirements  | PASS    | None - Comprehensive UI goals and interaction paradigms |
| 4. Functional Requirements       | PASS    | None - Well-structured FR/NFR with clear acceptance criteria |
| 5. Non-Functional Requirements   | PASS    | None - Performance, security, and reliability well-defined |
| 6. Epic & Story Structure        | PASS    | None - Logical sequencing with appropriate sizing |
| 7. Technical Guidance            | PASS    | None - Clear architecture direction and constraints |
| 8. Cross-Functional Requirements | PARTIAL | Minor - Data schema details could be more explicit |
| 9. Clarity & Communication       | PASS    | None - Excellent documentation quality and structure |
