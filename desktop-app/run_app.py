#!/usr/bin/env python3
"""SecureWipe Desktop Application Launcher."""

import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Add shared module to path
shared_path = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(shared_path))

# Now import and run the main application
if __name__ == "__main__":
    from main import main
    main()