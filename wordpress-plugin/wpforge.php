<?php
/**
 * Plugin Name: WPForge - WordPress AI仿站助手
 * Plugin URI: https://wpforge.com
 * Description: WPForge配套WordPress插件，提供产品批量导入、SEO优化、速度优化等功能
 * Version: 1.0.0
 * Author: WPForge Team
 * Author URI: https://wpforge.com
 * License: GPL v2 or later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain: wpforge
 * Domain Path: /languages
 */

// 防止直接访问
if (!defined('ABSPATH')) {
    exit;
}

// 插件版本
define('WPFORGE_VERSION', '1.0.0');
define('WPFORGE_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('WPFORGE_PLUGIN_URL', plugin_dir_url(__FILE__));
define('WPFORGE_PLUGIN_BASENAME', plugin_basename(__FILE__));

/**
 * WPForge主类
 */
class WPForge {
    
    /**
     * 单例实例
     */
    private static $instance = null;
    
    /**
     * 获取单例
     */
    public static function get_instance() {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    /**
     * 构造函数
     */
    private function __construct() {
        $this->init_hooks();
        $this->includes();
    }
    
    /**
     * 初始化钩子
     */
    private function init_hooks() {
        // 激活插件
        register_activation_hook(__FILE__, array($this, 'activate'));
        
        // 停用插件
        register_deactivation_hook(__FILE__, array($this, 'deactivate'));
        
        // 加载文本域
        add_action('plugins_loaded', array($this, 'load_textdomain'));
        
        // 添加管理菜单
        add_action('admin_menu', array($this, 'add_admin_menu'));
        
        // 注册设置
        add_action('admin_init', array($this, 'register_settings'));
        
        // 添加设置链接
        add_filter('plugin_action_links_' . WPFORGE_PLUGIN_BASENAME, array($this, 'add_settings_link'));
        
        // 注册REST API路由
        add_action('rest_api_init', array($this, 'register_rest_routes'));
        
        // 加载管理资源
        add_action('admin_enqueue_scripts', array($this, 'enqueue_admin_scripts'));
    }
    
    /**
     * 包含文件
     */
    private function includes() {
        // 产品导入类
        require_once WPFORGE_PLUGIN_DIR . 'includes/class-wpforge-product-importer.php';
        
        // SEO优化类
        require_once WPFORGE_PLUGIN_DIR . 'includes/class-wpforge-seo.php';
        
        // 速度优化类
        require_once WPFORGE_PLUGIN_DIR . 'includes/class-wpforge-speed.php';
        
        // API类
        require_once WPFORGE_PLUGIN_DIR . 'includes/class-wpforge-api.php';
    }
    
    /**
     * 激活插件
     */
    public function activate() {
        // 创建数据库表
        $this->create_tables();
        
        // 设置默认选项
        add_option('wpforge_version', WPFORGE_VERSION);
        add_option('wpforge_api_key', '');
        add_option('wpforge_api_url', '');
        add_option('wpforge_seo_enabled', 1);
        add_option('wpforge_speed_enabled', 1);
        add_option('wpforge_image_optimization', 1);
        add_option('wpforge_cache_enabled', 1);
        
        // 刷新重写规则
        flush_rewrite_rules();
    }
    
    /**
     * 停用插件
     */
    public function deactivate() {
        // 刷新重写规则
        flush_rewrite_rules();
    }
    
    /**
     * 创建数据库表
     */
    private function create_tables() {
        global $wpdb;
        
        $charset_collate = $wpdb->get_charset_collate();
        
        // 导入日志表
        $table_name = $wpdb->prefix . 'wpforge_import_logs';
        $sql = "CREATE TABLE $table_name (
            id bigint(20) NOT NULL AUTO_INCREMENT,
            task_id varchar(100) NOT NULL,
            type varchar(50) NOT NULL,
            status varchar(20) NOT NULL DEFAULT 'pending',
            total int(11) NOT NULL DEFAULT 0,
            success int(11) NOT NULL DEFAULT 0,
            failed int(11) NOT NULL DEFAULT 0,
            skipped int(11) NOT NULL DEFAULT 0,
            errors text DEFAULT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            updated_at datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY task_id (task_id),
            KEY status (status)
        ) $charset_collate;";
        
        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        dbDelta($sql);
    }
    
    /**
     * 加载文本域
     */
    public function load_textdomain() {
        load_plugin_textdomain('wpforge', false, dirname(WPFORGE_PLUGIN_BASENAME) . '/languages');
    }
    
    /**
     * 添加管理菜单
     */
    public function add_admin_menu() {
        add_menu_page(
            'WPForge',
            'WPForge',
            'manage_options',
            'wpforge',
            array($this, 'render_dashboard_page'),
            'dashicons-hammer',
            30
        );
        
        add_submenu_page(
            'wpforge',
            __('仪表盘', 'wpforge'),
            __('仪表盘', 'wpforge'),
            'manage_options',
            'wpforge',
            array($this, 'render_dashboard_page')
        );
        
        add_submenu_page(
            'wpforge',
            __('产品导入', 'wpforge'),
            __('产品导入', 'wpforge'),
            'manage_options',
            'wpforge-import',
            array($this, 'render_import_page')
        );
        
        add_submenu_page(
            'wpforge',
            __('SEO优化', 'wpforge'),
            __('SEO优化', 'wpforge'),
            'manage_options',
            'wpforge-seo',
            array($this, 'render_seo_page')
        );
        
        add_submenu_page(
            'wpforge',
            __('速度优化', 'wpforge'),
            __('速度优化', 'wpforge'),
            'manage_options',
            'wpforge-speed',
            array($this, 'render_speed_page')
        );
        
        add_submenu_page(
            'wpforge',
            __('设置', 'wpforge'),
            __('设置', 'wpforge'),
            'manage_options',
            'wpforge-settings',
            array($this, 'render_settings_page')
        );
    }
    
    /**
     * 注册设置
     */
    public function register_settings() {
        register_setting('wpforge_settings', 'wpforge_api_key');
        register_setting('wpforge_settings', 'wpforge_api_url');
        register_setting('wpforge_settings', 'wpforge_seo_enabled');
        register_setting('wpforge_settings', 'wpforge_speed_enabled');
        register_setting('wpforge_settings', 'wpforge_image_optimization');
        register_setting('wpforge_settings', 'wpforge_cache_enabled');
    }
    
    /**
     * 添加设置链接
     */
    public function add_settings_link($links) {
        $settings_link = '<a href="' . admin_url('admin.php?page=wpforge-settings') . '">' . __('设置', 'wpforge') . '</a>';
        array_unshift($links, $settings_link);
        return $links;
    }
    
    /**
     * 注册REST API路由
     */
    public function register_rest_routes() {
        $api = new WPForge_API();
        $api->register_routes();
    }
    
    /**
     * 加载管理脚本
     */
    public function enqueue_admin_scripts($hook) {
        // 只在插件页面加载
        if (strpos($hook, 'wpforge') === false) {
            return;
        }
        
        // 样式
        wp_enqueue_style('wpforge-admin', WPFORGE_PLUGIN_URL . 'assets/css/admin.css', array(), WPFORGE_VERSION);
        
        // 脚本
        wp_enqueue_script('wpforge-admin', WPFORGE_PLUGIN_URL . 'assets/js/admin.js', array('jquery'), WPFORGE_VERSION, true);
        
        // 本地化脚本
        wp_localize_script('wpforge-admin', 'wpforgeData', array(
            'ajaxUrl' => admin_url('admin-ajax.php'),
            'restUrl' => esc_url_raw(rest_url('wpforge/v1')),
            'restNonce' => wp_create_nonce('wp_rest'),
            'nonce' => wp_create_nonce('wpforge_nonce'),
            'apiUrl' => esc_url_raw(get_option('wpforge_api_url', '')),
            'apiKey' => get_option('wpforge_api_key', ''),
            'strings' => array(
                'confirm' => __('确定吗？', 'wpforge'),
                'importing' => __('导入中...', 'wpforge'),
                'success' => __('成功', 'wpforge'),
                'error' => __('错误', 'wpforge'),
                'requestFailed' => __('请求失败，请重试', 'wpforge'),
                'noPostId' => __('未找到可分析的内容，请先创建产品或文章', 'wpforge'),
            )
        ));
    }
    
    /**
     * 渲染仪表盘页面
     */
    public function render_dashboard_page() {
        include WPFORGE_PLUGIN_DIR . 'admin/pages/dashboard.php';
    }
    
    /**
     * 渲染导入页面
     */
    public function render_import_page() {
        include WPFORGE_PLUGIN_DIR . 'admin/pages/import.php';
    }
    
    /**
     * 渲染SEO页面
     */
    public function render_seo_page() {
        include WPFORGE_PLUGIN_DIR . 'admin/pages/seo.php';
    }
    
    /**
     * 渲染速度页面
     */
    public function render_speed_page() {
        include WPFORGE_PLUGIN_DIR . 'admin/pages/speed.php';
    }
    
    /**
     * 渲染设置页面
     */
    public function render_settings_page() {
        include WPFORGE_PLUGIN_DIR . 'admin/pages/settings.php';
    }
}

// 初始化插件
WPForge::get_instance();
