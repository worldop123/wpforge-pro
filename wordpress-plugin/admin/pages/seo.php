<?php
/**
 * SEO优化页面
 */
if (!defined('ABSPATH')) {
    exit;
}
?>

<div class="wrap wpforge-wrap">
    <h1><?php echo esc_html__('SEO优化', 'wpforge'); ?></h1>
    
    <div class="wpforge-content">
        <div class="wpforge-main">
            <div class="card">
                <h2><?php esc_html_e('SEO设置', 'wpforge'); ?></h2>
                
                <form method="post" action="options.php">
                    <?php
                    settings_fields('wpforge_seo_settings');
                    do_settings_sections('wpforge_seo_settings');
                    ?>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('启用SEO优化', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_seo_enabled" value="1" 
                                           <?php checked(get_option('wpforge_seo_enabled', 1), 1); ?>>
                                    <?php esc_html_e('启用SEO优化功能', 'wpforge'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('自动生成标题', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_auto_title" value="1" 
                                           <?php checked(get_option('wpforge_auto_title', 1), 1); ?>>
                                    <?php esc_html_e('自动生成SEO友好的标题', 'wpforge'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('自动生成描述', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_auto_description" value="1" 
                                           <?php checked(get_option('wpforge_auto_description', 1), 1); ?>>
                                    <?php esc_html_e('自动生成Meta描述', 'wpforge'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('自动生成关键词', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_auto_keywords" value="1" 
                                           <?php checked(get_option('wpforge_auto_keywords', 1), 1); ?>>
                                    <?php esc_html_e('自动从内容中提取关键词', 'wpforge'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('图片ALT标签', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_image_alt" value="1" 
                                           <?php checked(get_option('wpforge_image_alt', 1), 1); ?>>
                                    <?php esc_html_e('自动为图片生成ALT标签', 'wpforge'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('结构化数据', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_schema" value="1" 
                                           <?php checked(get_option('wpforge_schema', 1), 1); ?>>
                                    <?php esc_html_e('自动生成Schema结构化数据', 'wpforge'); ?>
                                </label>
                                <p class="description"><?php esc_html_e('包括产品、文章、面包屑等Schema', 'wpforge'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('XML Sitemap', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_sitemap" value="1" 
                                           <?php checked(get_option('wpforge_sitemap', 1), 1); ?>>
                                    <?php esc_html_e('自动生成XML Sitemap', 'wpforge'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label><?php esc_html_e('内部链接优化', 'wpforge'); ?></label>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox" name="wpforge_internal_links" value="1" 
                                           <?php checked(get_option('wpforge_internal_links', 0), 1); ?>>
                                    <?php esc_html_e('自动添加内部链接', 'wpforge'); ?>
                                </label>
                            </td>
                        </tr>
                    </table>
                    
                    <?php submit_button(); ?>
                </form>
            </div>
            
            <div class="card">
                <h2><?php esc_html_e('SEO审计', 'wpforge'); ?></h2>
                <p class="description">
                    <?php esc_html_e('分析您的网站SEO状况，找出问题并提供改进建议。', 'wpforge'); ?>
                </p>
                
                <button type="button" class="button button-primary" id="run-seo-audit">
                    <?php esc_html_e('运行SEO审计', 'wpforge'); ?>
                </button>
                
                <div id="seo-audit-results" style="margin-top: 20px; display: none;">
                    <h3><?php esc_html_e('审计结果', 'wpforge'); ?></h3>
                    <div class="seo-score">
                        <div class="score-circle">
                            <span class="score-value" id="seo-score-value">0</span>
                            <span class="score-label"><?php esc_html_e('SEO评分', 'wpforge'); ?></span>
                        </div>
                    </div>
                    
                    <div class="seo-issues">
                        <h4><?php esc_html_e('发现的问题', 'wpforge'); ?></h4>
                        <ul id="seo-issues-list"></ul>
                    </div>
                    
                    <div class="seo-recommendations">
                        <h4><?php esc_html_e('改进建议', 'wpforge'); ?></h4>
                        <ul id="seo-recommendations-list"></ul>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2><?php esc_html_e('批量SEO优化', 'wpforge'); ?></h2>
                <p class="description">
                    <?php esc_html_e('对已有的产品和文章进行批量SEO优化。', 'wpforge'); ?>
                </p>
                
                <table class="form-table">
                    <tr>
                        <th scope="row">
                            <label><?php esc_html_e('优化类型', 'wpforge'); ?></label>
                        </th>
                        <td>
                            <select name="optimize_type" id="optimize_type">
                                <option value="products"><?php esc_html_e('产品', 'wpforge'); ?></option>
                                <option value="posts"><?php esc_html_e('文章', 'wpforge'); ?></option>
                                <option value="pages"><?php esc_html_e('页面', 'wpforge'); ?></option>
                                <option value="all"><?php esc_html_e('全部', 'wpforge'); ?></option>
                            </select>
                        </td>
                    </tr>
                    
                    <tr>
                        <th scope="row">
                            <label><?php esc_html_e('优化项目', 'wpforge'); ?></label>
                        </th>
                        <td>
                            <label>
                                <input type="checkbox" name="optimize_title" value="1" checked>
                                <?php esc_html_e('优化标题', 'wpforge'); ?>
                            </label>
                            <br>
                            <label>
                                <input type="checkbox" name="optimize_description" value="1" checked>
                                <?php esc_html_e('优化描述', 'wpforge'); ?>
                            </label>
                            <br>
                            <label>
                                <input type="checkbox" name="optimize_keywords" value="1" checked>
                                <?php esc_html_e('优化关键词', 'wpforge'); ?>
                            </label>
                            <br>
                            <label>
                                <input type="checkbox" name="optimize_schema" value="1">
                                <?php esc_html_e('生成Schema', 'wpforge'); ?>
                            </label>
                        </td>
                    </tr>
                </table>
                
                <p class="submit">
                    <button type="button" class="button button-primary" id="start-bulk-seo">
                        <?php esc_html_e('开始批量优化', 'wpforge'); ?>
                    </button>
                </p>
            </div>
        </div>
        
        <div class="wpforge-sidebar">
            <div class="card">
                <h3><?php esc_html_e('SEO检查清单', 'wpforge'); ?></h3>
                <ul class="checklist">
                    <li class="done">✅ <?php esc_html_e('标题标签优化', 'wpforge'); ?></li>
                    <li class="done">✅ <?php esc_html_e('Meta描述', 'wpforge'); ?></li>
                    <li class="done">✅ <?php esc_html_e('标题层级', 'wpforge'); ?></li>
                    <li class="done">✅ <?php esc_html_e('图片ALT标签', 'wpforge'); ?></li>
                    <li class="done">✅ <?php esc_html_e('结构化数据', 'wpforge'); ?></li>
                    <li class="done">✅ <?php esc_html_e('XML Sitemap', 'wpforge'); ?></li>
                    <li class="done">✅ <?php esc_html_e('Robots.txt', 'wpforge'); ?></li>
                    <li class="pending">⏳ <?php esc_html_e('内部链接建设', 'wpforge'); ?></li>
                    <li class="pending">⏳ <?php esc_html_e('内容质量优化', 'wpforge'); ?></li>
                </ul>
            </div>
            
            <div class="card">
                <h3><?php esc_html_e('支持的Schema类型', 'wpforge'); ?></h3>
                <ul class="schema-list">
                    <li>📦 <?php esc_html_e('产品 (Product)', 'wpforge'); ?></li>
                    <li>📝 <?php esc_html_e('文章 (Article)', 'wpforge'); ?></li>
                    <li>🍞 <?php esc_html_e('面包屑 (Breadcrumb)', 'wpforge'); ?></li>
                    <li>⭐ <?php esc_html_e('评价 (Review)', 'wpforge'); ?></li>
                    <li>🏢 <?php esc_html_e('组织 (Organization)', 'wpforge'); ?></li>
                    <li>👤 <?php esc_html_e('人物 (Person)', 'wpforge'); ?></li>
                    <li>📚 <?php esc_html_e('FAQ', 'wpforge'); ?></li>
                    <li>❓ <?php esc_html_e('HowTo', 'wpforge'); ?></li>
                </ul>
            </div>
        </div>
    </div>
</div>
