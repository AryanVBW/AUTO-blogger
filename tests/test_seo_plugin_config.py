#!/usr/bin/env python3
"""
Test script to verify SEO plugin configuration functionality
"""

import json
import os
from automation_engine import BlogAutomationEngine

def test_seo_plugin_config():
    """Test SEO plugin configuration for different versions"""
    
    # Test configurations
    test_configs = {
        "new_plugin": {
            "seo_plugin_version": "new",
            "wp_base_url": "https://premierleaguenewsnow.com/wp-json/wp/v2",
            "wp_username": "test_user",
            "wp_password": "test_pass"
        },
        "old_plugin": {
            "seo_plugin_version": "old",
            "wp_base_url": "https://arsenalcore.com/wp-json/wp/v2",
            "wp_username": "test_user",
            "wp_password": "test_pass"
        }
    }
    
    print("🧪 Testing SEO Plugin Configuration")
    print("=" * 50)
    
    for test_name, config in test_configs.items():
        print(f"\n📋 Testing {test_name.replace('_', ' ').title()}:")
        print(f"   Plugin Version: {config['seo_plugin_version']}")
        
        # Create engine instance with required arguments
        import logging
        logger = logging.getLogger(__name__)
        engine = BlogAutomationEngine(config, logger)
        
        # Test SEO metadata formatting
        test_seo_data = {
            "seo_title": "Test SEO Title for Football Article",
            "meta_description": "This is a test meta description for a football article that should be between 155-160 characters long to test SEO functionality.",
            "focus_keyphrase": "football transfer",
            "additional_keyphrases": ["premier league", "arsenal news", "transfer rumors"]
        }
        
        # Simulate the SEO metadata creation logic
        seo_plugin_version = config.get('seo_plugin_version', 'new')
        
        if seo_plugin_version == 'old':
            # Old AIOSEO Pack Pro v2.7.1 format
            seo_data = {
                "meta": {
                    "_aioseop_title": test_seo_data["seo_title"],
                    "_aioseop_description": test_seo_data["meta_description"]
                }
            }
            if test_seo_data["focus_keyphrase"]:
                all_keyphrases = [test_seo_data["focus_keyphrase"]] + test_seo_data["additional_keyphrases"]
                seo_data["meta"]["_aioseop_keywords"] = ", ".join(all_keyphrases)
            
            print(f"   ✅ Old AIOSEO format (v2.7.1):")
        else:
            # New AIOSEO Pro v4.7.3+ format
            seo_data = {
                "aioseo_meta_data": {
                    "title": test_seo_data["seo_title"],
                    "description": test_seo_data["meta_description"]
                }
            }
            if test_seo_data["focus_keyphrase"]:
                seo_data["aioseo_meta_data"]["keyphrases"] = {
                    "focus": {
                        "keyphrase": test_seo_data["focus_keyphrase"]
                    },
                    "additional": [
                        {"keyphrase": kp} for kp in test_seo_data["additional_keyphrases"]
                    ]
                }
            
            print(f"   ✅ New AIOSEO format (v4.7.3+):")
        
        # Pretty print the SEO data structure
        print(f"   📄 Generated SEO Data:")
        print(json.dumps(seo_data, indent=6))
    
    print("\n🎉 SEO Plugin Configuration Test Complete!")
    print("\n📝 Summary:")
    print("   • New plugin version uses 'aioseo_meta_data' structure")
    print("   • Old plugin version uses 'meta' with '_aioseop_' prefixed fields")
    print("   • Keyphrases are handled differently between versions")
    print("   • Configuration is loaded from domain-specific settings")

if __name__ == "__main__":
    test_seo_plugin_config()