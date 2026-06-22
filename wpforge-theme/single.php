<?php
/**
 * The template for displaying all single posts
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

        while (have_posts()) :
            the_post();

            do_action('wpforge_before_post');
            ?>

            <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                <?php
                if (get_theme_mod('wpforge_single_show_featured_image', true) && has_post_thumbnail()) :
                    ?>
                    <div class="post-thumbnail single-thumbnail">
                        <?php the_post_thumbnail('large', array('loading' => 'eager')); ?>
                    </div>
                    <?php
                endif;
                ?>

                <header class="entry-header">
                    <?php
                    if (get_theme_mod('wpforge_single_show_category', true)) {
                        echo '<div class="entry-categories">' . get_the_category_list(', ') . '</div>';
                    }

                    the_title('<h1 class="entry-title">', '</h1>');
                    ?>

                    <div class="entry-meta">
                        <?php
                        if (get_theme_mod('wpforge_single_show_date', true)) {
                            echo '<span class="posted-on">' . get_the_date() . '</span>';
                        }

                        if (get_theme_mod('wpforge_single_show_author', true)) {
                            echo '<span class="byline"> ' . esc_html__('by', 'wpforge-theme') . ' ' . get_the_author() . '</span>';
                        }

                        if (get_theme_mod('wpforge_single_show_comments', true) && !post_password_required() && (comments_open() || get_comments_number())) {
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

                <div class="entry-content">
                    <?php
                    the_content();

                    wp_link_pages(array(
                        'before' => '<div class="page-links">' . esc_html__('Pages:', 'wpforge-theme'),
                        'after'  => '</div>',
                    ));
                    ?>
                </div>

                <footer class="entry-footer">
                    <?php
                    if (get_theme_mod('wpforge_single_show_tags', true)) {
                        $tags_list = get_the_tag_list('', ', ');
                        if ($tags_list) {
                            echo '<div class="entry-tags">' . esc_html__('Tags:', 'wpforge-theme') . ' ' . $tags_list . '</div>';
                        }
                    }
                    ?>
                </footer>
            </article>

            <?php
            do_action('wpforge_after_post');

            // Author box.
            if (get_theme_mod('wpforge_single_show_author_box', true)) :
                ?>
                <div class="author-box">
                    <div class="author-avatar">
                        <?php echo get_avatar(get_the_author_meta('ID'), 80); ?>
                    </div>
                    <div class="author-info">
                        <h3 class="author-name"><?php echo esc_html(get_the_author()); ?></h3>
                        <p class="author-bio"><?php echo esc_html(get_the_author_meta('description')); ?></p>
                    </div>
                </div>
                <?php
            endif;

            // Related posts.
            if (get_theme_mod('wpforge_single_show_related', true)) :
                if (function_exists('wpforge_related_posts')) {
                    wpforge_related_posts();
                }
            endif;

            // Previous/next post navigation.
            if (get_theme_mod('wpforge_single_show_nav', true)) :
                the_post_navigation(array(
                    'prev_text' => '<span class="nav-subtitle">' . esc_html__('Previous', 'wpforge-theme') . '</span> <span class="nav-title">%title</span>',
                    'next_text' => '<span class="nav-subtitle">' . esc_html__('Next', 'wpforge-theme') . '</span> <span class="nav-title">%title</span>',
                ));
            endif;

            // Comments.
            if (comments_open() || get_comments_number()) :
                comments_template();
            endif;

        endwhile;

        do_action('wpforge_after_content');
        ?>

    </main>
</div>

<?php
get_sidebar();
get_footer();
