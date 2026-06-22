<?php
/**
 * WPForge Theme - Funnel Data Processor
 *
 * 电商漏斗数据处理器
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

// Exit if accessed directly.
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Funnel_Data_Processor 类
 *
 * 负责处理和聚合电商漏斗数据
 *
 * @since 1.0.0
 */
class Funnel_Data_Processor {

    /**
     * 单例实例
     *
     * @since 1.0.0
     * @var Funnel_Data_Processor|null
     */
    private static $instance = null;

    /**
     * 获取单例实例
     *
     * @since 1.0.0
     * @return Funnel_Data_Processor
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
        // 构造函数留空
    }

    /**
     * 每日数据聚合
     *
     * @since 1.0.0
     */
    public function daily_aggregate() {
        $yesterday = date('Y-m-d', strtotime('-1 day'));
        $this->aggregate_day($yesterday);
        $this->aggregate_products_day($yesterday);
    }

    /**
     * 聚合某一天的数据
     *
     * @since 1.0.0
     * @param string $date 日期
     */
    public function aggregate_day($date) {
        global $wpdb;

        $collector = wpforge_funnel_dashboard()->collector;
        $data = $collector->get_funnel_data($date, $date);

        $table_daily = $wpdb->prefix . 'wpforge_funnel_daily';

        // 检查是否已存在
        $exists = $wpdb->get_var($wpdb->prepare(
            "SELECT id FROM {$table_daily} WHERE stat_date = %s",
            $date
        ));

        if ($exists) {
            // 更新
            $wpdb->update(
                $table_daily,
                array(
                    'visitors'           => $data['visitors'],
                    'product_views'      => $data['product_views'],
                    'add_to_cart'        => $data['add_to_cart'],
                    'checkout_starts'    => $data['checkout_starts'],
                    'purchases'          => $data['purchases'],
                    'orders'             => $data['orders'],
                    'revenue'            => $data['revenue'],
                    'avg_order_value'    => $data['avg_order_value'],
                    'conversion_rate'    => $data['conversion_rate'],
                    'avg_items_per_order' => $data['orders'] > 0 ? $this->get_avg_items_per_order($date) : 0,
                ),
                array('stat_date' => $date),
                array('%d', '%d', '%d', '%d', '%d', '%d', '%f', '%f', '%f', '%f'),
                array('%s')
            );
        } else {
            // 插入
            $wpdb->insert(
                $table_daily,
                array(
                    'stat_date'          => $date,
                    'visitors'           => $data['visitors'],
                    'product_views'      => $data['product_views'],
                    'add_to_cart'        => $data['add_to_cart'],
                    'checkout_starts'    => $data['checkout_starts'],
                    'purchases'          => $data['purchases'],
                    'orders'             => $data['orders'],
                    'revenue'            => $data['revenue'],
                    'avg_order_value'    => $data['avg_order_value'],
                    'conversion_rate'    => $data['conversion_rate'],
                    'avg_items_per_order' => $data['orders'] > 0 ? $this->get_avg_items_per_order($date) : 0,
                ),
                array('%s', '%d', '%d', '%d', '%d', '%d', '%d', '%f', '%f', '%f', '%f')
            );
        }
    }

    /**
     * 获取平均每订单商品数
     *
     * @since 1.0.0
     * @param string $date 日期
     * @return float
     */
    private function get_avg_items_per_order($date) {
        global $wpdb;

        $table_purchases = $wpdb->prefix . 'wpforge_funnel_purchases';

        $result = $wpdb->get_row($wpdb->prepare(
            "SELECT AVG(item_count) as avg_items, COUNT(*) as orders FROM {$table_purchases} WHERE event_date = %s",
            $date
        ));

        return $result && $result->orders > 0 ? round((float) $result->avg_items, 2) : 0;
    }

