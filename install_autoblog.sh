#!/bin/bash

# AUTO-blogger Installation Script with Auto-Update
# Copyright © 2025 AryanVBW
# GitHub: https://github.com/AryanVBW/AUTO-blogger

set -e  # Exit on any error

# Environment variables for automation
# Set AUTO_UPDATE=true for automatic updates without prompts
# Set NON_INTERACTIVE=true for completely non-interactive installation
AUTO_UPDATE=${AUTO_UPDATE:-false}
NON_INTERACTIVE=${NON_INTERACTIVE:-false}

# Check if running in non-interactive environment (CI/CD, piped input, etc.)
if [ ! -t 0 ] || [ ! -t 1 ]; then
    NON_INTERACTIVE=true
fi

# Configuration
REPO_URL="https://github.com/AryanVBW/AUTO-blogger.git"
INSTALL_DIR="$HOME/AUTO-blogger"
APP_NAME="AUTO-blogger"

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logo
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


# Function to detect OS with enhanced detection
detect_os() {
    local os="unknown"
    
    # Check for Windows first
    if [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ -n "$WINDIR" ]]; then
        os="windows"
    # Check for macOS
    elif [[ "$OSTYPE" == "darwin"* ]] || [[ "$(uname -s)" == "Darwin" ]]; then
        os="macos"
    # Check for Linux
    elif [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$(uname -s)" == "Linux" ]]; then
        os="linux"
    # Additional checks using uname
    elif command_exists uname; then
        case "$(uname -s)" in
            Linux*)     os="linux";;
            Darwin*)    os="macos";;
            CYGWIN*)    os="windows";;
            MINGW*)     os="windows";;
            MSYS*)      os="windows";;
        esac
    fi
    
    echo "$os"
}

# Function to install Git if not available
install_git() {
    local os=$(detect_os)
    echo -e "${YELLOW}📦 Installing Git...${NC}"
    
    case $os in
        "linux")
            if command_exists apt-get; then
                echo -e "${CYAN}🔄 Updating package lists...${NC}"
                sudo apt-get update || handle_error 1 "Failed to update package lists" "Check your internet connection and package manager"
                echo -e "${CYAN}🔄 Installing Git via apt-get...${NC}"
                sudo apt-get install -y git || handle_error 1 "Failed to install Git via apt-get" "Try installing manually: sudo apt-get install git"
            elif command_exists yum; then
                echo -e "${CYAN}🔄 Installing Git via yum...${NC}"
                sudo yum install -y git || handle_error 1 "Failed to install Git via yum" "Try installing manually: sudo yum install git"
            elif command_exists dnf; then
                echo -e "${CYAN}🔄 Installing Git via dnf...${NC}"
                sudo dnf install -y git || handle_error 1 "Failed to install Git via dnf" "Try installing manually: sudo dnf install git"
            elif command_exists pacman; then
                echo -e "${CYAN}🔄 Installing Git via pacman...${NC}"
                sudo pacman -S --noconfirm git || handle_error 1 "Failed to install Git via pacman" "Try installing manually: sudo pacman -S git"
            elif command_exists zypper; then
                echo -e "${CYAN}🔄 Installing Git via zypper...${NC}"
                sudo zypper install -y git || handle_error 1 "Failed to install Git via zypper" "Try installing manually: sudo zypper install git"
            else
                handle_error 1 "Unsupported Linux distribution" "Please install Git manually from https://git-scm.com/downloads"
            fi
            ;;
        "macos")
            if command_exists brew; then
                echo -e "${CYAN}🔄 Installing Git via Homebrew...${NC}"
                brew install git || handle_error 1 "Failed to install Git via Homebrew" "Try installing manually from https://git-scm.com/download/mac"
            elif command_exists port; then
                echo -e "${CYAN}🔄 Installing Git via MacPorts...${NC}"
                sudo port install git || handle_error 1 "Failed to install Git via MacPorts" "Try installing Homebrew or download from https://git-scm.com/download/mac"
            else
                handle_error 1 "No package manager found" "Please install Homebrew (https://brew.sh) or download Git from https://git-scm.com/download/mac"
            fi
            ;;
        "windows")
            handle_error 1 "Git installation required" "Please install Git from https://git-scm.com/download/win and run this script again"
            ;;
        *)
            handle_error 1 "Unsupported operating system" "Please install Git manually from https://git-scm.com/downloads"
            ;;
    esac
    
    # Verify Git installation
    if ! command_exists git; then
        handle_error 1 "Git installation failed" "Please install Git manually and try again"
    fi
    
    echo -e "${GREEN}✅ Git installed successfully${NC}"
}

# Function to check if Git is available
check_git() {
    echo -e "${YELLOW}🔍 Checking Git installation...${NC}"
    
    if command_exists git; then
        local git_version=$(git --version 2>/dev/null | cut -d' ' -f3)
        echo -e "${GREEN}✅ Git found (version: $git_version)${NC}"
        
        # Check if Git is properly configured
        if ! git config --global user.name >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠️ Git user not configured. Setting default configuration...${NC}"
            git config --global user.name "AUTO-blogger User" || true
            git config --global user.email "user@auto-blogger.local" || true
        fi
    else
        echo -e "${RED}❌ Git not found. Installing Git...${NC}"
        install_git
        
        # Verify installation
        if command_exists git; then
            local git_version=$(git --version 2>/dev/null | cut -d' ' -f3)
            echo -e "${GREEN}✅ Git successfully installed (version: $git_version)${NC}"
        else
            handle_error 1 "Git installation verification failed" "Please install Git manually and try again"
        fi
    fi
}

