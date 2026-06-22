<?php
/**
 * WPForge Theme - Funnel REST API
 *
 * 电商漏斗数据REST API
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

// Exit if accessed directly.
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Funnel_REST_API 类
 *
 * 提供电商漏斗数据的REST API端点
 *
 * @since 1.0.0
 */
class Funnel_REST_API {

    /**
     * 单例实例
     *
     * @since 1.0.0
     * @var Funnel_REST_API|null
     */
    private static $instance = null;

    /**
     * API命名空间
     *
     * @since 1.0.0
     * @var string
     */
    private $namespace = 'wpforge/v1';

    /**
     * 获取单例实例
     *
     * @since 1.0.0
     * @return Funnel_REST_API
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
        add_action('rest_api_init', array($this, 'register_routes'));
    }

    /**
     * 注册API路由
     *
     * @since 1.0.0
     */
    public function register_routes() {
        // 获取漏斗概览数据
        register_rest_route($this->namespace, '/funnel/overview', array(
            'methods'             => 'GET',
            'callback'            => array($this, 'get_overview'),
            'permission_callback' => array($this, 'check_permission'),
            'args'                => array(
                'start_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d', strtotime('-30 days')),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
                'end_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d'),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
            ),
        ));

        // 获取漏斗数据
        register_rest_route($this->namespace, '/funnel/data', array(
            'methods'             => 'GET',
            'callback'            => array($this, 'get_funnel_data'),
            'permission_callback' => array($this, 'check_permission'),
            'args'                => array(
                'start_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d', strtotime('-30 days')),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
                'end_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d'),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
            ),
        ));

        // 获取销售趋势
        register_rest_route($this->namespace, '/funnel/sales-trend', array(
            'methods'             => 'GET',
            'callback'            => array($this, 'get_sales_trend'),
            'permission_callback' => array($this, 'check_permission'),
            'args'                => array(
                'start_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d', strtotime('-30 days')),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
                'end_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d'),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
                'period' => array(
                    'required'          => false,
                    'default'           => 'day',
                    'sanitize_callback' => 'sanitize_text_field',
                    'enum'              => array('day', 'week', 'month'),
                ),
            ),
        ));

        // 获取热销产品
        register_rest_route($this->namespace, '/funnel/top-products', array(
            'methods'             => 'GET',
            'callback'            => array($this, 'get_top_products'),
            'permission_callback' => array($this, 'check_permission'),
            'args'                => array(
                'start_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d', strtotime('-30 days')),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
                'end_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d'),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
                'limit' => array(
                    'required'          => false,
                    'default'           => 10,
                    'sanitize_callback' => 'absint',
                ),
                'order_by' => array(
                    'required'          => false,
                    'default'           => 'sales',
                    'sanitize_callback' => 'sanitize_text_field',
                    'enum'              => array('sales', 'revenue', 'views', 'add_to_cart'),
                ),
            ),
        ));

        // 获取流量来源
        register_rest_route($this->namespace, '/funnel/traffic-sources', array(
            'methods'             => 'GET',
            'callback'            => array($this, 'get_traffic_sources'),
            'permission_callback' => array($this, 'check_permission'),
            'args'                => array(
                'start_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d', strtotime('-30 days')),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
                'end_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d'),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
            ),
        ));

        // 获取设备分布
        register_rest_route($this->namespace, '/funnel/device-distribution', array(
            'methods'             => 'GET',
            'callback'            => array($this, 'get_device_distribution'),
            'permission_callback' => array($this, 'check_permission'),
            'args'                => array(
                'start_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d', strtotime('-30 days')),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
                'end_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d'),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
            ),
        ));

        // 获取AI洞察
        register_rest_route($this->namespace, '/funnel/insights', array(
            'methods'             => 'GET',
            'callback'            => array($this, 'get_insights'),
            'permission_callback' => array($this, 'check_permission'),
            'args'                => array(
                'start_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d', strtotime('-30 days')),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
                'end_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d'),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
            ),
        ));

        // 获取对比数据
        register_rest_route($this->namespace, '/funnel/comparison', array(
            'methods'             => 'GET',
            'callback'            => array($this, 'get_comparison'),
            'permission_callback' => array($this, 'check_permission'),
            'args'                => array(
                'start_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d', strtotime('-30 days')),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
                'end_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d'),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
            ),
        ));

        // 导出数据
        register_rest_route($this->namespace, '/funnel/export', array(
            'methods'             => 'GET',
            'callback'            => array($this, 'export_data'),
            'permission_callback' => array($this, 'check_permission'),
            'args'                => array(
                'start_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d', strtotime('-30 days')),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
                'end_date' => array(
                    'required'          => false,
                    'default'           => date('Y-m-d'),
                    'sanitize_callback' => 'sanitize_text_field',
                ),
                'format' => array(
                    'required'          => false,
                    'default'           => 'csv',
                    'sanitize_callback' => 'sanitize_text_field',
                    'enum'              => array('csv', 'json'),
                ),
            ),
        ));
    }

    /**
     * 检查权限
     *
     * @since 1.0.0
     * @return bool
     */
    public function check_permission() {
        return current_user_can('manage_woocommerce');
    }

    /**
     * 获取概览数据
     *
     * @since 1.0.0
     * @param WP_REST_Request $request 请求对象
     * @return WP_REST_Response
     */
    public function get_overview($request) {
        $start_date = $request->get_param('start_date');
        $end_date = $request->get_param('end_date');

        $funnel_data = wpforge_funnel_dashboard()->collector->get_funnel_data($start_date, $end_date);
        $comparison = wpforge_funnel_dashboard()->processor->get_comparison_data($start_date, $end_date);

        return rest_ensure_response(array(
            'success'    => true,
            'data'       => $funnel_data,
            'comparison' => $comparison,
            'period'     => array(
                'start' => $start_date,
                'end'   => $end_date,
            ),
        ));
    }

    /**
     * 获取漏斗数据
     *
     * @since 1.0.0
     * @param WP_REST_Request $request 请求对象
     * @return WP_REST_Response
     */
    public function get_funnel_data($request) {
        $start_date = $request->get_param('start_date');
        $end_date = $request->get_param('end_date');

        $data = wpforge_funnel_dashboard()->collector->get_funnel_data($start_date, $end_date);

        // 构建漏斗层级
        $funnel_stages = array(
            array(
                'name'   => __('访客', 'wpforge-theme'),
                'value'  => $data['visitors'],
                'key'    => 'visitors',
                'color'  => '#3b82f6',
            ),
            array(
                'name'   => __('浏览产品', 'wpforge-theme'),
                'value'  => $data['product_views'],
                'key'    => 'product_views',
                'color'  => '#10b981',
                'conversion_from_prev' => $data['visitors'] > 0 ? round(($data['product_views'] / $data['visitors']) * 100, 2) : 0,
            ),
            array(
                'name'   => __('加入购物车', 'wpforge-theme'),
                'value'  => $data['add_to_cart'],
                'key'    => 'add_to_cart',
                'color'  => '#f59e0b',
                'conversion_from_prev' => $data['product_views'] > 0 ? round(($data['add_to_cart'] / $data['product_views']) * 100, 2) : 0,
            ),
            array(
                'name'   => __('开始结账', 'wpforge-theme'),
                'value'  => $data['checkout_starts'],
                'key'    => 'checkout_starts',
                'color'  => '#8b5cf6',
                'conversion_from_prev' => $data['add_to_cart'] > 0 ? round(($data['checkout_starts'] / $data['add_to_cart']) * 100, 2) : 0,
            ),
            array(
                'name'   => __('完成购买', 'wpforge-theme'),
                'value'  => $data['purchases'],
                'key'    => 'purchases',
                'color'  => '#ef4444',
                'conversion_from_prev' => $data['checkout_starts'] > 0 ? round(($data['purchases'] / $data['checkout_starts']) * 100, 2) : 0,
            ),
        );

        return rest_ensure_response(array(
            'success' => true,
            'data'    => array(
                'metrics' => $data,
                'stages'  => $funnel_stages,
            ),
        ));
    }

    /**
     * 获取销售趋势
     *
     * @since 1.0.0
     * @param WP_REST_Request $request 请求对象
     * @return WP_REST_Response
     */
    public function get_sales_trend($request) {
        $start_date = $request->get_param('start_date');
        $end_date = $request->get_param('end_date');
        $period = $request->get_param('period');

        $data = wpforge_funnel_dashboard()->processor->get_sales_trend($start_date, $end_date, $period);

        return rest_ensure_response(array(
            'success' => true,
            'data'    => $data,
        ));
    }

    /**
     * 获取热销产品
     *
     * @since 1.0.0
     * @param WP_REST_Request $request 请求对象
     * @return WP_REST_Response
     */
    public function get_top_products($request) {
        $start_date = $request->get_param('start_date');
        $end_date = $request->get_param('end_date');
        $limit = $request->get_param('limit');
        $order_by = $request->get_param('order_by');

        $products = wpforge_funnel_dashboard()->processor->get_top_products($start_date, $end_date, $limit, $order_by);

        return rest_ensure_response(array(
            'success' => true,
            'data'    => $products,
        ));
    }

    /**
     * 获取流量来源
     *
     * @since 1.0.0
     * @param WP_REST_Request $request 请求对象
     * @return WP_REST_Response
     */
    public function get_traffic_sources($request) {
        $start_date = $request->get_param('start_date');
        $end_date = $request->get_param('end_date');

        $sources = wpforge_funnel_dashboard()->processor->get_traffic_sources($start_date, $end_date);

        return rest_ensure_response(array(
            'success' => true,
            'data'    => $sources,
        ));
    }

    /**
     * 获取设备分布
     *
     * @since 1.0.0
     * @param WP_REST_Request $request 请求对象
     * @return WP_REST_Response
     */
    public function get_device_distribution($request) {
        $start_date = $request->get_param('start_date');
        $end_date = $request->get_param('end_date');

        $devices = wpforge_funnel_dashboard()->processor->get_device_distribution($start_date, $end_date);

        return rest_ensure_response(array(
            'success' => true,
            'data'    => $devices,
        ));
    }

    /**
     * 获取AI洞察
     *
     * @since 1.0.0
     * @param WP_REST_Request $request 请求对象
     * @return WP_REST_Response
     */
    public function get_insights($request) {
        $start_date = $request->get_param('start_date');
        $end_date = $request->get_param('end_date');

        $insights = wpforge_funnel_dashboard()->insights->generate_insights($start_date, $end_date);
        $summary = wpforge_funnel_dashboard()->insights->get_insights_summary($insights);

        return rest_ensure_response(array(
            'success' => true,
            'data'    => array(
                'insights' => $insights,
                'summary'  => $summary,
            ),
        ));
    }

    /**
     * 获取对比数据
     *
     * @since 1.0.0
     * @param WP_REST_Request $request 请求对象
     * @return WP_REST_Response
     */
    public function get_comparison($request) {
        $start_date = $request->get_param('start_date');
        $end_date = $request->get_param('end_date');

        $comparison = wpforge_funnel_dashboard()->processor->get_comparison_data($start_date, $end_date);

        return rest_ensure_response(array(
            'success' => true,
            'data'    => $comparison,
        ));
    }

    /**
     * 导出数据
     *
     * @since 1.0.0
     * @param WP_REST_Request $request 请求对象
     * @return WP_REST_Response
     */
    public function export_data($request) {
        $start_date = $request->get_param('start_date');
        $end_date = $request->get_param('end_date');
        $format = $request->get_param('format');

        $funnel_data = wpforge_funnel_dashboard()->collector->get_funnel_data($start_date, $end_date);
        $products = wpforge_funnel_dashboard()->processor->get_top_products($start_date, $end_date, 50, 'sales');
        $sources = wpforge_funnel_dashboard()->processor->get_traffic_sources($start_date, $end_date);

        $export_data = array(
            'period' => array(
                'start' => $start_date,
                'end'   => $end_date,
            ),
            'funnel_metrics' => $funnel_data,
            'top_products'   => $products,
            'traffic_sources' => $sources,
            'exported_at'    => current_time('mysql'),
        );

        if ($format === 'json') {
            return rest_ensure_response($export_data);
        }

        // CSV格式
        $csv = $this->generate_csv($export_data);

        header('Content-Type: text/csv; charset=utf-8');
        header('Content-Disposition: attachment; filename="wpforge-funnel-export-' . date('Y-m-d') . '.csv"');

        echo $csv;
        exit;
    }

    /**
     * 生成CSV
     *
     * @since 1.0.0
     * @param array $data 数据
     * @return string
     */
    private function generate_csv($data) {
        $output = '';

        // 漏斗指标
        $output .= "=== 漏斗指标 ===\n";
        $output .= "指标,数值\n";
        foreach ($data['funnel_metrics'] as $key => $value) {
            $output .= "{$key},{$value}\n";
        }
        $output .= "\n";

        // 热销产品
        $output .= "=== 热销产品 ===\n";
        $output .= "产品名称,浏览量,加购数,购买数,销售额\n";
        foreach ($data['top_products'] as $product) {
            $output .= "{$product['name']},{$product['views']},{$product['add_to_cart']},{$product['purchases']},{$product['revenue']}\n";
        }
        $output .= "\n";

        // 流量来源
        $output .= "=== 流量来源 ===\n";
        $output .= "来源,访客数,占比\n";
        foreach ($data['traffic_sources'] as $source) {
            $output .= "{$source['label']},{$source['visitors']},{$source['percentage']}%\n";
        }

        return $output;
    }
}
