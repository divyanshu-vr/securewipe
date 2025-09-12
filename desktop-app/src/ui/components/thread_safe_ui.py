"""Thread-safe UI update system for non-blocking operations."""

import queue
import threading
import time
import tkinter as tk
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional, Union
from pathlib import Path


class UIUpdateType(Enum):
    """Types of UI updates."""
    PROGRESS_UPDATE = "progress_update"
    STATUS_MESSAGE = "status_message"
    PHASE_CHANGE = "phase_change"
    STATISTICS_UPDATE = "statistics_update"
    OPERATION_COMPLETE = "operation_complete"
    ERROR_OCCURRED = "error_occurred"
    LOG_MESSAGE = "log_message"


@dataclass
class UIUpdateMessage:
    """Message for UI updates."""
    update_type: UIUpdateType
    data: Dict[str, Any]
    timestamp: float


class ThreadSafeUIManager:
    """Manages thread-safe UI updates with queue system."""
    
    def __init__(self, root_widget: tk.Widget):
        self.root_widget = root_widget
        self.update_queue = queue.Queue()
        self.is_running = False
        self.update_handlers = {}
        self.update_interval = 50  # 50ms for responsive UI
        
        # Operation control
        self.operation_cancelled = threading.Event()
        self.operation_paused = threading.Event()
        self.operation_paused.set()  # Start unpaused
        
        # Performance monitoring
        self.update_count = 0
        self.last_performance_check = time.time()
        
    def register_handler(self, update_type: UIUpdateType, handler: Callable[[Dict[str, Any]], None]):
        """Register a handler for specific update types."""
        self.update_handlers[update_type] = handler
    
    def start_ui_updates(self):
        """Start the UI update processing loop."""
        self.is_running = True
        self._schedule_next_update()
    
    def stop_ui_updates(self):
        """Stop the UI update processing loop."""
        self.is_running = False
    
    def queue_update(self, update_type: UIUpdateType, data: Dict[str, Any]):
        """Queue a UI update from any thread."""
        message = UIUpdateMessage(
            update_type=update_type,
            data=data,
            timestamp=time.time()
        )
        
        try:
            # Use non-blocking put with timeout to prevent queue overflow
            self.update_queue.put(message, timeout=0.1)
        except queue.Full:
            # If queue is full, drop oldest messages to prevent memory issues
            try:
                self.update_queue.get_nowait()  # Remove oldest
                self.update_queue.put(message, timeout=0.1)  # Add new
            except (queue.Empty, queue.Full):
                pass  # Skip this update if still can't add
    
    def _process_updates(self):
        """Process all queued UI updates."""
        updates_processed = 0
        max_updates_per_cycle = 10  # Limit updates per cycle for responsiveness
        
        while updates_processed < max_updates_per_cycle and not self.update_queue.empty():
            try:
                message = self.update_queue.get_nowait()
                self._handle_update(message)
                updates_processed += 1
                self.update_count += 1
            except queue.Empty:
                break
        
        # Performance monitoring
        current_time = time.time()
        if current_time - self.last_performance_check > 5.0:  # Every 5 seconds
            self._check_performance()
            self.last_performance_check = current_time
    
    def _handle_update(self, message: UIUpdateMessage):
        """Handle a single UI update message."""
        handler = self.update_handlers.get(message.update_type)
        if handler:
            try:
                handler(message.data)
            except Exception as e:
                # Log error but don't crash UI
                print(f"UI update error: {e}")
    
    def _schedule_next_update(self):
        """Schedule the next UI update cycle."""
        if self.is_running:
            self._process_updates()
            self.root_widget.after(self.update_interval, self._schedule_next_update)
    
    def _check_performance(self):
        """Monitor and adjust performance if needed."""
        updates_per_second = self.update_count / 5.0
        self.update_count = 0
        
        # Adjust update interval based on load
        if updates_per_second > 50:  # High load
            self.update_interval = min(100, self.update_interval + 10)
        elif updates_per_second < 10:  # Low load
            self.update_interval = max(25, self.update_interval - 5)
    
    # Operation control methods
    def pause_operation(self):
        """Pause the background operation."""
        self.operation_paused.clear()
        self.queue_update(UIUpdateType.STATUS_MESSAGE, {
            'message': 'Operation paused by user',
            'level': 'INFO'
        })
    
    def resume_operation(self):
        """Resume the background operation."""
        self.operation_paused.set()
        self.queue_update(UIUpdateType.STATUS_MESSAGE, {
            'message': 'Operation resumed',
            'level': 'INFO'
        })
    
    def cancel_operation(self):
        """Cancel the background operation."""
        self.operation_cancelled.set()
        self.operation_paused.set()  # Unblock any waiting threads
        self.queue_update(UIUpdateType.STATUS_MESSAGE, {
            'message': 'Cancellation requested',
            'level': 'WARNING'
        })
    
    def is_operation_cancelled(self) -> bool:
        """Check if operation has been cancelled."""
        return self.operation_cancelled.is_set()
    
    def is_operation_paused(self) -> bool:
        """Check if operation is paused."""
        return not self.operation_paused.is_set()
    
    def wait_if_paused(self, timeout: Optional[float] = None) -> bool:
        """Wait if operation is paused. Returns False if cancelled."""
        if self.operation_cancelled.is_set():
            return False
        
        self.operation_paused.wait(timeout)
        return not self.operation_cancelled.is_set()


