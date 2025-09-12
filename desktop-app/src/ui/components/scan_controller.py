"""Scan controller for managing threaded file scanning with UI updates."""

import queue
import sys
import threading
from pathlib import Path
from typing import Callable, List, Optional

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent / "shared"))

try:
    from shared.models.file_info import FileInfo, ScanProgress
except ImportError:
    # Fallback for testing
    from dataclasses import dataclass
    from datetime import datetime
    from enum import Enum

    class FileType(Enum):
        DOCUMENT = "document"
        OTHER = "other"

    @dataclass
    class FileInfo:
        path: Path
        size: int
        modified_date: datetime
        file_type: FileType
        is_accessible: bool = True

    @dataclass
    class ScanProgress:
        total_files: int = 0
        scanned_files: int = 0
        current_directory: Optional[Path] = None


class ScanController:
    """Controller for managing threaded file scanning operations."""

    def __init__(self):
        """Initialize scan controller."""
        self._scan_thread: Optional[threading.Thread] = None
        self._file_queue = queue.Queue()
        self._progress_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._scanner = None

        # Callbacks
        self._file_callback: Optional[Callable[[FileInfo], None]] = None
        self._progress_callback: Optional[Callable[[ScanProgress], None]] = None
        self._completion_callback: Optional[Callable[[bool], None]] = None

        # State
        self._is_scanning = False
        self._scan_cancelled = False

    def start_scan(
        self,
        directories: List[Path],
        scanner,  # FileScanner instance
        file_callback: Optional[Callable[[FileInfo], None]] = None,
        progress_callback: Optional[Callable[[ScanProgress], None]] = None,
        completion_callback: Optional[Callable[[bool], None]] = None,
    ):
        """Start scanning in a separate thread."""
        if self._is_scanning:
            raise RuntimeError("Scan already in progress")

        # Store callbacks
        self._file_callback = file_callback
        self._progress_callback = progress_callback
        self._completion_callback = completion_callback
        self._scanner = scanner

        # Reset state
        self._stop_event.clear()
        self._scan_cancelled = False
        self._is_scanning = True

        # Clear queues
        self._clear_queue(self._file_queue)
        self._clear_queue(self._progress_queue)

        # Start scan thread
        self._scan_thread = threading.Thread(
            target=self._scan_worker, args=(directories,), daemon=True
        )
        self._scan_thread.start()

        # Start UI update processing
        self._process_queues()

    def cancel_scan(self):
        """Cancel the current scan operation."""
        if not self._is_scanning:
            return

        self._scan_cancelled = True
        self._stop_event.set()

        # Cancel the scanner
        if self._scanner:
            self._scanner.cancel()

    def _scan_worker(self, directories: List[Path]):
        """Worker thread for file scanning."""
        try:
            # Define callbacks for the scanner
            def on_progress(progress: ScanProgress):
                if not self._stop_event.is_set():
                    self._progress_queue.put(progress)

            def on_file(file_info: FileInfo):
                if not self._stop_event.is_set():
                    self._file_queue.put(file_info)

            # Start scanning
            scan_generator = self._scanner.scan_directories(
                directories, progress_callback=on_progress, file_callback=on_file
            )

            # Process scan results
            for file_info in scan_generator:
                if self._stop_event.is_set():
                    break
                # File is already queued by on_file callback

            # Mark completion
            success = not self._scan_cancelled and not self._stop_event.is_set()
            self._progress_queue.put(("COMPLETE", success))

        except Exception as e:
            # Handle scan errors
            self._progress_queue.put(("ERROR", str(e)))

        finally:
            self._is_scanning = False

    def _process_queues(self):
        """Process file and progress queues on main thread."""
        if not self._is_scanning:
            return

        # Process file queue
        files_processed = 0
        while not self._file_queue.empty() and files_processed < 50:  # Batch limit
            try:
                file_info = self._file_queue.get_nowait()
                if self._file_callback:
                    self._file_callback(file_info)
                files_processed += 1
            except queue.Empty:
                break

        # Process progress queue
        while not self._progress_queue.empty():
            try:
                progress_item = self._progress_queue.get_nowait()

                if isinstance(progress_item, tuple):
                    # Special messages
                    msg_type, data = progress_item
                    if msg_type == "COMPLETE":
                        success = data
                        if self._completion_callback:
                            self._completion_callback(success)
                        return  # Stop processing
                    elif msg_type == "ERROR":
                        if self._completion_callback:
                            self._completion_callback(False)
                        return  # Stop processing
                else:
                    # Regular progress update
                    if self._progress_callback:
                        self._progress_callback(progress_item)

            except queue.Empty:
                break

        # Schedule next update
        if self._is_scanning:
            # Use after() to schedule on main thread
            if hasattr(self, "_root_widget"):
                self._root_widget.after(100, self._process_queues)

    def set_root_widget(self, widget):
        """Set root widget for scheduling updates."""
        self._root_widget = widget

    def _clear_queue(self, q: queue.Queue):
        """Clear all items from a queue."""
        while not q.empty():
            try:
                q.get_nowait()
            except queue.Empty:
                break

    @property
    def is_scanning(self) -> bool:
        """Check if scan is currently running."""
        return self._is_scanning

    @property
    def is_cancelled(self) -> bool:
        """Check if scan was cancelled."""
        return self._scan_cancelled

    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """Wait for scan to complete.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if scan completed, False if timeout
        """
        if self._scan_thread:
            self._scan_thread.join(timeout)
            return not self._scan_thread.is_alive()
        return True
