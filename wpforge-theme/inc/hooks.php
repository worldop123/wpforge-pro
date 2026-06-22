<?php
/**
 * WPForge Theme - Hooks System
 *
 * 提供丰富的动作钩子和过滤钩子，方便WPForge和其他插件扩展
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

// Exit if accessed directly.
if (!defined('ABSPATH')) {
    exit;
}

/**
 * ============================================
 * Action Hooks - 动作钩子
 * ============================================
 */

/**
 * Before header hook.
 *
 * @since 1.0.0
 */
function wpforge_before_header() {
    do_action('wpforge_before_header');
}

/**
 * Header hook.
 *
 * @since 1.0.0
 */
function wpforge_header() {
    do_action('wpforge_header');
}

/**
 * After header hook.
 *
 * @since 1.0.0
 */
function wpforge_after_header() {
    do_action('wpforge_after_header');
}

/**
 * Before content hook.
 *
 * @since 1.0.0
 */
function wpforge_before_content() {
    do_action('wpforge_before_content');
}

/**
 * Content hook.
 *
 * @since 1.0.0
 */
function wpforge_content() {
    do_action('wpforge_content');
}

/**
 * After content hook.
 *
 * @since 1.0.0
 */
function wpforge_after_content() {
    do_action('wpforge_after_content');
}

/**
 * Before sidebar hook.
 *
 * @since 1.0.0
 */
function wpforge_before_sidebar() {
    do_action('wpforge_before_sidebar');
}

/**
 * Sidebar hook.
 *
 * @since 1.0.0
 */
function wpforge_sidebar() {
    do_action('wpforge_sidebar');
}

/**
 * After sidebar hook.
 *
 * @since 1.0.0
 */
function wpforge_after_sidebar() {
    do_action('wpforge_after_sidebar');
}

/**
 * Before footer hook.
 *
 * @since 1.0.0
 */
function wpforge_before_footer() {
    do_action('wpforge_before_footer');
}

/**
 * Footer hook.
 *
 * @since 1.0.0
 */
function wpforge_footer() {
    do_action('wpforge_footer');
}

/**
 * After footer hook.
 *
 * @since 1.0.0
 */
function wpforge_after_footer() {
    do_action('wpforge_after_footer');
}

/**
 * Before post hook.
 *
 * @since 1.0.0
 */
function wpforge_before_post() {
    do_action('wpforge_before_post');
}

/**
 * Post hook.
 *
 * @since 1.0.0
 */
function wpforge_post() {
    do_action('wpforge_post');
}

/**
 * After post hook.
 *
 * @since 1.0.0
 */
function wpforge_after_post() {
    do_action('wpforge_after_post');
}

/**
 * Before product hook.
 *
 * @since 1.0.0
 */
function wpforge_before_product() {
    do_action('wpforge_before_product');
}

/**
 * Product hook.
 *
 * @since 1.0.0
 */
function wpforge_product() {
    do_action('wpforge_product');
}

/**
 * After product hook.
 *
 * @since 1.0.0
 */
function wpforge_after_product() {
    do_action('wpforge_after_product');
}

/**
 * Before page title hook.
 *
 * @since 1.0.0
 */
function wpforge_before_page_title() {
    do_action('wpforge_before_page_title');
}

/**
 * After page title hook.
 *
 * @since 1.0.0
 */
function wpforge_after_page_title() {
    do_action('wpforge_after_page_title');
}

/**
 * Before entry content hook.
 *
 * @since 1.0.0
 */
function wpforge_before_entry_content() {
    do_action('wpforge_before_entry_content');
}

/**
 * After entry content hook.
 *
 * @since 1.0.0
 */
function wpforge_after_entry_content() {
    do_action('wpforge_after_entry_content');
}

/**
 * Before comments hook.
 *
 * @since 1.0.0
 */
function wpforge_before_comments() {
    do_action('wpforge_before_comments');
}

/**
 * After comments hook.
 *
 * @since 1.0.0
 */
function wpforge_after_comments() {
    do_action('wpforge_after_comments');
}

/**
 * ============================================
 * Filter Hooks - 过滤钩子
 * ============================================
 */

/**
 * Filter CSS variables.
 *
 * @since 1.0.0
 * @param array $variables CSS variables.
 * @return array Modified CSS variables.
 */
function wpforge_css_variables($variables) {
    return apply_filters('wpforge_css_variables', $variables);
}

/**
 * Filter body classes.
 *
 * @since 1.0.0
 * @param array $classes Body classes.
 * @return array Modified body classes.
 */
function wpforge_body_classes_filter($classes) {
    return apply_filters('wpforge_body_classes', $classes);
}

