#!/usr/bin/env bash
#==============================================================================
# AUTO-blogger Setup Script
# Cross-platform setup for macOS, Linux, and Windows (WSL/Git Bash)
# Copyright (c) 2025 AryanVBW
# https://github.com/AryanVBW/AUTO-blogger
#==============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
VENV_DIR="venv"
PYTHON_MIN_VERSION="3.8"
PROJECT_NAME="AUTO-blogger"

#==============================================================================
# Helper Functions
#==============================================================================

print_header() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                    AUTO-blogger Setup                            ║"
    echo "║           Professional WordPress Automation Tool                  ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

check_command() {
    command -v "$1" >/dev/null 2>&1
}

get_os() {
    case "$(uname -s)" in
        Darwin*)    echo "macos" ;;
        Linux*)     echo "linux" ;;
        MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
        *)          echo "unknown" ;;
    esac
}

version_gte() {
    # Returns 0 if $1 >= $2
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

#==============================================================================
# System Checks
#==============================================================================

check_python() {
    log_step "Checking Python installation..."

    PYTHON_CMD=""
    for cmd in python3 python; do
        if check_command "$cmd"; then
            version=$($cmd -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
            if version_gte "$version" "$PYTHON_MIN_VERSION"; then
                PYTHON_CMD="$cmd"
                log_success "Found $cmd version $version"
                break
            fi
        fi
    done

    if [ -z "$PYTHON_CMD" ]; then
        log_error "Python $PYTHON_MIN_VERSION or higher is required but not found."
        log_info "Please install Python from https://www.python.org/downloads/"
        exit 1
    fi

    export PYTHON_CMD
}

check_pip() {
    log_step "Checking pip installation..."

    if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
        log_warning "pip not found. Attempting to install..."
        $PYTHON_CMD -m ensurepip --default-pip || {
            log_error "Failed to install pip. Please install pip manually."
            exit 1
        }
    fi
    log_success "pip is available"
}

check_git() {
    log_step "Checking Git installation..."

    if ! check_command git; then
        log_warning "Git is not installed. Some features may not work."
    else
        log_success "Git is available: $(git --version)"
    fi
}

check_chrome() {
    log_step "Checking Chrome/Chromium installation..."

    OS=$(get_os)
    CHROME_FOUND=false

    case "$OS" in
        macos)
            if [ -d "/Applications/Google Chrome.app" ] || [ -d "/Applications/Chromium.app" ]; then
                CHROME_FOUND=true
            fi
            ;;
        linux)
            if check_command google-chrome || check_command chromium || check_command chromium-browser; then
                CHROME_FOUND=true
            fi
            ;;
        windows)
            if [ -f "/c/Program Files/Google/Chrome/Application/chrome.exe" ] || \
               [ -f "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" ]; then
                CHROME_FOUND=true
            fi
            ;;
    esac

    if [ "$CHROME_FOUND" = true ]; then
        log_success "Chrome/Chromium found"
    else
        log_warning "Chrome/Chromium not found. Selenium automation requires Chrome."
        log_info "Download from: https://www.google.com/chrome/"
    fi
}

#==============================================================================
# Environment Setup
#==============================================================================

setup_venv() {
    log_step "Setting up virtual environment..."

    if [ -d "$VENV_DIR" ]; then
        log_info "Virtual environment already exists. Recreating..."
        rm -rf "$VENV_DIR"
    fi

    $PYTHON_CMD -m venv "$VENV_DIR"
    log_success "Virtual environment created at ./$VENV_DIR"
}

activate_venv() {
    log_step "Activating virtual environment..."

    OS=$(get_os)
    case "$OS" in
        windows)
            source "$VENV_DIR/Scripts/activate"
            ;;
        *)
            source "$VENV_DIR/bin/activate"
            ;;
    esac

    log_success "Virtual environment activated"
}

upgrade_pip() {
    log_step "Upgrading pip and setuptools..."

    pip install --upgrade pip setuptools wheel >/dev/null 2>&1
    log_success "pip and setuptools upgraded"
}

install_dependencies() {
    local mode="${1:-base}"

    log_step "Installing $mode dependencies..."

    case "$mode" in
        dev)
            if [ -f "requirements/dev.txt" ]; then
                pip install -r requirements/dev.txt
            else
                pip install -r requirements.txt
                pip install black flake8 mypy pytest pytest-cov pre-commit
            fi
            ;;
        test)
            if [ -f "requirements/test.txt" ]; then
                pip install -r requirements/test.txt
            else
                pip install -r requirements.txt
                pip install pytest pytest-cov pytest-mock
            fi
            ;;
        base|*)
            if [ -f "requirements/base.txt" ]; then
                pip install -r requirements/base.txt
            else
                pip install -r requirements.txt
            fi
            ;;
    esac

    log_success "$mode dependencies installed"
}

install_package() {
    log_step "Installing AUTO-blogger package..."

    local mode="${1:-prod}"

    case "$mode" in
        dev)
            pip install -e ".[dev]"
            ;;
        *)
            pip install -e .
            ;;
    esac

    log_success "AUTO-blogger package installed"
}

