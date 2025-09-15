"""Enhanced progress indicator components for file operations."""

import sys
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Callable, Optional

# Add shared modules to path
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

try:
    from models.file_info import ScanProgress
    from deletion.progress_tracker import ProgressInfo, ProgressState
except ImportError:
    # Fallback for testing
    from dataclasses import dataclass
    from enum import Enum

    class ProgressState(Enum):
        IDLE = "idle"
        RUNNING = "running"
        PAUSED = "paused"
        CANCELLED = "cancelled"
        COMPLETED = "completed"

    @dataclass
    class ScanProgress:
        total_files: int = 0
        scanned_files: int = 0
        total_size: int = 0
        scanned_size: int = 0
        current_directory: Optional[Path] = None
        scan_rate: float = 0.0
        estimated_remaining: Optional[float] = None
    
    @dataclass
    class ProgressInfo:
        total_files: int = 0
        processed_files: int = 0
        current_file: Optional[Path] = None
        bytes_processed: int = 0
        total_bytes: int = 0
        elapsed_time: float = 0.0
        estimated_remaining: float = 0.0
        state: ProgressState = ProgressState.IDLE
        success_count: int = 0
        error_count: int = 0
        skipped_count: int = 0


class AnimatedProgressBar(tk.Canvas):
    """Animated progress bar with gaming-style effects."""
    
    def __init__(self, parent, width=300, height=20, **kwargs):
        super().__init__(parent, width=width, height=height, bg='#f0f0f0', highlightthickness=1, **kwargs)
        self.width = width
        self.height = height
        self.progress = 0.0
        self.animation_offset = 0
        self._setup_bar()
        self._animate()
    
    def _setup_bar(self):
        """Setup animated progress bar elements."""
        # Background
        self.create_rectangle(0, 0, self.width, self.height, fill='#e0e0e0', outline='#cccccc')
        
        # Progress fill
        self.progress_rect = self.create_rectangle(0, 0, 0, self.height, fill='#4CAF50', outline='')
        
        # Animation stripes
        self.stripes = []
        for i in range(0, self.width + 20, 10):
            stripe = self.create_line(i, 0, i + 5, self.height, fill='#ffffff', width=1, stipple='gray25')
            self.stripes.append(stripe)
    
    def _animate(self):
        """Animate the progress bar stripes."""
        if self.progress > 0 and self.progress < 100:
            self.animation_offset = (self.animation_offset + 1) % 10
            for i, stripe in enumerate(self.stripes):
                x_pos = (i * 10 + self.animation_offset) % (self.width + 20)
                self.coords(stripe, x_pos, 0, x_pos + 5, self.height)
        
        self.after(100, self._animate)
    
    def set_progress(self, percentage: float):
        """Update progress (0.0 to 100.0)."""
        self.progress = max(0.0, min(100.0, percentage))
        fill_width = int(self.width * (self.progress / 100.0))
        self.coords(self.progress_rect, 0, 0, fill_width, self.height)


