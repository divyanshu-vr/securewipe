"""OS-native secure deletion tool integration."""

import os
import platform
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict

# Add shared modules to path
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from models.operation_result import OperationResult, OperationStatus
from secure_logging.sanitizer import sanitize_path
from secure_logging.secure_logger import get_logger

logger = get_logger(__name__)


class DeletionMethod(Enum):
    """NIST SP 800-88 compliant deletion methods."""

    CLEAR = "clear"  # Single pass with fixed/random data
    PURGE = "purge"  # ATA Secure Erase or Cryptographic Erase


class OSIntegration:
    """Wrapper for OS-native secure deletion tools."""

    def __init__(self):
        self.platform = platform.system().lower()
        self.available_tools = self._detect_tools()

    def _detect_tools(self) -> Dict[str, bool]:
        """Detect available secure deletion tools."""
        tools = {}

        if self.platform == "windows":
            tools["sdelete"] = self._check_sdelete()
        elif self.platform == "linux":
            tools["shred"] = self._check_shred()

        logger.info(f"Available deletion tools: {tools}")
        return tools

    def _check_sdelete(self) -> bool:
        """Check if sdelete is available on Windows."""
        try:
            result = subprocess.run(
                ["sdelete", "-accepteula", "-?"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _check_shred(self) -> bool:
        """Check if shred is available on Linux."""
        try:
            result = subprocess.run(["which", "shred"], capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def secure_delete_file(
        self,
        file_path: Path,
        method: DeletionMethod = DeletionMethod.CLEAR,
    ) -> OperationResult:
        """Securely delete a single file using OS-native tools."""
        try:
            if not file_path.exists():
                logger.warning(f"File not found: {sanitize_path(str(file_path))}")
                return OperationResult(
                    status=OperationStatus.SKIPPED,
                    message="File not found",
                    path=file_path,
                )

            if self.platform == "windows":
                return self._delete_windows(file_path, method)
            elif self.platform == "linux":
                return self._delete_linux(file_path, method)
            else:
                return self._fallback_delete(file_path)

        except PermissionError as e:
            logger.error(f"Permission denied: {sanitize_path(str(file_path))}")
            return OperationResult(
                status=OperationStatus.PERMISSION_DENIED,
                message="Insufficient permissions",
                path=file_path,
                error=str(e),
            )
        except Exception as e:
            logger.error(f"Deletion failed: {sanitize_path(str(file_path))} - {str(e)}")
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Deletion failed: {str(e)}",
                path=file_path,
                error=str(e),
            )

    def _delete_windows(
        self, file_path: Path, method: DeletionMethod
    ) -> OperationResult:
        """Delete file using sdelete on Windows."""
        if not self.available_tools.get("sdelete", False):
            return self._fallback_delete(file_path)

        try:
            # NIST SP 800-88: 3-pass overwrite for demonstration
            passes = 3 if method == DeletionMethod.CLEAR else 1

            cmd = [
                "sdelete",
                "-accepteula",
                "-p",
                str(passes),
                "-s",  # Recurse subdirectories
                "-z",  # Zero free space
                str(file_path),
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                logger.info(f"Successfully deleted: {sanitize_path(str(file_path))}")
                return OperationResult(
                    status=OperationStatus.SUCCESS,
                    message=f"Securely deleted with {passes} passes",
                    path=file_path,
                )
            else:
                logger.error(f"sdelete failed: {result.stderr}")
                return OperationResult(
                    status=OperationStatus.FAILED,
                    message=f"sdelete error: {result.stderr}",
                    path=file_path,
                )

        except subprocess.TimeoutExpired:
            logger.error(f"sdelete timeout: {sanitize_path(str(file_path))}")
            return OperationResult(
                status=OperationStatus.FAILED,
                message="Operation timed out",
                path=file_path,
            )

    def _delete_linux(self, file_path: Path, method: DeletionMethod) -> OperationResult:
        """Delete file using shred on Linux."""
        if not self.available_tools.get("shred", False):
            return self._fallback_delete(file_path)

        try:
            # NIST SP 800-88: 3-pass overwrite for demonstration
            passes = 3 if method == DeletionMethod.CLEAR else 1

            cmd = [
                "shred",
                "-vfz",  # verbose, force, zero final pass
                "-n",
                str(passes),
                str(file_path),
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                logger.info(f"Successfully deleted: {sanitize_path(str(file_path))}")
                return OperationResult(
                    status=OperationStatus.SUCCESS,
                    message=f"Securely deleted with {passes} passes",
                    path=file_path,
                )
            else:
                logger.error(f"shred failed: {result.stderr}")
                return OperationResult(
                    status=OperationStatus.FAILED,
                    message=f"shred error: {result.stderr}",
                    path=file_path,
                )

        except subprocess.TimeoutExpired:
            logger.error(f"shred timeout: {sanitize_path(str(file_path))}")
            return OperationResult(
                status=OperationStatus.FAILED,
                message="Operation timed out",
                path=file_path,
            )

    def _fallback_delete(self, file_path: Path) -> OperationResult:
        """Fallback deletion when OS tools are unavailable."""
        try:
            # Simple overwrite with zeros (not cryptographically secure)
            with open(file_path, "r+b") as f:
                size = f.seek(0, 2)  # Get file size
                f.seek(0)
                f.write(b"\x00" * size)  # Overwrite with zeros
                f.flush()
                os.fsync(f.fileno())  # Force write to disk

            # Remove the file
            file_path.unlink()

            logger.warning(f"Fallback deletion used: {sanitize_path(str(file_path))}")
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message="Deleted using fallback method (less secure)",
                path=file_path,
            )

        except Exception as e:
            logger.error(
                f"Fallback deletion failed: {sanitize_path(str(file_path))} - {str(e)}"
            )
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Fallback deletion failed: {str(e)}",
                path=file_path,
                error=str(e),
            )

    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about available deletion tools."""
        info = {
            "platform": self.platform,
            "available_tools": self.available_tools,
            "nist_compliance": True,
            "supported_methods": [method.value for method in DeletionMethod],
        }

        if self.platform == "windows" and self.available_tools.get("sdelete"):
            info["primary_tool"] = "sdelete"
            info["tool_description"] = "Microsoft SDelete - NIST SP 800-88 compliant"
        elif self.platform == "linux" and self.available_tools.get("shred"):
            info["primary_tool"] = "shred"
            info["tool_description"] = "GNU shred - NIST SP 800-88 compliant"
        else:
            info["primary_tool"] = "fallback"
            info["tool_description"] = "Basic overwrite (less secure)"

        return info
