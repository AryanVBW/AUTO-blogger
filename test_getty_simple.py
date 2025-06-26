#!/usr/bin/env python3
"""
Simple test for Getty Images functionality with enhanced logging
"""

import sys
import os
import logging

# Add the current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_getty_images_with_logging():
    """Test Getty Images with detailed logging"""
    
    # Setup detailed logging
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    try:
        from automation_engine import BlogAutomationEngine
        
        print("🚀 Starting Getty Images Test...")
        print("=" * 50)
        
        # Create automation engine with minimal config
        config = {
            'source_url': 'https://example.com',
            'article_selector': 'a',
            'wp_base_url': '',
            'wp_username': '',
            'wp_password': '',
            'gemini_api_key': ''
        }
        
        engine = BlogAutomationEngine(config)
        
        # Test the Getty Images functionality
        test_title = "Manchester United vs Liverpool Premier League Match"
        test_keywords = ["Manchester United", "Premier League", "football"]
        
        test_content = """
        <h2>Match Report</h2>
        <p>This is the first paragraph of our football match report.</p>
        <p>Manchester United played against Liverpool in an exciting Premier League match.</p>
        <p>The game was filled with action and great performances from both teams.</p>
        """
        
        print(f"📝 Test Content Length: {len(test_content)} characters")
        print(f"🏷️ Test Title: {test_title}")
        print(f"🔑 Test Keywords: {test_keywords}")
        print("\n" + "=" * 50)
        
        # Test adding Getty images to content
        print("🖼️ Testing Getty Images Integration...")
        modified_content = engine.add_getty_image_to_content(
            test_content, 
            test_title, 
            test_keywords
        )
        
        print("\n" + "=" * 50)
        print("📊 RESULTS:")
        print(f"• Original content length: {len(test_content)}")
        print(f"• Modified content length: {len(modified_content)}")
        print(f"• Content changed: {'YES' if modified_content != test_content else 'NO'}")
        
        if modified_content != test_content:
            print("✅ Getty Images functionality appears to be working!")
            
            # Check if Getty embed code is present
            if "embed.gettyimages.com" in modified_content or "Editorial Image" in modified_content:
                print("✅ Getty embed code found in content!")
            else:
                print("⚠️ No Getty embed code found, but content was modified")
                
            print("\n🔍 Content Preview (first 200 chars):")
            print(modified_content[:200] + "..." if len(modified_content) > 200 else modified_content)
        else:
            print("❌ Content was not modified - Getty Images may not be working")
        
        print("\n" + "=" * 50)
        print("✅ Test completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure automation_engine.py is in the same directory")
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")

if __name__ == "__main__":
    test_getty_images_with_logging()
