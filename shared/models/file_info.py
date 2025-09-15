"""File metadata models for SecureWipe scanner."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class FileType(Enum):
    """File type categories."""

    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    EXECUTABLE = "executable"
    OTHER = "other"


@dataclass
class FileInfo:
    """File metadata structure with all required fields."""

    path: Path
    size: int
    modified_time: float = 0.0
    created_time: float = 0.0
    is_hidden: bool = False
    extension: str = ""
    file_type: Optional[FileType] = None
    is_accessible: bool = True
    
    # Legacy compatibility
    @property
    def modified_date(self) -> datetime:
        """Convert modified_time to datetime for compatibility."""
        return datetime.fromtimestamp(self.modified_time)


@dataclass
class ScanProgress:
    """Progress tracking for file scanning operations."""
    
    total_files: int = 0
    scanned_files: int = 0
    scanned_size: int = 0
    current_directory: Optional[Path] = None
    scan_rate: float = 0.0
    estimated_remaining: float = 0.0
    error_message: Optional[str] = None
    category: Optional[str] = None
    category_reason: Optional[str] = None
    category_explanation: Optional[str] = None

    @property
    def name(self) -> str:
        """Get file name."""
        return self.path.name

    @property
    def extension(self) -> str:
        """Get file extension."""
        return self.path.suffix.lower()

    def __str__(self) -> str:
        return f"{self.name} ({self.size} bytes)"


@dataclass
class DirectoryStats:
    """Directory scanning statistics."""

    path: Path
    file_count: int = 0
    total_size: int = 0
    scanned_count: int = 0
    error_count: int = 0

    @property
    def progress_percent(self) -> float:
        """Calculate scan progress percentage."""
        if self.file_count == 0:
            return 0.0
        return min(100.0, (self.scanned_count / self.file_count) * 100.0)


@dataclass
class ScanProgress:
    """Overall scan progress tracking."""

    total_files: int = 0
    scanned_files: int = 0
    total_size: int = 0
    scanned_size: int = 0
    current_directory: Optional[Path] = None
    scan_rate: float = 0.0  # files per second
    estimated_remaining: Optional[float] = None  # seconds

    @property
    def progress_percent(self) -> float:
        """Calculate overall progress percentage."""
        if self.total_files == 0:
            return 0.0
        return min(100.0, (self.scanned_files / self.total_files) * 100.0)
