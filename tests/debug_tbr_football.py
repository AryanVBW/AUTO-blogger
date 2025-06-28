#!/usr/bin/env python3
"""
Debug script to test TBR Football article scraping
"""

import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_requests_approach():
    """Test using requests library"""
    print("=== Testing with Requests Library ===")
    
    url = "https://tbrfootball.com/topic/english-premier-league/"
    selector = "article.article h2 a"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"Page title: {soup.title.string if soup.title else 'No title'}")
            
            # Test the original selector
            articles = soup.select(selector)
            print(f"Articles found with '{selector}': {len(articles)}")
            
            if articles:
                for i, article in enumerate(articles[:3]):
                    print(f"  Article {i+1}: {article.get('href', 'No href')} - {article.get_text().strip()}")
            else:
                # Try alternative selectors
                print("\nTrying alternative selectors...")
                
                alternatives = [
                    "article h2 a",
                    "article a",
                    ".article h2 a",
                    ".article a",
                    "h2 a",
                    "h3 a",
                    "a[href*='tbrfootball.com']",
                    ".entry-title a",
                    ".post-title a"
                ]
                
                for alt_selector in alternatives:
                    alt_articles = soup.select(alt_selector)
                    print(f"  '{alt_selector}': {len(alt_articles)} articles")
                    if alt_articles and len(alt_articles) > 0:
                        for j, article in enumerate(alt_articles[:2]):
                            href = article.get('href', 'No href')
                            text = article.get_text().strip()
                            print(f"    Sample {j+1}: {href} - {text[:50]}...")
        else:
            print(f"Failed to fetch page. Status: {response.status_code}")
            
    except Exception as e:
        print(f"Error with requests: {e}")

def test_selenium_approach():
    """Test using Selenium with Chrome"""
    print("\n=== Testing with Selenium ===")
    
    url = "https://tbrfootball.com/topic/english-premier-league/"
    selector = "article.article h2 a"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print(f"Loading URL: {url}")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(3)
        
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Test the original selector
        try:
            articles = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"Articles found with '{selector}': {len(articles)}")
            
            if articles:
                for i, article in enumerate(articles[:3]):
                    href = article.get_attribute('href')
                    text = article.text.strip()
                    print(f"  Article {i+1}: {href} - {text}")
            else:
                # Try alternative selectors
                print("\nTrying alternative selectors...")
                
                alternatives = [
                    "article h2 a",
                    "article a",
                    ".article h2 a", 
                    ".article a",
                    "h2 a",
                    "h3 a",
                    "a[href*='tbrfootball.com']",
                    ".entry-title a",
                    ".post-title a",
                    ".post a"
                ]
                
                for alt_selector in alternatives:
                    try:
                        alt_articles = driver.find_elements(By.CSS_SELECTOR, alt_selector)
                        print(f"  '{alt_selector}': {len(alt_articles)} articles")
                        if alt_articles and len(alt_articles) > 0:
                            for j, article in enumerate(alt_articles[:2]):
                                href = article.get_attribute('href')
                                text = article.text.strip()
                                print(f"    Sample {j+1}: {href} - {text[:50]}...")
                                if href and 'tbrfootball.com' in href:
                                    print(f"    ✓ Valid TBR Football link found!")
                    except Exception as e:
                        print(f"    Error with '{alt_selector}': {e}")
                        
        except Exception as e:
            print(f"Error finding elements: {e}")
            
    except Exception as e:
        print(f"Error with Selenium: {e}")
    finally:
        if driver:
            driver.quit()

def test_page_structure():
    """Analyze the page structure"""
    print("\n=== Analyzing Page Structure ===")
    
    url = "https://tbrfootball.com/topic/english-premier-league/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all potential article containers
            print("Looking for potential article containers...")
            
            # Check for common article patterns
            patterns = ['article', '.article', '.post', '.entry', '.content-item', '.story']
            
            for pattern in patterns:
                elements = soup.select(pattern)
                if elements:
                    print(f"Found {len(elements)} elements matching '{pattern}'")
                    
                    # Look for links in the first few elements
                    for i, element in enumerate(elements[:2]):
                        links = element.find_all('a', href=True)
                        print(f"  Element {i+1} has {len(links)} links")
                        for j, link in enumerate(links[:3]):
                            href = link.get('href')
                            text = link.get_text().strip()
                            if href and ('tbrfootball.com' in href or href.startswith('/')):
                                print(f"    Link {j+1}: {href} - {text[:50]}...")
                                
    except Exception as e:
        print(f"Error analyzing page structure: {e}")

if __name__ == "__main__":
    print("TBR Football Debug Script")
    print("=" * 50)
    
    test_requests_approach()
    test_selenium_approach()
    test_page_structure()
    
    print("\n" + "=" * 50)
    print("Debug complete!")
