# AUTO-blogger - AI-Powered WordPress Automation Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/auto-blogger.svg)](https://badge.fury.io/py/auto-blogger)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/AryanVBW/AUTO-blogger)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub stars](https://img.shields.io/github/stars/AryanVBW/AUTO-blogger?style=social)](https://github.com/AryanVBW/AUTO-blogger/stargazers)

**Copyright (c) 2025 AryanVBW**

| Website | Documentation | Issues |
|---------|---------------|--------|
| [aryanvbw.github.io/AUTO-blogger](https://aryanvbw.github.io/AUTO-blogger/website/) | [Documentation](https://aryanvbw.github.io/AUTO-blogger/website/documentation.html) | [GitHub Issues](https://github.com/AryanVBW/AUTO-blogger/issues) |

> **Transform your WordPress content strategy with intelligent automation!**
>
> AUTO-blogger is a professional-grade WordPress automation tool that combines the power of AI content generation, Getty Images integration, and comprehensive SEO optimization.

---

## Quick Start

### Installation

```bash
# Install from PyPI (Recommended)
pip install auto-blogger

# Launch the application
autoblog
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/AryanVBW/AUTO-blogger.git
cd AUTO-blogger

# Run the setup script
./setup.sh          # macOS/Linux
setup.bat           # Windows CMD
.\setup.ps1         # Windows PowerShell

# Or for development
./setup.sh --dev
```

### Using Make (Development)

```bash
make help           # Show all available commands
make dev-setup      # Set up development environment
make run            # Run the application
make test           # Run tests
make lint           # Run linters
make format         # Format code
```

---

## Features

### AI-Powered Content Generation
- Automatic article scraping from source websites
- Gemini AI integration for content rewriting and paraphrasing
- SEO-optimized title and meta description generation
- Focus keyphrase and additional keyphrases extraction
- Smart internal and external link injection
- WordPress SEO compatibility (Yoast, AIOSEO)

### Advanced Image Generation
- OpenAI DALL-E integration for AI-generated images
- Featured image generation with customizable prompts
- Content image insertion for enhanced visuals
- Getty Images editorial content integration
- Professional sports photography enhancement

### Auto-Update System
- Automatic repository updates on launch
- Self-updating launcher with progress dialog
- Cross-platform compatibility (Windows, macOS, Linux)
- Git-based version control with rollback safety

### Real-Time Monitoring
- Step-by-step progress visualization
- Detailed logging with color-coded messages
- Performance metrics and timing information
- Export logs to file

### Multi-Domain Support
- Domain-specific configuration profiles
- Multi-site management from one interface
- Secure credential storage per domain

---

## Project Structure

```
AUTO-blogger/
├── auto_blogger/           # Main Python package
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Module entry point
│   ├── automation_engine.py # Core automation logic
│   ├── gui_blogger.py      # GUI application
│   ├── cli.py              # CLI interface
│   ├── log_manager.py      # Logging utilities
│   ├── css_selector_extractor.py
│   └── configs/            # Configuration files
│       ├── default.json
│       ├── gemini_prompts.json
│       ├── category_keywords.json
│       └── ...
│
├── tests/                  # Test suite
│   ├── conftest.py         # Pytest fixtures
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
│
├── requirements/           # Dependency files
│   ├── base.txt            # Core dependencies
│   ├── dev.txt             # Development dependencies
│   └── test.txt            # Test dependencies
│
├── docs/                   # Documentation
├── scripts/                # Utility scripts
├── website/                # GitHub Pages site
│
├── setup.sh                # Unix setup script
├── setup.bat               # Windows CMD setup script
├── setup.ps1               # Windows PowerShell setup script
├── run.sh                  # Unix run script
├── run.bat                 # Windows run script
├── Makefile                # Development automation
│
├── pyproject.toml          # Modern Python packaging config
├── setup.py                # Legacy setup (for compatibility)
├── setup.cfg               # Additional configuration
├── requirements.txt        # Dependencies (points to requirements/)
│
├── .env.example            # Environment template
├── .pre-commit-config.yaml # Pre-commit hooks
├── .gitignore              # Git ignore rules
│
├── README.md               # This file
├── CHANGELOG.md            # Version history
├── CONTRIBUTING.md         # Contribution guidelines
└── LICENSE                 # MIT License
```

---

## Installation Methods

### 1. PyPI Installation (Recommended)

```bash
pip install auto-blogger
autoblog
```

### 2. One-Command Installation

**macOS/Linux:**
```bash
curl -sSL https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install.sh | bash
```

**Windows PowerShell:**
```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install.sh -OutFile install.sh; bash install.sh
```

### 3. Development Installation

```bash
# Clone
git clone https://github.com/AryanVBW/AUTO-blogger.git
cd AUTO-blogger

# Setup with dev dependencies
./setup.sh --dev

# Activate environment
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows

# Install pre-commit hooks
pre-commit install
```

### Prerequisites

- Python 3.8 or higher
- Chrome/Chromium browser (for web scraping)
- WordPress site with REST API enabled
- Gemini API key
- OpenAI API key (optional, for image generation)

---

## Usage

### Command Line Interface

```bash
# Launch GUI (default)
autoblog

# Show version
autoblog --version

# Show system info
autoblog info
autoblog info --full

# Check requirements
autoblog check
autoblog check --fix

# Run with debug mode
autoblog --debug
```

### Running with Make

```bash
make run        # Run the GUI application
make run-gui    # Run the GUI explicitly
make run-cli    # Run CLI mode
```

### Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your API keys
```

Key environment variables:
- `WORDPRESS_URL` - Your WordPress site URL
- `WORDPRESS_USERNAME` - WordPress username
- `WORDPRESS_APP_PASSWORD` - WordPress application password
- `GEMINI_API_KEY` - Google Gemini AI API key
- `OPENAI_API_KEY` - OpenAI API key (optional)

---

## Development

### Setup

```bash
# Full development setup
./setup.sh --dev

# Or using Make
make dev-setup
```

### Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run fast tests only
make test-fast
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Type checking
make type-check

# All checks
make check
```

### Building

```bash
# Build distribution
make build

# Upload to PyPI
make upload

# Upload to TestPyPI
make upload-test
```

---

## Process Flow

The automation follows these steps:

1. **Fetch Article Links** - Scrape source website for new articles
2. **Extract Content** - Use Selenium to extract article title and content
3. **AI Paraphrasing** - Use Gemini AI to rewrite and optimize content
4. **Inject Internal Links** - Add relevant internal site links
5. **Inject External Links** - Add authoritative external references
6. **Add Content Images** - Generate and insert images within content
7. **Generate SEO Metadata** - Create optimized titles and descriptions
8. **Extract Keyphrases** - Generate focus and additional keyphrases
9. **Process Featured Images** - Generate or source featured images
10. **Detect Categories** - Automatically categorize content
11. **Generate Tags** - Extract and create relevant tags
12. **Create WordPress Post** - Publish as draft with all media
13. **Finalize** - Complete processing and update status

---

## Configuration

### Source Configuration
- **Source URL**: Website to scrape articles from
- **Article Selector**: CSS selector for article links
- **Timeout**: Maximum page load wait time

### WordPress Configuration
- **Site URL**: WordPress REST API endpoint
- **Username**: WordPress username with posting permissions
- **Password**: WordPress application password
- **API Key**: Gemini AI API key

### Image Configuration
- **OpenAI Model**: DALL-E 2 or DALL-E 3
- **Image Size**: 256x256 to 1792x1024
- **Style**: Vivid or Natural

---

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements/base.txt
```

**Selenium Issues:**
- Chrome/Chromium browser required
- ChromeDriver automatically managed by webdriver-manager

**WordPress Connection:**
- Verify REST API is enabled
- Use application passwords (not regular passwords)
- Check URL format: `https://yoursite.com/wp-json/wp/v2`

**API Issues:**
- Verify API keys are correct
- Check quota and usage limits
- Application handles rate limiting automatically

### Logs

Check the `logs/` directory or the Logs tab in the GUI for detailed error messages.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

### Quick Start

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/AUTO-blogger.git
cd AUTO-blogger

# Setup development environment
./setup.sh --dev

# Create feature branch
git checkout -b feature/your-feature

# Make changes, test, and submit PR
make test
make lint
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **GUI Framework**: Python tkinter
- **Web Scraping**: Selenium WebDriver
- **AI Integration**: Google Gemini AI, OpenAI DALL-E
- **WordPress API**: REST API
- **HTML Parsing**: BeautifulSoup4
- **Image Processing**: Pillow (PIL)

---

## Support

- **Documentation**: [aryanvbw.github.io/AUTO-blogger](https://aryanvbw.github.io/AUTO-blogger/website/)
- **Issues**: [GitHub Issues](https://github.com/AryanVBW/AUTO-blogger/issues)
- **Email**: AryanVBW@gmail.com
