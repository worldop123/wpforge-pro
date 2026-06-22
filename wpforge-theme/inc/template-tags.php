<?php
/**
 * WPForge Theme - Template Tags
 *
 * 自定义模板标签函数，供模板文件使用
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

// Exit if accessed directly.
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Display site logo.
 *
 * @since 1.0.0
 */
function wpforge_site_logo() {
    if (has_custom_logo()) {
        the_custom_logo();
    } else {
        echo '<a href="' . esc_url(home_url('/')) . '" class="wpforge-site-title" rel="home">';
        echo esc_html(get_bloginfo('name'));
        echo '</a>';
    }
}

/**
 * Display site description.
 *
 * @since 1.0.0
 */
function wpforge_site_description() {
    $description = get_bloginfo('description', 'display');
    if ($description || is_customize_preview()) {
        echo '<p class="wpforge-site-description">' . esc_html($description) . '</p>';
    }
}

/**
 * Display primary navigation.
 *
 * @since 1.0.0
 */
function wpforge_primary_navigation() {
    if (has_nav_menu('primary')) {
        wp_nav_menu(array(
            'theme_location' => 'primary',
            'menu_class'     => 'wpforge-nav-menu',
            'container'      => 'nav',
            'container_class' => 'wpforge-primary-navigation',
            'depth'          => 3,
            'fallback_cb'    => 'wpforge_nav_fallback',
        ));
    } else {
        wpforge_nav_fallback();
    }
}

/**
 * Display mobile navigation.
 *
 * @since 1.0.0
 */
function wpforge_mobile_navigation() {
    echo '<div class="wpforge-mobile-menu-toggle" aria-label="' . esc_attr__('Toggle menu', 'wpforge-theme') . '">';
    echo '<span></span><span></span><span></span>';
    echo '</div>';

    if (has_nav_menu('mobile') || has_nav_menu('primary')) {
        wp_nav_menu(array(
            'theme_location' => has_nav_menu('mobile') ? 'mobile' : 'primary',
            'menu_class'     => 'wpforge-mobile-menu',
            'container'      => 'nav',
            'container_class' => 'wpforge-mobile-navigation',
            'depth'          => 2,
            'fallback_cb'    => 'wpforge_nav_fallback',
        ));
    }
}

/**
 * Navigation fallback menu.
 *
 * @since 1.0.0
 */
function wpforge_nav_fallback() {
    echo '<nav class="wpforge-nav-fallback">';
    echo '<ul class="wpforge-nav-menu">';
    echo '<li><a href="' . esc_url(home_url('/')) . '">' . esc_html__('Home', 'wpforge-theme') . '</a></li>';
    
    if (current_user_can('manage_options')) {
        echo '<li><a href="' . esc_url(admin_url('nav-menus.php')) . '">' . esc_html__('Add Menu', 'wpforge-theme') . '</a></li>';
    }
    
    echo '</ul>';
    echo '</nav>';
}

/**
 * Display footer navigation.
 *
 * @since 1.0.0
 */
function wpforge_footer_navigation() {
    if (has_nav_menu('footer')) {
        wp_nav_menu(array(
            'theme_location' => 'footer',
            'menu_class'     => 'wpforge-footer-menu',
            'container'      => false,
            'depth'          => 1,
            'fallback_cb'    => false,
        ));
    }
}

/**
 * Display breadcrumb navigation.
 *
 * @since 1.0.0
 */
