#Requires -Version 5.1
<#
.SYNOPSIS
    AUTO-blogger Setup Script for Windows PowerShell

.DESCRIPTION
    Professional setup script for AUTO-blogger WordPress automation tool.
    Handles Python environment, dependencies, and configuration.

.PARAMETER Mode
    Installation mode: base, dev, or test

.PARAMETER Clean
    Remove existing virtual environment before setup

.PARAMETER NoVenv
    Skip virtual environment creation

.EXAMPLE
    .\setup.ps1
    Standard installation

.EXAMPLE
    .\setup.ps1 -Mode dev
    Development setup with all dev tools

.EXAMPLE
    .\setup.ps1 -Clean
    Clean reinstall

.NOTES
    Copyright (c) 2025 AryanVBW
    https://github.com/AryanVBW/AUTO-blogger
#>

[CmdletBinding()]
param(
    [ValidateSet('base', 'dev', 'test')]
    [string]$Mode = 'base',

    [switch]$Clean,

    [switch]$NoVenv,

    [switch]$Help
)

# Configuration
$VenvDir = "venv"
$PythonMinVersion = [Version]"3.8"
$ProjectName = "AUTO-blogger"

# ==============================================================================
# Helper Functions
# ==============================================================================

function Write-Header {
    Write-Host ""
    Write-Host "==============================================================================" -ForegroundColor Magenta
    Write-Host "                         AUTO-blogger Setup" -ForegroundColor Magenta
    Write-Host "              Professional WordPress Automation Tool" -ForegroundColor Magenta
    Write-Host "==============================================================================" -ForegroundColor Magenta
    Write-Host ""
}

function Write-LogInfo {
    param([string]$Message)
    Write-Host "[INFO] " -ForegroundColor Blue -NoNewline
    Write-Host $Message
}

