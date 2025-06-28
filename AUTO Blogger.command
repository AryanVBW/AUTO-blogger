#!/bin/bash

# AUTO Blogger macOS Application
# Double-click this file to launch AUTO Blogger with proper icon support

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set application properties for macOS
export CFBundleName="AUTO Blogger"
export CFBundleDisplayName="AUTO Blogger" 
export CFBundleIdentifier="com.aryanvbw.autoblogger"

echo "🚀 Launching AUTO Blogger..."

# Change to the script directory
cd "$SCRIPT_DIR"

# Launch the Python GUI application
python3 gui_blogger.py

# Keep terminal open briefly to show any final messages
sleep 2