function wpforge_breadcrumb() {
    if (!get_theme_mod('wpforge_breadcrumb_enabled', true)) {
        return;
    }

    if (is_front_page()) {
        return;
    }

    $items = array();
    $separator = get_theme_mod('wpforge_breadcrumb_separator', '›');

    // Home.
    $items[] = array(
        'url'   => home_url('/'),
        'title' => __('Home', 'wpforge-theme'),
    );

    if (is_category() || is_single()) {
        // Category.
        $categories = get_the_category();
        if ($categories) {
            $category = $categories[0];
            $items[] = array(
                'url'   => get_category_link($category),
                'title' => $category->name,
            );
        }

        if (is_single()) {
            $items[] = array(
                'title' => get_the_title(),
            );
        }
    } elseif (is_page()) {
        // Parent pages.
        $post = get_post();
        if ($post->post_parent) {
            $ancestors = array_reverse(get_post_ancestors($post->ID));
            foreach ($ancestors as $ancestor) {
                $items[] = array(
                    'url'   => get_permalink($ancestor),
                    'title' => get_the_title($ancestor),
                );
            }
        }

        $items[] = array(
            'title' => get_the_title(),
        );
    } elseif (is_tag()) {
        $items[] = array(
            'title' => single_tag_title('', false),
        );
    } elseif (is_author()) {
        $items[] = array(
            'title' => get_the_author(),
        );
    } elseif (is_date()) {
        if (is_year()) {
            $items[] = array(
                'title' => get_the_date('Y'),
            );
        } elseif (is_month()) {
            $items[] = array(
                'url'   => get_year_link(get_the_date('Y')),
                'title' => get_the_date('Y'),
            );
            $items[] = array(
                'title' => get_the_date('F'),
            );
        } elseif (is_day()) {
            $items[] = array(
                'url'   => get_year_link(get_the_date('Y')),
                'title' => get_the_date('Y'),
            );
            $items[] = array(
                'url'   => get_month_link(get_the_date('Y'), get_the_date('m')),
                'title' => get_the_date('F'),
            );
            $items[] = array(
                'title' => get_the_date('j'),
            );
        }
    } elseif (is_search()) {
        $items[] = array(
            'title' => __('Search Results', 'wpforge-theme'),
        );
    } elseif (is_404()) {
        $items[] = array(
            'title' => __('Page Not Found', 'wpforge-theme'),
        );
    } elseif (function_exists('is_woocommerce') && is_woocommerce()) {
        // Shop page.
        if (is_shop()) {
            $shop_page_id = wc_get_page_id('shop');
            if ($shop_page_id) {
                $items[] = array(
                    'title' => get_the_title($shop_page_id),
                );
            }
        } elseif (is_product_category()) {
            $shop_page_id = wc_get_page_id('shop');
            if ($shop_page_id) {
                $items[] = array(
                    'url'   => get_permalink($shop_page_id),
                    'title' => get_the_title($shop_page_id),
                );
            }

            $category = get_queried_object();
            $items[] = array(
                'title' => $category->name,
            );
        } elseif (is_product()) {
            $shop_page_id = wc_get_page_id('shop');
            if ($shop_page_id) {
                $items[] = array(
                    'url'   => get_permalink($shop_page_id),
                    'title' => get_the_title($shop_page_id),
                );
            }

            $items[] = array(
                'title' => get_the_title(),
            );
        }
    }

    // Allow filtering.
    $items = apply_filters('wpforge_breadcrumb_items', $items);

    if (empty($items)) {
        return;
    }

    echo '<nav class="wpforge-breadcrumb" aria-label="' . esc_attr__('Breadcrumb', 'wpforge-theme') . '">';
    echo '<ol class="wpforge-breadcrumb-list">';

    $total = count($items);
    foreach ($items as $index => $item) {
        $class = 'wpforge-breadcrumb-item';
        if ($index === $total - 1) {
            $class .= ' current';
        }

        echo '<li class="' . esc_attr($class) . '">';

        if (!empty($item['url']) && $index !== $total - 1) {
            echo '<a href="' . esc_url($item['url']) . '">' . esc_html($item['title']) . '</a>';
        } else {
            echo '<span>' . esc_html($item['title']) . '</span>';
        }

        if ($index < $total - 1) {
            echo '<span class="wpforge-breadcrumb-separator">' . esc_html($separator) . '</span>';
        }

        echo '</li>';
    }

    echo '</ol>';
    echo '</nav>';
}

/**
 * Display post meta information.
 *
 * @since 1.0.0
 */
function wpforge_post_meta() {
    $show_category = get_theme_mod('wpforge_show_category', true);
    $show_date     = get_theme_mod('wpforge_show_date', true);
    $show_author   = get_theme_mod('wpforge_show_author', true);
    $show_comments = get_theme_mod('wpforge_show_comments', true);

    echo '<div class="wpforge-post-meta">';

    if ($show_category) {
        echo '<span class="wpforge-post-categories">';
        the_category(', ');
        echo '</span>';
    }

    if ($show_date) {
        echo '<span class="wpforge-post-date">';
        echo '<time datetime="' . esc_attr(get_the_date('c')) . '">' . esc_html(get_the_date()) . '</time>';
        echo '</span>';
    }

    if ($show_author) {
        echo '<span class="wpforge-post-author">';
        echo '<a href="' . esc_url(get_author_posts_url(get_the_author_meta('ID'))) . '">';
        echo esc_html(get_the_author());
        echo '</a>';
        echo '</span>';
    }

    if ($show_comments && !post_password_required() && (comments_open() || get_comments_number())) {
        echo '<span class="wpforge-post-comments">';
        comments_popup_link(
            __('0 Comments', 'wpforge-theme'),
            __('1 Comment', 'wpforge-theme'),
            __('% Comments', 'wpforge-theme')
        );
        echo '</span>';
    }

    echo '</div>';
}

/**
 * Display single post meta.
 *
 * @since 1.0.0
 */
