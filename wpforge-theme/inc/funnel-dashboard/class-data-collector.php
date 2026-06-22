<?php
/**
 * WPForge Theme - Funnel Data Collector
 *
 * 电商漏斗数据采集器
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

// Exit if accessed directly.
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Funnel_Data_Collector 类
 *
 * 负责采集电商漏斗的各项数据
 *
 * @since 1.0.0
 */
class Funnel_Data_Collector {

    /**
     * 单例实例
     *
     * @since 1.0.0
     * @var Funnel_Data_Collector|null
     */
    private static $instance = null;

    /**
     * 获取单例实例
     *
     * @since 1.0.0
     * @return Funnel_Data_Collector
     */
    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    /**
     * 构造函数
     *
     * @since 1.0.0
     */
    private function __construct() {
        // 构造函数留空，初始化通过钩子完成
    }

    /**
     * 获取访客ID（基于Cookie）
     *
     * @since 1.0.0
     * @return string
     */
    public function get_visitor_id() {
        if (isset($_COOKIE['wpforge_funnel_visitor'])) {
            return sanitize_text_field($_COOKIE['wpforge_funnel_visitor']);
        }

        // 生成新的访客ID
        $visitor_id = md5(uniqid('wpforge_', true) . $_SERVER['REMOTE_ADDR'] . $_SERVER['HTTP_USER_AGENT']);

        // 设置Cookie，有效期2年
        setcookie(
            'wpforge_funnel_visitor',
            $visitor_id,
            time() + 2 * YEAR_IN_SECONDS,
            COOKIEPATH,
            COOKIE_DOMAIN,
            is_ssl()
        );

        return $visitor_id;
    }

    /**
     * 获取会话ID
     *
     * @since 1.0.0
     * @return string
     */
    public function get_session_id() {
        if (isset($_COOKIE['wpforge_funnel_session'])) {
            return sanitize_text_field($_COOKIE['wpforge_funnel_session']);
        }

        // 生成新的会话ID
        $session_id = md5(uniqid('session_', true) . microtime(true));

        // 设置Cookie，有效期30分钟
        setcookie(
            'wpforge_funnel_session',
            $session_id,
            time() + 30 * MINUTE_IN_SECONDS,
            COOKIEPATH,
            COOKIE_DOMAIN,
            is_ssl()
        );

        return $session_id;
    }

    /**
     * 可能追踪访问
     *
     * @since 1.0.0
     */
    public function maybe_track_visit() {
        // 不追踪管理员
        if (current_user_can('manage_options')) {
            return;
        }

        // 检查是否启用数据采集
        $enabled = wpforge_funnel_dashboard()->get_option('enable_tracking', true);
        if (!$enabled) {
            return;
        }

        $this->track_visit();
    }

    /**
     * 追踪访问
     *
     * @since 1.0.0
     */
    private function track_visit() {
        global $wpdb;

        $visitor_id = $this->get_visitor_id();
        $session_id = $this->get_session_id();
        $current_date = current_time('Y-m-d');
        $current_hour = (int) current_time('H');

        // 判断页面类型
        $page_type = 'other';
        $product_id = null;

        if (is_product()) {
            $page_type = 'product';
            $product_id = get_the_ID();
        } elseif (is_shop()) {
            $page_type = 'shop';
        } elseif (is_product_category()) {
            $page_type = 'category';
        } elseif (is_cart()) {
            $page_type = 'cart';
        } elseif (is_checkout()) {
            $page_type = 'checkout';
        } elseif (is_front_page()) {
            $page_type = 'home';
        }

        // 获取来源
        $source = $this->detect_source();
        $referrer = isset($_SERVER['HTTP_REFERER']) ? esc_url_raw($_SERVER['HTTP_REFERER']) : null;

        // 获取设备类型
        $device_type = $this->detect_device_type();

        // 插入访问记录
        $table_name = $wpdb->prefix . 'wpforge_funnel_visits';

        $wpdb->insert(
            $table_name,
            array(
                'visit_date'   => $current_date,
                'visit_hour'   => $current_hour,
                'visitor_id'   => $visitor_id,
                'session_id'   => $session_id,
                'page_type'    => $page_type,
                'product_id'   => $product_id,
                'referrer'     => $referrer,
                'source'       => $source,
                'device_type'  => $device_type,
            ),
            array(
                '%s',
                '%d',
                '%s',
                '%s',
                '%s',
                '%d',
                '%s',
                '%s',
                '%s',
            )
        );
    }

