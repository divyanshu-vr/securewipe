#!/usr/bin/env python3
"""Build script for standalone certificate verifier."""

import PyInstaller.__main__

PyInstaller.__main__.run([
    'src/main.py',
    '--onefile',
    '--name=securewipe-verifier',
    '--add-data=../shared/schema;shared/schema'
])