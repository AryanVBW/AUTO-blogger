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
import glob
import copy

# Import the automation engine
try:
    from automation_engine import BlogAutomationEngine, SELENIUM_AVAILABLE
except ImportError:
    BlogAutomationEngine = None
    SELENIUM_AVAILABLE = False

# Import the CSS selector extractor
try:
    from css_selector_extractor import CSSelectorExtractor
except ImportError:
    CSSelectorExtractor = None

# Import the icon factory
try:
    from icon_factory import IconFactory
except ImportError:
    try:
        from auto_blogger.icon_factory import IconFactory
    except ImportError:
        IconFactory = None

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

class ModernPopup:
    """Beautiful custom popup dialogs with canvas-drawn vector icons.

    Supports: info, success, warning, error, confirm (yes/no).
    Icons are drawn programmatically — no image files needed.
    """

    # Color themes per popup type
    THEMES = {
        'success': {'accent': '#10b981', 'bg': '#ecfdf5', 'border': '#6ee7b7', 'title_bg': '#10b981',
                     'icon_bg': '#d1fae5', 'icon_fg': '#059669'},
        'info':    {'accent': '#3b82f6', 'bg': '#eff6ff', 'border': '#93c5fd', 'title_bg': '#3b82f6',
                     'icon_bg': '#dbeafe', 'icon_fg': '#2563eb'},
        'warning': {'accent': '#f59e0b', 'bg': '#fffbeb', 'border': '#fcd34d', 'title_bg': '#f59e0b',
                     'icon_bg': '#fef3c7', 'icon_fg': '#d97706'},
        'error':   {'accent': '#ef4444', 'bg': '#fef2f2', 'border': '#fca5a5', 'title_bg': '#ef4444',
                     'icon_bg': '#fee2e2', 'icon_fg': '#dc2626'},
        'confirm': {'accent': '#8b5cf6', 'bg': '#f5f3ff', 'border': '#c4b5fd', 'title_bg': '#8b5cf6',
                     'icon_bg': '#ede9fe', 'icon_fg': '#7c3aed'},
    }

    @staticmethod
    def _draw_icon(canvas, popup_type, size=40):
        """Draw a vector icon on a tkinter Canvas.

        Each icon is hand-drawn with canvas primitives for crisp rendering at any size.
        """
        cx, cy = size / 2, size / 2
        r = size * 0.42  # circle radius
        theme = ModernPopup.THEMES[popup_type]
        fg = theme['icon_fg']
        bg = theme['icon_bg']

        # Background circle
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=bg, outline=fg, width=2)

        if popup_type == 'success':
            # Checkmark
            pts = [cx - r * 0.35, cy + r * 0.05,
                   cx - r * 0.08, cy + r * 0.35,
                   cx + r * 0.38, cy - r * 0.30]
            canvas.create_line(*pts, fill=fg, width=3, capstyle='round', joinstyle='round')

        elif popup_type == 'info':
            # "i" letter — dot + line
            dot_r = r * 0.10
            canvas.create_oval(cx - dot_r, cy - r * 0.45 - dot_r, cx + dot_r, cy - r * 0.45 + dot_r,
                               fill=fg, outline=fg)
            canvas.create_line(cx, cy - r * 0.18, cx, cy + r * 0.42, fill=fg, width=2.5, capstyle='round')

        elif popup_type == 'warning':
            # Exclamation mark — line + dot
            canvas.create_line(cx, cy - r * 0.42, cx, cy + r * 0.12, fill=fg, width=2.5, capstyle='round')
            dot_r = r * 0.10
            canvas.create_oval(cx - dot_r, cy + r * 0.30 - dot_r, cx + dot_r, cy + r * 0.30 + dot_r,
                               fill=fg, outline=fg)

        elif popup_type == 'error':
            # X cross
            off = r * 0.28
            canvas.create_line(cx - off, cy - off, cx + off, cy + off, fill=fg, width=2.5, capstyle='round')
            canvas.create_line(cx + off, cy - off, cx - off, cy + off, fill=fg, width=2.5, capstyle='round')

        elif popup_type == 'confirm':
            # Question mark — arc + dot
            canvas.create_arc(cx - r * 0.28, cy - r * 0.50, cx + r * 0.28, cy + r * 0.05,
                              start=0, extent=180, style='arc', outline=fg, width=2.5)
            canvas.create_line(cx, cy + r * 0.05, cx, cy + r * 0.18, fill=fg, width=2.5, capstyle='round')
            dot_r = r * 0.09
            canvas.create_oval(cx - dot_r, cy + r * 0.32 - dot_r, cx + dot_r, cy + r * 0.32 + dot_r,
                               fill=fg, outline=fg)

    @staticmethod
    def _draw_close_icon(canvas, size=14):
        """Draw an X close icon on a canvas."""
        m = 3  # margin
        canvas.create_line(m, m, size - m, size - m, fill='#ffffff', width=2, capstyle='round')
        canvas.create_line(size - m, m, m, size - m, fill='#ffffff', width=2, capstyle='round')

    @staticmethod
    def _create(parent, title, message, popup_type='info', auto_close_ms=0, on_result=None):
        """Create and display a modern popup dialog with drawn icons."""
        theme = ModernPopup.THEMES.get(popup_type, ModernPopup.THEMES['info'])
        result = [None]

        dialog = tk.Toplevel(parent)
        dialog.withdraw()
        dialog.title(title)
        dialog.overrideredirect(True)
        dialog.configure(bg=theme['border'])
        dialog.attributes('-topmost', True)

        # Outer border frame
        outer = tk.Frame(dialog, bg=theme['border'], padx=2, pady=2)
        outer.pack(fill=tk.BOTH, expand=True)

        # Main container
        container = tk.Frame(outer, bg='#ffffff')
        container.pack(fill=tk.BOTH, expand=True)

        # ── Title bar ──
        title_bar = tk.Frame(container, bg=theme['title_bg'], height=46)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)

        # Small icon in title bar (drawn on canvas)
        title_icon_canvas = tk.Canvas(title_bar, width=28, height=28,
                                       bg=theme['title_bg'], highlightthickness=0)
        title_icon_canvas.pack(side=tk.LEFT, padx=(12, 4), pady=9)
        # Draw a mini white-on-accent icon
        mini_r = 11
        title_icon_canvas.create_oval(14 - mini_r, 14 - mini_r, 14 + mini_r, 14 + mini_r,
                                       fill='', outline='#ffffff', width=1.5)
        if popup_type == 'success':
            title_icon_canvas.create_line(8, 14.5, 12, 18.5, 20, 9.5,
                                           fill='#ffffff', width=2, capstyle='round', joinstyle='round')
        elif popup_type == 'info':
            title_icon_canvas.create_oval(13, 6, 15, 8, fill='#ffffff', outline='#ffffff')
            title_icon_canvas.create_line(14, 11, 14, 21, fill='#ffffff', width=2, capstyle='round')
        elif popup_type == 'warning':
            title_icon_canvas.create_line(14, 7, 14, 16, fill='#ffffff', width=2, capstyle='round')
            title_icon_canvas.create_oval(13, 19, 15, 21, fill='#ffffff', outline='#ffffff')
        elif popup_type == 'error':
            title_icon_canvas.create_line(9, 9, 19, 19, fill='#ffffff', width=2, capstyle='round')
            title_icon_canvas.create_line(19, 9, 9, 19, fill='#ffffff', width=2, capstyle='round')
        elif popup_type == 'confirm':
            title_icon_canvas.create_arc(9, 5, 19, 15, start=0, extent=180,
                                          style='arc', outline='#ffffff', width=2)
            title_icon_canvas.create_line(14, 15, 14, 17, fill='#ffffff', width=2, capstyle='round')
            title_icon_canvas.create_oval(13, 19, 15, 21, fill='#ffffff', outline='#ffffff')

        # Title text
        title_label = tk.Label(
            title_bar, text=title,
            bg=theme['title_bg'], fg='#ffffff',
            font=('Helvetica', 13, 'bold'), anchor='w'
        )
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Close button (drawn X icon)
        close_canvas = tk.Canvas(title_bar, width=28, height=28,
                                  bg=theme['title_bg'], highlightthickness=0, cursor='hand2')
        close_canvas.pack(side=tk.RIGHT, padx=(0, 8), pady=9)
        # Draw X
        close_canvas.create_line(8, 8, 20, 20, fill='#ffffff', width=2, capstyle='round')
        close_canvas.create_line(20, 8, 8, 20, fill='#ffffff', width=2, capstyle='round')

        def close_dialog(confirm_result=None):
            if confirm_result is not None:
                result[0] = confirm_result
            try:
                dialog.destroy()
            except tk.TclError:
                pass

        close_canvas.bind('<Button-1>', lambda e: close_dialog(False if popup_type == 'confirm' else None))
        close_canvas.bind('<Enter>', lambda e: close_canvas.configure(bg='#ffffff') or
                          [close_canvas.itemconfigure(i, fill=theme['title_bg']) for i in close_canvas.find_all()])
        close_canvas.bind('<Leave>', lambda e: close_canvas.configure(bg=theme['title_bg']) or
                          [close_canvas.itemconfigure(i, fill='#ffffff') for i in close_canvas.find_all()])

        # Make title bar draggable
        drag_data = {'x': 0, 'y': 0}
        def start_drag(event):
            drag_data['x'] = event.x
            drag_data['y'] = event.y
        def do_drag(event):
            x = dialog.winfo_x() + event.x - drag_data['x']
            y = dialog.winfo_y() + event.y - drag_data['y']
            dialog.geometry(f"+{x}+{y}")
        for w in (title_bar, title_label, title_icon_canvas):
            w.bind('<Button-1>', start_drag)
            w.bind('<B1-Motion>', do_drag)

        # ── Body area ──
        body = tk.Frame(container, bg=theme['bg'], padx=24, pady=20)
        body.pack(fill=tk.BOTH, expand=True)

        # Icon + Message row
        content_row = tk.Frame(body, bg=theme['bg'])
        content_row.pack(fill=tk.BOTH, expand=True, pady=(0, 16))

        # Large body icon (drawn on canvas)
        icon_size = 48
        icon_canvas = tk.Canvas(content_row, width=icon_size, height=icon_size,
                                 bg=theme['bg'], highlightthickness=0)
        icon_canvas.pack(side=tk.LEFT, padx=(0, 16), anchor='n', pady=(2, 0))
        ModernPopup._draw_icon(icon_canvas, popup_type, size=icon_size)

        # Message text
        msg_label = tk.Label(
            content_row, text=message,
            bg=theme['bg'], fg='#1f2937',
            font=('Helvetica', 11),
            wraplength=380, justify=tk.LEFT, anchor='nw'
        )
        msg_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ── Button area ──
        btn_frame = tk.Frame(body, bg=theme['bg'])
        btn_frame.pack(fill=tk.X)

        def make_button(parent_frame, text, command, primary=False):
            bg_color = theme['accent'] if primary else '#e5e7eb'
            fg_color = '#ffffff' if primary else '#374151'
            hover_bg = theme['border'] if primary else '#d1d5db'

            btn = tk.Label(
                parent_frame, text=f'  {text}  ',
                bg=bg_color, fg=fg_color,
                font=('Helvetica', 11, 'bold' if primary else 'normal'),
                cursor='hand2', padx=20, pady=8, relief='flat',
            )
            btn.pack(side=tk.RIGHT, padx=(8, 0))
            btn.bind('<Button-1>', lambda e: command())
            btn.bind('<Enter>', lambda e: btn.configure(bg=hover_bg))
            btn.bind('<Leave>', lambda e: btn.configure(bg=bg_color))
            return btn

        if popup_type == 'confirm':
            make_button(btn_frame, 'No', lambda: close_dialog(False), primary=False)
            make_button(btn_frame, 'Yes', lambda: close_dialog(True), primary=True)
        else:
            make_button(btn_frame, 'OK', lambda: close_dialog(), primary=True)

        # Auto-close timer
        if auto_close_ms > 0 and popup_type != 'confirm':
            remaining = [auto_close_ms // 1000]
            timer_label = tk.Label(btn_frame, text=f"Auto-close in {remaining[0]}s",
                                   bg=theme['bg'], fg='#9ca3af', font=('Helvetica', 9))
            timer_label.pack(side=tk.LEFT)

            def tick():
                remaining[0] -= 1
                if remaining[0] <= 0:
                    close_dialog()
                else:
                    timer_label.config(text=f"Auto-close in {remaining[0]}s")
                    dialog.after(1000, tick)
            dialog.after(1000, tick)

        # Size and center
        dialog.update_idletasks()
        w = max(dialog.winfo_reqwidth(), 420)
        h = dialog.winfo_reqheight()
        px = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
        py = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
        dialog.geometry(f"{w}x{h}+{px}+{py}")
        dialog.deiconify()

        # Keyboard
        dialog.bind('<Return>', lambda e: close_dialog(True if popup_type == 'confirm' else None))
        dialog.bind('<Escape>', lambda e: close_dialog(False if popup_type == 'confirm' else None))

        dialog.focus_force()
        dialog.grab_set()
        parent.wait_window(dialog)
        return result[0]

    @staticmethod
    def showinfo(parent, title, message, auto_close_ms=0):
        """Show an info popup (auto-detects success theme for success-like titles)"""
        ptype = 'success' if any(w in title.lower() for w in ['success', 'saved', 'complete', 'done']) else 'info'
        return ModernPopup._create(parent, title, message, popup_type=ptype, auto_close_ms=auto_close_ms)

    @staticmethod
    def showwarning(parent, title, message, auto_close_ms=0):
        """Show a warning popup"""
        return ModernPopup._create(parent, title, message, popup_type='warning', auto_close_ms=auto_close_ms)

    @staticmethod
    def showerror(parent, title, message, auto_close_ms=0):
        """Show an error popup"""
        return ModernPopup._create(parent, title, message, popup_type='error', auto_close_ms=auto_close_ms)

    @staticmethod
    def askyesno(parent, title, message):
        """Show a confirm (yes/no) popup. Returns True or False."""
        return ModernPopup._create(parent, title, message, popup_type='confirm')


class BlogAutomationGUI:
    def __init__(self, root):
        """Initialize the GUI"""
        self.root = root
        self.root.title("AUTO Blogger")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Additional macOS-specific window enhancements
        try:
            # Set window class for better dock integration (if available)
            if hasattr(self.root, 'wm_class'):
                self.root.wm_class("AUTO Blogger", "AUTO Blogger")
            
            # Set application name for macOS dock
            import platform
            if platform.system() == "Darwin":  # macOS
                # Try to set bundle identifier for better app identification
                try:
                    import subprocess
                    subprocess.run([
                        "defaults", "write", 
                        f"{os.path.expanduser('~')}/Library/Preferences/com.aryanvbw.autoblogger.plist",
                        "CFBundleName", "AUTO Blogger"
                    ], check=False)
                except:
                    pass  # Fail silently if we can't set bundle preferences
                    
                # Set application name in dock (if available)
                try:
                    self.root.call('::tk::mac::standardAboutPanel')
                except:
                    pass  # Not available in all Tk versions
                
        except Exception as e:
            # Don't let window enhancement errors break the app
            print(f"Note: Some window enhancements not available: {e}")
        
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
        
        # Domain-based configuration system
        self.base_config_dir = os.path.abspath("configs")
        self.current_domain = None
        self.domain_config_dir = None
        
        # Load initial configuration (will be set when user logs in)
        self.config_files = []
        self.active_config_name = "default"
        self.config = self.get_default_config()
        
        # Load main blog_config.json and synchronize active source
        self.load_main_config()
        
        # Try to initialize automation engine if credentials exist
        if self.has_valid_credentials():
            try:
                # Pass domain-specific config directory to automation engine
                domain_config_dir = self.get_current_config_dir()
                if hasattr(BlogAutomationEngine, '__init__'):
                    # Create temporary config with domain config dir
                    temp_config = self.config.copy()
                    temp_config['config_dir'] = domain_config_dir
                    self.automation_engine = BlogAutomationEngine(temp_config, self.logger)
                else:
                    self.automation_engine = BlogAutomationEngine(self.config, self.logger)
                self.logger.info("[OK] Automation engine initialized on startup")
            except Exception as e:
                self.logger.error(f"Failed to initialize automation engine on startup: {e}")
        
        # Initialize icon factory (must be before create_ui)
        if IconFactory:
            self.icons = IconFactory(self.root, size=16)
        else:
            self.icons = None

        # Create UI
        self.create_ui()
        
        # Check prerequisites
        self.check_prerequisites()
        
        # Start log processing
        self.process_log_queue()
        
        # Add startup logs to verify logging is working
        self.logger.info("AUTO Blogger GUI started successfully")
        self.logger.info(f"Configuration directory: {self.base_config_dir}")
        self.logger.debug("Debug logging is active")
        
        # Log system information
        import platform
        self.logger.info(f"System: {platform.system()} {platform.release()}")
        self.logger.info(f"Python: {platform.python_version()}")
        
        # Check and log Selenium availability
        try:
            from selenium import webdriver
            self.logger.info("[OK] Selenium WebDriver available")
        except ImportError:
            self.logger.warning("[!] Selenium not available - install with: pip install selenium webdriver-manager")
        
        # Log initial status
        self.logger.info("[>>] Application ready for use")
        self.logger.info("Check logs tab to view all application logs")
        
    def setup_logging(self):
        """Setup advanced session-based logging to capture all messages"""
        # Import the unified log manager
        try:
            from unified_log_manager import initialize_unified_logging, get_unified_log_manager
        except ImportError:
            # Fallback to basic logging if unified_log_manager not available
            self._setup_basic_logging()
            return
        
        # Initialize unified session-based logging
        self.log_manager = initialize_unified_logging()
        self.session_info = self.log_manager.get_session_info()
        
        # Setup our main logger
        self.logger = logging.getLogger('BlogAutomation')
        self.logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create custom handler that sends to queue AND session logs
        class SessionAwareQueueHandler(logging.Handler):
            def __init__(self, log_queue, log_manager):
                super().__init__()
                self.log_queue = log_queue
                self.log_manager = log_manager
                self._processing = False  # Prevent recursion
                
            def emit(self, record):
                # Prevent recursive logging
                if self._processing:
                    return
                    
                try:
                    self._processing = True
                    
                    # Format message for GUI queue
                    msg = self.format(record)
                    self.log_queue.put(msg)
                    
                    # Skip logging setup messages to prevent recursion
                    if 'Advanced logging system initialized' in record.getMessage():
                        return
                    
                    # Route to appropriate session logger
                    message = record.getMessage().lower()
                    
                    # Determine the best category for this log
                    if record.levelno >= logging.ERROR:
                        category_logger = self.log_manager.get_logger('errors')
                    elif 'automation' in message or 'processing' in message or 'article' in message:
                        category_logger = self.log_manager.get_logger('automation')
                    elif 'api' in message or 'request' in message or 'wordpress' in message:
                        category_logger = self.log_manager.get_logger('api')
                    elif 'security' in message or 'auth' in message or 'login' in message or 'credential' in message:
                        category_logger = self.log_manager.get_logger('security')
                    elif record.levelno == logging.DEBUG:
                        category_logger = self.log_manager.get_logger('debug')
                    else:
                        category_logger = self.log_manager.get_logger('main')
                    
                    # Log to session category directly, bypass the handler chain
                    if hasattr(category_logger, 'handle'):
                        category_logger.handle(record)
                    
                except Exception:
                    pass  # Don't let logging errors break the app
                finally:
                    self._processing = False
        
        # Create session-aware queue handler for GUI
        session_handler = SessionAwareQueueHandler(self.log_queue, self.log_manager)
        gui_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        session_handler.setFormatter(gui_formatter)
        
        # Add handler to our logger only (not root logger to avoid recursion)
        self.logger.addHandler(session_handler)
        
        # Don't propagate to root logger to avoid duplicate logs
        self.logger.propagate = False
        
        # Log startup message with session info (only once)
        self.logger.info(f"[>>] Unified logging system initialized - Session: {self.session_info['session_id']}")
        self.logger.info(f"Session logs in: {self.session_info['base_dir']}")
        self.logger.info(f"Unified log file: {self.session_info['unified_log_file']}")
        
    def _setup_basic_logging(self):
        """Fallback to basic logging if log_manager is not available"""
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
        self.logger.info("[>>] Basic logging system initialized - capturing all logs")
        
    def get_config_files(self):
        """Get configuration files from current domain directory"""
        config_dir = self.get_current_config_dir()
        files = glob.glob(os.path.join(config_dir, "*.json"))
        return [os.path.splitext(os.path.basename(f))[0] for f in files if not f.endswith(("style_prompt.json","category_keywords.json","internal_links.json","external_links.json","tag_synonyms.json","static_clubs.json","stop_words.json","do_follow_urls.json","openai_image_config.json","weights.json"))]

    def get_last_used_config(self):
        """Get last used configuration for current domain"""
        config_dir = self.get_current_config_dir()
        path = os.path.join(config_dir, ".last_used")
        if os.path.exists(path):
            with open(path) as f:
                return f.read().strip()
        return None

    def set_last_used_config(self, name):
        """Set last used configuration for current domain"""
        config_dir = self.get_current_config_dir()
        path = os.path.join(config_dir, ".last_used")
        with open(path, "w") as f:
            f.write(name)

    def load_config(self, name):
        """Load configuration from current domain directory"""
        import json, os
        config_dir = self.get_current_config_dir()
        path = os.path.join(config_dir, f"{name}.json")
        config = self.get_default_config()
        if os.path.exists(path):
            with open(path) as f:
                config.update(json.load(f))
        # Migrate from old files if missing
        migration_map = {
            "internal_links": "internal_links.json",
            "external_links": "external_links.json",
            "style_prompt": "style_prompt.json",
            "category_keywords": "category_keywords.json",
            "tag_synonyms": "tag_synonyms.json",
            "static_clubs": "static_clubs.json",
            "stop_words": "stop_words.json",
            "do_follow_urls": "do_follow_urls.json"
        }
        for key, fname in migration_map.items():
            if key not in config or not config[key]:
                fpath = os.path.join(config_dir, fname)
                if os.path.exists(fpath):
                    with open(fpath) as f:
                        if key == "style_prompt":
                            config[key] = json.load(f).get("style_prompt", "")
                        else:
                            config[key] = json.load(f)
        self.active_config_name = name
        self.set_last_used_config(name)
        return config
        
    def save_config(self, name=None):
        """Save configuration to current domain directory"""
        if name is None:
            name = self.active_config_name
        config_dir = self.get_current_config_dir()
        path = os.path.join(config_dir, f"{name}.json")
        with open(path, "w") as f:
                json.dump(self.config, f, indent=2)
        self.set_last_used_config(name)
        self.logger.info(f"Configuration '{name}' saved to domain directory: {self.current_domain}")
            
    def get_default_config(self):
        return {
            "source_url": "https://tbrfootball.com/topic/english-premier-league/",
            "article_selector": "article.article h2 a",
            "wp_base_url": "https://example-sports-site.com/wp-json/wp/v2",
            "wp_username": "",
            "wp_password": "",
            "gemini_api_key": "",
            "openai_api_key": "",
            "max_articles": 2,
            "timeout": 10,
            "headless_mode": True,
            "seo_plugin_version": "new",
            "internal_links": {},
            "external_links": {},
            "style_prompt": "",
            "category_keywords": {},
            "tag_synonyms": {},
            "static_clubs": [],
            "stop_words": [],
            "do_follow_urls": []
        }
        
    def load_main_config(self):
        """Load main blog_config.json and synchronize active source"""
        try:
            import json
            import os
            
            # Check if blog_config.json exists
            if os.path.exists('blog_config.json'):
                with open('blog_config.json', 'r') as f:
                    main_config = json.load(f)
                
                # Update config with values from main config file
                self.config.update(main_config)
                
                # Synchronize active source from source_urls array
                if 'source_urls' in main_config and main_config['source_urls']:
                    active_source = None
                    
                    # Find the active source
                    for source in main_config['source_urls']:
                        if source.get('active', False):
                            active_source = source
                            break
                    
                    # If no active source found, use the first one and set it as active
                    if not active_source and main_config['source_urls']:
                        active_source = main_config['source_urls'][0]
                        active_source['active'] = True
                        
                        # Update the source_urls array in config
                        for i, source in enumerate(main_config['source_urls']):
                            if i == 0:
                                source['active'] = True
                            else:
                                source['active'] = False
                        
                        # Save the updated configuration
                        self.config['source_urls'] = main_config['source_urls']
                        self.save_main_config()
                    
                    # Synchronize the main source_url and article_selector fields
                    if active_source:
                        self.config['source_url'] = active_source['url']
                        self.config['article_selector'] = active_source['selector']
                        
                        self.logger.info(f"[OK] Active source synchronized: {active_source['name']}")
                        self.logger.info(f"Source URL: {active_source['url']}")
                        self.logger.info(f"Selector: {active_source['selector']}")
                    else:
                        self.logger.warning("[!] No active source found in source_urls array")
                else:
                    self.logger.info("No source_urls array found in configuration")
                    
            else:
                self.logger.info("blog_config.json not found, using default configuration")
                
        except Exception as e:
            self.logger.error(f"[X] Error loading main configuration: {e}")
            
    def save_main_config(self):
        """Save the main blog_config.json file"""
        try:
            import json
            with open('blog_config.json', 'w') as f:
                json.dump(self.config, f, indent=4)
            self.logger.info("[OK] Main configuration saved to blog_config.json")
        except Exception as e:
            self.logger.error(f"[X] Error saving main configuration: {e}")
        
    def _icon(self, name: str, size: int = 16, color: str = ''):
        """Get a named icon from the factory. Returns None if unavailable."""
        if self.icons:
            return self.icons.get(name, size=size, color=color)
        return None

    def _icon_opts(self, name: str, text: str, size: int = 16, color: str = ''):
        """Return dict of image/text/compound options for a widget, with fallback to plain text."""
        icon = self._icon(name, size, color)
        if icon:
            return {'text': f' {text}', 'image': icon, 'compound': 'left'}
        return {'text': text}

    def _add_tab(self, frame, text: str, icon_name: str):
        """Add a tab to the notebook with an icon."""
        icon = self._icon(icon_name)
        if icon:
            self.notebook.add(frame, text=f' {text}', image=icon, compound='left')
        else:
            self.notebook.add(frame, text=text)

    def _btn(self, parent, text: str, icon_name: str, command=None, **kwargs):
        """Create a ttk.Button with a drawn icon (fallback to plain text)."""
        icon = self._icon(icon_name)
        if icon:
            btn = ttk.Button(parent, text=f' {text}', image=icon, compound='left',
                             command=command, **kwargs)
            btn._icon_ref = icon  # prevent GC
        else:
            btn = ttk.Button(parent, text=text, command=command, **kwargs)
        return btn

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
        self.create_source_config_tab()
        self.create_openai_image_tab()  # New tab for OpenAI image config
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
        
        ModernPopup.showinfo(self.root,"About WordPress Blog Automation Suite", about_text)
        
    def create_login_tab(self):
        """Create login and authentication tab"""
        self.login_frame = ttk.Frame(self.notebook)
        self._add_tab(self.login_frame, "Authentication", "lock")
        
        # Title
        title_label = ttk.Label(self.login_frame, text="WordPress Blog Automation", font=('Arial', 16, 'bold'))
        title_label.pack(pady=20)

        # Main frame for form and sidebar
        main_frame = ttk.Frame(self.login_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        
        # Login form frame
        login_form = ttk.LabelFrame(main_frame, text="WordPress Credentials", padding=20)
        login_form.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 20))
        
        # WordPress URL
        ttk.Label(login_form, text="WordPress Site URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.wp_base_url_var = tk.StringVar(value=self.config.get('wp_base_url', ''))
        wp_url_entry = ttk.Entry(login_form, textvariable=self.wp_base_url_var, width=50)
        wp_url_entry.grid(row=0, column=1, pady=5, padx=10)
        self.add_entry_context_menu(wp_url_entry)
        
        # Username
        ttk.Label(login_form, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar(value=self.config.get('wp_username', ''))
        username_entry = ttk.Entry(login_form, textvariable=self.username_var, width=50)
        username_entry.grid(row=1, column=1, pady=5, padx=10)
        self.add_entry_context_menu(username_entry)
        
        # Password
        pw_label_frame = ttk.Frame(login_form)
        pw_label_frame.grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(pw_label_frame, text="Password:").pack(anchor=tk.W)
        ttk.Label(pw_label_frame, text="(Application Password)", font=("Arial", 7), foreground="#888").pack(anchor=tk.W)

        self.password_var = tk.StringVar(value=self.config.get('wp_password', ''))
        password_entry = ttk.Entry(login_form, textvariable=self.password_var, show="*", width=50)
        password_entry.grid(row=2, column=1, pady=5, padx=10)
        self.add_entry_context_menu(password_entry)
        ToolTip(password_entry,
            "Use a WordPress Application Password, not your login password.\n"
            "To create one: WordPress Admin → Users → Profile → Application Passwords\n"
            "Format: ABCD EFGH IJKL MNOP QRST UVWX (spaces are OK, they will be handled automatically)")
        
        # Gemini API Key (global)
        ttk.Label(login_form, text="Gemini API Key:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.gemini_key_var = tk.StringVar(value=self.config.get('gemini_api_key', ''))
        gemini_entry = ttk.Entry(login_form, textvariable=self.gemini_key_var, show="*", width=50)
        gemini_entry.grid(row=3, column=1, pady=5, padx=10)
        self.add_entry_context_menu(gemini_entry)
        
        # OpenAI API Key (global)
        ttk.Label(login_form, text="OpenAI API Key:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.openai_key_var = tk.StringVar(value=self.config.get('openai_api_key', ''))
        openai_entry = ttk.Entry(login_form, textvariable=self.openai_key_var, show="*", width=50)
        openai_entry.grid(row=4, column=1, pady=5, padx=10)
        self.add_entry_context_menu(openai_entry)
        
        # Buttons frame
        button_frame = ttk.Frame(login_form)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        self.test_btn = ttk.Button(button_frame, text="Test Connection", command=self.test_connection, style="Accent.TButton")
        self.test_btn.pack(side=tk.LEFT, padx=10)
        self.login_btn = ttk.Button(button_frame, text="Login & Save", command=self.save_wp_credentials, style="Accent.TButton")
        self.login_btn.pack(side=tk.LEFT, padx=10)
        
        # Connection status
        self.connection_status = ttk.Label(login_form, text="Not connected", foreground="red")
        self.connection_status.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Sidebar for user credentials (modern look)
        sidebar_frame = ttk.Frame(main_frame, style="Sidebar.TFrame")
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        sidebar_title = ttk.Label(sidebar_frame, text="Saved Users", font=("Arial", 11, "bold"))
        sidebar_title.pack(anchor=tk.W, pady=(0, 6), padx=6)

        style = ttk.Style()
        style.configure("Sidebar.Treeview", rowheight=28, font=("Arial", 10))
        style.map("Sidebar.Treeview", background=[('selected', '#e0eaff')])
        style.configure("Sidebar.TFrame", background="#f4f6fa", borderwidth=1, relief="solid")

        self.creds_tree = ttk.Treeview(sidebar_frame, columns=("site", "user"), show="headings", selectmode="browse", style="Sidebar.Treeview", height=8)
        self.creds_tree.heading("site", text="Site URL")
        self.creds_tree.heading("user", text="Username")
        self.creds_tree.column("site", width=180, anchor=tk.W)
        self.creds_tree.column("user", width=120, anchor=tk.W)
        self.creds_tree.pack(fill=tk.Y, expand=True, padx=4, pady=2)
        self.creds_tree.bind('<<TreeviewSelect>>', self.on_select_credential)
        self.load_saved_credentials()

        btn_frame = ttk.Frame(sidebar_frame)
        btn_frame.pack(fill=tk.X, pady=4)
        select_btn = ttk.Button(btn_frame, text="Select User", command=self.select_credential)
        select_btn.pack(side=tk.LEFT, padx=4)
        del_btn = self._btn(btn_frame, "Delete", "trash", command=self.delete_credential)
        del_btn.pack(side=tk.LEFT, padx=4)

    def create_openai_image_tab(self):
        import os
        import json
        self.openai_image_frame = ttk.Frame(self.notebook)
        self._add_tab(self.openai_image_frame, "OpenAI Images", "image")

        # Create a scrollable frame for all content
        canvas = tk.Canvas(self.openai_image_frame)
        scrollbar = ttk.Scrollbar(self.openai_image_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # OpenAI Image Configuration Section
        form = ttk.LabelFrame(scrollable_frame, text="OpenAI Image Configuration", padding=20)
        form.pack(pady=10, padx=20, fill=tk.X)

        # Load config
        config_dir = self.get_current_config_dir()
        config_path = os.path.join(config_dir, "openai_image_config.json")
        weights_path = os.path.join(config_dir, "weights.json")
        openai_defaults = {
            "image_size": "1024x1024",
            "image_style": "photorealistic",
            "image_model": "dall-e-3",
            "num_images": 1,
            "prompt_prefix": "",
            "prompt_suffix": ""
        }
        weights_defaults = {
            "summary_length": 120,
            "title_length": 60,
            "content_weight": 1.0,
            "seo_weight": 1.0,
            "image_weight": 1.0
        }
        if os.path.exists(config_path):
            with open(config_path) as f:
                openai_config = json.load(f)
        else:
            openai_config = openai_defaults.copy()
        if os.path.exists(weights_path):
            with open(weights_path) as f:
                weights_config = json.load(f)
        else:
            weights_config = weights_defaults.copy()

        # OpenAI image config fields
        self.openai_image_vars = {}
        row = 0
        
        # Image Size dropdown
        ttk.Label(form, text="Image Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
        size_var = tk.StringVar(value=openai_config.get("image_size", "1024x1024"))
        size_combo = ttk.Combobox(form, textvariable=size_var, values=["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"], width=15, state="readonly")
        size_combo.grid(row=row, column=1, pady=5, padx=10, sticky=tk.W)
        self.openai_image_vars["image_size"] = size_var
        row += 1

        # Image Style dropdown (for DALL-E 3)
        ttk.Label(form, text="Image Style:").grid(row=row, column=0, sticky=tk.W, pady=5)
        style_var = tk.StringVar(value=openai_config.get("image_style", "photorealistic"))
        style_combo = ttk.Combobox(form, textvariable=style_var, values=["photorealistic", "natural", "vivid"], width=15, state="readonly")
        style_combo.grid(row=row, column=1, pady=5, padx=10, sticky=tk.W)
        self.openai_image_vars["image_style"] = style_var
        row += 1

        # Image Model dropdown
        ttk.Label(form, text="Image Model:").grid(row=row, column=0, sticky=tk.W, pady=5)
        model_var = tk.StringVar(value=openai_config.get("image_model", "dall-e-3"))
        model_combo = ttk.Combobox(form, textvariable=model_var, values=["dall-e-3", "dall-e-2"], width=15, state="readonly")
        model_combo.grid(row=row, column=1, pady=5, padx=10, sticky=tk.W)
        self.openai_image_vars["image_model"] = model_var
        row += 1

        # Number of Images
        ttk.Label(form, text="Number of Images:").grid(row=row, column=0, sticky=tk.W, pady=5)
        num_var = tk.StringVar(value=str(openai_config.get("num_images", 1)))
        num_spinbox = ttk.Spinbox(form, from_=1, to=4, textvariable=num_var, width=10)
        num_spinbox.grid(row=row, column=1, pady=5, padx=10, sticky=tk.W)
        self.openai_image_vars["num_images"] = num_var
        row += 1

        # Prompt Prefix
        ttk.Label(form, text="Prompt Prefix:").grid(row=row, column=0, sticky=tk.W, pady=5)
        prefix_var = tk.StringVar(value=openai_config.get("prompt_prefix", ""))
        prefix_entry = ttk.Entry(form, textvariable=prefix_var, width=60)
        prefix_entry.grid(row=row, column=1, pady=5, padx=10, sticky=tk.W)
        self.add_entry_context_menu(prefix_entry)
        self.openai_image_vars["prompt_prefix"] = prefix_var
        row += 1

        # Prompt Suffix
        ttk.Label(form, text="Prompt Suffix:").grid(row=row, column=0, sticky=tk.W, pady=5)
        suffix_var = tk.StringVar(value=openai_config.get("prompt_suffix", ""))
        suffix_entry = ttk.Entry(form, textvariable=suffix_var, width=60)
        suffix_entry.grid(row=row, column=1, pady=5, padx=10, sticky=tk.W)
        self.add_entry_context_menu(suffix_entry)
        self.openai_image_vars["prompt_suffix"] = suffix_var
        row += 1

        # Custom Prompt Section
        custom_prompt_frame = ttk.LabelFrame(scrollable_frame, text="Custom Image Prompt (Optional)", padding=20)
        custom_prompt_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        ttk.Label(custom_prompt_frame, text="Custom Prompt for Content Images:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(custom_prompt_frame, text="Leave empty to use auto-generated prompts based on article content.", foreground="gray").pack(anchor=tk.W, pady=(0, 10))
        
        self.custom_prompt_var = tk.StringVar()
        custom_prompt_text = scrolledtext.ScrolledText(custom_prompt_frame, height=4, wrap=tk.WORD)
        custom_prompt_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Store reference to text widget
        self.custom_prompt_text = custom_prompt_text

        # Add some example prompts
        examples_frame = ttk.LabelFrame(custom_prompt_frame, text="Example Prompts", padding=10)
        examples_frame.pack(fill=tk.X, pady=(10, 0))

        examples = [
            "A photorealistic image of a football stadium with dramatic lighting",
            "An action shot of football players in motion, high-energy sports photography",
            "A close-up of a football with dramatic shadows and professional lighting",
            "An aerial view of a football pitch with players positioned strategically"
        ]

        for i, example in enumerate(examples):
            btn = ttk.Button(examples_frame, text=f"Example {i+1}", 
                           command=lambda ex=example: self.set_custom_prompt(ex))
            btn.pack(side=tk.LEFT, padx=5, pady=2)

        # Weights Section
        weights_frame = ttk.LabelFrame(scrollable_frame, text="Processing Weights & Lengths", padding=20)
        weights_frame.pack(pady=10, padx=20, fill=tk.X)

        self.weights_vars = {}
        weights_row = 0
        for label, key in [
            ("Summary Length", "summary_length"),
            ("Title Length", "title_length"),
            ("Content Weight", "content_weight"),
            ("SEO Weight", "seo_weight"),
            ("Image Weight", "image_weight")
        ]:
            ttk.Label(weights_frame, text=label+":").grid(row=weights_row, column=0, sticky=tk.W, pady=5)
            var = tk.StringVar(value=str(weights_config.get(key, weights_defaults.get(key, ""))))
            entry = ttk.Entry(weights_frame, textvariable=var, width=20)
            entry.grid(row=weights_row, column=1, pady=5, padx=10, sticky=tk.W)
            self.weights_vars[key] = var
            weights_row += 1

        # Save/Cancel buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(pady=20)
        save_btn = ttk.Button(button_frame, text="Save Configuration", command=self.save_openai_image_config, style="Accent.TButton")
        save_btn.pack(side=tk.LEFT, padx=10)
        cancel_btn = ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_openai_image_config)
        cancel_btn.pack(side=tk.LEFT, padx=10)

    def set_custom_prompt(self, prompt):
        """Set a custom prompt in the text area"""
        self.custom_prompt_text.delete(1.0, tk.END)
        self.custom_prompt_text.insert(1.0, prompt)

    def get_custom_prompt(self):
        """Get the custom prompt from the text area"""
        return self.custom_prompt_text.get(1.0, tk.END).strip()

    def reset_openai_image_config(self):
        """Reset OpenAI image configuration to defaults"""
        openai_defaults = {
            "image_size": "1024x1024",
            "image_style": "photorealistic",
            "image_model": "dall-e-3",
            "num_images": 1,
            "prompt_prefix": "",
            "prompt_suffix": ""
        }
        
        weights_defaults = {
            "summary_length": 120,
            "title_length": 60,
            "content_weight": 1.0,
            "seo_weight": 1.0,
            "image_weight": 1.0
        }
        
        for key, var in self.openai_image_vars.items():
            var.set(str(openai_defaults.get(key, "")))
        
        for key, var in self.weights_vars.items():
            var.set(str(weights_defaults.get(key, "")))
        
        self.custom_prompt_text.delete(1.0, tk.END)
        ModernPopup.showinfo(self.root,"Reset", "OpenAI image configuration and weights reset to defaults.")

    def save_openai_image_config(self):
        """Save OpenAI image configuration to current domain directory"""
        import os
        import json
        
        config_dir = self.get_current_config_dir()
        config_path = os.path.join(config_dir, "openai_image_config.json")
        weights_path = os.path.join(config_dir, "weights.json")
        
        openai_config = {k: v.get() for k, v in self.openai_image_vars.items()}
        
        # Convert num_images to int
        try:
            openai_config["num_images"] = int(openai_config["num_images"])
        except Exception:
            openai_config["num_images"] = 1
        
        # Save custom prompt if provided
        custom_prompt = self.get_custom_prompt()
        openai_config["custom_prompt"] = custom_prompt
        
        with open(config_path, 'w') as f:
            json.dump(openai_config, f, indent=2)
        
        weights_config = {k: v.get() for k, v in self.weights_vars.items()}
        # Convert numeric fields
        for k in ["summary_length", "title_length"]:
            try:
                weights_config[k] = int(weights_config[k])
            except Exception:
                weights_config[k] = 0
        for k in ["content_weight", "seo_weight", "image_weight"]:
            try:
                weights_config[k] = float(weights_config[k])
            except Exception:
                weights_config[k] = 1.0
        with open(weights_path, 'w') as f:
            json.dump(weights_config, f, indent=2)
        
        domain_info = f" for domain: {self.current_domain}" if self.current_domain else ""
        self.logger.info(f"[OK] OpenAI image and weights configuration saved{domain_info}")
        ModernPopup.showinfo(self.root,"Success", f"OpenAI image and weights configuration saved{domain_info}.")

    def cancel_openai_image_config(self):
        self.openai_image_frame.destroy()
        self.create_openai_image_tab()

    def save_wp_credentials(self):
        """Save credentials and setup domain-based configuration"""
        # Get credentials from UI
        wp_url = self.wp_base_url_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not all([wp_url, username, password]):
            ModernPopup.showerror(self.root,"Error", "Please fill in all WordPress credentials")
            return
        
        # Extract domain and setup domain-specific configuration
        domain = self.extract_domain_from_url(wp_url)
        self.setup_domain_config_directory(domain)
        
        self.logger.info(f"Setting up configuration for domain: {domain}")
        self.logger.info(f"Domain config directory: {self.domain_config_dir}")
        
        # Save credentials to config and domain-specific credentials.json
        creds = {
            'wp_base_url': wp_url,
            'wp_username': username,
            'wp_password': password,
            'domain': domain
        }
        
        # Update main config
        self.config['wp_base_url'] = creds['wp_base_url']
        self.config['wp_username'] = creds['wp_username']
        self.config['wp_password'] = creds['wp_password']
        self.config['gemini_api_key'] = self.gemini_key_var.get().strip()
        self.config['openai_api_key'] = self.openai_key_var.get().strip()
        self.save_config()
        
        # Save to domain-specific credentials.json
        creds_path = os.path.join(self.domain_config_dir, 'credentials.json')
        all_creds = []
        if os.path.exists(creds_path):
            with open(creds_path) as f:
                all_creds = json.load(f)
        
        # Remove any existing entry for this (url, username) in this domain
        all_creds = [c for c in all_creds if not (c['wp_base_url'] == creds['wp_base_url'] and c['wp_username'] == creds['wp_username'])]
        all_creds.insert(0, creds)  # Insert as most recent/default
        
        with open(creds_path, 'w') as f:
            json.dump(all_creds, f, indent=2)
        
        # Also maintain global credentials for easy switching between domains
        global_creds_path = os.path.join(self.base_config_dir, 'credentials.json')
        global_creds = []
        if os.path.exists(global_creds_path):
            with open(global_creds_path) as f:
                global_creds = json.load(f)
        
        # Remove existing entry and add updated one
        global_creds = [c for c in global_creds if not (c.get('wp_base_url') == creds['wp_base_url'] and c.get('wp_username') == creds['wp_username'])]
        global_creds.insert(0, creds)
        
        with open(global_creds_path, 'w') as f:
            json.dump(global_creds, f, indent=2)
        
        # Update UI to show domain-specific configurations
        self.load_saved_credentials()
        self.update_config_ui_for_domain()
        
        self.logger.info(f"[OK] Credentials saved for domain: {domain}")
        self.connection_status.config(text=f"Saved for {domain}", foreground="green")
        
        ModernPopup.showinfo(self.root,"Success", 
            f"Credentials saved successfully!\n\n"
            f"Domain: {domain}\n"
            f"Configuration directory: {self.domain_config_dir}\n\n"
            f"All settings for this domain are now isolated and separate from other domains.")
        
    def update_config_ui_for_domain(self):
        """Update configuration UI elements after domain change"""
        try:
            # Update config files list for current domain
            self.config_files = self.get_config_files()
            
            # Update config selector if it exists
            if hasattr(self, 'config_selector'):
                self.config_selector['values'] = self.config_files
                # Load default config for this domain
                self.active_config_name = self.get_last_used_config() or "default"
                self.config_selector_var.set(self.active_config_name)
                self.config = self.load_config(self.active_config_name)
                
            # Refresh config tab if it exists
            if hasattr(self, 'config_frame'):
                self.refresh_config_tab()
                
        except Exception as e:
            self.logger.error(f"Error updating config UI for domain: {e}")

    def load_saved_credentials(self):
        """Load saved credentials from global credentials file (all domains)"""
        # Clear existing items
        for i in self.creds_tree.get_children():
            self.creds_tree.delete(i)
        
        self.saved_creds = []
        
        # Load from global credentials file to show all domains
        global_creds_path = os.path.join(self.base_config_dir, 'credentials.json')
        if os.path.exists(global_creds_path):
            with open(global_creds_path) as f:
                self.saved_creds = json.load(f)
        
        # Group credentials by domain for better organization
        domain_groups = {}
        for idx, cred in enumerate(self.saved_creds):
            domain = cred.get('domain', self.extract_domain_from_url(cred.get('wp_base_url', '')))
            if domain not in domain_groups:
                domain_groups[domain] = []
            domain_groups[domain].append((idx, cred))
        
        # Display credentials grouped by domain
        for domain, creds in domain_groups.items():
            # Add domain header
            domain_header = self.creds_tree.insert("", "end", iid=f"domain_{domain}", 
                                                  values=(f"[{domain.upper()}]", ""),
                                                  tags=("domain_header",))
            
            # Add credentials under domain
            for idx, cred in creds:
                self.creds_tree.insert(domain_header, "end", iid=str(idx), 
                                     values=(cred['wp_base_url'], cred['wp_username']),
                                     tags=("credential",))
        
        # Expand all domain groups
        for domain in domain_groups.keys():
            self.creds_tree.item(f"domain_{domain}", open=True)
        
        # Configure tags for styling
        self.creds_tree.tag_configure("domain_header", background="#e0e0e0", font=("Arial", 9, "bold"))
        self.creds_tree.tag_configure("credential", background="#ffffff")

    def on_select_credential(self, event=None):
        """Handle credential selection from domain-organized tree"""
        idxs = self.creds_tree.selection()
        if idxs:
            selected_id = idxs[0]
            
            # Skip if domain header is selected
            if selected_id.startswith("domain_"):
                return
            
            try:
                idx = int(selected_id)
                cred = self.saved_creds[idx]
                
                # Extract domain and setup domain configuration
                domain = cred.get('domain', self.extract_domain_from_url(cred.get('wp_base_url', '')))
                self.setup_domain_config_directory(domain)
                
                # Load credentials into UI
                self.wp_base_url_var.set(cred['wp_base_url'])
                self.username_var.set(cred['wp_username'])
                self.password_var.set(cred['wp_password'])
                
                # Load domain-specific configuration
                self.active_config_name = self.get_last_used_config() or "default"
                self.config = self.load_config(self.active_config_name)
                
                # Update UI with domain-specific API keys if available
                self.gemini_key_var.set(self.config.get('gemini_api_key', ''))
                self.openai_key_var.set(self.config.get('openai_api_key', ''))
                
                # Update configuration UI for this domain
                self.update_config_ui_for_domain()
                
                self.connection_status.config(
                    text=f"Loaded: {domain} | {cred['wp_username']}", 
                    foreground="blue"
                )
                
                self.logger.info(f"[>>] Switched to domain configuration: {domain}")
                
            except (ValueError, IndexError, KeyError) as e:
                self.logger.error(f"Error selecting credential: {e}")

    def select_credential(self):
        """Select the currently highlighted credential"""
        self.on_select_credential()

    def delete_credential(self):
        """Delete selected credential from both domain and global files"""
        idxs = self.creds_tree.selection()
        if idxs:
            selected_id = idxs[0]
            
            # Skip if domain header is selected
            if selected_id.startswith("domain_"):
                ModernPopup.showinfo(self.root,"Info", "Please select a specific credential to delete, not the domain header.")
                return
            
            try:
                idx = int(selected_id)
                cred = self.saved_creds[idx]
                
                if ModernPopup.askyesno(self.root,"Delete Credential", 
                    f"Delete credentials for {cred['wp_username']} at {cred['wp_base_url']}?\n\n"
                    f"This will remove the credential from both domain-specific and global storage."):
                    
                    # Remove from global credentials
                    del self.saved_creds[idx]
                    global_creds_path = os.path.join(self.base_config_dir, 'credentials.json')
                    with open(global_creds_path, 'w') as f:
                        json.dump(self.saved_creds, f, indent=2)
                    
                    # Remove from domain-specific credentials if exists
                    domain = cred.get('domain', self.extract_domain_from_url(cred.get('wp_base_url', '')))
                    domain_dir = os.path.join(self.base_config_dir, domain)
                    domain_creds_path = os.path.join(domain_dir, 'credentials.json')
                    
                    if os.path.exists(domain_creds_path):
                        with open(domain_creds_path) as f:
                            domain_creds = json.load(f)
                        
                        # Remove matching credential
                        domain_creds = [c for c in domain_creds if not (
                            c['wp_base_url'] == cred['wp_base_url'] and 
                            c['wp_username'] == cred['wp_username']
                        )]
                        
                        with open(domain_creds_path, 'w') as f:
                            json.dump(domain_creds, f, indent=2)
                    
                    self.load_saved_credentials()
                    self.logger.info(f"Deleted credentials for {cred['wp_username']} at {cred['wp_base_url']}")
                    
            except (ValueError, IndexError, KeyError) as e:
                self.logger.error(f"Error deleting credential: {e}")
                ModernPopup.showerror(self.root,"Error", f"Error deleting credential: {e}")
        
    def create_prerequisites_section(self):
        """Create prerequisites check section"""
        prereq_frame = ttk.LabelFrame(self.login_frame, text="System Prerequisites", padding=20)
        prereq_frame.pack(pady=20, padx=40, fill=tk.X)
        
        # Check selenium
        selenium_status = "[OK] Available" if SELENIUM_AVAILABLE else "[X] Not installed"
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
                status = "[OK] Available"
            except ImportError:
                status = "[X] Not installed"
            ttk.Label(prereq_frame, text=f"{req_name}: {status}").pack(anchor=tk.W)
            
        if not SELENIUM_AVAILABLE:
            install_btn = ttk.Button(prereq_frame, text="Install Missing Requirements", 
                                   command=self.install_requirements)
            install_btn.pack(pady=10)
            
    def create_automation_tab(self):
        """Create main automation tab"""
        self.automation_frame = ttk.Frame(self.notebook)
        self._add_tab(self.automation_frame, "Automation", "robot")
        
        # Control panel
        control_panel = ttk.LabelFrame(self.automation_frame, text="Control Panel", padding=10)
        control_panel.pack(fill=tk.X, padx=10, pady=5)
        
        # Settings frame
        settings_frame = ttk.Frame(control_panel)
        settings_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(settings_frame, text="Max Articles:").pack(side=tk.LEFT)
        self.max_articles_var = tk.IntVar(value=self.config.get('max_articles', 2))
        max_articles_spin = ttk.Spinbox(settings_frame, from_=1, to=10, textvariable=self.max_articles_var, width=5)
        max_articles_spin.pack(side=tk.LEFT, padx=5)
        ToolTip(max_articles_spin, "How many articles to scrape and post in one run.\nStart with 1-2 to test your configuration before running larger batches.")

        # Force processing option
        self.force_processing_var = tk.BooleanVar(value=False)
        force_check = ttk.Checkbutton(settings_frame, text="Force Processing (ignore history)", variable=self.force_processing_var)
        force_check.pack(side=tk.LEFT, padx=20)
        ToolTip(force_check, "By default the app skips articles it has already posted.\nEnable this to reprocess and repost articles even if they were posted before.\nUseful for testing or fixing posts.")

        # Jupyter notebook style option
        self.use_jupyter_style_var = tk.BooleanVar(value=False)
        jupyter_checkbox = ttk.Checkbutton(settings_frame, text="Enhanced Processing (Jupyter Style)", variable=self.use_jupyter_style_var)
        jupyter_checkbox.pack(side=tk.LEFT, padx=20)
        ToolTip(jupyter_checkbox, "Use enhanced processing methods with improved SEO, tags, and content optimization.\nRecommended for production use. Uses more advanced Gemini prompts.")
        
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
        
        # Content Images section
        content_image_frame = ttk.LabelFrame(settings_frame, text="Content Images", padding=10)
        content_image_frame.pack(side=tk.LEFT, padx=20, fill=tk.BOTH)
        
        self.content_image_var = tk.StringVar(value="none")
        
        # Radio buttons for content image selection
        ttk.Radiobutton(content_image_frame, text="No Content Images", variable=self.content_image_var, value="none").pack(anchor=tk.W)
        openai_content_radio = ttk.Radiobutton(content_image_frame, text="OpenAI Generated Images", variable=self.content_image_var, value="openai")
        openai_content_radio.pack(anchor=tk.W)
        getty_content_radio = ttk.Radiobutton(content_image_frame, text="Getty Editorial Images", variable=self.content_image_var, value="getty")
        getty_content_radio.pack(anchor=tk.W)
        
        # Custom prompt option
        self.use_custom_prompt_var = tk.BooleanVar(value=False)
        custom_prompt_check = ttk.Checkbutton(content_image_frame, text="Use Custom Prompt", variable=self.use_custom_prompt_var)
        custom_prompt_check.pack(anchor=tk.W, pady=(5, 0))
        
        # Add tooltips for content images
        ToolTip(openai_content_radio, "Generates and inserts images within article content using OpenAI DALL-E. Configure prompts in the OpenAI Images tab.")
        ToolTip(getty_content_radio, "Inserts Getty Images editorial content within articles.")
        ToolTip(custom_prompt_check, "Use the custom prompt from the OpenAI Images tab instead of auto-generated prompts.")
        
        # Buttons frame
        buttons_frame = ttk.Frame(control_panel)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = self._btn(buttons_frame, "Start Automation", "play",
                                    command=self.start_automation, style="Accent.TButton")
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = self._btn(buttons_frame, "Stop", "stop",
                                  command=self.stop_automation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.clear_logs_btn = self._btn(buttons_frame, "Clear Logs", "trash",
                                        command=self.clear_logs)
        self.clear_logs_btn.pack(side=tk.LEFT, padx=5)

        self.test_config_btn = self._btn(buttons_frame, "Test Configuration", "search",
                                         command=self.test_configuration)
        self.test_config_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(self.automation_frame, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)

        # Overall progress row
        overall_row = ttk.Frame(progress_frame)
        overall_row.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(overall_row, text="Overall Progress:", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        self.overall_pct_label = ttk.Label(overall_row, text="0%", font=("Arial", 9, "bold"), foreground="#0078d4")
        self.overall_pct_label.pack(side=tk.RIGHT)
        self.articles_count_label = ttk.Label(overall_row, text="Articles: 0/0", foreground="#555")
        self.articles_count_label.pack(side=tk.RIGHT, padx=(0, 15))

        self.overall_progress = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.overall_progress.pack(fill=tk.X, pady=(0, 8))

        # Current step row
        step_row = ttk.Frame(progress_frame)
        step_row.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(step_row, text="Current Step:", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        self.step_counter_label = ttk.Label(step_row, text="", foreground="#555")
        self.step_counter_label.pack(side=tk.RIGHT)

        self.task_progress = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.task_progress.pack(fill=tk.X, pady=(0, 5))

        # Status / elapsed row
        self.status_frame = ttk.Frame(progress_frame)
        self.status_frame.pack(fill=tk.X, pady=2)

        self.current_task_label = ttk.Label(self.status_frame, text="Status: Ready", foreground="#333")
        self.current_task_label.pack(side=tk.LEFT)

        self.elapsed_label = ttk.Label(self.status_frame, text="", foreground="#777", font=("Arial", 8))
        self.elapsed_label.pack(side=tk.RIGHT)

        # Store automation start time
        self._automation_start_time = None
        self._step_start_time = None
        
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
        """Initialize the process steps with color-coded rows"""
        self.process_steps = [
            "Fetching article links",
            "Extracting article content",
            "Paraphrasing with Gemini",
            "Injecting internal links",
            "Injecting external links",
            "Adding content images",
            "Generating SEO metadata",
            "Generating keyphrases",
            "Processing featured images",
            "Detecting categories",
            "Generating tags",
            "Creating WordPress post",
            "Finalizing post"
        ]

        # Clear existing items
        for item in self.steps_tree.get_children():
            self.steps_tree.delete(item)

        # Configure color tags for step statuses
        self.steps_tree.tag_configure('running', background='#fff3cd', foreground='#856404')    # yellow
        self.steps_tree.tag_configure('completed', background='#d4edda', foreground='#155724')  # green
        self.steps_tree.tag_configure('error', background='#f8d7da', foreground='#721c24')      # red
        self.steps_tree.tag_configure('skipped', background='#e2e3e5', foreground='#383d41')    # grey
        self.steps_tree.tag_configure('pending', background='#ffffff', foreground='#333333')    # white

        # Add steps
        for i, step in enumerate(self.process_steps):
            self.steps_tree.insert('', 'end', iid=str(i), values=(step, '[...] Pending', '', ''), tags=('pending',))

        # Reset progress UI
        self.overall_progress['value'] = 0
        self.task_progress['value'] = 0
        if hasattr(self, 'overall_pct_label'):
            self.overall_pct_label.config(text="0%")
        if hasattr(self, 'step_counter_label'):
            self.step_counter_label.config(text="")
        if hasattr(self, 'elapsed_label'):
            self.elapsed_label.config(text="")
        self._automation_start_time = None
        self._step_start_time = None
            
    def create_logs_tab(self):
        """Create logs tab with session information and category viewing"""
        self.logs_frame = ttk.Frame(self.notebook)
        self._add_tab(self.logs_frame, "Logs", "clipboard")
        
        # Session info frame at top
        session_frame = ttk.LabelFrame(self.logs_frame, text="Current Session", padding=5)
        session_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Show session information if available
        if hasattr(self, 'session_info'):
            session_id_label = ttk.Label(session_frame, text=f"Session ID: {self.session_info['session_id']}", font=('Arial', 9, 'bold'))
            session_id_label.pack(side=tk.LEFT)
            
            # Add buttons to open log directory and view categories
            self._btn(session_frame, "Open Log Directory", "folder",
                      command=self.open_log_directory).pack(side=tk.RIGHT, padx=2)
            self._btn(session_frame, "Session Info", "chart",
                      command=self.show_session_info).pack(side=tk.RIGHT, padx=2)
        
        # Log category selector frame
        category_frame = ttk.Frame(self.logs_frame)
        category_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(category_frame, text="Log Category:").pack(side=tk.LEFT)
        self.log_category_var = tk.StringVar(value="All Logs")
        log_categories = ["All Logs", "Main", "Automation", "Errors", "Debug", "API", "Security"]
        category_combo = ttk.Combobox(category_frame, textvariable=self.log_category_var, 
                                     values=log_categories, width=15, state="readonly")
        category_combo.pack(side=tk.LEFT, padx=5)
        category_combo.bind('<<ComboboxSelected>>', self.on_log_category_change)
        
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
        
        # Configure text tags for enhanced colored output with backgrounds
        self.logs_text.tag_configure("ERROR", foreground="#FF4444", background="#FFE6E6", font=("Consolas", 10, "bold"))
        self.logs_text.tag_configure("WARNING", foreground="#FF8800", background="#FFF4E6", font=("Consolas", 10))
        self.logs_text.tag_configure("INFO", foreground="#0066CC", background="#E6F3FF", font=("Consolas", 10))
        self.logs_text.tag_configure("DEBUG", foreground="#666666", background="#F5F5F5", font=("Consolas", 9))
        self.logs_text.tag_configure("AUTOMATION", foreground="#00AA44", background="#E6FFE6", font=("Consolas", 10, "bold"))
        self.logs_text.tag_configure("API", foreground="#8800CC", background="#F0E6FF", font=("Consolas", 10))
        self.logs_text.tag_configure("SECURITY", foreground="#CC0000", background="#FFE6E6", font=("Consolas", 10, "bold"))
        self.logs_text.tag_configure("WEBDRIVER", foreground="#FF6600", background="#FFF0E6", font=("Consolas", 10))
        self.logs_text.tag_configure("CONTENT", foreground="#0088CC", background="#E6F8FF", font=("Consolas", 10))
        self.logs_text.tag_configure("SYSTEM", foreground="#444444", background="#F0F0F0", font=("Consolas", 10, "bold"))
        
        # Configure the text widget for better appearance
        self.logs_text.configure(font=("Consolas", 10), bg="#FAFAFA", fg="#333333")
        
        # Load existing logs from session files if available
        self.load_session_logs()
        
        # Start real-time log monitoring
        self.start_realtime_log_monitoring()
        
    def load_session_logs(self):
        """Load existing logs from session files"""
        try:
            if hasattr(self, 'session_info') and self.session_info:
                # Load from current session files
                self.logs_text.insert(tk.END, f"Loading logs from session: {self.session_info['session_id']}\n")
                self.logs_text.insert(tk.END, f"Log directory: {self.session_info['base_dir']}\n\n")
                
                # Load main log first
                main_log_file = self.session_info['log_files'].get('main')
                if main_log_file and os.path.exists(main_log_file):
                    with open(main_log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        # Load last 200 lines to avoid overwhelming the GUI
                        recent_lines = lines[-200:] if len(lines) > 200 else lines
                        
                    for line in recent_lines:
                        line = line.strip()
                        if line:  # Skip empty lines
                            self.add_log_message(line)
                            
                self.logs_text.insert(tk.END, "\n[>>] Real-time logs will appear below...\n")
                self.logs_text.see(tk.END)
                
                # Add separator
                separator = "=" * 80 + "\n"
                self.logs_text.insert(tk.END, separator)
                
            else:
                # Fallback to basic log file
                self.load_existing_logs()
                
        except Exception as e:
            self.logs_text.insert(tk.END, f"[!] Could not load session logs: {e}\n")
            # Fallback to basic logs
            self.load_existing_logs()
            
    def start_realtime_log_monitoring(self):
        """Start real-time monitoring of log files"""
        self.log_file_positions = {}
        self.monitor_log_files()
        
    def monitor_log_files(self):
        """Monitor log files for new entries and update display"""
        try:
            if hasattr(self, 'session_info') and self.session_info:
                # Monitor unified log file for real-time updates
                unified_log_file = self.session_info.get('unified_log_file')
                if unified_log_file and os.path.exists(unified_log_file):
                    self.check_log_file_updates(unified_log_file)
                    
        except Exception as e:
            print(f"Error monitoring log files: {e}")
        finally:
            # Schedule next check in 1 second
            self.root.after(1000, self.monitor_log_files)
            
    def check_log_file_updates(self, log_file):
        """Check for new lines in a log file and add them to display"""
        try:
            file_path = str(log_file)
            current_size = os.path.getsize(log_file)
            
            # Initialize position tracking for this file
            if file_path not in self.log_file_positions:
                self.log_file_positions[file_path] = current_size
                return
                
            last_position = self.log_file_positions[file_path]
            
            # Check if file has grown
            if current_size > last_position:
                with open(log_file, 'r', encoding='utf-8') as f:
                    f.seek(last_position)
                    new_lines = f.readlines()
                    
                    for line in new_lines:
                        line = line.strip()
                        if line:
                            # Add new log entry to display
                            self.add_log_message(line, add_timestamp=False)
                            
                # Update position
                self.log_file_positions[file_path] = current_size
                
        except Exception as e:
            print(f"Error checking log file updates: {e}")
            
    def on_log_category_change(self, event=None):
        """Handle log category selection change"""
        category = self.log_category_var.get()
        self.load_category_logs(category)
        
    def load_category_logs(self, category: str):
        """Load logs for a specific category"""
        if not hasattr(self, 'session_info') or not self.session_info:
            return
            
        self.logs_text.delete(1.0, tk.END)
        
        try:
            if category == "All Logs":
                # Load all logs mixed together (current behavior)
                self.load_session_logs()
                return
                
            # Map GUI category names to log file keys
            category_map = {
                "Main": "main",
                "Automation": "automation", 
                "Errors": "errors",
                "Debug": "debug",
                "API": "api",
                "Security": "security"
            }
            
            log_key = category_map.get(category)
            if not log_key:
                return
                
            log_file = self.session_info['log_files'].get(log_key)
            if not log_file or not os.path.exists(log_file):
                self.logs_text.insert(tk.END, f"No {category.lower()} logs found for this session.\n")
                return
                
            self.logs_text.insert(tk.END, f"Showing {category} logs from: {log_file}\n\n")
            
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if line:
                    self.add_log_message(line)
                    
            self.logs_text.see(tk.END)
            
        except Exception as e:
            self.logs_text.insert(tk.END, f"[!] Error loading {category} logs: {e}\n")
            
    def open_log_directory(self):
        """Open the log directory in file explorer"""
        try:
            if hasattr(self, 'session_info') and self.session_info:
                log_dir = self.session_info['base_dir']
            else:
                log_dir = os.path.abspath('logs')
                
            # Open directory based on OS
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", log_dir])
            elif system == "Windows":
                subprocess.run(["explorer", log_dir])
            else:  # Linux
                subprocess.run(["xdg-open", log_dir])
                
            self.logger.info(f"Opened log directory: {log_dir}")
            
        except Exception as e:
            self.logger.error(f"Error opening log directory: {e}")
            ModernPopup.showerror(self.root,"Error", f"Could not open log directory: {e}")
            
    def show_session_info(self):
        """Show detailed session information"""
        try:
            if not hasattr(self, 'session_info') or not self.session_info:
                ModernPopup.showinfo(self.root,"Session Info", "No session information available")
                return
                
            info = self.session_info
            
            # Get log manager for additional details
            if hasattr(self, 'log_manager'):
                sessions = self.log_manager.list_previous_sessions()
                current_session = next((s for s in sessions if s['session_id'] == info['session_id']), {})
                
                if current_session:
                    info.update(current_session)
            
            # Build info display
            info_text = f"""Session Information:

Session ID: {info['session_id']}
Timestamp: {info['timestamp']}
Start Time: {info.get('start_time', 'N/A')}
Status: {info.get('status', 'Active')}
Base Directory: {info['base_dir']}

Log Files:"""
            
            for category, filepath in info['log_files'].items():
                try:
                    size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
                    size_str = f" ({size:,} bytes)" if size > 0 else " (empty)"
                    info_text += f"\n  • {category.title()}: {filepath}{size_str}"
                except:
                    info_text += f"\n  • {category.title()}: {filepath} (error reading size)"
                    
            if 'duration_seconds' in info:
                duration = info['duration_seconds']
                info_text += f"\n\nSession Duration: {duration:.1f} seconds"
                
            # Show in dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Session Information")
            dialog.geometry("600x400")
            
            text_widget = scrolledtext.ScrolledText(dialog, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, info_text)
            text_widget.config(state=tk.DISABLED)
            
            ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
            
        except Exception as e:
            ModernPopup.showerror(self.root,"Error", f"Could not show session info: {e}")
        
    def load_existing_logs(self):
        """Load existing logs from the log file"""
        try:
            if os.path.exists('blog_automation.log'):
                with open('blog_automation.log', 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Load last 500 lines to avoid overwhelming the GUI
                    recent_lines = lines[-500:] if len(lines) > 500 else lines
                    
                self.logs_text.insert(tk.END, "Loading recent logs from blog_automation.log...\n\n")
                
                for line in recent_lines:
                    line = line.strip()
                    if line:  # Skip empty lines
                        self.add_log_message(line)
                        
                self.logs_text.insert(tk.END, "\n[>>] Real-time logs will appear below...\n")
                self.logs_text.see(tk.END)
                
                # Add separator
                separator = "=" * 80 + "\n"
                self.logs_text.insert(tk.END, separator)
                
        except Exception as e:
            self.logs_text.insert(tk.END, f"[!] Could not load existing logs: {e}\n")
            
    def refresh_logs(self):
        """Refresh logs by reloading from file"""
        self.logs_text.delete(1.0, tk.END)
        self.load_existing_logs()
        
    def create_config_tab(self):
        """Create configuration tab with domain-aware settings"""
        self.config_frame = ttk.Frame(self.notebook)
        self._add_tab(self.config_frame, "Configuration", "gear")
        
        # Domain info section at the top
        domain_info_frame = ttk.LabelFrame(self.config_frame, text="Domain Configuration", padding=10)
        domain_info_frame.pack(fill=tk.X, pady=5, padx=10)
        
        domain_text = self.current_domain or "No domain selected"
        config_dir_text = self.domain_config_dir or "Using base configuration"
        
        domain_label = ttk.Label(domain_info_frame, text=f"Current Domain: {domain_text}", font=("Arial", 10, "bold"))
        domain_label.pack(side=tk.LEFT)
        
        config_dir_label = ttk.Label(domain_info_frame, text=f"Config Directory: {config_dir_text}", font=("Arial", 8))
        config_dir_label.pack(side=tk.LEFT, padx=(20, 0))
        
        if not self.current_domain:
            warning_label = ttk.Label(domain_info_frame, text="Please login to select a domain", foreground="orange")
            warning_label.pack(side=tk.RIGHT)
        
        # Add config selector at the top
        selector_frame = ttk.Frame(self.config_frame)
        selector_frame.pack(fill=tk.X, pady=5, padx=10)
        ttk.Label(selector_frame, text="Active Configuration:").pack(side=tk.LEFT)
        self.config_selector_var = tk.StringVar(value=self.active_config_name)
        self.config_selector = ttk.Combobox(selector_frame, textvariable=self.config_selector_var, values=self.get_config_files(), state="readonly", width=20)
        self.config_selector.pack(side=tk.LEFT, padx=5)
        self.config_selector.bind('<<ComboboxSelected>>', self.on_config_selected)
        ttk.Button(selector_frame, text="Add", command=self.add_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(selector_frame, text="Duplicate", command=self.duplicate_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(selector_frame, text="Rename", command=self.rename_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(selector_frame, text="Delete", command=self.delete_config).pack(side=tk.LEFT, padx=2)

        # Sidebar + main editor frame
        main_frame = ttk.Frame(self.config_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Sidebar frame for visual distinction
        sidebar_frame = ttk.Frame(main_frame, style="Sidebar.TFrame")
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=2)
        sidebar_title = ttk.Label(sidebar_frame, text="Config Sections", font=("Arial", 11, "bold"))
        sidebar_title.pack(anchor=tk.W, pady=(0, 6), padx=6)

        # Enhanced sidebar with ttk.Treeview
        style = ttk.Style()
        style.configure("Sidebar.Treeview", rowheight=32, font=("Arial", 10))
        style.map("Sidebar.Treeview", background=[('selected', '#e0eaff')])
        style.configure("Sidebar.TFrame", background="#f4f6fa", borderwidth=1, relief="solid")

        self.config_sections = [
            ("SEO Plugin Settings", "seo_plugin_settings", ""),
            ("Internal Links", "internal_links", ""),
            ("External Links", "external_links", ""),
            ("Style Prompt", "style_prompt", ""),
            ("SEO Title & Meta Prompt", "seo_title_meta_prompt", ""),
            ("Tag Generation Prompt", "tag_generation_prompt", ""),
            ("Keyphrase Extraction Prompt", "keyphrase_extraction_prompt", ""),
            ("Category Keywords", "category_keywords", ""),
            ("Tag Synonyms", "tag_synonyms", ""),
            ("Static Clubs", "static_clubs", ""),
            ("Stop Words", "stop_words", ""),
            ("Do-Follow URLs", "do_follow_urls", "")
        ]
        sidebar = ttk.Treeview(sidebar_frame, show="tree", selectmode="browse", style="Sidebar.Treeview", height=len(self.config_sections))
        for idx, (label, _, _icon_unused) in enumerate(self.config_sections):
            sidebar.insert("", "end", iid=str(idx), text=label)
        sidebar.pack(fill=tk.Y, expand=True, padx=4, pady=2)
        sidebar.bind('<<TreeviewSelect>>', self.on_sidebar_select)
        self.sidebar = sidebar

        # Editor area
        editor_frame = ttk.Frame(main_frame)
        editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.editor_frame = editor_frame

        # Save/Cancel buttons
        self.button_frame = ttk.Frame(editor_frame)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        save_btn = ttk.Button(self.button_frame, text="Save Section", command=self.save_current_section, style="Accent.TButton")
        save_btn.pack(side=tk.LEFT, padx=10)
        cancel_btn = ttk.Button(self.button_frame, text="Cancel", command=self.refresh_config_tab)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # Add reset to default button for individual prompts
        reset_btn = ttk.Button(self.button_frame, text="Reset to Default", command=self.reset_prompt_to_default)
        reset_btn.pack(side=tk.LEFT, padx=10)

        # Show the first section by default
        sidebar.selection_set("0")
        self.show_section_editor(0)
        
        # Add comprehensive help section at the bottom
        help_frame = ttk.LabelFrame(self.config_frame, text="Configuration Guide", padding=10)
        help_frame.pack(fill=tk.X, pady=5, padx=10)
        
        help_text = (
            "Quick Start Guide:\n"
            "1. Select a configuration section from the sidebar (SEO Title & Meta, Tag Generation, etc.)\n"
            "2. Edit the prompt text in the editor area - default examples are provided\n"
            "3. Click 'Save Section' to apply your changes\n\n"
            "Pro Tips:\n"
            "• Each section contains example prompts that you can customize\n"
            "• Use 'Reset to Default' to restore original settings\n"
            "• Test your changes with the automation tools to see results\n"
            "• JSON sections require proper syntax - validate before saving"
        )
        
        help_label = ttk.Label(help_frame, text=help_text, font=("Arial", 9), foreground="#34495e", justify=tk.LEFT)
        help_label.pack(anchor=tk.W)
        
    def reset_prompt_to_default(self):
        """Reset current prompt section to default value"""
        if not hasattr(self, 'current_section_key'):
            return
            
        key = self.current_section_key
        
        # Default prompts for different sections
        defaults = {
            "seo_title_meta_prompt": "Generate an SEO-optimized title (max 60 characters) and meta description (max 160 characters) for this football article. Focus on including relevant keywords while maintaining readability.",
            "tag_generation_prompt": "Extract relevant tags from this football article content. Focus on player names, club names, competitions, and football-related keywords. Return as a comma-separated list.",
            "keyphrase_extraction_prompt": "Extract the main focus keyphrase and 3-5 additional SEO keyphrases from this football article. The focus keyphrase should be 2-4 words that best represent the article's main topic.",
            "style_prompt": "Rewrite this football article in an engaging, professional style suitable for a football news website. Maintain all factual information while improving readability and flow."
        }
        
        default_value = defaults.get(key, "")
        
        if default_value and hasattr(self, 'section_text'):
            self.section_text.delete(1.0, tk.END)
            self.section_text.insert(1.0, default_value)
            ModernPopup.showinfo(self.root,"Reset", f"Reset {key.replace('_', ' ').title()} to default value.")
        else:
            ModernPopup.showinfo(self.root,"No Default", f"No default value available for {key.replace('_', ' ').title()}.")

    def on_sidebar_select(self, event=None):
        idxs = self.sidebar.selection()
        if idxs:
            idx = int(idxs[0])
            self.show_section_editor(idx)

    def show_section_editor(self, idx):
        """Show section editor for domain-specific configuration"""
        # Clear previous widgets properly
        for widget in self.editor_frame.winfo_children():
            # Only keep the button_frame at the bottom
            if hasattr(self, 'button_frame') and widget == self.button_frame:
                continue
            widget.destroy()
        
        # Clear any previous widget references
        if hasattr(self, 'seo_plugin_var'):
            delattr(self, 'seo_plugin_var')
        if hasattr(self, 'section_text'):
            delattr(self, 'section_text')
        if hasattr(self, 'section_widget'):
            delattr(self, 'section_widget')
        label, key, _icon_unused = self.config_sections[idx]
        # Section label
        section_label = ttk.Label(self.editor_frame, text=label, font=("Arial", 12, "bold"))
        section_label.pack(anchor=tk.W, pady=(0, 6))
        
        # Add helpful descriptions and guidance for individual prompt sections
        if key == "seo_plugin_settings":
            desc_text = ("SEO Plugin Configuration\n"
                        "Configure which SEO plugin version your WordPress site uses.\n\n"
                        "Plugin Versions:\n"
                        "• New Version: All in One SEO Pro v4.7.3+ (example-sports-site.com, example-spurs-site.com, example-leeds-site.com)\n"
            "• Old Version: All in One SEO Pack Pro v2.7.1 (example-arsenal-site.com, example-city-site.com)\n\n"
                        "Note: This setting determines how SEO metadata is formatted and sent to your WordPress site.")
            desc_label = ttk.Label(self.editor_frame, text=desc_text, font=("Arial", 9), foreground="#2c3e50", justify=tk.LEFT)
            desc_label.pack(anchor=tk.W, pady=(0, 10))
        elif key == "seo_title_meta_prompt":
            desc_text = ("SEO Title & Meta Description Generator\n"
                        "This prompt creates SEO-optimized titles (50-59 chars) and meta descriptions (155-160 chars).\n\n"
                        "How to customize:\n"
                        "• Modify character limits and formatting rules\n"
                        "• Add specific keyword requirements\n"
                        "• Adjust tone and style preferences\n\n"
                        "Tip: Use clear instructions with specific character limits and examples")
            desc_label = ttk.Label(self.editor_frame, text=desc_text, font=("Arial", 9), foreground="#2c3e50", justify=tk.LEFT)
            desc_label.pack(anchor=tk.W, pady=(0, 10))
        elif key == "tag_generation_prompt":
            desc_text = ("Tag Extraction System\n"
                        "This prompt extracts relevant tags from article content (players, clubs, competitions).\n\n"
                        "How to customize:\n"
                        "• Add specific tag categories to focus on\n"
                        "• Modify output format (comma-separated, JSON, etc.)\n"
                        "• Include/exclude certain types of entities\n\n"
                        "Tip: Be specific about what to extract and how to format the output")
            desc_label = ttk.Label(self.editor_frame, text=desc_text, font=("Arial", 9), foreground="#2c3e50", justify=tk.LEFT)
            desc_label.pack(anchor=tk.W, pady=(0, 10))
        elif key == "keyphrase_extraction_prompt":
            desc_text = ("SEO Keyphrase Extraction\n"
                        "This prompt identifies focus keyphrases and additional SEO terms for search optimization.\n\n"
                        "How to customize:\n"
                        "• Adjust the number of keyphrases to extract\n"
                        "• Modify keyphrase length requirements (2-4 words)\n"
                        "• Add industry-specific terminology guidelines\n\n"
                        "Tip: Provide clear rules for keyphrase selection and formatting")
            desc_label = ttk.Label(self.editor_frame, text=desc_text, font=("Arial", 9), foreground="#2c3e50", justify=tk.LEFT)
            desc_label.pack(anchor=tk.W, pady=(0, 10))
        elif key == "style_prompt":
            desc_text = ("Article Rewriting Style Guide\n"
                        "This prompt controls how articles are rewritten and formatted for your blog.\n\n"
                        "How to customize:\n"
                        "• Adjust tone and voice (professional, casual, enthusiastic)\n"
                        "• Modify structural requirements (headings, paragraphs, word count)\n"
                        "• Add specific formatting rules and HTML requirements\n\n"
                        "Tip: Include detailed formatting rules and examples")
            desc_label = ttk.Label(self.editor_frame, text=desc_text, font=("Arial", 9), foreground="#2c3e50", justify=tk.LEFT)
            desc_label.pack(anchor=tk.W, pady=(0, 10))
        else:
            # General guidance for JSON configuration files
            desc_text = ("Configuration Settings\n"
                        "This section contains JSON configuration data for the system.\n\n"
                        "How to edit:\n"
                        "• Add new entries: Insert new key-value pairs following the existing format\n"
                        "• Edit existing entries: Modify values while keeping the JSON structure\n"
                        "• Use proper JSON syntax: strings in quotes, arrays with [], objects with {}\n\n"
                        "Tip: Always validate JSON syntax before saving to avoid errors")
            desc_label = ttk.Label(self.editor_frame, text=desc_text, font=("Arial", 9), foreground="#2c3e50", justify=tk.LEFT)
            desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Show current domain info
        if self.current_domain:
            domain_info = ttk.Label(self.editor_frame, text=f"Editing for domain: {self.current_domain}", 
                                  font=("Arial", 9, "italic"), foreground="blue")
            domain_info.pack(anchor=tk.W, pady=(0, 10))
        else:
            warning_info = ttk.Label(self.editor_frame, text="No domain selected - using base configuration", 
                                   font=("Arial", 9, "italic"), foreground="orange")
            warning_info.pack(anchor=tk.W, pady=(0, 10))
        
        # Editor - Special handling for SEO plugin settings
        if key == "seo_plugin_settings":
            # Create dropdown for SEO plugin version selection
            plugin_frame = ttk.Frame(self.editor_frame)
            plugin_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(plugin_frame, text="SEO Plugin Version:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
            
            self.seo_plugin_var = tk.StringVar()
            plugin_dropdown = ttk.Combobox(plugin_frame, textvariable=self.seo_plugin_var, 
                                         values=["new", "old"], state="readonly", width=20)
            plugin_dropdown.pack(anchor=tk.W, pady=(5, 0))
            
            # Load current value from domain-specific config
            import json
            config_dir = self.get_current_config_dir()
            config_file = os.path.join(config_dir, "default.json")
            current_value = "new"  # Default value
            
            # Try to load from domain-specific config first
            if os.path.exists(config_file):
                try:
                    with open(config_file) as f:
                        domain_config = json.load(f)
                        current_value = domain_config.get("seo_plugin_version", "new")
                except Exception as e:
                    self.logger.warning(f"Error loading SEO plugin version from domain config: {e}")
            
            # Fall back to main config if not found in domain config
            if current_value == "new" and "seo_plugin_version" in self.config:
                current_value = self.config.get("seo_plugin_version", "new")
            
            self.seo_plugin_var.set(current_value)
            
            # Add descriptions
            desc_frame = ttk.Frame(self.editor_frame)
            desc_frame.pack(fill=tk.X, pady=(10, 0))
            
            new_desc = ttk.Label(desc_frame, text="• New Version (v4.7.3+): For example-sports-site.com, example-spurs-site.com, example-leeds-site.com", 
                               font=("Arial", 9), foreground="#27ae60")
            new_desc.pack(anchor=tk.W)
            
            old_desc = ttk.Label(desc_frame, text="• Old Version (v2.7.1): For example-arsenal-site.com, example-city-site.com", 
                               font=("Arial", 9), foreground="#e74c3c")
            old_desc.pack(anchor=tk.W)
            
            # Add checkbox for printing SEO details (only for Old Plugin)
            seo_print_frame = ttk.Frame(self.editor_frame)
            seo_print_frame.pack(fill=tk.X, pady=(15, 0))
            
            self.print_seo_details_var = tk.BooleanVar()
            self.print_seo_checkbox = ttk.Checkbutton(
                seo_print_frame, 
                text="Print SEO details at the end of the blog",
                variable=self.print_seo_details_var
            )
            self.print_seo_checkbox.pack(anchor=tk.W)
            
            # Load current checkbox value from domain-specific config
            try:
                with open(config_file) as f:
                    domain_config = json.load(f)
                    current_checkbox_value = domain_config.get("print_seo_details_old_plugin", False)
                    self.print_seo_details_var.set(current_checkbox_value)
            except Exception as e:
                self.logger.warning(f"Error loading print_seo_details setting: {e}")
                self.print_seo_details_var.set(False)
            
            # Add description for the checkbox
            checkbox_desc = ttk.Label(seo_print_frame, 
                                    text="When checked, SEO Title, Description, and Keywords will be automatically\nappended to the end of blog posts (useful for Old Plugin compatibility)", 
                                    font=("Arial", 8), foreground="#666666")
            checkbox_desc.pack(anchor=tk.W, pady=(5, 0))
            
            # Function to show/hide checkbox based on plugin version
            def on_plugin_version_change(*args):
                if self.seo_plugin_var.get() == "old":
                    seo_print_frame.pack(fill=tk.X, pady=(15, 0))
                else:
                    seo_print_frame.pack_forget()
            
            # Bind the function to plugin version changes
            self.seo_plugin_var.trace_add('write', on_plugin_version_change)
            
            # Initial state based on current selection
            on_plugin_version_change()
            
            # Store reference for saving
            self.section_widget = plugin_dropdown
        else:
            # Regular text editor for other sections
            self.section_text = scrolledtext.ScrolledText(self.editor_frame, height=16)
            self.section_text.pack(fill=tk.BOTH, expand=True)
            self.section_widget = self.section_text
        
        # Load configuration from domain-specific directory
        config_dir = self.get_current_config_dir()
        value = self.config.get(key, "" if key in ("style_prompt", "seo_title_meta_prompt", "tag_generation_prompt", "keyphrase_extraction_prompt") else {} if key.endswith("links") or key.endswith("keywords") or key.endswith("synonyms") or key == "gemini_prompts" else [] if key in ("static_clubs", "stop_words", "do_follow_urls") else "")
        
        # Import json at the beginning to avoid scope issues
        import json
        
        # Try to load from specific config files in domain directory
        if key in ("seo_title_meta_prompt", "tag_generation_prompt", "keyphrase_extraction_prompt"):
            # Load individual prompts from gemini_prompts.json
            config_file = os.path.join(config_dir, "gemini_prompts.json")
            if os.path.exists(config_file):
                try:
                    with open(config_file) as f:
                        data = json.load(f)
                        value = data.get(key, "")
                except Exception as e:
                    self.logger.warning(f"Could not load {key} from gemini_prompts.json: {e}")
                    # Fall back to main configs directory
                    main_config_file = os.path.join(self.base_config_dir, "gemini_prompts.json")
                    if os.path.exists(main_config_file):
                        try:
                            with open(main_config_file) as f:
                                data = json.load(f)
                                value = data.get(key, "")
                        except Exception as e2:
                            self.logger.warning(f"Could not load {key} from main gemini_prompts.json: {e2}")
                            value = ""
            else:
                # Fall back to main configs directory
                main_config_file = os.path.join(self.base_config_dir, "gemini_prompts.json")
                if os.path.exists(main_config_file):
                    try:
                        with open(main_config_file) as f:
                            data = json.load(f)
                            value = data.get(key, "")
                            if not value:
                                self.logger.warning(f"Empty value for {key} in main gemini_prompts.json, using hardcoded default")
                                # Provide hardcoded defaults
                                defaults = {
                                    "seo_title_meta_prompt": "You are a passionate Premier League football blogger.\n\n1. Read the article content below and identify its one primary subject (player, event, or transfer saga). Then rewrite the original title into a single, sharp, SEO-friendly headline.\n\n- Preserve the correct capitalization of all proper nouns exactly as in the original.\n- Use sentence case—capitalize only the first word and proper nouns. All other words should be lowercase. **Example: Tottenham: Should Spurs chase Kudus over Crystal Palace's target?**\n- The headline must be **strictly** between 50 and 59 characters in length (counting spaces and punctuation).\n- **Crucially, your final output must be precisely within this character range. Do NOT go under 50 characters or over 59 characters.**\n- Ensure the headline is a grammatically complete and coherent sentence within the character limits.\n- Always use British English spelling for 'rumours' (with a 'u').\n\n2. Write an SEO meta description for the article:\n\n- Include 2–3 relevant keywords from the article.\n- No hashtags or special formatting.\n- Must be between 155 and 160 characters (inclusive).\n- Return plain text only, with no quotes or extra spaces.\n- Always use British English spelling for 'rumours' (with a 'u').\n\nReturn format:\n\nSEO_TITLE:\n<title here>\n\nMETA:\n<meta description here>",
                                    "tag_generation_prompt": "Extract only the full names of football players and the full names of the clubs mentioned in this article.\nReturn them as a comma-separated list with no extra punctuation.\n\nArticle Content:\n\\\"\\\"\\\"\n{content}\n\\\"\\\"\\\"",
                                    "keyphrase_extraction_prompt": "You are an SEO expert specializing in football content. Analyze the following article and extract:\n\n1. **Focus Keyphrase**: The single most important 2-4 word keyphrase that represents the core topic of this article. This should be what people would search for to find this specific article.\n\n2. **Additional Keyphrases**: 3-5 additional relevant keyphrases (2-4 words each) that are naturally mentioned in the content and would help with SEO ranking.\n\nRules:\n- Focus on keyphrases that football fans would actually search for\n- Include player names, club names, and football-specific terms\n- Avoid generic words like 'football', 'player', 'team' unless they're part of a specific phrase\n- Keyphrases should feel natural and be present in the content\n- Use British English spelling (e.g., 'rumours' not 'rumors')\n\nReturn format:\nFOCUS_KEYPHRASE:\n<main keyphrase here>\n\nADDITIONAL_KEYPHRASES:\n<keyphrase 1>\n<keyphrase 2>\n<keyphrase 3>\n<keyphrase 4>\n<keyphrase 5>\n\nArticle Title: {title}\n\nArticle Content:\n{content}"
                                }
                                value = defaults.get(key, "")
                    except Exception as e:
                        self.logger.warning(f"Could not load {key} from main gemini_prompts.json: {e}")
                        value = ""
                else:
                    self.logger.warning(f"Main gemini_prompts.json not found at {main_config_file}")
                    # Provide hardcoded defaults as last resort
                    defaults = {
                        "seo_title_meta_prompt": "You are a passionate Premier League football blogger.\n\n1. Read the article content below and identify its one primary subject (player, event, or transfer saga). Then rewrite the original title into a single, sharp, SEO-friendly headline.\n\n- Preserve the correct capitalization of all proper nouns exactly as in the original.\n- Use sentence case—capitalize only the first word and proper nouns. All other words should be lowercase. **Example: Tottenham: Should Spurs chase Kudus over Crystal Palace's target?**\n- The headline must be **strictly** between 50 and 59 characters in length (counting spaces and punctuation).\n- **Crucially, your final output must be precisely within this character range. Do NOT go under 50 characters or over 59 characters.**\n- Ensure the headline is a grammatically complete and coherent sentence within the character limits.\n- Always use British English spelling for 'rumours' (with a 'u').\n\n2. Write an SEO meta description for the article:\n\n- Include 2–3 relevant keywords from the article.\n- No hashtags or special formatting.\n- Must be between 155 and 160 characters (inclusive).\n- Return plain text only, with no quotes or extra spaces.\n- Always use British English spelling for 'rumours' (with a 'u').\n\nReturn format:\n\nSEO_TITLE:\n<title here>\n\nMETA:\n<meta description here>",
                        "tag_generation_prompt": "Extract only the full names of football players and the full names of the clubs mentioned in this article.\nReturn them as a comma-separated list with no extra punctuation.\n\nArticle Content:\n\\\"\\\"\\\"\n{content}\n\\\"\\\"\\\"",
                        "keyphrase_extraction_prompt": "You are an SEO expert specializing in football content. Analyze the following article and extract:\n\n1. **Focus Keyphrase**: The single most important 2-4 word keyphrase that represents the core topic of this article. This should be what people would search for to find this specific article.\n\n2. **Additional Keyphrases**: 3-5 additional relevant keyphrases (2-4 words each) that are naturally mentioned in the content and would help with SEO ranking.\n\nRules:\n- Focus on keyphrases that football fans would actually search for\n- Include player names, club names, and football-specific terms\n- Avoid generic words like 'football', 'player', 'team' unless they're part of a specific phrase\n- Keyphrases should feel natural and be present in the content\n- Use British English spelling (e.g., 'rumours' not 'rumors')\n\nReturn format:\nFOCUS_KEYPHRASE:\n<main keyphrase here>\n\nADDITIONAL_KEYPHRASES:\n<keyphrase 1>\n<keyphrase 2>\n<keyphrase 3>\n<keyphrase 4>\n<keyphrase 5>\n\nArticle Title: {title}\n\nArticle Content:\n{content}"
                    }
                    value = defaults.get(key, "")
        elif key not in ("style_prompt", "gemini_prompts"):
            config_file = os.path.join(config_dir, f"{key}.json")
            if os.path.exists(config_file):
                try:
                    with open(config_file) as f:
                        value = json.load(f)
                except Exception as e:
                    self.logger.warning(f"Could not load {key}.json from domain directory: {e}")
        elif key == "style_prompt":
            # Style prompt is stored differently
            config_file = os.path.join(config_dir, "style_prompt.json")
            if os.path.exists(config_file):
                try:
                    with open(config_file) as f:
                        data = json.load(f)
                        value = data.get("style_prompt", "")
                except Exception as e:
                    self.logger.warning(f"Could not load style_prompt.json from domain directory: {e}")
        elif key == "gemini_prompts":
            # Load enhanced Gemini prompts
            config_file = os.path.join(config_dir, "gemini_prompts.json")
            if os.path.exists(config_file):
                try:
                    import json
                    with open(config_file) as f:
                        value = json.load(f)
                except Exception as e:
                    self.logger.warning(f"Could not load gemini_prompts.json from domain directory: {e}")
                    # Fall back to main configs directory
                    main_config_file = os.path.join(self.base_config_dir, "gemini_prompts.json")
                    if os.path.exists(main_config_file):
                        try:
                            with open(main_config_file) as f:
                                value = json.load(f)
                        except Exception as e2:
                            self.logger.warning(f"Could not load gemini_prompts.json from main configs: {e2}")
                            value = {}
        
        import json
        if key == "seo_plugin_settings":
            # SEO plugin settings are handled by the dropdown widget
            pass
        elif key in ("style_prompt", "seo_title_meta_prompt", "tag_generation_prompt", "keyphrase_extraction_prompt"):
            self.section_text.insert(tk.END, value)
        else:
            self.section_text.insert(tk.END, json.dumps(value, indent=2))
        self.current_section_key = key

    def save_current_section(self):
        """Save current section to domain-specific configuration"""
        key = self.current_section_key
        
        if key == "seo_plugin_settings":
            # Get value from dropdown widget
            plugin_version = self.seo_plugin_var.get()
            self.config["seo_plugin_version"] = plugin_version
            
            # Save to domain-specific config file
            import json
            config_dir = self.get_current_config_dir()
            config_file = os.path.join(config_dir, "default.json")
            
            # Load existing config or create new one
            domain_config = {}
            if os.path.exists(config_file):
                try:
                    with open(config_file) as f:
                        domain_config = json.load(f)
                except Exception as e:
                    self.logger.warning(f"Error loading domain config: {e}")
            
            # Update SEO plugin version
            domain_config["seo_plugin_version"] = plugin_version
            
            # Save checkbox value for old plugin
            if hasattr(self, 'print_seo_details_var'):
                domain_config["print_seo_details_old_plugin"] = self.print_seo_details_var.get()
            
            # Save updated config
            try:
                with open(config_file, "w") as f:
                    json.dump(domain_config, f, indent=2)
                success_msg = f"SEO plugin version saved: {plugin_version}"
                if hasattr(self, 'print_seo_details_var') and plugin_version == "old":
                    checkbox_status = "enabled" if self.print_seo_details_var.get() else "disabled"
                    success_msg += f"\nPrint SEO details: {checkbox_status}"
                ModernPopup.showinfo(self.root,"Success", success_msg)
            except Exception as e:
                ModernPopup.showerror(self.root,"Error", f"Failed to save SEO plugin settings: {e}")
            return
        
        text = self.section_text.get("1.0", tk.END).strip()
        config_dir = self.get_current_config_dir()
        
        import json
        try:
            if key == "style_prompt":
                # Save to both main config and style_prompt.json in domain directory
                self.config[key] = text
                style_prompt_file = os.path.join(config_dir, "style_prompt.json")
                with open(style_prompt_file, "w") as f:
                    json.dump({"style_prompt": text}, f, indent=2)
            elif key in ("seo_title_meta_prompt", "tag_generation_prompt", "keyphrase_extraction_prompt"):
                # Save individual prompts to gemini_prompts.json
                gemini_prompts_file = os.path.join(config_dir, "gemini_prompts.json")
                
                # Load existing data or create new structure
                gemini_data = {}
                if os.path.exists(gemini_prompts_file):
                    try:
                        with open(gemini_prompts_file) as f:
                            gemini_data = json.load(f)
                    except Exception as e:
                        self.logger.warning(f"Error loading gemini_prompts.json: {e}")
                        # Try to load from main configs directory as fallback
                        main_config_file = os.path.join(self.base_config_dir, "gemini_prompts.json")
                        if os.path.exists(main_config_file):
                            try:
                                with open(main_config_file) as f:
                                    gemini_data = json.load(f)
                            except Exception as e2:
                                self.logger.warning(f"Error loading main gemini_prompts.json: {e2}")
                else:
                    # Copy from main configs directory if available
                    main_config_file = os.path.join(self.base_config_dir, "gemini_prompts.json")
                    if os.path.exists(main_config_file):
                        try:
                            with open(main_config_file) as f:
                                gemini_data = json.load(f)
                        except Exception as e:
                            self.logger.warning(f"Error loading main gemini_prompts.json: {e}")
                
                # Update the specific prompt
                gemini_data[key] = text
                
                # Save to domain-specific file
                with open(gemini_prompts_file, "w") as f:
                    json.dump(gemini_data, f, indent=2)
                
                # Update main config as well
                if 'gemini_prompts' not in self.config:
                    self.config['gemini_prompts'] = {}
                self.config['gemini_prompts'][key] = text
                
            elif key == "gemini_prompts":
                # Save enhanced Gemini prompts
                data = json.loads(text)
                self.config[key] = data
                gemini_prompts_file = os.path.join(config_dir, "gemini_prompts.json")
                with open(gemini_prompts_file, "w") as f:
                    json.dump(data, f, indent=2)
            else:
                # Parse JSON and save to both main config and specific file in domain directory
                data = json.loads(text)
                self.config[key] = data
                specific_file = os.path.join(config_dir, f"{key}.json")
                with open(specific_file, "w") as f:
                    json.dump(data, f, indent=2)
            
            # Save main config
            self.save_config()
            
            domain_info = f" for domain: {self.current_domain}" if self.current_domain else ""
            self.logger.info(f"[OK] Saved {key.replace('_', ' ').title()}{domain_info}")
            ModernPopup.showinfo(self.root,"Success", f"Saved {key.replace('_', ' ').title()}{domain_info} successfully.")
            
        except Exception as e:
            self.logger.error(f"Error saving {key}: {e}")
            ModernPopup.showerror(self.root,"Invalid Data", f"Error in {key}: {e}")

    def create_source_config_tab(self):
        self.source_config_frame = ttk.Frame(self.notebook)
        self._add_tab(self.source_config_frame, "Source & Automation", "wrench")

        self.source_edit_mode = False
        self.source_config_vars = {}
        self.source_config_prev = {}

        # Credentials info section
        info_frame = ttk.LabelFrame(self.source_config_frame, text="Credential Management", padding=10)
        info_frame.pack(pady=10, padx=40, fill=tk.X)
        
        info_lines = (
            "WordPress credentials and API keys → manage in the Authentication tab.\n"
            "Source URLs and CSS selectors → manage in the Article Selector section below.\n"
            "How it works: The app fetches the Source URL, finds article links using the CSS Selector, then scrapes and posts each article to WordPress."
        )
        ttk.Label(info_frame, text=info_lines, foreground="#1a56a4", font=("Arial", 9), wraplength=800, justify=tk.LEFT).pack(anchor=tk.W)

        # Article Selector section
        self.create_article_selector_section()

        # Frame with edit icon
        form = ttk.LabelFrame(self.source_config_frame, text="Source & Automation Settings", padding=20)
        form.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)
        self.source_config_form = form

        # Edit icon/button
        self.edit_icon_btn = self._btn(form, "Edit", "pencil", width=7, command=self.toggle_source_edit_mode)
        self.edit_icon_btn.place(relx=1.0, x=-10, y=10, anchor="ne")

        # Fields - Only source and automation settings (credentials are managed in Authentication tab)
        fields = [
            ("Source URL", 'source_url'),
            ("Article Selector", 'article_selector'),
            ("Max Articles", 'max_articles'),
            ("Timeout (seconds)", 'timeout'),
            ("Headless Mode", 'headless_mode')
        ]
        self.source_config_fields = fields
        for i, (label, key) in enumerate(fields):
            ttk.Label(form, text=label+":").grid(row=i, column=0, sticky=tk.W, pady=5)
            if key == 'headless_mode':
                var = tk.BooleanVar(value=self.config.get(key, True))
                entry = ttk.Checkbutton(form, variable=var, state='disabled')
                entry.grid(row=i, column=1, sticky=tk.W, pady=5, padx=10)
            elif key in ('max_articles', 'timeout'):
                var = tk.IntVar(value=self.config.get(key, 2 if key=='max_articles' else 10))
                entry = ttk.Spinbox(form, from_=1, to=60, textvariable=var, width=10, state='readonly')
                entry.grid(row=i, column=1, sticky=tk.W, pady=5, padx=10)
            else:
                var = tk.StringVar(value=self.config.get(key, ''))
                show = '*' if 'password' in key or 'key' in key else None
                entry = ttk.Entry(form, textvariable=var, width=50, state='readonly', show=show)
                entry.grid(row=i, column=1, pady=5, padx=10)
            self.source_config_vars[key] = (var, entry)

        # Save/Cancel/Set Default buttons (hidden unless in edit mode)
        self.source_btn_frame = ttk.Frame(form)
        self.source_btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        self.save_btn = ttk.Button(self.source_btn_frame, text="Save", command=self.save_source_config, style="Accent.TButton")
        self.cancel_btn = ttk.Button(self.source_btn_frame, text="Cancel", command=self.cancel_source_edit)
        self.set_default_btn = ttk.Button(self.source_btn_frame, text="Set as Default", command=self.set_source_config_default)
        self.save_btn.pack(side=tk.LEFT, padx=10)
        self.cancel_btn.pack(side=tk.LEFT, padx=10)
        self.set_default_btn.pack(side=tk.LEFT, padx=10)
        self.source_btn_frame.grid_remove()

    def create_article_selector_section(self):
        """Create the Article Selector section for managing multiple source URLs"""
        selector_frame = ttk.LabelFrame(self.source_config_frame, text="Article Selector", padding=15)
        selector_frame.pack(pady=10, padx=40, fill=tk.BOTH, expand=True)

        # Description with help text
        desc_text = (
            "Add website URLs to scrape articles from. You can activate MULTIPLE sources at once — "
            "the automation will pull articles from all active sources.\n"
            "Double-click a source to toggle active/inactive. Use 'Auto-Extract Selectors' when adding a new source."
        )
        ttk.Label(selector_frame, text=desc_text, font=("Arial", 9), foreground="#444", wraplength=700, justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 10))

        # Active sources summary bar
        self.active_sources_summary = tk.StringVar(value="No active sources")
        summary_frame = ttk.Frame(selector_frame)
        summary_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(summary_frame, text="Active:", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        ttk.Label(summary_frame, textvariable=self.active_sources_summary, font=("Arial", 9), foreground="#0078d4").pack(side=tk.LEFT, padx=(5, 0))

        # Create frame for source list and controls
        main_frame = ttk.Frame(selector_frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left side - Source list
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        ttk.Label(list_frame, text="Available Sources:", font=("Arial", 10, "bold")).pack(anchor=tk.W)

        # Create treeview for sources
        columns = ('Active', 'Name', 'URL', 'Selector')
        self.sources_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)

        # Define headings
        self.sources_tree.heading('Active', text='Active')
        self.sources_tree.heading('Name', text='Source Name')
        self.sources_tree.heading('URL', text='URL')
        self.sources_tree.heading('Selector', text='CSS Selector')

        # Define column widths
        self.sources_tree.column('Active', width=60)
        self.sources_tree.column('Name', width=200)
        self.sources_tree.column('URL', width=300)
        self.sources_tree.column('Selector', width=200)

        # Scrollbar for treeview
        sources_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.sources_tree.yview)
        self.sources_tree.configure(yscrollcommand=sources_scrollbar.set)

        # Pack treeview and scrollbar
        self.sources_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sources_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Right side - Controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        ttk.Label(controls_frame, text="Actions:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))

        # Control buttons
        self._btn(controls_frame, "Add Source", "plus", command=self.add_source_url, width=18).pack(pady=2, fill=tk.X)
        self._btn(controls_frame, "Bulk Import", "download", command=self.bulk_import_sources, width=18).pack(pady=2, fill=tk.X)
        self._btn(controls_frame, "Edit Source", "pencil", command=self.edit_source_url, width=18).pack(pady=2, fill=tk.X)
        self._btn(controls_frame, "Remove Source", "trash", command=self.remove_source_url, width=18).pack(pady=2, fill=tk.X)

        ttk.Separator(controls_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        self._btn(controls_frame, "Toggle Active", "check", command=self.toggle_active_source, width=18, style="Accent.TButton").pack(pady=2, fill=tk.X)
        self._btn(controls_frame, "Activate All", "toggle", command=self.activate_all_sources, width=18).pack(pady=2, fill=tk.X)
        self._btn(controls_frame, "Deactivate All", "circle", command=self.deactivate_all_sources, width=18).pack(pady=2, fill=tk.X)

        ttk.Separator(controls_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        self._btn(controls_frame, "Test Source", "search", command=self.test_selected_source, width=18).pack(pady=2, fill=tk.X)
        self._btn(controls_frame, "Refresh List", "refresh", command=self.refresh_sources_list, width=18).pack(pady=2, fill=tk.X)

        # Load sources into the tree
        self.refresh_sources_list()

        # Bind double-click to toggle active
        self.sources_tree.bind('<Double-1>', lambda e: self.toggle_active_source())

    def refresh_sources_list(self):
        """Refresh the sources list in the treeview"""
        # Clear existing items
        for item in self.sources_tree.get_children():
            self.sources_tree.delete(item)

        # Get source URLs from config
        source_urls = self.config.get('source_urls', [])

        # If no source_urls in config, create from legacy format
        if not source_urls and self.config.get('source_url'):
            source_urls = [{
                'name': 'Default Source',
                'url': self.config.get('source_url', ''),
                'selector': self.config.get('article_selector', ''),
                'active': True
            }]
            self.config['source_urls'] = source_urls
            self.save_config()

        # Add sources to tree
        active_names = []
        for i, source in enumerate(source_urls):
            is_active = source.get('active', False)
            active_text = "[ON]" if is_active else "[OFF]"
            self.sources_tree.insert('', 'end', values=(
                active_text,
                source.get('name', f'Source {i+1}'),
                source.get('url', ''),
                source.get('selector', '')
            ))
            if is_active:
                active_names.append(source.get('name', f'Source {i+1}'))

        # Update active sources summary
        if hasattr(self, 'active_sources_summary'):
            if active_names:
                self.active_sources_summary.set(f"{len(active_names)} source(s): {', '.join(active_names)}")
            else:
                self.active_sources_summary.set("No active sources — select at least one!")

    def add_source_url(self):
        """Add a new source URL"""
        self.show_source_dialog()

    def edit_source_url(self):
        """Edit the selected source URL"""
        selection = self.sources_tree.selection()
        if not selection:
            ModernPopup.showwarning(self.root,"No Selection", "Please select a source to edit.")
            return
        
        # Get the index of selected item
        item = selection[0]
        index = self.sources_tree.index(item)
        
        source_urls = self.config.get('source_urls', [])
        if index < len(source_urls):
            self.show_source_dialog(source_urls[index], index)

    def remove_source_url(self):
        """Remove the selected source URL(s)"""
        selection = self.sources_tree.selection()
        if not selection:
            ModernPopup.showwarning(self.root,"No Selection", "Please select a source to remove.")
            return

        count = len(selection)
        msg = f"Are you sure you want to remove {count} source(s)?" if count > 1 else "Are you sure you want to remove this source?"
        if ModernPopup.askyesno(self.root,"Confirm Removal", msg):
            source_urls = self.config.get('source_urls', [])
            # Get indices in reverse order to avoid shifting
            indices = sorted([self.sources_tree.index(item) for item in selection], reverse=True)
            removed_names = []
            for index in indices:
                if index < len(source_urls):
                    removed = source_urls.pop(index)
                    removed_names.append(removed.get('name', 'Unknown'))

            # If no active sources remain, activate the first one
            active_sources = [s for s in source_urls if s.get('active', False)]
            if not active_sources and source_urls:
                source_urls[0]['active'] = True
                self.update_active_source_config(source_urls[0])
            elif active_sources:
                self.update_active_source_config(active_sources[0])

            self.config['source_urls'] = source_urls
            self.save_config()
            self.save_main_config()
            self.refresh_sources_list()
            self.logger.info(f"Removed source(s): {', '.join(removed_names)}")

    def set_active_source(self):
        """Legacy method — redirects to toggle_active_source for backward compatibility"""
        self.toggle_active_source()

    def toggle_active_source(self):
        """Toggle active state of selected source(s) — supports multiple active sources"""
        selection = self.sources_tree.selection()
        if not selection:
            ModernPopup.showwarning(self.root,"No Selection", "Please select one or more sources to toggle.")
            return

        source_urls = self.config.get('source_urls', [])
        toggled_names = []

        for item in selection:
            index = self.sources_tree.index(item)
            if index < len(source_urls):
                # Toggle active state
                source_urls[index]['active'] = not source_urls[index].get('active', False)
                state = "activated" if source_urls[index]['active'] else "deactivated"
                name = source_urls[index].get('name', 'Unknown')
                toggled_names.append(f"{name} ({state})")

        # Sync the first active source to legacy config fields
        active_sources = [s for s in source_urls if s.get('active', False)]
        if active_sources:
            self.update_active_source_config(active_sources[0])

        self.config['source_urls'] = source_urls
        self.save_config()
        self.save_main_config()
        self.refresh_sources_list()

        # Update the source config form
        if hasattr(self, 'source_config_vars') and active_sources:
            self.source_config_vars['source_url'][0].set(active_sources[0]['url'])
            self.source_config_vars['article_selector'][0].set(active_sources[0]['selector'])

        self.logger.info(f"Toggled sources: {', '.join(toggled_names)}")
        ModernPopup.showinfo(self.root,"Sources Updated", "\n".join(toggled_names))

    def activate_all_sources(self):
        """Activate all sources"""
        source_urls = self.config.get('source_urls', [])
        if not source_urls:
            ModernPopup.showwarning(self.root,"No Sources", "No sources configured. Add a source first.")
            return
        for source in source_urls:
            source['active'] = True
        if source_urls:
            self.update_active_source_config(source_urls[0])
        self.config['source_urls'] = source_urls
        self.save_config()
        self.save_main_config()
        self.refresh_sources_list()
        self.logger.info(f"Activated all {len(source_urls)} sources")
        ModernPopup.showinfo(self.root,"Success", f"All {len(source_urls)} sources activated.")

    def deactivate_all_sources(self):
        """Deactivate all sources"""
        source_urls = self.config.get('source_urls', [])
        for source in source_urls:
            source['active'] = False
        self.config['source_urls'] = source_urls
        self.save_config()
        self.save_main_config()
        self.refresh_sources_list()
        self.logger.info("Deactivated all sources")
        ModernPopup.showinfo(self.root,"Success", "All sources deactivated.")

    def bulk_import_sources(self):
        """Import multiple sources at once by pasting URLs"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Bulk Import Sources")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Bulk Import Sources",
                  font=('TkDefaultFont', 14, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(main_frame,
                  text="Paste one URL per line. The app will auto-detect the best CSS selector for each URL.\n"
                       "URLs without http:// or https:// will be auto-corrected.",
                  font=('TkDefaultFont', 9), foreground='#444', wraplength=550).pack(anchor=tk.W, pady=(0, 10))

        # Text area for URLs
        text_frame = ttk.LabelFrame(main_frame, text="URLs (one per line)", padding=5)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        url_text = tk.Text(text_frame, wrap=tk.WORD, height=12, font=("Consolas", 10))
        url_text.pack(fill=tk.BOTH, expand=True)

        # Options
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        auto_activate = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Set imported sources as active", variable=auto_activate).pack(side=tk.LEFT)

        auto_detect_selector = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Auto-detect CSS selectors", variable=auto_detect_selector).pack(side=tk.LEFT, padx=(20, 0))

        # Progress
        progress_var = tk.StringVar(value="")
        ttk.Label(main_frame, textvariable=progress_var, foreground="#666").pack(anchor=tk.W)

        def do_import():
            raw = url_text.get("1.0", tk.END).strip()
            if not raw:
                ModernPopup.showwarning(self.root,"Empty", "Please paste at least one URL.")
                return

            urls = [line.strip() for line in raw.splitlines() if line.strip()]
            if not urls:
                ModernPopup.showwarning(self.root,"Empty", "No valid URLs found.")
                return

            source_urls = self.config.get('source_urls', [])
            existing_urls = {s.get('url', '') for s in source_urls}
            added = 0
            skipped = 0

            for i, url in enumerate(urls):
                progress_var.set(f"Processing {i+1}/{len(urls)}: {url[:50]}...")
                dialog.update()

                # Normalize URL
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url

                if url in existing_urls:
                    skipped += 1
                    continue

                # Auto-detect selector
                selector = ""
                if auto_detect_selector.get():
                    try:
                        from auto_blogger.css_selector_extractor import CSSelectorExtractor
                        extractor = CSSelectorExtractor(self.logger)
                        result = extractor.analyze_url(url)
                        if result.get('success') and result.get('selectors'):
                            selector = result['selectors'][0]['selector']
                    except Exception as e:
                        self.logger.debug(f"Auto-detect failed for {url}: {e}")

                if not selector:
                    selector = "article h2 a"  # Safe default

                # Generate name from domain
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(url).netloc.replace('www.', '')
                    name = domain.split('.')[0].title()
                except Exception:
                    name = f"Source {len(source_urls) + 1}"

                new_source = {
                    'name': name,
                    'url': url,
                    'selector': selector,
                    'active': auto_activate.get()
                }
                source_urls.append(new_source)
                existing_urls.add(url)
                added += 1

            self.config['source_urls'] = source_urls

            # Sync first active to legacy fields
            active_sources = [s for s in source_urls if s.get('active', False)]
            if active_sources:
                self.update_active_source_config(active_sources[0])

            self.save_config()
            self.save_main_config()
            self.refresh_sources_list()

            progress_var.set("")
            self.logger.info(f"Bulk import: {added} added, {skipped} skipped (duplicates)")
            ModernPopup.showinfo(self.root,"Import Complete",
                                f"Added: {added} source(s)\nSkipped: {skipped} (already exist)\n\n"
                                f"Tip: Edit sources to refine auto-detected CSS selectors.")
            dialog.destroy()

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        self._btn(btn_frame, "Import", "download", command=do_import, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        self._btn(btn_frame, "Cancel", "xmark", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def update_active_source_config(self, source):
        """Update the main config with the active source details"""
        self.config['source_url'] = source['url']
        self.config['article_selector'] = source['selector']
        
        # Update automation engine config if it exists
        if hasattr(self, 'automation_engine') and self.automation_engine:
            self.automation_engine.config['source_url'] = source['url']
            self.automation_engine.config['article_selector'] = source['selector']
            self.logger.info(f"Updated automation engine config with new active source: {source.get('name', 'Unknown')}")
            self.logger.info(f"New source URL: {source['url']}")
            self.logger.info(f"New article selector: {source['selector']}")
        
        # Update automation tab's source URL display if it exists
        if hasattr(self, 'config_source_url'):
            self.config_source_url.set(source['url'])
        
        # Update configuration tab's selector display if it exists
        if hasattr(self, 'config_selector'):
            self.config_selector.set(source['selector'])

    def test_selected_source(self):
        """Test the selected source URL"""
        selection = self.sources_tree.selection()
        if not selection:
            ModernPopup.showwarning(self.root,"No Selection", "Please select a source to test.")
            return
        
        # Get the index of selected item
        item = selection[0]
        index = self.sources_tree.index(item)
        
        source_urls = self.config.get('source_urls', [])
        if index < len(source_urls):
            source = source_urls[index]
            self.test_source_configuration(source['url'], source['selector'], source.get('name', 'Selected Source'))

    def add_entry_context_menu(self, entry_widget):
        """Add right-click context menu with copy/paste functionality to Entry widget"""
        def show_context_menu(event):
            context_menu = tk.Menu(self.root, tearoff=0)
            
            # Add menu items
            context_menu.add_command(label="Cut", command=lambda: self.cut_text(entry_widget))
            context_menu.add_command(label="Copy", command=lambda: self.copy_text(entry_widget))
            context_menu.add_command(label="Paste", command=lambda: self.paste_text(entry_widget))
            context_menu.add_separator()
            context_menu.add_command(label="Select All", command=lambda: self.select_all_text(entry_widget))
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        # Bind right-click to show context menu
        entry_widget.bind("<Button-3>", show_context_menu)  # Right-click on Windows/Linux
        entry_widget.bind("<Button-2>", show_context_menu)  # Right-click on macOS
        
        # Bind keyboard shortcuts
        entry_widget.bind("<Control-v>", lambda e: self.paste_text(entry_widget))
        entry_widget.bind("<Control-c>", lambda e: self.copy_text(entry_widget))
        entry_widget.bind("<Control-x>", lambda e: self.cut_text(entry_widget))
        entry_widget.bind("<Control-a>", lambda e: self.select_all_text(entry_widget))
        
        # macOS shortcuts
        entry_widget.bind("<Command-v>", lambda e: self.paste_text(entry_widget))
        entry_widget.bind("<Command-c>", lambda e: self.copy_text(entry_widget))
        entry_widget.bind("<Command-x>", lambda e: self.cut_text(entry_widget))
        entry_widget.bind("<Command-a>", lambda e: self.select_all_text(entry_widget))
    
    def cut_text(self, entry_widget):
        """Cut selected text from Entry widget"""
        try:
            if entry_widget.selection_present():
                entry_widget.event_generate("<<Cut>>")
        except tk.TclError:
            pass
    
    def copy_text(self, entry_widget):
        """Copy selected text from Entry widget"""
        try:
            if entry_widget.selection_present():
                entry_widget.event_generate("<<Copy>>")
        except tk.TclError:
            pass
    
    def paste_text(self, entry_widget):
        """Paste text from clipboard to Entry widget"""
        try:
            entry_widget.event_generate("<<Paste>>")
        except tk.TclError:
            pass
    
    def select_all_text(self, entry_widget):
        """Select all text in Entry widget"""
        try:
            entry_widget.select_range(0, tk.END)
        except tk.TclError:
            pass

    def show_source_dialog(self, source=None, index=None):
        """Show dialog for adding/editing source URL"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Source" if source is None else "Edit Source")
        dialog.geometry("600x450")
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Create form
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Instructions label
        instructions = ttk.Label(main_frame,
            text="Fill in the fields below. Use 'Auto-Extract Selectors' to automatically detect the CSS selector.\n"
                 "Multiple sources can be active at the same time — articles are fetched from all active sources.\n"
                 "Right-click any field for copy/paste, or use Ctrl+V / Cmd+V.",
            font=('TkDefaultFont', 9), foreground='#444444', wraplength=560, justify=tk.LEFT)
        instructions.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky=tk.W)

        # Name field
        ttk.Label(main_frame, text="Source Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=source.get('name', '') if source else '')
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=55)
        name_entry.grid(row=1, column=1, pady=5, padx=10)
        self.add_entry_context_menu(name_entry)

        # URL field with auto-name on paste/type
        ttk.Label(main_frame, text="Source URL:").grid(row=2, column=0, sticky=tk.W, pady=5)
        url_var = tk.StringVar(value=source.get('url', '') if source else '')
        url_entry = ttk.Entry(main_frame, textvariable=url_var, width=55)
        url_entry.grid(row=2, column=1, pady=5, padx=10)
        self.add_entry_context_menu(url_entry)

        def on_url_change(*args):
            """Auto-fill name from URL domain if name is empty"""
            url = url_var.get().strip()
            if url and not name_var.get().strip():
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url if url.startswith('http') else 'https://' + url)
                    domain = parsed.netloc.replace('www.', '')
                    name_var.set(domain.split('.')[0].title())
                except Exception:
                    pass

        url_var.trace_add('write', on_url_change)

        # Selector field
        css_label_frame = ttk.Frame(main_frame)
        css_label_frame.grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Label(css_label_frame, text="CSS Selector:").pack(anchor=tk.W)
        ttk.Label(css_label_frame, text="(e.g. article h2 a)", font=("Arial", 8), foreground="#888").pack(anchor=tk.W)
        selector_var = tk.StringVar(value=source.get('selector', '') if source else '')
        selector_entry = ttk.Entry(main_frame, textvariable=selector_var, width=55)
        selector_entry.grid(row=3, column=1, pady=5, padx=10)
        self.add_entry_context_menu(selector_entry)

        # Auto-extract selector button
        auto_extract_frame = ttk.Frame(main_frame)
        auto_extract_frame.grid(row=4, column=1, sticky=tk.W, pady=5)

        def auto_extract_selectors():
            """Automatically extract CSS selectors from the URL"""
            url = url_var.get().strip()
            if not url:
                ModernPopup.showerror(self.root,"Error", "Please enter a URL first.")
                return
            self.show_selector_extraction_dialog(url, selector_var, name_var.get().strip() or "Source")

        self._btn(auto_extract_frame, "Auto-Extract Selectors", "search", command=auto_extract_selectors).pack(side=tk.LEFT)
        ttk.Label(auto_extract_frame, text="Finds CSS selectors automatically",
                 font=('TkDefaultFont', 8), foreground='#666666').pack(side=tk.LEFT, padx=(10, 0))

        # Active checkbox
        active_var = tk.BooleanVar(value=source.get('active', True) if source else True)
        ttk.Checkbutton(main_frame, text="Set as active source (multiple sources can be active)", variable=active_var).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=10)

        # Test button
        test_frame = ttk.Frame(main_frame)
        test_frame.grid(row=6, column=0, columnspan=2, pady=10)

        def test_current_config():
            """Test the current configuration in the dialog"""
            name = name_var.get().strip()
            url = url_var.get().strip()
            selector = selector_var.get().strip()

            if not url:
                ModernPopup.showerror(self.root,"Error", "URL is required for testing.")
                return

            # Auto-detect selector if missing
            if not selector:
                ModernPopup.showinfo(self.root,"Auto-Detect", "No CSS selector set. Will auto-detect...")
                auto_extract_selectors()
                return

            self.test_source_configuration(url, selector, name or "Test Source")

        self._btn(test_frame, "Test Configuration", "flask", command=test_current_config).pack()

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)

        def save_source():
            name = name_var.get().strip()
            url = url_var.get().strip()
            selector = selector_var.get().strip()

            # Auto-correct URL protocol
            if url and not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                url_var.set(url)

            if not name or not url:
                ModernPopup.showerror(self.root,"Error", "Name and URL are required.")
                return

            # If no selector, try auto-detect before giving up
            if not selector:
                try:
                    from auto_blogger.css_selector_extractor import CSSelectorExtractor
                    extractor = CSSelectorExtractor(self.logger)
                    result = extractor.analyze_url(url)
                    if result.get('success') and result.get('selectors'):
                        selector = result['selectors'][0]['selector']
                        selector_var.set(selector)
                        self.logger.info(f"Auto-detected selector: {selector}")
                    else:
                        selector = "article h2 a"
                        selector_var.set(selector)
                        self.logger.info(f"Using default selector: {selector}")
                except Exception:
                    selector = "article h2 a"
                    selector_var.set(selector)

            source_urls = self.config.get('source_urls', [])

            new_source = {
                'name': name,
                'url': url,
                'selector': selector,
                'active': active_var.get()
            }

            if index is not None:  # Editing existing source
                source_urls[index] = new_source
            else:  # Adding new source
                source_urls.append(new_source)

            # Sync first active source to legacy config
            if active_var.get():
                self.update_active_source_config(new_source)

            self.config['source_urls'] = source_urls
            self.save_config()
            self.save_main_config()
            self.refresh_sources_list()

            # Update the source config form if it exists
            if hasattr(self, 'source_config_vars') and active_var.get():
                self.source_config_vars['source_url'][0].set(url)
                self.source_config_vars['article_selector'][0].set(selector)

            self.logger.info(f"{'Updated' if index is not None else 'Added'} source: {name}")
            dialog.destroy()

        self._btn(button_frame, "Save", "save", command=save_source, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        self._btn(button_frame, "Cancel", "xmark", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Focus on URL field if adding new, name field if editing
        if source is None:
            url_entry.focus()
        else:
            name_entry.focus()

        # Handle Enter key to save
        dialog.bind('<Return>', lambda e: save_source())
        dialog.bind('<KP_Enter>', lambda e: save_source())

    def test_source_configuration(self, url, selector, name="Source"):
        """Test a specific source configuration"""
        self.logger.info(f"Testing {name} configuration...")
        self.logger.info(f"URL: {url}")
        self.logger.info(f"Selector: {selector}")
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.select(selector)
            
            if articles:
                # Collect sample article titles/urls for display
                samples = []
                for tag in articles[:5]:
                    href = tag.get('href', '')
                    text = tag.get_text(strip=True)[:60] if tag.get_text(strip=True) else href[:60]
                    if href:
                        full_url = urljoin(url, href) if not href.startswith('http') else href
                        samples.append(f"• {text}\n  {full_url}")
                sample_text = "\n\n".join(samples) if samples else "(Could not retrieve sample titles)"
                self.logger.info(f"[OK] {name} test successful! Found {len(articles)} articles.")
                for s in samples:
                    self.logger.info(f"  {s}")
                ModernPopup.showinfo(self.root,
                    "Test Successful",
                    f"[OK] {name} is working!\n\nFound {len(articles)} article links.\n\nSample articles:\n\n{sample_text}"
                )
            else:
                self.logger.warning(f"[!] {name}: no articles found with selector '{selector}'")
                # Try to give the user a hint by listing common selectors found on the page
                hint_selectors = ["article h2 a", "h2 a", ".post-title a", ".entry-title a", "h3 a"]
                found_hints = []
                for hint_sel in hint_selectors:
                    count = len(soup.select(hint_sel))
                    if count > 0:
                        found_hints.append(f"  '{hint_sel}' → {count} match(es)")
                hint_text = "\n".join(found_hints) if found_hints else "  (no common article selectors found — try Auto-Extract)"
                ModernPopup.showwarning(self.root,
                    "No Articles Found",
                    f"[!] No articles found with selector:\n  {selector}\n\n"
                    f"Alternative selectors found on this page:\n{hint_text}\n\n"
                    f"Tip: Click 'Auto-Extract Selectors' in the Add/Edit Source dialog to automatically find the right selector."
                )
                
        except Exception as e:
            self.logger.error(f"[X] {name} test failed: {str(e)}")
            ModernPopup.showerror(self.root,"Test Failed", f"Failed to test {name}:\n{str(e)}")

    def show_selector_extraction_dialog(self, url, selector_var, source_name):
        """Show dialog for automatic CSS selector extraction"""
        if not CSSelectorExtractor:
            ModernPopup.showerror(self.root,"Error", "CSS Selector Extractor not available. Please check installation.")
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Auto-Extract CSS Selectors - {source_name}")
        dialog.geometry("900x700")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Automatic CSS Selector Extraction", 
                 font=('TkDefaultFont', 14, 'bold')).pack(side=tk.LEFT)
        
        # URL display
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(url_frame, text="Analyzing URL:").pack(side=tk.LEFT)
        ttk.Label(url_frame, text=url, font=('TkDefaultFont', 9), foreground='#666666').pack(side=tk.LEFT, padx=(10, 0))
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        progress_var = tk.StringVar(value="Click 'Analyze' to start extraction...")
        progress_label = ttk.Label(progress_frame, textvariable=progress_var)
        progress_label.pack(side=tk.LEFT)
        
        progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        progress_bar.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create treeview for selectors
        columns = ('selector', 'effectiveness', 'matches', 'examples')
        tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        tree.heading('selector', text='CSS Selector')
        tree.heading('effectiveness', text='Effectiveness')
        tree.heading('matches', text='Matches')
        tree.heading('examples', text='Example Articles')
        
        tree.column('selector', width=250)
        tree.column('effectiveness', width=100)
        tree.column('matches', width=80)
        tree.column('examples', width=400)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Latest post info
        latest_frame = ttk.LabelFrame(main_frame, text="Latest Post Found", padding=10)
        latest_frame.pack(fill=tk.X, pady=(0, 20))
        
        latest_var = tk.StringVar(value="No analysis performed yet.")
        latest_label = ttk.Label(latest_frame, textvariable=latest_var, wraplength=800)
        latest_label.pack(fill=tk.X)
        
        # Analysis results storage
        analysis_results = {}
        
        def perform_analysis():
            """Perform the CSS selector analysis"""
            try:
                progress_var.set("Analyzing webpage...")
                progress_bar.start()
                dialog.update()
                
                # Initialize extractor
                extractor = CSSelectorExtractor(self.logger)
                
                # Perform analysis
                results = extractor.analyze_url(url)
                analysis_results['data'] = results
                
                progress_bar.stop()
                
                if results.get('success'):
                    progress_var.set(f"[OK] Analysis complete! Found {results.get('article_links_count', 0)} article links.")
                    
                    # Clear existing items
                    for item in tree.get_children():
                        tree.delete(item)
                    
                    # Populate treeview with selectors
                    selectors = results.get('selectors', [])
                    for i, selector_data in enumerate(selectors):
                        effectiveness = f"{selector_data['effectiveness']*100:.1f}%"
                        matches = f"{selector_data['article_matches']}/{selector_data['total_matches']}"
                        
                        # Format examples
                        examples = selector_data.get('examples', [])
                        example_text = "; ".join([ex['text'][:50] + "..." if len(ex['text']) > 50 else ex['text'] for ex in examples[:2]])
                        
                        tree.insert('', 'end', values=(
                            selector_data['selector'],
                            effectiveness,
                            matches,
                            example_text
                        ))
                    
                    # Update latest post info
                    latest_post = results.get('latest_post')
                    if latest_post:
                        latest_text = f"Title: {latest_post['title']}\nURL: {latest_post['url']}"
                        latest_var.set(latest_text)
                    else:
                        latest_var.set("No latest post identified.")
                        
                    # Select the first (best) selector
                    if selectors:
                        tree.selection_set(tree.get_children()[0])
                        tree.focus(tree.get_children()[0])
                        
                else:
                    progress_var.set(f"[X] Analysis failed: {results.get('error', 'Unknown error')}")
                    latest_var.set("Analysis failed.")
                    
            except Exception as e:
                progress_bar.stop()
                progress_var.set(f"[X] Error during analysis: {str(e)}")
                latest_var.set("Analysis failed.")
                self.logger.error(f"CSS selector extraction error: {e}")
        
        def use_selected_selector():
            """Use the selected CSS selector"""
            selection = tree.selection()
            if not selection:
                ModernPopup.showwarning(self.root,"No Selection", "Please select a CSS selector from the list.")
                return
            
            # Get selected selector
            item = tree.item(selection[0])
            selected_selector = item['values'][0]
            
            # Set the selector in the parent dialog
            selector_var.set(selected_selector)
            
            # Show confirmation
            ModernPopup.showinfo(self.root,"Selector Applied", f"CSS selector has been set to:\n{selected_selector}")
            
            # Close dialog
            dialog.destroy()
        
        def test_selected_selector():
            """Test the selected CSS selector"""
            selection = tree.selection()
            if not selection:
                ModernPopup.showwarning(self.root,"No Selection", "Please select a CSS selector from the list.")
                return
            
            # Get selected selector
            item = tree.item(selection[0])
            selected_selector = item['values'][0]
            
            # Test the selector
            self.test_source_configuration(url, selected_selector, source_name)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self._btn(button_frame, "Analyze URL", "search", command=perform_analysis).pack(side=tk.LEFT, padx=(0, 10))
        self._btn(button_frame, "Test Selected", "flask", command=test_selected_selector).pack(side=tk.LEFT, padx=(0, 10))
        self._btn(button_frame, "Use Selected", "check", command=use_selected_selector, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        self._btn(button_frame, "Cancel", "xmark", command=dialog.destroy).pack(side=tk.RIGHT)
        
        # Auto-start analysis
        dialog.after(500, perform_analysis)

    def toggle_source_edit_mode(self):
        self.source_edit_mode = not self.source_edit_mode
        if self.source_edit_mode:
            # Save previous values
            self.source_config_prev = {k: v[0].get() for k, v in self.source_config_vars.items()}
            # Enable all fields
            for key, (var, entry) in self.source_config_vars.items():
                if key == 'headless_mode':
                    entry.config(state='normal')
                elif key in ('max_articles', 'timeout'):
                    entry.config(state='normal')
                else:
                    entry.config(state='normal')
                    # Add paste functionality to Entry widgets when enabled
                    if hasattr(entry, 'winfo_class') and entry.winfo_class() == 'TEntry':
                        self.add_entry_context_menu(entry)
            _save_icon = self._icon('save')
            self.edit_icon_btn.config(text=" Save", command=self.save_source_config,
                                       image=_save_icon, compound='left') if _save_icon else self.edit_icon_btn.config(text="Save", command=self.save_source_config)
            self.source_btn_frame.grid()
        else:
            # Disable all fields
            for key, (var, entry) in self.source_config_vars.items():
                if key == 'headless_mode':
                    entry.config(state='disabled')
                elif key in ('max_articles', 'timeout'):
                    entry.config(state='readonly')
                else:
                    entry.config(state='readonly')
            _edit_icon = self._icon('pencil')
            self.edit_icon_btn.config(text=" Edit", command=self.toggle_source_edit_mode,
                                       image=_edit_icon, compound='left') if _edit_icon else self.edit_icon_btn.config(text="Edit", command=self.toggle_source_edit_mode)
            self.source_btn_frame.grid_remove()

    def save_source_config(self):
        # Update config from UI
        for key, (var, entry) in self.source_config_vars.items():
            self.config[key] = var.get()
        self.save_config()
        self.logger.info("Source configuration saved successfully")
        ModernPopup.showinfo(self.root,"Success", "Source configuration saved successfully")
        self.toggle_source_edit_mode()

    def cancel_source_edit(self):
        # Restore previous values
        for key, (var, entry) in self.source_config_vars.items():
            var.set(self.source_config_prev.get(key, var.get()))
        self.toggle_source_edit_mode()
        
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
            ModernPopup.showinfo(self.root,"GitHub", "Visit: https://github.com/AryanVBW")
        
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
            
    def add_log_message(self, message, add_timestamp=True):
        """Add log message to the logs text area with improved filtering and formatting"""
        if not hasattr(self, 'logs_text') or not self.logs_text:
            return
            
        # Skip empty or whitespace-only messages
        if not message or not message.strip():
            return
            
        # Get current log level setting
        current_level = self.log_level_var.get() if hasattr(self, 'log_level_var') else "INFO"
        
        # Determine message level and category with improved parsing
        message_level = "INFO"  # Default
        message_category = "INFO"  # Default
        
        # Extract level from message - improved parsing
        message_upper = message.upper()
        if "ERROR" in message_upper or "[X]" in message:
            message_level = "ERROR"
            message_category = "ERROR"
        elif "WARNING" in message_upper or "WARN" in message_upper:
            message_level = "WARNING"
            message_category = "WARNING"
        elif "DEBUG" in message_upper:
            message_level = "DEBUG"
            message_category = "DEBUG"
        elif "INFO" in message_upper or "[OK]" in message or "[>>]" in message:
            message_level = "INFO"
            message_category = "INFO"
        
        # Enhanced category detection with better patterns
        lower_message = message.lower()
        if any(word in lower_message for word in ['automation', 'processing', 'article', 'blog', 'extracting', 'paraphrasing', 'generating']):
            message_category = "AUTOMATION"
        elif any(word in lower_message for word in ['api', 'request', 'response', 'wordpress', 'endpoint', 'post', 'wp-json']):
            message_category = "API"
        elif any(word in lower_message for word in ['security', 'auth', 'login', 'credential', 'password', 'authentication']):
            message_category = "SECURITY"
        elif any(word in lower_message for word in ['webdriver', 'selenium', 'chrome', 'driver', 'browser', 'chromedriver']):
            message_category = "WEBDRIVER"
        elif any(word in lower_message for word in ['content', 'image', 'featured', 'title', 'meta', 'seo']):
            message_category = "CONTENT"
        elif any(word in lower_message for word in ['session', 'initialized', 'finalized', 'system', 'configuration']):
            message_category = "SYSTEM"
            
        # Level hierarchy: DEBUG < INFO < WARNING < ERROR
        level_hierarchy = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
        
        # Only show if message level is >= current filter level
        if level_hierarchy.get(message_level, 1) >= level_hierarchy.get(current_level, 1):
            # Format message with timestamp if not already present and add_timestamp is True
            formatted_message = message
            if add_timestamp and not (message.startswith('20') and ' - ' in message[:25]):  # Check for existing timestamp
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                formatted_message = f"{timestamp} | {message_level} | {message}"
            
            # Insert message
            self.logs_text.insert(tk.END, formatted_message + "\n")
            
            # Apply color based on log category/level
            try:
                start_line = self.logs_text.index(tk.END + "-2l")
                end_line = self.logs_text.index(tk.END + "-1l")
                
                # Apply appropriate tag for coloring
                self.logs_text.tag_add(message_category, start_line, end_line)
            except tk.TclError:
                pass  # Handle widget destruction gracefully
                
            # Auto-scroll to bottom only if user is at bottom
            try:
                if self.logs_text.yview()[1] >= 0.95:  # Only auto-scroll if near bottom
                    self.logs_text.see(tk.END)
            except tk.TclError:
                pass
            
            # Update status bar based on message importance
            if hasattr(self, 'status_label'):
                try:
                    if message_level == "ERROR":
                        self.status_label.config(text="[X] Error occurred - check logs")
                    elif "starting" in lower_message:
                        self.status_label.config(text="[>>] Automation running...")
                    elif "completed" in lower_message or "success" in lower_message:
                        self.status_label.config(text="[OK] Operation completed")
                    elif "initializing" in lower_message:
                        self.status_label.config(text="[>>] Processing...")
                except tk.TclError:
                    pass
        
        # Limit log size to prevent memory issues
        try:
            lines = self.logs_text.get(1.0, tk.END).count('\n')
            if lines > 1000:  # Keep last 1000 lines
                self.logs_text.delete(1.0, f"{lines-1000}.0")
        except tk.TclError:
            # Handle case where widget might be destroyed
            pass
            
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
                
            ModernPopup.showinfo(self.root,"Success", "Requirements installed successfully! Please restart the application.")
            
        except Exception as e:
            self.logger.error(f"Error installing requirements: {e}")
            ModernPopup.showerror(self.root,"Error", f"Failed to install requirements: {e}")
            
    def _build_wp_session(self, wp_url: str) -> 'requests.Session':
        """Build a requests.Session that can talk to any WordPress site, including
        those protected by DDoS-Guard / slowAES bot challenges.

        1. Creates session with retry adapter and realistic browser headers.
        2. Makes a probe request; if the response contains the slowAES challenge,
           solves it with AES-CBC decryption and sets the __test cookie.
        3. Returns the ready-to-use session (cookie already set).
        """
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1,
                      status_forcelist=[500, 502, 503, 504],
                      allowed_methods=["GET", "POST"], raise_on_status=False)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "en-US,en;q=0.9",
        })

        verify = not wp_url.startswith('http://')
        probe_url = f"{wp_url.rstrip('/')}/posts"

        # Probe and solve DDoS-Guard if present
        try:
            r = session.get(probe_url, timeout=15, verify=verify,
                            headers={"Connection": "close"}, allow_redirects=False)

            if 'slowAES' in r.text:
                self.logger.info("DDoS-Guard protection detected — solving AES challenge...")
                cookie_val = self._solve_aes_challenge(r.text)
                if cookie_val:
                    from urllib.parse import urlparse
                    domain = urlparse(wp_url).netloc
                    session.cookies.set('__test', cookie_val, domain=domain, path='/')
                    self.logger.info(f"[OK] Challenge solved — __test cookie set")
                    # Hit the ?i=1 confirmation URL so the server sees the cookie
                    sep = '&' if '?' in probe_url else '?'
                    session.get(f"{probe_url}{sep}i=1", timeout=15, verify=verify,
                                allow_redirects=True)
                else:
                    self.logger.warning("[!] Could not solve DDoS-Guard challenge")
        except Exception as e:
            self.logger.debug(f"Session probe: {e}")

        return session

    def _solve_aes_challenge(self, html: str) -> str:
        """Parse and solve the slowAES DDoS-Guard challenge embedded in `html`.
        Returns the hex cookie value, or empty string on failure.
        """
        # Two common patterns in the challenge JS
        m = re.search(
            r'toNumbers\(["\']([0-9a-fA-F]+)["\']\)'
            r'.*?b=toNumbers\(["\']([0-9a-fA-F]+)["\']\)'
            r'.*?c=toNumbers\(["\']([0-9a-fA-F]+)["\']\)',
            html, re.DOTALL)
        if not m:
            m = re.search(
                r'var\s+a\s*=\s*toNumbers\(["\']([0-9a-fA-F]+)["\']\)'
                r'.*?b\s*=\s*toNumbers\(["\']([0-9a-fA-F]+)["\']\)'
                r'.*?c\s*=\s*toNumbers\(["\']([0-9a-fA-F]+)["\']\)',
                html, re.DOTALL)
        if not m:
            return ''

        key_b = bytes.fromhex(m.group(1))
        iv_b  = bytes.fromhex(m.group(2))
        ct_b  = bytes.fromhex(m.group(3))

        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            c = Cipher(algorithms.AES(key_b), modes.CBC(iv_b), backend=default_backend())
            d = c.decryptor()
            return (d.update(ct_b) + d.finalize()).hex()
        except Exception:
            pass
        try:
            from Crypto.Cipher import AES as _AES
            return _AES.new(key_b, _AES.MODE_CBC, iv_b).decrypt(ct_b).hex()
        except Exception:
            pass
        return ''

    def test_connection(self):
        """Test WordPress connection — handles DDoS-Guard, HTTP, HTTPS, and Application Passwords"""
        def _run_test():
            try:
                wp_url = self.wp_base_url_var.get().strip()
                username = self.username_var.get().strip()
                password = self.password_var.get().strip()

                if not all([wp_url, username, password]):
                    self.root.after(0, lambda: ModernPopup.showerror(self.root,
                        "Missing Fields", "Please fill in WordPress URL, Username, and Password."))
                    return

                # Normalise URL
                wp_url = wp_url.rstrip('/')
                if not wp_url.startswith(('http://', 'https://')):
                    wp_url = 'https://' + wp_url

                # Strip spaces from Application Password
                clean_password = password.replace(' ', '')

                self.root.after(0, lambda: self.connection_status.config(
                    text="Testing connection...", foreground="blue"))
                self.logger.info(f"Testing WordPress connection: {wp_url}")

                auth = HTTPBasicAuth(username, clean_password)

                # Build a DDoS-Guard-aware session
                session = self._build_wp_session(wp_url)

                verify = not wp_url.startswith('http://')
                test_url = f"{wp_url}/posts"

                try:
                    response = session.get(test_url, auth=auth, timeout=20, verify=verify)
                except requests.exceptions.SSLError:
                    self.logger.warning("[!] SSL error — retrying without certificate verification")
                    response = session.get(test_url, auth=auth, timeout=20, verify=False)

                # Check if we still got the challenge page instead of JSON
                if response.status_code == 200 and 'slowAES' in response.text:
                    self.root.after(0, lambda: self.connection_status.config(
                        text="Bot-protection could not be bypassed", foreground="orange"))
                    self.root.after(0, lambda: ModernPopup.showwarning(self.root,
                        "Bot Protection Active",
                        "[!] The site's DDoS-Guard protection could not be bypassed automatically.\n\n"
                        "This may happen if the site requires a real browser.\n"
                        "The automation will still attempt to post — try running it and check the logs."))
                    return

                if response.status_code == 200:
                    try:
                        data = response.json()
                        post_count = len(data) if isinstance(data, list) else 1
                    except Exception:
                        post_count = 0
                    self.root.after(0, lambda: self.connection_status.config(
                        text="Connected successfully", foreground="green"))
                    self.root.after(0, lambda: self.connection_indicator.config(foreground="green"))
                    self.logger.info(f"[OK] WordPress connection OK — {post_count} post(s) returned")
                    self.root.after(0, lambda: ModernPopup.showinfo(self.root,
                        "Connection Successful",
                        f"[OK] WordPress connection successful!\n\n"
                        f"URL: {wp_url}\n"
                        f"User: {username}\n"
                        f"Posts found: {post_count}\n\n"
                        f"Your site is reachable and authenticated correctly."))

                elif response.status_code == 401:
                    self.root.after(0, lambda: self.connection_status.config(
                        text="Authentication failed (401)", foreground="red"))
                    self.root.after(0, lambda: ModernPopup.showerror(self.root,
                        "Authentication Failed",
                        "[X] HTTP 401 — Authentication failed.\n\n"
                        "Please check:\n"
                        "• Username is your WordPress login username\n"
                        "• Password is an Application Password (not your login password)\n"
                        "  → WordPress Admin ▸ Users ▸ Profile ▸ Application Passwords\n"
                        "  Format example: ABCD EFGH IJKL MNOP QRST UVWX\n"
                        "• Application Password feature is enabled on the site"))

                elif response.status_code == 403:
                    self.root.after(0, lambda: self.connection_status.config(
                        text="Forbidden (403)", foreground="red"))
                    self.root.after(0, lambda: ModernPopup.showerror(self.root,
                        "Access Forbidden",
                        "[X] HTTP 403 — Access forbidden.\n\n"
                        "• WordPress REST API may be disabled\n"
                        "• A security plugin (Wordfence, etc.) may be blocking the request\n"
                        "• The user account may lack the required permissions"))

                else:
                    status = response.status_code
                    snippet = response.text[:300]
                    self.root.after(0, lambda: self.connection_status.config(
                        text=f"HTTP {status}", foreground="red"))
                    self.root.after(0, lambda: ModernPopup.showwarning(self.root,
                        "Unexpected Response",
                        f"HTTP {status}\n\nResponse preview:\n{snippet}"))

            except requests.exceptions.ConnectionError as e:
                err = str(e)
                if 'RemoteDisconnected' in err or 'Connection aborted' in err:
                    detail = (
                        "The server closed the connection without a response.\n\n"
                        "• Check that the URL is correct\n"
                        "• The server may be blocking non-browser requests\n"
                        "• Try the URL in a browser to confirm the site is up")
                else:
                    detail = f"Could not reach the server.\n\nCheck the URL and your internet connection.\n\n{err[:200]}"
                self.root.after(0, lambda d=detail: self.connection_status.config(
                    text="Connection failed", foreground="red"))
                self.root.after(0, lambda d=detail: ModernPopup.showerror(self.root,"Connection Error", f"[X] {d}"))
                self.logger.error(f"Connection error: {err}")

            except requests.exceptions.Timeout:
                self.root.after(0, lambda: self.connection_status.config(
                    text="Timed out", foreground="red"))
                self.root.after(0, lambda: ModernPopup.showerror(self.root,
                    "Timeout", "[X] The server did not respond within 20 seconds.\nCheck the URL and try again."))

            except Exception as e:
                msg = str(e)
                self.root.after(0, lambda m=msg: self.connection_status.config(
                    text=f"{m[:50]}", foreground="red"))
                self.root.after(0, lambda m=msg: ModernPopup.showerror(self.root,"Connection Error", f"[X] {m}"))
                self.logger.error(f"test_connection error: {e}")

        threading.Thread(target=_run_test, daemon=True).start()
            
    def login(self):
        """Login and initialize automation engine"""
        try:
            # Reload domain-specific configuration to ensure all settings are current
            if hasattr(self, 'active_config_name') and hasattr(self, 'load_config'):
                self.config = self.load_config(self.active_config_name)
            
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
            
            self.logger.info("[OK] Configuration saved")
            
            # Initialize automation engine
            self.automation_engine = BlogAutomationEngine(self.config, self.logger)
            
            # Update UI
            self.connection_status.config(text="Connected", foreground="green")
            
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
            ModernPopup.showerror(self.root,"Login Failed", f"Could not initialize automation engine: {e}")
            
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
            
            # Save advanced configs
            self.save_json_config_from_text("internal_links.json", self.internal_links_text.get("1.0", tk.END))
            self.save_json_config_from_text("external_links.json", self.external_links_text.get("1.0", tk.END))
            self.save_style_prompt_from_text(self.style_prompt_text.get("1.0", tk.END))
            self.save_json_config_from_text("category_keywords.json", self.category_keywords_text.get("1.0", tk.END))
            self.save_json_config_from_text("tag_synonyms.json", self.tag_synonyms_text.get("1.0", tk.END))
            self.save_json_config_from_text("static_clubs.json", self.static_clubs_text.get("1.0", tk.END))
            self.save_json_config_from_text("stop_words.json", self.stop_words_text.get("1.0", tk.END))
            self.save_json_config_from_text("do_follow_urls.json", self.do_follow_urls_text.get("1.0", tk.END))
            
            # Save to file
            with open("blog_config.json", 'w') as f:
                json.dump(self.config, f, indent=2)
                
            # Update source URL in automation tab
            self.config_source_url.set(self.config['source_url'])
            
            # Update max articles in automation tab
            self.max_articles_var.set(self.config['max_articles'])
            
            self.logger.info("Configuration saved successfully")
            ModernPopup.showinfo(self.root,"Success", "Configuration saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            ModernPopup.showerror(self.root,"Error", f"Failed to save configuration: {e}")
            
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
                ModernPopup.showinfo(self.root,"Success", f"Logs saved to {filename}")
                
        except Exception as e:
            ModernPopup.showerror(self.root,"Error", f"Failed to save logs: {e}")
            
    def update_step_status(self, step_index, status, details="", elapsed_time=""):
        """Update status of a specific step with color coding and progress bar update"""
        try:
            if step_index >= len(self.process_steps):
                return

            item_id = str(step_index)
            step_name = self.process_steps[step_index]
            total_steps = len(self.process_steps)

            status_symbols = {
                'pending': '[...]',
                'running': '[>>]',
                'completed': '[OK]',
                'error': '[X]',
                'skipped': '[--]'
            }
            display_status = f"{status_symbols.get(status, '[?]')} {status.title()}"

            # Update treeview item with color tag
            self.steps_tree.item(item_id, values=(step_name, display_status, details, elapsed_time), tags=(status,))
            self.steps_tree.see(item_id)

            # Update step progress bar (shows which step out of total)
            if hasattr(self, 'task_progress'):
                if status == 'running':
                    self._step_start_time = time.time()
                    self.task_progress.config(mode='determinate')
                    self.task_progress['maximum'] = total_steps
                    self.task_progress['value'] = step_index
                    if hasattr(self, 'step_counter_label'):
                        self.step_counter_label.config(text=f"Step {step_index + 1} of {total_steps}: {step_name}")
                    if hasattr(self, 'current_task_label'):
                        self.current_task_label.config(text=f"[>>] {step_name}...")
                elif status == 'completed':
                    self.task_progress['value'] = step_index + 1
                    if hasattr(self, 'step_counter_label'):
                        self.step_counter_label.config(text=f"Step {step_index + 1} of {total_steps}: {step_name} [OK]")
                    if hasattr(self, 'current_task_label') and elapsed_time:
                        self.current_task_label.config(text=f"[OK] {step_name} ({elapsed_time})")
                elif status == 'error':
                    if hasattr(self, 'current_task_label'):
                        self.current_task_label.config(text=f"[X] {step_name} failed")
                elif status == 'skipped':
                    self.task_progress['value'] = step_index + 1
                    if hasattr(self, 'current_task_label'):
                        self.current_task_label.config(text=f"[--] {step_name} skipped")

            # Update elapsed time display
            if hasattr(self, 'elapsed_label') and self._automation_start_time:
                elapsed = time.time() - self._automation_start_time
                mins, secs = divmod(int(elapsed), 60)
                self.elapsed_label.config(text=f"Elapsed: {mins:02d}:{secs:02d}")

        except Exception as e:
            self.logger.error(f"Error updating step status: {e}")
            
    def start_automation(self):
        """Start the automation process"""
        if self.is_running:
            ModernPopup.showwarning(self.root,"Warning", "Automation is already running")
            return
        
        # Check if automation engine is initialized
        if not self.automation_engine:
            try:
                # Try to initialize it
                if self.has_valid_credentials():
                    self.log_automation_event("[>>] Initializing automation engine...")
                    self.automation_engine = BlogAutomationEngine(self.config, self.logger)
                    self.log_automation_event("[OK] Automation engine initialized successfully")
                else:
                    self.log_automation_event("[X] Missing credentials for automation", "error")
                    ModernPopup.showerror(self.root,"Error", "Please login first in the Authentication tab")
                    self.notebook.select(self.login_frame)
                    return
            except Exception as e:
                self.log_automation_event(f"[X] Failed to initialize automation engine: {e}", "error")
                ModernPopup.showerror(self.root,"Error", f"Failed to initialize automation engine: {e}\n\nPlease check your configuration and try again.")
                return
        
        # Get max articles
        max_articles = self.max_articles_var.get()
        if max_articles <= 0:
            ModernPopup.showerror(self.root,"Error", "Please set a valid number of articles")
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
        
        # Record automation start time for elapsed tracking
        self._automation_start_time = time.time()

        # Log automation start with details
        self.log_automation_start()

        # Initialize steps
        self.initialize_steps()
        # Restore start time after initialize_steps resets it
        self._automation_start_time = time.time()

        # Start automation in a separate thread
        threading.Thread(target=self.run_automation, daemon=True).start()
        
    def stop_automation(self):
        """Stop the automation process"""
        self.stop_requested = True
        self.task_progress.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.is_running = False
        self.logger.info("Automation stopped by user")
        
    def run_automation(self):
        """Main automation process"""
        try:
            if not self.automation_engine:
                self.logger.error("Automation engine not initialized")
                self.automation_completed()
                return
            
            # Check if using Jupyter notebook style
            use_jupyter_style = self.use_jupyter_style_var.get()
            max_articles = self.max_articles_var.get()
            
            if use_jupyter_style:
                self.logger.info("[>>] Using Enhanced Processing (Jupyter Style)")
                # Run the Jupyter notebook style automation
                processed = self.automation_engine.run_automation_jupyter_style(max_articles)
                self.processed_count = processed
                self.automation_completed()
                return
                
            # Regular automation process
            self.logger.info("[>>] Using Standard Processing")
            
            # Initialize
            self.update_step_status(0, 'running', 'Fetching article links from source...')
            
            # Get article links using the automation engine
            article_links = self.automation_engine.get_article_links(limit=20)
            if not article_links:
                self.update_step_status(0, 'error', 'No article links found - check source URL and selector')
                self.logger.error(f"[X] Failed to find articles from: {self.automation_engine.config.get('source_url', 'N/A')}")
                self.logger.error(f"[X] Using selector: {self.automation_engine.config.get('article_selector', 'N/A')}")
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
                self.logger.warning("[!] All articles have already been processed.")
                self.logger.info("Tip: Enable 'Force Processing' option to reprocess articles.")
                ModernPopup.showinfo(self.root,"No New Articles", 
                    "All available articles have already been processed.\n\n"
                    "To reprocess articles, check the 'Force Processing' option in the Automation tab.")
                self.automation_completed()
                return
            
            # Use all articles if force processing, otherwise only new ones
            process_links = article_links if force_processing else new_articles
            
            self.total_articles = min(len(process_links), self.max_articles_var.get())
            self.overall_progress['maximum'] = self.total_articles
            
            if force_processing:
                self.logger.info(f"[>>] Force processing enabled - reprocessing {self.total_articles} articles")
            else:
                self.logger.info(f"[OK] Found {len(new_articles)} new articles to process")
            
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
                    
                # Update overall progress
                progress_val = i + 1
                self.overall_progress['value'] = progress_val
                pct = int((progress_val / self.total_articles) * 100) if self.total_articles > 0 else 0
                if hasattr(self, 'overall_pct_label'):
                    self.overall_pct_label.config(text=f"{pct}%")
                self.articles_count_label.config(text=f"Articles: {self.processed_count}/{self.total_articles}")
                
            self.automation_completed()
            
        except Exception as e:
            self.log_automation_event(f"[X] Critical automation error: {e}", "error")
            self.logger.error(f"Automation error: {e}", exc_info=True)
            
            # Show user-friendly error message
            try:
                ModernPopup.showerror(self.root,
                    "Automation Error",
                    f"The automation process encountered an error:\n\n{str(e)}\n\n"
                    f"Please check the logs for more details and try again."
                )
            except:
                pass
            
            self.automation_completed()
            
    def process_single_article(self, article_url):
        """Process a single article with improved error handling and logging"""
        try:
            start_time = time.time()
            self.log_automation_event(f"[>>] Starting article processing: {article_url}")
            
            # Step 0: Fetch article links (already done)
            self.update_step_status(0, 'completed', f'URL: {article_url[:50]}...', '')
            
            # Step 1: Extract content
            step_start = time.time()
            self.update_step_status(1, 'running', 'Extracting content with Selenium...')
            self.log_automation_event("Initializing content extraction...")
            
            with self.automation_engine.get_selenium_driver_context() as driver:
                if not driver:
                    error_msg = 'WebDriver initialization failed'
                    self.update_step_status(1, 'error', error_msg)
                    self.log_automation_event(f"[X] {error_msg}", "error")
                    return False
                    
                self.log_automation_event("[OK] WebDriver initialized, extracting content...")
                title, content = self.automation_engine.extract_article_with_selenium(driver, article_url)
                
            if not title or not content:
                error_msg = f'Content extraction failed - Title: {bool(title)}, Content: {bool(content)}'
                self.update_step_status(1, 'error', 'Failed to extract content')
                self.log_automation_event(f"[X] {error_msg}", "error")
                return False
            
            elapsed = f"{time.time() - step_start:.1f}s"
            self.update_step_status(1, 'completed', f'Title: {title[:50]}...', elapsed)
            self.log_automation_event(f"[OK] Content extracted successfully: '{title[:50]}...' ({len(content)} chars)")
            
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
            
            # Step 4.5: Add content images if enabled
            content_image_source = self.content_image_var.get()
            if content_image_source != "none":
                step_start = time.time()
                self.update_step_status(5, 'running', f'Adding {content_image_source} content images...')
                
                if content_image_source == "openai":
                    # Get custom prompt if enabled
                    custom_prompt = None
                    if self.use_custom_prompt_var.get():
                        try:
                            # Load the custom prompt from the saved config
                            config_dir = self.get_current_config_dir()
                            config_path = os.path.join(config_dir, "openai_image_config.json")
                            if os.path.exists(config_path):
                                with open(config_path, 'r') as f:
                                    openai_config = json.load(f)
                                    custom_prompt = openai_config.get('custom_prompt', '').strip()
                                    if not custom_prompt:
                                        custom_prompt = None
                        except Exception as e:
                            self.logger.warning(f"Could not load custom prompt: {e}")
                    
                    final_content = self.automation_engine.add_openai_image_to_content(
                        final_content, paraphrased_title, custom_prompt
                    )
                elif content_image_source == "getty":
                    final_content = self.automation_engine.add_getty_image_to_content(
                        final_content, paraphrased_title
                    )
                
                elapsed = f"{time.time() - step_start:.1f}s"
                self.update_step_status(5, 'completed', f'{content_image_source.title()} content images added', elapsed)
            else:
                self.update_step_status(5, 'skipped', 'No content images selected', '')
            
            # Step 6: Generate SEO metadata
            step_start = time.time()
            self.update_step_status(6, 'running', 'Generating SEO title and meta description...')
            
            seo_title, meta_description = self.automation_engine.generate_seo_title_and_meta(paraphrased_title, final_content)
            elapsed = f"{time.time() - step_start:.1f}s"
            self.update_step_status(6, 'completed', f'SEO title: {len(seo_title)} chars', elapsed)
            
            # Step 7: Extract keyphrases
            step_start = time.time()
            self.update_step_status(7, 'running', 'Extracting focus keyphrase and additional keyphrases...')
            
            focus_keyphrase, additional_keyphrases = self.automation_engine.extract_keyphrases_with_gemini(paraphrased_title, final_content)
            elapsed = f"{time.time() - step_start:.1f}s"
            keyphrase_count = 1 + len(additional_keyphrases) if focus_keyphrase else len(additional_keyphrases)
            self.update_step_status(7, 'completed', f'Extracted {keyphrase_count} keyphrases', elapsed)
            
            # Step 8: Handle featured images based on selected source
            image_source = self.image_source_var.get()
            media_id = None
            
            if image_source == "openai":
                step_start = time.time()
                self.update_step_status(8, 'running', 'Preparing OpenAI featured image...')
                
                # We'll set the media_id but post_id will be None until we create the post
                # We'll attach the image to the post later
                media_id = None  # Will be set after post creation
                elapsed = f"{time.time() - step_start:.1f}s"
                self.update_step_status(8, 'completed', 'Featured image prepared', elapsed)
                
            elif image_source == "getty":
                step_start = time.time()
                self.update_step_status(8, 'running', 'Preparing Getty Images for featured image...')
                
                # For Getty Images, we'll set it as featured image after post creation
                # Just mark that we need to process Getty images later
                media_id = None  # Will be set after post creation
                elapsed = f"{time.time() - step_start:.1f}s"
                self.update_step_status(8, 'completed', 'Getty Images prepared', elapsed)
                
            else:
                self.update_step_status(8, 'skipped', 'No featured images selected', '')
            
            # Step 9: Detect categories
            step_start = time.time()
            self.update_step_status(9, 'running', 'Detecting categories...')
            
            categories = self.automation_engine.detect_categories(paraphrased_title + " " + final_content)
            elapsed = f"{time.time() - step_start:.1f}s"
            self.update_step_status(9, 'completed', f'Found {len(categories)} categories', elapsed)
            
            # Step 10: Generate tags
            step_start = time.time()
            self.update_step_status(10, 'running', 'Generating tags...')
            
            tags = self.automation_engine.generate_tags_with_gemini(final_content)
            elapsed = f"{time.time() - step_start:.1f}s"
            self.update_step_status(10, 'completed', f'Generated {len(tags)} tags', elapsed)
            
            # Step 11: Create WordPress post
            step_start = time.time()
            self.update_step_status(11, 'running', 'Creating WordPress post...')
            
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
                self.update_step_status(11, 'error', 'Failed to create WordPress post')
                return False
                
            elapsed = f"{time.time() - step_start:.1f}s"
            self.update_step_status(11, 'completed', f'Post created (ID: {post_id})', elapsed)
            
            # Step 8b: Now that we have a post ID, handle featured images based on selected source
            if image_source == "openai":
                step_start = time.time()
                self.update_step_status(8, 'running', 'Uploading OpenAI featured image...')
                
                media_id = self.automation_engine.generate_and_upload_featured_image(
                    paraphrased_title, 
                    final_content,
                    post_id
                )
                
                if media_id:
                    elapsed = f"{time.time() - step_start:.1f}s"
                    self.update_step_status(8, 'completed', f'OpenAI featured image set (ID: {media_id})', elapsed)
                else:
                    self.update_step_status(8, 'error', 'Failed to set OpenAI featured image')
                    
            elif image_source == "getty":
                step_start = time.time()
                self.update_step_status(8, 'running', 'Searching and downloading Getty featured image...')
                
                media_id = self.automation_engine.generate_and_upload_getty_featured_image(
                    paraphrased_title, 
                    final_content,
                    post_id
                )
                
                if media_id:
                    elapsed = f"{time.time() - step_start:.1f}s"
                    self.update_step_status(8, 'completed', f'Getty featured image set (ID: {media_id})', elapsed)
                else:
                    self.update_step_status(8, 'error', 'Failed to set Getty featured image')
            
            # Step 12: Finalize
            self.update_step_status(12, 'completed', f'Article processing completed in {time.time() - start_time:.1f}s')
            
            return True
            
        except Exception as e:
            self.log_automation_event(f"[X] Error processing article {article_url}: {e}", "error")
            self.logger.error(f"Error processing article {article_url}: {e}", exc_info=True)
            
            # Update UI to show error
            try:
                self.update_step_status(12, 'error', f'Article processing failed: {str(e)[:50]}...')
            except:
                pass
            
            # Increment error count if it exists
            if hasattr(self, 'error_count'):
                self.error_count += 1
            else:
                self.error_count = 1
            
            return False
            
    def automation_completed(self):
        """Called when automation is completed"""
        self.task_progress.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.current_task_label.config(text=f"Completed - {self.processed_count} articles processed")

        # Final progress state
        if hasattr(self, 'overall_pct_label') and self.total_articles > 0:
            self.overall_pct_label.config(text="100%")
            self.overall_progress['value'] = self.total_articles
        if hasattr(self, 'task_progress'):
            self.task_progress.config(mode='determinate')
            self.task_progress['maximum'] = 100
            self.task_progress['value'] = 100
        if hasattr(self, 'step_counter_label'):
            self.step_counter_label.config(text="All steps completed")
        if hasattr(self, 'current_task_label'):
            self.current_task_label.config(text=f"Automation complete — {self.processed_count} article(s) posted")
        if hasattr(self, 'elapsed_label') and self._automation_start_time:
            elapsed = time.time() - self._automation_start_time
            mins, secs = divmod(int(elapsed), 60)
            self.elapsed_label.config(text=f"Total time: {mins:02d}:{secs:02d}")
        
        # Calculate error count for logging
        error_count = getattr(self, 'error_count', 0) if hasattr(self, 'error_count') else 0
        
        # Log completion with summary
        self.log_automation_complete(self.processed_count, error_count)
        
        if self.processed_count > 0:
            self.logger.info(f"Automation completed successfully! {self.processed_count} articles processed.")
            ModernPopup.showinfo(self.root,"Success", f"Automation completed!\n\n{self.processed_count} articles were processed and posted to WordPress.")
        else:
            self.logger.warning("[!] No articles were processed.")
            
            # Provide more detailed error information
            config = getattr(self.automation_engine, 'config', {})
            source_url = config.get('source_url', 'Not configured')
            selector = config.get('article_selector', 'Not configured')
            
            error_details = f"""No articles were processed. Possible issues:

Source URL: {source_url}
Article Selector: {selector}

Common solutions for TBR Football:
• Check if https://tbrfootball.com is accessible in your browser
• The correct selector for TBR Football should be: article h2 a OR article h3 a
• Verify your internet connection is working
• Try using a different article selector in Configuration tab
• Check the Logs tab for detailed technical information

Alternative selectors to try:
• article h2 a (default)
• article h3 a
• h2 a
• a[href*='tbrfootball.com']

Debugging steps:
1. Open https://tbrfootball.com/topic/english-premier-league/ in your browser
2. Check if articles are visible on the page
3. Try the 'Test Configuration' button below
4. Review the detailed logs in the Logs tab

See the Logs tab for more technical details."""
            
            ModernPopup.showwarning(self.root,"No Articles Processed", error_details)
            
    # Core automation methods (using automation engine)
    def get_internal_links(self):
        """Get default internal links configuration"""
        return {
            "Latest News": "https://example-sports-site.com/category/sports-news/",
            "Transfer News": "https://example-sports-site.com/category/sports-news/transfer-news/",
            "Arsenal": "https://example-sports-site.com/tag/arsenal-news/",
            "Liverpool": "https://example-sports-site.com/tag/liverpool-news/",
            "Manchester United": "https://example-sports-site.com/tag/manchester-united-news/",
            "Tottenham": "https://example-sports-site.com/tag/tottenham-news/",
            "Chelsea": "https://example-sports-site.com/tag/chelsea-news/"
        }
        
    def get_external_links(self):
        """Get default external links configuration"""
        return {
            "premier league": "https://www.premierleague.com/",
            "tottenham": "https://example-spurs-site.com/",
            "leeds united": "https://example-leeds-site.com/",
            "stats": "https://fbref.com/en/",
            "transfer news": "https://www.transfermarkt.com/"
        }
    
    def test_configuration(self):
        """Test the current configuration to help debug issues"""
        if not self.automation_engine:
            ModernPopup.showerror(self.root,"Error", "Automation engine not initialized. Please login first.")
            return
            
        def run_test():
            try:
                self.logger.info("Starting configuration test...")
                
                # Test article link extraction
                self.logger.info("Testing article link extraction...")
                article_links = self.automation_engine.get_article_links(limit=5)
                
                if article_links:
                    self.logger.info(f"[OK] Successfully found {len(article_links)} articles")
                    for i, link in enumerate(article_links):
                        self.logger.info(f"  {i+1}. {link}")
                    
                    # Test content extraction from first article
                    self.logger.info("Testing content extraction from first article...")
                    with self.automation_engine.get_selenium_driver_context() as driver:
                        if driver:
                            title, content = self.automation_engine.extract_article_with_selenium(driver, article_links[0])
                            if title and content:
                                self.logger.info(f"[OK] Successfully extracted content: {title[:60]}...")
                                ModernPopup.showinfo(self.root,"Test Results", 
                                    f"[OK] Configuration test passed!\n\n"
                                    f"Found {len(article_links)} articles\n"
                                    f"Successfully extracted content from: {title[:60]}...\n\n"
                                    f"Your configuration is working correctly!")
                            else:
                                self.logger.error("[X] Failed to extract content")
                                ModernPopup.showwarning(self.root,"Test Results",
                                    f"[!] Found {len(article_links)} articles but failed to extract content.\n"
                                    f"Check Selenium setup and website structure.")
                        else:
                            self.logger.error("[X] Failed to initialize WebDriver")
                            ModernPopup.showerror(self.root,"Test Results", 
                                "[X] Selenium WebDriver failed to initialize.\n"
                                "Please check Selenium installation.")
                else:
                    config = self.automation_engine.config
                    source_url = config.get('source_url', 'Not configured')
                    selector = config.get('article_selector', 'Not configured')
                    
                    self.logger.error("[X] No articles found")
                    ModernPopup.showerror(self.root,"Test Results", 
                        f"[X] Configuration test failed!\n\n"
                        f"No articles found with current settings:\n"
                        f"• Source URL: {source_url}\n"
                        f"• Selector: {selector}\n\n"
                        f"Please check the Configuration tab and verify:\n"
                        f"1. Source URL is accessible\n"
                        f"2. Article selector matches the website structure\n\n"
                        f"Check the logs for more details.")
                        
            except Exception as e:
                self.logger.error(f"[X] Test failed: {e}")
                ModernPopup.showerror(self.root,"Test Results", f"[X] Test failed with error:\n{e}")
        
        # Run test in separate thread to avoid blocking UI
        threading.Thread(target=run_test, daemon=True).start()
        
    def clear_posted_links(self):
        """Clear the posted links history"""
        try:
            if os.path.exists("posted_links.json"):
                # Ask for confirmation
                confirm = ModernPopup.askyesno(self.root,
                    "Confirm Clear History",
                    "Are you sure you want to clear the posted links history?\n\n"
                    "This will allow all articles to be processed again, even if they were processed before.",
                    icon="warning"
                )
                
                if confirm:
                    # Create empty file
                    with open("posted_links.json", "w") as f:
                        json.dump([], f)
                    
                    self.logger.info("[OK] Posted links history cleared")
                    ModernPopup.showinfo(self.root,"Success", "Posted links history has been cleared.")
                    
                    # Refresh the configuration tab
                    self.notebook.select(self.config_frame)
                    self.create_config_tab()
        except Exception as e:
            self.logger.error(f"Error clearing posted links: {e}")
            ModernPopup.showerror(self.root,"Error", f"Failed to clear posted links: {e}")

    def has_valid_credentials(self):
        """Check if valid credentials exist in the current domain config"""
        if not self.config:
            return False
        required_fields = ['wp_base_url', 'wp_username', 'wp_password', 'gemini_api_key']
        return all(field in self.config and self.config[field] for field in required_fields)

    def check_prerequisites(self):
        """Check system prerequisites"""
        # This is a placeholder for now
        pass

    def on_log_level_change(self, event=None):
        """Handle log level combo box change"""
        level = self.log_level_var.get()
        self.add_log_message(f"Log level changed to: {level}")
        
    def log_automation_start(self):
        """Log automation start with detailed info"""
        self.log_automation_event("[>>] Blog automation session started")
        self.log_automation_event(f"Configuration: Max articles={self.config.get('max_articles', 'N/A')}")
        self.log_automation_event(f"Source URL: {self.config.get('source_url', 'N/A')}")
        self.log_automation_event(f"WordPress URL: {self.config.get('wp_base_url', 'N/A')}")
        image_source = getattr(self, 'image_source_var', None)
        if image_source:
            self.log_automation_event(f"Image source: {image_source.get()}")
        
        # Also log to main logger for visibility
        self.logger.info("[>>] Starting blog automation...")
        self.logger.info(f"Configuration: Max articles={self.config.get('max_articles', 'N/A')}")
        self.logger.info(f"Source URL: {self.config.get('source_url', 'N/A')}")
        self.logger.info(f"WordPress URL: {self.config.get('wp_base_url', 'N/A')}")
        if image_source:
            self.logger.info(f"Image source: {image_source.get()}")
            
    def log_automation_complete(self, success_count=0, error_count=0):
        """Log automation completion with summary"""
        self.log_automation_event("Blog automation session completed")
        self.log_automation_event(f"[OK] Successfully processed: {success_count} articles")
        if error_count > 0:
            self.log_automation_event(f"[X] Errors encountered: {error_count} articles", "warning")
        self.log_automation_event("Session summary complete")
        
        # Also log to main logger
        self.logger.info("Blog automation completed!")
        self.logger.info(f"[OK] Successfully processed: {success_count} articles")
        if error_count > 0:
            self.logger.info(f"[X] Errors encountered: {error_count} articles")
        self.logger.info("Check logs above for detailed information")

    def on_config_selected(self, event=None):
        name = self.config_selector_var.get()
        self.config = self.load_config(name)
        self.refresh_config_tab()
        self.notebook.select(self.config_frame)  # Ensure Configuration tab stays active

    def refresh_config_tab(self):
        # Destroy and recreate config tab to reflect new config
        self.config_frame.destroy()
        self.create_config_tab()
        self.notebook.select(self.config_frame)  # Ensure Configuration tab stays active

    def add_config(self):
        name = self.prompt_for_name("New Configuration Name:")
        if name and name not in self.get_config_files():
            import copy
            new_config = copy.deepcopy(self.config)
            path = os.path.join(self.config_dir, f"{name}.json")
            with open(path, "w") as f:
                json.dump(new_config, f, indent=2)
            self.config_files = self.get_config_files()
            self.config_selector['values'] = self.config_files
            self.config_selector_var.set(name)
            self.on_config_selected()
            ModernPopup.showinfo(self.root,"Configuration Created", f"Configuration '{name}' has been created. You can now edit its settings.")

    def duplicate_config(self):
        name = self.prompt_for_name("Duplicate As:")
        if name and name not in self.get_config_files():
            self.save_config(name)
            self.config_files = self.get_config_files()
            self.config_selector['values'] = self.config_files
            self.config_selector_var.set(name)
            self.on_config_selected()

    def rename_config(self):
        old = self.active_config_name
        name = self.prompt_for_name("Rename Configuration To:")
        if name and name not in self.get_config_files():
            old_path = os.path.join(self.config_dir, f"{old}.json")
            new_path = os.path.join(self.config_dir, f"{name}.json")
            os.rename(old_path, new_path)
            self.config_files = self.get_config_files()
            self.config_selector['values'] = self.config_files
            self.config_selector_var.set(name)
            self.on_config_selected()

    def delete_config(self):
        name = self.active_config_name
        if name == "default":
            ModernPopup.showerror(self.root,"Error", "Cannot delete the default configuration.")
            return
        if ModernPopup.askyesno(self.root,"Delete Configuration", f"Are you sure you want to delete '{name}'?"):
            path = os.path.join(self.config_dir, f"{name}.json")
            os.remove(path)
            self.config_files = self.get_config_files()
            self.config_selector['values'] = self.config_files
            self.config_selector_var.set("default")
            self.on_config_selected()

    def prompt_for_name(self, prompt):
        popup = tk.Toplevel(self.root)
        popup.title(prompt)
        tk.Label(popup, text=prompt).pack(padx=10, pady=10)
        entry = tk.Entry(popup)
        entry.pack(padx=10, pady=5)
        entry.focus_set()
        result = {'name': None}
        def on_ok():
            result['name'] = entry.get().strip()
            popup.destroy()
        tk.Button(popup, text="OK", command=on_ok).pack(pady=10)
        self.root.wait_window(popup)
        return result['name']

    def load_json_config_text(self, filename):
        path = os.path.join(self.config_dir, filename)
        if os.path.exists(path):
            with open(path) as f:
                return json.dumps(json.load(f), indent=2)
        return "{}" if filename.endswith(".json") else "[]"

    def load_style_prompt_text(self):
        path = os.path.join(self.config_dir, "style_prompt.json")
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
                return data.get("style_prompt", "")
        return ""

    def save_json_config_from_text(self, filename, text):
        path = os.path.join(self.config_dir, filename)
        try:
            data = json.loads(text)
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Invalid JSON for {filename}: {e}")
            ModernPopup.showerror(self.root,"Invalid JSON", f"Error in {filename}: {e}")
            raise

    def save_style_prompt_from_text(self, text):
        path = os.path.join(self.config_dir, "style_prompt.json")
        try:
            with open(path, "w") as f:
                json.dump({"style_prompt": text.strip()}, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving style prompt: {e}")
            ModernPopup.showerror(self.root,"Error", f"Failed to save style prompt: {e}")
            raise

    def set_source_config_default(self):
        # Save current config as default.json in configs/
        import shutil
        self.save_source_config()
        default_path = os.path.join(self.config_dir, "default.json")
        current_path = os.path.join(self.config_dir, f"{self.active_config_name}.json")
        shutil.copyfile(current_path, default_path)
        self.logger.info("Current source configuration set as default")
        ModernPopup.showinfo(self.root,"Default Set", "Current source configuration set as default.")

    def extract_domain_from_url(self, url: str) -> str:
        """Extract domain name from WordPress URL for configuration separation"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            # Remove common subdomains and clean up
            domain = domain.replace('.', '_').replace('-', '_')
            return domain
        except Exception as e:
            self.logger.error(f"Error extracting domain from URL: {e}")
            return "default"
    
    def setup_domain_config_directory(self, domain: str):
        """Setup configuration directory for a specific domain"""
        try:
            # Create domain-specific config directory
            domain_dir = os.path.join(self.base_config_dir, domain)
            if not os.path.exists(domain_dir):
                os.makedirs(domain_dir, exist_ok=True)
                self.logger.info(f"Created configuration directory for domain: {domain}")
            
            self.current_domain = domain
            self.domain_config_dir = domain_dir
            
            # Initialize default configuration files for this domain if they don't exist
            self.initialize_domain_config_files(domain_dir)
            
            # Update config files list for this domain
            self.config_files = self.get_config_files()
            
            return domain_dir
            
        except Exception as e:
            self.logger.error(f"Error setting up domain config directory: {e}")
            # Fallback to base directory
            self.domain_config_dir = self.base_config_dir
            return self.base_config_dir
    
    def initialize_domain_config_files(self, domain_dir: str):
        """Initialize default configuration files for a new domain"""
        try:
            # List of configuration files to initialize
            config_files = {
                "default.json": self.get_default_config(),
                "internal_links.json": {},
                "external_links.json": {},
                "style_prompt.json": {"style_prompt": ""},
                "category_keywords.json": {},
                "tag_synonyms.json": {},
                "static_clubs.json": [],
                "stop_words.json": [],
                "do_follow_urls.json": [],
                "openai_image_config.json": {
                    "image_size": "1024x1024",
                    "image_style": "photorealistic", 
                    "image_model": "dall-e-3",
                    "num_images": 1,
                    "prompt_prefix": "",
                    "prompt_suffix": "",
                    "custom_prompt": ""
                },
                "weights.json": {
                    "summary_length": 120,
                    "title_length": 60,
                    "content_weight": 1.0,
                    "seo_weight": 1.0,
                    "image_weight": 1.0
                }
            }
            
            # Copy from base config directory if files exist there, otherwise create defaults
            for filename, default_content in config_files.items():
                domain_file_path = os.path.join(domain_dir, filename)
                base_file_path = os.path.join(self.base_config_dir, filename)
                
                if not os.path.exists(domain_file_path):
                    if os.path.exists(base_file_path) and filename != "default.json":
                        # Copy existing configuration as template (except default.json)
                        import shutil
                        shutil.copy2(base_file_path, domain_file_path)
                        self.logger.info(f"Copied template configuration: {filename}")
                    else:
                        # Create default configuration
                        with open(domain_file_path, 'w') as f:
                            json.dump(default_content, f, indent=2)
                        self.logger.info(f"Created default configuration: {filename}")
            
            # Create .last_used file
            last_used_path = os.path.join(domain_dir, ".last_used")
            if not os.path.exists(last_used_path):
                with open(last_used_path, 'w') as f:
                    f.write("default")
                    
        except Exception as e:
            self.logger.error(f"Error initializing domain config files: {e}")
    
    def get_current_config_dir(self) -> str:
        """Get the current configuration directory (domain-specific or base)"""
        return self.domain_config_dir or self.base_config_dir

    # Convenience logging methods using unified logging
    def log_automation_event(self, message: str, level: str = "info"):
        """Log an automation-specific event"""
        if hasattr(self, 'log_manager') and self.log_manager:
            self.log_manager.log_automation_event(level, f"{message}")
        else:
            log_method = getattr(self.logger, level.lower(), self.logger.info)
            log_method(f"AUTOMATION: {message}")
        
    def log_api_event(self, message: str, level: str = "info"):
        """Log an API-specific event"""
        if hasattr(self, 'log_manager') and self.log_manager:
            self.log_manager._log_with_category(level, f"{message}", "API")
        else:
            log_method = getattr(self.logger, level.lower(), self.logger.info)
            log_method(f"API: {message}")
        
    def log_security_event(self, message: str, level: str = "warning"):
        """Log a security-specific event"""
        if hasattr(self, 'log_manager') and self.log_manager:
            self.log_manager._log_with_category(level, f"{message}", "SECURITY")
        else:
            log_method = getattr(self.logger, level.lower(), self.logger.warning)
            log_method(f"SECURITY: {message}")
        
    def log_ui_event(self, message: str, level: str = "debug"):
        """Log a UI-specific event"""
        if hasattr(self, 'log_manager') and self.log_manager:
            self.log_manager._log_with_category(level, f"{message}", "UI")
        else:
            log_method = getattr(self.logger, level.lower(), self.logger.debug)
            log_method(f"UI: {message}")

def main():
    """Main function to run the application with global error handling"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Global exception handler to prevent crashes"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_msg = f"Unhandled exception: {exc_type.__name__}: {exc_value}"
        print(f"ERROR: {error_msg}")
        
        # Try to show error dialog if tkinter is available
        try:
            import tkinter.messagebox as messagebox
            ModernPopup.showerror(self.root,
                "Application Error", 
                f"An unexpected error occurred:\n\n{error_msg}\n\n"
                f"The application will continue running, but some features may not work properly.\n\n"
                f"Please check the logs for more details."
            )
        except:
            pass
    
    # Set global exception handler
    import sys
    sys.excepthook = handle_exception
    
    root = tk.Tk()
    
    # Set application icon
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            # Method 1: Use iconphoto() - works best for modern systems including macOS
            icon_image = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, icon_image)
            
            # Method 2: Also set the window icon name for better dock integration
            root.wm_iconname("AUTO Blogger")
            
            print(f"[OK] Application icon set: {icon_path}")
        else:
            print(f"[!] Icon file not found: {icon_path}")
    except Exception as e:
        print(f"[X] Error setting application icon: {e}")
        # Fallback: At least set the window icon name
        try:
            root.wm_iconname("AUTO Blogger")
        except:
            pass
    
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
            if ModernPopup.askyesno(root, "Quit", "Automation is running. Are you sure you want to quit?"):
                app.stop_requested = True
                
                # Finalize logging session
                try:
                    if hasattr(app, 'log_manager'):
                        from log_manager import finalize_logging
                        finalize_logging()
                        app.logger.info("Logging session finalized on application exit")
                except Exception as e:
                    print(f"Error finalizing logging: {e}")
                
                root.destroy()
        else:
            # Finalize logging session on normal exit
            try:
                if hasattr(app, 'log_manager'):
                    from log_manager import finalize_logging
                    finalize_logging()
                    app.logger.info("Logging session finalized on application exit")
            except Exception as e:
                print(f"Error finalizing logging: {e}")
                
            root.destroy()
            
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()
