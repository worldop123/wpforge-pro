<?php
/**
 * WPForge Theme - Performance Optimization Module
 *
 * 内置性能优化功能，无需额外优化插件
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

// Exit if accessed directly.
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Initialize performance module.
 *
 * @since 1.0.0
 */
function wpforge_performance_init() {
    // Disable emojis.
    if (get_theme_mod('wpforge_disable_emojis', true)) {
        add_action('init', 'wpforge_disable_emojis');
    }

    // Disable embeds.
    if (get_theme_mod('wpforge_disable_embeds', true)) {
        add_action('init', 'wpforge_disable_embeds', 9999);
    }

    // Remove WP version.
    if (get_theme_mod('wpforge_remove_wp_version', true)) {
        add_filter('the_generator', '__return_empty_string');
        remove_action('wp_head', 'wp_generator');
    }

    // Disable XML-RPC.
    if (get_theme_mod('wpforge_disable_xmlrpc', true)) {
        add_filter('xmlrpc_enabled', '__return_false');
        remove_action('wp_head', 'rsd_link');
        remove_action('wp_head', 'wlwmanifest_link');
    }

    // Lazy load images.
    if (get_theme_mod('wpforge_lazy_load_images', true)) {
        add_filter('wp_lazy_loading_enabled', '__return_true');
        add_filter('img_tag_add_lazy_load', 'wpforge_add_lazy_load_to_images', 10, 2);
    }

    // Defer JS.
    if (get_theme_mod('wpforge_defer_js', true)) {
        add_filter('script_loader_tag', 'wpforge_defer_scripts', 10, 3);
    }

    // Remove shortlink.
    remove_action('wp_head', 'wp_shortlink_wp_head', 10, 0);

    // Remove REST API link.
    remove_action('wp_head', 'rest_output_link_wp_head', 10);
    remove_action('template_redirect', 'rest_output_link_header', 11, 0);

    // DNS prefetch and preconnect.
    add_action('wp_head', 'wpforge_resource_hints', 1);

    // Clean up head.
    add_action('init', 'wpforge_cleanup_wp_head');
}
add_action('after_setup_theme', 'wpforge_performance_init');

/**
 * Disable emojis.
 *
 * @since 1.0.0
 */
function wpforge_disable_emojis() {
    remove_action('wp_head', 'print_emoji_detection_script', 7);
    remove_action('admin_print_scripts', 'print_emoji_detection_script');
    remove_action('wp_print_styles', 'print_emoji_styles');
    remove_action('admin_print_styles', 'print_emoji_styles');
    remove_filter('the_content_feed', 'wp_staticize_emoji');
    remove_filter('comment_text_rss', 'wp_staticize_emoji');
    remove_filter('wp_mail', 'wp_staticize_emoji_for_email');
    add_filter('tiny_mce_plugins', 'wpforge_disable_emojis_tinymce');
    add_filter('wp_resource_hints', 'wpforge_disable_emojis_remove_dns_prefetch', 10, 2);
}

/**
 * Disable emojis in TinyMCE.
 *
 * @since 1.0.0
 * @param array $plugins TinyMCE plugins.
 * @return array Modified plugins.
 */
function wpforge_disable_emojis_tinymce($plugins) {
    if (is_array($plugins)) {
        return array_diff($plugins, array('wpemoji'));
    }
    return array();
}

/**
 * Remove emoji CDN hostname from DNS prefetch hints.
 *
 * @since 1.0.0
 * @param array $urls URLs to print for resource hints.
 * @param string $relation_type The relation type the URLs are printed for.
 * @return array Modified URLs.
 */
function wpforge_disable_emojis_remove_dns_prefetch($urls, $relation_type) {
    if ('dns-prefetch' === $relation_type) {
        $emoji_svg_url = apply_filters('emoji_svg_url', 'https://s.w.org/images/core/emoji/2/svg/');
        $urls = array_diff($urls, array($emoji_svg_url));
    }
    return $urls;
}

/**
 * Disable embeds.
 *
 * @since 1.0.0
 */
