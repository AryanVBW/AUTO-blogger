#!/usr/bin/env python3
"""
AUTO-blogger Launcher with Auto-Update
Copyright © 2025 AryanVBW
GitHub: https://github.com/AryanVBW/AUTO-blogger

This launcher checks for updates before starting the application.
"""

import os
import sys
import subprocess
import json
import urllib.request
import urllib.error
from pathlib import Path
import time
import tkinter as tk
from tkinter import messagebox, ttk
import threading

# Configuration
REPO_URL = "https://github.com/AryanVBW/AUTO-blogger.git"
API_URL = "https://api.github.com/repos/AryanVBW/AUTO-blogger"
APP_DIR = Path(__file__).parent.absolute()
VENV_DIR = APP_DIR / "auto_blogger_venv_2344a2a5"

class UpdateChecker:
    def __init__(self):
        self.root = None
        self.progress_var = None
        self.status_var = None
        
    def show_update_dialog(self):
        """Show update progress dialog"""
        self.root = tk.Tk()
        self.root.title("AUTO-blogger Update")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="AUTO-blogger", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Status
        self.status_var = tk.StringVar(value="Checking for updates...")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        progress_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        return self.root
        
    def update_status(self, message, progress=None):
        """Update status message and progress"""
        if self.status_var:
            self.status_var.set(message)
        if progress is not None and self.progress_var:
            self.progress_var.set(progress)
        if self.root:
            self.root.update()
            
    def close_dialog(self):
        """Close the update dialog"""
        if self.root:
            self.root.destroy()
            
    def check_git_available(self):
        """Check if git is available"""
        try:
            subprocess.run(['git', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
            
    def is_git_repo(self):
        """Check if current directory is a git repository"""
        return (APP_DIR / '.git').exists()
        
    def get_local_commit(self):
        """Get local commit hash"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=APP_DIR,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
            
    def get_remote_commit(self):
        """Get remote commit hash from GitHub API"""
        try:
            with urllib.request.urlopen(f"{API_URL}/commits/main") as response:
                data = json.loads(response.read().decode())
                return data['sha']
        except (urllib.error.URLError, json.JSONDecodeError, KeyError):
            try:
                # Fallback to master branch
                with urllib.request.urlopen(f"{API_URL}/commits/master") as response:
                    data = json.loads(response.read().decode())
                    return data['sha']
            except (urllib.error.URLError, json.JSONDecodeError, KeyError):
                return None
                
    def update_repository(self):
        """Update the repository"""
        try:
            self.update_status("Fetching updates...", 30)
            subprocess.run(['git', 'fetch', 'origin'], cwd=APP_DIR, check=True)
            
            self.update_status("Applying updates...", 60)
            # Try main branch first, then master
            try:
                subprocess.run(['git', 'pull', 'origin', 'main'], cwd=APP_DIR, check=True)
            except subprocess.CalledProcessError:
                subprocess.run(['git', 'pull', 'origin', 'master'], cwd=APP_DIR, check=True)
                
            self.update_status("Update completed!", 100)
            return True
        except subprocess.CalledProcessError as e:
            self.update_status(f"Update failed: {e}", 0)
            return False
            
    def check_for_updates(self):
        """Check for updates and update if necessary"""
        # Show update dialog
        dialog = self.show_update_dialog()
        
        def update_thread():
            try:
                self.update_status("Initializing...", 10)
                time.sleep(0.5)
                
                # Check if git is available
                if not self.check_git_available():
                    self.update_status("Git not available, skipping update check", 100)
                    time.sleep(2)
                    self.close_dialog()
                    return
                    
                # Check if this is a git repository
                if not self.is_git_repo():
                    self.update_status("Not a git repository, skipping update check", 100)
                    time.sleep(2)
                    self.close_dialog()
                    return
                    
                self.update_status("Checking for updates...", 20)
                
                # Get local and remote commits
                local_commit = self.get_local_commit()
                remote_commit = self.get_remote_commit()
                
                if not local_commit or not remote_commit:
                    self.update_status("Could not check for updates", 100)
                    time.sleep(2)
                    self.close_dialog()
                    return
                    
                # Compare commits
                if local_commit == remote_commit:
                    self.update_status("Application is up to date!", 100)
                    time.sleep(1.5)
                    self.close_dialog()
                    return
                    
                # Updates available
                self.update_status("Updates available! Downloading...", 25)
                if self.update_repository():
                    time.sleep(1)
                    self.close_dialog()
                    
                    # Show success message
                    root = tk.Tk()
                    root.withdraw()
                    messagebox.showinfo(
                        "Update Complete", 
                        "AUTO-blogger has been updated successfully!\nThe application will now start."
                    )
                    root.destroy()
                else:
                    time.sleep(2)
                    self.close_dialog()
                    
            except Exception as e:
                self.update_status(f"Error: {str(e)}", 0)
                time.sleep(3)
                self.close_dialog()
                
        # Start update check in thread
        thread = threading.Thread(target=update_thread)
        thread.daemon = True
        thread.start()
        
        # Run dialog
        dialog.mainloop()
        
    def launch_app(self):
        """Launch the main application"""
        try:
            # Determine Python executable
            if sys.platform == "win32":
                python_exe = VENV_DIR / "Scripts" / "python.exe"
            else:
                python_exe = VENV_DIR / "bin" / "python"
                
            # Check if virtual environment exists
            if not python_exe.exists():
                python_exe = sys.executable
                
            # Launch the GUI
            gui_script = APP_DIR / "gui_blogger.py"
            if gui_script.exists():
                subprocess.run([str(python_exe), str(gui_script)])
            else:
                # Fallback to launch_blogger.py
                launch_script = APP_DIR / "launch_blogger.py"
                if launch_script.exists():
                    subprocess.run([str(python_exe), str(launch_script)])
                else:
                    raise FileNotFoundError("No launcher script found")
                    
        except Exception as e:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Launch Error", 
                f"Failed to launch AUTO-blogger:\n{str(e)}"
            )
            root.destroy()
            
def main():
    """Main function"""
    checker = UpdateChecker()
    
    # Check for updates first
    checker.check_for_updates()
    
    # Launch the application
    checker.launch_app()
    
if __name__ == "__main__":
    main()