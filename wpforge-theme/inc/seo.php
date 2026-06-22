<?php
/**
 * WPForge Theme - SEO Optimization Module
 *
 * 内置SEO优化功能，无需额外SEO插件
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

// Exit if accessed directly.
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Initialize SEO module.
 *
 * @since 1.0.0
 */
function wpforge_seo_init() {
    if (!get_theme_mod('wpforge_seo_enabled', true)) {
        return;
    }

    // Title optimization.
    add_filter('pre_get_document_title', 'wpforge_seo_title', 10);
    add_filter('document_title_separator', 'wpforge_seo_title_separator');

    // Meta tags.
    add_action('wp_head', 'wpforge_seo_meta_description', 5);
    add_action('wp_head', 'wpforge_seo_meta_keywords', 6);
    add_action('wp_head', 'wpforge_seo_canonical', 7);
    add_action('wp_head', 'wpforge_seo_prev_next', 8);

    // Schema structured data.
    if (get_theme_mod('wpforge_schema_enabled', true)) {
        add_action('wp_head', 'wpforge_seo_schema', 10);
    }

    // Open Graph.
    if (get_theme_mod('wpforge_open_graph_enabled', true)) {
        add_action('wp_head', 'wpforge_seo_open_graph', 15);
    }

    // Twitter Cards.
    if (get_theme_mod('wpforge_twitter_cards_enabled', true)) {
        add_action('wp_head', 'wpforge_seo_twitter_cards', 16);
    }

    // Image ALT auto-generation.
    add_filter('wp_get_attachment_image_attributes', 'wpforge_seo_image_alt', 10, 3);

    // Robots meta.
    add_action('wp_head', 'wpforge_seo_robots', 9);
}
add_action('wp', 'wpforge_seo_init');

/**
 * SEO Title optimization.
 *
 * @since 1.0.0
 * @param string $title Default title.
 * @return string Modified title.
 */
function wpforge_seo_title($title) {
    // Allow filtering.
    $title = apply_filters('wpforge_seo_title', $title);

    // Custom title for single posts/pages.
    if (is_singular()) {
        $custom_title = get_post_meta(get_the_ID(), '_wpforge_seo_title', true);
        if ($custom_title) {
            return $custom_title;
        }
    }

    return $title;
}

/**
 * SEO Title separator.
 *
 * @since 1.0.0
 * @param string $separator Default separator.
 * @return string Modified separator.
 */
function wpforge_seo_title_separator($separator) {
    $custom_separator = get_theme_mod('wpforge_title_separator', '-');
    return $custom_separator ? $custom_separator : $separator;
}

/**
 * Output meta description.
 *
 * @since 1.0.0
 */
function wpforge_seo_meta_description() {
    $description = '';

    if (is_singular()) {
        // Custom description.
        $custom_desc = get_post_meta(get_the_ID(), '_wpforge_seo_description', true);
        if ($custom_desc) {
            $description = $custom_desc;
        } else {
            // Auto-generate from excerpt or content.
            if (has_excerpt()) {
                $description = wp_strip_all_tags(get_the_excerpt());
            } else {
                $description = wp_strip_all_tags(get_the_content());
                $description = wp_trim_words($description, 30);
            }
        }
    } elseif (is_category() || is_tag() || is_tax()) {
        $term_description = term_description();
        if ($term_description) {
            $description = wp_strip_all_tags($term_description);
        } else {
            $description = single_term_title('', false);
        }
    } elseif (is_author()) {
        $author_description = get_the_author_meta('description');
        if ($author_description) {
            $description = wp_strip_all_tags($author_description);
        } else {
            $description = get_the_author();
        }
    } elseif (is_home() && !is_front_page()) {
        $description = get_bloginfo('description');
    } elseif (is_front_page()) {
        $description = get_bloginfo('description');
    }

    // Allow filtering.
    $description = apply_filters('wpforge_seo_description', $description);

    if ($description) {
        echo '<meta name="description" content="' . esc_attr($description) . '">' . "\n";
    }
}

/**
 * Output meta keywords.
 *
 * @since 1.0.0
 */
