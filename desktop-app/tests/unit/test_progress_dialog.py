"""Tests for progress dialog components."""

import sys
import threading
import time
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ui.progress_dialog import GameProgressBar, MilestoneIndicator, ProgressDialog
from ui.components.progress_indicator import AnimatedProgressBar
from deletion.progress_tracker import ProgressInfo, ProgressState, ProgressTracker


class TestGameProgressBar(unittest.TestCase):
    """Test gaming-style progress bar."""
    
    def setUp(self):
        """Setup test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests
        self.progress_bar = GameProgressBar(self.root)
    
    def tearDown(self):
        """Cleanup test environment."""
        self.root.destroy()
    
    def test_initial_state(self):
        """Test initial progress bar state."""
        self.assertEqual(self.progress_bar.progress, 0.0)
        self.assertEqual(self.progress_bar.width, 400)
        self.assertEqual(self.progress_bar.height, 30)
    
    def test_set_progress(self):
        """Test progress updates."""
        # Test normal progress
        self.progress_bar.set_progress(50.0)
        self.assertEqual(self.progress_bar.progress, 50.0)
        
        # Test boundary conditions
        self.progress_bar.set_progress(-10.0)
        self.assertEqual(self.progress_bar.progress, 0.0)
        
        self.progress_bar.set_progress(150.0)
        self.assertEqual(self.progress_bar.progress, 100.0)
    
    def test_color_changes(self):
        """Test progress bar color changes based on progress."""
        # Low progress should be red
        self.progress_bar.set_progress(20.0)
        # Medium progress should be orange
        self.progress_bar.set_progress(50.0)
        # High progress should be green
        self.progress_bar.set_progress(80.0)


class TestMilestoneIndicator(unittest.TestCase):
    """Test milestone checkpoint indicators."""
    
    def setUp(self):
        """Setup test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        self.milestone = MilestoneIndicator(self.root)
    
    def tearDown(self):
        """Cleanup test environment."""
        self.root.destroy()
    
    def test_milestone_creation(self):
        """Test milestone indicators are created."""
        expected_milestones = ['scan', 'categorize', 'delete', 'complete']
        for milestone in expected_milestones:
            self.assertIn(milestone, self.milestone.milestones)
    
    def test_set_milestone(self):
        """Test setting milestone states."""
        # Test completion
        self.milestone.set_milestone('scan', True)
        self.assertTrue(self.milestone.milestones['scan']['completed'])
        
        # Test active state
        self.milestone.set_milestone('delete', False)
        self.assertFalse(self.milestone.milestones['delete']['completed'])