function wpforge_single_post_meta() {
    $show_category = get_theme_mod('wpforge_single_show_category', true);
    $show_date     = get_theme_mod('wpforge_single_show_date', true);
    $show_author   = get_theme_mod('wpforge_single_show_author', true);
    $show_tags     = get_theme_mod('wpforge_single_show_tags', true);

    echo '<div class="wpforge-single-meta">';

    if ($show_category) {
        echo '<span class="wpforge-post-categories">';
        the_category(', ');
        echo '</span>';
    }

    if ($show_date) {
        echo '<span class="wpforge-post-date">';
        echo '<time datetime="' . esc_attr(get_the_date('c')) . '">' . esc_html(get_the_date()) . '</time>';
        echo '</span>';
    }

    if ($show_author) {
        echo '<span class="wpforge-post-author">';
        echo '<a href="' . esc_url(get_author_posts_url(get_the_author_meta('ID'))) . '">';
        echo esc_html(get_the_author());
        echo '</a>';
        echo '</span>';
    }

    if ($show_tags && has_tag()) {
        echo '<span class="wpforge-post-tags">';
        the_tags('', ', ', '');
        echo '</span>';
    }

    echo '</div>';
}

/**
 * Display featured image.
 *
 * @since 1.0.0
 * @param string $size Image size.
 */
function wpforge_featured_image($size = 'large') {
    if (!has_post_thumbnail()) {
        return;
    }

    echo '<div class="wpforge-featured-image">';
    echo '<a href="' . esc_url(get_permalink()) . '" aria-hidden="true" tabindex="-1">';
    the_post_thumbnail($size, array('loading' => 'lazy'));
    echo '</a>';
    echo '</div>';
}

/**
 * Display read more link.
 *
 * @since 1.0.0
 */
function wpforge_read_more() {
    $read_more_text = get_theme_mod('wpforge_read_more_text', __('Read More', 'wpforge-theme'));
    $read_more_text = apply_filters('wpforge_read_more_text', $read_more_text);

    echo '<div class="wpforge-read-more-wrapper">';
    echo '<a href="' . esc_url(get_permalink()) . '" class="wpforge-btn wpforge-btn-text">';
    echo esc_html($read_more_text);
    echo '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>';
    echo '</a>';
    echo '</div>';
}

/**
 * Display pagination.
 *
 * @since 1.0.0
 */
function wpforge_pagination() {
    the_posts_pagination(array(
        'mid_size'  => 2,
        'prev_text' => __('Previous', 'wpforge-theme'),
        'next_text' => __('Next', 'wpforge-theme'),
    ));
}

/**
 * Display footer widgets.
 *
 * @since 1.0.0
 */
function wpforge_footer_widgets() {
    $columns = get_theme_mod('wpforge_footer_columns', 4);

    if ($columns < 1) {
        return;
    }

    $has_widgets = false;
    for ($i = 1; $i <= $columns; $i++) {
        if (is_active_sidebar('footer-' . $i)) {
            $has_widgets = true;
            break;
        }
    }

    if (!$has_widgets) {
        return;
    }

    echo '<div class="wpforge-footer-widgets wpforge-footer-columns-' . esc_attr($columns) . '">';
    echo '<div class="wpforge-container">';

    for ($i = 1; $i <= $columns; $i++) {
        if (is_active_sidebar('footer-' . $i)) {
            echo '<div class="wpforge-footer-column">';
            dynamic_sidebar('footer-' . $i);
            echo '</div>';
        }
    }

    echo '</div>';
    echo '</div>';
}

/**
 * Display footer bottom bar.
 *
 * @since 1.0.0
 */
function wpforge_footer_bottom_bar() {
    if (!get_theme_mod('wpforge_footer_bottom_bar', true)) {
        return;
    }

    echo '<div class="wpforge-footer-bottom">';
    echo '<div class="wpforge-container">';

    // Copyright.
    $copyright_text = get_theme_mod('wpforge_copyright_text', '');
    if (empty($copyright_text)) {
        $copyright_text = sprintf(
            /* translators: %s: Site name */
            __('© %s. All rights reserved.', 'wpforge-theme'),
            get_bloginfo('name')
        );
    }
    $copyright_text = apply_filters('wpforge_copyright_text', $copyright_text);

    echo '<div class="wpforge-copyright">';
    echo wp_kses_post($copyright_text);
    echo '</div>';

    // Footer menu.
    if (has_nav_menu('footer')) {
        echo '<div class="wpforge-footer-menu-wrapper">';
        wpforge_footer_navigation();
        echo '</div>';
    }

    echo '</div>';
    echo '</div>';
}

/**
 * Display search form.
 *
 * @since 1.0.0
 */
function wpforge_search_form() {
    get_search_form();
}

/**
 * Display post format icon.
 *
 * @since 1.0.0
 */
