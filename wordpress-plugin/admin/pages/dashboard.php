<?php
/**
 * 仪表盘页面
 */
if (!defined('ABSPATH')) {
    exit;
}
?>

<div class="wrap wpforge-wrap">
    <h1><?php echo esc_html__('WPForge 仪表盘', 'wpforge'); ?></h1>
    
    <div class="wpforge-stats">
        <div class="stat-card">
            <div class="stat-icon">📦</div>
            <div class="stat-value"><?php echo esc_html(wp_count_posts('product')->publish); ?></div>
            <div class="stat-label"><?php esc_html_e('产品数量', 'wpforge'); ?></div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon">📥</div>
            <div class="stat-value"><?php echo esc_html(get_option('wpforge_total_imported', 0)); ?></div>
            <div class="stat-label"><?php esc_html_e('已导入产品', 'wpforge'); ?></div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon">🔍</div>
            <div class="stat-value"><?php echo esc_html(get_option('wpforge_seo_score', 'N/A')); ?></div>
            <div class="stat-label"><?php esc_html_e('SEO评分', 'wpforge'); ?></div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon">⚡</div>
            <div class="stat-value"><?php echo esc_html(get_option('wpforge_speed_score', 'N/A')); ?></div>
            <div class="stat-label"><?php esc_html_e('速度评分', 'wpforge'); ?></div>
        </div>
    </div>
    
    <div class="wpforge-content">
        <div class="wpforge-main">
            <div class="card">
                <h2><?php esc_html_e('快速操作', 'wpforge'); ?></h2>
                <div class="quick-actions">
                    <a href="<?php echo esc_url(admin_url('admin.php?page=wpforge-import')); ?>" class="button button-primary button-large">
                        <?php esc_html_e('开始导入产品', 'wpforge'); ?>
                    </a>
                    <a href="<?php echo esc_url(admin_url('admin.php?page=wpforge-seo')); ?>" class="button button-secondary button-large">
                        <?php esc_html_e('SEO优化', 'wpforge'); ?>
                    </a>
                    <a href="<?php echo esc_url(admin_url('admin.php?page=wpforge-speed')); ?>" class="button button-secondary button-large">
                        <?php esc_html_e('速度优化', 'wpforge'); ?>
                    </a>
                </div>
            </div>
            
            <div class="card">
                <h2><?php esc_html_e('最近导入', 'wpforge'); ?></h2>
                <?php
                global $wpdb;
                $table_name = $wpdb->prefix . 'wpforge_import_logs';
                $logs = $wpdb->get_results("SELECT * FROM $table_name ORDER BY created_at DESC LIMIT 5");
                
                if ($logs) {
                    echo '<table class="wp-list-table widefat fixed striped">';
                    echo '<thead><tr><th>' . esc_html__('任务ID', 'wpforge') . '</th><th>' . esc_html__('类型', 'wpforge') . '</th><th>' . esc_html__('状态', 'wpforge') . '</th><th>' . esc_html__('数量', 'wpforge') . '</th><th>' . esc_html__('时间', 'wpforge') . '</th></tr></thead>';
                    echo '<tbody>';
                    foreach ($logs as $log) {
                        echo '<tr>';
                        echo '<td>' . esc_html($log->task_id) . '</td>';
                        echo '<td>' . esc_html($log->type) . '</td>';
                        echo '<td><span class="status-' . esc_attr($log->status) . '">' . esc_html($log->status) . '</span></td>';
                        echo '<td>' . esc_html($log->success . '/' . $log->total) . '</td>';
                        echo '<td>' . esc_html($log->created_at) . '</td>';
                        echo '</tr>';
                    }
                    echo '</tbody>';
                    echo '</table>';
                } else {
                    echo '<p class="description">' . esc_html__('暂无导入记录', 'wpforge') . '</p>';
                }
                ?>
            </div>
        </div>
        
        <div class="wpforge-sidebar">
            <div class="card">
                <h3><?php esc_html_e('系统状态', 'wpforge'); ?></h3>
                <ul class="status-list">
                    <li>
                        <span class="status-label"><?php esc_html_e('PHP版本', 'wpforge'); ?></span>
                        <span class="status-value"><?php echo esc_html(phpversion()); ?></span>
                    </li>
                    <li>
                        <span class="status-label"><?php esc_html_e('WordPress版本', 'wpforge'); ?></span>
                        <span class="status-value"><?php echo esc_html(get_bloginfo('version')); ?></span>
                    </li>
                    <li>
                        <span class="status-label"><?php esc_html_e('WooCommerce', 'wpforge'); ?></span>
                        <span class="status-value <?php echo class_exists('WooCommerce') ? 'status-ok' : 'status-error'; ?>">
                            <?php echo class_exists('WooCommerce') ? esc_html__('已启用', 'wpforge') : esc_html__('未安装', 'wpforge'); ?>
                        </span>
                    </li>
                    <li>
                        <span class="status-label"><?php esc_html_e('API连接', 'wpforge'); ?></span>
                        <span class="status-value status-ok"><?php esc_html__('正常', 'wpforge'); ?></span>
                    </li>
                </ul>
            </div>
            
            <div class="card">
                <h3><?php esc_html_e('帮助与支持', 'wpforge'); ?></h3>
                <ul class="help-links">
                    <li><a href="#" target="_blank"><?php esc_html_e('使用文档', 'wpforge'); ?></a></li>
                    <li><a href="#" target="_blank"><?php esc_html_e('常见问题', 'wpforge'); ?></a></li>
                    <li><a href="#" target="_blank"><?php esc_html_e('技术支持', 'wpforge'); ?></a></li>
                </ul>
            </div>
        </div>
    </div>
</div>
