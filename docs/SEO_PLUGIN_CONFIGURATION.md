# SEO Plugin Configuration Guide

## Overview

The WordPress Blog Automation tool now supports dual SEO plugin configurations to handle different versions of the All in One SEO plugin across your blogging websites.

## Supported Plugin Versions

### New Version (All in One SEO Pro v4.7.3+)
- **Sites**: premierleaguenewsnow.com, tottenhaminsight.com, unitedleeds.com
- **Format**: Uses `aioseo_meta_data` structure
- **Features**: Advanced keyphrase management with focus and additional keyphrases

### Old Version (All in One SEO Pack Pro v2.7.1)
- **Sites**: arsenalcore.com, mancitycore.com
- **Format**: Uses `meta` structure with `_aioseop_` prefixed fields
- **Features**: Combined keyphrase handling in a single field

## How to Configure

### Using the GUI

1. **Open the Configuration Tab**
   - Launch the WordPress Blog Automation GUI
   - Navigate to the "⚙️ Configuration" tab

2. **Select Your Domain**
   - Choose your target domain from the domain selector
   - This ensures the configuration is saved for the correct website

3. **Access SEO Plugin Settings**
   - In the configuration sidebar, click on "🔧 SEO Plugin Settings"
   - You'll see a dropdown with two options:
     - **New**: For All in One SEO Pro v4.7.3+
     - **Old**: For All in One SEO Pack Pro v2.7.1

4. **Select the Correct Version**
   - Choose the version that matches your WordPress site's plugin
   - The interface will show which sites use which version

5. **Save Configuration**
   - Click the "Save" button to store the setting
   - The configuration is saved to your domain-specific settings

### Manual Configuration

You can also manually set the SEO plugin version in your domain's `default.json` file:

```json
{
  "seo_plugin_version": "new",
  // ... other configuration options
}
```

Or for old plugin version:

```json
{
  "seo_plugin_version": "old",
  // ... other configuration options
}
```

## Technical Details

### New Plugin Format (v4.7.3+)

```json
{
  "aioseo_meta_data": {
    "title": "SEO optimized title",
    "description": "Meta description",
    "keyphrases": {
      "focus": {
        "keyphrase": "main keyword"
      },
      "additional": [
        {"keyphrase": "secondary keyword 1"},
        {"keyphrase": "secondary keyword 2"}
      ]
    }
  }
}
```

### Old Plugin Format (v2.7.1)

```json
{
  "meta": {
    "_aioseop_title": "SEO optimized title",
    "_aioseop_description": "Meta description",
    "_aioseop_keywords": "main keyword, secondary keyword 1, secondary keyword 2"
  }
}
```

## Benefits

- **Compatibility**: Works with both old and new plugin versions
- **No Data Loss**: Safely configure without risking existing SEO data
- **Domain-Specific**: Each website can have its own plugin version setting
- **Automatic Detection**: The system automatically uses the correct format based on your configuration

## Troubleshooting

### Configuration Not Saving
- Ensure you have selected the correct domain before configuring
- Check that the domain directory exists in the `configs` folder
- Verify write permissions for the configuration files

### SEO Metadata Not Appearing
- Confirm the plugin version setting matches your WordPress site
- Check the WordPress API credentials are correct
- Verify the All in One SEO plugin is active on your WordPress site

### Wrong Format Being Used
- Double-check the SEO plugin version setting in the configuration
- Ensure the domain-specific configuration is being loaded
- Check the automation logs for any error messages

## Migration Guide

If you're upgrading from an old plugin version to a new one:

1. **Backup Your Data**: Always backup your WordPress database before upgrading
2. **Update Plugin**: Upgrade the All in One SEO plugin on your WordPress site
3. **Change Configuration**: Update the SEO plugin version setting from "old" to "new"
4. **Test**: Run a test post to ensure the new format is working correctly

## Support

For additional support or questions about SEO plugin configuration:
- Check the main project documentation
- Review the automation logs for detailed error messages
- Test with the provided test script: `python3 test_seo_plugin_config.py`