function wpforge_disable_embeds() {
    // Remove the REST API endpoint.
    remove_action('rest_api_init', 'wp_oembed_register_route');

    // Turn off oEmbed auto discovery.
    add_filter('embed_oembed_discover', '__return_false');

    // Don't filter oEmbed results.
    remove_filter('oembed_dataparse', 'wp_filter_oembed_result', 10);

    // Remove oEmbed discovery links.
    remove_action('wp_head', 'wp_oembed_add_discovery_links');

    // Remove oEmbed-specific JavaScript from the front-end and back-end.
    remove_action('wp_head', 'wp_oembed_add_host_js');

    // Remove all embeds rewrite rules.
    add_filter('rewrite_rules_array', 'wpforge_disable_embeds_rewrites');

    // Remove filter of the oEmbed result before any HTTP requests are made.
    remove_filter('pre_oembed_result', 'wp_filter_pre_oembed_result', 10);
}

/**
 * Remove embeds rewrite rules.
 *
 * @since 1.0.0
 * @param array $rules Rewrite rules.
 * @return array Modified rewrite rules.
 */
function wpforge_disable_embeds_rewrites($rules) {
    foreach ($rules as $rule => $rewrite) {
        if (false !== strpos($rewrite, 'embed=true')) {
            unset($rules[$rule]);
        }
    }
    return $rules;
}

/**
 * Add lazy load to images.
 *
 * @since 1.0.0
 * @param string $image Image HTML.
 * @param string $context Context.
 * @return string Modified image HTML.
 */
function wpforge_add_lazy_load_to_images($image, $context) {
    // Don't lazy load in admin.
    if (is_admin()) {
        return $image;
    }

    // Don't lazy load if already has loading attribute.
    if (false !== strpos($image, 'loading=')) {
        return $image;
    }

    // Add loading="lazy" attribute.
    $image = str_replace('<img ', '<img loading="lazy" ', $image);

    return $image;
}

/**
 * Defer scripts.
 *
 * @since 1.0.0
 * @param string $tag Script tag.
 * @param string $handle Script handle.
 * @param string $src Script source.
 * @return string Modified script tag.
 */
function wpforge_defer_scripts($tag, $handle, $src) {
    // Don't defer in admin.
    if (is_admin()) {
        return $tag;
    }

    // Skip certain scripts.
    $skip_scripts = apply_filters('wpforge_defer_skip_scripts', array(
        'jquery-core',
        'jquery-migrate',
        'wp-embed',
    ));

    if (in_array($handle, $skip_scripts, true)) {
        return $tag;
    }

    // Don't defer if already has defer or async.
    if (false !== strpos($tag, ' defer') || false !== strpos($tag, ' async')) {
        return $tag;
    }

    // Add defer attribute.
    $tag = str_replace('<script ', '<script defer ', $tag);

    return $tag;
}

/**
 * Add resource hints (DNS prefetch, preconnect).
 *
 * @since 1.0.0
 */
function wpforge_resource_hints() {
    // DNS prefetch for common domains.
    $dns_prefetch = apply_filters('wpforge_dns_prefetch', array(
        '//fonts.googleapis.com',
        '//fonts.gstatic.com',
        '//s.w.org',
    ));

    foreach ($dns_prefetch as $domain) {
        echo '<link rel="dns-prefetch" href="' . esc_url($domain) . '">' . "\n";
    }

    // Preconnect for critical domains.
    $preconnect = apply_filters('wpforge_preconnect', array());

    foreach ($preconnect as $domain) {
        echo '<link rel="preconnect" href="' . esc_url($domain) . '" crossorigin>' . "\n";
    }

    // Preload critical resources.
    $preload = apply_filters('wpforge_preload', array());

    foreach ($preload as $resource) {
        if (isset($resource['href'], $resource['as'])) {
            $attributes = '';
            foreach ($resource as $key => $value) {
                if ('href' === $key || 'as' === $key) {
                    continue;
                }
                $attributes .= ' ' . esc_attr($key) . '="' . esc_attr($value) . '"';
            }
            echo '<link rel="preload" href="' . esc_url($resource['href']) . '" as="' . esc_attr($resource['as']) . '"' . $attributes . '>' . "\n";
        }
    }
}

/**
 * Clean up WordPress head.
 *
 * @since 1.0.0
 */
