"""Tests for certificate generation functionality."""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))

from certificate.certificate_generator import CertificateGenerator, CertificateGenerationError
from models.certificate import Certificate, OperationType, DeletionMethod


class TestCertificateGenerator(unittest.TestCase):
    """Test certificate generation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.generator = CertificateGenerator()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('certificate.certificate_generator.get_device_info')
    def test_certificate_generation_success(self, mock_device_info):
        """Test successful certificate generation."""
        # Mock device info
        mock_device_info.return_value = {
            "device_id": "test_device_123456789",  # Must be at least 16 characters
            "hostname": "test-host",
            "operating_system": "Windows",
            "architecture": "x86_64",
            "user_context": "test_user"
        }

        # Test data
        operation_data = {
            "operation_type": "quick_clean",
            "deletion_method": "sdelete",
            "duration_seconds": 15.5
        }

        file_operations = [
            {
                "path": "/test/file1.txt",
                "size_bytes": 1024,
                "status": "deleted"
            },
            {
                "path": "/test/file2.txt", 
                "size_bytes": 2048,
                "status": "deleted"
            },
            {
                "path": "/test/file3.txt",
                "size_bytes": 512,
                "status": "failed",
                "reason": "Permission denied"
            }
        ]

        # Generate certificate
        certificate, cert_path = self.generator.generate_certificate(
            operation_data, file_operations, self.temp_dir / "test_cert.json"
        )

        # Verify certificate structure
        self.assertIsInstance(certificate, Certificate)
        self.assertEqual(certificate.schema_version, "1.0.0")
        self.assertEqual(certificate.operation_type, OperationType.QUICK_CLEAN)
        self.assertEqual(certificate.deletion_summary.deletion_method, DeletionMethod.SDELETE)
        self.assertEqual(certificate.deletion_summary.total_files, 3)
        self.assertEqual(certificate.deletion_summary.success_count, 2)
        self.assertEqual(certificate.deletion_summary.failure_count, 1)
        self.assertEqual(certificate.deletion_summary.total_size_bytes, 3584)

        # Verify file was created
        self.assertTrue(cert_path.exists())

        # Verify JSON structure
        with open(cert_path, 'r') as f:
            cert_dict = json.load(f)

        self.assertIn("schemaVersion", cert_dict)
        self.assertIn("certificateId", cert_dict)
        self.assertIn("timestamp", cert_dict)
        self.assertIn("deviceInfo", cert_dict)
        self.assertIn("cryptographicProof", cert_dict)

    def test_certificate_validation_failure(self):
        """Test certificate validation failure."""
        # Mock invalid signer
        with patch.object(self.generator, 'signer', None):
            operation_data = {"operation_type": "quick_clean"}
            file_operations = []

            with self.assertRaises(CertificateGenerationError):
                self.generator.generate_certificate(operation_data, file_operations)

    @patch('certificate.certificate_generator.get_device_info')
    def test_large_file_list_performance(self, mock_device_info):
        """Test certificate generation with large file list (performance test)."""
        # Mock device info
        mock_device_info.return_value = {
            "device_id": "test_device_123456789",  # Must be at least 16 characters
            "hostname": "test-host",
            "operating_system": "Windows",
            "architecture": "x86_64",
            "user_context": "test_user"
        }

        # Generate large file list (10,000 files)
        file_operations = []
        for i in range(10000):
            file_operations.append({
                "path": f"/test/file_{i}.txt",
                "size_bytes": 1024,
                "status": "deleted"
            })

        operation_data = {
            "operation_type": "quick_clean",
            "deletion_method": "sdelete",
            "duration_seconds": 120.0
        }

        # Measure generation time
        start_time = datetime.now()
        certificate, cert_path = self.generator.generate_certificate(
            operation_data, file_operations, self.temp_dir / "large_cert.json"
        )
        end_time = datetime.now()

        generation_time = (end_time - start_time).total_seconds()

        # Verify performance requirement (30 seconds max)
        self.assertLess(generation_time, 30.0, 
                       f"Certificate generation took {generation_time:.2f}s, exceeds 30s limit")

        # Verify certificate was generated correctly
        self.assertEqual(certificate.deletion_summary.total_files, 10000)
        self.assertEqual(len(certificate.file_operations), 10000)

    def test_certificate_verification(self):
        """Test certificate signature verification."""
        # Generate a certificate first
        with patch('certificate.certificate_generator.get_device_info') as mock_device_info:
            mock_device_info.return_value = {
                "device_id": "test_device_123456789",
                "hostname": "test-host",
                "operating_system": "Windows",
                "architecture": "x86_64",
                "user_context": "test_user"
            }

            operation_data = {
                "operation_type": "quick_clean",
                "deletion_method": "sdelete",
                "duration_seconds": 5.0
            }

            file_operations = [{
                "path": "/test/file.txt",
                "size_bytes": 1024,
                "status": "deleted"
            }]

            certificate, cert_path = self.generator.generate_certificate(
                operation_data, file_operations, self.temp_dir / "verify_cert.json"
            )

        # Verify the certificate
        is_valid = self.generator.verify_certificate(cert_path)
        self.assertTrue(is_valid, "Certificate signature verification failed")

    def test_certificate_schema_compliance(self):
        """Test certificate compliance with JSON schema."""
        with patch('certificate.certificate_generator.get_device_info') as mock_device_info:
            mock_device_info.return_value = {
                "device_id": "test_device_123456789",
                "hostname": "test-host",
                "operating_system": "Windows",
                "architecture": "x86_64",
                "user_context": "test_user"
            }

            operation_data = {
                "operation_type": "quick_clean",
                "deletion_method": "sdelete",
                "duration_seconds": 10.0
            }

            file_operations = [{
                "path": "/test/schema_test.txt",
                "size_bytes": 2048,
                "status": "deleted"
            }]

            # This should not raise an exception if schema validation passes
            certificate, cert_path = self.generator.generate_certificate(
                operation_data, file_operations, self.temp_dir / "schema_cert.json"
            )

            # Load and verify JSON structure
            with open(cert_path, 'r') as f:
                cert_dict = json.load(f)

            # Verify required fields exist
            required_fields = [
                "schemaVersion", "certificateId", "timestamp", "deviceInfo",
                "operationType", "deletionSummary", "fileOperations", "cryptographicProof"
            ]

            for field in required_fields:
                self.assertIn(field, cert_dict, f"Required field '{field}' missing from certificate")

    def test_default_save_location(self):
        """Test certificate saves to default location when no path specified."""
        with patch('certificate.certificate_generator.get_device_info') as mock_device_info:
            mock_device_info.return_value = {
                "device_id": "test_device_123456789",
                "hostname": "test-host",
                "operating_system": "Windows",
                "architecture": "x86_64",
                "user_context": "test_user"
            }

            operation_data = {
                "operation_type": "quick_clean",
                "deletion_method": "sdelete",
                "duration_seconds": 5.0
            }

            file_operations = [{
                "path": "/test/default_location.txt",
                "size_bytes": 1024,
                "status": "deleted"
            }]

            # Generate without specifying save path
            certificate, cert_path = self.generator.generate_certificate(
                operation_data, file_operations
            )

            # Verify path is in Documents folder
            self.assertTrue(str(cert_path).endswith('.json'))
            self.assertIn('Documents', str(cert_path))


if __name__ == '__main__':
    unittest.main()