<?php
/**
 * WPForge Theme - Funnel Dashboard Main Class
 *
 * 电商漏斗可视化数据面板主类
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

// Exit if accessed directly.
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Funnel_Dashboard 主类
 *
 * 负责初始化电商漏斗数据面板的所有功能
 *
 * @since 1.0.0
 */
class Funnel_Dashboard {

    /**
     * 单例实例
     *
     * @since 1.0.0
     * @var Funnel_Dashboard|null
     */
    private static $instance = null;

    /**
     * 数据采集器
     *
     * @since 1.0.0
     * @var Funnel_Data_Collector
     */
    public $collector;

    /**
     * 数据处理器
     *
     * @since 1.0.0
     * @var Funnel_Data_Processor
     */
    public $processor;

    /**
     * AI洞察引擎
     *
     * @since 1.0.0
     * @var Funnel_Insights_Engine
     */
    public $insights;

    /**
     * REST API
     *
     * @since 1.0.0
     * @var Funnel_REST_API
     */
    public $rest_api;

    /**
     * 获取单例实例
     *
     * @since 1.0.0
     * @return Funnel_Dashboard
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
        $this->includes();
        $this->init();
        $this->init_hooks();
    }

    /**
     * 包含必要文件
     *
     * @since 1.0.0
     */
    private function includes() {
        require_once WPFORGE_THEME_INC . '/funnel-dashboard/class-data-collector.php';
        require_once WPFORGE_THEME_INC . '/funnel-dashboard/class-data-processor.php';
        require_once WPFORGE_THEME_INC . '/funnel-dashboard/class-insights-engine.php';
        require_once WPFORGE_THEME_INC . '/funnel-dashboard/class-rest-api.php';
    }

    /**
     * 初始化组件
     *
     * @since 1.0.0
     */
    private function init() {
        $this->collector = Funnel_Data_Collector::get_instance();
        $this->processor = Funnel_Data_Processor::get_instance();
        $this->insights  = Funnel_Insights_Engine::get_instance();
        $this->rest_api  = Funnel_REST_API::get_instance();
    }

    /**
     * 初始化钩子
     *
     * @since 1.0.0
     */
    private function init_hooks() {
        // 后台菜单
        add_action('admin_menu', array($this, 'add_admin_menu'));

        // 后台脚本和样式
        add_action('admin_enqueue_scripts', array($this, 'enqueue_admin_assets'));

        // 注册数据库表
        add_action('after_switch_theme', array($this, 'create_tables'));

        // WP Cron 定时任务
        add_action('wp', array($this, 'schedule_cron_events'));
        add_action('wpforge_funnel_daily_aggregate', array($this->processor, 'daily_aggregate'));
        add_action('wpforge_funnel_hourly_collect', array($this->collector, 'collect_hourly_data'));

        // 数据采集钩子
        add_action('wp_footer', array($this->collector, 'maybe_track_visit'), 999);
        add_action('woocommerce_add_to_cart', array($this->collector, 'track_add_to_cart'), 10, 6);
        add_action('woocommerce_before_checkout_form', array($this->collector, 'track_checkout_start'));
        add_action('woocommerce_thankyou', array($this->collector, 'track_purchase_complete'));
    }

    /**
     * 添加后台菜单
     *
     * @since 1.0.0
     */
    public function add_admin_menu() {
        add_menu_page(
            __('电商漏斗', 'wpforge-theme'),
            __('电商漏斗', 'wpforge-theme'),
            'manage_woocommerce',
            'wpforge-funnel-dashboard',
            array($this, 'render_admin_page'),
            'dashicons-chart-bar',
            56
        );

        add_submenu_page(
            'wpforge-funnel-dashboard',
            __('仪表盘', 'wpforge-theme'),
            __('仪表盘', 'wpforge-theme'),
            'manage_woocommerce',
            'wpforge-funnel-dashboard',
            array($this, 'render_admin_page')
        );

        add_submenu_page(
            'wpforge-funnel-dashboard',
            __('设置', 'wpforge-theme'),
            __('设置', 'wpforge-theme'),
            'manage_woocommerce',
            'wpforge-funnel-settings',
            array($this, 'render_settings_page')
        );
    }

    /**
     * 渲染后台页面
     *
     * @since 1.0.0
     */
    public function render_admin_page() {
        include WPFORGE_THEME_INC . '/funnel-dashboard/admin-page.php';
    }