function wpforge_seo_meta_keywords() {
    $keywords = array();

    if (is_singular()) {
        // Custom keywords.
        $custom_keywords = get_post_meta(get_the_ID(), '_wpforge_seo_keywords', true);
        if ($custom_keywords) {
            $keywords = explode(',', $custom_keywords);
        } else {
            // Auto-generate from tags and categories.
            $tags = get_the_tags();
            if ($tags) {
                foreach ($tags as $tag) {
                    $keywords[] = $tag->name;
                }
            }

            $categories = get_the_category();
            if ($categories) {
                foreach ($categories as $category) {
                    $keywords[] = $category->name;
                }
            }
        }
    } elseif (is_category()) {
        $keywords[] = single_cat_title('', false);
    } elseif (is_tag()) {
        $keywords[] = single_tag_title('', false);
    }

    if (!empty($keywords)) {
        $keywords = array_unique($keywords);
        $keywords = array_slice($keywords, 0, 10); // Limit to 10 keywords.
        echo '<meta name="keywords" content="' . esc_attr(implode(', ', $keywords)) . '">' . "\n";
    }
}

/**
 * Output canonical URL.
 *
 * @since 1.0.0
 */
function wpforge_seo_canonical() {
    $canonical = '';

    if (is_singular()) {
        $canonical = get_permalink();
    } elseif (is_category()) {
        $canonical = get_category_link(get_queried_object_id());
    } elseif (is_tag()) {
        $canonical = get_tag_link(get_queried_object_id());
    } elseif (is_tax()) {
        $canonical = get_term_link(get_queried_object_id());
    } elseif (is_author()) {
        $canonical = get_author_posts_url(get_queried_object_id());
    } elseif (is_home() && !is_front_page()) {
        $canonical = get_permalink(get_option('page_for_posts'));
    } elseif (is_front_page()) {
        $canonical = home_url('/');
    } elseif (is_search()) {
        $canonical = get_search_link();
    }

    if ($canonical) {
        echo '<link rel="canonical" href="' . esc_url($canonical) . '">' . "\n";
    }
}

/**
 * Output prev/next links.
 *
 * @since 1.0.0
 */
function wpforge_seo_prev_next() {
    if (is_singular('post')) {
        // Single post - prev/next.
        $prev_post = get_adjacent_post(false, '', true);
        $next_post = get_adjacent_post(false, '', false);

        if ($prev_post) {
            echo '<link rel="prev" href="' . esc_url(get_permalink($prev_post->ID)) . '">' . "\n";
        }
        if ($next_post) {
            echo '<link rel="next" href="' . esc_url(get_permalink($next_post->ID)) . '">' . "\n";
        }
    } elseif (is_archive() || is_home() || is_search()) {
        // Archive pages - prev/next pages.
        global $paged, $wp_query;

        $max_pages = $wp_query->max_num_pages;

        if ($paged > 1) {
            echo '<link rel="prev" href="' . esc_url(get_pagenum_link($paged - 1)) . '">' . "\n";
        }
        if ($paged < $max_pages) {
            echo '<link rel="next" href="' . esc_url(get_pagenum_link($paged + 1)) . '">' . "\n";
        }
    }
}

/**
 * Output robots meta.
 *
 * @since 1.0.0
 */
function wpforge_seo_robots() {
    $robots = array();

    // Check if noindex is set.
    if (is_singular()) {
        $noindex = get_post_meta(get_the_ID(), '_wpforge_noindex', true);
        $nofollow = get_post_meta(get_the_ID(), '_wpforge_nofollow', true);

        if ($noindex) {
            $robots[] = 'noindex';
        }
        if ($nofollow) {
            $robots[] = 'nofollow';
        }
    }

    // Default: noindex for certain pages.
    if (is_404() || is_paged()) {
        $robots[] = 'noindex';
        $robots[] = 'nofollow';
    }

    if (!empty($robots)) {
        echo '<meta name="robots" content="' . esc_attr(implode(', ', array_unique($robots))) . '">' . "\n";
    }
}

/**
 * Output Schema structured data.
 *
 * @since 1.0.0
 */
function wpforge_seo_schema() {
    $schemas = array();

    // WebSite schema.
    $schemas['website'] = wpforge_get_schema_website();

    // Organization schema.
    $schemas['organization'] = wpforge_get_schema_organization();

    // BreadcrumbList schema.
    if (get_theme_mod('wpforge_breadcrumb_enabled', true) && !is_front_page()) {
        $schemas['breadcrumb'] = wpforge_get_schema_breadcrumb();
    }

    // Article/BlogPosting schema.
    if (is_singular('post')) {
        $schemas['article'] = wpforge_get_schema_article();
    }

    // Product schema (WooCommerce).
    if (function_exists('is_product') && is_product()) {
        $schemas['product'] = wpforge_get_schema_product();
    }

    // Allow filtering.
    $schemas = apply_filters('wpforge_schema_data', $schemas, 'all');

    // Output schemas.
    foreach ($schemas as $schema) {
        if ($schema) {
            echo '<script type="application/ld+json">' . wp_json_encode($schema) . '</script>' . "\n";
        }
    }
}

