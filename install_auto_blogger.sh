#!/bin/bash

# AUTO-blogger Installation Script
# This script detects OS, installs requirements, sets up virtual environment,
# and creates a command alias for easy access.
# 
# Copyright © 2025 AryanVBW
# GitHub: https://github.com/AryanVBW

set -e

# Define colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
#!/bin/bash

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


# Define installation directory
INSTALL_DIR="$HOME/AUTO-blogger"
# Generate unique virtual environment name to avoid conflicts
VENV_NAME="auto_blogger_venv_$(openssl rand -hex 4 2>/dev/null || date +%s | tail -c 8)"
REPO_URL="https://github.com/AryanVBW/AUTO-blogger.git"

# Detect operating system
detect_os() {
  echo -e "${YELLOW}Detecting operating system...${NC}"
  
  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo -e "${GREEN}Linux detected.${NC}"
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo -e "${GREEN}macOS detected.${NC}"
  elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
    echo -e "${GREEN}Windows detected.${NC}"
  else
    OS="unknown"
    echo -e "${YELLOW}Unknown OS detected. Will attempt installation anyway.${NC}"
  fi
}

# Check and install Homebrew on macOS
install_homebrew() {
  echo -e "${YELLOW}Checking Homebrew installation...${NC}"
  
  if ! command -v brew &> /dev/null; then
    echo -e "${YELLOW}Installing Homebrew...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for the current session
    if [[ "$(uname -m)" == "arm64" ]]; then
      # For Apple Silicon Macs
      eval "$(/opt/homebrew/bin/brew shellenv)"
    else
      # For Intel Macs
      eval "$(/usr/local/bin/brew shellenv)"
    fi
    
    echo -e "${GREEN}Homebrew installed successfully.${NC}"
  else
    echo -e "${GREEN}Homebrew is already installed.${NC}"
  fi
}

# Check if Python is installed and install if not
check_python() {
  echo -e "${YELLOW}Checking Python installation...${NC}"
  
  if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed.${NC}"
    
    if [[ "$OS" == "linux" ]]; then
      echo -e "${YELLOW}Installing Python 3...${NC}"
      if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv
      elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3 python3-pip
      elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip
      else
        echo -e "${RED}Could not install Python. Please install Python 3 manually.${NC}"
        exit 1
      fi
    elif [[ "$OS" == "macos" ]]; then
      # Install Homebrew first if needed
      install_homebrew
      # Then use Homebrew to install Python
      echo -e "${YELLOW}Installing Python 3 using Homebrew...${NC}"
      brew install python
    elif [[ "$OS" == "windows" ]]; then
      echo -e "${RED}Please install Python 3 manually from https://www.python.org/downloads/${NC}"
      exit 1
    fi
  else
    echo -e "${GREEN}Python 3 is already installed.${NC}"
  fi
  
  # Check Python version
  PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
  echo -e "${GREEN}Python version: $PYTHON_VERSION${NC}"
  
  # Check if pip is installed
  if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}pip is not installed.${NC}"
    if [[ "$OS" == "linux" ]]; then
      echo -e "${YELLOW}Installing pip...${NC}"
      if command -v apt &> /dev/null; then
        sudo apt install -y python3-pip
      elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3-pip
      elif command -v yum &> /dev/null; then
        sudo yum install -y python3-pip
      else
        echo -e "${RED}Could not install pip. Please install pip manually.${NC}"
        exit 1
      fi
    elif [[ "$OS" == "macos" ]]; then
      echo -e "${YELLOW}Setting up pip...${NC}"
      # Install Homebrew first if needed
      install_homebrew
      
      # Check if Python is installed via Homebrew, which should include pip
      if brew list python &>/dev/null; then
        echo -e "${GREEN}Using Homebrew's Python pip...${NC}"
        # pip should already be installed with Homebrew Python
      else
        echo -e "${YELLOW}Installing Python via Homebrew which includes pip...${NC}"
        brew install python
      fi
    fi
  else
    echo -e "${GREEN}pip is already installed.${NC}"
  fi
}

# Check if Git is installed and install if not
check_git() {
  echo -e "${YELLOW}Checking Git installation...${NC}"
  
  if ! command -v git &> /dev/null; then
    echo -e "${RED}Git is not installed.${NC}"
    
    if [[ "$OS" == "linux" ]]; then
      echo -e "${YELLOW}Installing Git...${NC}"
      if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y git
      elif command -v dnf &> /dev/null; then
        sudo dnf install -y git
      elif command -v yum &> /dev/null; then
        sudo yum install -y git
      else
        echo -e "${RED}Could not install Git. Please install Git manually.${NC}"
        exit 1
      fi
    elif [[ "$OS" == "macos" ]]; then
      # Install Homebrew first if needed
      install_homebrew
      
      echo -e "${YELLOW}Installing Git using Homebrew...${NC}"
      brew install git
    elif [[ "$OS" == "windows" ]]; then
      echo -e "${RED}Please install Git manually from https://git-scm.com/download/win${NC}"
      exit 1
    fi
  else
    echo -e "${GREEN}Git is already installed.${NC}"
  fi
}

