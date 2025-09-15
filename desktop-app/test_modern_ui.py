#!/usr/bin/env python3
"""
Test script for the modern UI components.
Run this to see the new modern interface in action.
"""

import sys
import tkinter as tk
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ui.modern_components import (
    ModernCard, ModernProgressBar, ModernStats, ModernLogViewer,
    configure_modern_styles, ModernColors
)


def test_modern_components():
    """Test the modern UI components."""
    
    # Create main window
    root = tk.Tk()
    root.title("SecureWipe - Modern UI Test")
    root.geometry("800x600")
    root.configure(bg=ModernColors.BACKGROUND)
    
    # Configure modern styles
    configure_modern_styles()
    
    # Main container
    main_frame = tk.Frame(root, bg=ModernColors.BACKGROUND, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title_label = tk.Label(main_frame, text="SecureWipe Modern UI", 
                          font=("Segoe UI", 20, "bold"),
                          bg=ModernColors.BACKGROUND,
                          fg=ModernColors.FOREGROUND)
    title_label.pack(pady=(0, 20))
    
    # Progress card
    progress_card = ModernCard(main_frame, title="Progress")
    progress_card.pack(fill=tk.X, pady=(0, 16))
    
    progress_bar = ModernProgressBar(progress_card.content, width=600)
    progress_bar.pack(fill=tk.X, pady=(8, 0))
    
    # Animate progress
    def animate_progress():
        for i in range(101):
            progress_bar.set_progress(i)
            root.update()
            root.after(50)  # 50ms delay
    
    # Stats card
    stats_card = ModernCard(main_frame, title="Statistics")
    stats_card.pack(fill=tk.X, pady=(0, 16))
    
    stats = ModernStats(stats_card.content)
    stats.pack(fill=tk.X, pady=(8, 0))
    
    stats.add_stat('files', 'Files Processed', '1,234', row=0, column=0)
    stats.add_stat('success', 'Successful', '1,200', 'success', row=0, column=1)
    stats.add_stat('errors', 'Errors', '34', 'error', row=0, column=2)
    
    # Log card
    log_card = ModernCard(main_frame, title="Operation Log")
    log_card.pack(fill=tk.BOTH, expand=True, pady=(0, 16))
    
    log_viewer = ModernLogViewer(log_card.content)
    log_viewer.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
    
    # Add some sample log entries
    log_viewer.add_log("Application started", "info")
    log_viewer.add_log("Scanning directories...", "info")
    log_viewer.add_log("Found 1,234 files", "success")
    log_viewer.add_log("Processing file: document.pdf", "info")
    log_viewer.add_log("File deleted successfully", "success")
    log_viewer.add_log("Permission denied for system file", "warning")
    log_viewer.add_log("Critical error in deletion engine", "error")
    
    # Control buttons
    button_frame = tk.Frame(main_frame, bg=ModernColors.BACKGROUND)
    button_frame.pack(fill=tk.X)
    
    tk.Button(button_frame, text="Animate Progress", 
             command=animate_progress,
             bg=ModernColors.PRIMARY, fg=ModernColors.PRIMARY_FOREGROUND,
             font=("Segoe UI", 9), padx=16, pady=8).pack(side=tk.LEFT)
    
    tk.Button(button_frame, text="Add Log Entry", 
             command=lambda: log_viewer.add_log("New operation completed", "success"),
             bg=ModernColors.SUCCESS, fg="#ffffff",
             font=("Segoe UI", 9), padx=16, pady=8).pack(side=tk.LEFT, padx=(8, 0))
    
    tk.Button(button_frame, text="Close", 
             command=root.quit,
             bg=ModernColors.SECONDARY, fg=ModernColors.SECONDARY_FOREGROUND,
             font=("Segoe UI", 9), padx=16, pady=8).pack(side=tk.RIGHT)
    
    # Start the application
    root.mainloop()


if __name__ == "__main__":
    test_modern_components()