function wpforge_post_format_icon() {
    $format = get_post_format();
    if (!$format) {
        $format = 'standard';
    }

    $icons = array(
        'standard' => '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>',
        'image'    => '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>',
        'video'    => '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg>',
        'audio'    => '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"></path><circle cx="6" cy="18" r="3"></circle><circle cx="18" cy="16" r="3"></circle></svg>',
        'gallery'  => '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>',
        'quote'    => '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z"></path><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z"></path></svg>',
        'link'     => '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>',
        'aside'    => '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>',
        'status'   => '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>',
        'chat'     => '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>',
    );

    if (isset($icons[$format])) {
        echo '<span class="wpforge-post-format-icon wpforge-post-format-' . esc_attr($format) . '">';
        echo $icons[$format]; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
        echo '</span>';
    }
}

/**
 * Display related posts.
 *
 * @since 1.0.0
 */
function wpforge_related_posts() {
    $count = get_theme_mod('wpforge_related_count', 3);

    $args = array(
        'posts_per_page'      => $count,
        'post__not_in'        => array(get_the_ID()),
        'ignore_sticky_posts' => 1,
        'orderby'             => 'rand',
    );

    // Try to get related posts by category.
    $categories = wp_get_post_categories(get_the_ID());
    if ($categories) {
        $args['category__in'] = $categories;
    }

    // Try to get related posts by tag.
    $tags = wp_get_post_tags(get_the_ID(), array('fields' => 'ids'));
    if ($tags) {
        $args['tag__in'] = $tags;
    }

    $args = apply_filters('wpforge_related_posts_args', $args);

    $related = new WP_Query($args);

    if (!$related->have_posts()) {
        return;
    }

    echo '<div class="wpforge-related-posts">';
    echo '<h3 class="wpforge-related-title">' . esc_html__('Related Posts', 'wpforge-theme') . '</h3>';
    echo '<div class="wpforge-related-grid">';

    while ($related->have_posts()) {
        $related->the_post();

        echo '<article class="wpforge-related-item">';

        if (has_post_thumbnail()) {
            echo '<div class="wpforge-related-thumbnail">';
            echo '<a href="' . esc_url(get_permalink()) . '">';
            the_post_thumbnail('medium', array('loading' => 'lazy'));
            echo '</a>';
            echo '</div>';
        }

        echo '<div class="wpforge-related-content">';
        echo '<h4 class="wpforge-related-post-title">';
        echo '<a href="' . esc_url(get_permalink()) . '">' . esc_html(get_the_title()) . '</a>';
        echo '</h4>';
        echo '<div class="wpforge-related-date">' . esc_html(get_the_date()) . '</div>';
        echo '</div>';

        echo '</article>';
    }

    echo '</div>';
    echo '</div>';

    wp_reset_postdata();
}

/**
 * Display author box.
 *
 * @since 1.0.0
 */
function wpforge_author_box() {
    $author_id = get_the_author_meta('ID');
    $author_description = get_the_author_meta('description');

    echo '<div class="wpforge-author-box">';
    echo '<div class="wpforge-author-avatar">';
    echo get_avatar($author_id, 80);
    echo '</div>';

    echo '<div class="wpforge-author-info">';
    echo '<h4 class="wpforge-author-name">';
    echo '<a href="' . esc_url(get_author_posts_url($author_id)) . '">';
    echo esc_html(get_the_author());
    echo '</a>';
    echo '</h4>';

    if ($author_description) {
        echo '<div class="wpforge-author-description">';
        echo wp_kses_post($author_description);
        echo '</div>';
    }

    echo '</div>';
    echo '</div>';
}

/**
 * Display 404 content.
 *
 * @since 1.0.0
 */
function wpforge_404_content() {
    echo '<div class="wpforge-404-content">';
    echo '<h1 class="wpforge-404-title">404</h1>';
    echo '<p class="wpforge-404-message">' . esc_html__('Oops! The page you are looking for does not exist.', 'wpforge-theme') . '</p>';
    echo '<div class="wpforge-404-search">';
    get_search_form();
    echo '</div>';
    echo '<a href="' . esc_url(home_url('/')) . '" class="wpforge-btn wpforge-btn-primary">';
    echo esc_html__('Back to Home', 'wpforge-theme');
    echo '</a>';
    echo '</div>';
}

/**
 * Display no posts content.
 *
 * @since 1.0.0
 */
function wpforge_no_posts_content() {
    echo '<div class="wpforge-no-posts">';
    echo '<h2>' . esc_html__('Nothing Found', 'wpforge-theme') . '</h2>';
    echo '<p>' . esc_html__('It seems we can&rsquo;t find what you&rsquo;re looking for. Perhaps searching can help.', 'wpforge-theme') . '</p>';
    get_search_form();
    echo '</div>';
}
