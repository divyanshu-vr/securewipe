"""Certificate data structures."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


class OperationType(Enum):
    """Supported SecureWipe operation types."""

    QUICK_CLEAN = "quick_clean"
    DEEP_CLEAN = "deep_clean"


class DeletionMethod(Enum):
    """Supported deletion methods."""

    SDELETE = "sdelete"
    SHRED = "shred"
    NWIPE_DOD = "nwipe-dod"
    NWIPE_GUTMANN = "nwipe-gutmann"


class OperationStatus(Enum):
    """File operation status."""

    DELETED = "deleted"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass
class DeviceInfo:
    """Device information."""

    device_id: str
    hostname: str
    operating_system: str
    architecture: str
    user_context: str


@dataclass
class DeletionSummary:
    """Deletion operation summary."""

    total_files: int
    total_size_bytes: int
    deletion_method: DeletionMethod
    duration_seconds: float
    success_count: int
    failure_count: int


@dataclass
class FileOperation:
    """Individual file operation."""

    path: str
    size_bytes: int
    operation: OperationStatus
    reason: Optional[str] = None


@dataclass
class CryptographicProof:
    """Cryptographic signature proof."""

    algorithm: str
    public_key: str
    signature: str
    signature_format: str


@dataclass
class Certificate:
    """SecureWipe certificate."""

    schema_version: str
    certificate_id: str
    timestamp: datetime
    device_info: DeviceInfo
    operation_type: OperationType
    deletion_summary: DeletionSummary
    file_operations: List[FileOperation]
    cryptographic_proof: CryptographicProof
