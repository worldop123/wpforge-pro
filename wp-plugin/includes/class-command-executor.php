<?php
/**
 * 指令执行引擎
 * 
 * 接收来自中转服务器的指令并执行操作
 */

// 防止直接访问
if (!defined('ABSPATH')) {
    exit;
}

class WPForge_Relay_Command_Executor {

    /**
     * WebSocket客户端实例
     */
    private $websocket_client = null;

    /**
     * 构造函数
     */
    public function __construct($websocket_client) {
        $this->websocket_client = $websocket_client;

        // 注册指令接收钩子
        add_action('wpforge_relay_command_received', array($this, 'execute_command'));
    }

    /**
     * 执行指令
     */
    public function execute_command($command_data) {
        $command_id = isset($command_data['messageId']) ? $command_data['messageId'] : '';
        $command = isset($command_data['command']) ? $command_data['command'] : '';
        $params = isset($command_data['params']) ? $command_data['params'] : array();

        if (empty($command)) {
            $this->send_error_response($command_id, 'Command is required');
            return;
        }

        try {
            // 执行指令
            $result = $this->dispatch_command($command, $params);

            // 发送成功响应
            $this->websocket_client->send_response(
                $command_id,
                true,
                $result
            );

        } catch (Exception $e) {
            // 发送错误响应
            $this->send_error_response($command_id, $e->getMessage());
        }
    }

    /**
     * 分发指令
     */
    private function dispatch_command($command, $params) {
        // 指令分类
        $command_map = array(
            // 内容管理
            'get_post' => array($this, 'cmd_get_post'),
            'create_post' => array($this, 'cmd_create_post'),
            'update_post' => array($this, 'cmd_update_post'),
            'delete_post' => array($this, 'cmd_delete_post'),
            'list_posts' => array($this, 'cmd_list_posts'),

            // 产品管理
            'get_product' => array($this, 'cmd_get_product'),
            'create_product' => array($this, 'cmd_create_product'),
            'update_product' => array($this, 'cmd_update_product'),
            'delete_product' => array($this, 'cmd_delete_product'),
            'list_products' => array($this, 'cmd_list_products'),
            'update_stock' => array($this, 'cmd_update_stock'),

            // 媒体管理
            'get_media' => array($this, 'cmd_get_media'),
            'upload_media' => array($this, 'cmd_upload_media'),
            'delete_media' => array($this, 'cmd_delete_media'),

            // 分类标签
            'get_categories' => array($this, 'cmd_get_categories'),
            'get_tags' => array($this, 'cmd_get_tags'),

            // 站点配置
            'get_site_info' => array($this, 'cmd_get_site_info'),
            'update_site_settings' => array($this, 'cmd_update_site_settings'),

            // 插件主题
            'list_plugins' => array($this, 'cmd_list_plugins'),
            'activate_plugin' => array($this, 'cmd_activate_plugin'),
            'deactivate_plugin' => array($this, 'cmd_deactivate_plugin'),
            'get_theme' => array($this, 'cmd_get_theme'),

            // 用户管理
            'get_user' => array($this, 'cmd_get_user'),
            'list_users' => array($this, 'cmd_list_users'),

            // SEO
            'update_seo' => array($this, 'cmd_update_seo'),

            // 系统工具
            'system_info' => array($this, 'cmd_system_info'),
            'clear_cache' => array($this, 'cmd_clear_cache'),
            'health_check' => array($this, 'cmd_health_check'),
        );

        if (isset($command_map[$command])) {
            return call_user_func($command_map[$command], $params);
        }

        throw new Exception('Unknown command: ' . $command);
    }

    // ===== 内容管理指令 =====

    /**
     * 获取文章
     */
    private function cmd_get_post($params) {
        $post_id = isset($params['post_id']) ? intval($params['post_id']) : 0;
        if (!$post_id) {
            throw new Exception('post_id is required');
        }

        $post = get_post($post_id);
        if (!$post) {
            throw new Exception('Post not found');
        }

        return array(
            'post_id' => $post->ID,
            'post_title' => $post->post_title,
            'post_content' => $post->post_content,
            'post_excerpt' => $post->post_excerpt,
            'post_status' => $post->post_status,
            'post_type' => $post->post_type,
            'post_author' => $post->post_author,
            'post_date' => $post->post_date,
            'post_modified' => $post->post_modified,
            'permalink' => get_permalink($post_id),
        );
    }

