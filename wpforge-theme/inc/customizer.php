<?php
/**
 * WPForge Theme - Customizer Settings
 *
 * 主题自定义设置面板，包含10个设置面板
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

// Exit if accessed directly.
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Initialize Customizer.
 *
 * @since 1.0.0
 * @param WP_Customize_Manager $wp_customize Theme Customizer object.
 */
function wpforge_customize_register($wp_customize) {
    // Add custom controls.
    require_once get_template_directory() . '/inc/customizer-controls.php';

    // ========== 1. Site Identity ==========
    // (Uses default WordPress section)

    // Add custom login logo setting.
    $wp_customize->add_setting('wpforge_login_logo', array(
        'default'           => '',
        'sanitize_callback' => 'esc_url_raw',
    ));

    $wp_customize->add_control(new WP_Customize_Image_Control($wp_customize, 'wpforge_login_logo', array(
        'label'    => __('Login Logo', 'wpforge-theme'),
        'section'  => 'title_tagline',
        'settings' => 'wpforge_login_logo',
        'priority' => 25,
    )));

    // Add site title toggle.
    $wp_customize->add_setting('wpforge_show_site_title', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_show_site_title', array(
        'label'    => __('Show Site Title', 'wpforge-theme'),
        'section'  => 'title_tagline',
        'settings' => 'wpforge_show_site_title',
        'type'     => 'checkbox',
        'priority' => 30,
    ));

    // Add site description toggle.
    $wp_customize->add_setting('wpforge_show_site_description', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_show_site_description', array(
        'label'    => __('Show Site Description', 'wpforge-theme'),
        'section'  => 'title_tagline',
        'settings' => 'wpforge_show_site_description',
        'type'     => 'checkbox',
        'priority' => 35,
    ));

    // ========== 2. Global Settings ==========

    // Add Global Settings panel.
    $wp_customize->add_panel('wpforge_global_panel', array(
        'title'    => __('Global Settings', 'wpforge-theme'),
        'priority' => 20,
    ));

    // --- Layout Section ---
    $wp_customize->add_section('wpforge_layout_section', array(
        'title' => __('Layout', 'wpforge-theme'),
        'panel' => 'wpforge_global_panel',
    ));

    // Site layout.
    $wp_customize->add_setting('wpforge_site_layout', array(
        'default'           => 'wide',
        'sanitize_callback' => 'wpforge_sanitize_select',
    ));

    $wp_customize->add_control('wpforge_site_layout', array(
        'label'   => __('Site Layout', 'wpforge-theme'),
        'section' => 'wpforge_layout_section',
        'type'    => 'select',
        'choices' => array(
            'wide'   => __('Wide', 'wpforge-theme'),
            'boxed'  => __('Boxed', 'wpforge-theme'),
            'narrow' => __('Narrow', 'wpforge-theme'),
        ),
    ));

    // Content width.
    $wp_customize->add_setting('wpforge_content_width', array(
        'default'           => 1200,
        'sanitize_callback' => 'absint',
    ));

    $wp_customize->add_control('wpforge_content_width', array(
        'label'   => __('Content Width (px)', 'wpforge-theme'),
        'section' => 'wpforge_layout_section',
        'type'    => 'number',
    ));

    // Sidebar position.
    $wp_customize->add_setting('wpforge_sidebar_position', array(
        'default'           => 'right',
        'sanitize_callback' => 'wpforge_sanitize_select',
    ));

    $wp_customize->add_control('wpforge_sidebar_position', array(
        'label'   => __('Sidebar Position', 'wpforge-theme'),
        'section' => 'wpforge_layout_section',
        'type'    => 'select',
        'choices' => array(
            'right' => __('Right', 'wpforge-theme'),
            'left'  => __('Left', 'wpforge-theme'),
            'none'  => __('None', 'wpforge-theme'),
        ),
    ));

    // Sidebar width.
    $wp_customize->add_setting('wpforge_sidebar_width', array(
        'default'           => 300,
        'sanitize_callback' => 'absint',
    ));

    $wp_customize->add_control('wpforge_sidebar_width', array(
        'label'   => __('Sidebar Width (px)', 'wpforge-theme'),
        'section' => 'wpforge_layout_section',
        'type'    => 'number',
    ));

    // --- Colors Section ---
    $wp_customize->add_section('wpforge_colors_section', array(
        'title' => __('Colors', 'wpforge-theme'),
        'panel' => 'wpforge_global_panel',
    ));

    // Primary color.
    $wp_customize->add_setting('wpforge_primary_color', array(
        'default'           => '#2563eb',
        'sanitize_callback' => 'sanitize_hex_color',
    ));

    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'wpforge_primary_color', array(
        'label'   => __('Primary Color', 'wpforge-theme'),
        'section' => 'wpforge_colors_section',
    )));

    // Secondary color.
    $wp_customize->add_setting('wpforge_secondary_color', array(
        'default'           => '#64748b',
        'sanitize_callback' => 'sanitize_hex_color',
    ));

    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'wpforge_secondary_color', array(
        'label'   => __('Secondary Color', 'wpforge-theme'),
        'section' => 'wpforge_colors_section',
    )));

    // Accent color.
    $wp_customize->add_setting('wpforge_accent_color', array(
        'default'           => '#f97316',
        'sanitize_callback' => 'sanitize_hex_color',
    ));

    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'wpforge_accent_color', array(
        'label'   => __('Accent Color', 'wpforge-theme'),
        'section' => 'wpforge_colors_section',
    )));

    // Text color.
    $wp_customize->add_setting('wpforge_text_color', array(
        'default'           => '#1e293b',
        'sanitize_callback' => 'sanitize_hex_color',
    ));

    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'wpforge_text_color', array(
        'label'   => __('Text Color', 'wpforge-theme'),
        'section' => 'wpforge_colors_section',
    )));

    // Background color.
    $wp_customize->add_setting('wpforge_background_color', array(
        'default'           => '#ffffff',
        'sanitize_callback' => 'sanitize_hex_color',
    ));

    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'wpforge_background_color', array(
        'label'   => __('Background Color', 'wpforge-theme'),
        'section' => 'wpforge_colors_section',
    )));

    // Border color.
    $wp_customize->add_setting('wpforge_border_color', array(
        'default'           => '#e2e8f0',
        'sanitize_callback' => 'sanitize_hex_color',
    ));

    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'wpforge_border_color', array(
        'label'   => __('Border Color', 'wpforge-theme'),
        'section' => 'wpforge_colors_section',
    )));

    // Dark mode.
    $wp_customize->add_setting('wpforge_dark_mode', array(
        'default'           => 'auto',
        'sanitize_callback' => 'wpforge_sanitize_select',
    ));

    $wp_customize->add_control('wpforge_dark_mode', array(
        'label'   => __('Dark Mode', 'wpforge-theme'),
        'section' => 'wpforge_colors_section',
        'type'    => 'select',
        'choices' => array(
            'auto'   => __('Auto (system preference)', 'wpforge-theme'),
            'manual' => __('Manual toggle', 'wpforge-theme'),
            'off'    => __('Off', 'wpforge-theme'),
        ),
    ));

    // --- Typography Section ---
    $wp_customize->add_section('wpforge_typography_section', array(
        'title' => __('Typography', 'wpforge-theme'),
        'panel' => 'wpforge_global_panel',
    ));

    // Body font.
    $wp_customize->add_setting('wpforge_body_font', array(
        'default'           => 'system-ui',
        'sanitize_callback' => 'wpforge_sanitize_select',
    ));

    $wp_customize->add_control('wpforge_body_font', array(
        'label'   => __('Body Font', 'wpforge-theme'),
        'section' => 'wpforge_typography_section',
        'type'    => 'select',
        'choices' => wpforge_get_font_choices(),
    ));

    // Heading font.
    $wp_customize->add_setting('wpforge_heading_font', array(
        'default'           => 'system-ui',
        'sanitize_callback' => 'wpforge_sanitize_select',
    ));

    $wp_customize->add_control('wpforge_heading_font', array(
        'label'   => __('Heading Font', 'wpforge-theme'),
        'section' => 'wpforge_typography_section',
        'type'    => 'select',
        'choices' => wpforge_get_font_choices(),
    ));

    // Body font size.
    $wp_customize->add_setting('wpforge_body_font_size', array(
        'default'           => 16,
        'sanitize_callback' => 'absint',
    ));

    $wp_customize->add_control('wpforge_body_font_size', array(
        'label'   => __('Body Font Size (px)', 'wpforge-theme'),
        'section' => 'wpforge_typography_section',
        'type'    => 'number',
    ));

    // Line height.
    $wp_customize->add_setting('wpforge_line_height', array(
        'default'           => 1.6,
        'sanitize_callback' => 'wpforge_sanitize_float',
    ));

    $wp_customize->add_control('wpforge_line_height', array(
        'label'   => __('Line Height', 'wpforge-theme'),
        'section' => 'wpforge_typography_section',
        'type'    => 'number',
    ));

    // --- Buttons Section ---
    $wp_customize->add_section('wpforge_buttons_section', array(
        'title' => __('Buttons', 'wpforge-theme'),
        'panel' => 'wpforge_global_panel',
    ));

    // Button background color.
    $wp_customize->add_setting('wpforge_button_bg_color', array(
        'default'           => '#2563eb',
        'sanitize_callback' => 'sanitize_hex_color',
    ));

    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'wpforge_button_bg_color', array(
        'label'   => __('Button Background', 'wpforge-theme'),
        'section' => 'wpforge_buttons_section',
    )));

    // Button text color.
    $wp_customize->add_setting('wpforge_button_text_color', array(
        'default'           => '#ffffff',
        'sanitize_callback' => 'sanitize_hex_color',
    ));

    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'wpforge_button_text_color', array(
        'label'   => __('Button Text Color', 'wpforge-theme'),
        'section' => 'wpforge_buttons_section',
    )));

    // Button border radius.
    $wp_customize->add_setting('wpforge_button_border_radius', array(
        'default'           => 6,
        'sanitize_callback' => 'absint',
    ));

    $wp_customize->add_control('wpforge_button_border_radius', array(
        'label'   => __('Button Border Radius (px)', 'wpforge-theme'),
        'section' => 'wpforge_buttons_section',
        'type'    => 'number',
    ));

    // ========== 3. Header Settings ==========

    $wp_customize->add_panel('wpforge_header_panel', array(
        'title'    => __('Header', 'wpforge-theme'),
        'priority' => 30,
    ));

    // --- Header Layout Section ---
    $wp_customize->add_section('wpforge_header_layout_section', array(
        'title' => __('Layout', 'wpforge-theme'),
        'panel' => 'wpforge_header_panel',
    ));

    // Header layout.
    $wp_customize->add_setting('wpforge_header_layout', array(
        'default'           => 'logo-left-nav-right',
        'sanitize_callback' => 'wpforge_sanitize_select',
    ));

    $wp_customize->add_control('wpforge_header_layout', array(
        'label'   => __('Header Layout', 'wpforge-theme'),
        'section' => 'wpforge_header_layout_section',
        'type'    => 'select',
        'choices' => array(
            'logo-left-nav-right'  => __('Logo Left + Navigation Right', 'wpforge-theme'),
            'logo-center-nav-below' => __('Logo Center + Navigation Below', 'wpforge-theme'),
            'logo-left-nav-center' => __('Logo Left + Navigation Center', 'wpforge-theme'),
        ),
    ));

    // Header height.
    $wp_customize->add_setting('wpforge_header_height', array(
        'default'           => 80,
        'sanitize_callback' => 'absint',
    ));

    $wp_customize->add_control('wpforge_header_height', array(
        'label'   => __('Header Height (px)', 'wpforge-theme'),
        'section' => 'wpforge_header_layout_section',
        'type'    => 'number',
    ));

    // Sticky header.
    $wp_customize->add_setting('wpforge_sticky_header', array(
        'default'           => false,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_sticky_header', array(
        'label'   => __('Sticky Header', 'wpforge-theme'),
        'section' => 'wpforge_header_layout_section',
        'type'    => 'checkbox',
    ));

    // Transparent header.
    $wp_customize->add_setting('wpforge_transparent_header', array(
        'default'           => false,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_transparent_header', array(
        'label'   => __('Transparent Header', 'wpforge-theme'),
        'section' => 'wpforge_header_layout_section',
        'type'    => 'checkbox',
    ));

    // --- Top Bar Section ---
    $wp_customize->add_section('wpforge_topbar_section', array(
        'title' => __('Top Bar', 'wpforge-theme'),
        'panel' => 'wpforge_header_panel',
    ));

    // Enable top bar.
    $wp_customize->add_setting('wpforge_topbar_enabled', array(
        'default'           => false,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_topbar_enabled', array(
        'label'   => __('Enable Top Bar', 'wpforge-theme'),
        'section' => 'wpforge_topbar_section',
        'type'    => 'checkbox',
    ));

    // Top bar content.
    $wp_customize->add_setting('wpforge_topbar_content', array(
        'default'           => 'text',
        'sanitize_callback' => 'wpforge_sanitize_select',
    ));

    $wp_customize->add_control('wpforge_topbar_content', array(
        'label'   => __('Top Bar Content', 'wpforge-theme'),
        'section' => 'wpforge_topbar_section',
        'type'    => 'select',
        'choices' => array(
            'text'     => __('Custom Text', 'wpforge-theme'),
            'social'   => __('Social Icons', 'wpforge-theme'),
            'contact'  => __('Contact Info', 'wpforge-theme'),
        ),
    ));

    // Top bar text.
    $wp_customize->add_setting('wpforge_topbar_text', array(
        'default'           => '',
        'sanitize_callback' => 'sanitize_text_field',
    ));

    $wp_customize->add_control('wpforge_topbar_text', array(
        'label'   => __('Top Bar Text', 'wpforge-theme'),
        'section' => 'wpforge_topbar_section',
        'type'    => 'text',
    ));

    // Top bar background color.
    $wp_customize->add_setting('wpforge_topbar_bg_color', array(
        'default'           => '#1e293b',
        'sanitize_callback' => 'sanitize_hex_color',
    ));

    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'wpforge_topbar_bg_color', array(
        'label'   => __('Top Bar Background', 'wpforge-theme'),
        'section' => 'wpforge_topbar_section',
    )));

    // Top bar text color.
    $wp_customize->add_setting('wpforge_topbar_text_color', array(
        'default'           => '#ffffff',
        'sanitize_callback' => 'sanitize_hex_color',
    ));

    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'wpforge_topbar_text_color', array(
        'label'   => __('Top Bar Text Color', 'wpforge-theme'),
        'section' => 'wpforge_topbar_section',
    )));

    // --- Mobile Header Section ---
    $wp_customize->add_section('wpforge_mobile_header_section', array(
        'title' => __('Mobile Header', 'wpforge-theme'),
        'panel' => 'wpforge_header_panel',
    ));

    // Mobile menu style.
    $wp_customize->add_setting('wpforge_mobile_menu_style', array(
        'default'           => 'drawer',
        'sanitize_callback' => 'wpforge_sanitize_select',
    ));

    $wp_customize->add_control('wpforge_mobile_menu_style', array(
        'label'   => __('Mobile Menu Style', 'wpforge-theme'),
        'section' => 'wpforge_mobile_header_section',
        'type'    => 'select',
        'choices' => array(
            'drawer'  => __('Slide Drawer', 'wpforge-theme'),
            'dropdown' => __('Dropdown', 'wpforge-theme'),
        ),
    ));

    // ========== 4. Footer Settings ==========

    $wp_customize->add_panel('wpforge_footer_panel', array(
        'title'    => __('Footer', 'wpforge-theme'),
        'priority' => 40,
    ));

    // --- Footer Layout Section ---
    $wp_customize->add_section('wpforge_footer_layout_section', array(
        'title' => __('Layout', 'wpforge-theme'),
        'panel' => 'wpforge_footer_panel',
    ));

    // Footer widget columns.
    $wp_customize->add_setting('wpforge_footer_widget_columns', array(
        'default'           => 4,
        'sanitize_callback' => 'absint',
    ));

    $wp_customize->add_control('wpforge_footer_widget_columns', array(
        'label'   => __('Footer Widget Columns', 'wpforge-theme'),
        'section' => 'wpforge_footer_layout_section',
        'type'    => 'select',
        'choices' => array(
            1 => '1',
            2 => '2',
            3 => '3',
            4 => '4',
        ),
    ));

    // Footer bottom bar.
    $wp_customize->add_setting('wpforge_footer_bottom_bar', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_footer_bottom_bar', array(
        'label'   => __('Show Footer Bottom Bar', 'wpforge-theme'),
        'section' => 'wpforge_footer_layout_section',
        'type'    => 'checkbox',
    ));

    // Copyright text.
    $wp_customize->add_setting('wpforge_copyright_text', array(
        'default'           => '',
        'sanitize_callback' => 'wpforge_sanitize_html',
    ));

    $wp_customize->add_control('wpforge_copyright_text', array(
        'label'   => __('Copyright Text', 'wpforge-theme'),
        'section' => 'wpforge_footer_layout_section',
        'type'    => 'textarea',
    ));

    // --- Footer Style Section ---
    $wp_customize->add_section('wpforge_footer_style_section', array(
        'title' => __('Style', 'wpforge-theme'),
        'panel' => 'wpforge_footer_panel',
    ));

    // Footer background color.
    $wp_customize->add_setting('wpforge_footer_bg_color', array(
        'default'           => '#1e293b',
        'sanitize_callback' => 'sanitize_hex_color',
    ));

    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'wpforge_footer_bg_color', array(
        'label'   => __('Footer Background', 'wpforge-theme'),
        'section' => 'wpforge_footer_style_section',
    )));

    // Footer text color.
    $wp_customize->add_setting('wpforge_footer_text_color', array(
        'default'           => '#94a3b8',
        'sanitize_callback' => 'sanitize_hex_color',
    ));

    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'wpforge_footer_text_color', array(
        'label'   => __('Footer Text Color', 'wpforge-theme'),
        'section' => 'wpforge_footer_style_section',
    )));

    // Footer link color.
    $wp_customize->add_setting('wpforge_footer_link_color', array(
        'default'           => '#ffffff',
        'sanitize_callback' => 'sanitize_hex_color',
    ));

    $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'wpforge_footer_link_color', array(
        'label'   => __('Footer Link Color', 'wpforge-theme'),
        'section' => 'wpforge_footer_style_section',
    )));

    // --- Back to Top Section ---
    $wp_customize->add_section('wpforge_back_to_top_section', array(
        'title' => __('Back to Top', 'wpforge-theme'),
        'panel' => 'wpforge_footer_panel',
    ));

    // Enable back to top.
    $wp_customize->add_setting('wpforge_back_to_top', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_back_to_top', array(
        'label'   => __('Enable Back to Top Button', 'wpforge-theme'),
        'section' => 'wpforge_back_to_top_section',
        'type'    => 'checkbox',
    ));

    // Back to top position.
    $wp_customize->add_setting('wpforge_back_to_top_position', array(
        'default'           => 'right',
        'sanitize_callback' => 'wpforge_sanitize_select',
    ));

    $wp_customize->add_control('wpforge_back_to_top_position', array(
        'label'   => __('Position', 'wpforge-theme'),
        'section' => 'wpforge_back_to_top_section',
        'type'    => 'select',
        'choices' => array(
            'right' => __('Bottom Right', 'wpforge-theme'),
            'left'  => __('Bottom Left', 'wpforge-theme'),
        ),
    ));

    // ========== 5. Blog Settings ==========

    $wp_customize->add_panel('wpforge_blog_panel', array(
        'title'    => __('Blog / Posts', 'wpforge-theme'),
        'priority' => 50,
    ));

    // --- Blog List Section ---
    $wp_customize->add_section('wpforge_blog_list_section', array(
        'title' => __('Blog List', 'wpforge-theme'),
        'panel' => 'wpforge_blog_panel',
    ));

    // Blog layout.
    $wp_customize->add_setting('wpforge_blog_layout', array(
        'default'           => 'grid',
        'sanitize_callback' => 'wpforge_sanitize_select',
    ));

    $wp_customize->add_control('wpforge_blog_layout', array(
        'label'   => __('Blog Layout', 'wpforge-theme'),
        'section' => 'wpforge_blog_list_section',
        'type'    => 'select',
        'choices' => array(
            'grid'    => __('Grid', 'wpforge-theme'),
            'list'    => __('List', 'wpforge-theme'),
            'classic' => __('Classic', 'wpforge-theme'),
        ),
    ));

    // Posts per row.
    $wp_customize->add_setting('wpforge_posts_per_row', array(
        'default'           => 3,
        'sanitize_callback' => 'absint',
    ));

    $wp_customize->add_control('wpforge_posts_per_row', array(
        'label'   => __('Posts Per Row', 'wpforge-theme'),
        'section' => 'wpforge_blog_list_section',
        'type'    => 'select',
        'choices' => array(
            1 => '1',
            2 => '2',
            3 => '3',
            4 => '4',
        ),
    ));

    // Show featured image.
    $wp_customize->add_setting('wpforge_show_featured_image', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_show_featured_image', array(
        'label'   => __('Show Featured Image', 'wpforge-theme'),
        'section' => 'wpforge_blog_list_section',
        'type'    => 'checkbox',
    ));

    // Show category.
    $wp_customize->add_setting('wpforge_show_category', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_show_category', array(
        'label'   => __('Show Category', 'wpforge-theme'),
        'section' => 'wpforge_blog_list_section',
        'type'    => 'checkbox',
    ));

    // Show date.
    $wp_customize->add_setting('wpforge_show_date', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_show_date', array(
        'label'   => __('Show Date', 'wpforge-theme'),
        'section' => 'wpforge_blog_list_section',
        'type'    => 'checkbox',
    ));

    // Show author.
    $wp_customize->add_setting('wpforge_show_author', array(
        'default'           => false,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_show_author', array(
        'label'   => __('Show Author', 'wpforge-theme'),
        'section' => 'wpforge_blog_list_section',
        'type'    => 'checkbox',
    ));

    // Excerpt length.
    $wp_customize->add_setting('wpforge_excerpt_length', array(
        'default'           => 30,
        'sanitize_callback' => 'absint',
    ));

    $wp_customize->add_control('wpforge_excerpt_length', array(
        'label'   => __('Excerpt Length (words)', 'wpforge-theme'),
        'section' => 'wpforge_blog_list_section',
        'type'    => 'number',
    ));

    // Read more text.
    $wp_customize->add_setting('wpforge_read_more_text', array(
        'default'           => __('Read More', 'wpforge-theme'),
        'sanitize_callback' => 'sanitize_text_field',
    ));

    $wp_customize->add_control('wpforge_read_more_text', array(
        'label'   => __('Read More Text', 'wpforge-theme'),
        'section' => 'wpforge_blog_list_section',
        'type'    => 'text',
    ));

    // --- Single Post Section ---
    $wp_customize->add_section('wpforge_single_post_section', array(
        'title' => __('Single Post', 'wpforge-theme'),
        'panel' => 'wpforge_blog_panel',
    ));

    // Single post layout.
    $wp_customize->add_setting('wpforge_single_post_layout', array(
        'default'           => 'sidebar',
        'sanitize_callback' => 'wpforge_sanitize_select',
    ));

    $wp_customize->add_control('wpforge_single_post_layout', array(
        'label'   => __('Single Post Layout', 'wpforge-theme'),
        'section' => 'wpforge_single_post_section',
        'type'    => 'select',
        'choices' => array(
            'full-width' => __('Full Width', 'wpforge-theme'),
            'sidebar'    => __('With Sidebar', 'wpforge-theme'),
        ),
    ));

    // Show featured image on single.
    $wp_customize->add_setting('wpforge_single_show_featured', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_single_show_featured', array(
        'label'   => __('Show Featured Image', 'wpforge-theme'),
        'section' => 'wpforge_single_post_section',
        'type'    => 'checkbox',
    ));

    // Show tags.
    $wp_customize->add_setting('wpforge_show_tags', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_show_tags', array(
        'label'   => __('Show Tags', 'wpforge-theme'),
        'section' => 'wpforge_single_post_section',
        'type'    => 'checkbox',
    ));

    // Show prev/next.
    $wp_customize->add_setting('wpforge_show_prev_next', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_show_prev_next', array(
        'label'   => __('Show Previous/Next', 'wpforge-theme'),
        'section' => 'wpforge_single_post_section',
        'type'    => 'checkbox',
    ));

    // Show related posts.
    $wp_customize->add_setting('wpforge_show_related_posts', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_show_related_posts', array(
        'label'   => __('Show Related Posts', 'wpforge-theme'),
        'section' => 'wpforge_single_post_section',
        'type'    => 'checkbox',
    ));

    // Related posts count.
    $wp_customize->add_setting('wpforge_related_posts_count', array(
        'default'           => 3,
        'sanitize_callback' => 'absint',
    ));

    $wp_customize->add_control('wpforge_related_posts_count', array(
        'label'   => __('Related Posts Count', 'wpforge-theme'),
        'section' => 'wpforge_single_post_section',
        'type'    => 'number',
    ));

    // Show author box.
    $wp_customize->add_setting('wpforge_show_author_box', array(
        'default'           => false,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_show_author_box', array(
        'label'   => __('Show Author Box', 'wpforge-theme'),
        'section' => 'wpforge_single_post_section',
        'type'    => 'checkbox',
    ));

    // ========== 6. Page Settings ==========

    $wp_customize->add_section('wpforge_page_section', array(
        'title'    => __('Pages', 'wpforge-theme'),
        'priority' => 60,
    ));

    // Show page title.
    $wp_customize->add_setting('wpforge_show_page_title', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_show_page_title', array(
        'label'   => __('Show Page Title', 'wpforge-theme'),
        'section' => 'wpforge_page_section',
        'type'    => 'checkbox',
    ));

    // Show page featured image.
    $wp_customize->add_setting('wpforge_show_page_featured', array(
        'default'           => false,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_show_page_featured', array(
        'label'   => __('Show Featured Image', 'wpforge-theme'),
        'section' => 'wpforge_page_section',
        'type'    => 'checkbox',
    ));

    // ========== 7. WooCommerce Settings ==========

    if (class_exists('WooCommerce')) {
        $wp_customize->add_panel('wpforge_woocommerce_panel', array(
            'title'    => __('WooCommerce', 'wpforge-theme'),
            'priority' => 70,
        ));

        // --- Shop Page Section ---
        $wp_customize->add_section('wpforge_shop_page_section', array(
            'title' => __('Shop Page', 'wpforge-theme'),
            'panel' => 'wpforge_woocommerce_panel',
        ));

        // Products per row.
        $wp_customize->add_setting('wpforge_products_per_row', array(
            'default'           => 4,
            'sanitize_callback' => 'absint',
        ));

        $wp_customize->add_control('wpforge_products_per_row', array(
            'label'   => __('Products Per Row', 'wpforge-theme'),
            'section' => 'wpforge_shop_page_section',
            'type'    => 'select',
            'choices' => array(
                2 => '2',
                3 => '3',
                4 => '4',
                5 => '5',
                6 => '6',
            ),
        ));

        // Show product image.
        $wp_customize->add_setting('wpforge_show_product_image', array(
            'default'           => true,
            'sanitize_callback' => 'wpforge_sanitize_checkbox',
        ));

        $wp_customize->add_control('wpforge_show_product_image', array(
            'label'   => __('Show Product Image', 'wpforge-theme'),
            'section' => 'wpforge_shop_page_section',
            'type'    => 'checkbox',
        ));

        // Show price.
        $wp_customize->add_setting('wpforge_show_product_price', array(
            'default'           => true,
            'sanitize_callback' => 'wpforge_sanitize_checkbox',
        ));

        $wp_customize->add_control('wpforge_show_product_price', array(
            'label'   => __('Show Price', 'wpforge-theme'),
            'section' => 'wpforge_shop_page_section',
            'type'    => 'checkbox',
        ));

        // Show rating.
        $wp_customize->add_setting('wpforge_show_product_rating', array(
            'default'           => true,
            'sanitize_callback' => 'wpforge_sanitize_checkbox',
        ));

        $wp_customize->add_control('wpforge_show_product_rating', array(
            'label'   => __('Show Rating', 'wpforge-theme'),
            'section' => 'wpforge_shop_page_section',
            'type'    => 'checkbox',
        ));

        // Show add to cart button.
        $wp_customize->add_setting('wpforge_show_add_to_cart', array(
            'default'           => true,
            'sanitize_callback' => 'wpforge_sanitize_checkbox',
        ));

        $wp_customize->add_control('wpforge_show_add_to_cart', array(
            'label'   => __('Show Add to Cart Button', 'wpforge-theme'),
            'section' => 'wpforge_shop_page_section',
            'type'    => 'checkbox',
        ));

        // --- Product Page Section ---
        $wp_customize->add_section('wpforge_product_page_section', array(
            'title' => __('Product Page', 'wpforge-theme'),
            'panel' => 'wpforge_woocommerce_panel',
        ));

        // Product page layout.
        $wp_customize->add_setting('wpforge_product_page_layout', array(
            'default'           => 'left-right',
            'sanitize_callback' => 'wpforge_sanitize_select',
        ));

        $wp_customize->add_control('wpforge_product_page_layout', array(
            'label'   => __('Product Page Layout', 'wpforge-theme'),
            'section' => 'wpforge_product_page_section',
            'type'    => 'select',
            'choices' => array(
                'left-right' => __('Image Left + Info Right', 'wpforge-theme'),
                'top-bottom' => __('Image Top + Info Bottom', 'wpforge-theme'),
            ),
        ));

        // Show related products.
        $wp_customize->add_setting('wpforge_show_related_products', array(
            'default'           => true,
            'sanitize_callback' => 'wpforge_sanitize_checkbox',
        ));

        $wp_customize->add_control('wpforge_show_related_products', array(
            'label'   => __('Show Related Products', 'wpforge-theme'),
            'section' => 'wpforge_product_page_section',
            'type'    => 'checkbox',
        ));

        // Related products count.
        $wp_customize->add_setting('wpforge_related_products_count', array(
            'default'           => 4,
            'sanitize_callback' => 'absint',
        ));

        $wp_customize->add_control('wpforge_related_products_count', array(
            'label'   => __('Related Products Count', 'wpforge-theme'),
            'section' => 'wpforge_product_page_section',
            'type'    => 'number',
        ));

        // Show upsells.
        $wp_customize->add_setting('wpforge_show_upsells', array(
            'default'           => true,
            'sanitize_callback' => 'wpforge_sanitize_checkbox',
        ));

        $wp_customize->add_control('wpforge_show_upsells', array(
            'label'   => __('Show Upsells', 'wpforge-theme'),
            'section' => 'wpforge_product_page_section',
            'type'    => 'checkbox',
        ));

        // Show product tags.
        $wp_customize->add_setting('wpforge_show_product_tags', array(
            'default'           => true,
            'sanitize_callback' => 'wpforge_sanitize_checkbox',
        ));

        $wp_customize->add_control('wpforge_show_product_tags', array(
            'label'   => __('Show Product Tags', 'wpforge-theme'),
            'section' => 'wpforge_product_page_section',
            'type'    => 'checkbox',
        ));

        // Show product category.
        $wp_customize->add_setting('wpforge_show_product_category', array(
            'default'           => true,
            'sanitize_callback' => 'wpforge_sanitize_checkbox',
        ));

        $wp_customize->add_control('wpforge_show_product_category', array(
            'label'   => __('Show Product Category', 'wpforge-theme'),
            'section' => 'wpforge_product_page_section',
            'type'    => 'checkbox',
        ));
    }

    // ========== 8. SEO Settings ==========

    $wp_customize->add_panel('wpforge_seo_panel', array(
        'title'    => __('SEO', 'wpforge-theme'),
        'priority' => 80,
    ));

    // --- Basic SEO Section ---
    $wp_customize->add_section('wpforge_basic_seo_section', array(
        'title' => __('Basic SEO', 'wpforge-theme'),
        'panel' => 'wpforge_seo_panel',
    ));

    // Enable SEO.
    $wp_customize->add_setting('wpforge_seo_enabled', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_seo_enabled', array(
        'label'   => __('Enable SEO Features', 'wpforge-theme'),
        'section' => 'wpforge_basic_seo_section',
        'type'    => 'checkbox',
    ));

    // Auto generate meta description.
    $wp_customize->add_setting('wpforge_auto_meta_description', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_auto_meta_description', array(
        'label'   => __('Auto Generate Meta Description', 'wpforge-theme'),
        'section' => 'wpforge_basic_seo_section',
        'type'    => 'checkbox',
    ));

    // Auto generate keywords.
    $wp_customize->add_setting('wpforge_auto_keywords', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_auto_keywords', array(
        'label'   => __('Auto Generate Keywords', 'wpforge-theme'),
        'section' => 'wpforge_basic_seo_section',
        'type'    => 'checkbox',
    ));

    // Title separator.
    $wp_customize->add_setting('wpforge_title_separator', array(
        'default'           => '-',
        'sanitize_callback' => 'sanitize_text_field',
    ));

    $wp_customize->add_control('wpforge_title_separator', array(
        'label'   => __('Title Separator', 'wpforge-theme'),
        'section' => 'wpforge_basic_seo_section',
        'type'    => 'text',
    ));

    // --- Schema Section ---
    $wp_customize->add_section('wpforge_schema_section', array(
        'title' => __('Schema Markup', 'wpforge-theme'),
        'panel' => 'wpforge_seo_panel',
    ));

    // Enable Schema.
    $wp_customize->add_setting('wpforge_schema_enabled', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_schema_enabled', array(
        'label'   => __('Enable Schema Markup', 'wpforge-theme'),
        'section' => 'wpforge_schema_section',
        'type'    => 'checkbox',
    ));

    // Article Schema.
    $wp_customize->add_setting('wpforge_article_schema', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_article_schema', array(
        'label'   => __('Article Schema', 'wpforge-theme'),
        'section' => 'wpforge_schema_section',
        'type'    => 'checkbox',
    ));

    // Product Schema.
    $wp_customize->add_setting('wpforge_product_schema', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_product_schema', array(
        'label'   => __('Product Schema (WooCommerce)', 'wpforge-theme'),
        'section' => 'wpforge_schema_section',
        'type'    => 'checkbox',
    ));

    // Breadcrumb Schema.
    $wp_customize->add_setting('wpforge_breadcrumb_schema', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_breadcrumb_schema', array(
        'label'   => __('Breadcrumb Schema', 'wpforge-theme'),
        'section' => 'wpforge_schema_section',
        'type'    => 'checkbox',
    ));

    // Organization Schema.
    $wp_customize->add_setting('wpforge_organization_schema', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_organization_schema', array(
        'label'   => __('Organization Schema', 'wpforge-theme'),
        'section' => 'wpforge_schema_section',
        'type'    => 'checkbox',
    ));

    // --- Breadcrumb Section ---
    $wp_customize->add_section('wpforge_breadcrumb_section', array(
        'title' => __('Breadcrumb', 'wpforge-theme'),
        'panel' => 'wpforge_seo_panel',
    ));

    // Enable breadcrumb.
    $wp_customize->add_setting('wpforge_breadcrumb_enabled', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_breadcrumb_enabled', array(
        'label'   => __('Enable Breadcrumb', 'wpforge-theme'),
        'section' => 'wpforge_breadcrumb_section',
        'type'    => 'checkbox',
    ));

    // Breadcrumb separator.
    $wp_customize->add_setting('wpforge_breadcrumb_separator', array(
        'default'           => '/',
        'sanitize_callback' => 'sanitize_text_field',
    ));

    $wp_customize->add_control('wpforge_breadcrumb_separator', array(
        'label'   => __('Breadcrumb Separator', 'wpforge-theme'),
        'section' => 'wpforge_breadcrumb_section',
        'type'    => 'text',
    ));

    // Show breadcrumb on home.
    $wp_customize->add_setting('wpforge_breadcrumb_show_home', array(
        'default'           => false,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_breadcrumb_show_home', array(
        'label'   => __('Show on Home Page', 'wpforge-theme'),
        'section' => 'wpforge_breadcrumb_section',
        'type'    => 'checkbox',
    ));

    // --- Social Section ---
    $wp_customize->add_section('wpforge_social_seo_section', array(
        'title' => __('Social Sharing', 'wpforge-theme'),
        'panel' => 'wpforge_seo_panel',
    ));

    // Open Graph.
    $wp_customize->add_setting('wpforge_open_graph_enabled', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_open_graph_enabled', array(
        'label'   => __('Open Graph', 'wpforge-theme'),
        'section' => 'wpforge_social_seo_section',
        'type'    => 'checkbox',
    ));

    // Twitter Cards.
    $wp_customize->add_setting('wpforge_twitter_cards_enabled', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_twitter_cards_enabled', array(
        'label'   => __('Twitter Cards', 'wpforge-theme'),
        'section' => 'wpforge_social_seo_section',
        'type'    => 'checkbox',
    ));

    // ========== 9. Performance Settings ==========

    $wp_customize->add_panel('wpforge_performance_panel', array(
        'title'    => __('Performance', 'wpforge-theme'),
        'priority' => 90,
    ));

    // --- CSS Optimization Section ---
    $wp_customize->add_section('wpforge_css_optimization_section', array(
        'title' => __('CSS Optimization', 'wpforge-theme'),
        'panel' => 'wpforge_performance_panel',
    ));

    // Disable Gutenberg block styles.
    $wp_customize->add_setting('wpforge_disable_gutenberg_styles', array(
        'default'           => false,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_disable_gutenberg_styles', array(
        'label'   => __('Disable Gutenberg Block Styles', 'wpforge-theme'),
        'section' => 'wpforge_css_optimization_section',
        'type'    => 'checkbox',
    ));

    // --- JS Optimization Section ---
    $wp_customize->add_section('wpforge_js_optimization_section', array(
        'title' => __('JavaScript Optimization', 'wpforge-theme'),
        'panel' => 'wpforge_performance_panel',
    ));

    // Defer JS.
    $wp_customize->add_setting('wpforge_defer_js', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_defer_js', array(
        'label'   => __('Defer JavaScript', 'wpforge-theme'),
        'section' => 'wpforge_js_optimization_section',
        'type'    => 'checkbox',
    ));

    // Disable jQuery Migrate.
    $wp_customize->add_setting('wpforge_disable_jquery_migrate', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_disable_jquery_migrate', array(
        'label'   => __('Disable jQuery Migrate', 'wpforge-theme'),
        'section' => 'wpforge_js_optimization_section',
        'type'    => 'checkbox',
    ));

    // Disable WP Embed.
    $wp_customize->add_setting('wpforge_disable_embeds', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_disable_embeds', array(
        'label'   => __('Disable WP Embed', 'wpforge-theme'),
        'section' => 'wpforge_js_optimization_section',
        'type'    => 'checkbox',
    ));

    // --- Image Optimization Section ---
    $wp_customize->add_section('wpforge_image_optimization_section', array(
        'title' => __('Image Optimization', 'wpforge-theme'),
        'panel' => 'wpforge_performance_panel',
    ));

    // Lazy load images.
    $wp_customize->add_setting('wpforge_lazy_load_images', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_lazy_load_images', array(
        'label'   => __('Lazy Load Images', 'wpforge-theme'),
        'section' => 'wpforge_image_optimization_section',
        'type'    => 'checkbox',
    ));

    // --- WordPress Optimization Section ---
    $wp_customize->add_section('wpforge_wp_optimization_section', array(
        'title' => __('WordPress Optimization', 'wpforge-theme'),
        'panel' => 'wpforge_performance_panel',
    ));

    // Disable emojis.
    $wp_customize->add_setting('wpforge_disable_emojis', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_disable_emojis', array(
        'label'   => __('Disable Emojis', 'wpforge-theme'),
        'section' => 'wpforge_wp_optimization_section',
        'type'    => 'checkbox',
    ));

    // Remove WP version.
    $wp_customize->add_setting('wpforge_remove_wp_version', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_remove_wp_version', array(
        'label'   => __('Remove WP Version', 'wpforge-theme'),
        'section' => 'wpforge_wp_optimization_section',
        'type'    => 'checkbox',
    ));

    // Disable XML-RPC.
    $wp_customize->add_setting('wpforge_disable_xmlrpc', array(
        'default'           => true,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_disable_xmlrpc', array(
        'label'   => __('Disable XML-RPC', 'wpforge-theme'),
        'section' => 'wpforge_wp_optimization_section',
        'type'    => 'checkbox',
    ));

    // Heartbeat frequency.
    $wp_customize->add_setting('wpforge_heartbeat_frequency', array(
        'default'           => 60,
        'sanitize_callback' => 'absint',
    ));

    $wp_customize->add_control('wpforge_heartbeat_frequency', array(
        'label'   => __('Heartbeat Frequency (seconds)', 'wpforge-theme'),
        'section' => 'wpforge_wp_optimization_section',
        'type'    => 'number',
    ));

    // Revision limit.
    $wp_customize->add_setting('wpforge_revision_limit', array(
        'default'           => 10,
        'sanitize_callback' => 'absint',
    ));

    $wp_customize->add_control('wpforge_revision_limit', array(
        'label'   => __('Post Revision Limit', 'wpforge-theme'),
        'section' => 'wpforge_wp_optimization_section',
        'type'    => 'number',
    ));

    // ========== 10. WPForge Integration ==========

    $wp_customize->add_section('wpforge_integration_section', array(
        'title'    => __('WPForge Integration', 'wpforge-theme'),
        'priority' => 100,
    ));

    // Theme version info.
    $wp_customize->add_setting('wpforge_theme_version_info', array(
        'sanitize_callback' => 'sanitize_text_field',
    ));

    $wp_customize->add_control(new WPForge_Customize_Info_Control($wp_customize, 'wpforge_theme_version_info', array(
        'label'   => __('Theme Version', 'wpforge-theme'),
        'section' => 'wpforge_integration_section',
        'info'    => WPFORGE_THEME_VERSION,
    )));

    // Debug mode.
    $wp_customize->add_setting('wpforge_debug_mode', array(
        'default'           => false,
        'sanitize_callback' => 'wpforge_sanitize_checkbox',
    ));

    $wp_customize->add_control('wpforge_debug_mode', array(
        'label'   => __('Debug Mode', 'wpforge-theme'),
        'section' => 'wpforge_integration_section',
        'type'    => 'checkbox',
    ));

    // Preset selector.
    $wp_customize->add_setting('wpforge_preset', array(
        'default'           => 'default',
        'sanitize_callback' => 'wpforge_sanitize_select',
    ));

    $wp_customize->add_control('wpforge_preset', array(
        'label'   => __('Apply Preset', 'wpforge-theme'),
        'section' => 'wpforge_integration_section',
        'type'    => 'select',
        'choices' => wpforge_get_preset_choices(),
    ));
}
add_action('customize_register', 'wpforge_customize_register');

