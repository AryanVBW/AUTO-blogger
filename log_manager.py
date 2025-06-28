#!/usr/bin/env python3
"""
Advanced Log Manager for AUTO Blogger
Creates timestamped log files in separate categories with session management

Copyright © 2025 AryanVBW
GitHub: https://github.com/AryanVBW
"""

import logging
import os
import json
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

class SessionLogManager:
    """
    Advanced logging manager that creates timestamped session-based log files
    Each session gets its own set of log files organized by category
    """
    
    def __init__(self, base_log_dir: str = "logs", session_prefix: str = "session"):
        """
        Initialize the Session Log Manager
        
        Args:
            base_log_dir: Base directory for all log files
            session_prefix: Prefix for session directories/files
        """
        self.base_log_dir = Path(base_log_dir)
        self.session_prefix = session_prefix
        self.session_id = None
        self.session_timestamp = None
        self.log_files = {}
        self.loggers = {}
        self.session_metadata = {}
        
        # Ensure logs directory exists
        self.base_log_dir.mkdir(exist_ok=True)
        
        # Initialize session
        self._initialize_session()
        
    def _initialize_session(self):
        """Initialize a new logging session with timestamped files"""
        # Generate session timestamp
        now = datetime.now()
        self.session_timestamp = now.strftime("%Y%m%d_%H%M%S")
        self.session_id = f"{self.session_prefix}_{self.session_timestamp}"
        
        # Define log categories and their configurations
        self.log_categories = {
            'main': {
                'level': logging.INFO,
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                'description': 'Main application logs'
            },
            'errors': {
                'level': logging.ERROR,
                'format': '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
                'description': 'Error and exception logs'
            },
            'debug': {
                'level': logging.DEBUG,
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                'description': 'Debug and development logs'
            },
            'automation': {
                'level': logging.INFO,
                'format': '%(asctime)s - AUTOMATION - %(levelname)s - %(message)s',
                'description': 'Blog automation process logs'
            },
            'api': {
                'level': logging.INFO,
                'format': '%(asctime)s - API - %(levelname)s - %(message)s',
                'description': 'API requests and responses'
            },
            'security': {
                'level': logging.WARNING,
                'format': '%(asctime)s - SECURITY - %(levelname)s - %(message)s',
                'description': 'Security-related events'
            }
        }
        
        # Create log files for each category
        self._create_log_files()
        
        # Create session metadata
        self._create_session_metadata()
        
        # Setup loggers
        self._setup_loggers()
        
        # Log session initialization
        self.get_logger('main').info(f"🚀 Logging system initialized for session: {self.session_id}")
        self.get_logger('main').info(f"📁 Log files created in: {self.base_log_dir.absolute()}")
        self.get_logger('main').info(f"📄 Main log: {self.log_files['main']}")
        self.get_logger('main').info(f"🚨 Error log: {self.log_files['errors']}")
        self.get_logger('main').info(f"🔧 Debug log: {self.log_files['debug']}")
        self.get_logger('main').info(f"🤖 Automation log: {self.log_files['automation']}")
        self.get_logger('main').info(f"🌐 API log: {self.log_files['api']}")
        self.get_logger('main').info(f"🔒 Security log: {self.log_files['security']}")
        
    def _create_log_files(self):
        """Create log files for each category"""
        for category in self.log_categories.keys():
            filename = f"{self.session_id}_{category}.log"
            file_path = self.base_log_dir / filename
            self.log_files[category] = str(file_path.relative_to('.'))
            
            # Create empty log file
            file_path.touch(exist_ok=True)
            
    def _create_session_metadata(self):
        """Create metadata file for the session"""
        self.session_metadata = {
            'session_id': self.session_id,
            'start_time': datetime.now().isoformat(),
            'timestamp': self.session_timestamp,
            'log_files': self.log_files.copy(),
            'categories': {k: v['description'] for k, v in self.log_categories.items()},
            'status': 'active'
        }
        
        metadata_file = self.base_log_dir / f"{self.session_id}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(self.session_metadata, f, indent=2)
            
    def _setup_loggers(self):
        """Setup loggers for each category"""
        # Clear any existing handlers from root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
        for category, config in self.log_categories.items():
            # Create logger for this category
            logger = logging.getLogger(f"{self.session_id}_{category}")
            logger.setLevel(config['level'])
            
            # Clear any existing handlers
            logger.handlers.clear()
            
            # Create file handler
            file_handler = logging.FileHandler(self.log_files[category])
            file_handler.setLevel(config['level'])
            
            # Create formatter
            formatter = logging.Formatter(config['format'])
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            logger.addHandler(file_handler)
            
            # Store logger reference
            self.loggers[category] = logger
            
        # Setup the main application logger to capture all levels
        app_logger = logging.getLogger('BlogAutomation')
        app_logger.handlers.clear()
        app_logger.setLevel(logging.DEBUG)
        
        # Don't use automatic routing - it causes conflicts
        # Individual loggers should be used directly for each category
        
    def get_logger(self, category: str = 'main') -> logging.Logger:
        """
        Get a logger for a specific category
        
        Args:
            category: Log category ('main', 'errors', 'debug', 'automation', 'api', 'security')
            
        Returns:
            Logger instance for the specified category
        """
        if category not in self.loggers:
            category = 'main'  # Fallback to main logger
        return self.loggers[category]
    
    def log_automation_event(self, level: str, message: str, **kwargs):
        """
        Log an automation-specific event
        
        Args:
            level: Log level ('info', 'warning', 'error', 'debug')
            message: Log message
            **kwargs: Additional context data
        """
        logger = self.get_logger('automation')
        log_method = getattr(logger, level.lower(), logger.info)
        
        if kwargs:
            context = ' | '.join([f"{k}={v}" for k, v in kwargs.items()])
            message = f"{message} | {context}"
            
        log_method(message)
        
    def log_api_event(self, method: str, url: str, status_code: int = None, response_time: float = None, error: str = None):
        """
        Log an API-specific event
        
        Args:
            method: HTTP method
            url: API endpoint URL
            status_code: HTTP status code
            response_time: Response time in seconds
            error: Error message if any
        """
        logger = self.get_logger('api')
        
        if error:
            logger.error(f"API ERROR | {method} {url} | Error: {error}")
        elif status_code:
            level = 'info' if 200 <= status_code < 400 else 'warning'
            log_method = getattr(logger, level)
            
            time_str = f" | {response_time:.2f}s" if response_time else ""
            log_method(f"API {method} {url} | Status: {status_code}{time_str}")
        else:
            logger.info(f"API REQUEST | {method} {url}")
            
    def log_security_event(self, event_type: str, details: str, severity: str = 'warning'):
        """
        Log a security-related event
        
        Args:
            event_type: Type of security event
            details: Event details
            severity: Severity level ('info', 'warning', 'error')
        """
        logger = self.get_logger('security')
        log_method = getattr(logger, severity.lower(), logger.warning)
        log_method(f"SECURITY {event_type.upper()} | {details}")
        
    def finalize_session(self):
        """Finalize the current session and update metadata"""
        try:
            # Update session metadata
            self.session_metadata['end_time'] = datetime.now().isoformat()
            self.session_metadata['status'] = 'completed'
            
            # Calculate session duration
            start_time = datetime.fromisoformat(self.session_metadata['start_time'])
            end_time = datetime.fromisoformat(self.session_metadata['end_time'])
            duration = (end_time - start_time).total_seconds()
            self.session_metadata['duration_seconds'] = duration
            
            # Add log file sizes
            file_sizes = {}
            for category, file_path in self.log_files.items():
                try:
                    size = os.path.getsize(file_path)
                    file_sizes[category] = size
                except OSError:
                    file_sizes[category] = 0
            self.session_metadata['file_sizes'] = file_sizes
            
            # Write updated metadata
            metadata_file = self.base_log_dir / f"{self.session_id}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(self.session_metadata, f, indent=2)
                
            # Log session end
            self.get_logger('main').info(f"📋 Session finalized: {self.session_id}")
            self.get_logger('main').info(f"⏱️ Session duration: {duration:.1f} seconds")
            
        except Exception as e:
            print(f"Error finalizing session: {e}")
            
    def get_session_info(self) -> Dict:
        """Get current session information"""
        return {
            'session_id': self.session_id,
            'timestamp': self.session_timestamp,
            'log_files': self.log_files.copy(),
            'base_dir': str(self.base_log_dir.absolute())
        }
        
    def list_previous_sessions(self) -> List[Dict]:
        """List all previous logging sessions"""
        sessions = []
        
        try:
            for metadata_file in self.base_log_dir.glob("*_metadata.json"):
                with open(metadata_file, 'r') as f:
                    session_data = json.load(f)
                    sessions.append(session_data)
                    
            # Sort by start time (newest first)
            sessions.sort(key=lambda x: x.get('start_time', ''), reverse=True)
            
        except Exception as e:
            print(f"Error listing sessions: {e}")
            
        return sessions
        
    def cleanup_old_sessions(self, keep_days: int = 30):
        """
        Clean up old session log files
        
        Args:
            keep_days: Number of days to keep log files
        """
        cutoff_date = datetime.now() - datetime.timedelta(days=keep_days)
        cleaned_count = 0
        
        try:
            for metadata_file in self.base_log_dir.glob("*_metadata.json"):
                try:
                    with open(metadata_file, 'r') as f:
                        session_data = json.load(f)
                    
                    start_time = datetime.fromisoformat(session_data.get('start_time', ''))
                    
                    if start_time < cutoff_date:
                        # Remove session files
                        session_id = session_data.get('session_id', '')
                        
                        # Remove log files
                        for log_file in self.base_log_dir.glob(f"{session_id}*"):
                            log_file.unlink()
                            cleaned_count += 1
                            
                except Exception as e:
                    print(f"Error cleaning session {metadata_file}: {e}")
                    
            if cleaned_count > 0:
                self.get_logger('main').info(f"🧹 Cleaned up {cleaned_count} old log files")
                
        except Exception as e:
            print(f"Error during cleanup: {e}")

