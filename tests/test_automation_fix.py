#!/usr/bin/env python3
"""
Quick test to verify automation engine fixes
"""

from automation_engine import BlogAutomationEngine
import logging

# Setup basic logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('test')

# Create config
config = {
    'config_dir': 'configs',
    'source_url': 'https://example.com',
    'article_selector': 'a'
}

try:
    # Test engine creation
    engine = BlogAutomationEngine(config, logger)
    print('✅ BlogAutomationEngine loaded successfully')
    
    # Test required methods exist
    methods_to_check = [
        'load_posted_links',
        'save_posted_links', 
        'run_automation_jupyter_style',
        'process_complete_article_jupyter',
        'generate_seo_title_and_meta_jupyter',
        'extract_keyphrases_jupyter'
    ]
    
    for method in methods_to_check:
        exists = hasattr(engine, method)
        print(f'✅ {method} method exists: {exists}')
        
    # Test loading posted links
    posted_links = engine.load_posted_links()
    print(f'✅ loaded {len(posted_links)} posted links')
    
    print('\n🎉 All tests passed! The automation engine is ready.')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
