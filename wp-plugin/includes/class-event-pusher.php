<?php
/**
 * 事件推送引擎
 * 
 * 监听WordPress和WooCommerce事件，自动推送到中转服务器
 */

// 防止直接访问
if (!defined('ABSPATH')) {
    exit;
}

class WPForge_Relay_Event_Pusher {

    /**
     * WebSocket客户端实例
     */
    private $websocket_client = null;

    /**
     * 启用的事件列表
     */
    private $enabled_events = array();

    /**
     * 构造函数
     */
    public function __construct($websocket_client) {
        $this->websocket_client = $websocket_client;
        $this->enabled_events = get_option('wpforge_relay_enabled_events', array());

        $this->register_hooks();
    }

    /**
     * 注册事件钩子
     */
    private function register_hooks() {
        // WooCommerce事件
        if (in_array('woocommerce_new_order', $this->enabled_events)) {
            add_action('woocommerce_new_order', array($this, 'on_new_order'), 10, 1);
        }

        if (in_array('woocommerce_order_status_changed', $this->enabled_events)) {
            add_action('woocommerce_order_status_changed', array($this, 'on_order_status_changed'), 10, 4);
        }

        if (in_array('woocommerce_low_stock', $this->enabled_events)) {
            add_action('woocommerce_low_stock', array($this, 'on_low_stock'), 10, 1);
        }

        if (in_array('woocommerce_no_stock', $this->enabled_events)) {
            add_action('woocommerce_no_stock', array($this, 'on_no_stock'), 10, 1);
        }

        if (in_array('woocommerce_product_updated', $this->enabled_events)) {
            add_action('woocommerce_update_product', array($this, 'on_product_updated'), 10, 2);
        }

        // WordPress核心事件
        if (in_array('post_published', $this->enabled_events)) {
            add_action('publish_post', array($this, 'on_post_published'), 10, 2);
            add_action('publish_page', array($this, 'on_post_published'), 10, 2);
        }

        if (in_array('post_updated', $this->enabled_events)) {
            add_action('post_updated', array($this, 'on_post_updated'), 10, 3);
        }

        if (in_array('comment_posted', $this->enabled_events)) {
            add_action('comment_post', array($this, 'on_comment_posted'), 10, 3);
        }

        if (in_array('user_registered', $this->enabled_events)) {
            add_action('user_register', array($this, 'on_user_registered'), 10, 1);
        }

        if (in_array('plugin_activated', $this->enabled_events)) {
            add_action('activated_plugin', array($this, 'on_plugin_activated'), 10, 2);
        }

        if (in_array('theme_switched', $this->enabled_events)) {
            add_action('switch_theme', array($this, 'on_theme_switched'), 10, 2);
        }

        // 系统事件
        add_action('wp_error', array($this, 'on_wp_error'), 10, 1);
    }

    // ===== WooCommerce事件 =====

    /**
     * 新订单事件
     */
    public function on_new_order($order_id) {
        $order = wc_get_order($order_id);
        if (!$order) {
            return;
        }

        $data = array(
            'order_id' => $order_id,
            'order_number' => $order->get_order_number(),
            'total' => $order->get_total(),
            'status' => $order->get_status(),
            'customer_id' => $order->get_customer_id(),
            'billing_email' => $order->get_billing_email(),
            'item_count' => count($order->get_items()),
            'date_created' => $order->get_date_created() ? $order->get_date_created()->date('Y-m-d H:i:s') : null,
        );

        $this->push_event('woocommerce_new_order', $data);
    }

    /**
     * 订单状态变更事件
     */
    public function on_order_status_changed($order_id, $old_status, $new_status, $order) {
        $data = array(
            'order_id' => $order_id,
            'order_number' => $order->get_order_number(),
            'old_status' => $old_status,
            'new_status' => $new_status,
            'total' => $order->get_total(),
            'customer_id' => $order->get_customer_id(),
        );

        $this->push_event('woocommerce_order_status_changed', $data);
    }

    /**
     * 低库存事件
     */
    public function on_low_stock($product) {
        if (is_numeric($product)) {
            $product = wc_get_product($product);
        }

        if (!$product) {
            return;
        }

        $data = array(
            'product_id' => $product->get_id(),
            'product_name' => $product->get_name(),
            'sku' => $product->get_sku(),
            'stock_quantity' => $product->get_stock_quantity(),
            'low_stock_amount' => get_option('woocommerce_notify_low_stock_amount'),
        );

        $this->push_event('woocommerce_low_stock', $data);
    }

    /**
     * 无库存事件
     */
    public function on_no_stock($product) {
        if (is_numeric($product)) {
            $product = wc_get_product($product);
        }

        if (!$product) {
            return;
        }

        $data = array(
            'product_id' => $product->get_id(),
            'product_name' => $product->get_name(),
            'sku' => $product->get_sku(),
            'stock_quantity' => $product->get_stock_quantity(),
        );

        $this->push_event('woocommerce_no_stock', $data);
    }

    /**
     * 产品更新事件
     */
    public function on_product_updated($product_id, $product) {
        $data = array(
            'product_id' => $product_id,
            'product_name' => $product->get_name(),
            'sku' => $product->get_sku(),
            'price' => $product->get_price(),
            'regular_price' => $product->get_regular_price(),
            'sale_price' => $product->get_sale_price(),
            'stock_quantity' => $product->get_stock_quantity(),
            'status' => $product->get_status(),
        );

        $this->push_event('woocommerce_product_updated', $data);
    }

