# AUTO-blogger

**Copyright © 2025 AryanVBW**  
**GitHub: [https://github.com/AryanVBW](https://github.com/AryanVBW)**

A comprehensive GUI application for automating WordPress blog posting with AI-powered content generation, SEO optimization, and automatic updates.

## ✨ Key Features

🤖 **AI-Powered Content Generation**
- Automatic article scraping from source websites
- Gemini AI integration for content rewriting and paraphrasing
- SEO-optimized title and meta description generation
- **Focus Keyphrase and Additional Keyphrases extraction for SEO**
- Smart internal and external link injection
- **Enhanced WordPress SEO compatibility with Yoast and AIOSEO plugins**

🖼️ **Advanced Image Generation**
- **OpenAI DALL-E integration for AI-generated images**
- **Featured image generation** with customizable prompts
- **Content image insertion** for enhanced article visuals
- **Custom prompt support** for personalized image styles
- **Configurable image settings** (size, style, model)
- Getty Images editorial content integration
- Professional sports photography enhancement

🔄 **Auto-Update System**
- **Automatic repository cloning and updates**
- **Self-updating launcher** that checks for new versions
- **One-command installation** with dependency management
- **Cross-platform compatibility** (Windows, macOS, Linux)
- **Zero-maintenance updates** - always runs the latest version

📊 **Real-Time Progress Tracking**
- Step-by-step progress visualization
- Detailed logging with color-coded messages
- Performance metrics and timing information
- Task completion status tracking

🔐 **Secure Authentication**
- WordPress REST API integration
- Secure credential storage
- Connection testing and validation
- Multi-site support with domain-specific configurations

⚙️ **Advanced Configuration**
- Customizable source URLs and selectors
- Configurable link injection rules
- Category and tag management
- Processing timeout settings
- Domain-specific configuration profiles

📋 **Comprehensive Logging**
- Real-time log display with filtering
- Export logs to file
- Error tracking and debugging
- Performance monitoring
- Session-based log management

## 📁 Project Structure

```
AUTO-blogger/
├── 📁 configs/                 # Configuration files for different domains
├── 📁 docs/                    # Documentation and implementation guides
├── 📁 logs/                    # Session-based log files
├── 📁 scripts/                 # Utility scripts and demos
├── 📁 temp_fixes/              # Temporary fix scripts
├── 📁 tests/                   # Test files and debugging scripts
├── 🐍 autoblog_launcher.py     # Auto-update launcher with progress dialog
├── 🐍 automation_engine.py     # Core automation logic
├── 🐍 gui_blogger.py          # Main GUI application
├── 🐍 launch_blogger.py       # Application launcher
├── 🐍 log_manager.py          # Advanced logging system
├── 🔧 install_autoblog.sh     # Cross-platform installation script
├── 🚀 autoblog                # System launcher script
├── 📄 requirements.txt        # Python dependencies
├── 📄 blog_config.json        # Main configuration file (auto-created)
├── 📄 posted_links.json       # Duplicate prevention (auto-created)
└── 📄 README.md               # This file
```

## 🚀 Installation

### One-Command Installation (Recommended)

**For macOS and Linux:**
```bash
curl -sSL https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_autoblog.sh | bash
```

**For Windows (PowerShell as Administrator):**
```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_autoblog.sh -OutFile install_autoblog.sh; bash install_autoblog.sh
```

**What the installer does:**
- ✅ Detects your operating system automatically
- ✅ Installs Git, Python 3.8+, and Chrome/Chromium
- ✅ Clones the repository with auto-update capability
- ✅ Creates a virtual environment with all dependencies
- ✅ Sets up system-wide launcher (`autoblog` command)
- ✅ Creates desktop shortcuts
- ✅ Tests the installation

### Launch AUTO-blogger

After installation, start AUTO-blogger using any of these methods:

```bash
# System-wide command (if available)
autoblog

# From installation directory
./autoblog

# Desktop shortcut (double-click)
# AUTO-blogger icon on desktop
```

### Prerequisites (Auto-installed)
- Python 3.8 or higher
- Git (for auto-updates)
- Chrome/Chromium browser (for web scraping)
- WordPress site with REST API enabled
- Gemini API key
- OpenAI API key (optional, for image generation)

### Manual Installation (Advanced Users)

1. **Clone the repository**
   ```bash
   git clone https://github.com/AryanVBW/AUTO-blogger.git
   cd AUTO-blogger
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the application**
   ```bash
   python autoblog_launcher.py
   ```

## 📖 Usage

### 1. Launch the Application
```bash
autoblog  # System-wide command
# OR
./autoblog  # From installation directory
```

The application will automatically check for updates before launching.

### 2. Configure Authentication
- Go to the **🔐 Authentication** tab
- Enter your WordPress site URL (e.g., `https://yoursite.com/wp-json/wp/v2`)
- Enter your WordPress username and password
- Enter your Gemini API key
- **NEW: Enter your OpenAI API key** for image generation
- Click **Test Connection** to verify
- Click **Login & Save** to store credentials

### 3. Configure OpenAI Image Generation (Optional)
- Go to the **🖼️ OpenAI Images** tab
- Configure image settings (size, style, model)
- Set prompt prefix and suffix for consistent styling
- **Add custom prompts** for specific image styles
- Test example prompts for different image types
- Save configuration

### 4. Configure Automation Settings
- Go to the **🤖 Automation** tab
- Set the maximum number of articles to process
- **Select Featured Images option**: None, OpenAI DALL-E, or Getty Editorial
- **Select Content Images option**: None, OpenAI Generated, or Getty Editorial
- **Enable "Use Custom Prompt"** to use your custom image prompts
- Verify the source URL for article scraping
- Click **▶️ Start Automation**

### 5. Monitor Progress
- Watch real-time progress in the step tracker
- View detailed logs in the **📋 Logs** tab
- Monitor completion status and performance metrics

### 6. Advanced Configuration
- Go to the **⚙️ Configuration** tab
- Customize source URLs and CSS selectors
- Configure internal and external link rules
- Adjust processing timeouts and settings

## Configuration Options

### Source Configuration
- **Source URL**: The website to scrape articles from
- **Article Selector**: CSS selector for finding article links
- **Timeout**: Maximum time to wait for page loads

### WordPress Configuration
- **Site URL**: Your WordPress REST API endpoint
- **Username**: WordPress username with posting permissions
- **Password**: WordPress application password
- **Gemini API Key**: Google Gemini AI API key

### Link Configuration
- **Internal Links**: JSON configuration for internal site links
- **External Links**: JSON configuration for external reference links

## Process Flow

The automation follows this step-by-step process:

1. **Fetch Article Links** - Scrape source website for new articles
2. **Extract Content** - Use Selenium to extract article title and content
3. **AI Paraphrasing** - Use Gemini AI to rewrite and optimize content
4. **Inject Internal Links** - Add relevant internal site links
5. **Inject External Links** - Add authoritative external references
6. **Add Content Images** - Generate and insert AI images or Getty editorial images within article content
7. **Generate SEO Metadata** - Create optimized titles and descriptions
8. **Extract Keyphrases** - Generate focus keyphrase and additional keyphrases for SEO
9. **Process Featured Images** - Generate or source featured images using OpenAI DALL-E or Getty Images
10. **Detect Categories** - Automatically categorize content
11. **Generate Tags** - Extract and create relevant tags
12. **Create WordPress Post** - Publish as draft to WordPress with all media attached
13. **Finalize** - Complete processing and update status

## 🔄 Auto-Update System

AUTO-blogger features a sophisticated auto-update system:

- **Automatic Updates**: Every launch checks for new versions
- **Progress Dialog**: Visual feedback during update process
- **Zero Downtime**: Updates happen before application launch
- **Rollback Safety**: Git-based updates with version tracking
- **Cross-Platform**: Works on Windows, macOS, and Linux

### How Auto-Updates Work

1. **Launch Detection**: `autoblog_launcher.py` checks GitHub for updates
2. **Update Check**: Compares local and remote commit hashes
3. **Download**: Pulls latest changes via Git
4. **Progress Display**: Shows update progress with tkinter dialog
5. **Launch**: Starts the updated application automatically

## 🔧 Troubleshooting

### Installation Issues

**1. Permission Errors**
- Run installation with appropriate permissions
- On Linux/macOS: Use `sudo` if needed for system-wide installation
- On Windows: Run PowerShell as Administrator

**2. Git Not Found**
- The installer will automatically install Git
- Manual install: [https://git-scm.com/downloads](https://git-scm.com/downloads)

**3. Python Version Issues**
- Requires Python 3.8 or higher
- The installer will install compatible Python version
- Check version: `python3 --version`

### Runtime Issues

**1. Import Errors**
- Ensure virtual environment is activated
- Run `autoblog` command instead of direct Python execution
- Reinstall dependencies: `pip install -r requirements.txt`

**2. Selenium Issues**
- Chrome/Chromium browser required (auto-installed)
- ChromeDriver automatically managed by webdriver-manager
- Check firewall/antivirus blocking WebDriver

**3. WordPress Connection Issues**
- Verify REST API is enabled on your WordPress site
- Use application passwords, not regular passwords
- Check URL format: `https://yoursite.com/wp-json/wp/v2`
- Test connection in Authentication tab

**4. API Issues**
- **Gemini API**: Verify key is correct and billing is set up
- **OpenAI API**: Check quotas and usage limits
- **Rate Limits**: Application handles rate limiting automatically

**5. Auto-Update Issues**
- Ensure Git is installed and accessible
- Check internet connection
- Verify GitHub repository access
- Manual update: `git pull origin main`

### Error Logs
Check the **📋 Logs** tab for detailed error messages and debugging information. Logs are saved in the `logs/` directory.

## Security Notes

- Credentials are stored locally in `blog_config.json`
- Use WordPress application passwords instead of regular passwords
- Keep your Gemini API key secure and don't share configuration files
- The application creates draft posts for review before publishing

## 📞 Support

For issues and support:

1. **Check Logs**: Review the **📋 Logs** tab for detailed error messages
2. **Test Components**: Verify WordPress connection and API keys in respective tabs
3. **Update Check**: Ensure you're running the latest version (auto-updates on launch)
4. **Documentation**: Check the `docs/` folder for detailed guides
5. **GitHub Issues**: Report bugs at [GitHub Issues](https://github.com/AryanVBW/AUTO-blogger/issues)
6. **Email Support**: AryanVBW@gmail.com

## 🏆 Benefits

### For Content Creators
- **Time Saving**: Automate entire blog posting workflow
- **SEO Optimized**: Built-in SEO best practices and keyphrase extraction
- **Professional Quality**: AI-generated images and content
- **Multi-Site Support**: Manage multiple WordPress sites

### For Developers
- **Always Updated**: Auto-update system ensures latest features
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Extensible**: Modular design for easy customization
- **Well-Documented**: Comprehensive documentation and guides

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **GUI Framework**: Python tkinter for cross-platform interface
- **Web Scraping**: Selenium WebDriver with automatic driver management
- **AI Integration**: Google Gemini AI and OpenAI DALL-E
- **WordPress API**: REST API for seamless publishing
- **HTML Parsing**: BeautifulSoup4 for content extraction
- **Image Processing**: Pillow (PIL) for image manipulation
- **Auto-Updates**: Git-based version control and updates