# Function to clone or update repository
clone_or_update_repo() {
    echo -e "${YELLOW}📥 Setting up repository...${NC}"
    
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}📁 Directory exists. Checking for updates...${NC}"
        cd "$INSTALL_DIR" || handle_error 1 "Failed to access installation directory" "Check permissions for $INSTALL_DIR"
        
        # Check if it's a git repository
        if [ -d ".git" ]; then
            echo -e "${CYAN}🔄 Updating existing installation...${NC}"
            
            # Fetch latest changes
            echo -e "${CYAN}📡 Fetching latest changes...${NC}"
            git fetch origin || handle_error 1 "Failed to fetch updates" "Check your internet connection and GitHub access"
            
            # Determine the default branch
            local default_branch
            default_branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@') || default_branch="main"
            
            # Fallback to main or master
            if ! git rev-parse "origin/$default_branch" >/dev/null 2>&1; then
                if git rev-parse "origin/main" >/dev/null 2>&1; then
                    default_branch="main"
                elif git rev-parse "origin/master" >/dev/null 2>&1; then
                    default_branch="master"
                else
                    handle_error 1 "Cannot determine repository branch" "Repository may be corrupted. Try removing $INSTALL_DIR and running again"
                fi
            fi
            
            # Check if updates are available
            local local_commit remote_commit
            local_commit=$(git rev-parse HEAD 2>/dev/null)
            remote_commit=$(git rev-parse "origin/$default_branch" 2>/dev/null)
            
            if [ "$local_commit" != "$remote_commit" ]; then
                echo -e "${GREEN}📦 Updates available! Updating from $default_branch...${NC}"
                
                # Stash any local changes
                git stash push -m "Auto-stash before update" >/dev/null 2>&1 || true
                
                # Pull updates
                git pull origin "$default_branch" || handle_error 1 "Failed to pull updates" "Repository may have conflicts. Try removing $INSTALL_DIR and running again"
                
                echo -e "${GREEN}✅ Repository updated successfully${NC}"
            else
                echo -e "${GREEN}✅ Repository is already up to date${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️ Directory exists but is not a git repository. Removing and cloning fresh...${NC}"
            cd .. || handle_error 1 "Failed to navigate to parent directory" "Check file system permissions"
            rm -rf "$INSTALL_DIR" || handle_error 1 "Failed to remove existing directory" "Check permissions and try running with sudo"
            
            echo -e "${CYAN}📥 Cloning fresh repository...${NC}"
            git clone "$REPO_URL" "$INSTALL_DIR" || handle_error 1 "Failed to clone repository" "Check your internet connection and GitHub access"
            cd "$INSTALL_DIR" || handle_error 1 "Failed to access cloned directory" "Check file system permissions"
        fi
    else
        echo -e "${CYAN}📥 Cloning repository...${NC}"
        
        # Create parent directory if needed
        mkdir -p "$(dirname "$INSTALL_DIR")" || handle_error 1 "Failed to create parent directory" "Check permissions for $(dirname "$INSTALL_DIR")"
        
        # Clone repository
        git clone "$REPO_URL" "$INSTALL_DIR" || handle_error 1 "Failed to clone repository" "Check your internet connection and GitHub access"
        cd "$INSTALL_DIR" || handle_error 1 "Failed to access cloned directory" "Check file system permissions"
        
        echo -e "${GREEN}✅ Repository cloned successfully${NC}"
    fi
    
    # Verify essential files exist
    local essential_files=("requirements.txt" "gui_blogger.py" "automation_engine.py" "autoblog_launcher.py")
    for file in "${essential_files[@]}"; do
        if [ ! -f "$file" ]; then
            handle_error 1 "Essential file missing: $file" "Repository may be corrupted. Try removing $INSTALL_DIR and running again"
        fi
    done
    
    echo -e "${GREEN}✅ Repository verification completed${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to handle errors with detailed messages
handle_error() {
    local error_code=$1
    local error_message="$2"
    local solution="$3"
    
    echo -e "${RED}❌ ERROR: $error_message${NC}"
    if [ -n "$solution" ]; then
        echo -e "${YELLOW}💡 SOLUTION: $solution${NC}"
    fi
    echo -e "${CYAN}📧 For support, contact: AryanVBW@gmail.com${NC}"
    exit $error_code
}

