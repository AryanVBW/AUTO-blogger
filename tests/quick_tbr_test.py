#!/usr/bin/env python3
"""
Quick TBR Football test script
"""

import requests
from bs4 import BeautifulSoup

def test_tbr_scraping():
    """Test TBR Football scraping with enhanced error handling"""
    
    url = "https://tbrfootball.com/topic/english-premier-league/"
    selector = "article.article h2 a"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"🔗 Testing: {url}")
        print(f"🎯 Selector: {selector}")
        
        response = requests.get(url, headers=headers, timeout=15)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"✅ Page Title: {soup.title.string if soup.title else 'No title'}")
            
            # Test original selector
            articles = soup.select(selector)
            print(f"📰 Original selector found: {len(articles)} articles")
            
            if articles:
                print("✅ TBR Football scraping is working!")
                for i, article in enumerate(articles[:3]):
                    href = article.get('href', 'No href')
                    text = article.get_text().strip()
                    print(f"  {i+1}. {href}")
                    print(f"     Title: {text[:50]}...")
                return True
            else:
                print("⚠️ No articles found with original selector")
                # Try alternative selectors
                alternatives = [
                    "article h2 a",
                    "article a",
                    "h2 a",
                    "h3 a",
                    "a[href*='tbrfootball.com']",
                    ".entry-title a",
                    ".post-title a"
                ]
                
                for alt in alternatives:
                    alt_articles = soup.select(alt)
                    print(f"  📰 {alt}: {len(alt_articles)} articles")
                    if alt_articles:
                        for j, article in enumerate(alt_articles[:2]):
                            href = article.get('href', 'No href')
                            text = article.get_text().strip()[:30]
                            if 'tbrfootball.com' in href or href.startswith('/'):
                                print(f"    ✅ Valid: {href} - {text}")
                                
                return len(alt_articles) > 0
        else:
            print(f"❌ Failed to fetch page: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("TBR Football Scraping Test")
    print("=" * 40)
    success = test_tbr_scraping()
    print("=" * 40)
    if success:
        print("🎉 TBR Football scraping is working!")
    else:
        print("💥 TBR Football scraping needs fixing!")
