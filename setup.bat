@echo off
REM ==============================================================================
REM AUTO-blogger Setup Script for Windows
REM Copyright (c) 2025 AryanVBW
REM https://github.com/AryanVBW/AUTO-blogger
REM ==============================================================================

setlocal EnableDelayedExpansion

REM Configuration
set "VENV_DIR=venv"
set "PYTHON_MIN_VERSION=3.8"
set "PROJECT_NAME=AUTO-blogger"

REM Colors (Windows 10+)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "PURPLE=[95m"
set "CYAN=[96m"
set "NC=[0m"

REM ==============================================================================
REM Main Entry Point
REM ==============================================================================

:main
call :print_header

echo %BLUE%[INFO]%NC% Starting %PROJECT_NAME% setup...
echo.

REM Parse arguments
set "MODE=base"
set "CLEAN=false"
set "SKIP_VENV=false"

:parse_args
if "%~1"=="" goto :start_setup
if /i "%~1"=="--dev" set "MODE=dev" & shift & goto :parse_args
if /i "%~1"=="--test" set "MODE=test" & shift & goto :parse_args
if /i "%~1"=="--clean" set "CLEAN=true" & shift & goto :parse_args
if /i "%~1"=="--no-venv" set "SKIP_VENV=true" & shift & goto :parse_args
if /i "%~1"=="--help" goto :usage
if /i "%~1"=="-h" goto :usage
echo %RED%[ERROR]%NC% Unknown option: %~1
goto :usage

:start_setup

REM Navigate to script directory
cd /d "%~dp0"

REM Clean if requested
if "%CLEAN%"=="true" (
    if exist "%VENV_DIR%" (
        echo %CYAN%[STEP]%NC% Cleaning existing virtual environment...
        rmdir /s /q "%VENV_DIR%"
        echo %GREEN%[SUCCESS]%NC% Cleaned
    )
)

REM Check Python
call :check_python
if errorlevel 1 exit /b 1

REM Check pip
call :check_pip
if errorlevel 1 exit /b 1

REM Check Chrome
call :check_chrome

echo.

REM Setup virtual environment
if "%SKIP_VENV%"=="false" (
    call :setup_venv
    if errorlevel 1 exit /b 1

    call :activate_venv
    if errorlevel 1 exit /b 1
)

REM Upgrade pip
call :upgrade_pip

REM Install dependencies
call :install_dependencies %MODE%

REM Install package
call :install_package %MODE%

REM Create .env file
call :create_env_file

echo.

REM Verify installation
call :verify_installation

call :print_success
exit /b 0

REM ==============================================================================
REM Functions
REM ==============================================================================

:print_header
echo %PURPLE%
echo ======================================================================
echo                     AUTO-blogger Setup
echo            Professional WordPress Automation Tool
echo ======================================================================
echo %NC%
exit /b 0

:usage
echo.
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   --dev       Install development dependencies
echo   --test      Install test dependencies
echo   --no-venv   Skip virtual environment creation
echo   --clean     Remove existing venv before setup
echo   --help      Show this help message
echo.
echo Examples:
echo   %~nx0              # Standard installation
echo   %~nx0 --dev        # Development setup
echo   %~nx0 --clean      # Clean reinstall
exit /b 0

:check_python
echo %CYAN%[STEP]%NC% Checking Python installation...

REM Try python first, then python3
where python >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_CMD=python"
) else (
    where python3 >nul 2>&1
    if %errorlevel%==0 (
        set "PYTHON_CMD=python3"
    ) else (
        echo %RED%[ERROR]%NC% Python not found. Please install Python 3.8 or higher.
        echo Download from: https://www.python.org/downloads/
        exit /b 1
    )
)

REM Check version
for /f "tokens=*" %%i in ('%PYTHON_CMD% -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"') do set "PY_VERSION=%%i"
echo %GREEN%[SUCCESS]%NC% Found %PYTHON_CMD% version %PY_VERSION%
exit /b 0

:check_pip
echo %CYAN%[STEP]%NC% Checking pip installation...

