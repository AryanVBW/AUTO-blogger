#!/bin/bash

# AUTO Blogger Launcher for macOS
# This script properly launches the AUTO Blogger application with icon support

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set the Python script path
PYTHON_SCRIPT="$SCRIPT_DIR/gui_blogger.py"
ICON_PATH="$SCRIPT_DIR/icon.png"

# Check if files exist
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "❌ Error: gui_blogger.py not found at $PYTHON_SCRIPT"
    exit 1
fi

if [[ ! -f "$ICON_PATH" ]]; then
    echo "⚠️ Warning: icon.png not found at $ICON_PATH"
fi

# Set application name for dock
export CFBundleName="AUTO Blogger"
export CFBundleDisplayName="AUTO Blogger"
export CFBundleIdentifier="com.aryanvbw.autoblogger"

echo "🚀 Launching AUTO Blogger..."
echo "📁 Working directory: $SCRIPT_DIR"
echo "🐍 Python script: $PYTHON_SCRIPT"
echo "🖼️ Icon: $ICON_PATH"

# Change to the script directory
cd "$SCRIPT_DIR"

# Launch the application
python3 gui_blogger.py

echo "✅ AUTO Blogger closed."
