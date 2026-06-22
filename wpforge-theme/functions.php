<?php
/**
 * WPForge Theme - Theme Functions
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

// Exit if accessed directly.
if (!defined('ABSPATH')) {
    exit;
}

// Theme version.
define('WPFORGE_THEME_VERSION', '1.0.0');
define('WPFORGE_THEME_DIR', get_template_directory());
define('WPFORGE_THEME_URI', get_template_directory_uri());
define('WPFORGE_THEME_INC', WPFORGE_THEME_DIR . '/inc');
define('WPFORGE_THEME_ASSETS', WPFORGE_THEME_URI . '/assets');

/**
 * Theme setup.
 *
 * @since 1.0.0
 */
function wpforge_theme_setup() {
    // Make theme available for translation.
    load_theme_textdomain('wpforge-theme', WPFORGE_THEME_DIR . '/languages');

    // Add default posts and comments RSS feed links to head.
    add_theme_support('automatic-feed-links');

    // Let WordPress manage the document title.
    add_theme_support('title-tag');

    // Enable support for Post Thumbnails on posts and pages.
    add_theme_support('post-thumbnails');

    // Register navigation menus.
    register_nav_menus(array(
        'primary' => esc_html__('Primary Menu', 'wpforge-theme'),
        'footer'  => esc_html__('Footer Menu', 'wpforge-theme'),
        'mobile'  => esc_html__('Mobile Menu', 'wpforge-theme'),
    ));

    // Switch default core markup for search form, comment form, and comments to output valid HTML5.
    add_theme_support('html5', array(
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
        'style',
        'script',
    ));

    // Add theme support for selective refresh for widgets.
    add_theme_support('customize-selective-refresh-widgets');

    // Add support for core custom logo.
    add_theme_support('custom-logo', array(
        'height'      => 100,
        'width'       => 300,
        'flex-width'  => true,
        'flex-height' => true,
    ));

    // Add support for custom background.
    add_theme_support('custom-background', array(
        'default-color' => 'ffffff',
    ));

    // Add support for custom header.
    add_theme_support('custom-header', array(
        'default-image' => '',
        'default-text-color' => '1e293b',
        'width' => 1920,
        'height' => 300,
        'flex-width' => true,
        'flex-height' => true,
    ));

    // Add support for post formats.
    add_theme_support('post-formats', array(
        'aside',
        'gallery',
        'link',
        'image',
        'quote',
        'status',
        'video',
        'audio',
        'chat',
    ));

    // Add support for WooCommerce.
    add_theme_support('woocommerce');
    add_theme_support('wc-product-gallery-zoom');
    add_theme_support('wc-product-gallery-lightbox');
    add_theme_support('wc-product-gallery-slider');

    // Add support for Elementor.
    add_theme_support('elementor');

    // Add support for wide and full alignment blocks.
    add_theme_support('align-wide');

    // Add support for responsive embeds.
    add_theme_support('responsive-embeds');

    // Add image sizes.
    add_image_size('wpforge-thumbnail', 400, 300, true);
    add_image_size('wpforge-medium', 800, 600, true);
    add_image_size('wpforge-large', 1200, 800, true);
    add_image_size('wpforge-full', 1920, 1080, true);
}
add_action('after_setup_theme', 'wpforge_theme_setup');

/**
 * Set the content width in pixels, based on the theme's design and stylesheet.
 *
 * @since 1.0.0
 */
function wpforge_content_width() {
    $GLOBALS['content_width'] = apply_filters('wpforge_content_width', 800);
}
add_action('after_setup_theme', 'wpforge_content_width', 0);

/**
 * Register widget area.
 *
 * @since 1.0.0
 */
function wpforge_widgets_init() {
    // Primary Sidebar.
    register_sidebar(array(
        'name'          => esc_html__('Primary Sidebar', 'wpforge-theme'),
        'id'            => 'sidebar-primary',
        'description'   => esc_html__('Add widgets here.', 'wpforge-theme'),
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget'  => '</section>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ));

    // Footer Widgets.
    $footer_columns = get_theme_mod('wpforge_footer_columns', 4);
    for ($i = 1; $i <= $footer_columns; $i++) {
        register_sidebar(array(
            /* translators: %d: Footer widget column number */
            'name'          => sprintf(esc_html__('Footer Column %d', 'wpforge-theme'), $i),
            'id'            => 'footer-' . $i,
            'description'   => esc_html__('Add widgets here.', 'wpforge-theme'),
            'before_widget' => '<section id="%1$s" class="widget %2$s">',
            'after_widget'  => '</section>',
            'before_title'  => '<h4 class="widget-title">',
            'after_title'   => '</h4>',
        ));
    }
}
add_action('widgets_init', 'wpforge_widgets_init');

