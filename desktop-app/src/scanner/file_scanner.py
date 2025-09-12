"""Core file system scanner with progressive discovery."""

import gc
import sys
import time
from collections import deque
from pathlib import Path
from typing import Callable, Iterator, List, Optional

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared"))

from models.file_info import FileInfo, ScanProgress

from shared.secure_logging.sanitizer import sanitize_path
from shared.secure_logging.secure_logger import get_logger

from .metadata_extractor import MetadataExtractor

logger = get_logger(__name__)


class FileScanner:
    """File system scanner with progressive display support."""

    def __init__(self, batch_size: int = 1000, progress_interval: float = 0.1):
        """Initialize scanner with performance settings."""
        self.batch_size = batch_size
        self.progress_interval = progress_interval
        self._cancelled = False
        self._scan_start_time = 0.0
        self._rate_samples = deque(maxlen=10)  # Rolling average for rate calculation

    def scan_directories(
        self,
        directories: List[Path],
        progress_callback: Optional[Callable[[ScanProgress], None]] = None,
        file_callback: Optional[Callable[[FileInfo], None]] = None,
    ) -> Iterator[FileInfo]:
        """
        Scan multiple directories progressively.

        Args:
            directories: List of directories to scan
            progress_callback: Called with progress updates
            file_callback: Called for each discovered file

        Yields:
            FileInfo objects as files are discovered
        """
        self._cancelled = False
        self._scan_start_time = time.time()

        # Initialize progress tracking
        progress = ScanProgress()

        try:
            # First pass: estimate total files for progress calculation
            logger.info("Estimating total files for progress tracking")
            total_files = self._estimate_total_files(directories)
            progress.total_files = total_files

            if progress_callback:
                progress_callback(progress)

            # Second pass: actual scanning with progress updates
            last_progress_time = time.time()

            for directory in directories:
                if self._cancelled:
                    break

                progress.current_directory = directory
                logger.info(f"Scanning directory: {sanitize_path(str(directory))}")

                for file_info in self._scan_directory_recursive(directory):
                    if self._cancelled:
                        break

                    progress.scanned_files += 1
                    progress.scanned_size += file_info.size

                    # Update scan rate
                    self._update_scan_rate(progress)

                    # Call file callback
                    if file_callback:
                        file_callback(file_info)

                    # Update progress at intervals
                    current_time = time.time()
                    if current_time - last_progress_time >= self.progress_interval:
                        if progress_callback:
                            progress_callback(progress)
                        last_progress_time = current_time

                    yield file_info

                    # Memory management for large scans
                    if progress.scanned_files % self.batch_size == 0:
                        gc.collect()

        except Exception as e:
            logger.error(f"Error during directory scan: {str(e)}")
            raise
        finally:
            # Final progress update
            if progress_callback:
                progress_callback(progress)

    def _scan_directory_recursive(self, directory: Path) -> Iterator[FileInfo]:
        """Recursively scan a directory for files."""
        try:
            for item in directory.iterdir():
                if self._cancelled:
                    break

                try:
                    if item.is_file():
                        # Extract metadata for regular files
                        file_info = MetadataExtractor.extract_metadata(item)
                        yield file_info

                    elif item.is_dir() and not item.is_symlink():
                        # Recursively scan subdirectories (skip symlinks to avoid loops)
                        yield from self._scan_directory_recursive(item)

                except (PermissionError, OSError):
                    # Log and skip inaccessible items
                    logger.warning(
                        f"Skipping inaccessible item: {sanitize_path(str(item))}"
                    )
                    continue

        except (PermissionError, OSError):
            logger.warning(f"Cannot access directory: {sanitize_path(str(directory))}")
            return

    def _estimate_total_files(self, directories: List[Path]) -> int:
        """Estimate total number of files for progress calculation."""
        total_estimate = 0

        for directory in directories:
            try:
                # Quick estimation by counting directory entries
                estimate = self._quick_count_files(directory)
                total_estimate += estimate
                logger.debug(
                    f"Estimated {estimate} files in {sanitize_path(str(directory))}"
                )

            except Exception as e:
                logger.warning(
                    f"Could not estimate files in {sanitize_path(str(directory))}: {str(e)}"
                )
                # Use conservative estimate
                total_estimate += 1000

        return max(total_estimate, 1)  # Ensure at least 1 for division

    def _quick_count_files(self, directory: Path, max_depth: int = 3) -> int:
        """Quick file count estimation with limited depth."""
        if max_depth <= 0:
            return 0

        count = 0
        try:
            for item in directory.iterdir():
                if self._cancelled:
                    break

                try:
                    if item.is_file():
                        count += 1
                    elif item.is_dir() and not item.is_symlink():
                        count += self._quick_count_files(item, max_depth - 1)

                except (PermissionError, OSError):
                    continue

        except (PermissionError, OSError):
            pass

        return count

    def _update_scan_rate(self, progress: ScanProgress) -> None:
        """Update scanning rate and estimated completion time."""
        current_time = time.time()
        elapsed_time = current_time - self._scan_start_time

        if elapsed_time > 0:
            current_rate = progress.scanned_files / elapsed_time
            self._rate_samples.append(current_rate)

            # Calculate rolling average rate
            if self._rate_samples:
                progress.scan_rate = sum(self._rate_samples) / len(self._rate_samples)

                # Estimate remaining time
                remaining_files = progress.total_files - progress.scanned_files
                if progress.scan_rate > 0 and remaining_files > 0:
                    progress.estimated_remaining = remaining_files / progress.scan_rate

    def cancel(self) -> None:
        """Cancel the current scan operation."""
        self._cancelled = True
        logger.info("File scan cancellation requested")

    @property
    def is_cancelled(self) -> bool:
        """Check if scan has been cancelled."""
        return self._cancelled

    def get_performance_stats(self) -> dict:
        """Get current performance statistics."""
        return {
            "batch_size": self.batch_size,
            "progress_interval": self.progress_interval,
            "rate_samples": len(self._rate_samples),
            "is_cancelled": self._cancelled,
        }
