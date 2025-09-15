#!/usr/bin/env python3
"""Test script for the modern progress bar functionality."""

import sys
import time
import tkinter as tk
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ui.modern_progress_dialog import ModernProgressDialog
from src.ui.modern_components import configure_modern_styles


def test_progress_bar():
    """Test the modern progress bar with simulated progress."""
    
    # Create root window
    root = tk.Tk()
    root.title("Progress Bar Test")
    root.geometry("400x300")
    
    # Configure modern styles
    configure_modern_styles()
    
    def start_test():
        """Start the progress test."""
        # Create progress dialog
        progress_dialog = ModernProgressDialog(
            root, 
            title="Testing Progress Bar"
        )
        
        # Start operation
        progress_dialog.start_operation(
            total_files=1000,
            cancel_callback=lambda: print("Cancelled!")
        )
        
        # Simulate progress updates
        def simulate_progress():
            for i in range(101):
                if not progress_dialog.winfo_exists():
                    break
                
                # Update progress
                progress_dialog.update_progress(
                    processed_files=i * 10,
                    current_file=f"test_file_{i}.txt",
                    current_operation=f"Processing file {i}...",
                    bytes_processed=i * 1024 * 1024,
                    success_count=i * 9,
                    error_count=i // 10
                )
                
                # Add some log messages
                if i % 20 == 0:
                    progress_dialog.add_log(f"Milestone: {i}% complete", "info")
                
                if i % 50 == 0 and i > 0:
                    progress_dialog.add_log(f"Major progress: {i}% done", "success")
                
                # Wait a bit
                time.sleep(0.1)
            
            # Complete the operation
            if progress_dialog.winfo_exists():
                progress_dialog.complete_operation()
                progress_dialog.add_log("Test completed successfully!", "success")
        
        # Start simulation in a thread
        import threading
        thread = threading.Thread(target=simulate_progress, daemon=True)
        thread.start()
    
    # Create test button
    test_button = tk.Button(root, text="Test Progress Bar", command=start_test)
    test_button.pack(pady=50)
    
    # Create info label
    info_label = tk.Label(root, text="Click the button to test the progress bar.\nWatch for smooth updates and accurate statistics.")
    info_label.pack(pady=20)
    
    # Run the test
    root.mainloop()


if __name__ == "__main__":
    test_progress_bar()