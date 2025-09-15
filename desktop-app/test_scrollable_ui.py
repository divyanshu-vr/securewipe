#!/usr/bin/env python3
"""
Test script to verify the scrollable scan results viewer works correctly.
"""

import sys
import tkinter as tk
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    # Try different import methods
    try:
        from ui.scan_results_viewer import ScanResultsViewer
        from ui.modern_components import configure_modern_styles, ModernColors
    except ImportError:
        # If relative imports fail, try absolute imports
        import ui.scan_results_viewer as srv
        import ui.modern_components as mc
        ScanResultsViewer = srv.ScanResultsViewer
        configure_modern_styles = mc.configure_modern_styles
        ModernColors = mc.ModernColors
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the desktop-app directory")
    print("Try: cd desktop-app && python test_scrollable_ui.py")
    sys.exit(1)


class MockFileInfo:
    """Mock file info for testing."""
    def __init__(self, path, size=1024):
        self.path = Path(path)
        self.size = size


def test_scrollable_results():
    """Test the scrollable scan results viewer."""
    # Create main window (don't hide it)
    root = tk.Tk()
    root.title("Scrollable UI Test - Main Window")
    root.geometry("400x300")
    root.configure(bg=ModernColors.BACKGROUND)
    
    # Configure modern styling
    configure_modern_styles()
    
    # Add a button to launch the test
    test_button = tk.Button(
        root,
        text="🧪 Launch Scrollable Scan Results Test",
        font=("Segoe UI", 12),
        bg=ModernColors.PRIMARY,
        fg=ModernColors.PRIMARY_FOREGROUND,
        padx=20,
        pady=10,
        command=lambda: launch_scan_results(root)
    )
    test_button.pack(expand=True)
    
    # Instructions
    instructions = tk.Label(
        root,
        text="Click the button above to test the scrollable scan results viewer.\nThis will open a window with 200+ mock files to test scrolling.",
        font=("Segoe UI", 10),
        bg=ModernColors.BACKGROUND,
        fg=ModernColors.SECONDARY_TEXT,
        wraplength=350,
        justify="center"
    )
    instructions.pack(pady=20)
    
    print("🔄 Scrollable UI Test Ready!")
    print("✅ Click the button in the window to test scrollable functionality")
    
    root.mainloop()


def launch_scan_results(parent):
    """Launch the scan results viewer with mock data."""
    try:
        # Create mock scan results with lots of files
        mock_files = []
        for i in range(200):  # Create 200 mock files
            mock_files.append(MockFileInfo(f"C:/Users/Test/Documents/file_{i:03d}.txt", 1024 * (i + 1)))
        
        scan_results = {
            'total_files': len(mock_files),
            'categorized_files': {
                'Safe': mock_files[:150],  # Most files are safe
                'Less Important': mock_files[150:180],
                'Important': mock_files[180:195],
                'Protected': mock_files[195:]
            },
            'scan_summary': {
                'safe_count': 150,
                'less_important_count': 30,
                'important_count': 15,
                'protected_count': 5
            }
        }
        
        print("📊 Creating scan results viewer with 200 mock files...")
        print("🖱️ Use mouse wheel or scrollbar to scroll through content")
        print("🎯 Action buttons should remain visible at the bottom")
        
        # Create and show the scrollable results viewer
        viewer = ScanResultsViewer(parent, scan_results)
        result = viewer.show_results()
        
        if result:
            print(f"📋 User action: {result['action']}")
            if result['action'] == 'proceed' and result.get('selected_files'):
                print(f"🗑️ Selected {len(result['selected_files'])} files for deletion")
        else:
            print("❌ Dialog was closed without action")
            
    except Exception as e:
        print(f"❌ Error launching scan results: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_scrollable_results()