"""Test schema validator functionality."""

import sys
import unittest
from pathlib import Path

# Add shared to path
sys.path.append(str(Path(__file__).parent.parent))

from schema.validator import validate_certificate


class TestSchemaValidator(unittest.TestCase):
    """Test certificate schema validation."""

    def test_valid_certificate(self):
        """Test validation of valid certificate."""
        valid_cert = {
            "schemaVersion": "1.0.0",
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

        # Should not raise exception
        self.assertTrue(validate_certificate(valid_cert))


if __name__ == "__main__":
    unittest.main()
