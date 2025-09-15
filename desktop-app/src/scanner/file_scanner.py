"""Optimized file system scanner with high-performance scanning."""

import gc
import os
import sys
import time
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Iterator, List, Optional, Set

# Add shared modules to path
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from models.file_info import FileInfo, ScanProgress
from secure_logging.sanitizer import sanitize_path
from secure_logging.secure_logger import get_logger

try:
    from .metadata_extractor import MetadataExtractor
except ImportError:
    from metadata_extractor import MetadataExtractor

logger = get_logger(__name__)


class OptimizedFileScanner:
    """High-performance file system scanner with multi-threading and optimizations."""

    def __init__(self, batch_size: int = 5000, progress_interval: float = 0.05, max_workers: int = 4):
        """Initialize scanner with performance settings."""
        self.batch_size = batch_size
        self.progress_interval = progress_interval
        self.max_workers = max_workers
        self._cancelled = False
        self._scan_start_time = 0.0
        self._rate_samples = deque(maxlen=20)  # More samples for better averaging
        self._processed_dirs = set()  # Cache to avoid duplicate processing
        self._file_cache = {}  # Cache for file metadata

    def scan_directories(
        self,
        directories: List[Path],
        progress_callback: Optional[Callable[[ScanProgress], None]] = None,
        file_callback: Optional[Callable[[FileInfo], None]] = None,
    ) -> Iterator[FileInfo]:
        """
        Accurate file scanning with proper progress tracking.

        Args:
            directories: List of directories to scan
            progress_callback: Called with progress updates
            file_callback: Called for each discovered file

        Yields:
            FileInfo objects as files are discovered
        """
        self._cancelled = False
        self._scan_start_time = time.time()
        self._processed_dirs.clear()
        self._file_cache.clear()

        # Initialize progress tracking
        progress = ScanProgress()
        all_files = []  # Collect all files first for accurate counting

        try:
            # Step 1: Scan all directories and collect files with real-time progress
            logger.info("Scanning directories for files...")
            
            for dir_index, directory in enumerate(directories):
                if self._cancelled:
                    break
                    
                progress.current_directory = directory
                logger.info(f"Scanning directory: {sanitize_path(str(directory))}")
                
                # Update progress to show which directory we're scanning
                if progress_callback:
                    progress_callback(progress)
                
                directory_files = self._scan_directory_accurate_with_progress(
                    directory, progress, progress_callback
                )
                all_files.extend(directory_files)
                
                # Update progress after each directory
                progress.total_files = len(all_files)
                progress.scanned_files = len(all_files)  # Show files found so far
                if progress_callback:
                    progress_callback(progress)

            # Step 2: Process files with accurate progress tracking
            logger.info(f"Processing {len(all_files)} files found...")
            progress.total_files = len(all_files)
            progress.scanned_files = 0
            
            last_progress_time = time.time()
            
            for i, file_info in enumerate(all_files):
                if self._cancelled:
                    break

                # Update progress counters
                progress.scanned_files = i + 1
                progress.scanned_size += file_info.size
                progress.current_directory = file_info.path.parent

                # Update scan rate
                self._update_scan_rate(progress)

                # Call callbacks
                if file_callback:
                    file_callback(file_info)

                # Update progress at intervals
                current_time = time.time()
                if current_time - last_progress_time >= self.progress_interval:
                    if progress_callback:
                        progress_callback(progress)
                    last_progress_time = current_time

                yield file_info

        except Exception as e:
            logger.error(f"Error during directory scan: {str(e)}")
            raise
        finally:
            # Final progress update
            progress.scanned_files = len(all_files)
            if progress_callback:
                progress_callback(progress)

    def _scan_directory_accurate(self, directory: Path) -> List[FileInfo]:
        """Accurate directory scanning with proper file counting."""
        files_found = []
        
        try:
            # Use os.walk for directory traversal
            for root, dirs, files in os.walk(str(directory)):
                if self._cancelled:
                    break
                
                # Skip system directories but be less aggressive to avoid missing files
                dirs[:] = [d for d in dirs if not d.startswith('.') and 
                          d.lower() not in {'system volume information', '$recycle.bin'}]
                
                root_path = Path(root)
                
                # Process files in current directory
                for filename in files:
                    if self._cancelled:
                        break
                    
                    try:
                        file_path = root_path / filename
                        
                        # Skip only truly hidden files, not temp files that might need deletion
                        if filename.startswith('.'):
                            continue
                        
                        # Use proper metadata extraction for accuracy
                        file_info = self._extract_file_info_accurate(file_path)
                        if file_info:
                            files_found.append(file_info)
                            
                    except (PermissionError, OSError, FileNotFoundError):
                        # Skip inaccessible files but log for debugging
                        logger.debug(f"Skipping inaccessible file: {sanitize_path(str(file_path))}")
                        continue
                        
        except (PermissionError, OSError) as e:
            logger.warning(f"Cannot access directory: {sanitize_path(str(directory))}")
        
        return files_found
    
    def _scan_directory_accurate_with_progress(
        self, 
        directory: Path, 
        progress: ScanProgress, 
        progress_callback: Optional[Callable[[ScanProgress], None]] = None
    ) -> List[FileInfo]:
        """Accurate directory scanning with real-time progress updates."""
        files_found = []
        last_progress_time = time.time()
        
        try:
            # Use os.walk for directory traversal
            for root, dirs, files in os.walk(str(directory)):
                if self._cancelled:
                    break
                
                # Skip system directories but be less aggressive to avoid missing files
                dirs[:] = [d for d in dirs if not d.startswith('.') and 
                          d.lower() not in {'system volume information', '$recycle.bin'}]
                
                root_path = Path(root)
                progress.current_directory = root_path
                
                # Process files in current directory
                for filename in files:
                    if self._cancelled:
                        break
                    
                    try:
                        file_path = root_path / filename
                        
                        # Skip only truly hidden files, not temp files that might need deletion
                        if filename.startswith('.'):
                            continue
                        
                        # Use proper metadata extraction for accuracy
                        file_info = self._extract_file_info_accurate(file_path)
                        if file_info:
                            files_found.append(file_info)
                            
                            # Update progress every 100 files or every 0.1 seconds
                            current_time = time.time()
                            if (len(files_found) % 100 == 0 or 
                                current_time - last_progress_time >= 0.1):
                                
                                progress.scanned_files = len(files_found)
                                progress.total_files = len(files_found)  # Running count
                                
                                if progress_callback:
                                    progress_callback(progress)
                                last_progress_time = current_time
                                
                    except (PermissionError, OSError, FileNotFoundError):
                        # Skip inaccessible files but log for debugging
                        logger.debug(f"Skipping inaccessible file: {sanitize_path(str(file_path))}")
                        continue
                        
        except (PermissionError, OSError) as e:
            logger.warning(f"Cannot access directory: {sanitize_path(str(directory))}")
        
        return files_found
    
    def _extract_file_info_accurate(self, file_path: Path) -> Optional[FileInfo]:
        """Accurate file info extraction."""
        try:
            # Get basic file stats
            stat_result = file_path.stat()
            
            # Create FileInfo with proper metadata
            file_info = FileInfo(
                path=file_path,
                size=stat_result.st_size,
                modified_time=stat_result.st_mtime,
                created_time=getattr(stat_result, 'st_birthtime', stat_result.st_ctime),
                is_hidden=file_path.name.startswith('.'),
                extension=file_path.suffix.lower()
            )
            
            return file_info
            
        except (PermissionError, OSError, FileNotFoundError):
            return None

    def _fast_estimate_files(self, directories: List[Path]) -> int:
        """Conservative file count estimation."""
        total_estimate = 0

        for directory in directories:
            try:
                # Use conservative estimation to avoid over-counting
                estimate = self._count_files_fast(directory)
                total_estimate += estimate
                logger.debug(
                    f"Estimated {estimate} files in {sanitize_path(str(directory))}"
                )

            except Exception as e:
                logger.warning(
                    f"Could not estimate files in {sanitize_path(str(directory))}: {str(e)}"
                )
                # Use very conservative estimate
                total_estimate += 100

        return max(total_estimate, 1)

    def _count_files_fast(self, directory: Path, max_dirs: int = 200) -> int:
        """Conservative file counting with early termination."""
        count = 0
        dir_count = 0
        
        try:
            for root, dirs, files in os.walk(str(directory)):
                if self._cancelled or dir_count > max_dirs:
                    # Don't extrapolate - just return what we counted to avoid over-estimation
                    break
                
                # Skip system directories for faster estimation
                dirs[:] = [d for d in dirs if not d.startswith('.') and 
                          d.lower() not in {'system volume information', '$recycle.bin'}]
                
                # Count files in current directory (same logic as actual scan)
                file_count = len([f for f in files if not f.startswith('.')])
                count += file_count
                dir_count += 1

        except (PermissionError, OSError):
            # If we can't access, return a small conservative estimate
            return 50

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


# Compatibility alias for existing code
FileScanner = OptimizedFileScanner
