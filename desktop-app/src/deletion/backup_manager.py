"""
Backup manager for creating backups of important files before deletion.
Provides progress tracking and validation for backup operations.
"""

import os
import shutil
import threading
from pathlib import Path
from typing import List, Dict, Optional, Callable
import time
from datetime import datetime

from shared.secure_logging.secure_logger import get_logger
from shared.utils.exceptions import SecureWipeError

logger = get_logger(__name__)


class BackupResult:
    """Result of backup operation."""
    
    def __init__(self):
        self.success = False
        self.total_files = 0
        self.backed_up_files = 0
        self.failed_files = 0
        self.total_size = 0
        self.backed_up_size = 0
        self.backup_location = None
        self.errors = []
        self.start_time = None
        self.end_time = None
        
    @property
    def duration(self) -> float:
        """Get backup duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
        
    @property
    def success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.backed_up_files / self.total_files) * 100


class BackupProgress:
    """Progress tracking for backup operations."""
    
    def __init__(self):
        self.current_file = ""
        self.files_completed = 0
        self.total_files = 0
        self.bytes_completed = 0
        self.total_bytes = 0
        self.current_file_progress = 0.0
        self.overall_progress = 0.0
        self.is_cancelled = False
        self.errors = []
        
    def update_file_progress(self, file_path: str, progress: float):
        """Update progress for current file."""
        self.current_file = file_path
        self.current_file_progress = progress
        self._calculate_overall_progress()
        
    def complete_file(self, file_path: str, size: int, success: bool = True):
        """Mark file as completed."""
        self.files_completed += 1
        if success:
            self.bytes_completed += size
        self._calculate_overall_progress()
        
    def add_error(self, file_path: str, error: str):
        """Add error for file."""
        self.errors.append({"file": file_path, "error": error})
        
    def _calculate_overall_progress(self):
        """Calculate overall progress percentage."""
        if self.total_files == 0:
            self.overall_progress = 0.0
        else:
            file_progress = self.files_completed / self.total_files
            current_file_contribution = (self.current_file_progress / self.total_files) if self.total_files > 0 else 0
            self.overall_progress = min(100.0, (file_progress + current_file_contribution) * 100)


class BackupManager:
    """Manager for backup operations with progress tracking."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._cancel_event = threading.Event()
        
    def create_backup(self, files: List[Path], backup_location: Path, 
                     progress_callback: Optional[Callable[[BackupProgress], None]] = None) -> BackupResult:
        """
        Create backup of specified files to backup location.
        
        Args:
            files: List of files to backup
            backup_location: Directory to create backup in
            progress_callback: Optional callback for progress updates
            
        Returns:
            BackupResult with operation details
        """
        result = BackupResult()
        result.start_time = datetime.now()
        result.total_files = len(files)
        result.backup_location = backup_location
        
        # Calculate total size
        for file_path in files:
            try:
                if file_path.exists() and file_path.is_file():
                    result.total_size += file_path.stat().st_size
            except Exception as e:
                self.logger.warning(f"Could not get size for {file_path}: {e}")
                
        progress = BackupProgress()
        progress.total_files = len(files)
        progress.total_bytes = result.total_size
        
        try:
            # Create backup directory structure
            backup_root = backup_location / f"SecureWipe_Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_root.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Starting backup of {len(files)} files to {backup_root}")
            
            # Backup each file
            for i, file_path in enumerate(files):
                if self._cancel_event.is_set():
                    self.logger.info("Backup cancelled by user")
                    break
                    
                try:
                    self._backup_single_file(file_path, backup_root, progress, progress_callback)
                    result.backed_up_files += 1
                    result.backed_up_size += file_path.stat().st_size if file_path.exists() else 0
                    
                except Exception as e:
                    error_msg = f"Failed to backup {file_path}: {e}"
                    self.logger.error(error_msg)
                    result.errors.append(error_msg)
                    result.failed_files += 1
                    progress.add_error(str(file_path), str(e))
                    
                # Update progress
                progress.complete_file(str(file_path), 
                                     file_path.stat().st_size if file_path.exists() else 0,
                                     success=(result.failed_files == 0))
                
                if progress_callback:
                    progress_callback(progress)
                    
            # Create backup manifest
            self._create_backup_manifest(backup_root, files, result)
            
            result.success = result.failed_files == 0 and not self._cancel_event.is_set()
            
        except Exception as e:
            error_msg = f"Backup operation failed: {e}"
            self.logger.error(error_msg)
            result.errors.append(error_msg)
            result.success = False
            
        finally:
            result.end_time = datetime.now()
            self._cancel_event.clear()
            
        self.logger.info(f"Backup completed: {result.backed_up_files}/{result.total_files} files, "
                        f"{result.backed_up_size} bytes in {result.duration:.1f}s")
        
        return result
        
    def _backup_single_file(self, source_path: Path, backup_root: Path, 
                           progress: BackupProgress, 
                           progress_callback: Optional[Callable[[BackupProgress], None]]):
        """Backup a single file with progress tracking."""
        if not source_path.exists():
            raise FileNotFoundError(f"Source file does not exist: {source_path}")
            
        # Create relative path structure in backup
        try:
            # Try to make path relative to user home for cleaner backup structure
            relative_path = source_path.relative_to(Path.home())
        except ValueError:
            # If not under home, use absolute path structure
            relative_path = Path(*source_path.parts[1:])  # Remove drive letter on Windows
            
        backup_file_path = backup_root / relative_path
        backup_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file with progress tracking for large files
        file_size = source_path.stat().st_size
        
        if file_size > 10 * 1024 * 1024:  # 10MB threshold for progress tracking
            self._copy_file_with_progress(source_path, backup_file_path, progress, progress_callback)
        else:
            # Small files - copy directly
            shutil.copy2(source_path, backup_file_path)
            progress.update_file_progress(str(source_path), 100.0)
            if progress_callback:
                progress_callback(progress)
                
    def _copy_file_with_progress(self, source: Path, destination: Path, 
                                progress: BackupProgress,
                                progress_callback: Optional[Callable[[BackupProgress], None]]):
        """Copy large file with progress updates."""
        buffer_size = 64 * 1024  # 64KB buffer
        total_size = source.stat().st_size
        copied_size = 0
        
        with open(source, 'rb') as src, open(destination, 'wb') as dst:
            while True:
                if self._cancel_event.is_set():
                    break
                    
                buffer = src.read(buffer_size)
                if not buffer:
                    break
                    
                dst.write(buffer)
                copied_size += len(buffer)
                
                # Update progress
                file_progress = (copied_size / total_size) * 100 if total_size > 0 else 100
                progress.update_file_progress(str(source), file_progress)
                
                if progress_callback:
                    progress_callback(progress)
                    
        # Copy metadata
        shutil.copystat(source, destination)
        
    def _create_backup_manifest(self, backup_root: Path, original_files: List[Path], 
                               result: BackupResult):
        """Create manifest file with backup information."""
        manifest_path = backup_root / "backup_manifest.txt"
        
        try:
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(f"SecureWipe Backup Manifest\n")
                f.write(f"Created: {result.start_time.isoformat()}\n")
                f.write(f"Total Files: {result.total_files}\n")
                f.write(f"Backed Up Files: {result.backed_up_files}\n")
                f.write(f"Failed Files: {result.failed_files}\n")
                f.write(f"Total Size: {result.total_size} bytes\n")
                f.write(f"Backed Up Size: {result.backed_up_size} bytes\n")
                f.write(f"Success Rate: {result.success_rate:.1f}%\n")
                f.write(f"\n--- Original File Paths ---\n")
                
                for file_path in original_files:
                    f.write(f"{file_path}\n")
                    
                if result.errors:
                    f.write(f"\n--- Errors ---\n")
                    for error in result.errors:
                        f.write(f"{error}\n")
                        
        except Exception as e:
            self.logger.error(f"Failed to create backup manifest: {e}")
            
    def cancel_backup(self):
        """Cancel ongoing backup operation."""
        self._cancel_event.set()
        self.logger.info("Backup cancellation requested")
        
    def validate_backup_location(self, location: Path) -> Dict[str, any]:
        """
        Validate backup location and return status information.
        
        Returns:
            Dict with validation results
        """
        validation = {
            'valid': False,
            'exists': False,
            'writable': False,
            'free_space': 0,
            'errors': []
        }
        
        try:
            # Check if location exists
            validation['exists'] = location.exists()
            
            if not validation['exists']:
                # Try to create directory
                try:
                    location.mkdir(parents=True, exist_ok=True)
                    validation['exists'] = True
                except Exception as e:
                    validation['errors'].append(f"Cannot create directory: {e}")
                    return validation
                    
            # Check if writable
            test_file = location / ".securewipe_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
                validation['writable'] = True
            except Exception as e:
                validation['errors'].append(f"Location not writable: {e}")
                return validation
                
            # Check free space
            try:
                stat = shutil.disk_usage(location)
                validation['free_space'] = stat.free
            except Exception as e:
                validation['errors'].append(f"Cannot determine free space: {e}")
                
            validation['valid'] = validation['exists'] and validation['writable']
            
        except Exception as e:
            validation['errors'].append(f"Validation error: {e}")
            
        return validation
        
    def estimate_backup_time(self, files: List[Path]) -> Dict[str, any]:
        """
        Estimate backup time and space requirements.
        
        Returns:
            Dict with estimates
        """
        estimate = {
            'total_files': len(files),
            'total_size': 0,
            'estimated_time_seconds': 0,
            'readable_files': 0,
            'unreadable_files': 0,
            'errors': []
        }
        
        # Calculate total size and check readability
        for file_path in files:
            try:
                if file_path.exists() and file_path.is_file():
                    size = file_path.stat().st_size
                    estimate['total_size'] += size
                    estimate['readable_files'] += 1
                else:
                    estimate['unreadable_files'] += 1
                    estimate['errors'].append(f"File not accessible: {file_path}")
            except Exception as e:
                estimate['unreadable_files'] += 1
                estimate['errors'].append(f"Error accessing {file_path}: {e}")
                
        # Estimate time (rough calculation: 50MB/s for local disk)
        if estimate['total_size'] > 0:
            estimated_throughput = 50 * 1024 * 1024  # 50 MB/s
            estimate['estimated_time_seconds'] = estimate['total_size'] / estimated_throughput
            
        return estimate