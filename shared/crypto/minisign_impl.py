"""Minisign fallback implementation."""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Tuple
from .certificate_signer import CertificateSigner


class MinisignCertificateSigner(CertificateSigner):
    """Certificate signer using minisign as fallback."""

    def generate_keypair(self) -> Tuple[str, str]:
        """Generate Ed25519 key pair using minisign."""
        with tempfile.TemporaryDirectory() as temp_dir:
            key_path = Path(temp_dir) / "key"

            # Generate key pair
            subprocess.run(
                ["minisign", "-G", "-p", f"{key_path}.pub", "-s", f"{key_path}.sec"],
                check=True,
                input=b"\n",
            )  # Empty passphrase

            public_key = (key_path.with_suffix(".pub")).read_text().strip()
            private_key = (key_path.with_suffix(".sec")).read_text().strip()

            return public_key, private_key

    def sign_certificate(
        self, certificate_data: Dict[str, Any], private_key: str
    ) -> str:
        """Sign certificate with Ed25519."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Write private key
            key_file = temp_path / "key.sec"
            key_file.write_text(private_key)

            # Write data to sign
            data_to_sign = {
                k: v for k, v in certificate_data.items() if k != "cryptographicProof"
            }
            data_file = temp_path / "data.json"
            data_file.write_text(json.dumps(data_to_sign, sort_keys=True))

            # Sign
            sig_file = temp_path / "data.json.minisig"
            subprocess.run(
                ["minisign", "-S", "-s", str(key_file), "-m", str(data_file)],
                check=True,
            )

            return sig_file.read_text().strip()

    def verify_signature(
        self, certificate_data: Dict[str, Any], signature: str, public_key: str
    ) -> bool:
        """Verify Ed25519 signature."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Write public key
                pub_file = temp_path / "key.pub"
                pub_file.write_text(public_key)

                # Write data
                data_to_verify = {
                    k: v
                    for k, v in certificate_data.items()
                    if k != "cryptographicProof"
                }
                data_file = temp_path / "data.json"
                data_file.write_text(json.dumps(data_to_verify, sort_keys=True))

                # Write signature
                sig_file = temp_path / "data.json.minisig"
                sig_file.write_text(signature)

                # Verify
                result = subprocess.run(
                    ["minisign", "-V", "-p", str(pub_file), "-m", str(data_file)],
                    capture_output=True,
                )

                return result.returncode == 0
        except Exception:
            return False
