#!/usr/bin/env python3
"""
Test script for Getty Images functionality
"""

import sys
import os
import logging

# Add the current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automation_engine import BlogAutomationEngine

def test_getty_images():
    """Test Getty Images search and embed functionality"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create automation engine with minimal config
    config = {
        'source_url': 'https://example.com',
        'article_selector': 'a',
        'wp_base_url': '',
        'wp_username': '',
        'wp_password': '',
        'gemini_api_key': ''
    }
    
    engine = BlogAutomationEngine(config)
    
    print("🔍 Testing Getty Images Search...")
    
    # Test search functionality
    test_queries = [
        "Premier League football",
        "Manchester United",
        "Liverpool FC",
        "Champions League soccer"
    ]
    
    for query in test_queries:
        print(f"\n📸 Searching for: {query}")
        images = engine.search_getty_images(query, num_results=2)
        
        if images:
            print(f"✅ Found {len(images)} images")
            for i, img in enumerate(images, 1):
                print(f"  {i}. ID: {img['id']}, Title: {img['title'][:50]}...")
                print(f"     Embed URL: {img['embed_url']}")
        else:
            print("❌ No images found")
    
    print("\n🎨 Testing Embed Code Generation...")
    
    # Test embed code generation
    test_image_id = "1234567890"
    test_title = "Test Football Image"
    embed_code = engine.get_getty_embed_code(test_image_id, test_title)
    
    if embed_code:
        print("✅ Embed code generated successfully")
        print("Sample embed code:")
        print(embed_code[:200] + "..." if len(embed_code) > 200 else embed_code)
    else:
        print("❌ Failed to generate embed code")
    
    print("\n📝 Testing Content Integration...")
    
    # Test adding images to content
    test_content = """
    <h2>Premier League Update</h2>
    <p>This is a test article about football.</p>
    <p>Manchester United had a great match yesterday.</p>
    <p>The team performed excellently in all aspects.</p>
    """
    
    test_title = "Manchester United vs Liverpool Match Report"
    test_keywords = ["Manchester United", "Premier League", "football"]
    
    modified_content = engine.add_getty_image_to_content(test_content, test_title, test_keywords)
    
    if modified_content != test_content:
        print("✅ Content modified with Getty image")
        print("Modified content length:", len(modified_content))
        print("Contains embed code:", "embed.gettyimages.com" in modified_content)
    else:
        print("❌ Content not modified")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    test_getty_images()
