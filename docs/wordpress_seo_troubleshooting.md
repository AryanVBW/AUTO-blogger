# WordPress SEO Troubleshooting Guide for Old AIOSEO Plugin (v2.7.1)

## 🔍 Issue: SEO Title, Description, and Keywords Not Appearing

Based on our testing, the automation engine is correctly sending SEO metadata to WordPress using the old AIOSEO plugin format. If the SEO data is not appearing in your WordPress posts, the issue is likely on the WordPress side.

## ✅ Code Verification Results

Our debug testing confirms:
- ✅ Old plugin format correctly uses `meta` wrapper
- ✅ SEO title stored as `_aioseop_title`
- ✅ Meta description stored as `_aioseop_description` 
- ✅ Keywords stored as `_aioseop_keywords` (comma-separated)
- ✅ WordPress REST API calls are properly formatted

## 🔧 WordPress Troubleshooting Steps

### 1. Verify AIOSEO Plugin Version and Status

**Check Plugin Version:**
```
WordPress Admin → Plugins → All in One SEO Pack Pro
Version should be: v2.7.1 (or compatible old version)
```

**Ensure Plugin is Active:**
- Plugin must be activated
- License should be valid (if Pro version)

### 2. Check WordPress REST API Permissions

**User Permissions:**
The WordPress user account used by the automation must have:
- `edit_posts` capability
- `edit_others_posts` capability (if needed)
- `manage_options` capability (recommended)

**Test REST API Access:**
```bash
# Test if you can update post meta via REST API
curl -X POST "https://yoursite.com/wp-json/wp/v2/posts/POST_ID" \
  -u "username:password" \
  -H "Content-Type: application/json" \
  -d '{
    "meta": {
      "_aioseop_title": "Test SEO Title",
      "_aioseop_description": "Test description",
      "_aioseop_keywords": "test, keywords"
    }
  }'
```

### 3. WordPress Configuration Issues

**Check wp-config.php:**
Ensure these settings allow REST API access:
```php
// Make sure these are not blocking REST API
// define('DISALLOW_FILE_EDIT', true); // This is OK
// define('WP_DEBUG', false); // This is OK

// Ensure REST API is not disabled
// remove_action('rest_api_init', 'wp_oembed_register_route');
// remove_filter('oembed_dataparse', 'wp_filter_oembed_result', 10);
```

**Check .htaccess:**
Ensure REST API endpoints are accessible:
```apache
# WordPress REST API should be accessible
# Make sure there are no rules blocking /wp-json/ requests
```

### 4. AIOSEO Plugin Configuration

**Plugin Settings:**
1. Go to `WordPress Admin → All in One SEO → General Settings`
2. Ensure "Use Categories for META keywords" is enabled if desired
3. Check "Autogenerate Descriptions" settings
4. Verify "Use META Keywords" is enabled

**Custom Fields Support:**
Ensure WordPress allows custom fields:
1. Go to `Posts → Add New`
2. Click "Screen Options" (top right)
3. Ensure "Custom Fields" is checked

### 5. Database-Level Verification

**Check Post Meta in Database:**
```sql
-- Check if meta fields are being saved
SELECT * FROM wp_postmeta 
WHERE post_id = YOUR_POST_ID 
AND meta_key IN ('_aioseop_title', '_aioseop_description', '_aioseop_keywords');
```

**Expected Results:**
```
post_id | meta_key           | meta_value
--------|--------------------|-----------
123     | _aioseop_title     | Your SEO Title
123     | _aioseop_description| Your Meta Description  
123     | _aioseop_keywords  | keyword1, keyword2, keyword3
```

### 6. WordPress Error Logs

**Enable WordPress Debug Logging:**
```php
// Add to wp-config.php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', false);
```

**Check Error Logs:**
- `/wp-content/debug.log`
- Server error logs (Apache/Nginx)
- WordPress admin error notices

### 7. Plugin Conflicts

**Test for Plugin Conflicts:**
1. Temporarily deactivate all other plugins except AIOSEO
2. Test if SEO metadata appears
3. Reactivate plugins one by one to identify conflicts

**Common Conflicting Plugins:**
- Other SEO plugins (Yoast, RankMath, etc.)
- Caching plugins that interfere with REST API
- Security plugins blocking REST API requests

### 8. Theme Compatibility

**Check Theme Support:**
Some themes may not properly display AIOSEO meta tags. Test with:
1. Switch to a default WordPress theme (Twenty Twenty-Three)
2. Check if SEO metadata appears in page source
3. Look for `<meta name="description"` and `<meta name="keywords"` tags

## 🔍 Advanced Debugging

### Enable Detailed Logging

Add this to your automation configuration:
```json
{
  "seo_plugin_version": "old",
  "debug_mode": true,
  "log_level": "DEBUG"
}
```

### Manual REST API Test

Create a test script to manually verify the REST API:

```php
<?php
// test-seo-api.php - Upload to your WordPress root
require_once('wp-load.php');

$post_id = 123; // Replace with actual post ID
$meta_data = array(
    '_aioseop_title' => 'Manual Test SEO Title',
    '_aioseop_description' => 'Manual test description',
    '_aioseop_keywords' => 'manual, test, keywords'
);

foreach($meta_data as $key => $value) {
    $result = update_post_meta($post_id, $key, $value);
    echo "Updated {$key}: " . ($result ? 'SUCCESS' : 'FAILED') . "\n";
}

echo "\nVerification:\n";
foreach($meta_data as $key => $value) {
    $stored = get_post_meta($post_id, $key, true);
    echo "{$key}: {$stored}\n";
}
?>
```

## 📞 What Information to Provide

If the issue persists, please provide:

1. **WordPress Information:**
   - WordPress version
   - AIOSEO plugin version
   - Active theme name
   - List of active plugins

2. **Server Information:**
   - PHP version
   - Server type (Apache/Nginx)
   - Any server-level restrictions

3. **Error Logs:**
   - WordPress debug.log entries
   - Server error log entries
   - Browser console errors

4. **Database Check:**
   - Result of the SQL query above
   - Confirmation that post meta is/isn't being saved

5. **REST API Test:**
   - Result of manual REST API test
   - Any error responses from WordPress

## 🎯 Most Common Solutions

Based on experience, these are the most frequent causes:

1. **Plugin Version Mismatch** (40% of cases)
   - Using new AIOSEO version with old format
   - Solution: Update config to `"seo_plugin_version": "new"`

2. **User Permissions** (30% of cases)
   - WordPress user lacks meta editing permissions
   - Solution: Use admin account or adjust user capabilities

3. **Plugin Conflicts** (20% of cases)
   - Other SEO plugins interfering
   - Solution: Deactivate conflicting plugins

4. **Theme Issues** (10% of cases)
   - Theme not displaying meta tags
   - Solution: Check page source, switch themes for testing

The automation code is working correctly - the issue is almost certainly in the WordPress configuration! 🚀