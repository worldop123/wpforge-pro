<?php
/**
 * Template Name: Landing Page
 * Template Post Type: page
 *
 * A clean landing page template with no sidebar and minimal distractions.
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

get_header();
?>

<div id="primary" class="content-area landing-page">
    <main id="main" class="site-main" role="main">

        <?php
        while (have_posts()) :
            the_post();
            ?>

            <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
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

<?php get_footer(); ?>
