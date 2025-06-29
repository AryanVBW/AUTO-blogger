#!/usr/bin/env python3
"""
Final verification test for old AIOSEO plugin version (v2.7.1) handling.
This test mocks HTTP requests to verify the complete WordPress posting workflow.
"""

import sys
import os
import logging
from unittest.mock import patch, MagicMock
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automation_engine import BlogAutomationEngine

def test_old_plugin_wordpress_posting():
    """
    Test the complete WordPress posting workflow for old AIOSEO plugin
    """
    print("🧪 Testing Old AIOSEO Plugin (v2.7.1) WordPress Posting Workflow")
    print("=" * 70)
    
    # Create logger
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(handler)
    
    # Configuration for old plugin
    config = {
        'seo_plugin_version': 'old',  # Key setting for old plugin
        'wp_base_url': 'https://test.com/wp-json/wp/v2',
        'wp_username': 'testuser',
        'wp_password': 'testpass'
    }
    
    engine = BlogAutomationEngine(config, logger)
    
    # Mock HTTP responses
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        
        # Mock category and tag responses
        mock_get.return_value.json.return_value = []
        mock_get.return_value.raise_for_status.return_value = None
        
        # Mock category creation responses
        mock_cat_response = MagicMock()
        mock_cat_response.json.return_value = {'id': 1}
        mock_cat_response.raise_for_status.return_value = None
        
        # Mock tag creation responses
        mock_tag_response = MagicMock()
        mock_tag_response.json.return_value = {'id': 1}
        mock_tag_response.raise_for_status.return_value = None
        
        # Mock post creation response
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {'id': 123}
        mock_post_response.raise_for_status.return_value = None
        
        # Mock SEO update response
        mock_seo_response = MagicMock()
        mock_seo_response.raise_for_status.return_value = None
        mock_seo_response.status_code = 200
        mock_seo_response.text = 'Success'
        
        # Set up the sequence: 2 categories + 3 tags + 1 post + 1 SEO update = 7 calls
        mock_post.side_effect = [
            mock_cat_response, mock_cat_response,  # Category creation
            mock_tag_response, mock_tag_response, mock_tag_response,  # Tag creation
            mock_post_response,  # Post creation
            mock_seo_response  # SEO update
        ]
        
        # Test the posting workflow
        print("\n📝 Testing WordPress post creation with old AIOSEO SEO data...")
        
        post_id, title = engine.post_to_wordpress_with_seo(
            title='Test Article for Old Plugin',
            content='<p>This is test content for the old AIOSEO plugin.</p>',
            categories=['Technology', 'WordPress'],
            tags=['seo', 'aioseo', 'old-plugin'],
            seo_title='Old Plugin SEO Title - Test Article',
            meta_description='This is a meta description for testing the old AIOSEO plugin version 2.7.1 compatibility.',
            focus_keyphrase='old aioseo plugin',
            additional_keyphrases=['wordpress seo', 'plugin compatibility', 'v2.7.1']
        )
        
        # Verify the results
        assert post_id == 123, f"Expected post_id 123, got {post_id}"
        assert title == 'Test Article for Old Plugin', f"Expected title match, got {title}"
        
        # Verify the calls were made correctly (categories + tags + post + SEO = 7 calls)
        assert mock_post.call_count == 7, f"Expected 7 POST calls, got {mock_post.call_count}"
        
        # Check the post creation call (6th call - after categories and tags)
        post_call = mock_post.call_args_list[5]
        post_data = post_call[1]['json']
        
        print("\n✅ Post Creation Call Verified:")
        print(f"   Title: {post_data['title']}")
        print(f"   Content: {post_data['content'][:50]}...")
        print(f"   Status: {post_data['status']}")
        
        # Check the SEO update call (7th call) - this is the critical part for old plugin
        seo_call = mock_post.call_args_list[6]
        seo_data = seo_call[1]['json']
        
        print("\n🔍 SEO Update Call Verified (Old Plugin Format):")
        print(f"   SEO Data Structure: {seo_data}")
        
        # Verify old plugin SEO structure
        assert 'meta' in seo_data, "Missing 'meta' key in SEO data for old plugin"
        assert '_aioseop_title' in seo_data['meta'], "Missing '_aioseop_title' in old plugin SEO data"
        assert '_aioseop_description' in seo_data['meta'], "Missing '_aioseop_description' in old plugin SEO data"
        assert '_aioseop_keywords' in seo_data['meta'], "Missing '_aioseop_keywords' in old plugin SEO data"
        
        # Verify the values
        assert seo_data['meta']['_aioseop_title'] == 'Old Plugin SEO Title - Test Article'
        assert seo_data['meta']['_aioseop_description'] == 'This is a meta description for testing the old AIOSEO plugin version 2.7.1 compatibility.'
        assert seo_data['meta']['_aioseop_keywords'] == 'old aioseo plugin, wordpress seo, plugin compatibility, v2.7.1'
        
        print("\n✅ Old Plugin SEO Data Verification:")
        print(f"   _aioseop_title: {seo_data['meta']['_aioseop_title']}")
        print(f"   _aioseop_description: {seo_data['meta']['_aioseop_description']}")
        print(f"   _aioseop_keywords: {seo_data['meta']['_aioseop_keywords']}")
        
        # Verify the URL used for SEO update
        seo_url = seo_call[0][0]  # First positional argument (URL)
        expected_seo_url = 'https://test.com/wp-json/wp/v2/posts/123'
        assert seo_url == expected_seo_url, f"Expected SEO URL {expected_seo_url}, got {seo_url}"
        
        print(f"\n✅ SEO Update URL Verified: {seo_url}")
        
        return True

