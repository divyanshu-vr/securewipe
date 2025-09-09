# Project Brief: SecureWipe

**Session Date:** December 19, 2024  
**Facilitator:** Business Analyst Mary  
**Participant:** SecureWipe Team Lead  

## Executive Summary

**SecureWipe** is a pragmatic data wiping application designed for safe IT asset recycling with verifiable proof of erasure. The MVP addresses India's ₹50,000 crore IT asset hoarding problem through a dual-approach solution: desktop "Quick Clean" for user folders and bootable "Deep Clean" for complete system wiping, featuring rule-based file categorization, offline certificate verification, and graceful edge case handling.

**Key MVP features:**
- **Smart defaults with manual override**: AI suggestions in separate tab, default to manual control
- **Robust edge case handling**: Encrypted drive detection, locked file skipping, SSD/HDD awareness
- **Offline-first verification**: Local certificate validation with embedded public keys
- **Demo-ready architecture**: VM compatibility, scripted checkpoints, fallback recordings

**Success criteria:** Judges can witness file scanning, confirm safe deletion, receive certificates, and verify authentically offline - all with clear language, safe defaults, and credible post-MVP roadmap.

## Problem Statement

India generates over 1.75 million tonnes of e-waste annually, with over ₹50,000 crore worth of IT assets hoarded in homes and offices due to data security fears. Current data sanitization solutions create barriers to safe recycling:

**Current State Pain Points:**
- **Complexity barrier**: Existing tools require technical expertise (command-line interfaces, complex configurations)
- **Trust deficit**: No verifiable proof of complete data erasure creates lingering anxiety
- **Cost prohibitive**: Enterprise-grade solutions are expensive for individual users
- **Accessibility gap**: Tools lack user-friendly interfaces for general public adoption

**Quantified Impact:**
- 1.75M tonnes annual e-waste generation with accelerating growth
- ₹50,000+ crore in hoarded IT assets preventing circular economy
- Millions of functional devices unused due to data security concerns
- Environmental impact from improper disposal and resource waste

**Why Existing Solutions Fall Short:**
- DBAN: Bootable but intimidating command-line interface
- CCleaner: Simple but lacks secure deletion verification
- Enterprise tools: Expensive, complex, designed for IT professionals
- Manual deletion: Users don't understand file recovery risks

**Urgency Drivers:**
- Rapid digitization increasing sensitive data on personal devices
- Growing environmental awareness demanding better e-waste management
- Government initiatives promoting circular economy requiring citizen participation
- Rising cybersecurity awareness creating demand for verifiable data protection

## Proposed Solution

**SecureWipe** transforms data wiping from a technical nightmare into a trustworthy, user-friendly experience through a dual-mode approach that addresses both casual cleaning and complete device preparation for disposal.

**Core Solution Approach:**

**Desktop Application (Quick Clean Mode):**
- One-click scanning of user directories (Documents, Downloads, Desktop, temp files)
- Rule-based file categorization with AI-enhanced suggestions in separate tab
- Secure overwrite using OS-native tools with progress visualization
- Immediate certificate generation with offline verification capability

**Bootable ISO (Deep Clean Mode):**
- Complete system wiping including OS, hidden partitions, and free space
- Simple   wizard interface familiar from antivirus rescue disks
- Hardware-aware wiping (SSD TRIM vs HDD overwrite patterns)
- Cryptographically signed completion certificates

**Key Differentiators:**

**Trust Through Transparency:**
- Offline certificate verification with embedded public keys
- QR codes linking to local verification tools (no internet dependency)
- Clear "before/after" reporting showing what was actually removed
- Plain-language explanations replacing technical jargon

**Anxiety-Reducing UX:**
- Familiar patterns borrowed from gaming (progress bars, checkpoints)
- Safe defaults with manual override options
- Double confirmation for risky operations
- Graceful handling of edge cases (encrypted drives, locked files)

**Technical Robustness:**
- NIST SP 800-88 compliant deletion methods
- Cross-platform compatibility (Windows/Linux focus for MVP)
- Offline-first architecture reducing dependency risks
- Modular design enabling parallel team development

**Why This Solution Succeeds:**
Unlike existing tools that prioritize either simplicity OR security, SecureWipe provides both through intelligent defaults and progressive disclosure. The dual-mode approach serves both "spring cleaning" users and "complete disposal" scenarios without overwhelming either group.

## Target Users

### Primary User Segment: Individual Device Owners Preparing for Disposal

**Demographic Profile:**
- Age: 25-55 years, tech-comfortable but not technical experts
- Income: Middle class with devices worth ₹20,000-₹1,00,000
- Location: Urban/semi-urban India with digital literacy
- Device ownership: 2-4 devices (laptop, smartphone, tablet) over 3-5 years

**Current Behaviors:**
- Keep old devices "just in case" rather than disposing
- Manually delete files but worry about recovery
- Avoid selling/donating due to data security fears
- Research data wiping but get overwhelmed by technical complexity

**Specific Pain Points:**
- "I deleted everything but can hackers still recover my photos?"
- "These data wiping tools look scary and complicated"
- "How do I know if it actually worked?"
- "What if I accidentally delete something important?"

