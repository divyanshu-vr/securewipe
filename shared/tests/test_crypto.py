"""Test cryptography implementations."""

import unittest
import sys
from pathlib import Path

# Add shared to path
sys.path.append(str(Path(__file__).parent.parent))

from crypto.key_management import get_signer


class TestCryptography(unittest.TestCase):
    """Test cryptography functionality."""

    def test_key_generation(self):
        """Test key pair generation."""
        signer = get_signer()
        public_key, private_key = signer.generate_keypair()

        self.assertIsInstance(public_key, str)
        self.assertIsInstance(private_key, str)
        self.assertGreater(len(public_key), 0)
        self.assertGreater(len(private_key), 0)

    def test_sign_and_verify(self):
        """Test certificate signing and verification."""
        signer = get_signer()
        public_key, private_key = signer.generate_keypair()

        test_data = {
            "schemaVersion": "1.0.0",
            "certificateId": "test-cert-id",
            "timestamp": "2024-12-19T10:30:00Z",
        }

        # Sign
        signature = signer.sign_certificate(test_data, private_key)
        self.assertIsInstance(signature, str)
        self.assertGreater(len(signature), 0)

        # Verify
        is_valid = signer.verify_signature(test_data, signature, public_key)
        self.assertTrue(is_valid)

        # Verify with wrong signature should fail
        is_invalid = signer.verify_signature(test_data, "invalid-signature", public_key)
        self.assertFalse(is_invalid)


if __name__ == "__main__":
    unittest.main()
