<?php
/**
 * 产品导入类
 */

// 防止直接访问
if (!defined('ABSPATH')) {
    exit;
}

class WPForge_Product_Importer {
    
    /**
     * 批量导入产品
     */
    public function import_products($products, $options = array()) {
        $defaults = array(
            'update_if_exists' => true,
            'skip_images' => false,
            'delay_between' => 0
        );
        
        $options = wp_parse_args($options, $defaults);
        
        $results = array(
            'total' => count($products),
            'success' => 0,
            'failed' => 0,
            'skipped' => 0,
            'errors' => array(),
            'imported_ids' => array()
        );
        
        foreach ($products as $product_data) {
            try {
                $product_id = $this->import_single_product($product_data, $options);
                
                if ($product_id) {
                    $results['success']++;
                    $results['imported_ids'][] = $product_id;
                } else {
                    $results['skipped']++;
                }
                
            } catch (Exception $e) {
                $results['failed']++;
                $results['errors'][] = array(
                    'sku' => isset($product_data['sku']) ? $product_data['sku'] : '',
                    'error' => $e->getMessage()
                );
            }
            
            if ($options['delay_between'] > 0) {
                usleep($options['delay_between'] * 1000000);
            }
        }
        
        return $results;
    }
    
    /**
     * 导入单个产品
     */
    public function import_single_product($product_data, $options = array()) {
        // 检查WooCommerce是否激活
        if (!class_exists('WooCommerce')) {
            throw new Exception(__('WooCommerce未激活', 'wpforge'));
        }
        
        $sku = isset($product_data['sku']) ? sanitize_text_field($product_data['sku']) : '';
        
        // 检查产品是否已存在
        $existing_product_id = $this->find_product_by_sku($sku);
        
        if ($existing_product_id && !$options['update_if_exists']) {
            return null; // 跳过
        }
        
        if ($existing_product_id) {
            // 更新现有产品
            $product = wc_get_product($existing_product_id);
        } else {
            // 创建新产品
            $product = new WC_Product_Simple();
        }
        
        // 设置产品数据
        if (isset($product_data['title'])) {
            $product->set_name(sanitize_text_field($product_data['title']));
        }
        
        if (isset($product_data['description'])) {
            $product->set_description(wp_kses_post($product_data['description']));
        }
        
        if (isset($product_data['short_description'])) {
            $product->set_short_description(wp_kses_post($product_data['short_description']));
        }
        
        if ($sku) {
            $product->set_sku($sku);
        }
        
        // 价格
        if (isset($product_data['regular_price'])) {
            $product->set_regular_price(floatval($product_data['regular_price']));
        }
        
        if (isset($product_data['sale_price'])) {
            $product->set_sale_price(floatval($product_data['sale_price']));
        }
        
        // 库存
        if (isset($product_data['stock_quantity'])) {
            $product->set_manage_stock(true);
            $product->set_stock_quantity(intval($product_data['stock_quantity']));
        }
        
        if (isset($product_data['in_stock'])) {
            $stock_status = $product_data['in_stock'] ? 'instock' : 'outofstock';
            $product->set_stock_status($stock_status);
        }
        
        // 分类
        if (isset($product_data['categories']) && is_array($product_data['categories'])) {
            $category_ids = array();
            foreach ($product_data['categories'] as $cat_name) {
                $category = $this->get_or_create_category($cat_name);
                if ($category) {
                    $category_ids[] = $category->term_id;
                }
            }
            $product->set_category_ids($category_ids);
        }
        
        // 标签
        if (isset($product_data['tags']) && is_array($product_data['tags'])) {
            $tag_ids = array();
            foreach ($product_data['tags'] as $tag_name) {
                $tag = $this->get_or_create_tag($tag_name);
                if ($tag) {
                    $tag_ids[] = $tag->term_id;
                }
            }
            $product->set_tag_ids($tag_ids);
        }
        
        // 品牌
        if (isset($product_data['brand'])) {
            $product->update_meta_data('_brand', sanitize_text_field($product_data['brand']));
        }
        
        // 属性
        if (isset($product_data['attributes']) && is_array($product_data['attributes'])) {
            $attributes = array();
            foreach ($product_data['attributes'] as $attr_name => $attr_values) {
                $attribute = new WC_Product_Attribute();
                $attribute->set_name(sanitize_text_field($attr_name));
                $attribute->set_options(is_array($attr_values) ? $attr_values : array($attr_values));
                $attribute->set_visible(true);
                $attribute->set_variation(false);
                $attributes[] = $attribute;
            }
            $product->set_attributes($attributes);
        }
        
        // 保存产品
        $product_id = $product->save();
        
        // 导入图片
        if (!$options['skip_images'] && isset($product_data['images']) && is_array($product_data['images'])) {
            $this->import_product_images($product_id, $product_data['images']);
        }
        
        // 设置特色图片
        if (!$options['skip_images'] && isset($product_data['featured_image'])) {
            $this->set_featured_image($product_id, $product_data['featured_image']);
        }
        
        // 元数据
        if (isset($product_data['meta_data']) && is_array($product_data['meta_data'])) {
            foreach ($product_data['meta_data'] as $key => $value) {
                $product->update_meta_data(sanitize_key($key), $value);
            }
            $product->save();
        }
        
        return $product_id;
    }
    