class ProgressIndicator(ttk.Frame):
    """Enhanced progress indicator widget with real-time updates."""

    def __init__(self, parent, **kwargs):
        """Initialize progress indicator."""
        super().__init__(parent, **kwargs)

        self._setup_ui()
        self._progress = ScanProgress()
        self._is_scanning = False
        self._phase = "idle"

    def _setup_ui(self):
        """Setup the enhanced progress indicator UI."""
        # Phase indicator
        self.phase_var = tk.StringVar(value="Ready")
        phase_label = ttk.Label(self, textvariable=self.phase_var, font=('Arial', 10, 'bold'))
        phase_label.pack(fill=tk.X, padx=5, pady=(5, 2))
        
        # Animated progress bar
        self.animated_progress = AnimatedProgressBar(self, width=400, height=25)
        self.animated_progress.pack(fill=tk.X, padx=5, pady=5)
        
        # Standard progress bar (fallback)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode="determinate",
        )
        # Don't pack by default - use animated version

        # Status label
        self.status_var = tk.StringVar(value="Ready to scan")
        self.status_label = ttk.Label(self, textvariable=self.status_var)
        self.status_label.pack(fill=tk.X, padx=5, pady=2)

        # Details frame
        details_frame = ttk.Frame(self)
        details_frame.pack(fill=tk.X, padx=5, pady=2)

        # Files count
        self.files_var = tk.StringVar(value="Files: 0 / 0")
        files_label = ttk.Label(details_frame, textvariable=self.files_var)
        files_label.pack(side=tk.LEFT)

        # Size info
        self.size_var = tk.StringVar(value="Size: 0 MB")
        size_label = ttk.Label(details_frame, textvariable=self.size_var)
        size_label.pack(side=tk.RIGHT)

        # Rate and time frame
        rate_frame = ttk.Frame(self)
        rate_frame.pack(fill=tk.X, padx=5, pady=2)

        # Scan rate
        self.rate_var = tk.StringVar(value="Rate: 0 files/sec")
        rate_label = ttk.Label(rate_frame, textvariable=self.rate_var)
        rate_label.pack(side=tk.LEFT)

        # Estimated time
        self.time_var = tk.StringVar(value="")
        time_label = ttk.Label(rate_frame, textvariable=self.time_var)
        time_label.pack(side=tk.RIGHT)

        # Cancel button
        self.cancel_var = tk.BooleanVar()
        self.cancel_button = ttk.Button(
            self, text="Cancel", command=self._on_cancel, state=tk.DISABLED
        )
        self.cancel_button.pack(pady=5)

    def start_scan(self, cancel_callback: Optional[Callable[[], None]] = None):
        """Start scanning mode."""
        self._is_scanning = True
        self._cancel_callback = cancel_callback
        self.cancel_button.config(state=tk.NORMAL)
        self.status_var.set("Initializing scan...")
        self.progress_var.set(0)

    def update_progress(self, progress: ScanProgress):
        """Update progress display with new data."""
        self._progress = progress

        # Update progress bar
        self.progress_var.set(progress.progress_percent)

        # Update status message
        if progress.current_directory:
            dir_name = progress.current_directory.name or str(
                progress.current_directory
            )
            self.status_var.set(f"Scanning {dir_name}...")
        else:
            self.status_var.set("Scanning files...")

        # Update file count
        self.files_var.set(
            f"Files: {progress.scanned_files:,} / {progress.total_files:,}"
        )

        # Update size info
        size_mb = progress.scanned_size / (1024 * 1024)
        self.size_var.set(f"Size: {size_mb:.1f} MB")

        # Update scan rate
        if progress.scan_rate > 0:
            self.rate_var.set(f"Rate: {progress.scan_rate:.0f} files/sec")
        else:
            self.rate_var.set("Rate: calculating...")

        # Update estimated time
        if progress.estimated_remaining is not None:
            time_str = self._format_time(progress.estimated_remaining)
            self.time_var.set(f"Est. time: {time_str}")
        else:
            self.time_var.set("")

    def finish_scan(self, success: bool = True):
        """Finish scanning mode."""
        self._is_scanning = False
        self.cancel_button.config(state=tk.DISABLED)

        if success:
            self.status_var.set("Scan completed successfully")
            self.progress_var.set(100)
        else:
            self.status_var.set("Scan cancelled or failed")

        # Final update
        files_text = f"Files: {self._progress.scanned_files:,}"
        if self._progress.total_files > 0:
            files_text += f" / {self._progress.total_files:,}"
        self.files_var.set(files_text)

        size_mb = self._progress.scanned_size / (1024 * 1024)
        self.size_var.set(f"Total size: {size_mb:.1f} MB")

        self.rate_var.set("")
        self.time_var.set("")

    def _on_cancel(self):
        """Handle cancel button click."""
        if (
            self._is_scanning
            and hasattr(self, "_cancel_callback")
            and self._cancel_callback
        ):
            self._cancel_callback()
            self.status_var.set("Cancelling scan...")
            self.cancel_button.config(state=tk.DISABLED)

    def _format_time(self, seconds: float) -> str:
        """Format time duration for display."""
        if seconds < 30:
            return f"About {int(seconds)} seconds"
        elif seconds < 300:  # 5 minutes
            minutes = int(seconds / 60)
            return f"About {minutes} minute{'s' if minutes != 1 else ''}"
        else:
            minutes = int(seconds / 60)
            return f"About {minutes} minutes (large operation)"

    def set_phase(self, phase: str):
        """Set the current operation phase with enhanced visual indicators."""
        self._phase = phase
        phase_icons = {
            "idle": "⏸️",
            "Initializing": "⚙️",
            "Scanning": "🔍",
            "Categorizing": "📂", 
            "Deleting": "🗑️",
            "Paused": "⏸️",
            "Complete": "✅",
            "Cancelled": "❌"
        }
        
        # Add phase-specific colors for better differentiation
        phase_colors = {
            "idle": "#666666",
            "Initializing": "#0066cc",
            "Scanning": "#ff8800",
            "Categorizing": "#8800ff",
            "Deleting": "#cc0000",
            "Paused": "#ffaa00",
            "Complete": "#00aa00",
            "Cancelled": "#aa0000"
        }
        
        icon = phase_icons.get(phase, "⚙️")
        color = phase_colors.get(phase, "#000000")
        
        # Update phase display with color coding
        self.phase_var.set(f"{icon} {phase}")
    
    def update_deletion_progress(self, progress_info: ProgressInfo):
        """Update progress for deletion operations with enhanced status display."""
        percentage = (progress_info.processed_files / max(1, progress_info.total_files)) * 100
        
        # Update progress bars
        self.progress_var.set(percentage)
        self.animated_progress.set_progress(percentage)
        
        # Enhanced phase differentiation with contextual information
        if progress_info.state == ProgressState.RUNNING:
            if percentage < 1:
                self.set_phase("Initializing")
                phase_detail = "Preparing secure deletion process"
            elif percentage < 10:
                self.set_phase("Scanning")
                phase_detail = "Analyzing files for deletion"
            elif percentage < 20:
                self.set_phase("Categorizing")
                phase_detail = "Organizing files by type and priority"
            else:
                self.set_phase("Deleting")
                phase_detail = "Securely overwriting file data"
        elif progress_info.state == ProgressState.PAUSED:
            self.set_phase("Paused")
            phase_detail = "Operation temporarily suspended"
        elif progress_info.state == ProgressState.COMPLETED:
            self.set_phase("Complete")
            phase_detail = "All files processed successfully"
        elif progress_info.state == ProgressState.CANCELLED:
            self.set_phase("Cancelled")
            phase_detail = "Operation stopped by user request"
        else:
            phase_detail = "Ready to begin"
        
        # Update status message with plain-language descriptions
        if progress_info.current_file:
            file_name = progress_info.current_file.name
            
            if len(file_name) > 40:
                file_name = file_name[:37] + "..."
            
            # Add contextual information based on phase
            if self._phase == "Scanning":
                self.status_var.set(f"Analyzing: {file_name}")
            elif self._phase == "Categorizing":
                self.status_var.set(f"Categorizing: {file_name}")
            elif self._phase == "Deleting":
                self.status_var.set(f"Securely deleting: {file_name}")
            else:
                self.status_var.set(f"Processing: {file_name}")
        else:
            self.status_var.set(phase_detail)
        
        # Update file count with contextual information
        remaining = progress_info.total_files - progress_info.processed_files
        self.files_var.set(
            f"Files: {progress_info.processed_files:,} / {progress_info.total_files:,} ({remaining:,} remaining)"
        )
        
        # Update size info with processing context
        size_mb = progress_info.bytes_processed / (1024 * 1024)
        total_mb = progress_info.total_bytes / (1024 * 1024) if progress_info.total_bytes > 0 else 0
        
        if total_mb > 0:
            self.size_var.set(f"Data: {size_mb:.1f} MB / {total_mb:.1f} MB")
        else:
            self.size_var.set(f"Processed: {size_mb:.1f} MB")
        
        # Enhanced time estimate with processing speed
        if progress_info.estimated_remaining > 0:
            time_str = self._format_time(progress_info.estimated_remaining)
            # Calculate processing speed
            if progress_info.elapsed_time > 0:
                files_per_sec = progress_info.processed_files / progress_info.elapsed_time
                self.rate_var.set(f"Speed: {files_per_sec:.1f} files/sec")
                self.time_var.set(f"Time left: {time_str}")
            else:
                self.rate_var.set("Speed: calculating...")
                self.time_var.set(f"Time left: {time_str}")
        else:
            self.rate_var.set("Speed: calculating...")
            self.time_var.set("Calculating...")
    
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
    
    @property
    def is_scanning(self) -> bool:
        """Check if currently scanning."""
        return self._is_scanning