/**
 * Enqueue scripts and styles.
 *
 * @since 1.0.0
 */
function wpforge_scripts() {
    // Main stylesheet.
    wp_enqueue_style('wpforge-style', get_stylesheet_uri(), array(), WPFORGE_THEME_VERSION);

    // Main CSS.
    wp_enqueue_style('wpforge-main', WPFORGE_THEME_ASSETS . '/css/main.css', array('wpforge-style'), WPFORGE_THEME_VERSION);

    // Header CSS.
    wp_enqueue_style('wpforge-header', WPFORGE_THEME_ASSETS . '/css/header.css', array('wpforge-main'), WPFORGE_THEME_VERSION);

    // Footer CSS.
    wp_enqueue_style('wpforge-footer', WPFORGE_THEME_ASSETS . '/css/footer.css', array('wpforge-main'), WPFORGE_THEME_VERSION);

    // Single post CSS.
    if (is_singular()) {
        wp_enqueue_style('wpforge-single', WPFORGE_THEME_ASSETS . '/css/single.css', array('wpforge-main'), WPFORGE_THEME_VERSION);
    }

    // WooCommerce CSS.
    if (class_exists('WooCommerce') && (is_woocommerce() || is_cart() || is_checkout() || is_account_page())) {
        wp_enqueue_style('wpforge-woocommerce', WPFORGE_THEME_ASSETS . '/css/woocommerce.css', array('wpforge-main'), WPFORGE_THEME_VERSION);
    }

    // Main JS.
    wp_enqueue_script('wpforge-main', WPFORGE_THEME_ASSETS . '/js/main.js', array(), WPFORGE_THEME_VERSION, true);

    // Navigation JS.
    wp_enqueue_script('wpforge-navigation', WPFORGE_THEME_ASSETS . '/js/navigation.js', array('wpforge-main'), WPFORGE_THEME_VERSION, true);

    // Comment reply script.
    if (is_singular() && comments_open() && get_option('thread_comments')) {
        wp_enqueue_script('comment-reply');
    }

    // Localize script.
    wp_localize_script('wpforge-main', 'wpforgeTheme', array(
        'ajaxUrl' => admin_url('admin-ajax.php'),
        'nonce'   => wp_create_nonce('wpforge_nonce'),
        'strings' => array(
            'loading' => esc_html__('Loading...', 'wpforge-theme'),
            'search'  => esc_html__('Search', 'wpforge-theme'),
            'menu'    => esc_html__('Menu', 'wpforge-theme'),
            'close'   => esc_html__('Close', 'wpforge-theme'),
        ),
    ));
}
add_action('wp_enqueue_scripts', 'wpforge_scripts');

/**
 * Include required files.
 *
 * @since 1.0.0
 */
function wpforge_include_files() {
    // Hooks system.
    require_once WPFORGE_THEME_INC . '/hooks.php';

    // Customizer settings.
    require_once WPFORGE_THEME_INC . '/customizer.php';

    // SEO optimization.
    require_once WPFORGE_THEME_INC . '/seo.php';

    // Performance optimization.
    require_once WPFORGE_THEME_INC . '/performance.php';

    // Page builder support.
    require_once WPFORGE_THEME_INC . '/builder-support.php';

    // WooCommerce support.
    if (class_exists('WooCommerce')) {
        require_once WPFORGE_THEME_INC . '/woocommerce.php';
    }

    // WPForge API integration.
    require_once WPFORGE_THEME_INC . '/wpforge-api.php';

    // Template tags.
    require_once WPFORGE_THEME_INC . '/template-tags.php';

    // Funnel Dashboard (requires WooCommerce).
    if (class_exists('WooCommerce')) {
        require_once WPFORGE_THEME_INC . '/funnel-dashboard/class-funnel-dashboard.php';
    }
}
add_action('after_setup_theme', 'wpforge_include_files', 5);

/**
 * Add body classes.
 *
 * @since 1.0.0
 * @param array $classes Body classes.
 * @return array Modified body classes.
 */
