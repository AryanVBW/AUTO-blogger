#!/usr/bin/env bash
#==============================================================================
# AUTO-blogger Run Script
# Copyright (c) 2025 AryanVBW
#==============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
VENV_DIR="venv"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

#==============================================================================
# Helper Functions
#==============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

get_os() {
    case "$(uname -s)" in
        Darwin*)    echo "macos" ;;
        Linux*)     echo "linux" ;;
        MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
        *)          echo "unknown" ;;
    esac
}

activate_venv() {
    local OS=$(get_os)

    if [ ! -d "$VENV_DIR" ]; then
        log_error "Virtual environment not found. Run setup.sh first."
        log_info "  ./setup.sh"
        exit 1
    fi

    case "$OS" in
        windows)
            source "$VENV_DIR/Scripts/activate"
            ;;
        *)
            source "$VENV_DIR/bin/activate"
            ;;
    esac
}

show_help() {
    echo ""
    echo "AUTO-blogger Run Script"
    echo "========================"
    echo ""
    echo "Usage: ./run.sh [OPTIONS] [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  gui         Run the GUI application (default)"
    echo "  cli         Run command-line interface"
    echo "  test        Run tests"
    echo "  shell       Start Python shell with package loaded"
    echo ""
    echo "Options:"
    echo "  --no-venv   Run without activating virtual environment"
    echo "  --debug     Run with debug logging"
    echo "  --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run.sh              # Run GUI"
    echo "  ./run.sh gui          # Run GUI"
    echo "  ./run.sh cli          # Run CLI"
    echo "  ./run.sh --debug gui  # Run GUI with debug"
    echo ""
}

#==============================================================================
# Main
#==============================================================================

main() {
    cd "$SCRIPT_DIR"

    local command="gui"
    local use_venv=true
    local debug=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-venv)
                use_venv=false
                shift
                ;;
            --debug)
                debug=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            gui|cli|test|shell)
                command="$1"
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Activate virtual environment if needed
    if [ "$use_venv" = true ]; then
        if [ -d "$VENV_DIR" ]; then
            activate_venv
        else
            log_info "No virtual environment found. Using system Python."
        fi
    fi

    # Set debug mode
    if [ "$debug" = true ]; then
        export AUTO_BLOGGER_DEBUG=1
        export PYTHONVERBOSE=1
        log_info "Debug mode enabled"
    fi

    # Execute command
    case $command in
        gui)
            log_info "Starting AUTO-blogger GUI..."
            python -m auto_blogger.gui_blogger "$@"
            ;;
        cli)
            log_info "Starting AUTO-blogger CLI..."
            if command -v autoblog &> /dev/null; then
                autoblog "$@"
            else
                python -m auto_blogger "$@"
            fi
            ;;
        test)
            log_info "Running tests..."
            pytest tests/ -v "$@"
            ;;
        shell)
            log_info "Starting Python shell..."
            python -c "
import auto_blogger
from auto_blogger import automation_engine, gui_blogger
print('AUTO-blogger loaded. Available modules:')
print('  - auto_blogger')
print('  - automation_engine')
print('  - gui_blogger')
" && python -i -c "from auto_blogger import *"
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
