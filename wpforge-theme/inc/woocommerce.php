<?php
/**
 * WPForge Theme - WooCommerce Integration
 *
 * 深度集成WooCommerce，与主题颜色/字体系统完全同步
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

// Exit if accessed directly.
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Check if WooCommerce is active.
 *
 * @since 1.0.0
 * @return bool Whether WooCommerce is active.
 */
function wpforge_is_woocommerce_active() {
    return class_exists('WooCommerce');
}

/**
 * Initialize WooCommerce support.
 *
 * @since 1.0.0
 */
function wpforge_woocommerce_init() {
    if (!wpforge_is_woocommerce_active()) {
        return;
    }

    // Add WooCommerce theme support.
    add_theme_support('woocommerce');
    add_theme_support('wc-product-gallery-zoom');
    add_theme_support('wc-product-gallery-lightbox');
    add_theme_support('wc-product-gallery-slider');

    // Remove default WooCommerce wrappers.
    remove_action('woocommerce_before_main_content', 'woocommerce_output_content_wrapper', 10);
    remove_action('woocommerce_after_main_content', 'woocommerce_output_content_wrapper_end', 10);

    // Add theme wrappers.
    add_action('woocommerce_before_main_content', 'wpforge_woocommerce_wrapper_start', 10);
    add_action('woocommerce_after_main_content', 'wpforge_woocommerce_wrapper_end', 10);

    // Remove default sidebar.
    remove_action('woocommerce_sidebar', 'woocommerce_get_sidebar', 10);

    // Add theme sidebar.
    add_action('woocommerce_sidebar', 'wpforge_woocommerce_get_sidebar', 10);

    // Customize shop page.
    add_filter('loop_shop_columns', 'wpforge_woocommerce_loop_columns');
    add_filter('loop_shop_per_page', 'wpforge_woocommerce_products_per_page', 20);

    // Remove default breadcrumb.
    remove_action('woocommerce_before_main_content', 'woocommerce_breadcrumb', 20);

    // Add theme breadcrumb.
    add_action('woocommerce_before_main_content', 'wpforge_woocommerce_breadcrumb', 20);

    // Customize product page.
    remove_action('woocommerce_single_product_summary', 'woocommerce_template_single_title', 5);
    add_action('woocommerce_single_product_summary', 'wpforge_woocommerce_single_title', 5);

    // Customize product card.
    remove_action('woocommerce_before_shop_loop_item_title', 'woocommerce_template_loop_product_thumbnail', 10);
    add_action('woocommerce_before_shop_loop_item_title', 'wpforge_woocommerce_product_thumbnail', 10);

    // Add to cart AJAX.
    add_filter('woocommerce_enable_ajax_add_to_cart', '__return_true');

    // Enqueue WooCommerce styles.
    add_action('wp_enqueue_scripts', 'wpforge_woocommerce_enqueue_styles');

    // Customize WooCommerce CSS variables.
    add_action('wp_head', 'wpforge_woocommerce_css_variables', 4);

    // Hide/Show elements based on customizer settings.
    add_action('wp', 'wpforge_woocommerce_toggle_elements');

    // Related products count.
    add_filter('woocommerce_output_related_products_args', 'wpforge_woocommerce_related_products_args');

    // Upsells count.
    add_filter('woocommerce_upsell_display_args', 'wpforge_woocommerce_upsells_args');

    // Product page layout.
    add_action('wp', 'wpforge_woocommerce_product_layout');
}
add_action('after_setup_theme', 'wpforge_woocommerce_init');

/**
 * WooCommerce wrapper start.
 *
 * @since 1.0.0
 */
function wpforge_woocommerce_wrapper_start() {
    ?>
    <div id="primary" class="content-area">
        <main id="main" class="site-main" role="main">
    <?php
}

/**
 * WooCommerce wrapper end.
 *
 * @since 1.0.0
 */
function wpforge_woocommerce_wrapper_end() {
    ?>
        </main>
    </div>
    <?php
}

/**
 * Get WooCommerce sidebar.
 *
 * @since 1.0.0
 */
function wpforge_woocommerce_get_sidebar() {
    $sidebar_position = get_theme_mod('wpforge_sidebar_position', 'right');

    if ('none' === $sidebar_position) {
        return;
    }

    if (is_active_sidebar('shop-sidebar')) {
        ?>
        <aside id="secondary" class="widget-area shop-sidebar" role="complementary">
            <?php dynamic_sidebar('shop-sidebar'); ?>
        </aside>
        <?php
    }
}

/**
 * WooCommerce loop columns.
 *
 * @since 1.0.0
 * @return int Number of columns.
 */
function wpforge_woocommerce_loop_columns() {
    return get_theme_mod('wpforge_products_per_row', 4);
}

