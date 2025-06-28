#!/usr/bin/env python3
"""
Debug script to test article link extraction

Copyright © 2025 AryanVBW
GitHub: https://github.com/AryanVBW
"""

import json
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def test_article_extraction():
    """Test article link extraction with detailed debugging"""
    print("🔍 Testing Article Link Extraction")
    print("=" * 50)
    
    # Load configuration
    try:
        with open('blog_config.json', 'r') as f:
            config = json.load(f)
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return
    
    source_url = config.get('source_url', '')
    selector = config.get('article_selector', '')
    
    print(f"🔗 Source URL: {source_url}")
    print(f"🎯 Article Selector: {selector}")
    print()
    
    if not source_url:
        print("❌ No source URL configured!")
        return
        
    if not selector:
        print("❌ No article selector configured!")
        return
    
    try:
        # Test website accessibility
        print("📡 Testing website accessibility...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        
        response = requests.get(source_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"✅ Website accessible (Status: {response.status_code})")
        print(f"📄 Content length: {len(response.content)} bytes")
        print()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Test the configured selector
        print(f"🎯 Testing selector: {selector}")
        tags = soup.select(selector)
        print(f"Found {len(tags)} elements")
        
        if tags:
            print("✅ Articles found with configured selector:")
            for i, tag in enumerate(tags[:5]):  # Show first 5
                href = tag.get("href", "No href")
                text = tag.get_text(strip=True)[:60]
                print(f"  {i+1}. {text}... -> {href}")
        else:
            print("❌ No articles found with configured selector")
            print("🔄 Trying alternative selectors...")
            
            # Try alternative selectors
            alternative_selectors = [
                "article h2 a",
                "h2 a", 
                "h3 a",
                ".post-title a",
                ".entry-title a",
                "a[href*='post']",
                "a[href*='article']",
                ".title a",
                ".headline a"
            ]
            
            for alt_selector in alternative_selectors:
                alt_tags = soup.select(alt_selector)
                if alt_tags:
                    print(f"✅ Found {len(alt_tags)} articles with: {alt_selector}")
                    for i, tag in enumerate(alt_tags[:3]):  # Show first 3
                        href = tag.get("href", "No href")
                        text = tag.get_text(strip=True)[:60]
                        full_url = urljoin(source_url, href) if href else "No URL"
                        print(f"  {i+1}. {text}... -> {full_url}")
                    print(f"💡 Consider updating article_selector to: {alt_selector}")
                    break
            else:
                print("❌ No articles found with any selector")
                print("\n🔍 Page structure analysis:")
                
                # Show some common elements for debugging
                articles = soup.find_all(['article', 'div'], class_=True, limit=10)
                for i, article in enumerate(articles):
                    classes = article.get('class', [])
                    if classes:
                        print(f"  Element {i+1}: <{article.name} class='{' '.join(classes)}'>")
                        # Show any links inside
                        links = article.find_all('a', limit=2)
                        for link in links:
                            link_text = link.get_text(strip=True)[:40]
                            if link_text:
                                print(f"    Link: {link_text}...")
        
        print()
        print("=" * 50)
        print("🎯 Debugging complete!")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        print("💡 Check your internet connection and try again")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_article_extraction()
