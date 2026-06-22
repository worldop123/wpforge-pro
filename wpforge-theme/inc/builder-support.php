<?php
/**
 * WPForge Theme - Page Builder Support
 *
 * 深度支持Elementor、Bricks Builder等页面构建器
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

// Exit if accessed directly.
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Initialize page builder support.
 *
 * @since 1.0.0
 */
function wpforge_builder_support_init() {
    // Elementor support.
    if (did_action('elementor/loaded')) {
        add_action('elementor/init', 'wpforge_elementor_support');
    }

    // Bricks Builder support.
    if (defined('BRICKS_VERSION')) {
        add_action('init', 'wpforge_bricks_support');
    }

    // Gutenberg support.
    add_theme_support('align-wide');
    add_theme_support('responsive-embeds');
    add_theme_support('wp-block-styles');

    // Add page templates for builders.
    add_filter('theme_page_templates', 'wpforge_add_builder_templates');
}
add_action('after_setup_theme', 'wpforge_builder_support_init');

/**
 * Elementor support.
 *
 * @since 1.0.0
 */
function wpforge_elementor_support() {
    // Add theme support for Elementor.
    add_theme_support('elementor');

    // Add Elementor locations.
    add_action('elementor/theme/register_locations', 'wpforge_register_elementor_locations');

    // Sync theme colors with Elementor global colors.
    add_action('elementor/editor/after_enqueue_styles', 'wpforge_elementor_sync_colors');

    // Sync theme fonts with Elementor global fonts.
    add_action('elementor/editor/after_enqueue_styles', 'wpforge_elementor_sync_fonts');

    // Add Elementor full width page template support.
    add_filter('template_include', 'wpforge_elementor_canvas_template');

    // Optimize Elementor CSS loading.
    if (get_theme_mod('wpforge_optimize_elementor', true)) {
        add_action('wp_enqueue_scripts', 'wpforge_optimize_elementor_assets', 999);
    }
}

/**
 * Register Elementor locations.
 *
 * @since 1.0.0
 * @param ElementorPro\Modules\ThemeBuilder\Classes\Locations_Manager $elementor_theme_manager Elementor theme manager.
 */
function wpforge_register_elementor_locations($elementor_theme_manager) {
    $elementor_theme_manager->register_all_core_location();
}

/**
 * Sync theme colors with Elementor global colors.
 *
 * @since 1.0.0
 */
function wpforge_elementor_sync_colors() {
    $primary_color = get_theme_mod('wpforge_primary_color', '#2563eb');
    $secondary_color = get_theme_mod('wpforge_secondary_color', '#64748b');
    $accent_color = get_theme_mod('wpforge_accent_color', '#f97316');
    $text_color = get_theme_mod('wpforge_text_color', '#1e293b');

    $custom_css = "
        :root {
            --e-global-color-primary: {$primary_color};
            --e-global-color-secondary: {$secondary_color};
            --e-global-color-accent: {$accent_color};
            --e-global-color-text: {$text_color};
        }
    ";

    wp_add_inline_style('elementor-editor', $custom_css);
}

/**
 * Sync theme fonts with Elementor global fonts.
 *
 * @since 1.0.0
 */
function wpforge_elementor_sync_fonts() {
    $body_font = get_theme_mod('wpforge_body_font', 'system-ui');
    $heading_font = get_theme_mod('wpforge_heading_font', 'system-ui');

    $custom_css = "
        :root {
            --e-global-typography-primary-font-family: {$body_font};
            --e-global-typography-secondary-font-family: {$heading_font};
        }
    ";

    wp_add_inline_style('elementor-editor', $custom_css);
}

/**
 * Elementor canvas template.
 *
 * @since 1.0.0
 * @param string $template Template path.
 * @return string Modified template path.
 */
function wpforge_elementor_canvas_template($template) {
    if (is_singular()) {
        $page_template = get_post_meta(get_the_ID(), '_wp_page_template', true);

        if ('elementor_canvas' === $page_template) {
            $new_template = get_template_directory() . '/page-templates/elementor-canvas.php';
            if (file_exists($new_template)) {
                return $new_template;
            }
        }

        if ('elementor_header_footer' === $page_template) {
            $new_template = get_template_directory() . '/page-templates/elementor-header-footer.php';
            if (file_exists($new_template)) {
                return $new_template;
            }
        }
    }

    return $template;
}

/**
 * Optimize Elementor assets.
 *
 * @since 1.0.0
 */
function wpforge_optimize_elementor_assets() {
    // Don't optimize in editor mode.
    if (\Elementor\Plugin::$instance->preview->is_preview_mode()) {
        return;
    }

    // Dequeue unused Elementor scripts.
    if (!is_singular() || !get_post_meta(get_the_ID(), '_elementor_edit_mode', true)) {
        // Page is not built with Elementor, dequeue Elementor assets.
        wp_dequeue_style('elementor-frontend');
        wp_dequeue_style('elementor-global');
        wp_dequeue_script('elementor-frontend');
        wp_dequeue_script('elementor-webpack-runtime');
    }
}

/**
 * Bricks Builder support.
 *
 * @since 1.0.0
 */
function wpforge_bricks_support() {
    // Add theme support for Bricks.
    add_theme_support('bricks');

    // Sync theme colors with Bricks global colors.
    add_action('bricks/builder/enqueue_scripts', 'wpforge_bricks_sync_colors');

    // Sync theme fonts with Bricks global fonts.
    add_action('bricks/builder/enqueue_scripts', 'wpforge_bricks_sync_fonts');

    // Add Bricks page template support.
    add_filter('template_include', 'wpforge_bricks_canvas_template');
}

/**
 * Sync theme colors with Bricks global colors.
 *
 * @since 1.0.0
 */
