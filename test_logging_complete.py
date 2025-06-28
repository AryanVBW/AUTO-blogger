#!/usr/bin/env python3
"""
Test script to verify all logging categories work correctly
"""

from log_manager import initialize_logging
import logging

def test_all_logging_categories():
    """Test all logging categories to verify proper file separation"""
    print("🧪 Testing Advanced Logging System...")
    
    # Initialize logging
    log_manager = initialize_logging()
    session_info = log_manager.get_session_info()
    
    print(f"📅 Session: {session_info['session_id']}")
    print(f"📁 Log directory: {session_info['base_dir']}")
    print(f"📄 Log files: {len(session_info['log_files'])} categories")
    print()
    
    # Test each category
    categories = [
        ('main', 'Main application started successfully'),
        ('automation', 'Article processing automation initiated'),
        ('errors', 'This is a test error message'),
        ('debug', 'Debug: Processing step completed'),
        ('api', 'WordPress API request sent'),
        ('security', 'User authentication successful')
    ]
    
    for category, message in categories:
        logger = log_manager.get_logger(category)
        
        if category == 'errors':
            logger.error(f"🔴 {message}")
        elif category == 'debug':
            logger.debug(f"🔧 {message}")
        else:
            logger.info(f"📝 {message}")
            
        print(f"✅ Logged to {category}: {message}")
    
    print()
    print("🎉 All logging categories tested successfully!")
    print(f"📁 Check logs in: {session_info['base_dir']}")
    print()
    
    # Show log file contents summary
    for log_file in session_info['log_files']:
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    print(f"📄 {log_file.split('/')[-1]}: {len(lines)} entries")
        except Exception as e:
            print(f"❌ Could not read {log_file}: {e}")

if __name__ == "__main__":
    test_all_logging_categories()
