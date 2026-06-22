<?php
/**
 * WPForge Theme - Funnel Insights Engine
 *
 * 电商漏斗AI洞察引擎
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

// Exit if accessed directly.
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Funnel_Insights_Engine 类
 *
 * 负责生成智能洞察和优化建议
 *
 * @since 1.0.0
 */
class Funnel_Insights_Engine {

    /**
     * 单例实例
     *
     * @since 1.0.0
     * @var Funnel_Insights_Engine|null
     */
    private static $instance = null;

    /**
     * 获取单例实例
     *
     * @since 1.0.0
     * @return Funnel_Insights_Engine
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
     * 生成所有洞察
     *
     * @since 1.0.0
     * @param string $start_date 开始日期
     * @param string $end_date 结束日期
     * @return array
     */
    public function generate_insights($start_date, $end_date) {
        $insights = array();

        // 获取对比数据
        $comparison = wpforge_funnel_dashboard()->processor->get_comparison_data($start_date, $end_date);

        // 1. 转化率异常检测
        $conversion_insights = $this->analyze_conversion_rate($comparison);
        $insights = array_merge($insights, $conversion_insights);

        // 2. 销售额趋势分析
        $revenue_insights = $this->analyze_revenue_trend($comparison);
        $insights = array_merge($insights, $revenue_insights);

        // 3. 漏斗各环节分析
        $funnel_insights = $this->analyze_funnel_stages($comparison);
        $insights = array_merge($insights, $funnel_insights);

        // 4. 流量来源分析
        $traffic_insights = $this->analyze_traffic_sources($start_date, $end_date);
        $insights = array_merge($insights, $traffic_insights);

        // 5. 设备类型分析
        $device_insights = $this->analyze_device_performance($start_date, $end_date);
        $insights = array_merge($insights, $device_insights);

        // 按优先级排序
        usort($insights, function($a, $b) {
            $priority_order = array('critical' => 0, 'high' => 1, 'medium' => 2, 'low' => 3);
            return $priority_order[$a['priority']] - $priority_order[$b['priority']];
        });

        return $insights;
    }

    /**
     * 分析转化率
     *
     * @since 1.0.0
     * @param array $comparison 对比数据
     * @return array
     */
    private function analyze_conversion_rate($comparison) {
        $insights = array();

        if (!isset($comparison['conversion_rate'])) {
            return $insights;
        }

        $conv = $comparison['conversion_rate'];
        $current_rate = $conv['current'];
        $change = $conv['change'];

        // 转化率过低警告
        if ($current_rate < 1) {
            $insights[] = array(
                'type'        => 'warning',
                'icon'        => '⚠️',
                'title'       => __('转化率偏低', 'wpforge-theme'),
                'description' => sprintf(__('当前整体转化率为 %.2f%%，低于行业平均水平（2-3%%）。建议优化产品页面和结账流程。', 'wpforge-theme'), $current_rate),
                'data'        => sprintf(__('当前转化率：%.2f%%', 'wpforge-theme'), $current_rate),
                'action'      => __('优化产品描述、添加用户评价、简化结账流程', 'wpforge-theme'),
                'priority'    => 'high',
                'impact'      => __('预计可提升转化率 30-50%', 'wpforge-theme'),
            );
        }

        // 转化率大幅下降
        if ($change < -20) {
            $insights[] = array(
                'type'        => 'warning',
                'icon'        => '⚠️',
                'title'       => __('转化率大幅下降', 'wpforge-theme'),
                'description' => sprintf(__('转化率较上一周期下降了 %.1f%%，请检查是否有技术问题或流量质量变化。', 'wpforge-theme'), abs($change)),
                'data'        => sprintf(__('下降幅度：%.1f%%', 'wpforge-theme'), abs($change)),
                'action'      => __('检查网站可用性、支付网关状态、流量来源变化', 'wpforge-theme'),
                'priority'    => 'critical',
                'impact'      => __('立即排查问题', 'wpforge-theme'),
            );
        }

        // 转化率提升
        if ($change > 10) {
            $insights[] = array(
                'type'        => 'success',
                'icon'        => '📈',
                'title'       => __('转化率显著提升', 'wpforge-theme'),
                'description' => sprintf(__('转化率较上一周期提升了 %.1f%%，表现优秀！', 'wpforge-theme'), $change),
                'data'        => sprintf(__('提升幅度：%.1f%%', 'wpforge-theme'), $change),
                'action'      => __('继续保持当前优化策略，分析成功原因并推广', 'wpforge-theme'),
                'priority'    => 'low',
                'impact'      => __('继续保持', 'wpforge-theme'),
            );
        }

        return $insights;
    }

