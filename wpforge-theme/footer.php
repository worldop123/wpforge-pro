<?php
/**
 * The footer for our theme
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */
?>
    </div>
</div>

<?php do_action('wpforge_before_footer'); ?>

<footer id="colophon" class="site-footer" role="contentinfo">
    <?php do_action('wpforge_footer'); ?>

    <?php if (is_active_sidebar('footer-1') || is_active_sidebar('footer-2') || is_active_sidebar('footer-3') || is_active_sidebar('footer-4')) : ?>
        <div class="footer-widgets">
            <div class="container">
                <div class="footer-widgets-grid">
                    <?php
                    $columns = get_theme_mod('wpforge_footer_widget_columns', 4);
                    for ($i = 1; $i <= $columns; $i++) :
                        if (is_active_sidebar('footer-' . $i)) :
                            ?>
                            <div class="footer-widget-column">
                                <?php dynamic_sidebar('footer-' . $i); ?>
                            </div>
                            <?php
                        endif;
                    endfor;
                    ?>
                </div>
            </div>
        </div>
    <?php endif; ?>

    <?php if (get_theme_mod('wpforge_footer_bottom_bar', true)) : ?>
        <div class="footer-bottom-bar">
            <div class="container">
                <div class="footer-bottom-bar-inner">
                    <div class="footer-copyright">
                        <?php
                        $copyright = get_theme_mod('wpforge_copyright_text', '');
                        if ($copyright) {
                            echo wp_kses_post($copyright);
                        } else {
                            echo sprintf(
                                esc_html__('© %1$s %2$s. All rights reserved.', 'wpforge-theme'),
                                date('Y'),
                                get_bloginfo('name')
                            );
                        }
                        ?>
                    </div>

                    <?php if (has_nav_menu('footer')) : ?>
                        <nav class="footer-navigation" role="navigation" aria-label="<?php esc_attr_e('Footer Menu', 'wpforge-theme'); ?>">
                            <?php
                            wp_nav_menu(array(
                                'theme_location' => 'footer',
                                'menu_id'        => 'footer-menu',
                                'container'      => false,
                                'depth'          => 1,
                            ));
                            ?>
                        </nav>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    <?php endif; ?>
</footer>

<?php if (get_theme_mod('wpforge_back_to_top', true)) : ?>
    <button class="back-to-top" aria-label="<?php esc_attr_e('Back to top', 'wpforge-theme'); ?>">
        <span class="screen-reader-text"><?php esc_html_e('Back to top', 'wpforge-theme'); ?></span>
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="18 15 12 9 6 15"></polyline>
        </svg>
    </button>
<?php endif; ?>

<?php do_action('wpforge_after_footer'); ?>

<?php wp_footer(); ?>

</body>
</html>