function wpforge_body_classes($classes) {
    // Layout class.
    $layout = get_theme_mod('wpforge_site_layout', 'wide');
    $classes[] = 'wpforge-layout-' . $layout;

    // Sidebar position.
    $sidebar_position = get_theme_mod('wpforge_sidebar_position', 'right');
    if (is_active_sidebar('sidebar-primary') && !is_page_template('page-templates/full-width.php') && !is_page_template('page-templates/canvas.php')) {
        $classes[] = 'wpforge-sidebar-' . $sidebar_position;
    } else {
        $classes[] = 'wpforge-no-sidebar';
    }

    // Header type.
    $header_type = get_theme_mod('wpforge_header_type', 'classic');
    $classes[] = 'wpforge-header-' . $header_type;

    // Sticky header.
    if (get_theme_mod('wpforge_sticky_header', true)) {
        $classes[] = 'wpforge-sticky-header';
    }

    // Dark mode.
    $dark_mode = get_theme_mod('wpforge_dark_mode', 'auto');
    if ($dark_mode === 'manual') {
        $classes[] = 'wpforge-dark-mode';
    } elseif ($dark_mode === 'auto') {
        $classes[] = 'wpforge-dark-mode-auto';
    }

    // Page template class.
    if (is_page_template()) {
        $template_slug = basename(get_page_template_slug(), '.php');
        $classes[] = 'page-template-' . $template_slug;
    }

    // WooCommerce class.
    if (class_exists('WooCommerce')) {
        $classes[] = 'wpforge-woocommerce';
    }

    // Elementor class.
    if (did_action('elementor/loaded')) {
        $classes[] = 'wpforge-elementor';
    }

    return apply_filters('wpforge_body_classes', $classes);
}
add_filter('body_class', 'wpforge_body_classes');

/**
 * Add post classes.
 *
 * @since 1.0.0
 * @param array $classes Post classes.
 * @return array Modified post classes.
 */
function wpforge_post_classes($classes) {
    // Add post format class.
    if (get_post_format()) {
        $classes[] = 'format-' . get_post_format();
    }

    // Add featured image class.
    if (has_post_thumbnail()) {
        $classes[] = 'has-post-thumbnail';
    }

    return apply_filters('wpforge_post_classes', $classes);
}
add_filter('post_class', 'wpforge_post_classes');

/**
 * Custom excerpt length.
 *
 * @since 1.0.0
 * @param int $length Excerpt length.
 * @return int Modified excerpt length.
 */
function wpforge_excerpt_length($length) {
    if (is_admin()) {
        return $length;
    }

    $custom_length = get_theme_mod('wpforge_excerpt_length', 30);
    return absint($custom_length);
}
add_filter('excerpt_length', 'wpforge_excerpt_length', 999);

/**
 * Custom excerpt more.
 *
 * @since 1.0.0
 * @param string $more Excerpt more text.
 * @return string Modified excerpt more text.
 */
function wpforge_excerpt_more($more) {
    if (is_admin()) {
        return $more;
    }

    $read_more_text = get_theme_mod('wpforge_read_more_text', __('Read More', 'wpforge-theme'));
    return '... <a href="' . esc_url(get_permalink()) . '" class="wpforge-read-more">' . esc_html($read_more_text) . '</a>';
}
add_filter('excerpt_more', 'wpforge_excerpt_more');

/**
 * Register page templates.
 *
 * @since 1.0.0
 */
function wpforge_register_page_templates() {
    // Page templates are registered via file headers in page-templates directory.
    // This function is a placeholder for future template registration logic.
}
add_action('after_setup_theme', 'wpforge_register_page_templates');

/**
 * Add pingback header.
 *
 * @since 1.0.0
 */
function wpforge_pingback_header() {
    if (is_singular() && pings_open()) {
        printf('<link rel="pingback" href="%s">', esc_url(get_bloginfo('pingback_url')));
    }
}
add_action('wp_head', 'wpforge_pingback_header');

/**
 * Theme activation hook.
 *
 * @since 1.0.0
 */
function wpforge_theme_activation() {
    // Flush rewrite rules.
    flush_rewrite_rules();

    // Set default theme mods if not set.
    $default_mods = wpforge_get_default_theme_mods();
    foreach ($default_mods as $key => $value) {
        if (get_theme_mod($key) === false) {
            set_theme_mod($key, $value);
        }
    }

    // Set activation flag.
    update_option('wpforge_theme_activated', true);
    update_option('wpforge_theme_version', WPFORGE_THEME_VERSION);
}
add_action('after_switch_theme', 'wpforge_theme_activation');

/**
 * Theme deactivation hook.
 *
 * @since 1.0.0
 */
function wpforge_theme_deactivation() {
    // Flush rewrite rules.
    flush_rewrite_rules();

    // Remove activation flag.
    delete_option('wpforge_theme_activated');
}
add_action('switch_theme', 'wpforge_theme_deactivation');

/**
 * Get default theme mods.
 *
 * @since 1.0.0
 * @return array Default theme modifications.
 */