    /**
     * 创建文章
     */
    private function cmd_create_post($params) {
        $post_data = array(
            'post_title' => isset($params['title']) ? sanitize_text_field($params['title']) : '',
            'post_content' => isset($params['content']) ? wp_kses_post($params['content']) : '',
            'post_excerpt' => isset($params['excerpt']) ? sanitize_text_field($params['excerpt']) : '',
            'post_status' => isset($params['status']) ? sanitize_text_field($params['status']) : 'draft',
            'post_type' => isset($params['type']) ? sanitize_text_field($params['type']) : 'post',
            'post_author' => isset($params['author']) ? intval($params['author']) : get_current_user_id(),
        );

        if (empty($post_data['post_title'])) {
            throw new Exception('Title is required');
        }

        $post_id = wp_insert_post($post_data, true);

        if (is_wp_error($post_id)) {
            throw new Exception($post_id->get_error_message());
        }

        // 设置分类
        if (isset($params['categories']) && is_array($params['categories'])) {
            wp_set_post_categories($post_id, $params['categories']);
        }

        // 设置标签
        if (isset($params['tags']) && is_array($params['tags'])) {
            wp_set_post_tags($post_id, $params['tags']);
        }

        return array(
            'post_id' => $post_id,
            'permalink' => get_permalink($post_id),
        );
    }

    /**
     * 更新文章
     */
    private function cmd_update_post($params) {
        $post_id = isset($params['post_id']) ? intval($params['post_id']) : 0;
        if (!$post_id) {
            throw new Exception('post_id is required');
        }

        $post = get_post($post_id);
        if (!$post) {
            throw new Exception('Post not found');
        }

        $post_data = array('ID' => $post_id);

        if (isset($params['title'])) {
            $post_data['post_title'] = sanitize_text_field($params['title']);
        }
        if (isset($params['content'])) {
            $post_data['post_content'] = wp_kses_post($params['content']);
        }
        if (isset($params['excerpt'])) {
            $post_data['post_excerpt'] = sanitize_text_field($params['excerpt']);
        }
        if (isset($params['status'])) {
            $post_data['post_status'] = sanitize_text_field($params['status']);
        }

        $result = wp_update_post($post_data, true);

        if (is_wp_error($result)) {
            throw new Exception($result->get_error_message());
        }

        return array('success' => true, 'post_id' => $post_id);
    }

    /**
     * 删除文章
     */
    private function cmd_delete_post($params) {
        $post_id = isset($params['post_id']) ? intval($params['post_id']) : 0;
        $force = isset($params['force']) ? boolval($params['force']) : false;

        if (!$post_id) {
            throw new Exception('post_id is required');
        }

        $result = wp_delete_post($post_id, $force);

        if (!$result) {
            throw new Exception('Failed to delete post');
        }

        return array('success' => true);
    }

    /**
     * 文章列表
     */
    private function cmd_list_posts($params) {
        $args = array(
            'post_type' => isset($params['type']) ? sanitize_text_field($params['type']) : 'post',
            'post_status' => isset($params['status']) ? sanitize_text_field($params['status']) : 'publish',
            'posts_per_page' => isset($params['limit']) ? intval($params['limit']) : 20,
            'paged' => isset($params['page']) ? intval($params['page']) : 1,
            'orderby' => isset($params['orderby']) ? sanitize_text_field($params['orderby']) : 'date',
            'order' => isset($params['order']) ? sanitize_text_field($params['order']) : 'DESC',
        );

        $query = new WP_Query($args);
        $posts = array();

        foreach ($query->posts as $post) {
            $posts[] = array(
                'post_id' => $post->ID,
                'post_title' => $post->post_title,
                'post_status' => $post->post_status,
                'post_date' => $post->post_date,
                'post_modified' => $post->post_modified,
                'permalink' => get_permalink($post->ID),
            );
        }

        return array(
            'posts' => $posts,
            'total' => $query->found_posts,
            'pages' => $query->max_num_pages,
        );
    }

    // ===== 产品管理指令 =====

    /**
     * 获取产品
     */
    private function cmd_get_product($params) {
        if (!function_exists('wc_get_product')) {
            throw new Exception('WooCommerce is not installed');
        }

        $product_id = isset($params['product_id']) ? intval($params['product_id']) : 0;
        if (!$product_id) {
            throw new Exception('product_id is required');
        }

        $product = wc_get_product($product_id);
        if (!$product) {
            throw new Exception('Product not found');
        }

        return array(
            'product_id' => $product->get_id(),
            'name' => $product->get_name(),
            'sku' => $product->get_sku(),
            'price' => $product->get_price(),
            'regular_price' => $product->get_regular_price(),
            'sale_price' => $product->get_sale_price(),
            'stock_quantity' => $product->get_stock_quantity(),
            'stock_status' => $product->get_stock_status(),
            'status' => $product->get_status(),
            'description' => $product->get_description(),
            'short_description' => $product->get_short_description(),
            'permalink' => $product->get_permalink(),
            'categories' => wp_get_post_terms($product_id, 'product_cat', array('fields' => 'names')),
            'tags' => wp_get_post_terms($product_id, 'product_tag', array('fields' => 'names')),
        );
    }

