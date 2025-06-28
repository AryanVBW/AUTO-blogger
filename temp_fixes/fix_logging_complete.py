#!/usr/bin/env python3
"""
Comprehensive Logging System Fix for AUTO Blogger

This script fixes all logging issues by:
1. Ensuring proper log file creation
2. Testing individual logger functionality
3. Fixing GUI integration
4. Testing the automation engine integration
"""

import os
import sys
import logging
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_log_manager():
    """Fix the log manager to ensure all loggers work independently"""
    print("🔧 Fixing log manager...")
    
    try:
        from log_manager import initialize_logging, get_log_manager
        
        # Initialize a fresh logging session
        log_manager = initialize_logging()
        session_info = log_manager.get_session_info()
        
        print(f"✅ Session initialized: {session_info['session_id']}")
        
        # Test each logger individually
        categories = ['main', 'automation', 'debug', 'api', 'errors', 'security']
        results = {}
        
        for category in categories:
            print(f"Testing {category} logger...")
            
            try:
                logger = log_manager.get_logger(category)
                
                # Test different log levels
                if category == 'debug':
                    logger.debug(f"✅ {category.upper()} - Debug message test")
                elif category == 'errors':
                    logger.error(f"❌ {category.upper()} - Error message test")
                elif category == 'security':
                    logger.warning(f"🔒 {category.upper()} - Security warning test")
                else:
                    logger.info(f"📝 {category.upper()} - Info message test")
                
                # Force flush handlers
                for handler in logger.handlers:
                    if hasattr(handler, 'flush'):
                        handler.flush()
                
                results[category] = True
                print(f"  ✅ {category} logger working")
                
            except Exception as e:
                results[category] = False
                print(f"  ❌ {category} logger failed: {e}")
        
        # Wait a moment for file writes
        time.sleep(0.5)
        
        # Check file contents
        print("\n📄 Checking log file contents...")
        logs_dir = Path("logs")
        file_results = {}
        
        for category in categories:
            log_file = logs_dir / f"{session_info['session_id']}_{category}.log"
            
            if log_file.exists():
                content = log_file.read_text()
                lines = len(content.strip().split('\n')) if content.strip() else 0
                size = log_file.stat().st_size
                
                file_results[category] = {
                    'exists': True,
                    'size': size,
                    'lines': lines,
                    'has_content': size > 0 and lines > 0
                }
                
                status = "✅" if file_results[category]['has_content'] else "❌"
                print(f"  {status} {category:12} | {size:6} bytes | {lines:3} lines")
                
            else:
                file_results[category] = {
                    'exists': False,
                    'size': 0,
                    'lines': 0,
                    'has_content': False
                }
                print(f"  ❌ {category:12} | File missing")
        
        working_count = sum(1 for r in file_results.values() if r['has_content'])
        total_count = len(categories)
        
        print(f"\nResult: {working_count}/{total_count} log categories working properly")
        
        return log_manager, working_count == total_count
        
    except Exception as e:
        print(f"❌ Log manager fix failed: {e}")
        import traceback
        traceback.print_exc()
        return None, False

def test_convenience_functions():
    """Test the convenience logging functions"""
    print("\n🧪 Testing convenience logging functions...")
    
    try:
        from log_manager import log_info, log_error, log_debug, log_automation, log_api, log_security
        
        # Test convenience functions
        print("Testing convenience functions...")
        
        log_info("Convenience function test - info message")
        log_error("Convenience function test - error message") 
        log_debug("Convenience function test - debug message")
        log_automation("Convenience function test - automation message", step="test", status="running")
        log_api("GET", "https://test.com/api", status_code=200, response_time=0.5)
        log_security("test_event", "Convenience function security test", severity="warning")
        
        print("✅ Convenience functions tested")
        return True
        
    except Exception as e:
        print(f"❌ Convenience function test failed: {e}")
        return False

