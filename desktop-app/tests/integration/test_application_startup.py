"""Integration tests for application startup and basic functionality."""

import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import threading
import time

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestApplicationStartup:
    """Test application startup and initialization."""
    
    def test_main_module_imports(self):
        """Test that main module imports successfully."""
        try:
            import main
            assert hasattr(main, 'main')
            assert hasattr(main, 'parse_arguments')
        except ImportError as e:
            pytest.fail(f"Failed to import main module: {e}")
    
    def test_argument_parsing(self):
        """Test command-line argument parsing."""
        import main
        
        # Test default arguments
        with patch('sys.argv', ['securewipe']):
            args = main.parse_arguments()
            assert args.debug is False
    
    def test_ui_components_import(self):
        """Test that UI components can be imported."""
        try:
            from ui.main_window import MainWindow
            assert MainWindow is not None
        except ImportError as e:
            pytest.fail(f"Failed to import UI components: {e}")
    
    def test_configuration_initialization(self):
        """Test configuration system initialization."""
        try:
            from config.settings import settings
            from config.defaults import get_user_config_dir, get_log_file_path
            
            # Test that configuration functions work
            config_dir = get_user_config_dir()
            assert isinstance(config_dir, Path)
            
            log_path = get_log_file_path()
            assert isinstance(log_path, Path)
            
            # Test settings access
            log_level = settings.get("log_level")
            assert log_level is not None
            
        except Exception as e:
            pytest.fail(f"Configuration initialization failed: {e}")
    
    def test_logging_setup(self):
        """Test logging system initialization."""
        try:
            from logging_setup import setup_application_logging, get_application_logger
            
            # Test logging setup
            logger = setup_application_logging(debug=True)
            assert logger is not None
            
            # Test component logger
            component_logger = get_application_logger("test.component", debug=True)
            assert component_logger is not None
            
        except Exception as e:
            pytest.fail(f"Logging setup failed: {e}")
    
    def test_directory_detector_integration(self):
        """Test directory detection integration."""
        try:
            from directory_detector import DirectoryDetector
            
            detector = DirectoryDetector(debug=True)
            summary = detector.get_directory_summary()
            
            # Verify summary structure
            assert isinstance(summary, dict)
            assert "platform" in summary
            assert "user_directories" in summary
            assert "accessible_count" in summary
            
        except Exception as e:
            pytest.fail(f"Directory detector integration failed: {e}")
    
    @pytest.mark.skipif(
        sys.platform.startswith('linux') and 'DISPLAY' not in os.environ,
        reason="No display available for GUI testing"
    )
    def test_main_window_creation(self):
        """Test main window can be created (requires display)."""
        try:
            # Import after display check
            import os
            from ui.main_window import MainWindow
            
            # Create window without running main loop
            window = MainWindow(debug=True)
            assert window is not None
            assert window.root is not None
            
            # Cleanup
            window.root.destroy()
            
        except Exception as e:
            pytest.fail(f"Main window creation failed: {e}")
    
    def test_cross_platform_paths(self):
        """Test cross-platform path handling."""
        from config.defaults import TEMP_DIRECTORIES
        import os
        
        # Test that platform-specific temp directories are defined
        if os.name == 'nt':
            assert "windows" in TEMP_DIRECTORIES
            windows_temps = TEMP_DIRECTORIES["windows"]
            assert len(windows_temps) > 0
        else:
            assert "linux" in TEMP_DIRECTORIES
            linux_temps = TEMP_DIRECTORIES["linux"]
            assert len(linux_temps) > 0