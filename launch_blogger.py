#!/usr/bin/env python3
"""
AUTO-blogger Launch Script
Copyright © 2025 AryanVBW
GitHub: https://github.com/AryanVBW/AUTO-blogger

This script launches the AUTO-blogger GUI application.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

def main():
    """Main function to launch the GUI"""
    try:
        # Import and run the GUI
        from gui_blogger import main as gui_main
        print("🚀 Starting AUTO-blogger GUI...")
        gui_main()
    except ImportError as e:
        print(f"❌ Failed to import GUI module: {e}")
        print("Please ensure all dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Error launching AUTO-blogger: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()