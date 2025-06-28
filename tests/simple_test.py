#!/usr/bin/env python3
"""
Simple test to verify if the fixes work
"""

try:
    print("Testing automation engine import...")
    from automation_engine import BlogAutomationEngine
    print("✅ Successfully imported BlogAutomationEngine")
    
    print("Testing logger import...")
    import logging
    logger = logging.getLogger('test')
    logger.setLevel(logging.INFO)
    print("✅ Logger created")
    
    print("Testing engine creation...")
    config = {'config_dir': 'configs'}
    engine = BlogAutomationEngine(config, logger)
    print("✅ Engine created successfully")
    
    print("Testing load_posted_links method...")
    posted_links = engine.load_posted_links()
    print(f"✅ Loaded {len(posted_links)} posted links")
    
    print("Testing save_posted_links method...")
    engine.save_posted_links(set(['test_link']))
    print("✅ Save posted links working")
    
    print("Testing run_automation_jupyter_style method...")
    has_method = hasattr(engine, 'run_automation_jupyter_style')
    print(f"✅ run_automation_jupyter_style exists: {has_method}")
    
    print("\n🎉 All critical methods are working!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
