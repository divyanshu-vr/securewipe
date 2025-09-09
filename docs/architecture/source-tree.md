# SecureWipe Source Tree Organization

## Repository Structure

```
SecureWipe/
├── .github/
│   └── workflows/
│       ├── desktop-ci.yml           # Desktop app CI/CD
│       ├── iso-build.yml            # Bootable ISO build
│       └── certificate-compat.yml   # Cross-mode compatibility tests
├── desktop-app/                     # Team 1: Desktop Quick Clean
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                  # Application entry point
│   │   ├── ui/                      # User interface components
│   │   │   ├── __init__.py
│   │   │   ├── main_window.py       # Primary application window
│   │   │   ├── progress_dialog.py   # Deletion progress display
│   │   │   ├── certificate_viewer.py # Certificate display/export
│   │   │   └── components/          # Reusable UI components
│   │   │       ├── file_tree.py     # File selection tree
│   │   │       ├── category_panel.py # File categorization display
│   │   │       └── ai_suggestions.py # Optional AI recommendations
│   │   ├── scanner/                 # File system scanning
│   │   │   ├── __init__.py
│   │   │   ├── file_scanner.py      # Directory traversal and analysis
│   │   │   ├── categorizer.py       # Rule-based file categorization
│   │   │   └── metadata_extractor.py # File metadata collection
│   │   ├── deletion/                # Secure deletion engine
│   │   │   ├── __init__.py
│   │   │   ├── secure_delete.py     # Main deletion orchestrator
│   │   │   ├── os_integration.py    # sdelete/shred wrapper
│   │   │   └── progress_tracker.py  # Real-time progress monitoring
│   │   ├── ai/                      # Optional AI features
│   │   │   ├── __init__.py
│   │   │   ├── file_classifier.py   # ML-based file importance
│   │   │   └── suggestion_engine.py # User recommendation system
│   │   └── config/                  # Configuration management
│   │       ├── __init__.py
│   │       ├── settings.py          # User preferences
│   │       └── defaults.py          # Default configurations
│   ├── tests/                       # Desktop application tests
│   │   ├── unit/
│   │   │   ├── test_scanner.py
│   │   │   ├── test_deletion.py
│   │   │   └── test_ui_components.py
│   │   ├── integration/
│   │   │   ├── test_full_workflow.py
│   │   │   └── test_certificate_generation.py
│   │   └── fixtures/                # Test data and mocks
│   ├── requirements.txt             # Python dependencies
│   ├── requirements-dev.txt         # Development dependencies
│   ├── build.py                     # PyInstaller build script
│   └── README.md                    # Desktop app documentation
├── bootable-iso/                    # Team 2: Bootable Deep Clean
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                  # ISO application entry point
│   │   ├── wizard/                  # User interface wizard
│   │   │   ├── __init__.py
│   │   │   ├── main_wizard.py       # Step-by-step wizard
│   │   │   ├── hardware_detect.py   # Storage device detection
│   │   │   ├── confirmation.py      # Multi-step confirmations
│   │   │   └── progress_display.py  # Wipe progress visualization
│   │   ├── wiping/                  # Disk wiping operations
│   │   │   ├── __init__.py
│   │   │   ├── nwipe_wrapper.py     # nwipe integration
│   │   │   ├── device_manager.py    # Hardware device management
│   │   │   └── wipe_methods.py      # NIST-compliant wipe algorithms
│   │   ├── tui/                     # Text-based fallback interface
│   │   │   ├── __init__.py
│   │   │   ├── ncurses_ui.py        # Terminal-based interface
│   │   │   └── menu_system.py       # Navigation menus
│   │   └── system/                  # System integration
│   │       ├── __init__.py
│   │       ├── hardware_info.py     # System information collection
│   │       └── boot_environment.py  # Live environment utilities
│   ├── build/                       # ISO customization
│   │   ├── customize-iso.sh         # Ubuntu ISO modification script
│   │   ├── preseed.cfg              # Automated installation config
│   │   ├── isolinux/                # Boot loader configuration
│   │   └── packages.list            # Required Ubuntu packages
│   ├── tests/                       # Bootable system tests
│   │   ├── vm/                      # Virtual machine test scripts
│   │   │   ├── test_boot.py         # Boot sequence validation
│   │   │   └── test_hardware_detect.py # Device detection tests
│   │   └── unit/
│   │       ├── test_nwipe_wrapper.py
│   │       └── test_wizard.py
│   ├── requirements.txt             # Python dependencies for ISO
│   └── README.md                    # Bootable ISO documentation
├── shared/                          # Shared components (Both teams)
│   ├── __init__.py
│   ├── schema/                      # Certificate schema definitions
│   │   ├── __init__.py
│   │   ├── certificate_v1.json      # JSON schema specification
│   │   ├── validator.py             # Schema validation logic
│   │   └── migration.py             # Schema version migration
│   ├── crypto/                      # Cryptography implementations
│   │   ├── __init__.py
│   │   ├── certificate_signer.py    # Abstract signer interface
│   │   ├── pyca_impl.py             # pyca/cryptography implementation
│   │   ├── minisign_impl.py         # minisign fallback implementation
│   │   └── key_management.py        # Key generation and storage
│   ├── logging/                     # OWASP-compliant logging
│   │   ├── __init__.py
│   │   ├── secure_logger.py         # Main logging interface
│   │   ├── sanitizer.py             # Data sanitization utilities
│   │   └── formatters.py            # Custom log formatters
│   ├── utils/                       # Common utilities
│   │   ├── __init__.py
│   │   ├── device_id.py             # Unique device identification
│   │   ├── qr_generator.py          # QR code creation
│   │   ├── file_utils.py            # Cross-platform file operations
│   │   └── exceptions.py            # Custom exception classes
│   └── models/                      # Data models and types
│       ├── __init__.py
│       ├── certificate.py           # Certificate data structures
│       ├── file_info.py             # File metadata models
│       └── operation_result.py      # Operation status tracking
├── verifier/                        # Standalone certificate verifier
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                  # Verifier application entry
│   │   ├── verifier_ui.py           # Simple verification interface
│   │   ├── certificate_validator.py # Certificate verification logic
│   │   └── qr_scanner.py            # QR code scanning capability
│   ├── tests/
│   │   ├── test_verification.py
│   │   └── test_ui.py
│   ├── build.py                     # Standalone executable build
│   └── README.md                    # Verifier documentation
├── scripts/                         # Build and deployment automation
│   ├── setup-dev-env.sh             # Development environment setup
│   ├── setup-dev-env.bat            # Windows development setup
│   ├── run-tests.sh                 # Comprehensive test runner
│   ├── build-all.sh                 # Build all components
│   ├── build-desktop.sh             # Desktop app build
│   ├── build-iso.sh                 # Bootable ISO build
│   └── validate-certificates.py     # Certificate compatibility testing
├── docs/                            # Project documentation
│   ├── prd.md                       # Product Requirements Document
│   ├── architecture.md              # System architecture
│   ├── architecture/                # Detailed architecture docs
│   │   ├── coding-standards.md      # Development standards
│   │   ├── tech-stack.md            # Technology details
│   │   └── source-tree.md           # This file
│   ├── development-guide.md         # Developer onboarding
│   ├── api/                         # API documentation
│   │   ├── certificate-schema.md    # Certificate format specification
│   │   └── shared-modules.md        # Shared component APIs
│   └── deployment/                  # Deployment guides
│       ├── desktop-deployment.md    # Desktop app distribution
│       └── iso-creation.md          # Bootable ISO creation
├── .env.example                     # Environment configuration template
├── .gitignore                       # Git ignore patterns
├── requirements-dev.txt             # Global development dependencies
├── pyproject.toml                   # Python project configuration
└── README.md                        # Project overview and quick start
```

