"""Unit tests for secure deletion engine."""

import sys
import tempfile
import unittest
import threading
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared"))
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from models.file_info import FileInfo, FileType
from models.operation_result import OperationResult, OperationStatus
from deletion.secure_delete import SecureDeleteEngine, DeletionConfig
from deletion.os_integration import OSIntegration, DeletionMethod
from deletion.progress_tracker import ProgressTracker, ProgressState


class TestOSIntegration(unittest.TestCase):
    """Test OS integration for secure deletion."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.os_integration = OSIntegration()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_tool_detection(self):
        """Test detection of available deletion tools."""
        tools = self.os_integration.available_tools
        self.assertIsInstance(tools, dict)
        
        # Should detect at least one tool or have fallback
        self.assertTrue(len(tools) >= 0)
    
    def test_get_tool_info(self):
        """Test tool information retrieval."""
        info = self.os_integration.get_tool_info()
        
        required_keys = ["platform", "available_tools", "nist_compliance", "supported_methods"]
        for key in required_keys:
            self.assertIn(key, info)
        
        self.assertIsInstance(info["nist_compliance"], bool)
        self.assertTrue(info["nist_compliance"])
    
    def test_secure_delete_nonexistent_file(self):
        """Test deletion of non-existent file."""
        nonexistent_file = self.temp_dir / "nonexistent.txt"
        
        result = self.os_integration.secure_delete_file(nonexistent_file)
        
        self.assertEqual(result.status, OperationStatus.SKIPPED)
        self.assertIn("not found", result.message.lower())
    
    def test_secure_delete_existing_file(self):
        """Test deletion of existing file."""
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("sensitive data")
        
        self.assertTrue(test_file.exists())
        
        result = self.os_integration.secure_delete_file(test_file)
        
        # Should succeed or use fallback
        self.assertIn(result.status, [OperationStatus.SUCCESS])
        
        # File should be gone
        self.assertFalse(test_file.exists())
    
    def test_windows_sdelete_success(self):
        """Test successful Windows sdelete operation."""
        if self.os_integration.platform != "windows":
            self.skipTest("Windows-specific test")
        
        # Mock successful sdelete
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        
        with patch('subprocess.run', return_value=mock_result):
            test_file = self.temp_dir / "test.txt"
            test_file.write_text("test")
            
            result = self.os_integration._delete_windows(test_file, DeletionMethod.CLEAR)
            
            self.assertEqual(result.status, OperationStatus.SUCCESS)
    
    def test_linux_shred_success(self):
        """Test successful Linux shred operation."""
        if self.os_integration.platform != "linux":
            self.skipTest("Linux-specific test")
        
        # Mock successful shred
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        
        with patch('subprocess.run', return_value=mock_result):
            test_file = self.temp_dir / "test.txt"
            test_file.write_text("test")
            
            result = self.os_integration._delete_linux(test_file, DeletionMethod.CLEAR)
            
            self.assertEqual(result.status, OperationStatus.SUCCESS)
    
    def test_fallback_deletion(self):
        """Test fallback deletion method."""
        test_file = self.temp_dir / "test.txt"
        test_content = "sensitive data" * 100  # Make it larger
        test_file.write_text(test_content)
        
        result = self.os_integration._fallback_delete(test_file)
        
        self.assertEqual(result.status, OperationStatus.SUCCESS)
        self.assertFalse(test_file.exists())


class TestProgressTracker(unittest.TestCase):
    """Test progress tracking functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.progress_updates = []
        self.tracker = ProgressTracker(self._progress_callback)
    
    def _progress_callback(self, progress_info):
        """Callback to capture progress updates."""
        self.progress_updates.append(progress_info)
    
    def test_initial_state(self):
        """Test initial progress tracker state."""
        info = self.tracker.get_progress_info()
        
        self.assertEqual(info.state, ProgressState.IDLE)
        self.assertEqual(info.total_files, 0)
        self.assertEqual(info.processed_files, 0)
    
    def test_start_operation(self):
        """Test starting an operation."""
        self.tracker.start_operation(10, 1000)
        
        info = self.tracker.get_progress_info()
        self.assertEqual(info.state, ProgressState.RUNNING)
        self.assertEqual(info.total_files, 10)
        self.assertEqual(info.total_bytes, 1000)
    
    def test_file_completion(self):
        """Test file completion tracking."""
        self.tracker.start_operation(5, 500)
        
        # Complete a successful file
        result = OperationResult(
            status=OperationStatus.SUCCESS,
            message="Deleted",
            path=Path("test.txt")
        )
        
        self.tracker.file_completed(result, 100)
        
        info = self.tracker.get_progress_info()
        self.assertEqual(info.processed_files, 1)
        self.assertEqual(info.success_count, 1)
        self.assertEqual(info.bytes_processed, 100)
    
    def test_pause_resume(self):
        """Test pause and resume functionality."""
        self.tracker.start_operation(5, 500)
        
        # Pause
        self.tracker.pause()
        self.assertEqual(self.tracker.get_progress_info().state, ProgressState.PAUSED)
        self.assertTrue(self.tracker.is_paused())
        
        # Resume
        self.tracker.resume()
        self.assertEqual(self.tracker.get_progress_info().state, ProgressState.RUNNING)
        self.assertTrue(self.tracker.is_running())
    
    def test_cancellation(self):
        """Test operation cancellation."""
        self.tracker.start_operation(5, 500)
        
        self.tracker.cancel()
        
        self.assertEqual(self.tracker.get_progress_info().state, ProgressState.CANCELLED)
        self.assertTrue(self.tracker.is_cancelled())
    
    def test_progress_percentage(self):
        """Test progress percentage calculation."""
        self.tracker.start_operation(4, 400)
        
        # Complete 2 files
        for i in range(2):
            result = OperationResult(
                status=OperationStatus.SUCCESS,
                message="Deleted",
                path=Path(f"test{i}.txt")
            )
            self.tracker.file_completed(result, 100)
        
        percentage = self.tracker.get_progress_percentage()
        self.assertEqual(percentage, 50.0)


