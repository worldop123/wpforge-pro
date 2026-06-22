<?php
/**
 * 速度优化类
 */

// 防止直接访问
if (!defined('ABSPATH')) {
    exit;
}

class WPForge_Speed {
    
    /**
     * 构造函数
     */
    public function __construct() {
        if (get_option('wpforge_speed_enabled', 1)) {
            $this->init_hooks();
        }
    }
    
    /**
     * 初始化钩子
     */
    private function init_hooks() {
        // 图片懒加载
        if (get_option('wpforge_image_optimization', 1)) {
            add_filter('the_content', array($this, 'add_lazy_loading'));
            add_filter('post_thumbnail_html', array($this, 'add_lazy_loading'));
            add_filter('widget_text', array($this, 'add_lazy_loading'));
        }
        
        // 禁用Emoji
        remove_action('wp_head', 'print_emoji_detection_script', 7);
        remove_action('wp_print_styles', 'print_emoji_styles');
        remove_action('admin_print_scripts', 'print_emoji_detection_script');
        remove_action('admin_print_styles', 'print_emoji_styles');
        
        // 移除WordPress版本号
        remove_action('wp_head', 'wp_generator');
        
        // 禁用XML-RPC
        add_filter('xmlrpc_enabled', '__return_false');
        
        // 心跳API控制
        add_action('init', array($this, 'control_heartbeat'));
        
        // 修订版本控制
        add_filter('wp_revisions_to_keep', array($this, 'limit_revisions'), 10, 2);
        
        // GZIP压缩
        add_action('init', array($this, 'enable_gzip_compression'));
        
        // 浏览器缓存
        add_action('init', array($this, 'add_cache_headers'));
    }
    
    /**
     * 添加图片懒加载
     */
    public function add_lazy_loading($content) {
        // 只在前端生效
        if (is_admin()) {
            return $content;
        }
        
        // 为图片添加loading="lazy"属性
        $content = preg_replace('/<img(?!.*loading=)/i', '<img loading="lazy"', $content);
        
        return $content;
    }
    
    /**
     * 控制心跳API
     */
    public function control_heartbeat() {
        // 减少心跳频率
        if (!is_admin()) {
            wp_deregister_script('heartbeat');
            wp_register_script('heartbeat', includes_url('js/heartbeat.min.js'), array('jquery'), false, true);
            
            // 修改心跳间隔为60秒
            wp_localize_script('heartbeat', 'heartbeatSettings', array(
                'interval' => 60,
                'nonce' => wp_create_nonce('heartbeat-nonce')
            ));
        }
    }
    
    /**
     * 限制修订版本数量
     */
    public function limit_revisions($num, $post) {
        // 限制为5个修订版本
        return 5;
    }
    
    /**
     * 启用GZIP压缩
     */
    public function enable_gzip_compression() {
        // 通过.htaccess或PHP实现GZIP压缩
        if (!is_admin() && !ob_start('ob_gzhandler')) {
            // 如果ob_gzhandler不可用，尝试其他方式
        }
    }
    
    /**
     * 添加缓存头
     */
    public function add_cache_headers() {
        if (is_admin()) {
            return;
        }
        
        // 静态资源缓存
        if (!is_user_logged_in()) {
            // 设置缓存控制头
            header('Cache-Control: public, max-age=3600');
        }
    }
    
