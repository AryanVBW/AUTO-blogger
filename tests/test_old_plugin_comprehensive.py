#!/usr/bin/env python3
"""
Comprehensive test for old AIOSEO plugin version (v2.7.1) handling.
This test verifies that the SEO metadata is correctly formatted for the old plugin version.
"""

import sys
import os
import logging
from unittest.mock import Mock, patch

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automation_engine import BlogAutomationEngine

def test_old_plugin_seo_metadata():
    """
    Test SEO metadata formatting for old AIOSEO plugin version (v2.7.1)
    """
    print("\n🧪 Testing Old AIOSEO Plugin Version (v2.7.1) SEO Metadata Handling")
    print("=" * 80)
    
    # Create logger
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(handler)
    
    # Create config for old plugin version
    config = {
        'seo_plugin_version': 'old',  # This is the key setting
        'wordpress_sites': {
            'test_site': {
                'url': 'https://test-site.com',
                'username': 'test_user',
                'password': 'test_pass'
            }
        }
    }
    
    # Initialize BlogAutomationEngine
    engine = BlogAutomationEngine(config, logger)
    
    # Test data
    test_cases = [
        {
            'name': 'Basic SEO data with focus keyphrase',
            'seo_title': 'Test SEO Title for Old Plugin',
            'meta_description': 'This is a test meta description for the old AIOSEO plugin version.',
            'focus_keyphrase': 'old aioseo plugin',
            'additional_keyphrases': ['wordpress seo', 'meta tags'],
            'expected_meta': {
                '_aioseop_title': 'Test SEO Title for Old Plugin',
                '_aioseop_description': 'This is a test meta description for the old AIOSEO plugin version.',
                '_aioseop_keywords': 'old aioseo plugin, wordpress seo, meta tags'
            }
        },
        {
            'name': 'SEO data with only focus keyphrase',
            'seo_title': 'Another Test Title',
            'meta_description': 'Another test description.',
            'focus_keyphrase': 'focus keyword only',
            'additional_keyphrases': None,
            'expected_meta': {
                '_aioseop_title': 'Another Test Title',
                '_aioseop_description': 'Another test description.',
                '_aioseop_keywords': 'focus keyword only'
            }
        },
        {
            'name': 'SEO data with only additional keyphrases',
            'seo_title': 'Title Without Focus',
            'meta_description': 'Description without focus keyphrase.',
            'focus_keyphrase': None,
            'additional_keyphrases': ['keyword1', 'keyword2', 'keyword3'],
            'expected_meta': {
                '_aioseop_title': 'Title Without Focus',
                '_aioseop_description': 'Description without focus keyphrase.',
                '_aioseop_keywords': 'keyword1, keyword2, keyword3'
            }
        },
        {
            'name': 'SEO data without any keyphrases',
            'seo_title': 'Title Only',
            'meta_description': 'Description only.',
            'focus_keyphrase': None,
            'additional_keyphrases': None,
            'expected_meta': {
                '_aioseop_title': 'Title Only',
                '_aioseop_description': 'Description only.'
                # No _aioseop_keywords should be present
            }
        },
        {
            'name': 'SEO data with special characters',
            'seo_title': 'Title with "Quotes" & Ampersands',
            'meta_description': 'Description with special chars: <>&"\'\'',
            'focus_keyphrase': 'special "characters"',
            'additional_keyphrases': ['chars & symbols', 'quotes "test"'],
            'expected_meta': {
                '_aioseop_title': 'Title with "Quotes" & Ampersands',
                '_aioseop_description': 'Description with special chars: <>&"\'\'',
                '_aioseop_keywords': 'special "characters", chars & symbols, quotes "test"'
            }
        }
    ]
    
    # Mock the WordPress API calls
    with patch('requests.post') as mock_post:
        # Mock successful post creation
        mock_post_response = Mock()
        mock_post_response.json.return_value = {'id': 123}
        mock_post_response.raise_for_status.return_value = None
        
        # Mock successful SEO update
        mock_seo_response = Mock()
        mock_seo_response.raise_for_status.return_value = None
        mock_seo_response.status_code = 200
        mock_seo_response.text = 'Success'
        
        # Configure mock to return different responses for different calls
        mock_post.side_effect = [mock_post_response, mock_seo_response] * len(test_cases)
        
        # Run tests
        for i, test_case in enumerate(test_cases):
            print(f"\n📋 Test Case {i+1}: {test_case['name']}")
            print("-" * 60)
            
            try:
                # Call the method that handles WordPress posting
                post_id, title = engine.post_to_wordpress_with_seo(
                    title='Test Post Title',
                    content='<p>Test content</p>',
                    categories=['Test'],
                    tags=['test'],
                    seo_title=test_case['seo_title'],
                    meta_description=test_case['meta_description'],
                    focus_keyphrase=test_case['focus_keyphrase'],
                    additional_keyphrases=test_case['additional_keyphrases']
                )
                
                # Verify the post was created
                assert post_id == 123, f"Expected post_id 123, got {post_id}"
                
                # Get the SEO update call (second call to requests.post)
                seo_call_args = mock_post.call_args_list[(i*2) + 1]
                seo_data = seo_call_args[1]['json']  # Get the JSON data from kwargs
                
                print(f"✅ SEO Data Structure: {seo_data}")
                
                # Verify the structure
                assert 'meta' in seo_data, "SEO data should contain 'meta' field for old plugin"
                assert 'aioseo_meta_data' not in seo_data, "Old plugin should not use 'aioseo_meta_data'"
                
                # Verify meta fields
                meta_data = seo_data['meta']
                expected_meta = test_case['expected_meta']
                
                for key, expected_value in expected_meta.items():
                    assert key in meta_data, f"Missing meta field: {key}"
                    assert meta_data[key] == expected_value, f"Meta field {key}: expected '{expected_value}', got '{meta_data[key]}'"
                    print(f"  ✓ {key}: {meta_data[key]}")
                
                # Verify no unexpected keywords field when no keyphrases
                if not test_case['focus_keyphrase'] and not test_case['additional_keyphrases']:
                    assert '_aioseop_keywords' not in meta_data, "Should not have keywords when no keyphrases provided"
                    print(f"  ✓ No _aioseop_keywords field (as expected)")
                
                print(f"✅ Test Case {i+1} PASSED")
                
            except Exception as e:
                print(f"❌ Test Case {i+1} FAILED: {e}")
                return False
    
    print("\n🎉 All Old Plugin SEO Metadata Tests PASSED!")
    print("=" * 80)
    return True