    /**
     * 聚合某一天的产品数据
     *
     * @since 1.0.0
     * @param string $date 日期
     */
    public function aggregate_products_day($date) {
        global $wpdb;

        $table_visits = $wpdb->prefix . 'wpforge_funnel_visits';
        $table_cart = $wpdb->prefix . 'wpforge_funnel_cart_events';
        $table_purchases = $wpdb->prefix . 'wpforge_funnel_purchases';
        $table_product_stats = $wpdb->prefix . 'wpforge_funnel_product_stats';

        // 获取所有有浏览记录的产品
        $products = $wpdb->get_col($wpdb->prepare(
            "SELECT DISTINCT product_id FROM {$table_visits} WHERE visit_date = %s AND product_id IS NOT NULL",
            $date
        ));

        // 加上有加购记录的产品
        $cart_products = $wpdb->get_col($wpdb->prepare(
            "SELECT DISTINCT product_id FROM {$table_cart} WHERE event_date = %s",
            $date
        ));

        $products = array_unique(array_merge($products, $cart_products));

        foreach ($products as $product_id) {
            if (!$product_id) {
                continue;
            }

            // 浏览量
            $views = $wpdb->get_var($wpdb->prepare(
                "SELECT COUNT(*) FROM {$table_visits} WHERE visit_date = %s AND product_id = %d",
                $date,
                $product_id
            ));

            // 加购数
            $add_to_cart = $wpdb->get_var($wpdb->prepare(
                "SELECT COUNT(*) FROM {$table_cart} WHERE event_date = %s AND product_id = %d",
                $date,
                $product_id
            ));

            // 购买数和销售额（从订单中获取）
            $purchases = 0;
            $revenue = 0;

            // 检查是否存在
            $exists = $wpdb->get_var($wpdb->prepare(
                "SELECT id FROM {$table_product_stats} WHERE stat_date = %s AND product_id = %d",
                $date,
                $product_id
            ));

            $abandonment_rate = $add_to_cart > 0 ? round((($add_to_cart - $purchases) / $add_to_cart) * 100, 2) : 0;

            if ($exists) {
                $wpdb->update(
                    $table_product_stats,
                    array(
                        'views'             => $views,
                        'add_to_cart'       => $add_to_cart,
                        'purchases'         => $purchases,
                        'revenue'           => $revenue,
                        'abandonment_rate'  => $abandonment_rate,
                    ),
                    array('stat_date' => $date, 'product_id' => $product_id),
                    array('%d', '%d', '%d', '%f', '%f'),
                    array('%s', '%d')
                );
            } else {
                $wpdb->insert(
                    $table_product_stats,
                    array(
                        'stat_date'         => $date,
                        'product_id'        => $product_id,
                        'views'             => $views,
                        'add_to_cart'       => $add_to_cart,
                        'purchases'         => $purchases,
                        'revenue'           => $revenue,
                        'abandonment_rate'  => $abandonment_rate,
                    ),
                    array('%s', '%d', '%d', '%d', '%d', '%f', '%f')
                );
            }
        }
    }

    /**
     * 获取销售趋势数据
     *
     * @since 1.0.0
     * @param string $start_date 开始日期
     * @param string $end_date 结束日期
     * @param string $period 周期：day/week/month
     * @return array
     */
    public function get_sales_trend($start_date, $end_date, $period = 'day') {
        global $wpdb;

        $table_daily = $wpdb->prefix . 'wpforge_funnel_daily';

        $results = $wpdb->get_results($wpdb->prepare(
            "SELECT stat_date, revenue, orders, conversion_rate 
             FROM {$table_daily} 
             WHERE stat_date BETWEEN %s AND %s 
             ORDER BY stat_date ASC",
            $start_date,
            $end_date
        ));

        $labels = array();
        $revenue_data = array();
        $orders_data = array();
        $conversion_data = array();

        foreach ($results as $row) {
            $labels[] = date('m-d', strtotime($row->stat_date));
            $revenue_data[] = (float) $row->revenue;
            $orders_data[] = (int) $row->orders;
            $conversion_data[] = (float) $row->conversion_rate;
        }

        return array(
            'labels'      => $labels,
            'revenue'     => $revenue_data,
            'orders'      => $orders_data,
            'conversion'  => $conversion_data,
        );
    }

    /**
     * 获取热销产品排行
     *
     * @since 1.0.0
     * @param string $start_date 开始日期
     * @param string $end_date 结束日期
     * @param int $limit 数量限制
     * @param string $order_by 排序方式
     * @return array
     */
    public function get_top_products($start_date, $end_date, $limit = 10, $order_by = 'sales') {
        global $wpdb;

        $table_product_stats = $wpdb->prefix . 'wpforge_funnel_product_stats';

        $order_field = 'purchases';
        if ($order_by === 'revenue') {
            $order_field = 'revenue';
        } elseif ($order_by === 'views') {
            $order_field = 'views';
        } elseif ($order_by === 'add_to_cart') {
            $order_field = 'add_to_cart';
        }

        $results = $wpdb->get_results($wpdb->prepare(
            "SELECT product_id, SUM(views) as views, SUM(add_to_cart) as add_to_cart, 
                    SUM(purchases) as purchases, SUM(revenue) as revenue
             FROM {$table_product_stats}
             WHERE stat_date BETWEEN %s AND %s
             GROUP BY product_id
             ORDER BY {$order_field} DESC
             LIMIT %d",
            $start_date,
            $end_date,
            $limit
        ));

        $products = array();
        foreach ($results as $row) {
            $product = wc_get_product($row->product_id);
            if (!$product) {
                continue;
            }

            $products[] = array(
                'id'           => $row->product_id,
                'name'         => $product->get_name(),
                'image'        => get_the_post_thumbnail_url($row->product_id, 'thumbnail'),
                'views'        => (int) $row->views,
                'add_to_cart'  => (int) $row->add_to_cart,
                'purchases'    => (int) $row->purchases,
                'revenue'      => (float) $row->revenue,
                'edit_url'     => get_edit_post_link($row->product_id),
            );
        }

        return $products;
    }

