"""Directory detection and validation for SecureWipe Desktop."""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add shared module to path
sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))

from config.defaults import DEFAULT_USER_DIRECTORIES, TEMP_DIRECTORIES

from shared.secure_logging.sanitizer import sanitize_path
from shared.secure_logging.secure_logger import get_logger


class DirectoryDetector:
    """Detects and validates user directories for scanning."""

    def __init__(self, debug: bool = False):
        self.logger = get_logger(__name__, debug=debug)
        self.platform = "windows" if os.name == "nt" else "linux"

    def detect_user_directories(self) -> Dict[str, Optional[Path]]:
        """Detect standard user directories."""
        directories = {}

        for dir_name in DEFAULT_USER_DIRECTORIES:
            try:
                path = self._get_user_directory_path(dir_name)
                if path and self._validate_directory_access(path):
                    directories[dir_name] = path
                    self.logger.info(f"Detected {dir_name} directory")
                else:
                    directories[dir_name] = None
                    self.logger.warning(f"Could not access {dir_name} directory")
            except Exception as e:
                directories[dir_name] = None
                self.logger.error(
                    f"Error detecting {dir_name}: {sanitize_path(str(e))}"
                )

        return directories

    def detect_temp_directories(self) -> List[Path]:
        """Detect temporary directories for the current platform."""
        temp_dirs = []
        platform_temps = TEMP_DIRECTORIES.get(self.platform, [])

        for temp_path in platform_temps:
            try:
                path = Path(temp_path).resolve()
                if self._validate_directory_access(path):
                    temp_dirs.append(path)
                    self.logger.info(
                        f"Detected temp directory: {sanitize_path(str(path))}"
                    )
            except Exception as e:
                self.logger.warning(
                    f"Could not access temp directory {sanitize_path(temp_path)}: {e}"
                )

        return temp_dirs

    def _get_user_directory_path(self, dir_name: str) -> Optional[Path]:
        """Get path for a standard user directory."""
        try:
            if self.platform == "windows":
                return self._get_windows_user_directory(dir_name)
            else:
                return self._get_linux_user_directory(dir_name)
        except Exception as e:
            self.logger.error(f"Error getting {dir_name} path: {e}")
            return None

    def _get_windows_user_directory(self, dir_name: str) -> Optional[Path]:
        """Get Windows user directory path."""
        user_profile = os.environ.get("USERPROFILE")
        if not user_profile:
            return None

        directory_map = {
            "Documents": Path(user_profile) / "Documents",
            "Downloads": Path(user_profile) / "Downloads",
            "Desktop": Path(user_profile) / "Desktop",
        }

        return directory_map.get(dir_name)

    def _get_linux_user_directory(self, dir_name: str) -> Optional[Path]:
        """Get Linux user directory path."""
        home = Path.home()

        directory_map = {
            "Documents": home / "Documents",
            "Downloads": home / "Downloads",
            "Desktop": home / "Desktop",
        }

        return directory_map.get(dir_name)

    def _validate_directory_access(self, path: Path) -> bool:
        """Validate directory exists and is accessible."""
        try:
            if not path.exists():
                self.logger.warning(
                    f"Directory does not exist: {sanitize_path(str(path))}"
                )
                return False

            if not path.is_dir():
                self.logger.warning(
                    f"Path is not a directory: {sanitize_path(str(path))}"
                )
                return False

            # Test read access
            try:
                list(path.iterdir())
                return True
            except PermissionError:
                self.logger.warning(f"Permission denied: {sanitize_path(str(path))}")
                return False

        except Exception as e:
            self.logger.error(
                f"Error validating directory {sanitize_path(str(path))}: {e}"
            )
            return False

    def check_permissions(self, path: Path) -> Dict[str, bool]:
        """Check specific permissions for a directory."""
        permissions = {"read": False, "write": False, "execute": False}

        try:
            # Test read permission
            try:
                list(path.iterdir())
                permissions["read"] = True
            except PermissionError:
                pass

            # Test write permission
            try:
                test_file = path / ".securewipe_test"
                test_file.touch()
                test_file.unlink()
                permissions["write"] = True
            except (PermissionError, OSError):
                pass

            # Test execute permission (directory traversal)
            try:
                path.resolve()
                permissions["execute"] = True
            except PermissionError:
                pass

        except Exception as e:
            self.logger.error(
                f"Error checking permissions for {sanitize_path(str(path))}: {e}"
            )

        return permissions

    def get_directory_summary(self) -> Dict[str, any]:
        """Get comprehensive directory detection summary."""
        user_dirs = self.detect_user_directories()
        temp_dirs = self.detect_temp_directories()

        summary = {
            "platform": self.platform,
            "user_directories": {},
            "temp_directories": [],
            "accessible_count": 0,
            "total_count": 0,
        }

        # Process user directories
        for name, path in user_dirs.items():
            summary["total_count"] += 1
            if path:
                summary["accessible_count"] += 1
                permissions = self.check_permissions(path)
                summary["user_directories"][name] = {
                    "path": str(path),
                    "accessible": True,
                    "permissions": permissions,
                }
            else:
                summary["user_directories"][name] = {
                    "path": None,
                    "accessible": False,
                    "permissions": {"read": False, "write": False, "execute": False},
                }

        # Process temp directories
        for path in temp_dirs:
            summary["total_count"] += 1
            summary["accessible_count"] += 1
            permissions = self.check_permissions(path)
            summary["temp_directories"].append(
                {"path": str(path), "accessible": True, "permissions": permissions}
            )

        self.logger.info(
            f"Directory detection complete: {summary['accessible_count']}/{summary['total_count']} accessible"
        )
        return summary
