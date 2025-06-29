#!/usr/bin/env python3
"""
Core automation engine for WordPress blog posting
Contains all the core functionality from the original script

Copyright © 2025 AryanVBW
GitHub: https://github.com/AryanVBW
"""

import re
import requests
import logging
import json
import os
import urllib.parse
import hashlib
import traceback
import time
import base64
from typing import Optional, Tuple, List, Dict, Set
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from contextlib import contextmanager
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError, RequestException
import unicodedata
import time

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class BlogAutomationEngine:
    """Core automation engine for blog posting"""
    
    def __init__(self, config: Dict, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.posted_links_file = "posted_links.json"
        
        # Use domain-specific config directory if provided, otherwise default
        self.config_dir = config.get('config_dir', "configs")
        
        # Initialize configurations
        self.setup_configurations()
        
    def setup_configurations(self):
        """Setup all configuration dictionaries"""
        
        # Category keywords mapping
        self.CATEGORY_KEYWORDS = self.load_json_config(
            "category_keywords.json",
            {
                "academy": "Academy",
                "analysis": "Analysis",
                "champions league": "Champions League",
                "europa league": "Europa League",
                "exclusive": "Exclusive",
                "fa cup": "FA Cup",
                "fantasy premier league": "Fantasy Premier League",
                "injury update": "Injury News",
                "injury": "Injury News",
                "international": "International",
                "league cup": "League Cup",
                "loan watch": "Loan Watch",
                "match preview": "Match Preview",
                "match report": "Match Report",
                "player profile": "Player Profile",
                "premier league derbies": "Premier League Derbies",
                "transfer news": "Transfer News",
                "transfer": "Transfer News",
                "deal": "Transfer News",
                "sign": "Transfer News",
                "join": "Transfer News",
                "agree": "Transfer News",
                "reaction": "Exclusive",
                "fans share": "Exclusive",
                "derby": "Premier League Derbies",
            }
        )
        
        # Internal links
        self.INTERNAL_LINKS = self.load_json_config(
            "internal_links.json",
            {}
        )
        
        # External links
        self.EXTERNAL_LINKS = self.load_json_config(
            "external_links.json",
            {}
        )
        
        # Static clubs for tag generation
        self.STATIC_CLUBS = set(self.load_json_config(
            "static_clubs.json",
            []
        ))
        
        # Tag synonyms
        self.TAG_SYNONYMS = self.load_json_config(
            "tag_synonyms.json",
            {}
        )
        
        # Stop words for slug generation
        self.STOP_WORDS = set(self.load_json_config(
            "stop_words.json",
            []
        ))
        
        # Do-follow URLs
        self.DO_FOLLOW_URLS = set(self.load_json_config(
            "do_follow_urls.json",
            []
        ))
        
        # Style prompt for Gemini
        self.STYLE_PROMPT = self.load_json_config(
            "style_prompt.json",
            {"style_prompt": ""}
        )["style_prompt"]
        
        # Load Gemini prompts configuration
        self.GEMINI_PROMPTS = self.load_json_config(
            "gemini_prompts.json",
            {
                "style_prompt": "",
                "seo_title_meta_prompt": "",
                "tag_generation_prompt": "",
                "keyphrase_extraction_prompt": "",
                "post_processing_replacements": {}
            }
        )
        
        # Custom SEO Keywords configuration
        self.CUSTOM_SEO_KEYWORDS = self.load_json_config(
            "custom_seo_keywords.json",
            {
                "enabled": False,
                "custom_keywords": {
                    "focus_keywords": [],
                    "additional_keywords": [],
                    "team_specific_keywords": {},
                    "competition_keywords": [],
                    "seasonal_keywords": []
                },
                "keyword_settings": {
                    "max_focus_keywords_per_article": 2,
                    "max_additional_keywords_per_article": 8,
                    "combine_with_auto_keywords": True,
                    "prioritize_custom_keywords": False,
                    "auto_select_team_keywords": True,
                    "auto_select_competition_keywords": True
                }
            }
        )
        
    def load_json_config(self, filename, default):
        """Load JSON configuration file with proper error handling"""
        path = os.path.join(self.config_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.logger.debug(f"✅ Successfully loaded {filename}")
                    return data
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON decode error in {filename}: {e}")
            except Exception as e:
                self.logger.error(f"Error loading {filename}: {e}")
        else:
            self.logger.warning(f"Config file not found: {filename}, using defaults")
        return default

    def load_posted_links(self) -> Set[str]:
        """Load previously posted article links from file"""
        try:
            if os.path.exists(self.posted_links_file):
                with open(self.posted_links_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Handle both old format (list) and new format (object)
                    if isinstance(data, list):
                        self.logger.info("Converting old posted_links format to new format")
                        return set(data)
                    elif isinstance(data, dict):
                        return set(data.get('posted_links', []))
                    else:
                        self.logger.warning("Unexpected posted_links format, returning empty set")
                        return set()
            return set()
        except Exception as e:
            self.logger.error(f"Error loading posted links: {e}")
            return set()

    def save_posted_links(self, posted_links: Set[str]):
        """Save posted article links to file"""
        try:
            data = {
                'posted_links': list(posted_links),
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(self.posted_links_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved {len(posted_links)} posted links to {self.posted_links_file}")
        except Exception as e:
            self.logger.error(f"Error saving posted links: {e}")

    @contextmanager
    def get_selenium_driver_context(self):
        """Context manager for Chrome WebDriver with improved error handling"""
        driver_instance = None
        try:
            # Check if Selenium is available
            if not SELENIUM_AVAILABLE:
                self.logger.error("❌ Selenium not available. Please install selenium and webdriver-manager")
                yield None
                return
            
            self.logger.info("🔄 Initializing Chrome WebDriver...")
            
            # Install ChromeDriver with permission fix
            try:
                driver_path = ChromeDriverManager().install()
                self.logger.info(f"📁 ChromeDriver installed at: {driver_path}")
                
                # Ensure ChromeDriver is executable (fix for macOS permissions)
                import stat
                import os
                try:
                    current_permissions = os.stat(driver_path).st_mode
                    os.chmod(driver_path, current_permissions | stat.S_IEXEC)
                    self.logger.info("✅ ChromeDriver permissions updated")
                except Exception as perm_error:
                    self.logger.warning(f"⚠️ Could not update ChromeDriver permissions: {perm_error}")
                
                service = Service(driver_path)
            except Exception as e:
                self.logger.error(f"❌ Failed to install ChromeDriver: {e}")
                self.logger.info("💡 Try running: pip install --upgrade webdriver-manager")
                yield None
                return
            
            # Configure Chrome options with macOS ARM64 compatibility
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-logging')
            options.add_argument('--log-level=3')
            options.add_argument('--incognito')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--remote-debugging-port=0')  # Use random port
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-ipc-flooding-protection')
            options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Suppress Chrome logs and automation detection
            options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option('detach', True)
            
            # macOS specific fixes
            import platform
            if platform.system() == 'Darwin':  # macOS
                options.add_argument('--disable-features=TranslateUI')
                options.add_argument('--disable-default-apps')
                options.add_argument('--disable-component-extensions-with-background-pages')
            
            # Initialize WebDriver
            driver_instance = webdriver.Chrome(service=service, options=options)
            driver_instance.set_page_load_timeout(30)
            
            self.logger.info("✅ Chrome WebDriver initialized successfully")
            yield driver_instance
            
        except WebDriverException as e:
            self.logger.error(f"❌ WebDriver error: {e}")
            self.logger.info("💡 Troubleshooting tips:")
            self.logger.info("   • Ensure Chrome browser is installed")
            self.logger.info("   • Check internet connection for ChromeDriver download")
            self.logger.info("   • Try updating Chrome browser")
            yield None
            
        except Exception as e:
            self.logger.error(f"❌ Unexpected error initializing WebDriver: {e}")
            self.logger.exception("Full error details:")
            yield None
            
        finally:
            if driver_instance:
                try:
                    self.logger.debug("🔄 Closing WebDriver...")
                    driver_instance.quit()
                    self.logger.debug("✅ WebDriver closed successfully")
                except Exception as e:
                    self.logger.warning(f"⚠️ Error closing WebDriver: {e}")

    def get_latest_article_link(self) -> Optional[str]:
        """Fetches the most recent article link"""
        try:
            source_url = self.config.get('source_url', '')
            selector = self.config.get('article_selector', '')
            
            resp = requests.get(source_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.content, "html.parser")
            tag = soup.select_one(selector)
            
            if not tag or not tag.get("href"):
                self.logger.warning(f"⚠️ No link found with selector '{selector}' on {source_url}")
                return None

            return urljoin(source_url, tag["href"])
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Error fetching page {source_url}: {e}")
            return None

    def get_article_links(self, limit: int = 10) -> List[str]:
        """Get multiple article links from source"""
        try:
            source_url = self.config.get('source_url', '')
            selector = self.config.get('article_selector', '')
            
            if not source_url:
                self.logger.error("❌ No source URL configured")
                return []
                
            if not selector:
                self.logger.error("❌ No article selector configured")
                return []
            
            self.logger.info(f"🔗 Fetching articles from: {source_url}")
            self.logger.info(f"🎯 Using selector: {selector}")
            
            # Add headers to mimic a real browser
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            
            resp = requests.get(source_url, headers=headers, timeout=15)
            resp.raise_for_status()
            
            self.logger.info(f"✅ Successfully fetched page (Status: {resp.status_code})")
            
            soup = BeautifulSoup(resp.content, "html.parser")
            tags = soup.select(selector)
            
            self.logger.info(f"🔍 Found {len(tags)} elements matching selector")
            
            if len(tags) == 0:
                # Try alternative selectors with TBR Football specific ones
                alternative_selectors = [
                    "article h2 a",
                    "article h3 a",
                    "h2 a",
                    "h3 a",
                    ".post-title a",
                    ".entry-title a",
                    ".article-title a",
                    "a[href*='tbrfootball.com']",
                    "a[href*='/post/']",
                    "a[href*='/article/']",
                    "a[href*='/news/']",
                    ".post a",
                    ".entry a",
                    ".content a[href*='tbrfootball']"
                ]
                
                self.logger.warning(f"⚠️ No articles found with selector '{selector}', trying alternatives...")
                
                for alt_selector in alternative_selectors:
                    alt_tags = soup.select(alt_selector)
                    if alt_tags:
                        # Filter to only include TBR Football links
                        valid_tags = []
                        for tag in alt_tags:
                            href = tag.get("href", "")
                            if href and ("tbrfootball.com" in href or href.startswith("/")):
                                valid_tags.append(tag)
                        
                        if valid_tags:
                            self.logger.info(f"✅ Found {len(valid_tags)} valid articles with alternative selector: {alt_selector}")
                            tags = valid_tags
                            break
                        else:
                            self.logger.debug(f"Found {len(alt_tags)} links with '{alt_selector}' but none were TBR Football articles")
                
                if not tags:
                    self.logger.error("❌ No articles found with any selector")
                    # Enhanced debugging - log page structure and available links
                    self.logger.info("🔍 Debugging page structure...")
                    
                    # Check for any links that might be articles
                    all_links = soup.find_all('a', href=True)
                    tbr_links = [link for link in all_links if 'tbrfootball.com' in link.get('href', '') or link.get('href', '').startswith('/')]
                    
                    self.logger.info(f"Total links found: {len(all_links)}")
                    self.logger.info(f"TBR Football related links: {len(tbr_links)}")
                    
                    # Show sample of TBR links
                    for i, link in enumerate(tbr_links[:5]):
                        href = link.get('href')
                        text = link.get_text().strip()[:50]
                        self.logger.info(f"TBR Link {i+1}: {href} - {text}")
                    
                    # Show page structure sample
                    articles = soup.find_all(['article', 'div', 'section'], class_=True, limit=5)
                    for i, article in enumerate(articles):
                        classes = ' '.join(article.get('class', []))
                        self.logger.info(f"Container {i+1} classes: {classes}")
                        links_in_container = article.find_all('a', href=True)
                        self.logger.info(f"  Links in container: {len(links_in_container)}")
                    
                    return []
            
            links = []
            for i, tag in enumerate(tags):
                href = tag.get("href")
                if href:
                    # Handle relative URLs
                    if href.startswith('/'):
                        full_url = urljoin(source_url, href)
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        full_url = urljoin(source_url, href)
                    
                    # Validate URL and avoid duplicates
                    if full_url not in links and self.is_valid_article_url(full_url):
                        links.append(full_url)
                        self.logger.debug(f"Added article {len(links)}: {full_url}")
                        
                if len(links) >= limit:
                    break
            
            self.logger.info(f"✅ Successfully extracted {len(links)} article links")
            return links
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Network error fetching article links: {e}")
            return []
        except Exception as e:
            self.logger.error(f"❌ Error fetching article links: {e}")
            return []

    def is_valid_article_url(self, url: str) -> bool:
        """Check if URL looks like a valid article URL"""
        try:
            # Basic validation
            if not url or len(url) < 10:
                return False
                
            # Must be HTTP/HTTPS
            if not url.startswith(('http://', 'https://')):
                return False
            
            url_lower = url.lower()
            
            # For TBR Football, be more specific about what constitutes an article
            if 'tbrfootball.com' in url_lower:
                # TBR Football specific validation
                # Accept URLs that look like articles
                valid_patterns = [
                    '/post/',
                    '/news/',
                    '/article/',
                    '/football/',
                    '/premier-league/',
                    '/transfer',
                    '/analysis'
                ]
                
                # Check if URL contains article-like patterns
                has_valid_pattern = any(pattern in url_lower for pattern in valid_patterns)
                
                # Avoid obvious non-article URLs
                invalid_patterns = [
                    'javascript:', 'mailto:', '#', '/tag/', '/category/', 
                    '/author/', '/page/', '/search/', '/login', '/register',
                    '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.pdf',
                    '/topic/english-premier-league/' # Avoid the main topic page
                ]
                
                has_invalid_pattern = any(pattern in url_lower for pattern in invalid_patterns)
                
                # For TBR Football, either accept if it has valid pattern or if it doesn't have invalid patterns
                if has_valid_pattern and not has_invalid_pattern:
                    return True
                elif not has_invalid_pattern and len(url) > 30:  # Likely an article if it's a longer URL
                    return True
                else:
                    return False
            else:
                # Generic validation for other sites
                invalid_patterns = [
                    'javascript:', 'mailto:', '#', 'tag/', 'category/', 
                    'author/', 'page/', 'search/', 'login', 'register',
                    '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.pdf'
                ]
                
                for pattern in invalid_patterns:
                    if pattern in url_lower:
                        return False
                        
            return True
            
        except Exception:
            return False

    def extract_article_with_selenium(self, driver: 'webdriver.Chrome', url: str, timeout: int = 15) -> Tuple[Optional[str], Optional[str]]:
        """Extract article content using Selenium with improved error handling"""
        if not driver:
            self.logger.error("❌ No WebDriver provided for content extraction")
            return None, None
            
        if not url:
            self.logger.error("❌ No URL provided for content extraction")
            return None, None

        self.logger.info(f"🔄 Extracting content from: {url}")
        
        try:
            # Navigate to the page
            driver.get(url)
            wait = WebDriverWait(driver, timeout)
            
            # Wait for page to load
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self.logger.debug("✅ Page loaded successfully")

            # Extract title with multiple selectors
            title = None
            title_selectors = ["h1", ".entry-title", ".post-title", "[class*='title']", "title"]
            
            for selector in title_selectors:
                try:
                    title_el = driver.find_element(By.CSS_SELECTOR, selector)
                    if title_el and title_el.text.strip():
                        title = title_el.text.strip()
                        self.logger.debug(f"✅ Title found with selector: {selector}")
                        break
                except:
                    continue
            
            if not title:
                self.logger.warning("⚠️ Could not extract title from page")
                title = "Untitled Article"

            # Extract content with multiple strategies
            content = None
            content_selectors = [
                "article p",
                ".entry-content p", 
                ".post-content p",
                ".content p",
                "[class*='content'] p",
                "main p",
                "p"
            ]
            
            for selector in content_selectors:
                try:
                    paras = driver.find_elements(By.CSS_SELECTOR, selector)
                    if paras and len(paras) >= 3:  # Ensure we have substantial content
                        content_texts = [p.text.strip() for p in paras if p.text.strip() and len(p.text.strip()) > 20]
                        if content_texts:
                            content = "\n\n".join(content_texts)
                            self.logger.debug(f"✅ Content found with selector: {selector} ({len(content_texts)} paragraphs)")
                            break
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not content:
                self.logger.warning("⚠️ Could not extract meaningful content from page")
                # Try to get any text content as fallback
                try:
                    body = driver.find_element(By.TAG_NAME, "body")
                    content = body.text[:1000] + "..." if len(body.text) > 1000 else body.text
                    self.logger.info("ℹ️ Using fallback content extraction")
                except:
                    content = "Content extraction failed"

            # Validate extracted content
            if title and content and len(content) > 100:
                self.logger.info(f"✅ Successfully extracted: '{title[:50]}...' ({len(content)} chars)")
                return title, content
            else:
                self.logger.warning(f"⚠️ Extracted content may be incomplete: title={bool(title)}, content_length={len(content) if content else 0}")
                return title, content

        except TimeoutException:
            self.logger.error(f"❌ Page load timeout ({timeout}s) for {url}")
            self.logger.info("💡 Try increasing timeout or check if the website is accessible")
            return None, None
            
        except WebDriverException as e:
            self.logger.error(f"❌ WebDriver error during extraction: {e}")
            self.logger.info("💡 This might be due to page structure changes or network issues")
            return None, None
            
        except Exception as e:
            self.logger.error(f"❌ Unexpected error during content extraction: {e}")
            self.logger.exception("Full error details:")
            return None, None

    def sentence_case(self, text: str) -> str:
        """Convert text to sentence case"""
        if not text:
            return text

        words = text.split()
        if not words:
            return text

        # Capitalize first word
        words[0] = words[0].capitalize()

        # Process remaining words
        processed_words = [words[0]]
        for word in words[1:]:
            if word.isupper() or (len(word) > 1 and word[0].isupper()):
                processed_words.append(word)
            else:
                processed_words.append(word.lower())

        return ' '.join(processed_words)

    def post_process_text(self, text: str) -> str:
        """Apply targeted capitalization rules and clean markdown artifacts"""
        if not text:
            return text
        
        # Remove markdown code blocks that might be accidentally included
        # Remove ````html (4 backticks) patterns
        text = re.sub(r'````html\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*````\s*', '', text, flags=re.IGNORECASE)
        # Remove ```html (3 backticks) patterns
        text = re.sub(r'```html\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*```\s*', '', text, flags=re.IGNORECASE)
        # Remove any remaining backtick patterns
        text = re.sub(r'`{3,4}[a-zA-Z]*\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*`{3,4}\s*', '', text, flags=re.IGNORECASE)
        
        # Clean up any extra whitespace that might result from removing code blocks
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Replace multiple newlines with double newlines
        text = text.strip()  # Remove leading/trailing whitespace
        
        # Load replacements from configuration or use default
        replacements = self.GEMINI_PROMPTS.get("post_processing_replacements", {
            r'\bpremier league\b': 'Premier League',
            r'\bthe premier league\b': 'the Premier League',
            r'\bchampionship\b': 'Championship',
            r'\bchampions league\b': 'Champions League',
            r'\bfa cup\b': 'FA Cup',
            r'\bleague cup\b': 'League Cup',
            r'\bcarabao cup\b': 'Carabao Cup',
            r'\bserie a\b': 'Serie A',
            r'\bbundesliga\b': 'Bundesliga',
            r'\blaliga\b': 'La Liga',
            r'\bligue 1\b': 'Ligue 1',
            r'\bworld cup\b': 'World Cup',
            r'\beuros\b': 'Euros',
            r'\buefa\b': 'UEFA',
            r'\bfifa\b': 'FIFA',
            r'\bvar\b': 'VAR',
            r'\bpl\b': 'PL',
            r'\belland road\b': 'Elland Road',
            r'\bleeds united\b': 'Leeds United',
            r'\btottenham hotspur\b': 'Tottenham Hotspur',
            r'\bmanchester united\b': 'Manchester United',
            r'\bmanchester city\b': 'Manchester City'
        })

        # Apply replacements using regex for whole word matching and case-insensitivity
        for lower_term, correct_term in replacements.items():
            text = re.sub(lower_term, correct_term, text, flags=re.IGNORECASE)

        return text

    def gemini_paraphrase_content_and_title(self, original_title: str, article_html: str) -> Tuple[str, str]:
        """Use enhanced Gemini prompts from Jupyter notebook to paraphrase content and generate title"""
        
        # Use the enhanced style prompt from configuration
        style_prompt = self.GEMINI_PROMPTS.get("style_prompt", "")
        
        if not style_prompt:
            # Fallback to basic prompt if not configured
            style_prompt = """You are a skilled Premier League football blogger. Rewrite the provided HTML article content into a clean, engaging, and SEO-optimized blog post for football fans.

**CONTENT REWRITE RULES:**
1. Begin with 2–3 exciting, punchy introductory sentences highlighting the central story
2. Insert exactly 2 or 3 `<h3>` headings in sentence case
3. Maintain a confident, energetic, fan-first tone
4. Use active voice in at least 90% of sentences
5. Keep sentences under 15 words
6. Use short paragraphs with 2–3 sentences maximum
7. Wrap every paragraph in `<p>` tags
8. Conclude with Author's take, Conclusion, or What's next heading
9. Minimum 400 words
10. Use simple, everyday football language

**HEADLINE GENERATION RULES:**
- Generate exactly one headline
- Avoid specific player or manager names in headline
- Use indirect identifiers like "25yo winger", "veteran midfielder"
- Make it curiosity-driven and indirect
- Use sentence case only
- No quotes or punctuation marks"""

        prompt = f"""
{style_prompt}

Original title:
\"\"\"{original_title}\"\"\"

Original HTML content:
\"\"\"{article_html}\"\"\"

---

Return format:
CONTENT:
<rewritten HTML>

HEADLINE:
<rewritten headline>
"""

        try:
            gemini_api_key = self.config.get('gemini_api_key', '')
            if not gemini_api_key:
                raise ValueError("Gemini API key not configured")
                
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {"contents": [{"parts": [{"text": prompt}]}]}

            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            # Add error handling for API response structure
            response_data = response.json()
            if not response_data.get("candidates") or len(response_data["candidates"]) == 0:
                self.logger.error("Empty or invalid Gemini API response for paraphrasing")
                raise ValueError("Invalid API response structure")
                
            if not response_data["candidates"][0].get("content") or not response_data["candidates"][0]["content"].get("parts") or len(response_data["candidates"][0]["content"]["parts"]) == 0:
                self.logger.error("Invalid content structure in Gemini API response for paraphrasing")
                raise ValueError("Invalid content structure in API response")

            text = response_data["candidates"][0]["content"]["parts"][0].get("text", "")
            content_match = re.search(r"CONTENT:\s*(.*?)\s*HEADLINE:", text, re.DOTALL)
            headline_match = re.search(r"HEADLINE:\s*(.+)", text)

            if not content_match or not headline_match:
                self.logger.error("Gemini response missing expected sections")
                # Fallback generation
                seo_title = original_title[:59] if len(original_title) > 59 else original_title
                clean_content = re.sub(r'<[^>]+>', '', article_html)
                meta_desc = clean_content[:157] + "..." if len(clean_content) > 157 else clean_content
                return seo_title, meta_desc

            html = content_match.group(1).strip()
            headline_raw = headline_match.group(1).strip()

            # Apply the enhanced post-processing from Jupyter notebook
            processed_html = self.post_process_text(html)
            processed_headline_raw = self.post_process_text(headline_raw)

            # Apply sentence case specifically for the headline
            final_headline = self.sentence_case(processed_headline_raw)

            self.logger.info(f"✅ Gemini paraphrasing completed - Title: {final_headline[:50]}...")
            return processed_html, final_headline

        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Gemini API request error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Error in Gemini paraphrasing: {e}")
            return article_html, original_title

    def inject_internal_links(self, content: str) -> str:
        """Inject internal links into content"""
        linked_keys = set()
        parts = re.split(r'(<h3>.*?</h3>)', content, flags=re.DOTALL)

        for i, part in enumerate(parts):
            if part.startswith("<h3>"):
                continue
                
            current_part_modified = part
            for key, url in self.INTERNAL_LINKS.items():
                low_key = key.lower()
                if low_key in linked_keys:
                    continue

                pattern = re.compile(rf'(?<!href=")\b{re.escape(key)}\b', flags=re.IGNORECASE)

                def repl(m):
                    linked_keys.add(low_key)
                    return f'<a href="{url}">{m.group(0)}</a>'

                new_part, count = pattern.subn(repl, current_part_modified, count=1)
                if count:
                    current_part_modified = new_part

            parts[i] = current_part_modified

        self.logger.info(f"Injected {len(linked_keys)} internal links")
        return "".join(parts)

    def inject_external_links(self, content: str) -> str:
        """Inject external links into content"""
        linked_urls = set()
        segments = re.split(r'(<h3>.*?</h3>|<a.*?</a>)', content, flags=re.IGNORECASE | re.DOTALL)

        for i, segment in enumerate(segments):
            if segment.lower().startswith("<h3>") or segment.lower().startswith("<a"):
                continue

            current_segment_modified = segment
            for phrase, url in self.EXTERNAL_LINKS.items():
                if url in linked_urls:
                    continue

                pattern = re.compile(rf'\b({re.escape(phrase)})\b', flags=re.IGNORECASE)

                def _replacer(match):
                    linked_urls.add(url)
                    rel_attr = "noopener" if url in self.DO_FOLLOW_URLS else "nofollow noopener"
                    return f'<a href="{url}" target="_blank" rel="{rel_attr}">{match.group(1)}</a>'

                new_segment, count = pattern.subn(_replacer, current_segment_modified, count=1)
                if count:
                    current_segment_modified = new_segment

            segments[i] = current_segment_modified

        self.logger.info(f"Injected {len(linked_urls)} external links")
        return "".join(segments)

    def generate_seo_title_and_meta(self, title: str, content: str) -> Tuple[str, str]:
        """Generate SEO title and meta description using enhanced Jupyter notebook implementation"""
        if not title or not content:
            self.logger.error("Both title and content are required for SEO generation")
            return title, ""

        try:
            gemini_api_key = self.config.get('gemini_api_key', '')
            if not gemini_api_key:
                # Fallback to simple generation
                seo_title = title[:59] if len(title) > 59 else title
                clean_content = re.sub(r'<[^>]+>', '', content)
                meta_desc = clean_content[:157] + "..." if len(clean_content) > 157 else clean_content
                self.logger.warning("No Gemini API key - using fallback SEO generation")
                return seo_title, meta_desc

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"

            # Use the configurable prompt from GEMINI_PROMPTS
            prompt = self.GEMINI_PROMPTS.get('seo_title_meta_prompt', '')
            if not prompt:
                # Fallback to default prompt if not configured
                prompt = f"""You are a passionate Premier League football blogger.

1. Read the article content below and identify its one primary subject (player, event, or transfer saga). Then rewrite the original title into a single, sharp, SEO-friendly headline.

- Preserve the correct capitalization of all proper nouns exactly as in the original.
- Use sentence case—capitalize only the first word and proper nouns. All other words should be lowercase. **Example: Tottenham: Should Spurs chase Kudus over Crystal Palace's target?**
- The headline must be **strictly** between 50 and 59 characters in length (counting spaces and punctuation).
- **Crucially, your final output must be precisely within this character range. Do NOT go under 50 characters or over 59 characters.**
- Ensure the headline is a grammatically complete and coherent sentence within the character limits.
- Always use British English spelling for 'rumours' (with a 'u').

2. Write an SEO meta description for the article:

- Include 2–3 relevant keywords from the article.
- No hashtags or special formatting.
- Must be between 155 and 160 characters (inclusive).
- Return plain text only, with no quotes or extra spaces.
- Always use British English spelling for 'rumours' (with a 'u').

Return format:

SEO_TITLE:
<title here>

META:
<meta description here>

Original Title: "{title}"

Article Content:
\"\"\"{content}\"\"\""""
            else:
                # Use the configured prompt and format it with title and content
                prompt = prompt.format(title=title, content=content)

            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            response.raise_for_status()
            
            # Add error handling for API response structure
            response_data = response.json()
            if not response_data.get("candidates") or len(response_data["candidates"]) == 0:
                self.logger.error("Empty or invalid Gemini API response")
                raise ValueError("Invalid API response structure")
                
            if not response_data["candidates"][0].get("content") or not response_data["candidates"][0]["content"].get("parts") or len(response_data["candidates"][0]["content"]["parts"]) == 0:
                self.logger.error("Invalid content structure in Gemini API response")
                raise ValueError("Invalid content structure in API response")
                
            text = response_data["candidates"][0]["content"]["parts"][0].get("text", "").strip()

            seo_title, meta_description = "", ""

            # Parse response using regex from Jupyter notebook
            match_seo = re.search(r"SEO_TITLE:\s*(.*?)\s*META:", text, re.DOTALL)
            match_meta = re.search(r"META:\s*(.+)", text, re.DOTALL)

            if match_seo:
                seo_title = match_seo.group(1).strip()
            if match_meta:
                meta_description = match_meta.group(1).strip()

            # Clean up
            seo_title = seo_title.strip()
            meta_description = meta_description.strip()

            # Enhanced SEO title validation from Jupyter notebook
            length = len(seo_title)
            if length < 50 or length > 59:
                self.logger.warning(f"SEO title has {length} chars (expected 50–59). Adjusting...")
                if length > 59:
                    snippet = seo_title[:59]
                    # Try to find a natural break point
                    m = re.search(r'(.+[\\.?!])(?=[^\\.?!]*$)', snippet)
                    if m:
                        seo_title = m.group(1).strip()
                    else:
                        seo_title = snippet.rsplit(" ", 1)[0].strip() if " " in snippet else snippet.strip()
                elif length < 50:
                    self.logger.warning("SEO title is under 50 characters. Keeping it short for now.")

            # Avoid bad trailing words from Jupyter notebook logic
            if seo_title and seo_title.split() and seo_title.split()[-1].lower() in {"to", "on", "with", "and", "or", "but", "for", "in"}:
                seo_title = " ".join(seo_title.split()[:-1])
                self.logger.warning("Trimmed dangling word from SEO title end")

            self.logger.info(f"Final SEO title ({len(seo_title)} chars): {seo_title}")

            # Enhanced META validation from Jupyter notebook
            length_meta = len(meta_description)
            if not (155 <= length_meta <= 160):
                self.logger.warning(f"Meta description is {length_meta} chars (expected 155–160). Falling back to snippet.")
                # Create fallback meta from content using Jupyter notebook logic
                plain = re.sub(r'<[^>]+>', ' ', content)
                plain = re.sub(r'https?:\\/\\/\\S+|[^<\\s]+\\/\\\">', ' ', plain)
                plain = re.sub(r'\\s+', ' ', plain).strip()

                words = plain.split() if plain else []
                snippet = ""
                for w in words:
                    candidate = f"{snippet} {w}".strip()
                    if len(candidate) > 160:
                        break
                    snippet = candidate

                if len(snippet) < 155:
                    for word in plain[len(snippet):].strip().split():
                        temp = f"{snippet} {word}".strip()
                        if len(temp) > 160:
                            break
                        snippet = temp
                        if len(snippet) >= 155:
                            break
                if len(snippet) < 155:
                    snippet = plain[:155].rsplit(" ", 1)[0]
                meta_description = snippet

            self.logger.info(f"Final Meta Description ({len(meta_description)} chars)")
            return seo_title, meta_description

        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Gemini API request error: {e}")
            # Fallback generation
            seo_title = title[:59] if len(title) > 59 else title
            clean_content = re.sub(r'<[^>]+>', '', content)
            meta_desc = clean_content[:157] + "..." if len(clean_content) > 157 else clean_content
            return seo_title, meta_desc
        except Exception as e:
            self.logger.error(f"❌ Error in SEO generation: {e}")
            # Fallback generation
            seo_title = title[:59] if len(title) > 59 else title
            clean_content = re.sub(r'<[^>]+>', '', content)
            meta_desc = clean_content[:157] + "..." if len(clean_content) > 157 else clean_content
            return seo_title, meta_desc

    def generate_tags_with_gemini(self, content: str) -> List[str]:
        """Generate tags using Gemini AI"""
        seen = set()
        tags = []

        try:
            gemini_api_key = self.config.get('gemini_api_key', '')
            if not gemini_api_key:
                # Fallback to simple tag generation
                return self.generate_tags_fallback(content)

            # Use the configurable prompt from GEMINI_PROMPTS
            prompt = self.GEMINI_PROMPTS.get('tag_generation_prompt', '')
            if not prompt:
                # Fallback to default prompt if not configured
                prompt = f"""Extract only the full names of football players and the full names of the clubs mentioned in this article.
Return them as a comma-separated list with no extra punctuation.

Article Content:
\"\"\"{content}\"\"\""""
            else:
                # Use the configured prompt and format it with content
                prompt = prompt.format(content=content)

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
            
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("candidates") and len(response_data["candidates"]) > 0:
                    candidate = response_data["candidates"][0]
                    if candidate.get("content") and candidate["content"].get("parts") and len(candidate["content"]["parts"]) > 0:
                        raw = candidate["content"]["parts"][0].get("text", "")
                        for cand in [c.strip() for c in raw.split(",") if c.strip()]:
                            name = re.sub(r"\\s+", " ", cand)
                            
                            # Apply synonym normalization from Jupyter notebook
                            if name in self.TAG_SYNONYMS:
                                name = self.TAG_SYNONYMS[name]
                            
                            # Keep if valid and present in content (from Jupyter notebook logic)
                            if (
                                (name in self.STATIC_CLUBS or re.fullmatch(r"[A-Z][a-z]+(?:\\s[A-Z][a-z]+)*", name))
                                and re.search(rf"\\b{re.escape(name)}\\b", content, re.IGNORECASE)
                                and name not in seen
                            ):
                                seen.add(name)
                                tags.append(name)
                    else:
                        self.logger.error("Invalid content structure in Gemini tag API response")
                else:
                    self.logger.error("No candidates in Gemini tag API response")
            else:
                self.logger.error(f"Gemini Tag API Error {response.status_code}: {response.text}")

            # Fallback scan from Jupyter notebook implementation
            for club in self.STATIC_CLUBS:
                if club not in seen and re.search(rf"\\b{re.escape(club)}\\b", content, re.IGNORECASE):
                    seen.add(club)
                    tags.append(club)

            self.logger.info(f"Generated tags: {tags}")
            return tags

        except Exception as e:
            self.logger.error(f"Error in Gemini tag generation: {e}")
            return self.generate_tags_fallback(content)

    def generate_tags_with_gemini_jupyter(self, content: str) -> List[str]:
        """Enhanced tag generation using Jupyter notebook approach with synonym normalization"""
        try:
            # Use the existing generate_tags_with_gemini method first
            raw_tags = self.generate_tags_with_gemini(content)
            
            if not raw_tags:
                self.logger.warning("No raw tags generated, using fallback")
                return self.generate_tags_fallback(content)
            
            # Apply synonym normalization from Jupyter notebook
            normalized_tags = []
            for tag in raw_tags:
                normalized = self.normalize_tag_with_synonyms(tag)
                if normalized and normalized not in normalized_tags:
                    normalized_tags.append(normalized)
            
            self.logger.info(f"Generated {len(normalized_tags)} normalized tags from {len(raw_tags)} raw tags")
            return normalized_tags[:15]  # Limit to 15 tags as in Jupyter notebook
            
        except Exception as e:
            self.logger.error(f"Error in enhanced tag generation: {e}")
            return self.generate_tags_fallback(content)
    
    def normalize_tag_with_synonyms(self, tag: str) -> str:
        """Normalize tags using synonym mapping from Jupyter notebook"""
        try:
            # Convert to lowercase for matching
            lower_tag = tag.lower().strip()
            
            # Check if tag exists in synonym mapping
            for canonical, synonyms in self.TAG_SYNONYMS.items():
                if lower_tag == canonical.lower():
                    return canonical
                if lower_tag in [syn.lower() for syn in synonyms]:
                    return canonical
            
            # If no synonym found, return title case version
            return tag.title()
            
        except Exception as e:
            self.logger.warning(f"Error normalizing tag '{tag}': {e}")
            return tag.title()
    
    def generate_slug_jupyter(self, title: str) -> str:
        """Enhanced slug generation using Jupyter notebook approach with stop word filtering"""
        try:
            # Convert to lowercase and replace spaces with hyphens
            slug = title.lower()
            
            # Remove special characters but keep alphanumeric and spaces
            slug = re.sub(r'[^\w\s-]', '', slug)
            
            # Split into words and filter out stop words
            words = slug.split()
            filtered_words = []
            
            for word in words:
                # Skip stop words (if available) and very short words
                if len(word) > 2 and word not in self.STOP_WORDS:
                    filtered_words.append(word)
            
            # Join with hyphens and limit length
            slug = '-'.join(filtered_words)
            
            # Ensure slug isn't too long (WordPress limitation)
            if len(slug) > 50:
                # Take first 50 characters and ensure we don't cut in middle of word
                slug = slug[:50]
                if slug.endswith('-'):
                    slug = slug[:-1]
                last_hyphen = slug.rfind('-')
                if last_hyphen > 30:  # Only trim if we have a reasonable length
                    slug = slug[:last_hyphen]
            
            self.logger.info(f"Generated slug: {slug}")
            return slug
            
        except Exception as e:
            self.logger.error(f"Error generating enhanced slug: {e}")
            # Fallback to simple slug generation
            return re.sub(r'[^\w\s-]', '', title.lower()).replace(' ', '-')[:50]

    def process_complete_article_jupyter(self, url: str) -> Optional[Dict]:
        """Complete article processing pipeline using Jupyter notebook implementation"""
        try:
            self.logger.info(f"🔗 Processing article: {url}")
            
            # Extract article content using Selenium
            with self.get_selenium_driver_context() as driver:
                if not driver:
                    self.logger.error("❌ Selenium driver could not be initialized")
                    return None

                title, content = self.extract_article_with_selenium(driver, url)
                if not title or not content:
                    self.logger.warning("⚠️ Failed to extract title/content")
                    return None

                # Gemini paraphrasing - enhanced version
                try:
                    paraphrased_content, paraphrased_title = self.gemini_paraphrase_content_and_title(title, content)
                except Exception as e:
                    self.logger.warning(f"⚠️ Gemini paraphrasing failed: {e}")
                    return None

                # Internal + external link injection
                internal_linked = self.inject_internal_links(paraphrased_content)
                final_linked_content = self.inject_external_links(internal_linked)

                # Enhanced category + tag detection from Jupyter notebook
                categories = self.detect_categories_jupyter(paraphrased_content, paraphrased_title)
                tags = self.generate_tags_with_gemini_jupyter(paraphrased_content)

                # Enhanced SEO generation from Jupyter notebook
                seo_title, meta_description = self.generate_seo_title_and_meta_jupyter(paraphrased_title, final_linked_content)
                
                # Enhanced slug generation from Jupyter notebook
                slug = self.generate_slug_jupyter(seo_title)

                # Keyphrase extraction from Jupyter notebook
                focus_keyphrase, additional_keyphrases = self.extract_keyphrases_jupyter(paraphrased_title, final_linked_content)

                return {
                    'original_title': title,
                    'original_content': content,
                    'title': paraphrased_title,
                    'content': final_linked_content,
                    'categories': categories,
                    'tags': tags,
                    'seo_title': seo_title,
                    'meta_description': meta_description,
                    'slug': slug,
                    'focus_keyphrase': focus_keyphrase,
                    'additional_keyphrases': additional_keyphrases,
                    'url': url
                }

        except Exception as e:
            self.logger.error(f"❌ Error processing article: {e}")
            return None

    def detect_categories_jupyter(self, content: str, title: str = "") -> List[str]:
        """Enhanced category detection from Jupyter notebook - always include Latest News as parent"""
        # Combine title and content for better category detection
        text = f"{title}. {content}" if title else content
        lower = text.lower()
        cats: List[str] = ["Latest News"]  # always first

        for kw, subcat in self.CATEGORY_KEYWORDS.items():
            if kw in lower and subcat not in cats:
                cats.append(subcat)
                self.logger.info(f"Matched sub-category '{subcat}' via keyword '{kw}'")

        self.logger.info(f"Final categories: {cats}")
        return cats

    def detect_categories(self, text: str) -> List[str]:
        """Legacy method for backward compatibility - calls the enhanced version"""
        return self.detect_categories_jupyter(text, "")

    def run_automation_jupyter_style(self, max_articles: int = 2) -> int:
        """Run the complete automation pipeline using Jupyter notebook implementation"""
        processed = 0
        posted_links = self.load_posted_links()

        try:
            # Get article links from source
            article_links = self.get_article_links(limit=10)
            if not article_links:
                self.logger.error("❌ No article links found")
                return 0

            self.logger.info(f"✅ Found {len(article_links)} article links")

            for link in article_links:
                if link in posted_links:
                    self.logger.info(f"⏩ Skipping already posted article: {link}")
                    continue

                # Process the complete article using Jupyter notebook methods
                article_data = self.process_complete_article_jupyter(link)
                if not article_data:
                    self.logger.warning(f"⚠️ Failed to process article: {link}")
                    continue

                # Post to WordPress with all the enhanced data
                post_id = self.post_to_wordpress_jupyter_style(article_data)
                
                if post_id:
                    self.logger.info(f"✅ Draft post created with ID: {post_id}")
                    posted_links.add(link)
                    self.save_posted_links(posted_links)
                    processed += 1
                else:
                    self.logger.error(f"❌ Failed to post article for: {link}")

                if processed >= max_articles:
                    self.logger.info(f"✅ Reached target of {max_articles} articles. Ending.")
                    break

            if processed == 0:
                self.logger.warning("⚠️ No new articles were posted")
            else:
                self.logger.info(f"🎉 Total new articles posted: {processed}")

            return processed

        except Exception as e:
            self.logger.error(f"❌ Error in automation pipeline: {e}")
            return processed

    def post_to_wordpress_jupyter_style(self, article_data: Dict) -> Optional[int]:
        """Post to WordPress using enhanced data from Jupyter notebook processing"""
        try:
            # WordPress API setup
            wp_base_url = self.config.get('wp_base_url', '')
            username = self.config.get('wp_username', '')
            password = self.config.get('wp_password', '')
            
            if not all([wp_base_url, username, password]):
                self.logger.error("❌ WordPress credentials not properly configured")
                return None

            auth = HTTPBasicAuth(username, password)
            
            # Create excerpt from content
            clean_content = re.sub(r'<[^>]+>', '', article_data['content']).strip()
            excerpt = clean_content[:297] + "..." if len(clean_content) > 300 else clean_content

            # Build payload with enhanced data
            payload = {
                "title": article_data['title'],
                "content": article_data['content'],
                "slug": article_data['slug'],
                "excerpt": excerpt,
                "status": "draft",
                "categories": [],
                "tags": []
            }

            # Process categories
            categories_url = f"{wp_base_url}/categories"
            cat_ids = []
            
            for cat in article_data['categories']:
                try:
                    resp = requests.get(categories_url, auth=auth, params={"search": cat}, timeout=10)
                    resp.raise_for_status()
                    found = resp.json()
                    
                    cid = next((c["id"] for c in found if c["name"].lower() == cat.lower()), None)
                    if not cid and found:
                        cid = found[0]["id"]
                    
                    if not cid:
                        # Create new category
                        create_resp = requests.post(categories_url, auth=auth, json={"name": cat}, timeout=10)
                        create_resp.raise_for_status()
                        cid = create_resp.json().get("id")
                    
                    if cid and cid not in cat_ids:
                        cat_ids.append(cid)
                        
                except Exception as e:
                    self.logger.warning(f"Error processing category '{cat}': {e}")
                    
            payload["categories"] = cat_ids

            # Process tags
            tags_url = f"{wp_base_url}/tags"
            tag_ids = []
            
            for tag in article_data['tags']:
                try:
                    resp = requests.get(tags_url, auth=auth, params={"search": tag}, timeout=10)
                    resp.raise_for_status()
                    found = resp.json()
                    
                    tid = next((t["id"] for t in found if t["name"].lower() == tag.lower()), None)
                    if not tid and found:
                        tid = found[0]["id"]
                    
                    if not tid:
                        # Create new tag
                        create_resp = requests.post(tags_url, auth=auth, json={"name": tag}, timeout=10)
                        create_resp.raise_for_status()
                        tid = create_resp.json().get("id")
                    
                    if tid and tid not in tag_ids:
                        tag_ids.append(tid)
                        
                except Exception as e:
                    self.logger.warning(f"Error processing tag '{tag}': {e}")
                    
            payload["tags"] = tag_ids

            # Create the post
            posts_url = f"{wp_base_url}/posts"
            post_resp = requests.post(posts_url, auth=auth, json=payload, timeout=30)
            post_resp.raise_for_status()
            
            post_id = post_resp.json().get("id")
            if not post_id:
                self.logger.error("❌ Post created but ID not returned")
                return None

            # Set SEO metadata (if AIOSEO plugin is available)
            try:
                aioseo_data = {
                    "aioseo_meta_data": {
                        "title": article_data['seo_title'],
                        "description": article_data['meta_description']
                    }
                }
                if article_data.get('focus_keyphrase'):
                    aioseo_data["aioseo_meta_data"]["keyphrases"] = {
                        "focus": {
                            "keyphrase": article_data['focus_keyphrase']
                        },
                        "additional": [
                            {"keyphrase": kp} for kp in article_data.get('additional_keyphrases', [])
                        ]
                    }
                
                update_resp = requests.post(f"{posts_url}/{post_id}", auth=auth, json=aioseo_data, timeout=10)
                update_resp.raise_for_status()
                self.logger.info("✅ SEO metadata updated successfully")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to update SEO metadata: {e}")

            self.logger.info(f"✅ WordPress draft post created (ID: {post_id})")
            return post_id

        except Exception as e:
            self.logger.error(f"❌ Error posting to WordPress: {e}")
            return None

    def generate_tags_fallback(self, content: str) -> list:
        """Fallback tag generation: extract capitalized words as possible names/clubs."""
        import re
        # Extract capitalized words (simple heuristic for names/clubs)
        words = re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', content)
        # Remove duplicates and filter short words
        tags = list({w for w in words if len(w) > 2})
        self.logger.info(f"Fallback tags generated: {tags}")
        return tags[:10]

    def extract_keyphrases_with_gemini(self, content: str, title: str = "") -> dict:
        """Extract focus and additional keyphrases using Gemini or fallback."""
        gemini_api_key = self.config.get('gemini_api_key', '')
        if not gemini_api_key:
            self.logger.warning("No Gemini API key found, using fallback keyphrase extraction.")
            return self.extract_keyphrases_fallback(content, title)
        try:
            # Use the configurable prompt from GEMINI_PROMPTS
            prompt = self.GEMINI_PROMPTS.get('keyphrase_extraction_prompt', '')
            if not prompt:
                # Fallback to default prompt if not configured
                prompt = "You are an SEO expert specializing in football content. Analyze the following article and extract:\n\n1. **Focus Keyphrase**: The single most important 2-4 word keyphrase that represents the core topic of this article. This should be what people would search for to find this specific article.\n\n2. **Additional Keyphrases**: 3-5 additional relevant keyphrases (2-4 words each) that are naturally mentioned in the content and would help with SEO ranking.\n\nRules:\n- Focus on keyphrases that football fans would actually search for\n- Include player names, club names, and football-specific terms\n- Avoid generic words like 'football', 'player', 'team' unless they're part of a specific phrase\n- Keyphrases should feel natural and be present in the content\n- Use British English spelling (e.g., 'rumours' not 'rumors')\n\nReturn format:\nFOCUS_KEYPHRASE:\n<main keyphrase here>\n\nADDITIONAL_KEYPHRASES:\n<keyphrase 1>\n<keyphrase 2>\n<keyphrase 3>\n<keyphrase 4>\n<keyphrase 5>\n\nArticle Title: {title}\n\nArticle Content:\n{content}"
            prompt = prompt.format(title=title, content=content)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            if response.status_code != 200:
                self.logger.error(f"Gemini Keyphrase API Error {response.status_code}: {response.text}")
                return self.extract_keyphrases_fallback(content, title)
                
            response_data = response.json()
            if not response_data.get("candidates") or len(response_data["candidates"]) == 0:
                self.logger.error("Empty or invalid Gemini API response for keyphrase extraction")
                return self.extract_keyphrases_fallback(content, title)
                
            candidate = response_data["candidates"][0]
            if not candidate.get("content") or not candidate["content"].get("parts") or len(candidate["content"]["parts"]) == 0:
                self.logger.error("Invalid content structure in Gemini API response for keyphrase extraction")
                return self.extract_keyphrases_fallback(content, title)
                
            text = candidate["content"]["parts"][0].get("text", "")
            # Parse the result
            focus = ""
            additional = []
            in_focus = False
            in_additional = False
            for line in text.splitlines():
                if line.strip().lower().startswith('focus_keyphrase:'):
                    in_focus = True
                    in_additional = False
                    continue
                if line.strip().lower().startswith('additional_keyphrases:'):
                    in_focus = False
                    in_additional = True
                    continue
                if in_focus and line.strip():
                    focus = line.strip()
                if in_additional and line.strip():
                    additional.append(line.strip())
            # Apply custom SEO keywords if enabled
            if self.CUSTOM_SEO_KEYWORDS.get("enabled", False):
                enhanced_focus, enhanced_additional = self.apply_custom_seo_keywords(
                    focus, additional, title, content
                )
                return enhanced_focus, enhanced_additional
            
            return focus, additional
        except Exception as e:
            self.logger.error(f"Error extracting keyphrases with Gemini: {e}")
            return self.extract_keyphrases_fallback(content, title)

    def extract_keyphrases_fallback(self, content: str, title: str = "") -> Tuple[str, List[str]]:
        """Fallback: extract keyphrases by picking most frequent meaningful words and phrases."""
        import re
        from collections import Counter
        
        # Combine title and content for better keyword extraction
        combined_text = f"{title} {content}"
        
        # Clean the text and extract meaningful phrases and words
        # Remove HTML tags and normalize whitespace
        clean_text = re.sub(r'<[^>]+>', ' ', combined_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # Extract multi-word phrases (2-4 words) with proper capitalization
        phrases = re.findall(r'\b[A-Z][a-zA-Z]{2,}(?:\s+[A-Z][a-zA-Z]{2,}){1,3}\b', clean_text)
        
        # Extract single meaningful words (capitalized, at least 3 chars)
        single_words = re.findall(r'\b[A-Z][a-zA-Z]{2,}\b', clean_text)
        
        # Enhanced stop words list
        stop_words = {
            'The', 'This', 'That', 'With', 'From', 'They', 'Were', 'Been', 'Have', 'Will', 
            'Would', 'Could', 'Should', 'When', 'Where', 'What', 'Which', 'While', 'After',
            'Before', 'During', 'Since', 'Until', 'About', 'Above', 'Below', 'Between',
            'Through', 'Under', 'Over', 'Into', 'Onto', 'Upon', 'Within', 'Without'
        }
        
        # Filter and clean keywords
        filtered_phrases = []
        filtered_words = []
        
        for phrase in phrases:
            words_in_phrase = phrase.split()
            if not any(word in stop_words for word in words_in_phrase) and len(phrase) > 4:
                filtered_phrases.append(phrase)
        
        for word in single_words:
            if word not in stop_words and len(word) > 2:
                filtered_words.append(word)
        
        # Count frequencies
        phrase_freq = Counter(filtered_phrases)
        word_freq = Counter(filtered_words)
        
        # Get top phrases and words
        top_phrases = [phrase for phrase, count in phrase_freq.most_common(10)]
        top_words = [word for word, count in word_freq.most_common(15)]
        
        # Prioritize phrases for focus keyphrase
        focus_keyphrase = 'football news'  # default
        if top_phrases:
            focus_keyphrase = top_phrases[0]
        elif top_words:
            # Try to create a meaningful phrase from top words
            if len(top_words) >= 2:
                focus_keyphrase = f"{top_words[0]} {top_words[1]}"
            else:
                focus_keyphrase = top_words[0]
        
        # Build additional keyphrases list
        additional_keyphrases = []
        
        # Add remaining phrases
        for phrase in top_phrases[1:6]:  # Skip the focus phrase
            if phrase != focus_keyphrase:
                additional_keyphrases.append(phrase)
        
        # Add meaningful single words if we need more
        for word in top_words:
            if len(additional_keyphrases) >= 5:
                break
            if word not in focus_keyphrase and word not in ' '.join(additional_keyphrases):
                additional_keyphrases.append(word)
        
        # Add football-specific defaults if we still don't have enough
        if len(additional_keyphrases) < 3:
            football_defaults = [
                'Premier League', 'transfer news', 'match report', 'football analysis', 
                'team news', 'player performance', 'match preview', 'football updates'
            ]
            for default in football_defaults:
                if default not in additional_keyphrases and default != focus_keyphrase:
                    additional_keyphrases.append(default)
                if len(additional_keyphrases) >= 5:
                    break
        # Apply custom SEO keywords if enabled
        if self.CUSTOM_SEO_KEYWORDS.get("enabled", False):
            enhanced_focus, enhanced_additional = self.apply_custom_seo_keywords(
                focus_keyphrase, additional_keyphrases, title, content
            )
            return enhanced_focus, enhanced_additional
        
        return focus_keyphrase, additional_keyphrases

    def generate_seo_title_and_meta_jupyter(self, title: str, content: str) -> Tuple[str, str]:
        """Enhanced SEO title and meta generation using Jupyter notebook implementation"""
        return self.generate_seo_title_and_meta(title, content)
        
    def extract_keyphrases_jupyter(self, title: str, content: str) -> Tuple[str, List[str]]:
        """Enhanced keyphrase extraction using Jupyter notebook implementation"""
        result = self.extract_keyphrases_with_gemini(content, title)
        focus = result.get('focus_keyphrase', '')
        additional = result.get('additional_keyphrases', [])
        
        # Apply custom SEO keywords if enabled
        focus, additional = self.apply_custom_seo_keywords(focus, additional, title, content)
        
        return focus, additional
        
    def apply_custom_seo_keywords(self, auto_focus: str, auto_additional: List[str], 
                                 title: str, content: str) -> Tuple[str, List[str]]:
        """Apply custom SEO keywords from configuration to auto-generated keyphrases"""
        # Skip if custom keywords are not enabled
        if not self.CUSTOM_SEO_KEYWORDS.get("enabled", False):
            return auto_focus, auto_additional
            
        self.logger.info("Applying custom SEO keywords from configuration")
        
        # Get settings
        settings = self.CUSTOM_SEO_KEYWORDS.get("keyword_settings", {})
        custom_keywords = self.CUSTOM_SEO_KEYWORDS.get("custom_keywords", {})
        
        max_focus = settings.get("max_focus_keywords_per_article", 2)
        max_additional = settings.get("max_additional_keywords_per_article", 8)
        combine_with_auto = settings.get("combine_with_auto_keywords", True)
        prioritize_custom = settings.get("prioritize_custom_keywords", False)
        
        # Get custom keywords
        custom_focus = custom_keywords.get("focus_keywords", [])
        custom_additional = custom_keywords.get("additional_keywords", [])
        
        # Add team-specific keywords if enabled
        if settings.get("auto_select_team_keywords", True):
            combined_text = f"{title} {content}".lower()
            team_keywords = custom_keywords.get("team_specific_keywords", {})
            
            for team, keywords in team_keywords.items():
                if team.lower() in combined_text:
                    self.logger.info(f"Adding team-specific keywords for {team}")
                    custom_additional.extend(keywords)
        
        # Add competition keywords if enabled
        if settings.get("auto_select_competition_keywords", True):
            combined_text = f"{title} {content}".lower()
            competition_keywords = custom_keywords.get("competition_keywords", [])
            
            for keyword in competition_keywords:
                if keyword.lower() in combined_text:
                    custom_additional.append(keyword)
        
        # Add seasonal keywords
        custom_additional.extend(custom_keywords.get("seasonal_keywords", []))
        
        # Remove duplicates
        custom_additional = list(set(custom_additional))
        
        # Combine or replace auto-generated keywords
        if combine_with_auto:
            # For focus keyphrase
            focus_keyphrases = []
            if prioritize_custom:
                focus_keyphrases.extend(custom_focus[:max_focus])
                if len(focus_keyphrases) < max_focus and auto_focus:
                    focus_keyphrases.append(auto_focus)
            else:
                if auto_focus:
                    focus_keyphrases.append(auto_focus)
                focus_keyphrases.extend(custom_focus[:max_focus - len(focus_keyphrases)])
            
            # For additional keyphrases
            additional_keyphrases = []
            if prioritize_custom:
                additional_keyphrases.extend(custom_additional[:max_additional])
                remaining = max_additional - len(additional_keyphrases)
                additional_keyphrases.extend(auto_additional[:remaining])
            else:
                additional_keyphrases.extend(auto_additional)
                remaining = max_additional - len(additional_keyphrases)
                additional_keyphrases.extend(custom_additional[:remaining])
        else:
            # Use only custom keywords
            focus_keyphrases = custom_focus[:max_focus]
            additional_keyphrases = custom_additional[:max_additional]
        
        # Ensure we have at least one focus keyphrase
        if not focus_keyphrases and auto_focus:
            focus_keyphrases.append(auto_focus)
        
        # Remove duplicates and limit to max counts
        focus_keyphrases = list(dict.fromkeys(focus_keyphrases))[:max_focus]
        additional_keyphrases = list(dict.fromkeys(additional_keyphrases))[:max_additional]
        
        # Log the results
        self.logger.info(f"Final focus keyphrases: {focus_keyphrases}")
        self.logger.info(f"Final additional keyphrases: {additional_keyphrases}")
        
        # Return the first focus keyphrase and all additional keyphrases
        return focus_keyphrases[0] if focus_keyphrases else "", additional_keyphrases

    def search_getty_images(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Search for editorial images - now uses reliable sports image sources"""
        try:
            self.logger.info(f"🔍 Searching for editorial sports images for: {query}")
            
            # Since Getty Images blocks scraping, we'll use a more reliable approach
            # with high-quality sports image sources that are readily available
            
            # Generate high-quality sports images using multiple sources
            images = self.get_reliable_sports_images(query, num_results)
            
            if images:
                self.logger.info(f"✅ Found {len(images)} editorial sports images for '{query}'")
            else:
                self.logger.warning(f"⚠️ No sports images found for '{query}', using fallback")
                images = self.get_fallback_getty_images(query, num_results)
                
            return images
            
        except Exception as e:
            self.logger.error(f"❌ Error searching for editorial images: {e}")
            # Always return fallback images
            return self.get_fallback_getty_images(query, num_results)

    def get_reliable_sports_images(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Get high-quality sports images from reliable sources"""
        try:
            self.logger.info(f"🏆 Getting reliable sports images for: {query}")
            
            # Create realistic sports images using reliable services
            images = []
            
            # Unsplash has high-quality sports photos with API access
            unsplash_images = self.search_unsplash_sports(query, num_results)
            if unsplash_images:
                images.extend(unsplash_images)
            
            # If we don't have enough, add themed placeholder images
            if len(images) < num_results:
                themed_images = self.get_themed_placeholder_images(query, num_results - len(images))
                images.extend(themed_images)
            
            return images[:num_results]
            
        except Exception as e:
            self.logger.error(f"❌ Error getting reliable sports images: {e}")
            return []

    def search_unsplash_sports(self, query: str, num_results: int = 3) -> List[Dict[str, str]]:
        """Search Unsplash for high-quality sports images"""
        try:
            # Unsplash has a public API for accessing high-quality images
            # Using their Source API which doesn't require API keys for basic usage
            
            self.logger.info(f"📷 Searching Unsplash for sports images: {query}")
            
            # Extract sports-related keywords from query
            sports_keywords = self.extract_sports_keywords(query)
            search_term = "football soccer sports" if not sports_keywords else " ".join(sports_keywords)
            
            images = []
            for i in range(num_results):
                # Unsplash Source API provides random images by topic
                # Different dimensions and random seeds for variety
                dimensions = ["1200x800", "1600x900", "1920x1080"]
                dimension = dimensions[i % len(dimensions)]
                
                image_url = f"https://source.unsplash.com/{dimension}/?{search_term}&sig={i}"
                
                images.append({
                    "id": f"unsplash_{hashlib.md5(f'{query}_{i}'.encode()).hexdigest()[:10]}",
                    "title": f"Sports Editorial: {query}",
                    "embed_url": "",  # Not used for featured images
                    "thumbnail": image_url,
                    "download_url": image_url,
                    "search_query": query,
                    "source": "unsplash",
                    "is_fallback": False
                })
            
            self.logger.info(f"✅ Generated {len(images)} Unsplash sports images")
            return images
            
        except Exception as e:
            self.logger.error(f"❌ Error searching Unsplash: {e}")
            return []

    def extract_sports_keywords(self, query: str) -> List[str]:
        """Extract sports-related keywords from query"""
        sports_terms = [
            "football", "soccer", "premier league", "champions league", 
            "manchester united", "liverpool", "arsenal", "chelsea", 
            "manchester city", "tottenham", "stadium", "match", "goal",
            "player", "team", "club", "league", "championship"
        ]
        
        query_lower = query.lower()
        found_terms = [term for term in sports_terms if term in query_lower]
        
        # If no specific terms found, use general sports terms
        if not found_terms:
            found_terms = ["football", "soccer", "sports"]
        
        return found_terms[:3]  # Limit to 3 terms

    def get_themed_placeholder_images(self, query: str, num_results: int = 2) -> List[Dict[str, str]]:
        """Get themed placeholder images for sports content"""
        try:
            self.logger.info(f"🎨 Creating themed placeholder images for: {query}")
            
            # Create themed placeholder images using Picsum with sports-like IDs
            images = []
            
            # Use specific photo IDs from Picsum that look more professional/sports-like
            sports_photo_ids = [237, 256, 274, 431, 452, 473, 494, 515]
            
            for i in range(num_results):
                photo_id = sports_photo_ids[i % len(sports_photo_ids)]
                
                # Different dimensions for variety
                dimensions = ["1200/800", "1600/900", "1920/1080"]
                dimension = dimensions[i % len(dimensions)]
                
                image_url = f"https://picsum.photos/id/{photo_id}/{dimension}"
                
                images.append({
                    "id": f"placeholder_{photo_id}_{i}",
                    "title": f"Editorial Image: {query}",
                    "embed_url": "",
                    "thumbnail": image_url,
                    "download_url": image_url,
                    "search_query": query,
                    "source": "placeholder",
                    "is_fallback": True
                })
            
            self.logger.info(f"✅ Created {len(images)} themed placeholder images")
            return images
            
        except Exception as e:
            self.logger.error(f"❌ Error creating themed placeholders: {e}")
            return []
            
    def get_fallback_getty_images(self, query: str, num_results: int = 3) -> List[Dict[str, str]]:
        """Generate fallback high-quality sports images when search fails"""
        try:
            self.logger.info(f"🔄 Generating fallback sports images for: {query}")
            
            # Use reliable image sources for fallback
            images = []
            
            # Method 1: Use themed sports images from Picsum
            sports_themes = ["sports", "football", "soccer", "action", "team"]
            
            for i in range(num_results):
                # Use specific photo IDs that look professional
                photo_ids = [1084, 1073, 1055, 1043, 1035, 1025, 1015, 1005]
                photo_id = photo_ids[i % len(photo_ids)]
                
                # Vary dimensions for diversity
                dimensions = ["1200/800", "1600/900", "1920/1080"]
                dimension = dimensions[i % len(dimensions)]
                
                image_url = f"https://picsum.photos/id/{photo_id}/{dimension}"
                
                images.append({
                    "id": f"fallback_{photo_id}_{i}",
                    "title": f"Sports Editorial: {query}",
                    "embed_url": "",
                    "thumbnail": image_url,
                    "download_url": image_url,
                    "search_query": query,
                    "source": "fallback",
                    "is_fallback": True
                })
            
            self.logger.info(f"✅ Generated {len(images)} high-quality fallback images")
            return images
            
        except Exception as e:
            self.logger.error(f"❌ Error generating fallback images: {e}")
            # Last resort: create simple placeholder
            return [{
                "id": "emergency_fallback",
                "title": f"Editorial Image: {query}",
                "embed_url": "",
                "thumbnail": "https://picsum.photos/1200/800?grayscale",
                "download_url": "https://picsum.photos/1200/800?grayscale", 
                "search_query": query,
                "source": "emergency",
                "is_fallback": True
            }]

    def generate_getty_search_terms_with_gemini(self, title: str, content: str) -> str:
        """Use Gemini AI to generate optimal search terms for finding the best editorial image on Getty Images"""
        try:
            gemini_api_key = self.config.get('gemini_api_key', '')
            if not gemini_api_key:
                self.logger.warning("⚠️ Gemini API key not available for Getty search optimization")
                return title
            
            # Clean content for analysis
            clean_content = re.sub(r'<[^>]+>', '', content[:1000])  # First 1000 chars, no HTML
            
            prompt = f"""
Analyze this football/sports article and generate 2-3 optimal search terms for finding the best editorial image on Getty Images.

Article Title: {title}
Article Content: {clean_content}

Think about:
- What would be the most visually appealing image for this article?
- What specific sports moment, player, team, or venue would work best?
- What are the key visual elements readers would expect to see?

Provide ONLY the search terms, separated by commas. Keep it simple and specific.
Focus on visual elements like: team names, player names, stadium names, specific match moments, or general sports concepts.

Example responses:
- "Manchester United, Old Trafford, Premier League"
- "Liverpool FC, Anfield Stadium, Champions League" 
- "Premier League football, match action"
- "Arsenal Emirates Stadium, football crowd"

Your response (search terms only):
"""
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
            
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            
            if response.status_code == 200:
                search_terms = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                # Clean up the response
                search_terms = re.sub(r'[^\w\s,]', '', search_terms)  # Remove special chars except commas
                search_terms = search_terms.replace('\n', ', ').replace('  ', ' ')
                
                self.logger.info(f"🤖 Gemini suggested search terms: {search_terms}")
                return search_terms
            else:
                self.logger.warning(f"⚠️ Gemini API error: {response.status_code}")
                return title
                
        except Exception as e:
            self.logger.error(f"❌ Error generating Getty search terms with Gemini: {e}")
            return title

    def download_getty_image(self, image_url: str, filename: str) -> Optional[bytes]:
        """Download sports image from URL with reliable fallback"""
        try:
            self.logger.info(f"⬇️ Downloading sports image: {image_url}")
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "image/webp,image/apng,image/jpeg,image/png,image/*,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            }
            
            # Try downloading the image
            response = requests.get(image_url, headers=headers, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            content_length = len(response.content)
            
            self.logger.info(f"📄 Response - Type: {content_type}, Size: {content_length} bytes")
            
            # Check if it's a valid image
            if (content_type.startswith('image/') and content_length > 1000) or content_length > 50000:
                self.logger.info(f"✅ Successfully downloaded image ({content_length} bytes)")
                return response.content
            else:
                self.logger.warning(f"⚠️ Downloaded content may not be a valid image")
                # If the download seems suspicious, try fallback
                return self.download_fallback_placeholder_image()
                
        except Exception as e:
            self.logger.error(f"❌ Error downloading image: {e}")
            # Always try fallback on any error
            return self.download_fallback_placeholder_image()

    def download_fallback_placeholder_image(self) -> Optional[bytes]:
        """Download a reliable fallback placeholder image"""
        try:
            self.logger.info("🔄 Downloading reliable fallback placeholder image...")
            
            # Use multiple fallback sources in order of preference
            fallback_urls = [
                "https://picsum.photos/1200/800?grayscale",  # Picsum - very reliable
                "https://source.unsplash.com/1200x800/?sports,football",  # Unsplash sports
                "https://picsum.photos/1200/800",  # Picsum color version
                "https://via.placeholder.com/1200x800/808080/FFFFFF?text=Sports+Image"  # Simple placeholder
            ]
            
            for url in fallback_urls:
                try:
                    self.logger.info(f"🔄 Trying fallback URL: {url}")
                    
                    response = requests.get(url, timeout=15, allow_redirects=True)
                    response.raise_for_status()
                    
                    if len(response.content) > 1000:  # Reasonable image size
                        self.logger.info(f"✅ Downloaded fallback image ({len(response.content)} bytes)")
                        return response.content
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Fallback URL failed: {e}")
                    continue
            
            # If all fallbacks fail, create a minimal placeholder
            self.logger.error("❌ All fallback URLs failed, creating minimal placeholder")
            return self.create_minimal_placeholder_image()
                
        except Exception as e:
            self.logger.error(f"❌ Error in fallback download: {e}")
            return self.create_minimal_placeholder_image()

    def create_minimal_placeholder_image(self) -> Optional[bytes]:
        """Create a minimal placeholder image as last resort"""
        try:
            # This creates a simple 1x1 transparent PNG as absolute fallback
            # Base64 encoded minimal PNG image data
            minimal_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            
            image_data = base64.b64decode(minimal_png_b64)
            
            self.logger.info("✅ Created minimal placeholder image")
            return image_data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create minimal placeholder: {e}")
            return None

    def add_openai_image_to_content(self, content: str, title: str, custom_prompt: str = None) -> str:
        """Add OpenAI generated image to content"""
        try:
            self.logger.info("🎨 Adding OpenAI generated image to content...")
            
            # Load OpenAI image configuration
            openai_config = self.load_openai_image_config()
            
            # Generate image prompt
            image_prompt = self.create_openai_image_prompt(title, content, openai_config, custom_prompt=custom_prompt)
            
            # Generate image using OpenAI DALL-E
            image_url = self.generate_openai_image(image_prompt, openai_config)
            
            if image_url:
                # Create image HTML block
                image_html = f'''
<div class="wp-block-image">
    <figure class="aligncenter size-large">
        <img src="{image_url}" alt="{title}" class="wp-image-generated"/>
        <figcaption>{title}</figcaption>
    </figure>
</div>
'''
                
                # Insert after first or second paragraph
                paragraphs = content.split('</p>')
                if len(paragraphs) >= 3:
                    # Insert after second paragraph
                    insert_point = 2
                else:
                    # Insert after first paragraph
                    insert_point = 1
                
                if len(paragraphs) > insert_point:
                    paragraphs[insert_point-1] += '</p>' + image_html
                    content = '</p>'.join(paragraphs)
                else:
                    # Fallback: add at the beginning
                    content = image_html + content
                
                self.logger.info("✅ OpenAI image added to content successfully")
                return content
            else:
                self.logger.warning("⚠️ Failed to generate OpenAI image")
                return content
                
        except Exception as e:
            self.logger.error(f"❌ Error adding OpenAI image to content: {e}")
            return content
    
    def add_getty_image_to_content(self, content: str, title: str, topic_keywords: List[str] = None) -> str:
        """Add Getty Images to content"""
        try:
            self.logger.info("📷 Adding Getty Images to content...")
            
            # Generate search terms using Gemini AI
            search_terms = self.generate_getty_search_terms_with_gemini(title, content)
            
            # Search for Getty images
            images = self.search_getty_images(search_terms, num_results=3)
            
            if images:
                # Use the first (best) image
                image = images[0]
                
                # Get embed code
                embed_code = self.get_getty_embed_code(image['id'], image['title'])
                
                if embed_code:
                    # Create image HTML block
                    image_html = f'''
<div style="padding: 16px;">
    <div style="display: flex; align-items: center; justify-content: center; flex-direction: column; width: 100%; background-color: #F4F4F4; border-radius: 4px;">
        {embed_code}
        <p style="margin: 0; color: #000; font-family: Arial,sans-serif; font-size: 14px;">{image['title']}</p>
    </div>
</div>
'''
                    
                    # Insert after first or second paragraph
                    paragraphs = content.split('</p>')
                    if len(paragraphs) >= 3:
                        # Insert after second paragraph
                        insert_point = 2
                    else:
                        # Insert after first paragraph
                        insert_point = 1
                    
                    if len(paragraphs) > insert_point:
                        paragraphs[insert_point-1] += '</p>' + image_html
                        content = '</p>'.join(paragraphs)
                    else:
                        # Fallback: add at the beginning
                        content = image_html + content
                    
                    self.logger.info("✅ Getty image added to content successfully")
                    return content
                else:
                    self.logger.warning("⚠️ Failed to get Getty embed code")
                    return content
            else:
                self.logger.warning("⚠️ No Getty images found")
                return content
                
        except Exception as e:
            self.logger.error(f"❌ Error adding Getty image to content: {e}")
            return content
    
    def load_openai_image_config(self) -> Dict:
        """Load OpenAI image configuration"""
        try:
            config_path = os.path.join(self.config_dir, "openai_image_config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                # Return default configuration
                return {
                    "image_size": "1024x1024",
                    "image_style": "photorealistic",
                    "image_model": "dall-e-3",
                    "num_images": 1,
                    "prompt_prefix": "High-quality professional sports photography:",
                    "prompt_suffix": "Make it look like a professional sports photograph with dramatic lighting and composition."
                }
        except Exception as e:
            self.logger.error(f"❌ Error loading OpenAI config: {e}")
            return {}
    
    def create_openai_image_prompt(self, title: str, content: str, config: Dict, custom_prompt: str = None) -> str:
        """Create OpenAI image prompt"""
        try:
            if custom_prompt:
                return custom_prompt
            
            # Extract key themes from content
            clean_content = re.sub(r'<[^>]+>', '', content[:500])  # First 500 chars, no HTML
            
            # Build prompt
            prompt_prefix = config.get('prompt_prefix', '')
            prompt_suffix = config.get('prompt_suffix', '')
            
            prompt = f"{prompt_prefix} {title}. {prompt_suffix}"
            
            return prompt.strip()
            
        except Exception as e:
            self.logger.error(f"❌ Error creating OpenAI prompt: {e}")
            return title
    
    def generate_openai_image(self, prompt: str, config: Dict) -> Optional[str]:
        """Generate image using OpenAI DALL-E"""
        try:
            openai_api_key = self.config.get('openai_api_key', '')
            if not openai_api_key:
                self.logger.warning("⚠️ OpenAI API key not available")
                return None
            
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)
            
            response = client.images.generate(
                prompt=prompt,
                n=config.get('num_images', 1),
                size=config.get('image_size', '1024x1024'),
                model=config.get('image_model', 'dall-e-3')
            )
            
            if response.data:
                image_url = response.data[0].url
                self.logger.info(f"✅ OpenAI image generated: {image_url}")
                return image_url
            else:
                self.logger.warning("⚠️ No image data received from OpenAI")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error generating OpenAI image: {e}")
            return None
    
    def get_getty_embed_code(self, image_id: str, title: str) -> str:
        """Generate Getty Images embed code"""
        try:
            # Create standard Getty embed iframe
            embed_code = f'<iframe src="https://embed.gettyimages.com/embed/{image_id}" width="594" height="396" frameborder="0" scrolling="no"></iframe>'
            return embed_code
        except Exception as e:
            self.logger.error(f"❌ Error creating Getty embed code: {e}")
            return ""

    def generate_and_upload_featured_image(self, title: str, content: str, post_id: int) -> Optional[int]:
        """Generate OpenAI featured image and upload to WordPress"""
        try:
            self.logger.info(f"🎨 Generating OpenAI featured image for post {post_id}")
            
            # Load OpenAI image configuration
            openai_config = self.load_openai_image_config()
            
            # Create featured image prompt
            image_prompt = self.create_openai_image_prompt(title, content, openai_config, custom_prompt=None)
            
            # Generate image using OpenAI DALL-E
            image_url = self.generate_openai_image(image_prompt, openai_config)
            
            if not image_url:
                self.logger.error("❌ Failed to generate OpenAI image")
                return None
            
            # Download the generated image
            import requests
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            image_data = response.content
            
            # Upload to WordPress and set as featured image
            success = self.upload_featured_image_to_wordpress(image_data, post_id, f"AI Generated: {title}")
            
            if success:
                self.logger.info(f"✅ OpenAI featured image uploaded and set for post {post_id}")
                # Return a media ID (we'll need to modify upload_featured_image_to_wordpress to return it)
                return post_id  # Temporary return value
            else:
                self.logger.error("❌ Failed to upload OpenAI featured image")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error in generate_and_upload_featured_image: {e}")
            return None

    def upload_featured_image_to_wordpress(self, image_data: bytes, post_id: int, title: str = "Featured Image") -> Optional[int]:
        """Upload image data to WordPress and set as featured image"""
        try:
            self.logger.info(f"📤 Uploading featured image to WordPress for post {post_id}")
            
            # Prepare the image file for upload
            files = {
                'file': (f'featured_image_{post_id}.jpg', image_data, 'image/jpeg')
            }
            
            # WordPress media upload endpoint
            wp_base_url = self.config.get('wp_base_url', '')
            username = self.config.get('wp_username', '')
            password = self.config.get('wp_password', '')
            
            if not all([wp_base_url, username, password]):
                self.logger.error("❌ WordPress credentials not properly configured")
                return None

            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(username, password)
            media_url = f"{wp_base_url}/media"
            
            # Upload the image
            response = requests.post(
                media_url,
                files=files,
                auth=auth,
                data={
                    'title': title,
                    'alt_text': title,
                    'caption': title
                },
                timeout=60
            )
            
            if response.status_code == 201:
                media_data = response.json()
                media_id = media_data['id']
                
                self.logger.info(f"✅ Image uploaded successfully, media ID: {media_id}")
                
                # Set as featured image for the post
                post_url = f"{wp_base_url}/posts/{post_id}"
                
                update_response = requests.post(
                    post_url,
                    auth=auth,
                    headers={'Content-Type': 'application/json'},
                    json={'featured_media': media_id},
                    timeout=30
                )
                
                if update_response.status_code == 200:
                    self.logger.info(f"✅ Featured image set successfully for post {post_id}")
                    return media_id
                else:
                    self.logger.error(f"❌ Failed to set featured image: {update_response.status_code}")
                    return None
            else:
                self.logger.error(f"❌ Failed to upload image: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error uploading featured image: {e}")
            return None

    def post_to_wordpress_with_seo(self, title: str, content: str, categories: list, tags: list, 
                                   seo_title: str, meta_description: str, focus_keyphrase: str = None, 
                                   additional_keyphrases: list = None) -> tuple:
        """Post to WordPress with SEO optimization"""
        try:
            # WordPress API setup
            wp_base_url = self.config.get('wp_base_url', '')
            username = self.config.get('wp_username', '')
            password = self.config.get('wp_password', '')
            
            if not all([wp_base_url, username, password]):
                self.logger.error("❌ WordPress credentials not properly configured")
                return None, None

            auth = HTTPBasicAuth(username, password)
            
            # Create excerpt from content
            clean_content = re.sub(r'<[^>]+>', '', content).strip()
            excerpt = clean_content[:297] + "..." if len(clean_content) > 300 else clean_content
            
            # Generate slug from title
            slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
            slug = re.sub(r'\s+', '-', slug).strip('-')

            # Build payload
            payload = {
                "title": title,
                "content": content,
                "slug": slug,
                "excerpt": excerpt,
                "status": "draft",
                "categories": [],
                "tags": []
            }

            # Process categories
            categories_url = f"{wp_base_url}/categories"
            cat_ids = []
            
            for cat in categories:
                try:
                    resp = requests.get(categories_url, auth=auth, params={"search": cat}, timeout=10)
                    resp.raise_for_status()
                    found = resp.json()
                    
                    cid = next((c["id"] for c in found if c["name"].lower() == cat.lower()), None)
                    if not cid and found:
                        cid = found[0]["id"]
                    
                    if not cid:
                        # Create new category
                        create_resp = requests.post(categories_url, auth=auth, json={"name": cat}, timeout=10)
                        create_resp.raise_for_status()
                        cid = create_resp.json().get("id")
                    
                    if cid and cid not in cat_ids:
                        cat_ids.append(cid)
                        
                except Exception as e:
                    self.logger.warning(f"Error processing category '{cat}': {e}")
                    
            payload["categories"] = cat_ids

            # Process tags
            tags_url = f"{wp_base_url}/tags"
            tag_ids = []
            
            for tag in tags:
                try:
                    resp = requests.get(tags_url, auth=auth, params={"search": tag}, timeout=10)
                    resp.raise_for_status()
                    found = resp.json()
                    
                    tid = next((t["id"] for t in found if t["name"].lower() == tag.lower()), None)
                    if not tid and found:
                        tid = found[0]["id"]
                    
                    if not tid:
                        # Create new tag
                        create_resp = requests.post(tags_url, auth=auth, json={"name": tag}, timeout=10)
                        create_resp.raise_for_status()
                        tid = create_resp.json().get("id")
                    
                    if tid and tid not in tag_ids:
                        tag_ids.append(tid)
                        
                except Exception as e:
                    self.logger.warning(f"Error processing tag '{tag}': {e}")
                    
            payload["tags"] = tag_ids

            # Create the post
            posts_url = f"{wp_base_url}/posts"
            post_resp = requests.post(posts_url, auth=auth, json=payload, timeout=30)
            post_resp.raise_for_status()
            
            post_id = post_resp.json().get("id")
            if not post_id:
                self.logger.error("❌ Post created but ID not returned")
                return None, None

            # Set SEO metadata based on plugin version
            try:
                # Get SEO plugin version from config (default to 'new' for backward compatibility)
                seo_plugin_version = self.config.get('seo_plugin_version', 'new')
                
                if seo_plugin_version == 'old':
                    # Old AIOSEO Pack Pro v2.7.1 format - uses WordPress meta fields
                    seo_data = {
                        "meta": {
                            "_aioseop_title": seo_title,
                            "_aioseop_description": meta_description
                        }
                    }
                    # Add keywords (focus + additional keyphrases)
                    if focus_keyphrase or additional_keyphrases:
                        all_keyphrases = []
                        if focus_keyphrase:
                            all_keyphrases.append(focus_keyphrase)
                        if additional_keyphrases:
                            all_keyphrases.extend(additional_keyphrases)
                        seo_data["meta"]["_aioseop_keywords"] = ", ".join(all_keyphrases)
                    
                    self.logger.info(f"🔧 Using old AIOSEO format (v2.7.1) for SEO metadata")
                    
                    # For old version, use PUT request to update the post with meta fields
                    update_resp = requests.post(f"{posts_url}/{post_id}", auth=auth, json=seo_data, timeout=10)
                    update_resp.raise_for_status()
                    self.logger.info("✅ Old AIOSEO SEO metadata updated successfully")
                    
                else:
                    # New AIOSEO Pro v4.7.3+ format - uses aioseo_meta_data field
                    seo_data = {
                        "aioseo_meta_data": {
                            "title": seo_title,
                            "description": meta_description
                        }
                    }
                    # Add focus keyphrase tag and keyphrases structure
                    if focus_keyphrase:
                        seo_data["aioseo_meta_data"]["focus_keyphrase"] = focus_keyphrase
                        seo_data["aioseo_meta_data"]["keyphrases"] = {
                            "focus": {
                                "keyphrase": focus_keyphrase
                            },
                            "additional": [
                                {"keyphrase": kp} for kp in (additional_keyphrases or [])
                            ]
                        }
                    
                    self.logger.info(f"🔧 Using new AIOSEO format (v4.7.3+) for SEO metadata")
                    
                    # For new version, use the aioseo_meta_data field
                    update_resp = requests.post(f"{posts_url}/{post_id}", auth=auth, json=seo_data, timeout=10)
                    update_resp.raise_for_status()
                    self.logger.info("✅ New AIOSEO SEO metadata updated successfully")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to update SEO metadata: {e}")
                # Log the response for debugging
                if 'update_resp' in locals():
                    self.logger.warning(f"Response status: {update_resp.status_code}")
                    self.logger.warning(f"Response text: {update_resp.text[:500]}")

            self.logger.info(f"✅ WordPress draft post created (ID: {post_id})")
            return post_id, title

        except Exception as e:
            self.logger.error(f"❌ Error posting to WordPress: {e}")
            return None, None