    /**
     * 分析销售额趋势
     *
     * @since 1.0.0
     * @param array $comparison 对比数据
     * @return array
     */
    private function analyze_revenue_trend($comparison) {
        $insights = array();

        if (!isset($comparison['revenue'])) {
            return $insights;
        }

        $revenue = $comparison['revenue'];
        $change = $revenue['change'];

        // 销售额大幅下降
        if ($change < -30) {
            $insights[] = array(
                'type'        => 'warning',
                'icon'        => '⚠️',
                'title'       => __('销售额大幅下滑', 'wpforge-theme'),
                'description' => sprintf(__('销售额较上一周期下降了 %.1f%%，需要立即关注。', 'wpforge-theme'), abs($change)),
                'data'        => sprintf(__('下降幅度：%.1f%%', 'wpforge-theme'), abs($change)),
                'action'      => __('检查流量、转化率、客单价变化，推出促销活动', 'wpforge-theme'),
                'priority'    => 'critical',
                'impact'      => __('立即采取行动', 'wpforge-theme'),
            );
        }

        // 销售额增长
        if ($change > 20) {
            $insights[] = array(
                'type'        => 'success',
                'icon'        => '📈',
                'title'       => __('销售额强劲增长', 'wpforge-theme'),
                'description' => sprintf(__('销售额较上一周期增长了 %.1f%%，增长势头良好！', 'wpforge-theme'), $change),
                'data'        => sprintf(__('增长幅度：%.1f%%', 'wpforge-theme'), $change),
                'action'      => __('分析增长来源，加大投入，乘胜追击', 'wpforge-theme'),
                'priority'    => 'low',
                'impact'      => __('继续保持增长', 'wpforge-theme'),
            );
        }

        // 客单价分析
        if (isset($comparison['orders']) && isset($comparison['revenue'])) {
            $current_aov = $comparison['revenue']['current'] / max($comparison['orders']['current'], 1);
            $prev_aov = $comparison['revenue']['previous'] / max($comparison['orders']['previous'], 1);

            if ($current_aov > $prev_aov * 1.1) {
                $insights[] = array(
                    'type'        => 'success',
                    'icon'        => '💡',
                    'title'       => __('客单价提升', 'wpforge-theme'),
                    'description' => __('客单价有所提升，交叉销售和追加销售策略见效。', 'wpforge-theme'),
                    'data'        => sprintf(__('当前客单价：¥%.2f', 'wpforge-theme'), $current_aov),
                    'action'      => __('继续优化相关产品推荐，设置满减门槛', 'wpforge-theme'),
                    'priority'    => 'medium',
                    'impact'      => __('预计可继续提升 10-15%', 'wpforge-theme'),
                );
            }
        }

        return $insights;
    }