**Goals They're Trying to Achieve:**
- Confidently dispose of devices without data breach risk
- Get some value back (sale/donation) rather than hoarding
- Simple process that doesn't require technical expertise
- Proof that data is actually gone for peace of mind

### Secondary User Segment: Small Business IT Managers

**Demographic Profile:**
- Role: IT managers/admins in 10-100 employee companies
- Technical level: Moderate, handles basic IT but not security specialist
- Budget constraints: Limited resources for enterprise security tools
- Compliance awareness: Understands need for data protection

**Current Behaviors:**
- Manually wipe devices using basic tools
- Worry about compliance and audit requirements
- Seek cost-effective solutions for device lifecycle management
- Need documentation for compliance purposes

**Specific Needs:**
- Batch processing capabilities for multiple devices
- Audit trail and compliance documentation
- Cost-effective alternative to expensive enterprise tools
- Simple training for non-technical staff

**Goals:**
- Meet basic compliance requirements affordably
- Streamline device disposal process
- Reduce liability from improper data handling
- Enable safe device resale/donation programs

## Goals & Success Metrics

### Business Objectives
- **SIH Hackathon Victory**: Win or place in top 3 through compelling demo and technical innovation
- **Judge Engagement**: Achieve 90%+ positive feedback on solution practicality and AI integration
- **Technical Demonstration**: Successfully demo both Quick Clean and Deep Clean modes with certificate verification
- **Team Coordination**: Complete parallel development tracks (3+3 split) with integrated final product

### User Success Metrics
- **Confidence Building**: Users report feeling "confident" or "very confident" about data security post-wipe
- **Completion Rate**: 95%+ of users complete the full wipe process without abandoning
- **Trust Verification**: Users successfully verify certificates using offline tools without assistance
- **Anxiety Reduction**: Users describe process as "simple" rather than "scary" or "technical"

### Key Performance Indicators (KPIs)

- **Demo Success Rate**: 100% successful live demonstrations without technical failures
- **Certificate Generation**: Generate valid, verifiable certificates for 100% of completed wipes
- **Edge Case Handling**: Gracefully handle 90%+ of common edge cases (encrypted drives, locked files)
- **AI Integration Appeal**: Judges specifically mention AI features as innovative/valuable
- **Development Velocity**: Complete MVP features within 2-week timeline with working demos
- **Verification Accuracy**: 100% certificate verification accuracy using offline tools

### MVP Success Criteria

**Technical Success:**
- Desktop app scans user folders and categorizes files using rule-based + AI suggestions
- Bootable ISO boots successfully in VM environment with functional UI
- Certificate generation works offline with cryptographic signatures
- Verification tools validate certificates without internet dependency

**User Experience Success:**
- Complete wipe process in under 10 minutes for typical user data
- Clear progress indication with plain-language status messages
- Safe defaults prevent accidental deletion of critical system files
- Double confirmation prevents user errors

**Demo Success:**
- Live demonstration shows complete flow: Scan → Select → Wipe → Certificate → Verify
- Judges can interact with both desktop app and bootable ISO
- Certificate verification demonstrates tamper-proof nature
- Team can explain technical architecture and post-MVP roadmap

## MVP Scope

### Core Features (Must Have)

- **Desktop File Scanner**: Scans user directories (Documents, Downloads, Desktop, temp folders) and displays files with size/count summaries
- **Rule-Based Categorization**: Categorizes files by extension, path, and access time into "Safe to Delete/Less Important/Important" with AI suggestions in separate tab
- **Secure File Deletion**: Uses OS-native secure deletion tools (sdelete on Windows, shred on Linux) with progress visualization
- **Certificate Generation**: Creates JSON report with device ID, timestamp, file paths, and cryptographic signature using local self-signed keys
- **Offline Verification**: Standalone verifier app that validates certificate signatures against embedded public keys
- **Bootable ISO UI**: Simple wizard interface for Deep Clean mode with hardware detection and encrypted drive warnings
- **Edge Case Handling**: Graceful handling of locked files, encrypted drives, and non-English filenames with clear user messaging

### Out of Scope for MVP

- Multi-language support beyond English
- Enterprise batch processing features
- Advanced cryptographic key management (HSM, key escrow)
- Content-based file analysis or privacy risk scoring
- Blockchain or distributed verification systems
- Mobile app versions (Android/iOS)
- Network-based certificate verification
- Advanced SSD vendor tool integration
- Automated scheduling or background operations

### MVP Success Criteria

**Functional Success:**
- Complete desktop app workflow: Scan → Review → Wipe → Certificate → Verify in under 10 minutes
- Bootable ISO boots in VM environment with functional UI (Deep Clean mode demonstration)
- Generate tamper-proof certificates that verify successfully offline
- Handle common edge cases without crashes or data loss

**Demo Success:**
- Live demonstration shows both Quick Clean (desktop) and Deep Clean (bootable) modes
- Certificate verification demonstrates cryptographic integrity
- Judges can interact with working software and understand the value proposition
- Team can articulate technical architecture and post-MVP roadmap convincingly

