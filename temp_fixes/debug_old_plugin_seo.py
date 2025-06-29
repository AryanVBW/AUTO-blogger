#!/usr/bin/env python3
"""
Debug script to test old AIOSEO plugin SEO metadata in real WordPress scenario.
This script will help identify why SEO metadata might not be added.
"""

import sys
import os
import json
import logging
from unittest.mock import patch, MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automation_engine import BlogAutomationEngine

def debug_old_plugin_seo():
    """
    Debug the old plugin SEO metadata handling
    """
    print("🔍 Debugging Old AIOSEO Plugin SEO Metadata")
    print("=" * 60)
    
    # Create logger
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger = logging.getLogger('debug_old_plugin')
    
    # Configuration for old plugin
    config = {
        'seo_plugin_version': 'old',  # This should trigger old plugin logic
        'wp_base_url': 'https://test.com/wp-json/wp/v2',
        'wp_username': 'test_user',
        'wp_password': 'test_pass'
    }
    
    # Create engine
    engine = BlogAutomationEngine(config, logger)
    
    print(f"📋 Configuration:")
    print(f"   SEO Plugin Version: {config.get('seo_plugin_version')}")
    print(f"   WordPress URL: {config.get('wp_base_url')}")
    
    # Test SEO data that should be processed
    test_seo_data = {
        'seo_title': 'Test SEO Title for Old Plugin',
        'meta_description': 'This is a test meta description for old AIOSEO plugin.',
        'focus_keyphrase': 'old aioseo plugin',
        'additional_keyphrases': ['wordpress seo', 'plugin compatibility']
    }
    
    print(f"\n📝 Input SEO Data:")
    for key, value in test_seo_data.items():
        print(f"   {key}: {value}")
    
    # Mock the WordPress API calls to capture what's being sent
    with patch('requests.post') as mock_post, patch('requests.get') as mock_get:
        # Mock responses for categories, tags, post creation
        mock_get.return_value.json.return_value = []  # No existing categories/tags
        mock_get.return_value.raise_for_status.return_value = None
        
        # Mock category and tag creation
        mock_cat_response = MagicMock()
        mock_cat_response.json.return_value = {'id': 1}
        mock_cat_response.raise_for_status.return_value = None
        
        mock_tag_response = MagicMock()
        mock_tag_response.json.return_value = {'id': 1}
        mock_tag_response.raise_for_status.return_value = None
        
        # Mock post creation
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {'id': 123}
        mock_post_response.raise_for_status.return_value = None
        
        # Mock SEO update
        mock_seo_response = MagicMock()
        mock_seo_response.raise_for_status.return_value = None
        mock_seo_response.status_code = 200
        mock_seo_response.text = 'Success'
        
        # Set up mock responses
        mock_post.side_effect = [
            mock_cat_response,  # Category creation
            mock_tag_response,  # Tag creation  
            mock_tag_response,  # Second tag creation
            mock_post_response,  # Post creation
            mock_seo_response   # SEO update
        ]
        
        print(f"\n🚀 Testing WordPress posting with old plugin SEO...")
        
        try:
            # Call the method
            post_id, title = engine.post_to_wordpress_with_seo(
                title='Debug Test Article',
                content='<p>This is test content for debugging old plugin SEO.</p>',
                categories=['Test Category'],
                tags=['debug', 'old-plugin'],
                **test_seo_data
            )
            
            print(f"\n✅ Post created successfully:")
            print(f"   Post ID: {post_id}")
            print(f"   Title: {title}")
            
            # Analyze the API calls made
            print(f"\n🔍 API Calls Analysis:")
            print(f"   Total POST calls made: {mock_post.call_count}")
            
            if mock_post.call_count >= 5:
                # Check the SEO update call (should be the 5th call)
                seo_call = mock_post.call_args_list[4]
                seo_url = seo_call[0][0]
                seo_payload = seo_call[1]['json']
                
                print(f"\n📡 SEO Update Call Details:")
                print(f"   URL: {seo_url}")
                print(f"   Payload: {json.dumps(seo_payload, indent=2)}")
                
                # Verify old plugin structure
                if 'meta' in seo_payload:
                    print(f"\n✅ Old Plugin SEO Structure Verified:")
                    meta_data = seo_payload['meta']
                    
                    for key, value in meta_data.items():
                        print(f"   {key}: {value}")
                    
                    # Check required fields
                    required_fields = ['_aioseop_title', '_aioseop_description', '_aioseop_keywords']
                    missing_fields = [field for field in required_fields if field not in meta_data]
                    
                    if missing_fields:
                        print(f"\n❌ Missing SEO fields: {missing_fields}")
                        return False
                    else:
                        print(f"\n✅ All required SEO fields present!")
                        return True
                else:
                    print(f"\n❌ ERROR: 'meta' field missing from SEO payload!")
                    print(f"   Expected old plugin format with 'meta' wrapper")
                    return False
            else:
                print(f"\n❌ ERROR: Expected 5 API calls, got {mock_post.call_count}")
                return False
                
        except Exception as e:
            print(f"\n❌ ERROR during testing: {e}")
            import traceback
            traceback.print_exc()
            return False

def check_configuration_issues():
    """
    Check for common configuration issues that might prevent SEO metadata
    """
    print(f"\n🔧 Checking Configuration Issues")
    print("=" * 40)
    
    # Check arsenalcore.com config
    config_path = '/Users/vivek-w/Desktop/AUTO-blogger/configs/arsenalcore_com/default.json'
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"📋 ArsenalCore.com Configuration:")
        print(f"   SEO Plugin Version: {config.get('seo_plugin_version', 'NOT SET')}")
        print(f"   WordPress URL: {config.get('wp_base_url', 'NOT SET')}")
        print(f"   WordPress Username: {config.get('wp_username', 'NOT SET')}")
        print(f"   WordPress Password: {'SET' if config.get('wp_password') else 'NOT SET'}")
        
        if config.get('seo_plugin_version') == 'old':
            print(f"\n✅ Configuration correctly set for old plugin")
        else:
            print(f"\n❌ Configuration issue: seo_plugin_version should be 'old'")
            
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")

if __name__ == "__main__":
    print("🚀 Starting Old Plugin SEO Debug Session")
    print("=" * 60)
    
    # Check configuration
    check_configuration_issues()
    
    # Debug SEO metadata handling
    success = debug_old_plugin_seo()
    
    print(f"\n" + "=" * 60)
    if success:
        print("✅ DEBUG COMPLETED: Old plugin SEO metadata handling is working correctly!")
        print("\n📋 Summary:")
        print("   - Old plugin format uses 'meta' wrapper")
        print("   - SEO title stored as '_aioseop_title'")
        print("   - Meta description stored as '_aioseop_description'")
        print("   - Keywords stored as '_aioseop_keywords'")
        print("\n💡 If SEO data is still not appearing in WordPress:")
        print("   1. Check WordPress plugin version (should be v2.7.1)")
        print("   2. Verify plugin is active and configured")
        print("   3. Check WordPress user permissions")
        print("   4. Review WordPress error logs")
    else:
        print("❌ DEBUG FAILED: Issues found with old plugin SEO metadata handling")
        print("\n🔧 Possible solutions:")
        print("   1. Check seo_plugin_version in configuration")
        print("   2. Verify WordPress API credentials")
        print("   3. Check WordPress plugin compatibility")