/**
 * Sanitize checkbox.
 *
 * @since 1.0.0
 * @param bool $value Checkbox value.
 * @return bool Sanitized value.
 */
function wpforge_sanitize_checkbox($value) {
    return (bool) $value;
}

/**
 * Sanitize select.
 *
 * @since 1.0.0
 * @param string $value Select value.
 * @param WP_Customize_Setting $setting Setting object.
 * @return string Sanitized value.
 */
function wpforge_sanitize_select($value, $setting) {
    // Ensure value is a slug.
    $value = sanitize_key($value);

    // Get list of valid choices.
    $choices = $setting->manager->get_control($setting->id)->choices;

    // Return default if value is not valid.
    return array_key_exists($value, $choices) ? $value : $setting->default;
}

/**
 * Sanitize float.
 *
 * @since 1.0.0
 * @param float $value Float value.
 * @return float Sanitized value.
 */
function wpforge_sanitize_float($value) {
    return floatval($value);
}

/**
 * Sanitize HTML.
 *
 * @since 1.0.0
 * @param string $value HTML value.
 * @return string Sanitized value.
 */
function wpforge_sanitize_html($value) {
    return wp_kses_post($value);
}

/**
 * Get font choices.
 *
 * @since 1.0.0
 * @return array Font choices.
 */
