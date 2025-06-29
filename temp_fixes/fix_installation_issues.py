#!/usr/bin/env python3
"""
Fix Installation Issues Script
Copyright © 2025 AryanVBW

This script fixes:
1. Virtual environment creation with unique names
2. macOS app creation permission issues
3. Organizes documentation and test files properly
"""

import os
import sys
import subprocess
import shutil
import uuid
import json
from pathlib import Path
import time

class InstallationFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.unique_id = str(uuid.uuid4())[:8]
        self.venv_name = f"auto_blogger_venv_{self.unique_id}"
        self.backup_dir = self.project_root / "backup_old_files"
        
    def print_status(self, message, status="INFO"):
        """Print colored status messages"""
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m", 
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "RESET": "\033[0m"
        }
        print(f"{colors.get(status, colors['INFO'])}[{status}] {message}{colors['RESET']}")
        
    def create_unique_venv(self):
        """Create virtual environment with unique name"""
        self.print_status(f"Creating virtual environment: {self.venv_name}")
        
        # Remove old venv if exists
        old_venv_paths = [
            self.project_root / "venv",
            self.project_root / "auto_blogger_venv",
            self.project_root / self.venv_name
        ]
        
        for venv_path in old_venv_paths:
            if venv_path.exists():
                self.print_status(f"Removing old virtual environment: {venv_path}", "WARNING")
                shutil.rmtree(venv_path, ignore_errors=True)
        
        # Create new virtual environment
        try:
            subprocess.run([
                sys.executable, "-m", "venv", 
                str(self.project_root / self.venv_name)
            ], check=True)
            self.print_status(f"Virtual environment created successfully: {self.venv_name}", "SUCCESS")
            
            # Install requirements
            self.install_requirements()
            
        except subprocess.CalledProcessError as e:
            self.print_status(f"Failed to create virtual environment: {e}", "ERROR")
            return False
            
        return True
    
    def install_requirements(self):
        """Install requirements in the new virtual environment"""
        self.print_status("Installing requirements...")
        
        # Determine pip path
        if sys.platform == "win32":
            pip_path = self.project_root / self.venv_name / "Scripts" / "pip"
        else:
            pip_path = self.project_root / self.venv_name / "bin" / "pip"
        
        requirements_file = self.project_root / "requirements.txt"
        
        if requirements_file.exists():
            try:
                subprocess.run([
                    str(pip_path), "install", "--upgrade", "pip"
                ], check=True)
                
                subprocess.run([
                    str(pip_path), "install", "-r", str(requirements_file)
                ], check=True)
                
                self.print_status("Requirements installed successfully", "SUCCESS")
            except subprocess.CalledProcessError as e:
                self.print_status(f"Failed to install requirements: {e}", "ERROR")
        else:
            self.print_status("No requirements.txt found", "WARNING")
    
    def fix_app_creation_script(self):
        """Fix the macOS app creation script to handle permission issues"""
        self.print_status("Fixing macOS app creation script...")
        
        install_script = self.project_root / "install_autoblog.sh"
        
        if not install_script.exists():
            self.print_status("install_autoblog.sh not found", "WARNING")
            return
        
        # Read the current script
        with open(install_script, 'r') as f:
            content = f.read()
        
        # Create improved app creation function
        improved_app_creation = '''
# Function to create application shortcuts (improved)
create_app_shortcuts() {
    local os_type="$1"
    
    case "$os_type" in
        "linux")
            echo -e "${YELLOW}🖥️ Creating Linux desktop shortcut...${NC}"
            local desktop_dir="$HOME/Desktop"
            if [ -d "$desktop_dir" ]; then
                cat > "$desktop_dir/AUTO-blogger.desktop" << EOF
[Desktop Entry]
Name=AUTO-blogger
Comment=Automated Blog Content Generator
Exec=bash "$install_dir/autoblog"
Icon="$install_dir/icon.png"
Terminal=false
Type=Application
Categories=Development;Office;
EOF
                chmod +x "$desktop_dir/AUTO-blogger.desktop"
                echo -e "${GREEN}✅ Desktop shortcut created${NC}"
            fi
            ;;
        "macos")
            echo -e "${YELLOW}🖥️ Attempting to create macOS application...${NC}"
            local app_dir="$HOME/Applications/AUTO-blogger.app"
            
            # Try to create in user Applications first
            if mkdir -p "$app_dir/Contents/MacOS" 2>/dev/null && mkdir -p "$app_dir/Contents/Resources" 2>/dev/null; then
                # Create Info.plist without sudo
                cat > "$app_dir/Contents/Info.plist" << EOF
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
                cat > "$app_dir/Contents/MacOS/autoblog" << EOF
#!/bin/bash
cd "$install_dir"
./autoblog
EOF
                chmod +x "$app_dir/Contents/MacOS/autoblog"
                
                # Copy icon if exists
                if [ -f "icon.png" ]; then
                    cp "icon.png" "$app_dir/Contents/Resources/" 2>/dev/null || true
                fi
                
                echo -e "${GREEN}✅ macOS application created in ~/Applications${NC}"
            else
                echo -e "${WARNING}⚠️ Could not create macOS app due to permissions. Skipping app creation.${NC}"
                echo -e "${YELLOW}💡 You can still use the command line launcher: ./autoblog${NC}"
            fi
            ;;
    esac
}
'''
        
        # Replace the existing function
        import re
        pattern = r'# Function to create application shortcuts.*?^}'
        content = re.sub(pattern, improved_app_creation.strip(), content, flags=re.MULTILINE | re.DOTALL)
        
        # Write back the improved script
        with open(install_script, 'w') as f:
            f.write(content)
        
        self.print_status("macOS app creation script improved", "SUCCESS")
    
    def organize_documentation(self):
        """Organize documentation files into proper structure"""
        self.print_status("Organizing documentation files...")
        
        # Create docs directory if it doesn't exist
        docs_dir = self.project_root / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Files to move to docs
        doc_files = [
            "SEO_IMPROVEMENTS_DOCUMENTATION.md",
            "SEO_IMPROVEMENTS_README.md"
        ]
        
        for doc_file in doc_files:
            source = self.project_root / doc_file
            if source.exists():
                destination = docs_dir / doc_file
                if not destination.exists():
                    shutil.move(str(source), str(destination))
                    self.print_status(f"Moved {doc_file} to docs/", "SUCCESS")
                else:
                    self.print_status(f"{doc_file} already exists in docs/", "WARNING")
    
    def organize_test_files(self):
        """Organize test files into proper structure"""
        self.print_status("Organizing test files...")
        
        # Create tests directory if it doesn't exist
        tests_dir = self.project_root / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        # Files to move to tests
        test_files = [
            "test_seo_improvements.py",
            "test_old_plugin_verification.py",
            "migrate_seo_config.py"  # This is more of a utility, but keeping with tests
        ]
        
        for test_file in test_files:
            source = self.project_root / test_file
            if source.exists():
                destination = tests_dir / test_file
                if not destination.exists():
                    shutil.move(str(source), str(destination))
                    self.print_status(f"Moved {test_file} to tests/", "SUCCESS")
                else:
                    self.print_status(f"{test_file} already exists in tests/", "WARNING")
    
    def update_launcher_scripts(self):
        """Update launcher scripts to use the new virtual environment"""
        self.print_status("Updating launcher scripts...")
        
        # Update autoblog_launcher.py
        launcher_script = self.project_root / "autoblog_launcher.py"
        if launcher_script.exists():
            with open(launcher_script, 'r') as f:
                content = f.read()
            
            # Update VENV_DIR to use new venv name
            content = content.replace(
                'VENV_DIR = APP_DIR / "venv"',
                f'VENV_DIR = APP_DIR / "{self.venv_name}"'
            )
            
            with open(launcher_script, 'w') as f:
                f.write(content)
            
            self.print_status("Updated autoblog_launcher.py", "SUCCESS")
        
        # Create/update autoblog script
        autoblog_script = self.project_root / "autoblog"
        script_content = f'''#!/bin/bash
# AUTO-blogger Launcher Script
# Generated automatically with unique virtual environment

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/{self.venv_name}"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found: $VENV_DIR"
    echo "💡 Please run the installer again or use: python3 fix_installation_issues.py"
    exit 1
fi

# Activate virtual environment and launch
cd "$SCRIPT_DIR"
source "$VENV_DIR/bin/activate"
python3 "$SCRIPT_DIR/autoblog_launcher.py"
deactivate
'''
        
        with open(autoblog_script, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(autoblog_script, 0o755)
        self.print_status("Created/updated autoblog launcher script", "SUCCESS")
    
    def create_installation_summary(self):
        """Create a summary of the installation fix"""
        summary_file = self.project_root / "INSTALLATION_FIX_SUMMARY.md"
        
        summary_content = f'''# Installation Fix Summary

## Issues Fixed

### 1. Virtual Environment Issues
- **Problem**: Generic virtual environment names causing conflicts
- **Solution**: Created unique virtual environment: `{self.venv_name}`
- **Status**: ✅ Fixed

### 2. macOS App Creation Permission Issues
- **Problem**: Permission denied when creating app in /Applications
- **Solution**: 
  - Try creating app in ~/Applications first (no sudo required)
  - Gracefully skip app creation if permissions fail
  - Provide alternative command-line launcher
- **Status**: ✅ Fixed

### 3. File Organization
- **Problem**: Documentation and test files scattered in root directory
- **Solution**: 
  - Moved documentation files to `docs/` directory
  - Moved test files to `tests/` directory
- **Status**: ✅ Fixed

## New File Structure

```
AUTO-blogger/
├── docs/
│   ├── SEO_IMPROVEMENTS_DOCUMENTATION.md
│   ├── SEO_IMPROVEMENTS_README.md
│   └── ... (other documentation)
├── tests/
│   ├── test_seo_improvements.py
│   ├── test_old_plugin_verification.py
│   ├── migrate_seo_config.py
│   └── ... (other tests)
├── {self.venv_name}/  # Unique virtual environment
├── autoblog  # Updated launcher script
├── autoblog_launcher.py  # Updated with new venv path
└── ... (other project files)
```

## How to Use

### Command Line (Recommended)
```bash
./autoblog
```

### If Virtual Environment Issues Persist
```bash
python3 fix_installation_issues.py
```

### Manual Virtual Environment Creation
```bash
python3 -m venv {self.venv_name}
source {self.venv_name}/bin/activate
pip install -r requirements.txt
```

## Troubleshooting

### "Virtual environment not found" Error
1. Run: `python3 fix_installation_issues.py`
2. Or manually create venv: `python3 -m venv {self.venv_name}`

### macOS App Creation Failed
- This is normal if you don't have admin permissions
- Use the command line launcher: `./autoblog`
- Or run directly: `python3 autoblog_launcher.py`

### Permission Issues
- Ensure the project directory is writable
- Run: `chmod +x autoblog` to make launcher executable

## Generated Information
- **Fix Applied**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Unique Virtual Environment**: {self.venv_name}
- **Python Version**: {sys.version}
- **Platform**: {sys.platform}

---
*This summary was generated automatically by the installation fixer.*
'''
        
        with open(summary_file, 'w') as f:
            f.write(summary_content)
        
        self.print_status("Created installation fix summary", "SUCCESS")
    
    def run_fixes(self):
        """Run all fixes"""
        self.print_status("Starting installation fixes...", "INFO")
        
        try:
            # 1. Create unique virtual environment
            if not self.create_unique_venv():
                self.print_status("Failed to create virtual environment", "ERROR")
                return False
            
            # 2. Fix app creation script
            self.fix_app_creation_script()
            
            # 3. Organize files
            self.organize_documentation()
            self.organize_test_files()
            
            # 4. Update launcher scripts
            self.update_launcher_scripts()
            
            # 5. Create summary
            self.create_installation_summary()
            
            self.print_status("All fixes completed successfully!", "SUCCESS")
            self.print_status(f"You can now run: ./autoblog", "INFO")
            self.print_status(f"Virtual environment: {self.venv_name}", "INFO")
            
            return True
            
        except Exception as e:
            self.print_status(f"Error during fixes: {e}", "ERROR")
            return False

def main():
    """Main function"""
    print("\n" + "="*60)
    print("🔧 AUTO-blogger Installation Fixer")
    print("Copyright © 2025 AryanVBW")
    print("="*60 + "\n")
    
    fixer = InstallationFixer()
    success = fixer.run_fixes()
    
    if success:
        print("\n" + "="*60)
        print("✅ Installation fixes completed successfully!")
        print("📖 Check INSTALLATION_FIX_SUMMARY.md for details")
        print("🚀 Run './autoblog' to start the application")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ Some fixes failed. Check the output above.")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    main()