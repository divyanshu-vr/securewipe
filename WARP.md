# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

SecureWipe is a dual-mode secure file deletion system addressing India's IT asset disposal problem. It provides:
- **Desktop Application** ("Quick Clean"): Secure deletion of user directories
- **Bootable ISO** ("Deep Clean"): Complete system wiping from bootable media
- **Shared Certificate Schema**: Cryptographically signed proof of deletion operations

The system is offline-first with no cloud dependencies, designed for air-gapped environments.

## Development Setup

### Initial Setup
```bash
# Windows
scripts\setup-dev-env.bat

# Linux/Mac  
./scripts/setup-dev-env.sh

# Manual activation
# Windows: venv\Scripts\activate.bat
# Linux/Mac: source venv/bin/activate
```

### Development Dependencies
- Python 3.8+ required
- All dependencies managed through pip and requirements files
- Virtual environment automatically created by setup scripts

## Common Development Commands

### Testing
```bash
# Run all tests
pytest

# Component-specific tests
cd desktop-app && pytest tests/
cd bootable-iso && pytest tests/
cd shared && pytest tests/

# Certificate compatibility validation
python scripts/validate-certificates.py

# Coverage report
pytest --cov --cov-report=html
```

### Code Quality
```bash
# Format code (Black)
black .

# Lint code (flake8)
flake8 .

# Type checking (MyPy)
mypy shared/
```

### Building
```bash
# Desktop application
cd desktop-app && python build.py

# Certificate verifier
cd verifier && python build.py

# Bootable ISO (requires Linux)
cd bootable-iso && ./build/customize-iso.sh
```

### Single Test Execution
```bash
# Run specific test file
pytest desktop-app/tests/test_scanner.py

# Run specific test method
pytest desktop-app/tests/test_scanner.py::TestFileScanner::test_scan_directory

# Run tests matching pattern
pytest -k "test_certificate"
```

## Architecture & Code Organization

### Dual-Mode Architecture
The system operates in two modes sharing a common certificate schema:

1. **Desktop Mode** (`desktop-app/`): tkinter-based GUI for user directory cleaning
2. **Bootable Mode** (`bootable-iso/`): Ubuntu-based live system for complete device wiping
3. **Shared Components** (`shared/`): Certificate schema, cryptography, logging

### Key Architectural Patterns

- **Shared Certificate Schema**: Both modes generate compatible JSON certificates using `shared/schema/certificate_v1.json`
- **Offline-First Design**: No internet dependencies, works in air-gapped environments
- **OS-Native Integration**: Uses platform-specific tools (sdelete/shred/nwipe)
- **Cryptographic Fallback**: Primary pyca/cryptography with minisign fallback
- **OWASP Secure Logging**: All file operations use sanitized logging

### Module Structure
```
SecureWipe/
├── desktop-app/        # Team 1: Desktop Quick Clean
├── bootable-iso/       # Team 2: Bootable Deep Clean
├── shared/             # Common: Certificate schema, crypto, logging
├── verifier/           # Standalone certificate verifier
├── scripts/            # Build & deployment automation
└── docs/               # Architecture & development guides
```

### Critical Shared Components

**Certificate Schema** (`shared/schema/`):
- JSON-based certificate format for deletion proof
- Version 1.0.0 with additive-only changes for compatibility
- Required validation against schema before saving

**Cryptography** (`shared/crypto/`):
- Primary: pyca/cryptography (RSA-2048-SHA256) 
- Fallback: minisign (Ed25519)
- Self-signed certificates for MVP, enterprise PKI upgrade path documented

**Secure Logging** (`shared/secure_logging/`):
- OWASP-compliant logging with path sanitization
- Never logs sensitive file information
- Required for all file system operations

## Critical Development Rules

### Certificate Schema Compliance
- ALL certificate generation MUST validate against `shared/schema/certificate_v1.json`
- Use `shared.schema.validator.validate_certificate()` before saving certificates
- Schema modifications require version bump and migration support

### OWASP Secure Logging
- Use `shared.logging.secure_logger` for ALL file system operations
- Never log full file paths - use `sanitizer.sanitize_path()`
- Log levels: ERROR for failures, INFO for operations, DEBUG for development only

### Cross-Platform File Operations
- Use `pathlib.Path` for ALL file system operations (never string concatenation)
- Test path operations on both Windows and Linux
- Handle platform-specific secure deletion tools properly

### Error Handling Pattern
```python
try:
    result = os_operation()
except PermissionError as e:
    logger.error(f"Permission denied: {sanitizer.sanitize_path(path)}")
    raise SecureWipeError("Insufficient permissions") from e
except FileNotFoundError as e:
    logger.warning(f"File not found: {sanitizer.sanitize_path(path)}")
    return OperationResult.SKIPPED
```

### Cryptography Implementation Pattern
```python
# Always implement fallback
try:
    from shared.crypto.pyca_impl import CertificateSigner
    signer = CertificateSigner()
except ImportError:
    from shared.crypto.minisign_impl import CertificateSigner
    signer = CertificateSigner()
```

### Shared Module Import Pattern
```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "shared"))

from schema.validator import validate_certificate
from crypto.key_management import get_signer
from logging.secure_logger import get_logger
```

## Security & Performance Requirements

### Security Model
- Self-signed certificates with offline verification (MVP)
- Certificate private keys protected using OS keystore
- All user input sanitized before logging
- Production upgrade path to enterprise PKI/HSM documented

### Performance Targets
- File scanning: <2 minutes for typical user directories
- Progress updates: Every 100ms minimum
- Certificate generation: <30 seconds post-deletion
- Memory management: Use generators for large directory traversal

## Testing Strategy

### Required Test Coverage
- Unit tests for all shared components with >90% coverage
- Integration tests for certificate compatibility between modes
- Cross-platform testing on Windows and Linux
- VM-based testing for bootable ISO functionality

### Test Organization
- Component tests in respective `tests/` directories
- Shared component tests in `shared/tests/`
- Certificate compatibility tests via `scripts/validate-certificates.py`

## Platform-Specific Considerations

### Windows Development
- Uses sdelete for secure deletion
- PowerShell build scripts
- PyInstaller for executable creation

### Linux Development  
- Uses shred for secure deletion
- Bash build scripts
- ISO customization requires Ubuntu environment

### Bootable ISO Requirements
- Ubuntu LTS 22.04+ base
- nwipe integration for hardware wiping
- Secure Boot compatibility maintained