def test_new_vs_old_plugin_comparison():
    """
    Test that demonstrates the difference between old and new plugin formats
    """
    print("\n🔄 Testing New vs Old Plugin Format Comparison")
    print("=" * 80)
    
    # Create logger
    logger = logging.getLogger('comparison_logger')
    logger.setLevel(logging.INFO)
    
    test_data = {
        'seo_title': 'Comparison Test Title',
        'meta_description': 'This is a comparison test description.',
        'focus_keyphrase': 'comparison test',
        'additional_keyphrases': ['old plugin', 'new plugin']
    }
    
    # Test old plugin format
    old_config = {'seo_plugin_version': 'old'}
    old_engine = BlogAutomationEngine(old_config, logger)
    
    # Test new plugin format
    new_config = {'seo_plugin_version': 'new'}
    new_engine = BlogAutomationEngine(new_config, logger)
    
    with patch('requests.post') as mock_post:
        # Mock responses
        mock_response = Mock()
        mock_response.json.return_value = {'id': 456}
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200
        mock_response.text = 'Success'
        mock_post.return_value = mock_response
        
        # Test old plugin
        print("\n📊 Old Plugin Format (v2.7.1):")
        old_engine.post_to_wordpress_with_seo(
            title='Test Post',
            content='<p>Test content</p>',
            categories=['Test'],
            tags=['test'],
            seo_title="Old Plugin SEO Title",
            meta_description="Old plugin meta description",
            focus_keyphrase="old",
            additional_keyphrases=["plugin", "keywords"]
        )
        
        old_seo_call = mock_post.call_args_list[1]  # Second call is SEO update
        old_seo_data = old_seo_call[1]['json']
        print(f"  Structure: {list(old_seo_data.keys())}")
        print(f"  Meta fields: {list(old_seo_data['meta'].keys())}")
        
        # Reset mock
        mock_post.reset_mock()
        
        # Test new plugin
        print("\n📊 New Plugin Format (v4.7.3+):")
        new_engine.post_to_wordpress_with_seo(
            title='Test Post',
            content='<p>Test content</p>',
            categories=['Test'],
            tags=['test'],
            seo_title="New Plugin SEO Title",
            meta_description="New plugin meta description",
            focus_keyphrase="new",
            additional_keyphrases=["plugin", "keywords"]
        )
        
        new_seo_call = mock_post.call_args_list[1]  # Second call is SEO update
        new_seo_data = new_seo_call[1]['json']
        print(f"  Structure: {list(new_seo_data.keys())}")
        print(f"  AIOSEO fields: {list(new_seo_data['aioseo_meta_data'].keys())}")
        
        print("\n✅ Format Comparison Complete")
        print("=" * 80)
    
    return True

if __name__ == '__main__':
    print("🚀 Starting Comprehensive Old AIOSEO Plugin Tests")
    
    success = True
    
    # Run SEO metadata tests
    if not test_old_plugin_seo_metadata():
        success = False
    
    # Run comparison tests
    if not test_new_vs_old_plugin_comparison():
        success = False
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Old AIOSEO plugin handling is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED! Please check the implementation.")
        sys.exit(1)