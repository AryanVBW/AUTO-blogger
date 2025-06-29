#!/usr/bin/env python3
"""
Test script to verify SEO Plugin UI behavior
This script tests that the SEO plugin dropdown only appears in the SEO Plugin Settings section
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui_blogger import BlogAutomationGUI

def test_seo_plugin_ui():
    """Test that SEO plugin dropdown only appears in SEO Plugin Settings section"""
    print("🧪 Testing SEO Plugin UI Behavior...")
    
    # Create a test GUI instance
    root = tk.Tk()
    root.withdraw()  # Hide the main window for testing
    
    try:
        app = BlogAutomationGUI(root)
        
        # Test each section to ensure SEO plugin dropdown only appears in the right place
        config_sections = [
            ("SEO Plugin Settings", "seo_plugin_settings", "🔧"),
            ("Internal Links", "internal_links", "🔗"),
            ("External Links", "external_links", "🌐"),
            ("Style Prompt", "style_prompt", "📝"),
            ("SEO Title & Meta Prompt", "seo_title_meta_prompt", "🎯"),
            ("Tag Generation Prompt", "tag_generation_prompt", "🏷️"),
            ("Keyphrase Extraction Prompt", "keyphrase_extraction_prompt", "🔑")
        ]
        
        results = []
        
        for idx, (label, key, emoji) in enumerate(config_sections):
            print(f"\n📋 Testing section: {label} ({key})")
            
            # Simulate showing this section
            try:
                app.show_section_editor(idx)
                
                # Check if seo_plugin_var exists
                has_seo_dropdown = hasattr(app, 'seo_plugin_var')
                
                if key == "seo_plugin_settings":
                    if has_seo_dropdown:
                        print(f"✅ PASS: SEO plugin dropdown correctly appears in {label}")
                        results.append((label, "PASS", "SEO dropdown present as expected"))
                    else:
                        print(f"❌ FAIL: SEO plugin dropdown missing from {label}")
                        results.append((label, "FAIL", "SEO dropdown missing"))
                else:
                    if not has_seo_dropdown:
                        print(f"✅ PASS: SEO plugin dropdown correctly absent from {label}")
                        results.append((label, "PASS", "SEO dropdown absent as expected"))
                    else:
                        print(f"❌ FAIL: SEO plugin dropdown incorrectly appears in {label}")
                        results.append((label, "FAIL", "SEO dropdown present when it shouldn't be"))
                        
            except Exception as e:
                print(f"❌ ERROR: Failed to test {label}: {e}")
                results.append((label, "ERROR", str(e)))
        
        # Print summary
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        
        passed = 0
        failed = 0
        errors = 0
        
        for label, status, message in results:
            if status == "PASS":
                print(f"✅ {label}: {message}")
                passed += 1
            elif status == "FAIL":
                print(f"❌ {label}: {message}")
                failed += 1
            else:
                print(f"⚠️  {label}: {message}")
                errors += 1
        
        print(f"\n📈 Results: {passed} passed, {failed} failed, {errors} errors")
        
        if failed == 0 and errors == 0:
            print("🎉 ALL TESTS PASSED! SEO plugin dropdown behavior is correct.")
            return True
        else:
            print("⚠️  Some tests failed. Please review the implementation.")
            return False
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: Failed to initialize GUI: {e}")
        return False
    finally:
        root.destroy()

if __name__ == "__main__":
    success = test_seo_plugin_ui()
    sys.exit(0 if success else 1)