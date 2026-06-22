<?php
/**
 * The template for displaying archive pages
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

get_header();
?>

<div id="primary" class="content-area">
    <main id="main" class="site-main" role="main">

        <?php
        do_action('wpforge_before_content');

        if (have_posts()) :
            ?>
            <header class="page-header">
                <?php
                the_archive_title('<h1 class="page-title">', '</h1>');
                the_archive_description('<div class="archive-description">', '</div>');
                ?>
            </header>

            <div class="posts-grid">
                <?php
                while (have_posts()) :
                    the_post();

                    do_action('wpforge_before_post');
                    ?>

                    <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                        <?php
                        if (get_theme_mod('wpforge_show_featured_image', true) && has_post_thumbnail()) :
                            ?>
                            <div class="post-thumbnail">
                                <a href="<?php the_permalink(); ?>" aria-hidden="true" tabindex="-1">
                                    <?php the_post_thumbnail('medium', array('loading' => 'lazy')); ?>
                                </a>
                            </div>
                            <?php
                        endif;
                        ?>

                        <header class="entry-header">
                            <?php
                            if (get_theme_mod('wpforge_show_category', true)) {
                                echo '<div class="entry-categories">' . get_the_category_list(', ') . '</div>';
                            }

                            the_title('<h2 class="entry-title"><a href="' . esc_url(get_permalink()) . '" rel="bookmark">', '</a></h2>');
                            ?>

                            <div class="entry-meta">
                                <?php
                                if (get_theme_mod('wpforge_show_date', true)) {
                                    echo '<span class="posted-on">' . get_the_date() . '</span>';
                                }

                                if (get_theme_mod('wpforge_show_author', true)) {
                                    echo '<span class="byline"> ' . esc_html__('by', 'wpforge-theme') . ' ' . get_the_author() . '</span>';
                                }
                                ?>
                            </div>
                        </header>

                        <div class="entry-summary">
                            <?php
                            $excerpt_length = get_theme_mod('wpforge_excerpt_length', 40);
                            echo wp_trim_words(get_the_excerpt(), $excerpt_length);
                            ?>
                        </div>

                        <footer class="entry-footer">
                            <?php
                            $read_more_text = get_theme_mod('wpforge_read_more_text', __('Read More', 'wpforge-theme'));
                            echo '<a href="' . esc_url(get_permalink()) . '" class="read-more">' . esc_html($read_more_text) . '</a>';
                            ?>
                        </footer>
                    </article>

                    <?php
                    do_action('wpforge_after_post');

                endwhile;
                ?>
            </div>

            <?php
            if (function_exists('wpforge_pagination')) {
                wpforge_pagination();
            } else {
                the_posts_navigation();
            }

        else :

            if (function_exists('wpforge_no_posts_content')) {
                wpforge_no_posts_content();
            } else {
                ?>
                <section class="no-results not-found">
                    <header class="page-header">
                        <h1 class="page-title"><?php esc_html_e('Nothing Found', 'wpforge-theme'); ?></h1>
                    </header>
                    <div class="page-content">
                        <p><?php esc_html_e('It seems we can&rsquo;t find what you&rsquo;re looking for. Perhaps searching can help.', 'wpforge-theme'); ?></p>
                        <?php get_search_form(); ?>
                    </div>
                </section>
                <?php
            }

        endif;

        do_action('wpforge_after_content');
        ?>

    </main>
</div>

<?php
get_sidebar();
get_footer();
