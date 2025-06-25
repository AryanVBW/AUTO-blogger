#!/usr/bin/env python3
"""
WordPress Blog Automation GUI
A comprehensive interface for automated blog posting with progress tracking

Copyright © 2025 AryanVBW
GitHub: https://github.com/AryanVBW
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import logging
import sys
import os
import json
import queue
import time
import webbrowser
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import unicodedata
from contextlib import contextmanager
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError, RequestException

# Import the automation engine
try:
    from automation_engine import BlogAutomationEngine, SELENIUM_AVAILABLE
except ImportError:
    BlogAutomationEngine = None
    SELENIUM_AVAILABLE = False

class BlogAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WordPress Blog Automation Suite - © 2025 AryanVBW")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Initialize variables
        self.config = {}
        self.is_logged_in = False
        self.current_task = None
        self.stop_flag = False
        self.log_queue = queue.Queue()
        self.processed_count = 0
        self.total_articles = 0
        
        # Configuration file
        self.config_file = "blog_config.json"
        
        # Initialize logging
        self.setup_logging()
        
        # Load configuration
        self.load_config()
        
        # Initialize automation engine
        self.automation_engine = None
        
        # Create GUI
        self.create_widgets()
        
        # Start log processing
        self.process_log_queue()
        
        # Apply theme
        self.apply_theme()
        
    def setup_logging(self):
        """Setup logging to capture all messages"""
        self.logger = logging.getLogger('BlogAutomation')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create custom handler that sends to queue
        class QueueHandler(logging.Handler):
            def __init__(self, log_queue):
                super().__init__()
                self.log_queue = log_queue
                
            def emit(self, record):
                self.log_queue.put(self.format(record))
        
        handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                self.logger.info("Configuration loaded successfully")
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                self.config = {}
        else:
            self.config = self.get_default_config()
            
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info("Configuration saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            
    def get_default_config(self):
        """Get default configuration"""
        return {
            "source_url": "https://tbrfootball.com/topic/english-premier-league/",
            "article_selector": "article.article h2 a",
            "wp_base_url": "https://premierleaguenewsnow.com/wp-json/wp/v2",
            "wp_username": "",
            "wp_password": "",
            "gemini_api_key": "",
            "max_articles": 2,
            "timeout": 10,
            "headless_mode": True
        }
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Create menu bar
        self.create_menu_bar()
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_login_tab()
        self.create_automation_tab()
        self.create_logs_tab()
        self.create_config_tab()
        
        # Status bar
        self.create_status_bar()
        
    def create_menu_bar(self):
        """Create menu bar"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about_dialog)
        help_menu.add_separator()
        help_menu.add_command(label="GitHub Repository", command=lambda: self.open_github_link(None))
        
    def show_about_dialog(self):
        """Show About dialog"""
        about_text = """WordPress Blog Automation Suite
        
A comprehensive GUI application for automating WordPress blog posting with AI-powered content generation and SEO optimization.

Features:
• AI-powered content rewriting with Gemini
• Focus keyphrase and additional keyphrases extraction
• Smart internal and external link injection
• Real-time progress tracking
• WordPress REST API integration
• SEO optimization

Copyright © 2025 AryanVBW
GitHub: https://github.com/AryanVBW

Licensed under the MIT License"""
        
        messagebox.showinfo("About WordPress Blog Automation Suite", about_text)
        
    def create_login_tab(self):
        """Create login and authentication tab"""
        self.login_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="🔐 Authentication")
        
        # Title
        title_label = ttk.Label(self.login_frame, text="WordPress Blog Automation", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=20)
        
        # Login form frame
        login_form = ttk.LabelFrame(self.login_frame, text="WordPress Credentials", padding=20)
        login_form.pack(pady=20, padx=40, fill=tk.X)
        
        # WordPress URL
        ttk.Label(login_form, text="WordPress Site URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.wp_url_var = tk.StringVar(value=self.config.get('wp_base_url', ''))
        ttk.Entry(login_form, textvariable=self.wp_url_var, width=50).grid(row=0, column=1, pady=5, padx=10)
        
        # Username
        ttk.Label(login_form, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar(value=self.config.get('wp_username', ''))
        ttk.Entry(login_form, textvariable=self.username_var, width=50).grid(row=1, column=1, pady=5, padx=10)
        
        # Password
        ttk.Label(login_form, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar(value=self.config.get('wp_password', ''))
        ttk.Entry(login_form, textvariable=self.password_var, show="*", width=50).grid(row=2, column=1, pady=5, padx=10)
        
        # Gemini API Key
        ttk.Label(login_form, text="Gemini API Key:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.gemini_key_var = tk.StringVar(value=self.config.get('gemini_api_key', ''))
        ttk.Entry(login_form, textvariable=self.gemini_key_var, show="*", width=50).grid(row=3, column=1, pady=5, padx=10)
        
        # Buttons frame
        button_frame = ttk.Frame(login_form)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Test connection button
        self.test_btn = ttk.Button(button_frame, text="Test Connection", 
                                  command=self.test_connection, style="Accent.TButton")
        self.test_btn.pack(side=tk.LEFT, padx=10)
        
        # Login button
        self.login_btn = ttk.Button(button_frame, text="Login & Save", 
                                   command=self.login, style="Accent.TButton")
        self.login_btn.pack(side=tk.LEFT, padx=10)
        
        # Connection status
        self.connection_status = ttk.Label(login_form, text="Not connected", foreground="red")
        self.connection_status.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Prerequisites check
        self.create_prerequisites_section()
        
    def create_prerequisites_section(self):
        """Create prerequisites check section"""
        prereq_frame = ttk.LabelFrame(self.login_frame, text="System Prerequisites", padding=20)
        prereq_frame.pack(pady=20, padx=40, fill=tk.X)
        
        # Check selenium
        selenium_status = "✅ Available" if SELENIUM_AVAILABLE else "❌ Not installed"
        ttk.Label(prereq_frame, text=f"Selenium WebDriver: {selenium_status}").pack(anchor=tk.W)
        
        # Check other requirements
        requirements = [
            ("requests", "requests"),
            ("beautifulsoup4", "bs4"),
            ("webdriver-manager", "webdriver_manager")
        ]
        
        for req_name, import_name in requirements:
            try:
                __import__(import_name)
                status = "✅ Available"
            except ImportError:
                status = "❌ Not installed"
            ttk.Label(prereq_frame, text=f"{req_name}: {status}").pack(anchor=tk.W)
            
        if not SELENIUM_AVAILABLE:
            install_btn = ttk.Button(prereq_frame, text="Install Missing Requirements", 
                                   command=self.install_requirements)
            install_btn.pack(pady=10)
            
    def create_automation_tab(self):
        """Create main automation tab"""
        self.automation_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.automation_frame, text="🤖 Automation")
        
        # Control panel
        control_panel = ttk.LabelFrame(self.automation_frame, text="Control Panel", padding=10)
        control_panel.pack(fill=tk.X, padx=10, pady=5)
        
        # Settings frame
        settings_frame = ttk.Frame(control_panel)
        settings_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(settings_frame, text="Max Articles:").pack(side=tk.LEFT)
        self.max_articles_var = tk.IntVar(value=self.config.get('max_articles', 2))
        ttk.Spinbox(settings_frame, from_=1, to=10, textvariable=self.max_articles_var, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(settings_frame, text="Source URL:").pack(side=tk.LEFT, padx=(20, 5))
        self.source_url_var = tk.StringVar(value=self.config.get('source_url', ''))
        ttk.Entry(settings_frame, textvariable=self.source_url_var, width=40).pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(control_panel)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(buttons_frame, text="▶️ Start Automation", 
                                   command=self.start_automation, style="Accent.TButton")
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(buttons_frame, text="⏹️ Stop", 
                                  command=self.stop_automation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_logs_btn = ttk.Button(buttons_frame, text="🗑️ Clear Logs", 
                                        command=self.clear_logs)
        self.clear_logs_btn.pack(side=tk.LEFT, padx=5)
        
        self.test_config_btn = ttk.Button(buttons_frame, text="🔍 Test Configuration", 
                                         command=self.test_configuration)
        self.test_config_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(self.automation_frame, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Overall progress
        ttk.Label(progress_frame, text="Overall Progress:").pack(anchor=tk.W)
        self.overall_progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.overall_progress.pack(fill=tk.X, pady=5)
        
        # Current task progress
        ttk.Label(progress_frame, text="Current Task:").pack(anchor=tk.W, pady=(10, 0))
        self.task_progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.task_progress.pack(fill=tk.X, pady=5)
        
        # Status labels
        self.status_frame = ttk.Frame(progress_frame)
        self.status_frame.pack(fill=tk.X, pady=5)
        
        self.current_task_label = ttk.Label(self.status_frame, text="Status: Ready")
        self.current_task_label.pack(side=tk.LEFT)
        
        self.articles_count_label = ttk.Label(self.status_frame, text="Articles: 0/0")
        self.articles_count_label.pack(side=tk.RIGHT)
        
        # Steps tracking
        self.create_steps_tracking()
        
    def create_steps_tracking(self):
        """Create step-by-step progress tracking"""
        steps_frame = ttk.LabelFrame(self.automation_frame, text="Process Steps", padding=10)
        steps_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview for steps
        columns = ('Step', 'Status', 'Details', 'Time')
        self.steps_tree = ttk.Treeview(steps_frame, columns=columns, show='headings', height=10)
        
        # Define headings
        self.steps_tree.heading('Step', text='Step')
        self.steps_tree.heading('Status', text='Status')
        self.steps_tree.heading('Details', text='Details')
        self.steps_tree.heading('Time', text='Time')
        
        # Define column widths
        self.steps_tree.column('Step', width=200)
        self.steps_tree.column('Status', width=100)
        self.steps_tree.column('Details', width=400)
        self.steps_tree.column('Time', width=150)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(steps_frame, orient=tk.VERTICAL, command=self.steps_tree.yview)
        self.steps_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.steps_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initialize steps
        self.initialize_steps()
        
    def initialize_steps(self):
        """Initialize the process steps"""
        self.process_steps = [
            "Fetching article links",
            "Extracting article content", 
            "Paraphrasing with Gemini",
            "Injecting internal links",
            "Injecting external links",
            "Generating SEO metadata",
            "Extracting keyphrases",
            "Detecting categories",
            "Generating tags",
            "Creating WordPress post",
            "Finalizing post"
        ]
        
        # Clear existing items
        for item in self.steps_tree.get_children():
            self.steps_tree.delete(item)
            
        # Add steps
        for i, step in enumerate(self.process_steps):
            self.steps_tree.insert('', 'end', iid=str(i), values=(step, '⏳ Pending', '', ''))
            
    def create_logs_tab(self):
        """Create logs tab"""
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="📋 Logs")
        
        # Logs toolbar
        logs_toolbar = ttk.Frame(self.logs_frame)
        logs_toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(logs_toolbar, text="Log Level:").pack(side=tk.LEFT)
        self.log_level_var = tk.StringVar(value="INFO")
        log_level_combo = ttk.Combobox(logs_toolbar, textvariable=self.log_level_var, 
                                      values=["DEBUG", "INFO", "WARNING", "ERROR"], 
                                      width=10, state="readonly")
        log_level_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(logs_toolbar, text="Save Logs", command=self.save_logs).pack(side=tk.RIGHT, padx=5)
        ttk.Button(logs_toolbar, text="Clear", command=self.clear_logs).pack(side=tk.RIGHT)
        
        # Logs text area
        self.logs_text = scrolledtext.ScrolledText(self.logs_frame, wrap=tk.WORD, height=25)
        self.logs_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Configure text tags for colored output
        self.logs_text.tag_configure("ERROR", foreground="red")
        self.logs_text.tag_configure("WARNING", foreground="orange")
        self.logs_text.tag_configure("INFO", foreground="blue")
        self.logs_text.tag_configure("DEBUG", foreground="gray")
        
    def create_config_tab(self):
        """Create configuration tab"""
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="⚙️ Configuration")
        
        # Create scrollable frame
        canvas = tk.Canvas(self.config_frame)
        scrollbar = ttk.Scrollbar(self.config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Source configuration
        source_frame = ttk.LabelFrame(scrollable_frame, text="Source Configuration", padding=10)
        source_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(source_frame, text="Source URL:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.config_source_url = tk.StringVar(value=self.config.get('source_url', ''))
        ttk.Entry(source_frame, textvariable=self.config_source_url, width=60).grid(row=0, column=1, pady=2, padx=10)
        
        ttk.Label(source_frame, text="Article Selector:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.config_selector = tk.StringVar(value=self.config.get('article_selector', ''))
        ttk.Entry(source_frame, textvariable=self.config_selector, width=60).grid(row=1, column=1, pady=2, padx=10)
        
        # Processing configuration
        process_frame = ttk.LabelFrame(scrollable_frame, text="Processing Configuration", padding=10)
        process_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(process_frame, text="Timeout (seconds):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.config_timeout = tk.IntVar(value=self.config.get('timeout', 10))
        ttk.Spinbox(process_frame, from_=5, to=60, textvariable=self.config_timeout, width=10).grid(row=0, column=1, sticky=tk.W, pady=2, padx=10)
        
        ttk.Label(process_frame, text="Headless Mode:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.config_headless = tk.BooleanVar(value=self.config.get('headless_mode', True))
        ttk.Checkbutton(process_frame, variable=self.config_headless).grid(row=1, column=1, sticky=tk.W, pady=2, padx=10)
        
        # Links configuration - create text areas for complex configs
        links_frame = ttk.LabelFrame(scrollable_frame, text="Links Configuration", padding=10)
        links_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Internal links
        ttk.Label(links_frame, text="Internal Links (JSON format):").pack(anchor=tk.W)
        self.internal_links_text = scrolledtext.ScrolledText(links_frame, height=8)
        self.internal_links_text.pack(fill=tk.X, pady=5)
        self.internal_links_text.insert(tk.END, json.dumps(self.get_internal_links(), indent=2))
        
        # External links
        ttk.Label(links_frame, text="External Links (JSON format):").pack(anchor=tk.W, pady=(10, 0))
        self.external_links_text = scrolledtext.ScrolledText(links_frame, height=8)
        self.external_links_text.pack(fill=tk.X, pady=5)
        self.external_links_text.insert(tk.END, json.dumps(self.get_external_links(), indent=2))
        
        # Save button
        ttk.Button(scrollable_frame, text="Save Configuration", 
                  command=self.save_configuration, style="Accent.TButton").pack(pady=20)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status label
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Copyright label in the center
        self.copyright_label = ttk.Label(
            self.status_bar, 
            text="© 2025 AryanVBW | github.com/AryanVBW",
            font=('TkDefaultFont', 8),
            foreground='#666666',
            cursor='hand2'
        )
        self.copyright_label.pack(side=tk.LEFT, expand=True, padx=20)
        
        # Make copyright label clickable
        self.copyright_label.bind("<Button-1>", self.open_github_link)
        
        # Time label
        self.time_label = ttk.Label(self.status_bar, text="")
        self.time_label.pack(side=tk.RIGHT, padx=10)
        
        # Connection indicator
        self.connection_indicator = ttk.Label(self.status_bar, text="●", foreground="red")
        self.connection_indicator.pack(side=tk.RIGHT, padx=10)
        
        # Update time every second
        self.update_time()
        
    def open_github_link(self, event):
        """Open GitHub link when copyright is clicked"""
        try:
            webbrowser.open("https://github.com/AryanVBW")
            self.logger.info("Opened GitHub link in browser")
        except Exception as e:
            self.logger.error(f"Error opening GitHub link: {e}")
            messagebox.showinfo("GitHub", "Visit: https://github.com/AryanVBW")
        
    def apply_theme(self):
        """Apply a modern theme to the GUI"""
        style = ttk.Style()
        
        # Use a modern theme if available
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
            
        # Configure custom styles
        style.configure("Accent.TButton", foreground="white", background="#0078d4")
        style.map("Accent.TButton", 
                 background=[('active', '#106ebe'), ('pressed', '#005a9e')])
        
    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
        
    def process_log_queue(self):
        """Process log messages from queue"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.add_log_message(message)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_log_queue)
            
    def add_log_message(self, message):
        """Add log message to the logs text area"""
        self.logs_text.insert(tk.END, message + "\n")
        
        # Apply color based on log level
        if "ERROR" in message:
            start_line = self.logs_text.index(tk.END + "-2l")
            end_line = self.logs_text.index(tk.END + "-1l")
            self.logs_text.tag_add("ERROR", start_line, end_line)
        elif "WARNING" in message:
            start_line = self.logs_text.index(tk.END + "-2l")  
            end_line = self.logs_text.index(tk.END + "-1l")
            self.logs_text.tag_add("WARNING", start_line, end_line)
        elif "INFO" in message:
            start_line = self.logs_text.index(tk.END + "-2l")
            end_line = self.logs_text.index(tk.END + "-1l") 
            self.logs_text.tag_add("INFO", start_line, end_line)
            
        # Auto-scroll to bottom
        self.logs_text.see(tk.END)
        
        # Update status bar
        if "ERROR" in message:
            self.status_label.config(text="Error occurred - check logs")
        elif "Starting" in message:
            self.status_label.config(text="Automation running...")
        elif "Completed" in message:
            self.status_label.config(text="Automation completed")
            
    def install_requirements(self):
        """Install missing Python requirements"""
        try:
            import subprocess
            import sys
            
            requirements = [
                "selenium",
                "webdriver-manager", 
                "requests",
                "beautifulsoup4"
            ]
            
            for req in requirements:
                self.logger.info(f"Installing {req}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", req])
                
            messagebox.showinfo("Success", "Requirements installed successfully! Please restart the application.")
            
        except Exception as e:
            self.logger.error(f"Error installing requirements: {e}")
            messagebox.showerror("Error", f"Failed to install requirements: {e}")
            
    def test_connection(self):
        """Test WordPress connection"""
        try:
            wp_url = self.wp_url_var.get().strip()
            username = self.username_var.get().strip()
            password = self.password_var.get().strip()
            
            if not all([wp_url, username, password]):
                messagebox.showerror("Error", "Please fill in all WordPress credentials")
                return
                
            # Test API endpoint
            auth = HTTPBasicAuth(username, password)
            test_url = f"{wp_url}/posts"
            
            response = requests.get(test_url, auth=auth, timeout=10)
            
            if response.status_code == 200:
                self.connection_status.config(text="✅ Connected successfully", foreground="green")
                self.connection_indicator.config(foreground="green")
                self.logger.info("WordPress connection test successful")
                return True
            else:
                self.connection_status.config(text=f"❌ Connection failed ({response.status_code})", foreground="red")
                self.logger.error(f"Connection test failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.connection_status.config(text=f"❌ Connection error: {str(e)}", foreground="red")
            self.logger.error(f"Connection test error: {e}")
            return False
            
    def login(self):
        """Login and save credentials"""
        if self.test_connection():
            # Save configuration
            self.config.update({
                'wp_base_url': self.wp_url_var.get().strip(),
                'wp_username': self.username_var.get().strip(), 
                'wp_password': self.password_var.get().strip(),
                'gemini_api_key': self.gemini_key_var.get().strip()
            })
            
            self.save_config()
            self.is_logged_in = True
            
            # Initialize automation engine
            try:
                self.automation_engine = BlogAutomationEngine(self.config, self.logger)
                self.logger.info("Automation engine initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize automation engine: {e}")
                messagebox.showerror("Error", f"Failed to initialize automation engine: {e}")
                return
            
            self.logger.info("Login successful and configuration saved")
            messagebox.showinfo("Success", "Login successful! You can now use the automation features.")
            
            # Switch to automation tab
            self.notebook.select(1)
        else:
            messagebox.showerror("Error", "Login failed. Please check your credentials.")
            
    def save_configuration(self):
        """Save configuration from config tab"""
        try:
            # Update basic config
            self.config.update({
                'source_url': self.config_source_url.get(),
                'article_selector': self.config_selector.get(),
                'timeout': self.config_timeout.get(),
                'headless_mode': self.config_headless.get()
            })
            
            # Parse and save link configurations
            try:
                internal_links = json.loads(self.internal_links_text.get(1.0, tk.END))
                external_links = json.loads(self.external_links_text.get(1.0, tk.END))
                
                self.config['internal_links'] = internal_links
                self.config['external_links'] = external_links
                
            except json.JSONDecodeError as e:
                messagebox.showerror("Error", f"Invalid JSON format in links configuration: {e}")
                return
                
            self.save_config()
            messagebox.showinfo("Success", "Configuration saved successfully!")
            self.logger.info("Configuration updated and saved")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
            self.logger.error(f"Error saving configuration: {e}")
            
    def clear_logs(self):
        """Clear the logs text area"""
        self.logs_text.delete(1.0, tk.END)
        self.initialize_steps()
        
    def save_logs(self):
        """Save logs to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write(self.logs_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Logs saved to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save logs: {e}")
            
    def update_step_status(self, step_index, status, details="", elapsed_time=""):
        """Update status of a specific step"""
        try:
            if step_index < len(self.process_steps):
                item_id = str(step_index)
                step_name = self.process_steps[step_index]
                
                # Status emojis
                status_emojis = {
                    'pending': '⏳',
                    'running': '🔄',
                    'completed': '✅',
                    'error': '❌',
                    'skipped': '⏭️'
                }
                
                display_status = f"{status_emojis.get(status, '❓')} {status.title()}"
                
                # Update the treeview item
                self.steps_tree.item(item_id, values=(step_name, display_status, details, elapsed_time))
                
                # Scroll to current step
                self.steps_tree.see(item_id)
                
        except Exception as e:
            self.logger.error(f"Error updating step status: {e}")
            
    def start_automation(self):
        """Start the automation process"""
        if not self.is_logged_in:
            messagebox.showerror("Error", "Please login first")
            self.notebook.select(0)  # Switch to login tab
            return
            
        if not SELENIUM_AVAILABLE:
            messagebox.showerror("Error", "Selenium is not available. Please install requirements first.")
            return
            
        # Reset state
        self.stop_flag = False
        self.processed_count = 0
        self.total_articles = self.max_articles_var.get()
        
        # Update UI
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.task_progress.start()
        
        # Initialize progress
        self.overall_progress['maximum'] = self.total_articles
        self.overall_progress['value'] = 0
        self.initialize_steps()
        
        # Start automation in separate thread
        self.current_task = threading.Thread(target=self.run_automation)
        self.current_task.daemon = True
        self.current_task.start()
        
        self.logger.info("Starting automation process...")
        
    def stop_automation(self):
        """Stop the automation process"""
        self.stop_flag = True
        self.task_progress.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.logger.info("Automation stopped by user")
        
    def run_automation(self):
        """Main automation process"""
        try:
            if not self.automation_engine:
                self.logger.error("Automation engine not initialized")
                self.automation_completed()
                return
                
            # Initialize
            self.update_step_status(0, 'running', 'Fetching article links from source...')
            
            # Get article links using the automation engine
            article_links = self.automation_engine.get_article_links(limit=20)
            if not article_links:
                self.update_step_status(0, 'error', 'No article links found - check source URL and selector')
                self.logger.error(f"❌ Failed to find articles from: {self.automation_engine.config.get('source_url', 'N/A')}")
                self.logger.error(f"❌ Using selector: {self.automation_engine.config.get('article_selector', 'N/A')}")
                self.automation_completed()
                return
                
            self.update_step_status(0, 'completed', f'Found {len(article_links)} articles')
            self.total_articles = min(len(article_links), self.max_articles_var.get())
            self.overall_progress['maximum'] = self.total_articles
            
            # Load posted links to avoid duplicates
            posted_links = self.automation_engine.load_posted_links()
            
            # Process each article
            for i, link in enumerate(article_links):
                if self.stop_flag or i >= self.max_articles_var.get():
                    break
                    
                if link in posted_links:
                    self.logger.info(f"Skipping already posted article: {link}")
                    continue
                    
                self.logger.info(f"Processing article {i+1}/{self.total_articles}: {link}")
                self.current_task_label.config(text=f"Processing article {i+1}")
                
                # Process single article
                success = self.process_single_article(link)
                
                if success:
                    self.processed_count += 1
                    posted_links.add(link)
                    self.automation_engine.save_posted_links(posted_links)
                    
                # Update progress
                self.overall_progress['value'] = i + 1
                self.articles_count_label.config(text=f"Articles: {self.processed_count}/{self.total_articles}")
                
            self.automation_completed()
            
        except Exception as e:
            self.logger.error(f"Automation error: {e}")
            self.automation_completed()
            
    def process_single_article(self, article_url):
        """Process a single article through the complete pipeline"""
        if not self.automation_engine:
            self.logger.error("Automation engine not initialized")
            return False
            
        try:
            start_time = time.time()
            
            # Step 1: Extract article content
            self.update_step_status(1, 'running', f'Extracting content from {article_url[:50]}...')
            
            with self.automation_engine.get_selenium_driver_context() as driver:
                if not driver:
                    self.update_step_status(1, 'error', 'Failed to initialize WebDriver')
                    return False
                    
                title, content = self.automation_engine.extract_article_with_selenium(driver, article_url)
                
                if not title or not content:
                    self.update_step_status(1, 'error', 'Failed to extract content')
                    return False
                    
            elapsed = f"{time.time() - start_time:.1f}s"
            self.update_step_status(1, 'completed', f'Extracted {len(content)} characters', elapsed)
            
            # Step 2: Paraphrase with Gemini
            step_start = time.time()
            self.update_step_status(2, 'running', 'Paraphrasing content with Gemini AI...')
            
            paraphrased_content, paraphrased_title = self.automation_engine.gemini_paraphrase_content_and_title(title, content)
            if not paraphrased_content:
                self.update_step_status(2, 'error', 'Gemini paraphrasing failed')
                return False
                
            elapsed = f"{time.time() - step_start:.1f}s"
            self.update_step_status(2, 'completed', 'Content paraphrased successfully', elapsed)
            
            # Step 3: Inject internal links
            step_start = time.time()
            self.update_step_status(3, 'running', 'Injecting internal links...')
            
            internal_linked = self.automation_engine.inject_internal_links(paraphrased_content)
            elapsed = f"{time.time() - step_start:.1f}s"
            self.update_step_status(3, 'completed', 'Internal links added', elapsed)
            
            # Step 4: Inject external links
            step_start = time.time()
            self.update_step_status(4, 'running', 'Injecting external links...')
            
            final_content = self.automation_engine.inject_external_links(internal_linked)
            elapsed = f"{time.time() - step_start:.1f}s"
            self.update_step_status(4, 'completed', 'External links added', elapsed)
            
            # Step 5: Generate SEO metadata
            step_start = time.time()
            self.update_step_status(5, 'running', 'Generating SEO title and meta description...')
            
            seo_title, meta_description = self.automation_engine.generate_seo_title_and_meta(paraphrased_title, final_content)
            elapsed = f"{time.time() - step_start:.1f}s"
            self.update_step_status(5, 'completed', f'SEO title: {len(seo_title)} chars', elapsed)
            
            # Step 6: Extract keyphrases
            step_start = time.time()
            self.update_step_status(6, 'running', 'Extracting focus keyphrase and additional keyphrases...')
            
            focus_keyphrase, additional_keyphrases = self.automation_engine.extract_keyphrases_with_gemini(paraphrased_title, final_content)
            elapsed = f"{time.time() - step_start:.1f}s"
            keyphrase_count = 1 + len(additional_keyphrases) if focus_keyphrase else len(additional_keyphrases)
            self.update_step_status(6, 'completed', f'Extracted {keyphrase_count} keyphrases', elapsed)
            
            # Step 7: Detect categories
            step_start = time.time()
            self.update_step_status(7, 'running', 'Detecting categories...')
            
            categories = self.automation_engine.detect_categories(paraphrased_title + " " + final_content)
            elapsed = f"{time.time() - step_start:.1f}s"
            self.update_step_status(7, 'completed', f'Found {len(categories)} categories', elapsed)
            
            # Step 8: Generate tags
            step_start = time.time()
            self.update_step_status(8, 'running', 'Generating tags...')
            
            tags = self.automation_engine.generate_tags_with_gemini(final_content)
            elapsed = f"{time.time() - step_start:.1f}s"
            self.update_step_status(8, 'completed', f'Generated {len(tags)} tags', elapsed)
            
            # Step 9: Create WordPress post
            step_start = time.time()
            self.update_step_status(9, 'running', 'Creating WordPress post...')
            
            post_id, final_seo_title = self.automation_engine.post_to_wordpress_with_seo(
                title=paraphrased_title,
                content=final_content,
                categories=categories,
                tags=tags,
                seo_title=seo_title,
                meta_description=meta_description,
                focus_keyphrase=focus_keyphrase,
                additional_keyphrases=additional_keyphrases
            )
            
            if not post_id:
                self.update_step_status(9, 'error', 'Failed to create WordPress post')
                return False
                
            elapsed = f"{time.time() - step_start:.1f}s"
            self.update_step_status(9, 'completed', f'Post created (ID: {post_id})', elapsed)
            
            # Step 10: Finalize
            self.update_step_status(10, 'completed', f'Article processing completed in {time.time() - start_time:.1f}s')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing article: {e}")
            return False
            
    def automation_completed(self):
        """Called when automation is completed"""
        self.task_progress.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.current_task_label.config(text=f"Completed - {self.processed_count} articles processed")
        
        if self.processed_count > 0:
            self.logger.info(f"🎉 Automation completed successfully! {self.processed_count} articles processed.")
            messagebox.showinfo("Success", f"Automation completed!\n\n{self.processed_count} articles were processed and posted to WordPress.")
        else:
            self.logger.warning("⚠️ No articles were processed.")
            
            # Provide more detailed error information
            config = getattr(self.automation_engine, 'config', {})
            source_url = config.get('source_url', 'Not configured')
            selector = config.get('article_selector', 'Not configured')
            
            error_details = f"""No articles were processed. Possible issues:

🔗 Source URL: {source_url}
🎯 Article Selector: {selector}

Common solutions:
• Check if the source website is accessible
• Verify the article selector is correct
• Ensure you have internet connection
• Check logs for detailed error information

See the Logs tab for more technical details."""
            
            messagebox.showwarning("No Articles Processed", error_details)
            
    # Core automation methods (using automation engine)
    def get_internal_links(self):
        """Get default internal links configuration"""
        return {
            "Latest News": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/",
            "Transfer News": "https://premierleaguenewsnow.com/category/premier-league-football-news-now/premier-league-transfer-news-rumours/",
            "Arsenal": "https://premierleaguenewsnow.com/tag/arsenal-news-now/",
            "Liverpool": "https://premierleaguenewsnow.com/tag/liverpool-news-now/",
            "Manchester United": "https://premierleaguenewsnow.com/tag/manchester-united-news-now/",
            "Tottenham": "https://premierleaguenewsnow.com/tag/tottenham-hotspur-news-now/",
            "Chelsea": "https://premierleaguenewsnow.com/tag/chelsea-news-now/"
        }
        
    def get_external_links(self):
        """Get default external links configuration"""
        return {
            "premier league": "https://www.premierleague.com/",
            "tottenham": "https://tottenhaminsight.com/",
            "leeds united": "https://unitedleeds.com/",
            "stats": "https://fbref.com/en/",
            "transfer news": "https://www.transfermarkt.com/"
        }
    
    def test_configuration(self):
        """Test the current configuration to help debug issues"""
        if not self.automation_engine:
            messagebox.showerror("Error", "Automation engine not initialized. Please login first.")
            return
            
        def run_test():
            try:
                self.logger.info("🔍 Starting configuration test...")
                
                # Test article link extraction
                self.logger.info("Testing article link extraction...")
                article_links = self.automation_engine.get_article_links(limit=5)
                
                if article_links:
                    self.logger.info(f"✅ Successfully found {len(article_links)} articles")
                    for i, link in enumerate(article_links):
                        self.logger.info(f"  {i+1}. {link}")
                    
                    # Test content extraction from first article
                    self.logger.info("Testing content extraction from first article...")
                    with self.automation_engine.get_selenium_driver_context() as driver:
                        if driver:
                            title, content = self.automation_engine.extract_article_with_selenium(driver, article_links[0])
                            if title and content:
                                self.logger.info(f"✅ Successfully extracted content: {title[:60]}...")
                                messagebox.showinfo("Test Results", 
                                    f"✅ Configuration test passed!\n\n"
                                    f"Found {len(article_links)} articles\n"
                                    f"Successfully extracted content from: {title[:60]}...\n\n"
                                    f"Your configuration is working correctly!")
                            else:
                                self.logger.error("❌ Failed to extract content")
                                messagebox.showwarning("Test Results",
                                    f"⚠️ Found {len(article_links)} articles but failed to extract content.\n"
                                    f"Check Selenium setup and website structure.")
                        else:
                            self.logger.error("❌ Failed to initialize WebDriver")
                            messagebox.showerror("Test Results", 
                                "❌ Selenium WebDriver failed to initialize.\n"
                                "Please check Selenium installation.")
                else:
                    config = self.automation_engine.config
                    source_url = config.get('source_url', 'Not configured')
                    selector = config.get('article_selector', 'Not configured')
                    
                    self.logger.error("❌ No articles found")
                    messagebox.showerror("Test Results", 
                        f"❌ Configuration test failed!\n\n"
                        f"No articles found with current settings:\n"
                        f"• Source URL: {source_url}\n"
                        f"• Selector: {selector}\n\n"
                        f"Please check the Configuration tab and verify:\n"
                        f"1. Source URL is accessible\n"
                        f"2. Article selector matches the website structure\n\n"
                        f"Run the debug_articles.py script for more details.")
                        
            except Exception as e:
                self.logger.error(f"❌ Test failed: {e}")
                messagebox.showerror("Test Results", f"❌ Test failed with error:\n{e}")
        
        # Run test in separate thread to avoid blocking UI
        threading.Thread(target=run_test, daemon=True).start()
        
def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = BlogAutomationGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Set minimum window size
    root.minsize(1000, 700)
    
    # Handle window closing
    def on_closing():
        if app.current_task and app.current_task.is_alive():
            if messagebox.askokcancel("Quit", "Automation is running. Do you want to stop and quit?"):
                app.stop_automation()
                root.destroy()
        else:
            root.destroy()
            
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()
