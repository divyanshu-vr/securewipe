#!/usr/bin/env python3
"""
Script to fix shared module imports in all desktop-app files.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix shared module imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if no shared imports
        if 'from shared.' not in content:
            return False
        
        # Replace the sys.path.append line
        content = re.sub(
            r'sys\.path\.append\(str\(Path\(__file__\)\.parent.*?"shared"\)\)',
            'shared_path = Path(__file__).parent.parent.parent.parent / "shared"\nsys.path.insert(0, str(shared_path))',
            content
        )
        
        # Replace shared.models imports
        content = re.sub(r'from shared\.models\.', 'from models.', content)
        
        # Replace shared.secure_logging imports
        content = re.sub(r'from shared\.secure_logging\.', 'from secure_logging.', content)
        
        # Replace shared.utils imports
        content = re.sub(r'from shared\.utils\.', 'from utils.', content)
        
        # Replace shared.crypto imports
        content = re.sub(r'from shared\.crypto\.', 'from crypto.', content)
        
        # Replace shared.schema imports
        content = re.sub(r'from shared\.schema\.', 'from schema.', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix imports in all Python files."""
    src_dir = Path("src")
    fixed_count = 0
    
    for py_file in src_dir.rglob("*.py"):
        if fix_imports_in_file(py_file):
            print(f"Fixed imports in: {py_file}")
            fixed_count += 1
    
    print(f"\nFixed imports in {fixed_count} files.")

if __name__ == "__main__":
    main()