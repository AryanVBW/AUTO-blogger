#!/usr/bin/env python3
"""
AUTO-blogger __main__ module

Allows running the package as a module:
    python -m auto_blogger

Copyright (c) 2025 AryanVBW
"""

import sys

from auto_blogger.cli import main

if __name__ == "__main__":
    sys.exit(main())