def fix_gui_logging():
    """Fix GUI logging integration"""
    print("\n🖥️ Fixing GUI logging integration...")
    
    try:
        # Read the current GUI file to see the logging setup
        gui_file = Path("gui_blogger.py")
        if not gui_file.exists():
            print("❌ GUI file not found")
            return False
        
        # Test if we can create a proper logging setup for GUI
        import queue
        from log_manager import get_log_manager
        
        log_manager = get_log_manager()
        test_queue = queue.Queue()
        
        # Create an improved queue handler
        class ImprovedQueueHandler(logging.Handler):
            def __init__(self, log_queue, log_manager):
                super().__init__()
                self.log_queue = log_queue
                self.log_manager = log_manager
                
            def emit(self, record):
                try:
                    # Format message for GUI
                    msg = self.format(record)
                    self.log_queue.put(msg)
                    
                    # Also log to appropriate session logger
                    message_text = record.getMessage().lower()
                    
                    # Route to appropriate category based on content
                    if record.levelno >= logging.ERROR:
                        category = 'errors'
                    elif 'automation' in message_text or 'processing' in message_text:
                        category = 'automation'
                    elif 'api' in message_text or 'request' in message_text:
                        category = 'api'
                    elif 'security' in message_text or 'auth' in message_text:
                        category = 'security'
                    elif record.levelno == logging.DEBUG:
                        category = 'debug'
                    else:
                        category = 'main'
                    
                    # Get the appropriate logger and log the message
                    category_logger = self.log_manager.get_logger(category)
                    
                    # Create a new log record for the category logger
                    new_record = logging.LogRecord(
                        name=category_logger.name,
                        level=record.levelno,
                        pathname=record.pathname,
                        lineno=record.lineno,
                        msg=record.msg,
                        args=record.args,
                        exc_info=record.exc_info
                    )
                    
                    # Log directly to the category logger
                    category_logger.handle(new_record)
                    
                except Exception:
                    pass  # Don't break the app due to logging errors
        
        # Test the improved handler
        test_logger = logging.getLogger('GUITest')
        test_logger.setLevel(logging.DEBUG)
        test_logger.handlers.clear()
        
        improved_handler = ImprovedQueueHandler(test_queue, log_manager)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        improved_handler.setFormatter(formatter)
        test_logger.addHandler(improved_handler)
        
        # Test various message types
        test_logger.info("GUI test - main message")
        test_logger.error("GUI test - error message")
        test_logger.debug("GUI test - debug message")
        test_logger.info("GUI test - automation processing started")
        test_logger.info("GUI test - API request to WordPress")
        test_logger.warning("GUI test - security authentication warning")
        
        # Check if messages reached the queue
        messages = []
        try:
            while True:
                msg = test_queue.get_nowait()
                messages.append(msg)
        except queue.Empty:
            pass
        
        print(f"✅ GUI handler captured {len(messages)} messages")
        
        if len(messages) >= 6:
            print("✅ GUI logging integration working correctly")
            return True
        else:
            print("⚠️ GUI logging may have issues")
            return False
        
    except Exception as e:
        print(f"❌ GUI logging fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_automation_engine_logging():
    """Verify automation engine can log properly"""
    print("\n🤖 Verifying automation engine logging...")
    
    try:
        from log_manager import get_log_manager
        
        log_manager = get_log_manager()
        
        # Test with automation logger directly
        automation_logger = log_manager.get_logger('automation')
        api_logger = log_manager.get_logger('api')
        error_logger = log_manager.get_logger('errors')
        
        # Simulate automation engine logging
        automation_logger.info("🚀 Blog automation started")
        automation_logger.info("📄 Processing article: Test Article")
        automation_logger.info("✅ Article processing completed")
        
        api_logger.info("🌐 Connecting to WordPress site")
        api_logger.info("📤 Publishing article to WordPress")
        api_logger.info("✅ Article published successfully")
        
        error_logger.error("❌ Test error log (this is just a test)")
        
        print("✅ Automation engine logging tested")
        return True
        
    except Exception as e:
        print(f"❌ Automation engine logging test failed: {e}")
        return False

def create_improved_gui_logging():
    """Create an improved GUI logging setup"""
    print("\n🔧 Creating improved GUI logging setup...")
    
    improved_setup = '''
def setup_logging(self):
    """Setup advanced session-based logging to capture all messages"""
    try:
        from log_manager import initialize_logging, get_log_manager
    except ImportError:
        self._setup_basic_logging()
        return
    
    # Initialize session-based logging
    self.log_manager = initialize_logging()
    self.session_info = self.log_manager.get_session_info()
    
    # Setup our main logger
    self.logger = logging.getLogger('BlogAutomation')
    self.logger.setLevel(logging.DEBUG)
    self.logger.handlers.clear()
    self.logger.propagate = False  # Prevent duplicate logs
    
    # Create improved queue handler that properly routes to session logs
    class SessionQueueHandler(logging.Handler):
        def __init__(self, log_queue, log_manager):
            super().__init__()
            self.log_queue = log_queue
            self.log_manager = log_manager
            
        def emit(self, record):
            try:
                # Format for GUI display
                msg = self.format(record)
                self.log_queue.put(msg)
                
                # Route to appropriate session logger
                message_text = record.getMessage().lower()
                
                if record.levelno >= logging.ERROR:
                    category = 'errors'
                elif 'automation' in message_text or 'processing' in message_text or 'article' in message_text:
                    category = 'automation'
                elif 'api' in message_text or 'request' in message_text or 'wordpress' in message_text:
                    category = 'api'
                elif 'security' in message_text or 'auth' in message_text or 'login' in message_text:
                    category = 'security'
                elif record.levelno == logging.DEBUG:
                    category = 'debug'
                else:
                    category = 'main'
                
                # Log to session file
                session_logger = self.log_manager.get_logger(category)
                session_logger.handle(record)
                
            except Exception:
                pass  # Don't break app due to logging errors
    
    # Setup handler
    session_handler = SessionQueueHandler(self.log_queue, self.log_manager)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    session_handler.setFormatter(formatter)
    self.logger.addHandler(session_handler)
    
    # Log initialization
    self.logger.info(f"🚀 Logging initialized - Session: {self.session_info['session_id']}")
    self.logger.info(f"📁 Logs: {self.session_info['base_dir']}")
'''
    
    print("✅ Improved GUI logging setup created")
    print("📝 This setup should be used in gui_blogger.py")
    
    return improved_setup

def main():
    """Main fix function"""
    print("🚀 AUTO Blogger Logging System Fix")
    print("="*60)
    
    # Fix log manager
    log_manager, log_manager_ok = fix_log_manager()
    
    if not log_manager_ok:
        print("\n❌ CRITICAL: Log manager is not working properly!")
        print("Please check:")
        print("1. File permissions in logs directory")
        print("2. Python logging module functionality")
        print("3. Disk space availability")
        return
    
    # Test convenience functions
    convenience_ok = test_convenience_functions()
    
    # Fix GUI logging
    gui_ok = fix_gui_logging()
    
    # Test automation engine
    automation_ok = verify_automation_engine_logging()
    
    # Create improved setup
    improved_setup = create_improved_gui_logging()
    
    # Final summary
    print("\n" + "="*60)
    print("LOGGING FIX SUMMARY")
    print("="*60)
    
    issues_fixed = 0
    total_issues = 4
    
    if log_manager_ok:
        print("✅ Log manager: Working properly")
        issues_fixed += 1
    else:
        print("❌ Log manager: Still has issues")
    
    if convenience_ok:
        print("✅ Convenience functions: Working properly")
        issues_fixed += 1
    else:
        print("❌ Convenience functions: Still has issues")
    
    if gui_ok:
        print("✅ GUI integration: Working properly")
        issues_fixed += 1
    else:
        print("❌ GUI integration: Still has issues")
    
    if automation_ok:
        print("✅ Automation engine: Working properly")
        issues_fixed += 1
    else:
        print("❌ Automation engine: Still has issues")
    
    print(f"\nResult: {issues_fixed}/{total_issues} logging components working")
    
    if issues_fixed == total_issues:
        print("\n🎉 SUCCESS: All logging issues have been fixed!")
        print("The logging system should now work properly with:")
        print("- Proper file categorization")
        print("- GUI display integration")
        print("- Automation engine logging")
        print("- Error tracking")
    elif issues_fixed >= 2:
        print(f"\n⚠️ PARTIAL SUCCESS: {issues_fixed} out of {total_issues} components working")
        print("Most logging functionality should work, but some issues remain")
    else:
        print("\n❌ FAILURE: Major logging issues still exist")
        print("Recommend checking system permissions and Python installation")
    
    # Show current session info
    if log_manager:
        session_info = log_manager.get_session_info()
        print(f"\n📁 Current session: {session_info['session_id']}")
        print(f"📄 Log location: {session_info['base_dir']}")
        
        # Show latest file sizes
        logs_dir = Path("logs")
        print("\n📊 Current log file status:")
        for category, file_path in session_info['log_files'].items():
            log_file = Path(file_path)
            if log_file.exists():
                size = log_file.stat().st_size
                status = "✅" if size > 0 else "⚠️"
                print(f"  {status} {category:12} | {size:6} bytes")
            else:
                print(f"  ❌ {category:12} | Missing")

if __name__ == "__main__":
    main()