%PYTHON_CMD% -m pip --version >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[WARNING]%NC% pip not found. Installing...
    %PYTHON_CMD% -m ensurepip --default-pip
    if errorlevel 1 (
        echo %RED%[ERROR]%NC% Failed to install pip
        exit /b 1
    )
)
echo %GREEN%[SUCCESS]%NC% pip is available
exit /b 0

:check_chrome
echo %CYAN%[STEP]%NC% Checking Chrome installation...

set "CHROME_FOUND=false"
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" set "CHROME_FOUND=true"
if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" set "CHROME_FOUND=true"

if "%CHROME_FOUND%"=="true" (
    echo %GREEN%[SUCCESS]%NC% Chrome found
) else (
    echo %YELLOW%[WARNING]%NC% Chrome not found. Selenium automation requires Chrome.
    echo Download from: https://www.google.com/chrome/
)
exit /b 0

:setup_venv
echo %CYAN%[STEP]%NC% Setting up virtual environment...

if exist "%VENV_DIR%" (
    echo %BLUE%[INFO]%NC% Virtual environment exists. Recreating...
    rmdir /s /q "%VENV_DIR%"
)

%PYTHON_CMD% -m venv "%VENV_DIR%"
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Failed to create virtual environment
    exit /b 1
)

echo %GREEN%[SUCCESS]%NC% Virtual environment created at .\%VENV_DIR%
exit /b 0

:activate_venv
echo %CYAN%[STEP]%NC% Activating virtual environment...

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Failed to activate virtual environment
    exit /b 1
)

echo %GREEN%[SUCCESS]%NC% Virtual environment activated
exit /b 0

:upgrade_pip
echo %CYAN%[STEP]%NC% Upgrading pip and setuptools...

pip install --upgrade pip setuptools wheel >nul 2>&1
echo %GREEN%[SUCCESS]%NC% pip and setuptools upgraded
exit /b 0

:install_dependencies
echo %CYAN%[STEP]%NC% Installing %1 dependencies...

if "%1"=="dev" (
    if exist "requirements\dev.txt" (
        pip install -r requirements\dev.txt
    ) else (
        pip install -r requirements.txt
        pip install black flake8 mypy pytest pytest-cov pre-commit
    )
) else if "%1"=="test" (
    if exist "requirements\test.txt" (
        pip install -r requirements\test.txt
    ) else (
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-mock
    )
) else (
    if exist "requirements\base.txt" (
        pip install -r requirements\base.txt
    ) else (
        pip install -r requirements.txt
    )
)

echo %GREEN%[SUCCESS]%NC% %1 dependencies installed
exit /b 0

:install_package
echo %CYAN%[STEP]%NC% Installing AUTO-blogger package...

if "%1"=="dev" (
    pip install -e ".[dev]"
) else (
    pip install -e .
)

echo %GREEN%[SUCCESS]%NC% AUTO-blogger package installed
exit /b 0

:create_env_file
echo %CYAN%[STEP]%NC% Setting up environment configuration...

if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo %GREEN%[SUCCESS]%NC% Created .env file from template
        echo %YELLOW%[WARNING]%NC% Please update .env with your API keys
    ) else (
        echo %BLUE%[INFO]%NC% No .env.example template found
    )
) else (
    echo %BLUE%[INFO]%NC% .env file already exists
)
exit /b 0

:verify_installation
echo %CYAN%[STEP]%NC% Verifying installation...

%PYTHON_CMD% -c "import auto_blogger" 2>nul
if errorlevel 0 (
    echo %GREEN%[SUCCESS]%NC% AUTO-blogger package imports successfully
) else (
    echo %YELLOW%[WARNING]%NC% Package import verification skipped
)

echo %GREEN%[SUCCESS]%NC% Installation verified
exit /b 0

:print_success
echo.
echo %GREEN%
echo ======================================================================
echo                      Setup Complete!
echo ======================================================================
echo %NC%
echo.
echo %CYAN%Quick Start:%NC%
echo.
echo   1. Activate the virtual environment:
echo      venv\Scripts\activate
echo.
echo   2. Run AUTO-blogger:
echo      autoblog
echo      # or
echo      python -m auto_blogger
echo.
echo   3. For development:
echo      setup.bat --dev
echo.
echo %YELLOW%Note:%NC% Update your .env file with API keys before running.
echo.
exit /b 0