# Function to check if AUTO-blogger is already installed
check_existing_installation() {
    echo -e "${YELLOW}🔍 Checking for existing installation...${NC}"
    
    # Check if directory exists
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}⚠️ AUTO-blogger is already installed at: $INSTALL_DIR${NC}"
        
        # Check for non-interactive mode or auto-update flag
        if [ "$AUTO_UPDATE" = "true" ] || [ "$NON_INTERACTIVE" = "true" ] || [ ! -t 0 ]; then
            echo -e "${CYAN}🔄 Non-interactive mode detected - proceeding with update...${NC}"
            echo -e "${GREEN}✅ Proceeding with update...${NC}"
            return 0
        fi
        
        echo -e "${CYAN}What would you like to do?${NC}"
        echo "1) Update existing installation (recommended)"
        echo "2) Remove and reinstall completely"
        echo "3) Cancel installation"
        echo ""
        echo -e "${YELLOW}💡 Tip: Use 'curl -sSL ... | AUTO_UPDATE=true bash' for automatic updates${NC}"
        
        # Add timeout for automated environments
        local choice
        if read -t 30 -p "Enter your choice (1-3) [default: 1 in 30s]: " choice; then
            echo ""
        else
            echo ""
            echo -e "${YELLOW}⏰ No input received within 30 seconds, defaulting to update...${NC}"
            choice="1"
        fi
        
        case $choice in
            1|"")
                echo -e "${GREEN}✅ Proceeding with update...${NC}"
                return 0
                ;;
            2)
                echo -e "${YELLOW}🗑️ Removing existing installation...${NC}"
                rm -rf "$INSTALL_DIR" || handle_error 1 "Failed to remove existing installation" "Check permissions and try running with sudo"
                echo -e "${GREEN}✅ Existing installation removed${NC}"
                return 0
                ;;
            3)
                echo -e "${BLUE}👋 Installation cancelled by user${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Invalid choice. Defaulting to update...${NC}"
                return 0
                ;;
        esac
    else
        echo -e "${GREEN}✅ No existing installation found${NC}"
    fi
}

# Function to verify system requirements
verify_requirements() {
    local os=$(detect_os)
    echo -e "${YELLOW}🔍 Verifying system requirements...${NC}"
    
    # Check OS support
    if [ "$os" == "unknown" ]; then
        handle_error 1 "Unsupported operating system" "This installer supports Windows, macOS, and Linux only"
    fi
    
    echo -e "${GREEN}✅ Operating System: $os${NC}"
    
    # Check internet connectivity
    echo -e "${CYAN}🌐 Testing internet connectivity...${NC}"
    if ! ping -c 1 google.com >/dev/null 2>&1 && ! ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        handle_error 1 "No internet connection" "Please check your internet connection and try again"
    fi
    
    echo -e "${GREEN}✅ Internet connection verified${NC}"
    
    # Check available disk space (at least 500MB)
    echo -e "${CYAN}💾 Checking disk space...${NC}"
    local available_space
    if command_exists df; then
        available_space=$(df "$HOME" | tail -1 | awk '{print $4}')
        if [ "$available_space" -lt 512000 ]; then
            handle_error 1 "Insufficient disk space" "At least 500MB of free space required"
        fi
        echo -e "${GREEN}✅ Sufficient disk space available${NC}"
    fi
    
    # Check write permissions
    echo -e "${CYAN}🔐 Checking permissions...${NC}"
    if [ ! -w "$(dirname "$INSTALL_DIR")" ]; then
        handle_error 1 "No write permission" "Cannot write to installation directory. Check permissions or run with sudo"
    fi
    
    echo -e "${GREEN}✅ All system requirements verified${NC}"
}

# Function to install Python on different systems
install_python() {
    local os=$(detect_os)
    echo -e "${YELLOW}📦 Installing Python...${NC}"
    
    case $os in
        "linux")
            if command_exists apt-get; then
                echo -e "${CYAN}🔄 Updating package lists...${NC}"
                sudo apt-get update || handle_error 1 "Failed to update package lists" "Check your internet connection and package manager"
                echo -e "${CYAN}🔄 Installing Python via apt-get...${NC}"
                sudo apt-get install -y python3 python3-pip python3-venv python3-tk python3-dev || handle_error 1 "Failed to install Python via apt-get" "Try installing manually: sudo apt-get install python3 python3-pip python3-venv"
            elif command_exists yum; then
                echo -e "${CYAN}🔄 Installing Python via yum...${NC}"
                sudo yum install -y python3 python3-pip python3-tkinter python3-devel || handle_error 1 "Failed to install Python via yum" "Try installing manually: sudo yum install python3 python3-pip"
            elif command_exists dnf; then
                echo -e "${CYAN}🔄 Installing Python via dnf...${NC}"
                sudo dnf install -y python3 python3-pip python3-tkinter python3-devel || handle_error 1 "Failed to install Python via dnf" "Try installing manually: sudo dnf install python3 python3-pip"
            elif command_exists pacman; then
                echo -e "${CYAN}🔄 Installing Python via pacman...${NC}"
                sudo pacman -S --noconfirm python python-pip tk || handle_error 1 "Failed to install Python via pacman" "Try installing manually: sudo pacman -S python python-pip"
            elif command_exists zypper; then
                echo -e "${CYAN}🔄 Installing Python via zypper...${NC}"
                sudo zypper install -y python3 python3-pip python3-devel python3-tk || handle_error 1 "Failed to install Python via zypper" "Try installing manually: sudo zypper install python3 python3-pip"
            else
                handle_error 1 "Unsupported Linux distribution" "Please install Python 3.8+ manually from https://www.python.org/downloads/"
            fi
            ;;
        "macos")
            if command_exists brew; then
                echo -e "${CYAN}🔄 Installing Python via Homebrew...${NC}"
                brew install python@3.11 python-tk || handle_error 1 "Failed to install Python via Homebrew" "Try installing manually from https://www.python.org/downloads/mac-osx/"
            elif command_exists port; then
                echo -e "${CYAN}🔄 Installing Python via MacPorts...${NC}"
                sudo port install python39 +universal || handle_error 1 "Failed to install Python via MacPorts" "Try installing Homebrew or download from https://www.python.org/downloads/mac-osx/"
            else
                echo -e "${YELLOW}⚠️ Homebrew not found. Installing Homebrew first...${NC}"
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || handle_error 1 "Failed to install Homebrew" "Please install Homebrew manually from https://brew.sh"
                brew install python@3.11 python-tk || handle_error 1 "Failed to install Python after Homebrew installation" "Please install Python manually from https://www.python.org/downloads/mac-osx/"
            fi
            ;;
        "windows")
            handle_error 1 "Python installation required" "Please install Python 3.8+ from https://python.org/downloads/ and run this script again"
            ;;
        *)
            handle_error 1 "Unsupported operating system" "Please install Python 3.8+ manually from https://www.python.org/downloads/"
            ;;
    esac
    
    # Verify Python installation
    if ! command_exists python3; then
        handle_error 1 "Python installation failed" "Please install Python manually and try again"
    fi
    
    echo -e "${GREEN}✅ Python installed successfully${NC}"
}