/**
 * Filter post classes.
 *
 * @since 1.0.0
 * @param array $classes Post classes.
 * @return array Modified post classes.
 */
function wpforge_post_classes_filter($classes) {
    return apply_filters('wpforge_post_classes', $classes);
}

/**
 * Filter breadcrumb items.
 *
 * @since 1.0.0
 * @param array $items Breadcrumb items.
 * @return array Modified breadcrumb items.
 */
function wpforge_breadcrumb_items($items) {
    return apply_filters('wpforge_breadcrumb_items', $items);
}

/**
 * Filter related posts args.
 *
 * @since 1.0.0
 * @param array $args Related posts query args.
 * @return array Modified query args.
 */
function wpforge_related_posts_args($args) {
    return apply_filters('wpforge_related_posts_args', $args);
}

/**
 * Filter schema data.
 *
 * @since 1.0.0
 * @param array $data Schema data.
 * @param string $type Schema type.
 * @return array Modified schema data.
 */
function wpforge_schema_data($data, $type) {
    return apply_filters('wpforge_schema_data', $data, $type);
}

/**
 * Filter SEO title.
 *
 * @since 1.0.0
 * @param string $title SEO title.
 * @return string Modified SEO title.
 */
function wpforge_seo_title($title) {
    return apply_filters('wpforge_seo_title', $title);
}

/**
 * Filter SEO description.
 *
 * @since 1.0.0
 * @param string $description SEO description.
 * @return string Modified SEO description.
 */
function wpforge_seo_description($description) {
    return apply_filters('wpforge_seo_description', $description);
}

/**
 * Filter performance settings.
 *
 * @since 1.0.0
 * @param array $settings Performance settings.
 * @return array Modified performance settings.
 */
function wpforge_performance_settings($settings) {
    return apply_filters('wpforge_performance_settings', $settings);
}

/**
 * Filter excerpt length.
 *
 * @since 1.0.0
 * @param int $length Excerpt length.
 * @return int Modified excerpt length.
 */
function wpforge_excerpt_length_filter($length) {
    return apply_filters('wpforge_excerpt_length', $length);
}

/**
 * Filter excerpt more.
 *
 * @since 1.0.0
 * @param string $more Excerpt more text.
 * @return string Modified excerpt more text.
 */
function wpforge_excerpt_more_filter($more) {
    return apply_filters('wpforge_excerpt_more', $more);
}

/**
 * Filter read more text.
 *
 * @since 1.0.0
 * @param string $text Read more text.
 * @return string Modified read more text.
 */
function wpforge_read_more_text($text) {
    return apply_filters('wpforge_read_more_text', $text);
}

/**
 * Filter copyright text.
 *
 * @since 1.0.0
 * @param string $text Copyright text.
 * @return string Modified copyright text.
 */
function wpforge_copyright_text($text) {
    return apply_filters('wpforge_copyright_text', $text);
}

/**
 * Filter header classes.
 *
 * @since 1.0.0
 * @param array $classes Header classes.
 * @return array Modified header classes.
 */
function wpforge_header_classes($classes) {
    return apply_filters('wpforge_header_classes', $classes);
}

/**
 * Filter footer classes.
 *
 * @since 1.0.0
 * @param array $classes Footer classes.
 * @return array Modified footer classes.
 */
function wpforge_footer_classes($classes) {
    return apply_filters('wpforge_footer_classes', $classes);
}

/**
 * Filter content width.
 *
 * @since 1.0.0
 * @param int $width Content width.
 * @return int Modified content width.
 */
function wpforge_content_width_filter($width) {
    return apply_filters('wpforge_content_width', $width);
}

/**
 * Filter sidebar widget areas.
 *
 * @since 1.0.0
 * @param array $sidebars Sidebar widget areas.
 * @return array Modified sidebars.
 */
function wpforge_sidebar_widget_areas($sidebars) {
    return apply_filters('wpforge_sidebar_widget_areas', $sidebars);
}

/**
 * Filter footer widget areas.
 *
 * @since 1.0.0
 * @param array $sidebars Footer widget areas.
 * @return array Modified sidebars.
 */
function wpforge_footer_widget_areas($sidebars) {
    return apply_filters('wpforge_footer_widget_areas', $sidebars);
}

/**
 * Filter theme defaults.
 *
 * @since 1.0.0
 * @param array $defaults Theme defaults.
 * @return array Modified defaults.
 */
function wpforge_theme_defaults($defaults) {
    return apply_filters('wpforge_theme_defaults', $defaults);
}

