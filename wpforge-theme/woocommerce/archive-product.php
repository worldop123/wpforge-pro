<?php
/**
 * 产品列表页模板
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

get_header('shop');
?>

<?php
/**
 * woocommerce_before_main_content hook.
 *
 * @hooked woocommerce_output_content_wrapper - 10 (outputs opening divs for the content)
 * @hooked woocommerce_breadcrumb - 20
 */
do_action('woocommerce_before_main_content');
?>

<?php if (apply_filters('woocommerce_show_page_title', true)) : ?>
    <header class="woocommerce-products-header page-header">
        <h1 class="woocommerce-products-header__title page-title"><?php woocommerce_page_title(); ?></h1>
        <?php
        /**
         * woocommerce_archive_description hook.
         *
         * @hooked woocommerce_taxonomy_archive_description - 10
         * @hooked woocommerce_product_archive_description - 10
         */
        do_action('woocommerce_archive_description');
        ?>
    </header>
<?php endif; ?>

<?php
/**
 * woocommerce_before_shop_loop hook.
 *
 * @hooked woocommerce_result_count - 20
 * @hooked woocommerce_catalog_ordering - 30
 */
do_action('woocommerce_before_shop_loop');
?>

<?php if (woocommerce_product_loop()) : ?>

    <?php woocommerce_product_loop_start(); ?>

    <?php if (wc_get_loop_prop('total')) : ?>
        <?php while (have_posts()) : ?>
            <?php the_post(); ?>

            <?php
            /**
             * woocommerce_shop_loop hook.
             *
             * @hooked WC_Structured_Data::generate_product_data() - 10
             */
            do_action('woocommerce_shop_loop');
            ?>

            <?php wc_get_template_part('content', 'product'); ?>

        <?php endwhile; // end of the loop. ?>
    <?php endif; ?>

    <?php woocommerce_product_loop_end(); ?>

    <?php
    /**
     * woocommerce_after_shop_loop hook.
     *
     * @hooked woocommerce_pagination - 10
     */
    do_action('woocommerce_after_shop_loop');
    ?>

<?php else : ?>

    <?php
    /**
     * woocommerce_no_products_found hook.
     *
     * @hooked wc_no_products_found - 10
     */
    do_action('woocommerce_no_products_found');
    ?>

<?php endif; ?>

<?php
/**
 * woocommerce_after_main_content hook.
 *
 * @hooked woocommerce_output_content_wrapper_end - 10 (outputs closing divs for the content)
 */
do_action('woocommerce_after_main_content');
?>

<?php
/**
 * woocommerce_sidebar hook.
 *
 * @hooked woocommerce_get_sidebar - 10
 */
do_action('woocommerce_sidebar');
?>

<?php get_footer('shop'); ?>