    /**
     * 渲染设置页面
     *
     * @since 1.0.0
     */
    public function render_settings_page() {
        echo '<div class="wrap">';
        echo '<h1>' . esc_html__('电商漏斗设置', 'wpforge-theme') . '</h1>';
        echo '<p>' . esc_html__('设置电商漏斗数据面板的各项参数。', 'wpforge-theme') . '</p>';
        echo '</div>';
    }

    /**
     * 加载后台资源
     *
     * @since 1.0.0
     * @param string $hook 当前页面钩子
     */
    public function enqueue_admin_assets($hook) {
        // 只在漏斗数据面板页面加载
        if (strpos($hook, 'wpforge-funnel') === false) {
            return;
        }

        // 加载样式
        wp_enqueue_style(
            'wpforge-funnel-dashboard',
            WPFORGE_THEME_ASSETS . '/css/funnel-dashboard.css',
            array(),
            WPFORGE_THEME_VERSION
        );

        // 加载漏斗面板脚本
        wp_enqueue_script(
            'wpforge-funnel-dashboard',
            WPFORGE_THEME_ASSETS . '/js/funnel-dashboard.js',
            array('jquery'),
            WPFORGE_THEME_VERSION,
            true
        );

        // 本地化脚本
        wp_localize_script('wpforge-funnel-dashboard', 'wpforgeFunnelData', array(
            'rest_url'   => rest_url('wpforge/v1'),
            'nonce'     => wp_create_nonce('wp_rest'),
            'strings'   => array(
                'loading'       => __('加载中...', 'wpforge-theme'),
                'visitors'      => __('访客数', 'wpforge-theme'),
                'productViews'  => __('浏览产品', 'wpforge-theme'),
                'addToCart'     => __('加入购物车', 'wpforge-theme'),
                'checkout'      => __('开始结账', 'wpforge-theme'),
                'purchases'     => __('完成购买', 'wpforge-theme'),
                'conversionRate' => __('转化率', 'wpforge-theme'),
                'revenue'       => __('销售额', 'wpforge-theme'),
                'orders'        => __('订单数', 'wpforge-theme'),
                'avgOrderValue' => __('客单价', 'wpforge-theme'),
            ),
        ));
    }

    /**
     * 创建数据库表
     *
     * @since 1.0.0
     */
    public function create_tables() {
        global $wpdb;

        $charset_collate = $wpdb->get_charset_collate();

        // 访问记录表
        $table_visits = $wpdb->prefix . 'wpforge_funnel_visits';
        $sql_visits = "CREATE TABLE IF NOT EXISTS $table_visits (
            id bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
            visit_date date NOT NULL,
            visit_hour tinyint(2) UNSIGNED NOT NULL DEFAULT 0,
            visitor_id varchar(64) NOT NULL,
            session_id varchar(64) NOT NULL,
            page_type varchar(32) NOT NULL DEFAULT 'other',
            product_id bigint(20) UNSIGNED DEFAULT NULL,
            referrer varchar(255) DEFAULT NULL,
            source varchar(32) DEFAULT 'direct',
            device_type varchar(16) DEFAULT 'desktop',
            country_code varchar(8) DEFAULT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY visit_date (visit_date),
            KEY visitor_id (visitor_id),
            KEY product_id (product_id),
            KEY source (source),
            KEY device_type (device_type)
        ) $charset_collate;";

