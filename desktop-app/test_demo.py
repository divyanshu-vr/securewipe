#!/usr/bin/env python3
"""
Demo test file to generate mock scan results for UI testing
"""

import sys
import os
from pathlib import Path
import random
from datetime import datetime

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui.scan_results_viewer import ScanResultsViewer
from scanner.file_scanner import FileScanner
import tkinter as tk
from tkinter import ttk

class MockFileScanner:
    """Mock file scanner that generates fake results instantly"""
    
    def __init__(self):
        self.categories = {
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff'],
            'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'Code': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.c'],
            'Executables': ['.exe', '.msi', '.deb', '.rpm', '.dmg', '.app'],
            'Temporary': ['.tmp', '.temp', '.cache', '.log', '.bak']
        }
        
        self.sample_names = [
            'project_report', 'vacation_photos', 'meeting_notes', 'backup_data',
            'presentation', 'music_collection', 'old_documents', 'downloads',
            'screenshots', 'work_files', 'personal_stuff', 'archive_2023',
            'temp_files', 'cache_data', 'log_files', 'system_backup'
        ]
    
    def generate_mock_results(self, num_files=100):
        """Generate mock scan results"""
        results = {}
        
        for category, extensions in self.categories.items():
            category_files = []
            num_category_files = random.randint(5, 20)
            
            for i in range(num_category_files):
                # Generate random file
                name = random.choice(self.sample_names)
                ext = random.choice(extensions)
                size = random.randint(1024, 100 * 1024 * 1024)  # 1KB to 100MB
                
                # Create fake path
                fake_path = f"C:\\Users\\TestUser\\{category}\\{name}_{i}{ext}"
                
                file_info = {
                    'path': fake_path,
                    'size': size,
                    'modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'category': category
                }
                
                category_files.append(file_info)
            
            if category_files:
                results[category] = category_files
        
        return results

def create_demo_window():
    """Create demo window with mock scan results"""
    root = tk.Tk()
    root.title("File Scanner Demo - Mock Results")
    root.geometry("1200x800")
    
    # Create mock scanner and results
    mock_scanner = MockFileScanner()
    mock_results = mock_scanner.generate_mock_results()
    
    # Calculate totals for display
    total_files = sum(len(files) for files in mock_results.values())
    total_size = sum(sum(f['size'] for f in files) for files in mock_results.values())
    
    # Create main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Add info label
    info_text = f"Demo Mode - Generated {total_files} mock files ({total_size / (1024*1024):.1f} MB total)"
    info_label = ttk.Label(main_frame, text=info_text, font=('Arial', 10, 'italic'))
    info_label.pack(pady=(0, 10))
    
    # Create scan results viewer with mock data
    results_viewer = ScanResultsViewer(main_frame)
    results_viewer.pack(fill=tk.BOTH, expand=True)
    
    # Load mock results
    results_viewer.display_results(mock_results)
    
    # Add refresh button to generate new mock data
    def refresh_demo():
        new_results = mock_scanner.generate_mock_results()
        results_viewer.display_results(new_results)
        new_total_files = sum(len(files) for files in new_results.values())
        new_total_size = sum(sum(f['size'] for f in files) for files in new_results.values())
        info_label.config(text=f"Demo Mode - Generated {new_total_files} mock files ({new_total_size / (1024*1024):.1f} MB total)")
    
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(10, 0))
    
    refresh_btn = ttk.Button(button_frame, text="Generate New Mock Data", command=refresh_demo)
    refresh_btn.pack(side=tk.LEFT)
    
    quit_btn = ttk.Button(button_frame, text="Quit Demo", command=root.quit)
    quit_btn.pack(side=tk.RIGHT)
    
    return root

if __name__ == "__main__":
    print("Starting File Scanner Demo with Mock Data...")
    print("This will show the scan results viewer with fake data for testing.")
    
    try:
        demo_window = create_demo_window()
        demo_window.mainloop()
    except Exception as e:
        print(f"Error running demo: {e}")
        import traceback
        traceback.print_exc()