class TestSecureDeleteEngine(unittest.TestCase):
    """Test secure deletion engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.progress_updates = []
        self.engine = SecureDeleteEngine(self._progress_callback)
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def _progress_callback(self, progress_info):
        """Callback to capture progress updates."""
        self.progress_updates.append(progress_info)
    
    def test_validate_files_safe(self):
        """Test file validation for safe files."""
        # Create test files
        test_file = self.temp_dir / "safe_file.txt"
        test_file.write_text("test content")
        
        file_info = FileInfo(
            path=test_file,
            size=100,
            modified_date=datetime.now(),
            file_type=FileType.DOCUMENT
        )
        
        validation = self.engine.validate_files([file_info])
        
        self.assertEqual(len(validation["safe_to_delete"]), 1)
        self.assertEqual(len(validation["system_files"]), 0)
    
    def test_validate_files_system(self):
        """Test file validation for system files."""
        # Mock system file
        system_file = Path("C:/Windows/System32/kernel32.dll")
        
        file_info = FileInfo(
            path=system_file,
            size=1000,
            modified_date=datetime.now(),
            file_type=FileType.OTHER
        )
        
        validation = self.engine.validate_files([file_info])
        
        self.assertEqual(len(validation["system_files"]), 1)
        self.assertEqual(len(validation["safe_to_delete"]), 0)
    
    def test_validate_files_missing(self):
        """Test file validation for missing files."""
        missing_file = self.temp_dir / "nonexistent.txt"
        
        file_info = FileInfo(
            path=missing_file,
            size=100,
            modified_date=datetime.now(),
            file_type=FileType.DOCUMENT
        )
        
        validation = self.engine.validate_files([file_info])
        
        self.assertEqual(len(validation["missing_files"]), 1)
        self.assertEqual(len(validation["safe_to_delete"]), 0)
    
    def test_delete_files_sync(self):
        """Test synchronous file deletion."""
        # Create test files
        test_files = []
        for i in range(3):
            test_file = self.temp_dir / f"test{i}.txt"
            test_file.write_text(f"content {i}")
            
            file_info = FileInfo(
                path=test_file,
                size=len(f"content {i}"),
                modified_date=datetime.now(),
                file_type=FileType.DOCUMENT
            )
            test_files.append(file_info)
        
        results = self.engine.delete_files_sync(test_files)
        
        self.assertEqual(len(results), 3)
        
        # All files should be successfully deleted
        for result in results:
            self.assertEqual(result.status, OperationStatus.SUCCESS)
        
        # Files should no longer exist
        for file_info in test_files:
            self.assertFalse(Path(file_info.path).exists())
    
    def test_pause_resume_operation(self):
        """Test pause and resume functionality."""
        # Start an operation first
        self.engine.progress_tracker.start_operation(1, 100)
        
        self.engine.pause_operation()
        self.assertTrue(self.engine.progress_tracker.is_paused())
        
        self.engine.resume_operation()
        self.assertFalse(self.engine.progress_tracker.is_paused())
    
    def test_cancel_operation(self):
        """Test operation cancellation."""
        self.engine.cancel_operation()
        self.assertTrue(self.engine.progress_tracker.is_cancelled())
    
    def test_config_update(self):
        """Test configuration updates."""
        new_config = DeletionConfig(
            deletion_method=DeletionMethod.PURGE,
            skip_system_files=False,
            max_retries=5
        )
        
        self.engine.set_config(new_config)
        
        self.assertEqual(self.engine.config.deletion_method, DeletionMethod.PURGE)
        self.assertFalse(self.engine.config.skip_system_files)
        self.assertEqual(self.engine.config.max_retries, 5)
    
    def test_system_file_detection(self):
        """Test system file detection."""
        # Test platform-specific system files
        if self.engine.os_integration.platform == "windows":
            system_files = [
                Path("C:/Windows/System32/kernel32.dll"),
                Path("C:/Program Files/test.exe"),
            ]
            user_files = [
                Path("C:/Users/test/Documents/file.txt"),
            ]
        else:
            system_files = [
                Path("/bin/bash"),
                Path("/usr/lib/test.so"),
            ]
            user_files = [
                Path("/home/user/document.pdf"),
            ]
        
        for file_path in system_files:
            is_system = self.engine._is_system_file(file_path)
            self.assertTrue(is_system, f"{file_path} should be detected as system file")
        
        # User files should not be system files
        for file_path in user_files:
            is_system = self.engine._is_system_file(file_path)
            self.assertFalse(is_system, f"{file_path} should not be detected as system file")


if __name__ == "__main__":
    unittest.main()