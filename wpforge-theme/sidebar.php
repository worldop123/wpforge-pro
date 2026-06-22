<?php
/**
 * The sidebar containing the main widget area
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

$sidebar_position = get_theme_mod('wpforge_sidebar_position', 'right');

if ('none' === $sidebar_position) {
    return;
}

if (!is_active_sidebar('sidebar-1')) {
    return;
}
?>

<aside id="secondary" class="widget-area" role="complementary">
    <?php do_action('wpforge_before_sidebar'); ?>

    <?php dynamic_sidebar('sidebar-1'); ?>

    <?php do_action('wpforge_after_sidebar'); ?>
</aside>
