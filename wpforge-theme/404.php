<?php
/**
 * The template for displaying 404 pages (not found)
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

        if (function_exists('wpforge_404_content')) {
            wpforge_404_content();
        } else {
            ?>
            <section class="error-404 not-found">
                <header class="page-header">
                    <h1 class="page-title"><?php esc_html_e('Oops! That page can&rsquo;t be found.', 'wpforge-theme'); ?></h1>
                </header>

                <div class="page-content">
                    <p><?php esc_html_e('It looks like nothing was found at this location. Maybe try one of the links below or a search?', 'wpforge-theme'); ?></p>

                    <?php get_search_form(); ?>

                    <div class="widget widget_categories">
                        <h2 class="widget-title"><?php esc_html_e('Most Used Categories', 'wpforge-theme'); ?></h2>
                        <ul>
                            <?php
                            wp_list_categories(array(
                                'orderby'    => 'count',
                                'order'      => 'DESC',
                                'show_count' => 1,
                                'title_li'   => '',
                                'number'     => 10,
                            ));
                            ?>
                        </ul>
                    </div>

                    <?php
                    the_widget('WP_Widget_Recent_Posts');
                    ?>
                </div>
            </section>
            <?php
        }

        do_action('wpforge_after_content');
        ?>

    </main>
</div>

<?php
get_sidebar();
get_footer();
