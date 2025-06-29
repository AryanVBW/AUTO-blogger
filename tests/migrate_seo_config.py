#!/usr/bin/env python3
"""
SEO Configuration Migration Helper

This script helps migrate existing configurations to use the new SEO improvements.
It validates configurations and provides guidance for proper setup.

Usage:
    python3 migrate_seo_config.py [config_directory]
"""

import os
import sys
import json
from typing import Dict, List, Tuple

def load_config(config_path: str) -> Dict:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {config_path}: {e}")
        return {}
    except Exception as e:
        print(f"❌ Error loading {config_path}: {e}")
        return {}

def save_config(config_path: str, config: Dict) -> bool:
    """Save configuration to JSON file"""
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Error saving {config_path}: {e}")
        return False

def validate_seo_config(config: Dict) -> Tuple[bool, List[str]]:
    """Validate SEO configuration and return issues"""
    issues = []
    
    # Check SEO plugin version
    seo_version = config.get('seo_plugin_version')
    if not seo_version:
        issues.append("Missing 'seo_plugin_version' field")
    elif seo_version not in ['old', 'new']:
        issues.append(f"Invalid 'seo_plugin_version': {seo_version}. Must be 'old' or 'new'")
    
    # Check WordPress credentials
    required_wp_fields = ['wp_base_url', 'wp_username', 'wp_password']
    for field in required_wp_fields:
        if not config.get(field):
            issues.append(f"Missing or empty '{field}' field")
    
    # Validate wp_base_url format
    wp_url = config.get('wp_base_url', '')
    if wp_url and not wp_url.endswith('/wp-json/wp/v2'):
        issues.append("'wp_base_url' should end with '/wp-json/wp/v2'")
    
    return len(issues) == 0, issues

def suggest_seo_version(config: Dict) -> str:
    """Suggest appropriate SEO plugin version based on configuration"""
    # Look for clues in the configuration
    if 'aioseo_version' in config:
        version = config['aioseo_version']
        if version.startswith('2.'):
            return 'old'
        elif version.startswith('4.') or version.startswith('5.'):
            return 'new'
    
    # Default to 'new' for modern installations
    return 'new'

def migrate_single_config(config_path: str, dry_run: bool = True) -> bool:
    """Migrate a single configuration file"""
    print(f"\n📁 Processing: {config_path}")
    
    config = load_config(config_path)
    if not config:
        return False
    
    # Check current validation status
    is_valid, issues = validate_seo_config(config)
    
    if is_valid:
        print("✅ Configuration is already valid")
        return True
    
    print("⚠️ Configuration issues found:")
    for issue in issues:
        print(f"   - {issue}")
    
    # Suggest fixes
    changes_made = False
    
    # Add missing seo_plugin_version
    if not config.get('seo_plugin_version'):
        suggested_version = suggest_seo_version(config)
        print(f"\n🔧 Suggested fix: Add 'seo_plugin_version': '{suggested_version}'")
        
        if not dry_run:
            config['seo_plugin_version'] = suggested_version
            changes_made = True
            print(f"   ✅ Added seo_plugin_version: {suggested_version}")
    
    # Fix wp_base_url format
    wp_url = config.get('wp_base_url', '')
    if wp_url and not wp_url.endswith('/wp-json/wp/v2'):
        if wp_url.endswith('/'):
            new_url = wp_url + 'wp-json/wp/v2'
        else:
            new_url = wp_url + '/wp-json/wp/v2'
        
        print(f"\n🔧 Suggested fix: Update wp_base_url to: {new_url}")
        
        if not dry_run:
            config['wp_base_url'] = new_url
            changes_made = True
            print(f"   ✅ Updated wp_base_url")
    
    # Save changes if not dry run
    if changes_made and not dry_run:
        if save_config(config_path, config):
            print(f"✅ Configuration updated successfully")
        else:
            print(f"❌ Failed to save configuration")
            return False
    
    # Re-validate after changes
    if changes_made:
        is_valid_after, remaining_issues = validate_seo_config(config)
        if is_valid_after:
            print("🎉 Configuration is now valid!")
        else:
            print("⚠️ Remaining issues (require manual attention):")
            for issue in remaining_issues:
                print(f"   - {issue}")
    
    return True

def find_config_files(directory: str) -> List[str]:
    """Find all default.json configuration files in directory"""
    config_files = []
    
    if os.path.isfile(directory) and directory.endswith('.json'):
        return [directory]
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == 'default.json':
                config_files.append(os.path.join(root, file))
    
    return config_files

def print_summary(total_configs: int, valid_configs: int, migrated_configs: int):
    """Print migration summary"""
    print("\n" + "="*50)
    print("📊 MIGRATION SUMMARY")
    print("="*50)
    print(f"Total configurations found: {total_configs}")
    print(f"Already valid: {valid_configs}")
    print(f"Successfully migrated: {migrated_configs}")
    print(f"Requiring manual attention: {total_configs - valid_configs - migrated_configs}")
    
    if migrated_configs > 0:
        print("\n✅ Migration completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Test your configuration with: python3 test_seo_improvements.py")
        print("   2. Run a test post to verify SEO metadata handling")
        print("   3. Check logs for any validation warnings")
    
    print("\n📖 For more information, see: SEO_IMPROVEMENTS_DOCUMENTATION.md")

def main():
    """Main migration function"""
    print("🚀 SEO Configuration Migration Helper")
    print("=====================================")
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        config_directory = sys.argv[1]
    else:
        config_directory = "configs"
    
    if not os.path.exists(config_directory):
        print(f"❌ Directory not found: {config_directory}")
        print("\nUsage: python3 migrate_seo_config.py [config_directory]")
        sys.exit(1)
    
    # Find configuration files
    config_files = find_config_files(config_directory)
    
    if not config_files:
        print(f"❌ No configuration files found in: {config_directory}")
        sys.exit(1)
    
    print(f"\n📁 Found {len(config_files)} configuration file(s)")
    
    # Ask for confirmation
    print("\n🔍 Running in DRY RUN mode (no changes will be made)")
    print("This will analyze your configurations and suggest improvements.")
    
    response = input("\nProceed with analysis? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Migration cancelled.")
        sys.exit(0)
    
    # Process configurations
    total_configs = len(config_files)
    valid_configs = 0
    migrated_configs = 0
    
    for config_file in config_files:
        try:
            config = load_config(config_file)
            if config:
                is_valid, _ = validate_seo_config(config)
                if is_valid:
                    valid_configs += 1
                    print(f"\n📁 {config_file}: ✅ Already valid")
                else:
                    if migrate_single_config(config_file, dry_run=True):
                        # Ask if user wants to apply changes
                        print(f"\nApply changes to {config_file}? (y/N): ", end="")
                        apply_response = input().strip().lower()
                        if apply_response in ['y', 'yes']:
                            if migrate_single_config(config_file, dry_run=False):
                                migrated_configs += 1
        except Exception as e:
            print(f"❌ Error processing {config_file}: {e}")
    
    # Print summary
    print_summary(total_configs, valid_configs, migrated_configs)

if __name__ == "__main__":
    main()