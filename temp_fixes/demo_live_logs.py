#!/usr/bin/env python3
"""
Live Log Demonstration Script
Generates continuous log entries to demonstrate real-time monitoring in the GUI
"""

import time
import random
from unified_log_manager import UnifiedLogManager

def demo_live_logging():
    """Generate continuous live log entries for demonstration"""
    print("🚀 Starting Live Log Demonstration...")
    print("📱 Open the GUI application to see real-time log updates!")
    print("⏹️  Press Ctrl+C to stop the demonstration")
    
    # Initialize log manager
    log_manager = UnifiedLogManager()
    
    # Demo scenarios
    scenarios = [
        # Blog automation scenarios
        ("log_automation_event", "Starting blog post generation", "INIT"),
        ("log_content_event", "Fetching latest football news", "SCRAPE"),
        ("log_api_event", "Requesting OpenAI content generation", "POST /v1/chat/completions"),
        ("log_content_event", "Processing article content", "PARSE"),
        ("log_ui_event", "Updating blog post preview", "RENDER"),
        ("log_automation_event", "Publishing blog post", "PUBLISH"),
        
        # WebDriver scenarios
        ("log_webdriver_event", "Initializing Chrome WebDriver", "INIT"),
        ("log_webdriver_event", "Navigating to target website", "NAVIGATE"),
        ("log_webdriver_event", "Extracting page content", "SCRAPE"),
        ("log_webdriver_event", "Taking screenshot", "CAPTURE"),
        
        # Security and API scenarios
        ("log_security_event", "Validating API credentials", "AUTH"),
        ("log_api_event", "Fetching Getty Images", "GET /v3/search/images"),
        ("log_security_event", "Rate limiting check", "THROTTLE"),
        
        # System events
        ("log_info", "System health check completed", "SYSTEM"),
        ("log_warning", "High memory usage detected", "SYSTEM"),
        ("log_error", "Network timeout occurred", "NETWORK"),
        ("log_debug", "Cache cleanup initiated", "SYSTEM"),
    ]
    
    try:
        counter = 1
        while True:
            # Select random scenario
            method, message, category = random.choice(scenarios)
            
            # Add counter to make each message unique
            timestamped_message = f"[{counter:03d}] {message}"
            
            print(f"📝 Generating: {method} - {timestamped_message}")
            
            # Call the appropriate logging method
            if method == "log_info":
                log_manager.log_info(timestamped_message, category)
            elif method == "log_automation_event":
                log_manager.log_automation_event(timestamped_message, category)
            elif method == "log_webdriver_event":
                log_manager.log_webdriver_event(timestamped_message, category)
            elif method == "log_api_event":
                log_manager.log_api_event(timestamped_message, category)
            elif method == "log_security_event":
                log_manager.log_security_event(timestamped_message, category)
            elif method == "log_content_event":
                log_manager.log_content_event(timestamped_message, category)
            elif method == "log_ui_event":
                log_manager.log_ui_event(timestamped_message, category)
            elif method == "log_error":
                log_manager.log_error(timestamped_message, category)
            elif method == "log_warning":
                log_manager.log_warning(timestamped_message, category)
            elif method == "log_debug":
                log_manager.log_debug(timestamped_message, category)
            
            counter += 1
            
            # Random delay between 1-4 seconds for realistic timing
            delay = random.uniform(1, 4)
            time.sleep(delay)
            
    except KeyboardInterrupt:
        print("\n🛑 Live log demonstration stopped by user")
        log_manager.log_info("Live log demonstration ended", "SYSTEM")
        print("✅ Demonstration completed!")

if __name__ == "__main__":
    demo_live_logging()