function wpforge_bricks_sync_colors() {
    $primary_color = get_theme_mod('wpforge_primary_color', '#2563eb');
    $secondary_color = get_theme_mod('wpforge_secondary_color', '#64748b');
    $accent_color = get_theme_mod('wpforge_accent_color', '#f97316');

    $custom_css = "
        :root {
            --bricks-color-primary: {$primary_color};
            --bricks-color-secondary: {$secondary_color};
            --bricks-color-accent: {$accent_color};
        }
    ";

    wp_add_inline_style('bricks-builder', $custom_css);
}

/**
 * Sync theme fonts with Bricks global fonts.
 *
 * @since 1.0.0
 */
function wpforge_bricks_sync_fonts() {
    $body_font = get_theme_mod('wpforge_body_font', 'system-ui');
    $heading_font = get_theme_mod('wpforge_heading_font', 'system-ui');

    $custom_css = "
        :root {
            --bricks-typography-primary-font-family: {$body_font};
            --bricks-typography-heading-font-family: {$heading_font};
        }
    ";

    wp_add_inline_style('bricks-builder', $custom_css);
}

/**
 * Bricks canvas template.
 *
 * @since 1.0.0
 * @param string $template Template path.
 * @return string Modified template path.
 */
function wpforge_bricks_canvas_template($template) {
    if (is_singular()) {
        $page_template = get_post_meta(get_the_ID(), '_wp_page_template', true);

        if ('bricks_canvas' === $page_template) {
            $new_template = get_template_directory() . '/page-templates/bricks-canvas.php';
            if (file_exists($new_template)) {
                return $new_template;
            }
        }
    }

    return $template;
}

/**
 * Add builder page templates.
 *
 * @since 1.0.0
 * @param array $templates Page templates.
 * @return array Modified templates.
 */
function wpforge_add_builder_templates($templates) {
    $templates['page-templates/full-width.php'] = __('Full Width (No Sidebar)', 'wpforge-theme');
    $templates['page-templates/canvas.php'] = __('Canvas (Blank)', 'wpforge-theme');
    $templates['page-templates/no-header.php'] = __('No Header', 'wpforge-theme');
    $templates['page-templates/no-footer.php'] = __('No Footer', 'wpforge-theme');
    $templates['page-templates/landing-page.php'] = __('Landing Page', 'wpforge-theme');

    return $templates;
}

/**
 * Check if current page is built with a page builder.
 *
 * @since 1.0.0
 * @return bool Whether the page is built with a builder.
 */
function wpforge_is_builder_page() {
    // Check Elementor.
    if (did_action('elementor/loaded')) {
        if (get_post_meta(get_the_ID(), '_elementor_edit_mode', true)) {
            return true;
        }
    }

    // Check Bricks.
    if (defined('BRICKS_VERSION')) {
        if (get_post_meta(get_the_ID(), '_bricks_page_content_2', true)) {
            return true;
        }
    }

    // Check Gutenberg blocks.
    if (has_blocks()) {
        return true;
    }

    return false;
}

/**
 * Remove theme styles interference on builder pages.
 *
 * @since 1.0.0
 */
function wpforge_builder_page_cleanup() {
    if (!is_singular()) {
        return;
    }

    if (!wpforge_is_builder_page()) {
        return;
    }

    // Remove theme's content styles to avoid conflicts.
    add_filter('body_class', function($classes) {
        $classes[] = 'builder-page';
        return $classes;
    });
}
add_action('wp', 'wpforge_builder_page_cleanup');

/**
 * Get builder content width.
 *
 * @since 1.0.0
 * @return int Content width in pixels.
 */
function wpforge_get_builder_content_width() {
    $content_width = get_theme_mod('wpforge_content_width', 1200);
    return apply_filters('wpforge_builder_content_width', $content_width);
}

/**
 * Add custom Elementor widgets.
 *
 * Note: This is a placeholder for future expansion.
 *
 * @since 1.0.0
 */
function wpforge_register_elementor_widgets() {
    // Check if Elementor is active.
    if (!did_action('elementor/loaded')) {
        return;
    }

    // Register custom widgets here.
    // Widgets would go in /inc/elementor-widgets/ directory.
}
add_action('elementor/widgets/widgets_registered', 'wpforge_register_elementor_widgets');

/**
 * Add custom Bricks elements.
 *
 * Note: This is a placeholder for future expansion.
 *
 * @since 1.0.0
 */
function wpforge_register_bricks_elements() {
    // Check if Bricks is active.
    if (!defined('BRICKS_VERSION')) {
        return;
    }

    // Register custom elements here.
    // Elements would go in /inc/bricks-elements/ directory.
}
add_action('bricks/elements/register_elements', 'wpforge_register_bricks_elements');

/**
 * Get builder compatibility info.
 *
 * @since 1.0.0
 * @return array Builder compatibility information.
 */
function wpforge_get_builder_compatibility() {
    $compatibility = array(
        'elementor' => array(
            'name'        => 'Elementor',
            'supported'   => true,
            'version'     => '3.0+',
            'features'    => array(
                'full_width_support' => true,
                'canvas_support'     => true,
                'theme_locations'    => true,
                'color_sync'         => true,
                'font_sync'          => true,
            ),
        ),
        'bricks' => array(
            'name'        => 'Bricks Builder',
            'supported'   => true,
            'version'     => '1.5+',
            'features'    => array(
                'full_width_support' => true,
                'canvas_support'     => true,
                'color_sync'         => true,
                'font_sync'          => true,
            ),
        ),
        'gutenberg' => array(
            'name'        => 'Gutenberg',
            'supported'   => true,
            'version'     => '5.8+',
            'features'    => array(
                'wide_alignment'     => true,
                'responsive_embeds'  => true,
                'block_styles'       => true,
            ),
        ),
    );

    return $compatibility;
}