## Team Responsibilities

### Team 1: Desktop Application (desktop-app/)
**Focus:** Quick Clean mode for user directories
**Key Components:**
- tkinter-based user interface
- File system scanning and categorization
- Secure deletion using OS-native tools
- Certificate generation and display
- Optional AI-powered suggestions

### Team 2: Bootable ISO (bootable-iso/)
**Focus:** Deep Clean mode for complete system wiping
**Key Components:**
- Ubuntu Live ISO customization
- Hardware detection and device management
- nwipe integration for disk-level operations
- Wizard interface (GUI/TUI fallback)
- Certificate generation for offline verification

### Shared Responsibilities (shared/)
**Focus:** Common components and compatibility
**Key Components:**
- Certificate schema and validation
- Cryptography implementations with fallback
- OWASP-compliant secure logging
- Cross-platform utilities and models

## Development Workflow

### Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd SecureWipe

# Setup development environment
./scripts/setup-dev-env.sh

# Install shared dependencies
pip install -r requirements-dev.txt
```

### Team-Specific Development
```bash
# Desktop team
cd desktop-app
pip install -r requirements.txt
python src/main.py

# Bootable team
cd bootable-iso
pip install -r requirements.txt
# ISO development requires VM environment
```

### Testing Strategy
```bash
# Run all tests
./scripts/run-tests.sh

# Team-specific tests
cd desktop-app && python -m pytest tests/
cd bootable-iso && python -m pytest tests/

# Certificate compatibility tests
python scripts/validate-certificates.py
```

### Build Process
```bash
# Build all components
./scripts/build-all.sh

# Individual builds
./scripts/build-desktop.sh    # Creates desktop executable
./scripts/build-iso.sh        # Creates bootable ISO
```

## File Naming Conventions

### Python Modules
- **snake_case** for all Python files
- **PascalCase** for class names
- **UPPER_CASE** for constants

### Configuration Files
- **kebab-case** for shell scripts
- **snake_case** for Python configuration
- **camelCase** for JSON configuration keys

### Test Files
- Prefix with `test_` for pytest discovery
- Mirror source structure in test directories
- Use descriptive test method names

## Import Guidelines

### Shared Module Access
```python
# From desktop-app or bootable-iso
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "shared"))

from schema.validator import validate_certificate
from crypto.certificate_signer import CertificateSigner
```

### Relative Imports Within Modules
```python
# Within desktop-app/src/
from .scanner.file_scanner import FileScanner
from .ui.main_window import MainWindow
```

### External Dependencies
```python
# Standard library first
import os
import sys
from pathlib import Path

# Third-party packages
import tkinter as tk
from cryptography.hazmat.primitives import hashes

# Local imports last
from shared.schema import validator
```

## Documentation Standards

### Code Documentation
- Docstrings for all public functions and classes
- Type hints for function parameters and returns
- Inline comments for complex logic only

### README Files
- Each major directory has README.md
- Include setup instructions and usage examples
- Document any special requirements or dependencies

### API Documentation
- Shared modules documented in docs/api/
- Certificate schema specification maintained
- Integration examples for both teams