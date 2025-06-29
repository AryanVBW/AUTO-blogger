#!/usr/bin/env python3
"""
AUTO-blogger Auto-Update Test Script
Copyright © 2025 AryanVBW
GitHub: https://github.com/AryanVBW/AUTO-blogger

This script tests the auto-update functionality and installation features.
"""

import os
import sys
import subprocess
import json
import urllib.request
import urllib.error
from pathlib import Path
import tempfile
import shutil

def test_git_availability():
    """Test if Git is available"""
    print("🔍 Testing Git availability...")
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True, check=True)
        print(f"✅ Git found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git not found")
        return False

def test_git_repo_status():
    """Test if current directory is a git repository"""
    print("\n📁 Testing Git repository status...")
    app_dir = Path(__file__).parent.absolute()
    
    if (app_dir / '.git').exists():
        print("✅ Current directory is a Git repository")
        
        # Test getting local commit
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=app_dir,
                capture_output=True,
                text=True,
                check=True
            )
            local_commit = result.stdout.strip()
            print(f"✅ Local commit: {local_commit[:8]}...")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to get local commit")
            return False
    else:
        print("❌ Current directory is not a Git repository")
        return False

def test_remote_api_access():
    """Test access to GitHub API"""
    print("\n🌐 Testing GitHub API access...")
    api_url = "https://api.github.com/repos/AryanVBW/AUTO-blogger"
    
    try:
        with urllib.request.urlopen(f"{api_url}/commits/main") as response:
            data = json.loads(response.read().decode())
            remote_commit = data['sha']
            print(f"✅ Remote commit (main): {remote_commit[:8]}...")
            return True
    except (urllib.error.URLError, json.JSONDecodeError, KeyError):
        try:
            # Fallback to master branch
            with urllib.request.urlopen(f"{api_url}/commits/master") as response:
                data = json.loads(response.read().decode())
                remote_commit = data['sha']
                print(f"✅ Remote commit (master): {remote_commit[:8]}...")
                return True
        except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
            print(f"❌ Failed to access GitHub API: {e}")
            return False

def test_launcher_script():
    """Test the launcher script exists and is executable"""
    print("\n🚀 Testing launcher script...")
    app_dir = Path(__file__).parent.absolute()
    
    # Test Python launcher
    python_launcher = app_dir / "autoblog_launcher.py"
    if python_launcher.exists():
        print("✅ Python launcher (autoblog_launcher.py) exists")
        if os.access(python_launcher, os.X_OK):
            print("✅ Python launcher is executable")
        else:
            print("⚠️ Python launcher is not executable")
    else:
        print("❌ Python launcher not found")
        return False
    
    # Test shell launcher
    shell_launcher = app_dir / "autoblog"
    if shell_launcher.exists():
        print("✅ Shell launcher (autoblog) exists")
        if os.access(shell_launcher, os.X_OK):
            print("✅ Shell launcher is executable")
        else:
            print("⚠️ Shell launcher is not executable")
    else:
        print("⚠️ Shell launcher not found (may not be created yet)")
    
    return True

def test_virtual_environment():
    """Test virtual environment setup"""
    print("\n🐍 Testing virtual environment...")
    app_dir = Path(__file__).parent.absolute()
    venv_dir = app_dir / "venv"
    
    if venv_dir.exists():
        print("✅ Virtual environment directory exists")
        
        # Check for Python executable
        if sys.platform == "win32":
            python_exe = venv_dir / "Scripts" / "python.exe"
        else:
            python_exe = venv_dir / "bin" / "python"
            
        if python_exe.exists():
            print("✅ Python executable found in virtual environment")
            
            # Test running Python in venv
            try:
                result = subprocess.run(
                    [str(python_exe), '--version'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"✅ Virtual environment Python: {result.stdout.strip()}")
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to run Python in virtual environment")
                return False
        else:
            print("❌ Python executable not found in virtual environment")
            return False
    else:
        print("⚠️ Virtual environment not found (may not be created yet)")
        return False

def test_dependencies():
    """Test if required dependencies are available"""
    print("\n📦 Testing dependencies...")
    app_dir = Path(__file__).parent.absolute()
    venv_dir = app_dir / "venv"
    
    if sys.platform == "win32":
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        python_exe = venv_dir / "bin" / "python"
    
    if not python_exe.exists():
        python_exe = sys.executable
        print("⚠️ Using system Python instead of virtual environment")
    
    dependencies = [
        'tkinter',
        'requests',
        'openai',
        'bs4',
        'selenium',
        'PIL'
    ]
    
    success_count = 0
    for dep in dependencies:
        try:
            result = subprocess.run(
                [str(python_exe), '-c', f'import {dep}; print(f"{dep} imported successfully")'],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ {dep}: Available")
            success_count += 1
        except subprocess.CalledProcessError:
            print(f"❌ {dep}: Not available")
    
    print(f"\n📊 Dependencies: {success_count}/{len(dependencies)} available")
    return success_count == len(dependencies)

def test_installation_script():
    """Test the installation script"""
    print("\n📋 Testing installation script...")
    app_dir = Path(__file__).parent.absolute()
    install_script = app_dir / "install_autoblog.sh"
    
    if install_script.exists():
        print("✅ Installation script exists")
        if os.access(install_script, os.X_OK):
            print("✅ Installation script is executable")
        else:
            print("⚠️ Installation script is not executable")
        
        # Check if script contains auto-update functionality
        with open(install_script, 'r') as f:
            content = f.read()
            if 'clone_or_update_repo' in content:
                print("✅ Auto-update functionality found in script")
            else:
                print("❌ Auto-update functionality not found in script")
                return False
            
            if 'autoblog_launcher.py' in content:
                print("✅ Auto-update launcher integration found")
            else:
                print("❌ Auto-update launcher integration not found")
                return False
        
        return True
    else:
        print("❌ Installation script not found")
        return False

def test_core_files():
    """Test if core application files exist"""
    print("\n📄 Testing core application files...")
    app_dir = Path(__file__).parent.absolute()
    
    core_files = [
        'gui_blogger.py',
        'automation_engine.py',
        'launch_blogger.py',
        'requirements.txt',
        'setup.py'
    ]
    
    success_count = 0
    for file in core_files:
        file_path = app_dir / file
        if file_path.exists():
            print(f"✅ {file}: Found")
            success_count += 1
        else:
            print(f"❌ {file}: Not found")
    
    print(f"\n📊 Core files: {success_count}/{len(core_files)} found")
    return success_count == len(core_files)

def main():
    """Main test function"""
    print("🧪 AUTO-blogger Auto-Update Test Suite")
    print("=" * 50)
    
    tests = [
        ("Git Availability", test_git_availability),
        ("Git Repository Status", test_git_repo_status),
        ("GitHub API Access", test_remote_api_access),
        ("Launcher Scripts", test_launcher_script),
        ("Virtual Environment", test_virtual_environment),
        ("Dependencies", test_dependencies),
        ("Installation Script", test_installation_script),
        ("Core Files", test_core_files)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AUTO-blogger auto-update system is ready!")
        return True
    else:
        print(f"⚠️ {total - passed} test(s) failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)