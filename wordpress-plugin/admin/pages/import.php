<?php
/**
 * 产品导入页面
 */
if (!defined('ABSPATH')) {
    exit;
}
?>

<div class="wrap wpforge-wrap">
    <h1><?php echo esc_html__('产品导入', 'wpforge'); ?></h1>
    
    <div class="wpforge-content">
        <div class="wpforge-main">
            <div class="card">
                <h2><?php esc_html_e('批量导入产品', 'wpforge'); ?></h2>
                <p class="description">
                    <?php esc_html_e('从WPForge后台导入产品数据，支持自动翻译、图片处理、SEO优化等功能。', 'wpforge'); ?>
                </p>
                
                <form method="post" action="" id="wpforge-import-form">
                    <?php wp_nonce_field('wpforge_import_nonce', 'wpforge_nonce'); ?>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row">
                                <label for="import_source"><?php esc_html_e('导入来源', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <select name="import_source" id="import_source" class="regular-text">
                                    <option value="wpforge"><?php esc_html_e('WPForge 采集任务', 'wpforge'); ?></option>
                                    <option value="csv"><?php esc_html_e('CSV文件', 'wpforge'); ?></option>
                                    <option value="json"><?php esc_html_e('JSON文件', 'wpforge'); ?></option>
                                </select>
                            </td>
                        </tr>
                        
                        <tr id="task-id-row">
                            <th scope="row">
                                <label for="task_id"><?php esc_html_e('任务ID', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <input type="text" name="task_id" id="task_id" class="regular-text" 
                                       placeholder="<?php esc_attr_e('输入WPForge任务ID', 'wpforge'); ?>">
                                <p class="description"><?php esc_html_e('从WPForge后台获取任务ID', 'wpforge'); ?></p>
                            </td>
                        </tr>
                        
                        <tr id="file-upload-row" style="display:none;">
                            <th scope="row">
                                <label for="import_file"><?php esc_html_e('选择文件', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <input type="file" name="import_file" id="import_file" accept=".csv,.json">
                                <p class="description"><?php esc_html_e('支持CSV和JSON格式', 'wpforge'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('导入选项', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="update_existing" value="1" checked>
                                    <?php esc_html_e('更新已存在的产品', 'wpforge'); ?>
                                </label>
                                <br>
                                <label>
                                    <input type="checkbox" name="import_images" value="1" checked>
                                    <?php esc_html_e('导入产品图片', 'wpforge'); ?>
                                </label>
                                <br>
                                <label>
                                    <input type="checkbox" name="import_variations" value="1" checked>
                                    <?php esc_html_e('导入产品变体', 'wpforge'); ?>
                                </label>
                                <br>
                                <label>
                                    <input type="checkbox" name="auto_publish" value="1">
                                    <?php esc_html_e('自动发布产品', 'wpforge'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('图片处理', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="compress_images" value="1" checked>
                                    <?php esc_html_e('自动压缩图片', 'wpforge'); ?>
                                </label>
                                <br>
                                <label>
                                    <input type="checkbox" name="generate_webp" value="1">
                                    <?php esc_html_e('生成WebP格式', 'wpforge'); ?>
                                </label>
                                <br>
                                <label>
                                    <input type="checkbox" name="auto_alt" value="1" checked>
                                    <?php esc_html_e('自动生成ALT标签', 'wpforge'); ?>
                                </label>
                            </td>
                        </tr>
                    </table>
                    
                    <p class="submit">
                        <button type="submit" class="button button-primary button-large" id="start-import-btn">
                            <?php esc_html_e('开始导入', 'wpforge'); ?>
                        </button>
                        <span class="spinner" id="import-spinner"></span>
                    </p>
                </form>
            </div>
            
            <div class="card" id="import-progress" style="display:none;">
                <h2><?php esc_html_e('导入进度', 'wpforge'); ?></h2>
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill" id="import-progress-fill" style="width: 0%;"></div>
                    </div>
                    <div class="progress-text">
                        <span id="import-progress-text">0%</span>
                    </div>
                </div>
                <div class="import-stats">
                    <div class="stat">
                        <span class="stat-label"><?php esc_html_e('总计', 'wpforge'); ?></span>
                        <span class="stat-value" id="total-products">0</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label"><?php esc_html_e('成功', 'wpforge'); ?></span>
                        <span class="stat-value success" id="success-products">0</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label"><?php esc_html_e('失败', 'wpforge'); ?></span>
                        <span class="stat-value error" id="failed-products">0</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label"><?php esc_html_e('跳过', 'wpforge'); ?></span>
                        <span class="stat-value warning" id="skipped-products">0</span>
                    </div>
                </div>
                <div id="import-log" class="import-log"></div>
            </div>
            
            <div class="card">
                <h2><?php esc_html_e('导入历史', 'wpforge'); ?></h2>
                <?php
                global $wpdb;
                $table_name = $wpdb->prefix . 'wpforge_import_logs';
                $logs = $wpdb->get_results("SELECT * FROM $table_name ORDER BY created_at DESC LIMIT 20");
                
                if ($logs) {
                    echo '<table class="wp-list-table widefat fixed striped">';
                    echo '<thead><tr><th>' . esc_html__('任务ID', 'wpforge') . '</th><th>' . esc_html__('类型', 'wpforge') . '</th><th>' . esc_html__('状态', 'wpforge') . '</th><th>' . esc_html__('成功/总计', 'wpforge') . '</th><th>' . esc_html__('时间', 'wpforge') . '</th><th>' . esc_html__('操作', 'wpforge') . '</th></tr></thead>';
                    echo '<tbody>';
                    foreach ($logs as $log) {
                        echo '<tr>';
                        echo '<td>' . esc_html($log->task_id) . '</td>';
                        echo '<td>' . esc_html($log->type) . '</td>';
                        echo '<td><span class="status-' . esc_attr($log->status) . '">' . esc_html($log->status) . '</span></td>';
                        echo '<td>' . esc_html($log->success . '/' . $log->total) . '</td>';
                        echo '<td>' . esc_html($log->created_at) . '</td>';
                        echo '<td><a href="#" class="button button-small">' . esc_html__('查看详情', 'wpforge') . '</a></td>';
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
                <h3><?php esc_html_e('导入说明', 'wpforge'); ?></h3>
                <ul class="help-list">
                    <li><?php esc_html_e('支持从WPForge采集任务直接导入', 'wpforge'); ?></li>
                    <li><?php esc_html_e('支持CSV和JSON文件导入', 'wpforge'); ?></li>
                    <li><?php esc_html_e('自动处理产品图片和变体', 'wpforge'); ?></li>
                    <li><?php esc_html_e('支持增量更新', 'wpforge'); ?></li>
                    <li><?php esc_html_e('自动生成SEO信息', 'wpforge'); ?></li>
                </ul>
            </div>
            
            <div class="card">
                <h3><?php esc_html_e('支持的字段', 'wpforge'); ?></h3>
                <ul class="field-list">
                    <li>✅ <?php esc_html_e('产品标题', 'wpforge'); ?></li>
                    <li>✅ <?php esc_html_e('产品描述', 'wpforge'); ?></li>
                    <li>✅ <?php esc_html_e('产品图片', 'wpforge'); ?></li>
                    <li>✅ <?php esc_html_e('产品价格', 'wpforge'); ?></li>
                    <li>✅ <?php esc_html_e('库存信息', 'wpforge'); ?></li>
                    <li>✅ <?php esc_html_e('产品分类', 'wpforge'); ?></li>
                    <li>✅ <?php esc_html_e('产品标签', 'wpforge'); ?></li>
                    <li>✅ <?php esc_html_e('产品属性', 'wpforge'); ?></li>
                    <li>✅ <?php esc_html_e('产品变体', 'wpforge'); ?></li>
                    <li>✅ <?php esc_html_e('SEO信息', 'wpforge'); ?></li>
                </ul>
            </div>
        </div>
    </div>
</div>
