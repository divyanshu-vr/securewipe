"""Key generation and storage utilities."""

import os
from pathlib import Path
from typing import Optional, Tuple, Dict

try:
    from ..secure_logging.secure_logger import get_logger
except ImportError:
    from secure_logging.secure_logger import get_logger

logger = get_logger(__name__)


class KeyManager:
    """Manages cryptographic keys for certificate signing."""
    
    def __init__(self, key_dir: Optional[Path] = None):
        if key_dir is None:
            key_dir = Path.home() / ".securewipe" / "keys"
        self.key_dir = key_dir
        self.key_dir.mkdir(parents=True, exist_ok=True)
        
        # Set secure permissions on key directory
        try:
            os.chmod(self.key_dir, 0o700)  # Owner only
        except OSError:
            logger.warning("Could not set secure permissions on key directory")
    
    def store_keys(self, public_key: str, private_key: str):
        """Store key pair securely."""
        try:
            # Store private key with secure permissions
            private_path = self.key_dir / "private.pem"
            private_path.write_text(private_key, encoding='utf-8')
            try:
                os.chmod(private_path, 0o600)  # Owner read/write only
            except OSError:
                logger.warning("Could not set secure permissions on private key")
            
            # Store public key
            public_path = self.key_dir / "public.pem"
            public_path.write_text(public_key, encoding='utf-8')
            
            logger.info("Keys stored successfully")
            
        except Exception as e:
            logger.error(f"Failed to store keys: {e}")
            raise
    
    def load_keys(self) -> Optional[Dict[str, str]]:
        """Load existing key pair."""
        try:
            private_path = self.key_dir / "private.pem"
            public_path = self.key_dir / "public.pem"
            
            if not (private_path.exists() and public_path.exists()):
                return None
            
            private_key = private_path.read_text(encoding='utf-8')
            public_key = public_path.read_text(encoding='utf-8')
            
            logger.info("Keys loaded successfully")
            return {
                "private_key": private_key,
                "public_key": public_key
            }
            
        except Exception as e:
            logger.error(f"Failed to load keys: {e}")
            return None
    
    def keys_exist(self) -> bool:
        """Check if key pair exists."""
        private_path = self.key_dir / "private.pem"
        public_path = self.key_dir / "public.pem"
        return private_path.exists() and public_path.exists()


def get_signer():
    """Get available certificate signer implementation."""
    try:
        from .pyca_impl import PycaCertificateSigner
        return PycaCertificateSigner()
    except ImportError:
        try:
            from .minisign_impl import MinisignCertificateSigner
            return MinisignCertificateSigner()
        except ImportError:
            raise ImportError("No cryptographic signer implementation available")


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
    try:
        os.chmod(private_key_path, 0o600)  # Owner read/write only
    except OSError:
        pass

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
