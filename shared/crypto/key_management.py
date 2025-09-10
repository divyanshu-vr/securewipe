"""Key generation and storage utilities."""

from pathlib import Path
from typing import Optional, Tuple

from .certificate_signer import CertificateSigner


def get_signer() -> CertificateSigner:
    """Get available certificate signer implementation."""
    try:
        from .pyca_impl import PycaCertificateSigner

        return PycaCertificateSigner()
    except ImportError:
        from .minisign_impl import MinisignCertificateSigner

        return MinisignCertificateSigner()


def generate_and_store_keypair(key_dir: Optional[Path] = None) -> Tuple[str, Path]:
    """Generate and store key pair.

    Args:
        key_dir: Directory to store keys (default: ~/.securewipe/keys)

    Returns:
        Tuple of (public_key, private_key_path)
    """
    if key_dir is None:
        key_dir = Path.home() / ".securewipe" / "keys"

    key_dir.mkdir(parents=True, exist_ok=True)

    signer = get_signer()
    public_key, private_key = signer.generate_keypair()

    # Store private key securely
    private_key_path = key_dir / "private.pem"
    private_key_path.write_text(private_key)
    private_key_path.chmod(0o600)  # Owner read/write only

    # Store public key
    public_key_path = key_dir / "public.pem"
    public_key_path.write_text(public_key)

    return public_key, private_key_path


def load_private_key(key_path: Path) -> str:
    """Load private key from file.

    Args:
        key_path: Path to private key file

    Returns:
        Private key content
    """
    return key_path.read_text()
