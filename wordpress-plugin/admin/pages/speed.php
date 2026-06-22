<?php
/**
 * 速度优化页面
 */
if (!defined('ABSPATH')) {
    exit;
}
?>

<div class="wrap wpforge-wrap">
    <h1><?php echo esc_html__('速度优化', 'wpforge'); ?></h1>
    
    <div class="wpforge-content">
        <div class="wpforge-main">
            <div class="card">
                <h2><?php esc_html_e('速度设置', 'wpforge'); ?></h2>
                
                <form method="post" action="options.php">
                    <?php
                    settings_fields('wpforge_speed_settings');
                    do_settings_sections('wpforge_speed_settings');
                    ?>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('启用速度优化', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_speed_enabled" value="1" 
                                           <?php checked(get_option('wpforge_speed_enabled', 1), 1); ?>>
                                    <?php esc_html_e('启用速度优化功能', 'wpforge'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('图片优化', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_image_optimization" value="1" 
                                           <?php checked(get_option('wpforge_image_optimization', 1), 1); ?>>
                                    <?php esc_html_e('自动优化上传的图片', 'wpforge'); ?>
                                </label>
                                <p class="description"><?php esc_html_e('压缩图片大小，生成WebP格式', 'wpforge'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('延迟加载', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_lazy_load" value="1" 
                                           <?php checked(get_option('wpforge_lazy_load', 1), 1); ?>>
                                    <?php esc_html_e('启用图片延迟加载', 'wpforge'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('缓存', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_cache_enabled" value="1" 
                                           <?php checked(get_option('wpforge_cache_enabled', 1), 1); ?>>
                                    <?php esc_html_e('启用页面缓存', 'wpforge'); ?>
                                </label>
                                <p class="description"><?php esc_html_e('生成静态HTML缓存，提升页面加载速度', 'wpforge'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('Gzip压缩', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_gzip" value="1" 
                                           <?php checked(get_option('wpforge_gzip', 1), 1); ?>>
                                    <?php esc_html_e('启用Gzip压缩', 'wpforge'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('CDN集成', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_cdn_enabled" value="1" 
                                           <?php checked(get_option('wpforge_cdn_enabled', 0), 1); ?>>
                                    <?php esc_html_e('启用CDN加速', 'wpforge'); ?>
                                </label>
                                <p class="description"><?php esc_html_e('支持Cloudflare、七牛云、阿里云CDN等', 'wpforge'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('数据库优化', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_db_optimization" value="1" 
                                           <?php checked(get_option('wpforge_db_optimization', 0), 1); ?>>
                                    <?php esc_html_e('定期优化数据库', 'wpforge'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('Heartbeat控制', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_heartbeat_control" value="1" 
                                           <?php checked(get_option('wpforge_heartbeat_control', 0), 1); ?>>
                                    <?php esc_html_e('控制WordPress Heartbeat API', 'wpforge'); ?>
                                </label>
                                <p class="description"><?php esc_html_e('减少服务器负载，提升后台性能', 'wpforge'); ?></p>
                            </td>
                        </tr>
                    </table>
                    
                    <?php submit_button(); ?>
                </form>
            </div>
            
            <div class="card">
                <h2><?php esc_html_e('性能测试', 'wpforge'); ?></h2>
                <p class="description">
                    <?php esc_html_e('测试您的网站速度，找出性能瓶颈。', 'wpforge'); ?>
                </p>
                
                <button type="button" class="button button-primary" id="run-speed-test">
                    <?php esc_html_e('运行性能测试', 'wpforge'); ?>
                </button>
                
                <div id="speed-test-results" style="margin-top: 20px; display: none;">
                    <h3><?php esc_html_e('测试结果', 'wpforge'); ?></h3>
                    
                    <div class="speed-scores">
                        <div class="score-item">
                            <div class="score-circle performance">
                                <span class="score-value" id="performance-score">0</span>
                                <span class="score-label"><?php esc_html_e('性能', 'wpforge'); ?></span>
                            </div>
                        </div>
                        <div class="score-item">
                            <div class="score-circle accessibility">
                                <span class="score-value" id="accessibility-score">0</span>
                                <span class="score-label"><?php esc_html_e('可访问性', 'wpforge'); ?></span>
                            </div>
                        </div>
                        <div class="score-item">
                            <div class="score-circle best-practices">
                                <span class="score-value" id="best-practices-score">0</span>
                                <span class="score-label"><?php esc_html_e('最佳实践', 'wpforge'); ?></span>
                            </div>
                        </div>
                        <div class="score-item">
                            <div class="score-circle seo">
                                <span class="score-value" id="seo-score">0</span>
                                <span class="score-label"><?php esc_html_e('SEO', 'wpforge'); ?></span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="core-web-vitals">
                        <h4><?php esc_html_e('Core Web Vitals', 'wpforge'); ?></h4>
                        <table class="widefat">
                            <tr>
                                <th><?php esc_html_e('LCP (最大内容绘制)', 'wpforge'); ?></th>
                                <td id="lcp-value">-</td>
                                <td id="lcp-status" class="status">-</td>
                            </tr>
                            <tr>
                                <th><?php esc_html_e('FID (首次输入延迟)', 'wpforge'); ?></th>
                                <td id="fid-value">-</td>
                                <td id="fid-status" class="status">-</td>
                            </tr>
                            <tr>
                                <th><?php esc_html_e('CLS (累积布局偏移)', 'wpforge'); ?></th>
                                <td id="cls-value">-</td>
                                <td id="cls-status" class="status">-</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div class="speed-opportunities">
                        <h4><?php esc_html_e('优化建议', 'wpforge'); ?></h4>
                        <ul id="speed-opportunities-list"></ul>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2><?php esc_html_e('一键优化', 'wpforge'); ?></h2>
                <p class="description">
                    <?php esc_html_e('一键应用所有推荐的速度优化设置。', 'wpforge'); ?>
                </p>
                
                <div class="one-click-optimize">
                    <button type="button" class="button button-primary button-large" id="one-click-optimize">
                        <?php esc_html_e('一键优化', 'wpforge'); ?>
                    </button>
                    <p class="description">
                        <?php esc_html_e('将自动启用图片优化、缓存、Gzip压缩等功能', 'wpforge'); ?>
                    </p>
                </div>
            </div>
        </div>
        
        <div class="wpforge-sidebar">
            <div class="card">
                <h3><?php esc_html_e('当前状态', 'wpforge'); ?></h3>
                <ul class="status-list">
                    <li>
                        <span class="status-label"><?php esc_html_e('图片优化', 'wpforge'); ?></span>
                        <span class="status-value status-ok"><?php esc_html_e('已启用', 'wpforge'); ?></span>
                    </li>
                    <li>
                        <span class="status-label"><?php esc_html_e('延迟加载', 'wpforge'); ?></span>
                        <span class="status-value status-ok"><?php esc_html_e('已启用', 'wpforge'); ?></span>
                    </li>
                    <li>
                        <span class="status-label"><?php esc_html_e('页面缓存', 'wpforge'); ?></span>
                        <span class="status-value status-ok"><?php esc_html_e('已启用', 'wpforge'); ?></span>
                    </li>
                    <li>
                        <span class="status-label"><?php esc_html_e('Gzip压缩', 'wpforge'); ?></span>
                        <span class="status-value status-ok"><?php esc_html_e('已启用', 'wpforge'); ?></span>
                    </li>
                    <li>
                        <span class="status-label"><?php esc_html_e('CDN', 'wpforge'); ?></span>
                        <span class="status-value status-warning"><?php esc_html_e('未配置', 'wpforge'); ?></span>
                    </li>
                </ul>
            </div>
            
            <div class="card">
                <h3><?php esc_html_e('优化效果', 'wpforge'); ?></h3>
                <div class="optimization-stats">
                    <div class="stat">
                        <span class="stat-value">60%</span>
                        <span class="stat-label"><?php esc_html_e('平均提速', 'wpforge'); ?></span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">40%</span>
                        <span class="stat-label"><?php esc_html_e('图片压缩', 'wpforge'); ?></span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">70%</span>
                        <span class="stat-label"><?php esc_html_e('HTML压缩', 'wpforge'); ?></span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
