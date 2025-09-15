#!/usr/bin/env python3
"""SecureWipe Desktop Application Entry Point."""

import argparse
import sys
from pathlib import Path

# Add shared module to path
project_root = Path(__file__).parent.parent.parent
shared_path = str(project_root / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)
    sys.path.insert(0, str(project_root))

# Import logging setup
try:
    from .logging_setup import setup_application_logging
except ImportError:
    from logging_setup import setup_application_logging

# Simple exception class
class SecureWipeError(Exception):
    """Base exception for SecureWipe application."""
    pass


def parse_arguments():
    """Parse command-line arguments for future extensibility."""
    parser = argparse.ArgumentParser(
        description="SecureWipe - Secure File Deletion System", prog="SecureWipe"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--version", action="version", version="SecureWipe 1.0.0")
    return parser.parse_args()


def main():
    """Main application entry point."""
    try:
        args = parse_arguments()

        # Setup logging first
        setup_application_logging(debug=args.debug)

        # Import UI after argument parsing to handle early exits
        try:
            from .ui.main_window import MainWindow
        except ImportError:
            from ui.main_window import MainWindow

        # Initialize and run application
        app = MainWindow(debug=args.debug)
        app.run()

    except SecureWipeError as e:
        print(f"SecureWipe Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication interrupted by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