    /**
     * 检测流量来源
     *
     * @since 1.0.0
     * @return string
     */
    private function detect_source() {
        $source = 'direct';

        if (!isset($_SERVER['HTTP_REFERER'])) {
            return $source;
        }

        $referrer = $_SERVER['HTTP_REFERER'];
        $site_url = site_url();

        // 检查是否是站内跳转
        if (strpos($referrer, $site_url) !== false) {
            return $source;
        }

        // 检查搜索引擎
        $search_engines = array(
            'google'    => 'google.',
            'bing'      => 'bing.',
            'yahoo'     => 'yahoo.',
            'baidu'     => 'baidu.',
            'duckduckgo' => 'duckduckgo.',
        );

        foreach ($search_engines as $name => $domain) {
            if (strpos($referrer, $domain) !== false) {
                return 'search';
            }
        }

        // 检查社交媒体
        $social_media = array(
            'facebook', 'twitter', 'instagram', 'linkedin',
            'youtube', 'tiktok', 'pinterest', 'reddit',
        );

        foreach ($social_media as $social) {
            if (strpos($referrer, $social) !== false) {
                return 'social';
            }
        }

        // 检查是否是邮件
        if (strpos($referrer, 'mail.') !== false || strpos($referrer, 'gmail') !== false) {
            return 'email';
        }

        // 其他推荐来源
        return 'referral';
    }

    /**
     * 检测设备类型
     *
     * @since 1.0.0
     * @return string
     */
    private function detect_device_type() {
        $user_agent = isset($_SERVER['HTTP_USER_AGENT']) ? $_SERVER['HTTP_USER_AGENT'] : '';

        // 检测移动设备
        $mobile_keywords = array(
            'android', 'iphone', 'ipad', 'ipod',
            'blackberry', 'windows phone', 'opera mini',
            'mobile', 'webos', 'symbian',
        );

        $is_mobile = false;
        foreach ($mobile_keywords as $keyword) {
            if (stripos($user_agent, $keyword) !== false) {
                $is_mobile = true;
                break;
            }
        }

        if (!$is_mobile) {
            return 'desktop';
        }

        // 检测平板
        $tablet_keywords = array('ipad', 'tablet', 'kindle', 'playbook');
        foreach ($tablet_keywords as $keyword) {
            if (stripos($user_agent, $keyword) !== false) {
                return 'tablet';
            }
        }

        return 'mobile';
    }

    /**
     * 追踪加入购物车
     *
     * @since 1.0.0
     * @param string $cart_item_key 购物车项目键
     * @param int $product_id 产品ID
     * @param int $quantity 数量
     * @param int $variation_id 变体ID
     * @param array $variation 变体数据
     * @param array $cart_item_data 购物车项目数据
     */
    public function track_add_to_cart($cart_item_key, $product_id, $quantity, $variation_id, $variation, $cart_item_data) {
        global $wpdb;

        $visitor_id = $this->get_visitor_id();
        $session_id = $this->get_session_id();
        $current_date = current_time('Y-m-d');

        $table_name = $wpdb->prefix . 'wpforge_funnel_cart_events';

        $wpdb->insert(
            $table_name,
            array(
                'event_date'     => $current_date,
                'visitor_id'     => $visitor_id,
                'session_id'     => $session_id,
                'product_id'     => $product_id,
                'quantity'       => $quantity,
                'cart_item_key'  => $cart_item_key,
            ),
            array(
                '%s',
                '%s',
                '%s',
                '%d',
                '%d',
                '%s',
            )
        );
    }

    /**
     * 追踪开始结账
     *
     * @since 1.0.0
     */
    public function track_checkout_start() {
        global $wpdb;

        // 避免重复记录
        if (did_action('wpforge_funnel_checkout_tracked')) {
            return;
        }
        do_action('wpforge_funnel_checkout_tracked');

        $visitor_id = $this->get_visitor_id();
        $session_id = $this->get_session_id();
        $current_date = current_time('Y-m-d');

        $cart_hash = WC()->cart ? WC()->cart->get_cart_hash() : '';

        $table_name = $wpdb->prefix . 'wpforge_funnel_checkout_events';

        $wpdb->insert(
            $table_name,
            array(
                'event_date'  => $current_date,
                'visitor_id'  => $visitor_id,
                'session_id'  => $session_id,
                'cart_hash'   => $cart_hash,
            ),
            array(
                '%s',
                '%s',
                '%s',
                '%s',
            )
        );
    }

