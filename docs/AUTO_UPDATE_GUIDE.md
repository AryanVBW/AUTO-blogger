# AUTO-blogger Auto-Update System Guide

🔄 **AUTO-blogger** now includes a comprehensive auto-update system that automatically keeps your installation up-to-date with the latest features and bug fixes from the GitHub repository.

## 🌟 New Features

### 1. 📦 Automatic Repository Cloning
- The installation script now automatically clones the repository from GitHub
- No need to manually download or clone the repository
- Installs to `~/AUTO-blogger` by default

### 2. 🔄 Auto-Update on Launch
- Every time you launch AUTO-blogger, it checks for updates
- Automatically downloads and applies updates if available
- Shows a progress dialog during the update process
- Seamlessly launches the updated application

### 3. 🚀 Enhanced Installation Script
- One-command installation that handles everything
- Automatic Git installation if not available
- Repository cloning and setup
- Virtual environment creation
- Dependency installation
- System launcher creation with auto-update

## 🛠️ How It Works

### Installation Process

1. **Git Check**: Verifies Git is installed, installs if needed
2. **Repository Setup**: Clones or updates the repository
3. **Environment Setup**: Creates Python virtual environment
4. **Dependencies**: Installs all required packages
5. **Launcher Creation**: Creates system-wide launcher with auto-update

### Auto-Update Process

1. **Launch Detection**: When you run `autoblog` command
2. **Update Check**: Compares local and remote repository commits
3. **Download**: Fetches updates if available
4. **Apply**: Updates the local repository
5. **Launch**: Starts the updated application

## 📋 Installation Commands

### Quick Installation (Recommended)

```bash
# One-command installation
curl -fsSL https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_autoblog.sh | bash
```

### Manual Installation

```bash
# Download installation script
wget https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_autoblog.sh

# Make executable and run
chmod +x install_autoblog.sh
./install_autoblog.sh
```

## 🎯 Usage

### Starting AUTO-blogger

```bash
# System-wide command (after installation)
autoblog

# Or from installation directory
cd ~/AUTO-blogger
./autoblog
```

### What Happens on Launch

1. **Update Dialog**: Shows "Checking for updates..." dialog
2. **Progress Bar**: Displays update progress if updates are found
3. **Success Message**: Confirms successful update (if applicable)
4. **Application Launch**: Starts the main GUI

## 🔧 Technical Details

### Files Created

- `autoblog_launcher.py`: Python auto-update launcher
- `autoblog`: Shell script that calls the Python launcher
- `launch_blogger.py`: Application entry point
- `test_autoupdate.py`: Comprehensive test suite

### Auto-Update Components

1. **UpdateChecker Class**: Handles update logic
2. **Git Integration**: Uses Git commands for repository management
3. **GitHub API**: Checks for new commits via GitHub API
4. **Progress Dialog**: Tkinter-based update progress display
5. **Error Handling**: Graceful fallbacks and error messages

### Update Detection

- Compares local Git commit hash with remote repository
- Uses GitHub API to fetch latest commit information
- Falls back from `main` to `master` branch if needed
- Handles network errors gracefully

## 🧪 Testing

Run the comprehensive test suite:

```bash
cd ~/AUTO-blogger
python3 test_autoupdate.py
```

The test suite verifies:
- ✅ Git availability
- ✅ Repository status
- ✅ GitHub API access
- ✅ Launcher scripts
- ✅ Virtual environment
- ✅ Dependencies
- ✅ Installation script
- ✅ Core files

## 🔍 Troubleshooting

### Common Issues

**Git Not Found**
- The installer will automatically install Git
- On macOS: Requires Homebrew or manual installation
- On Linux: Uses package manager (apt, yum, dnf, pacman)

**Network Issues**
- Auto-update requires internet connection
- Falls back gracefully if GitHub API is unavailable
- Application still launches even if update check fails

**Permission Issues**
- Desktop shortcuts may require sudo on some systems
- Core functionality works without desktop shortcuts

### Manual Update

If auto-update fails, you can manually update:

```bash
cd ~/AUTO-blogger
git pull origin main
# or
git pull origin master
```

## 🎉 Benefits

### For Users
- 🔄 **Always Up-to-Date**: Never miss new features or bug fixes
- 🚀 **Zero Maintenance**: Updates happen automatically
- 💻 **One-Click Install**: Complete setup with single command
- 🛡️ **Isolated Environment**: Virtual environment prevents conflicts

### For Developers
- 📦 **Easy Distribution**: Users always get latest version
- 🐛 **Rapid Bug Fixes**: Fixes reach users immediately
- 📊 **Simplified Support**: Everyone runs the same version
- 🔧 **Continuous Deployment**: Push updates directly to users

## 🔮 Future Enhancements

- **Version Notifications**: Show changelog for updates
- **Selective Updates**: Allow users to skip certain updates
- **Rollback Feature**: Ability to revert to previous version
- **Update Scheduling**: Configure when to check for updates
- **Offline Mode**: Cache updates for offline installation

---

**Copyright © 2025 AryanVBW**  
**GitHub**: https://github.com/AryanVBW/AUTO-blogger

*AUTO-blogger: Intelligent Blog Automation with Auto-Update Technology*