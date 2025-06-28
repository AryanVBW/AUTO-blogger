#!/usr/bin/env python3
"""
Simple logging test to debug AUTO Blogger logging issues
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_logging():
    """Test basic logging functionality"""
    print("Testing basic logging...")
    
    try:
        from log_manager import initialize_logging, get_log_manager
        
        # Initialize logging
        print("Initializing log manager...")
        log_manager = initialize_logging()
        
        # Get session info
        session_info = log_manager.get_session_info()
        print(f"Session ID: {session_info['session_id']}")
        print(f"Log directory: {session_info['base_dir']}")
        
        # Test different loggers
        print("Testing different log categories...")
        
        # Main logger
        main_logger = log_manager.get_logger('main')
        main_logger.info("🔵 Main logger test message")
        print("Main logger tested")
        
        # Automation logger
        automation_logger = log_manager.get_logger('automation')
        automation_logger.info("🤖 Automation logger test message")
        print("Automation logger tested")
        
        # Debug logger
        debug_logger = log_manager.get_logger('debug')
        debug_logger.debug("🔧 Debug logger test message")
        print("Debug logger tested")
        
        # Error logger
        error_logger = log_manager.get_logger('errors')
        error_logger.error("❌ Error logger test message")
        print("Error logger tested")
        
        # API logger
        api_logger = log_manager.get_logger('api')
        api_logger.info("🌐 API logger test message")
        print("API logger tested")
        
        # Security logger
        security_logger = log_manager.get_logger('security')
        security_logger.warning("🔒 Security logger test message")
        print("Security logger tested")
        
        # Check if files were created and have content
        logs_dir = Path("logs")
        session_files = {}
        
        for category in ['main', 'automation', 'debug', 'errors', 'api', 'security']:
            file_pattern = f"{session_info['session_id']}_{category}.log"
            log_file = logs_dir / file_pattern
            
            if log_file.exists():
                size = log_file.stat().st_size
                content = log_file.read_text() if size > 0 else ""
                lines = len(content.strip().split('\n')) if content.strip() else 0
                session_files[category] = {
                    'file': str(log_file),
                    'size': size,
                    'lines': lines,
                    'exists': True
                }
            else:
                session_files[category] = {
                    'file': str(log_file),
                    'size': 0,
                    'lines': 0,
                    'exists': False
                }
        
        print("\n" + "="*50)
        print("LOG FILE STATUS")
        print("="*50)
        
        working_count = 0
        for category, info in session_files.items():
            status = "✅" if info['exists'] and info['size'] > 0 else "❌"
            print(f"{status} {category:12} | {info['size']:6} bytes | {info['lines']:3} lines | {info['file']}")
            if info['exists'] and info['size'] > 0:
                working_count += 1
        
        print(f"\nResult: {working_count}/{len(session_files)} log categories are working")
        
        if working_count == 0:
            print("\n❌ CRITICAL: No logging is working!")
            print("Possible issues:")
            print("- File permissions in logs directory")
            print("- Log handler configuration")
            print("- Logger setup problems")
        elif working_count < len(session_files):
            print(f"\n⚠️ WARNING: Only {working_count} out of {len(session_files)} log categories are working")
        else:
            print("\n✅ SUCCESS: All logging categories are working!")
        
        return working_count > 0
        
    except Exception as e:
        print(f"❌ Error testing logging: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_logging_integration():
    """Test if GUI logging would work"""
    print("\n" + "="*50)
    print("TESTING GUI LOGGING INTEGRATION")
    print("="*50)
    
    try:
        # Test if we can import GUI components
        import tkinter as tk
        print("✅ Tkinter available")
        
        # Test log manager integration
        from log_manager import get_log_manager
        log_manager = get_log_manager()
        
        # Create a test queue like the GUI would
        import queue
        test_queue = queue.Queue()
        
        # Create a test handler like the GUI would
        class TestQueueHandler(logging.Handler):
            def __init__(self, log_queue):
                super().__init__()
                self.log_queue = log_queue
                
            def emit(self, record):
                try:
                    msg = self.format(record)
                    self.log_queue.put(msg)
                except Exception:
                    pass
        
        # Setup test logger
        test_logger = logging.getLogger('GUITest')
        test_logger.setLevel(logging.DEBUG)
        
        # Clear handlers
        for handler in test_logger.handlers[:]:
            test_logger.removeHandler(handler)
        
        # Add queue handler
        queue_handler = TestQueueHandler(test_queue)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        queue_handler.setFormatter(formatter)
        test_logger.addHandler(queue_handler)
        
        # Test logging
        test_logger.info("GUI test message 1")
        test_logger.debug("GUI test message 2")
        test_logger.warning("GUI test message 3")
        
        # Check queue
        messages = []
        try:
            while True:
                msg = test_queue.get_nowait()
                messages.append(msg)
        except queue.Empty:
            pass
        
        print(f"✅ Queue handler captured {len(messages)} messages")
        
        if messages:
            print("Sample messages:")
            for i, msg in enumerate(messages[:3]):
                print(f"  {i+1}. {msg}")
        
        return len(messages) > 0
        
    except Exception as e:
        print(f"❌ GUI logging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_permissions():
    """Fix common permission issues"""
    print("\n" + "="*50)
    print("CHECKING AND FIXING PERMISSIONS")
    print("="*50)
    
    try:
        logs_dir = Path("logs")
        
        # Check if logs directory exists
        if not logs_dir.exists():
            logs_dir.mkdir(exist_ok=True)
            print("✅ Created logs directory")
        
        # Check if directory is writable
        test_file = logs_dir / "test_write.tmp"
        try:
            test_file.write_text("test")
            test_file.unlink()
            print("✅ Logs directory is writable")
        except Exception as e:
            print(f"❌ Logs directory is not writable: {e}")
            return False
        
        # Check existing log files permissions
        log_files = list(logs_dir.glob("session_*.log"))
        if log_files:
            print(f"📄 Found {len(log_files)} existing log files")
            
            for log_file in log_files[-3:]:  # Check last 3 files
                try:
                    # Try to append to file
                    with open(log_file, 'a') as f:
                        f.write("")  # Just test writing
                    print(f"✅ {log_file.name} is writable")
                except Exception as e:
                    print(f"❌ {log_file.name} is not writable: {e}")
        else:
            print("📄 No existing log files found")
        
        return True
        
    except Exception as e:
        print(f"❌ Permission check failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 AUTO Blogger Logging Debug Test")
    print("="*50)
    
    # Fix permissions first
    permissions_ok = fix_permissions()
    if not permissions_ok:
        print("\n❌ CRITICAL: Permission issues detected!")
        return
    
    # Test basic logging
    basic_logging_ok = test_basic_logging()
    
    # Test GUI integration
    gui_logging_ok = test_gui_logging_integration()
    
    # Summary
    print("\n" + "="*50)
    print("FINAL SUMMARY")
    print("="*50)
    
    if basic_logging_ok and gui_logging_ok:
        print("✅ All logging tests passed!")
        print("The logging system should be working properly.")
    elif basic_logging_ok:
        print("⚠️ Basic logging works, but GUI integration may have issues")
    elif gui_logging_ok:
        print("⚠️ GUI logging works, but session logging may have issues")
    else:
        print("❌ Major logging issues detected!")
        print("\nRecommended actions:")
        print("1. Check file permissions in logs directory")
        print("2. Verify log_manager.py is working correctly")
        print("3. Check for conflicting logging configurations")
    
    print(f"\n📁 Check logs directory: {Path('logs').absolute()}")

if __name__ == "__main__":
    main()
