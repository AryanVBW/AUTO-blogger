#!/usr/bin/env python3
"""
Test script to verify OpenAI integration fix
Copyright © 2025 AryanVBW
"""

import sys
import os

def test_openai_import():
    """Test if OpenAI module can be imported correctly"""
    try:
        from openai import OpenAI
        print("✅ OpenAI module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import OpenAI: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing OpenAI: {e}")
        return False

def test_openai_client_creation():
    """Test if OpenAI client can be created (without API key)"""
    try:
        from openai import OpenAI
        # Test client creation with dummy API key
        client = OpenAI(api_key="test-key")
        print("✅ OpenAI client created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create OpenAI client: {e}")
        return False

def test_automation_engine_import():
    """Test if automation engine can be imported"""
    try:
        from automation_engine import BlogAutomationEngine
        print("✅ BlogAutomationEngine imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import BlogAutomationEngine: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing BlogAutomationEngine: {e}")
        return False

def test_gui_import():
    """Test if GUI module can be imported"""
    try:
        import gui_blogger
        print("✅ GUI module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import GUI module: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing GUI module: {e}")
        return False

def test_all_dependencies():
    """Test all critical dependencies"""
    dependencies = [
        ('requests', 'Web requests'),
        ('bs4', 'BeautifulSoup'),
        ('selenium', 'Selenium WebDriver'),
        ('PIL', 'Pillow (Image processing)'),
        ('openai', 'OpenAI API'),
    ]
    
    failed = []
    
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"✅ {description} - OK")
        except ImportError:
            print(f"❌ {description} - MISSING")
            failed.append(module)
        except Exception as e:
            print(f"⚠️ {description} - ERROR: {e}")
            failed.append(module)
    
    return len(failed) == 0, failed

def main():
    """Run all tests"""
    print("🧪 Testing AUTO-blogger Dependencies and OpenAI Fix")
    print("=" * 50)
    
    tests = [
        ("OpenAI Import", test_openai_import),
        ("OpenAI Client Creation", test_openai_client_creation),
        ("Automation Engine Import", test_automation_engine_import),
        ("GUI Import", test_gui_import),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"   Test failed: {test_name}")
    
    print(f"\n📊 Dependency Check:")
    deps_ok, failed_deps = test_all_dependencies()
    
    print(f"\n📋 Test Results:")
    print(f"   Core Tests: {passed}/{total} passed")
    print(f"   Dependencies: {'✅ All OK' if deps_ok else f'❌ {len(failed_deps)} missing'}")
    
    if passed == total and deps_ok:
        print(f"\n🎉 All tests passed! AUTO-blogger is ready to use.")
        print(f"\n🚀 To start the application:")
        print(f"   1. Run: ./autoblog")
        print(f"   2. Or: python gui_blogger.py")
        return True
    else:
        print(f"\n❌ Some tests failed. Please check the installation.")
        if failed_deps:
            print(f"\n📦 Missing dependencies: {', '.join(failed_deps)}")
            print(f"   Run: pip install {' '.join(failed_deps)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)