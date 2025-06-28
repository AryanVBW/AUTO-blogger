#!/usr/bin/env python3
"""
Test if the OpenAI image tab loads correctly in the actual GUI
"""

import tkinter as tk
from tkinter import ttk
import sys
import time

def test_openai_tab_in_gui():
    """Test OpenAI image tab loading in the actual GUI"""
    print("🧪 Testing OpenAI Image Tab in Full GUI...")
    
    try:
        # Import GUI class
        from gui_blogger import BlogAutomationGUI
        
        # Create root window
        root = tk.Tk()
        root.title("OpenAI Tab Test")
        root.geometry("800x600")
        
        # Create GUI application
        app = BlogAutomationGUI(root)
        print("✅ GUI application created successfully")
        
        # Check if notebook exists and has tabs
        if hasattr(app, 'notebook'):
            print("✅ Notebook widget exists")
            
            # Get all tabs
            tab_count = app.notebook.index('end')
            print(f"📋 Number of tabs: {tab_count}")
            
            # List all tabs
            tab_names = []
            for i in range(tab_count):
                tab_name = app.notebook.tab(i, 'text')
                tab_names.append(tab_name)
                print(f"  Tab {i+1}: {tab_name}")
            
            # Check specifically for OpenAI tab
            openai_tab_found = any("OpenAI" in tab for tab in tab_names)
            if openai_tab_found:
                print("✅ OpenAI Images tab found!")
                
                # Try to select the OpenAI tab
                for i, tab_name in enumerate(tab_names):
                    if "OpenAI" in tab_name:
                        try:
                            app.notebook.select(i)
                            print(f"✅ Successfully selected OpenAI tab (index {i})")
                            break
                        except Exception as e:
                            print(f"⚠️ Could not select OpenAI tab: {e}")
            else:
                print("❌ OpenAI Images tab not found")
                return False
        else:
            print("❌ Notebook widget not found")
            return False
            
        # Test if OpenAI image variables exist
        if hasattr(app, 'openai_image_vars'):
            print("✅ OpenAI image variables exist")
            print(f"📋 OpenAI config vars: {list(app.openai_image_vars.keys())}")
        else:
            print("⚠️ OpenAI image variables not found")
            
        # Keep window open for a moment to visually verify
        print("\n🎉 All tests passed!")
        print("💡 OpenAI Image tab should be working correctly")
        print("📖 You can now close this window and test the main application")
        
        # Create a simple close button
        close_btn = ttk.Button(root, text="Close Test", command=root.destroy)
        close_btn.pack(pady=20)
        
        # Start the GUI loop
        root.mainloop()
        return True
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_openai_tab_in_gui()
    sys.exit(0 if success else 1)