function wpforge_get_font_choices() {
    return array(
        'system-ui'        => __('System UI (Recommended)', 'wpforge-theme'),
        '-apple-system'    => __('Apple System', 'wpforge-theme'),
        'Segoe UI'         => __('Segoe UI', 'wpforge-theme'),
        'Roboto'           => __('Roboto', 'wpforge-theme'),
        'Helvetica Neue'   => __('Helvetica Neue', 'wpforge-theme'),
        'Arial'            => __('Arial', 'wpforge-theme'),
        'sans-serif'       => __('Sans Serif', 'wpforge-theme'),
        'Georgia'          => __('Georgia', 'wpforge-theme'),
        'Times New Roman'  => __('Times New Roman', 'wpforge-theme'),
        'serif'            => __('Serif', 'wpforge-theme'),
        'Monaco'           => __('Monaco', 'wpforge-theme'),
        'Consolas'         => __('Consolas', 'wpforge-theme'),
        'monospace'        => __('Monospace', 'wpforge-theme'),
    );
}

/**
 * Get preset choices.
 *
 * @since 1.0.0
 * @return array Preset choices.
 */
function wpforge_get_preset_choices() {
    return array(
        'default'   => __('Default', 'wpforge-theme'),
        'modern'    => __('Modern Blue', 'wpforge-theme'),
        'elegant'   => __('Elegant Purple', 'wpforge-theme'),
        'fresh'     => __('Fresh Green', 'wpforge-theme'),
        'warm'      => __('Warm Orange', 'wpforge-theme'),
        'dark'      => __('Dark Mode', 'wpforge-theme'),
        'minimal'   => __('Minimal Black', 'wpforge-theme'),
        'ecommerce' => __('E-Commerce', 'wpforge-theme'),
        'blog'      => __('Blog Style', 'wpforge-theme'),
        'corporate' => __('Corporate', 'wpforge-theme'),
    );
}

