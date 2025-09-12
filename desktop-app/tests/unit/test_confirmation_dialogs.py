"""
Unit tests for confirmation dialogs and safety controls.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
from pathlib import Path
import sys
import os

# Add both src and shared to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

# Mock the shared modules to avoid import issues during testing
sys.modules['shared'] = Mock()
sys.modules['shared.models'] = Mock()
sys.modules['shared.models.operation_result'] = Mock()
sys.modules['shared.models.file_info'] = Mock()
sys.modules['shared.secure_logging'] = Mock()
sys.modules['shared.secure_logging.secure_logger'] = Mock()
sys.modules['shared.secure_logging.sanitizer'] = Mock()
sys.modules['shared.utils'] = Mock()
sys.modules['shared.utils.exceptions'] = Mock()

# Mock specific classes and functions
class MockOperationResult:
    def __init__(self):
        self.success = True
        self.status = "SUCCESS"

class MockOperationStatus:
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class MockSecureWipeError(Exception):
    pass

# Mock get_logger function
def mock_get_logger(name):
    return Mock()

# Set up the mocks
sys.modules['shared.models.operation_result'].OperationResult = MockOperationResult
sys.modules['shared.models.operation_result'].OperationStatus = MockOperationStatus
sys.modules['shared.secure_logging.secure_logger'].get_logger = mock_get_logger
sys.modules['shared.utils.exceptions'].SecureWipeError = MockSecureWipeError

from ui.confirmation_dialogs import DeletionSummary
from deletion.system_protection import ProtectionLevel
from deletion.backup_manager import BackupResult
from ui.emergency_controls import EmergencyStopController


class TestDeletionSummary(unittest.TestCase):
    """Test deletion summary data model."""
    
    def setUp(self):
        self.summary = DeletionSummary()
        
    def test_initialization(self):
        """Test summary initialization."""
        self.assertEqual(self.summary.total_files, 0)
        self.assertEqual(self.summary.total_size, 0)
        self.assertIn('Safe', self.summary.categories)
        self.assertIn('Less Important', self.summary.categories)
        self.assertIn('Important', self.summary.categories)
        
    def test_category_structure(self):
        """Test category data structure."""
        for category in self.summary.categories.values():
            self.assertIn('count', category)
            self.assertIn('size', category)
            self.assertEqual(category['count'], 0)
            self.assertEqual(category['size'], 0)


class TestProtectionLevel(unittest.TestCase):
    """Test protection level constants."""
    
    def test_protection_levels(self):
        """Test protection level constants exist."""
        self.assertEqual(ProtectionLevel.CRITICAL, "critical")
        self.assertEqual(ProtectionLevel.SYSTEM, "system")
        self.assertEqual(ProtectionLevel.IMPORTANT, "important")
        self.assertEqual(ProtectionLevel.USER, "user")


class TestBackupResult(unittest.TestCase):
    """Test backup result functionality."""
    
    def test_backup_result_initialization(self):
        """Test backup result data structure."""
        result = BackupResult()
        self.assertFalse(result.success)
        self.assertEqual(result.total_files, 0)
        self.assertEqual(result.backed_up_files, 0)
        self.assertEqual(result.failed_files, 0)
        
    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        result = BackupResult()
        result.total_files = 10
        result.backed_up_files = 8
        
        self.assertEqual(result.success_rate, 80.0)
        
    def test_success_rate_zero_files(self):
        """Test success rate with zero files."""
        result = BackupResult()
        result.total_files = 0
        result.backed_up_files = 0
        
        self.assertEqual(result.success_rate, 0.0)


class TestEmergencyStopController(unittest.TestCase):
    """Test emergency stop functionality."""
    
    def setUp(self):
        self.controller = EmergencyStopController()
        
    def test_initialization(self):
        """Test controller initialization."""
        self.assertFalse(self.controller._is_active)
        self.assertFalse(self.controller.is_stop_requested())
        
    def test_activation_deactivation(self):
        """Test activation and deactivation."""
        self.controller.activate()
        self.assertTrue(self.controller._is_active)
        
        self.controller.deactivate()
        self.assertFalse(self.controller._is_active)
        
    def test_stop_trigger(self):
        """Test emergency stop trigger."""
        self.controller.activate()
        
        # Add mock callback
        callback_called = False
        def mock_callback(reason):
            nonlocal callback_called
            callback_called = True
            
        self.controller.add_stop_callback(mock_callback)
        
        # Trigger stop
        self.controller.trigger_stop("Test stop")
        
        self.assertTrue(self.controller.is_stop_requested())
        self.assertTrue(callback_called)
        
    def test_callback_management(self):
        """Test callback addition and removal."""
        def mock_callback(reason):
            pass
            
        # Add callback
        self.controller.add_stop_callback(mock_callback)
        self.assertIn(mock_callback, self.controller._stop_callbacks)
        
        # Remove callback
        self.controller.remove_stop_callback(mock_callback)
        self.assertNotIn(mock_callback, self.controller._stop_callbacks)


class TestConfirmationFlow(unittest.TestCase):
    """Test confirmation flow logic."""
    
    def test_deletion_summary_categories(self):
        """Test deletion summary has required categories."""
        summary = DeletionSummary()
        required_categories = ['Safe', 'Less Important', 'Important']
        
        for category in required_categories:
            self.assertIn(category, summary.categories)
            self.assertIn('count', summary.categories[category])
            self.assertIn('size', summary.categories[category])


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)