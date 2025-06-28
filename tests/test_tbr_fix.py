#!/usr/bin/env python3
"""
Test script to verify TBR Football scraping fix
"""

import json
from automation_engine import AutomationEngine

def test_tbr_scraping():
    """Test the improved TBR Football scraping"""
    
    print("Testing TBR Football Article Scraping Fix")
    print("=" * 50)
    
    # Load the default config
    try:
        with open('configs/default.json', 'r') as f:
            config = json.load(f)
        
        print(f"✅ Loaded config")
        print(f"Source URL: {config.get('source_url')}")
        print(f"Article Selector: {config.get('article_selector')}")
        print()
        
        # Initialize automation engine
        engine = AutomationEngine(config)
        
        # Test article link extraction
        print("🔍 Testing article link extraction...")
        links = engine.get_article_links(limit=5)
        
        print(f"📊 Results:")
        print(f"Found {len(links)} article links")
        
        if links:
            print("\n📝 Article Links Found:")
            for i, link in enumerate(links, 1):
                print(f"  {i}. {link}")
                
                # Test URL validation
                is_valid = engine.is_valid_article_url(link)
                print(f"     Valid: {'✅' if is_valid else '❌'}")
        else:
            print("❌ No article links found")
            print("\n🔧 Debugging suggestions:")
            print("1. Check if the TBR Football website is accessible")
            print("2. Verify the article selector is correct")
            print("3. Check the logs for detailed error information")
            
        print("\n" + "=" * 50)
        print("Test completed!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tbr_scraping()
