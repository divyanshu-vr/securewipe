# SecureWipe

<div align="center">

**Professional Secure File Deletion with Cryptographic Proof**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-TBD-green.svg)](LICENSE)
[![Cross-Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)](https://github.com/divyanshu-vr/securewipe)

</div>

---

## Overview

SecureWipe is a comprehensive secure file deletion system designed to permanently remove sensitive data from your computer with cryptographic proof of deletion. Whether you're preparing to recycle an old device, cleaning up after a project, or ensuring compliance with data protection regulations, SecureWipe provides the tools you need with transparency and confidence.

### Why SecureWipe?

- **Complete Data Erasure**: Permanently delete files using industry-standard secure deletion methods that make recovery impossible
- **Cryptographic Verification**: Generate tamper-proof certificates that provide verifiable proof of deletion
- **Dual-Mode Operation**: Choose between Quick Clean for targeted file deletion or Deep Clean for complete system wiping
- **User-Friendly Interface**: Simple, intuitive desktop application that guides you through the deletion process
- **Privacy-First Design**: Works completely offline with no cloud dependencies or data transmission
- **Cross-Platform Support**: Native support for Windows and Linux operating systems

## Features

### Desktop Application (Quick Clean)

The SecureWipe desktop application provides a user-friendly interface for secure file deletion:

- **Smart File Scanning**: Automatically detects and scans common user directories (Documents, Downloads, Desktop, temp folders)
- **Intelligent Categorization**: Files are automatically categorized based on type, size, age, and usage patterns
- **Secure Deletion**: Uses OS-native secure deletion tools (sdelete on Windows, shred on Linux) that overwrite data multiple times
- **Real-Time Progress**: Visual progress indicators show deletion status with detailed statistics
- **Certificate Generation**: Automatically generates cryptographically signed certificates documenting what was deleted
- **Offline Verification**: Verify deletion certificates without internet connectivity
- **Safe Defaults**: Smart defaults prevent accidental deletion of critical system files

### Bootable ISO (Deep Clean)

For complete system wiping before recycling or disposal:

- **Complete System Wipe**: Erase entire drives including OS, hidden partitions, and free space
- **Hardware-Aware**: Optimized deletion methods for SSDs (TRIM) and HDDs (overwrite patterns)
- **Bootable Environment**: Ubuntu-based live environment that runs without installing anything
- **Wizard Interface**: Step-by-step guidance through the complete wiping process
- **NIST Compliance**: Implements NIST SP 800-88 guidelines for media sanitization

### Security & Compliance

- **NIST SP 800-88 Compliant**: Follows National Institute of Standards and Technology guidelines
- **OWASP Secure Logging**: All operations are logged securely with data sanitization
- **Cryptographic Signatures**: Uses industry-standard cryptography (pyca/cryptography library)
- **Offline Operation**: No internet required, works in air-gapped environments
- **Tamper-Proof Certificates**: Digital signatures ensure deletion records cannot be forged

## Installation

### Prerequisites

- Python 3.8 or higher
- Windows 10/11 or Linux (Ubuntu 20.04+, Debian 10+)
- Administrator/root privileges (required for secure deletion)

### Desktop Application

1. **Clone the repository:**
   ```bash
   git clone https://github.com/divyanshu-vr/securewipe.git
   cd securewipe
   ```

2. **Install dependencies:**
   ```bash
   cd desktop-app
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python src/main.py
   ```

### System Requirements

- **Minimum**: 2GB RAM, 500MB free disk space
- **Recommended**: 4GB RAM, 1GB free disk space
- **Permissions**: Administrator/root access for secure deletion operations

## Usage

### Quick Start

1. **Launch SecureWipe**: Run the desktop application
2. **Scan**: Click "Scan Directories" to analyze your user folders
3. **Review**: Examine the categorized file list and select what to delete
4. **Delete**: Click "Secure Delete" to permanently remove selected files
5. **Verify**: Review the generated certificate documenting the deletion

### Command Line Options

```bash
python src/main.py [OPTIONS]

Options:
  --debug          Enable debug logging for troubleshooting
  --version        Display version information
  --help           Show help message
```

### Best Practices

- **Backup First**: Always backup important files before secure deletion
- **Review Carefully**: Double-check file selections before confirming deletion
- **Save Certificates**: Keep deletion certificates for compliance or audit purposes
- **Regular Cleaning**: Periodically delete temporary and unnecessary files
- **Pre-Disposal**: Use Deep Clean mode before recycling or selling devices

## Project Structure

```
securewipe/
├── desktop-app/         # Desktop application (Quick Clean mode)
│   ├── src/            # Application source code
│   │   ├── ui/         # User interface components
│   │   ├── scanner/    # File scanning and categorization
│   │   ├── deletion/   # Secure deletion operations
│   │   └── certificate/ # Certificate generation and verification
│   ├── tests/          # Unit and integration tests
│   └── requirements.txt # Python dependencies
│
├── bootable-iso/        # Bootable environment (Deep Clean mode)
│   └── src/            # ISO customization and tooling
│
├── shared/              # Shared libraries and utilities
│   ├── logging/        # Secure logging framework
│   ├── schema/         # Certificate schema definitions
│   └── crypto/         # Cryptography utilities
│
├── verifier/            # Standalone certificate verification tool
├── docs/                # Documentation
└── scripts/             # Build and deployment scripts
```

## Technology Stack

- **Language**: Python 3.8+ for maximum compatibility
- **UI Framework**: tkinter (included with Python, no external dependencies)
- **Cryptography**: [pyca/cryptography](https://cryptography.io/) for secure operations
- **Secure Deletion**: 
  - Windows: sdelete (Sysinternals)
  - Linux: shred (GNU coreutils)
  - Bootable: nwipe (for complete drives)
- **Data Format**: JSON for certificates and configuration
- **Compliance**: NIST SP 800-88 Rev. 1 media sanitization guidelines

## Certificate Format

SecureWipe generates JSON-formatted certificates that document deletion operations:

```json
{
  "schemaVersion": "1.0.0",
  "certificateId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-15T10:30:00Z",
  "deviceInfo": {
    "deviceId": "DEVICE-ABC123",
    "hostname": "user-laptop",
    "platform": "Windows 11"
  },
  "operationType": "quick_clean",
  "deletionSummary": {
    "totalFiles": 1247,
    "successCount": 1247,
    "totalSize": 2456789123
  },
  "cryptographicProof": {
    "algorithm": "RSA-SHA256",
    "signature": "base64-encoded-signature",
    "publicKey": "base64-encoded-public-key"
  }
}
```

Certificates can be verified using the included verification tool to ensure authenticity and detect tampering.

## Security Model

### Cryptographic Operations

- **Key Generation**: RSA 2048-bit or higher for certificate signing
- **Signature Algorithm**: SHA-256 for hashing, RSA for digital signatures
- **Key Storage**: Private keys protected using OS-native keystore mechanisms
- **Offline Verification**: Public keys embedded in certificates for air-gapped validation

### Deletion Methods

- **Multiple Passes**: Configurable overwrite patterns (default: 3 passes)
- **Randomization**: Random data patterns for each overwrite pass
- **Verification**: Post-deletion verification ensures complete erasure
- **SSD-Aware**: Uses TRIM commands on solid-state drives when supported

### Privacy Protection

- **No Telemetry**: Zero data collection or transmission
- **Local Processing**: All operations performed entirely on your device
- **Secure Logging**: Logs sanitized to prevent sensitive data leakage
- **Offline Operation**: No internet connectivity required

## Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/divyanshu-vr/securewipe.git
cd securewipe

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest desktop-app/tests/unit/test_scanner.py
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy shared/
```

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Code Standards**: Follow [PEP 8](https://pep8.org/) and our [coding standards](docs/architecture/coding-standards.md)
2. **Type Hints**: Use type hints for all function parameters and return values
3. **Documentation**: Add docstrings for public functions and classes
4. **Testing**: Write unit tests for new functionality (aim for >90% coverage)
5. **Security**: Follow OWASP guidelines for secure coding practices

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with clear, descriptive commits
4. Write or update tests as needed
5. Ensure all tests pass and code is formatted
6. Submit a pull request with a clear description

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Architecture Guide](docs/architecture.md)**: System design and architecture
- **[Development Guide](docs/development-guide.md)**: Setup and development workflow
- **[API Documentation](docs/api/)**: Shared module APIs and interfaces
- **[Security Model](docs/security.md)**: Security considerations and best practices

## License

License details to be determined. See [LICENSE](LICENSE) file for more information.

## Support

For questions, issues, or feature requests:

- **Documentation**: Check the [docs/](docs/) directory for detailed guides
- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/divyanshu-vr/securewipe/issues)
- **Discussions**: Join community discussions in the repository

## Acknowledgments

SecureWipe implements industry-standard secure deletion methods and follows guidelines from:

- NIST Special Publication 800-88 Rev. 1 (Media Sanitization)
- OWASP Secure Coding Practices
- Center for Internet Security (CIS) Benchmarks

---

<div align="center">

**Secure deletion you can trust. Privacy you can verify.**

Made with ❤️ by the SecureWipe team

</div>