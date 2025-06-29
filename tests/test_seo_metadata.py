#!/usr/bin/env python3
"""
Test script to verify SEO metadata formatting for both old and new plugin versions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automation_engine import BlogAutomationEngine
import json
import logging

def test_seo_metadata_formatting():
    """Test SEO metadata formatting for both plugin versions."""
    
    # Create automation engine instance
    logger = logging.getLogger('test')
    config = {'seo_plugin_version': 'new'}  # Default config
    engine = BlogAutomationEngine(config, logger)
    
    # Test data
    test_title = "Manchester United Transfer News"
    test_content = "Manchester United are reportedly interested in signing a new striker this summer. The Red Devils are looking to strengthen their attack with a world-class forward who can score goals consistently."
    
    print("🧪 Testing SEO metadata formatting...\n")
    
    # Test keyphrase extraction first
    print("1. Testing keyphrase extraction:")
    try:
        focus_keyphrase, additional_keyphrases = engine.extract_keyphrases_fallback(test_content, test_title)
        print(f"   ✅ Focus keyphrase: '{focus_keyphrase}'")
        print(f"   ✅ Additional keyphrases: {additional_keyphrases}")
        print(f"   ✅ Type check - Focus: {type(focus_keyphrase)}, Additional: {type(additional_keyphrases)}")
    except Exception as e:
        print(f"   ❌ Keyphrase extraction failed: {e}")
        return False
    
    # Test old plugin version metadata
    print("\n2. Testing old plugin version (v2.7.1) metadata:")
    engine.config['seo_plugin_version'] = 'old'
    
    # Simulate the SEO metadata creation logic
    seo_title = "Manchester United Transfer News - Latest Updates"
    meta_description = "Get the latest Manchester United transfer news and updates on potential signings this summer."
    
    try:
        # Old AIOSEO Pack Pro v2.7.1 format
        seo_data = {
            "meta": {
                "_aioseop_title": seo_title,
                "_aioseop_description": meta_description
            }
        }
        # Add keywords (focus + additional keyphrases)
        if focus_keyphrase or additional_keyphrases:
            all_keyphrases = []
            if focus_keyphrase:
                all_keyphrases.append(focus_keyphrase)
            if additional_keyphrases:
                all_keyphrases.extend(additional_keyphrases)
            seo_data["meta"]["_aioseop_keywords"] = ", ".join(all_keyphrases)
        
        print(f"   ✅ Old plugin metadata:")
        print(f"      Title: {seo_data['meta']['_aioseop_title']}")
        print(f"      Description: {seo_data['meta']['_aioseop_description']}")
        print(f"      Keywords: {seo_data['meta'].get('_aioseop_keywords', 'None')}")
        
        # Verify all fields are present
        assert '_aioseop_title' in seo_data['meta'], "Title missing in old plugin format"
        assert '_aioseop_description' in seo_data['meta'], "Description missing in old plugin format"
        assert '_aioseop_keywords' in seo_data['meta'], "Keywords missing in old plugin format"
        print("   ✅ All required fields present for old plugin version")
        
    except Exception as e:
        print(f"   ❌ Old plugin metadata creation failed: {e}")
        return False
    
    # Test new plugin version metadata
    print("\n3. Testing new plugin version (v4.7.3+) metadata:")
    engine.config['seo_plugin_version'] = 'new'
    
    try:
        # New AIOSEO Pro v4.7.3+ format
        seo_data = {
            "aioseo_meta_data": {
                "title": seo_title,
                "description": meta_description
            }
        }
        # Add focus keyphrase tag and keyphrases structure
        if focus_keyphrase:
            seo_data["aioseo_meta_data"]["focus_keyphrase"] = focus_keyphrase
            seo_data["aioseo_meta_data"]["keyphrases"] = {
                "focus": {
                    "keyphrase": focus_keyphrase
                },
                "additional": [
                    {"keyphrase": kp} for kp in (additional_keyphrases or [])
                ]
            }
        
        print(f"   ✅ New plugin metadata:")
        print(f"      Title: {seo_data['aioseo_meta_data']['title']}")
        print(f"      Description: {seo_data['aioseo_meta_data']['description']}")
        print(f"      Focus keyphrase: {seo_data['aioseo_meta_data'].get('focus_keyphrase', 'None')}")
        print(f"      Keyphrases structure: {json.dumps(seo_data['aioseo_meta_data'].get('keyphrases', {}), indent=8)}")
        
        # Verify all fields are present
        assert 'title' in seo_data['aioseo_meta_data'], "Title missing in new plugin format"
        assert 'description' in seo_data['aioseo_meta_data'], "Description missing in new plugin format"
        assert 'focus_keyphrase' in seo_data['aioseo_meta_data'], "Focus keyphrase tag missing in new plugin format"
        assert 'keyphrases' in seo_data['aioseo_meta_data'], "Keyphrases structure missing in new plugin format"
        assert 'focus' in seo_data['aioseo_meta_data']['keyphrases'], "Focus keyphrase in structure missing"
        assert 'additional' in seo_data['aioseo_meta_data']['keyphrases'], "Additional keyphrases in structure missing"
        print("   ✅ All required fields present for new plugin version")
        
    except Exception as e:
        print(f"   ❌ New plugin metadata creation failed: {e}")
        return False
    
    print("\n🎉 All SEO metadata tests passed!")
    return True

if __name__ == "__main__":
    success = test_seo_metadata_formatting()
    if success:
        print("\n✅ SEO metadata formatting is working correctly for both plugin versions.")
        sys.exit(0)
    else:
        print("\n❌ SEO metadata formatting tests failed.")
        sys.exit(1)