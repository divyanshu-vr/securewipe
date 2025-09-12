"""Certificate generation and signing service."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

# Add shared modules to path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared"))

try:
    from models.certificate import (
        Certificate, DeviceInfo, DeletionSummary, FileOperation,
        CryptographicProof, OperationType, DeletionMethod, OperationStatus
    )
    from schema.validator import validate_certificate
    from crypto.certificate_signer import CertificateSigner
    from utils.device_id import get_device_info
    from secure_logging.secure_logger import get_logger
except ImportError:
    # Fallback for different import contexts
    from shared.models.certificate import (
        Certificate, DeviceInfo, DeletionSummary, FileOperation,
        CryptographicProof, OperationType, DeletionMethod, OperationStatus
    )
    from shared.schema.validator import validate_certificate
    from shared.crypto.certificate_signer import CertificateSigner
    from shared.utils.device_id import get_device_info
    from shared.secure_logging.secure_logger import get_logger

logger = get_logger(__name__)


class CertificateGenerationError(Exception):
    """Certificate generation error."""
    pass


class CertificateGenerator:
    """Handles certificate generation and cryptographic signing."""
    
    def __init__(self):
        self.signer: Optional[CertificateSigner] = None
        self._initialize_signer()
    
    def _initialize_signer(self):
        """Initialize cryptographic signer with fallback."""
        try:
            # Try pyca/cryptography first
            try:
                from crypto.pyca_impl import PycaCertificateSigner
                self.signer = PycaCertificateSigner()
                logger.info("Initialized pyca/cryptography signer")
            except ImportError:
                from shared.crypto.pyca_impl import PycaCertificateSigner
                self.signer = PycaCertificateSigner()
                logger.info("Initialized pyca/cryptography signer")
        except ImportError:
            try:
                # Fallback to minisign
                try:
                    from crypto.minisign_impl import MinisignCertificateSigner
                    self.signer = MinisignCertificateSigner()
                    logger.info("Initialized minisign fallback signer")
                except ImportError:
                    from shared.crypto.minisign_impl import MinisignCertificateSigner
                    self.signer = MinisignCertificateSigner()
                    logger.info("Initialized minisign fallback signer")
            except ImportError:
                logger.error("No cryptographic signer available")
                raise CertificateGenerationError("No cryptographic implementation available")
    
    def generate_certificate(
        self,
        operation_data: dict,
        file_operations: List[dict],
        save_path: Optional[Path] = None
    ) -> Tuple[Certificate, Path]:
        """
        Generate and save cryptographically signed certificate.
        
        Args:
            operation_data: Deletion operation metadata
            file_operations: List of file operations performed
            save_path: Optional custom save location
            
        Returns:
            Tuple[Certificate, Path]: Generated certificate and file path
            
        Raises:
            CertificateGenerationError: If certificate generation fails
        """
        try:
            logger.info("Starting certificate generation")
            
            # Generate certificate data
            certificate = self._create_certificate_data(operation_data, file_operations)
            
            # Sign certificate
            signed_certificate = self._sign_certificate(certificate)
            
            # Validate against schema
            self._validate_certificate(signed_certificate)
            
            # Save certificate
            cert_path = self._save_certificate(signed_certificate, save_path)
            
            logger.info(f"Certificate generated successfully: {cert_path}")
            return signed_certificate, cert_path
            
        except Exception as e:
            logger.error(f"Certificate generation failed: {e}")
            raise CertificateGenerationError(f"Failed to generate certificate: {e}") from e
    
    def _create_certificate_data(self, operation_data: dict, file_operations: List[dict]) -> Certificate:
        """Create certificate data structure."""
        # Generate unique certificate ID
        certificate_id = str(uuid.uuid4())
        
        # Get device information
        device_data = get_device_info()
        device_info = DeviceInfo(
            device_id=device_data["device_id"],
            hostname=device_data["hostname"],
            operating_system=device_data["operating_system"],
            architecture=device_data["architecture"],
            user_context=device_data["user_context"]
        )
        
        # Create deletion summary
        total_files = len(file_operations)
        total_size = sum(op.get("size_bytes", 0) for op in file_operations)
        success_count = sum(1 for op in file_operations if op.get("status") == "deleted")
        failure_count = total_files - success_count
        
        deletion_summary = DeletionSummary(
            total_files=total_files,
            total_size_bytes=total_size,
            deletion_method=DeletionMethod(operation_data.get("deletion_method", "sdelete")),
            duration_seconds=operation_data.get("duration_seconds", 0.0),
            success_count=success_count,
            failure_count=failure_count
        )
        
        # Convert file operations
        cert_file_ops = []
        for op in file_operations:
            file_op = FileOperation(
                path=op["path"],
                size_bytes=op.get("size_bytes", 0),
                operation=OperationStatus(op.get("status", "failed")),
                reason=op.get("reason") if op.get("reason") is not None else None
            )
            cert_file_ops.append(file_op)
        
        # Create certificate (without signature initially)
        certificate = Certificate(
            schema_version="1.0.0",
            certificate_id=certificate_id,
            timestamp=datetime.now(timezone.utc),
            device_info=device_info,
            operation_type=OperationType(operation_data.get("operation_type", "quick_clean")),
            deletion_summary=deletion_summary,
            file_operations=cert_file_ops,
            cryptographic_proof=CryptographicProof(
                algorithm="",
                public_key="",
                signature="",
                signature_format=""
            )
        )
        
        return certificate
    
    def _sign_certificate(self, certificate: Certificate) -> Certificate:
        """Add cryptographic signature to certificate."""
        if not self.signer:
            raise CertificateGenerationError("No signer available")
        
        # Convert certificate to JSON for signing (without signature)
        cert_dict = self._certificate_to_dict(certificate)
        cert_dict.pop("cryptographicProof", None)  # Remove empty signature
        
        cert_json = json.dumps(cert_dict, sort_keys=True, separators=(',', ':'))
        cert_bytes = cert_json.encode('utf-8')
        
        # Sign the certificate data
        signature_data = self.signer.sign(cert_bytes)
        
        # Update certificate with signature
        certificate.cryptographic_proof = CryptographicProof(
            algorithm=signature_data["algorithm"],
            public_key=signature_data["public_key"],
            signature=signature_data["signature"],
            signature_format=signature_data["signature_format"]
        )
        
        return certificate
    
    def _validate_certificate(self, certificate: Certificate):
        """Validate certificate against JSON schema."""
        cert_dict = self._certificate_to_dict(certificate)
        
        try:
            validate_certificate(cert_dict)
            logger.info("Certificate validation passed")
        except Exception as e:
            logger.error(f"Certificate validation failed: {e}")
            raise CertificateGenerationError(f"Certificate validation failed: {e}") from e
    
    def _save_certificate(self, certificate: Certificate, save_path: Optional[Path] = None) -> Path:
        """Save certificate to file."""
        if save_path is None:
            # Generate default filename
            timestamp = certificate.timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"securewipe_certificate_{timestamp}.json"
            save_path = Path.home() / "Documents" / filename
        
        # Ensure directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dictionary and save
        cert_dict = self._certificate_to_dict(certificate)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(cert_dict, f, indent=2, default=str)
        
        logger.info(f"Certificate saved to {save_path}")
        return save_path
    
    def _certificate_to_dict(self, certificate: Certificate) -> dict:
        """Convert certificate to dictionary for JSON serialization."""
        return {
            "schemaVersion": certificate.schema_version,
            "certificateId": certificate.certificate_id,
            "timestamp": certificate.timestamp.isoformat(),
            "deviceInfo": {
                "deviceId": certificate.device_info.device_id,
                "hostname": certificate.device_info.hostname,
                "operatingSystem": certificate.device_info.operating_system,
                "architecture": certificate.device_info.architecture,
                "userContext": certificate.device_info.user_context
            },
            "operationType": certificate.operation_type.value,
            "deletionSummary": {
                "totalFiles": certificate.deletion_summary.total_files,
                "totalSizeBytes": certificate.deletion_summary.total_size_bytes,
                "deletionMethod": certificate.deletion_summary.deletion_method.value,
                "durationSeconds": certificate.deletion_summary.duration_seconds,
                "successCount": certificate.deletion_summary.success_count,
                "failureCount": certificate.deletion_summary.failure_count
            },
            "fileOperations": [
                {
                    k: v for k, v in {
                        "path": op.path,
                        "sizeBytes": op.size_bytes,
                        "operation": op.operation.value,
                        "reason": op.reason
                    }.items() if v is not None
                }
                for op in certificate.file_operations
            ],
            "cryptographicProof": {
                "algorithm": certificate.cryptographic_proof.algorithm,
                "publicKey": certificate.cryptographic_proof.public_key,
                "signature": certificate.cryptographic_proof.signature,
                "signatureFormat": certificate.cryptographic_proof.signature_format
            }
        }
    
    def verify_certificate(self, certificate_path: Path) -> bool:
        """
        Verify certificate signature.
        
        Args:
            certificate_path: Path to certificate file
            
        Returns:
            bool: True if signature is valid
        """
        try:
            with open(certificate_path, 'r', encoding='utf-8') as f:
                cert_dict = json.load(f)
            
            # Extract signature data
            crypto_proof = cert_dict.pop("cryptographicProof")
            
            # Recreate signed data
            cert_json = json.dumps(cert_dict, sort_keys=True, separators=(',', ':'))
            cert_bytes = cert_json.encode('utf-8')
            
            # Verify signature
            if self.signer:
                return self.signer.verify(cert_bytes, crypto_proof)
            
            return False
            
        except Exception as e:
            logger.error(f"Certificate verification failed: {e}")
            return False