# Function to check Python version
check_python() {
    echo -e "${YELLOW}🔍 Checking Python installation...${NC}"
    
    local python_cmd=""
    local python_version=""
    
    # Check for python3 first, then python
    if command_exists python3; then
        python_cmd="python3"
        python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null)
    elif command_exists python; then
        # Check if python points to Python 3
        local py_major=$(python -c "import sys; print(sys.version_info.major)" 2>/dev/null)
        if [ "$py_major" = "3" ]; then
            python_cmd="python"
            python_version=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null)
        fi
    fi
    
    if [ -n "$python_cmd" ] && [ -n "$python_version" ]; then
        local required_version="3.8"
        local current_version=$(echo "$python_version" | cut -d'.' -f1,2)
        
        # Compare versions
        if [ "$(printf '%s\n' "$required_version" "$current_version" | sort -V | head -n1)" = "$required_version" ]; then
            echo -e "${GREEN}✅ Python $python_version found ($python_cmd)${NC}"
            
            # Set global PYTHON_CMD variable
            PYTHON_CMD="$python_cmd"
            
            # Check if pip is available
            if ! $python_cmd -m pip --version >/dev/null 2>&1; then
                echo -e "${YELLOW}⚠️ pip not found. Installing pip...${NC}"
                $python_cmd -m ensurepip --upgrade 2>/dev/null || handle_error 1 "Failed to install pip" "Please install pip manually"
            fi
            
            # Verify pip installation
            local pip_version=$($python_cmd -m pip --version 2>/dev/null | cut -d' ' -f2)
            echo -e "${GREEN}✅ pip $pip_version found${NC}"
        else
            echo -e "${RED}❌ Python $python_version found, but version $required_version or higher is required${NC}"
            install_python
            
            # Re-verify after installation
            if command_exists python3; then
                PYTHON_CMD="python3"
                python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null)
                echo -e "${GREEN}✅ Python $python_version installed successfully${NC}"
            else
                handle_error 1 "Python installation verification failed" "Please install Python 3.8+ manually"
            fi
        fi
    else
        echo -e "${RED}❌ Python not found. Installing Python...${NC}"
        install_python
        
        # Verify installation
        if command_exists python3; then
            PYTHON_CMD="python3"
            python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null)
            echo -e "${GREEN}✅ Python $python_version installed successfully${NC}"
        else
            handle_error 1 "Python installation verification failed" "Please install Python 3.8+ manually"
        fi
    fi
}

