# Old AIOSEO Plugin (v2.7.1) SEO Metadata Troubleshooting Guide

## ✅ Code Verification Complete

Our testing confirms that the automation engine **correctly sends SEO metadata** for the old AIOSEO plugin version 2.7.1. The system properly:

- Detects `seo_plugin_version: "old"` in configuration
- Structures SEO data using the `meta` field with:
  - `_aioseop_title`: SEO Title
  - `_aioseop_description`: SEO Description  
  - `_aioseop_keywords`: Comma-separated keywords
- Sends the data via WordPress REST API POST request

## 🔍 WordPress-Side Issues to Check

Since the automation code is working correctly, the issue is likely on the WordPress side:

### 1. Plugin Version Verification
```bash
# Check your actual AIOSEO plugin version
# Go to WordPress Admin → Plugins → All in One SEO Pack
# Verify it shows exactly "Version 2.7.1"
```

### 2. WordPress REST API Permissions
```bash
# Test REST API access manually:
curl -X GET "https://arsenalcore.com/wp-json/wp/v2/posts/[POST_ID]" \
  -u "Vivek:4mVV MLfs 8abN 0Efi cuIT 5dds"

# Check if meta fields are visible in response
```

### 3. User Permissions Check
- Ensure user "Vivek" has `edit_posts` capability
- Verify user can edit custom fields/meta data
- Check if user has AIOSEO plugin permissions

### 4. Plugin Configuration
```bash
# In WordPress Admin, check:
# 1. All in One SEO → General Settings
# 2. Ensure "Use Custom Field for SEO Title" is enabled
# 3. Verify "Use Custom Field for SEO Description" is enabled
# 4. Check "Use Custom Field for SEO Keywords" is enabled
```

### 5. Database Verification
```sql
-- Check if meta fields are being saved:
SELECT post_id, meta_key, meta_value 
FROM wp_postmeta 
WHERE meta_key IN ('_aioseop_title', '_aioseop_description', '_aioseop_keywords')
AND post_id = [YOUR_POST_ID];
```

### 6. WordPress Error Logs
```bash
# Check WordPress error logs:
tail -f /path/to/wordpress/wp-content/debug.log

# Or enable WordPress debugging in wp-config.php:
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
```

### 7. Plugin Conflicts
```bash
# Test with minimal plugins:
# 1. Deactivate all plugins except AIOSEO v2.7.1
# 2. Test if SEO data appears
# 3. Reactivate plugins one by one to find conflicts
```

### 8. Theme Compatibility
```bash
# Switch to default WordPress theme:
# 1. Activate Twenty Twenty-Three theme
# 2. Test if SEO metadata appears
# 3. Check if custom theme blocks meta field display
```

### 9. REST API Meta Field Registration
```php
// Add to theme's functions.php to expose meta fields:
add_action('rest_api_init', function() {
    register_rest_field('post', '_aioseop_title', array(
        'get_callback' => function($post) {
            return get_post_meta($post['id'], '_aioseop_title', true);
        },
        'update_callback' => function($value, $post) {
            return update_post_meta($post->ID, '_aioseop_title', $value);
        }
    ));
    
    register_rest_field('post', '_aioseop_description', array(
        'get_callback' => function($post) {
            return get_post_meta($post['id'], '_aioseop_description', true);
        },
        'update_callback' => function($value, $post) {
            return update_post_meta($post->ID, '_aioseop_description', $value);
        }
    ));
    
    register_rest_field('post', '_aioseop_keywords', array(
        'get_callback' => function($post) {
            return get_post_meta($post['id'], '_aioseop_keywords', true);
        },
        'update_callback' => function($value, $post) {
            return update_post_meta($post->ID, '_aioseop_keywords', $value);
        }
    ));
});
```

### 10. Manual Verification Steps

1. **Create a test post manually** in WordPress admin
2. **Add SEO data** using AIOSEO interface
3. **Check database** to see how AIOSEO stores the data
4. **Compare format** with what automation sends

### 11. Alternative Debugging

```php
// Add to theme's functions.php for debugging:
add_action('wp_insert_post', function($post_id, $post, $update) {
    if ($update) {
        error_log("Post updated: $post_id");
        $meta = get_post_meta($post_id);
        error_log("Meta data: " . print_r($meta, true));
    }
}, 10, 3);
```

## 🎯 Most Likely Causes

1. **Plugin Version Mismatch**: AIOSEO is not actually v2.7.1
2. **REST API Meta Registration**: WordPress not allowing meta field updates via REST API
3. **User Permissions**: Insufficient permissions to update custom fields
4. **Plugin Configuration**: AIOSEO not configured to use custom fields

## 🚀 Next Steps

1. **Verify plugin version** in WordPress admin
2. **Check database** for meta field presence
3. **Test REST API permissions** manually
4. **Enable WordPress debugging** and check logs
5. **Add REST API meta registration** code if needed

## 📞 Support Information

If SEO data still doesn't appear after these checks:
- The automation code is working correctly
- The issue is WordPress configuration-related
- Focus troubleshooting on WordPress/AIOSEO setup
- Consider updating to newer AIOSEO version if possible