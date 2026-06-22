<?php
/**
 * Template Name: Canvas (Blank)
 * Template Post Type: post, page
 *
 * A completely blank template for page builders.
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

<body <?php body_class('canvas-template'); ?>>
<?php wp_body_open(); ?>

<div id="primary" class="content-area canvas">
    <main id="main" class="site-main" role="main">

        <?php
        while (have_posts()) :
            the_post();
            the_content();
        endwhile;
        ?>

    </main>
</div>

<?php wp_footer(); ?>

</body>
</html>