    /**
     * 生成.htaccess优化规则
     */
    public function generate_htaccess_rules($optimizations = array()) {
        $rules = '';
        
        // GZIP压缩
        if (in_array('gzip', $optimizations) || in_array('compression', $optimizations)) {
            $rules .= "# WPForge GZIP Compression\n";
            $rules .= "<IfModule mod_deflate.c>\n";
            $rules .= "    AddOutputFilterByType DEFLATE text/plain\n";
            $rules .= "    AddOutputFilterByType DEFLATE text/html\n";
            $rules .= "    AddOutputFilterByType DEFLATE text/xml\n";
            $rules .= "    AddOutputFilterByType DEFLATE text/css\n";
            $rules .= "    AddOutputFilterByType DEFLATE application/xml\n";
            $rules .= "    AddOutputFilterByType DEFLATE application/xhtml+xml\n";
            $rules .= "    AddOutputFilterByType DEFLATE application/rss+xml\n";
            $rules .= "    AddOutputFilterByType DEFLATE application/javascript\n";
            $rules .= "    AddOutputFilterByType DEFLATE application/x-javascript\n";
            $rules .= "</IfModule>\n\n";
        }
        
        // 浏览器缓存
        if (in_array('caching', $optimizations) || in_array('browser_cache', $optimizations)) {
            $rules .= "# WPForge Browser Caching\n";
            $rules .= "<IfModule mod_expires.c>\n";
            $rules .= "    ExpiresActive On\n";
            $rules .= "    ExpiresByType image/jpg \"access plus 1 year\"\n";
            $rules .= "    ExpiresByType image/jpeg \"access plus 1 year\"\n";
            $rules .= "    ExpiresByType image/gif \"access plus 1 year\"\n";
            $rules .= "    ExpiresByType image/png \"access plus 1 year\"\n";
            $rules .= "    ExpiresByType image/webp \"access plus 1 year\"\n";
            $rules .= "    ExpiresByType text/css \"access plus 1 month\"\n";
            $rules .= "    ExpiresByType application/pdf \"access plus 1 month\"\n";
            $rules .= "    ExpiresByType text/javascript \"access plus 1 month\"\n";
            $rules .= "    ExpiresByType application/javascript \"access plus 1 month\"\n";
            $rules .= "    ExpiresByType application/x-javascript \"access plus 1 month\"\n";
            $rules .= "    ExpiresByType application/x-shockwave-flash \"access plus 1 month\"\n";
            $rules .= "    ExpiresByType image/x-icon \"access plus 1 year\"\n";
            $rules .= "    ExpiresDefault \"access plus 2 days\"\n";
            $rules .= "</IfModule>\n\n";
        }
        
        // 禁用ETag
        if (in_array('etag', $optimizations)) {
            $rules .= "# WPForge Disable ETags\n";
            $rules .= "FileETag None\n";
            $rules .= "Header unset ETag\n\n";
        }
        
        // 禁止目录浏览
        if (in_array('security', $optimizations)) {
            $rules .= "# WPForge Security\n";
            $rules .= "Options -Indexes\n\n";
        }
        
        return $rules;
    }
    
