<?php
/**
 * Plugin Name: WPForge Relay
 * Plugin URI: https://wpforge.com
 * Description: WPForge中转服务器WordPress插件，提供实时双向通信能力
 * Version: 1.0.0
 * Author: WPForge Team
 * Author URI: https://wpforge.com
 * License: GPL v3
 * License URI: https://www.gnu.org/licenses/gpl-3.0.html
 * Text Domain: wpforge-relay
 * Domain Path: /languages
 */

// 防止直接访问
if (!defined('ABSPATH')) {
    exit;
}

// 插件版本
define('WPFORGE_RELAY_VERSION', '1.0.0');
define('WPFORGE_RELAY_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('WPFORGE_RELAY_PLUGIN_URL', plugin_dir_url(__FILE__));
define('WPFORGE_RELAY_PLUGIN_BASENAME', plugin_basename(__FILE__));

// 加载核心类
require_once WPFORGE_RELAY_PLUGIN_DIR . 'includes/class-websocket-client.php';
require_once WPFORGE_RELAY_PLUGIN_DIR . 'includes/class-event-pusher.php';
require_once WPFORGE_RELAY_PLUGIN_DIR . 'includes/class-command-executor.php';
require_once WPFORGE_RELAY_PLUGIN_DIR . 'includes/class-message-queue.php';

// 管理后台
if (is_admin()) {
    require_once WPFORGE_RELAY_PLUGIN_DIR . 'includes/class-admin-settings.php';
}

/**
 * 插件主类
 */
class WPForge_Relay {

    /**
     * 单例实例
     */
    private static $instance = null;

    /**
     * WebSocket客户端
     */
    private $websocket_client = null;

    /**
     * 事件推送器
     */
    private $event_pusher = null;

    /**
     * 指令执行器
     */
    private $command_executor = null;

    /**
     * 消息队列
     */
    private $message_queue = null;

    /**
     * 获取单例实例
     */
    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    /**
     * 构造函数
     */
    private function __construct() {
        $this->init();
    }

    /**
     * 初始化
     */
    private function init() {
        // 初始化组件
        $this->message_queue = new WPForge_Relay_Message_Queue();
        $this->websocket_client = new WPForge_Relay_WebSocket_Client($this->message_queue);
        $this->event_pusher = new WPForge_Relay_Event_Pusher($this->websocket_client);
        $this->command_executor = new WPForge_Relay_Command_Executor($this->websocket_client);

        // 注册钩子
        add_action('plugins_loaded', array($this, 'load_textdomain'));
        add_action('wpforge_relay_process_queue', array($this, 'process_queue'));

        // 激活钩子
        register_activation_hook(__FILE__, array($this, 'activate'));
        register_deactivation_hook(__FILE__, array($this, 'deactivate'));
    }

    /**
     * 加载翻译
     */
    public function load_textdomain() {
        load_plugin_textdomain('wpforge-relay', false, dirname(WPFORGE_RELAY_PLUGIN_BASENAME) . '/languages');
    }

    /**
     * 插件激活
     */
    public function activate() {
        // 创建数据库表
        $this->message_queue->create_table();
        
        // 设置默认选项
        add_option('wpforge_relay_server_url', '');
        add_option('wpforge_relay_site_id', '');
        add_option('wpforge_relay_site_token', '');
        add_option('wpforge_relay_auto_reconnect', true);
        add_option('wpforge_relay_heartbeat_interval', 30);
        add_option('wpforge_relay_enabled_events', array(
            'woocommerce_new_order',
            'woocommerce_order_status_changed',
            'woocommerce_low_stock',
            'post_published',
            'comment_posted',
            'user_registered'
        ));

        // 调度队列处理
        if (!wp_next_scheduled('wpforge_relay_process_queue')) {
            wp_schedule_event(time(), 'wpforge_relay_1min', 'wpforge_relay_process_queue');
        }
    }

    /**
     * 插件停用
     */
    public function deactivate() {
        // 清除定时任务
        wp_clear_scheduled_hook('wpforge_relay_process_queue');
    }

    /**
     * 处理消息队列
     */
    public function process_queue() {
        $this->message_queue->process_pending_messages();
    }

    /**
     * 获取WebSocket客户端
     */
    public function get_websocket_client() {
        return $this->websocket_client;
    }

    /**
     * 获取事件推送器
     */
    public function get_event_pusher() {
        return $this->event_pusher;
    }

    /**
     * 获取指令执行器
     */
    public function get_command_executor() {
        return $this->command_executor;
    }

    /**
     * 获取消息队列
     */
    public function get_message_queue() {
        return $this->message_queue;
    }
}

// 初始化插件
function wpforge_relay() {
    return WPForge_Relay::get_instance();
}

// 启动插件
add_action('plugins_loaded', 'wpforge_relay', 10);

// 添加自定义cron间隔
add_filter('cron_schedules', function($schedules) {
    $schedules['wpforge_relay_1min'] = array(
        'interval' => 60,
        'display' => __('Every minute', 'wpforge-relay')
    );
    return $schedules;
});