    /**
     * 通过SKU查找产品
     */
    public function find_product_by_sku($sku) {
        if (!$sku) {
            return false;
        }
        
        global $wpdb;
        
        $product_id = $wpdb->get_var($wpdb->prepare(
            "SELECT post_id FROM {$wpdb->postmeta} WHERE meta_key = '_sku' AND meta_value = %s LIMIT 1",
            $sku
        ));
        
        return $product_id ? intval($product_id) : false;
    }
    
    /**
     * 获取或创建产品分类
     */
    public function get_or_create_category($name) {
        $name = sanitize_text_field($name);
        
        $term = get_term_by('name', $name, 'product_cat');
        
        if (!$term || is_wp_error($term)) {
            $result = wp_insert_term($name, 'product_cat');
            if (!is_wp_error($result)) {
                $term = get_term($result['term_id'], 'product_cat');
            }
        }
        
        return $term;
    }
    
    /**
     * 获取或创建产品标签
     */
    public function get_or_create_tag($name) {
        $name = sanitize_text_field($name);
        
        $term = get_term_by('name', $name, 'product_tag');
        
        if (!$term || is_wp_error($term)) {
            $result = wp_insert_term($name, 'product_tag');
            if (!is_wp_error($result)) {
                $term = get_term($result['term_id'], 'product_tag');
            }
        }
        
        return $term;
    }
    
    /**
     * 导入产品图片
     */
    public function import_product_images($product_id, $images) {
        if (!function_exists('media_sideload_image')) {
            require_once(ABSPATH . 'wp-admin/includes/media.php');
            require_once(ABSPATH . 'wp-admin/includes/file.php');
            require_once(ABSPATH . 'wp-admin/includes/image.php');
        }
        
        $gallery_ids = array();
        
        foreach ($images as $index => $image_url) {
            $image_id = media_sideload_image($image_url, $product_id, null, 'id');
            
            if (!is_wp_error($image_id)) {
                if ($index === 0) {
                    // 第一张设为特色图片
                    set_post_thumbnail($product_id, $image_id);
                } else {
                    $gallery_ids[] = $image_id;
                }
            }
        }
        
        // 设置产品图库
        if (!empty($gallery_ids)) {
            update_post_meta($product_id, '_product_image_gallery', implode(',', $gallery_ids));
        }
    }
    
    /**
     * 设置特色图片
     */
    public function set_featured_image($product_id, $image_url) {
        if (!function_exists('media_sideload_image')) {
            require_once(ABSPATH . 'wp-admin/includes/media.php');
            require_once(ABSPATH . 'wp-admin/includes/file.php');
            require_once(ABSPATH . 'wp-admin/includes/image.php');
        }
        
        $image_id = media_sideload_image($image_url, $product_id, null, 'id');
        
        if (!is_wp_error($image_id)) {
            set_post_thumbnail($product_id, $image_id);
        }
    }
    
    /**
     * 获取产品分类列表
     */
    public function get_categories() {
        $categories = get_terms(array(
            'taxonomy' => 'product_cat',
            'hide_empty' => false,
            'number' => 100
        ));
        
        $result = array();
        foreach ($categories as $cat) {
            $result[] = array(
                'id' => $cat->term_id,
                'name' => $cat->name,
                'slug' => $cat->slug,
                'count' => $cat->count,
                'parent' => $cat->parent
            );
        }
        
        return $result;
    }
    
    /**
     * 创建产品分类
     */
    public function create_category($name, $parent_id = 0) {
        $name = sanitize_text_field($name);
        
        $result = wp_insert_term($name, 'product_cat', array(
            'parent' => intval($parent_id)
        ));
        
        if (is_wp_error($result)) {
            return false;
        }
        
        return $result['term_id'];
    }
}
