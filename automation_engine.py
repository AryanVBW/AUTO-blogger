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
        
        # Initialize configurations
        self.setup_configurations()
        
    def setup_configurations(self):
        """Setup all configuration dictionaries"""
        
        # Category keywords mapping
        self.CATEGORY_KEYWORDS = {
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
        
        # Internal links
        self.INTERNAL_LINKS = {
            "Latest News": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/",
            "Academy": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/academy/",
            "Analysis": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/analysis/",
            "Champions League": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/champions-league/",
            "Europa League": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/europa-league/",
            "Exclusive": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/exclusive/",
            "FA Cup": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/fa-cup/",
            "Fantasy Premier League": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/fantasy-premier-league-fpl/",
            "Injury News": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/premier-league-injury-news/",
            "International": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/international/",
            "League Cup": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/football-league-cup/",
            "Loan Watch": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/loan-watch/",
            "Match Preview": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/match-preview/",
            "Match Report": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/match-report/",
            "Player Profile": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/player-profile/",
            "Premier League Derbies": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/premier-league-derbies/",
            "Transfer News": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/premier-league-transfer-news-rumours/",
            "Liverpool": "https://premierleaguenewsnow.com/tag/liverpool-news-now/",
            "Arsenal": "https://premierleaguenewsnow.com/tag/arsenal-news-now/",
            "Manchester United": "https://premierleaguenewsnow.com/tag/manchester-united-news-now/",
            "Manchester City": "https://premierleaguenewsnow.com/tag/manchester-city-news-now/",
            "Tottenham": "https://premierleaguenewsnow.com/tag/tottenham-hotspur-news-now/",
            "Chelsea": "https://premierleaguenewsnow.com/tag/chelsea-news-now/",
            "West Ham": "https://premierleaguenewsnow.com/tag/west-ham-united-news-now/",
            "Wolves": "https://premierleaguenewsnow.com/tag/wolverhampton-wanderers-news-now/",
            "Newcastle United": "https://premierleaguenewsnow.com/tag/newcastle-united-news-now/",
            "Leicester City": "https://premierleaguenewsnow.com/tag/leicester-city-news-now/",
            "Aston Villa": "https://premierleaguenewsnow.com/tag/aston-villa-news-now/",
            "Brighton": "https://premierleaguenewsnow.com/tag/brighton-hove-albion-news-now/",
            "Crystal Palace": "https://premierleaguenewsnow.com/tag/crystal-palace-news-now/",
            "Brentford": "https://premierleaguenewsnow.com/tag/brentford-news-now/",
        }
        
        # External links
        self.EXTERNAL_LINKS = {
            "premier league": "https://www.premierleague.com/",
            "leeds united": "https://unitedleeds.com/",
            "tottenham": "https://tottenhaminsight.com/",
            "tottenham hotspur": "https://tottenhaminsight.com/",
            "spurs": "https://tottenhaminsight.com/",
            "stats": "https://fbref.com/en/",
            "transfer news": "https://www.transfermarkt.com/",
            "transfer update": "https://www.transfermarkt.com/",
        }
        
        # Static clubs for tag generation
        self.STATIC_CLUBS = {
            "AFC Bournemouth", "Arsenal", "Aston Villa", "Brentford",
            "Brighton", "Burnley", "Chelsea", "Crystal Palace",
            "Everton", "Fulham", "Huddersfield Town", "Leeds United",
            "Leicester City", "Liverpool", "Manchester City", "Manchester United",
            "Newcastle United", "Norwich City", "Nottingham Forest", "Sheffield United",
            "Southampton", "Tottenham Hotspur", "Watford", "West Bromwich Albion",
            "West Ham United", "Wolverhampton Wanderers", "Women's Super League"
        }
        
        # Tag synonyms
        self.TAG_SYNONYMS = {
            "Spurs": "Tottenham Hotspur",
            "Tottenham": "Tottenham Hotspur",
            "Leeds": "Leeds United",
            "Newcastle": "Newcastle United",
        }
        
        # Stop words for slug generation
        self.STOP_WORDS = {
            'a', 'an', 'and', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'from',
            'by', 'with', 'is', 'are', 'was', 'were', 'be', 'has', 'had', 'will',
            'would', 'this', 'that', 'these', 'those', 'as', 'it', 'its', 'but',
            'or', 'not', 'so', 'can', 'amid'
        }
        
        # Do-follow URLs
        self.DO_FOLLOW_URLS = {
            "https://tottenhaminsight.com/",
            "https://unitedleeds.com/",
        }
        
    @contextmanager
    def get_selenium_driver_context(self):
        """Context manager for Chrome WebDriver"""
        driver_instance = None
        try:
            service = Service(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--log-level=3')
            options.add_argument('--incognito')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

            driver_instance = webdriver.Chrome(service=service, options=options)
            self.logger.info("✅ Selenium WebDriver initialized successfully")
            yield driver_instance
            
        except WebDriverException as e:
            self.logger.error(f"❌ Error initializing Selenium WebDriver: {e}")
            yield None
            
        finally:
            if driver_instance:
                self.logger.info("ℹ️ Quitting Selenium WebDriver")
                driver_instance.quit()

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
                # Try alternative selectors
                alternative_selectors = [
                    "article h2 a",
                    "h2 a",
                    "h3 a",
                    ".post-title a",
                    ".entry-title a",
                    "a[href*='post']",
                    "a[href*='article']"
                ]
                
                self.logger.warning(f"⚠️ No articles found with selector '{selector}', trying alternatives...")
                
                for alt_selector in alternative_selectors:
                    alt_tags = soup.select(alt_selector)
                    if alt_tags:
                        self.logger.info(f"✅ Found {len(alt_tags)} articles with alternative selector: {alt_selector}")
                        tags = alt_tags
                        break
                
                if not tags:
                    self.logger.error("❌ No articles found with any selector")
                    # Log the page structure for debugging
                    self.logger.debug("Page structure sample:")
                    articles = soup.find_all(['article', 'div'], limit=5)
                    for i, article in enumerate(articles):
                        self.logger.debug(f"Article {i+1}: {str(article)[:200]}...")
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
                
            # Avoid obvious non-article URLs
            invalid_patterns = [
                'javascript:', 'mailto:', '#', 'tag/', 'category/', 
                'author/', 'page/', 'search/', 'login', 'register',
                '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.pdf'
            ]
            
            url_lower = url.lower()
            for pattern in invalid_patterns:
                if pattern in url_lower:
                    return False
                    
            return True
            
        except Exception:
            return False

    def extract_article_with_selenium(self, driver: webdriver.Chrome, url: str, timeout: int = 10) -> Tuple[Optional[str], Optional[str]]:
        """Extract article content using Selenium"""
        if not driver:
            self.logger.error("No WebDriver provided")
            return None, None
            
        if not url:
            self.logger.error("No URL provided")
            return None, None

        try:
            driver.get(url)
            wait = WebDriverWait(driver, timeout)

            # Extract title
            title_el = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            title = title_el.text.strip() or None

            # Extract content paragraphs
            paras = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article p")))
            content = "\n\n".join(p.text for p in paras) if paras else None

            self.logger.info(f"Extracted title '{title}' and {len(paras)} paragraphs from {url}")
            return title, content

        except TimeoutException:
            self.logger.error(f"❌ Selenium extraction timed out for {url}")
            return None, None
            
        except WebDriverException as e:
            self.logger.error(f"❌ Selenium WebDriver error during extraction for {url}: {e}")
            return None, None
            
        except Exception as e:
            self.logger.exception(f"❌ Unexpected error during Selenium extraction for {url}")
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
        """Apply targeted capitalization rules"""
        replacements = {
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
            r'\bvardy\b': 'Vardy',
            r'\belland road\b': 'Elland Road',
            r'\bleeds united\b': 'Leeds United',
            r'\bjaka bijol\b': 'Jaka Bijol',
            r'\blukas nmecha\b': 'Lukas Nmecha',
            r'\bnikola krstovic\b': 'Nikola Krstovic',
            r'\blecce\b': 'Lecce',
            r'\budinese\b': 'Udinese',
            r'\bs a\b': 'Serie A',
        }

        for lower_term, correct_term in replacements.items():
            text = re.sub(lower_term, correct_term, text, flags=re.IGNORECASE)

        return text

    def gemini_paraphrase_content_and_title(self, original_title: str, article_html: str) -> Tuple[str, str]:
        """Use Gemini to paraphrase content and generate title"""
        
        style_prompt = """
You are a highly skilled and passionate Premier League football blogger. Your task is to rewrite the provided HTML article content into a clean, engaging, and SEO-optimized blog post, specifically tailored for avid football fans. Adhere to every single rule below with utmost precision, without exception:

**Crucial Note on Keywords:** Before generating content, thoroughly analyze the provided article to identify its main subjects, key players (even if names aren't used directly in headlines/headings), clubs, and central themes. These will serve as the "article-specific keywords" required for your headings and overall SEO optimization.

**CONTENT REWRITE RULES:**

1. **Opening Hook:** Begin with 2–3 exciting, punchy introductory sentences (no heading). These must immediately highlight the central story, **explicitly incorporating the most prominent article-related keywords, including main club(s) and relevant player names**, and clearly stating why the topic matters to football fans.
2. **Strategic Headings:** Insert exactly 2 or 3 `<h3>` headings. Each heading **must prominently feature key article-related keywords, including main club names and specific player names where relevant**. These headings must follow **sentence case** (only the first word and proper nouns capitalized).
3. **Authentic Voice:** Maintain a confident, energetic, fan-first tone. Write as if you're talking to fellow football fans, offering strong opinions and insider-style commentary.
4. **Active Voice:** Ensure that at least 90% of all sentences use the active voice.
5. **Concise Sentences:** Keep every sentence **under 15 words**.
6. **Clear Language:** Use simple, everyday football language. Avoid jargon, buzzwords, formal tones, or robotic phrasing.
7. **Paragraph Structure:** Use short paragraphs — each with a maximum of 2–3 sentences.
8. **Smooth Transitions:** Use transition words like "however," "meanwhile," "furthermore," "as a result," or "consequently" in at least 30% of sentences to ensure seamless flow.
9. **HTML Integrity:** Wrap **every paragraph** in proper `<p>` tags. Do **not** use any Markdown or bullet points.
10. **Definitive Conclusion:** Conclude with a strong opinion or outlook using **one of the following exact headings**: `<h3>Author's take</h3>`, `<h3>Conclusion</h3>`, `<h3>What's next</h3>`
11. **Word Count:** The total output must be **at least 400 words**.
12. **Readability Score:** Ensure a **Flesch Reading Ease score between 60–70**.
13. **Human Tone:** The writing must sound natural, emotional, and undeniably human — never robotic.
14. **WordPress Ready:** The output must begin directly with a `<p>` tag and contain valid HTML only (no Markdown, no code blocks, no system messages).

**HEADLINE GENERATION RULES:**

- **Singular Headline:** Generate **exactly one headline** for the rewritten article. No more, no less.
- **No Specific Names:** **Crucially, explicitly avoid using any specific player or manager names** in the headline.
- **Indirect Identifiers Only:** Instead of names, utilize indirect and descriptive phrases. Examples include: "25yo winger," "veteran midfielder," "Championship side's new target," or "former Arsenal ace."
- **Curiosity-Driven Hook:** The headline must be intensely **curiosity-driven and indirect**. Its primary purpose is to strongly tease the story without revealing its core details immediately, compelling the reader to click and learn more.
- **Clean Punctuation:** Do **NOT** include any quotes or punctuation marks in the headline whatsoever.
- **Strict Sentence Case:** Write the headline strictly in **sentence case**. This means:
  * Only the first word of the headline must be capitalized.
  * All proper nouns (e.g., specific player names, club names, league names like "Premier League," competition names like "Champions League," specific stadium names like "Old Trafford") must be capitalized according to standard English capitalization rules.
  * All other words within the headline must remain in lowercase.
  * **Example: Championship side eyes striker with similar traits to former Premier League ace**
- **Engaging Vocabulary:** Use simple, clear vocabulary that genuinely connects with football fans, ensuring the headline functions as a strong, compelling hook.
"""

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

            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            content_match = re.search(r"CONTENT:\s*(.*?)\s*HEADLINE:", text, re.DOTALL)
            headline_match = re.search(r"HEADLINE:\s*(.+)", text)

            if not content_match or not headline_match:
                raise ValueError("Gemini response missing expected sections.")

            html = content_match.group(1).strip()
            headline_raw = headline_match.group(1).strip()

            # Apply post-processing
            processed_html = self.post_process_text(html)
            processed_headline_raw = self.post_process_text(headline_raw)

            # Apply sentence case to headline
            final_headline = self.sentence_case(processed_headline_raw)

            return processed_html, final_headline
            
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
        """Generate SEO title and meta description"""
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
                return seo_title, meta_desc

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"

            prompt = f"""
You are a passionate Premier League football blogger.

1. Read the article content below and identify its one primary subject. Then rewrite the original title into a single, sharp, SEO-friendly headline.

- Preserve the correct capitalization of all proper nouns exactly as in the original.
- Use sentence case—capitalize only the first word and proper nouns. All other words should be lowercase.
- The headline must be **strictly** between 50 and 59 characters in length (counting spaces and punctuation).
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
\"\"\"
{content}
\"\"\"
"""

            resp = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            resp.raise_for_status()
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

            seo_title, meta_description = "", ""

            match_seo = re.search(r"SEO_TITLE:\s*(.*?)\s*META:", text, re.DOTALL)
            match_meta = re.search(r"META:\s*(.+)", text, re.DOTALL)

            if match_seo:
                seo_title = match_seo.group(1).strip()
            if match_meta:
                meta_description = match_meta.group(1).strip()

            # Ensure SEO title fits 50–59 characters
            length = len(seo_title)
            if length > 59:
                seo_title = seo_title[:59].rsplit(" ", 1)[0].strip()
            elif length < 50:
                self.logger.warning("SEO title is under 50 characters")

            self.logger.info(f"Generated SEO title ({len(seo_title)} chars): {seo_title}")
            return seo_title, meta_description

        except Exception as e:
            self.logger.error(f"❌ Error generating SEO metadata: {e}")
            # Fallback
            seo_title = title[:59] if len(title) > 59 else title
            clean_content = re.sub(r'<[^>]+>', '', content)
            meta_desc = clean_content[:157] + "..." if len(clean_content) > 157 else clean_content
            return seo_title, meta_desc

    def detect_categories(self, text: str) -> List[str]:
        """Detect categories from text"""
        lower = text.lower()
        cats = ["Latest News"]  # Always include default category

        for kw, subcat in self.CATEGORY_KEYWORDS.items():
            if kw in lower and subcat not in cats:
                cats.append(subcat)
                self.logger.info(f"Matched category '{subcat}' via keyword '{kw}'")

        return cats

    def generate_tags_with_gemini(self, content: str) -> List[str]:
        """Generate tags using Gemini AI"""
        seen = set()
        tags = []

        try:
            gemini_api_key = self.config.get('gemini_api_key', '')
            if not gemini_api_key:
                # Fallback to simple tag generation
                return self.generate_tags_fallback(content)

            prompt = f"""
Extract only the full names of football players and the full names of the clubs mentioned in this article.
Return them as a comma-separated list with no extra punctuation.

Article Content:
\"\"\"
{content}
\"\"\"
"""
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
            
            resp = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            
            if resp.status_code == 200:
                raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                for cand in [c.strip() for c in raw.split(",") if c.strip()]:
                    name = re.sub(r"\s+", " ", cand)
                    
                    # Synonym normalization
                    if name in self.TAG_SYNONYMS:
                        name = self.TAG_SYNONYMS[name]
                        
                    # Keep if valid and present in content
                    if (
                        (name in self.STATIC_CLUBS or re.fullmatch(r"[A-Z][a-z]+(?:\s[A-Z][a-z]+)*", name))
                        and re.search(rf"\b{re.escape(name)}\b", content, re.IGNORECASE)
                        and name not in seen
                    ):
                        seen.add(name)
                        tags.append(name)
            else:
                self.logger.error(f"Gemini Tag API Error {resp.status_code}: {resp.text}")

        except Exception as e:
            self.logger.error(f"❌ Error generating tags with Gemini: {e}")

        # Fallback scan
        for club in self.STATIC_CLUBS:
            if club not in seen and re.search(rf"\b{re.escape(club)}\b", content, re.IGNORECASE):
                seen.add(club)
                tags.append(club)

        self.logger.info(f"Generated tags: {tags}")
        return tags

    def generate_tags_fallback(self, content: str) -> List[str]:
        """Fallback tag generation without Gemini"""
        tags = []
        
        # Check for static clubs
        for club in self.STATIC_CLUBS:
            if re.search(rf"\b{re.escape(club)}\b", content, re.IGNORECASE):
                tags.append(club)
                
        return tags[:10]  # Limit to 10 tags

    def generate_slug(self, title: str, max_length: int = 50) -> str:
        """Generate URL-friendly slug from title"""
        # Normalize and clean
        text_norm = unicodedata.normalize('NFKD', title)
        text_ascii = text_norm.encode('ascii', 'ignore').decode('ascii')
        text_clean = re.sub(r'[^a-z0-9\s-]', '', text_ascii.lower())

        # Filter stop words
        words = text_clean.split()
        keywords = [w for w in words if w not in self.STOP_WORDS]

        # Join and clean up
        slug = '-'.join(keywords)
        slug = re.sub(r'-{2,}', '-', slug)
        slug = slug.strip('-')

        # Trim to max_length
        if max_length and len(slug) > max_length:
            temp_slug = slug[:max_length]
            if "-" in temp_slug:
                slug = temp_slug.rsplit('-', 1)[0]
            else:
                slug = temp_slug
            slug = slug.strip('-')

        self.logger.info(f"Generated slug: {slug} (Length: {len(slug)})")
        return slug

    def post_to_wordpress_with_seo(
        self, 
        title: str, 
        content: str, 
        categories: List[str], 
        tags: List[str], 
        excerpt: Optional[str] = None,
        seo_title: Optional[str] = None, 
        meta_description: Optional[str] = None,
        focus_keyphrase: Optional[str] = None,
        additional_keyphrases: Optional[List[str]] = None
    ) -> Tuple[Optional[int], Optional[str]]:
        """Post to WordPress with SEO optimization"""
        
        try:
            wp_base_url = self.config.get('wp_base_url', '')
            username = self.config.get('wp_username', '')
            password = self.config.get('wp_password', '')
            
            if not all([wp_base_url, username, password]):
                self.logger.error("WordPress credentials not properly configured")
                return None, None
                
            auth = HTTPBasicAuth(username, password)
            
            # Generate SEO elements if not provided
            if not seo_title or not meta_description:
                self.logger.info("Generating SEO title and meta description")
                seo_title, meta_description = self.generate_seo_title_and_meta(title, content)
                
            # Generate keyphrases if not provided
            if not focus_keyphrase or not additional_keyphrases:
                self.logger.info("Extracting focus keyphrase and additional keyphrases")
                focus_keyphrase, additional_keyphrases = self.extract_keyphrases_with_gemini(title, content)
                
            seo_slug = self.generate_slug(seo_title)

            # Generate excerpt if not provided
            if not excerpt:
                clean = re.sub(r'<[^>]+>', '', content).strip()
                if len(clean) > 300:
                    excerpt = clean[:297]
                    last_space = excerpt.rfind(' ')
                    if last_space != -1:
                        excerpt = excerpt[:last_space]
                    excerpt += "..."
                else:
                    excerpt = clean

            # Prepare post payload
            payload = {
                "title": title,
                "content": content,
                "slug": seo_slug,
                "excerpt": excerpt,
                "status": "draft",
                "categories": [],
                "tags": [],
                "yoast_head": "",
                "focuskw": focus_keyphrase,
                "metadesc": meta_description,
                "additional_keyphrases": additional_keyphrases
            }

            # Handle categories
            categories_url = f"{wp_base_url}/categories"
            cat_ids = []
            
            for cat in categories:
                try:
                    resp = requests.get(categories_url, auth=auth, params={"search": cat}, timeout=10)
                    resp.raise_for_status()
                    found = resp.json()
                    
                    cid = None
                    if found:
                        # Look for exact match first
                        cid = next((c["id"] for c in found if c["name"].lower() == cat.lower()), None)
                        if not cid:
                            cid = found[0]["id"]  # Use first match
                    
                    if not cid:
                        # Create new category
                        crt = requests.post(categories_url, auth=auth, json={"name": cat}, timeout=10)
                        crt.raise_for_status()
                        cid = crt.json().get("id")
                        
                    if cid and cid not in cat_ids:
                        cat_ids.append(cid)
                        
                except HTTPError as e:
                    if e.response.status_code == 401:
                        self.logger.error("401 Unauthorized - check WordPress credentials")
                        return None, None
                    self.logger.warning(f"HTTP error for category '{cat}': {e}")
                except Exception as e:
                    self.logger.warning(f"Error processing category '{cat}': {e}")
                    
            payload["categories"] = cat_ids

            # Handle tags
            tags_url = f"{wp_base_url}/tags"
            tag_ids = []
            
            for tag in tags:
                try:
                    resp = requests.get(tags_url, auth=auth, params={"search": tag}, timeout=10)
                    resp.raise_for_status()
                    found = resp.json()
                    
                    tid = None
                    if found:
                        tid = next((t["id"] for t in found if t["name"].lower() == tag.lower()), None)
                        if not tid:
                            tid = found[0]["id"]
                    
                    if not tid:
                        # Create new tag
                        crt = requests.post(tags_url, auth=auth, json={"name": tag}, timeout=10)
                        crt.raise_for_status()
                        tid = crt.json().get("id")
                        
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
                self.logger.error("Post created but ID not returned")
                return None, None

            # Update with AIOSEO meta data including keyphrases
            try:
                aioseo_meta = {
                    "aioseo_meta_data": {
                        "title": seo_title, 
                        "description": meta_description,
                        "keyphrases": {
                            "focus": {
                                "keyphrase": focus_keyphrase,
                                "score": 100
                            },
                            "additional": [
                                {"keyphrase": kp, "score": 75} 
                                for kp in (additional_keyphrases or [])
                            ]
                        }
                    }
                }
                
                # Also add Yoast SEO meta fields for compatibility
                yoast_meta = {
                    "yoast_wpseo_focuskw": focus_keyphrase,
                    "yoast_wpseo_metadesc": meta_description,
                    "yoast_wpseo_title": seo_title
                }
                
                # Try AIOSEO format first
                upd = requests.put(f"{posts_url}/{post_id}", auth=auth, json=aioseo_meta, timeout=10)
                if upd.status_code not in [200, 201]:
                    # Fallback to Yoast format
                    upd = requests.put(f"{posts_url}/{post_id}", auth=auth, json=yoast_meta, timeout=10)
                
                upd.raise_for_status()
                self.logger.info(f"✅ SEO meta data updated with focus keyphrase: {focus_keyphrase}")
                
            except Exception as e:
                self.logger.warning(f"Could not update SEO meta data: {e}")
                # Try updating custom fields directly
                try:
                    meta_fields = {
                        "meta": {
                            "_yoast_wpseo_focuskw": focus_keyphrase,
                            "_yoast_wpseo_metadesc": meta_description,
                            "_yoast_wpseo_title": seo_title,
                            "focus_keyphrase": focus_keyphrase,
                            "additional_keyphrases": ", ".join(additional_keyphrases or [])
                        }
                    }
                    upd = requests.put(f"{posts_url}/{post_id}", auth=auth, json=meta_fields, timeout=10)
                    self.logger.info(f"✅ SEO custom fields updated with keyphrases")
                except Exception as e2:
                    self.logger.warning(f"Could not update custom fields either: {e2}")

            self.logger.info(f"✅ WordPress draft post created (ID: {post_id})")
            return post_id, seo_title

        except HTTPError as e:
            self.logger.error(f"HTTP error creating WordPress post: {e}")
            return None, None
        except Exception as e:
            self.logger.error(f"Error creating WordPress post: {e}")
            return None, None

    def load_posted_links(self) -> set:
        """Load previously posted links"""
        if os.path.exists(self.posted_links_file):
            try:
                with open(self.posted_links_file, "r") as f:
                    return set(json.load(f))
            except Exception as e:
                self.logger.error(f"Error loading posted links: {e}")
        return set()

    def save_posted_links(self, links: set):
        """Save posted links to file"""
        try:
            with open(self.posted_links_file, "w") as f:
                json.dump(list(links), f)
        except Exception as e:
            self.logger.error(f"Error saving posted links: {e}")

    def extract_keyphrases_with_gemini(self, title: str, content: str) -> Tuple[str, List[str]]:
        """Extract focus keyphrase and additional keyphrases using Gemini AI"""
        try:
            gemini_api_key = self.config.get('gemini_api_key', '')
            if not gemini_api_key:
                return self.extract_keyphrases_fallback(title, content)

            # Clean content for analysis
            clean_content = re.sub(r'<[^>]+>', '', content).strip()
            
            prompt = f"""
Analyze this football article and extract SEO keyphrases:

Title: {title}
Content: {clean_content[:1000]}...

Based on this content, provide:
1. ONE primary focus keyphrase (2-4 words, most important topic)
2. 3-5 additional keyphrases (2-4 words each, related topics)

The keyphrases should be:
- Natural search terms people would use
- Related to football/soccer, clubs, players, transfers, matches
- Found naturally in the content
- Good for SEO ranking

Format your response exactly like this:
FOCUS: primary keyphrase here
ADDITIONAL: keyphrase1, keyphrase2, keyphrase3, keyphrase4, keyphrase5
"""
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
            
            resp = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            
            if resp.status_code == 200:
                raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                
                # Parse response
                focus_keyphrase = ""
                additional_keyphrases = []
                
                for line in raw.split('\n'):
                    line = line.strip()
                    if line.startswith('FOCUS:'):
                        focus_keyphrase = line.replace('FOCUS:', '').strip()
                    elif line.startswith('ADDITIONAL:'):
                        additional_text = line.replace('ADDITIONAL:', '').strip()
                        additional_keyphrases = [kp.strip() for kp in additional_text.split(',') if kp.strip()]
                
                # Validate and clean keyphrases
                if focus_keyphrase:
                    focus_keyphrase = re.sub(r'\s+', ' ', focus_keyphrase).lower()
                
                additional_keyphrases = [
                    re.sub(r'\s+', ' ', kp).lower() 
                    for kp in additional_keyphrases 
                    if kp and len(kp.split()) <= 4
                ][:5]  # Limit to 5 additional keyphrases
                
                self.logger.info(f"Extracted focus keyphrase: {focus_keyphrase}")
                self.logger.info(f"Extracted additional keyphrases: {additional_keyphrases}")
                
                return focus_keyphrase, additional_keyphrases
            else:
                self.logger.error(f"Gemini Keyphrase API Error {resp.status_code}: {resp.text}")
                
        except Exception as e:
            self.logger.error(f"❌ Error extracting keyphrases with Gemini: {e}")
        
        # Fallback
        return self.extract_keyphrases_fallback(title, content)

    def extract_keyphrases_fallback(self, title: str, content: str) -> Tuple[str, List[str]]:
        """Fallback keyphrase extraction without Gemini"""
        # Clean content
        clean_title = re.sub(r'<[^>]+>', '', title).strip().lower()
        clean_content = re.sub(r'<[^>]+>', '', content).strip().lower()
        combined_text = f"{clean_title} {clean_content}"
        
        # Common football keywords that might be focus keyphrases
        football_terms = [
            "premier league", "transfer news", "manchester united", "liverpool", 
            "arsenal", "chelsea", "manchester city", "tottenham", "leeds united",
            "champions league", "europa league", "fa cup", "injury update",
            "match report", "player profile", "transfer deal", "contract extension",
            "goal scorer", "midfielder", "defender", "striker", "goalkeeper"
        ]
        
        # Find focus keyphrase (most prominent term)
        focus_keyphrase = ""
        max_mentions = 0
        
        for term in football_terms:
            mentions = len(re.findall(rf'\b{re.escape(term)}\b', combined_text))
            if mentions > max_mentions:
                max_mentions = mentions
                focus_keyphrase = term
        
        # If no specific term found, use title words
        if not focus_keyphrase:
            title_words = re.findall(r'\b[a-z]+\b', clean_title)
            if len(title_words) >= 2:
                focus_keyphrase = ' '.join(title_words[:2])
        
        # Extract additional keyphrases from most frequent word combinations
        words = re.findall(r'\b[a-z]+\b', combined_text)
        word_freq = {}
        
        # Count 2-3 word combinations
        for i in range(len(words) - 1):
            if words[i] not in self.STOP_WORDS and words[i+1] not in self.STOP_WORDS:
                phrase = f"{words[i]} {words[i+1]}"
                word_freq[phrase] = word_freq.get(phrase, 0) + 1
                
                # Also check 3-word combinations
                if i < len(words) - 2 and words[i+2] not in self.STOP_WORDS:
                    phrase3 = f"{words[i]} {words[i+1]} {words[i+2]}"
                    word_freq[phrase3] = word_freq.get(phrase3, 0) + 1
        
        # Get top additional keyphrases
        additional_keyphrases = []
        sorted_phrases = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        for phrase, count in sorted_phrases:
            if (count >= 2 and 
                phrase != focus_keyphrase and 
                len(phrase.split()) <= 3 and
                len(additional_keyphrases) < 5):
                additional_keyphrases.append(phrase)
        
        self.logger.info(f"Fallback focus keyphrase: {focus_keyphrase}")
        self.logger.info(f"Fallback additional keyphrases: {additional_keyphrases}")
        
        return focus_keyphrase, additional_keyphrases

    def generate_and_upload_featured_image(self, title: str, content: str, post_id: int) -> Optional[int]:
        """Generate an image using OpenAI and upload it as a featured image to WordPress"""
        try:
            openai_api_key = self.config.get('openai_api_key', '')
            if not openai_api_key:
                self.logger.error("OpenAI API key not configured")
                return None
            
            # Clean content for prompt creation
            clean_content = re.sub(r'<[^>]+>', '', content[:500])
            clean_title = re.sub(r'<[^>]+>', '', title)
            
            # Create a prompt for image generation
            prompt = f"Create a realistic, professional image for a football article with title: {clean_title}. The image should be suitable as a featured image for a sports blog, showing relevant football/soccer imagery. Make it look like a professional sports photograph."
            
            self.logger.info(f"🎨 Generating image with OpenAI for: {clean_title[:50]}...")
            
            # Make OpenAI API request
            import base64
            import requests
            from io import BytesIO
            
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "dall-e-3",
                    "prompt": prompt,
                    "n": 1,
                    "size": "1024x1024",
                    "response_format": "b64_json"
                },
                timeout=60
            )
            
            if response.status_code != 200:
                self.logger.error(f"❌ OpenAI API error: {response.status_code} - {response.text}")
                return None
            
            # Get the image data
            image_data = response.json()["data"][0]["b64_json"]
            image_bytes = base64.b64decode(image_data)
            
            # Upload to WordPress
            wp_base_url = self.config.get('wp_base_url', '')
            username = self.config.get('wp_username', '')
            password = self.config.get('wp_password', '')
            
            if not all([wp_base_url, username, password]):
                self.logger.error("WordPress credentials not properly configured")
                return None
            
            auth = HTTPBasicAuth(username, password)
            
            # Generate a filename based on the post title
            import hashlib
            import time
            
            title_hash = hashlib.md5(clean_title.encode()).hexdigest()[:10]
            timestamp = int(time.time())
            filename = f"ai-generated-{title_hash}-{timestamp}.png"
            
            # Upload the image to WordPress
            media_url = f"{wp_base_url}/media"
            
            upload_response = requests.post(
                media_url,
                auth=auth,
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"',
                    "Content-Type": "image/png"
                },
                data=image_bytes,
                timeout=30
            )
            
            if upload_response.status_code not in [200, 201]:
                self.logger.error(f"❌ WordPress media upload error: {upload_response.status_code} - {upload_response.text}")
                return None
            
            media_id = upload_response.json().get("id")
            if not media_id:
                self.logger.error("❌ Media uploaded but ID not returned")
                return None
            
            # Set as featured image for the post
            if post_id:
                update_url = f"{wp_base_url}/posts/{post_id}"
                update_response = requests.post(
                    update_url,
                    auth=auth,
                    json={"featured_media": media_id},
                    timeout=10
                )
                
                if update_response.status_code not in [200, 201]:
                    self.logger.error(f"❌ Failed to set featured image: {update_response.status_code} - {update_response.text}")
                    return None
                
                self.logger.info(f"✅ Featured image set for post ID {post_id}")
            
            return media_id
            
        except Exception as e:
            self.logger.error(f"❌ Error generating/uploading image: {e}")
            return None