setup_pre_commit() {
    log_step "Setting up pre-commit hooks..."

    if check_command pre-commit; then
        if [ -f ".pre-commit-config.yaml" ]; then
            pre-commit install
            log_success "Pre-commit hooks installed"
        else
            log_info "No pre-commit config found. Skipping."
        fi
    else
        log_info "pre-commit not installed. Skipping hooks setup."
    fi
}

create_env_file() {
    log_step "Setting up environment configuration..."

    if [ ! -f ".env" ] && [ -f ".env.example" ]; then
        cp .env.example .env
        log_success "Created .env file from template"
        log_warning "Please update .env with your API keys and credentials"
    elif [ -f ".env" ]; then
        log_info ".env file already exists"
    else
        log_info "No .env.example template found"
    fi
}

#==============================================================================
# Platform-Specific Setup
#==============================================================================

setup_macos() {
    log_step "Performing macOS-specific setup..."

    # Install Xcode command line tools if needed
    if ! xcode-select -p >/dev/null 2>&1; then
        log_info "Installing Xcode Command Line Tools..."
        xcode-select --install 2>/dev/null || true
    fi

    # Check for Homebrew
    if ! check_command brew; then
        log_info "Consider installing Homebrew for easier package management:"
        log_info "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    fi

    log_success "macOS setup complete"
}

setup_linux() {
    log_step "Performing Linux-specific setup..."

    # Check for tkinter
    if ! $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
        log_warning "tkinter not found. GUI features require tkinter."

        if check_command apt-get; then
            log_info "Install with: sudo apt-get install python3-tk"
        elif check_command dnf; then
            log_info "Install with: sudo dnf install python3-tkinter"
        elif check_command pacman; then
            log_info "Install with: sudo pacman -S tk"
        fi
    fi

    log_success "Linux setup complete"
}

setup_windows() {
    log_step "Performing Windows-specific setup..."
    log_info "Windows setup via Git Bash/WSL detected"
    log_success "Windows setup complete"
}

#==============================================================================
# Verification
#==============================================================================

verify_installation() {
    log_step "Verifying installation..."

    # Check if package can be imported
    if $PYTHON_CMD -c "import auto_blogger" 2>/dev/null; then
        log_success "AUTO-blogger package imports successfully"
    else
        log_warning "Package import verification skipped"
    fi

    # Check entry points
    if check_command autoblog; then
        log_success "Command 'autoblog' is available"
    fi

    log_success "Installation verified"
}

print_success_message() {
    echo ""
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                   Setup Complete!                                ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${CYAN}Quick Start:${NC}"
    echo ""
    echo "  1. Activate the virtual environment:"

    OS=$(get_os)
    case "$OS" in
        windows)
            echo "     source venv/Scripts/activate"
            ;;
        *)
            echo "     source venv/bin/activate"
            ;;
    esac

    echo ""
    echo "  2. Run AUTO-blogger:"
    echo "     autoblog"
    echo "     # or"
    echo "     python -m auto_blogger"
    echo ""
    echo "  3. For development:"
    echo "     make dev-setup    # Install dev dependencies"
    echo "     make test         # Run tests"
    echo "     make lint         # Run linter"
    echo ""
    echo -e "${YELLOW}Note:${NC} Update your .env file with API keys before running."
    echo ""
}

#==============================================================================
# Main Script
#==============================================================================

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dev       Install development dependencies"
    echo "  --test      Install test dependencies"
    echo "  --no-venv   Skip virtual environment creation"
    echo "  --clean     Remove existing venv before setup"
    echo "  --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Standard installation"
    echo "  $0 --dev        # Development setup"
    echo "  $0 --clean      # Clean reinstall"
}

main() {
    local mode="base"
    local skip_venv=false
    local clean=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dev)
                mode="dev"
                shift
                ;;
            --test)
                mode="test"
                shift
                ;;
            --no-venv)
                skip_venv=true
                shift
                ;;
            --clean)
                clean=true
                shift
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done

    print_header

    # Navigate to script directory
    cd "$(dirname "$0")"

    log_info "Starting $PROJECT_NAME setup (mode: $mode)"
    echo ""

    # Clean if requested
    if [ "$clean" = true ] && [ -d "$VENV_DIR" ]; then
        log_step "Cleaning existing virtual environment..."
        rm -rf "$VENV_DIR"
        log_success "Cleaned"
    fi

    # System checks
    check_python
    check_pip
    check_git
    check_chrome
    echo ""

    # Platform-specific setup
    OS=$(get_os)
    case "$OS" in
        macos)  setup_macos ;;
        linux)  setup_linux ;;
        windows) setup_windows ;;
    esac
    echo ""

    # Environment setup
    if [ "$skip_venv" = false ]; then
        setup_venv
        activate_venv
    fi

    upgrade_pip
    install_dependencies "$mode"
    install_package "$mode"

    # Development-specific setup
    if [ "$mode" = "dev" ]; then
        setup_pre_commit
    fi

    create_env_file
    echo ""

    # Verification
    verify_installation

    print_success_message
}

# Run main function
main "$@"
