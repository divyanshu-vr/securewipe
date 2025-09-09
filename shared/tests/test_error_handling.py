"""Test error handling and edge cases."""

import unittest
import sys
from pathlib import Path

# Add shared to path
sys.path.append(str(Path(__file__).parent.parent))

from schema.validator import validate_certificate
from utils.exceptions import CertificateValidationError


class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios."""

    def test_invalid_certificate_raises_proper_exception(self):
        """Test that invalid certificates raise CertificateValidationError."""
        invalid_cert = {
            "schemaVersion": "1.0.0",
            # Missing required fields
        }

        with self.assertRaises(CertificateValidationError):
            validate_certificate(invalid_cert)

    def test_invalid_schema_version(self):
        """Test handling of invalid schema version."""
        invalid_cert = {
            "schemaVersion": "2.0.0",  # Unsupported version
            "certificateId": "550e8400-e29b-41d4-a716-446655440000",
            "timestamp": "2024-12-19T10:30:00Z",
            "deviceInfo": {
                "deviceId": "test-device-123456",
                "hostname": "test-desktop",
                "operatingSystem": "Windows",
                "architecture": "x86_64",
                "userContext": "testuser",
            },
            "operationType": "quick_clean",
            "deletionSummary": {
                "totalFiles": 5,
                "totalSizeBytes": 1024,
                "deletionMethod": "sdelete",
                "durationSeconds": 30.5,
                "successCount": 5,
                "failureCount": 0,
            },
            "fileOperations": [],
            "cryptographicProof": {
                "algorithm": "RSA-2048-SHA256",
                "publicKey": "test-public-key",
                "signature": "test-signature",
                "signatureFormat": "base64",
            },
        }

        with self.assertRaises(CertificateValidationError):
            validate_certificate(invalid_cert)


if __name__ == "__main__":
    unittest.main()
