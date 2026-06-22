<?php
/**
 * The template for displaying the blog page
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

            if (is_home() && !is_front_page()) :
                ?>
                <header class="page-header">
                    <h1 class="page-title"><?php single_post_title(); ?></h1>
                </header>
                <?php
            endif;

            echo '<div class="posts-grid">';

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

                            if (get_theme_mod('wpforge_show_comments', true) && !post_password_required() && (comments_open() || get_comments_number())) {
                                echo '<span class="comments-link">';
                                comments_popup_link(
                                    esc_html__('Leave a comment', 'wpforge-theme'),
                                    esc_html__('1 Comment', 'wpforge-theme'),
                                    esc_html__('% Comments', 'wpforge-theme')
                                );
                                echo '</span>';
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

            echo '</div>';

            if (function_exists('wpforge_pagination')) {
                wpforge_pagination();
            } else {
                the_posts_navigation();
            }

        else :

            get_template_part('template-parts/content', 'none');

        endif;

        do_action('wpforge_after_content');
        ?>

    </main>
</div>

<?php
get_sidebar();
get_footer();