    // ===== WordPress核心事件 =====

    /**
     * 文章发布事件
     */
    public function on_post_published($post_id, $post) {
        // 避免自动保存和修订
        if (wp_is_post_autosave($post_id) || wp_is_post_revision($post_id)) {
            return;
        }

        $data = array(
            'post_id' => $post_id,
            'post_title' => $post->post_title,
            'post_type' => $post->post_type,
            'post_status' => $post->post_status,
            'post_author' => $post->post_author,
            'post_date' => $post->post_date,
            'permalink' => get_permalink($post_id),
        );

        $this->push_event('post_published', $data);
    }

    /**
     * 文章更新事件
     */
    public function on_post_updated($post_id, $post_after, $post_before) {
        if (wp_is_post_autosave($post_id) || wp_is_post_revision($post_id)) {
            return;
        }

        $data = array(
            'post_id' => $post_id,
            'post_title' => $post_after->post_title,
            'post_type' => $post_after->post_type,
            'post_status' => $post_after->post_status,
            'post_modified' => $post_after->post_modified,
        );

        $this->push_event('post_updated', $data);
    }

    /**
     * 评论发布事件
     */
    public function on_comment_posted($comment_id, $comment_approved, $commentdata) {
        $comment = get_comment($comment_id);
        if (!$comment) {
            return;
        }

        $data = array(
            'comment_id' => $comment_id,
            'comment_author' => $comment->comment_author,
            'comment_author_email' => $comment->comment_author_email,
            'comment_content' => $comment->comment_content,
            'comment_approved' => $comment_approved,
            'post_id' => $comment->comment_post_ID,
            'post_title' => get_the_title($comment->comment_post_ID),
        );

        $this->push_event('comment_posted', $data);
    }

    /**
     * 用户注册事件
     */
    public function on_user_registered($user_id) {
        $user = get_user_by('id', $user_id);
        if (!$user) {
            return;
        }

        $data = array(
            'user_id' => $user_id,
            'user_login' => $user->user_login,
            'user_email' => $user->user_email,
            'user_nicename' => $user->user_nicename,
            'display_name' => $user->display_name,
            'roles' => $user->roles,
            'user_registered' => $user->user_registered,
        );

        $this->push_event('user_registered', $data);
    }

    /**
     * 插件激活事件
     */
    public function on_plugin_activated($plugin, $network_wide) {
        $data = array(
            'plugin' => $plugin,
            'network_wide' => $network_wide,
        );

        $this->push_event('plugin_activated', $data);
    }

    /**
     * 主题切换事件
     */
    public function on_theme_switched($new_name, $new_theme) {
        $data = array(
            'new_theme' => $new_name,
            'old_theme' => get_option('theme_switched'),
        );

        $this->push_event('theme_switched', $data);
    }

    // ===== 系统事件 =====

    /**
     * WordPress错误事件
     */
    public function on_wp_error($error) {
        if (is_wp_error($error)) {
            $data = array(
                'error_code' => $error->get_error_code(),
                'error_message' => $error->get_error_message(),
                'error_data' => $error->get_error_data(),
            );

            $this->push_event('wp_error', $data);
        }
    }

    // ===== 核心方法 =====

    /**
     * 推送事件
     */
    private function push_event($event_type, $event_data) {
        // 检查是否启用了该事件
        if (!in_array($event_type, $this->enabled_events) && !in_array('wp_error', $this->enabled_events)) {
            // 错误事件总是推送
            if ($event_type !== 'wp_error') {
                return;
            }
        }

        // 添加站点信息
        $event_data['site_url'] = site_url();
        $event_data['site_name'] = get_bloginfo('name');

        // 发送事件
        $this->websocket_client->send_event($event_type, $event_data);
    }

    /**
     * 手动触发事件
     */
    public function trigger_event($event_type, $event_data = array()) {
        $this->push_event($event_type, $event_data);
    }

    /**
     * 获取所有可用事件
     */
    public function get_available_events() {
        return array(
            'woocommerce' => array(
                'woocommerce_new_order' => __('新订单', 'wpforge-relay'),
                'woocommerce_order_status_changed' => __('订单状态变更', 'wpforge-relay'),
                'woocommerce_low_stock' => __('低库存预警', 'wpforge-relay'),
                'woocommerce_no_stock' => __('缺货预警', 'wpforge-relay'),
                'woocommerce_product_updated' => __('产品更新', 'wpforge-relay'),
            ),
            'wordpress' => array(
                'post_published' => __('文章发布', 'wpforge-relay'),
                'post_updated' => __('文章更新', 'wpforge-relay'),
                'comment_posted' => __('新评论', 'wpforge-relay'),
                'user_registered' => __('用户注册', 'wpforge-relay'),
                'plugin_activated' => __('插件激活', 'wpforge-relay'),
                'theme_switched' => __('主题切换', 'wpforge-relay'),
            ),
            'system' => array(
                'wp_error' => __('系统错误', 'wpforge-relay'),
            ),
        );
    }
}
