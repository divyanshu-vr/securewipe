"""Custom log formatters for SecureWipe."""

import logging
from datetime import datetime

from .sanitizer import sanitize_message


class SecureFormatter(logging.Formatter):
    """OWASP-compliant log formatter with automatic sanitization."""

    def __init__(self):
        # Standard format with timestamp, logger name, level, and message
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        super().__init__(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with sanitization."""
        # Sanitize the message before formatting
        if hasattr(record, "msg") and record.msg:
            record.msg = sanitize_message(str(record.msg))

        # Format the record
        formatted = super().format(record)

        # Additional sanitization of the full formatted message
        return sanitize_message(formatted)


class DebugFormatter(logging.Formatter):
    """Enhanced formatter for debug logging with additional context."""

    def __init__(self):
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        super().__init__(fmt, datefmt="%Y-%m-%d %H:%M:%S.%f")

    def format(self, record: logging.LogRecord) -> str:
        """Format debug record with function and line information."""
        # Sanitize the message
        if hasattr(record, "msg") and record.msg:
            record.msg = sanitize_message(str(record.msg))

        # Format with debug info
        formatted = super().format(record)

        return sanitize_message(formatted)


class AuditFormatter(logging.Formatter):
    """Formatter for audit trail logging with structured format."""

    def __init__(self):
        # Structured format for audit logs
        fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        super().__init__(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        """Format audit record with structured layout."""
        # Sanitize the message
        if hasattr(record, "msg") and record.msg:
            record.msg = sanitize_message(str(record.msg))

        # Add audit context if available
        if hasattr(record, "audit_action"):
            record.msg = f"[{record.audit_action}] {record.msg}"

        formatted = super().format(record)

        return sanitize_message(formatted)