# Clone the repository
clone_repository() {
  echo -e "${YELLOW}Cloning AUTO-blogger repository...${NC}"
  
  # Remove existing installation if it exists
  if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Existing installation found. Removing...${NC}"
    rm -rf "$INSTALL_DIR"
  fi
  
  # Clone the repository
  git clone "$REPO_URL" "$INSTALL_DIR"
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}Repository cloned successfully.${NC}"
  else
    echo -e "${RED}Failed to clone repository.${NC}"
    exit 1
  fi
}

# Set up virtual environment
setup_virtualenv() {
  echo -e "${YELLOW}Setting up virtual environment...${NC}"
  
  cd "$INSTALL_DIR"
  
  # Create virtual environment with unique name
  echo -e "${BLUE}Creating virtual environment: $VENV_NAME${NC}"
  python3 -m venv "$VENV_NAME"
  
  # Activate virtual environment and install requirements
  if [[ "$OS" == "windows" ]]; then
    source "$VENV_NAME/Scripts/activate"
  else
    source "$VENV_NAME/bin/activate"
  fi
  
  # Upgrade pip
  pip install --upgrade pip
  
  # Install requirements
  pip install -r requirements.txt
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}Requirements installed successfully.${NC}"
  else
    echo -e "${RED}Failed to install requirements.${NC}"
    exit 1
  fi
  
  # Deactivate virtual environment
  deactivate
}

# Create autoV command alias
create_command_alias() {
  echo -e "${YELLOW}Creating command alias...${NC}"
  
  # Create launch script
  cat > "$INSTALL_DIR/autoV.sh" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
source "$INSTALL_DIR/$VENV_NAME/bin/activate"
python3 "$INSTALL_DIR/launch_blogger.py"
deactivate
EOF

  chmod +x "$INSTALL_DIR/autoV.sh"
  
  # Create alias based on OS
  if [[ "$OS" == "linux" ]] || [[ "$OS" == "macos" ]]; then
    # Determine shell configuration file
    if [[ "$SHELL" == *"zsh"* ]]; then
      CONFIG_FILE="$HOME/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
      CONFIG_FILE="$HOME/.bashrc"
    elif [[ "$OS" == "macos" ]]; then
      # Default to zshrc on macOS since it's the default shell since Catalina
      CONFIG_FILE="$HOME/.zshrc"
      echo -e "${YELLOW}macOS detected. Using .zshrc as default shell config.${NC}"
    else
      # Default to bashrc if shell can't be determined
      CONFIG_FILE="$HOME/.bashrc"
      echo -e "${YELLOW}Could not determine shell type. Using .bashrc as default.${NC}"
    fi
    
    # Check if alias already exists and remove it
    if [[ -f "$CONFIG_FILE" ]]; then
      # macOS sed requires a backup extension, Linux sed can work without it
      if [[ "$OS" == "macos" ]]; then
        sed -i '' '/alias autoV=/d' "$CONFIG_FILE" 2>/dev/null || true
      else
        sed -i '/alias autoV=/d' "$CONFIG_FILE" 2>/dev/null || true
      fi
    fi
    
    # Add alias to shell configuration
    echo "alias autoV='bash $INSTALL_DIR/autoV.sh'" >> "$CONFIG_FILE"
    
    echo -e "${GREEN}Alias 'autoV' created successfully.${NC}"
    
    # Create standalone executable in appropriate bin directory (requires sudo)
    echo -e "${YELLOW}Creating system-wide command...${NC}"
    cat > /tmp/autov << EOF
#!/bin/bash
bash "$INSTALL_DIR/autoV.sh"
EOF
    
    chmod +x /tmp/autov
    echo -e "${YELLOW}You may be asked for your password to install the command system-wide.${NC}"
    
    # Use the appropriate bin directory for macOS
    if [[ "$OS" == "macos" ]]; then
      if [[ -d "/usr/local/bin" ]]; then
        BIN_DIR="/usr/local/bin"
      elif [[ -d "/opt/homebrew/bin" ]]; then
        # For Apple Silicon Macs where Homebrew might install to /opt
        BIN_DIR="/opt/homebrew/bin"
      else
        BIN_DIR="/usr/local/bin"
      fi
    else
      BIN_DIR="/usr/local/bin"
    fi
    
    sudo mv /tmp/autov "$BIN_DIR/autoV" 2>/dev/null || {
      echo -e "${YELLOW}Could not create system-wide command. You can still use the alias.${NC}"
    }
    
    # Source the configuration file to make alias available immediately
    if [[ -f "$CONFIG_FILE" ]]; then
      echo -e "${YELLOW}Activating alias in current shell...${NC}"
      source "$CONFIG_FILE" 2>/dev/null || {
        echo -e "${YELLOW}Could not source $CONFIG_FILE automatically.${NC}"
        echo -e "${YELLOW}Please run 'source $CONFIG_FILE' or restart your terminal to use the 'autoV' command.${NC}"
      }
    fi
  elif [[ "$OS" == "windows" ]]; then
    # Create batch file for Windows
    cat > "$INSTALL_DIR/autoV.bat" << EOF
@echo off
cd "$INSTALL_DIR"
call "$INSTALL_DIR\\$VENV_NAME\\Scripts\\activate.bat"
python "$INSTALL_DIR\\launch_blogger.py"
deactivate
EOF
    
    echo -e "${GREEN}Batch file created at '$INSTALL_DIR/autoV.bat'${NC}"
    echo -e "${YELLOW}To create a command alias in Windows, add the directory to your PATH or create a shortcut.${NC}"
  fi
}

