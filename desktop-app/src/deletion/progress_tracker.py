"""Real-time progress tracking for secure deletion operations."""

import sys
import threading
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Optional

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared"))

from models.operation_result import OperationResult, OperationStatus
from secure_logging.secure_logger import get_logger

logger = get_logger(__name__)


class ProgressState(Enum):
    """Progress tracking states."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


@dataclass
class ProgressInfo:
    """Progress information structure."""

    total_files: int
    processed_files: int
    current_file: Optional[Path]
    bytes_processed: int
    total_bytes: int
    elapsed_time: float
    estimated_remaining: float
    state: ProgressState
    success_count: int
    error_count: int
    skipped_count: int


class ProgressTracker:
    """Real-time progress tracking for deletion operations."""

    def __init__(
        self, update_callback: Optional[Callable[[ProgressInfo], None]] = None
    ):
        self.update_callback = update_callback
        self.progress_info = ProgressInfo(
            total_files=0,
            processed_files=0,
            current_file=None,
            bytes_processed=0,
            total_bytes=0,
            elapsed_time=0.0,
            estimated_remaining=0.0,
            state=ProgressState.IDLE,
            success_count=0,
            error_count=0,
            skipped_count=0,
        )

        self._start_time = 0.0
        self._last_update = 0.0
        self._update_interval = 0.1  # 100ms minimum update interval
        self._lock = threading.Lock()
        self._pause_event = threading.Event()
        self._cancel_event = threading.Event()

        # Set initial state to not paused
        self._pause_event.set()

    def start_operation(self, total_files: int, total_bytes: int = 0):
        """Start tracking a new deletion operation."""
        with self._lock:
            self.progress_info.total_files = total_files
            self.progress_info.total_bytes = total_bytes
            self.progress_info.processed_files = 0
            self.progress_info.bytes_processed = 0
            self.progress_info.success_count = 0
            self.progress_info.error_count = 0
            self.progress_info.skipped_count = 0
            self.progress_info.state = ProgressState.RUNNING

            self._start_time = time.time()
            self._last_update = self._start_time

            # Reset events
            self._pause_event.set()
            self._cancel_event.clear()

        self._notify_update()
        logger.info(
            f"Started deletion operation: {total_files} files, "
            f"{total_bytes} bytes"
        )

    def update_current_file(self, file_path: Path, file_size: int = 0):
        """Update the currently processing file."""
        with self._lock:
            self.progress_info.current_file = file_path

        self._notify_update()

    def file_completed(self, result: OperationResult, file_size: int = 0):
        """Mark a file as completed and update counters."""
        with self._lock:
            self.progress_info.processed_files += 1
            self.progress_info.bytes_processed += file_size

            if result.status == OperationStatus.SUCCESS:
                self.progress_info.success_count += 1
            elif result.status == OperationStatus.SKIPPED:
                self.progress_info.skipped_count += 1
            else:
                self.progress_info.error_count += 1

            # Update timing
            current_time = time.time()
            self.progress_info.elapsed_time = current_time - self._start_time

            # Calculate estimated remaining time
            if self.progress_info.processed_files > 0:
                avg_time_per_file = (
                    self.progress_info.elapsed_time / self.progress_info.processed_files
                )
                remaining_files = (
                    self.progress_info.total_files - self.progress_info.processed_files
                )
                self.progress_info.estimated_remaining = (
                    avg_time_per_file * remaining_files
                )

            # Check if operation is complete
            if self.progress_info.processed_files >= self.progress_info.total_files:
                self.progress_info.state = ProgressState.COMPLETED
                self.progress_info.current_file = None

        self._notify_update()

    def pause(self):
        """Pause the deletion operation."""
        with self._lock:
            if self.progress_info.state == ProgressState.RUNNING:
                self.progress_info.state = ProgressState.PAUSED
                self._pause_event.clear()

        self._notify_update()
        logger.info("Deletion operation paused")

    def resume(self):
        """Resume the deletion operation."""
        with self._lock:
            if self.progress_info.state == ProgressState.PAUSED:
                self.progress_info.state = ProgressState.RUNNING
                self._pause_event.set()

        self._notify_update()
        logger.info("Deletion operation resumed")

    def cancel(self):
        """Cancel the deletion operation."""
        with self._lock:
            self.progress_info.state = ProgressState.CANCELLED
            self._cancel_event.set()
            self._pause_event.set()  # Unblock any waiting threads

        self._notify_update()
        logger.info("Deletion operation cancelled")

    def wait_if_paused(self):
        """Block if operation is paused, return True if should continue, False if cancelled."""
        self._pause_event.wait()
        return not self._cancel_event.is_set()

    def is_cancelled(self) -> bool:
        """Check if operation has been cancelled."""
        return self._cancel_event.is_set()

    def is_paused(self) -> bool:
        """Check if operation is paused."""
        return self.progress_info.state == ProgressState.PAUSED

    def is_running(self) -> bool:
        """Check if operation is running."""
        return self.progress_info.state == ProgressState.RUNNING

    def is_completed(self) -> bool:
        """Check if operation is completed."""
        return self.progress_info.state == ProgressState.COMPLETED

    def get_progress_info(self) -> ProgressInfo:
        """Get current progress information."""
        with self._lock:
            # Return a copy to avoid threading issues
            return ProgressInfo(
                total_files=self.progress_info.total_files,
                processed_files=self.progress_info.processed_files,
                current_file=self.progress_info.current_file,
                bytes_processed=self.progress_info.bytes_processed,
                total_bytes=self.progress_info.total_bytes,
                elapsed_time=self.progress_info.elapsed_time,
                estimated_remaining=self.progress_info.estimated_remaining,
                state=self.progress_info.state,
                success_count=self.progress_info.success_count,
                error_count=self.progress_info.error_count,
                skipped_count=self.progress_info.skipped_count,
            )

    def get_progress_percentage(self) -> float:
        """Get progress as percentage (0.0 to 100.0)."""
        with self._lock:
            if self.progress_info.total_files == 0:
                return 0.0
            return (
                self.progress_info.processed_files
                / self.progress_info.total_files
            ) * 100.0

    def get_summary(self) -> Dict[str, Any]:
        """Get operation summary."""
        info = self.get_progress_info()
        return {
            "total_files": info.total_files,
            "processed_files": info.processed_files,
            "success_count": info.success_count,
            "error_count": info.error_count,
            "skipped_count": info.skipped_count,
            "progress_percentage": self.get_progress_percentage(),
            "elapsed_time": info.elapsed_time,
            "estimated_remaining": info.estimated_remaining,
            "state": info.state.value,
            "bytes_processed": info.bytes_processed,
            "total_bytes": info.total_bytes,
        }

    def _notify_update(self):
        """Notify callback of progress update if enough time has passed."""
        current_time = time.time()

        # Throttle updates to avoid overwhelming the UI
        if current_time - self._last_update >= self._update_interval:
            self._last_update = current_time

            if self.update_callback:
                try:
                    self.update_callback(self.get_progress_info())
                except Exception as e:
                    logger.error(f"Progress callback error: {str(e)}")
