# WordPress Blog Automation Suite

**Copyright © 2025 AryanVBW**  
**GitHub: [https://github.com/AryanVBW](https://github.com/AryanVBW)**

A comprehensive GUI application for automating WordPress blog posting with AI-powered content generation and SEO optimization.

## Features

🤖 **AI-Powered Content Generation**
- Automatic article scraping from source websites
- Gemini AI integration for content rewriting and paraphrasing
- SEO-optimized title and meta description generation
- **NEW: Focus Keyphrase and Additional Keyphrases extraction for SEO**
- Smart internal and external link injection
- **Enhanced WordPress SEO compatibility with Yoast and AIOSEO plugins**

🖼️ **Advanced Image Generation**
- **NEW: OpenAI DALL-E integration for AI-generated images**
- **Featured image generation** with customizable prompts
- **Content image insertion** for enhanced article visuals
- **Custom prompt support** for personalized image styles
- **Configurable image settings** (size, style, model)
- Getty Images editorial content integration
- Professional sports photography enhancement

📊 **Real-Time Progress Tracking**
- Step-by-step progress visualization
- Detailed logging with color-coded messages
- Performance metrics and timing information
- Task completion status tracking

🔐 **Secure Authentication**
- WordPress REST API integration
- Secure credential storage
- Connection testing and validation
- Multi-site support

⚙️ **Advanced Configuration**
- Customizable source URLs and selectors
- Configurable link injection rules
- Category and tag management
- Processing timeout settings

📋 **Comprehensive Logging**
- Real-time log display with filtering
- Export logs to file
- Error tracking and debugging
- Performance monitoring

## Installation

### Quick Installation (One-Line Command)

```bash
# For macOS and Linux:
curl -sSL https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_auto_blogger.sh | bash

# For Windows (Run in PowerShell as Administrator):
Invoke-WebRequest -Uri https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_auto_blogger.sh -OutFile install_auto_blogger.sh; bash install_auto_blogger.sh
```

After installation, you can start AUTO-blogger by typing `autoV` in your terminal.

### Prerequisites
- Python 3.7 or higher
- Chrome browser (for web scraping)
- WordPress site with REST API enabled
- Gemini API key

### Quick Start

1. **Clone or download the files to a directory**
   ```bash
   git clone <repository-url>
   cd AUTO-blogger
   ```

2. **Install dependencies (automatic)**
   ```bash
   python launch_blogger.py
   ```
   The launcher will automatically detect and install missing requirements.

3. **Manual installation (if needed)**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Launch the Application
```bash
python launch_blogger.py
```

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

### 4. Monitor Progress
- Watch real-time progress in the step tracker
- View detailed logs in the **📋 Logs** tab
- Monitor completion status and performance metrics

### 5. Advanced Configuration
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

## File Structure

```
AUTO-blogger/
├── launch_blogger.py      # Main launcher script
├── gui_blogger.py         # GUI application code
├── automation_engine.py   # Core automation logic
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── blog_config.json      # Configuration storage (auto-created)
└── posted_links.json     # Duplicate prevention (auto-created)
```

## Troubleshooting

### Common Issues

**1. Import Errors**
- Ensure all files are in the same directory
- Run `python launch_blogger.py` instead of direct GUI launch
- Install requirements: `pip install -r requirements.txt`

**2. Selenium Issues**
- Ensure Chrome browser is installed
- ChromeDriver will be automatically downloaded
- Check firewall/antivirus blocking WebDriver

**3. WordPress Connection Issues**
- Verify REST API is enabled on your WordPress site
- Use application passwords, not regular passwords
- Check URL format: `https://yoursite.com/wp-json/wp/v2`

**4. Gemini API Issues**
- Verify API key is correct and active
- Check API quotas and usage limits
- Ensure billing is set up for Gemini API

### Error Logs
Check the **📋 Logs** tab for detailed error messages and debugging information.

## Security Notes

- Credentials are stored locally in `blog_config.json`
- Use WordPress application passwords instead of regular passwords
- Keep your Gemini API key secure and don't share configuration files
- The application creates draft posts for review before publishing

## Support

For issues and support:
1. Check the logs tab for detailed error messages
2. Verify all prerequisites are installed
3. Test individual components (WordPress connection, Gemini API)
4. Check the configuration settings

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python tkinter for the GUI
- Uses Selenium for web scraping
- Integrates Google Gemini AI for content generation
- WordPress REST API for publishing
- BeautifulSoup for HTML parsing
# AUTO-blogger
