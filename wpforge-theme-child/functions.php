<?php
/**
 * WPForge Theme Child - Functions
 *
 * Child theme functions file
 *
 * @package WPForge_Theme_Child
 * @since 1.0.0
 */

// Exit if accessed directly.
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Enqueue parent and child theme styles.
 *
 * @since 1.0.0
 */
function wpforge_child_enqueue_styles() {
    // Enqueue parent theme styles.
    wp_enqueue_style(
        'wpforge-parent-style',
        get_template_directory_uri() . '/style.css',
        array(),
        wp_get_theme()->parent()->get('Version')
    );

    // Enqueue child theme styles.
    wp_enqueue_style(
        'wpforge-child-style',
        get_stylesheet_directory_uri() . '/style.css',
        array('wpforge-parent-style'),
        wp_get_theme()->get('Version')
    );
}
add_action('wp_enqueue_scripts', 'wpforge_child_enqueue_styles', 10);

/**
 * Example: Add custom function below.
 *
 * @since 1.0.0
 */
/*
function wpforge_child_custom_function() {
    // Your custom code here.
}
add_action('wp_head', 'wpforge_child_custom_function');
*/
