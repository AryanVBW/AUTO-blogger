#!/bin/bash

# AUTO-blogger Direct Launcher
# This script launches AUTO-blogger without requiring system-wide installation

echo -e "\033[96m+===========================================================================+\033[0m"
echo -e "\033[96m| █████   █████  ███                       █████         █████   ███   █████ |\033[0m"
echo -e "\033[96m|░░███   ░░███  ░░░                       ░░███         ░░███   ░███  ░░███  |\033[0m"
echo -e "\033[96m| ░███    ░███  ████  █████ █████  ██████  ░███ █████    ░███   ░███   ░███  |\033[0m"
echo -e "\033[96m| ░███    ░███ ░░███ ░░███ ░░███  ███░░███ ░███░░███     ░███   ░███   ░███  |\033[0m"
echo -e "\033[96m| ░░███   ███   ░███  ░███  ░███ ░███████  ░██████░      ░░███  █████  ███   |\033[0m"
echo -e "\033[96m|  ░░░█████░    ░███  ░░███ ███  ░███░░░   ░███░░███      ░░░█████░█████░    |\033[0m"
echo -e "\033[96m|    ░░███      █████  ░░█████   ░░██████  ████ █████       ░░███ ░░███      |\033[0m"
echo -e "\033[96m|     ░░░      ░░░░░    ░░░░░     ░░░░░░  ░░░░ ░░░░░         ░░░   ░░░       |\033[0m"
echo -e "\033[95m|                                                                            |\033[0m"
echo -e "\033[95m|                           🔥GitHub:    github.com/AryanVBW                 |\033[0m"
echo -e "\033[95m|                               Copyright © 2025 AryanVBW                    |\033[0m"
echo -e "\033[95m|                           💖Instagram: Aryan_Technolog1es                  |\033[0m"
echo -e "\033[95m|                           📧Email:    vivek.aryanvbw@gmail.com             |\033[0m"
echo -e "\033[32m+===========================================================================+\033[0m"
echo -e "\033[93m|                            Welcome to AUTO Blogger!                        |\033[0m"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the installation directory
cd "$SCRIPT_DIR"

echo "🚀 Starting AUTO-blogger..."
echo "📁 Working directory: $SCRIPT_DIR"

# Try different Python commands
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python not found. Please install Python 3.7 or higher."
    exit 1
fi

echo "🐍 Using Python: $PYTHON_CMD"

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    if [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
else
    echo "⚠️ Virtual environment not found. Using system Python."
fi

# Check if gui_blogger.py exists
if [ ! -f "gui_blogger.py" ]; then
    echo "❌ Error: gui_blogger.py not found in $SCRIPT_DIR"
    echo "Please make sure you're running this script from the AUTO-blogger directory."
    exit 1
fi

# Launch the application
$PYTHON_CMD gui_blogger.py

# Keep terminal open briefly to show any final messages
echo ""
echo "✅ AUTO-blogger session ended."
sleep 1