#!/usr/bin/env python3
"""
Debug script to test old AIOSEO plugin SEO metadata handling
"""

import json
import sys
import os
import logging
from unittest.mock import Mock, patch

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automation_engine import BlogAutomationEngine

def test_old_aioseo_seo_metadata():
    """Test the old AIOSEO plugin SEO metadata creation"""
    print("🔍 Testing old AIOSEO plugin SEO metadata handling...")
    
    # Create engine with old plugin config
    config = {
        'seo_plugin_version': 'old',
        'wp_base_url': 'https://test.com/wp-json/wp/v2',
        'wp_username': 'test',
        'wp_password': 'test',
        'timeout': 10
    }
    
    # Create a simple logger
    logger = logging.getLogger('test')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(handler)
    
    engine = BlogAutomationEngine(config, logger)
    
    # Mock article data
    article_data = {
        'title': 'Test Article Title',
        'content': 'Test article content',
        'category': 'Test Category',
        'tags': ['tag1', 'tag2'],
        'seo_title': 'Test SEO Title',
        'meta_description': 'Test SEO Description',
        'focus_keyphrase': 'test keyword',
        'additional_keyphrases': ['keyword1', 'keyword2']
    }
    
    # Mock responses for API calls
    mock_responses = [
        # Category creation
        Mock(status_code=201, json=lambda: {'id': 1}),
        # Tag creation 1
        Mock(status_code=201, json=lambda: {'id': 1}),
        # Tag creation 2
        Mock(status_code=201, json=lambda: {'id': 2}),
        # Post creation
        Mock(status_code=201, json=lambda: {'id': 123}),
        # SEO metadata update (old plugin)
        Mock(status_code=200, json=lambda: {'id': 123})
    ]
    
    with patch('requests.post') as mock_post:
        mock_post.side_effect = mock_responses
        
        try:
            # Call the post creation method
            post_id, post_url = engine.post_to_wordpress_with_seo(
                article_data['title'],
                article_data['content'],
                [article_data['category']],
                article_data['tags'],
                seo_title=article_data['seo_title'],
                meta_description=article_data['meta_description'],
                focus_keyphrase=article_data['focus_keyphrase'],
                additional_keyphrases=article_data['additional_keyphrases']
            )
            
            print(f"✅ Post created with ID: {post_id}")
            
            # Check all API calls made
            print(f"\n📊 Total API calls made: {len(mock_post.call_args_list)}")
            
            # Look for SEO update call (should be the last call)
            if len(mock_post.call_args_list) >= 2:
                # Check the last call for SEO update
                seo_call = mock_post.call_args_list[-1]  # Last call
                seo_payload = seo_call[1]['json']  # Get the JSON payload
                
                print("\n🔍 SEO Update Call Details:")
                print(f"URL: {seo_call[0][0]}")
                print(f"Payload: {json.dumps(seo_payload, indent=2)}")
                
                # Verify old plugin structure
                if 'meta' in seo_payload:
                    meta = seo_payload['meta']
                    print("\n✅ Old plugin SEO structure detected:")
                    
                    if '_aioseop_title' in meta:
                        print(f"  📝 SEO Title: {meta['_aioseop_title']}")
                    else:
                        print("  ❌ SEO Title missing!")
                        
                    if '_aioseop_description' in meta:
                        print(f"  📄 SEO Description: {meta['_aioseop_description']}")
                    else:
                        print("  ❌ SEO Description missing!")
                        
                    if '_aioseop_keywords' in meta:
                        print(f"  🏷️ SEO Keywords: {meta['_aioseop_keywords']}")
                    else:
                        print("  ❌ SEO Keywords missing!")
                        
                    return True
                else:
                    print("❌ No 'meta' field found in SEO payload!")
                    return False
            else:
                print(f"❌ Expected at least 2 API calls, got {len(mock_post.call_args_list)}")
                return False
                
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False

if __name__ == "__main__":
    success = test_old_aioseo_seo_metadata()
    if success:
        print("\n🎉 Old AIOSEO plugin SEO metadata test PASSED")
    else:
        print("\n💥 Old AIOSEO plugin SEO metadata test FAILED")
        print("\n📋 Troubleshooting steps:")
        print("1. Verify seo_plugin_version is set to 'old' in config")
        print("2. Check WordPress REST API permissions")
        print("3. Verify AIOSEO plugin version is 2.7.1")
        print("4. Check WordPress error logs")
        print("5. Test with a different user account")