/**
 * Get WebSite schema.
 *
 * @since 1.0.0
 * @return array WebSite schema data.
 */
function wpforge_get_schema_website() {
    $schema = array(
        '@context' => 'https://schema.org',
        '@type'    => 'WebSite',
        'name'     => get_bloginfo('name'),
        'url'      => home_url('/'),
    );

    // Add search action.
    $schema['potentialAction'] = array(
        '@type'       => 'SearchAction',
        'target'      => home_url('/?s={search_term_string}'),
        'query-input' => 'required name=search_term_string',
    );

    return $schema;
}

/**
 * Get Organization schema.
 *
 * @since 1.0.0
 * @return array Organization schema data.
 */
function wpforge_get_schema_organization() {
    $schema = array(
        '@context' => 'https://schema.org',
        '@type'    => 'Organization',
        'name'     => get_bloginfo('name'),
        'url'      => home_url('/'),
    );

    // Add logo if custom logo exists.
    if (has_custom_logo()) {
        $custom_logo_id = get_theme_mod('custom_logo');
        $logo_image = wp_get_attachment_image_src($custom_logo_id, 'full');
        if ($logo_image) {
            $schema['logo'] = $logo_image[0];
        }
    }

    return $schema;
}

/**
 * Get BreadcrumbList schema.
 *
 * @since 1.0.0
 * @return array BreadcrumbList schema data.
 */
function wpforge_get_schema_breadcrumb() {
    $items = array();
    $position = 1;

    // Home.
    $items[] = array(
        '@type'    => 'ListItem',
        'position' => $position++,
        'name'     => __('Home', 'wpforge-theme'),
        'item'     => home_url('/'),
    );

    if (is_category() || is_single()) {
        // Category.
        $categories = get_the_category();
        if ($categories) {
            $category = $categories[0];
            $items[] = array(
                '@type'    => 'ListItem',
                'position' => $position++,
                'name'     => $category->name,
                'item'     => get_category_link($category),
            );
        }

        if (is_single()) {
            $items[] = array(
                '@type'    => 'ListItem',
                'position' => $position,
                'name'     => get_the_title(),
            );
        }
    } elseif (is_page()) {
        // Parent pages.
        $post = get_post();
        if ($post->post_parent) {
            $ancestors = array_reverse(get_post_ancestors($post->ID));
            foreach ($ancestors as $ancestor) {
                $items[] = array(
                    '@type'    => 'ListItem',
                    'position' => $position++,
                    'name'     => get_the_title($ancestor),
                    'item'     => get_permalink($ancestor),
                );
            }
        }

        $items[] = array(
            '@type'    => 'ListItem',
            'position' => $position,
            'name'     => get_the_title(),
        );
    } elseif (is_tag()) {
        $items[] = array(
            '@type'    => 'ListItem',
            'position' => $position,
            'name'     => single_tag_title('', false),
        );
    } elseif (is_search()) {
        $items[] = array(
            '@type'    => 'ListItem',
            'position' => $position,
            'name'     => __('Search Results', 'wpforge-theme'),
        );
    }

    if (count($items) < 2) {
        return null;
    }

    return array(
        '@context'        => 'https://schema.org',
        '@type'           => 'BreadcrumbList',
        'itemListElement' => $items,
    );
}

/**
 * Get Article schema.
 *
 * @since 1.0.0
 * @return array Article schema data.
 */
