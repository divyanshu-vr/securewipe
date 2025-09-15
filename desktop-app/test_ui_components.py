#!/usr/bin/env python3
"""
Test script for individual UI components
"""

import sys
import os
import tkinter as tk
from tkinter import ttk
import threading
import time
import random

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_progress_dialog():
    """Test the progress dialog with simulated scanning"""
    from ui.progress_dialog import ProgressDialog
    
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    # Create progress dialog
    progress_dialog = ProgressDialog(root)
    
    def simulate_scan():
        """Simulate a file scanning process"""
        total_files = 150
        
        for i in range(total_files + 1):
            if not progress_dialog.winfo_exists():
                break
                
            # Simulate processing
            progress = (i / total_files) * 100
            files_processed = i
            
            # Simulate varying speed
            if i < total_files:
                speed = random.randint(5, 25)
                throughput = random.uniform(0.5, 5.0)
            else:
                # Test completion behavior - should show 0 speed/throughput
                speed = 0
                throughput = 0.0
            
            # Update progress
            progress_dialog.update_progress(
                progress=progress,
                current_file=f"Processing file_{i}.txt" if i < total_files else "Scan Complete",
                files_processed=files_processed,
                total_files=total_files,
                speed=speed,
                throughput=throughput
            )
            
            time.sleep(0.1)  # Simulate processing time
        
        # Keep dialog open for a moment to see completion state
        time.sleep(2)
        if progress_dialog.winfo_exists():
            progress_dialog.destroy()
    
    # Start simulation in background thread
    thread = threading.Thread(target=simulate_scan, daemon=True)
    thread.start()
    
    root.mainloop()

def test_scan_results_viewer():
    """Test the scan results viewer with mock data"""
    from ui.scan_results_viewer import ScanResultsViewer
    
    root = tk.Tk()
    root.title("Scan Results Viewer Test")
    root.geometry("1200x800")
    
    # Create mock results
    mock_results = {
        'Documents': [
            {'path': 'C:\\Users\\Test\\Documents\\report.pdf', 'size': 2048576, 'modified': '2024-01-15 10:30:00', 'category': 'Documents'},
            {'path': 'C:\\Users\\Test\\Documents\\notes.txt', 'size': 1024, 'modified': '2024-01-14 15:45:00', 'category': 'Documents'},
            {'path': 'C:\\Users\\Test\\Documents\\presentation.pptx', 'size': 5242880, 'modified': '2024-01-13 09:15:00', 'category': 'Documents'},
        ],
        'Images': [
            {'path': 'C:\\Users\\Test\\Pictures\\photo1.jpg', 'size': 3145728, 'modified': '2024-01-12 14:20:00', 'category': 'Images'},
            {'path': 'C:\\Users\\Test\\Pictures\\screenshot.png', 'size': 1572864, 'modified': '2024-01-11 11:30:00', 'category': 'Images'},
        ],
        'Videos': [
            {'path': 'C:\\Users\\Test\\Videos\\movie.mp4', 'size': 104857600, 'modified': '2024-01-10 16:45:00', 'category': 'Videos'},
        ],
        'Temporary': [
            {'path': 'C:\\Temp\\cache_file.tmp', 'size': 512000, 'modified': '2024-01-16 08:00:00', 'category': 'Temporary'},
            {'path': 'C:\\Temp\\old_log.log', 'size': 256000, 'modified': '2024-01-09 12:00:00', 'category': 'Temporary'},
        ]
    }
    
    # Create results viewer
    results_viewer = ScanResultsViewer(root)
    results_viewer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Display mock results
    results_viewer.display_results(mock_results)
    
    root.mainloop()

def test_both_components():
    """Test both progress dialog and results viewer in sequence"""
    print("Testing Progress Dialog first...")
    test_progress_dialog()
    
    print("Now testing Scan Results Viewer...")
    test_scan_results_viewer()

if __name__ == "__main__":
    print("UI Component Test Menu")
    print("1. Test Progress Dialog")
    print("2. Test Scan Results Viewer") 
    print("3. Test Both Components")
    
    choice = input("Enter choice (1-3): ").strip()
    
    try:
        if choice == "1":
            test_progress_dialog()
        elif choice == "2":
            test_scan_results_viewer()
        elif choice == "3":
            test_both_components()
        else:
            print("Invalid choice. Running full demo...")
            test_both_components()
    except Exception as e:
        print(f"Error running test: {e}")
        import traceback
        traceback.print_exc()