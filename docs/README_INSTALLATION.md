# AUTO-blogger - Automated WordPress Blog Posting Tool

🚀 **Automated WordPress Blog Posting Tool with AI Integration**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/AryanVBW/AUTO-blogger)](https://github.com/AryanVBW/AUTO-blogger/issues)

## 📋 Table of Contents

- [Features](#-features)
- [Quick Installation](#-quick-installation)
- [Manual Installation](#-manual-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

## ✨ Features

- 🤖 **AI-Powered Content Generation** - OpenAI DALL-E image generation
- 🔄 **Auto-Update System** - Automatically checks and updates from GitHub repository
- 📦 **One-Click Installation** - Clone repository and setup everything automatically
- 📝 **Automated Blog Posting** - Direct WordPress integration
- 🎨 **Getty Images Integration** - Professional stock photos
- 🔍 **SEO Optimization** - Automated meta tags and keywords
- 🌐 **Multi-Domain Support** - Manage multiple WordPress sites
- 📊 **Real-time Logging** - Track all operations with detailed logs
- 🖥️ **User-Friendly GUI** - Easy-to-use graphical interface
- ⚡ **Web Scraping** - Automated content sourcing
- 🔧 **Highly Configurable** - Customizable for different use cases

## 🚀 Quick Installation

### One-Command Installation (Recommended)

The installation script will automatically:
- Clone the repository from GitHub
- Install all dependencies
- Set up virtual environment
- Create system-wide launcher with auto-update
- Create desktop shortcuts

```bash
# Download and run the installation script
curl -fsSL https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_autoblog.sh | bash
```

**Or download and run manually:**

```bash
# Download the installation script
wget https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_autoblog.sh
# or
curl -O https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_autoblog.sh

# Make it executable and run
chmod +x install_autoblog.sh
./install_autoblog.sh
```

After installation, simply type `autoblog` in your terminal to launch the application!

### What the installer does:

1. **🔍 Checks and installs Git** (if not available)
2. **📥 Clones the repository** to `~/AUTO-blogger`
3. **🐍 Installs Python** (if not available)
4. **🌐 Installs Chrome browser** (for web automation)
5. **📦 Creates virtual environment** with all dependencies
6. **🚀 Creates system launcher** with auto-update functionality
7. **🖥️ Creates desktop shortcuts** (where supported)

## 🛠️ Manual Installation

### Prerequisites

- **Python 3.8+** (with tkinter support)
- **Chrome or Chromium browser** (for web automation)
- **Git** (for cloning the repository)

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/AryanVBW/AUTO-blogger.git
cd AUTO-blogger
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

#### 4. Install Chrome/Chromium (if not already installed)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install google-chrome-stable
# OR
sudo apt-get install chromium-browser
```

**macOS:**
```bash
brew install --cask google-chrome
# OR
brew install --cask chromium
```

**CentOS/RHEL/Fedora:**
```bash
sudo dnf install chromium
# OR
sudo yum install chromium
```

#### 5. Create Launcher (Optional)

```bash
# Make the main script executable
chmod +x gui_blogger.py

# Create a simple launcher script
echo '#!/bin/bash' > autoblog
echo 'cd "$(dirname "$0")"' >> autoblog
echo 'source venv/bin/activate' >> autoblog
echo 'python gui_blogger.py' >> autoblog
chmod +x autoblog
```

## 🎯 Usage

### Starting the Application

After installation, you can start AUTO-blogger in several ways. **The application will automatically check for updates each time it launches!**

**Method 1: Using the system command (after automated installation)**
```bash
autoblog
```

**Method 2: Using the local launcher**
```bash
cd ~/AUTO-blogger
./autoblog
```

**Method 3: Direct Python execution**
```bash
source venv/bin/activate  # Activate virtual environment
python gui_blogger.py
```

### Auto-Update Feature

🔄 **Automatic Updates**: Every time you launch AUTO-blogger, it will:
- Check for updates from the GitHub repository
- Download and apply updates automatically if available
- Show a progress dialog during the update process
- Launch the updated application

This ensures you always have the latest features and bug fixes!

### First-Time Setup

1. **Launch the application**
2. **Configure WordPress credentials** in the Settings tab
3. **Set up API keys** (OpenAI, Google Gemini) if using AI features
4. **Configure domain-specific settings** for your WordPress site
5. **Test the connection** using the built-in test features

### Basic Workflow

1. 🔧 **Configure your WordPress site** credentials
2. 🎯 **Select content sources** (URLs, RSS feeds, etc.)
3. 🤖 **Enable AI features** (optional) for enhanced content
4. ▶️ **Start the automation** process
5. 📊 **Monitor progress** in real-time logs
6. ✅ **Review posted content** on your WordPress site

## ⚙️ Configuration

### WordPress Configuration

```json
{
  "wordpress_url": "https://yoursite.com",
  "wordpress_username": "your_username",
  "wordpress_password": "your_app_password",
  "default_category": "General",
  "default_status": "publish"
}
```

### AI Configuration (Optional)

```json
{
  "openai_api_key": "your_openai_api_key",
  "gemini_api_key": "your_gemini_api_key",
  "image_generation": true,
  "content_enhancement": true
}
```

### Domain-Specific Configurations

The application supports multiple domain configurations stored in the `configs/` directory:

- `configs/default.json` - Default settings
- `configs/yourdomain_com/` - Domain-specific settings
- `configs/yourdomain_com/credentials.json` - Domain credentials
- `configs/yourdomain_com/style_prompt.json` - Writing style settings

## 🔧 Troubleshooting

### Common Issues

#### "No module named 'openai'" Error

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall OpenAI package
pip install --upgrade openai

# Verify installation
python -c "import openai; print('OpenAI installed successfully')"
```

#### Chrome/Selenium Issues

**Solution:**
```bash
# Update webdriver-manager
pip install --upgrade webdriver-manager

# Clear webdriver cache
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
```

#### Permission Denied on macOS/Linux

**Solution:**
```bash
# Make scripts executable
chmod +x install_autoblog.sh
chmod +x autoblog

# If system-wide installation fails, use local launcher
./autoblog
```

#### Virtual Environment Issues

**Solution:**
```bash
# Remove and recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Getting Help

1. **Check the logs** in the `logs/` directory
2. **Review configuration files** in the `configs/` directory
3. **Test individual components** using the test scripts in `tests/`
4. **Open an issue** on GitHub with detailed error information

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/AryanVBW/AUTO-blogger.git
cd AUTO-blogger

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Run tests
pytest tests/

# Format code
black .

# Lint code
flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Email:** AryanVBW@gmail.com
- **GitHub Issues:** [Report a Bug](https://github.com/AryanVBW/AUTO-blogger/issues)
- **GitHub Discussions:** [Ask Questions](https://github.com/AryanVBW/AUTO-blogger/discussions)

## 🌟 Star History

If you find this project useful, please consider giving it a star on GitHub!

[![Star History Chart](https://api.star-history.com/svg?repos=AryanVBW/AUTO-blogger&type=Date)](https://star-history.com/#AryanVBW/AUTO-blogger&Date)

---

**Made with ❤️ by [AryanVBW](https://github.com/AryanVBW)**

*Happy Blogging! 🚀*