function wpforge_get_schema_article() {
    global $post;

    $schema = array(
        '@context'         => 'https://schema.org',
        '@type'            => 'BlogPosting',
        'headline'         => get_the_title(),
        'description'      => wp_strip_all_tags(get_the_excerpt()),
        'datePublished'    => get_the_date('c'),
        'dateModified'     => get_the_modified_date('c'),
        'mainEntityOfPage' => get_permalink(),
    );

    // Author.
    $schema['author'] = array(
        '@type' => 'Person',
        'name'  => get_the_author(),
        'url'   => get_author_posts_url(get_the_author_meta('ID')),
    );

    // Publisher.
    $schema['publisher'] = array(
        '@type' => 'Organization',
        'name'  => get_bloginfo('name'),
        'url'   => home_url('/'),
    );

    // Featured image.
    if (has_post_thumbnail()) {
        $image_id = get_post_thumbnail_id();
        $image = wp_get_attachment_image_src($image_id, 'full');
        if ($image) {
            $schema['image'] = array(
                '@type'  => 'ImageObject',
                'url'    => $image[0],
                'width'  => $image[1],
                'height' => $image[2],
            );
        }
    }

    return $schema;
}

/**
 * Get Product schema (WooCommerce).
 *
 * @since 1.0.0
 * @return array Product schema data.
 */
function wpforge_get_schema_product() {
    if (!function_exists('wc_get_product')) {
        return null;
    }

    global $product;
    if (!$product) {
        $product = wc_get_product(get_the_ID());
    }

    if (!$product) {
        return null;
    }

    $schema = array(
        '@context' => 'https://schema.org',
        '@type'    => 'Product',
        'name'     => $product->get_name(),
        'sku'      => $product->get_sku(),
        'url'      => get_permalink(),
    );

    // Description.
    $description = $product->get_short_description();
    if (!$description) {
        $description = $product->get_description();
    }
    if ($description) {
        $schema['description'] = wp_strip_all_tags($description);
    }

    // Image.
    $image_id = $product->get_image_id();
    if ($image_id) {
        $image = wp_get_attachment_image_src($image_id, 'full');
        if ($image) {
            $schema['image'] = $image[0];
        }
    }

    // Price.
    if ($product->is_type('variable')) {
        $prices = $product->get_variation_prices();
        $min_price = $prices['price'][0];
        $max_price = end($prices['price']);

        $schema['offers'] = array(
            '@type'         => 'AggregateOffer',
            'priceCurrency' => get_woocommerce_currency(),
            'lowPrice'      => $min_price,
            'highPrice'     => $max_price,
            'availability'  => $product->is_in_stock() ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock',
            'url'           => get_permalink(),
        );
    } else {
        $schema['offers'] = array(
            '@type'         => 'Offer',
            'priceCurrency' => get_woocommerce_currency(),
            'price'         => $product->get_price(),
            'availability'  => $product->is_in_stock() ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock',
            'url'           => get_permalink(),
            'priceValidUntil' => date('Y-12-31', strtotime('+1 year')),
        );
    }

    // Rating.
    $rating_count = $product->get_rating_count();
    if ($rating_count > 0) {
        $schema['aggregateRating'] = array(
            '@type'       => 'AggregateRating',
            'ratingValue' => $product->get_average_rating(),
            'reviewCount' => $rating_count,
        );
    }

    // Brand.
    $brands = wp_get_post_terms($product->get_id(), 'product_brand', array('fields' => 'names'));
    if (!empty($brands) && !is_wp_error($brands)) {
        $schema['brand'] = array(
            '@type' => 'Brand',
            'name'  => $brands[0],
        );
    }

    return $schema;
}

/**
 * Output Open Graph tags.
 *
 * @since 1.0.0
 */
