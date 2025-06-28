#!/usr/bin/env python3
"""
Simple Logging Test for AUTO Blogger - FIXED VERSION

This script directly tests logging and shows immediate results.
"""

import os
import sys
import logging
import time
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_direct_logging():
    """Test logging directly without complex routing"""
    print("🧪 Testing Direct Logging System")
    print("="*50)
    
    try:
        # Import the log manager
        from log_manager import initialize_logging, get_log_manager
        
        # Initialize a new session
        log_manager = initialize_logging()
        session_info = log_manager.get_session_info()
        
        print(f"Session: {session_info['session_id']}")
        print(f"Logs Dir: {session_info['base_dir']}")
        
        # Test each logger directly with specific messages
        print("\nTesting individual loggers:")
        
        # 1. Main Logger
        main_logger = log_manager.get_logger('main')
        main_logger.info("🔵 MAIN: This is a main log message")
        print("✅ Main logger tested")
        
        # 2. Automation Logger  
        automation_logger = log_manager.get_logger('automation')
        automation_logger.info("🤖 AUTOMATION: Blog automation process started")
        automation_logger.info("📄 AUTOMATION: Processing article from TBR Football")
        automation_logger.info("✅ AUTOMATION: Article published successfully")
        print("✅ Automation logger tested")
        
        # 3. Debug Logger
        debug_logger = log_manager.get_logger('debug')
        debug_logger.debug("🔧 DEBUG: Debug message for troubleshooting")
        debug_logger.debug("🔍 DEBUG: Checking website scraping functionality")
        print("✅ Debug logger tested")
        
        # 4. API Logger
        api_logger = log_manager.get_logger('api')
        api_logger.info("🌐 API: Connecting to WordPress REST API")
        api_logger.info("📤 API: POST request to /wp/v2/posts")
        api_logger.info("📥 API: Response received - Status 201")
        print("✅ API logger tested")
        
        # 5. Error Logger
        error_logger = log_manager.get_logger('errors')
        error_logger.error("❌ ERROR: Test error message (this is just a test)")
        error_logger.error("⚠️ ERROR: Failed to connect to source website")
        print("✅ Error logger tested")
        
        # 6. Security Logger
        security_logger = log_manager.get_logger('security')
        security_logger.warning("🔒 SECURITY: Authentication attempt")
        security_logger.warning("🔐 SECURITY: Login credentials verified")
        print("✅ Security logger tested")
        
        # Force flush all handlers
        print("\nFlushing log handlers...")
        for category in ['main', 'automation', 'debug', 'api', 'errors', 'security']:
            logger = log_manager.get_logger(category)
            for handler in logger.handlers:
                if hasattr(handler, 'flush'):
                    handler.flush()
        
        # Wait for writes to complete
        time.sleep(1)
        
        # Check results
        print("\n� Checking Log File Results:")
        print("="*50)
        
        logs_dir = Path("logs")
        total_working = 0
        total_categories = 6
        
        for category in ['main', 'automation', 'debug', 'api', 'errors', 'security']:
            log_file = logs_dir / f"{session_info['session_id']}_{category}.log"
            
            if log_file.exists():
                content = log_file.read_text()
                size = log_file.stat().st_size
                lines = len([l for l in content.split('\n') if l.strip()]) if content.strip() else 0
                
                if size > 0 and lines > 0:
                    print(f"✅ {category:12} | {size:6} bytes | {lines:2} lines | WORKING")
                    total_working += 1
                else:
                    print(f"⚠️ {category:12} | {size:6} bytes | {lines:2} lines | EMPTY")
                    
            else:
                print(f"❌ {category:12} | File not found")
        
        print(f"\nResult: {total_working}/{total_categories} categories working")
        
        if total_working == total_categories:
            print("🎉 SUCCESS: All logging categories are working!")
        elif total_working > 0:
            print(f"⚠️ PARTIAL: {total_working} categories working, {total_categories-total_working} need fixing")
        else:
            print("❌ FAILURE: No logging categories are working")
        
        # Show sample content from working logs
        if total_working > 0:
            print("\n📄 Sample Log Content:")
            for category in ['main', 'automation', 'debug']:
                log_file = logs_dir / f"{session_info['session_id']}_{category}.log"
                if log_file.exists() and log_file.stat().st_size > 0:
                    content = log_file.read_text().strip()
                    lines = content.split('\n')
                    print(f"\n{category.upper()} LOG:")
                    for line in lines[-2:]:  # Show last 2 lines
                        print(f"  {line}")
        
        return total_working > 0
        
    except Exception as e:
        print(f"❌ Error in logging test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 AUTO Blogger Logging Debug - FIXED VERSION")
    print("Current time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    # Test direct logging
    direct_ok = test_direct_logging()
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL TEST RESULTS")
    print("="*60)
    
    if direct_ok:
        print("✅ SUCCESS: Logging system is working!")
        print("The logs should now be visible in each category.")
    else:
        print("❌ CRITICAL: Logging system is still not working properly!")
    
    print(f"\n� Check logs directory: {Path('logs').absolute()}")

if __name__ == "__main__":
    main()
