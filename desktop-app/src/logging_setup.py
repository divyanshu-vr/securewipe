"""Logging setup for SecureWipe Desktop Application."""

import sys
from pathlib import Path

# Add shared module to path
shared_path = str(Path(__file__).parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

try:
    from .config.defaults import get_log_file_path
except ImportError:
    from config.defaults import get_log_file_path

from secure_logging.secure_logger import get_logger


def setup_application_logging(debug: bool = False) -> None:
    """Setup application-wide logging configuration.

    Args:
        debug: Enable debug logging level
    """
    log_file = get_log_file_path()

    # Create main application logger
    logger = get_logger("securewipe.desktop", debug=debug, log_file=log_file)

    # Log startup information
    logger.info("=" * 50)
    logger.info("SecureWipe Desktop Application Starting")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Log file: {log_file}")
    logger.info("=" * 50)

    return logger


def get_application_logger(name: str, debug: bool = False):
    """Get a logger for application components.

    Args:
        name: Logger name (typically __name__)
        debug: Enable debug logging

    Returns:
        Configured logger instance
    """
    log_file = get_log_file_path()
    return get_logger(name, debug=debug, log_file=log_file)