function wpforge_seo_open_graph() {
    echo '<meta property="og:site_name" content="' . esc_attr(get_bloginfo('name')) . '">' . "\n";
    echo '<meta property="og:locale" content="' . esc_attr(get_locale()) . '">' . "\n";

    if (is_singular()) {
        echo '<meta property="og:type" content="article">' . "\n";
        echo '<meta property="og:title" content="' . esc_attr(get_the_title()) . '">' . "\n";
        echo '<meta property="og:url" content="' . esc_url(get_permalink()) . '">' . "\n";

        // Description.
        if (has_excerpt()) {
            echo '<meta property="og:description" content="' . esc_attr(wp_strip_all_tags(get_the_excerpt())) . '">' . "\n";
        }

        // Image.
        if (has_post_thumbnail()) {
            $image_id = get_post_thumbnail_id();
            $image = wp_get_attachment_image_src($image_id, 'full');
            if ($image) {
                echo '<meta property="og:image" content="' . esc_url($image[0]) . '">' . "\n";
                echo '<meta property="og:image:width" content="' . esc_attr($image[1]) . '">' . "\n";
                echo '<meta property="og:image:height" content="' . esc_attr($image[2]) . '">' . "\n";
            }
        }

        // Article specific.
        if (is_single()) {
            echo '<meta property="article:published_time" content="' . esc_attr(get_the_date('c')) . '">' . "\n";
            echo '<meta property="article:modified_time" content="' . esc_attr(get_the_modified_date('c')) . '">' . "\n";
            echo '<meta property="article:author" content="' . esc_attr(get_the_author()) . '">' . "\n";

            // Categories.
            $categories = get_the_category();
            if ($categories) {
                foreach ($categories as $category) {
                    echo '<meta property="article:section" content="' . esc_attr($category->name) . '">' . "\n";
                }
            }

            // Tags.
            $tags = get_the_tags();
            if ($tags) {
                foreach ($tags as $tag) {
                    echo '<meta property="article:tag" content="' . esc_attr($tag->name) . '">' . "\n";
                }
            }
        }
    } elseif (is_front_page() || is_home()) {
        echo '<meta property="og:type" content="website">' . "\n";
        echo '<meta property="og:title" content="' . esc_attr(get_bloginfo('name')) . '">' . "\n";
        echo '<meta property="og:description" content="' . esc_attr(get_bloginfo('description')) . '">' . "\n";
        echo '<meta property="og:url" content="' . esc_url(home_url('/')) . '">' . "\n";
    } else {
        echo '<meta property="og:type" content="website">' . "\n";
        echo '<meta property="og:title" content="' . esc_attr(wp_title('', false)) . '">' . "\n";
        echo '<meta property="og:url" content="' . esc_url((is_ssl() ? 'https://' : 'http://') . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI']) . '">' . "\n";
    }
}

/**
 * Output Twitter Cards tags.
 *
 * @since 1.0.0
 */
function wpforge_seo_twitter_cards() {
    echo '<meta name="twitter:card" content="summary_large_image">' . "\n";
    echo '<meta name="twitter:site" content="' . esc_attr(get_bloginfo('name')) . '">' . "\n";

    if (is_singular()) {
        echo '<meta name="twitter:title" content="' . esc_attr(get_the_title()) . '">' . "\n";

        if (has_excerpt()) {
            echo '<meta name="twitter:description" content="' . esc_attr(wp_strip_all_tags(get_the_excerpt())) . '">' . "\n";
        }

        if (has_post_thumbnail()) {
            $image_id = get_post_thumbnail_id();
            $image = wp_get_attachment_image_src($image_id, 'full');
            if ($image) {
                echo '<meta name="twitter:image" content="' . esc_url($image[0]) . '">' . "\n";
            }
        }

        echo '<meta name="twitter:creator" content="' . esc_attr(get_the_author()) . '">' . "\n";
    } else {
        echo '<meta name="twitter:title" content="' . esc_attr(get_bloginfo('name')) . '">' . "\n";
        echo '<meta name="twitter:description" content="' . esc_attr(get_bloginfo('description')) . '">' . "\n";
    }
}

/**
 * Auto-generate image ALT text.
 *
 * @since 1.0.0
 * @param array $attr Image attributes.
 * @param WP_Post $attachment Attachment post object.
 * @param string|array $size Image size.
 * @return array Modified image attributes.
 */
function wpforge_seo_image_alt($attr, $attachment, $size) {
    // If ALT is already set, keep it.
    if (!empty($attr['alt'])) {
        return $attr;
    }

    // Use attachment title as ALT.
    $attr['alt'] = wp_strip_all_tags($attachment->post_title);

    return $attr;
}

/**
 * Add SEO meta box to post edit screen.
 *
 * @since 1.0.0
 */
function wpforge_seo_add_meta_box() {
    add_meta_box(
        'wpforge_seo_meta_box',
        __('WPForge SEO Settings', 'wpforge-theme'),
        'wpforge_seo_meta_box_callback',
        array('post', 'page', 'product'),
        'normal',
        'high'
    );
}
add_action('add_meta_boxes', 'wpforge_seo_add_meta_box');

/**
 * SEO meta box callback.
 *
 * @since 1.0.0
 * @param WP_Post $post Post object.
 */
function wpforge_seo_meta_box_callback($post) {
    // Add nonce field.
    wp_nonce_field('wpforge_seo_meta_box', 'wpforge_seo_nonce');

    // Get existing values.
    $seo_title = get_post_meta($post->ID, '_wpforge_seo_title', true);
    $seo_description = get_post_meta($post->ID, '_wpforge_seo_description', true);
    $seo_keywords = get_post_meta($post->ID, '_wpforge_seo_keywords', true);
    $noindex = get_post_meta($post->ID, '_wpforge_noindex', true);
    $nofollow = get_post_meta($post->ID, '_wpforge_nofollow', true);

    ?>
    <div class="wpforge-seo-meta-box">
        <p>
            <label for="wpforge_seo_title"><strong><?php esc_html_e('SEO Title', 'wpforge-theme'); ?></strong></label>
            <input type="text" id="wpforge_seo_title" name="wpforge_seo_title" value="<?php echo esc_attr($seo_title); ?>" class="widefat">
            <span class="description"><?php esc_html_e('Recommended: 50-60 characters', 'wpforge-theme'); ?></span>
        </p>

        <p>
            <label for="wpforge_seo_description"><strong><?php esc_html_e('Meta Description', 'wpforge-theme'); ?></strong></label>
            <textarea id="wpforge_seo_description" name="wpforge_seo_description" rows="3" class="widefat"><?php echo esc_textarea($seo_description); ?></textarea>
            <span class="description"><?php esc_html_e('Recommended: 150-160 characters', 'wpforge-theme'); ?></span>
        </p>

        <p>
            <label for="wpforge_seo_keywords"><strong><?php esc_html_e('Keywords', 'wpforge-theme'); ?></strong></label>
            <input type="text" id="wpforge_seo_keywords" name="wpforge_seo_keywords" value="<?php echo esc_attr($seo_keywords); ?>" class="widefat">
            <span class="description"><?php esc_html_e('Comma-separated keywords', 'wpforge-theme'); ?></span>
        </p>

        <p>
            <label>
                <input type="checkbox" name="wpforge_noindex" value="1" <?php checked($noindex, '1'); ?>>
                <?php esc_html_e('Noindex (discourage search engines from indexing this page)', 'wpforge-theme'); ?>
            </label>
        </p>

        <p>
            <label>
                <input type="checkbox" name="wpforge_nofollow" value="1" <?php checked($nofollow, '1'); ?>>
                <?php esc_html_e('Nofollow (discourage search engines from following links)', 'wpforge-theme'); ?>
            </label>
        </p>
    </div>
    <?php
}

/**
 * Save SEO meta box data.
 *
 * @since 1.0.0
 * @param int $post_id Post ID.
 */
function wpforge_seo_save_meta_box($post_id) {
    // Check if our nonce is set.
    if (!isset($_POST['wpforge_seo_nonce'])) {
        return;
    }

    // Verify that the nonce is valid.
    if (!wp_verify_nonce($_POST['wpforge_seo_nonce'], 'wpforge_seo_meta_box')) {
        return;
    }

    // If this is an autosave, our form has not been submitted, so we don't want to do anything.
    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) {
        return;
    }

    // Check the user's permissions.
    if (isset($_POST['post_type']) && 'page' === $_POST['post_type']) {
        if (!current_user_can('edit_page', $post_id)) {
            return;
        }
    } else {
        if (!current_user_can('edit_post', $post_id)) {
            return;
        }
    }

    // Save SEO title.
    if (isset($_POST['wpforge_seo_title'])) {
        update_post_meta($post_id, '_wpforge_seo_title', sanitize_text_field($_POST['wpforge_seo_title']));
    }

    // Save SEO description.
    if (isset($_POST['wpforge_seo_description'])) {
        update_post_meta($post_id, '_wpforge_seo_description', sanitize_textarea_field($_POST['wpforge_seo_description']));
    }

    // Save SEO keywords.
    if (isset($_POST['wpforge_seo_keywords'])) {
        update_post_meta($post_id, '_wpforge_seo_keywords', sanitize_text_field($_POST['wpforge_seo_keywords']));
    }

    // Save noindex.
    $noindex = isset($_POST['wpforge_noindex']) ? '1' : '0';
    update_post_meta($post_id, '_wpforge_noindex', $noindex);

    // Save nofollow.
    $nofollow = isset($_POST['wpforge_nofollow']) ? '1' : '0';
    update_post_meta($post_id, '_wpforge_nofollow', $nofollow);
}
add_action('save_post', 'wpforge_seo_save_meta_box');
