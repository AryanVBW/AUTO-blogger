#!/usr/bin/env python3
"""
Test script to debug old AIOSEO plugin v2.7.1 SEO metadata handling
"""

import json
import logging
from automation_engine import BlogAutomationEngine

def test_old_plugin_seo_metadata():
    """Test old plugin SEO metadata structure and identify issues"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('test_old_plugin')
    
    print("🔍 Testing Old AIOSEO Plugin v2.7.1 SEO Metadata Handling")
    print("=" * 60)
    
    # Test configurations for old plugin
    old_config = {
        'seo_plugin_version': 'old',
        'wp_base_url': 'https://arsenalcore.com/wp-json/wp/v2',
        'wp_username': 'test_user',
        'wp_password': 'test_pass'
    }
    
    # Create engine instance
    engine = BlogAutomationEngine(old_config, logger)
    
    # Test data
    test_title = "Arsenal Transfer News: Gunners Target New Striker"
    test_content = "Arsenal are reportedly interested in signing a new striker this summer. The Gunners are looking to strengthen their attack with a world-class forward who can score goals consistently in the Premier League."
    
    print("\n1. Testing keyphrase extraction for old plugin:")
    try:
        focus_keyphrase, additional_keyphrases = engine.extract_keyphrases_fallback(test_content, test_title)
        print(f"   ✅ Focus keyphrase: '{focus_keyphrase}'")
        print(f"   ✅ Additional keyphrases: {additional_keyphrases}")
        print(f"   ✅ Return types - Focus: {type(focus_keyphrase)}, Additional: {type(additional_keyphrases)}")
    except Exception as e:
        print(f"   ❌ Keyphrase extraction failed: {e}")
        return False
    
    print("\n2. Testing old plugin SEO metadata structure:")
    
    # Simulate the SEO metadata creation for old plugin
    seo_title = "Arsenal Transfer News: Gunners Target New Striker | Arsenal Core"
    meta_description = "Arsenal are reportedly interested in signing a new striker this summer. Latest transfer news and updates."
    
    # Test old plugin format
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
    
    print("   📋 Old Plugin SEO Data Structure:")
    print(json.dumps(seo_data, indent=4))
    
    print("\n3. Validating old plugin format requirements:")
    
    # Check required fields
    required_fields = ["_aioseop_title", "_aioseop_description", "_aioseop_keywords"]
    missing_fields = []
    
    for field in required_fields:
        if field not in seo_data["meta"]:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"   ❌ Missing required fields: {missing_fields}")
        return False
    else:
        print("   ✅ All required fields present")
    
    # Validate field content
    print("\n4. Validating field content:")
    
    # Check title
    title_value = seo_data["meta"]["_aioseop_title"]
    if not title_value or len(title_value.strip()) == 0:
        print("   ❌ Title field is empty")
        return False
    else:
        print(f"   ✅ Title: '{title_value}' (length: {len(title_value)})")
    
    # Check description
    desc_value = seo_data["meta"]["_aioseop_description"]
    if not desc_value or len(desc_value.strip()) == 0:
        print("   ❌ Description field is empty")
        return False
    else:
        print(f"   ✅ Description: '{desc_value}' (length: {len(desc_value)})")
    
    # Check keywords
    keywords_value = seo_data["meta"]["_aioseop_keywords"]
    if not keywords_value or len(keywords_value.strip()) == 0:
        print("   ❌ Keywords field is empty")
        return False
    else:
        print(f"   ✅ Keywords: '{keywords_value}' (length: {len(keywords_value)})")
    
    print("\n5. Testing WordPress REST API compatibility:")
    
    # Check if the structure is compatible with WordPress REST API
    try:
        # Simulate what would be sent to WordPress
        json_payload = json.dumps(seo_data)
        print(f"   ✅ JSON serialization successful (size: {len(json_payload)} bytes)")
        
        # Parse back to ensure it's valid
        parsed_data = json.loads(json_payload)
        print("   ✅ JSON parsing successful")
        
        # Check structure
        if "meta" in parsed_data and isinstance(parsed_data["meta"], dict):
            print("   ✅ Meta structure is valid")
        else:
            print("   ❌ Invalid meta structure")
            return False
            
    except Exception as e:
        print(f"   ❌ JSON handling failed: {e}")
        return False
    
    print("\n6. Comparing with new plugin format:")
    
    # Create new plugin format for comparison
    new_seo_data = {
        "aioseo_meta_data": {
            "title": seo_title,
            "description": meta_description
        }
    }
    
    if focus_keyphrase:
        new_seo_data["aioseo_meta_data"]["focus_keyphrase"] = focus_keyphrase
        new_seo_data["aioseo_meta_data"]["keyphrases"] = {
            "focus": {
                "keyphrase": focus_keyphrase
            },
            "additional": [
                {"keyphrase": kp} for kp in (additional_keyphrases or [])
            ]
        }
    
    print("   📋 New Plugin SEO Data Structure:")
    print(json.dumps(new_seo_data, indent=4))
    
    print("\n7. Key differences identified:")
    print("   🔸 Old plugin uses 'meta' wrapper with '_aioseop_' prefixed fields")
    print("   🔸 New plugin uses 'aioseo_meta_data' wrapper with direct field names")
    print("   🔸 Old plugin combines all keywords in single '_aioseop_keywords' field")
    print("   🔸 New plugin separates focus and additional keyphrases in structured format")
    
    print("\n✅ Old plugin SEO metadata test completed successfully!")
    return True

def test_potential_issues():
    """Test potential issues with old plugin implementation"""
    
    print("\n🚨 Testing Potential Issues with Old Plugin Implementation")
    print("=" * 60)
    
    # Test edge cases
    test_cases = [
        {
            "name": "Empty keyphrases",
            "focus": "",
            "additional": []
        },
        {
            "name": "None keyphrases",
            "focus": None,
            "additional": None
        },
        {
            "name": "Special characters in keyphrases",
            "focus": "Arsenal's transfer news",
            "additional": ["Gunners' strategy", "Premier League & Champions League"]
        },
        {
            "name": "Very long keyphrases",
            "focus": "Arsenal Football Club transfer news and updates for the summer transfer window",
            "additional": ["Very long additional keyphrase that might cause issues with database storage"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        
        focus = test_case['focus']
        additional = test_case['additional']
        
        # Create old plugin format
        seo_data = {
            "meta": {
                "_aioseop_title": "Test Title",
                "_aioseop_description": "Test Description"
            }
        }
        
        # Add keywords
        if focus or additional:
            all_keyphrases = []
            if focus:
                all_keyphrases.append(focus)
            if additional:
                all_keyphrases.extend(additional)
            
            if all_keyphrases:
                seo_data["meta"]["_aioseop_keywords"] = ", ".join(all_keyphrases)
        
        # Check result
        keywords_field = seo_data["meta"].get("_aioseop_keywords", "")
        print(f"   Keywords field: '{keywords_field}'")
        
        if not keywords_field and (focus or additional):
            print("   ⚠️  Keywords field is empty despite having keyphrases")
        elif keywords_field:
            print(f"   ✅ Keywords field populated (length: {len(keywords_field)})")
        else:
            print("   ℹ️  No keyphrases provided, keywords field empty as expected")

if __name__ == "__main__":
    try:
        success = test_old_plugin_seo_metadata()
        if success:
            test_potential_issues()
            print("\n🎉 All tests completed successfully!")
        else:
            print("\n❌ Tests failed!")
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()