# Function to install Chrome/Chromium for Selenium
install_chrome() {
    local os=$(detect_os)
    echo -e "${YELLOW}🌐 Installing Chrome/Chromium for web automation...${NC}"
    
    case $os in
        "linux")
            if command_exists apt-get; then
                echo -e "${CYAN}🔄 Installing Google Chrome via apt-get...${NC}"
                # Install Chrome
                if ! wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add - 2>/dev/null; then
                    echo -e "${YELLOW}⚠️ Failed to add Google signing key, trying alternative method...${NC}"
                    # Try installing chromium instead
                    sudo apt-get update || true
                    sudo apt-get install -y chromium-browser || sudo apt-get install -y chromium || echo -e "${YELLOW}⚠️ Could not install Chrome/Chromium automatically${NC}"
                else
                    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list >/dev/null
                    sudo apt-get update || handle_error 1 "Failed to update package lists" "Check your internet connection"
                    sudo apt-get install -y google-chrome-stable || {
                        echo -e "${YELLOW}⚠️ Chrome installation failed, trying Chromium...${NC}"
                        sudo apt-get install -y chromium-browser || sudo apt-get install -y chromium || echo -e "${YELLOW}⚠️ Could not install Chrome/Chromium automatically${NC}"
                    }
                fi
            elif command_exists yum; then
                echo -e "${CYAN}🔄 Installing Chromium via yum...${NC}"
                sudo yum install -y chromium || echo -e "${YELLOW}⚠️ Could not install Chromium automatically${NC}"
            elif command_exists dnf; then
                echo -e "${CYAN}🔄 Installing Chromium via dnf...${NC}"
                sudo dnf install -y chromium || echo -e "${YELLOW}⚠️ Could not install Chromium automatically${NC}"
            elif command_exists pacman; then
                echo -e "${CYAN}🔄 Installing Chromium via pacman...${NC}"
                sudo pacman -S --noconfirm chromium || echo -e "${YELLOW}⚠️ Could not install Chromium automatically${NC}"
            elif command_exists zypper; then
                echo -e "${CYAN}🔄 Installing Chromium via zypper...${NC}"
                sudo zypper install -y chromium || echo -e "${YELLOW}⚠️ Could not install Chromium automatically${NC}"
            else
                echo -e "${YELLOW}⚠️ Unsupported package manager. Please install Chrome or Chromium manually.${NC}"
            fi
            ;;
        "macos")
            if command_exists brew; then
                echo -e "${CYAN}🔄 Installing Google Chrome via Homebrew...${NC}"
                brew install --cask google-chrome || echo -e "${YELLOW}⚠️ Chrome installation failed. Please install manually from https://www.google.com/chrome/${NC}"
            else
                echo -e "${YELLOW}⚠️ Homebrew not found. Please install Chrome from https://www.google.com/chrome/${NC}"
            fi
            ;;
        "windows")
            echo -e "${YELLOW}⚠️ Please install Chrome from https://www.google.com/chrome/ for web automation features${NC}"
            ;;
        *)
            echo -e "${YELLOW}⚠️ Please install Chrome or Chromium manually for web automation features${NC}"
            ;;
    esac
    
    # Verify Chrome/Chromium installation
    if command_exists google-chrome || command_exists google-chrome-stable || command_exists chromium || command_exists chromium-browser || [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
        echo -e "${GREEN}✅ Chrome/Chromium installed successfully${NC}"
    else
        echo -e "${YELLOW}⚠️ Chrome/Chromium installation could not be verified. Web automation may not work properly.${NC}"
        echo -e "${CYAN}💡 You can install Chrome manually later from https://www.google.com/chrome/${NC}"
    fi
}

# Function to create virtual environment
create_venv() {
    echo -e "${YELLOW}🔧 Creating Python virtual environment...${NC}"
    
    if [ -d "venv" ]; then
        echo -e "${YELLOW}⚠️ Virtual environment already exists. Removing old one...${NC}"
        rm -rf venv || handle_error 1 "Failed to remove existing virtual environment" "Check permissions and try running with sudo"
    fi
    
    echo -e "${CYAN}🔄 Creating new virtual environment...${NC}"
    $PYTHON_CMD -m venv venv || handle_error 1 "Failed to create virtual environment" "Ensure Python venv module is installed: $PYTHON_CMD -m pip install --user virtualenv"
    
    # Activate virtual environment
    echo -e "${CYAN}🔄 Activating virtual environment...${NC}"
    if [[ "$(detect_os)" == "windows" ]]; then
        source venv/Scripts/activate || handle_error 1 "Failed to activate virtual environment" "Virtual environment may be corrupted. Try removing venv folder and running again"
    else
        source venv/bin/activate || handle_error 1 "Failed to activate virtual environment" "Virtual environment may be corrupted. Try removing venv folder and running again"
    fi
    
    # Verify activation
    if [ "$VIRTUAL_ENV" = "" ]; then
        handle_error 1 "Virtual environment activation failed" "Check if venv activation script exists and is executable"
    fi
    
    # Upgrade pip
    echo -e "${YELLOW}📦 Upgrading pip...${NC}"
    pip install --upgrade pip || handle_error 1 "Failed to upgrade pip" "Check your internet connection and try again"
    
    # Verify pip upgrade
    local pip_version=$(pip --version 2>/dev/null | cut -d' ' -f2)
    echo -e "${GREEN}✅ Virtual environment created and activated (pip $pip_version)${NC}"
}

