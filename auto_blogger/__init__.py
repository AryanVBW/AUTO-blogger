#!/usr/bin/env python3
"""
AUTO-blogger - AI-Powered WordPress Automation Tool

A comprehensive WordPress automation tool that combines AI content generation,
Getty Images integration, and comprehensive SEO optimization.

Copyright (c) 2025 AryanVBW
GitHub: https://github.com/AryanVBW/AUTO-blogger
License: MIT
"""

__version__ = "1.0.0"
__author__ = "AryanVBW"
__email__ = "AryanVBW@gmail.com"
__description__ = "Automated WordPress Blog Posting Tool with AI Integration"
__url__ = "https://github.com/AryanVBW/AUTO-blogger"
__license__ = "MIT"

# Import main components for easy access
try:
    from .gui_blogger import BlogAutomationGUI, main
    from .automation_engine import BlogAutomationEngine
    from .log_manager import SessionLogManager
    from .css_selector_extractor import CSSelectorExtractor
except ImportError as e:
    # Handle import errors gracefully (e.g., missing tkinter)
    import warnings
    warnings.warn(f"Some components could not be imported: {e}")

    # Define fallback main function
    def main():
        """Fallback main function when GUI components unavailable."""
        try:
            from .gui_blogger import main as gui_main
            return gui_main()
        except ImportError:
            print("Error: Could not import GUI components.")
            print("Please ensure all dependencies are installed:")
            print("  pip install auto-blogger")
            return 1

    # Define placeholder classes
    BlogAutomationGUI = None
    BlogAutomationEngine = None
    SessionLogManager = None
    CSSelectorExtractor = None


def cli_main():
    """
    Console script entry point.

    This function is called when running `autoblog` or `auto-blogger`
    from the command line.
    """
    from .cli import main as cli_entry
    import sys
    sys.exit(cli_entry())


def get_version():
    """Return the package version."""
    return __version__


# Package metadata
__all__ = [
    # Classes
    "BlogAutomationGUI",
    "BlogAutomationEngine",
    "SessionLogManager",
    "CSSelectorExtractor",
    # Functions
    "main",
    "cli_main",
    "get_version",
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "__url__",
    "__license__",
]