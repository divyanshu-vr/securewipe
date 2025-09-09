# SecureWipe Coding Standards

## Critical Rules for AI Agents

### Certificate Schema Compliance
- All certificate generation MUST validate against `shared/schema/certificate_v1.json`
- Use `shared.schema.validator.validate_certificate()` before saving
- Never modify certificate structure without schema version bump

### OWASP Secure Logging
- Use `shared.logging.secure_logger` for ALL file system operations
- Never log full file paths - use `sanitizer.sanitize_path()`
- Log levels: ERROR for failures, INFO for operations, DEBUG for development only

### Error Handling Patterns
```python
# Required pattern for OS operations
try:
    result = os_operation()
except PermissionError as e:
    logger.error(f"Permission denied: {sanitizer.sanitize_path(path)}")
    raise SecureWipeError("Insufficient permissions") from e
except FileNotFoundError as e:
    logger.warning(f"File not found: {sanitizer.sanitize_path(path)}")
    return OperationResult.SKIPPED
```

### Cross-Platform File Operations
- Use `pathlib.Path` for ALL file system operations
- Never use string concatenation for paths
- Test path operations on both Windows and Linux

### Cryptography Implementation
```python
# Primary implementation with fallback
try:
    from shared.crypto.pyca_impl import CertificateSigner
    signer = CertificateSigner()
except ImportError:
    from shared.crypto.minisign_impl import CertificateSigner
    signer = CertificateSigner()
```

## File Organization Rules

### Module Structure
```
module_name/
├── __init__.py          # Public API only
├── core.py             # Main implementation
├── exceptions.py       # Module-specific exceptions
└── tests/
    └── test_core.py    # Comprehensive tests
```

### Import Standards
```python
# Standard library first
import os
import sys
from pathlib import Path

# Third-party libraries
import pytest

# Local imports last
from shared.schema import validator
from shared.logging import secure_logger
```

## Testing Requirements

### Unit Test Structure
```python
class TestSecureDelete:
    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
        
    def test_delete_single_file_success(self):
        # Arrange
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("sensitive data")
        
        # Act
        result = secure_delete_file(test_file)
        
        # Assert
        assert result.status == OperationStatus.SUCCESS
        assert not test_file.exists()
```

## Security Guidelines

### Sensitive Data Handling
- Never store passwords or keys in plain text
- Use OS keystore for certificate private keys
- Sanitize all user input before logging
- Clear sensitive variables after use: `del sensitive_data`

### Input Validation
```python
def validate_file_path(path: str) -> Path:
    """Validate and normalize file path input."""
    if not path or len(path) > 4096:
        raise ValueError("Invalid path length")
    
    normalized = Path(path).resolve()
    if not normalized.is_relative_to(Path.home()):
        raise SecurityError("Path outside user directory")
    
    return normalized
```

## Performance Standards

### File Scanning
- Process files in batches of 1000
- Update progress every 100ms minimum
- Use generators for large directory traversal
- Implement cancellation support

### Memory Management
```python
def scan_large_directory(directory: Path) -> Iterator[FileInfo]:
    """Scan directory without loading all files into memory."""
    for batch in batch_files(directory, batch_size=1000):
        yield from process_batch(batch)
        gc.collect()
```