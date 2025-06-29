#!/usr/bin/env python3
"""
Unified Log Manager for AUTO Blogger
Consolidates all logs into a single file with tags for better organization

Copyright © 2025 AryanVBW
GitHub: https://github.com/AryanVBW
"""

import logging
import os
import json
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

class UnifiedLogManager:
    """
    Unified logging manager that creates a single log file with tags
    All log entries are consolidated with appropriate tags for filtering
    """
    
    def __init__(self, base_log_dir: str = "logs", session_prefix: str = "session"):
        """
        Initialize the Unified Log Manager
        
        Args:
            base_log_dir: Base directory for all log files
            session_prefix: Prefix for session directories/files
        """
        self.base_log_dir = Path(base_log_dir)
        self.session_prefix = session_prefix
        self.session_id = None
        self.session_timestamp = None
        self.unified_log_file = None
        self.logger = None
        self.session_metadata = {}
        
        # Ensure logs directory exists
        self.base_log_dir.mkdir(exist_ok=True)
        
        # Initialize session
        self._initialize_session()
        
    def _initialize_session(self):
        """Initialize a new logging session with unified log file"""
        # Generate session timestamp
        now = datetime.now()
        self.session_timestamp = now.strftime("%Y%m%d_%H%M%S")
        self.session_id = f"{self.session_prefix}_{self.session_timestamp}"
        
        # Create unified log file
        filename = f"{self.session_id}_unified.log"
        self.unified_log_file = self.base_log_dir / filename
        
        # Setup unified logger
        self._setup_unified_logger()
        
        # Create session metadata
        self._create_session_metadata()
        
        # Log session initialization
        self.log_info("🚀 Unified logging system initialized", category="SYSTEM")
        self.log_info(f"📁 Session: {self.session_id}", category="SYSTEM")
        self.log_info(f"📄 Unified log file: {self.unified_log_file.relative_to('.')}", category="SYSTEM")
        
    def _setup_unified_logger(self):
        """Setup the unified logger"""
        # Create unified logger
        self.logger = logging.getLogger(f"{self.session_id}_unified")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create file handler
        file_handler = logging.FileHandler(self.unified_log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create unified formatter with tags
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | [%(category)s] | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
        
    def _create_session_metadata(self):
        """Create metadata file for the session"""
        self.session_metadata = {
            'session_id': self.session_id,
            'start_time': datetime.now().isoformat(),
            'timestamp': self.session_timestamp,
            'unified_log_file': str(self.unified_log_file.relative_to('.')),
            'log_format': 'unified_with_tags',
            'categories': [
                'SYSTEM', 'MAIN', 'ERROR', 'DEBUG', 'AUTOMATION', 
                'API', 'SECURITY', 'UI', 'WEBDRIVER', 'CONTENT'
            ],
            'status': 'active'
        }
        
        metadata_file = self.base_log_dir / f"{self.session_id}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(self.session_metadata, f, indent=2)
            
    def _log_with_category(self, level: str, message: str, category: str = "MAIN", **kwargs):
        """
        Internal method to log with category tag
        
        Args:
            level: Log level ('debug', 'info', 'warning', 'error', 'critical')
            message: Log message
            category: Category tag for filtering
            **kwargs: Additional context data
        """
        # Add context if provided
        if kwargs:
            context = ' | '.join([f"{k}={v}" for k, v in kwargs.items()])
            message = f"{message} | {context}"
            
        # Create log record with category
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        
        # Use extra parameter to pass category to formatter
        log_method(message, extra={'category': category})
        
    def log_debug(self, message: str, category: str = "DEBUG", **kwargs):
        """Log a debug message"""
        self._log_with_category('debug', message, category, **kwargs)
        
    def log_info(self, message: str, category: str = "MAIN", **kwargs):
        """Log an info message"""
        self._log_with_category('info', message, category, **kwargs)
        
    def log_warning(self, message: str, category: str = "MAIN", **kwargs):
        """Log a warning message"""
        self._log_with_category('warning', message, category, **kwargs)
        
    def log_error(self, message: str, category: str = "ERROR", **kwargs):
        """Log an error message"""
        self._log_with_category('error', message, category, **kwargs)
        
    def log_critical(self, message: str, category: str = "ERROR", **kwargs):
        """Log a critical message"""
        self._log_with_category('critical', message, category, **kwargs)
        
    def log_automation_event(self, level: str, message: str, **kwargs):
        """
        Log an automation-specific event
        
        Args:
            level: Log level ('info', 'warning', 'error', 'debug')
            message: Log message
            **kwargs: Additional context data
        """
        self._log_with_category(level, message, "AUTOMATION", **kwargs)
        
    def log_api_event(self, method: str, url: str, status_code: int = None, 
                     response_time: float = None, error: str = None):
        """
        Log an API-specific event
        
        Args:
            method: HTTP method
            url: API endpoint URL
            status_code: HTTP status code
            response_time: Response time in seconds
            error: Error message if any
        """
        if error:
            self.log_error(f"API ERROR | {method} {url} | Error: {error}", category="API")
        elif status_code:
            level = 'info' if 200 <= status_code < 400 else 'warning'
            time_str = f" | {response_time:.2f}s" if response_time else ""
            self._log_with_category(level, f"API {method} {url} | Status: {status_code}{time_str}", "API")
        else:
            self.log_info(f"API REQUEST | {method} {url}", category="API")
            
    def log_security_event(self, event_type: str, details: str, severity: str = 'warning'):
        """
        Log a security-related event
        
        Args:
            event_type: Type of security event
            details: Event details
            severity: Severity level ('info', 'warning', 'error')
        """
        self._log_with_category(severity, f"SECURITY {event_type.upper()} | {details}", "SECURITY")
        
    def log_ui_event(self, event: str, details: str = "", level: str = 'info'):
        """Log a UI-related event"""
        message = f"UI {event.upper()}"
        if details:
            message += f" | {details}"
        self._log_with_category(level, message, "UI")
        
    def log_webdriver_event(self, event: str, details: str = "", level: str = 'info'):
        """Log a WebDriver-related event"""
        message = f"WEBDRIVER {event.upper()}"
        if details:
            message += f" | {details}"
        self._log_with_category(level, message, "WEBDRIVER")
        
    def log_content_event(self, event: str, details: str = "", level: str = 'info'):
        """Log a content processing event"""
        message = f"CONTENT {event.upper()}"
        if details:
            message += f" | {details}"
        self._log_with_category(level, message, "CONTENT")
        
    def get_session_info(self) -> Dict:
        """Get current session information"""
        return {
            'session_id': self.session_id,
            'timestamp': self.session_timestamp,
            'unified_log_file': str(self.unified_log_file.relative_to('.')),
            'base_dir': str(self.base_log_dir.absolute())
        }
        
    def list_previous_sessions(self) -> List[Dict]:
        """List all previous logging sessions"""
        sessions = []
        try:
            # Look for metadata files in the logs directory
            for metadata_file in self.base_log_dir.glob('*_metadata.json'):
                try:
                    with open(metadata_file, 'r') as f:
                        session_data = json.load(f)
                        sessions.append(session_data)
                except Exception as e:
                    print(f"Error reading metadata file {metadata_file}: {e}")
                    
            # Sort by start time (newest first)
            sessions.sort(key=lambda x: x.get('start_time', ''), reverse=True)
            return sessions
            
        except Exception as e:
            print(f"Error listing previous sessions: {e}")
            return []
        
    def finalize_session(self):
        """Finalize the current session and update metadata"""
        try:
            # Update session metadata
            self.session_metadata['end_time'] = datetime.now().isoformat()
            self.session_metadata['status'] = 'completed'
            
            # Write updated metadata
            metadata_file = self.base_log_dir / f"{self.session_id}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(self.session_metadata, f, indent=2)
                
            # Log session end
            self.log_info(f"📋 Session finalized: {self.session_id}", category="SYSTEM")
            
        except Exception as e:
            print(f"Error finalizing session: {e}")

# Global unified log manager instance
_unified_log_manager = None

def get_unified_log_manager() -> UnifiedLogManager:
    """Get the global unified log manager instance"""
    global _unified_log_manager
    if _unified_log_manager is None:
        _unified_log_manager = UnifiedLogManager()
    return _unified_log_manager

def initialize_unified_logging() -> UnifiedLogManager:
    """Initialize the unified logging system and return the log manager"""
    global _unified_log_manager
    _unified_log_manager = UnifiedLogManager()
    return _unified_log_manager

def finalize_unified_logging():
    """Finalize the current unified logging session"""
    global _unified_log_manager
    if _unified_log_manager:
        _unified_log_manager.finalize_session()

# Convenience functions for unified logging
def log_info(message: str, category: str = "MAIN", **kwargs):
    """Log an info message"""
    get_unified_log_manager().log_info(message, category, **kwargs)

def log_error(message: str, category: str = "ERROR", **kwargs):
    """Log an error message"""
    get_unified_log_manager().log_error(message, category, **kwargs)

def log_debug(message: str, category: str = "DEBUG", **kwargs):
    """Log a debug message"""
    get_unified_log_manager().log_debug(message, category, **kwargs)

def log_warning(message: str, category: str = "MAIN", **kwargs):
    """Log a warning message"""
    get_unified_log_manager().log_warning(message, category, **kwargs)

def log_automation(message: str, level: str = 'info', **kwargs):
    """Log an automation event"""
    get_unified_log_manager().log_automation_event(level, message, **kwargs)