    /**
     * 分析漏斗各环节
     *
     * @since 1.0.0
     * @param array $comparison 对比数据
     * @return array
     */
    private function analyze_funnel_stages($comparison) {
        $insights = array();

        if (!isset($comparison['visitors']) || !isset($comparison['purchases'])) {
            return $insights;
        }

        $visitors = $comparison['visitors']['current'];
        $product_views = $comparison['product_views']['current'];
        $add_to_cart = $comparison['add_to_cart']['current'];
        $checkout_starts = $comparison['checkout_starts']['current'];
        $purchases = $comparison['purchases']['current'];

        // 计算各环节转化率
        $view_rate = $visitors > 0 ? ($product_views / $visitors) * 100 : 0;
        $cart_rate = $product_views > 0 ? ($add_to_cart / $product_views) * 100 : 0;
        $checkout_rate = $add_to_cart > 0 ? ($checkout_starts / $add_to_cart) * 100 : 0;
        $purchase_rate = $checkout_starts > 0 ? ($purchases / $checkout_starts) * 100 : 0;

        // 浏览产品转化率低
        if ($view_rate < 40 && $visitors > 100) {
            $insights[] = array(
                'type'        => 'optimization',
                'icon'        => '🔧',
                'title'       => __('产品浏览率偏低', 'wpforge-theme'),
                'description' => sprintf(__('只有 %.1f%% 的访客浏览了产品页面，建议优化首页和分类页的产品展示。', 'wpforge-theme'), $view_rate),
                'data'        => sprintf(__('浏览转化率：%.1f%%', 'wpforge-theme'), $view_rate),
                'action'      => __('优化首页产品推荐、改进分类导航、添加热门产品区块', 'wpforge-theme'),
                'priority'    => 'medium',
                'impact'      => __('预计可提升 20-30%', 'wpforge-theme'),
            );
        }

        // 加购转化率低
        if ($cart_rate < 5 && $product_views > 50) {
            $insights[] = array(
                'type'        => 'optimization',
                'icon'        => '🔧',
                'title'       => __('加购转化率偏低', 'wpforge-theme'),
                'description' => sprintf(__('只有 %.1f%% 的产品浏览者加入了购物车，建议优化产品详情页。', 'wpforge-theme'), $cart_rate),
                'data'        => sprintf(__('加购转化率：%.1f%%', 'wpforge-theme'), $cart_rate),
                'action'      => __('优化产品图片、添加用户评价、显示库存紧迫感、优化加购按钮', 'wpforge-theme'),
                'priority'    => 'high',
                'impact'      => __('预计可提升 30-50%', 'wpforge-theme'),
            );
        }

        // 结账转化率低
        if ($checkout_rate < 30 && $add_to_cart > 20) {
            $insights[] = array(
                'type'        => 'optimization',
                'icon'        => '🔧',
                'title'       => __('弃购率偏高', 'wpforge-theme'),
                'description' => sprintf(__('只有 %.1f%% 的加购用户进入了结账页面，购物车弃购率较高。', 'wpforge-theme'), $checkout_rate),
                'data'        => sprintf(__('结账转化率：%.1f%%', 'wpforge-theme'), $checkout_rate),
                'action'      => __('添加弃购挽回邮件、优化购物车页面、显示免运费门槛、添加信任徽章', 'wpforge-theme'),
                'priority'    => 'high',
                'impact'      => __('预计可挽回 15-25% 弃购', 'wpforge-theme'),
            );
        }

        // 购买完成率低
        if ($purchase_rate < 50 && $checkout_starts > 10) {
            $insights[] = array(
                'type'        => 'optimization',
                'icon'        => '🔧',
                'title'       => __('结账完成率偏低', 'wpforge-theme'),
                'description' => sprintf(__('只有 %.1f%% 的结账用户完成了购买，结账流程可能有问题。', 'wpforge-theme'), $purchase_rate),
                'data'        => sprintf(__('购买完成率：%.1f%%', 'wpforge-theme'), $purchase_rate),
                'action'      => __('简化结账流程、添加访客结账、优化支付方式、检查支付网关', 'wpforge-theme'),
                'priority'    => 'high',
                'impact'      => __('预计可提升 20-40%', 'wpforge-theme'),
            );
        }

        return $insights;
    }

