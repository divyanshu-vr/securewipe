"""Tests for UI components."""

import pytest
import tkinter as tk
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# Add src to path for testing
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

# Mock shared modules
sys.modules['shared'] = Mock()
sys.modules['shared.models'] = Mock()
sys.modules['shared.models.file_info'] = Mock()

# Import components after mocking
from ui.components.progress_indicator import ProgressIndicator, BatchProgressTracker
from ui.components.file_tree import FileTreeView
from ui.components.scan_controller import ScanController


class TestProgressIndicator:
    """Test progress indicator component."""
    
    def setup_method(self):
        """Setup test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests
        self.progress = ProgressIndicator(self.root)
        
    def teardown_method(self):
        """Cleanup test environment."""
        self.root.destroy()
    
    def test_initialization(self):
        """Test progress indicator initialization."""
        assert self.progress.is_scanning is False
        assert self.progress.progress_var.get() == 0
        assert "Ready to scan" in self.progress.status_var.get()
    
    def test_start_scan(self):
        """Test starting scan mode."""
        cancel_callback = Mock()
        self.progress.start_scan(cancel_callback)
        
        assert self.progress.is_scanning is True
        assert "Initializing" in self.progress.status_var.get()
        assert self.progress.cancel_button['state'] == 'normal'
    
    def test_finish_scan_success(self):
        """Test finishing scan successfully."""
        self.progress.start_scan()
        self.progress.finish_scan(success=True)
        
        assert self.progress.is_scanning is False
        assert "completed successfully" in self.progress.status_var.get()
        assert self.progress.progress_var.get() == 100
    
    def test_finish_scan_failure(self):
        """Test finishing scan with failure."""
        self.progress.start_scan()
        self.progress.finish_scan(success=False)
        
        assert self.progress.is_scanning is False
        assert "cancelled or failed" in self.progress.status_var.get()
    
    def test_format_time(self):
        """Test time formatting."""
        # Test various time formats
        assert "seconds" in self.progress._format_time(15)
        assert "minute" in self.progress._format_time(90)
        assert "minutes" in self.progress._format_time(180)
        assert "large operation" in self.progress._format_time(600)


class TestBatchProgressTracker:
    """Test batch progress tracker."""
    
    def setup_method(self):
        """Setup test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        self.progress_indicator = ProgressIndicator(self.root)
        self.tracker = BatchProgressTracker(self.progress_indicator, batch_size=5)
        
    def teardown_method(self):
        """Cleanup test environment."""
        self.root.destroy()
    
    def test_batch_tracking(self):
        """Test batch progress tracking."""
        # Mock progress object
        mock_progress = Mock()
        mock_progress.progress_percent = 50.0
        
        # Add files - should update every 5 files
        for i in range(10):
            self.tracker.add_file(mock_progress)
        
        # Verify batch size is respected
        assert self.tracker._file_count == 10


class TestFileTreeView:
    """Test file tree view component."""
    
    def setup_method(self):
        """Setup test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        self.tree_view = FileTreeView(self.root)
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Cleanup test environment."""
        self.root.destroy()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test tree view initialization."""
        # Check that tree is created
        assert self.tree_view.tree is not None
        assert self.tree_view.summary_tree is not None
        
        # Check initial state
        stats = self.tree_view.get_statistics()
        assert stats['total_files'] == 0
        assert stats['total_size'] == 0
    
    def test_format_size(self):
        """Test size formatting."""
        assert self.tree_view._format_size(0) == '0 B'
        assert self.tree_view._format_size(512) == '512 B'
        assert self.tree_view._format_size(1024) == '1.0 KB'
        assert self.tree_view._format_size(1048576) == '1.0 MB'
        assert self.tree_view._format_size(1073741824) == '1.0 GB'
    
    def test_clear(self):
        """Test clearing tree contents."""
        self.tree_view.clear()
        
        # Verify tree is empty
        assert len(self.tree_view.tree.get_children()) == 0
        assert len(self.tree_view._file_nodes) == 0
        assert len(self.tree_view._directory_nodes) == 0
        
        # Verify counters are reset
        stats = self.tree_view.get_statistics()
        assert stats['total_files'] == 0
        assert stats['total_size'] == 0


class TestScanController:
    """Test scan controller."""
    
    def setup_method(self):
        """Setup test environment."""
        self.controller = ScanController()
        
    def test_initialization(self):
        """Test controller initialization."""
        assert self.controller.is_scanning is False
        assert self.controller.is_cancelled is False
    
    def test_cancel_scan(self):
        """Test scan cancellation."""
        # Mock scanner
        mock_scanner = Mock()
        mock_scanner.cancel = Mock()
        
        self.controller._scanner = mock_scanner
        self.controller._is_scanning = True
        
        self.controller.cancel_scan()
        
        assert self.controller._scan_cancelled is True
        mock_scanner.cancel.assert_called_once()
    
    def test_clear_queue(self):
        """Test queue clearing."""
        # Add items to queue
        import queue
        test_queue = queue.Queue()
        test_queue.put("item1")
        test_queue.put("item2")
        
        # Clear queue
        self.controller._clear_queue(test_queue)
        
        # Verify queue is empty
        assert test_queue.empty()


if __name__ == "__main__":
    pytest.main([__file__])