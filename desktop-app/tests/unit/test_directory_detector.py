"""Unit tests for directory detection functionality."""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from directory_detector import DirectoryDetector


class TestDirectoryDetector:
    """Test cases for DirectoryDetector class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.detector = DirectoryDetector(debug=True)
    
    def test_initialization(self):
        """Test DirectoryDetector initialization."""
        assert self.detector is not None
        assert self.detector.platform in ["windows", "linux"]
    
    def test_platform_detection(self):
        """Test platform detection logic."""
        with patch('os.name', 'nt'):
            detector = DirectoryDetector()
            assert detector.platform == "windows"
        
        with patch('os.name', 'posix'):
            detector = DirectoryDetector()
            assert detector.platform == "linux"
    
    def test_validate_directory_access_existing(self):
        """Test directory validation with existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            result = self.detector._validate_directory_access(temp_path)
            assert result is True
    
    def test_validate_directory_access_nonexistent(self):
        """Test directory validation with non-existent directory."""
        nonexistent_path = Path("/nonexistent/directory/path")
        result = self.detector._validate_directory_access(nonexistent_path)
        assert result is False
    
    def test_check_permissions(self):
        """Test permission checking functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            permissions = self.detector.check_permissions(temp_path)
            
            assert isinstance(permissions, dict)
            assert "read" in permissions
            assert "write" in permissions
            assert "execute" in permissions
            # Should have at least read access to temp directory
            assert permissions["read"] is True
    
    @patch('os.environ.get')
    def test_windows_user_directory_detection(self, mock_env):
        """Test Windows user directory detection."""
        mock_env.return_value = "C:\\Users\\TestUser"
        
        with patch.object(self.detector, 'platform', 'windows'):
            path = self.detector._get_windows_user_directory("Documents")
            expected = Path("C:\\Users\\TestUser\\Documents")
            assert path == expected
    
    def test_linux_user_directory_detection(self):
        """Test Linux user directory detection."""
        with patch.object(self.detector, 'platform', 'linux'):
            with patch('pathlib.Path.home') as mock_home:
                mock_home.return_value = Path("/home/testuser")
                path = self.detector._get_linux_user_directory("Documents")
                expected = Path("/home/testuser/Documents")
                assert path == expected
    
    def test_detect_temp_directories(self):
        """Test temporary directory detection."""
        temp_dirs = self.detector.detect_temp_directories()
        assert isinstance(temp_dirs, list)
        # Should find at least one temp directory on any platform
        # Note: This might be empty in some test environments
    
    def test_get_directory_summary(self):
        """Test comprehensive directory summary."""
        summary = self.detector.get_directory_summary()
        
        assert isinstance(summary, dict)
        assert "platform" in summary
        assert "user_directories" in summary
        assert "temp_directories" in summary
        assert "accessible_count" in summary
        assert "total_count" in summary
        
        assert summary["platform"] in ["windows", "linux"]
        assert isinstance(summary["accessible_count"], int)
        assert isinstance(summary["total_count"], int)
        assert summary["accessible_count"] <= summary["total_count"]