    /**
     * 分析流量来源
     *
     * @since 1.0.0
     * @param string $start_date 开始日期
     * @param string $end_date 结束日期
     * @return array
     */
    private function analyze_traffic_sources($start_date, $end_date) {
        $insights = array();

        $sources = wpforge_funnel_dashboard()->processor->get_traffic_sources($start_date, $end_date);

        // 自然搜索占比低
        if (isset($sources['search']) && $sources['search']['percentage'] < 20) {
            $insights[] = array(
                'type'        => 'opportunity',
                'icon'        => '💡',
                'title'       => __('自然搜索流量潜力大', 'wpforge-theme'),
                'description' => sprintf(__('目前自然搜索流量仅占 %.1f%%，SEO优化空间很大。', 'wpforge-theme'), $sources['search']['percentage']),
                'data'        => sprintf(__('搜索流量占比：%.1f%%', 'wpforge-theme'), $sources['search']['percentage']),
                'action'      => __('优化产品页面SEO、创建博客内容、建设外链', 'wpforge-theme'),
                'priority'    => 'medium',
                'impact'      => __('长期可带来稳定免费流量', 'wpforge-theme'),
            );
        }

        // 社交媒体流量机会
        if (isset($sources['social']) && $sources['social']['percentage'] < 5) {
            $insights[] = array(
                'type'        => 'opportunity',
                'icon'        => '💡',
                'title'       => __('社交媒体流量待开发', 'wpforge-theme'),
                'description' => sprintf(__('社交媒体流量仅占 %.1f%%，可以加强社媒运营。', 'wpforge-theme'), $sources['social']['percentage']),
                'data'        => sprintf(__('社交流量占比：%.1f%%', 'wpforge-theme'), $sources['social']['percentage']),
                'action'      => __('创建Instagram/Facebook账号、发布产品内容、投放社交广告', 'wpforge-theme'),
                'priority'    => 'low',
                'impact'      => __('可拓展新的流量渠道', 'wpforge-theme'),
            );
        }

        // 直接访问占比高（品牌优势）
        if (isset($sources['direct']) && $sources['direct']['percentage'] > 40) {
            $insights[] = array(
                'type'        => 'success',
                'icon'        => '📈',
                'title'       => __('品牌认知度良好', 'wpforge-theme'),
                'description' => sprintf(__('直接访问流量占 %.1f%%，说明品牌已有一定认知度。', 'wpforge-theme'), $sources['direct']['percentage']),
                'data'        => sprintf(__('直接访问占比：%.1f%%', 'wpforge-theme'), $sources['direct']['percentage']),
                'action'      => __('继续加强品牌建设，推出会员计划，提高复购率', 'wpforge-theme'),
                'priority'    => 'low',
                'impact'      => __('继续保持品牌优势', 'wpforge-theme'),
            );
        }

        return $insights;
    }

    /**
     * 分析设备表现
     *
     * @since 1.0.0
     * @param string $start_date 开始日期
     * @param string $end_date 结束日期
     * @return array
     */
    private function analyze_device_performance($start_date, $end_date) {
        $insights = array();

        $devices = wpforge_funnel_dashboard()->processor->get_device_distribution($start_date, $end_date);

        // 移动端流量占比高
        if (isset($devices['mobile']) && $devices['mobile']['percentage'] > 50) {
            $insights[] = array(
                'type'        => 'info',
                'icon'        => '📱',
                'title'       => __('移动端流量为主', 'wpforge-theme'),
                'description' => sprintf(__('移动端流量占比 %.1f%%，移动体验至关重要。', 'wpforge-theme'), $devices['mobile']['percentage']),
                'data'        => sprintf(__('移动端占比：%.1f%%', 'wpforge-theme'), $devices['mobile']['percentage']),
                'action'      => __('确保移动端体验优秀、优化移动端结账流程、考虑APP化', 'wpforge-theme'),
                'priority'    => 'medium',
                'impact'      => __('提升移动端转化率', 'wpforge-theme'),
            );
        }

        // 桌面端流量占比高
        if (isset($devices['desktop']) && $devices['desktop']['percentage'] > 60) {
            $insights[] = array(
                'type'        => 'info',
                'icon'        => '💻',
                'title'       => __('桌面端流量为主', 'wpforge-theme'),
                'description' => sprintf(__('桌面端流量占比 %.1f%%，B端用户可能较多。', 'wpforge-theme'), $devices['desktop']['percentage']),
                'data'        => sprintf(__('桌面端占比：%.1f%%', 'wpforge-theme'), $devices['desktop']['percentage']),
                'action'      => __('优化桌面端体验、提供详细产品规格、考虑批发功能', 'wpforge-theme'),
                'priority'    => 'low',
                'impact'      => __('更好地服务桌面用户', 'wpforge-theme'),
            );
        }

        return $insights;
    }

    /**
     * 获取洞察摘要
     *
     * @since 1.0.0
     * @param array $insights 洞察列表
     * @return array
     */
    public function get_insights_summary($insights) {
        $summary = array(
            'total'     => count($insights),
            'critical'  => 0,
            'high'      => 0,
            'medium'    => 0,
            'low'       => 0,
            'warnings'  => 0,
            'successes' => 0,
            'opportunities' => 0,
            'optimizations' => 0,
        );

        foreach ($insights as $insight) {
            if (isset($summary[$insight['priority']])) {
                $summary[$insight['priority']]++;
            }

            $type_key = $insight['type'] . 's';
            if (isset($summary[$type_key])) {
                $summary[$type_key]++;
            }
        }

        return $summary;
    }
}
