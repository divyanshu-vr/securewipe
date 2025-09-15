"""
Modern progress dialog with real-time updates and responsive UI.
Fixes all progress tracking and performance issues.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Callable, Optional, Dict, Any
from pathlib import Path

try:
    from .modern_components import (
        ModernCard, ModernProgressBar, ModernStats, ModernLogViewer,
        ModernColors, ModernButton, configure_modern_styles
    )
except ImportError:
    from modern_components import (
        ModernCard, ModernProgressBar, ModernStats, ModernLogViewer,
        ModernColors, ModernButton, configure_modern_styles
    )


class RealTimeProgressTracker:
    """Real-time progress tracking with thread-safe updates."""
    
    def __init__(self):
        self.total_files = 0
        self.processed_files = 0
        self.success_count = 0
        self.error_count = 0
        self.skipped_count = 0
        self.current_file = None
        self.current_directory = None
        self.current_operation = "Initializing..."
        self.start_time = time.time()
        self.bytes_processed = 0
        self.total_bytes = 0
        self._lock = threading.Lock()
    
    def update(self, **kwargs):
        """Thread-safe update of progress data."""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
    
    def get_snapshot(self) -> Dict[str, Any]:
        """Get thread-safe snapshot of current progress."""
        with self._lock:
            elapsed = time.time() - self.start_time
            
            # Ensure we don't have invalid values
            total_files = max(self.total_files, 1)
            processed_files = min(self.processed_files, total_files)  # Prevent over-counting
            
            # Calculate rates (only if we have meaningful elapsed time)
            if elapsed > 0.1:
                files_per_sec = processed_files / elapsed
                bytes_per_sec = self.bytes_processed / elapsed
            else:
                files_per_sec = 0
                bytes_per_sec = 0
            
            # Calculate progress percentage (cap at 100%, handle division by zero)
            if total_files > 0:
                progress_percentage = min((processed_files / total_files) * 100, 100.0)
            else:
                # During scanning phase, show activity even without known total
                progress_percentage = min(processed_files * 0.1, 50.0) if processed_files > 0 else 0.0
            
            # Calculate ETA
            remaining_files = max(total_files - processed_files, 0)
            if files_per_sec > 0 and remaining_files > 0:
                eta_seconds = remaining_files / files_per_sec
            else:
                eta_seconds = 0
            
            return {
                'total_files': total_files,
                'processed_files': processed_files,
                'success_count': self.success_count,
                'error_count': self.error_count,
                'skipped_count': self.skipped_count,
                'current_file': self.current_file,
                'current_directory': self.current_directory,
                'current_operation': self.current_operation,
                'progress_percentage': progress_percentage,
                'elapsed_time': elapsed,
                'files_per_sec': files_per_sec,
                'bytes_per_sec': bytes_per_sec,
                'eta_seconds': eta_seconds,
                'bytes_processed': self.bytes_processed,
                'total_bytes': self.total_bytes
            }


class ModernProgressDialog(tk.Toplevel):
    """Modern progress dialog with real-time updates and responsive UI."""
    
    def __init__(self, parent, title="SecureWipe Progress", **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configure window
        self.title(title)
        self.geometry("700x600")
        self.resizable(True, True)
        self.minsize(600, 500)
        
        # Configure modern styling
        configure_modern_styles()
        self.configure(bg=ModernColors.BACKGROUND)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Progress tracking
        self.progress_tracker = RealTimeProgressTracker()
        self.update_thread = None
        self.is_running = False
        self.is_cancelled = False
        
        # Callbacks
        self.cancel_callback = None
        self.pause_callback = None
        
        # UI update frequency (60 FPS for smooth updates)
        self.update_interval = 16  # ~60 FPS
        
        self._setup_ui()
        self._center_window()
        
        # Start UI update loop
        self._start_ui_updates()
    
    def _setup_ui(self):
        """Setup the modern UI layout."""
        # Main container with padding
        main_frame = ttk.Frame(self, padding="24")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header section
        self._create_header(main_frame)
        
        # Progress section
        self._create_progress_section(main_frame)
        
        # Statistics section
        self._create_stats_section(main_frame)
        
        # Current operation section
        self._create_operation_section(main_frame)
        
        # Log section
        self._create_log_section(main_frame)
        
        # Control buttons
        self._create_controls(main_frame)
    
    def _create_header(self, parent):
        """Create the header section."""
        header_card = ModernCard(parent, title="Secure File Deletion")
        header_card.pack(fill=tk.X, pady=(0, 16))
        
        # Phase indicators
        phase_frame = ttk.Frame(header_card.content)
        phase_frame.pack(fill=tk.X, pady=(8, 0))
        
        self.phases = {
            'scan': {'label': '🔍 Scanning', 'active': False},
            'categorize': {'label': '📂 Categorizing', 'active': False},
            'delete': {'label': '🗑️ Deleting', 'active': False},
            'complete': {'label': '✅ Complete', 'active': False}
        }
        
        self.phase_labels = {}
        for i, (phase, data) in enumerate(self.phases.items()):
            label = ttk.Label(phase_frame, text=data['label'], 
                             font=("Segoe UI", 10),
                             foreground=ModernColors.MUTED_FOREGROUND)
            label.grid(row=0, column=i, padx=(0, 20), sticky="w")
            self.phase_labels[phase] = label
        
        phase_frame.grid_columnconfigure(3, weight=1)
    
    def _create_progress_section(self, parent):
        """Create the progress bar section."""
        progress_card = ModernCard(parent, title="Overall Progress")
        progress_card.pack(fill=tk.X, pady=(0, 16))
        
        # Main progress bar
        self.progress_bar = ModernProgressBar(progress_card.content, width=600, height=12)
        self.progress_bar.pack(fill=tk.X, pady=(8, 4))
        
        # Progress percentage
        self.progress_label = ttk.Label(progress_card.content, text="0%", 
                                       font=("Segoe UI", 14, "bold"),
                                       style="Modern.TLabel")
        self.progress_label.pack(pady=(4, 0))
    
    def _create_stats_section(self, parent):
        """Create the statistics section."""
        stats_card = ModernCard(parent, title="Statistics")
        stats_card.pack(fill=tk.X, pady=(0, 16))
        
        self.stats = ModernStats(stats_card.content)
        self.stats.pack(fill=tk.X, pady=(8, 0))
        
        # Add statistics
        self.stats.add_stat('files', 'Files Processed', '0 / 0', row=0, column=0)
        self.stats.add_stat('success', 'Successful', '0', 'success', row=0, column=1)
        self.stats.add_stat('errors', 'Errors', '0', 'error', row=0, column=2)
        
        self.stats.add_stat('speed', 'Processing Speed', '0 files/sec', row=1, column=0)
        self.stats.add_stat('throughput', 'Data Throughput', '0 MB/sec', row=1, column=1)
        self.stats.add_stat('eta', 'Time Remaining', 'Calculating...', row=1, column=2)
    
    def _create_operation_section(self, parent):
        """Create the current operation section."""
        operation_card = ModernCard(parent, title="Current Operation")
        operation_card.pack(fill=tk.X, pady=(0, 16))
        
        # Current file
        self.current_file_var = tk.StringVar(value="Ready to begin...")
        current_file_label = ttk.Label(operation_card.content, 
                                      textvariable=self.current_file_var,
                                      font=("Segoe UI", 10),
                                      style="Modern.TLabel",
                                      wraplength=600)
        current_file_label.pack(anchor=tk.W, pady=(8, 4))
        
        # Current operation
        self.current_op_var = tk.StringVar(value="Initializing...")
        current_op_label = ttk.Label(operation_card.content, 
                                    textvariable=self.current_op_var,
                                    font=("Segoe UI", 9),
                                    foreground=ModernColors.MUTED_FOREGROUND)
        current_op_label.pack(anchor=tk.W)
    
    def _create_log_section(self, parent):
        """Create the log viewer section."""
        log_card = ModernCard(parent, title="Operation Log")
        log_card.pack(fill=tk.BOTH, expand=True, pady=(0, 16))
        
        self.log_viewer = ModernLogViewer(log_card.content)
        self.log_viewer.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
    
    def _create_controls(self, parent):
        """Create control buttons."""
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X)
        
        # Left side buttons
        left_frame = tk.Frame(controls_frame, bg=ModernColors.BACKGROUND)
        left_frame.pack(side=tk.LEFT)
        
        self.pause_button = ModernButton(left_frame, text="⏸️ Pause", 
                                        variant="secondary", size="md",
                                        command=self._on_pause)
        self.pause_button.configure(state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.cancel_button = ModernButton(left_frame, text="❌ Cancel", 
                                         variant="destructive", size="md",
                                         command=self._on_cancel)
        self.cancel_button.configure(state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT)
        
        # Right side buttons
        right_frame = tk.Frame(controls_frame, bg=ModernColors.BACKGROUND)
        right_frame.pack(side=tk.RIGHT)
        
        self.close_button = ModernButton(right_frame, text="✅ Close", 
                                        variant="primary", size="md",
                                        command=self._on_close)
        self.close_button.configure(state=tk.DISABLED)
        self.close_button.pack()
    
    def _center_window(self):
        """Center the dialog on the parent window."""
        self.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width - self.winfo_width()) // 2
        y = parent_y + (parent_height - self.winfo_height()) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def _start_ui_updates(self):
        """Start the UI update loop."""
        self._update_ui()
    
    def _update_ui(self):
        """Update UI elements with current progress data."""
        try:
            # Get current progress snapshot
            progress = self.progress_tracker.get_snapshot()
            
            # Update progress bar
            self.progress_bar.set_progress(progress['progress_percentage'])
            self.progress_label.config(text=f"{progress['progress_percentage']:.1f}%")
            
            # Update statistics
            if progress['total_files'] > 0 and progress['processed_files'] <= progress['total_files']:
                # Normal progress with known total
                self.stats.update_stat('files', 
                                      f"{progress['processed_files']:,} / {progress['total_files']:,}")
            else:
                # Scanning phase - show files found so far
                self.stats.update_stat('files', 
                                      f"{progress['processed_files']:,} found")
            
            self.stats.update_stat('success', f"{progress['success_count']:,}", 'success')
            self.stats.update_stat('errors', f"{progress['error_count']:,}", 
                                  'error' if progress['error_count'] > 0 else 'default')
            
            # Format speed (reset to 0 when complete)
            if progress['progress_percentage'] >= 100.0:
                speed = "0 files/sec"
                throughput = "0 MB/sec"
            else:
                speed = f"{progress['files_per_sec']:.1f} files/sec"
                throughput_mb = progress['bytes_per_sec'] / (1024 * 1024)
                throughput = f"{throughput_mb:.1f} MB/sec"
            
            self.stats.update_stat('speed', speed)
            self.stats.update_stat('throughput', throughput)
            
            # Format ETA (show "Complete" when done)
            if progress['progress_percentage'] >= 100.0:
                eta = "Complete"
            else:
                eta_seconds = progress['eta_seconds']
                if eta_seconds > 0:
                    if eta_seconds < 60:
                        eta = f"{eta_seconds:.0f}s"
                    elif eta_seconds < 3600:
                        eta = f"{eta_seconds/60:.1f}m"
                    else:
                        eta = f"{eta_seconds/3600:.1f}h"
                else:
                    eta = "Calculating..."
            self.stats.update_stat('eta', eta)
            
            # Update current operation
            if progress['current_file']:
                file_name = Path(progress['current_file']).name
                if len(file_name) > 60:
                    file_name = file_name[:57] + "..."
                self.current_file_var.set(f"Processing: {file_name}")
            elif progress.get('current_directory'):
                # Show current directory during scanning
                dir_name = Path(str(progress['current_directory'])).name
                if len(dir_name) > 60:
                    dir_name = dir_name[:57] + "..."
                self.current_file_var.set(f"Scanning: {dir_name}")
            else:
                self.current_file_var.set("Scanning directories...")
            
            self.current_op_var.set(progress['current_operation'])
            
            # Update phase indicators
            self._update_phase_indicators(progress['progress_percentage'])
            
        except Exception as e:
            if hasattr(self, 'log_viewer'):
                self.log_viewer.add_log(f"UI update error: {str(e)}", "error")
        
        # Schedule next update only if dialog still exists
        try:
            if self.winfo_exists():
                self.after(self.update_interval, self._update_ui)
        except tk.TclError:
            # Dialog has been destroyed
            pass
    
    def _update_phase_indicators(self, progress_percentage: float):
        """Update phase indicators based on progress."""
        # Reset all phases
        for phase, label in self.phase_labels.items():
            label.config(foreground=ModernColors.MUTED_FOREGROUND)
        
        # Activate phases based on progress
        if progress_percentage >= 0:
            self.phase_labels['scan'].config(foreground=ModernColors.INFO)
        if progress_percentage >= 25:
            self.phase_labels['scan'].config(foreground=ModernColors.SUCCESS)
            self.phase_labels['categorize'].config(foreground=ModernColors.INFO)
        if progress_percentage >= 50:
            self.phase_labels['categorize'].config(foreground=ModernColors.SUCCESS)
            self.phase_labels['delete'].config(foreground=ModernColors.INFO)
        if progress_percentage >= 100:
            self.phase_labels['delete'].config(foreground=ModernColors.SUCCESS)
            self.phase_labels['complete'].config(foreground=ModernColors.SUCCESS)
    
    def start_operation(self, total_files: int = 0, cancel_callback: Optional[Callable] = None):
        """Start monitoring an operation."""
        self.is_running = True
        self.is_cancelled = False
        self.cancel_callback = cancel_callback
        
        # Initialize progress
        self.progress_tracker.update(
            total_files=total_files,
            start_time=time.time()
        )
        
        # Enable controls
        self.pause_button.configure(state=tk.NORMAL)
        self.cancel_button.configure(state=tk.NORMAL)
        
        self.log_viewer.add_log("Operation started", "info")
    
    def update_progress(self, **kwargs):
        """Update progress data (thread-safe)."""
        self.progress_tracker.update(**kwargs)
        
        # Force immediate UI update for responsiveness
        try:
            self.after_idle(self._update_ui_immediate)
        except tk.TclError:
            # Dialog destroyed, ignore
            pass
    
    def _update_ui_immediate(self):
        """Immediate UI update for responsive progress."""
        try:
            if self.winfo_exists():
                progress = self.progress_tracker.get_snapshot()
                
                # Update only the most critical elements for responsiveness
                self.progress_bar.set_progress(progress['progress_percentage'])
                self.progress_label.config(text=f"{progress['progress_percentage']:.1f}%")
                
                # Update current operation (show completion when done)
                if progress['progress_percentage'] >= 100.0:
                    self.current_file_var.set("Processing complete")
                    self.current_op_var.set("All files processed successfully")
                else:
                    if progress['current_file']:
                        file_name = Path(progress['current_file']).name
                        if len(file_name) > 60:
                            file_name = file_name[:57] + "..."
                        self.current_file_var.set(f"Processing: {file_name}")
                    
                    self.current_op_var.set(progress['current_operation'])
        except Exception:
            # Ignore errors during immediate updates
            pass
    
    def add_log(self, message: str, level: str = "info"):
        """Add a log message."""
        self.log_viewer.add_log(message, level)
    
    def complete_operation(self):
        """Mark operation as complete."""
        self.is_running = False
        
        # Update progress to 100% to trigger completion state
        self.progress_tracker.update(
            processed_files=self.progress_tracker.total_files,
            current_operation="Operation completed"
        )
        
        # Update UI
        self.progress_bar.set_progress(100.0)
        self.progress_label.config(text="100%")
        self.current_file_var.set("Processing complete")
        self.current_op_var.set("Operation completed successfully")
        
        # Reset speed and throughput statistics
        self.stats.update_stat('speed', "0 files/sec")
        self.stats.update_stat('throughput', "0 MB/sec")
        self.stats.update_stat('eta', "Complete")
        
        # Update controls
        self.pause_button.configure(state=tk.DISABLED)
        self.cancel_button.configure(state=tk.DISABLED)
        self.close_button.configure(state=tk.NORMAL)
        
        self.add_log("Operation completed successfully", "success")
    
    def _on_pause(self):
        """Handle pause button."""
        if self.pause_callback:
            self.pause_callback()
        self.add_log("Operation paused by user", "warning")
    
    def _on_cancel(self):
        """Handle cancel button."""
        self.is_cancelled = True
        if self.cancel_callback:
            self.cancel_callback()
        self.add_log("Operation cancelled by user", "warning")
        self._on_close()
    
    def _on_close(self):
        """Handle close button."""
        self.destroy()