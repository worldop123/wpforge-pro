<?php
/**
 * API类 - REST API路由
 */

// 防止直接访问
if (!defined('ABSPATH')) {
    exit;
}

class WPForge_API {
    
    /**
     * 命名空间
     */
    private $namespace = 'wpforge/v1';
    
    /**
     * 注册路由
     */
    public function register_routes() {
        // 产品导入
        register_rest_route($this->namespace, '/products/import', array(
            'methods' => 'POST',
            'callback' => array($this, 'import_products'),
            'permission_callback' => array($this, 'check_permission'),
        ));
        
        // 获取产品分类
        register_rest_route($this->namespace, '/categories', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_categories'),
            'permission_callback' => array($this, 'check_permission'),
        ));
        
        // 创建产品分类
        register_rest_route($this->namespace, '/categories', array(
            'methods' => 'POST',
            'callback' => array($this, 'create_category'),
            'permission_callback' => array($this, 'check_permission'),
        ));
        
        // 站点健康检查
        register_rest_route($this->namespace, '/site/health', array(
            'methods' => 'GET',
            'callback' => array($this, 'site_health_check'),
            'permission_callback' => array($this, 'check_permission'),
        ));
        
        // 测试连接
        register_rest_route($this->namespace, '/site/test', array(
            'methods' => 'GET',
            'callback' => array($this, 'test_connection'),
            'permission_callback' => array($this, 'check_permission'),
        ));
        
        // SEO分析
        register_rest_route($this->namespace, '/seo/analyze/(?P<id>\d+)', array(
            'methods' => 'GET',
            'callback' => array($this, 'analyze_seo'),
            'permission_callback' => array($this, 'check_permission'),
        ));
        
