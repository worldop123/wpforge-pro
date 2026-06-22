<?php
/**
 * 产品卡片模板
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

global $product;

// Ensure visibility
if (empty($product) || !$product->is_visible()) {
    return;
}
?>

<li <?php wc_product_class('', $product); ?>>
    <div class="product-card">
        <?php
        /**
         * woocommerce_before_shop_loop_item hook.
         *
         * @hooked woocommerce_template_loop_product_link_open - 10
         */
        do_action('woocommerce_before_shop_loop_item');
        ?>

        <div class="product-image">
            <?php
            /**
             * woocommerce_before_shop_loop_item_title hook.
             *
             * @hooked woocommerce_show_product_loop_sale_flash - 10
             * @hooked woocommerce_template_loop_product_thumbnail - 10
             */
            do_action('woocommerce_before_shop_loop_item_title');
            ?>

            <div class="product-actions">
                <?php if ($product->is_in_stock()) : ?>
                    <a href="<?php echo esc_url($product->add_to_cart_url()); ?>"
                       class="button add_to_cart_button ajax_add_to_cart"
                       data-product_id="<?php echo esc_attr($product->get_id()); ?>"
                       data-product_sku="<?php echo esc_attr($product->get_sku()); ?>"
                       aria-label="<?php echo esc_attr(sprintf(__('Add %s to cart', 'wpforge-theme'), $product->get_name())); ?>"
                       rel="nofollow">
                        <?php echo esc_html($product->add_to_cart_text()); ?>
                    </a>
                <?php endif; ?>
            </div>
        </div>

        <div class="product-info">
            <?php
            /**
             * woocommerce_shop_loop_item_title hook.
             *
             * @hooked woocommerce_template_loop_product_title - 10
             */
            do_action('woocommerce_shop_loop_item_title');
            ?>

            <?php
            /**
             * woocommerce_after_shop_loop_item_title hook.
             *
             * @hooked woocommerce_template_loop_rating - 5
             * @hooked woocommerce_template_loop_price - 10
             */
            do_action('woocommerce_after_shop_loop_item_title');
            ?>

            <?php
            /**
             * woocommerce_after_shop_loop_item hook.
             *
             * @hooked woocommerce_template_loop_product_link_close - 5
             * @hooked woocommerce_template_loop_add_to_cart - 10
             */
            do_action('woocommerce_after_shop_loop_item');
            ?>
        </div>
    </div>
</li>