        // 加购记录表
        $table_cart = $wpdb->prefix . 'wpforge_funnel_cart_events';
        $sql_cart = "CREATE TABLE IF NOT EXISTS $table_cart (
            id bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
            event_date date NOT NULL,
            visitor_id varchar(64) NOT NULL,
            session_id varchar(64) NOT NULL,
            product_id bigint(20) UNSIGNED NOT NULL,
            quantity int(10) UNSIGNED NOT NULL DEFAULT 1,
            cart_item_key varchar(64) DEFAULT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY event_date (event_date),
            KEY visitor_id (visitor_id),
            KEY product_id (product_id)
        ) $charset_collate;";

        // 结账记录表
        $table_checkout = $wpdb->prefix . 'wpforge_funnel_checkout_events';
        $sql_checkout = "CREATE TABLE IF NOT EXISTS $table_checkout (
            id bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
            event_date date NOT NULL,
            visitor_id varchar(64) NOT NULL,
            session_id varchar(64) NOT NULL,
            cart_hash varchar(64) DEFAULT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY event_date (event_date),
            KEY visitor_id (visitor_id)
        ) $charset_collate;";

        // 购买记录表
        $table_purchases = $wpdb->prefix . 'wpforge_funnel_purchases';
        $sql_purchases = "CREATE TABLE IF NOT EXISTS $table_purchases (
            id bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
            event_date date NOT NULL,
            visitor_id varchar(64) DEFAULT NULL,
            order_id bigint(20) UNSIGNED NOT NULL,
            customer_id bigint(20) UNSIGNED DEFAULT NULL,
            total_amount decimal(10,2) NOT NULL DEFAULT 0.00,
            item_count int(10) UNSIGNED NOT NULL DEFAULT 0,
            payment_method varchar(32) DEFAULT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY event_date (event_date),
            KEY order_id (order_id),
            KEY customer_id (customer_id)
        ) $charset_collate;";

        // 每日聚合表
        $table_daily = $wpdb->prefix . 'wpforge_funnel_daily';
        $sql_daily = "CREATE TABLE IF NOT EXISTS $table_daily (
            id bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
            stat_date date NOT NULL,
            visitors int(10) UNSIGNED NOT NULL DEFAULT 0,
            product_views int(10) UNSIGNED NOT NULL DEFAULT 0,
            add_to_cart int(10) UNSIGNED NOT NULL DEFAULT 0,
            checkout_starts int(10) UNSIGNED NOT NULL DEFAULT 0,
            purchases int(10) UNSIGNED NOT NULL DEFAULT 0,
            orders int(10) UNSIGNED NOT NULL DEFAULT 0,
            revenue decimal(12,2) NOT NULL DEFAULT 0.00,
            avg_order_value decimal(10,2) NOT NULL DEFAULT 0.00,
            conversion_rate decimal(5,2) NOT NULL DEFAULT 0.00,
            avg_items_per_order decimal(4,2) NOT NULL DEFAULT 0.00,
            PRIMARY KEY (id),
            UNIQUE KEY stat_date (stat_date)
        ) $charset_collate;";

        // 产品统计数据表
        $table_products = $wpdb->prefix . 'wpforge_funnel_product_stats';
        $sql_products = "CREATE TABLE IF NOT EXISTS $table_products (
            id bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
            stat_date date NOT NULL,
            product_id bigint(20) UNSIGNED NOT NULL,
            views int(10) UNSIGNED NOT NULL DEFAULT 0,
            add_to_cart int(10) UNSIGNED NOT NULL DEFAULT 0,
            purchases int(10) UNSIGNED NOT NULL DEFAULT 0,
            revenue decimal(12,2) NOT NULL DEFAULT 0.00,
            abandonment_rate decimal(5,2) NOT NULL DEFAULT 0.00,
            PRIMARY KEY (id),
            UNIQUE KEY date_product (stat_date, product_id),
            KEY product_id (product_id)
        ) $charset_collate;";

        require_once ABSPATH . 'wp-admin/includes/upgrade.php';
        dbDelta($sql_visits);
        dbDelta($sql_cart);
        dbDelta($sql_checkout);
        dbDelta($sql_purchases);
        dbDelta($sql_daily);
        dbDelta($sql_products);
    }

    /**
     * 注册定时任务
     *
     * @since 1.0.0
     */
    public function schedule_cron_events() {
        if (!wp_next_scheduled('wpforge_funnel_daily_aggregate')) {
            wp_schedule_event(strtotime('tomorrow 2:00 am'), 'daily', 'wpforge_funnel_daily_aggregate');
        }

        if (!wp_next_scheduled('wpforge_funnel_hourly_collect')) {
            wp_schedule_event(time(), 'hourly', 'wpforge_funnel_hourly_collect');
        }
    }

    /**
     * 获取设置选项
     *
     * @since 1.0.0
     * @param string $key 选项键
     * @param mixed $default 默认值
     * @return mixed
     */
    public function get_option($key, $default = null) {
        $options = get_option('wpforge_funnel_settings', array());
        return isset($options[$key]) ? $options[$key] : $default;
    }

    /**
     * 更新设置选项
     *
     * @since 1.0.0
     * @param string $key 选项键
     * @param mixed $value 选项值
     */
    public function update_option($key, $value) {
        $options = get_option('wpforge_funnel_settings', array());
        $options[$key] = $value;
        update_option('wpforge_funnel_settings', $options);
    }
}

/**
 * 获取漏斗数据面板实例
 *
 * @since 1.0.0
 * @return Funnel_Dashboard
 */
function wpforge_funnel_dashboard() {
    return Funnel_Dashboard::get_instance();
}
