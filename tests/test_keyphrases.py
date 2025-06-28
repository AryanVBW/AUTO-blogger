#!/usr/bin/env python3
"""
Test script for the new keyphrase extraction functionality

Copyright © 2025 AryanVBW
GitHub: https://github.com/AryanVBW
"""

import json
import logging
from automation_engine import BlogAutomationEngine

def test_keyphrase_extraction():
    """Test the new keyphrase extraction functionality"""
    print("🔑 Testing Focus Keyphrase and Additional Keyphrases Extraction")
    print("=" * 60)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('Keyphrase Test')
    
    # Load configuration
    with open('blog_config.json', 'r') as f:
        config = json.load(f)
    
    # Initialize engine
    engine = BlogAutomationEngine(config, logger)
    
    # Test data
    test_title = "Manchester United eye Premier League defender in January transfer window"
    test_content = """
    <p>Manchester United are reportedly interested in signing a top Premier League defender 
    during the January transfer window. The Red Devils are looking to strengthen their 
    defensive options as they push for a top-four finish this season.</p>
    
    <p>Sources close to the club suggest that Erik ten Hag is keen on adding defensive 
    reinforcements, with several key players linked with moves to Old Trafford. The 
    defender in question has been impressive this season and would bring valuable 
    Premier League experience to United's backline.</p>
    
    <p>The transfer news comes as Manchester United continue their pursuit of Champions League 
    qualification. The potential signing could be crucial for their defensive stability 
    and overall team performance in the second half of the season.</p>
    """
    
    print(f"Test Title: {test_title}")
    print(f"Test Content Length: {len(test_content)} characters")
    print()
    
    # Test Gemini-based extraction
    print("🤖 Testing Gemini-based keyphrase extraction...")
    try:
        focus_keyphrase, additional_keyphrases = engine.extract_keyphrases_with_gemini(test_title, test_content)
        print(f"✅ Focus Keyphrase: '{focus_keyphrase}'")
        print(f"✅ Additional Keyphrases: {additional_keyphrases}")
    except Exception as e:
        print(f"❌ Gemini extraction failed: {e}")
        print("Falling back to basic extraction...")
    
    print()
    
    # Test fallback extraction
    print("🔧 Testing fallback keyphrase extraction...")
    focus_keyphrase_fallback, additional_keyphrases_fallback = engine.extract_keyphrases_fallback(test_title, test_content)
    print(f"✅ Fallback Focus Keyphrase: '{focus_keyphrase_fallback}'")
    print(f"✅ Fallback Additional Keyphrases: {additional_keyphrases_fallback}")
    
    print()
    print("=" * 60)
    print("🎯 Keyphrase Extraction Test Complete!")
    print()
    print("These keyphrases will now be automatically:")
    print("• Added to WordPress posts as focus keyphrase")
    print("• Included in SEO metadata for better ranking")
    print("• Compatible with Yoast SEO and AIOSEO plugins")
    print("• Used to improve search engine optimization")

if __name__ == "__main__":
    test_keyphrase_extraction()
