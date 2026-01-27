# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Professional project structure with commercial-grade organization
- Cross-platform setup scripts (`setup.sh`, `setup.bat`, `setup.ps1`)
- Makefile for common development operations
- Run scripts for easy application launching (`run.sh`, `run.bat`)
- Environment configuration template (`.env.example`)
- Comprehensive pre-commit configuration
- CLI module with subcommands (`autoblog info`, `autoblog check`, etc.)
- Proper test directory structure with unit and integration tests
- Type hints support marker (`py.typed`)
- Separated requirements files (`requirements/base.txt`, `requirements/dev.txt`, `requirements/test.txt`)
- Modern `pyproject.toml` with comprehensive tool configurations
- `setup.cfg` for flake8 and metadata configuration

### Changed
- Updated `pyproject.toml` to modern Python packaging standards
- Enhanced `.gitignore` with comprehensive ignore rules
- Reorganized project structure following Python best practices

## [1.0.0] - 2025-01-15

### Added
- Initial release of AUTO-blogger
- AI-powered content generation using Google Gemini
- OpenAI DALL-E image generation integration
- Getty Images integration for editorial sports photography
- WordPress REST API integration with multi-domain support
- Professional Tkinter GUI with multi-tab interface
- SEO optimization with keyphrase extraction
- Auto-update system via Git
- Session-based logging with multiple log categories
- CSS selector auto-detection for article scraping
- British English spelling enforcement
- Internal and external link injection
- Category and tag automatic detection
- PyPI package distribution

### Security
- Local credential storage only
- WordPress application password support
- Draft-only posting for manual review
- Secure HTTPS connections

## [0.1.0] - 2024-12-01

### Added
- Initial development version
- Basic WordPress automation
- Selenium web scraping
- Simple content extraction

[Unreleased]: https://github.com/AryanVBW/AUTO-blogger/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/AryanVBW/AUTO-blogger/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/AryanVBW/AUTO-blogger/releases/tag/v0.1.0