# Set file permissions and organize project structure
set_permissions() {
  echo -e "${YELLOW}Setting file permissions and organizing project structure...${NC}"
  
  chmod +x "$INSTALL_DIR/launch_blogger.py"
  chmod +x "$INSTALL_DIR/start_blogger.sh"
  
  # Ensure docs and tests directories exist
  mkdir -p "$INSTALL_DIR/docs"
  mkdir -p "$INSTALL_DIR/tests"
  
  # Set permissions for scripts
  if [ -f "$INSTALL_DIR/autoblog" ]; then
    chmod +x "$INSTALL_DIR/autoblog"
  fi
  
  if [ -f "$INSTALL_DIR/fix_installation_issues.py" ]; then
    chmod +x "$INSTALL_DIR/fix_installation_issues.py"
  fi
  
  echo -e "${GREEN}Permissions set and project structure organized.${NC}"
}

# Post-installation fixes and optimizations
run_post_installation_fixes() {
  echo -e "${YELLOW}Running post-installation optimizations...${NC}"
  
  cd "$INSTALL_DIR"
  
  # Run the fix script if it exists
  if [ -f "fix_installation_issues.py" ]; then
    echo -e "${BLUE}Applying installation fixes and optimizations...${NC}"
    
    # Activate virtual environment
    if [[ "$OS" == "windows" ]]; then
      source "$VENV_NAME/Scripts/activate"
    else
      source "$VENV_NAME/bin/activate"
    fi
    
    python3 fix_installation_issues.py
    
    # Deactivate virtual environment
    deactivate
    
    echo -e "${GREEN}Post-installation fixes applied successfully.${NC}"
  else
    echo -e "${YELLOW}No post-installation fixes found. Skipping...${NC}"
  fi
}

# Run all installation steps
run_installation() {
  detect_os
  
  # Install Homebrew first if on macOS
  if [[ "$OS" == "macos" ]]; then
    install_homebrew
  fi
  
  check_python
  check_git
  clone_repository
  setup_virtualenv
  create_command_alias
  set_permissions
  run_post_installation_fixes
  
  echo -e "${GREEN}Installation complete!${NC}"
  echo -e "${BLUE}=================================${NC}"
  echo -e "${GREEN}AUTO-blogger has been installed successfully with enhanced features!${NC}"
  echo -e "${BLUE}✨ Features included:${NC}"
  echo -e "${GREEN}  • Enhanced SEO automation with improved error handling${NC}"
  echo -e "${GREEN}  • Organized project structure (docs/, tests/ directories)${NC}"
  echo -e "${GREEN}  • Unique virtual environment to avoid conflicts${NC}"
  echo -e "${GREEN}  • Comprehensive testing and validation tools${NC}"
  echo -e "${YELLOW}To start AUTO-blogger, type 'autoV' in your terminal.${NC}"
  
  # Provide immediate execution instructions
  if [[ "$OS" == "linux" ]] || [[ "$OS" == "macos" ]]; then
    echo -e "${YELLOW}If 'autoV' command is not working, you can run it directly with:${NC}"
    echo -e "${GREEN}bash $INSTALL_DIR/autoV.sh${NC}"
    
    if [[ "$OS" == "macos" ]]; then
      echo -e "${YELLOW}For macOS users: You may need to restart your terminal or run:${NC}"
      echo -e "${GREEN}source $CONFIG_FILE${NC}"
      echo -e "${YELLOW}To enable the autoV command.${NC}"
      
      # Check if terminal requires additional permissions
      if [[ -n "$TERM_PROGRAM" && "$TERM_PROGRAM" == "Apple_Terminal" ]]; then
        echo -e "${YELLOW}Note: If Terminal asks for disk access permissions, please allow it.${NC}"
      fi
    fi
  elif [[ "$OS" == "windows" ]]; then
    echo -e "${YELLOW}For Windows users, run '$INSTALL_DIR/autoV.bat'${NC}"
  fi
  
  echo -e "${BLUE}📁 Project Structure:${NC}"
  echo -e "${GREEN}  • docs/ - Documentation and guides${NC}"
  echo -e "${GREEN}  • tests/ - Testing and validation scripts${NC}"
  echo -e "${GREEN}  • $VENV_NAME/ - Isolated virtual environment${NC}"
  echo -e "${BLUE}🔧 Additional Tools:${NC}"
  echo -e "${GREEN}  • Run tests: python3 tests/test_seo_improvements.py${NC}"
  echo -e "${GREEN}  • Check documentation: ls docs/${NC}"
  echo -e "${BLUE}=================================${NC}"
}

# Execute the installation
run_installation