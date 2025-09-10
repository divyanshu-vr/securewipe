"""Default configurations for SecureWipe Desktop Application."""

import os
from pathlib import Path

# Application metadata
APP_NAME = "SecureWipe"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Secure File Deletion System"

# UI Configuration
WINDOW_TITLE = f"{APP_NAME} - Desktop Quick Clean"
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600
WINDOW_DEFAULT_WIDTH = 1024
WINDOW_DEFAULT_HEIGHT = 768

# Logging Configuration
LOG_LEVEL_DEFAULT = "INFO"
LOG_LEVEL_DEBUG = "DEBUG"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Directory Detection
DEFAULT_USER_DIRECTORIES = ["Documents", "Downloads", "Desktop"]

# Temporary directories (platform-specific)
TEMP_DIRECTORIES = {
    "windows": [
        os.path.expandvars(r"%TEMP%"),
        os.path.expandvars(r"%TMP%"),
        os.path.expandvars(r"%LOCALAPPDATA%\Temp"),
    ],
    "linux": ["/tmp", "/var/tmp", os.path.expanduser("~/.cache")],
}


# File paths
def get_user_config_dir() -> Path:
    """Get user-specific configuration directory."""
    if os.name == "nt":  # Windows
        return Path(os.path.expandvars(r"%APPDATA%")) / APP_NAME
    else:  # Linux/Unix
        return Path.home() / f".{APP_NAME.lower()}"


def get_log_file_path() -> Path:
    """Get log file path in user-appropriate location."""
    return get_user_config_dir() / "debug.log"
