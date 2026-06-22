<?php
/**
 * SEO优化类
 */

// 防止直接访问
if (!defined('ABSPATH')) {
    exit;
}

class WPForge_SEO {
    
    /**
     * 构造函数
     */
    public function __construct() {
        if (get_option('wpforge_seo_enabled', 1)) {
            $this->init_hooks();
        }
    }
    
    /**
     * 初始化钩子
     */
    private function init_hooks() {
        // 标题优化
        add_filter('pre_get_document_title', array($this, 'optimize_title'), 10, 1);
        
        // Meta描述
        add_action('wp_head', array($this, 'add_meta_description'), 5);
        
        // Canonical标签
        add_action('wp_head', array($this, 'add_canonical'), 5);
        
        // Open Graph标签
        add_action('wp_head', array($this, 'add_og_tags'), 5);
        
        // 结构化数据
        add_action('wp_footer', array($this, 'add_structured_data'));
        
        // 图片alt属性优化
        add_filter('wp_get_attachment_image_attributes', array($this, 'optimize_image_alt'), 10, 3);
        
        // 内容SEO优化
        add_filter('the_content', array($this, 'optimize_content_seo'));
    }
    
    /**
     * 优化页面标题
     */
    public function optimize_title($title) {
        if (is_single() || is_page()) {
            global $post;
            
            // 获取自定义SEO标题
            $seo_title = get_post_meta($post->ID, '_wpforge_seo_title', true);
            
            if ($seo_title) {
                return $seo_title;
            }
        }
        
        return $title;
    }
    
    /**
     * 添加Meta描述
     */
    public function add_meta_description() {
        $description = '';
        
        if (is_single() || is_page()) {
            global $post;
            
            // 获取自定义描述
            $description = get_post_meta($post->ID, '_wpforge_meta_description', true);
            
            if (!$description) {
                // 从内容生成摘要
                $description = wp_trim_words($post->post_content, 30, '...');
            }
        } elseif (is_category() || is_tag() || is_tax()) {
            $term = get_queried_object();
            $description = term_description($term->term_id, $term->taxonomy);
        } elseif (is_home() || is_front_page()) {
            $description = get_bloginfo('description');
        }
        
        if ($description) {
            echo '<meta name="description" content="' . esc_attr($description) . '" />' . "\n";
        }
    }
    
    /**
     * 添加Canonical标签
     */
    public function add_canonical() {
        $canonical = '';
        
        if (is_single() || is_page()) {
            $canonical = get_permalink();
        } elseif (is_category()) {
            $canonical = get_category_link(get_query_var('cat'));
        } elseif (is_tag()) {
            $canonical = get_tag_link(get_query_var('tag_id'));
        } elseif (is_home()) {
            $canonical = home_url('/');
        }
        
        if ($canonical) {
            echo '<link rel="canonical" href="' . esc_url($canonical) . '" />' . "\n";
        }
    }
    
    /**
     * 添加Open Graph标签
     */
    public function add_og_tags() {
        global $post;
        
        $og_tags = array();
        
        // OG: Title
        if (is_single() || is_page()) {
            $og_tags['og:title'] = get_the_title($post->ID);
        } else {
            $og_tags['og:title'] = get_bloginfo('name');
        }
        
        // OG: Description
        if (is_single() || is_page()) {
            $og_tags['og:description'] = wp_trim_words($post->post_content, 20, '...');
        } else {
            $og_tags['og:description'] = get_bloginfo('description');
        }
        
        // OG: Type
        if (is_single()) {
            $og_tags['og:type'] = 'article';
        } elseif (is_product()) {
            $og_tags['og:type'] = 'product';
        } else {
            $og_tags['og:type'] = 'website';
        }
        
        // OG: URL
        $og_tags['og:url'] = home_url($_SERVER['REQUEST_URI']);
        
        // OG: Site Name
        $og_tags['og:site_name'] = get_bloginfo('name');
        
        // OG: Image
        if (is_single() || is_page()) {
            if (has_post_thumbnail($post->ID)) {
                $thumbnail = wp_get_attachment_image_src(get_post_thumbnail_id($post->ID), 'large');
                if ($thumbnail) {
                    $og_tags['og:image'] = $thumbnail[0];
                }
            }
        }
        
        // 输出OG标签
        foreach ($og_tags as $property => $content) {
            if ($content) {
                echo '<meta property="' . esc_attr($property) . '" content="' . esc_attr($content) . '" />' . "\n";
            }
        }
    }
    
