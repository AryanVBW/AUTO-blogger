#!/usr/bin/env python3
"""
Unit Tests for Package Imports

Tests to ensure all package components can be imported correctly.

Copyright (c) 2025 AryanVBW
"""

import pytest


class TestPackageImports:
    """Test package imports."""

    def test_import_package(self):
        """Test that the main package can be imported."""
        import auto_blogger
        assert auto_blogger is not None

    def test_package_version(self):
        """Test that package version is defined."""
        from auto_blogger import __version__
        assert __version__ is not None
        assert isinstance(__version__, str)
        # Version should be in semver format (x.y.z)
        parts = __version__.split(".")
        assert len(parts) >= 2

    def test_package_metadata(self):
        """Test that package metadata is defined."""
        from auto_blogger import __author__, __email__, __url__
        assert __author__ is not None
        assert __email__ is not None
        assert __url__ is not None

    def test_import_automation_engine(self):
        """Test that automation engine can be imported."""
        from auto_blogger import automation_engine
        assert automation_engine is not None

    def test_import_automation_engine_class(self):
        """Test that BlogAutomationEngine class can be imported."""
        from auto_blogger.automation_engine import BlogAutomationEngine
        assert BlogAutomationEngine is not None

    def test_import_log_manager(self):
        """Test that log manager can be imported."""
        from auto_blogger import log_manager
        assert log_manager is not None

    def test_import_css_selector_extractor(self):
        """Test that CSS selector extractor can be imported."""
        from auto_blogger.css_selector_extractor import CSSelectorExtractor
        assert CSSelectorExtractor is not None

    def test_import_cli(self):
        """Test that CLI module can be imported."""
        from auto_blogger import cli
        assert cli is not None
        assert hasattr(cli, "main")

    @pytest.mark.gui
    def test_import_gui_blogger(self):
        """Test that GUI blogger can be imported."""
        try:
            from auto_blogger import gui_blogger
            assert gui_blogger is not None
        except ImportError as e:
            if "tkinter" in str(e).lower():
                pytest.skip("tkinter not available")
            raise


class TestMainFunction:
    """Test main function and entry points."""

    def test_cli_main_exists(self):
        """Test that cli_main function exists."""
        from auto_blogger import cli_main
        assert cli_main is not None
        assert callable(cli_main)

    def test_main_exists(self):
        """Test that main function exists."""
        from auto_blogger import main
        assert main is not None
        assert callable(main)


class TestAllExports:
    """Test that __all__ exports are valid."""

    def test_all_exports_exist(self):
        """Test that all items in __all__ can be accessed."""
        import auto_blogger

        if hasattr(auto_blogger, "__all__"):
            for name in auto_blogger.__all__:
                assert hasattr(auto_blogger, name), f"Missing export: {name}"
