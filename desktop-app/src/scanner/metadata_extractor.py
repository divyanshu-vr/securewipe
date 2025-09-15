"""File metadata extraction utilities."""

import sys
from datetime import datetime
from pathlib import Path

# Add shared modules to path
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from models.file_info import FileInfo, FileType
from secure_logging.sanitizer import sanitize_path
from secure_logging.secure_logger import get_logger

logger = get_logger(__name__)


class MetadataExtractor:
    """Extract metadata from files safely."""

    # File type mappings
    FILE_TYPE_MAP = {
        # Documents
        ".pdf": FileType.DOCUMENT,
        ".doc": FileType.DOCUMENT,
        ".docx": FileType.DOCUMENT,
        ".txt": FileType.DOCUMENT,
        ".rtf": FileType.DOCUMENT,
        ".odt": FileType.DOCUMENT,
        ".xls": FileType.DOCUMENT,
        ".xlsx": FileType.DOCUMENT,
        ".ppt": FileType.DOCUMENT,
        ".pptx": FileType.DOCUMENT,
        # Images
        ".jpg": FileType.IMAGE,
        ".jpeg": FileType.IMAGE,
        ".png": FileType.IMAGE,
        ".gif": FileType.IMAGE,
        ".bmp": FileType.IMAGE,
        ".tiff": FileType.IMAGE,
        ".svg": FileType.IMAGE,
        ".webp": FileType.IMAGE,
        # Videos
        ".mp4": FileType.VIDEO,
        ".avi": FileType.VIDEO,
        ".mkv": FileType.VIDEO,
        ".mov": FileType.VIDEO,
        ".wmv": FileType.VIDEO,
        ".flv": FileType.VIDEO,
        ".webm": FileType.VIDEO,
        # Audio
        ".mp3": FileType.AUDIO,
        ".wav": FileType.AUDIO,
        ".flac": FileType.AUDIO,
        ".aac": FileType.AUDIO,
        ".ogg": FileType.AUDIO,
        ".wma": FileType.AUDIO,
        # Archives
        ".zip": FileType.ARCHIVE,
        ".rar": FileType.ARCHIVE,
        ".7z": FileType.ARCHIVE,
        ".tar": FileType.ARCHIVE,
        ".gz": FileType.ARCHIVE,
        ".bz2": FileType.ARCHIVE,
        # Executables
        ".exe": FileType.EXECUTABLE,
        ".msi": FileType.EXECUTABLE,
        ".deb": FileType.EXECUTABLE,
        ".rpm": FileType.EXECUTABLE,
        ".dmg": FileType.EXECUTABLE,
        ".app": FileType.EXECUTABLE,
    }

    @classmethod
    def extract_metadata(cls, file_path: Path) -> FileInfo:
        """Extract metadata from a file safely."""
        try:
            # Get basic file stats
            stat = file_path.stat()
            size = stat.st_size
            modified_date = datetime.fromtimestamp(stat.st_mtime)

            # Determine file type
            file_type = cls._get_file_type(file_path)

            return FileInfo(
                path=file_path,
                size=size,
                modified_date=modified_date,
                file_type=file_type,
                is_accessible=True,
            )

        except PermissionError:
            logger.warning(f"Permission denied: {sanitize_path(str(file_path))}")
            return FileInfo(
                path=file_path,
                size=0,
                modified_date=datetime.now(),
                file_type=FileType.OTHER,
                is_accessible=False,
                error_message="Permission denied",
            )

        except FileNotFoundError:
            logger.warning(f"File not found: {sanitize_path(str(file_path))}")
            return FileInfo(
                path=file_path,
                size=0,
                modified_date=datetime.now(),
                file_type=FileType.OTHER,
                is_accessible=False,
                error_message="File not found",
            )

        except OSError as e:
            logger.warning(f"OS error accessing file: {sanitize_path(str(file_path))}")
            return FileInfo(
                path=file_path,
                size=0,
                modified_date=datetime.now(),
                file_type=FileType.OTHER,
                is_accessible=False,
                error_message=f"OS error: {str(e)}",
            )

    @classmethod
    def _get_file_type(cls, file_path: Path) -> FileType:
        """Determine file type from extension."""
        extension = file_path.suffix.lower()
        return cls.FILE_TYPE_MAP.get(extension, FileType.OTHER)

    @classmethod
    def is_accessible(cls, file_path: Path) -> bool:
        """Check if file is accessible without full metadata extraction."""
        try:
            file_path.stat()
            return True
        except (PermissionError, FileNotFoundError, OSError):
            return False