# Function to install Python dependencies
install_dependencies() {
    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
    
    # Ensure we're in virtual environment
    if [ "$VIRTUAL_ENV" = "" ]; then
        echo -e "${CYAN}🔄 Activating virtual environment...${NC}"
        if [[ "$(detect_os)" == "windows" ]]; then
            source venv/Scripts/activate || handle_error 1 "Failed to activate virtual environment" "Virtual environment may be corrupted. Try removing venv folder and running again"
        else
            source venv/bin/activate || handle_error 1 "Failed to activate virtual environment" "Virtual environment may be corrupted. Try removing venv folder and running again"
        fi
    fi
    
    # Verify we're in the correct virtual environment
    local venv_python=$(which python)
    if [[ "$venv_python" != *"venv"* ]]; then
        handle_error 1 "Virtual environment not properly activated" "Try removing venv folder and running the installer again"
    fi
    
    # Install from requirements.txt if it exists
    if [ -f "requirements.txt" ]; then
        echo -e "${CYAN}📋 Installing from requirements.txt...${NC}"
        
        # Count total packages for progress indication
        local total_packages=$(grep -v '^#' requirements.txt | grep -v '^$' | wc -l | tr -d ' ')
        echo -e "${CYAN}📊 Installing $total_packages packages...${NC}"
        
        # Install with timeout and retry logic
        pip install --timeout 300 --retries 3 -r requirements.txt || {
            echo -e "${YELLOW}⚠️ Some packages failed to install. Trying individual installation...${NC}"
            
            # Try installing packages individually
            while IFS= read -r package; do
                # Skip comments and empty lines
                if [[ "$package" =~ ^#.*$ ]] || [[ -z "$package" ]]; then
                    continue
                fi
                
                echo -e "${CYAN}📦 Installing: $package${NC}"
                pip install "$package" || echo -e "${YELLOW}⚠️ Failed to install: $package${NC}"
            done < requirements.txt
        }
    else
        echo -e "${YELLOW}⚠️ requirements.txt not found. Installing essential packages...${NC}"
        
        # Install essential packages with error handling
        local essential_packages=("requests" "beautifulsoup4" "lxml" "selenium" "webdriver-manager" "openai" "google-generativeai" "pillow" "python-dotenv" "colorama" "tqdm" "validators")
        
        for package in "${essential_packages[@]}"; do
            echo -e "${CYAN}📦 Installing: $package${NC}"
            pip install "$package" || echo -e "${YELLOW}⚠️ Failed to install: $package${NC}"
        done
    fi
    
    # Verify critical packages are installed
    echo -e "${YELLOW}🔍 Verifying critical packages...${NC}"
    local critical_packages=("requests" "bs4" "selenium" "openai")
    local missing_packages=()
    
    for package in "${critical_packages[@]}"; do
        if ! python -c "import $package" 2>/dev/null; then
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠️ Some critical packages are missing: ${missing_packages[*]}${NC}"
        echo -e "${CYAN}💡 The application may still work, but some features might be limited${NC}"
    else
        echo -e "${GREEN}✅ All critical packages verified${NC}"
    fi
    
    # Show installed packages summary
    local installed_count=$(pip list | wc -l | tr -d ' ')
    echo -e "${GREEN}✅ Dependencies installation completed ($installed_count packages installed)${NC}"
}

# Function to create launcher script
create_launcher() {
    local install_dir=$(pwd)
    local os=$(detect_os)
    
    echo -e "${YELLOW}🚀 Creating launcher script with auto-update...${NC}"
    
    # Verify essential files exist
    if [ ! -f "gui_blogger.py" ]; then
        handle_error 1 "Main application file missing: gui_blogger.py" "Repository may be corrupted. Try removing $INSTALL_DIR and running again"
    fi
    
    # Create the autoblog launcher script
    echo -e "${CYAN}🔄 Creating shell launcher...${NC}"
    cat > autoblog << 'EOF'
#!/bin/bash

# AUTO-blogger Launcher Script with Auto-Update
# This script launches the auto-update launcher

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the installation directory
cd "$SCRIPT_DIR" || {
    echo -e "${RED}❌ Failed to access installation directory${NC}"
    exit 1
}

# Determine Python executable
if [ -f "venv/bin/python" ]; then
    PYTHON_EXE="venv/bin/python"
elif [ -f "venv/Scripts/python.exe" ]; then
    PYTHON_EXE="venv/Scripts/python.exe"
else
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo -e "${YELLOW}💡 Please run the installer again${NC}"
    exit 1
fi

# Check if main application exists
if [ ! -f "autoblog_launcher.py" ]; then
    echo -e "${RED}❌ Launcher application not found${NC}"
    echo -e "${YELLOW}💡 Please run the installer again${NC}"
    exit 1
fi

# Set application icon (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e 'tell application "System Events" to set the dock tile of application "Terminal" to "🤖"' 2>/dev/null || true
fi

echo -e "${CYAN}🚀 Starting AUTO-blogger with auto-update...${NC}"

# Launch the auto-update launcher
"$PYTHON_EXE" autoblog_launcher.py
EOF

    # Make the launcher executable
    chmod +x autoblog || handle_error 1 "Failed to make launcher executable" "Check file permissions"
    
    # Create system-wide launcher based on OS
    case $os in
        "linux" | "macos")
            # Create symlink in /usr/local/bin for system-wide access
            if [ -w "/usr/local/bin" ] || sudo -n true 2>/dev/null; then
                echo -e "${YELLOW}🔗 Creating system-wide launcher...${NC}"
                sudo ln -sf "$install_dir/autoblog" "/usr/local/bin/autoblog" 2>/dev/null && {
                    echo -e "${GREEN}✅ System-wide launcher created: autoblog${NC}"
                    echo -e "${CYAN}💡 You can now run 'autoblog' from anywhere in the terminal${NC}"
                } || {
                    echo -e "${YELLOW}⚠️ Could not create system-wide launcher. You can run './autoblog' from this directory.${NC}"
                }
            else
                echo -e "${YELLOW}⚠️ No sudo access. You can run './autoblog' from this directory.${NC}"
            fi
            ;;
        "windows")
            # For Windows, create a batch file
            echo -e "${CYAN}🔄 Creating Windows batch launcher...${NC}"
            cat > "autoblog.bat" << 'EOF'
@echo off
setlocal

REM AUTO-blogger Windows Launcher
echo 🚀 Starting AUTO-blogger...

REM Change to script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found
    echo 💡 Please run the installer again
    pause
    exit /b 1
)

REM Check if launcher exists
if not exist "autoblog_launcher.py" (
    echo ❌ Launcher application not found
    echo 💡 Please run the installer again
    pause
    exit /b 1
)