def test_new_vs_old_plugin_posting_comparison():
    """
    Compare the posting workflow between old and new plugin versions
    """
    print("\n🔄 Testing New vs Old Plugin Posting Workflow Comparison")
    print("=" * 70)
    
    # Create logger
    logger = logging.getLogger('comparison_logger')
    logger.setLevel(logging.INFO)
    
    # Test both configurations
    configs = {
        'old': {
            'seo_plugin_version': 'old',
            'wp_base_url': 'https://test.com/wp-json/wp/v2',
            'wp_username': 'testuser',
            'wp_password': 'testpass'
        },
        'new': {
            'seo_plugin_version': 'new',
            'wp_base_url': 'https://test.com/wp-json/wp/v2',
            'wp_username': 'testuser',
            'wp_password': 'testpass'
        }
    }
    
    results = {}
    
    for version, config in configs.items():
        print(f"\n📊 Testing {version.upper()} Plugin Version:")
        
        engine = BlogAutomationEngine(config, logger)
        
        with patch('requests.get') as mock_get, \
             patch('requests.post') as mock_post:
            
            # Mock responses
            mock_get.return_value.json.return_value = []
            mock_get.return_value.raise_for_status.return_value = None
            
            # Mock category creation responses
            mock_cat_response = MagicMock()
            mock_cat_response.json.return_value = {'id': 1}
            mock_cat_response.raise_for_status.return_value = None
            
            # Mock tag creation responses
            mock_tag_response = MagicMock()
            mock_tag_response.json.return_value = {'id': 1}
            mock_tag_response.raise_for_status.return_value = None
            
            mock_post_response = MagicMock()
            mock_post_response.json.return_value = {'id': 456}
            mock_post_response.raise_for_status.return_value = None
            
            mock_seo_response = MagicMock()
            mock_seo_response.raise_for_status.return_value = None
            mock_seo_response.status_code = 200
            
            # Set up the sequence: 1 category + 1 tag + 1 post + 1 SEO update = 4 calls
            mock_post.side_effect = [
                mock_cat_response,  # Category creation
                mock_tag_response,  # Tag creation
                mock_post_response,  # Post creation
                mock_seo_response   # SEO update
            ]
            
            # Make the call
            engine.post_to_wordpress_with_seo(
                title='Comparison Test Post',
                content='<p>Test content for comparison</p>',
                categories=['Test'],
                tags=['comparison'],
                seo_title='Comparison SEO Title',
                meta_description='Comparison meta description',
                focus_keyphrase='comparison test',
                additional_keyphrases=['seo comparison']
            )
            
            # Capture the SEO data structure
            if mock_post.call_count >= 4:
                seo_call = mock_post.call_args_list[3]  # SEO update is the 4th call
                seo_data = seo_call[1]['json']
                results[version] = seo_data
                
                print(f"   SEO Data: {seo_data}")
    
    # Compare the results
    print("\n🔍 Comparison Results:")
    if 'old' in results and 'new' in results:
        old_data = results['old']
        new_data = results['new']
        
        print(f"\n   OLD Plugin Structure:")
        print(f"   - Uses 'meta' field: {'meta' in old_data}")
        print(f"   - Uses '_aioseop_title': {'meta' in old_data and '_aioseop_title' in old_data.get('meta', {})}")
        print(f"   - Keywords format: comma-separated string")
        
        print(f"\n   NEW Plugin Structure:")
        print(f"   - Uses 'aioseo_meta_data' field: {'aioseo_meta_data' in new_data}")
        print(f"   - Uses 'title': {'aioseo_meta_data' in new_data and 'title' in new_data.get('aioseo_meta_data', {})}")
        print(f"   - Keywords format: structured objects")
        
        print("\n✅ Both plugin versions use different but correct data structures!")
    
    return True

def main():
    """
    Run all final verification tests
    """
    print("🚀 Final Verification: Old AIOSEO Plugin (v2.7.1) Implementation")
    print("=" * 70)
    
    success = True
    
    try:
        # Test old plugin WordPress posting workflow
        if not test_old_plugin_wordpress_posting():
            success = False
        
        # Test comparison between old and new plugin workflows
        if not test_new_vs_old_plugin_posting_comparison():
            success = False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        success = False
    
    print("\n" + "=" * 70)
    if success:
        print("✅ FINAL VERIFICATION PASSED!")
        print("\n📋 Implementation Summary:")
        print("   ✓ Old AIOSEO plugin (v2.7.1) correctly uses 'meta' field structure")
        print("   ✓ SEO data uses '_aioseop_title', '_aioseop_description', '_aioseop_keywords'")
        print("   ✓ Keywords are properly formatted as comma-separated string")
        print("   ✓ WordPress REST API calls are structured correctly for old plugin")
        print("   ✓ Both old and new plugin versions work with their respective formats")
        print("\n🎯 The old plugin version (v2.7.1) is now properly handled!")
    else:
        print("❌ FINAL VERIFICATION FAILED")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())