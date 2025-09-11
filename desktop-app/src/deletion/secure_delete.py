"""Main secure deletion orchestrator."""

import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared"))

from models.file_info import FileInfo
from models.operation_result import OperationResult, OperationStatus
from secure_logging.sanitizer import sanitize_path
from secure_logging.secure_logger import get_logger

from .os_integration import DeletionMethod, OSIntegration
from .progress_tracker import ProgressInfo, ProgressState, ProgressTracker

logger = get_logger(__name__)


@dataclass
class DeletionConfig:
    """Configuration for deletion operations."""

    deletion_method: DeletionMethod = DeletionMethod.CLEAR
    skip_system_files: bool = True
    require_confirmation: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0


class SecureDeleteEngine:
    """Main orchestrator for secure file deletion operations."""

    def __init__(
        self, progress_callback: Optional[Callable[[ProgressInfo], None]] = None
    ):
        self.os_integration = OSIntegration()
        self.progress_tracker = ProgressTracker(progress_callback)
        self.config = DeletionConfig()
        self._deletion_thread: Optional[threading.Thread] = None

    def validate_files(self, files: List[FileInfo]) -> Dict[str, List[FileInfo]]:
        """Validate files before deletion and categorize them."""
        validation_result = {
            "safe_to_delete": [],
            "system_files": [],
            "locked_files": [],
            "missing_files": [],
        }

        for file_info in files:
            try:
                file_path = Path(file_info.path)

                # Check if file exists
                if not file_path.exists():
                    validation_result["missing_files"].append(file_info)
                    continue

                # Check if it's a system file
                if self._is_system_file(file_path):
                    validation_result["system_files"].append(file_info)
                    continue

                # Check if file is locked
                if self._is_file_locked(file_path):
                    validation_result["locked_files"].append(file_info)
                    continue

                # File is safe to delete
                validation_result["safe_to_delete"].append(file_info)

            except Exception as e:
                logger.error(
                    f"Validation error for "
                    f"{sanitize_path(str(file_info.path))}: {str(e)}"
                )
                validation_result["locked_files"].append(file_info)

        logger.info(
            f"File validation complete: "
            f"{len(validation_result['safe_to_delete'])} safe, "
            f"{len(validation_result['system_files'])} system, "
            f"{len(validation_result['locked_files'])} locked, "
            f"{len(validation_result['missing_files'])} missing"
        )

        return validation_result

    def delete_files_async(self, files: List[FileInfo]) -> threading.Thread:
        """Start asynchronous deletion of files."""
        if self._deletion_thread and self._deletion_thread.is_alive():
            raise RuntimeError("Deletion operation already in progress")

        self._deletion_thread = threading.Thread(
            target=self._delete_files_worker, args=(files,), daemon=True
        )
        self._deletion_thread.start()
        return self._deletion_thread

    def delete_files_sync(self, files: List[FileInfo]) -> List[OperationResult]:
        """Synchronously delete files."""
        return self._delete_files_worker(files)

    def _delete_files_worker(self, files: List[FileInfo]) -> List[OperationResult]:
        """Worker method for file deletion."""
        results = []

        try:
            # Validate files first
            validation = self.validate_files(files)

            # Get files safe to delete
            safe_files = validation["safe_to_delete"]

            # Calculate total size for progress tracking
            total_size = sum(getattr(f, "size", 0) for f in safe_files)

            # Start progress tracking
            self.progress_tracker.start_operation(len(safe_files), total_size)

            # Process each file
            for file_info in safe_files:
                # Check for cancellation or pause
                if not self.progress_tracker.wait_if_paused():
                    logger.info("Deletion operation cancelled")
                    break

                # Update current file
                file_path = Path(file_info.path)
                file_size = getattr(file_info, "size", 0)
                self.progress_tracker.update_current_file(file_path, file_size)

                # Attempt deletion with retries
                result = self._delete_file_with_retries(file_path)
                results.append(result)

                # Update progress
                self.progress_tracker.file_completed(result, file_size)

            # Handle files that couldn't be deleted
            for file_info in validation["system_files"]:
                result = OperationResult(
                    status=OperationStatus.SKIPPED,
                    message="System file - skipped for safety",
                    path=Path(file_info.path),
                )
                results.append(result)
                self.progress_tracker.file_completed(result)

            for file_info in validation["locked_files"]:
                result = OperationResult(
                    status=OperationStatus.PERMISSION_DENIED,
                    message="File is locked or in use",
                    path=Path(file_info.path),
                )
                results.append(result)
                self.progress_tracker.file_completed(result)

            for file_info in validation["missing_files"]:
                result = OperationResult(
                    status=OperationStatus.SKIPPED,
                    message="File not found",
                    path=Path(file_info.path),
                )
                results.append(result)
                self.progress_tracker.file_completed(result)

            logger.info(f"Deletion operation completed: {len(results)} files processed")

        except Exception as e:
            logger.error(f"Deletion operation failed: {str(e)}")
            # Ensure progress tracker is updated even on error
            if self.progress_tracker.progress_info.state == ProgressState.RUNNING:
                self.progress_tracker.cancel()

        return results

    def _delete_file_with_retries(self, file_path: Path) -> OperationResult:
        """Delete a file with retry logic."""
        last_result = None

        for attempt in range(self.config.max_retries):
            try:
                result = self.os_integration.secure_delete_file(
                    file_path, self.config.deletion_method
                )

                if result.status == OperationStatus.SUCCESS:
                    return result

                last_result = result

                # Don't retry certain errors
                if result.status in [
                    OperationStatus.SKIPPED,
                    OperationStatus.PERMISSION_DENIED,
                ]:
                    break

                # Wait before retry
                if attempt < self.config.max_retries - 1:
                    import time

                    time.sleep(self.config.retry_delay)

            except Exception as e:
                logger.error(
                    f"Deletion attempt {attempt + 1} failed: "
                    f"{sanitize_path(str(file_path))} - {str(e)}"
                )
                last_result = OperationResult(
                    status=OperationStatus.FAILED,
                    message=f"Attempt {attempt + 1} failed: {str(e)}",
                    path=file_path,
                    error=str(e),
                )

        return last_result or OperationResult(
            status=OperationStatus.FAILED,
            message="All retry attempts failed",
            path=file_path,
        )

    def _is_system_file(self, file_path: Path) -> bool:
        """Check if file is a system file that should not be deleted."""
        if not self.config.skip_system_files:
            return False

        path_str = str(file_path).lower()

        # Windows system paths
        system_paths = [
            "c:\\windows\\",
            "c:\\program files\\",
            "c:\\program files (x86)\\",
            "c:\\programdata\\",
            "/bin/",
            "/sbin/",
            "/usr/bin/",
            "/usr/sbin/",
            "/lib/",
            "/usr/lib/",
            "/etc/",
            "/boot/",
            "/sys/",
            "/proc/",
        ]

        return any(path_str.startswith(sys_path) for sys_path in system_paths)

    def _is_file_locked(self, file_path: Path) -> bool:
        """Check if file is locked or in use."""
        try:
            # Try to open file in exclusive mode
            with open(file_path, "r+b"):
                pass
            return False
        except (PermissionError, OSError):
            return True

    def pause_operation(self):
        """Pause the current deletion operation."""
        self.progress_tracker.pause()

    def resume_operation(self):
        """Resume the paused deletion operation."""
        self.progress_tracker.resume()

    def cancel_operation(self):
        """Cancel the current deletion operation."""
        self.progress_tracker.cancel()

    def get_progress(self) -> ProgressInfo:
        """Get current operation progress."""
        return self.progress_tracker.get_progress_info()

    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about available deletion tools."""
        return self.os_integration.get_tool_info()

    def set_config(self, config: DeletionConfig):
        """Update deletion configuration."""
        self.config = config
        logger.info(
            f"Deletion config updated: method={config.deletion_method.value}, "
            f"skip_system={config.skip_system_files}, "
            f"retries={config.max_retries}"
        )

    def is_operation_active(self) -> bool:
        """Check if a deletion operation is currently active."""
        return (
            self._deletion_thread
            and self._deletion_thread.is_alive()
            and self.progress_tracker.is_running()
        )