    /**
     * 创建产品
     */
    private function cmd_create_product($params) {
        if (!function_exists('wc_get_product')) {
            throw new Exception('WooCommerce is not installed');
        }

        $product = new WC_Product_Simple();

        if (isset($params['name'])) {
            $product->set_name(sanitize_text_field($params['name']));
        }
        if (isset($params['sku'])) {
            $product->set_sku(sanitize_text_field($params['sku']));
        }
        if (isset($params['regular_price'])) {
            $product->set_regular_price(floatval($params['regular_price']));
        }
        if (isset($params['sale_price'])) {
            $product->set_sale_price(floatval($params['sale_price']));
        }
        if (isset($params['description'])) {
            $product->set_description(wp_kses_post($params['description']));
        }
        if (isset($params['short_description'])) {
            $product->set_short_description(wp_kses_post($params['short_description']));
        }
        if (isset($params['stock_quantity'])) {
            $product->set_stock_quantity(intval($params['stock_quantity']));
            $product->set_manage_stock(true);
        }
        if (isset($params['status'])) {
            $product->set_status(sanitize_text_field($params['status']));
        } else {
            $product->set_status('draft');
        }

        $product_id = $product->save();

        if (!$product_id) {
            throw new Exception('Failed to create product');
        }

        return array(
            'product_id' => $product_id,
            'permalink' => get_permalink($product_id),
        );
    }

    /**
     * 更新产品
     */
    private function cmd_update_product($params) {
        if (!function_exists('wc_get_product')) {
            throw new Exception('WooCommerce is not installed');
        }

        $product_id = isset($params['product_id']) ? intval($params['product_id']) : 0;
        if (!$product_id) {
            throw new Exception('product_id is required');
        }

        $product = wc_get_product($product_id);
        if (!$product) {
            throw new Exception('Product not found');
        }

        if (isset($params['name'])) {
            $product->set_name(sanitize_text_field($params['name']));
        }
        if (isset($params['regular_price'])) {
            $product->set_regular_price(floatval($params['regular_price']));
        }
        if (isset($params['sale_price'])) {
            $product->set_sale_price(floatval($params['sale_price']));
        }
        if (isset($params['description'])) {
            $product->set_description(wp_kses_post($params['description']));
        }
        if (isset($params['stock_quantity'])) {
            $product->set_stock_quantity(intval($params['stock_quantity']));
            $product->set_manage_stock(true);
        }
        if (isset($params['status'])) {
            $product->set_status(sanitize_text_field($params['status']));
        }

        $product->save();

        return array('success' => true, 'product_id' => $product_id);
    }

    /**
     * 删除产品
     */
    private function cmd_delete_product($params) {
        if (!function_exists('wc_get_product')) {
            throw new Exception('WooCommerce is not installed');
        }

        $product_id = isset($params['product_id']) ? intval($params['product_id']) : 0;
        $force = isset($params['force']) ? boolval($params['force']) : false;

        if (!$product_id) {
            throw new Exception('product_id is required');
        }

        $result = wp_delete_post($product_id, $force);

        if (!$result) {
            throw new Exception('Failed to delete product');
        }

        return array('success' => true);
    }

    /**
     * 产品列表
     */
    private function cmd_list_products($params) {
        if (!function_exists('wc_get_products')) {
            throw new Exception('WooCommerce is not installed');
        }

        $args = array(
            'limit' => isset($params['limit']) ? intval($params['limit']) : 20,
            'page' => isset($params['page']) ? intval($params['page']) : 1,
            'status' => isset($params['status']) ? sanitize_text_field($params['status']) : 'publish',
            'orderby' => isset($params['orderby']) ? sanitize_text_field($params['orderby']) : 'date',
            'order' => isset($params['order']) ? sanitize_text_field($params['order']) : 'DESC',
            'return' => 'objects',
        );

        $products = wc_get_products($args);
        $result = array();

        foreach ($products as $product) {
            $result[] = array(
                'product_id' => $product->get_id(),
                'name' => $product->get_name(),
                'sku' => $product->get_sku(),
                'price' => $product->get_price(),
                'stock_quantity' => $product->get_stock_quantity(),
                'stock_status' => $product->get_stock_status(),
                'status' => $product->get_status(),
                'permalink' => $product->get_permalink(),
            );
        }

        return array(
            'products' => $result,
            'total' => wc_get_products(array_merge($args, array('limit' => -1, 'fields' => 'ids'))),
        );
    }

