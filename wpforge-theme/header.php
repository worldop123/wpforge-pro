<?php
/**
 * The header for our theme
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */
?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="profile" href="https://gmpg.org/xfn/11">

    <?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<a class="skip-link screen-reader-text" href="#primary"><?php esc_html_e('Skip to content', 'wpforge-theme'); ?></a>

<?php do_action('wpforge_before_header'); ?>

<header id="masthead" class="site-header" role="banner">
    <?php do_action('wpforge_header'); ?>

    <div class="site-header-inner container">
        <div class="site-branding">
            <?php
            if (function_exists('wpforge_site_logo')) {
                wpforge_site_logo();
            }

            if (get_theme_mod('wpforge_show_site_title', true)) :
                if (is_front_page() && is_home()) :
                    ?>
                    <h1 class="site-title"><a href="<?php echo esc_url(home_url('/')); ?>" rel="home"><?php bloginfo('name'); ?></a></h1>
                <?php else : ?>
                    <p class="site-title"><a href="<?php echo esc_url(home_url('/')); ?>" rel="home"><?php bloginfo('name'); ?></a></p>
                <?php
                endif;
            endif;

            if (get_theme_mod('wpforge_show_site_description', true)) :
                $description = get_bloginfo('description', 'display');
                if ($description || is_customize_preview()) :
                    ?>
                    <p class="site-description"><?php echo $description; ?></p>
                <?php
                endif;
            endif;
            ?>
        </div>

        <nav id="site-navigation" class="main-navigation" role="navigation" aria-label="<?php esc_attr_e('Primary Menu', 'wpforge-theme'); ?>">
            <button class="menu-toggle" aria-controls="primary-menu" aria-expanded="false">
                <span class="screen-reader-text"><?php esc_html_e('Primary Menu', 'wpforge-theme'); ?></span>
                <span class="menu-icon"></span>
            </button>

            <?php
            if (function_exists('wpforge_primary_navigation')) {
                wpforge_primary_navigation();
            } else {
                wp_nav_menu(array(
                    'theme_location' => 'primary',
                    'menu_id'        => 'primary-menu',
                    'container'      => false,
                    'fallback_cb'    => 'wpforge_nav_fallback',
                ));
            }
            ?>
        </nav>
    </div>
</header>

<?php do_action('wpforge_after_header'); ?>

<div id="page" class="site-content">
    <div class="container">
        <?php
        if (function_exists('wpforge_breadcrumb')) {
            wpforge_breadcrumb();
        }
        ?>