    /**
     * 追踪购买完成
     *
     * @since 1.0.0
     * @param int $order_id 订单ID
     */
    public function track_purchase_complete($order_id) {
        global $wpdb;

        // 避免重复记录
        if (get_post_meta($order_id, '_wpforge_funnel_tracked', true)) {
            return;
        }
        update_post_meta($order_id, '_wpforge_funnel_tracked', '1');

        $order = wc_get_order($order_id);
        if (!$order) {
            return;
        }

        $visitor_id = $this->get_visitor_id();
        $current_date = current_time('Y-m-d');

        $table_name = $wpdb->prefix . 'wpforge_funnel_purchases';

        $wpdb->insert(
            $table_name,
            array(
                'event_date'      => $current_date,
                'visitor_id'      => $visitor_id,
                'order_id'        => $order_id,
                'customer_id'     => $order->get_customer_id(),
                'total_amount'    => $order->get_total(),
                'item_count'      => $order->get_item_count(),
                'payment_method'  => $order->get_payment_method(),
            ),
            array(
                '%s',
                '%s',
                '%d',
                '%d',
                '%f',
                '%d',
                '%s',
            )
        );
    }

    /**
     * 每小时数据采集
     *
     * @since 1.0.0
     */
    public function collect_hourly_data() {
        // 清理过期数据
        $this->cleanup_old_data();
    }

    /**
     * 清理过期数据
     *
     * @since 1.0.0
     */
    private function cleanup_old_data() {
        global $wpdb;

        $retention_days = wpforge_funnel_dashboard()->get_option('data_retention_days', 90);

        if ($retention_days <= 0) {
            return;
        }

        $cutoff_date = date('Y-m-d', strtotime("-{$retention_days} days"));

        $tables = array(
            $wpdb->prefix . 'wpforge_funnel_visits',
            $wpdb->prefix . 'wpforge_funnel_cart_events',
            $wpdb->prefix . 'wpforge_funnel_checkout_events',
        );

        foreach ($tables as $table) {
            $wpdb->query($wpdb->prepare(
                "DELETE FROM {$table} WHERE event_date < %s",
                $cutoff_date
            ));
        }
    }

    /**
     * 获取指定日期范围的漏斗数据
     *
     * @since 1.0.0
     * @param string $start_date 开始日期
     * @param string $end_date 结束日期
     * @return array
     */
    public function get_funnel_data($start_date, $end_date) {
        global $wpdb;

        $table_visits = $wpdb->prefix . 'wpforge_funnel_visits';
        $table_cart = $wpdb->prefix . 'wpforge_funnel_cart_events';
        $table_checkout = $wpdb->prefix . 'wpforge_funnel_checkout_events';
        $table_purchases = $wpdb->prefix . 'wpforge_funnel_purchases';

        // 访客数（去重）
        $visitors = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(DISTINCT visitor_id) FROM {$table_visits} WHERE visit_date BETWEEN %s AND %s",
            $start_date,
            $end_date
        ));

        // 产品浏览数（去重访客）
        $product_views = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(DISTINCT visitor_id) FROM {$table_visits} WHERE visit_date BETWEEN %s AND %s AND page_type = 'product'",
            $start_date,
            $end_date
        ));

        // 加购数（去重访客）
        $add_to_cart = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(DISTINCT visitor_id) FROM {$table_cart} WHERE event_date BETWEEN %s AND %s",
            $start_date,
            $end_date
        ));

        // 开始结账数（去重访客）
        $checkout_starts = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(DISTINCT visitor_id) FROM {$table_checkout} WHERE event_date BETWEEN %s AND %s",
            $start_date,
            $end_date
        ));

        // 完成购买数
        $purchases = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(DISTINCT visitor_id) FROM {$table_purchases} WHERE event_date BETWEEN %s AND %s",
            $start_date,
            $end_date
        ));

        // 订单数和销售额
        $orders_data = $wpdb->get_row($wpdb->prepare(
            "SELECT COUNT(*) as orders, COALESCE(SUM(total_amount), 0) as revenue FROM {$table_purchases} WHERE event_date BETWEEN %s AND %s",
            $start_date,
            $end_date
        ));

        return array(
            'visitors'        => (int) $visitors,
            'product_views'   => (int) $product_views,
            'add_to_cart'     => (int) $add_to_cart,
            'checkout_starts' => (int) $checkout_starts,
            'purchases'       => (int) $purchases,
            'orders'          => (int) $orders_data->orders,
            'revenue'         => (float) $orders_data->revenue,
            'avg_order_value' => $orders_data->orders > 0 ? (float) $orders_data->revenue / $orders_data->orders : 0,
            'conversion_rate' => $visitors > 0 ? round(($purchases / $visitors) * 100, 2) : 0,
        );
    }
}
