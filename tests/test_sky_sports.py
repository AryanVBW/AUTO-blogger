#!/usr/bin/env python3
"""
Quick test to verify the Sky Sports configuration works
"""

import requests
from bs4 import BeautifulSoup

def test_sky_sports():
    """Test Sky Sports configuration"""
    
    url = "https://www.skysports.com/premier-league-news"
    selector = ".news-list__item .news-list__headline-link"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("Testing Sky Sports Configuration")
    print("=" * 40)
    print(f"URL: {url}")
    print(f"Selector: {selector}")
    print()
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.select(selector)
            
            print(f"Articles found: {len(articles)}")
            
            if articles:
                print("\nSample articles:")
                for i, article in enumerate(articles[:5]):
                    href = article.get('href', 'No href')
                    text = article.get_text().strip()
                    print(f"{i+1}. {href}")
                    print(f"   Title: {text}")
                    print()
                
                print("✅ Sky Sports configuration is WORKING!")
                return True
            else:
                print("❌ No articles found with selector")
                return False
        else:
            print(f"❌ Failed to access website: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_sky_sports()
    
    if success:
        print("\n🎯 SOLUTION: Use Sky Sports configuration")
        print("The default configuration has been updated.")
        print("Your automation should now work correctly!")
    else:
        print("\n❌ Sky Sports test failed")
        print("You may need to try alternative sources or check connectivity.")
