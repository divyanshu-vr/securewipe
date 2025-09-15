"""Operation result tracking models."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional


class OperationStatus(Enum):
    """Operation status enumeration."""

    SUCCESS = "success"
    SKIPPED = "skipped"
    ERROR = "error"
    FAILED = "failed"
    PERMISSION_DENIED = "permission_denied"
    CANCELLED = "cancelled"
    NOT_FOUND = "not_found"


@dataclass
class OperationResult:
    """Result of a file operation."""

    status: OperationStatus
    message: Optional[str] = None
    path: Optional[Path] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

    @property
    def is_success(self) -> bool:
        """Check if operation was successful."""
        return self.status == OperationStatus.SUCCESS

    @property
    def is_error(self) -> bool:
        """Check if operation had an error."""
        return self.status == OperationStatus.ERROR


@dataclass
class BatchResult:
    """Result of a batch operation."""

    results: List[OperationResult]
    total_processed: int
    success_count: int
    error_count: int
    skipped_count: int

    @classmethod
    def from_results(cls, results: List[OperationResult]) -> "BatchResult":
        """Create BatchResult from list of OperationResults."""
        success_count = sum(1 for r in results if r.status == OperationStatus.SUCCESS)
        error_count = sum(1 for r in results if r.status == OperationStatus.ERROR)
        skipped_count = sum(1 for r in results if r.status == OperationStatus.SKIPPED)

        return cls(
            results=results,
            total_processed=len(results),
            success_count=success_count,
            error_count=error_count,
            skipped_count=skipped_count,
        )
