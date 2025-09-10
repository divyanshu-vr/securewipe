"""Progress indicator component for file scanning operations."""

import sys
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Callable, Optional

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent / "shared"))

try:
    from models.file_info import ScanProgress
except ImportError:
    # Fallback for testing
    from dataclasses import dataclass

    @dataclass
    class ScanProgress:
        total_files: int = 0
        scanned_files: int = 0
        total_size: int = 0
        scanned_size: int = 0
        current_directory: Optional[Path] = None
        scan_rate: float = 0.0
        estimated_remaining: Optional[float] = None


class ProgressIndicator(ttk.Frame):
    """Progress indicator widget with real-time updates."""

    def __init__(self, parent, **kwargs):
        """Initialize progress indicator."""
        super().__init__(parent, **kwargs)

        self._setup_ui()
        self._progress = ScanProgress()
        self._is_scanning = False

    def _setup_ui(self):
        """Setup the progress indicator UI."""
        # Main progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode="determinate",
        )
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)

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

    @property
    def is_scanning(self) -> bool:
        """Check if currently scanning."""
        return self._is_scanning


class BatchProgressTracker:
    """Helper class for tracking batch progress updates."""

    def __init__(self, progress_indicator: ProgressIndicator, batch_size: int = 100):
        """Initialize batch tracker."""
        self.progress_indicator = progress_indicator
        self.batch_size = batch_size
        self._file_count = 0
        self._last_update = time.time()
        self._update_interval = 0.1  # 100ms minimum

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

    def force_update(self, progress: ScanProgress):
        """Force an immediate progress update."""
        self.progress_indicator.update_progress(progress)
        self._last_update = time.time()