echo Starting AUTO-blogger with auto-update...
venv\Scripts\python.exe autoblog_launcher.py
if errorlevel 1 (
    echo ⚠️ Application exited with errors
    pause
)
EOF
            echo -e "${GREEN}✅ Windows launcher created: autoblog.bat${NC}"
            ;;
    esac
    
    echo -e "${GREEN}✅ Launcher with auto-update created successfully${NC}"
}

# Function to create desktop shortcut
create_desktop_shortcut() {
    local install_dir=$(pwd)
    local os=$(detect_os)
    
    case $os in
        "linux")
            local desktop_dir="$HOME/Desktop"
            if [ -d "$desktop_dir" ]; then
                echo -e "${YELLOW}🖥️ Creating desktop shortcut...${NC}"
                cat > "$desktop_dir/AUTO-blogger.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=AUTO-blogger
Comment=Automated WordPress Blog Posting Tool
Exec=$install_dir/autoblog
Icon=$install_dir/icon.png
Terminal=false
Categories=Development;Office;
EOF
                chmod +x "$desktop_dir/AUTO-blogger.desktop"
                echo -e "${GREEN}✅ Desktop shortcut created${NC}"
            fi
            ;;
        "macos")
            echo -e "${YELLOW}🖥️ Creating macOS application...${NC}"
            local app_dir="/Applications/AUTO-blogger.app"
            sudo mkdir -p "$app_dir/Contents/MacOS"
            sudo mkdir -p "$app_dir/Contents/Resources"
            
            # Create Info.plist
            sudo cat > "$app_dir/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>autoblog</string>
    <key>CFBundleIdentifier</key>
    <string>com.aryanbw.autoblogger</string>
    <key>CFBundleName</key>
    <string>AUTO-blogger</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
</dict>
</plist>
EOF
            
            # Create launcher script
            sudo cat > "$app_dir/Contents/MacOS/autoblog" << EOF
#!/bin/bash
cd "$install_dir"
./autoblog
EOF
            sudo chmod +x "$app_dir/Contents/MacOS/autoblog"
            
            # Copy icon if exists
            if [ -f "icon.png" ]; then
                sudo cp "icon.png" "$app_dir/Contents/Resources/"
            fi
            
            echo -e "${GREEN}✅ macOS application created in /Applications${NC}"
            ;;
    esac
}

