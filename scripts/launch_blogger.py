#!/usr/bin/env python3
"""
WordPress Blog Automation - Launcher Script
This script launches the GUI application with proper error handling

Copyright © 2025 AryanVBW
GitHub: https://github.com/AryanVBW
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
import subprocess

def check_requirements():
    """Check if all requirements are installed"""
    required_packages = [
        ('requests', 'requests'),
        ('beautifulsoup4', 'bs4'),
        ('selenium', 'selenium'),
        ('webdriver-manager', 'webdriver_manager')
    ]
    
    missing = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    return missing

def install_requirements(missing_packages):
    """Install missing requirements"""
    try:
        for package in missing_packages:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        return False

def main():
    """Main launcher function"""
    # Check if we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check requirements
    missing = check_requirements()
    
    if missing:
        print(f"Missing required packages: {', '.join(missing)}")
        response = input("Would you like to install them now? (y/n): ")
        
        if response.lower() == 'y':
            if install_requirements(missing):
                print("Requirements installed successfully!")
                print("Please restart the application.")
                return
            else:
                print("Failed to install requirements. Please install manually:")
                for package in missing:
                    print(f"pip install {package}")
                return
        else:
            print("Cannot run application without required packages.")
            return
    
    # Import and run the GUI
    try:
        from gui_blogger import main as run_gui
        run_gui()
    except ImportError as e:
        print(f"Error importing GUI module: {e}")
        print("Make sure gui_blogger.py and automation_engine.py are in the same directory.")
    except Exception as e:
        print(f"Error running application: {e}")

if __name__ == "__main__":
    main()
