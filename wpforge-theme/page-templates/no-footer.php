<?php
/**
 * Template Name: No Footer
 * Template Post Type: post, page
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

get_header();
?>

<div id="primary" class="content-area">
    <main id="main" class="site-main" role="main">

        <?php
        while (have_posts()) :
            the_post();
            ?>

            <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                <?php
                if (get_theme_mod('wpforge_page_show_title', true)) :
                    ?>
                    <header class="entry-header">
                        <?php the_title('<h1 class="entry-title">', '</h1>'); ?>
                    </header>
                    <?php
                endif;

                if (has_post_thumbnail()) :
                    ?>
                    <div class="post-thumbnail page-thumbnail">
                        <?php the_post_thumbnail('large', array('loading' => 'eager')); ?>
                    </div>
                    <?php
                endif;
                ?>

                <div class="entry-content">
                    <?php
                    the_content();

                    wp_link_pages(array(
                        'before' => '<div class="page-links">' . esc_html__('Pages:', 'wpforge-theme'),
                        'after'  => '</div>',
                    ));
                    ?>
                </div>
            </article>

            <?php
            if (comments_open() || get_comments_number()) :
                comments_template();
            endif;

        endwhile;
        ?>

    </main>
</div>

<?php get_sidebar(); ?>

<?php wp_footer(); ?>

</body>
</html>
