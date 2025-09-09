# SecureWipe - Dual-Mode Secure File Deletion System

## Overview

SecureWipe addresses India's ₹50,000+ crore IT asset hoarding problem by providing trustworthy, verifiable secure file deletion through dual-mode operation: desktop "Quick Clean" for user folders and bootable "Deep Clean" for complete system preparation.

## Architecture Highlights

- **Dual-Mode Design:** Desktop application + bootable ISO with shared certificate schema
- **Offline-First:** No cloud dependencies, works in air-gapped environments  
- **Cryptographic Proof:** Signed certificates with offline verification
- **Cross-Platform:** Windows/Linux desktop support, Ubuntu LTS bootable base
- **Security-Focused:** OWASP logging, NIST SP 800-88 compliance, enterprise upgrade path

## Quick Start

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd SecureWipe

# Setup development environment
./scripts/setup-dev-env.sh

# Install dependencies
pip install -r requirements-dev.txt
```

### Desktop Application Development

```bash
cd desktop-app
pip install -r requirements.txt
python src/main.py
```

### Bootable ISO Development

```bash
cd bootable-iso
pip install -r requirements.txt
# Requires VM environment for testing
```

## Project Structure

```
SecureWipe/
├── desktop-app/        # Team 1: Desktop Quick Clean
├── bootable-iso/       # Team 2: Bootable Deep Clean  
├── shared/             # Common components & certificate schema
├── verifier/           # Standalone certificate verifier
├── docs/               # Architecture & development guides
└── scripts/            # Build & deployment automation
```

## Key Technologies

- **Language:** Python 3.8+ for cross-platform compatibility
- **Desktop UI:** tkinter (no external dependencies)
- **Cryptography:** pyca/cryptography primary, minisign fallback
- **Secure Deletion:** sdelete (Windows), shred (Linux), nwipe (bootable)
- **Bootable Base:** Ubuntu LTS with Secure Boot compatibility

## Team Organization

### Team 1: Desktop Application (3 developers)
- File system scanning and categorization
- tkinter-based user interface
- Secure deletion using OS-native tools
- Certificate generation and display

### Team 2: Bootable ISO (3 developers)  
- Ubuntu Live ISO customization
- Hardware detection and nwipe integration
- Wizard interface with TUI fallback
- Certificate generation for offline verification

### Shared Responsibilities
- Certificate schema compatibility
- Cryptography implementations
- OWASP-compliant logging
- Cross-platform utilities

## Development Workflow

### Testing
```bash
# Run all tests
./scripts/run-tests.sh

# Certificate compatibility validation
python scripts/validate-certificates.py
```

### Building
```bash
# Build all components
./scripts/build-all.sh

# Individual builds
./scripts/build-desktop.sh    # Desktop executable
./scripts/build-iso.sh        # Bootable ISO
```

## Security Model

### MVP (Hackathon)
- Self-signed certificates with offline verification
- OWASP-compliant logging with data sanitization
- OS-native secure deletion tools
- Secure Boot compatible ISO

### Production Upgrade Path
- Enterprise PKI integration
- Hardware Security Module (HSM) key storage
- NIST SP 800-57 key lifecycle management
- Enhanced audit logging and SIEM integration

## Documentation

- **[Architecture](docs/architecture.md):** Complete system design
- **[Coding Standards](docs/architecture/coding-standards.md):** Development guidelines
- **[Tech Stack](docs/architecture/tech-stack.md):** Technology details
- **[Source Tree](docs/architecture/source-tree.md):** Repository organization

## Certificate Schema

SecureWipe uses a shared JSON certificate schema ensuring compatibility between desktop and bootable modes:

```json
{
  "schemaVersion": "1.0.0",
  "certificateId": "uuid4",
  "timestamp": "ISO 8601",
  "deviceInfo": { "deviceId": "...", "hostname": "..." },
  "operationType": "quick_clean | deep_clean",
  "deletionSummary": { "totalFiles": 0, "successCount": 0 },
  "fileOperations": [...],
  "cryptographicProof": { "algorithm": "...", "signature": "..." }
}
```

## Demo Strategy

### Hackathon Demo Flow
1. **Desktop Quick Clean:** Scan user directories, categorize files, secure deletion
2. **Certificate Generation:** Cryptographically signed proof of deletion
3. **Bootable Deep Clean:** VM demonstration of complete system wiping
4. **Certificate Verification:** Offline validation with QR codes

### Fallback Strategies
- VM snapshots for guaranteed bootable demo
- Pre-recorded wipe sequences for time constraints
- Multiple cryptography implementations for compatibility
- TUI fallback for GUI issues

## Contributing

### Code Standards
- Follow [coding standards](docs/architecture/coding-standards.md)
- Use type hints and comprehensive error handling
- Implement OWASP-compliant logging
- Validate against certificate schema

### Testing Requirements
- Unit tests for all components
- Integration tests for certificate compatibility
- VM-based testing for bootable functionality
- Cross-platform validation

## License

[License details to be determined]

## Support

For development questions and architecture clarification, refer to the comprehensive documentation in the `docs/` directory or contact the architecture team.