function Write-LogSuccess {
    param([string]$Message)
    Write-Host "[SUCCESS] " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-LogWarning {
    param([string]$Message)
    Write-Host "[WARNING] " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Write-LogError {
    param([string]$Message)
    Write-Host "[ERROR] " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

function Write-LogStep {
    param([string]$Message)
    Write-Host "[STEP] " -ForegroundColor Cyan -NoNewline
    Write-Host $Message
}

function Test-PythonVersion {
    param([string]$PythonCmd)

    try {
        $versionOutput = & $PythonCmd -c "import sys; print('.'.join(map(str, sys.version_info[:2])))" 2>$null
        $version = [Version]$versionOutput
        return $version -ge $PythonMinVersion
    }
    catch {
        return $false
    }
}

# ==============================================================================
# System Checks
# ==============================================================================

function Find-Python {
    Write-LogStep "Checking Python installation..."

    $pythonCmds = @('python', 'python3', 'py')

    foreach ($cmd in $pythonCmds) {
        if (Get-Command $cmd -ErrorAction SilentlyContinue) {
            if (Test-PythonVersion $cmd) {
                $version = & $cmd -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"
                Write-LogSuccess "Found $cmd version $version"
                return $cmd
            }
        }
    }

    Write-LogError "Python $PythonMinVersion or higher is required but not found."
    Write-LogInfo "Please install Python from https://www.python.org/downloads/"
    return $null
}

function Test-Pip {
    param([string]$PythonCmd)

    Write-LogStep "Checking pip installation..."

    try {
        & $PythonCmd -m pip --version 2>$null | Out-Null
        Write-LogSuccess "pip is available"
        return $true
    }
    catch {
        Write-LogWarning "pip not found. Attempting to install..."
        try {
            & $PythonCmd -m ensurepip --default-pip
            Write-LogSuccess "pip installed"
            return $true
        }
        catch {
            Write-LogError "Failed to install pip"
            return $false
        }
    }
}

function Test-Chrome {
    Write-LogStep "Checking Chrome installation..."

    $chromePaths = @(
        "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
        "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
    )

    foreach ($path in $chromePaths) {
        if (Test-Path $path) {
            Write-LogSuccess "Chrome found at $path"
            return $true
        }
    }

    Write-LogWarning "Chrome not found. Selenium automation requires Chrome."
    Write-LogInfo "Download from: https://www.google.com/chrome/"
    return $false
}

# ==============================================================================
# Environment Setup
# ==============================================================================

function New-VirtualEnvironment {
    param([string]$PythonCmd)

    Write-LogStep "Setting up virtual environment..."

    if (Test-Path $VenvDir) {
        Write-LogInfo "Virtual environment exists. Recreating..."
        Remove-Item -Recurse -Force $VenvDir
    }

    & $PythonCmd -m venv $VenvDir

    if ($LASTEXITCODE -ne 0) {
        Write-LogError "Failed to create virtual environment"
        return $false
    }

    Write-LogSuccess "Virtual environment created at .\$VenvDir"
    return $true
}

function Enter-VirtualEnvironment {
    Write-LogStep "Activating virtual environment..."

    $activateScript = Join-Path $VenvDir "Scripts\Activate.ps1"

    if (-not (Test-Path $activateScript)) {
        Write-LogError "Activation script not found"
        return $false
    }

    & $activateScript
    Write-LogSuccess "Virtual environment activated"
    return $true
}

function Update-Pip {
    Write-LogStep "Upgrading pip and setuptools..."

    pip install --upgrade pip setuptools wheel 2>$null | Out-Null
    Write-LogSuccess "pip and setuptools upgraded"
}

function Install-Dependencies {
    param([string]$InstallMode)

    Write-LogStep "Installing $InstallMode dependencies..."

    switch ($InstallMode) {
        'dev' {
            if (Test-Path "requirements\dev.txt") {
                pip install -r requirements\dev.txt
            } else {
                pip install -r requirements.txt
                pip install black flake8 mypy pytest pytest-cov pre-commit
            }
        }
        'test' {
            if (Test-Path "requirements\test.txt") {
                pip install -r requirements\test.txt
            } else {
                pip install -r requirements.txt
                pip install pytest pytest-cov pytest-mock
            }
        }
        default {
            if (Test-Path "requirements\base.txt") {
                pip install -r requirements\base.txt
            } else {
                pip install -r requirements.txt
            }
        }
    }

    Write-LogSuccess "$InstallMode dependencies installed"
}

function Install-Package {
    param([string]$InstallMode)

    Write-LogStep "Installing AUTO-blogger package..."

    if ($InstallMode -eq 'dev') {
        pip install -e ".[dev]"
    } else {
        pip install -e .
    }

    Write-LogSuccess "AUTO-blogger package installed"
}

function Initialize-EnvFile {
    Write-LogStep "Setting up environment configuration..."

    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-LogSuccess "Created .env file from template"
            Write-LogWarning "Please update .env with your API keys"
        } else {
            Write-LogInfo "No .env.example template found"
        }
    } else {
        Write-LogInfo ".env file already exists"
    }
}

function Test-Installation {
    param([string]$PythonCmd)

    Write-LogStep "Verifying installation..."

    try {
        & $PythonCmd -c "import auto_blogger" 2>$null
        Write-LogSuccess "AUTO-blogger package imports successfully"
    }
    catch {
        Write-LogWarning "Package import verification skipped"
    }

    Write-LogSuccess "Installation verified"
}

function Write-SuccessMessage {
    Write-Host ""
    Write-Host "==============================================================================" -ForegroundColor Green
    Write-Host "                          Setup Complete!" -ForegroundColor Green
    Write-Host "==============================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Quick Start:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1. Activate the virtual environment:"
    Write-Host "     .\venv\Scripts\Activate.ps1"
    Write-Host ""
    Write-Host "  2. Run AUTO-blogger:"
    Write-Host "     autoblog"
    Write-Host "     # or"
    Write-Host "     python -m auto_blogger"
    Write-Host ""
    Write-Host "  3. For development:"
    Write-Host "     .\setup.ps1 -Mode dev"
    Write-Host ""
    Write-Host "Note: " -ForegroundColor Yellow -NoNewline
    Write-Host "Update your .env file with API keys before running."
    Write-Host ""
}

function Show-Usage {
    Write-Host ""
    Write-Host "AUTO-blogger Setup Script" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\setup.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Mode <base|dev|test>  Installation mode (default: base)"
    Write-Host "  -Clean                 Remove existing venv before setup"
    Write-Host "  -NoVenv                Skip virtual environment creation"
    Write-Host "  -Help                  Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\setup.ps1                # Standard installation"
    Write-Host "  .\setup.ps1 -Mode dev      # Development setup"
    Write-Host "  .\setup.ps1 -Clean         # Clean reinstall"
    Write-Host ""
}

# ==============================================================================
# Main Script
# ==============================================================================

function Main {
    if ($Help) {
        Show-Usage
        return
    }

    Write-Header

    # Navigate to script directory
    Push-Location $PSScriptRoot

    try {
        Write-LogInfo "Starting $ProjectName setup (mode: $Mode)"
        Write-Host ""

        # Clean if requested
        if ($Clean -and (Test-Path $VenvDir)) {
            Write-LogStep "Cleaning existing virtual environment..."
            Remove-Item -Recurse -Force $VenvDir
            Write-LogSuccess "Cleaned"
        }

        # System checks
        $pythonCmd = Find-Python
        if (-not $pythonCmd) {
            return
        }

        if (-not (Test-Pip $pythonCmd)) {
            return
        }

        Test-Chrome
        Write-Host ""

        # Environment setup
        if (-not $NoVenv) {
            if (-not (New-VirtualEnvironment $pythonCmd)) {
                return
            }

            if (-not (Enter-VirtualEnvironment)) {
                return
            }
        }

        Update-Pip
        Install-Dependencies $Mode
        Install-Package $Mode
        Initialize-EnvFile
        Write-Host ""

        # Verification
        Test-Installation $pythonCmd

        Write-SuccessMessage
    }
    finally {
        Pop-Location
    }
}

# Run main function
Main
