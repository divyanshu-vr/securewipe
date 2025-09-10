"""User preferences and settings management."""

import json
from typing import Any, Dict

from .defaults import LOG_LEVEL_DEFAULT, get_user_config_dir


class Settings:
    """Manages user preferences and application settings."""

    def __init__(self):
        self.config_dir = get_user_config_dir()
        self.config_file = self.config_dir / "settings.json"
        self._settings: Dict[str, Any] = {}
        self._load_settings()

    def _load_settings(self) -> None:
        """Load settings from file or create defaults."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self._settings = json.load(f)
            else:
                self._create_default_settings()
        except (json.JSONDecodeError, OSError):
            self._create_default_settings()

    def _create_default_settings(self) -> None:
        """Create default settings."""
        self._settings = {
            "log_level": LOG_LEVEL_DEFAULT,
            "window_geometry": {"width": 1024, "height": 768, "x": None, "y": None},
            "scan_preferences": {
                "include_hidden_files": False,
                "include_system_files": False,
            },
            "ui_preferences": {"theme": "default", "show_tooltips": True},
        }
        self.save()

    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value by key."""
        keys = key.split(".")
        value = self._settings

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set setting value by key."""
        keys = key.split(".")
        setting = self._settings

        for k in keys[:-1]:
            if k not in setting:
                setting[k] = {}
            setting = setting[k]

        setting[keys[-1]] = value

    def save(self) -> None:
        """Save settings to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2)
        except OSError as e:
            # Log error but don't crash application
            print(f"Warning: Could not save settings: {e}")


# Global settings instance
settings = Settings()