class BackgroundOperationManager:
    """Manages background operations with progress reporting."""
    
    def __init__(self, ui_manager: ThreadSafeUIManager):
        self.ui_manager = ui_manager
        self.current_operation = None
        self.operation_thread = None
    
    def start_operation(self, operation_func: Callable, *args, **kwargs):
        """Start a background operation."""
        if self.current_operation and self.operation_thread and self.operation_thread.is_alive():
            raise RuntimeError("Another operation is already running")
        
        # Reset operation state
        self.ui_manager.operation_cancelled.clear()
        self.ui_manager.operation_paused.set()
        
        # Start operation in background thread
        self.operation_thread = threading.Thread(
            target=self._run_operation,
            args=(operation_func,) + args,
            kwargs=kwargs,
            daemon=True
        )
        self.operation_thread.start()
    
    def _run_operation(self, operation_func: Callable, *args, **kwargs):
        """Run operation in background thread with error handling."""
        try:
            self.current_operation = operation_func
            
            # Notify operation started
            self.ui_manager.queue_update(UIUpdateType.STATUS_MESSAGE, {
                'message': 'Background operation started',
                'level': 'INFO'
            })
            
            # Run the operation
            result = operation_func(self.ui_manager, *args, **kwargs)
            
            # Notify completion
            self.ui_manager.queue_update(UIUpdateType.OPERATION_COMPLETE, {
                'result': result,
                'success': True
            })
            
        except Exception as e:
            # Notify error
            self.ui_manager.queue_update(UIUpdateType.ERROR_OCCURRED, {
                'error': str(e),
                'exception': e
            })
            
        finally:
            self.current_operation = None
    
    def is_operation_running(self) -> bool:
        """Check if an operation is currently running."""
        return (self.operation_thread and 
                self.operation_thread.is_alive() and 
                not self.ui_manager.is_operation_cancelled())


class ProgressReporter:
    """Helper class for reporting progress from background operations."""
    
    def __init__(self, ui_manager: ThreadSafeUIManager, total_items: int):
        self.ui_manager = ui_manager
        self.total_items = total_items
        self.processed_items = 0
        self.start_time = time.time()
        self.last_report_time = self.start_time
        self.report_interval = 0.1  # Report every 100ms minimum
    
    def report_progress(self, current_item: Optional[Path] = None, 
                       items_processed: int = 1, 
                       force_update: bool = False):
        """Report progress update."""
        self.processed_items += items_processed
        current_time = time.time()
        
        # Throttle updates for performance
        if not force_update and current_time - self.last_report_time < self.report_interval:
            return
        
        self.last_report_time = current_time
        
        # Calculate statistics
        elapsed_time = current_time - self.start_time
        percentage = (self.processed_items / max(1, self.total_items)) * 100
        
        # Estimate remaining time
        if self.processed_items > 0 and elapsed_time > 0:
            items_per_second = self.processed_items / elapsed_time
            remaining_items = self.total_items - self.processed_items
            estimated_remaining = remaining_items / items_per_second if items_per_second > 0 else 0
        else:
            estimated_remaining = 0
        
        # Queue progress update
        self.ui_manager.queue_update(UIUpdateType.PROGRESS_UPDATE, {
            'total_items': self.total_items,
            'processed_items': self.processed_items,
            'current_item': current_item,
            'percentage': percentage,
            'elapsed_time': elapsed_time,
            'estimated_remaining': estimated_remaining,
            'items_per_second': self.processed_items / elapsed_time if elapsed_time > 0 else 0
        })
    
    def report_phase_change(self, phase: str, description: str = ""):
        """Report phase change."""
        self.ui_manager.queue_update(UIUpdateType.PHASE_CHANGE, {
            'phase': phase,
            'description': description,
            'timestamp': time.time()
        })
    
    def report_statistics(self, stats: Dict[str, Any]):
        """Report detailed statistics."""
        self.ui_manager.queue_update(UIUpdateType.STATISTICS_UPDATE, {
            'statistics': stats,
            'timestamp': time.time()
        })
    
    def check_cancellation(self) -> bool:
        """Check if operation should be cancelled."""
        if self.ui_manager.is_operation_cancelled():
            return True
        
        # Wait if paused
        return not self.ui_manager.wait_if_paused(timeout=0.1)


def example_long_operation(ui_manager: ThreadSafeUIManager, file_list: list):
    """Example of a long-running operation with progress reporting."""
    reporter = ProgressReporter(ui_manager, len(file_list))
    
    reporter.report_phase_change("initializing", "Preparing file processing")
    
    for i, file_path in enumerate(file_list):
        # Check for cancellation/pause
        if reporter.check_cancellation():
            break
        
        # Simulate file processing
        time.sleep(0.1)  # Simulate work
        
        # Report progress
        reporter.report_progress(current_item=Path(file_path))
        
        # Report phase changes
        if i == len(file_list) // 4:
            reporter.report_phase_change("categorizing", "Organizing files by type")
        elif i == len(file_list) // 2:
            reporter.report_phase_change("processing", "Processing files")
        elif i == len(file_list) * 3 // 4:
            reporter.report_phase_change("finalizing", "Completing operation")
    
    return {"processed": i + 1, "total": len(file_list)}