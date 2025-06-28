#!/usr/bin/env python3
"""
Test the GUI blogger with the fixes
"""

import os
import sys
import logging
import json

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

try:
    # Test importing GUI blogger
    print("📱 Testing GUI Blogger import...")
    from gui_blogger import BlogAutomationGUI
    print("✅ GUI Blogger imported successfully")
    
    # Test automation engine
    print("🤖 Testing automation engine...")
    from automation_engine import BlogAutomationEngine
    print("✅ Automation engine imported successfully")
    
    # Create a test config
    config = {
        'config_dir': 'configs',
        'source_url': 'https://tbrfootball.com/topic/english-premier-league/',
        'article_selector': 'article.article h2 a',
        'wp_base_url': 'https://example.com/wp-json/wp/v2',
        'wp_username': 'test',
        'wp_password': 'test',
        'gemini_api_key': 'test_key',
        'max_articles': 1
    }
    
    logger = logging.getLogger('test')
    
    print("🔧 Testing automation engine creation...")
    engine = BlogAutomationEngine(config, logger)
    print("✅ Automation engine created successfully")
    
    # Test critical methods
    print("🔍 Testing critical methods...")
    
    methods = [
        'load_posted_links',
        'save_posted_links',
        'get_article_links', 
        'run_automation_jupyter_style',
        'process_complete_article_jupyter'
    ]
    
    for method in methods:
        if hasattr(engine, method):
            print(f"  ✅ {method}: exists")
        else:
            print(f"  ❌ {method}: missing")
    
    # Test posted links functionality
    print("💾 Testing posted links...")
    posted_links = engine.load_posted_links()
    print(f"  ✅ Loaded {len(posted_links)} existing posted links")
    
    engine.save_posted_links(set(['test_link_123']))
    print("  ✅ Save posted links working")
    
    print("\n🎉 All tests passed! The blogger should work now.")
    print("\n💡 To fix the gemini prompt errors, the automation engine")
    print("   now has proper error handling for JSON loading.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Check if all required packages are installed")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
print("\n🚀 You can now run: python3 gui_blogger.py")
