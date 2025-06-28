#!/usr/bin/env python3
"""
Test script for the Enhanced Log Manager System
Demonstrates the timestamped session-based logging functionality

Copyright © 2025 AryanVBW
GitHub: https://github.com/AryanVBW
"""

import time
from log_manager import initialize_logging, finalize_logging, get_log_manager

def test_logging_system():
    """Test the enhanced logging system"""
    print("🧪 Testing Enhanced AUTO Blogger Logging System")
    print("=" * 60)
    
    # Initialize logging
    log_manager = initialize_logging()
    session_info = log_manager.get_session_info()
    
    print(f"✅ Session initialized: {session_info['session_id']}")
    print(f"📁 Log directory: {session_info['base_dir']}")
    print(f"📄 Log files created: {len(session_info['log_files'])} categories")
    print()
    
    # Test different log categories
    print("🔬 Testing different log categories...")
    
    # Main logs
    main_logger = log_manager.get_logger('main')
    main_logger.info("🚀 AUTO Blogger application started")
    main_logger.info("📋 Configuration loaded successfully")
    main_logger.warning("⚠️ Some optional features are disabled")
    
    # Automation logs
    log_manager.log_automation_event('info', "Blog automation session started", 
                                   articles=5, source="test-site.com")
    log_manager.log_automation_event('info', "Article processing completed", 
                                   title="Test Article", status="success")
    log_manager.log_automation_event('warning', "Article skipped due to duplicate content")
    
    # API logs
    log_manager.log_api_event('GET', 'https://test.com/wp-json/wp/v2/posts', 
                             status_code=200, response_time=0.5)
    log_manager.log_api_event('POST', 'https://test.com/wp-json/wp/v2/posts', 
                             status_code=201, response_time=1.2)
    log_manager.log_api_event('GET', 'https://api.openai.com/v1/images/generations',
                             error="Rate limit exceeded")
    
    # Security logs
    log_manager.log_security_event('login_attempt', 'User authentication successful')
    log_manager.log_security_event('credential_validation', 'WordPress credentials verified')
    log_manager.log_security_event('api_key_usage', 'OpenAI API key utilized for image generation', 'info')
    
    # Error logs
    error_logger = log_manager.get_logger('errors')
    error_logger.error("❌ Failed to connect to external service")
    error_logger.error("❌ Image generation failed: Invalid prompt")
    
    # Debug logs  
    debug_logger = log_manager.get_logger('debug')
    debug_logger.debug("🔧 Selenium WebDriver initialized")
    debug_logger.debug("🔧 Article content extracted: 1,250 words")
    debug_logger.debug("🔧 Internal links injected: 3 links")
    
    print("✅ Test logs generated successfully!")
    print()
    
    # Simulate some processing time
    print("⏳ Simulating automation process...")
    for i in range(3):
        time.sleep(1)
        log_manager.log_automation_event('info', f"Processing article {i+1}/3", 
                                       progress=f"{((i+1)/3)*100:.0f}%")
    
    # Show session information
    session_info = log_manager.get_session_info()
    print("📊 Current Session Information:")
    print(f"   Session ID: {session_info['session_id']}")
    print(f"   Base Directory: {session_info['base_dir']}")
    print("   Log Files:")
    for category, filepath in session_info['log_files'].items():
        print(f"     • {category.title()}: {filepath}")
    print()
    
    # List previous sessions
    sessions = log_manager.list_previous_sessions()
    print(f"📋 Found {len(sessions)} total sessions (including current)")
    if len(sessions) > 1:
        print("   Previous sessions:")
        for session in sessions[1:6]:  # Show last 5 previous sessions
            status = session.get('status', 'unknown')
            start_time = session.get('start_time', 'unknown')
            print(f"     • {session['session_id']} - {status} - {start_time}")
    print()
    
    # Test log file contents
    print("📄 Sample log file contents:")
    main_log_file = session_info['log_files']['main']
    try:
        with open(main_log_file, 'r') as f:
            lines = f.readlines()
            print(f"   Main log has {len(lines)} lines")
            if lines:
                print("   Last few entries:")
                for line in lines[-3:]:
                    print(f"     {line.strip()}")
    except Exception as e:
        print(f"   Error reading log file: {e}")
    print()
    
    # Finalize session
    print("🏁 Finalizing session...")
    finalize_logging()
    
    # Check updated session info
    sessions = log_manager.list_previous_sessions()
    current_session = sessions[0] if sessions else {}
    if current_session:
        duration = current_session.get('duration_seconds', 0)
        file_sizes = current_session.get('file_sizes', {})
        print(f"✅ Session finalized: {current_session['session_id']}")
        print(f"⏱️ Duration: {duration:.1f} seconds")
        print("📊 File Sizes:")
        for category, size in file_sizes.items():
            print(f"   • {category.title()}: {size:,} bytes")
    
    print()
    print("🎉 Logging system test completed successfully!")
    print(f"📁 Check the logs directory: {session_info['base_dir']}")
    print("📋 Each session creates separate timestamped files for easy tracking")

if __name__ == "__main__":
    test_logging_system()