/**
 * Products per page.
 *
 * @since 1.0.0
 * @param int $cols Default number of products per page.
 * @return int Modified number of products per page.
 */
function wpforge_woocommerce_products_per_page($cols) {
    return get_theme_mod('wpforge_products_per_page', 12);
}

/**
 * WooCommerce breadcrumb.
 *
 * @since 1.0.0
 */
function wpforge_woocommerce_breadcrumb() {
    if (!get_theme_mod('wpforge_breadcrumb_enabled', true)) {
        return;
    }

    if (is_front_page() && !get_theme_mod('wpforge_breadcrumb_show_home', false)) {
        return;
    }

    if (function_exists('wpforge_breadcrumb')) {
        wpforge_breadcrumb();
    }
}

/**
 * Custom product title.
 *
 * @since 1.0.0
 */
function wpforge_woocommerce_single_title() {
    the_title('<h1 class="product_title entry-title">', '</h1>');
}

/**
 * Custom product thumbnail.
 *
 * @since 1.0.0
 */
function wpforge_woocommerce_product_thumbnail() {
    global $product;

    if (!get_theme_mod('wpforge_show_product_image', true)) {
        return;
    }

    $size = 'woocommerce_thumbnail';
    $attr = array(
        'loading' => 'lazy',
    );

    echo woocommerce_get_product_thumbnail($size, $attr);
}

/**
 * Enqueue WooCommerce styles.
 *
 * @since 1.0.0
 */
function wpforge_woocommerce_enqueue_styles() {
    if (!wpforge_is_woocommerce_active()) {
        return;
    }

    // Only load on WooCommerce pages.
    if (!is_woocommerce() && !is_cart() && !is_checkout() && !is_account_page()) {
        return;
    }

    wp_enqueue_style(
        'wpforge-woocommerce',
        get_template_directory_uri() . '/assets/css/woocommerce.css',
        array(),
        WPFORGE_THEME_VERSION
    );
}

/**
 * WooCommerce CSS variables.
 *
 * Sync theme colors with WooCommerce.
 *
 * @since 1.0.0
 */
function wpforge_woocommerce_css_variables() {
    if (!wpforge_is_woocommerce_active()) {
        return;
    }

    $primary_color = get_theme_mod('wpforge_primary_color', '#2563eb');
    $secondary_color = get_theme_mod('wpforge_secondary_color', '#64748b');
    $accent_color = get_theme_mod('wpforge_accent_color', '#f97316');
    $text_color = get_theme_mod('wpforge_text_color', '#1e293b');
    $background_color = get_theme_mod('wpforge_background_color', '#ffffff');
    $border_color = get_theme_mod('wpforge_border_color', '#e2e8f0');
    $button_radius = get_theme_mod('wpforge_button_border_radius', 6);

    $css = "
        :root {
            --wpforge-wc-primary: {$primary_color};
            --wpforge-wc-secondary: {$secondary_color};
            --wpforge-wc-accent: {$accent_color};
            --wpforge-wc-text: {$text_color};
            --wpforge-wc-background: {$background_color};
            --wpforge-wc-border: {$border_color};
            --wpforge-wc-button-radius: {$button_radius}px;
        }
    ";

    echo '<style id="wpforge-woocommerce-variables">' . $css . '</style>';
}

/**
 * Toggle WooCommerce elements based on customizer settings.
 *
 * @since 1.0.0
 */
function wpforge_woocommerce_toggle_elements() {
    if (!wpforge_is_woocommerce_active()) {
        return;
    }

    // Shop page elements.
    if (is_shop() || is_product_category() || is_product_tag()) {
        if (!get_theme_mod('wpforge_show_product_price', true)) {
            remove_action('woocommerce_after_shop_loop_item_title', 'woocommerce_template_loop_price', 10);
        }

        if (!get_theme_mod('wpforge_show_product_rating', true)) {
            remove_action('woocommerce_after_shop_loop_item_title', 'woocommerce_template_loop_rating', 5);
        }

        if (!get_theme_mod('wpforge_show_add_to_cart', true)) {
            remove_action('woocommerce_after_shop_loop_item', 'woocommerce_template_loop_add_to_cart', 10);
        }
    }

    // Single product page elements.
    if (is_product()) {
        if (!get_theme_mod('wpforge_show_product_tags', true)) {
            remove_action('woocommerce_single_product_summary', 'woocommerce_template_single_meta', 40);
        }

        if (!get_theme_mod('wpforge_show_product_category', true)) {
            // Categories are in meta, handled above.
        }

        if (!get_theme_mod('wpforge_show_related_products', true)) {
            remove_action('woocommerce_after_single_product_summary', 'woocommerce_output_related_products', 20);
        }

        if (!get_theme_mod('wpforge_show_upsells', true)) {
            remove_action('woocommerce_after_single_product_summary', 'woocommerce_upsell_display', 15);
        }
    }
}

