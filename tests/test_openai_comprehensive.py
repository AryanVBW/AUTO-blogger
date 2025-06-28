#!/usr/bin/env python3
"""
Comprehensive test for OpenAI image tab functionality
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import os
import sys

def test_comprehensive_openai_tab():
    """Comprehensive test of OpenAI image tab functionality"""
    print("🔬 Comprehensive OpenAI Image Tab Test")
    print("=" * 50)
    
    try:
        # Test 1: Import and basic setup
        print("1. Testing imports and basic setup...")
        from gui_blogger import BlogAutomationGUI
        print("   ✅ GUI class imported successfully")
        
        # Test 2: Create GUI instance
        print("2. Creating GUI instance...")
        root = tk.Tk()
        root.withdraw()  # Hide for testing
        app = BlogAutomationGUI(root)
        print("   ✅ GUI instance created successfully")
        
        # Test 3: Check if required attributes exist
        print("3. Checking required attributes...")
        required_attrs = ['notebook', 'base_config_dir', 'get_current_config_dir']
        for attr in required_attrs:
            if hasattr(app, attr):
                print(f"   ✅ {attr} exists")
            else:
                print(f"   ❌ {attr} missing")
                return False
        
        # Test 4: Test config directory
        print("4. Testing configuration directory...")
        config_dir = app.get_current_config_dir()
        print(f"   📁 Config directory: {config_dir}")
        if os.path.exists(config_dir):
            print("   ✅ Config directory exists")
        else:
            print("   ⚠️ Config directory doesn't exist, will be created")
            os.makedirs(config_dir, exist_ok=True)
            
        # Test 5: Test config file loading
        print("5. Testing OpenAI config file...")
        config_path = os.path.join(config_dir, "openai_image_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                print(f"   ✅ Config loaded: {len(config)} settings")
            except Exception as e:
                print(f"   ❌ Config load error: {e}")
                return False
        else:
            print("   ⚠️ Config file doesn't exist, will use defaults")
            
        # Test 6: Create OpenAI tab
        print("6. Creating OpenAI image tab...")
        try:
            app.create_openai_image_tab()
            print("   ✅ OpenAI image tab created successfully")
        except Exception as e:
            print(f"   ❌ Tab creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        # Test 7: Check tab in notebook
        print("7. Checking tab in notebook...")
        tab_count = app.notebook.index('end')
        print(f"   📊 Total tabs: {tab_count}")
        
        openai_tab_found = False
        for i in range(tab_count):
            tab_name = app.notebook.tab(i, 'text')
            if "OpenAI" in tab_name:
                print(f"   ✅ OpenAI tab found: '{tab_name}' at index {i}")
                openai_tab_found = True
                break
                
        if not openai_tab_found:
            print("   ❌ OpenAI tab not found in notebook")
            return False
            
        # Test 8: Check variables
        print("8. Checking OpenAI variables...")
        if hasattr(app, 'openai_image_vars'):
            vars_count = len(app.openai_image_vars)
            print(f"   ✅ OpenAI variables: {vars_count} configured")
            print(f"   📋 Variables: {list(app.openai_image_vars.keys())}")
        else:
            print("   ❌ OpenAI variables not found")
            return False
            
        # Test 9: Check custom prompt widget
        print("9. Checking custom prompt widget...")
        if hasattr(app, 'custom_prompt_text'):
            print("   ✅ Custom prompt text widget exists")
        else:
            print("   ❌ Custom prompt text widget missing")
            return False
            
        # Test 10: Test save functionality
        print("10. Testing save functionality...")
        try:
            app.save_openai_image_config()
            print("   ✅ Save function executed successfully")
        except Exception as e:
            print(f"   ❌ Save function failed: {e}")
            return False
            
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("✅ OpenAI Image tab is working correctly")
        print("💡 You can now use the main application")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive test failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'root' in locals():
            root.destroy()

if __name__ == "__main__":
    success = test_comprehensive_openai_tab()
    sys.exit(0 if success else 1)
