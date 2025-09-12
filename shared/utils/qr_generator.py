"""QR code generation utilities."""

import base64
from io import BytesIO
from pathlib import Path
from typing import Optional, Union

try:
    import qrcode
    from PIL import Image
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

try:
    from ..secure_logging.secure_logger import get_logger
except ImportError:
    from secure_logging.secure_logger import get_logger

logger = get_logger(__name__)


class QRGeneratorError(Exception):
    """QR code generation error."""
    pass


def generate_qr_code(
    data: str,
    output_path: Optional[Union[str, Path]] = None,
    size: int = 10,
    border: int = 4
) -> Optional[bytes]:
    """
    Generate QR code for certificate data.
    
    Args:
        data: Data to encode in QR code
        output_path: Optional file path to save QR code image
        size: QR code size (1-40, higher = more data capacity)
        border: Border size in modules
        
    Returns:
        bytes: PNG image data if successful, None if QR library unavailable
        
    Raises:
        QRGeneratorError: If QR code generation fails
    """
    if not QR_AVAILABLE:
        logger.warning("QR code library not available - install qrcode[pil]")
        return None
        
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,  # Auto-adjust version based on data
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=size,
            border=border,
        )
        
        # Add data and optimize
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to file if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(output_path)
            logger.info(f"QR code saved to {output_path}")
        
        # Return PNG bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        png_data = buffer.getvalue()
        buffer.close()
        
        logger.info("QR code generated successfully")
        return png_data
        
    except Exception as e:
        logger.error(f"QR code generation failed: {e}")
        raise QRGeneratorError(f"Failed to generate QR code: {e}") from e


def generate_certificate_qr(certificate_path: Union[str, Path]) -> Optional[bytes]:
    """
    Generate QR code linking to certificate file.
    
    Args:
        certificate_path: Path to certificate file
        
    Returns:
        bytes: PNG image data or None if unavailable
    """
    if not QR_AVAILABLE:
        return None
        
    try:
        cert_path = Path(certificate_path)
        
        # Create QR data with file reference
        qr_data = f"securewipe-certificate:{cert_path.name}"
        
        return generate_qr_code(qr_data)
        
    except Exception as e:
        logger.error(f"Certificate QR generation failed: {e}")
        raise QRGeneratorError(f"Failed to generate certificate QR: {e}") from e


def get_qr_data_limit() -> int:
    """
    Get maximum data capacity for QR codes.
    
    Returns:
        int: Maximum bytes that can be encoded
    """
    if not QR_AVAILABLE:
        return 0
        
    # QR Code version 40 with error correction M can hold ~2953 bytes
    return 2953


def is_qr_available() -> bool:
    """Check if QR code generation is available."""
    return QR_AVAILABLE