<?php
/**
 * WPForge Theme - Funnel Dashboard Admin Page
 *
 * 电商漏斗数据面板后台页面
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

// Exit if accessed directly.
if (!defined('ABSPATH')) {
    exit;
}
?>

<div class="wrap wpforge-funnel-dashboard">
    <div class="funnel-header">
        <div class="funnel-header-left">
            <h1><?php esc_html_e('电商漏斗仪表盘', 'wpforge-theme'); ?></h1>
            <p class="description"><?php esc_html_e('实时监控您的电商转化漏斗，发现优化机会', 'wpforge-theme'); ?></p>
        </div>
        <div class="funnel-header-right">
            <div class="funnel-date-range">
                <select id="funnel-date-preset" class="funnel-select">
                    <option value="today"><?php esc_html_e('今天', 'wpforge-theme'); ?></option>
                    <option value="yesterday"><?php esc_html_e('昨天', 'wpforge-theme'); ?></option>
                    <option value="7days" selected><?php esc_html_e('最近7天', 'wpforge-theme'); ?></option>
                    <option value="30days"><?php esc_html_e('最近30天', 'wpforge-theme'); ?></option>
                    <option value="90days"><?php esc_html_e('最近90天', 'wpforge-theme'); ?></option>
                    <option value="this_month"><?php esc_html_e('本月', 'wpforge-theme'); ?></option>
                    <option value="last_month"><?php esc_html_e('上月', 'wpforge-theme'); ?></option>
                    <option value="custom"><?php esc_html_e('自定义', 'wpforge-theme'); ?></option>
                </select>
                <div class="funnel-date-custom" style="display: none;">
                    <input type="date" id="funnel-start-date" class="funnel-input">
                    <span><?php esc_html_e('至', 'wpforge-theme'); ?></span>
                    <input type="date" id="funnel-end-date" class="funnel-input">
                </div>
            </div>
            <button id="funnel-refresh" class="button button-secondary">
                <span class="dashicons dashicons-update"></span>
                <?php esc_html_e('刷新', 'wpforge-theme'); ?>
            </button>
            <button id="funnel-export" class="button button-primary">
                <span class="dashicons dashicons-download"></span>
                <?php esc_html_e('导出', 'wpforge-theme'); ?>
            </button>
        </div>
    </div>

    <!-- KPI 卡片 -->
    <div class="funnel-kpi-cards">
        <div class="funnel-kpi-card">
            <div class="kpi-icon visitors">
                <span class="dashicons dashicons-groups"></span>
            </div>
            <div class="kpi-content">
                <div class="kpi-label"><?php esc_html_e('总访客数', 'wpforge-theme'); ?></div>
                <div class="kpi-value" id="kpi-visitors">--</div>
                <div class="kpi-change" id="kpi-visitors-change">
                    <span class="change-arrow">--</span>
                    <span class="change-value">--</span>
                </div>
            </div>
        </div>

        <div class="funnel-kpi-card">
            <div class="kpi-icon add-to-cart">
                <span class="dashicons dashicons-cart"></span>
            </div>
            <div class="kpi-content">
                <div class="kpi-label"><?php esc_html_e('加入购物车', 'wpforge-theme'); ?></div>
                <div class="kpi-value" id="kpi-add-to-cart">--</div>
                <div class="kpi-change" id="kpi-add-to-cart-change">
                    <span class="change-arrow">--</span>
                    <span class="change-value">--</span>
                </div>
            </div>
        </div>

        <div class="funnel-kpi-card">
            <div class="kpi-icon checkout">
                <span class="dashicons dashicons-credit-card"></span>
            </div>
            <div class="kpi-content">
                <div class="kpi-label"><?php esc_html_e('开始结账', 'wpforge-theme'); ?></div>
                <div class="kpi-value" id="kpi-checkout">--</div>
                <div class="kpi-change" id="kpi-checkout-change">
                    <span class="change-arrow">--</span>
                    <span class="change-value">--</span>
                </div>
            </div>
        </div>

        <div class="funnel-kpi-card">
            <div class="kpi-icon purchases">
                <span class="dashicons dashicons-yes-alt"></span>
            </div>
            <div class="kpi-content">
                <div class="kpi-label"><?php esc_html_e('完成购买', 'wpforge-theme'); ?></div>
                <div class="kpi-value" id="kpi-purchases">--</div>
                <div class="kpi-change" id="kpi-purchases-change">
                    <span class="change-arrow">--</span>
                    <span class="change-value">--</span>
                </div>
            </div>
        </div>

        <div class="funnel-kpi-card">
            <div class="kpi-icon revenue">
                <span class="dashicons dashicons-chart-line"></span>
            </div>
            <div class="kpi-content">
                <div class="kpi-label"><?php esc_html_e('总销售额', 'wpforge-theme'); ?></div>
                <div class="kpi-value" id="kpi-revenue">--</div>
                <div class="kpi-change" id="kpi-revenue-change">
                    <span class="change-arrow">--</span>
                    <span class="change-value">--</span>
                </div>
            </div>
        </div>

        <div class="funnel-kpi-card">
            <div class="kpi-icon conversion">
                <span class="dashicons dashicons-performance"></span>
            </div>
            <div class="kpi-content">
                <div class="kpi-label"><?php esc_html_e('转化率', 'wpforge-theme'); ?></div>
                <div class="kpi-value" id="kpi-conversion">--</div>
                <div class="kpi-change" id="kpi-conversion-change">
                    <span class="change-arrow">--</span>
                    <span class="change-value">--</span>
                </div>
            </div>
        </div>
    </div>

    <!-- 转化漏斗图 -->
    <div class="funnel-section">
        <div class="funnel-section-header">
            <h2><?php esc_html_e('电商转化漏斗', 'wpforge-theme'); ?></h2>
            <div class="funnel-section-actions">
                <div class="funnel-toggle-group">
                    <button class="funnel-toggle active" data-view="absolute"><?php esc_html_e('绝对值', 'wpforge-theme'); ?></button>
                    <button class="funnel-toggle" data-view="percentage"><?php esc_html_e('百分比', 'wpforge-theme'); ?></button>
                </div>
            </div>
        </div>
        <div class="funnel-chart-container">
            <div id="funnel-chart" class="funnel-chart"></div>
        </div>
    </div>

    <!-- 销售趋势 + 漏斗趋势 -->
    <div class="funnel-row">
        <div class="funnel-col funnel-col-2">
            <div class="funnel-section">
                <div class="funnel-section-header">
                    <h2><?php esc_html_e('销售趋势', 'wpforge-theme'); ?></h2>
                </div>
                <div class="funnel-chart-container">
                    <canvas id="sales-trend-chart"></canvas>
                </div>
            </div>
        </div>
        <div class="funnel-col funnel-col-2">
            <div class="funnel-section">
                <div class="funnel-section-header">
                    <h2><?php esc_html_e('转化率趋势', 'wpforge-theme'); ?></h2>
                </div>
                <div class="funnel-chart-container">
                    <canvas id="conversion-trend-chart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- 热销产品 + 弃购产品 -->
    <div class="funnel-row">
        <div class="funnel-col funnel-col-2">
            <div class="funnel-section">
                <div class="funnel-section-header">
                    <h2><?php esc_html_e('热销产品 TOP10', 'wpforge-theme'); ?></h2>
                    <select id="top-products-order" class="funnel-select small">
                        <option value="sales"><?php esc_html_e('按销量', 'wpforge-theme'); ?></option>
                        <option value="revenue"><?php esc_html_e('按销售额', 'wpforge-theme'); ?></option>
                        <option value="views"><?php esc_html_e('按浏览量', 'wpforge-theme'); ?></option>
                        <option value="add_to_cart"><?php esc_html_e('按加购数', 'wpforge-theme'); ?></option>
                    </select>
                </div>
                <div class="funnel-product-list" id="top-products-list">
                    <div class="funnel-loading"><?php esc_html_e('加载中...', 'wpforge-theme'); ?></div>
                </div>
            </div>
        </div>
        <div class="funnel-col funnel-col-2">
            <div class="funnel-section">
                <div class="funnel-section-header">
                    <h2><?php esc_html_e('弃购产品分析', 'wpforge-theme'); ?></h2>
                </div>
                <div class="funnel-product-list" id="abandoned-products-list">
                    <div class="funnel-loading"><?php esc_html_e('加载中...', 'wpforge-theme'); ?></div>
                </div>
            </div>
        </div>
    </div>

    <!-- 流量来源 + 设备分布 -->
    <div class="funnel-row">
        <div class="funnel-col funnel-col-2">
            <div class="funnel-section">
                <div class="funnel-section-header">
                    <h2><?php esc_html_e('流量来源分析', 'wpforge-theme'); ?></h2>
                </div>
                <div class="funnel-chart-container">
                    <canvas id="traffic-sources-chart"></canvas>
                </div>
            </div>
        </div>
        <div class="funnel-col funnel-col-2">
            <div class="funnel-section">
                <div class="funnel-section-header">
                    <h2><?php esc_html_e('设备类型分布', 'wpforge-theme'); ?></h2>
                </div>
                <div class="funnel-chart-container">
                    <canvas id="device-distribution-chart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- AI智能洞察 -->
    <div class="funnel-section">
        <div class="funnel-section-header">
            <h2>
                <span class="dashicons dashicons-lightbulb"></span>
                <?php esc_html_e('AI 智能洞察与优化建议', 'wpforge-theme'); ?>
            </h2>
            <div class="funnel-insights-summary" id="insights-summary">
                <!-- 动态填充 -->
            </div>
        </div>
        <div class="funnel-insights-list" id="insights-list">
            <div class="funnel-loading"><?php esc_html_e('正在分析数据...', 'wpforge-theme'); ?></div>
        </div>
    </div>
</div>
