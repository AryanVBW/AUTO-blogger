#!/usr/bin/env python3
"""
Integration Tests for Configuration

Tests for configuration file loading and validation.

Copyright (c) 2025 AryanVBW
"""

import json
from pathlib import Path

import pytest


class TestConfigurationFiles:
    """Test configuration file loading."""

    def test_default_config_exists(self, configs_dir):
        """Test that default.json exists."""
        config_path = configs_dir / "default.json"
        assert config_path.exists(), f"default.json not found at {config_path}"

    def test_default_config_valid_json(self, configs_dir):
        """Test that default.json is valid JSON."""
        config_path = configs_dir / "default.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            assert isinstance(config, dict)

    def test_gemini_prompts_exists(self, configs_dir):
        """Test that gemini_prompts.json exists."""
        config_path = configs_dir / "gemini_prompts.json"
        assert config_path.exists(), f"gemini_prompts.json not found at {config_path}"

    def test_gemini_prompts_valid_json(self, configs_dir):
        """Test that gemini_prompts.json is valid JSON."""
        config_path = configs_dir / "gemini_prompts.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            assert isinstance(config, dict)

    def test_category_keywords_exists(self, configs_dir):
        """Test that category_keywords.json exists."""
        config_path = configs_dir / "category_keywords.json"
        assert config_path.exists(), f"category_keywords.json not found at {config_path}"

    def test_all_config_files_valid_json(self, configs_dir):
        """Test that all JSON config files are valid."""
        if not configs_dir.exists():
            pytest.skip("configs directory not found")

        for config_file in configs_dir.glob("*.json"):
            try:
                with open(config_file) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {config_file.name}: {e}")


class TestProjectStructure:
    """Test project structure."""

    def test_auto_blogger_package_exists(self, project_root):
        """Test that auto_blogger package exists."""
        package_dir = project_root / "auto_blogger"
        assert package_dir.exists()
        assert package_dir.is_dir()

    def test_init_file_exists(self, project_root):
        """Test that __init__.py exists."""
        init_file = project_root / "auto_blogger" / "__init__.py"
        assert init_file.exists()

    def test_automation_engine_exists(self, project_root):
        """Test that automation_engine.py exists."""
        engine_file = project_root / "auto_blogger" / "automation_engine.py"
        assert engine_file.exists()

    def test_gui_blogger_exists(self, project_root):
        """Test that gui_blogger.py exists."""
        gui_file = project_root / "auto_blogger" / "gui_blogger.py"
        assert gui_file.exists()

    def test_requirements_files_exist(self, project_root):
        """Test that requirements files exist."""
        assert (project_root / "requirements.txt").exists() or \
               (project_root / "requirements" / "base.txt").exists()

    def test_setup_files_exist(self, project_root):
        """Test that setup files exist."""
        # Check for either modern or legacy setup
        has_pyproject = (project_root / "pyproject.toml").exists()
        has_setup_py = (project_root / "setup.py").exists()
        assert has_pyproject or has_setup_py

    def test_readme_exists(self, project_root):
        """Test that README exists."""
        readme_paths = [
            project_root / "README.md",
            project_root / "README.rst",
            project_root / "README.txt",
        ]
        assert any(p.exists() for p in readme_paths)

    def test_license_exists(self, project_root):
        """Test that LICENSE file exists."""
        license_paths = [
            project_root / "LICENSE",
            project_root / "LICENSE.txt",
            project_root / "LICENSE.md",
        ]
        assert any(p.exists() for p in license_paths)
