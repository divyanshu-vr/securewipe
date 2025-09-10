"""Basic tests for scanner components without shared dependencies."""

import pytest
import tempfile
import shutil
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# Add src to path for testing
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

# Mock the shared modules to avoid import issues
sys.modules['shared'] = Mock()
sys.modules['shared.logging'] = Mock()
sys.modules['shared.logging.secure_logger'] = Mock()
sys.modules['shared.logging.sanitizer'] = Mock()
sys.modules['shared.models'] = Mock()
sys.modules['shared.models.file_info'] = Mock()

# Mock logger functions
mock_logger = Mock()
mock_logger.info = Mock()
mock_logger.warning = Mock()
mock_logger.error = Mock()
mock_logger.debug = Mock()

def mock_get_logger(name):
    return mock_logger

def mock_sanitize_path(path):
    return str(path)

# Patch the imports
with patch.dict('sys.modules', {
    'shared.logging.secure_logger': Mock(get_logger=mock_get_logger),
    'shared.logging.sanitizer': Mock(sanitize_path=mock_sanitize_path),
}):
    from scanner.metadata_extractor import MetadataExtractor, FileType


class TestMetadataExtractorBasic:
    """Basic test for metadata extraction functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_file_type_detection(self):
        """Test file type detection from extensions."""
        test_cases = [
            ("test.pdf", FileType.DOCUMENT),
            ("image.jpg", FileType.IMAGE),
            ("video.mp4", FileType.VIDEO),
            ("audio.mp3", FileType.AUDIO),
            ("archive.zip", FileType.ARCHIVE),
            ("program.exe", FileType.EXECUTABLE),
            ("unknown.xyz", FileType.OTHER),
        ]
        
        for filename, expected_type in test_cases:
            test_file = self.temp_dir / filename
            actual_type = MetadataExtractor._get_file_type(test_file)
            assert actual_type == expected_type, f"Expected {expected_type} for {filename}, got {actual_type}"
    
    def test_extract_metadata_success(self):
        """Test successful metadata extraction."""
        # Create test file
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("test content")
        
        # Extract metadata
        file_info = MetadataExtractor.extract_metadata(test_file)
        
        # Verify results
        assert file_info.path == test_file
        assert file_info.size > 0
        assert file_info.file_type == FileType.DOCUMENT
        assert file_info.is_accessible is True
        assert file_info.error_message is None
    
    def test_is_accessible(self):
        """Test file accessibility check."""
        # Create accessible file
        test_file = self.temp_dir / "accessible.txt"
        test_file.write_text("test")
        
        assert MetadataExtractor.is_accessible(test_file) is True
        
        # Test non-existent file
        nonexistent = self.temp_dir / "nonexistent.txt"
        assert MetadataExtractor.is_accessible(nonexistent) is False


if __name__ == "__main__":
    pytest.main([__file__])