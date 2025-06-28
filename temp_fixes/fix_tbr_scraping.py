#!/usr/bin/env python3
"""
TBR Football Configuration Test and Fix Script
This script tests different selectors and provides fixes for TBR Football article scraping
"""

import requests
from bs4 import BeautifulSoup
import json

def test_tbr_selectors():
    """Test different selectors on TBR Football website"""
    
    url = "https://tbrfootball.com/topic/english-premier-league/"
    
    # Different selectors to try
    selectors_to_test = [
        "article.article h2 a",  # Original
        "article h2 a",
        "article h3 a", 
        "article a",
        ".article h2 a",
        ".article h3 a",
        ".article a",
        "h2 a",
        "h3 a",
        ".post-title a",
        ".entry-title a",
        "a[href*='tbrfootball.com']",
        ".post a",
        ".entry a",
        ".content a"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("TBR Football Selector Test")
    print("=" * 50)
    print(f"Testing URL: {url}")
    print()
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"✅ Website accessible (Status: {response.status_code})")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"✅ Page loaded successfully")
            print(f"Page title: {soup.title.string if soup.title else 'No title'}")
            print()
            
            best_selector = None
            max_articles = 0
            
            for selector in selectors_to_test:
                try:
                    elements = soup.select(selector)
                    article_count = 0
                    
                    # Count valid TBR Football articles
                    for element in elements:
                        href = element.get('href', '')
                        if href and ('tbrfootball.com' in href or href.startswith('/')):
                            if not any(pattern in href.lower() for pattern in ['tag/', 'category/', 'author/', '#']):
                                article_count += 1
                    
                    print(f"Selector: '{selector}'")
                    print(f"  Total elements: {len(elements)}")
                    print(f"  Valid articles: {article_count}")
                    
                    if article_count > 0:
                        print(f"  ✅ WORKING SELECTOR")
                        
                        # Show sample articles
                        sample_count = 0
                        for element in elements:
                            if sample_count >= 3:
                                break
                            href = element.get('href', '')
                            text = element.get_text().strip()
                            if href and ('tbrfootball.com' in href or href.startswith('/')):
                                if not any(pattern in href.lower() for pattern in ['tag/', 'category/', 'author/', '#']):
                                    print(f"    Sample: {href} - {text[:50]}...")
                                    sample_count += 1
                        
                        if article_count > max_articles:
                            max_articles = article_count
                            best_selector = selector
                    else:
                        print(f"  ❌ No valid articles found")
                    
                    print()
                    
                except Exception as e:
                    print(f"Selector: '{selector}' - Error: {e}")
                    print()
            
            if best_selector:
                print("🎯 RECOMMENDED SOLUTION:")
                print(f"Best selector: {best_selector}")
                print(f"Articles found: {max_articles}")
                print()
                print("UPDATE YOUR CONFIGURATION:")
                print(f'Set "article_selector" to: "{best_selector}"')
                
                # Create updated config
                try:
                    with open('configs/default.json', 'r') as f:
                        config = json.load(f)
                    
                    config['article_selector'] = best_selector
                    
                    with open('configs/tbr_fixed.json', 'w') as f:
                        json.dump(config, f, indent=2)
                    
                    print(f"✅ Created fixed config: configs/tbr_fixed.json")
                    
                except Exception as e:
                    print(f"⚠️ Could not create fixed config: {e}")
                    
            else:
                print("❌ NO WORKING SELECTORS FOUND")
                print("The website structure may have changed or there might be other issues.")
                
        else:
            print(f"❌ Failed to access website (Status: {response.status_code})")
            
    except Exception as e:
        print(f"❌ Error testing selectors: {e}")

def analyze_page_structure():
    """Analyze the page structure to understand the HTML layout"""
    
    url = "https://tbrfootball.com/topic/english-premier-league/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("\nPage Structure Analysis")
    print("=" * 30)
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links
            all_links = soup.find_all('a', href=True)
            tbr_links = []
            
            for link in all_links:
                href = link.get('href')
                if href and ('tbrfootball.com' in href or href.startswith('/')):
                    # Skip navigation and category links
                    if not any(pattern in href.lower() for pattern in ['tag/', 'category/', 'author/', 'topic/', '#']):
                        tbr_links.append((href, link.get_text().strip()))
            
            print(f"Total links: {len(all_links)}")
            print(f"TBR article links: {len(tbr_links)}")
            
            if tbr_links:
                print("\nSample article links found:")
                for i, (href, text) in enumerate(tbr_links[:5]):
                    print(f"  {i+1}. {href}")
                    print(f"     Text: {text[:60]}...")
                    
                    # Find the parent elements to understand structure
                    link_element = soup.find('a', href=href)
                    if link_element:
                        parent = link_element.parent
                        if parent:
                            print(f"     Parent: <{parent.name}> with classes: {parent.get('class', [])}")
                    print()
            else:
                print("No TBR article links found in the expected format")
                
    except Exception as e:
        print(f"Error analyzing page structure: {e}")

if __name__ == "__main__":
    test_tbr_selectors()
    analyze_page_structure()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("1. Run this script to find the best selector")
    print("2. Update your configuration with the recommended selector")
    print("3. Test the automation again")
    print("4. If still having issues, the website may have changed structure")
