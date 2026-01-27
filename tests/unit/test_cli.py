#!/usr/bin/env python3
"""
Unit Tests for CLI Module

Tests for command-line interface functionality.

Copyright (c) 2025 AryanVBW
"""

import sys
from unittest.mock import patch

import pytest

from auto_blogger.cli import create_parser, get_version, main, show_info


class TestCLIParser:
    """Test CLI argument parser."""

    def test_create_parser(self):
        """Test that parser can be created."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "autoblog"

    def test_version_argument(self):
        """Test --version argument."""
        parser = create_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])
        assert exc_info.value.code == 0

    def test_help_argument(self):
        """Test --help argument."""
        parser = create_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--help"])
        assert exc_info.value.code == 0

    def test_debug_argument(self):
        """Test --debug argument."""
        parser = create_parser()
        args = parser.parse_args(["--debug"])
        assert args.debug is True

    def test_verbose_argument(self):
        """Test -v argument."""
        parser = create_parser()
        args = parser.parse_args(["-v"])
        assert args.verbose == 1

        args = parser.parse_args(["-vv"])
        assert args.verbose == 2

    def test_gui_subcommand(self):
        """Test gui subcommand."""
        parser = create_parser()
        args = parser.parse_args(["gui"])
        assert args.command == "gui"

    def test_info_subcommand(self):
        """Test info subcommand."""
        parser = create_parser()
        args = parser.parse_args(["info"])
        assert args.command == "info"

    def test_info_full_option(self):
        """Test info --full option."""
        parser = create_parser()
        args = parser.parse_args(["info", "--full"])
        assert args.command == "info"
        assert args.full is True

    def test_check_subcommand(self):
        """Test check subcommand."""
        parser = create_parser()
        args = parser.parse_args(["check"])
        assert args.command == "check"

    def test_config_subcommand(self):
        """Test config subcommand."""
        parser = create_parser()
        args = parser.parse_args(["config", "--show"])
        assert args.command == "config"
        assert args.show is True


class TestCLIFunctions:
    """Test CLI functions."""

    def test_get_version(self):
        """Test get_version function."""
        version = get_version()
        assert version is not None
        assert isinstance(version, str)

    def test_show_info(self, capsys):
        """Test show_info function."""
        result = show_info(full=False)
        assert result == 0

        captured = capsys.readouterr()
        assert "AUTO-blogger" in captured.out
        assert "Version" in captured.out
        assert "Python" in captured.out

    def test_show_info_full(self, capsys):
        """Test show_info with full option."""
        result = show_info(full=True)
        assert result == 0

        captured = capsys.readouterr()
        assert "Dependencies" in captured.out


class TestCLIMain:
    """Test main CLI function."""

    def test_main_info_command(self):
        """Test main with info command."""
        result = main(["info"])
        assert result == 0

    def test_main_check_command(self):
        """Test main with check command."""
        # This may return 0 or 1 depending on system setup
        result = main(["check"])
        assert result in [0, 1]

    @patch("auto_blogger.cli.run_gui")
    def test_main_default_runs_gui(self, mock_run_gui):
        """Test that default command runs GUI."""
        mock_run_gui.return_value = 0
        result = main([])
        mock_run_gui.assert_called_once()
        assert result == 0

    def test_main_no_gui_option(self, capsys):
        """Test --no-gui option."""
        result = main(["--no-gui"])
        assert result == 1  # CLI mode not fully implemented

        captured = capsys.readouterr()
        assert "CLI mode" in captured.out or "not yet" in captured.out

    def test_main_debug_sets_env(self, monkeypatch):
        """Test that --debug sets environment variable."""
        import os

        monkeypatch.delenv("AUTO_BLOGGER_DEBUG", raising=False)

        with patch("auto_blogger.cli.run_gui", return_value=0):
            main(["--debug"])

        assert os.environ.get("AUTO_BLOGGER_DEBUG") == "1"
