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
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║              AUTO-blogger Installation Script             ║"
echo "║                                                           ║"
echo "║                 Copyright © 2025 AryanVBW                 ║"
echo "║           GitHub: https://github.com/AryanVBW            ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Define installation directory
INSTALL_DIR="$HOME/AUTO-blogger"
VENV_NAME="auto_blogger_venv"
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
      if command -v brew &> /dev/null; then
        echo -e "${YELLOW}Installing Python 3 using Homebrew...${NC}"
        brew install python
      else
        echo -e "${RED}Homebrew not found. Installing Homebrew...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        brew install python
      fi
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
      echo -e "${YELLOW}Installing pip...${NC}"
      curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
      python3 get-pip.py
      rm get-pip.py
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
      if command -v brew &> /dev/null; then
        echo -e "${YELLOW}Installing Git using Homebrew...${NC}"
        brew install git
      else
        echo -e "${RED}Homebrew not found. Please install Git manually.${NC}"
        exit 1
      fi
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
  
  # Create virtual environment
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
    else
      CONFIG_FILE="$HOME/.bashrc"
    fi
    
    # Check if alias already exists and remove it
    sed -i.bak '/alias autoV=/d' "$CONFIG_FILE" 2>/dev/null || true
    
    # Add alias to shell configuration
    echo "alias autoV='bash $INSTALL_DIR/autoV.sh'" >> "$CONFIG_FILE"
    
    echo -e "${GREEN}Alias 'autoV' created successfully.${NC}"
    echo -e "${YELLOW}Please run 'source $CONFIG_FILE' or restart your terminal to use the command.${NC}"
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

# Set file permissions
set_permissions() {
  echo -e "${YELLOW}Setting file permissions...${NC}"
  
  chmod +x "$INSTALL_DIR/launch_blogger.py"
  chmod +x "$INSTALL_DIR/start_blogger.sh"
  
  echo -e "${GREEN}Permissions set.${NC}"
}

# Run all installation steps
run_installation() {
  detect_os
  check_python
  check_git
  clone_repository
  setup_virtualenv
  create_command_alias
  set_permissions
  
  echo -e "${GREEN}Installation complete!${NC}"
  echo -e "${BLUE}=================================${NC}"
  echo -e "${GREEN}AUTO-blogger has been installed successfully.${NC}"
  echo -e "${YELLOW}To start AUTO-blogger, type 'autoV' in your terminal.${NC}"
  echo -e "${YELLOW}For Windows users, run '$INSTALL_DIR/autoV.bat'${NC}"
  echo -e "${BLUE}=================================${NC}"
}

# Execute the installation
run_installation 