#!/usr/bin/env python3
"""
Demo Script for WordPress Blog Automation Suite
This demonstrates the core functionality without the GUI

Copyright © 2025 AryanVBW
GitHub: https://github.com/AryanVBW
"""

import json
import logging
from automation_engine import BlogAutomationEngine

def setup_demo_config():
    """Setup demo configuration"""
    config = {
        'source_url': 'https://tbrfootball.com/topic/english-premier-league/',
        'article_selector': 'article.article h2 a',
        'wp_base_url': 'https://premierleaguenewsnow.com/wp-json/wp/v2',
        'wp_username': 'YOUR_USERNAME',
        'wp_password': 'YOUR_PASSWORD',
        'gemini_api_key': 'YOUR_GEMINI_API_KEY',
        'timeout': 10,
        'headless_mode': True
    }
    return config

def demo_article_extraction():
    """Demo article extraction functionality"""
    print("🔗 Testing Article Link Extraction...")
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('Demo')
    
    # Setup config
    config = setup_demo_config()
    
    # Initialize engine
    engine = BlogAutomationEngine(config, logger)
    
    # Test article link extraction
    links = engine.get_article_links(limit=5)
    print(f"✅ Found {len(links)} article links:")
    for i, link in enumerate(links, 1):
        print(f"  {i}. {link}")
    
    if links:
        print(f"\n📄 Testing content extraction from first article...")
        
        # Test content extraction
        with engine.get_selenium_driver_context() as driver:
            if driver:
                title, content = engine.extract_article_with_selenium(driver, links[0])
                if title and content:
                    print(f"✅ Title: {title}")
                    print(f"✅ Content length: {len(content)} characters")
                    print(f"✅ Content preview: {content[:200]}...")
                else:
                    print("❌ Failed to extract content")
            else:
                print("❌ Failed to initialize WebDriver")
    
    return links

def demo_text_processing():
    """Demo text processing functionality"""
    print("\n🧠 Testing Text Processing...")
    
    # Setup
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('Demo')
    config = setup_demo_config()
    engine = BlogAutomationEngine(config, logger)
    
    # Test data
    sample_title = "premier league star linked with championship club leeds united eyes forward"
    sample_content = """
    <p>sources indicate that a prominent figure from the premier league, known for his prolific goal-scoring, might be making a surprising move to a championship side. he played for udinese in serie a and is compared to vardy.</p>
    <p>this player, often compared to jamie vardy for his pace and clinical finishing, has been a key asset for his current club. however, recent developments suggest a transfer could be on the horizon.</p>
    <p>leeds united, fresh off a strong season, are reportedly keen on securing his services. this acquisition would significantly bolster their attacking options. the fa cup is important.</p>
    """
    
    # Test post-processing
    print("🔄 Testing text post-processing...")
    processed_title = engine.post_process_text(sample_title)
    processed_content = engine.post_process_text(sample_content)
    
    print(f"Original title: {sample_title}")
    print(f"Processed title: {processed_title}")
    
    # Test sentence case
    print("\n📝 Testing sentence case conversion...")
    sentence_cased = engine.sentence_case(processed_title)
    print(f"Sentence case: {sentence_cased}")
    
    # Test link injection
    print("\n🔗 Testing link injection...")
    internal_linked = engine.inject_internal_links(processed_content)
    final_content = engine.inject_external_links(internal_linked)
    
    print("✅ Links injected successfully")
    print("Content with links (preview):")
    print(final_content[:300] + "...")
    
    # Test SEO generation
    print("\n📈 Testing SEO metadata generation...")
    seo_title, meta_desc = engine.generate_seo_title_and_meta(processed_title, final_content)
    print(f"SEO Title ({len(seo_title)} chars): {seo_title}")
    print(f"Meta Description ({len(meta_desc)} chars): {meta_desc}")
    
    # Test categorization
    print("\n📂 Testing category detection...")
    categories = engine.detect_categories(processed_title + " " + final_content)
    print(f"Detected categories: {categories}")
    
    # Test tag generation
    print("\n🏷️ Testing tag generation...")
    tags = engine.generate_tags_fallback(final_content)  # Using fallback for demo
    print(f"Generated tags: {tags}")
    
    # Test keyphrase extraction
    print("\n🔑 Testing keyphrase extraction...")
    focus_keyphrase, additional_keyphrases = engine.extract_keyphrases_fallback(processed_title, final_content)
    print(f"Focus keyphrase: {focus_keyphrase}")
    print(f"Additional keyphrases: {additional_keyphrases}")
    
    # Test slug generation
    print("\n🔗 Testing slug generation...")
    slug = engine.generate_slug(seo_title)
    print(f"Generated slug: {slug}")

def main():
    """Main demo function"""
    print("=" * 60)
    print("🚀 WordPress Blog Automation Suite - Demo")
    print("=" * 60)
    
    try:
        # Test requirements
        print("📋 Checking requirements...")
        import requests
        import bs4
        print("✅ Basic requirements available")
        
        try:
            import selenium
            print("✅ Selenium available")
            selenium_ok = True
        except ImportError:
            print("❌ Selenium not available - install with: pip install selenium")
            selenium_ok = False
        
        # Demo text processing (always works)
        demo_text_processing()
        
        # Demo article extraction (requires selenium)
        if selenium_ok:
            print("\n" + "=" * 60)
            demo_article_extraction()
        else:
            print("\n⚠️ Skipping web scraping demo - Selenium not available")
        
        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("\nTo run the full application:")
        print("1. Install requirements: pip install -r requirements.txt")
        print("2. Run the GUI: python launch_blogger.py")
        print("3. Configure your WordPress and Gemini API credentials")
        print("4. Start automation!")
        
    except ImportError as e:
        print(f"❌ Missing requirement: {e}")
        print("Please install requirements: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    main()
