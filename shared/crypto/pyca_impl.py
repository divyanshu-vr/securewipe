"""pyca/cryptography implementation."""

import base64
import json
from pathlib import Path
from typing import Any, Dict, Tuple

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

try:
    from .certificate_signer import CertificateSigner
except ImportError:
    from certificate_signer import CertificateSigner
try:
    from .key_management import KeyManager
except ImportError:
    from key_management import KeyManager


class PycaCertificateSigner(CertificateSigner):
    """Certificate signer using pyca/cryptography."""

    def __init__(self):
        self.key_manager = KeyManager()
        self._private_key = None
        self._public_key = None
        self._load_or_generate_keys()

    def _load_or_generate_keys(self):
        """Load existing keys or generate new ones."""
        try:
            # Try to load existing keys
            keys = self.key_manager.load_keys()
            if keys:
                self._private_key = serialization.load_pem_private_key(
                    keys["private_key"].encode(), password=None
                )
                self._public_key = serialization.load_pem_public_key(
                    keys["public_key"].encode()
                )
            else:
                # Generate new keys
                self._generate_and_store_keys()
        except Exception:
            # Fallback to generating new keys
            self._generate_and_store_keys()

    def _generate_and_store_keys(self):
        """Generate new key pair and store securely."""
        self._private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048
        )
        self._public_key = self._private_key.public_key()

        # Store keys
        private_pem = self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()

        public_pem = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()

        self.key_manager.store_keys(public_pem, private_pem)

    def generate_keypair(self) -> Tuple[str, str]:
        """Generate RSA-2048 key pair."""
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()

        public_pem = (
            private_key.public_key()
            .public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode()
        )

        return public_pem, private_pem

    def sign_certificate(
        self, certificate_data: Dict[str, Any], private_key: str
    ) -> str:
        """Sign certificate with RSA-2048-SHA256."""
        # Remove cryptographicProof for signing
        data_to_sign = {
            k: v for k, v in certificate_data.items() if k != "cryptographicProof"
        }
        message = json.dumps(data_to_sign, sort_keys=True).encode()

        key = serialization.load_pem_private_key(private_key.encode(), password=None)
        signature = key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )

        return base64.b64encode(signature).decode()

    def verify_signature(
        self, certificate_data: Dict[str, Any], signature: str, public_key: str
    ) -> bool:
        """Verify RSA signature."""
        try:
            # Remove cryptographicProof for verification
            data_to_verify = {
                k: v for k, v in certificate_data.items() if k != "cryptographicProof"
            }
            message = json.dumps(data_to_verify, sort_keys=True).encode()

            key = serialization.load_pem_public_key(public_key.encode())
            sig_bytes = base64.b64decode(signature)

            key.verify(
                sig_bytes,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False

    def sign(self, data: bytes) -> Dict[str, str]:
        """Sign raw data and return signature metadata."""
        if not self._private_key:
            raise RuntimeError("No private key available")

        signature = self._private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )

        public_pem = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()

        return {
            "algorithm": "RSA-2048-SHA256",
            "public_key": public_pem,
            "signature": base64.b64encode(signature).decode(),
            "signature_format": "base64"
        }

    def verify(self, data: bytes, signature_data: Dict[str, str]) -> bool:
        """Verify raw data signature."""
        try:
            public_key = serialization.load_pem_public_key(
                signature_data["public_key"].encode()
            )
            signature = base64.b64decode(signature_data["signature"])

            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False


# Alias for backward compatibility
CertificateSigner = PycaCertificateSigner
