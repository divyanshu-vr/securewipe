"""Tests for certificate viewer functionality."""

import tempfile
import tkinter as tk
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import sys
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared"))

from ui.certificate_viewer import CertificateViewer
from shared.models.certificate import (
    Certificate, DeviceInfo, DeletionSummary, FileOperation,
    CryptographicProof, OperationType, DeletionMethod, OperationStatus
)


class TestCertificateViewer(unittest.TestCase):
    """Test certificate viewer functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests
        self.viewer = CertificateViewer(self.root)
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create test certificate
        self.test_certificate = Certificate(
            schema_version="1.0.0",
            certificate_id="test-cert-123",
            timestamp=datetime.now(timezone.utc),
            device_info=DeviceInfo(
                device_id="test_device_123456789",
                hostname="test-host",
                operating_system="Windows",
                architecture="x86_64",
                user_context="test_user"
            ),
            operation_type=OperationType.QUICK_CLEAN,
            deletion_summary=DeletionSummary(
                total_files=3,
                total_size_bytes=3584,
                deletion_method=DeletionMethod.SDELETE,
                duration_seconds=15.5,
                success_count=2,
                failure_count=1
            ),
            file_operations=[
                FileOperation(
                    path="/test/file1.txt",
                    size_bytes=1024,
                    operation=OperationStatus.DELETED
                ),
                FileOperation(
                    path="/test/file2.txt",
                    size_bytes=2048,
                    operation=OperationStatus.DELETED
                ),
                FileOperation(
                    path="/test/file3.txt",
                    size_bytes=512,
                    operation=OperationStatus.FAILED,
                    reason="Permission denied"
                )
            ],
            cryptographic_proof=CryptographicProof(
                algorithm="RSA-2048-SHA256",
                public_key="test_public_key",
                signature="test_signature",
                signature_format="base64"
            )
        )

    def tearDown(self):
        """Clean up test fixtures."""
        self.root.destroy()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_certificate_display(self):
        """Test certificate display functionality."""
        cert_path = self.temp_dir / "test_cert.json"
        cert_path.write_text('{"test": "data"}')

        # This should not raise an exception
        try:
            self.viewer.show_certificate(self.test_certificate, cert_path)
        except Exception as e:
            self.fail(f"Certificate display failed: {e}")

    def test_certificate_to_dict_conversion(self):
        """Test certificate to dictionary conversion."""
        cert_dict = self.viewer._certificate_to_dict()

        # Verify structure
        self.assertIn("schemaVersion", cert_dict)
        self.assertIn("certificateId", cert_dict)
        self.assertIn("timestamp", cert_dict)
        self.assertIn("deviceInfo", cert_dict)
        self.assertIn("operationType", cert_dict)
        self.assertIn("deletionSummary", cert_dict)
        self.assertIn("fileOperations", cert_dict)
        self.assertIn("cryptographicProof", cert_dict)

        # Verify values
        self.assertEqual(cert_dict["schemaVersion"], "1.0.0")
        self.assertEqual(cert_dict["certificateId"], "test-cert-123")
        self.assertEqual(cert_dict["operationType"], "quick_clean")
        self.assertEqual(len(cert_dict["fileOperations"]), 3)

    def test_file_size_formatting(self):
        """Test file size formatting utility."""
        # Test various sizes
        self.assertEqual(self.viewer._format_size(0), "0.0 B")
        self.assertEqual(self.viewer._format_size(512), "512.0 B")
        self.assertEqual(self.viewer._format_size(1024), "1.0 KB")
        self.assertEqual(self.viewer._format_size(1048576), "1.0 MB")
        self.assertEqual(self.viewer._format_size(1073741824), "1.0 GB")

    @patch('ui.certificate_viewer.generate_certificate_qr')
    def test_qr_code_generation(self, mock_qr_gen):
        """Test QR code generation for certificate."""
        mock_qr_gen.return_value = b"fake_qr_data"

        cert_path = self.temp_dir / "qr_test_cert.json"
        cert_path.write_text('{"test": "data"}')

        # Set up viewer with certificate
        self.viewer.certificate = self.test_certificate

        # Test QR display creation
        qr_frame = tk.Frame(self.root)
        try:
            self.viewer._create_qr_display(qr_frame, cert_path)
            mock_qr_gen.assert_called_once_with(cert_path)
        except Exception as e:
            self.fail(f"QR code generation test failed: {e}")

    @patch('tkinter.filedialog.asksaveasfilename')
    @patch('shutil.copy2')
    def test_certificate_export(self, mock_copy, mock_dialog):
        """Test certificate export functionality."""
        # Mock file dialog
        export_path = str(self.temp_dir / "exported_cert.json")
        mock_dialog.return_value = export_path

        cert_path = self.temp_dir / "original_cert.json"
        cert_path.write_text('{"test": "data"}')

        # Test export
        try:
            self.viewer._export_certificate(cert_path)
            mock_copy.assert_called_once_with(cert_path, export_path)
        except Exception as e:
            self.fail(f"Certificate export test failed: {e}")

    def test_certificate_info_display(self):
        """Test certificate information display creation."""
        info_frame = tk.Frame(self.root)
        self.viewer.certificate = self.test_certificate

        try:
            self.viewer._create_certificate_info(info_frame)
        except Exception as e:
            self.fail(f"Certificate info display failed: {e}")

    def test_operation_summary_display(self):
        """Test operation summary display creation."""
        summary_frame = tk.Frame(self.root)
        self.viewer.certificate = self.test_certificate

        try:
            self.viewer._create_operation_summary(summary_frame)
        except Exception as e:
            self.fail(f"Operation summary display failed: {e}")

    @patch('tkinter.filedialog.asksaveasfilename')
    def test_qr_code_save(self, mock_dialog):
        """Test QR code save functionality."""
        # Mock file dialog
        qr_path = str(self.temp_dir / "test_qr.png")
        mock_dialog.return_value = qr_path

        # Set fake QR image data
        self.viewer.qr_image = b"fake_png_data"

        try:
            self.viewer._save_qr_code()
            
            # Verify file was created
            saved_path = Path(qr_path)
            self.assertTrue(saved_path.exists())
            
            # Verify content
            with open(saved_path, 'rb') as f:
                content = f.read()
            self.assertEqual(content, b"fake_png_data")
            
        except Exception as e:
            self.fail(f"QR code save test failed: {e}")

    def test_json_view_display(self):
        """Test JSON view functionality."""
        self.viewer.certificate = self.test_certificate

        try:
            self.viewer._view_json()
        except Exception as e:
            self.fail(f"JSON view display failed: {e}")


if __name__ == '__main__':
    unittest.main()