    /**
     * 更新库存
     */
    private function cmd_update_stock($params) {
        if (!function_exists('wc_get_product')) {
            throw new Exception('WooCommerce is not installed');
        }

        $product_id = isset($params['product_id']) ? intval($params['product_id']) : 0;
        $quantity = isset($params['quantity']) ? intval($params['quantity']) : 0;

        if (!$product_id) {
            throw new Exception('product_id is required');
        }

        $product = wc_get_product($product_id);
        if (!$product) {
            throw new Exception('Product not found');
        }

        $product->set_stock_quantity($quantity);
        $product->set_manage_stock(true);
        $product->save();

        return array(
            'success' => true,
            'product_id' => $product_id,
            'new_quantity' => $quantity,
        );
    }

    // ===== 站点配置指令 =====

    /**
     * 获取站点信息
     */
    private function cmd_get_site_info($params) {
        return array(
            'site_name' => get_bloginfo('name'),
            'site_description' => get_bloginfo('description'),
            'site_url' => site_url(),
            'home_url' => home_url(),
            'admin_email' => get_bloginfo('admin_email'),
            'language' => get_bloginfo('language'),
            'wp_version' => get_bloginfo('version'),
            'php_version' => phpversion(),
            'theme' => get_option('stylesheet'),
            'plugins' => get_option('active_plugins'),
        );
    }

    /**
     * 更新站点设置
     */
    private function cmd_update_site_settings($params) {
        if (isset($params['blogname'])) {
            update_option('blogname', sanitize_text_field($params['blogname']));
        }
        if (isset($params['blogdescription'])) {
            update_option('blogdescription', sanitize_text_field($params['blogdescription']));
        }
        if (isset($params['admin_email'])) {
            update_option('admin_email', sanitize_email($params['admin_email']));
        }

        return array('success' => true);
    }

    // ===== 插件主题指令 =====

    /**
     * 插件列表
     */
    private function cmd_list_plugins($params) {
        if (!function_exists('get_plugins')) {
            require_once ABSPATH . 'wp-admin/includes/plugin.php';
        }

        $all_plugins = get_plugins();
        $active_plugins = get_option('active_plugins', array());
        $result = array();

        foreach ($all_plugins as $plugin_file => $plugin_data) {
            $result[] = array(
                'plugin_file' => $plugin_file,
                'name' => $plugin_data['Name'],
                'version' => $plugin_data['Version'],
                'description' => $plugin_data['Description'],
                'author' => $plugin_data['Author'],
                'active' => in_array($plugin_file, $active_plugins),
            );
        }

        return array('plugins' => $result);
    }

    /**
     * 激活插件
     */
    private function cmd_activate_plugin($params) {
        if (!function_exists('activate_plugin')) {
            require_once ABSPATH . 'wp-admin/includes/plugin.php';
        }

        $plugin = isset($params['plugin']) ? sanitize_text_field($params['plugin']) : '';
        if (!$plugin) {
            throw new Exception('plugin is required');
        }

        $result = activate_plugin($plugin);

        if (is_wp_error($result)) {
            throw new Exception($result->get_error_message());
        }

        return array('success' => true, 'plugin' => $plugin);
    }

    /**
     * 停用插件
     */
    private function cmd_deactivate_plugin($params) {
        if (!function_exists('deactivate_plugins')) {
            require_once ABSPATH . 'wp-admin/includes/plugin.php';
        }

        $plugin = isset($params['plugin']) ? sanitize_text_field($params['plugin']) : '';
        if (!$plugin) {
            throw new Exception('plugin is required');
        }

        deactivate_plugins($plugin);

        return array('success' => true, 'plugin' => $plugin);
    }

    /**
     * 获取当前主题
     */
    private function cmd_get_theme($params) {
        $theme = wp_get_theme();

        return array(
            'name' => $theme->get('Name'),
            'version' => $theme->get('Version'),
            'author' => $theme->get('Author'),
            'description' => $theme->get('Description'),
            'stylesheet' => get_option('stylesheet'),
            'template' => get_option('template'),
        );
    }