    /**
     * 获取流量来源分析
     *
     * @since 1.0.0
     * @param string $start_date 开始日期
     * @param string $end_date 结束日期
     * @return array
     */
    public function get_traffic_sources($start_date, $end_date) {
        global $wpdb;

        $table_visits = $wpdb->prefix . 'wpforge_funnel_visits';

        $results = $wpdb->get_results($wpdb->prepare(
            "SELECT source, COUNT(DISTINCT visitor_id) as visitors
             FROM {$table_visits}
             WHERE visit_date BETWEEN %s AND %s
             GROUP BY source
             ORDER BY visitors DESC",
            $start_date,
            $end_date
        ));

        $sources = array(
            'direct'   => array('label' => __('直接访问', 'wpforge-theme'), 'visitors' => 0, 'color' => '#3b82f6'),
            'search'   => array('label' => __('搜索引擎', 'wpforge-theme'), 'visitors' => 0, 'color' => '#10b981'),
            'social'   => array('label' => __('社交媒体', 'wpforge-theme'), 'visitors' => 0, 'color' => '#f59e0b'),
            'referral' => array('label' => __('推荐链接', 'wpforge-theme'), 'visitors' => 0, 'color' => '#8b5cf6'),
            'email'    => array('label' => __('邮件营销', 'wpforge-theme'), 'visitors' => 0, 'color' => '#ef4444'),
        );

        $total = 0;
        foreach ($results as $row) {
            if (isset($sources[$row->source])) {
                $sources[$row->source]['visitors'] = (int) $row->visitors;
                $total += (int) $row->visitors;
            }
        }

        // 计算百分比
        foreach ($sources as &$source) {
            $source['percentage'] = $total > 0 ? round(($source['visitors'] / $total) * 100, 1) : 0;
        }

        return $sources;
    }

    /**
     * 获取设备类型分布
     *
     * @since 1.0.0
     * @param string $start_date 开始日期
     * @param string $end_date 结束日期
     * @return array
     */
    public function get_device_distribution($start_date, $end_date) {
        global $wpdb;

        $table_visits = $wpdb->prefix . 'wpforge_funnel_visits';

        $results = $wpdb->get_results($wpdb->prepare(
            "SELECT device_type, COUNT(DISTINCT visitor_id) as visitors
             FROM {$table_visits}
             WHERE visit_date BETWEEN %s AND %s
             GROUP BY device_type",
            $start_date,
            $end_date
        ));

        $devices = array(
            'desktop' => array('label' => __('桌面端', 'wpforge-theme'), 'visitors' => 0, 'color' => '#3b82f6'),
            'mobile'  => array('label' => __('移动端', 'wpforge-theme'), 'visitors' => 0, 'color' => '#10b981'),
            'tablet'  => array('label' => __('平板', 'wpforge-theme'), 'visitors' => 0, 'color' => '#f59e0b'),
        );

        $total = 0;
        foreach ($results as $row) {
            if (isset($devices[$row->device_type])) {
                $devices[$row->device_type]['visitors'] = (int) $row->visitors;
                $total += (int) $row->visitors;
            }
        }

        // 计算百分比
        foreach ($devices as &$device) {
            $device['percentage'] = $total > 0 ? round(($device['visitors'] / $total) * 100, 1) : 0;
        }

        return $devices;
    }

    /**
     * 获取环比数据
     *
     * @since 1.0.0
     * @param string $start_date 开始日期
     * @param string $end_date 结束日期
     * @return array
     */
    public function get_comparison_data($start_date, $end_date) {
        $current_data = wpforge_funnel_dashboard()->collector->get_funnel_data($start_date, $end_date);

        // 计算上一周期的日期
        $days = (strtotime($end_date) - strtotime($start_date)) / 86400 + 1;
        $prev_end = date('Y-m-d', strtotime($start_date) - 86400);
        $prev_start = date('Y-m-d', strtotime($prev_end) - ($days - 1) * 86400);

        $previous_data = wpforge_funnel_dashboard()->collector->get_funnel_data($prev_start, $prev_end);

        $comparison = array();
        $metrics = array('visitors', 'product_views', 'add_to_cart', 'checkout_starts', 'purchases', 'orders', 'revenue', 'conversion_rate');

        foreach ($metrics as $metric) {
            $current = isset($current_data[$metric]) ? $current_data[$metric] : 0;
            $previous = isset($previous_data[$metric]) ? $previous_data[$metric] : 0;

            if ($previous > 0) {
                $change = round((($current - $previous) / $previous) * 100, 1);
            } else {
                $change = $current > 0 ? 100 : 0;
            }

            $comparison[$metric] = array(
                'current'   => $current,
                'previous'  => $previous,
                'change'    => $change,
                'direction' => $change >= 0 ? 'up' : 'down',
            );
        }

        return $comparison;
    }
}
