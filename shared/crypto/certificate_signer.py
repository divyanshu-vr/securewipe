"""Abstract certificate signer interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple


class CertificateSigner(ABC):
    """Abstract interface for certificate signing."""

    @abstractmethod
    def generate_keypair(self) -> Tuple[str, str]:
        """Generate public/private key pair.

        Returns:
            Tuple of (public_key, private_key)
        """
        pass

    @abstractmethod
    def sign_certificate(
        self, certificate_data: Dict[str, Any], private_key: str
    ) -> str:
        """Sign certificate data.

        Args:
            certificate_data: Certificate to sign
            private_key: Private key for signing

        Returns:
            Base64 encoded signature
        """
        pass

    @abstractmethod
    def verify_signature(
        self, certificate_data: Dict[str, Any], signature: str, public_key: str
    ) -> bool:
        """Verify certificate signature.

        Args:
            certificate_data: Certificate data
            signature: Signature to verify
            public_key: Public key for verification

        Returns:
            True if signature is valid
        """
        pass
