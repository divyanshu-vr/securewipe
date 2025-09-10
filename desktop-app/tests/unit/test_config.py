"""Unit tests for configuration management."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch
import sys

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from config.settings import Settings
from config.defaults import get_user_config_dir, get_log_file_path


class TestSettings:
    """Test cases for Settings class."""
    
    def setup_method(self):
        """Setup test environment with temporary config."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / "settings.json"
        
        # Patch the config directory
        with patch('config.settings.get_user_config_dir', return_value=self.temp_dir):
            self.settings = Settings()
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization_creates_defaults(self):
        """Test that initialization creates default settings."""
        assert self.settings.get("log_level") == "INFO"
        assert self.settings.get("window_geometry.width") == 1024
        assert self.settings.get("window_geometry.height") == 768
    
    def test_get_nested_setting(self):
        """Test getting nested setting values."""
        width = self.settings.get("window_geometry.width")
        assert width == 1024
        
        # Test non-existent key with default
        value = self.settings.get("nonexistent.key", "default_value")
        assert value == "default_value"
    
    def test_set_nested_setting(self):
        """Test setting nested values."""
        self.settings.set("window_geometry.width", 1200)
        assert self.settings.get("window_geometry.width") == 1200
        
        # Test creating new nested structure
        self.settings.set("new.nested.key", "test_value")
        assert self.settings.get("new.nested.key") == "test_value"
    
    def test_save_and_load_settings(self):
        """Test saving and loading settings from file."""
        # Modify a setting
        self.settings.set("log_level", "DEBUG")
        self.settings.save()
        
        # Verify file was created
        assert self.config_file.exists()
        
        # Load settings in new instance
        with patch('config.settings.get_user_config_dir', return_value=self.temp_dir):
            new_settings = Settings()
            assert new_settings.get("log_level") == "DEBUG"
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON in config file."""
        # Create invalid JSON file
        with open(self.config_file, 'w') as f:
            f.write("invalid json content")
        
        # Should create defaults when JSON is invalid
        with patch('config.settings.get_user_config_dir', return_value=self.temp_dir):
            settings = Settings()
            assert settings.get("log_level") == "INFO"


class TestDefaults:
    """Test cases for default configuration functions."""
    
    def test_get_user_config_dir_windows(self):
        """Test Windows config directory detection."""
        with patch('os.name', 'nt'), patch('os.path.expandvars') as mock_expand:
            mock_expand.return_value = "C:\\Users\\TestUser\\AppData\\Roaming"
            config_dir = get_user_config_dir()
            expected = Path("C:\\Users\\TestUser\\AppData\\Roaming\\SecureWipe")
            assert config_dir == expected
    
    def test_get_user_config_dir_linux(self):
        """Test Linux config directory detection."""
        with patch('os.name', 'posix'), patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path("/home/testuser")
            config_dir = get_user_config_dir()
            expected = Path("/home/testuser/.securewipe")
            assert config_dir == expected
    
    def test_get_log_file_path(self):
        """Test log file path generation."""
        with patch('config.defaults.get_user_config_dir') as mock_config_dir:
            mock_config_dir.return_value = Path("/test/config")
            log_path = get_log_file_path()
            expected = Path("/test/config/debug.log")
            assert log_path == expected