    /**
     * 添加结构化数据
     */
    public function add_structured_data() {
        $schema = array();
        
        if (is_single() && !is_product()) {
            // 文章结构化数据
            global $post;
            
            $schema = array(
                '@context' => 'https://schema.org',
                '@type' => 'Article',
                'headline' => get_the_title($post->ID),
                'datePublished' => get_the_date('c', $post->ID),
                'dateModified' => get_the_modified_date('c', $post->ID),
                'author' => array(
                    '@type' => 'Person',
                    'name' => get_the_author_meta('display_name', $post->post_author)
                ),
                'publisher' => array(
                    '@type' => 'Organization',
                    'name' => get_bloginfo('name')
                )
            );
            
            // 添加特色图片
            if (has_post_thumbnail($post->ID)) {
                $thumbnail = wp_get_attachment_image_src(get_post_thumbnail_id($post->ID), 'large');
                if ($thumbnail) {
                    $schema['image'] = $thumbnail[0];
                }
            }
            
        } elseif (is_product()) {
            // 产品结构化数据
            global $product;
            
            if ($product) {
                $schema = array(
                    '@context' => 'https://schema.org',
                    '@type' => 'Product',
                    'name' => $product->get_name(),
                    'description' => wp_strip_all_tags($product->get_short_description()),
                    'sku' => $product->get_sku(),
                    'offers' => array(
                        '@type' => 'Offer',
                        'price' => $product->get_price(),
                        'priceCurrency' => get_woocommerce_currency(),
                        'availability' => $product->is_in_stock() ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock'
                    )
                );
                
                // 添加产品图片
                $image_id = $product->get_image_id();
                if ($image_id) {
                    $image = wp_get_attachment_image_src($image_id, 'large');
                    if ($image) {
                        $schema['image'] = $image[0];
                    }
                }
                
                // 添加品牌
                $brand = $product->get_meta('_brand');
                if ($brand) {
                    $schema['brand'] = array(
                        '@type' => 'Brand',
                        'name' => $brand
                    );
                }
            }
        }
        
        if (!empty($schema)) {
            echo '<script type="application/ld+json">' . json_encode($schema, JSON_UNESCAPED_UNICODE) . '</script>' . "\n";
        }
    }
    
    /**
     * 优化图片alt属性
     */
    public function optimize_image_alt($attr, $attachment, $size) {
        // 如果没有alt属性，使用图片标题
        if (empty($attr['alt'])) {
            $attr['alt'] = get_the_title($attachment->ID);
        }
        
        return $attr;
    }
    
    /**
     * 优化内容SEO
     */
    public function optimize_content_seo($content) {
        // 确保内容中有内部链接的机会
        // 这里可以添加更多的SEO优化逻辑
        
        return $content;
    }
    
    /**
     * 生成SEO标题
     */
    public function generate_seo_title($content, $keywords = array()) {
        // 简化的标题生成逻辑
        $title = wp_trim_words($content, 10, '');
        
        if (!empty($keywords)) {
            $title = $keywords[0] . ' - ' . $title;
        }
        
        // 确保标题长度在30-60字符之间
        if (mb_strlen($title) > 60) {
            $title = mb_substr($title, 0, 57) . '...';
        }
        
        return $title;
    }
    
    /**
     * 生成Meta描述
     */
    public function generate_meta_description($content, $keywords = array()) {
        // 简化的描述生成逻辑
        $description = wp_trim_words($content, 25, '...');
        
        // 确保描述长度在70-160字符之间
        if (mb_strlen($description) > 160) {
            $description = mb_substr($description, 0, 157) . '...';
        }
        
        return $description;
    }
    
    /**
     * 分析页面SEO
     */
    public function analyze_seo($post_id) {
        $post = get_post($post_id);
        
        if (!$post) {
            return new WP_Error('invalid_post', __('无效的文章ID', 'wpforge'));
        }
        
        $analysis = array(
            'overall_score' => 0,
            'issues' => array(),
            'recommendations' => array()
        );
        
        $score = 100;
        
        // 检查标题
        $title = get_the_title($post_id);
        $title_length = mb_strlen($title);
        
        if ($title_length < 30) {
            $score -= 10;
            $analysis['issues'][] = array(
                'type' => 'title',
                'severity' => 'warning',
                'message' => sprintf(__('标题过短: %d字符，建议30-60字符', 'wpforge'), $title_length)
            );
        } elseif ($title_length > 60) {
            $score -= 10;
            $analysis['issues'][] = array(
                'type' => 'title',
                'severity' => 'warning',
                'message' => sprintf(__('标题过长: %d字符，建议30-60字符', 'wpforge'), $title_length)
            );
        }
        
        // 检查Meta描述
        $meta_description = get_post_meta($post_id, '_wpforge_meta_description', true);
        if (!$meta_description) {
            $score -= 15;
            $analysis['issues'][] = array(
                'type' => 'description',
                'severity' => 'error',
                'message' => __('缺少meta description', 'wpforge')
            );
        }
        
        // 检查内容长度
        $content_length = mb_strlen(wp_strip_all_tags($post->post_content));
        if ($content_length < 300) {
            $score -= 15;
            $analysis['issues'][] = array(
                'type' => 'content',
                'severity' => 'warning',
                'message' => sprintf(__('内容较少: %d字，建议至少300字', 'wpforge'), $content_length)
            );
        }
        
        // 检查H1标签
        if (substr_count($post->post_content, '<h1') > 1) {
            $score -= 10;
            $analysis['issues'][] = array(
                'type' => 'headings',
                'severity' => 'warning',
                'message' => __('有多个H1标题，建议只有1个', 'wpforge')
            );
        }
        
        // 检查图片alt属性
        $images = preg_match_all('/<img[^>]+>/i', $post->post_content, $matches);
        $missing_alt = 0;
        
        if ($images > 0) {
            foreach ($matches[0] as $img) {
                if (!preg_match('/alt\s*=\s*["\'][^"\']+["\']/i', $img)) {
                    $missing_alt++;
                }
            }
        }
        
        if ($missing_alt > 0) {
            $score -= 5;
            $analysis['issues'][] = array(
                'type' => 'images',
                'severity' => 'warning',
                'message' => sprintf(__('有%d张图片缺少alt属性', 'wpforge'), $missing_alt)
            );
        }
        
        $analysis['overall_score'] = max(0, $score);
        
        return $analysis;
    }
}
