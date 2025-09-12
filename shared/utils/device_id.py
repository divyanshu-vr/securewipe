"""Device identification utilities."""

import hashlib
import platform
import socket
import uuid
from typing import Optional

try:
    from ..secure_logging.secure_logger import get_logger
except ImportError:
    from secure_logging.secure_logger import get_logger

logger = get_logger(__name__)


def get_device_id() -> str:
    """
    Generate a unique device identifier based on hardware characteristics.
    
    Returns:
        str: Unique device identifier (32-character hex string)
    """
    try:
        # Collect hardware identifiers
        identifiers = []
        
        # MAC address (most stable hardware identifier)
        mac = uuid.getnode()
        identifiers.append(str(mac))
        
        # System UUID (if available)
        try:
            system_uuid = _get_system_uuid()
            if system_uuid:
                identifiers.append(system_uuid)
        except Exception:
            logger.debug("System UUID not available")
        
        # CPU info
        identifiers.append(platform.processor())
        identifiers.append(platform.machine())
        
        # Hostname as fallback
        identifiers.append(socket.gethostname())
        
        # Create deterministic hash
        combined = "|".join(filter(None, identifiers))
        device_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        
        logger.info("Device ID generated successfully")
        return device_hash[:32]  # 32-character identifier
        
    except Exception as e:
        logger.error(f"Failed to generate device ID: {e}")
        # Fallback to MAC address only
        mac = uuid.getnode()
        fallback_hash = hashlib.sha256(str(mac).encode('utf-8')).hexdigest()
        return fallback_hash[:32]


def _get_system_uuid() -> Optional[str]:
    """Get system UUID from various sources."""
    import subprocess
    import sys
    
    try:
        if sys.platform == "win32":
            # Windows: Use wmic
            result = subprocess.run(
                ["wmic", "csproduct", "get", "UUID", "/value"],
                capture_output=True,
                text=True,
                timeout=5
            )
            for line in result.stdout.split('\n'):
                if line.startswith('UUID='):
                    return line.split('=', 1)[1].strip()
                    
        elif sys.platform.startswith("linux"):
            # Linux: Try /sys/class/dmi/id/product_uuid
            try:
                with open('/sys/class/dmi/id/product_uuid', 'r') as f:
                    return f.read().strip()
            except (FileNotFoundError, PermissionError):
                # Fallback to dmidecode
                result = subprocess.run(
                    ["dmidecode", "-s", "system-uuid"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.strip()
                    
        elif sys.platform == "darwin":
            # macOS: Use system_profiler
            result = subprocess.run(
                ["system_profiler", "SPHardwareDataType"],
                capture_output=True,
                text=True,
                timeout=5
            )
            for line in result.stdout.split('\n'):
                if 'Hardware UUID' in line:
                    return line.split(':', 1)[1].strip()
                    
    except Exception:
        pass
    
    return None


def get_device_info() -> dict:
    """
    Get comprehensive device information for certificate.
    
    Returns:
        dict: Device information including ID, hostname, OS, etc.
    """
    try:
        import getpass
        
        device_info = {
            "device_id": get_device_id(),
            "hostname": socket.gethostname(),
            "operating_system": _get_os_name(),
            "architecture": _normalize_architecture(platform.machine()),
            "user_context": getpass.getuser()
        }
        
        logger.info("Device information collected successfully")
        return device_info
        
    except Exception as e:
        logger.error(f"Failed to collect device information: {e}")
        raise


def _get_os_name() -> str:
    """Get standardized OS name."""
    system = platform.system().lower()
    
    if system == "windows":
        return "Windows"
    elif system == "linux":
        return "Linux"
    elif system == "darwin":
        return "macOS"
    else:
        return system.capitalize()


def _normalize_architecture(arch: str) -> str:
    """Normalize architecture string to schema-compliant values."""
    arch_lower = arch.lower()
    
    # Map common architecture names to schema values
    if arch_lower in ["amd64", "x86_64", "x64"]:
        return "x86_64"
    elif arch_lower in ["aarch64", "arm64"]:
        return "aarch64"
    elif arch_lower in ["i386", "i686", "x86"]:
        return "x86"
    else:
        # Default to x86_64 for unknown architectures
        logger.warning(f"Unknown architecture '{arch}', defaulting to x86_64")
        return "x86_64"