<?php
/**
 * 管理设置页面类
 * 
 * 提供WordPress后台的插件设置界面
 */

// 防止直接访问
if (!defined('ABSPATH')) {
    exit;
}

class WPForge_Relay_Admin_Settings {

    /**
     * 选项组名称
     */
    private $option_group = 'wpforge_relay_options';

    /**
     * 构造函数
     */
    public function __construct() {
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'register_settings'));
        add_action('admin_enqueue_scripts', array($this, 'enqueue_scripts'));
    }

    /**
     * 添加管理菜单
     */
    public function add_admin_menu() {
        add_options_page(
            __('WPForge Relay 设置', 'wpforge-relay'),
            __('WPForge Relay', 'wpforge-relay'),
            'manage_options',
            'wpforge-relay',
            array($this, 'render_settings_page')
        );
    }

    /**
     * 注册设置
     */
    public function register_settings() {
        register_setting($this->option_group, 'wpforge_relay_server_url');
        register_setting($this->option_group, 'wpforge_relay_site_id');
        register_setting($this->option_group, 'wpforge_relay_site_token');
        register_setting($this->option_group, 'wpforge_relay_auto_reconnect');
        register_setting($this->option_group, 'wpforge_relay_heartbeat_interval');
        register_setting($this->option_group, 'wpforge_relay_enabled_events');
    }

    /**
     * 加载脚本和样式
     */
    public function enqueue_scripts($hook) {
        if ('settings_page_wpforge-relay' !== $hook) {
            return;
        }

        // 可以在这里添加自定义CSS和JS
    }

    /**
     * 渲染设置页面
     */
    public function render_settings_page() {
        if (!current_user_can('manage_options')) {
            wp_die(__('您没有权限访问此页面。', 'wpforge-relay'));
        }

        $relay = wpforge_relay();
        $websocket_client = $relay->get_websocket_client();
        $message_queue = $relay->get_message_queue();
        $event_pusher = $relay->get_event_pusher();

        $connection_status = $websocket_client->is_connected();
        $queue_stats = $message_queue->get_stats();
        $available_events = $event_pusher->get_available_events();
        $enabled_events = get_option('wpforge_relay_enabled_events', array());

        ?>
        <div class="wrap">
            <h1><?php echo esc_html(get_admin_page_title()); ?></h1>

            <!-- 连接状态 -->
            <div class="card" style="max-width: 100%; margin-bottom: 20px;">
                <h2><?php _e('连接状态', 'wpforge-relay'); ?></h2>
                <table class="form-table">
                    <tr>
                        <th scope="row"><?php _e('服务器连接', 'wpforge-relay'); ?></th>
                        <td>
                            <?php if ($connection_status): ?>
                                <span style="color: #46b450; font-weight: bold;">
                                    <?php _e('已连接', 'wpforge-relay'); ?>
                                </span>
                            <?php else: ?>
                                <span style="color: #dc3232; font-weight: bold;">
                                    <?php _e('未连接', 'wpforge-relay'); ?>
                                </span>
                                <p class="description">
                                    <?php _e('请检查服务器地址、站点ID和Token是否正确。', 'wpforge-relay'); ?>
                                </p>
                            <?php endif; ?>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><?php _e('消息队列', 'wpforge-relay'); ?></th>
                        <td>
                            <?php printf(__('待处理: %d, 已完成: %d, 失败: %d', 'wpforge-relay'), 
                                $queue_stats['pending'], 
                                $queue_stats['completed'], 
                                $queue_stats['failed']
                            ); ?>
                        </td>
                    </tr>
                </table>
            </div>

            <form method="post" action="options.php">
                <?php
                settings_fields($this->option_group);
                do_settings_sections($this->option_group);
                ?>

                <!-- 基本设置 -->
                <h2 class="title"><?php _e('基本设置', 'wpforge-relay'); ?></h2>
                <table class="form-table">
                    <tr>
                        <th scope="row">
                            <label for="wpforge_relay_server_url">
                                <?php _e('中转服务器地址', 'wpforge-relay'); ?>
                            </label>
                        </th>
                        <td>
                            <input
                                type="text"
                                id="wpforge_relay_server_url"
                                name="wpforge_relay_server_url"
                                value="<?php echo esc_attr(get_option('wpforge_relay_server_url', '')); ?>"
                                class="regular-text"
                                placeholder="wss://relay.example.com"
                            />
                            <p class="description">
                                <?php _e('中转服务器的WebSocket地址，例如 wss://relay.yourdomain.com', 'wpforge-relay'); ?>
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">
                            <label for="wpforge_relay_site_id">
                                <?php _e('站点ID', 'wpforge-relay'); ?>
                            </label>
                        </th>
                        <td>
                            <input
                                type="text"
                                id="wpforge_relay_site_id"
                                name="wpforge_relay_site_id"
                                value="<?php echo esc_attr(get_option('wpforge_relay_site_id', '')); ?>"
                                class="regular-text"
                                readonly
                            />
                            <p class="description">
                                <?php _e('在中转服务器管理面板注册站点后获得的站点ID', 'wpforge-relay'); ?>
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">
                            <label for="wpforge_relay_site_token">
                                <?php _e('站点Token', 'wpforge-relay'); ?>
                            </label>
                        </th>
                        <td>
                            <input
                                type="password"
                                id="wpforge_relay_site_token"
                                name="wpforge_relay_site_token"
                                value="<?php echo esc_attr(get_option('wpforge_relay_site_token', '')); ?>"
                                class="regular-text"
                                autocomplete="off"
                            />
                            <p class="description">
                                <?php _e('在中转服务器管理面板注册站点后获得的认证Token', 'wpforge-relay'); ?>
                            </p>
                        </td>
                    </tr>
                </table>

                <!-- 高级设置 -->
                <h2 class="title"><?php _e('高级设置', 'wpforge-relay'); ?></h2>
                <table class="form-table">
                    <tr>
                        <th scope="row">
                            <label for="wpforge_relay_auto_reconnect">
                                <?php _e('自动重连', 'wpforge-relay'); ?>
                            </label>
                        </th>
                        <td>
                            <label>
                                <input
                                    type="checkbox"
                                    id="wpforge_relay_auto_reconnect"
                                    name="wpforge_relay_auto_reconnect"
                                    value="1"
                                    <?php checked(get_option('wpforge_relay_auto_reconnect', true)); ?>
                                />
                                <?php _e('连接断开时自动尝试重连', 'wpforge-relay'); ?>
                            </label>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">
                            <label for="wpforge_relay_heartbeat_interval">
                                <?php _e('心跳间隔(秒)', 'wpforge-relay'); ?>
                            </label>
                        </th>
                        <td>
                            <input
                                type="number"
                                id="wpforge_relay_heartbeat_interval"
                                name="wpforge_relay_heartbeat_interval"
                                value="<?php echo esc_attr(get_option('wpforge_relay_heartbeat_interval', 30)); ?>"
                                min="10"
                                max="300"
                                class="small-text"
                            />
                            <p class="description">
                                <?php _e('发送心跳包的间隔时间，用于保持连接活跃', 'wpforge-relay'); ?>
                            </p>
                        </td>
                    </tr>
                </table>

                <!-- 事件推送设置 -->
                <h2 class="title"><?php _e('事件推送设置', 'wpforge-relay'); ?></h2>
                <p class="description">
                    <?php _e('选择需要推送到中转服务器的事件类型', 'wpforge-relay'); ?>
                </p>

                <?php foreach ($available_events as $category => $events): ?>
                    <h3><?php echo esc_html(ucfirst($category)); ?></h3>
                    <table class="form-table">
                        <?php foreach ($events as $event_key => $event_label): ?>
                            <tr>
                                <th scope="row" style="padding-left: 20px;">
                                    <label>
                                        <input
                                            type="checkbox"
                                            name="wpforge_relay_enabled_events[]"
                                            value="<?php echo esc_attr($event_key); ?>"
                                            <?php checked(in_array($event_key, $enabled_events)); ?>
                                        />
                                        <?php echo esc_html($event_label); ?>
                                    </label>
                                </th>
                                <td>
                                    <code style="font-size: 12px;"><?php echo esc_html($event_key); ?></code>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </table>
                <?php endforeach; ?>

                <?php submit_button(); ?>
            </form>

            <!-- 说明文档 -->
            <div class="card" style="max-width: 100%; margin-top: 20px;">
                <h2><?php _e('使用说明', 'wpforge-relay'); ?></h2>
                <ol>
                    <li><?php _e('在中转服务器管理面板中注册您的站点，获取站点ID和Token', 'wpforge-relay'); ?></li>
                    <li><?php _e('将站点ID和Token填入上方表单', 'wpforge-relay'); ?></li>
                    <li><?php _e('选择需要推送的事件类型', 'wpforge-relay'); ?></li>
                    <li><?php _e('保存设置，插件将自动连接到中转服务器', 'wpforge-relay'); ?></li>
                </ol>
                <p>
                    <strong><?php _e('注意：', 'wpforge-relay'); ?></strong>
                    <?php _e('本插件需要中转服务器支持才能正常工作。如果您还没有部署中转服务器，请先部署中转服务器。', 'wpforge-relay'); ?>
                </p>
            </div>
        </div>
        <?php
    }
}

// 初始化管理设置
new WPForge_Relay_Admin_Settings();
