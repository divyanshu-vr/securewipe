"""Tests for file scanner components."""

import pytest
import tempfile
import shutil
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# Add src to path for testing
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared"))

from scanner.file_scanner import FileScanner
from scanner.metadata_extractor import MetadataExtractor
from models.file_info import FileInfo, FileType, ScanProgress


class TestMetadataExtractor:
    """Test metadata extraction functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
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
    
    def test_extract_metadata_permission_error(self):
        """Test handling of permission errors."""
        # Create test file path that doesn't exist
        test_file = self.temp_dir / "nonexistent.txt"
        
        # Extract metadata
        file_info = MetadataExtractor.extract_metadata(test_file)
        
        # Verify error handling
        assert file_info.path == test_file
        assert file_info.is_accessible is False
        assert file_info.error_message is not None
    
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
            test_file.write_text("test")
            
            file_info = MetadataExtractor.extract_metadata(test_file)
            assert file_info.file_type == expected_type
    
    def test_is_accessible(self):
        """Test file accessibility check."""
        # Create accessible file
        test_file = self.temp_dir / "accessible.txt"
        test_file.write_text("test")
        
        assert MetadataExtractor.is_accessible(test_file) is True
        
        # Test non-existent file
        nonexistent = self.temp_dir / "nonexistent.txt"
        assert MetadataExtractor.is_accessible(nonexistent) is False


class TestFileScanner:
    """Test file scanner functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.scanner = FileScanner(batch_size=10, progress_interval=0.01)
        
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_scan_empty_directory(self):
        """Test scanning empty directory."""
        progress_updates = []
        files_found = []
        
        def progress_callback(progress):
            progress_updates.append(progress)
        
        def file_callback(file_info):
            files_found.append(file_info)
        
        # Scan empty directory
        results = list(self.scanner.scan_directories(
            [self.temp_dir], 
            progress_callback=progress_callback,
            file_callback=file_callback
        ))
        
        # Verify results
        assert len(results) == 0
        assert len(files_found) == 0
        assert len(progress_updates) > 0
        assert progress_updates[-1].scanned_files == 0
    
    def test_scan_directory_with_files(self):
        """Test scanning directory with files."""
        # Create test files
        (self.temp_dir / "file1.txt").write_text("content1")
        (self.temp_dir / "file2.pdf").write_text("content2")
        
        subdir = self.temp_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.jpg").write_text("content3")
        
        progress_updates = []
        files_found = []
        
        def progress_callback(progress):
            progress_updates.append(progress)
        
        def file_callback(file_info):
            files_found.append(file_info)
        
        # Scan directory
        results = list(self.scanner.scan_directories(
            [self.temp_dir],
            progress_callback=progress_callback,
            file_callback=file_callback
        ))
        
        # Verify results
        assert len(results) == 3
        assert len(files_found) == 3
        assert len(progress_updates) > 0
        
        # Check final progress
        final_progress = progress_updates[-1]
        assert final_progress.scanned_files == 3
        assert final_progress.total_size > 0
        
        # Verify file types
        file_types = {f.file_type for f in results}
        assert FileType.DOCUMENT in file_types
        assert FileType.IMAGE in file_types
    
    def test_scan_cancellation(self):
        """Test scan cancellation."""
        # Create many files to allow cancellation
        for i in range(20):
            (self.temp_dir / f"file{i}.txt").write_text(f"content{i}")
        
        files_found = []
        
        def file_callback(file_info):
            files_found.append(file_info)
            # Cancel after finding 5 files
            if len(files_found) >= 5:
                self.scanner.cancel()
        
        # Scan with cancellation
        results = list(self.scanner.scan_directories(
            [self.temp_dir],
            file_callback=file_callback
        ))
        
        # Verify cancellation worked
        assert len(results) < 20
        assert self.scanner.is_cancelled is True
    
    def test_performance_stats(self):
        """Test performance statistics."""
        stats = self.scanner.get_performance_stats()
        
        assert 'batch_size' in stats
        assert 'progress_interval' in stats
        assert 'rate_samples' in stats
        assert 'is_cancelled' in stats
        
        assert stats['batch_size'] == 10
        assert stats['progress_interval'] == 0.01
    
    @patch('scanner.file_scanner.logger')
    def test_error_handling(self, mock_logger):
        """Test error handling during scan."""
        # Create directory that will cause permission error
        restricted_dir = self.temp_dir / "restricted"
        restricted_dir.mkdir()
        
        # Mock permission error
        with patch.object(Path, 'iterdir', side_effect=PermissionError("Access denied")):
            results = list(self.scanner.scan_directories([restricted_dir]))
            
            # Should handle error gracefully
            assert len(results) == 0
            mock_logger.warning.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])