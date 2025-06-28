#!/usr/bin/env python3
"""
Test script for Jupyter notebook enhancement implementation
This script verifies that all the new Jupyter-style methods are working correctly
"""

import os
import json
import logging
from automation_engine import BlogAutomationEngine

def setup_test_logging():
    """Setup test logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('test_jupyter.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('test_jupyter')

def load_test_config():
    """Load configuration for testing"""
    config_file = "configs/default.json"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        print(f"❌ Config file not found: {config_file}")
        return None
    
    return config

def test_jupyter_methods():
    """Test all Jupyter notebook enhanced methods"""
    logger = setup_test_logging()
    logger.info("🚀 Starting Jupyter enhancement test")
    
    # Load configuration
    config = load_test_config()
    if not config:
        logger.error("❌ Failed to load configuration")
        return False
    
    # Initialize automation engine
    try:
        engine = BlogAutomationEngine(config, logger)
        logger.info("✅ Automation engine initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize automation engine: {e}")
        return False
    
    # Test article processing
    test_url = "https://premierleaguenewsnow.com/transfer-news/crystal-palace-manager-reveals-the-player-his-club-will-try-to-keep/"
    
    logger.info(f"🔍 Testing enhanced article processing with URL: {test_url}")
    
    try:
        # Test the complete article processing
        article_data = engine.process_complete_article_jupyter(test_url)
        
        if article_data:
            logger.info("✅ Article processing completed successfully")
            logger.info(f"📝 Title: {article_data.get('title', 'N/A')[:100]}...")
            logger.info(f"🏷️ Categories: {article_data.get('categories', [])}")
            logger.info(f"🔖 Tags: {article_data.get('tags', [])[:5]}...")  # Show first 5 tags
            logger.info(f"🎯 SEO Title: {article_data.get('seo_title', 'N/A')}")
            logger.info(f"📄 Meta Description: {article_data.get('meta_description', 'N/A')[:100]}...")
            logger.info(f"🔑 Focus Keyphrase: {article_data.get('focus_keyphrase', 'N/A')}")
            logger.info(f"📝 Content length: {len(article_data.get('content', ''))} characters")
            logger.info(f"🔗 Slug: {article_data.get('slug', 'N/A')}")
            
            return True
        else:
            logger.error("❌ Article processing failed - no data returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during article processing: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_individual_methods():
    """Test individual Jupyter notebook methods"""
    logger = setup_test_logging()
    
    # Load configuration
    config = load_test_config()
    if not config:
        return False
    
    # Initialize automation engine
    engine = BlogAutomationEngine(config, logger)
    
    # Test content
    test_content = """
    <p>Crystal Palace manager Oliver Glasner has revealed that the club will make every effort to retain midfielder Eberechi Eze despite increasing interest from top Premier League clubs. The 25-year-old England international has been in exceptional form this season, attracting attention from Arsenal, Tottenham, and Manchester City.</p>
    
    <p>Eze has scored 11 goals and provided 6 assists in 25 appearances this season, establishing himself as one of the most creative players in the Premier League. His performances have not gone unnoticed, with several top clubs reportedly preparing substantial bids for the summer transfer window.</p>
    
    <p>Speaking about the situation, Glasner emphasized the importance of keeping key players at Selhurst Park. "Eberechi is a fantastic player and person. We will do everything we can to keep him here," the Austrian manager stated during his press conference.</p>
    """
    
    test_title = "Crystal Palace boss reveals club will fight to keep Premier League star"
    
    logger.info("🧪 Testing individual methods")
    
    try:
        # Test category detection
        categories = engine.detect_categories_jupyter(test_content, test_title)
        logger.info(f"✅ Categories detected: {categories}")
        
        # Test tag generation
        tags = engine.generate_tags_with_gemini_jupyter(test_content)
        logger.info(f"✅ Tags generated: {tags[:5]}...")  # Show first 5
        
        # Test slug generation
        slug = engine.generate_slug_jupyter(test_title)
        logger.info(f"✅ Slug generated: {slug}")
        
        # Test keyphrase extraction
        keyphrases = engine.extract_keyphrases_with_gemini(test_content, test_title)
        if keyphrases:
            logger.info(f"✅ Focus keyphrase: {keyphrases.get('focus_keyphrase', 'N/A')}")
            logger.info(f"✅ Additional keyphrases: {keyphrases.get('additional_keyphrases', [])}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing individual methods: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main test function"""
    print("🚀 Testing Jupyter Notebook Enhancement Implementation")
    print("=" * 60)
    
    # Test individual methods first
    print("\n📋 Testing Individual Methods...")
    if test_individual_methods():
        print("✅ Individual methods test PASSED")
    else:
        print("❌ Individual methods test FAILED")
        return
    
    # Test complete article processing
    print("\n📄 Testing Complete Article Processing...")
    if test_jupyter_methods():
        print("✅ Complete article processing test PASSED")
    else:
        print("❌ Complete article processing test FAILED")
        return
    
    print("\n🎉 All tests completed successfully!")
    print("💡 You can now use the 'Enhanced Processing (Jupyter Style)' option in the GUI")

if __name__ == "__main__":
    main()
