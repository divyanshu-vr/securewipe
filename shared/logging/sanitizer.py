"""Data sanitization utilities for secure logging."""

import re
from pathlib import Path
from typing import Union


def sanitize_path(path: Union[str, Path]) -> str:
    """Sanitize file path for logging by removing sensitive information.
    
    Args:
        path: File path to sanitize
        
    Returns:
        Sanitized path string safe for logging
    """
    if not path:
        return "<empty_path>"
    
    path_str = str(path)
    
    # Replace username in paths
    path_str = re.sub(r'\\Users\\[^\\]+', r'\\Users\\<user>', path_str)
    path_str = re.sub(r'/home/[^/]+', r'/home/<user>', path_str)
    
    # Replace full paths with relative indicators
    if len(path_str) > 100:
        # Show only filename and parent directory
        try:
            p = Path(path_str)
            return f".../{p.parent.name}/{p.name}"
        except:
            return f"<long_path:{len(path_str)}_chars>"
    
    return path_str


def sanitize_message(message: str) -> str:
    """Sanitize log message to remove sensitive information.
    
    Args:
        message: Log message to sanitize
        
    Returns:
        Sanitized message safe for logging
    """
    if not message:
        return ""
    
    # Remove potential file paths
    sanitized = re.sub(r'[A-Za-z]:\\[^\\s]+', lambda m: sanitize_path(m.group()), message)
    sanitized = re.sub(r'/[^\\s]+', lambda m: sanitize_path(m.group()), sanitized)
    
    # Remove potential email addresses
    sanitized = re.sub(r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b', '<email>', sanitized)
    
    # Remove potential IP addresses
    sanitized = re.sub(r'\\b(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b', '<ip_address>', sanitized)
    
    # Remove potential phone numbers
    sanitized = re.sub(r'\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b', '<phone>', sanitized)
    
    # Remove potential credit card numbers (basic pattern)
    sanitized = re.sub(r'\\b\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}\\b', '<card_number>', sanitized)
    
    return sanitized


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for logging while preserving extension.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "<empty_filename>"
    
    try:
        path = Path(filename)
        name = path.stem
        ext = path.suffix
        
        # Keep first and last 2 characters of name, replace middle with asterisks
        if len(name) <= 4:
            sanitized_name = "*" * len(name)
        else:
            sanitized_name = name[:2] + "*" * (len(name) - 4) + name[-2:]
        
        return sanitized_name + ext
    except:
        return "<invalid_filename>"


def sanitize_error_message(error: Exception) -> str:
    """Sanitize exception message for logging.
    
    Args:
        error: Exception to sanitize
        
    Returns:
        Sanitized error message
    """
    error_msg = str(error)
    
    # Sanitize any paths in error message
    sanitized = sanitize_message(error_msg)
    
    # Keep error type but sanitize message
    error_type = type(error).__name__
    
    return f"{error_type}: {sanitized}"