#!/usr/bin/env python3
"""
Automatic CSS Selector Extractor
Analyzes web pages to automatically extract and suggest CSS selectors for article links

Copyright © 2025 AryanVBW
GitHub: https://github.com/AryanVBW
"""

import requests
import logging
import re
import time
from typing import List, Dict, Tuple, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import Counter
import json

class CSSelectorExtractor:
    """Automatically extract and analyze CSS selectors for article links"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Common article link patterns to look for
        self.article_patterns = [
            r'/article/',
            r'/post/',
            r'/news/',
            r'/story/',
            r'/blog/',
            r'/\d{4}/\d{2}/',           # Date patterns like /2024/01/
            r'/\d{4}/\d{1,2}/\d{1,2}/', # Full date patterns
            r'-\d{4}-\d{2}-\d{2}',      # Date in URL
            r'/read/',
            r'/watch/',
            r'/p/',                       # Substack/Medium short paths
            r'/entry/',
            r'/topic/',
            r'/feature/',
            r'/review/',
            r'/guide/',
            r'/opinion/',
            r'/analysis/',
        ]

        # Common non-article patterns to avoid
        self.exclude_patterns = [
            r'javascript:',
            r'mailto:',
            r'^#',
            r'/tag/', r'/tags/',
            r'/category/', r'/categories/',
            r'/author/', r'/authors/',
            r'/page/\d+',
            r'/search/',
            r'/login', r'/signup', r'/register',
            r'/contact',
            r'/about$', r'/about/',
            r'/privacy', r'/terms', r'/tos',
            r'\.(css|js|png|jpg|jpeg|gif|svg|pdf|xml|rss|ico|woff|ttf|eot)$',
            r'/feed/', r'/rss/',
            r'/sitemap',
            r'/cart', r'/checkout', r'/account',
            r'/wp-admin', r'/wp-login',
            r'/cdn-cgi/',
            r'#comments$',
        ]

        # CMS-specific known selectors — tried first for instant matching
        self.cms_selectors = [
            # WordPress
            "article h2 a", ".entry-title a", ".post-title a",
            ".wp-block-post-title a", ".hentry h2 a",
            # Ghost CMS
            ".post-card a", ".gh-card-link", ".post-feed .post-card-title a",
            # Medium
            "article a[data-action='open-post']", ".postArticle-readMore a",
            # Substack
            ".post-preview a", "[data-testid='post-preview-title'] a",
            # Hugo / Jekyll
            ".post-link", ".post-list a",
            # General news sites
            ".headline a", ".story-link", ".article-card a",
            ".teaser a", ".teaser__link",
            ".card-title a", ".news-title a",
            "[class*='title'] a", "[class*='article'] a",
            # Common patterns
            "article h3 a", "article h1 a",
            "main h2 a", "main h3 a",
            "h2 a", "h3 a",
        ]
        
        # Headers to mimic real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL to ensure proper protocol and format"""
        url = url.strip()
        
        # Remove common URL artifacts and malformed endings
        if url.endswith('/:'):
            url = url[:-2]
        elif url.endswith('//'):
            url = url[:-1]
        elif url.endswith('/') and not url.endswith('://'):
            url = url[:-1]
        
        # Remove any trailing colons that aren't part of protocol
        if url.endswith(':') and not url.endswith('://'):
            url = url[:-1]
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            # Default to HTTPS for modern websites
            url = 'https://' + url
        
        # Ensure the URL is properly formatted
        if url.count('://') > 1:
            # Fix double protocol issues
            parts = url.split('://')
            url = parts[0] + '://' + '://'.join(parts[1:]).replace('://', '')
        
        return url
    
    def _get_user_friendly_error(self, error: Exception, url: str) -> str:
        """Convert technical errors to user-friendly messages"""
        error_str = str(error).lower()
        
        if 'no route to host' in error_str or 'connection refused' in error_str:
            return f"Cannot connect to {url}. The website may be down or the URL may be incorrect."
        elif 'name or service not known' in error_str or 'nodename nor servname provided' in error_str:
            return f"Cannot find the website {url}. Please check if the URL is correct."
        elif 'timeout' in error_str:
            return f"Connection to {url} timed out. The website may be slow or temporarily unavailable."
        elif 'ssl' in error_str or 'certificate' in error_str:
            return f"SSL/Security certificate issue with {url}. The website may have security problems."
        elif 'max retries exceeded' in error_str:
            return f"Failed to connect to {url} after multiple attempts. The website may be temporarily unavailable."
        elif '404' in error_str:
            return f"Page not found at {url}. The URL may be incorrect or the page may have been moved."
        elif '403' in error_str:
            return f"Access denied to {url}. The website may be blocking automated requests."
        elif '500' in error_str or '502' in error_str or '503' in error_str:
            return f"Server error at {url}. The website is experiencing technical difficulties."
        else:
            return f"Network error accessing {url}: {str(error)}"
    
    def _fetch_with_fallback(self, url: str) -> requests.Response:
        """Fetch URL with HTTP/HTTPS fallback logic"""
        # Try the URL as provided first
        try:
            self.logger.debug(f"Attempting to fetch: {url}")
            response = requests.get(url, headers=self.headers, timeout=15, allow_redirects=True)
            if response.status_code == 200:
                return response
        except requests.exceptions.ConnectionError as e:
            self.logger.debug(f"Connection failed for {url}: {e}")
        except requests.exceptions.RequestException as e:
            self.logger.debug(f"Request failed for {url}: {e}")
        
        # If HTTPS failed, try HTTP
        if url.startswith('https://'):
            http_url = url.replace('https://', 'http://', 1)
            try:
                self.logger.debug(f"Falling back to HTTP: {http_url}")
                response = requests.get(http_url, headers=self.headers, timeout=15, allow_redirects=True)
                if response.status_code == 200:
                    return response
            except requests.exceptions.RequestException as e:
                self.logger.debug(f"HTTP fallback also failed for {http_url}: {e}")
        
        # If HTTP failed, try HTTPS (in case original was HTTP)
        elif url.startswith('http://'):
            https_url = url.replace('http://', 'https://', 1)
            try:
                self.logger.debug(f"Trying HTTPS: {https_url}")
                response = requests.get(https_url, headers=self.headers, timeout=15, allow_redirects=True)
                if response.status_code == 200:
                    return response
            except requests.exceptions.RequestException as e:
                self.logger.debug(f"HTTPS attempt also failed for {https_url}: {e}")
        
        # If all attempts failed, make one final attempt with the original URL
        # This will raise the actual exception for proper error handling
        return requests.get(url, headers=self.headers, timeout=15, allow_redirects=True)
    
    def analyze_url(self, url: str) -> Dict:
        """
        Analyze a URL and extract all possible CSS selectors for article links
        
        Args:
            url: The URL to analyze
            
        Returns:
            Dict containing analysis results with selectors, examples, and metadata
        """
        self.logger.info(f"Analyzing URL: {url}")
        
        # Normalize URL - ensure proper protocol
        normalized_url = self._normalize_url(url)
        
        try:
            # Fetch the page with fallback logic
            response = self._fetch_with_fallback(normalized_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract all links
            all_links = soup.find_all('a', href=True)
            self.logger.info(f"Found {len(all_links)} total links")

            # Quick CMS detection — try known selectors first for instant results
            cms_matches = self._try_cms_selectors(soup, normalized_url)

            # Filter potential article links
            article_links = self._filter_article_links(all_links, normalized_url)
            self.logger.info(f"Identified {len(article_links)} potential article links")

            # Generate CSS selectors from page analysis
            selectors = self._generate_selectors(article_links, soup)

            # Merge CMS matches (prioritized) with generated selectors
            if cms_matches:
                # Deduplicate by selector string, CMS matches first
                seen_selectors = set()
                merged = []
                for s in cms_matches + selectors:
                    if s['selector'] not in seen_selectors:
                        seen_selectors.add(s['selector'])
                        merged.append(s)
                selectors = merged[:15]  # Top 15

            # Get latest post information
            latest_post = self._find_latest_post(article_links, normalized_url)
            
            return {
                'url': normalized_url,
                'original_url': url,
                'total_links': len(all_links),
                'article_links_count': len(article_links),
                'selectors': selectors,
                'latest_post': latest_post,
                'analysis_timestamp': time.time(),
                'success': True
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = self._get_user_friendly_error(e, normalized_url)
            self.logger.error(f"[X] Network error analyzing {url} (normalized: {normalized_url}): {e}")
            return {
                'url': normalized_url,
                'original_url': url,
                'error': error_msg,
                'success': False
            }
        except Exception as e:
            self.logger.error(f"[X] Error analyzing {url} (normalized: {normalized_url}): {e}")
            return {
                'url': normalized_url,
                'original_url': url,
                'error': f"Analysis error: {str(e)}",
                'success': False
            }
    
    def _try_cms_selectors(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Try known CMS-specific selectors for instant matching"""
        results = []
        base_domain = urlparse(base_url).netloc

        for selector in self.cms_selectors:
            try:
                matches = soup.select(selector)
                if not matches:
                    continue

                # Validate matches are actual article links
                article_matches = []
                for match in matches:
                    href = match.get('href', '')
                    text = match.get_text().strip()
                    if not href or not text or len(text) < 8:
                        continue

                    full_url = urljoin(base_url, href)
                    link_domain = urlparse(full_url).netloc

                    # Must be same domain
                    if base_domain not in link_domain and link_domain not in base_domain:
                        continue

                    # Must not match exclude patterns
                    if any(re.search(p, full_url, re.IGNORECASE) for p in self.exclude_patterns):
                        continue

                    article_matches.append({
                        'href': full_url,
                        'text': text[:100]
                    })

                if len(article_matches) >= 2:  # Need at least 2 matches to be meaningful
                    effectiveness = len(article_matches) / len(matches) if matches else 0
                    results.append({
                        'selector': selector,
                        'total_matches': len(matches),
                        'article_matches': len(article_matches),
                        'effectiveness': effectiveness,
                        'examples': article_matches[:3],
                        'frequency': len(article_matches),
                    })
            except Exception:
                continue

        # Sort by article_matches * effectiveness
        results.sort(key=lambda x: (x['effectiveness'] * x['article_matches']), reverse=True)
        return results[:5]

    def _filter_article_links(self, links: List, base_url: str) -> List:
        """Filter links to find potential article links"""
        article_links = []
        base_domain = urlparse(base_url).netloc
        
        for link in links:
            href = link.get('href', '').strip()
            if not href:
                continue
            
            # Convert relative URLs to absolute
            if href.startswith('/'):
                full_url = urljoin(base_url, href)
            elif href.startswith('http'):
                full_url = href
            else:
                full_url = urljoin(base_url, href)
            
            # Check if it's from the same domain or subdomain
            link_domain = urlparse(full_url).netloc
            if base_domain not in link_domain and link_domain not in base_domain:
                continue
            
            # Check against exclude patterns
            if any(re.search(pattern, full_url, re.IGNORECASE) for pattern in self.exclude_patterns):
                continue
            
            # Check for article patterns or reasonable link text
            link_text = link.get_text().strip()
            has_article_pattern = any(re.search(pattern, full_url, re.IGNORECASE) for pattern in self.article_patterns)
            has_meaningful_text = len(link_text) > 10 and not re.match(r'^(Home|About|Contact|Login|Register)$', link_text, re.IGNORECASE)
            
            if has_article_pattern or has_meaningful_text:
                article_links.append({
                    'element': link,
                    'href': full_url,
                    'text': link_text,
                    'has_pattern': has_article_pattern
                })
        
        return article_links
    
    def _generate_selectors(self, article_links: List, soup: BeautifulSoup) -> List[Dict]:
        """Generate CSS selectors for the article links"""
        selectors = []
        
        if not article_links:
            return selectors
        
        # Analyze common patterns in article links
        selector_candidates = []
        
        for link_data in article_links:
            link = link_data['element']
            
            # Generate various selector patterns
            candidates = self._generate_selector_candidates(link, soup)
            selector_candidates.extend(candidates)
        
        # Count frequency of each selector pattern
        selector_counts = Counter(selector_candidates)
        
        # Test each selector and rank by effectiveness
        for selector, count in selector_counts.most_common(20):  # Top 20 most common
            try:
                matches = soup.select(selector)
                article_matches = []
                
                # Check how many matches are actually article links
                for match in matches:
                    match_href = match.get('href')
                    if match_href:
                        # Convert to absolute URL for comparison
                        if match_href.startswith('/'):
                            match_href = urljoin(article_links[0]['href'], match_href)
                        
                        # Check if this match is in our article links
                        for article_link in article_links:
                            if article_link['href'] == match_href:
                                article_matches.append({
                                    'href': match_href,
                                    'text': match.get_text().strip()[:100]
                                })
                                break
                
                if article_matches:
                    effectiveness = len(article_matches) / len(matches) if matches else 0
                    selectors.append({
                        'selector': selector,
                        'total_matches': len(matches),
                        'article_matches': len(article_matches),
                        'effectiveness': effectiveness,
                        'examples': article_matches[:3],  # Show first 3 examples
                        'frequency': count
                    })
                    
            except Exception as e:
                self.logger.debug(f"Error testing selector '{selector}': {e}")
                continue
        
        # Sort by effectiveness and article matches
        selectors.sort(key=lambda x: (x['effectiveness'], x['article_matches']), reverse=True)
        
        return selectors[:10]  # Return top 10 selectors
    
    def _generate_selector_candidates(self, link, soup: BeautifulSoup) -> List[str]:
        """Generate various CSS selector candidates for a link element"""
        candidates = []
        
        # Get element hierarchy
        parents = []
        current = link
        while current and current.name and len(parents) < 4:
            parents.append(current)
            current = current.parent
        
        # Generate different selector patterns
        tag_name = link.name
        
        # 1. Simple tag selector
        candidates.append(tag_name)
        
        # 2. Tag with href attribute
        if link.get('href'):
            candidates.append(f"{tag_name}[href]")
        
        # 3. Class-based selectors
        if link.get('class'):
            classes = link.get('class')
            for cls in classes:
                candidates.append(f"{tag_name}.{cls}")
                candidates.append(f".{cls}")
        
        # 4. Parent-child combinations
        if len(parents) > 1:
            parent = parents[1]
            parent_tag = parent.name
            
            # Parent tag + child tag
            candidates.append(f"{parent_tag} {tag_name}")
            
            # Parent with class + child
            if parent.get('class'):
                for cls in parent.get('class'):
                    candidates.append(f"{parent_tag}.{cls} {tag_name}")
                    candidates.append(f".{cls} {tag_name}")
            
            # Specific parent-child relationships
            candidates.append(f"{parent_tag} > {tag_name}")
        
        # 5. Multi-level parent combinations
        if len(parents) > 2:
            grandparent = parents[2]
            parent = parents[1]
            
            gp_tag = grandparent.name
            p_tag = parent.name
            
            candidates.append(f"{gp_tag} {p_tag} {tag_name}")
            
            # With classes
            if grandparent.get('class'):
                for cls in grandparent.get('class'):
                    candidates.append(f"{gp_tag}.{cls} {tag_name}")
                    candidates.append(f".{cls} {tag_name}")
        
        # 6. Attribute-based selectors
        if link.get('title'):
            candidates.append(f"{tag_name}[title]")
        
        # 7. Content-based patterns (for common article structures)
        # Look for common article container patterns
        for parent in parents[1:3]:  # Check immediate and grandparent
            if parent.name in ['article', 'div', 'section', 'li']:
                if parent.get('class'):
                    for cls in parent.get('class'):
                        if any(keyword in cls.lower() for keyword in ['post', 'article', 'entry', 'news', 'story', 'content']):
                            candidates.append(f"{parent.name}.{cls} {tag_name}")
                            candidates.append(f".{cls} {tag_name}")
        
        return candidates
    
    def _find_latest_post(self, article_links: List, base_url: str) -> Optional[Dict]:
        """Find the most recent post from the article links"""
        if not article_links:
            return None
        
        # For now, return the first article link as it's often the most recent
        # In the future, this could be enhanced with date parsing
        latest = article_links[0]
        
        return {
            'url': latest['href'],
            'title': latest['text'],
            'has_date_pattern': latest['has_pattern']
        }
    
    def get_recommended_selector(self, analysis_result: Dict) -> Optional[str]:
        """Get the most recommended CSS selector from analysis results"""
        if not analysis_result.get('success') or not analysis_result.get('selectors'):
            return None
        
        # Return the top-ranked selector
        top_selector = analysis_result['selectors'][0]
        return top_selector['selector']
    
    def format_analysis_report(self, analysis_result: Dict) -> str:
        """Format the analysis results into a readable report"""
        if not analysis_result.get('success'):
            return f"[X] Analysis failed: {analysis_result.get('error', 'Unknown error')}"
        
        report = []
        report.append(f"Analysis Report for: {analysis_result['url']}")
        report.append(f"Total links found: {analysis_result['total_links']}")
        report.append(f"Article links identified: {analysis_result['article_links_count']}")
        report.append("")
        
        if analysis_result.get('latest_post'):
            latest = analysis_result['latest_post']
            report.append(f"Latest post: {latest['title'][:60]}...")
            report.append(f"URL: {latest['url']}")
            report.append("")
        
        selectors = analysis_result.get('selectors', [])
        if selectors:
            report.append("Recommended CSS Selectors:")
            report.append("")
            
            for i, selector_data in enumerate(selectors[:5], 1):
                effectiveness = selector_data['effectiveness'] * 100
                report.append(f"{i}. {selector_data['selector']}")
                report.append(f"   Effectiveness: {effectiveness:.1f}% ({selector_data['article_matches']}/{selector_data['total_matches']} matches)")
                
                if selector_data.get('examples'):
                    report.append("   Examples:")
                    for example in selector_data['examples'][:2]:
                        report.append(f"      • {example['text'][:50]}...")
                report.append("")
        else:
            report.append("[X] No suitable CSS selectors found")
        
        return "\n".join(report)