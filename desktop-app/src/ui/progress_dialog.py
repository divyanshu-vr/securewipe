"""Gaming-inspired progress dialog for secure deletion operations."""

import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared"))

from shared.models.operation_result import OperationResult, OperationStatus
from deletion.progress_tracker import ProgressInfo, ProgressState, ProgressTracker
from ui.components.statistics_tracker import StatisticsTracker, OperationStatistics
from ui.components.thread_safe_ui import ThreadSafeUIManager, UIUpdateType, BackgroundOperationManager


class GameProgressBar(tk.Canvas):
    """Gaming-style XP bar progress indicator."""
    
    def __init__(self, parent, width=400, height=30, **kwargs):
        super().__init__(parent, width=width, height=height, bg='#2c2c2c', highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.progress = 0.0
        self._setup_bar()
    
    def _setup_bar(self):
        """Setup the XP bar visual elements."""
        # Background bar
        self.create_rectangle(2, 2, self.width-2, self.height-2, 
                            fill='#1a1a1a', outline='#555555', width=2)
        
        # Progress fill (will be updated)
        self.progress_rect = self.create_rectangle(4, 4, 4, self.height-4, 
                                                 fill='#00ff88', outline='')
        
        # Shine effect
        self.create_rectangle(4, 4, self.width-4, 8, 
                            fill='#ffffff', stipple='gray25', outline='')
    
    def set_progress(self, percentage: float):
        """Update progress bar (0.0 to 100.0)."""
        self.progress = max(0.0, min(100.0, percentage))
        fill_width = max(0, int((self.width - 8) * (self.progress / 100.0)))
        
        # Update progress rectangle
        self.coords(self.progress_rect, 4, 4, 4 + fill_width, self.height - 4)
        
        # Color based on progress
        if self.progress < 30:
            color = '#ff4444'  # Red for low progress
        elif self.progress < 70:
            color = '#ffaa00'  # Orange for medium progress
        else:
            color = '#00ff88'  # Green for high progress
        
        self.itemconfig(self.progress_rect, fill=color)


class MilestoneIndicator(ttk.Frame):
    """Checkpoint-style milestone indicators."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.milestones = {}
        self._setup_milestones()
    
    def _setup_milestones(self):
        """Setup milestone checkpoints."""
        milestones = [
            ("scan", "Scanning Files", "🔍"),
            ("categorize", "Categorizing", "📂"),
            ("delete", "Deleting Files", "🗑️"),
            ("complete", "Complete", "✅")
        ]
        
        for i, (key, label, icon) in enumerate(milestones):
            frame = ttk.Frame(self)
            frame.pack(side=tk.LEFT, padx=10, pady=5)
            
            # Icon label
            try:
                bg_color = self.cget('background')
            except tk.TclError:
                bg_color = 'white'  # Fallback for testing
            
            icon_label = tk.Label(frame, text=icon, font=('Arial', 16), bg=bg_color)
            icon_label.pack()
            
            # Text label
            text_label = ttk.Label(frame, text=label, font=('Arial', 8))
            text_label.pack()
            
            self.milestones[key] = {
                'frame': frame,
                'icon': icon_label,
                'text': text_label,
                'completed': False
            }
    
    def set_milestone(self, milestone: str, completed: bool = True):
        """Mark a milestone as completed or active."""
        if milestone in self.milestones:
            milestone_data = self.milestones[milestone]
            if completed:
                milestone_data['icon'].config(fg='#00aa00')  # Green
                milestone_data['text'].config(foreground='#00aa00')
            else:
                milestone_data['icon'].config(fg='#0066cc')  # Blue (active)
                milestone_data['text'].config(foreground='#0066cc')
            milestone_data['completed'] = completed


class ProgressDialog(tk.Toplevel):
    """Main progress dialog with gaming-inspired elements."""
    
    def __init__(self, parent, title="Secure Deletion Progress", **kwargs):
        super().__init__(parent, **kwargs)
        self.title(title)
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Make dialog modal (skip in testing)
        self.transient(parent)
        try:
            self.grab_set()
        except tk.TclError:
            # Skip grab in testing environment
            pass
        
        # Progress tracking
        self.progress_tracker = None
        self.statistics_tracker = StatisticsTracker()
        self.update_thread = None
        self.is_running = False
        
        # Enhanced operation logging with detailed history
        self.operation_log = []  # List of (timestamp, level, message, details) tuples
        self.operation_history = []  # Historical operations for session
        self.max_log_entries = 10000  # Prevent memory issues with very long operations
        
        # Thread-safe UI management
        self.ui_manager = ThreadSafeUIManager(self)
        self.operation_manager = BackgroundOperationManager(self.ui_manager)
        self._setup_ui_handlers()
        
        # Callbacks
        self.cancel_callback = None
        self.pause_callback = None
        self.resume_callback = None
        
        self._setup_ui()
        self._center_window()
    
    def _setup_ui_handlers(self):
        """Setup thread-safe UI update handlers."""
        # Register handlers for different update types
        self.ui_manager.register_handler(
            UIUpdateType.PROGRESS_UPDATE, 
            self._handle_progress_update
        )
        self.ui_manager.register_handler(
            UIUpdateType.STATUS_MESSAGE, 
            self._handle_status_message
        )
        self.ui_manager.register_handler(
            UIUpdateType.PHASE_CHANGE, 
            self._handle_phase_change
        )
        self.ui_manager.register_handler(
            UIUpdateType.STATISTICS_UPDATE, 
            self._handle_statistics_update
        )
        self.ui_manager.register_handler(
            UIUpdateType.OPERATION_COMPLETE, 
            self._handle_operation_complete
        )
        self.ui_manager.register_handler(
            UIUpdateType.ERROR_OCCURRED, 
            self._handle_error
        )
        
        # Start UI update processing
        self.ui_manager.start_ui_updates()
    
    def _setup_ui(self):
        """Setup the complete UI."""
        # Main container
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Secure File Deletion", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Milestone indicators
        self.milestone_indicator = MilestoneIndicator(main_frame)
        self.milestone_indicator.pack(fill=tk.X, pady=(0, 20))
        
        # Main progress bar (gaming style)
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.game_progress = GameProgressBar(progress_frame)
        self.game_progress.pack(fill=tk.X)
        
        # Progress percentage
        self.progress_label = ttk.Label(progress_frame, text="0%", 
                                       font=('Arial', 12, 'bold'))
        self.progress_label.pack(pady=(5, 0))
        
        # Current status
        status_frame = ttk.LabelFrame(main_frame, text="Current Operation", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.current_file_var = tk.StringVar(value="Ready to begin...")
        self.current_file_label = ttk.Label(status_frame, textvariable=self.current_file_var,
                                           font=('Arial', 10))
        self.current_file_label.pack(fill=tk.X)
        
        self.phase_var = tk.StringVar(value="Initializing")
        self.phase_label = ttk.Label(status_frame, textvariable=self.phase_var,
                                    font=('Arial', 9), foreground='#666666')
        self.phase_label.pack(fill=tk.X, pady=(5, 0))
        
        # Statistics dashboard
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Stats grid
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # Files processed
        ttk.Label(stats_grid, text="Files:").grid(row=0, column=0, sticky=tk.W)
        self.files_var = tk.StringVar(value="0 / 0")
        ttk.Label(stats_grid, textvariable=self.files_var).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Success count
        ttk.Label(stats_grid, text="Success:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.success_var = tk.StringVar(value="0")
        success_label = ttk.Label(stats_grid, textvariable=self.success_var, foreground='#00aa00')
        success_label.grid(row=0, column=3, sticky=tk.W, padx=(10, 0))
        
        # Error count
        ttk.Label(stats_grid, text="Errors:").grid(row=1, column=0, sticky=tk.W)
        self.errors_var = tk.StringVar(value="0")
        error_label = ttk.Label(stats_grid, textvariable=self.errors_var, foreground='#cc0000')
        error_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Time remaining
        ttk.Label(stats_grid, text="Time left:").grid(row=1, column=2, sticky=tk.W, padx=(20, 0))
        self.time_var = tk.StringVar(value="Calculating...")
        ttk.Label(stats_grid, textvariable=self.time_var).grid(row=1, column=3, sticky=tk.W, padx=(10, 0))
        
        # Processing speed
        ttk.Label(stats_grid, text="Speed:").grid(row=2, column=0, sticky=tk.W)
        self.speed_var = tk.StringVar(value="0 files/sec")
        ttk.Label(stats_grid, textvariable=self.speed_var).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Data throughput
        ttk.Label(stats_grid, text="Throughput:").grid(row=2, column=2, sticky=tk.W, padx=(20, 0))
        self.throughput_var = tk.StringVar(value="0 MB/sec")
        ttk.Label(stats_grid, textvariable=self.throughput_var).grid(row=2, column=3, sticky=tk.W, padx=(10, 0))
        
        # Detailed log section
        log_frame = ttk.LabelFrame(main_frame, text="Operation Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Log text with scrollbar
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_container, height=8, wrap=tk.WORD, 
                               font=('Consolas', 9), state=tk.DISABLED)
        log_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enhanced log filter options with operation history
        filter_frame = ttk.Frame(log_frame)
        filter_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Filter checkboxes
        filter_left = ttk.Frame(filter_frame)
        filter_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.show_all_var = tk.BooleanVar(value=True)
        self.show_errors_var = tk.BooleanVar(value=False)
        self.show_success_var = tk.BooleanVar(value=False)
        self.show_warnings_var = tk.BooleanVar(value=True)
        self.show_info_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(filter_left, text="All", variable=self.show_all_var,
                       command=self._update_log_filter).pack(side=tk.LEFT)
        ttk.Checkbutton(filter_left, text="Info", variable=self.show_info_var,
                       command=self._update_log_filter).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Checkbutton(filter_left, text="Success", variable=self.show_success_var,
                       command=self._update_log_filter).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Checkbutton(filter_left, text="Warnings", variable=self.show_warnings_var,
                       command=self._update_log_filter).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Checkbutton(filter_left, text="Errors", variable=self.show_errors_var,
                       command=self._update_log_filter).pack(side=tk.LEFT, padx=(5, 0))
        
        # Log controls
        filter_right = ttk.Frame(filter_frame)
        filter_right.pack(side=tk.RIGHT)
        
        ttk.Button(filter_right, text="Clear Log", 
                  command=self._clear_log).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(filter_right, text="Save Log", 
                  command=self._save_log).pack(side=tk.RIGHT)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.pause_button = ttk.Button(button_frame, text="Pause", 
                                      command=self._on_pause, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT)
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", 
                                       command=self._on_cancel, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=(10, 0))
        
        self.close_button = ttk.Button(button_frame, text="Close", 
                                      command=self._on_close, state=tk.DISABLED)
        self.close_button.pack(side=tk.RIGHT)
        
        # Export log button
        self.export_button = ttk.Button(button_frame, text="Export Log", 
                                       command=self._export_log, state=tk.DISABLED)
        self.export_button.pack(side=tk.RIGHT, padx=(0, 10))
    
    def start_operation(self, progress_tracker: ProgressTracker, 
                       cancel_callback: Optional[Callable] = None,
                       pause_callback: Optional[Callable] = None,
                       resume_callback: Optional[Callable] = None):
        """Start monitoring a deletion operation."""
        self.progress_tracker = progress_tracker
        self.cancel_callback = cancel_callback
        self.pause_callback = pause_callback
        self.resume_callback = resume_callback
        
        self.is_running = True
        self.operation_log.clear()
        
        # Enable controls
        self.pause_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.NORMAL)
        
        # Initialize statistics tracking
        progress_info = self.progress_tracker.get_progress_info()
        self.statistics_tracker.start_operation(
            total_files=progress_info.total_files,
            total_bytes=progress_info.total_bytes
        )
        
        # Set initial milestone
        self.milestone_indicator.set_milestone('scan', False)
        
        # Start update thread
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        self._log_message("Operation started", "INFO")
    
    def start_background_operation(self, operation_func: Callable, *args, **kwargs):
        """Start a background operation using thread-safe UI management."""
        self.is_running = True
        
        # Enable controls
        self.pause_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.NORMAL)
        
        # Clear operation log
        self.operation_log.clear()
        
        # Initialize statistics tracking
        if self.progress_tracker:
            progress_info = self.progress_tracker.get_progress_info()
            self.statistics_tracker.start_operation(
                total_files=progress_info.total_files,
                total_bytes=progress_info.total_bytes
            )
        
        # Set initial milestone
        self.milestone_indicator.set_milestone('scan', False)
        
        # Start background operation using thread-safe manager
        self.operation_manager.start_operation(operation_func, *args, **kwargs)
    
    def _update_loop(self):
        """Background thread for updating progress."""
        while self.is_running and self.progress_tracker:
            try:
                progress_info = self.progress_tracker.get_progress_info()
                
                # Schedule UI update on main thread
                self.after(0, self._update_ui, progress_info)
                
                # Check if operation is complete
                if progress_info.state in [ProgressState.COMPLETED, ProgressState.CANCELLED]:
                    self.after(0, self._operation_finished, progress_info.state)
                    break
                
                time.sleep(0.1)  # 100ms update interval
                
            except Exception as e:
                self.after(0, self._log_message, f"Update error: {str(e)}", "ERROR")
                break
    
    def _update_ui(self, progress_info: ProgressInfo):
        """Update UI elements with current progress and enhanced statistics."""
        # Update statistics tracker
        if progress_info.current_file:
            self.statistics_tracker.update_current_file(progress_info.current_file)
        
        # Simulate file completion for statistics (in real implementation, this would be called from deletion engine)
        if progress_info.processed_files > 0:
            self.statistics_tracker.file_completed(
                success=(progress_info.success_count > 0),
                file_size=1024  # Placeholder size
            )
        
        # Get enhanced statistics
        stats = self.statistics_tracker.get_statistics()
        time_estimates = self.statistics_tracker.get_time_estimates()
        performance = self.statistics_tracker.get_performance_summary()
        
        # Update progress bar
        percentage = (progress_info.processed_files / max(1, progress_info.total_files)) * 100
        self.game_progress.set_progress(percentage)
        self.progress_label.config(text=f"{percentage:.1f}%")
        
        # Update current file with enhanced context
        if progress_info.current_file:
            file_name = progress_info.current_file.name
            if len(file_name) > 50:
                file_name = file_name[:47] + "..."
            
            # Add file size if available
            try:
                file_size = progress_info.current_file.stat().st_size
                size_str = self._format_file_size(file_size)
                self.current_file_var.set(f"Processing: {file_name} ({size_str})")
            except:
                self.current_file_var.set(f"Processing: {file_name}")
        else:
            self.current_file_var.set("Processing files...")
        
        # Update phase based on progress with enhanced milestones
        if percentage < 1:
            phase = "Initializing deletion process"
            self.milestone_indicator.set_milestone('scan', False)
            self.statistics_tracker.set_phase("initializing")
        elif percentage < 10:
            phase = "Analyzing files for deletion"
            self.milestone_indicator.set_milestone('scan', False)
            self.statistics_tracker.set_phase("scanning")
        elif percentage < 20:
            phase = "Categorizing files by priority"
            self.milestone_indicator.set_milestone('scan', True)
            self.milestone_indicator.set_milestone('categorize', False)
            self.statistics_tracker.set_phase("categorizing")
        elif percentage < 95:
            phase = "Securely deleting files"
            self.milestone_indicator.set_milestone('categorize', True)
            self.milestone_indicator.set_milestone('delete', False)
            self.statistics_tracker.set_phase("deleting")
        else:
            phase = "Finalizing operation"
            self.milestone_indicator.set_milestone('delete', True)
            self.statistics_tracker.set_phase("finalizing")
        
        self.phase_var.set(phase)
        
        # Update enhanced statistics
        remaining = progress_info.total_files - progress_info.processed_files
        self.files_var.set(f"{progress_info.processed_files:,} / {progress_info.total_files:,} ({remaining:,} remaining)")
        self.success_var.set(f"{progress_info.success_count} ({performance['success_rate']*100:.1f}%)")
        self.errors_var.set(f"{progress_info.error_count} ({performance['error_rate']*100:.1f}%)")
        
        # Update time estimates with enhanced accuracy
        self.time_var.set(time_estimates['remaining'])
        
        # Update processing speed and throughput
        self.speed_var.set(f"{stats.files_per_second:.1f} files/sec")
        
        # Format throughput
        if stats.bytes_per_second > 1024 * 1024:
            throughput = f"{stats.bytes_per_second / (1024 * 1024):.1f} MB/sec"
        elif stats.bytes_per_second > 1024:
            throughput = f"{stats.bytes_per_second / 1024:.1f} KB/sec"
        else:
            throughput = f"{stats.bytes_per_second:.0f} B/sec"
        
        self.throughput_var.set(throughput)
    
    def _operation_finished(self, final_state: ProgressState):
        """Handle operation completion."""
        self.is_running = False
        
        if final_state == ProgressState.COMPLETED:
            self.milestone_indicator.set_milestone('complete', True)
            self.phase_var.set("Operation completed successfully")
            self.game_progress.set_progress(100.0)
            self.progress_label.config(text="100%")
            self._log_message("Operation completed successfully", "SUCCESS")
        else:
            self.phase_var.set("Operation cancelled")
            self._log_message("Operation was cancelled", "WARNING")
        
        # Update button states
        self.pause_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)
        self.close_button.config(state=tk.NORMAL)
        
        self.time_var.set("Finished")
    
    def _log_message(self, message: str, level: str = "INFO", details: Dict[str, Any] = None):
        """Add message to operation log with enhanced details."""
        timestamp = time.time()
        formatted_time = time.strftime("%H:%M:%S", time.localtime(timestamp))
        microseconds = int((timestamp % 1) * 1000)
        full_timestamp = f"{formatted_time}.{microseconds:03d}"
        
        log_entry = f"[{full_timestamp}] {level}: {message}"
        
        # Store detailed log entry
        detailed_entry = {
            'timestamp': timestamp,
            'formatted_time': full_timestamp,
            'level': level,
            'message': message,
            'details': details or {},
            'thread': threading.current_thread().name
        }
        
        # Add to log with size limit
        self.operation_log.append((log_entry, level, detailed_entry))
        if len(self.operation_log) > self.max_log_entries:
            self.operation_log.pop(0)  # Remove oldest entry
        
        # Update log display if filters allow (with safety check)
        try:
            self._update_log_display()
        except tk.TclError:
            # Dialog is being destroyed, ignore the update
            pass
    
    def _log_file_operation(self, file_path: Path, operation: str, result: str, 
                           details: Dict[str, Any] = None):
        """Log file-specific operations with detailed context."""
        file_name = file_path.name if file_path else "Unknown"
        message = f"{operation}: {file_name} - {result}"
        
        operation_details = {
            'file_path': str(file_path) if file_path else None,
            'operation_type': operation,
            'result': result,
            **(details or {})
        }
        
        level = "SUCCESS" if result.lower() == "success" else "ERROR" if "error" in result.lower() else "INFO"
        self._log_message(message, level, operation_details)
    
    def _log_phase_transition(self, from_phase: str, to_phase: str, 
                             duration: float = None, stats: Dict[str, Any] = None):
        """Log phase transitions with timing and statistics."""
        message = f"Phase transition: {from_phase} → {to_phase}"
        if duration:
            message += f" (completed in {duration:.1f}s)"
        
        transition_details = {
            'from_phase': from_phase,
            'to_phase': to_phase,
            'duration_seconds': duration,
            'phase_stats': stats or {}
        }
        
        self._log_message(message, "INFO", transition_details)
    
    def _update_log_display(self):
        """Update the log text widget based on current filters."""
        # Check if widget still exists (prevent errors during dialog destruction)
        try:
            if not self.log_text.winfo_exists():
                return
        except tk.TclError:
            return
            
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        
        displayed_count = 0
        for entry_data in self.operation_log:
            if len(entry_data) >= 3:
                log_entry, level, detailed_entry = entry_data
            else:
                # Backward compatibility with old format
                log_entry, level = entry_data
                detailed_entry = None
            
            show_entry = self._should_show_log_entry(level)
            
            if show_entry:
                # Add color coding based on level
                if level == "ERROR":
                    self.log_text.insert(tk.END, log_entry + "\n")
                    start_line = f"{displayed_count + 1}.0"
                    end_line = f"{displayed_count + 1}.end"
                    self.log_text.tag_add("error", start_line, end_line)
                elif level == "SUCCESS":
                    self.log_text.insert(tk.END, log_entry + "\n")
                    start_line = f"{displayed_count + 1}.0"
                    end_line = f"{displayed_count + 1}.end"
                    self.log_text.tag_add("success", start_line, end_line)
                elif level == "WARNING":
                    self.log_text.insert(tk.END, log_entry + "\n")
                    start_line = f"{displayed_count + 1}.0"
                    end_line = f"{displayed_count + 1}.end"
                    self.log_text.tag_add("warning", start_line, end_line)
                else:
                    self.log_text.insert(tk.END, log_entry + "\n")
                
                displayed_count += 1
        
        # Configure text colors
        self.log_text.tag_configure("error", foreground="#cc0000")
        self.log_text.tag_configure("success", foreground="#00aa00")
        self.log_text.tag_configure("warning", foreground="#ff8800")
        
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)
    
    def _should_show_log_entry(self, level: str) -> bool:
        """Determine if a log entry should be shown based on current filters."""
        if self.show_all_var.get():
            return True
        
        # If show_all is False, check individual filters
        filter_map = {
            "ERROR": self.show_errors_var.get(),
            "WARNING": self.show_warnings_var.get(), 
            "SUCCESS": self.show_success_var.get(),
            "INFO": self.show_info_var.get()
        }
        
        return filter_map.get(level, False)  # Default to False if level not found
    
    def _clear_log(self):
        """Clear the current operation log."""
        if len(self.operation_log) == 0:
            return
        
        # Confirm clearing log
        from tkinter import messagebox
        if messagebox.askyesno("Clear Log", "Are you sure you want to clear the operation log?"):
            # Save current operation to history before clearing
            if self.operation_log:
                operation_summary = {
                    'start_time': time.time(),
                    'log_entries': self.operation_log.copy(),
                    'entry_count': len(self.operation_log)
                }
                self.operation_history.append(operation_summary)
                
                # Keep only last 10 operations in history
                if len(self.operation_history) > 10:
                    self.operation_history.pop(0)
            
            self.operation_log.clear()
            self._update_log_display()
            self._log_message("Log cleared by user", "INFO")
    
    def _save_log(self):
        """Save the current operation log with enhanced formatting."""
        from tkinter import filedialog
        
        if not self.operation_log:
            self._log_message("No log entries to save", "WARNING")
            return
        
        # Get filename from user
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        default_filename = f"SecureWipe_Log_{timestamp}.txt"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialvalue=default_filename,
            filetypes=[
                ("Text files", "*.txt"),
                ("Log files", "*.log"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ],
            title="Save Operation Log"
        )
        
        if filename:
            try:
                file_extension = filename.lower().split('.')[-1]
                
                if file_extension == 'json':
                    self._save_log_json(filename)
                else:
                    self._save_log_text(filename)
                    
                self._log_message(f"Log saved to {filename}", "SUCCESS")
            except Exception as e:
                self._log_message(f"Failed to save log: {str(e)}", "ERROR")
    
    def _save_log_text(self, filename: str):
        """Save log in human-readable text format."""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("SecureWipe Operation Log\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Entries: {len(self.operation_log)}\n")
            f.write("\n" + "-" * 50 + "\n\n")
            
            for entry_data in self.operation_log:
                if len(entry_data) >= 3:
                    log_entry, level, detailed_entry = entry_data
                    f.write(log_entry + "\n")
                    
                    # Add detailed information if available
                    if detailed_entry and detailed_entry.get('details'):
                        details = detailed_entry['details']
                        if details:
                            f.write(f"    Details: {details}\n")
                    f.write("\n")
                else:
                    # Backward compatibility
                    log_entry, level = entry_data
                    f.write(log_entry + "\n\n")
    
    def _save_log_json(self, filename: str):
        """Save log in structured JSON format for analysis."""
        import json
        
        log_data = {
            'metadata': {
                'generated_at': time.time(),
                'formatted_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_entries': len(self.operation_log),
                'format_version': '1.0'
            },
            'operation_history': self.operation_history,
            'current_operation': []
        }
        
        for entry_data in self.operation_log:
            if len(entry_data) >= 3:
                log_entry, level, detailed_entry = entry_data
                log_data['current_operation'].append(detailed_entry)
            else:
                # Backward compatibility
                log_entry, level = entry_data
                log_data['current_operation'].append({
                    'formatted_entry': log_entry,
                    'level': level,
                    'timestamp': time.time()
                })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def _update_log_filter(self):
        """Handle log filter changes."""
        self._update_log_display()
    
    def _format_time(self, seconds: float) -> str:
        """Format time duration for display."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}m {int(seconds % 60)}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size for display."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def _on_pause(self):
        """Handle pause button click."""
        if not self.ui_manager.is_operation_paused():
            self.ui_manager.pause_operation()
            self.pause_button.config(text="Resume")
            if self.pause_callback:
                self.pause_callback()
        else:
            self.ui_manager.resume_operation()
            self.pause_button.config(text="Pause")
            if self.resume_callback:
                self.resume_callback()
    
    def _on_cancel(self):
        """Handle cancel button click."""
        self.ui_manager.cancel_operation()
        if self.cancel_callback:
            self.cancel_callback()
        self.is_running = False
    
    def _on_close(self):
        """Handle close button click."""
        self.is_running = False
        self.ui_manager.stop_ui_updates()
        self.destroy()
    
    def _export_log(self):
        """Export operation log to file."""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Operation Log"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("SecureWipe Operation Log\n")
                    f.write("=" * 50 + "\n\n")
                    for log_entry, _ in self.operation_log:
                        f.write(log_entry + "\n")
                self._log_message(f"Log exported to {filename}", "SUCCESS")
            except Exception as e:
                self._log_message(f"Export failed: {str(e)}", "ERROR")
    
    def _center_window(self):
        """Center the dialog on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    # Thread-safe UI update handlers
    def _handle_progress_update(self, data: Dict[str, Any]):
        """Handle progress updates from background thread."""
        if 'percentage' in data:
            self.game_progress.set_progress(data['percentage'])
            self.progress_label.config(text=f"{data['percentage']:.1f}%")
        
        if 'processed_items' in data and 'total_items' in data:
            remaining = data['total_items'] - data['processed_items']
            self.files_var.set(f"{data['processed_items']:,} / {data['total_items']:,} ({remaining:,} remaining)")
        
        if 'current_item' in data and data['current_item']:
            item_name = str(data['current_item'])
            if len(item_name) > 50:
                item_name = item_name[:47] + "..."
            self.current_file_var.set(f"Processing: {item_name}")
        
        if 'items_per_second' in data:
            self.speed_var.set(f"{data['items_per_second']:.1f} files/sec")
        
        if 'estimated_remaining' in data:
            self.time_var.set(self._format_time(data['estimated_remaining']))
    
    def _handle_status_message(self, data: Dict[str, Any]):
        """Handle status messages from background thread."""
        message = data.get('message', '')
        level = data.get('level', 'INFO')
        self._log_message(message, level)
    
    def _handle_phase_change(self, data: Dict[str, Any]):
        """Handle phase changes from background thread."""
        phase = data.get('phase', '')
        description = data.get('description', '')
        
        self.phase_var.set(description or phase.replace('_', ' ').title())
        
        # Update milestone indicators based on phase
        if phase == 'initializing':
            self.milestone_indicator.set_milestone('scan', False)
        elif phase == 'scanning':
            self.milestone_indicator.set_milestone('scan', False)
        elif phase == 'categorizing':
            self.milestone_indicator.set_milestone('scan', True)
            self.milestone_indicator.set_milestone('categorize', False)
        elif phase in ['processing', 'deleting']:
            self.milestone_indicator.set_milestone('categorize', True)
            self.milestone_indicator.set_milestone('delete', False)
        elif phase == 'finalizing':
            self.milestone_indicator.set_milestone('delete', True)
        elif phase == 'complete':
            self.milestone_indicator.set_milestone('complete', True)
    
    def _handle_statistics_update(self, data: Dict[str, Any]):
        """Handle statistics updates from background thread."""
        stats = data.get('statistics', {})
        
        if 'success_count' in stats:
            self.success_var.set(str(stats['success_count']))
        if 'error_count' in stats:
            self.errors_var.set(str(stats['error_count']))
        if 'throughput' in stats:
            self.throughput_var.set(stats['throughput'])
    
    def _handle_operation_complete(self, data: Dict[str, Any]):
        """Handle operation completion from background thread."""
        success = data.get('success', True)
        
        if success:
            self.milestone_indicator.set_milestone('complete', True)
            self.phase_var.set("Operation completed successfully")
            self.game_progress.set_progress(100.0)
            self.progress_label.config(text="100%")
            self._log_message("Operation completed successfully", "SUCCESS")
        else:
            self.phase_var.set("Operation completed with errors")
            self._log_message("Operation completed with errors", "WARNING")
        
        # Update button states
        self.pause_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)
        self.close_button.config(state=tk.NORMAL)
        
        self.time_var.set("Finished")
        self.is_running = False
    
    def _handle_error(self, data: Dict[str, Any]):
        """Handle error messages from background thread."""
        error = data.get('error', 'Unknown error occurred')
        self._log_message(f"Error: {error}", "ERROR")
