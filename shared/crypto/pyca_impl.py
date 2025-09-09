"""pyca/cryptography implementation."""

import json
import base64
from typing import Dict, Any, Tuple
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

from .certificate_signer import CertificateSigner


class PycaCertificateSigner(CertificateSigner):
    """Certificate signer using pyca/cryptography."""

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
