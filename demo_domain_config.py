#!/usr/bin/env python3
"""
Demonstration script showing the domain-based configuration system in action
"""

import os
import json
import sys

def demonstrate_domain_config():
    """Demonstrate the domain-based configuration system"""
    
    print("🚀 AUTO Blogger - Domain-Based Configuration System Demo\n")
    
    configs_dir = "configs"
    
    # Check if configs directory exists
    if not os.path.exists(configs_dir):
        print("❌ Configs directory not found. Please run this from the AUTO-blogger directory.")
        return
    
    print("📁 Current configuration structure:")
    print(f"   {configs_dir}/")
    
    # List all items in configs directory
    items = sorted(os.listdir(configs_dir))
    domain_dirs = []
    config_files = []
    
    for item in items:
        item_path = os.path.join(configs_dir, item)
        if os.path.isdir(item_path) and not item.startswith('.'):
            domain_dirs.append(item)
        elif item.endswith('.json'):
            config_files.append(item)
    
    # Show global configuration files
    print("\n🌐 Global Configuration Files:")
    for file in config_files:
        file_path = os.path.join(configs_dir, file)
        if file == "credentials.json":
            try:
                with open(file_path) as f:
                    creds = json.load(f)
                    print(f"   📄 {file} ({len(creds)} saved domains)")
                    for i, cred in enumerate(creds):
                        domain = cred.get('domain', 'unknown')
                        url = cred.get('wp_base_url', 'N/A')
                        print(f"      {i+1}. {domain} -> {url}")
            except:
                print(f"   📄 {file} (error reading)")
        else:
            print(f"   📄 {file}")
    
    # Show domain-specific directories
    if domain_dirs:
        print(f"\n🏠 Domain-Specific Configuration Directories ({len(domain_dirs)} domains):")
        
        for domain in domain_dirs:
            domain_path = os.path.join(configs_dir, domain)
            print(f"\n   📁 {domain}/")
            
            # List files in domain directory
            try:
                domain_files = sorted([f for f in os.listdir(domain_path) if f.endswith('.json')])
                for file in domain_files:
                    file_path = os.path.join(domain_path, file)
                    file_size = os.path.getsize(file_path)
                    
                    # Show brief content summary for key files
                    if file == "default.json":
                        try:
                            with open(file_path) as f:
                                config = json.load(f)
                                source_url = config.get('source_url', 'N/A')
                                wp_url = config.get('wp_base_url', 'N/A')
                                print(f"      📋 {file} ({file_size} bytes)")
                                print(f"         Source: {source_url}")
                                print(f"         WordPress: {wp_url}")
                        except:
                            print(f"      📋 {file} ({file_size} bytes) - error reading")
                    
                    elif file == "internal_links.json":
                        try:
                            with open(file_path) as f:
                                links = json.load(f)
                                print(f"      🔗 {file} ({len(links)} internal links)")
                        except:
                            print(f"      🔗 {file} - error reading")
                    
                    elif file == "external_links.json":
                        try:
                            with open(file_path) as f:
                                links = json.load(f)
                                print(f"      🌐 {file} ({len(links)} external links)")
                        except:
                            print(f"      🌐 {file} - error reading")
                    
                    elif file == "style_prompt.json":
                        try:
                            with open(file_path) as f:
                                style_data = json.load(f)
                                prompt = style_data.get('style_prompt', '')
                                preview = prompt[:50] + "..." if len(prompt) > 50 else prompt
                                print(f"      📝 {file} - \"{preview}\"")
                        except:
                            print(f"      📝 {file} - error reading")
                    
                    else:
                        print(f"      📄 {file} ({file_size} bytes)")
                        
            except Exception as e:
                print(f"      ❌ Error reading domain directory: {e}")
    else:
        print("\n📭 No domain-specific directories found yet.")
        print("   💡 Domain directories are created automatically when you log in with WordPress credentials.")
    
    print(f"\n✨ Summary:")
    print(f"   • {len(config_files)} global configuration files")
    print(f"   • {len(domain_dirs)} domain-specific configuration sets")
    print(f"   • Each domain has complete configuration isolation")
    print(f"   • No conflicts between different WordPress sites")
    
    if domain_dirs:
        print(f"\n🔧 How it works:")
        print(f"   1. User logs in with WordPress credentials")
        print(f"   2. System extracts domain from URL (e.g., premierleaguenewsnow.com)")
        print(f"   3. Creates domain directory: configs/{domain_dirs[0]}/")
        print(f"   4. All configuration changes apply only to that domain")
        print(f"   5. Switching domains loads different configuration sets")
    
    print(f"\n🎯 Benefits:")
    print(f"   ✅ Complete separation between different WordPress sites")
    print(f"   ✅ Different writing styles for different blogs")
    print(f"   ✅ Domain-specific source URLs and content settings")
    print(f"   ✅ Isolated SEO and image generation settings")
    print(f"   ✅ Easy management of multiple blogs without conflicts")

if __name__ == "__main__":
    demonstrate_domain_config()