    /**
     * 优化数据库
     */
    public function optimize_database() {
        global $wpdb;
        
        $results = array(
            'revisions_deleted' => 0,
            'spam_comments_deleted' => 0,
            'trash_posts_deleted' => 0,
            'transients_cleared' => 0,
            'tables_optimized' => 0
        );
        
        // 删除修订版本
        $revisions = $wpdb->get_var("SELECT COUNT(*) FROM $wpdb->posts WHERE post_type = 'revision'");
        if ($revisions > 0) {
            $wpdb->query("DELETE FROM $wpdb->posts WHERE post_type = 'revision'");
            $results['revisions_deleted'] = $revisions;
        }
        
        // 删除垃圾评论
        $spam_comments = $wpdb->get_var("SELECT COUNT(*) FROM $wpdb->comments WHERE comment_approved = 'spam'");
        if ($spam_comments > 0) {
            $wpdb->query("DELETE FROM $wpdb->comments WHERE comment_approved = 'spam'");
            $results['spam_comments_deleted'] = $spam_comments;
        }
        
        // 删除回收站文章
        $trash_posts = $wpdb->get_var("SELECT COUNT(*) FROM $wpdb->posts WHERE post_status = 'trash'");
        if ($trash_posts > 0) {
            $wpdb->query("DELETE FROM $wpdb->posts WHERE post_status = 'trash'");
            $results['trash_posts_deleted'] = $trash_posts;
        }
        
        // 清除过期瞬态
        $transients = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM $wpdb->options WHERE option_name LIKE %s AND option_value < %d",
            '_transient_timeout_%',
            time()
        ));
        if ($transients > 0) {
            $wpdb->query($wpdb->prepare(
                "DELETE FROM $wpdb->options WHERE option_name LIKE %s AND option_value < %d",
                '_transient_timeout_%',
                time()
            ));
            $results['transients_cleared'] = $transients;
        }
        
        // 优化数据库表
        $tables = $wpdb->get_results("SHOW TABLES", ARRAY_N);
        foreach ($tables as $table) {
            $wpdb->query("OPTIMIZE TABLE {$table[0]}");
            $results['tables_optimized']++;
        }
        
        return $results;
    }
    
    /**
     * 获取速度优化建议
     */
    public function get_optimization_suggestions() {
        $suggestions = array();
        
        // 图片优化
        $suggestions[] = array(
            'category' => 'images',
            'title' => __('图片压缩与WebP格式', 'wpforge'),
            'description' => __('压缩图片并转换为WebP格式可以显著减少图片大小，加快加载速度', 'wpforge'),
            'priority' => 'high',
            'tools' => array('WPForge Image Optimizer', 'ShortPixel', 'Smush')
        );
        
        // 缓存配置
        $suggestions[] = array(
            'category' => 'caching',
            'title' => __('配置页面缓存', 'wpforge'),
            'description' => __('启用页面缓存可以大幅减少服务器响应时间，提升访问速度', 'wpforge'),
            'priority' => 'high',
            'tools' => array('WP Rocket', 'W3 Total Cache', 'LiteSpeed Cache')
        );
        
        // CDN
        $suggestions[] = array(
            'category' => 'cdn',
            'title' => __('配置CDN加速', 'wpforge'),
            'description' => __('使用CDN分发静态资源，减少延迟，提升全球访问速度', 'wpforge'),
            'priority' => 'high',
            'tools' => array('Cloudflare', 'StackPath', 'KeyCDN')
        );
        
        // 懒加载
        $suggestions[] = array(
            'category' => 'lazyload',
            'title' => __('图片懒加载', 'wpforge'),
            'description' => __('延迟加载视窗外的图片，加快首屏加载速度', 'wpforge'),
            'priority' => 'medium',
            'tools' => array('原生loading属性', 'Lazy Load插件')
        );
        
        // 数据库优化
        $suggestions[] = array(
            'category' => 'database',
            'title' => __('数据库优化', 'wpforge'),
            'description' => __('清理修订版本、垃圾评论、过期瞬态等，优化数据库性能', 'wpforge'),
            'priority' => 'medium',
            'tools' => array('WP-Optimize', 'WP-Sweep')
        );
        
        // GZIP压缩
        $suggestions[] = array(
            'category' => 'compression',
            'title' => __('启用GZIP/Brotli压缩', 'wpforge'),
            'description' => __('压缩文本资源可以减少传输大小，加快加载速度', 'wpforge'),
            'priority' => 'medium',
            'tools' => array('.htaccess配置', 'Nginx配置', 'CDN配置')
        );
        
        // 字体优化
        $suggestions[] = array(
            'category' => 'fonts',
            'title' => __('字体优化', 'wpforge'),
            'description' => __('字体预加载、子集化可以减少字体文件大小，加快渲染', 'wpforge'),
            'priority' => 'low',
            'tools' => array('font-display: swap', '字体子集化工具')
        );
        
        return $suggestions;
    }
    
    /**
     * 获取网站性能数据
     */
    public function get_performance_data() {
        $data = array(
            'php_version' => phpversion(),
            'wp_version' => get_bloginfo('version'),
            'memory_limit' => ini_get('memory_limit'),
            'max_execution_time' => ini_get('max_execution_time'),
            'upload_max_filesize' => ini_get('upload_max_filesize'),
            'post_max_size' => ini_get('post_max_size'),
            'active_plugins' => count(get_option('active_plugins', array())),
            'total_posts' => wp_count_posts()->publish,
            'total_pages' => wp_count_posts('page')->publish,
            'total_comments' => wp_count_comments()->total_comments
        );
        
        // 数据库大小
        global $wpdb;
        $db_size = $wpdb->get_var("SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) FROM information_schema.tables WHERE table_schema = DATABASE()");
        $data['database_size_mb'] = $db_size;
        
        return $data;
    }
}
