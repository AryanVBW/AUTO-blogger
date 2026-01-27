#!/usr/bin/env python3
"""
AUTO-blogger CLI Module

Command-line interface for AUTO-blogger.
Provides both GUI and CLI access to the automation tool.

Copyright (c) 2025 AryanVBW
"""

import argparse
import sys
from pathlib import Path


def get_version() -> str:
    """Get the package version."""
    try:
        from auto_blogger import __version__
        return __version__
    except ImportError:
        return "unknown"


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="autoblog",
        description="AUTO-blogger - AI-Powered WordPress Automation Tool",
        epilog="For more information, visit: https://github.com/AryanVBW/AUTO-blogger",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"AUTO-blogger {get_version()}",
        help="Show version and exit",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (can be repeated)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )

    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Run in headless/CLI mode (if available)",
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to configuration file",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # GUI command (default)
    gui_parser = subparsers.add_parser("gui", help="Launch the GUI application")
    gui_parser.add_argument(
        "--theme",
        choices=["light", "dark", "system"],
        default="system",
        help="GUI theme",
    )

    # Info command
    info_parser = subparsers.add_parser("info", help="Show system information")
    info_parser.add_argument(
        "--full",
        action="store_true",
        help="Show detailed system information",
    )

    # Config command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_parser.add_argument(
        "--show",
        action="store_true",
        help="Show current configuration",
    )
    config_parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset configuration to defaults",
    )
    config_parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate configuration",
    )

    # Check command
    check_parser = subparsers.add_parser("check", help="Check system requirements")
    check_parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix issues",
    )

    return parser


def show_info(full: bool = False) -> int:
    """Show system information."""
    import platform

    print("\n=== AUTO-blogger System Information ===\n")
    print(f"Version: {get_version()}")
    print(f"Python: {platform.python_version()}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Machine: {platform.machine()}")

    if full:
        print("\n=== Dependencies ===\n")
        dependencies = [
            "requests",
            "beautifulsoup4",
            "selenium",
            "openai",
            "google.generativeai",
            "PIL",
            "colorama",
            "tqdm",
        ]

        for dep in dependencies:
            try:
                if dep == "PIL":
                    import PIL
                    print(f"  Pillow: {PIL.__version__}")
                elif dep == "google.generativeai":
                    import google.generativeai
                    print(f"  google-generativeai: OK")
                elif dep == "beautifulsoup4":
                    import bs4
                    print(f"  beautifulsoup4: {bs4.__version__}")
                else:
                    module = __import__(dep)
                    version = getattr(module, "__version__", "OK")
                    print(f"  {dep}: {version}")
            except ImportError:
                print(f"  {dep}: NOT INSTALLED")

    print()
    return 0


def check_requirements(fix: bool = False) -> int:
    """Check system requirements."""
    print("\n=== Checking System Requirements ===\n")

    issues = []

    # Check Python version
    import sys
    if sys.version_info < (3, 8):
        issues.append(f"Python 3.8+ required, found {sys.version}")
    else:
        print(f"[OK] Python version: {sys.version_info.major}.{sys.version_info.minor}")

    # Check tkinter
    try:
        import tkinter
        print("[OK] tkinter available")
    except ImportError:
        issues.append("tkinter not installed (required for GUI)")

    # Check Chrome/Chromium
    import shutil
    chrome_found = False
    for browser in ["google-chrome", "chromium", "chromium-browser"]:
        if shutil.which(browser):
            chrome_found = True
            print(f"[OK] Browser found: {browser}")
            break

    if not chrome_found:
        # Check common paths on macOS/Windows
        import platform
        if platform.system() == "Darwin":
            if Path("/Applications/Google Chrome.app").exists():
                chrome_found = True
                print("[OK] Chrome found at /Applications/Google Chrome.app")
        elif platform.system() == "Windows":
            chrome_paths = [
                Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
                Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
            ]
            for path in chrome_paths:
                if path.exists():
                    chrome_found = True
                    print(f"[OK] Chrome found at {path}")
                    break

    if not chrome_found:
        issues.append("Chrome/Chromium not found (required for web automation)")

    # Check core dependencies
    core_deps = [
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"),
        ("selenium", "selenium"),
        ("openai", "openai"),
        ("google-generativeai", "google.generativeai"),
        ("Pillow", "PIL"),
    ]

    for name, module in core_deps:
        try:
            __import__(module)
            print(f"[OK] {name}")
        except ImportError:
            issues.append(f"{name} not installed")

    print()

    if issues:
        print("=== Issues Found ===\n")
        for issue in issues:
            print(f"  [!] {issue}")
        print()

        if fix:
            print("Attempting to fix issues...")
            import subprocess
            for issue in issues:
                if "not installed" in issue:
                    package = issue.split()[0]
                    try:
                        subprocess.run(
                            [sys.executable, "-m", "pip", "install", package],
                            check=True,
                        )
                        print(f"  [FIXED] Installed {package}")
                    except subprocess.CalledProcessError:
                        print(f"  [FAILED] Could not install {package}")

        return 1

    print("All requirements satisfied!")
    return 0


def run_gui() -> int:
    """Run the GUI application."""
    try:
        from auto_blogger.gui_blogger import main
        return main() or 0
    except ImportError as e:
        print(f"Error: Could not import GUI components: {e}")
        print("Please ensure all dependencies are installed:")
        print("  pip install auto-blogger")
        return 1


def main(args: list = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Set debug mode
    if parsed_args.debug:
        import os
        os.environ["AUTO_BLOGGER_DEBUG"] = "1"

    # Handle commands
    if parsed_args.command == "info":
        return show_info(full=parsed_args.full)

    if parsed_args.command == "check":
        return check_requirements(fix=parsed_args.fix)

    if parsed_args.command == "config":
        if parsed_args.show:
            # Show configuration
            config_path = Path.home() / ".auto_blogger" / "config.json"
            if config_path.exists():
                print(config_path.read_text())
            else:
                print("No configuration file found.")
            return 0

        if parsed_args.reset:
            print("Configuration reset is not yet implemented.")
            return 1

        if parsed_args.validate:
            print("Configuration validation is not yet implemented.")
            return 1

        print("Use --show, --reset, or --validate")
        return 1

    # Default: run GUI
    if not parsed_args.no_gui:
        return run_gui()

    print("CLI mode is not yet fully implemented.")
    print("Please run without --no-gui to use the GUI application.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
