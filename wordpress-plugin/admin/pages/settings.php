<?php
/**
 * 设置页面
 */
if (!defined('ABSPATH')) {
    exit;
}
?>

<div class="wrap wpforge-wrap">
    <h1><?php echo esc_html__('WPForge 设置', 'wpforge'); ?></h1>
    
    <div class="wpforge-content">
        <div class="wpforge-main">
            <div class="card">
                <h2><?php esc_html_e('API连接设置', 'wpforge'); ?></h2>
                <p class="description">
                    <?php esc_html_e('配置WPForge后台API连接，用于同步数据和执行任务。', 'wpforge'); ?>
                </p>
                
                <form method="post" action="options.php">
                    <?php
                    settings_fields('wpforge_settings');
                    do_settings_sections('wpforge_settings');
                    ?>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row">
                                <label for="wpforge_api_url"><?php esc_html_e('API地址', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <input type="url" name="wpforge_api_url" id="wpforge_api_url" 
                                       value="<?php echo esc_attr(get_option('wpforge_api_url', '')); ?>" 
                                       class="regular-text"
                                       placeholder="https://api.wpforge.com">
                                <p class="description"><?php esc_html_e('WPForge后台API的地址', 'wpforge'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label for="wpforge_api_key"><?php esc_html_e('API密钥', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <input type="password" name="wpforge_api_key" id="wpforge_api_key" 
                                       value="<?php echo esc_attr(get_option('wpforge_api_key', '')); ?>" 
                                       class="regular-text"
                                       placeholder="输入您的API密钥">
                                <p class="description"><?php esc_html_e('从WPForge后台获取API密钥', 'wpforge'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('连接状态', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <span class="status status-ok"><?php esc_html_e('已连接', 'wpforge'); ?></span>
                                <button type="button" class="button button-secondary" id="test-connection">
                                    <?php esc_html_e('测试连接', 'wpforge'); ?>
                                </button>
                            </td>
                        </tr>
                    </table>
                    
                    <?php submit_button(); ?>
                </form>
            </div>
            
            <div class="card">
                <h2><?php esc_html_e('常规设置', 'wpforge'); ?></h2>
                
                <form method="post" action="options.php">
                    <?php
                    settings_fields('wpforge_general_settings');
                    do_settings_sections('wpforge_general_settings');
                    ?>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('默认语言', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <select name="wpforge_default_language" id="wpforge_default_language">
                                    <option value="zh-CN" <?php selected(get_option('wpforge_default_language', 'zh-CN'), 'zh-CN'); ?>>
                                        <?php esc_html_e('简体中文', 'wpforge'); ?>
                                    </option>
                                    <option value="en" <?php selected(get_option('wpforge_default_language', 'zh-CN'), 'en'); ?>>
                                        <?php esc_html_e('英语', 'wpforge'); ?>
                                    </option>
                                    <option value="de" <?php selected(get_option('wpforge_default_language', 'zh-CN'), 'de'); ?>>
                                        <?php esc_html_e('德语', 'wpforge'); ?>
                                    </option>
                                    <option value="fr" <?php selected(get_option('wpforge_default_language', 'zh-CN'), 'fr'); ?>>
                                        <?php esc_html_e('法语', 'wpforge'); ?>
                                    </option>
                                    <option value="ja" <?php selected(get_option('wpforge_default_language', 'zh-CN'), 'ja'); ?>>
                                        <?php esc_html_e('日语', 'wpforge'); ?>
                                    </option>
                                </select>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('默认货币', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <select name="wpforge_default_currency" id="wpforge_default_currency">
                                    <option value="CNY" <?php selected(get_option('wpforge_default_currency', 'CNY'), 'CNY'); ?>>
                                        <?php esc_html_e('人民币 (CNY)', 'wpforge'); ?>
                                    </option>
                                    <option value="USD" <?php selected(get_option('wpforge_default_currency', 'CNY'), 'USD'); ?>>
                                        <?php esc_html_e('美元 (USD)', 'wpforge'); ?>
                                    </option>
                                    <option value="EUR" <?php selected(get_option('wpforge_default_currency', 'CNY'), 'EUR'); ?>>
                                        <?php esc_html_e('欧元 (EUR)', 'wpforge'); ?>
                                    </option>
                                    <option value="GBP" <?php selected(get_option('wpforge_default_currency', 'CNY'), 'GBP'); ?>>
                                        <?php esc_html_e('英镑 (GBP)', 'wpforge'); ?>
                                    </option>
                                    <option value="JPY" <?php selected(get_option('wpforge_default_currency', 'CNY'), 'JPY'); ?>>
                                        <?php esc_html_e('日元 (JPY)', 'wpforge'); ?>
                                    </option>
                                </select>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('数据同步', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_auto_sync" value="1" 
                                           <?php checked(get_option('wpforge_auto_sync', 1), 1); ?>>
                                    <?php esc_html_e('启用自动同步', 'wpforge'); ?>
                                </label>
                                <p class="description"><?php esc_html_e('定期与WPForge后台同步数据', 'wpforge'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('调试模式', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_debug_mode" value="1" 
                                           <?php checked(get_option('wpforge_debug_mode', 0), 1); ?>>
                                    <?php esc_html_e('启用调试模式', 'wpforge'); ?>
                                </label>
                                <p class="description"><?php esc_html_e('记录详细的调试日志', 'wpforge'); ?></p>
                            </td>
                        </tr>
                    </table>
                    
                    <?php submit_button(); ?>
                </form>
            </div>
            
            <div class="card">
                <h2><?php esc_html_e('系统信息', 'wpforge'); ?></h2>
                
                <table class="widefat">
                    <tr>
                        <th><?php esc_html_e('插件版本', 'wpforge'); ?></th>
                        <td><?php echo esc_html(WPFORGE_VERSION); ?></td>
                    </tr>
                    <tr>
                        <th><?php esc_html_e('PHP版本', 'wpforge'); ?></th>
                        <td><?php echo esc_html(phpversion()); ?></td>
                    </tr>
                    <tr>
                        <th><?php esc_html_e('WordPress版本', 'wpforge'); ?></th>
                        <td><?php echo esc_html(get_bloginfo('version')); ?></td>
                    </tr>
                    <tr>
                        <th><?php esc_html_e('WooCommerce版本', 'wpforge'); ?></th>
                        <td>
                            <?php 
                            if (class_exists('WooCommerce')) {
                                echo esc_html(WC()->version);
                            } else {
                                esc_html_e('未安装', 'wpforge');
                            }
                            ?>
                        </td>
                    </tr>
                    <tr>
                        <th><?php esc_html_e('内存限制', 'wpforge'); ?></th>
                        <td><?php echo esc_html(ini_get('memory_limit')); ?></td>
                    </tr>
                    <tr>
                        <th><?php esc_html_e('最大执行时间', 'wpforge'); ?></th>
                        <td><?php echo esc_html(ini_get('max_execution_time') . ' 秒'); ?></td>
                    </tr>
                    <tr>
                        <th><?php esc_html_e('上传大小限制', 'wpforge'); ?></th>
                        <td><?php echo esc_html(ini_get('upload_max_filesize')); ?></td>
                    </tr>
                </table>
            </div>
        </div>
        
        <div class="wpforge-sidebar">
            <div class="card">
                <h3><?php esc_html_e('关于WPForge', 'wpforge'); ?></h3>
                <p><?php esc_html_e('WPForge是一款强大的WordPress AI仿站和产品采集工具，帮助您快速搭建和运营跨境电商网站。', 'wpforge'); ?></p>
                <ul>
                    <li>📦 <?php esc_html_e('智能产品采集', 'wpforge'); ?></li>
                    <li>🌐 <?php esc_html_e('多语言翻译', 'wpforge'); ?></li>
                    <li>🔍 <?php esc_html_e('SEO优化', 'wpforge'); ?></li>
                    <li>⚡ <?php esc_html_e('速度优化', 'wpforge'); ?></li>
                    <li>🎨 <?php esc_html_e('AI仿站', 'wpforge'); ?></li>
                </ul>
            </div>
            
            <div class="card">
                <h3><?php esc_html_e('帮助与支持', 'wpforge'); ?></h3>
                <ul class="help-links">
                    <li><a href="#" target="_blank"><?php esc_html_e('📖 使用文档', 'wpforge'); ?></a></li>
                    <li><a href="#" target="_blank"><?php esc_html_e('❓ 常见问题', 'wpforge'); ?></a></li>
                    <li><a href="#" target="_blank"><?php esc_html_e('💬 技术支持', 'wpforge'); ?></a></li>
                    <li><a href="#" target="_blank"><?php esc_html_e('🐛 提交Bug', 'wpforge'); ?></a></li>
                    <li><a href="#" target="_blank"><?php esc_html_e('💡 功能建议', 'wpforge'); ?></a></li>
                </ul>
            </div>
            
            <div class="card">
                <h3><?php esc_html_e('许可证', 'wpforge'); ?></h3>
                <p><?php esc_html_e('本插件采用GPL v2或更高版本许可证发布。', 'wpforge'); ?></p>
                <p class="description">
                    <?php esc_html_e('WPForge © 2024. 保留所有权利。', 'wpforge'); ?>
                </p>
            </div>
        </div>
    </div>
</div>