    // ===== 用户管理指令 =====

    /**
     * 获取用户
     */
    private function cmd_get_user($params) {
        $user_id = isset($params['user_id']) ? intval($params['user_id']) : 0;
        if (!$user_id) {
            throw new Exception('user_id is required');
        }

        $user = get_user_by('id', $user_id);
        if (!$user) {
            throw new Exception('User not found');
        }

        return array(
            'user_id' => $user->ID,
            'user_login' => $user->user_login,
            'user_email' => $user->user_email,
            'display_name' => $user->display_name,
            'roles' => $user->roles,
            'user_registered' => $user->user_registered,
        );
    }

    /**
     * 用户列表
     */
    private function cmd_list_users($params) {
        $args = array(
            'number' => isset($params['limit']) ? intval($params['limit']) : 20,
            'paged' => isset($params['page']) ? intval($params['page']) : 1,
            'role' => isset($params['role']) ? sanitize_text_field($params['role']) : '',
            'orderby' => isset($params['orderby']) ? sanitize_text_field($params['orderby']) : 'ID',
            'order' => isset($params['order']) ? sanitize_text_field($params['order']) : 'ASC',
        );

        $user_query = new WP_User_Query($args);
        $users = array();

        foreach ($user_query->get_results() as $user) {
            $users[] = array(
                'user_id' => $user->ID,
                'user_login' => $user->user_login,
                'user_email' => $user->user_email,
                'display_name' => $user->display_name,
                'roles' => $user->roles,
            );
        }

        return array(
            'users' => $users,
            'total' => $user_query->get_total(),
        );
    }

    // ===== 系统工具指令 =====

    /**
     * 系统信息
     */
    private function cmd_system_info($params) {
        return array(
            'wordpress_version' => get_bloginfo('version'),
            'php_version' => phpversion(),
            'mysql_version' => $GLOBALS['wpdb']->db_version(),
            'server_software' => isset($_SERVER['SERVER_SOFTWARE']) ? $_SERVER['SERVER_SOFTWARE'] : '',
            'memory_limit' => ini_get('memory_limit'),
            'max_execution_time' => ini_get('max_execution_time'),
            'upload_max_filesize' => ini_get('upload_max_filesize'),
            'post_max_size' => ini_get('post_max_size'),
            'active_plugins_count' => count(get_option('active_plugins', array())),
            'theme' => get_option('stylesheet'),
            'site_url' => site_url(),
            'home_url' => home_url(),
        );
    }

    /**
     * 清除缓存
     */
    private function cmd_clear_cache($params) {
        // 清除对象缓存
        if (function_exists('wp_cache_flush')) {
            wp_cache_flush();
        }

        // 清除瞬态
        global $wpdb;
        $wpdb->query("DELETE FROM $wpdb->options WHERE option_name LIKE '_transient_%'");
        $wpdb->query("DELETE FROM $wpdb->options WHERE option_name LIKE '_site_transient_%'");

        return array('success' => true, 'message' => 'Cache cleared');
    }

    /**
     * 健康检查
     */
    private function cmd_health_check($params) {
        $checks = array();

        // PHP版本检查
        $checks['php_version'] = array(
            'status' => version_compare(phpversion(), '7.4', '>=') ? 'good' : 'warning',
            'message' => 'PHP ' . phpversion(),
        );

        // WordPress版本检查
        $checks['wp_version'] = array(
            'status' => 'good',
            'message' => 'WordPress ' . get_bloginfo('version'),
        );

        // 数据库连接检查
        $checks['database'] = array(
            'status' => $GLOBALS['wpdb']->check_connection() ? 'good' : 'error',
            'message' => 'Database connection',
        );

        // 插件连接状态
        $checks['relay_connection'] = array(
            'status' => $this->websocket_client->is_connected() ? 'good' : 'warning',
            'message' => 'Relay server connection',
        );

        // 计算总体状态
        $overall = 'good';
        foreach ($checks as $check) {
            if ($check['status'] === 'error') {
                $overall = 'error';
                break;
            } elseif ($check['status'] === 'warning') {
                $overall = 'warning';
            }
        }

        return array(
            'overall' => $overall,
            'checks' => $checks,
        );
    }

    // ===== 辅助方法 =====

    /**
     * 发送错误响应
     */
    private function send_error_response($command_id, $error_message) {
        $this->websocket_client->send_response(
            $command_id,
            false,
            array(),
            $error_message
        );
    }
}
