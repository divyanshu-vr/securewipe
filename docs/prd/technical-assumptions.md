# Technical Assumptions

## Repository Structure: Monorepo

Single repository with desktop-app/, bootable-iso/, and shared/ folders containing schema.json to enable the 3+3 team split while maintaining shared certificate format compatibility.

## Service Architecture

**Dual-Mode Standalone Applications**: Desktop application as single-process Python application with tkinter/Electron UI, bootable ISO as separate Ubuntu LTS live distribution. Both generate compatible JSON certificates using shared schema for seamless integration.

## Testing Requirements

**Unit + Integration Testing**: Python unittest for desktop components, automated ISO build validation, certificate format compatibility tests, and VM boot verification. Manual testing convenience methods for demo preparation and edge case validation.

## Additional Technical Assumptions and Requests

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