/**
 * Related products args.
 *
 * @since 1.0.0
 * @param array $args Related products query args.
 * @return array Modified args.
 */
function wpforge_woocommerce_related_products_args($args) {
    $count = get_theme_mod('wpforge_related_products_count', 4);
    $columns = get_theme_mod('wpforge_products_per_row', 4);

    $args['posts_per_page'] = $count;
    $args['columns'] = $columns;

    return $args;
}

/**
 * Upsells args.
 *
 * @since 1.0.0
 * @param array $args Upsells display args.
 * @return array Modified args.
 */
function wpforge_woocommerce_upsells_args($args) {
    $columns = get_theme_mod('wpforge_products_per_row', 4);

    $args['columns'] = $columns;

    return $args;
}

/**
 * Product page layout.
 *
 * @since 1.0.0
 */
function wpforge_woocommerce_product_layout() {
    if (!is_product()) {
        return;
    }

    $layout = get_theme_mod('wpforge_product_page_layout', 'left-right');

    if ('top-bottom' === $layout) {
        // Remove default image position.
        remove_action('woocommerce_before_single_product_summary', 'woocommerce_show_product_images', 20);
        add_action('woocommerce_single_product_summary', 'woocommerce_show_product_images', 4);
    }
}

/**
 * Register WooCommerce widget areas.
 *
 * @since 1.0.0
 */
function wpforge_woocommerce_widgets_init() {
    if (!wpforge_is_woocommerce_active()) {
        return;
    }

    // Shop sidebar.
    register_sidebar(array(
        'name'          => __('Shop Sidebar', 'wpforge-theme'),
        'id'            => 'shop-sidebar',
        'description'   => __('Sidebar for shop pages', 'wpforge-theme'),
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget'  => '</section>',
        'before_title'  => '<h2 class="widget-title">',
        'after_title'   => '</h2>',
    ));
}
add_action('widgets_init', 'wpforge_woocommerce_widgets_init');

/**
 * Add WooCommerce body classes.
 *
 * @since 1.0.0
 * @param array $classes Body classes.
 * @return array Modified classes.
 */
function wpforge_woocommerce_body_classes($classes) {
    if (!wpforge_is_woocommerce_active()) {
        return $classes;
    }

    if (is_woocommerce() || is_cart() || is_checkout() || is_account_page()) {
        $classes[] = 'wpforge-woocommerce';

        $sidebar_position = get_theme_mod('wpforge_sidebar_position', 'right');
        $classes[] = 'sidebar-' . $sidebar_position;
    }

    return $classes;
}
add_filter('body_class', 'wpforge_woocommerce_body_classes');

/**
 * Get WooCommerce settings.
 *
 * @since 1.0.0
 * @return array WooCommerce settings.
 */
function wpforge_get_woocommerce_settings() {
    if (!wpforge_is_woocommerce_active()) {
        return array();
    }

    $settings = array(
        'products_per_row'      => get_theme_mod('wpforge_products_per_row', 4),
        'products_per_page'     => get_theme_mod('wpforge_products_per_page', 12),
        'show_product_image'    => get_theme_mod('wpforge_show_product_image', true),
        'show_price'            => get_theme_mod('wpforge_show_product_price', true),
        'show_rating'           => get_theme_mod('wpforge_show_product_rating', true),
        'show_add_to_cart'      => get_theme_mod('wpforge_show_add_to_cart', true),
        'product_page_layout'   => get_theme_mod('wpforge_product_page_layout', 'left-right'),
        'show_related_products' => get_theme_mod('wpforge_show_related_products', true),
        'related_products_count' => get_theme_mod('wpforge_related_products_count', 4),
        'show_upsells'          => get_theme_mod('wpforge_show_upsells', true),
        'show_product_tags'     => get_theme_mod('wpforge_show_product_tags', true),
        'show_product_category' => get_theme_mod('wpforge_show_product_category', true),
    );

    return $settings;
}

/**
 * Get WooCommerce compatibility info.
 *
 * @since 1.0.0
 * @return array WooCommerce compatibility information.
 */
function wpforge_get_woocommerce_compatibility() {
    return array(
        'name'      => 'WooCommerce',
        'supported' => true,
        'version'   => '5.0+',
        'features'  => array(
            'product_gallery'      => true,
            'gallery_zoom'         => true,
            'gallery_lightbox'     => true,
            'gallery_slider'       => true,
            'ajax_add_to_cart'     => true,
            'shop_sidebar'         => true,
            'customizer_integration' => true,
            'color_sync'           => true,
            'font_sync'            => true,
            'template_override'    => true,
        ),
    );
}