# Function to test installation
test_installation() {
    echo -e "${YELLOW}🧪 Testing installation...${NC}"
    
    # Activate virtual environment
    echo -e "${CYAN}🔄 Activating virtual environment for testing...${NC}"
    if [[ "$(detect_os)" == "windows" ]]; then
        source venv/Scripts/activate || handle_error 1 "Failed to activate virtual environment for testing" "Virtual environment may be corrupted"
    else
        source venv/bin/activate || handle_error 1 "Failed to activate virtual environment for testing" "Virtual environment may be corrupted"
    fi
    
    # Test critical Python imports
    echo -e "${CYAN}🔍 Testing critical package imports...${NC}"
    local test_packages=("requests" "bs4" "selenium" "openai")
    local failed_packages=()
    
    for package in "${test_packages[@]}"; do
        echo -e "${CYAN}  Testing: $package${NC}"
        if python -c "import $package" 2>/dev/null; then
            echo -e "${GREEN}    ✅ $package - OK${NC}"
        else
            echo -e "${YELLOW}    ⚠️ $package - Failed${NC}"
            failed_packages+=("$package")
        fi
    done
    
    # Test main application file
    echo -e "${CYAN}🔍 Testing main application...${NC}"
    if [ -f "gui_blogger.py" ]; then
        # Try to run a basic syntax check
        if python -m py_compile gui_blogger.py 2>/dev/null; then
            echo -e "${GREEN}✅ Main application syntax - OK${NC}"
        else
            echo -e "${YELLOW}⚠️ Main application syntax check failed${NC}"
        fi
    else
        echo -e "${RED}❌ Main application file missing${NC}"
        failed_packages+=("gui_blogger.py")
    fi
    
    # Test launcher
    echo -e "${CYAN}🔍 Testing launcher script...${NC}"
    if [ -f "autoblog_launcher.py" ]; then
        if python -m py_compile autoblog_launcher.py 2>/dev/null; then
            echo -e "${GREEN}✅ Launcher script syntax - OK${NC}"
        else
            echo -e "${YELLOW}⚠️ Launcher script syntax check failed${NC}"
        fi
    else
        echo -e "${RED}❌ Launcher script missing${NC}"
        failed_packages+=("autoblog_launcher.py")
    fi
    
    # Summary
    if [ ${#failed_packages[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed successfully!${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ Some tests failed: ${failed_packages[*]}${NC}"
        echo -e "${CYAN}💡 The application may still work, but some features might be limited${NC}"
        return 1
    fi
}

# Function to print logo
print_logo() {
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
}

# Function to show completion message
show_completion() {
    local test_result=$1
    
    echo ""
    echo -e "${GREEN}🎉 AUTO-blogger installation completed!${NC}"
    echo -e "${CYAN}📍 Installation directory: $INSTALL_DIR${NC}"
    
    if [ "$test_result" -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed - Installation is fully functional${NC}"
    else
        echo -e "${YELLOW}⚠️ Installation completed with some warnings${NC}"
        echo -e "${CYAN}💡 Check the test results above for details${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}🚀 How to use AUTO-blogger:${NC}"
    
    local os=$(detect_os)
    case $os in
        "linux" | "macos")
            if [ -f "/usr/local/bin/autoblog" ]; then
                echo -e "${CYAN}   • System-wide: Run 'autoblog' from anywhere in terminal${NC}"
            fi
            echo -e "${CYAN}   • Local: Run './autoblog' from installation directory${NC}"
            echo -e "${CYAN}   • Python: Run 'python autoblog_launcher.py' from installation directory${NC}"
            ;;
        "windows")
            echo -e "${CYAN}   • Double-click: autoblog.bat in installation directory${NC}"
            echo -e "${CYAN}   • Command line: Run 'autoblog.bat' from installation directory${NC}"
            echo -e "${CYAN}   • Python: Run 'python autoblog_launcher.py' from installation directory${NC}"
            ;;
    esac
    
    echo ""
    echo -e "${YELLOW}📁 Important Files:${NC}"
    echo -e "${CYAN}   • Main Application: gui_blogger.py${NC}"
    echo -e "${CYAN}   • Configuration: configs/ directory${NC}"
    echo -e "${CYAN}   • Logs: Check the application for log locations${NC}"
    
    echo ""
    echo -e "${YELLOW}📚 Documentation:${NC}"
    echo -e "${CYAN}   • README: $INSTALL_DIR/README.md${NC}"
    echo -e "${CYAN}   • Installation Guide: $INSTALL_DIR/docs/README_INSTALLATION.md${NC}"
    echo -e "${CYAN}   • Troubleshooting: $INSTALL_DIR/docs/wordpress_seo_troubleshooting.md${NC}"
    
    echo ""
    echo -e "${YELLOW}🔧 First Time Setup:${NC}"
    echo -e "${CYAN}   1. Launch the application using one of the methods above${NC}"
    echo -e "${CYAN}   2. Configure your API keys (WordPress, OpenAI, Gemini)${NC}"
    echo -e "${CYAN}   3. Set up your automation preferences${NC}"
    echo -e "${CYAN}   4. Start generating content!${NC}"
    
    echo ""
    echo -e "${YELLOW}🆘 Support:${NC}"
    echo -e "${CYAN}   • Email: AryanVBW@gmail.com${NC}"
    echo -e "${CYAN}   • Issues: https://github.com/AryanVBW/AUTO-blogger/issues${NC}"
    echo -e "${CYAN}   • Documentation: Check the docs/ folder for guides${NC}"
    
    echo ""
    if [ "$test_result" -eq 0 ]; then
        echo -e "${GREEN}🚀 Ready to start blogging! Happy writing! 📝✨${NC}"
    else
        echo -e "${YELLOW}⚠️ Installation completed with warnings. Please check the issues above.${NC}"
        echo -e "${CYAN}💡 You can still try running the application - it may work despite the warnings.${NC}"
    fi
    echo ""
}

# Main installation function
main() {
    # Handle Ctrl+C gracefully
    trap 'echo -e "\n${RED}❌ Installation interrupted by user${NC}"; echo -e "${CYAN}💡 You can run this installer again to complete the setup${NC}"; exit 1' INT
    
    # Start installation
    print_logo
    
    echo -e "${CYAN}🚀 Starting AUTO-blogger installation...${NC}"
    echo -e "${CYAN}📅 $(date)${NC}"
    echo ""
    
    # Step 1: System verification
    echo -e "${YELLOW}📋 Step 1/10: System Verification${NC}"
    verify_requirements
    echo ""
    
    # Step 2: Check existing installation
    echo -e "${YELLOW}📋 Step 2/10: Installation Check${NC}"
    check_existing_installation
    echo ""
    
    # Step 3: Git setup
    echo -e "${YELLOW}📋 Step 3/10: Git Setup${NC}"
    check_git
    echo ""
    
    # Step 4: Repository setup
    echo -e "${YELLOW}📋 Step 4/10: Repository Setup${NC}"
    clone_or_update_repo
    echo ""
    
    # Step 5: Python setup
    echo -e "${YELLOW}📋 Step 5/10: Python Setup${NC}"
    check_python
    echo ""
    
    # Step 6: Browser setup
    echo -e "${YELLOW}📋 Step 6/10: Browser Setup${NC}"
    install_chrome
    echo ""
    
    # Step 7: Virtual environment
    echo -e "${YELLOW}📋 Step 7/10: Virtual Environment${NC}"
    create_venv
    echo ""
    
    # Step 8: Dependencies
    echo -e "${YELLOW}📋 Step 8/10: Dependencies Installation${NC}"
    install_dependencies
    echo ""
    
    # Step 9: Launcher creation
     echo -e "${YELLOW}📋 Step 9/10: Launcher Creation${NC}"
     create_launchers
     create_desktop_shortcut
     echo ""
     
     # Step 10: Testing and completion
     echo -e "${YELLOW}📋 Step 10/10: Testing Installation${NC}"
    test_installation
    local test_result=$?
    echo ""
    
    # Show completion message
    show_completion $test_result
    
    # Final status
    if [ $test_result -eq 0 ]; then
        echo -e "${GREEN}🎯 Installation completed successfully!${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️ Installation completed with warnings${NC}"
        exit 2
    fi
}

# Handle script interruption
trap 'echo -e "\n${RED}❌ Installation interrupted by user${NC}"; exit 1' INT

# Run main function
main "$@"