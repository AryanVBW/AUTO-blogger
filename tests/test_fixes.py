#!/usr/bin/env python3
"""
Test the fixes for the automation engine
"""

from automation_engine import BlogAutomationEngine
import logging

# Set up logger
logger = logging.getLogger('test')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
logger.addHandler(handler)

# Test config
config = {
    'config_dir': 'configs',
    'source_url': 'https://tbrfootball.com',
    'article_selector': 'article h2 a'
}

try:
    # Create engine
    engine = BlogAutomationEngine(config, logger)
    print("✅ Engine initialized successfully")

    # Test the posted links loading
    posted_links = engine.load_posted_links()
    print(f"✅ Loaded {len(posted_links)} posted links")

    # Test detect_categories method
    test_text = 'This is a test about Premier League transfer news for Arsenal'
    categories = engine.detect_categories(test_text)
    print(f"✅ Categories: {categories}")

    # Test detect_categories_jupyter method
    categories_jupyter = engine.detect_categories_jupyter(test_text, 'Test Title')
    print(f"✅ Categories (jupyter): {categories_jupyter}")

    print("✅ All basic functionality tests passed")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