function wpforge_cleanup_wp_head() {
    // Remove feed links.
    remove_action('wp_head', 'feed_links', 2);
    remove_action('wp_head', 'feed_links_extra', 3);

    // Remove index link.
    remove_action('wp_head', 'index_rel_link');

    // Remove parent post link.
    remove_action('wp_head', 'parent_post_rel_link', 10, 0);

    // Remove start link.
    remove_action('wp_head', 'start_post_rel_link', 10, 0);

    // Remove adjacent posts links.
    remove_action('wp_head', 'adjacent_posts_rel_link', 10, 0);
    remove_action('wp_head', 'adjacent_posts_rel_link_wp_head', 10, 0);

    // Remove canonical (we handle it in SEO module).
    remove_action('wp_head', 'rel_canonical');
}

/**
 * Add browser caching headers via .htaccess rules.
 *
 * Note: This is a helper function to generate .htaccess rules.
 * Actual implementation would need to write to .htaccess.
 *
 * @since 1.0.0
 * @return string .htaccess rules.
 */
function wpforge_get_browser_caching_rules() {
    $rules = array(
        '# BEGIN WPForge Browser Caching',
        '<IfModule mod_expires.c>',
        'ExpiresActive On',
        'ExpiresByType image/jpg "access plus 1 year"',
        'ExpiresByType image/jpeg "access plus 1 year"',
        'ExpiresByType image/gif "access plus 1 year"',
        'ExpiresByType image/png "access plus 1 year"',
        'ExpiresByType image/webp "access plus 1 year"',
        'ExpiresByType image/svg+xml "access plus 1 year"',
        'ExpiresByType image/x-icon "access plus 1 year"',
        'ExpiresByType text/css "access plus 1 month"',
        'ExpiresByType application/pdf "access plus 1 month"',
        'ExpiresByType text/javascript "access plus 1 month"',
        'ExpiresByType application/javascript "access plus 1 month"',
        'ExpiresByType application/x-javascript "access plus 1 month"',
        'ExpiresByType text/html "access plus 0 seconds"',
        'ExpiresByType application/xhtml+xml "access plus 0 seconds"',
        'ExpiresByType application/xml "access plus 0 seconds"',
        'ExpiresByType application/json "access plus 0 seconds"',
        'ExpiresByType application/ld+json "access plus 0 seconds"',
        'ExpiresByType application/manifest+json "access plus 1 week"',
        'ExpiresByType application/rss+xml "access plus 1 hour"',
        'ExpiresByType application/atom+xml "access plus 1 hour"',
        'ExpiresByType text/x-component "access plus 1 month"',
        'ExpiresByType font/ttf "access plus 1 year"',
        'ExpiresByType font/otf "access plus 1 year"',
        'ExpiresByType font/woff "access plus 1 year"',
        'ExpiresByType font/woff2 "access plus 1 year"',
        'ExpiresByType application/font-woff "access plus 1 year"',
        'ExpiresByType application/vnd.ms-fontobject "access plus 1 year"',
        'ExpiresByType application/x-font-ttf "access plus 1 year"',
        'ExpiresByType application/x-font-opentype "access plus 1 year"',
        'ExpiresByType audio/ogg "access plus 1 year"',
        'ExpiresByType video/mp4 "access plus 1 year"',
        'ExpiresByType video/ogg "access plus 1 year"',
        'ExpiresByType video/webm "access plus 1 year"',
        'ExpiresByType application/x-shockwave-flash "access plus 1 month"',
        '</IfModule>',
        '# END WPForge Browser Caching',
    );

    return implode("\n", $rules);
}

/**
 * Add Gzip compression rules via .htaccess.
 *
 * @since 1.0.0
 * @return string .htaccess rules.
 */
function wpforge_get_gzip_rules() {
    $rules = array(
        '# BEGIN WPForge Gzip Compression',
        '<IfModule mod_deflate.c>',
        'AddOutputFilterByType DEFLATE text/plain',
        'AddOutputFilterByType DEFLATE text/html',
        'AddOutputFilterByType DEFLATE text/xml',
        'AddOutputFilterByType DEFLATE text/css',
        'AddOutputFilterByType DEFLATE text/javascript',
        'AddOutputFilterByType DEFLATE application/xml',
        'AddOutputFilterByType DEFLATE application/xhtml+xml',
        'AddOutputFilterByType DEFLATE application/rss+xml',
        'AddOutputFilterByType DEFLATE application/javascript',
        'AddOutputFilterByType DEFLATE application/x-javascript',
        'AddOutputFilterByType DEFLATE application/json',
        'AddOutputFilterByType DEFLATE application/ld+json',
        'AddOutputFilterByType DEFLATE application/manifest+json',
        'AddOutputFilterByType DEFLATE application/vnd.ms-fontobject',
        'AddOutputFilterByType DEFLATE application/x-font-ttf',
        'AddOutputFilterByType DEFLATE application/x-font-opentype',
        'AddOutputFilterByType DEFLATE font/opentype',
        'AddOutputFilterByType DEFLATE font/otf',
        'AddOutputFilterByType DEFLATE font/ttf',
        'AddOutputFilterByType DEFLATE font/woff',
        'AddOutputFilterByType DEFLATE font/woff2',
        'AddOutputFilterByType DEFLATE image/svg+xml',
        'AddOutputFilterByType DEFLATE image/x-icon',
        '</IfModule>',
        '# END WPForge Gzip Compression',
    );

    return implode("\n", $rules);
}

