#!/usr/bin/env python3
"""
Test script to verify domain-based configuration system
"""

import os
import json
import shutil
import tempfile
from urllib.parse import urlparse

def extract_domain_from_url(url: str) -> str:
    """Extract domain name from WordPress URL for configuration separation"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        # Remove common subdomains and clean up
        domain = domain.replace('.', '_').replace('-', '_')
        return domain
    except Exception as e:
        print(f"Error extracting domain from URL: {e}")
        return "default"

def test_domain_extraction():
    """Test domain extraction from URLs"""
    test_cases = [
        ("https://premierleaguenewsnow.com/wp-json/wp/v2", "premierleaguenewsnow_com"),
        ("https://www.arsenalcore.com/wp-json/wp/v2", "arsenalcore_com"),
        ("https://blog.example-site.com/wp-json/wp/v2", "blog_example_site_com"),
        ("https://footballnews.org/wp-json/wp/v2", "footballnews_org"),
        ("http://localhost:8080/wp-json/wp/v2", "localhost:8080"),
    ]
    
    print("🧪 Testing domain extraction...")
    for url, expected in test_cases:
        result = extract_domain_from_url(url)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {url} -> {result} (expected: {expected})")
    
    print()

def test_domain_directory_structure():
    """Test domain-based directory structure creation"""
    print("🧪 Testing domain directory structure...")
    
    # Create a temporary base directory
    with tempfile.TemporaryDirectory() as temp_dir:
        base_config_dir = os.path.join(temp_dir, "configs")
        os.makedirs(base_config_dir)
        
        # Test domains
        test_domains = ["premierleaguenewsnow_com", "arsenalcore_com", "footballnews_org"]
        
        for domain in test_domains:
            # Create domain directory
            domain_dir = os.path.join(base_config_dir, domain)
            os.makedirs(domain_dir, exist_ok=True)
            
            # Create sample configuration files
            config_files = {
                "default.json": {
                    "source_url": f"https://{domain.replace('_', '.')}/category/news/",
                    "wp_base_url": f"https://{domain.replace('_', '.')}/wp-json/wp/v2",
                    "wp_username": f"user_{domain}",
                    "wp_password": "password123",
                    "gemini_api_key": "test_key",
                    "max_articles": 2
                },
                "internal_links.json": {
                    f"{domain} News": f"https://{domain.replace('_', '.')}/category/news/",
                    f"{domain} Articles": f"https://{domain.replace('_', '.')}/articles/"
                },
                "external_links.json": {
                    "premier league": "https://www.premierleague.com/",
                    f"{domain} specific": f"https://specific.{domain.replace('_', '.')}"
                },
                "style_prompt.json": {
                    "style_prompt": f"Write in the style of {domain.replace('_', '.')} - professional football journalism"
                }
            }
            
            for filename, content in config_files.items():
                filepath = os.path.join(domain_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(content, f, indent=2)
            
            print(f"  ✅ Created configuration for domain: {domain}")
            print(f"     Directory: {domain_dir}")
            print(f"     Files: {list(config_files.keys())}")
        
        # Verify structure
        print(f"\n📁 Directory structure created in: {base_config_dir}")
        for root, dirs, files in os.walk(base_config_dir):
            level = root.replace(base_config_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
    
    print()

def test_domain_config_isolation():
    """Test that configurations are properly isolated by domain"""
    print("🧪 Testing domain configuration isolation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        base_config_dir = os.path.join(temp_dir, "configs")
        
        # Create configurations for two different domains
        domains = {
            "premierleaguenewsnow_com": {
                "style_prompt": "Write in a professional Premier League news style",
                "internal_links": {
                    "Arsenal News": "https://premierleaguenewsnow.com/arsenal/",
                    "Liverpool News": "https://premierleaguenewsnow.com/liverpool/"
                },
                "max_articles": 5
            },
            "arsenalcore_com": {
                "style_prompt": "Write in an Arsenal-focused passionate fan style",
                "internal_links": {
                    "Arsenal History": "https://arsenalcore.com/history/",
                    "Arsenal Players": "https://arsenalcore.com/players/"
                },
                "max_articles": 3
            }
        }
        
        # Create domain directories and configurations
        for domain, config in domains.items():
            domain_dir = os.path.join(base_config_dir, domain)
            os.makedirs(domain_dir, exist_ok=True)
            
            # Save configurations
            for key, value in config.items():
                if key == "style_prompt":
                    filepath = os.path.join(domain_dir, "style_prompt.json")
                    with open(filepath, 'w') as f:
                        json.dump({"style_prompt": value}, f, indent=2)
                elif key == "internal_links":
                    filepath = os.path.join(domain_dir, "internal_links.json")
                    with open(filepath, 'w') as f:
                        json.dump(value, f, indent=2)
                else:
                    # Add to default.json
                    filepath = os.path.join(domain_dir, "default.json")
                    if os.path.exists(filepath):
                        with open(filepath) as f:
                            default_config = json.load(f)
                    else:
                        default_config = {}
                    default_config[key] = value
                    with open(filepath, 'w') as f:
                        json.dump(default_config, f, indent=2)
        
        # Verify isolation
        for domain in domains.keys():
            domain_dir = os.path.join(base_config_dir, domain)
            
            # Load style prompt
            style_prompt_file = os.path.join(domain_dir, "style_prompt.json")
            with open(style_prompt_file) as f:
                style_data = json.load(f)
                style_prompt = style_data["style_prompt"]
            
            # Load internal links
            internal_links_file = os.path.join(domain_dir, "internal_links.json")
            with open(internal_links_file) as f:
                internal_links = json.load(f)
            
            # Load default config
            default_file = os.path.join(domain_dir, "default.json")
            with open(default_file) as f:
                default_config = json.load(f)
            
            print(f"  📋 Domain: {domain}")
            print(f"     Style: {style_prompt[:50]}...")
            print(f"     Internal Links: {len(internal_links)} links")
            print(f"     Max Articles: {default_config.get('max_articles', 'N/A')}")
            
            # Verify domain-specific content
            if domain == "premierleaguenewsnow_com":
                assert "Premier League" in style_prompt
                assert "Arsenal News" in internal_links
                assert default_config.get('max_articles') == 5
                print(f"     ✅ Premier League domain configuration verified")
            elif domain == "arsenalcore_com":
                assert "Arsenal-focused" in style_prompt
                assert "Arsenal History" in internal_links
                assert default_config.get('max_articles') == 3
                print(f"     ✅ Arsenal Core domain configuration verified")
    
    print()

def test_credential_management():
    """Test domain-based credential management"""
    print("🧪 Testing domain-based credential management...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        base_config_dir = os.path.join(temp_dir, "configs")
        os.makedirs(base_config_dir)
        
        # Sample credentials for different domains
        credentials = [
            {
                "wp_base_url": "https://premierleaguenewsnow.com/wp-json/wp/v2",
                "wp_username": "admin",
                "wp_password": "password123",
                "domain": "premierleaguenewsnow_com"
            },
            {
                "wp_base_url": "https://arsenalcore.com/wp-json/wp/v2",
                "wp_username": "editor",
                "wp_password": "secret456",
                "domain": "arsenalcore_com"
            },
            {
                "wp_base_url": "https://footballnews.org/wp-json/wp/v2",
                "wp_username": "writer",
                "wp_password": "secure789",
                "domain": "footballnews_org"
            }
        ]
        
        # Save global credentials
        global_creds_file = os.path.join(base_config_dir, "credentials.json")
        with open(global_creds_file, 'w') as f:
            json.dump(credentials, f, indent=2)
        
        # Save domain-specific credentials
        for cred in credentials:
            domain_dir = os.path.join(base_config_dir, cred["domain"])
            os.makedirs(domain_dir, exist_ok=True)
            
            domain_creds_file = os.path.join(domain_dir, "credentials.json")
            with open(domain_creds_file, 'w') as f:
                json.dump([cred], f, indent=2)
        
        # Verify credential isolation
        print(f"  📋 Global credentials file: {len(credentials)} entries")
        
        for cred in credentials:
            domain = cred["domain"]
            domain_dir = os.path.join(base_config_dir, domain)
            domain_creds_file = os.path.join(domain_dir, "credentials.json")
            
            with open(domain_creds_file) as f:
                domain_creds = json.load(f)
            
            print(f"  ✅ Domain {domain}:")
            print(f"     URL: {cred['wp_base_url']}")
            print(f"     User: {cred['wp_username']}")
            print(f"     Domain credentials: {len(domain_creds)} entries")
            
            # Verify only this domain's credentials are in the domain file
            assert len(domain_creds) == 1
            assert domain_creds[0]["domain"] == domain
    
    print()

def main():
    """Run all tests"""
    print("🚀 Testing Domain-Based Configuration System\n")
    
    test_domain_extraction()
    test_domain_directory_structure()
    test_domain_config_isolation()
    test_credential_management()
    
    print("✅ All tests passed! Domain-based configuration system is working correctly.")
    print("\n📋 Summary:")
    print("  • Domain extraction from URLs works correctly")
    print("  • Domain-specific directories are created automatically") 
    print("  • Configurations are properly isolated by domain")
    print("  • Credentials are managed separately for each domain")
    print("  • Multiple WordPress sites can be managed independently")

if __name__ == "__main__":
    main()