# Global log manager instance
_log_manager = None

def get_log_manager() -> SessionLogManager:
    """Get the global log manager instance"""
    global _log_manager
    if _log_manager is None:
        _log_manager = SessionLogManager()
    return _log_manager

def initialize_logging() -> SessionLogManager:
    """Initialize the logging system and return the log manager"""
    global _log_manager
    _log_manager = SessionLogManager()
    return _log_manager

def finalize_logging():
    """Finalize the current logging session"""
    global _log_manager
    if _log_manager:
        _log_manager.finalize_session()

# Convenience functions for common logging operations
def log_info(message: str, category: str = 'main'):
    """Log an info message"""
    get_log_manager().get_logger(category).info(message)

def log_error(message: str, category: str = 'errors'):
    """Log an error message"""
    get_log_manager().get_logger(category).error(message)

def log_debug(message: str, category: str = 'debug'):
    """Log a debug message"""
    get_log_manager().get_logger(category).debug(message)

def log_automation(message: str, **kwargs):
    """Log an automation event"""
    get_log_manager().log_automation_event('info', message, **kwargs)

def log_api(method: str, url: str, **kwargs):
    """Log an API event"""
    get_log_manager().log_api_event(method, url, **kwargs)

def log_security(event_type: str, details: str, severity: str = 'warning'):
    """Log a security event"""
    get_log_manager().log_security_event(event_type, details, severity)

if __name__ == "__main__":
    # Test the log manager
    print("Testing SessionLogManager...")
    
    # Initialize
    log_manager = initialize_logging()
    print(f"Session initialized: {log_manager.session_id}")
    
    # Test different log categories
    log_info("This is a test info message")
    log_error("This is a test error message")
    log_debug("This is a test debug message")
    log_automation("Blog automation started", articles=5, source="test.com")
    log_api("GET", "https://api.wordpress.com/posts", status_code=200, response_time=0.5)
    log_security("login_attempt", "User attempted login with invalid credentials")
    
    # Show session info
    session_info = log_manager.get_session_info()
    print("\nSession Info:")
    for key, value in session_info.items():
        print(f"  {key}: {value}")
    
    # List previous sessions
    sessions = log_manager.list_previous_sessions()
    print(f"\nFound {len(sessions)} previous sessions")
    
    # Finalize
    finalize_logging()
    print("Session finalized")