**Technical Success:**
- Cross-platform compatibility (Windows primary, Linux secondary)
- Offline-first architecture with no internet dependencies
- NIST-compliant deletion methods for demonstration purposes
- Modular codebase enabling parallel team development

## Technical Considerations

### Platform Requirements
- **Target Platforms:** Windows 10/11 (primary), Linux Ubuntu/Debian (secondary)
- **Browser/OS Support:** Desktop applications only, no web browser dependencies
- **Performance Requirements:** Complete user folder scan in <2 minutes, file deletion progress visible in real-time

### Technology Preferences
- **Frontend:** Python tkinter or Electron for cross-platform desktop UI
- **Backend:** Python for file operations, cryptography, and AI integration
- **Database:** Local JSON files for configuration and logs (no database server)
- **Hosting/Infrastructure:** Standalone applications, no cloud dependencies

### Architecture Considerations
- **Repository Structure:** Monorepo with separate folders for desktop-app/ and bootable-iso/
- **Service Architecture:** Single-process desktop app, bootable ISO as separate Linux distribution
- **Integration Requirements:** Shared JSON certificate format between desktop and ISO components
- **Security/Compliance:** Self-signed certificates for MVP, NIST SP 800-88 deletion methods, offline verification

## Constraints & Assumptions

### Constraints
- **Budget:** Free and open-source tools only (Python, Linux distributions, standard libraries)
- **Timeline:** 2-week hackathon deadline with working demo required
- **Resources:** 6-person team split into 3 software developers + 3 bootable ISO developers
- **Technical:** Cross-platform compatibility limited to Windows/Linux, no mobile platforms

### Key Assumptions
- Team members have basic Python and Linux knowledge for parallel development
- VM environment available for bootable ISO testing and demo
- Standard user directories contain majority of sensitive personal data
- Self-signed certificates acceptable for MVP demonstration purposes
- Judges will value working demo over perfect production implementation
- Users prefer simple defaults over complex configuration options
- Offline verification more trustworthy than online certificate checking

## Risks & Open Questions

### Key Risks & MVP Mitigations

**Team Coordination Risk (incompatible certificate formats):**
- **Mitigation:** Publish JSON Schema v1.0.0 with semantic versioning, additive-only changes during hackathon, shared repo with golden samples and CI validation

**Hardware Compatibility Risk (UEFI/Secure Boot):**
- **Mitigation:** Ubuntu LTS live base with Microsoft-signed shim, VM demo with OVMF firmware as guaranteed fallback, temporary Secure Boot disable guidance

**AI Integration Risk (non-standard types, non-English names):**
- **Mitigation:** AI advisory-only with rule-based defaults (path/extension/size/access time), full manual view available, confidence labeling with easy ignore

**Demo Failure Risk (live constraints):**
- **Mitigation:** Scripted demo with checkpoints, 90-second boot recording, VM preloaded with ISO, offline verifier for air-gapped demonstration

### Technical Architecture Decisions (Locked)

- **Bootable ISO:** Ubuntu LTS live base with Microsoft-signed shim for Secure Boot compatibility
- **Cryptography:** pyca/cryptography primary, minisign fallback for signing/verification  
- **AI Integration:** Optional toggle with rule-based defaults (path/extension/size/access time)
- **Certificate Format:** Versioned JSON schema with additive-only changes during hackathon
- **Secure Deletion:** nwipe for bootable mode, shred/srm for desktop file-level wiping

## Next Steps

### Immediate Actions

1. **Create shared repository structure** with desktop-app/, bootable-iso/, and shared/ folders containing schema.json
2. **Publish JSON Schema v1.0.0** with required fields (deviceId, timestamp, files, signature) and validation script
3. **Set up development environments** - Python 3.8+ with pyca/cryptography, Ubuntu LTS live ISO build tools
4. **Create demo VM** with OVMF UEFI firmware and test bootable ISO compatibility
5. **Assign team roles** - 3 desktop developers (scanner, UI, certificates), 3 ISO developers (live distro, nwipe integration, UI)

### Demo Kit Preparation

**Live Demo:** Desktop app complete flow with VM bootable ISO demonstration
**Backup Plans:** Pre-recorded boot sequence, pre-built certificates, offline verifier
**Hardware Fallback:** VM with OVMF if venue hardware has Secure Boot issues

### PM Handoff

This Project Brief provides the complete context for **SecureWipe MVP**. The solution addresses India's e-waste crisis through user-friendly data wiping with verifiable certificates, targeting individual device owners preparing for disposal.

**Key MVP deliverables:**
- Desktop application with AI-assisted file categorization
- Bootable ISO for complete device wiping
- Cryptographically signed certificates with offline verification
- Cross-platform compatibility with robust edge case handling

The technical architecture decisions are locked to enable parallel team development while maintaining demo reliability. All risks have identified mitigations, and the scope is focused on core value delivery within the 2-week hackathon timeline.

---

*Project Brief created using the BMAD-METHOD™ framework*