/**
 * Optimize image sizes.
 *
 * @since 1.0.0
 * @param array $sizes Image sizes.
 * @return array Modified image sizes.
 */
function wpforge_optimize_image_sizes($sizes) {
    // Remove unused image sizes.
    $unused_sizes = apply_filters('wpforge_unused_image_sizes', array(
        'medium_large',
        '1536x1536',
        '2048x2048',
    ));

    foreach ($unused_sizes as $size) {
        if (isset($sizes[$size])) {
            unset($sizes[$size]);
        }
    }

    return $sizes;
}
add_filter('intermediate_image_sizes_advanced', 'wpforge_optimize_image_sizes');

/**
 * Add WebP support.
 *
 * @since 1.0.0
 * @param array $mime_types MIME types.
 * @return array Modified MIME types.
 */
function wpforge_add_webp_support($mime_types) {
    $mime_types['webp'] = 'image/webp';
    return $mime_types;
}
add_filter('mime_types', 'wpforge_add_webp_support');

/**
 * Disable jQuery Migrate.
 *
 * @since 1.0.0
 * @param WP_Scripts $scripts WP_Scripts object.
 */
function wpforge_disable_jquery_migrate($scripts) {
    if (!is_admin() && isset($scripts->registered['jquery'])) {
        $script = $scripts->registered['jquery'];
        if ($script->deps) {
            $script->deps = array_diff($script->deps, array('jquery-migrate'));
        }
    }
}
add_action('wp_default_scripts', 'wpforge_disable_jquery_migrate');

/**
 * Control heartbeat API frequency.
 *
 * @since 1.0.0
 * @param array $settings Heartbeat settings.
 * @return array Modified settings.
 */
function wpforge_heartbeat_settings($settings) {
    $heartbeat_frequency = get_theme_mod('wpforge_heartbeat_frequency', 60);
    $settings['interval'] = absint($heartbeat_frequency);
    return $settings;
}
add_filter('heartbeat_settings', 'wpforge_heartbeat_settings');

/**
 * Limit post revisions.
 *
 * @since 1.0.0
 * @param int $num Number of revisions.
 * @return int Modified number.
 */
function wpforge_limit_post_revisions($num) {
    $revision_limit = get_theme_mod('wpforge_revision_limit', 10);
    return absint($revision_limit);
}
add_filter('wp_revisions_to_keep', 'wpforge_limit_post_revisions');

/**
 * Disable comment reply JS on non-singular pages.
 *
 * @since 1.0.0
 */
function wpforge_optimize_comment_reply_js() {
    if (!is_singular() || !comments_open() || !get_option('thread_comments')) {
        wp_dequeue_script('comment-reply');
    }
}
add_action('wp_enqueue_scripts', 'wpforge_optimize_comment_reply_js', 100);

/**
 * Optimize WooCommerce scripts and styles.
 *
 * Only load WooCommerce assets on WooCommerce pages.
 *
 * @since 1.0.0
 */
function wpforge_optimize_woocommerce_assets() {
    if (!function_exists('is_woocommerce')) {
        return;
    }

    if (!is_woocommerce() && !is_cart() && !is_checkout() && !is_account_page() && !is_product()) {
        // Dequeue WooCommerce styles.
        wp_dequeue_style('woocommerce-general');
        wp_dequeue_style('woocommerce-layout');
        wp_dequeue_style('woocommerce-smallscreen');

        // Dequeue WooCommerce scripts.
        wp_dequeue_script('wc-cart-fragments');
        wp_dequeue_script('woocommerce');
        wp_dequeue_script('wc-add-to-cart');
    }
}
add_action('wp_enqueue_scripts', 'wpforge_optimize_woocommerce_assets', 999);

