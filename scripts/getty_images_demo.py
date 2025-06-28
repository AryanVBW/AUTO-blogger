#!/usr/bin/env python3
"""
Demo of the new Getty Images functionality for the WordPress Blog Automation Suite

This demo shows how to use the new image source options:
1. OpenAI Generated Images (existing feature)
2. Getty Images Editorial (new feature)
"""

import sys
import os

# Add the current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_getty_images_feature():
    """Demonstrate the new Getty Images functionality"""
    
    print("=" * 60)
    print("🎯 WORDPRESS BLOG AUTOMATION - GETTY IMAGES DEMO")
    print("=" * 60)
    
    print("\n📷 NEW FEATURE: Getty Images Integration")
    print("-" * 40)
    
    print("✨ What's New:")
    print("• Added option to choose between OpenAI generated images and Getty Images")
    print("• Getty Images searches based on article topic and keywords")
    print("• Uses official Getty Images embed code (no API key required)")
    print("• Automatically integrates images into article content")
    print("• Editorial images from Getty's professional collection")
    
    print("\n🎛️ How to Use:")
    print("-" * 40)
    print("1. Launch the Blog Automation GUI")
    print("2. Go to the Settings section")
    print("3. Choose from three image options:")
    print("   ○ No Images")
    print("   ○ Generate with OpenAI DALL-E (requires API key)")
    print("   ○ Getty Images Editorial (no API key needed)")
    print("4. Process articles as usual")
    
    print("\n🔍 Getty Images Search Process:")
    print("-" * 40)
    print("• Searches Getty Images based on article title and keywords")
    print("• Selects relevant editorial images")
    print("• Embeds using Getty's standard embed code")
    print("• Automatically places images in article content")
    print("• Maintains proper attribution and licensing")
    
    print("\n📋 Example Implementation:")
    print("-" * 40)
    print("Article Title: 'Manchester United vs Liverpool Match Report'")
    print("Keywords: ['Manchester United', 'Premier League', 'football']")
    print("→ Getty Search: 'Manchester United Premier League football'")
    print("→ Result: Professional match photos from Getty's editorial collection")
    print("→ Embed: <iframe src='https://embed.gettyimages.com/embed/[ID]'>")
    
    print("\n⚙️ Technical Features:")
    print("-" * 40)
    print("• Smart keyword extraction for relevant image search")
    print("• Automatic content integration")
    print("• Fallback handling if no images found")
    print("• Professional embed code with proper styling")
    print("• Error handling and logging")
    
    print("\n🎨 Code Structure:")
    print("-" * 40)
    print("New Functions Added:")
    print("• search_getty_images() - Searches Getty Images")
    print("• get_getty_embed_code() - Generates embed code")
    print("• add_getty_image_to_content() - Integrates images into content")
    
    print("\n🚀 Benefits:")
    print("-" * 40)
    print("✅ No API key required for Getty Images")
    print("✅ Professional quality editorial images")
    print("✅ Proper licensing and attribution")
    print("✅ Automatic content integration")
    print("✅ Fallback options available")
    print("✅ User-friendly interface")
    
    print("\n" + "=" * 60)
    print("🎯 Ready to use! Launch gui_blogger.py to get started!")
    print("=" * 60)
    
    # Show code example
    print("\n📝 Code Example:")
    print("-" * 40)
    print("""
# Example of how Getty Images are integrated:

if image_source == "getty":
    # Add Getty images directly to content using keywords
    topic_keywords = [focus_keyphrase] + additional_keyphrases
    final_content = automation_engine.add_getty_image_to_content(
        final_content, 
        article_title, 
        topic_keywords
    )
    """)

if __name__ == "__main__":
    demo_getty_images_feature()