function wpforge_get_default_theme_mods() {
    return apply_filters('wpforge_default_theme_mods', array(
        // Layout.
        'wpforge_site_layout'        => 'wide',
        'wpforge_container_width'    => 1200,
        'wpforge_content_width'      => 800,
        'wpforge_sidebar_position'   => 'right',
        'wpforge_sidebar_width'      => 300,

        // Colors.
        'wpforge_primary_color'      => '#2563eb',
        'wpforge_secondary_color'    => '#64748b',
        'wpforge_accent_color'       => '#f59e0b',
        'wpforge_text_color'         => '#1e293b',
        'wpforge_bg_color'           => '#ffffff',
        'wpforge_border_color'       => '#e2e8f0',
        'wpforge_dark_mode'          => 'auto',

        // Typography.
        'wpforge_body_font'          => 'system',
        'wpforge_heading_font'       => 'system',
        'wpforge_body_font_size'     => 16,
        'wpforge_body_line_height'   => 1.7,
        'wpforge_heading_font_weight' => 700,

        // Header.
        'wpforge_header_type'        => 'classic',
        'wpforge_header_height'      => 70,
        'wpforge_sticky_header'      => true,
        'wpforge_transparent_header' => false,
        'wpforge_top_bar'            => false,

        // Footer.
        'wpforge_footer_columns'     => 4,
        'wpforge_footer_bottom_bar'  => true,
        'wpforge_back_to_top'        => true,

        // Blog.
        'wpforge_blog_layout'        => 'grid',
        'wpforge_blog_columns'       => 2,
        'wpforge_show_featured_image' => true,
        'wpforge_show_category'      => true,
        'wpforge_show_date'          => true,
        'wpforge_show_author'        => true,
        'wpforge_show_comments'      => true,
        'wpforge_excerpt_length'     => 30,
        'wpforge_read_more_text'     => __('Read More', 'wpforge-theme'),

        // Single post.
        'wpforge_single_layout'      => 'right-sidebar',
        'wpforge_single_show_featured' => true,
        'wpforge_single_show_category' => true,
        'wpforge_single_show_date'   => true,
        'wpforge_single_show_author' => true,
        'wpforge_single_show_tags'   => true,
        'wpforge_single_show_nav'    => true,
        'wpforge_single_show_related' => true,
        'wpforge_related_count'      => 3,
        'wpforge_single_show_author_box' => false,

        // SEO.
        'wpforge_seo_enabled'        => true,
        'wpforge_schema_enabled'     => true,
        'wpforge_breadcrumb_enabled' => true,
        'wpforge_open_graph_enabled' => true,
        'wpforge_twitter_cards_enabled' => true,

        // Performance.
        'wpforge_lazy_load_images'   => true,
        'wpforge_disable_emojis'     => true,
        'wpforge_disable_embeds'     => true,
        'wpforge_remove_wp_version'  => true,
        'wpforge_disable_xmlrpc'     => true,
        'wpforge_defer_js'           => true,
    ));
}

/**
 * Get theme option with default fallback.
 *
 * @since 1.0.0
 * @param string $key Option key.
 * @param mixed $default Default value.
 * @return mixed Option value.
 */
function wpforge_get_option($key, $default = null) {
    $value = get_theme_mod($key, $default);
    
    if ($value === null) {
        $defaults = wpforge_get_default_theme_mods();
        $value = isset($defaults[$key]) ? $defaults[$key] : $default;
    }

    return apply_filters('wpforge_get_option', $value, $key);
}

/**
 * Check if WPForge plugin is active.
 *
 * @since 1.0.0
 * @return bool Whether WPForge plugin is active.
 */
function wpforge_plugin_active() {
    return class_exists('WPForge') || defined('WPFORGE_VERSION');
}

/**
 * Add admin notice if WPForge plugin is not active.
 *
 * @since 1.0.0
 */
function wpforge_theme_admin_notice() {
    if (!wpforge_plugin_active() && current_user_can('manage_options')) {
        ?>
        <div class="notice notice-info">
            <p>
                <?php
                printf(
                    /* translators: %s: WPForge plugin link */
                    esc_html__('WPForge Theme works best with the %s plugin installed and activated for full AI-driven website building capabilities.', 'wpforge-theme'),
                    '<strong>' . esc_html__('WPForge', 'wpforge-theme') . '</strong>'
                );
                ?>
            </p>
        </div>
        <?php
    }
}
add_action('admin_notices', 'wpforge_theme_admin_notice');

/**
 * Add theme support for Gutenberg editor styles.
 *
 * @since 1.0.0
 */
function wpforge_gutenberg_editor_styles() {
    add_theme_support('editor-styles');
    add_editor_style(WPFORGE_THEME_ASSETS . '/css/editor.css');
}
add_action('after_setup_theme', 'wpforge_gutenberg_editor_styles');

/**
 * Enqueue block editor assets.
 *
 * @since 1.0.0
 */
function wpforge_enqueue_block_editor_assets() {
    wp_enqueue_style(
        'wpforge-block-editor',
        WPFORGE_THEME_ASSETS . '/css/block-editor.css',
        array(),
        WPFORGE_THEME_VERSION
    );
}
add_action('enqueue_block_editor_assets', 'wpforge_enqueue_block_editor_assets');
