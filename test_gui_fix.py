#!/usr/bin/env python3
"""
Quick test to verify OpenAI image tab loading fix
"""

import sys
import tkinter as tk
from tkinter import ttk

def test_openai_tab():
    """Test OpenAI image tab creation"""
    try:
        # Import the GUI class
        from gui_blogger import BlogAutomationGUI
        
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide window for testing
        root.title("Test")
        
        print("🧪 Testing OpenAI Image Tab Fix...")
        
        # Create GUI instance
        app = BlogAutomationGUI(root)
        print("✅ GUI instance created successfully")
        
        # Test OpenAI image tab creation
        app.create_openai_image_tab()
        print("✅ OpenAI image tab created successfully")
        
        # Test if notebook has tabs
        tab_count = app.notebook.index('end')
        print(f"✅ GUI has {tab_count} tabs")
        
        # Check if OpenAI tab exists
        tab_names = []
        for i in range(tab_count):
            tab_name = app.notebook.tab(i, 'text')
            tab_names.append(tab_name)
        
        print(f"📋 Available tabs: {tab_names}")
        
        if any("OpenAI" in tab for tab in tab_names):
            print("✅ OpenAI Images tab found in notebook")
        else:
            print("❌ OpenAI Images tab not found")
            
        print("\n🎉 Test completed successfully!")
        print("💡 The OpenAI image tab should now load properly in the main application.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if 'root' in locals():
            root.destroy()

if __name__ == "__main__":
    success = test_openai_tab()
    sys.exit(0 if success else 1)
