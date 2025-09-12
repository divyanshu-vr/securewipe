"""Statistics tracking and time estimation for progress operations."""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class OperationStatistics:
    """Comprehensive operation statistics."""
    
    # Timing information
    start_time: float
    elapsed_time: float
    estimated_remaining: float
    estimated_total: float
    
    # File processing stats
    total_files: int
    processed_files: int
    success_count: int
    error_count: int
    skipped_count: int
    
    # Data processing stats
    total_bytes: int
    processed_bytes: int
    
    # Performance metrics
    files_per_second: float
    bytes_per_second: float
    average_file_size: float
    
    # Current operation
    current_file: Optional[Path]
    current_phase: str


class StatisticsTracker:
    """Advanced statistics tracking with dynamic time estimation."""
    
    def __init__(self):
        self.start_time = 0.0
        self.total_files = 0
        self.processed_files = 0
        self.success_count = 0
        self.error_count = 0
        self.skipped_count = 0
        self.total_bytes = 0
        self.processed_bytes = 0
        self.current_file = None
        self.current_phase = "idle"
        
        # Performance tracking
        self._file_timestamps = []
        self._byte_timestamps = []
        self._performance_window = 30  # Track last 30 operations for smoothing
        
        # Estimation parameters
        self._estimation_samples = []
        self._min_samples_for_estimate = 5
        
    def start_operation(self, total_files: int, total_bytes: int = 0):
        """Start tracking a new operation."""
        self.start_time = time.time()
        self.total_files = total_files
        self.total_bytes = total_bytes
        self.processed_files = 0
        self.success_count = 0
        self.error_count = 0
        self.skipped_count = 0
        self.processed_bytes = 0
        self.current_file = None
        self.current_phase = "initializing"
        
        # Reset tracking arrays
        self._file_timestamps.clear()
        self._byte_timestamps.clear()
        self._estimation_samples.clear()
    
    def update_current_file(self, file_path: Path, file_size: int = 0):
        """Update the currently processing file."""
        self.current_file = file_path
        
        # Record timestamp for performance tracking
        current_time = time.time()
        self._file_timestamps.append(current_time)
        if file_size > 0:
            self._byte_timestamps.append((current_time, file_size))
        
        # Keep only recent samples for performance calculation
        cutoff_time = current_time - 60  # Last 60 seconds
        self._file_timestamps = [t for t in self._file_timestamps if t > cutoff_time]
        self._byte_timestamps = [(t, s) for t, s in self._byte_timestamps if t > cutoff_time]
    
    def file_completed(self, success: bool, file_size: int = 0):
        """Mark a file as completed and update statistics."""
        self.processed_files += 1
        self.processed_bytes += file_size
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
        
        # Update estimation samples
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if self.processed_files > 0:
            avg_time_per_file = elapsed / self.processed_files
            self._estimation_samples.append(avg_time_per_file)
            
            # Keep only recent samples for better estimation
            if len(self._estimation_samples) > 50:
                self._estimation_samples = self._estimation_samples[-30:]
    
    def file_skipped(self):
        """Mark a file as skipped."""
        self.processed_files += 1
        self.skipped_count += 1
    
    def set_phase(self, phase: str):
        """Set the current operation phase."""
        self.current_phase = phase
    
    def get_statistics(self) -> OperationStatistics:
        """Get comprehensive operation statistics."""
        current_time = time.time()
        elapsed_time = current_time - self.start_time if self.start_time > 0 else 0
        
        # Calculate performance metrics
        files_per_second = self._calculate_files_per_second()
        bytes_per_second = self._calculate_bytes_per_second()
        average_file_size = self.processed_bytes / max(1, self.processed_files)
        
        # Calculate time estimates
        estimated_remaining = self._calculate_estimated_remaining()
        estimated_total = elapsed_time + estimated_remaining
        
        return OperationStatistics(
            start_time=self.start_time,
            elapsed_time=elapsed_time,
            estimated_remaining=estimated_remaining,
            estimated_total=estimated_total,
            total_files=self.total_files,
            processed_files=self.processed_files,
            success_count=self.success_count,
            error_count=self.error_count,
            skipped_count=self.skipped_count,
            total_bytes=self.total_bytes,
            processed_bytes=self.processed_bytes,
            files_per_second=files_per_second,
            bytes_per_second=bytes_per_second,
            average_file_size=average_file_size,
            current_file=self.current_file,
            current_phase=self.current_phase
        )
    
    def _calculate_files_per_second(self) -> float:
        """Calculate current files per second processing rate."""
        if len(self._file_timestamps) < 2:
            return 0.0
        
        # Use recent timestamps for current rate
        recent_timestamps = self._file_timestamps[-10:]  # Last 10 files
        if len(recent_timestamps) < 2:
            return 0.0
        
        time_span = recent_timestamps[-1] - recent_timestamps[0]
        if time_span <= 0:
            return 0.0
        
        return (len(recent_timestamps) - 1) / time_span
    
    def _calculate_bytes_per_second(self) -> float:
        """Calculate current bytes per second processing rate."""
        if len(self._byte_timestamps) < 2:
            return 0.0
        
        # Use recent timestamps for current rate
        recent_timestamps = self._byte_timestamps[-10:]  # Last 10 files
        if len(recent_timestamps) < 2:
            return 0.0
        
        time_span = recent_timestamps[-1][0] - recent_timestamps[0][0]
        total_bytes = sum(size for _, size in recent_timestamps)
        
        if time_span <= 0:
            return 0.0
        
        return total_bytes / time_span
    
    def _calculate_estimated_remaining(self) -> float:
        """Calculate estimated remaining time using multiple methods."""
        if self.processed_files == 0 or self.total_files <= self.processed_files:
            return 0.0
        
        remaining_files = self.total_files - self.processed_files
        
        # Method 1: Simple average (fallback)
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        simple_estimate = (elapsed_time / self.processed_files) * remaining_files
        
        # Method 2: Recent performance based estimate
        files_per_second = self._calculate_files_per_second()
        if files_per_second > 0:
            performance_estimate = remaining_files / files_per_second
        else:
            performance_estimate = simple_estimate
        
        # Method 3: Weighted average of recent samples
        if len(self._estimation_samples) >= self._min_samples_for_estimate:
            # Use exponential weighted average for recent samples
            weights = [0.8 ** i for i in range(len(self._estimation_samples))]
            weights.reverse()  # Most recent gets highest weight
            
            weighted_avg = sum(w * s for w, s in zip(weights, self._estimation_samples)) / sum(weights)
            sample_estimate = weighted_avg * remaining_files
        else:
            sample_estimate = simple_estimate
        
        # Combine estimates with weights based on confidence
        if len(self._estimation_samples) >= 10 and files_per_second > 0:
            # High confidence: weight recent performance heavily
            final_estimate = (0.6 * performance_estimate + 
                            0.3 * sample_estimate + 
                            0.1 * simple_estimate)
        elif len(self._estimation_samples) >= 5:
            # Medium confidence: balance methods
            final_estimate = (0.4 * performance_estimate + 
                            0.4 * sample_estimate + 
                            0.2 * simple_estimate)
        else:
            # Low confidence: use simple method with slight performance weighting
            final_estimate = (0.3 * performance_estimate + 0.7 * simple_estimate)
        
        # Apply bounds checking
        min_estimate = max(1.0, remaining_files * 0.1)  # At least 0.1 sec per file
        max_estimate = remaining_files * 300  # At most 5 minutes per file
        
        return max(min_estimate, min(max_estimate, final_estimate))
    
    def get_performance_summary(self) -> Dict[str, float]:
        """Get performance metrics summary."""
        stats = self.get_statistics()
        
        return {
            'files_per_second': stats.files_per_second,
            'bytes_per_second': stats.bytes_per_second,
            'average_file_size': stats.average_file_size,
            'success_rate': stats.success_count / max(1, stats.processed_files),
            'error_rate': stats.error_count / max(1, stats.processed_files),
            'completion_percentage': (stats.processed_files / max(1, stats.total_files)) * 100
        }
    
    def get_time_estimates(self) -> Dict[str, str]:
        """Get formatted time estimates."""
        stats = self.get_statistics()
        
        def format_duration(seconds: float) -> str:
            if seconds < 60:
                return f"{int(seconds)}s"
            elif seconds < 3600:
                minutes = int(seconds / 60)
                secs = int(seconds % 60)
                return f"{minutes}m {secs}s"
            else:
                hours = int(seconds / 3600)
                minutes = int((seconds % 3600) / 60)
                return f"{hours}h {minutes}m"
        
        return {
            'elapsed': format_duration(stats.elapsed_time),
            'remaining': format_duration(stats.estimated_remaining),
            'total': format_duration(stats.estimated_total)
        }