        // 速度优化建议
        register_rest_route($this->namespace, '/speed/suggestions', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_speed_suggestions'),
            'permission_callback' => array($this, 'check_permission'),
        ));
        
        // 数据库优化
        register_rest_route($this->namespace, '/database/optimize', array(
            'methods' => 'POST',
            'callback' => array($this, 'optimize_database'),
            'permission_callback' => array($this, 'check_permission'),
        ));
        
        // 获取导入日志
        register_rest_route($this->namespace, '/import/logs', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_import_logs'),
            'permission_callback' => array($this, 'check_permission'),
        ));
    }
    
    /**
     * 权限检查
     *
     * 允许两种访问方式：
     * 1. 已登录的管理员用户（通过 WP REST nonce 验证，用于后台管理页面）
     * 2. 携带有效 API 密钥的请求（用于外部 API 调用）
     */
    public function check_permission() {
        // 优先检查已登录的管理员用户（后台页面调用）
        if (is_user_logged_in() && current_user_can('manage_options')) {
            return true;
        }

        // 检查API密钥（外部调用）
        $api_key = get_option('wpforge_api_key', '');

        if (!$api_key) {
            return new WP_Error('no_api_key', __('API密钥未配置', 'wpforge'), array('status' => 403));
        }

        $request_key = isset($_SERVER['HTTP_X_WPFORGE_API_KEY']) ? $_SERVER['HTTP_X_WPFORGE_API_KEY'] : '';

        if (!$request_key || $request_key !== $api_key) {
            return new WP_Error('invalid_api_key', __('无效的API密钥', 'wpforge'), array('status' => 403));
        }

        return true;
    }
    
    /**
     * 导入产品
     */
    public function import_products($request) {
        $params = $request->get_json_params();
        
        if (!isset($params['products']) || !is_array($params['products'])) {
            return new WP_Error('invalid_params', __('无效的产品数据', 'wpforge'), array('status' => 400));
        }
        
        $options = isset($params['options']) ? $params['options'] : array();
        
        $importer = new WPForge_Product_Importer();
        $results = $importer->import_products($params['products'], $options);
        
        // 记录日志
        $this->log_import($results, isset($params['task_id']) ? $params['task_id'] : '');
        
        return rest_ensure_response($results);
    }
    
    /**
     * 获取产品分类
     */
    public function get_categories($request) {
        $importer = new WPForge_Product_Importer();
        $categories = $importer->get_categories();
        
        return rest_ensure_response(array(
            'total' => count($categories),
            'categories' => $categories
        ));
    }
    
    /**
     * 创建产品分类
     */
    public function create_category($request) {
        $params = $request->get_json_params();
        
        if (!isset($params['name'])) {
            return new WP_Error('invalid_params', __('分类名称不能为空', 'wpforge'), array('status' => 400));
        }
        
        $importer = new WPForge_Product_Importer();
        $category_id = $importer->create_category(
            $params['name'],
            isset($params['parent']) ? $params['parent'] : 0
        );
        
        if (!$category_id) {
            return new WP_Error('create_failed', __('创建分类失败', 'wpforge'), array('status' => 500));
        }
        
        return rest_ensure_response(array(
            'success' => true,
            'category_id' => $category_id,
            'name' => $params['name']
        ));
    }
    
    /**
     * 站点健康检查
     */
    public function site_health_check($request) {
        $checks = array();
        
        // WordPress版本
        $checks['wordpress_version'] = array(
            'value' => get_bloginfo('version'),
            'status' => version_compare(get_bloginfo('version'), '5.0', '>=') ? 'pass' : 'fail',
            'message' => __('WordPress版本', 'wpforge')
        );
        
        // PHP版本
        $checks['php_version'] = array(
            'value' => phpversion(),
            'status' => version_compare(phpversion(), '7.4', '>=') ? 'pass' : 'fail',
            'message' => __('PHP版本', 'wpforge')
        );
        
        // WooCommerce
        $checks['woocommerce'] = array(
            'value' => class_exists('WooCommerce') ? WC()->version : '未安装',
            'status' => class_exists('WooCommerce') ? 'pass' : 'fail',
            'message' => __('WooCommerce', 'wpforge')
        );
        
        // 内存限制
        $memory_limit = ini_get('memory_limit');
        $checks['memory_limit'] = array(
            'value' => $memory_limit,
            'status' => $this->return_bytes($memory_limit) >= 128 * 1024 * 1024 ? 'pass' : 'warning',
            'message' => __('内存限制', 'wpforge')
        );
        
        // 最大执行时间
        $checks['max_execution_time'] = array(
            'value' => ini_get('max_execution_time') . 's',
            'status' => ini_get('max_execution_time') >= 30 ? 'pass' : 'warning',
            'message' => __('最大执行时间', 'wpforge')
        );
        
        // 上传大小限制
        $upload_max = ini_get('upload_max_filesize');
        $checks['upload_max_filesize'] = array(
            'value' => $upload_max,
            'status' => $this->return_bytes($upload_max) >= 32 * 1024 * 1024 ? 'pass' : 'warning',
            'message' => __('上传大小限制', 'wpforge')
        );
        
        // 计算总体状态
        $pass_count = 0;
        foreach ($checks as $check) {
            if ($check['status'] === 'pass') {
                $pass_count++;
            }
        }
        
        $overall_status = $pass_count === count($checks) ? 'good' : ($pass_count >= count($checks) * 0.7 ? 'ok' : 'poor');
        
        return rest_ensure_response(array(
            'overall_status' => $overall_status,
            'checks' => $checks,
            'site_url' => get_site_url(),
            'home_url' => home_url()
        ));
    }
    
    /**
     * 测试连接
     */
    public function test_connection($request) {
        return rest_ensure_response(array(
            'success' => true,
            'message' => __('连接成功', 'wpforge'),
            'site_name' => get_bloginfo('name'),
            'wp_version' => get_bloginfo('version'),
            'plugin_version' => WPFORGE_VERSION
        ));
    }
    
    /**
     * SEO分析
     */
    public function analyze_seo($request) {
        $post_id = $request->get_param('id');
        
        $seo = new WPForge_SEO();
        $analysis = $seo->analyze_seo($post_id);
        
        if (is_wp_error($analysis)) {
            return $analysis;
        }
        
        return rest_ensure_response($analysis);
    }
    
    /**
     * 获取速度优化建议
     */
    public function get_speed_suggestions($request) {
        $speed = new WPForge_Speed();
        $suggestions = $speed->get_optimization_suggestions();
        $performance_data = $speed->get_performance_data();
        
        return rest_ensure_response(array(
            'suggestions' => $suggestions,
            'performance' => $performance_data
        ));
    }
    
    /**
     * 优化数据库
     */
    public function optimize_database($request) {
        $speed = new WPForge_Speed();
        $results = $speed->optimize_database();
        
        return rest_ensure_response(array(
            'success' => true,
            'results' => $results
        ));
    }
    
    /**
     * 获取导入日志
     */
    public function get_import_logs($request) {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'wpforge_import_logs';
        
        $page = $request->get_param('page') ? intval($request->get_param('page')) : 1;
        $per_page = $request->get_param('per_page') ? intval($request->get_param('per_page')) : 20;
        $offset = ($page - 1) * $per_page;
        
        $logs = $wpdb->get_results(
            $wpdb->prepare(
                "SELECT * FROM $table_name ORDER BY created_at DESC LIMIT %d OFFSET %d",
                $per_page,
                $offset
            ),
            ARRAY_A
        );
        
        $total = $wpdb->get_var("SELECT COUNT(*) FROM $table_name");
        
        return rest_ensure_response(array(
            'total' => intval($total),
            'page' => $page,
            'per_page' => $per_page,
            'logs' => $logs
        ));
    }
    
    /**
     * 记录导入日志
     */
    private function log_import($results, $task_id = '') {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'wpforge_import_logs';
        
        $wpdb->insert(
            $table_name,
            array(
                'task_id' => $task_id ? $task_id : uniqid('wpforge_'),
                'type' => 'products',
                'status' => $results['failed'] > 0 ? 'partial' : 'completed',
                'total' => $results['total'],
                'success' => $results['success'],
                'failed' => $results['failed'],
                'skipped' => $results['skipped'],
                'errors' => !empty($results['errors']) ? json_encode($results['errors']) : null,
            ),
            array('%s', '%s', '%s', '%d', '%d', '%d', '%d', '%s')
        );
    }
    
    /**
     * 转换内存大小为字节
     */
    private function return_bytes($val) {
        $val = trim($val);
        $last = strtolower($val[strlen($val)-1]);
        $val = intval($val);
        
        switch($last) {
            case 'g':
                $val *= 1024;
            case 'm':
                $val *= 1024;
            case 'k':
                $val *= 1024;
        }
        
        return $val;
    }
}
