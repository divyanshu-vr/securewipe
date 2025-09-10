#!/usr/bin/env python3
"""Certificate compatibility validation tests."""

import json
import unittest
from pathlib import Path

import jsonschema


class TestCertificateCompatibility(unittest.TestCase):
    """Validate certificate compatibility between desktop and bootable modes."""

    def setUp(self):
        """Load certificate schema."""
        schema_path = Path(__file__).parent.parent / "schema" / "certificate_v1.json"
        with open(schema_path) as f:
            self.schema = json.load(f)

    def test_desktop_certificate_format(self):
        """Test desktop-generated certificate validates against schema."""
        desktop_cert = {
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
            "fileOperations": [
                {
                    "path": "C:\\Users\\test\\temp.txt",
                    "sizeBytes": 1024,
                    "operation": "deleted",
                }
            ],
            "cryptographicProof": {
                "algorithm": "RSA-2048-SHA256",
                "publicKey": "test-public-key",
                "signature": "test-signature",
                "signatureFormat": "base64",
            },
        }

        jsonschema.validate(desktop_cert, self.schema)

    def test_bootable_certificate_format(self):
        """Test bootable-generated certificate validates against schema."""
        bootable_cert = {
            "schemaVersion": "1.0.0",
            "certificateId": "550e8400-e29b-41d4-a716-446655440001",
            "timestamp": "2024-12-19T10:35:00Z",
            "deviceInfo": {
                "deviceId": "test-device-789012",
                "hostname": "securewipe-live",
                "operatingSystem": "Linux",
                "architecture": "x86_64",
                "userContext": "root",
            },
            "operationType": "deep_clean",
            "deletionSummary": {
                "totalFiles": 0,
                "totalSizeBytes": 500000000,
                "deletionMethod": "nwipe-dod",
                "durationSeconds": 600.0,
                "successCount": 1,
                "failureCount": 0,
            },
            "fileOperations": [],
            "cryptographicProof": {
                "algorithm": "Ed25519",
                "publicKey": "test-ed25519-key",
                "signature": "test-ed25519-sig",
                "signatureFormat": "hex",
            },
        }

        jsonschema.validate(bootable_cert, self.schema)


if __name__ == "__main__":
    unittest.main()