class TestAnimatedProgressBar(unittest.TestCase):
    """Test animated progress bar component."""
    
    def setUp(self):
        """Setup test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        self.animated_bar = AnimatedProgressBar(self.root)
    
    def tearDown(self):
        """Cleanup test environment."""
        self.root.destroy()
    
    def test_initial_state(self):
        """Test initial animated bar state."""
        self.assertEqual(self.animated_bar.progress, 0.0)
        self.assertEqual(self.animated_bar.animation_offset, 0)
    
    def test_progress_update(self):
        """Test progress updates."""
        self.animated_bar.set_progress(75.0)
        self.assertEqual(self.animated_bar.progress, 75.0)
    
    def test_animation_setup(self):
        """Test animation elements are created."""
        self.assertIsNotNone(self.animated_bar.progress_rect)
        self.assertGreater(len(self.animated_bar.stripes), 0)


class TestProgressDialog(unittest.TestCase):
    """Test main progress dialog."""
    
    def setUp(self):
        """Setup test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
        self.dialog = ProgressDialog(self.root)
        
        # Mock progress tracker
        self.mock_tracker = MagicMock(spec=ProgressTracker)
        self.mock_tracker.get_progress_info.return_value = ProgressInfo(
            total_files=100,
            processed_files=50,
            current_file=Path("test_file.txt"),
            bytes_processed=1024000,
            total_bytes=2048000,
            elapsed_time=30.0,
            estimated_remaining=30.0,
            state=ProgressState.RUNNING,
            success_count=45,
            error_count=2,
            skipped_count=3
        )
    
    def tearDown(self):
        """Cleanup test environment."""
        self.dialog.destroy()
        self.root.destroy()
    
    def test_dialog_creation(self):
        """Test dialog is created properly."""
        self.assertIsNotNone(self.dialog.game_progress)
        self.assertIsNotNone(self.dialog.milestone_indicator)
        self.assertIsNotNone(self.dialog.log_text)
    
    def test_start_operation(self):
        """Test starting an operation."""
        cancel_callback = MagicMock()
        
        self.dialog.start_operation(
            self.mock_tracker,
            cancel_callback=cancel_callback
        )
        
        self.assertTrue(self.dialog.is_running)
        self.assertEqual(self.dialog.cancel_callback, cancel_callback)
        self.assertEqual(self.dialog.progress_tracker, self.mock_tracker)
    
    def test_ui_updates(self):
        """Test UI updates with progress info."""
        progress_info = ProgressInfo(
            total_files=100,
            processed_files=75,
            current_file=Path("current_file.txt"),
            bytes_processed=1536000,
            total_bytes=2048000,
            elapsed_time=45.0,
            estimated_remaining=15.0,
            state=ProgressState.RUNNING,
            success_count=70,
            error_count=3,
            skipped_count=2
        )
        
        self.dialog._update_ui(progress_info)
        
        # Check progress bar update
        self.assertEqual(self.dialog.game_progress.progress, 75.0)
        
        # Check file display
        self.assertIn("current_file.txt", self.dialog.current_file_var.get())
        
        # Check statistics
        self.assertEqual(self.dialog.files_var.get(), "75 / 100")
        self.assertEqual(self.dialog.success_var.get(), "70")
        self.assertEqual(self.dialog.errors_var.get(), "3")
    
    def test_operation_completion(self):
        """Test operation completion handling."""
        self.dialog.is_running = True
        
        # Test successful completion
        self.dialog._operation_finished(ProgressState.COMPLETED)
        
        self.assertFalse(self.dialog.is_running)
        self.assertEqual(self.dialog.game_progress.progress, 100.0)
        self.assertIn("completed successfully", self.dialog.phase_var.get())
    
    def test_operation_cancellation(self):
        """Test operation cancellation."""
        self.dialog.is_running = True
        
        # Test cancellation
        self.dialog._operation_finished(ProgressState.CANCELLED)
        
        self.assertFalse(self.dialog.is_running)
        self.assertIn("cancelled", self.dialog.phase_var.get())
    
    def test_log_filtering(self):
        """Test log message filtering."""
        # Add test messages
        self.dialog._log_message("Test info message", "INFO")
        self.dialog._log_message("Test error message", "ERROR")
        self.dialog._log_message("Test success message", "SUCCESS")
        
        # Test all messages shown
        self.dialog.show_all_var.set(True)
        self.dialog._update_log_filter()
        log_content = self.dialog.log_text.get(1.0, tk.END)
        self.assertIn("Test info message", log_content)
        self.assertIn("Test error message", log_content)
        self.assertIn("Test success message", log_content)
        
        # Test errors only
        self.dialog.show_all_var.set(False)
        self.dialog.show_errors_var.set(True)
        self.dialog.show_success_var.set(False)
        self.dialog.show_info_var.set(False)  # Also set info filter to False
        self.dialog._update_log_filter()
        log_content = self.dialog.log_text.get(1.0, tk.END)
        self.assertIn("Test error message", log_content)
        self.assertNotIn("Test info message", log_content)
    
    def test_time_formatting(self):
        """Test time duration formatting."""
        # Test seconds
        self.assertEqual(self.dialog._format_time(30), "30s")
        
        # Test minutes
        self.assertEqual(self.dialog._format_time(90), "1m 30s")
        
        # Test hours
        self.assertEqual(self.dialog._format_time(3665), "1h 1m")
    
    def test_pause_resume_functionality(self):
        """Test pause and resume controls."""
        # Setup running operation
        self.mock_tracker.is_running.return_value = True
        self.mock_tracker.is_paused.return_value = False
        
        pause_callback = MagicMock()
        resume_callback = MagicMock()
        
        self.dialog.start_operation(
            self.mock_tracker,
            pause_callback=pause_callback,
            resume_callback=resume_callback
        )
        
        # Test pause
        self.dialog._on_pause()
        pause_callback.assert_called_once()
        
        # Test resume
        self.mock_tracker.is_running.return_value = False
        self.mock_tracker.is_paused.return_value = True
        self.dialog._on_pause()
        resume_callback.assert_called_once()
    
    def test_cancel_functionality(self):
        """Test cancel operation."""
        cancel_callback = MagicMock()
        
        self.dialog.start_operation(
            self.mock_tracker,
            cancel_callback=cancel_callback
        )
        
        self.dialog._on_cancel()
        cancel_callback.assert_called_once()
        self.assertFalse(self.dialog.is_running)
    
    @patch('tkinter.filedialog.asksaveasfilename')
    @patch('builtins.open', create=True)
    def test_log_export(self, mock_open, mock_filedialog):
        """Test log export functionality."""
        mock_filedialog.return_value = "test_log.txt"
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Add some log entries
        self.dialog._log_message("Test message 1", "INFO")
        self.dialog._log_message("Test message 2", "ERROR")
        
        # Export log
        self.dialog._export_log()
        
        # Verify file operations
        mock_filedialog.assert_called_once()
        mock_open.assert_called_once_with("test_log.txt", 'w', encoding='utf-8')
        mock_file.write.assert_called()


class TestProgressIntegration(unittest.TestCase):
    """Test integration between progress components."""
    
    def setUp(self):
        """Setup test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Cleanup test environment."""
        self.root.destroy()
    
    def test_progress_tracker_integration(self):
        """Test integration with progress tracker."""
        # Create progress tracker with callback
        progress_updates = []
        
        def update_callback(progress_info):
            progress_updates.append(progress_info)
        
        tracker = ProgressTracker(update_callback)
        
        # Start operation
        tracker.start_operation(total_files=10, total_bytes=1024000)
        
        # Simulate file processing
        from models.operation_result import OperationResult, OperationStatus
        
        for i in range(5):
            tracker.update_current_file(Path(f"file_{i}.txt"), 102400)
            result = OperationResult(status=OperationStatus.SUCCESS)
            tracker.file_completed(result, 102400)
        
        # Verify progress updates
        self.assertGreater(len(progress_updates), 0)
        final_progress = tracker.get_progress_info()
        self.assertEqual(final_progress.processed_files, 5)
        self.assertEqual(final_progress.success_count, 5)
    
    def test_threading_safety(self):
        """Test thread safety of progress updates."""
        dialog = ProgressDialog(self.root)
        
        # Mock progress tracker
        mock_tracker = MagicMock(spec=ProgressTracker)
        mock_tracker.get_progress_info.return_value = ProgressInfo(
            total_files=100,
            processed_files=50,
            state=ProgressState.RUNNING
        )
        
        # Start operation
        dialog.start_operation(mock_tracker)
        
        # Let update thread run briefly
        time.sleep(0.2)
        
        # Stop operation
        dialog.is_running = False
        
        # Verify no exceptions occurred
        self.assertIsNotNone(dialog.progress_tracker)


if __name__ == '__main__':
    unittest.main()