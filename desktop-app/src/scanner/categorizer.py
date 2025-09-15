"""Rule-based file categorization engine."""

import json
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

# Add shared modules to path
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from models.file_info import FileInfo
from secure_logging.sanitizer import sanitize_path
from secure_logging.secure_logger import get_logger

logger = get_logger(__name__)


class CategoryType(Enum):
    """File safety categories."""

    SAFE = "safe"
    LESS_IMPORTANT = "lessImportant"
    IMPORTANT = "important"


class CategoryReason(Enum):
    """Reasons for categorization decisions."""

    EXTENSION = "extension"
    PATH_PATTERN = "pathPattern"
    SYSTEM_FILE = "systemFile"
    TEMP_FILE = "tempFile"
    USER_DOCUMENT = "userDocument"
    ACCESS_TIME = "accessTime"
    USER_OVERRIDE = "userOverride"


class CategoryResult:
    """Result of file categorization."""

    def __init__(
        self, category: CategoryType, reason: CategoryReason, explanation: str
    ):
        self.category = category
        self.reason = reason
        self.explanation = explanation
        self.confidence = 1.0
        self.override_allowed = True


class FileCategorizer:
    """Rule-based file categorization system."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize categorizer with rules configuration."""
        self._rules = {}
        self._user_overrides = {}
        self._load_rules(config_path)

    def _load_rules(self, config_path: Optional[Path] = None) -> None:
        """Load categorization rules from configuration."""
        if config_path is None:
            config_path = (
                Path(__file__).parent.parent / "config" / "categorization_rules.json"
            )

        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    self._rules = json.load(f)
                logger.info(
                    f"Loaded categorization rules from "
                    f"{sanitize_path(str(config_path))}"
                )
            else:
                self._rules = self._get_default_rules()
                logger.info("Using default categorization rules")
        except Exception as e:
            logger.error(f"Error loading rules: {str(e)}")
            self._rules = self._get_default_rules()

    def _get_default_rules(self) -> Dict:
        """Get default categorization rules."""
        return {
            "schemaVersion": "1.0.0",
            "categories": {
                "safe": {
                    "extensions": [
                        ".tmp",
                        ".cache",
                        ".log",
                        ".bak",
                        ".old",
                        ".~",
                        ".swp",
                    ],
                    "pathPatterns": [
                        "temp",
                        "cache",
                        "logs",
                        "downloads",
                        "recycle",
                        "trash",
                    ],
                    "description": "Files safe to delete without data loss",
                },
                "lessImportant": {
                    "extensions": [
                        ".doc",
                        ".docx",
                        ".pdf",
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".mp4",
                        ".mp3",
                        ".txt",
                    ],
                    "pathPatterns": [
                        "documents",
                        "pictures",
                        "videos",
                        "music",
                        "desktop",
                    ],
                    "description": "User files that may have value but are not critical",
                },
                "important": {
                    "extensions": [".exe", ".dll", ".sys", ".ini", ".cfg", ".config"],
                    "pathPatterns": [
                        "windows",
                        "program files",
                        "system32",
                        "usr",
                        "etc",
                        "bin",
                    ],
                    "description": "System files and applications - deletion may cause issues",
                },
            },
            "accessTimeRules": {
                "oldFileThresholdDays": 365,
                "recentFileThresholdDays": 30,
            },
        }

    def categorize_file(self, file_info: FileInfo) -> CategoryResult:
        """Categorize a single file based on rules."""
        try:
            # Check for user override first
            if str(file_info.path) in self._user_overrides:
                override = self._user_overrides[str(file_info.path)]
                return CategoryResult(
                    CategoryType(override["category"]),
                    CategoryReason.USER_OVERRIDE,
                    override["explanation"],
                )

            # Check system file patterns (highest priority)
            if self._is_system_file(file_info.path):
                explanation = self._get_system_file_explanation(file_info.path)
                return CategoryResult(
                    CategoryType.IMPORTANT, CategoryReason.SYSTEM_FILE, explanation
                )

            # Check temporary file patterns
            if self._is_temp_file(file_info.path):
                explanation = self._get_temp_file_explanation(file_info.path)
                return CategoryResult(
                    CategoryType.SAFE, CategoryReason.TEMP_FILE, explanation
                )

            # Check extension-based rules
            extension_result = self._categorize_by_extension(file_info)
            if extension_result:
                return extension_result

            # Check path-based rules
            path_result = self._categorize_by_path(file_info.path)
            if path_result:
                return path_result

            # Default to less important for user files
            return CategoryResult(
                CategoryType.LESS_IMPORTANT,
                CategoryReason.USER_DOCUMENT,
                "User file - review before deletion",
            )

        except Exception as e:
            logger.error(
                f"Error categorizing file "
                f"{sanitize_path(str(file_info.path))}: {str(e)}"
            )
            return CategoryResult(
                CategoryType.IMPORTANT,
                CategoryReason.SYSTEM_FILE,
                "Could not categorize - marked as important for safety",
            )

    def _is_system_file(self, path: Path) -> bool:
        """Check if file is in system directories with comprehensive detection."""
        path_str = str(path).lower()

        # Critical Windows system paths (exact matches)
        windows_critical = [
            "c:\\windows\\system32",
            "c:\\windows\\syswow64",
            "c:\\windows\\winsxs",
            "c:\\windows\\boot",
            "c:\\windows\\drivers",
            "c:\\windows\\inf",
        ]

        # Linux system paths (exact matches)
        linux_critical = [
            "/boot",
            "/etc",
            "/bin",
            "/sbin",
            "/lib",
            "/lib64",
            "/usr/bin",
            "/usr/sbin",
            "/usr/lib",
            "/sys",
            "/proc",
            "/dev",
        ]

        # Check critical system paths first
        for critical_path in windows_critical + linux_critical:
            if critical_path in path_str:
                return True

        # Check for Windows system directory patterns (broader match)
        if "c:\\windows\\" in path_str and not any(
            temp in path_str for temp in ["temp", "cache"]
        ):
            return True

        # Check Program Files for all files (not just executables)
        if "c:\\program files" in path_str or "c:\\program files (x86)" in path_str:
            return True

        # Check for system file extensions in any location
        system_extensions = [".sys", ".dll", ".drv", ".ocx", ".cpl"]
        if path.suffix.lower() in system_extensions:
            return True

        return False

    def _get_system_file_explanation(self, path: Path) -> str:
        """Get detailed explanation for system file categorization."""
        path_str = str(path).lower()

        if "system32" in path_str or "syswow64" in path_str:
            return "Windows system file - critical for OS operation, deletion will cause system failure"
        elif "c:\\windows\\" in path_str:
            return "Windows system file - essential for OS operation, deletion may cause system instability"
        elif "program files" in path_str:
            return "Application file in protected system directory - deletion may break installed programs"
        elif (
            "/etc" in path_str
            or "/bin" in path_str
            or "/sbin" in path_str
            or "/usr" in path_str
        ):
            return "Linux system file - essential for system operation, deletion will cause instability"
        elif path.suffix.lower() in [".sys", ".dll"]:
            return f"System library file ({path.suffix}) - required by applications and OS components"
        else:
            return "System file or critical directory - deletion may cause system instability"

    def _is_temp_file(self, path: Path) -> bool:
        """Check if file is in temporary directories with comprehensive detection."""
        path_str = str(path).lower()

        # Windows temporary locations
        windows_temp = [
            "\\temp\\",
            "\\tmp\\",
            "\\cache\\",
            "\\logs\\",
            "appdata\\local\\temp",
            "appdata\\roaming\\temp",
            "\\temporary internet files",
            "\\webcache",
            "\\microsoft\\windows\\temporary internet files",
            "\\google\\chrome\\user data\\default\\cache",
            "\\mozilla\\firefox\\profiles\\cache",
        ]

        # Linux temporary locations
        linux_temp = [
            "/tmp/",
            "/var/tmp/",
            "/var/cache/",
            "/var/log/",
            "/.cache/",
            "/.mozilla/firefox/",
            "/.config/google-chrome/",
        ]

        # Check all temporary patterns
        for pattern in windows_temp + linux_temp:
            if pattern in path_str:
                return True

        # Check for temporary file extensions
        temp_extensions = [".tmp", ".temp", ".cache", ".log", ".bak", ".old", ".~"]
        if path.suffix.lower() in temp_extensions:
            return True

        # Check for browser cache patterns
        if any(
            browser in path_str for browser in ["chrome", "firefox", "edge", "safari"]
        ):
            if any(cache_dir in path_str for cache_dir in ["cache", "temp", "cookies"]):
                return True

        return False

    def _get_temp_file_explanation(self, path: Path) -> str:
        """Get detailed explanation for temporary file categorization."""
        path_str = str(path).lower()

        if "cache" in path_str:
            if any(browser in path_str for browser in ["chrome", "firefox", "edge"]):
                return "Browser cache file - safe to delete, will free up disk space"
            else:
                return (
                    "Application cache file - safe to delete, may improve performance"
                )
        elif "temp" in path_str or path.suffix.lower() in [".tmp", ".temp"]:
            return "Temporary file - safe to delete, created for short-term use"
        elif "log" in path_str or path.suffix.lower() == ".log":
            return "Log file - safe to delete, contains historical application data"
        elif path.suffix.lower() in [".bak", ".old"]:
            return "Backup file - safe to delete, contains outdated data"
        else:
            return "Temporary file that can be safely deleted without data loss"

    def _categorize_by_extension(self, file_info: FileInfo) -> Optional[CategoryResult]:
        """Categorize file by extension."""
        extension = file_info.extension

        for category_name, rules in self._rules["categories"].items():
            if extension in rules["extensions"]:
                return CategoryResult(
                    CategoryType(category_name),
                    CategoryReason.EXTENSION,
                    f"{extension} files are {rules['description']}",
                )

        return None

    def _categorize_by_path(self, path: Path) -> Optional[CategoryResult]:
        """Categorize file by path patterns."""
        path_str = str(path).lower()

        for category_name, rules in self._rules["categories"].items():
            for pattern in rules["pathPatterns"]:
                if pattern.lower() in path_str:
                    return CategoryResult(
                        CategoryType(category_name),
                        CategoryReason.PATH_PATTERN,
                        f"Files in {pattern} folders are {rules['description']}",
                    )

        return None

    def _categorize_by_access_time(
        self, file_info: FileInfo
    ) -> Optional[CategoryResult]:
        """Categorize file based on last access/modification time."""
        try:
            access_rules = self._rules.get("accessTimeRules", {})
            old_threshold = access_rules.get("oldFileThresholdDays", 365)
            recent_threshold = access_rules.get("recentFileThresholdDays", 30)

            # Calculate days since modification
            days_old = (datetime.now() - file_info.modified_date).days

            # Only apply access time rules to user documents
            if self._is_user_document(file_info.path):
                if days_old > old_threshold:
                    return CategoryResult(
                        CategoryType.SAFE,
                        CategoryReason.ACCESS_TIME,
                        f"Old user file (not accessed for {days_old} days) - likely safe to delete",
                    )
                elif days_old < recent_threshold:
                    return CategoryResult(
                        CategoryType.LESS_IMPORTANT,
                        CategoryReason.ACCESS_TIME,
                        f"Recently used file ({days_old} days ago) - review before deletion",
                    )

            return None

        except Exception as e:
            logger.error(f"Error in access time categorization: {str(e)}")
            return None

    def _is_user_document(self, path: Path) -> bool:
        """Check if file is in user document directories."""
        path_str = str(path).lower()

        user_dirs = [
            "documents",
            "desktop",
            "pictures",
            "videos",
            "music",
            "downloads",
            "my documents",
            "/home/",
            "users",
        ]

        return any(user_dir in path_str for user_dir in user_dirs)

    def set_user_override(
        self, file_path: Path, category: CategoryType, explanation: str
    ) -> None:
        """Set user override for file category."""
        self._user_overrides[str(file_path)] = {
            "category": category.value,
            "explanation": explanation,
            "timestamp": datetime.now().isoformat(),
        }
        logger.info(
            f"User override set for {sanitize_path(str(file_path))}: {category.value}"
        )

    def remove_user_override(self, file_path: Path) -> None:
        """Remove user override for file."""
        if str(file_path) in self._user_overrides:
            del self._user_overrides[str(file_path)]
            logger.info(f"User override removed for {sanitize_path(str(file_path))}")

    def get_category_stats(self, files: List[FileInfo]) -> Dict[CategoryType, int]:
        """Get statistics for file categories."""
        stats = {category: 0 for category in CategoryType}

        for file_info in files:
            result = self.categorize_file(file_info)
            stats[result.category] += 1

        return stats

    def get_rules_documentation(self) -> Dict:
        """Get human-readable rules documentation."""
        return {
            "categories": self._rules["categories"],
            "systemPaths": {
                "windows": ["C:\\Windows", "C:\\Program Files", "System32"],
                "linux": ["/usr", "/etc", "/bin", "/sbin"],
            },
            "tempPaths": {
                "windows": ["%TEMP%", "%APPDATA%\\Local\\Temp"],
                "linux": ["/tmp", "/var/cache"],
            },
        }
