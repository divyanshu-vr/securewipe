# SecureWipe Technology Stack Details

## Core Technologies

### Python 3.8+ Runtime
**Purpose:** Cross-platform compatibility and rapid development
**Installation:** 
```bash
# Windows
winget install Python.Python.3.11
# Linux
sudo apt install python3.11 python3.11-venv
```

### Desktop Framework: tkinter
**Purpose:** Native GUI without external dependencies
**Key Components:**
- `tkinter.ttk` for modern widgets
- `tkinter.filedialog` for file selection
- `tkinter.messagebox` for user notifications
- Custom progress bars for deletion operations

### Cryptography Stack

#### Primary: pyca/cryptography
```bash
pip install cryptography==41.0.2
```
**Usage:**
```python
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
```

#### Fallback: minisign
```bash
# Windows
winget install jedisct1.minisign
# Linux
sudo apt install minisign
```

### Secure Deletion Tools

#### Windows: sdelete
**Download:** Microsoft Sysinternals
**Usage:** `sdelete -p 3 -s -z C:\path\to\delete`

#### Linux: shred
**Built-in:** GNU coreutils
**Usage:** `shred -vfz -n 3 /path/to/file`

#### Bootable: nwipe
**Installation:** 
```bash
sudo apt install nwipe
```
**Integration:** Python subprocess wrapper

## Development Dependencies

### Testing Framework
```bash
pip install pytest==7.4.3 pytest-cov==4.1.0
```

### Build Tools
```bash
pip install pyinstaller==6.2.0
```

### Development Tools
```bash
pip install black==23.11.0 flake8==6.1.0 mypy==1.7.1
```

## Platform-Specific Considerations

### Windows Development
- Visual Studio Build Tools for native extensions
- Windows SDK for system integration
- PowerShell for build scripts

### Linux Development
- GCC compiler for native extensions
- libc6-dev for system headers
- bash for build scripts

### Cross-Platform Testing
- GitHub Actions for automated testing
- VirtualBox/VMware for ISO testing
- Docker for consistent build environments

## Security Libraries

### Certificate Validation
```python
# JSON Schema validation
pip install jsonschema==4.20.0

# QR Code generation
pip install qrcode[pil]==7.4.2
```

### Logging Security
```python
# Built-in logging with custom sanitization
import logging
import re

class SecureFormatter(logging.Formatter):
    def format(self, record):
        # Sanitize sensitive data
        record.msg = sanitize_paths(record.msg)
        return super().format(record)
```

## Build Configuration

### PyInstaller Spec
```python
# desktop-app/build.spec
a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[('shared/schema/', 'shared/schema/')],
    hiddenimports=['tkinter', 'cryptography'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
```

### ISO Build Dependencies
```bash
# Ubuntu packages for ISO customization
sudo apt install squashfs-tools genisoimage isolinux
```

## Version Management

### Dependency Pinning
```txt
# requirements.txt - exact versions for reproducible builds
cryptography==41.0.2
pyinstaller==6.2.0
pytest==7.4.3
qrcode==7.4.2
jsonschema==4.20.0
```

### Python Version Matrix
- **Minimum:** Python 3.8 (Ubuntu 20.04 LTS compatibility)
- **Recommended:** Python 3.11 (performance and features)
- **Maximum:** Python 3.12 (latest stable)

## Performance Optimization

### Memory Management
```python
# Use generators for large file operations
def scan_directory(path: Path) -> Iterator[FileInfo]:
    for item in path.iterdir():
        yield FileInfo(item)
        # Explicit cleanup for large operations
        if should_cleanup():
            gc.collect()
```

### Threading Strategy
```python
# UI responsiveness during long operations
import threading
from concurrent.futures import ThreadPoolExecutor

def long_operation_with_progress(files, progress_callback):
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(process_file, f) for f in files]
        for i, future in enumerate(futures):
            result = future.result()
            progress_callback(i / len(futures))
```

## Integration Points

### Shared Module Access
```python
# All applications import shared components
import sys
sys.path.append(str(Path(__file__).parent.parent / "shared"))

from schema.validator import validate_certificate
from crypto.certificate_signer import CertificateSigner
from logging.secure_logger import get_logger
```

### Certificate Compatibility
```python
# Ensure compatibility between desktop and bootable modes
CERTIFICATE_SCHEMA_VERSION = "1.0.0"
SUPPORTED_CRYPTO_ALGORITHMS = ["RSA-2048", "Ed25519"]
CERTIFICATE_FORMAT = "JSON"
```

## Deployment Strategy

### Desktop Application
1. PyInstaller creates standalone executable
2. Include shared/ modules in bundle
3. Embed certificate schema and public keys
4. Sign executable for Windows SmartScreen

### Bootable ISO
1. Ubuntu LTS base with minimal modifications
2. Python runtime and dependencies pre-installed
3. SecureWipe application in /opt/securewipe/
4. Auto-start script for wizard interface

### Certificate Verifier
1. Separate PyInstaller build
2. Embedded public keys for offline verification
3. Minimal dependencies for portability
4. Cross-platform executable distribution