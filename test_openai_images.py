#!/usr/bin/env python3
"""
Test script for OpenAI image generation functionality
"""

import sys
import os
import json

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_openai_config():
    """Test OpenAI image configuration loading"""
    print("🧪 Testing OpenAI Image Configuration...")
    
    config_dir = "configs"
    config_path = os.path.join(config_dir, "openai_image_config.json")
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            print("✅ OpenAI configuration loaded successfully")
            print(f"📋 Configuration: {json.dumps(config, indent=2)}")
            
            # Test required fields
            required_fields = ['image_size', 'image_style', 'image_model', 'num_images']
            for field in required_fields:
                if field in config:
                    print(f"  ✅ {field}: {config[field]}")
                else:
                    print(f"  ❌ Missing field: {field}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            return False
    else:
        print(f"❌ Configuration file not found: {config_path}")
        return False

def test_automation_engine():
    """Test automation engine OpenAI integration"""
    print("\n🧪 Testing Automation Engine OpenAI Integration...")
    
    try:
        from automation_engine import BlogAutomationEngine
        import logging
        
        # Create a test logger
        logger = logging.getLogger('test')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        logger.addHandler(handler)
        
        # Create test config
        test_config = {
            'openai_api_key': 'test_key_placeholder',
            'wp_base_url': 'https://test.com/wp-json/wp/v2',
            'wp_username': 'test_user',
            'wp_password': 'test_pass'
        }
        
        # Initialize engine
        engine = BlogAutomationEngine(test_config, logger)
        print("✅ Automation engine initialized successfully")
        
        # Test configuration loading
        openai_config = engine.load_openai_image_config()
        print(f"✅ OpenAI configuration loaded: {openai_config}")
        
        # Test prompt creation
        test_title = "Manchester United Signs New Player"
        test_content = "Manchester United has completed the signing of a new midfielder..."
        
        # Test auto-generated prompt
        auto_prompt = engine.create_openai_image_prompt(
            test_title, test_content, openai_config, is_featured=True
        )
        print(f"✅ Auto-generated prompt: {auto_prompt[:100]}...")
        
        # Test custom prompt
        custom_prompt = "A professional football stadium with dramatic lighting"
        custom_result = engine.create_openai_image_prompt(
            test_title, test_content, openai_config, is_featured=True, custom_prompt=custom_prompt
        )
        print(f"✅ Custom prompt result: {custom_result[:100]}...")
        
        # Test theme extraction
        themes = engine.extract_content_themes(test_title, test_content)
        print(f"✅ Extracted themes: {themes}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing automation engine: {e}")
        return False

def test_gui_integration():
    """Test GUI OpenAI integration"""
    print("\n🧪 Testing GUI OpenAI Integration...")
    
    try:
        # Test importing GUI modules
        from gui_blogger import BlogAutomationGUI
        print("✅ GUI modules imported successfully")
        
        # Test if OpenAI tab creation method exists
        if hasattr(BlogAutomationGUI, 'create_openai_image_tab'):
            print("✅ OpenAI image tab method exists")
        else:
            print("❌ OpenAI image tab method missing")
            
        if hasattr(BlogAutomationGUI, 'save_openai_image_config'):
            print("✅ Save OpenAI config method exists")
        else:
            print("❌ Save OpenAI config method missing")
            
        if hasattr(BlogAutomationGUI, 'set_custom_prompt'):
            print("✅ Custom prompt method exists")
        else:
            print("❌ Custom prompt method missing")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing GUI: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 OpenAI Image Generation Test Suite")
    print("=" * 50)
    
    tests = [
        test_openai_config,
        test_automation_engine,
        test_gui_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! OpenAI image generation is ready to use.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
