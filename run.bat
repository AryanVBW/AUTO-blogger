@echo off
REM ==============================================================================
REM AUTO-blogger Run Script for Windows
REM Copyright (c) 2025 AryanVBW
REM ==============================================================================

setlocal EnableDelayedExpansion

set "VENV_DIR=venv"
set "SCRIPT_DIR=%~dp0"

REM Colors
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Default values
set "COMMAND=gui"
set "USE_VENV=true"
set "DEBUG=false"

REM Parse arguments
:parse_args
if "%~1"=="" goto :run
if /i "%~1"=="--no-venv" set "USE_VENV=false" & shift & goto :parse_args
if /i "%~1"=="--debug" set "DEBUG=true" & shift & goto :parse_args
if /i "%~1"=="--help" goto :show_help
if /i "%~1"=="-h" goto :show_help
if /i "%~1"=="gui" set "COMMAND=gui" & shift & goto :parse_args
if /i "%~1"=="cli" set "COMMAND=cli" & shift & goto :parse_args
if /i "%~1"=="test" set "COMMAND=test" & shift & goto :parse_args
if /i "%~1"=="shell" set "COMMAND=shell" & shift & goto :parse_args
echo %RED%[ERROR]%NC% Unknown option: %~1
goto :show_help

:run
cd /d "%SCRIPT_DIR%"

REM Activate virtual environment
if "%USE_VENV%"=="true" (
    if exist "%VENV_DIR%\Scripts\activate.bat" (
        call "%VENV_DIR%\Scripts\activate.bat"
    ) else (
        echo %BLUE%[INFO]%NC% No virtual environment found. Using system Python.
    )
)

REM Set debug mode
if "%DEBUG%"=="true" (
    set "AUTO_BLOGGER_DEBUG=1"
    set "PYTHONVERBOSE=1"
    echo %BLUE%[INFO]%NC% Debug mode enabled
)

REM Execute command
if "%COMMAND%"=="gui" goto :run_gui
if "%COMMAND%"=="cli" goto :run_cli
if "%COMMAND%"=="test" goto :run_test
if "%COMMAND%"=="shell" goto :run_shell

:run_gui
echo %BLUE%[INFO]%NC% Starting AUTO-blogger GUI...
python -m auto_blogger.gui_blogger %*
goto :end

:run_cli
echo %BLUE%[INFO]%NC% Starting AUTO-blogger CLI...
where autoblog >nul 2>&1
if %errorlevel%==0 (
    autoblog %*
) else (
    python -m auto_blogger %*
)
goto :end

:run_test
echo %BLUE%[INFO]%NC% Running tests...
pytest tests/ -v %*
goto :end

:run_shell
echo %BLUE%[INFO]%NC% Starting Python shell...
python -c "from auto_blogger import *; print('AUTO-blogger loaded.')"
python -i -c "from auto_blogger import *"
goto :end

:show_help
echo.
echo AUTO-blogger Run Script
echo ========================
echo.
echo Usage: run.bat [OPTIONS] [COMMAND]
echo.
echo Commands:
echo   gui         Run the GUI application (default)
echo   cli         Run command-line interface
echo   test        Run tests
echo   shell       Start Python shell with package loaded
echo.
echo Options:
echo   --no-venv   Run without activating virtual environment
echo   --debug     Run with debug logging
echo   --help      Show this help message
echo.
echo Examples:
echo   run.bat              # Run GUI
echo   run.bat gui          # Run GUI
echo   run.bat cli          # Run CLI
echo   run.bat --debug gui  # Run GUI with debug
echo.
goto :end

:end
endlocal
