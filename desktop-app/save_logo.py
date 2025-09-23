#!/usr/bin/env python3
"""
Script to help save the WipeX logo to the assets folder.

Instructions:
1. Save the WipeX logo image as 'wipex_logo.png' in the assets folder
2. The image should be PNG format with transparent background
3. Recommended size: 120x120 pixels or larger

The logo will be automatically resized to 80x80 pixels in the application.
"""

import os
from pathlib import Path

def main():
    assets_dir = Path(__file__).parent / "assets"
    logo_path = assets_dir / "wipex_logo.png"
    
    print(f"Assets directory: {assets_dir}")
    print(f"Expected logo path: {logo_path}")
    
    if logo_path.exists():
        print("✓ WipeX logo found!")
        print(f"  File size: {logo_path.stat().st_size} bytes")
    else:
        print("✗ WipeX logo not found.")
        print("\nPlease save the WipeX logo image as 'wipex_logo.png' in the assets folder.")
        print("The application will use a text fallback until the image is available.")

if __name__ == "__main__":
    main()