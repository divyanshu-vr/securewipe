"""OWASP-compliant secure logging for SecureWipe."""

import logging
import sys
from pathlib import Path
from typing import Optional

from .sanitizer import sanitize_message
from .formatters import SecureFormatter


def get_logger(name: str, debug: bool = False, log_file: Optional[Path] = None) -> logging.Logger:
    """Get a configured secure logger instance.
    
    Args:
        name: Logger name (typically __name__)
        debug: Enable debug logging level
        log_file: Optional log file path
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Set logging level
    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)
    
    # Create formatter
    formatter = SecureFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)  # Always debug level for file
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except OSError as e:
            # Log to console if file logging fails
            logger.warning(f"Could not create log file {log_file}: {e}")
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


class SecureLogger:
    """Secure logger wrapper with automatic sanitization."""
    
    def __init__(self, name: str, debug: bool = False, log_file: Optional[Path] = None):
        self.logger = get_logger(name, debug, log_file)
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message with sanitization."""
        sanitized = sanitize_message(message)
        self.logger.debug(sanitized, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message with sanitization."""
        sanitized = sanitize_message(message)
        self.logger.info(sanitized, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message with sanitization."""
        sanitized = sanitize_message(message)
        self.logger.warning(sanitized, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message with sanitization."""
        sanitized = sanitize_message(message)
        self.logger.error(sanitized, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message with sanitization."""
        sanitized = sanitize_message(message)
        self.logger.critical(sanitized, *args, **kwargs)