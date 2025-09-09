#!/usr/bin/env python3
"""Quick certificate validation script."""

import subprocess
import sys
from pathlib import Path

def main():
    """Run certificate compatibility tests."""
    test_file = Path(__file__).parent.parent / "shared" / "tests" / "test_certificate_compatibility.py"
    
    try:
        result = subprocess.run([sys.executable, str(test_file)], 
                              capture_output=True, text=True, check=True)
        print("Certificate compatibility tests PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print("Certificate compatibility tests FAILED")
        print(e.stdout)
        print(e.stderr)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)