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

class ToolTip:
    """
    Simple tooltip implementation for Tkinter widgets
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create a toplevel window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip, text=self.text, background="#ffffe0", 
                         relief="solid", borderwidth=1, padding=2)
        label.pack()
    
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class BlogAutomationGUI:
    def __init__(self, root):
        """Initialize the GUI"""
        self.root = root
        self.root.title("AUTO Blogger")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Set theme
        style = ttk.Style()
        style.theme_use('clam')  # Use a modern theme
        
        # Initialize variables
        self.log_queue = queue.Queue()
        self.automation_engine = None
        self.stop_requested = False
        self.processed_count = 0
        self.is_running = False
        
        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger('blog_automation')
        
        # Load configuration
        self.config = self.load_config()
        
        # Try to initialize automation engine if credentials exist
        if self.has_valid_credentials():
            try:
                self.automation_engine = BlogAutomationEngine(self.config, self.logger)
                self.logger.info("✅ Automation engine initialized on startup")
            except Exception as e:
                self.logger.error(f"Failed to initialize automation engine on startup: {e}")
        
        # Create UI
        self.create_ui()
        
        # Check prerequisites
        self.check_prerequisites()
        
        # Start log processing
        self.process_log_queue()
        
        # Add startup test logs to verify logging is working
        self.logger.info("🎯 AUTO Blogger GUI started successfully")
        self.logger.debug("🔧 Debug logging is working")
        self.logger.warning("⚠️ Warning logging is working")
        self.logger.error("❌ Error logging is working (this is just a test)")
        self.logger.info("📋 Check logs tab to view all application logs")
        
    def setup_logging(self):
        """Setup logging to capture all messages"""
        # Setup root logger to capture everything
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Setup our specific logger
        self.logger = logging.getLogger('BlogAutomation')
        self.logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create custom handler that sends to queue
        class QueueHandler(logging.Handler):
            def __init__(self, log_queue):
                super().__init__()
                self.log_queue = log_queue
                
            def emit(self, record):
                try:
                    msg = self.format(record)
                    self.log_queue.put(msg)
                except Exception:
                    pass  # Don't let logging errors break the app
        
        # Create file handler for persistent logging
        file_handler = logging.FileHandler('blog_automation.log')
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Create queue handler for GUI
        queue_handler = QueueHandler(self.log_queue)
        gui_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        queue_handler.setFormatter(gui_formatter)
        
        # Add handlers to root logger to catch everything
        root_logger.addHandler(file_handler)
        root_logger.addHandler(queue_handler)
        
        # Also add to our specific logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(queue_handler)
        
        # Log startup message
        self.logger.info("🚀 Logging system initialized - capturing all logs")
        
    def load_config(self):
        """Load configuration from file"""
        config = {}
        if os.path.exists("blog_config.json"):
            try:
                with open("blog_config.json", 'r') as f:
                    config = json.load(f)
                self.logger.info("Configuration loaded successfully")
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                config = {}
        else:
            config = self.get_default_config()
        return config
        
    def save_config(self):
        """Save configuration to file"""
        try:
            with open("blog_config.json", 'w') as f:
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
        
    def create_ui(self):
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
        self.wp_base_url_var = tk.StringVar(value=self.config.get('wp_base_url', ''))
        ttk.Entry(login_form, textvariable=self.wp_base_url_var, width=50).grid(row=0, column=1, pady=5, padx=10)
        
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
        
        # OpenAI API Key
        ttk.Label(login_form, text="OpenAI API Key:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.openai_key_var = tk.StringVar(value=self.config.get('openai_api_key', ''))
        ttk.Entry(login_form, textvariable=self.openai_key_var, show="*", width=50).grid(row=4, column=1, pady=5, padx=10)
        
        # Buttons frame
        button_frame = ttk.Frame(login_form)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
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
        self.connection_status.grid(row=6, column=0, columnspan=2, pady=10)
        
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
        
        # Force processing option
        self.force_processing_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="Force Processing (ignore history)", variable=self.force_processing_var).pack(side=tk.LEFT, padx=20)
        
        # Image generation options
        image_frame = ttk.LabelFrame(settings_frame, text="Featured Images", padding=10)
        image_frame.pack(side=tk.LEFT, padx=20, fill=tk.BOTH)
        
        self.image_source_var = tk.StringVar(value="none")
        
        # Radio buttons for image source selection
        ttk.Radiobutton(image_frame, text="No Images", variable=self.image_source_var, value="none").pack(anchor=tk.W)
        openai_radio = ttk.Radiobutton(image_frame, text="Generate with OpenAI DALL-E", variable=self.image_source_var, value="openai")
        openai_radio.pack(anchor=tk.W)
        getty_radio = ttk.Radiobutton(image_frame, text="Getty Images Editorial", variable=self.image_source_var, value="getty")
        getty_radio.pack(anchor=tk.W)
        
        # Add tooltips
        ToolTip(openai_radio, "Generates featured images using OpenAI DALL-E. Requires an OpenAI API key in the Authentication tab.")
        ToolTip(getty_radio, "Fetches editorial images from Getty Images and embeds them using standard Getty embed code. No API key required.")
        
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
            "Generating keyphrases",
            "Processing images",
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
        log_level_combo.bind('<<ComboboxSelected>>', self.on_log_level_change)
        
        ttk.Button(logs_toolbar, text="Save Logs", command=self.save_logs).pack(side=tk.RIGHT, padx=5)
        ttk.Button(logs_toolbar, text="Refresh", command=self.refresh_logs).pack(side=tk.RIGHT, padx=2)
        ttk.Button(logs_toolbar, text="Clear", command=self.clear_logs).pack(side=tk.RIGHT)
        
        # Logs text area
        self.logs_text = scrolledtext.ScrolledText(self.logs_frame, wrap=tk.WORD, height=25)
        self.logs_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Configure text tags for colored output
        self.logs_text.tag_configure("ERROR", foreground="red")
        self.logs_text.tag_configure("WARNING", foreground="orange")
        self.logs_text.tag_configure("INFO", foreground="blue")
        self.logs_text.tag_configure("DEBUG", foreground="gray")
        
        # Load existing logs from file
        self.load_existing_logs()
        
    def load_existing_logs(self):
        """Load existing logs from the log file"""
        try:
            if os.path.exists('blog_automation.log'):
                with open('blog_automation.log', 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Load last 500 lines to avoid overwhelming the GUI
                    recent_lines = lines[-500:] if len(lines) > 500 else lines
                    
                self.logs_text.insert(tk.END, "📋 Loading recent logs from blog_automation.log...\n\n")
                
                for line in recent_lines:
                    line = line.strip()
                    if line:  # Skip empty lines
                        self.add_log_message(line)
                        
                self.logs_text.insert(tk.END, "\n🔄 Real-time logs will appear below...\n")
                self.logs_text.see(tk.END)
                
                # Add separator
                separator = "=" * 80 + "\n"
                self.logs_text.insert(tk.END, separator)
                
        except Exception as e:
            self.logs_text.insert(tk.END, f"⚠️ Could not load existing logs: {e}\n")
            
    def refresh_logs(self):
        """Refresh logs by reloading from file"""
        self.logs_text.delete(1.0, tk.END)
        self.load_existing_logs()
        
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
        
        # Main config form
        config_form = ttk.LabelFrame(scrollable_frame, text="Configuration Settings", padding=20)
        config_form.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Source configuration
        source_frame = ttk.LabelFrame(config_form, text="Source Settings", padding=10)
        source_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(source_frame, text="Source URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.config_source_url = tk.StringVar(value=self.config.get('source_url', ''))
        ttk.Entry(source_frame, textvariable=self.config_source_url, width=50).grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(source_frame, text="Article Selector:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.config_selector = tk.StringVar(value=self.config.get('article_selector', ''))
        ttk.Entry(source_frame, textvariable=self.config_selector, width=50).grid(row=1, column=1, pady=5, padx=10)
        
        # Processing configuration
        proc_frame = ttk.LabelFrame(config_form, text="Processing Settings", padding=10)
        proc_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(proc_frame, text="Default Max Articles:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.config_max_articles = tk.IntVar(value=self.config.get('max_articles', 2))
        ttk.Spinbox(proc_frame, from_=1, to=20, textvariable=self.config_max_articles, width=10).grid(row=0, column=1, sticky=tk.W, pady=5, padx=10)
        
        ttk.Label(proc_frame, text="Timeout (seconds):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.config_timeout = tk.IntVar(value=self.config.get('timeout', 10))
        ttk.Spinbox(proc_frame, from_=5, to=60, textvariable=self.config_timeout, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        
        ttk.Label(proc_frame, text="Headless Mode:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.config_headless = tk.BooleanVar(value=self.config.get('headless_mode', True))
        ttk.Checkbutton(proc_frame, variable=self.config_headless).grid(row=2, column=1, sticky=tk.W, pady=5, padx=10)
        
        # Data management frame
        data_frame = ttk.LabelFrame(config_form, text="Data Management", padding=10)
        data_frame.pack(fill=tk.X, pady=10)
        
        # Add button to clear posted links history
        ttk.Label(data_frame, text="Posted Links:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        posted_links_count = 0
        try:
            if os.path.exists("posted_links.json"):
                with open("posted_links.json", "r") as f:
                    posted_links_count = len(json.load(f))
        except:
            pass
        
        posted_links_label = ttk.Label(data_frame, text=f"{posted_links_count} articles in history")
        posted_links_label.grid(row=0, column=1, sticky=tk.W, pady=5, padx=10)
        
        clear_links_btn = ttk.Button(data_frame, text="Clear History", 
                                   command=self.clear_posted_links)
        clear_links_btn.grid(row=0, column=2, sticky=tk.W, pady=5, padx=10)
        
        # Links configuration - create text areas for complex configs
        links_frame = ttk.LabelFrame(config_form, text="Links Configuration", padding=10)
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
        
        # Buttons
        button_frame = ttk.Frame(config_form)
        button_frame.pack(pady=20)
        
        save_btn = ttk.Button(button_frame, text="Save Configuration", 
                            command=self.save_configuration, style="Accent.TButton")
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", 
                              command=lambda: self.load_config())
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
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
        """Process log messages from the queue"""
        try:
            while not self.log_queue.empty():
                msg = self.log_queue.get_nowait()
                # Use the correct logs_text widget and add_log_message method
                if hasattr(self, 'logs_text'):
                    self.add_log_message(msg)
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Error processing log queue: {e}")
        finally:
            # Schedule to run again
            self.root.after(100, self.process_log_queue)
            
    def add_log_message(self, message):
        """Add log message to the logs text area with filtering and formatting"""
        if not hasattr(self, 'logs_text') or not self.logs_text:
            return
            
        # Get current log level setting
        current_level = self.log_level_var.get() if hasattr(self, 'log_level_var') else "INFO"
        
        # Determine message level
        message_level = "INFO"  # Default
        if "ERROR" in message:
            message_level = "ERROR"
        elif "WARNING" in message:
            message_level = "WARNING"
        elif "DEBUG" in message:
            message_level = "DEBUG"
        elif "INFO" in message:
            message_level = "INFO"
            
        # Level hierarchy: DEBUG < INFO < WARNING < ERROR
        level_hierarchy = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
        
        # Only show if message level is >= current filter level
        if level_hierarchy.get(message_level, 1) >= level_hierarchy.get(current_level, 1):
            # Add timestamp if not already present
            if not message.startswith('20'):  # Simple check for timestamp
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                message = f"{timestamp} - {message_level} - {message}"
            
            # Insert message
            self.logs_text.insert(tk.END, message + "\n")
            
            # Apply color based on log level
            start_line = self.logs_text.index(tk.END + "-2l")
            end_line = self.logs_text.index(tk.END + "-1l")
            
            if message_level == "ERROR":
                self.logs_text.tag_add("ERROR", start_line, end_line)
            elif message_level == "WARNING":
                self.logs_text.tag_add("WARNING", start_line, end_line)
            elif message_level == "INFO":
                self.logs_text.tag_add("INFO", start_line, end_line)
            elif message_level == "DEBUG":
                self.logs_text.tag_add("DEBUG", start_line, end_line)
                
            # Auto-scroll to bottom
            self.logs_text.see(tk.END)
            
            # Update status bar
            if hasattr(self, 'status_label'):
                if message_level == "ERROR":
                    self.status_label.config(text="❌ Error occurred - check logs")
                elif "Starting" in message or "🚀" in message:
                    self.status_label.config(text="🔄 Automation running...")
                elif "Completed" in message or "✅" in message:
                    self.status_label.config(text="✅ Automation completed")
                elif "Processing" in message:
                    self.status_label.config(text="📝 Processing articles...")
        
        # Limit log size to prevent memory issues
        lines = self.logs_text.get(1.0, tk.END).count('\n')
        if lines > 1000:  # Keep last 1000 lines
            self.logs_text.delete(1.0, f"{lines-1000}.0")
            
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
            wp_url = self.wp_base_url_var.get().strip()
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
        """Login and initialize automation engine"""
        try:
            # Update config with current values
            self.config.update({
                'wp_base_url': self.wp_base_url_var.get().strip(),
                'wp_username': self.username_var.get().strip(), 
                'wp_password': self.password_var.get().strip(),
                'gemini_api_key': self.gemini_key_var.get().strip(),
                'openai_api_key': self.openai_key_var.get().strip()
            })
            
            # Save to config file
            with open('blog_config.json', 'w') as f:
                json.dump(self.config, f, indent=4)
            
            self.logger.info("✅ Configuration saved")
            
            # Initialize automation engine
            self.automation_engine = BlogAutomationEngine(self.config, self.logger)
            
            # Update UI
            self.connection_status.config(text="Connected ✅", foreground="green")
            
            # Update source URL in automation tab if it exists
            if hasattr(self, 'config_source_url'):
                self.config_source_url.set(self.config.get('source_url', ''))
            
            # Update max articles in automation tab
            self.max_articles_var.set(self.config.get('max_articles', 2))
            
            # Switch to automation tab
            self.notebook.select(self.automation_frame)
            
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            self.connection_status.config(text=f"Connection failed: {str(e)}", foreground="red")
            messagebox.showerror("Login Failed", f"Could not initialize automation engine: {e}")
            
    def save_configuration(self):
        """Save configuration to file"""
        try:
            # Update config from UI
            self.config['source_url'] = self.config_source_url.get()
            self.config['article_selector'] = self.config_selector.get()
            self.config['timeout'] = self.config_timeout.get()
            self.config['headless_mode'] = self.config_headless.get()
            self.config['max_articles'] = self.config_max_articles.get()
            
            # Try to parse and update internal/external links
            try:
                internal_links = json.loads(self.internal_links_text.get("1.0", tk.END))
                if isinstance(internal_links, dict):
                    self.automation_engine.INTERNAL_LINKS = internal_links
            except:
                self.logger.error("Invalid JSON format for internal links")
                
            try:
                external_links = json.loads(self.external_links_text.get("1.0", tk.END))
                if isinstance(external_links, dict):
                    self.automation_engine.EXTERNAL_LINKS = external_links
            except:
                self.logger.error("Invalid JSON format for external links")
            
            # Save to file
            with open("blog_config.json", 'w') as f:
                json.dump(self.config, f, indent=2)
                
            # Update source URL in automation tab
            self.config_source_url.set(self.config['source_url'])
            
            # Update max articles in automation tab
            self.max_articles_var.set(self.config['max_articles'])
            
            self.logger.info("Configuration saved successfully")
            messagebox.showinfo("Success", "Configuration saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
            
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
        if self.is_running:
            messagebox.showwarning("Warning", "Automation is already running")
            return
        
        # Check if automation engine is initialized
        if not self.automation_engine:
            try:
                # Try to initialize it
                if self.has_valid_credentials():
                    self.automation_engine = BlogAutomationEngine(self.config, self.logger)
                    self.logger.info("✅ Automation engine initialized")
                else:
                    messagebox.showerror("Error", "Please login first in the Authentication tab")
                    self.notebook.select(self.login_frame)
                    return
            except Exception as e:
                self.logger.error(f"Failed to initialize automation engine: {e}")
                messagebox.showerror("Error", f"Failed to initialize automation engine: {e}")
                return
        
        # Get max articles
        max_articles = self.max_articles_var.get()
        if max_articles <= 0:
            messagebox.showerror("Error", "Please set a valid number of articles")
            return
        
        # Update UI
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.current_task_label.config(text="Running automation...")
        self.task_progress.start()
        
        # Reset counters
        self.processed_count = 0
        self.stop_requested = False
        self.is_running = True
        
        # Log automation start with details
        self.log_automation_start()
        
        # Initialize steps
        self.initialize_steps()
        
        # Start automation in a separate thread
        threading.Thread(target=self.run_automation, daemon=True).start()
        
    def stop_automation(self):
        """Stop the automation process"""
        self.stop_requested = True
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
            
            # Load posted links to avoid duplicates (unless force processing is enabled)
            posted_links = set()
            force_processing = self.force_processing_var.get()
            
            if not force_processing:
                posted_links = self.automation_engine.load_posted_links()
            
            # Check if all articles have already been processed
            new_articles = [link for link in article_links if link not in posted_links]
            
            if not new_articles and not force_processing:
                self.logger.warning("⚠️ All articles have already been processed.")
                self.logger.info("💡 Enable 'Force Processing' option to reprocess articles.")
                messagebox.showinfo("No New Articles", 
                    "All available articles have already been processed.\n\n"
                    "To reprocess articles, check the 'Force Processing' option in the Automation tab.")
                self.automation_completed()
                return
            
            # Use all articles if force processing, otherwise only new ones
            process_links = article_links if force_processing else new_articles
            
            self.total_articles = min(len(process_links), self.max_articles_var.get())
            self.overall_progress['maximum'] = self.total_articles
            
            if force_processing:
                self.logger.info(f"🔄 Force processing enabled - reprocessing {self.total_articles} articles")
            else:
                self.logger.info(f"✅ Found {len(new_articles)} new articles to process")
            
            # Process each article
            for i, link in enumerate(process_links):
                if self.stop_requested or i >= self.max_articles_var.get():
                    break
                    
                if link in posted_links and not force_processing:
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
        """Process a single article"""
        try:
            start_time = time.time()
            
            # Step 0: Fetch article links (already done)
            self.update_step_status(0, 'completed', f'URL: {article_url[:50]}...', '')
            
            # Step 1: Extract content
            step_start = time.time()
            self.update_step_status(1, 'running', 'Extracting content with Selenium...')
            
            with self.automation_engine.get_selenium_driver_context() as driver:
                if not driver:
                    self.update_step_status(1, 'error', 'Failed to initialize WebDriver')
                    return False
                    
                title, content = self.automation_engine.extract_article_with_selenium(driver, article_url)
                
            if not title or not content:
                self.update_step_status(1, 'error', 'Failed to extract content')
                return False
            
            elapsed = f"{time.time() - step_start:.1f}s"
            self.update_step_status(1, 'completed', f'Title: {title[:50]}...', elapsed)
            
            # Step 2: Paraphrase with Gemini
            step_start = time.time()
            self.update_step_status(2, 'running', 'Paraphrasing with Gemini AI...')
            
            paraphrased_content, paraphrased_title = self.automation_engine.gemini_paraphrase_content_and_title(title, content)
            elapsed = f"{time.time() - step_start:.1f}s"
            self.update_step_status(2, 'completed', f'New title: {paraphrased_title[:50]}...', elapsed)
            
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
            
            # Step 7: Handle images based on selected source
            image_source = self.image_source_var.get()
            media_id = None
            
            if image_source == "openai":
                step_start = time.time()
                self.update_step_status(7, 'running', 'Generating image with OpenAI...')
                
                # We'll set the media_id but post_id will be None until we create the post
                # We'll attach the image to the post later
                media_id = None  # Will be set after post creation
                elapsed = f"{time.time() - step_start:.1f}s"
                self.update_step_status(7, 'completed', 'Image generated', elapsed)
                
            elif image_source == "getty":
                step_start = time.time()
                self.update_step_status(7, 'running', 'Preparing Getty Images for featured image...')
                
                # For Getty Images, we'll set it as featured image after post creation
                # Just mark that we need to process Getty images later
                media_id = None  # Will be set after post creation
                elapsed = f"{time.time() - step_start:.1f}s"
                self.update_step_status(7, 'completed', 'Getty Images prepared', elapsed)
                
            else:
                self.update_step_status(7, 'skipped', 'No images selected', '')
            
            # Step 8: Detect categories
            step_start = time.time()
            self.update_step_status(8, 'running', 'Detecting categories...')
            
            categories = self.automation_engine.detect_categories(paraphrased_title + " " + final_content)
            elapsed = f"{time.time() - step_start:.1f}s"
            self.update_step_status(8, 'completed', f'Found {len(categories)} categories', elapsed)
            
            # Step 9: Generate tags
            step_start = time.time()
            self.update_step_status(9, 'running', 'Generating tags...')
            
            tags = self.automation_engine.generate_tags_with_gemini(final_content)
            elapsed = f"{time.time() - step_start:.1f}s"
            self.update_step_status(9, 'completed', f'Generated {len(tags)} tags', elapsed)
            
            # Step 10: Create WordPress post
            step_start = time.time()
            self.update_step_status(10, 'running', 'Creating WordPress post...')
            
            post_id, post_title = self.automation_engine.post_to_wordpress_with_seo(
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
                self.update_step_status(10, 'error', 'Failed to create WordPress post')
                return False
                
            elapsed = f"{time.time() - step_start:.1f}s"
            self.update_step_status(10, 'completed', f'Post created (ID: {post_id})', elapsed)
            
            # Step 7b: Now that we have a post ID, handle images based on selected source
            if image_source == "openai":
                step_start = time.time()
                self.update_step_status(7, 'running', 'Uploading OpenAI image and setting as featured...')
                
                media_id = self.automation_engine.generate_and_upload_featured_image(
                    paraphrased_title, 
                    final_content,
                    post_id
                )
                
                if media_id:
                    elapsed = f"{time.time() - step_start:.1f}s"
                    self.update_step_status(7, 'completed', f'OpenAI featured image set (ID: {media_id})', elapsed)
                else:
                    self.update_step_status(7, 'error', 'Failed to set OpenAI featured image')
                    
            elif image_source == "getty":
                step_start = time.time()
                self.update_step_status(7, 'running', 'Searching and downloading Getty Images...')
                
                media_id = self.automation_engine.generate_and_upload_getty_featured_image(
                    paraphrased_title, 
                    final_content,
                    post_id
                )
                
                if media_id:
                    elapsed = f"{time.time() - step_start:.1f}s"
                    self.update_step_status(7, 'completed', f'Getty featured image set (ID: {media_id})', elapsed)
                else:
                    self.update_step_status(7, 'error', 'Failed to set Getty featured image')
            
            # Step 11: Finalize
            self.update_step_status(11, 'completed', f'Article processing completed in {time.time() - start_time:.1f}s')
            
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
        
        # Calculate error count for logging
        error_count = getattr(self, 'error_count', 0) if hasattr(self, 'error_count') else 0
        
        # Log completion with summary
        self.log_automation_complete(self.processed_count, error_count)
        
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
        
    def clear_posted_links(self):
        """Clear the posted links history"""
        try:
            if os.path.exists("posted_links.json"):
                # Ask for confirmation
                confirm = messagebox.askyesno(
                    "Confirm Clear History",
                    "Are you sure you want to clear the posted links history?\n\n"
                    "This will allow all articles to be processed again, even if they were processed before.",
                    icon="warning"
                )
                
                if confirm:
                    # Create empty file
                    with open("posted_links.json", "w") as f:
                        json.dump([], f)
                    
                    self.logger.info("✅ Posted links history cleared")
                    messagebox.showinfo("Success", "Posted links history has been cleared.")
                    
                    # Refresh the configuration tab
                    self.notebook.select(self.config_frame)
                    self.create_config_tab()
        except Exception as e:
            self.logger.error(f"Error clearing posted links: {e}")
            messagebox.showerror("Error", f"Failed to clear posted links: {e}")

    def has_valid_credentials(self):
        """Check if valid credentials exist in the config"""
        required_fields = ['wp_base_url', 'wp_username', 'wp_password', 'gemini_api_key']
        return all(field in self.config and self.config[field] for field in required_fields)

    def check_prerequisites(self):
        """Check system prerequisites"""
        # This is a placeholder for now
        pass

    def on_log_level_change(self, event=None):
        """Handle log level combo box change"""
        level = self.log_level_var.get()
        self.add_log_message(f"🔧 Log level changed to: {level}")
        
    def log_automation_start(self):
        """Log automation start with detailed info"""
        self.add_log_message("🚀 Starting blog automation...")
        self.add_log_message(f"📊 Configuration: Max articles={self.config.get('max_articles', 'N/A')}")
        self.add_log_message(f"🌐 Source URL: {self.config.get('source_url', 'N/A')}")
        self.add_log_message(f"📝 WordPress URL: {self.config.get('wp_base_url', 'N/A')}")
        image_source = getattr(self, 'image_source_var', None)
        if image_source:
            self.add_log_message(f"🖼️ Image source: {image_source.get()}")
            
    def log_automation_complete(self, success_count=0, error_count=0):
        """Log automation completion with summary"""
        self.add_log_message("🏁 Blog automation completed!")
        self.add_log_message(f"✅ Successfully processed: {success_count} articles")
        if error_count > 0:
            self.add_log_message(f"❌ Errors encountered: {error_count} articles")
        self.add_log_message("📋 Check logs above for detailed information")

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
        if app.is_running:
            if messagebox.askokcancel("Quit", "Automation is running. Are you sure you want to quit?"):
                app.stop_requested = True
                root.destroy()
        else:
            root.destroy()
            
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()