/**
 * Output Customizer CSS.
 *
 * @since 1.0.0
 */
function wpforge_customize_css() {
    $css = '';

    // Primary color.
    $primary_color = get_theme_mod('wpforge_primary_color', '#2563eb');
    if ($primary_color) {
        $css .= ":root { --wpforge-primary: {$primary_color}; }\n";
    }

    // Secondary color.
    $secondary_color = get_theme_mod('wpforge_secondary_color', '#64748b');
    if ($secondary_color) {
        $css .= ":root { --wpforge-secondary: {$secondary_color}; }\n";
    }

    // Accent color.
    $accent_color = get_theme_mod('wpforge_accent_color', '#f97316');
    if ($accent_color) {
        $css .= ":root { --wpforge-accent: {$accent_color}; }\n";
    }

    // Text color.
    $text_color = get_theme_mod('wpforge_text_color', '#1e293b');
    if ($text_color) {
        $css .= ":root { --wpforge-text: {$text_color}; }\n";
    }

    // Background color.
    $bg_color = get_theme_mod('wpforge_background_color', '#ffffff');
    if ($bg_color) {
        $css .= ":root { --wpforge-background: {$bg_color}; }\n";
    }

    // Border color.
    $border_color = get_theme_mod('wpforge_border_color', '#e2e8f0');
    if ($border_color) {
        $css .= ":root { --wpforge-border: {$border_color}; }\n";
    }

    // Content width.
    $content_width = get_theme_mod('wpforge_content_width', 1200);
    if ($content_width) {
        $css .= ":root { --wpforge-content-width: {$content_width}px; }\n";
    }

    // Sidebar width.
    $sidebar_width = get_theme_mod('wpforge_sidebar_width', 300);
    if ($sidebar_width) {
        $css .= ":root { --wpforge-sidebar-width: {$sidebar_width}px; }\n";
    }

    // Body font size.
    $body_font_size = get_theme_mod('wpforge_body_font_size', 16);
    if ($body_font_size) {
        $css .= ":root { --wpforge-font-size-base: {$body_font_size}px; }\n";
    }

    // Line height.
    $line_height = get_theme_mod('wpforge_line_height', 1.6);
    if ($line_height) {
        $css .= ":root { --wpforge-line-height: {$line_height}; }\n";
    }

    // Button border radius.
    $button_radius = get_theme_mod('wpforge_button_border_radius', 6);
    if ($button_radius) {
        $css .= ":root { --wpforge-button-radius: {$button_radius}px; }\n";
    }

    // Header height.
    $header_height = get_theme_mod('wpforge_header_height', 80);
    if ($header_height) {
        $css .= ":root { --wpforge-header-height: {$header_height}px; }\n";
    }

    // Footer background.
    $footer_bg = get_theme_mod('wpforge_footer_bg_color', '#1e293b');
    if ($footer_bg) {
        $css .= ":root { --wpforge-footer-bg: {$footer_bg}; }\n";
    }

    // Footer text color.
    $footer_text = get_theme_mod('wpforge_footer_text_color', '#94a3b8');
    if ($footer_text) {
        $css .= ":root { --wpforge-footer-text: {$footer_text}; }\n";
    }

    // Footer link color.
    $footer_link = get_theme_mod('wpforge_footer_link_color', '#ffffff');
    if ($footer_link) {
        $css .= ":root { --wpforge-footer-link: {$footer_link}; }\n";
    }

    // Output CSS.
    if ($css) {
        echo '<style id="wpforge-customizer-css">' . $css . '</style>';
    }
}
add_action('wp_head', 'wpforge_customize_css', 3);

/**
 * Custom Customizer Control Classes.
 *
 * @since 1.0.0
 */
if (class_exists('WP_Customize_Control')) {

    /**
     * Info control.
     *
     * @since 1.0.0
     */
    class WPForge_Customize_Info_Control extends WP_Customize_Control {
        public $type = 'info';
        public $info = '';

        public function render_content() {
            ?>
            <label>
                <?php if (!empty($this->label)) : ?>
                    <span class="customize-control-title"><?php echo esc_html($this->label); ?></span>
                <?php endif; ?>
                <?php if (!empty($this->info)) : ?>
                    <div class="customize-control-info" style="padding: 10px; background: #f0f0f1; border-radius: 4px; font-family: monospace;">
                        <?php echo esc_html($this->info); ?>
                    </div>
                <?php endif; ?>
            </label>
            <?php
        }
    }
}