/**
 * Add critical CSS inline.
 *
 * @since 1.0.0
 */
function wpforge_critical_css() {
    $critical_css = get_theme_mod('wpforge_critical_css', '');

    if ($critical_css) {
        echo '<style id="wpforge-critical-css">' . wp_strip_all_tags($critical_css) . '</style>' . "\n";
    }
}
add_action('wp_head', 'wpforge_critical_css', 2);

/**
 * Lazy load iframes.
 *
 * @since 1.0.0
 * @param string $content Post content.
 * @return string Modified content.
 */
function wpforge_lazy_load_iframes($content) {
    if (is_admin() || is_feed() || is_preview()) {
        return $content;
    }

    // Add loading="lazy" to iframes.
    $content = preg_replace('/<iframe /i', '<iframe loading="lazy" ', $content);

    return $content;
}
add_filter('the_content', 'wpforge_lazy_load_iframes', 20);

/**
 * Add image width and height attributes.
 *
 * Helps prevent CLS (Cumulative Layout Shift).
 *
 * @since 1.0.0
 * @param string $content Post content.
 * @return string Modified content.
 */
function wpforge_add_image_dimensions($content) {
    if (is_admin() || is_feed()) {
        return $content;
    }

    // Find all images without width/height attributes.
    preg_match_all('/<img [^>]+>/', $content, $images);

    foreach ($images[0] as $image) {
        // Skip if already has width and height.
        if (strpos($image, 'width=') !== false && strpos($image, 'height=') !== false) {
            continue;
        }

        // Get image src.
        preg_match('/src="([^"]+)"/', $image, $src_match);
        if (empty($src_match[1])) {
            continue;
        }

        $image_src = $src_match[1];

        // Try to get image size from URL.
        $image_id = attachment_url_to_postid($image_src);
        if ($image_id) {
            $image_meta = wp_get_attachment_metadata($image_id);
            if ($image_meta && isset($image_meta['width'], $image_meta['height'])) {
                $new_image = str_replace('<img ', '<img width="' . $image_meta['width'] . '" height="' . $image_meta['height'] . '" ', $image);
                $content = str_replace($image, $new_image, $content);
            }
        }
    }

    return $content;
}
add_filter('the_content', 'wpforge_add_image_dimensions', 10);

/**
 * Disable password strength meter on non-account pages.
 *
 * @since 1.0.0
 */
function wpforge_disable_password_strength_meter() {
    if (!is_account_page() && !is_checkout()) {
        wp_dequeue_script('wc-password-strength-meter');
    }
}
add_action('wp_enqueue_scripts', 'wpforge_disable_password_strength_meter', 999);

/**
 * Get performance stats.
 *
 * @since 1.0.0
 * @return array Performance statistics.
 */
function wpforge_get_performance_stats() {
    $stats = array(
        'css_optimized'      => get_theme_mod('wpforge_disable_emojis', true) && get_theme_mod('wpforge_disable_embeds', true),
        'js_optimized'       => get_theme_mod('wpforge_defer_js', true),
        'images_optimized'   => get_theme_mod('wpforge_lazy_load_images', true),
        'wp_cleaned_up'      => get_theme_mod('wpforge_remove_wp_version', true) && get_theme_mod('wpforge_disable_xmlrpc', true),
        'lazy_load_enabled'  => get_theme_mod('wpforge_lazy_load_images', true),
        'emojis_disabled'    => get_theme_mod('wpforge_disable_emojis', true),
        'embeds_disabled'    => get_theme_mod('wpforge_disable_embeds', true),
        'xmlrpc_disabled'    => get_theme_mod('wpforge_disable_xmlrpc', true),
        'wp_version_hidden'  => get_theme_mod('wpforge_remove_wp_version', true),
        'jquery_migrate_off' => true, // Always disabled.
    );

    // Calculate performance score.
    $score = 0;
    $total = count($stats);

    foreach ($stats as $enabled) {
        if ($enabled) {
            $score++;
        }
    }

    $stats['performance_score'] = round(($score / $total) * 100);

    return $stats;
}