/**
 * Filter presets.
 *
 * @since 1.0.0
 * @param array $presets Theme presets.
 * @return array Modified presets.
 */
function wpforge_theme_presets($presets) {
    return apply_filters('wpforge_theme_presets', $presets);
}

/**
 * ============================================
 * Default Hook Implementations - 默认钩子实现
 * ============================================
 */

/**
 * Default header implementation.
 *
 * @since 1.0.0
 */
function wpforge_default_header() {
    get_template_part('template-parts/header/header');
}
add_action('wpforge_header', 'wpforge_default_header');

/**
 * Default footer implementation.
 *
 * @since 1.0.0
 */
function wpforge_default_footer() {
    get_template_part('template-parts/footer/footer');
}
add_action('wpforge_footer', 'wpforge_default_footer');

/**
 * Default sidebar implementation.
 *
 * @since 1.0.0
 */
function wpforge_default_sidebar() {
    if (is_active_sidebar('sidebar-primary')) {
        dynamic_sidebar('sidebar-primary');
    }
}
add_action('wpforge_sidebar', 'wpforge_default_sidebar');

/**
 * Default breadcrumb implementation.
 *
 * @since 1.0.0
 */
function wpforge_default_breadcrumb() {
    if (function_exists('wpforge_breadcrumb')) {
        wpforge_breadcrumb();
    }
}
add_action('wpforge_before_content', 'wpforge_default_breadcrumb', 10);

/**
 * Default page title implementation.
 *
 * @since 1.0.0
 */
function wpforge_default_page_title() {
    if (is_page() || is_single()) {
        return;
    }

    if (is_home() && !is_front_page()) {
        echo '<h1 class="wpforge-page-title">' . esc_html(get_the_title(get_option('page_for_posts'))) . '</h1>';
    } elseif (is_category()) {
        echo '<h1 class="wpforge-page-title">' . single_cat_title('', false) . '</h1>';
    } elseif (is_tag()) {
        echo '<h1 class="wpforge-page-title">' . single_tag_title('', false) . '</h1>';
    } elseif (is_author()) {
        echo '<h1 class="wpforge-page-title">' . get_the_author() . '</h1>';
    } elseif (is_date()) {
        echo '<h1 class="wpforge-page-title">' . get_the_archive_title() . '</h1>';
    } elseif (is_search()) {
        echo '<h1 class="wpforge-page-title">';
        printf(
            /* translators: %s: Search query */
            esc_html__('Search Results for: %s', 'wpforge-theme'),
            '<span>' . get_search_query() . '</span>'
        );
        echo '</h1>';
    } elseif (is_404()) {
        echo '<h1 class="wpforge-page-title">' . esc_html__('Page Not Found', 'wpforge-theme') . '</h1>';
    }
}
add_action('wpforge_before_content', 'wpforge_default_page_title', 20);

/**
 * Default post navigation implementation.
 *
 * @since 1.0.0
 */
function wpforge_default_post_navigation() {
    if (is_single() && get_theme_mod('wpforge_single_show_nav', true)) {
        the_post_navigation(array(
            'prev_text' => '<span class="nav-subtitle">' . esc_html__('Previous', 'wpforge-theme') . '</span> <span class="nav-title">%title</span>',
            'next_text' => '<span class="nav-subtitle">' . esc_html__('Next', 'wpforge-theme') . '</span> <span class="nav-title">%title</span>',
        ));
    }
}
add_action('wpforge_after_post', 'wpforge_default_post_navigation', 10);

/**
 * Default related posts implementation.
 *
 * @since 1.0.0
 */
function wpforge_default_related_posts() {
    if (is_single() && get_theme_mod('wpforge_single_show_related', true)) {
        get_template_part('template-parts/post/related-posts');
    }
}
add_action('wpforge_after_post', 'wpforge_default_related_posts', 20);

/**
 * Default author box implementation.
 *
 * @since 1.0.0
 */
function wpforge_default_author_box() {
    if (is_single() && get_theme_mod('wpforge_single_show_author_box', false)) {
        get_template_part('template-parts/post/author-box');
    }
}
add_action('wpforge_after_post', 'wpforge_default_author_box', 30);

/**
 * Default back to top implementation.
 *
 * @since 1.0.0
 */
function wpforge_default_back_to_top() {
    if (get_theme_mod('wpforge_back_to_top', true)) {
        echo '<a href="#" class="wpforge-back-to-top" aria-label="' . esc_attr__('Back to top', 'wpforge-theme') . '">';
        echo '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"></polyline></svg>';
        echo '</a>';
    }
}
add_action('wpforge_after_footer', 'wpforge_default_back_to_top');