class BatchProgressTracker:
    """Helper class for tracking batch progress updates with enhanced responsiveness."""

    def __init__(self, progress_indicator: ProgressIndicator, batch_size: int = 50):
        """Initialize batch tracker with optimized batch size for responsiveness."""
        self.progress_indicator = progress_indicator
        self.batch_size = batch_size
        self._file_count = 0
        self._last_update = time.time()
        self._update_interval = 0.1  # 100ms minimum for responsive UI

    def add_file(self, progress: ScanProgress):
        """Add a file to the batch and update if needed."""
        self._file_count += 1
        current_time = time.time()

        # Update every batch_size files or every update_interval seconds
        if (
            self._file_count % self.batch_size == 0
            or current_time - self._last_update >= self._update_interval
        ):
            self.progress_indicator.update_progress(progress)
            self._last_update = current_time

    def add_deletion_progress(self, progress_info: ProgressInfo):
        """Add deletion progress and update if needed."""
        self._file_count += 1
        current_time = time.time()

        # Update every batch_size files or every update_interval seconds
        if (
            self._file_count % self.batch_size == 0
            or current_time - self._last_update >= self._update_interval
        ):
            self.progress_indicator.update_deletion_progress(progress_info)
            self._last_update = current_time

    def force_update(self, progress: ScanProgress):
        """Force an immediate progress update."""
        self.progress_indicator.update_progress(progress)
        self._last_update = time.time()
    
    def force_deletion_update(self, progress_info: ProgressInfo):
        """Force an immediate deletion progress update."""
        self.progress_indicator.update_deletion_progress(progress_info)
        self._last_update = time.time()
