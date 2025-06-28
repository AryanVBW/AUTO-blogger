#!/usr/bin/env python3
"""
Comprehensive TBR Football Fix and Alternative Sources
This script provides multiple solutions for the article scraping issue
"""

import requests
from bs4 import BeautifulSoup
import json
import time

def test_source_availability():
    """Test multiple news sources to find working alternatives"""
    
    sources = [
        {
            "name": "TBR Football (Original)",
            "url": "https://tbrfootball.com/topic/english-premier-league/",
            "selectors": ["article.article h2 a", "article h2 a", "article h3 a", "article a"]
        },
        {
            "name": "Sky Sports Premier League",
            "url": "https://www.skysports.com/premier-league-news",
            "selectors": [".news-list__item .news-list__headline-link", ".news-list__headline-link", ".sdc-article-widget__headline-link"]
        },
        {
            "name": "BBC Sport Premier League",
            "url": "https://www.bbc.com/sport/football/premier-league",
            "selectors": [".gs-c-promo-heading__title", ".gs-c-promo h3 a", ".gel-double-pica-bold"]
        },
        {
            "name": "Football365",
            "url": "https://www.football365.com/premier-league",
            "selectors": [".teaser-title a", ".entry-title a", "h2 a", "h3 a"]
        },
        {
            "name": "Goal.com Premier League",
            "url": "https://www.goal.com/en/premier-league/news",
            "selectors": [".teaser-title a", ".article-title a", "h2 a", "h3 a"]
        }
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("Testing Multiple News Sources")
    print("=" * 50)
    
    working_sources = []
    
    for source in sources:
        print(f"\nTesting: {source['name']}")
        print(f"URL: {source['url']}")
        
        try:
            response = requests.get(source['url'], headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Website accessible (Status: {response.status_code})")
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                best_selector = None
                max_articles = 0
                
                for selector in source['selectors']:
                    try:
                        elements = soup.select(selector)
                        article_count = len([el for el in elements if el.get('href')])
                        
                        if article_count > max_articles:
                            max_articles = article_count
                            best_selector = selector
                        
                        print(f"  Selector '{selector}': {article_count} articles")
                        
                    except Exception as e:
                        print(f"  Selector '{selector}': Error - {e}")
                
                if best_selector and max_articles > 0:
                    print(f"✅ WORKING SOURCE - Best selector: '{best_selector}' ({max_articles} articles)")
                    working_sources.append({
                        "name": source['name'],
                        "url": source['url'],
                        "selector": best_selector,
                        "article_count": max_articles
                    })
                else:
                    print(f"❌ No working selectors found")
                    
            else:
                print(f"❌ Website not accessible (Status: {response.status_code})")
                
        except Exception as e:
            print(f"❌ Error testing {source['name']}: {e}")
        
        print("-" * 30)
    
    return working_sources

def create_alternative_configs(working_sources):
    """Create configuration files for working sources"""
    
    if not working_sources:
        print("❌ No working sources found to create configs")
        return
    
    print(f"\nCreating Alternative Configurations")
    print("=" * 40)
    
    # Load the base configuration
    try:
        with open('configs/default.json', 'r') as f:
            base_config = json.load(f)
    except Exception as e:
        print(f"❌ Could not load base config: {e}")
        return
    
    for i, source in enumerate(working_sources):
        try:
            # Create new config
            new_config = base_config.copy()
            new_config['source_url'] = source['url']
            new_config['article_selector'] = source['selector']
            
            # Save config file
            filename = f"configs/alternative_{i+1}_{source['name'].lower().replace(' ', '_')}.json"
            with open(filename, 'w') as f:
                json.dump(new_config, f, indent=2)
            
            print(f"✅ Created: {filename}")
            print(f"   Source: {source['name']}")
            print(f"   Articles: {source['article_count']}")
            print()
            
        except Exception as e:
            print(f"❌ Error creating config for {source['name']}: {e}")

def fix_tbr_football_specific():
    """Try to fix TBR Football specifically with enhanced methods"""
    
    print("\nTrying Enhanced TBR Football Fix")
    print("=" * 40)
    
    url = "https://tbrfootball.com/topic/english-premier-league/"
    
    # Try different user agents and headers
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]
    
    for i, user_agent in enumerate(user_agents):
        print(f"\nTry {i+1}: Using User-Agent: {user_agent[:50]}...")
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                print(f"✅ Success with User-Agent {i+1}")
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try comprehensive selectors
                selectors = [
                    "article.article h2 a",
                    "article.article h3 a",
                    "article h2 a",
                    "article h3 a",
                    ".article h2 a",
                    ".article h3 a",
                    "h2 a",
                    "h3 a",
                    "a[href*='tbrfootball.com']",
                    ".post-title a",
                    ".entry-title a"
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    valid_articles = []
                    
                    for element in elements:
                        href = element.get('href', '')
                        if href and ('tbrfootball.com' in href or href.startswith('/')):
                            if not any(bad in href.lower() for bad in ['tag/', 'category/', 'author/', 'topic/']):
                                valid_articles.append((href, element.get_text().strip()))
                    
                    if valid_articles:
                        print(f"✅ Found {len(valid_articles)} articles with '{selector}'")
                        
                        # Show samples
                        for j, (href, text) in enumerate(valid_articles[:3]):
                            print(f"   {j+1}. {href} - {text[:50]}...")
                        
                        # Create fixed config
                        try:
                            with open('configs/default.json', 'r') as f:
                                config = json.load(f)
                            
                            config['article_selector'] = selector
                            
                            with open('configs/tbr_fixed.json', 'w') as f:
                                json.dump(config, f, indent=2)
                            
                            print(f"✅ Created fixed TBR config: configs/tbr_fixed.json")
                            return True
                            
                        except Exception as e:
                            print(f"⚠️ Could not save config: {e}")
                            
                print(f"❌ No articles found with any selector using User-Agent {i+1}")
                
            else:
                print(f"❌ Failed with status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error with User-Agent {i+1}: {e}")
        
        time.sleep(1)  # Brief pause between attempts
    
    return False

def main():
    """Main function to run all fixes"""
    
    print("TBR Football Comprehensive Fix Script")
    print("=" * 50)
    print("This script will:")
    print("1. Test TBR Football with enhanced methods")
    print("2. Test alternative news sources")
    print("3. Create working configuration files")
    print("=" * 50)
    
    # Try to fix TBR Football specifically
    tbr_fixed = fix_tbr_football_specific()
    
    # Test alternative sources
    working_sources = test_source_availability()
    
    if working_sources:
        create_alternative_configs(working_sources)
        
        print(f"\n🎯 SOLUTION SUMMARY:")
        print(f"Found {len(working_sources)} working sources:")
        
        for source in working_sources:
            print(f"✅ {source['name']} - {source['article_count']} articles")
        
        print(f"\nTo use an alternative source:")
        print(f"1. Go to Configuration tab in the GUI")
        print(f"2. Load one of the alternative config files")
        print(f"3. Test the configuration")
        print(f"4. Run automation")
        
    elif tbr_fixed:
        print(f"\n🎯 TBR Football has been fixed!")
        print(f"Use the configs/tbr_fixed.json configuration")
        
    else:
        print(f"\n❌ No working sources found")
        print(f"Possible issues:")
        print(f"• Network connectivity problems")
        print(f"• Website blocking automated requests")
        print(f"• Websites have changed their structure")
        print(f"• Temporary server issues")

if __name__ == "__main__":
    main()
