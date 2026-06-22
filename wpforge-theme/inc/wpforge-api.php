<?php
/**
 * WPForge Theme - WPForge API Integration
 *
 * WPForge系统深度集成，提供REST API、配置导入导出、预设模板等功能
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

// Exit if accessed directly.
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Initialize WPForge API integration.
 *
 * @since 1.0.0
 */
function wpforge_api_init() {
    // Register REST API routes.
    add_action('rest_api_init', 'wpforge_register_api_routes');

    // Add WPForge admin menu.
    add_action('admin_menu', 'wpforge_add_admin_menu');

    // Add admin bar menu.
    add_action('admin_bar_menu', 'wpforge_add_admin_bar_menu', 100);

    // Handle preset import.
    add_action('admin_init', 'wpforge_handle_preset_import');

    // Handle config export.
    add_action('admin_init', 'wpforge_handle_config_export');

    // Handle config import.
    add_action('admin_init', 'wpforge_handle_config_import');
}
add_action('after_setup_theme', 'wpforge_api_init');

/**
 * Register WPForge REST API routes.
 *
 * @since 1.0.0
 */
function wpforge_register_api_routes() {
    // Get theme settings.
    register_rest_route('wpforge/v1', '/theme/settings', array(
        'methods'             => 'GET',
        'callback'            => 'wpforge_api_get_settings',
        'permission_callback' => 'wpforge_api_permission_check',
    ));

    // Update theme settings.
    register_rest_route('wpforge/v1', '/theme/settings', array(
        'methods'             => 'POST',
        'callback'            => 'wpforge_api_update_settings',
        'permission_callback' => 'wpforge_api_permission_check',
    ));

    // Get theme presets.
    register_rest_route('wpforge/v1', '/theme/presets', array(
        'methods'             => 'GET',
        'callback'            => 'wpforge_api_get_presets',
        'permission_callback' => 'wpforge_api_permission_check',
    ));

    // Apply preset.
    register_rest_route('wpforge/v1', '/theme/preset/(?P<preset>[a-zA-Z0-9_-]+)', array(
        'methods'             => 'POST',
        'callback'            => 'wpforge_api_apply_preset',
        'permission_callback' => 'wpforge_api_permission_check',
    ));

    // Export config.
    register_rest_route('wpforge/v1', '/theme/export', array(
        'methods'             => 'GET',
        'callback'            => 'wpforge_api_export_config',
        'permission_callback' => 'wpforge_api_permission_check',
    ));

    // Import config.
    register_rest_route('wpforge/v1', '/theme/import', array(
        'methods'             => 'POST',
        'callback'            => 'wpforge_api_import_config',
        'permission_callback' => 'wpforge_api_permission_check',
    ));

    // Get theme info.
    register_rest_route('wpforge/v1', '/theme/info', array(
        'methods'             => 'GET',
        'callback'            => 'wpforge_api_get_theme_info',
        'permission_callback' => 'wpforge_api_permission_check',
    ));

    // Get performance stats.
    register_rest_route('wpforge/v1', '/theme/performance', array(
        'methods'             => 'GET',
        'callback'            => 'wpforge_api_get_performance_stats',
        'permission_callback' => 'wpforge_api_permission_check',
    ));
}

/**
 * API permission check.
 *
 * @since 1.0.0
 * @return bool Whether user has permission.
 */
function wpforge_api_permission_check() {
    return current_user_can('edit_theme_options');
}

/**
 * Get theme settings via API.
 *
 * @since 1.0.0
 * @return WP_REST_Response REST response.
 */
function wpforge_api_get_settings() {
    $settings = wpforge_get_all_theme_settings();

    return rest_ensure_response(array(
        'success'  => true,
        'settings' => $settings,
    ));
}

/**
 * Update theme settings via API.
 *
 * @since 1.0.0
 * @param WP_REST_Request $request REST request.
 * @return WP_REST_Response REST response.
 */
function wpforge_api_update_settings($request) {
    $params = $request->get_json_params();
    $settings = isset($params['settings']) ? $params['settings'] : array();

    if (empty($settings)) {
        return new WP_Error('empty_settings', __('No settings provided', 'wpforge-theme'), array('status' => 400));
    }

    $result = wpforge_update_theme_settings($settings);

    return rest_ensure_response(array(
        'success' => $result,
        'message' => $result ? __('Settings updated successfully', 'wpforge-theme') : __('Failed to update settings', 'wpforge-theme'),
    ));
}

/**
 * Get theme presets via API.
 *
 * @since 1.0.0
 * @return WP_REST_Response REST response.
 */
function wpforge_api_get_presets() {
    $presets = wpforge_get_all_presets();

    return rest_ensure_response(array(
        'success' => true,
        'presets' => $presets,
    ));
}

/**
 * Apply preset via API.
 *
 * @since 1.0.0
 * @param WP_REST_Request $request REST request.
 * @return WP_REST_Response REST response.
 */
function wpforge_api_apply_preset($request) {
    $preset = $request->get_param('preset');

    $result = wpforge_apply_preset($preset);

    if (is_wp_error($result)) {
        return $result;
    }

    return rest_ensure_response(array(
        'success' => true,
        'message' => sprintf(__('Preset "%s" applied successfully', 'wpforge-theme'), $preset),
        'preset'  => $preset,
    ));
}

/**
 * Export config via API.
 *
 * @since 1.0.0
 * @return WP_REST_Response REST response.
 */
function wpforge_api_export_config() {
    $config = wpforge_export_theme_config();

    return rest_ensure_response(array(
        'success' => true,
        'config'  => $config,
        'version' => WPFORGE_THEME_VERSION,
    ));
}

/**
 * Import config via API.
 *
 * @since 1.0.0
 * @param WP_REST_Request $request REST request.
 * @return WP_REST_Response REST response.
 */
function wpforge_api_import_config($request) {
    $params = $request->get_json_params();
    $config = isset($params['config']) ? $params['config'] : null;

    if (!$config) {
        return new WP_Error('empty_config', __('No config provided', 'wpforge-theme'), array('status' => 400));
    }

    $result = wpforge_import_theme_config($config);

    if (is_wp_error($result)) {
        return $result;
    }

    return rest_ensure_response(array(
        'success' => true,
        'message' => __('Config imported successfully', 'wpforge-theme'),
    ));
}

/**
 * Get theme info via API.
 *
 * @since 1.0.0
 * @return WP_REST_Response REST response.
 */
function wpforge_api_get_theme_info() {
    $info = array(
        'name'        => 'WPForge Theme',
        'version'     => WPFORGE_THEME_VERSION,
        'description' => 'AI-Driven Ultra-Lightweight WordPress Theme',
        'author'      => 'WPForge Team',
        'theme_uri'   => 'https://wpforge.io/theme',
        'text_domain' => 'wpforge-theme',
        'features'    => array(
            'ultra_lightweight' => true,
            'seo_optimized'     => true,
            'page_builder_support' => array('elementor', 'bricks', 'gutenberg'),
            'woocommerce_support' => true,
            'customizer_api'    => true,
            'rest_api'          => true,
            'dark_mode'         => true,
            'performance_optimization' => true,
            'schema_markup'     => true,
        ),
        'requirements' => array(
            'wordpress' => '5.6+',
            'php'       => '7.4+',
        ),
    );

    return rest_ensure_response(array(
        'success' => true,
        'info'    => $info,
    ));
}

/**
 * Get performance stats via API.
 *
 * @since 1.0.0
 * @return WP_REST_Response REST response.
 */
function wpforge_api_get_performance_stats() {
    if (function_exists('wpforge_get_performance_stats')) {
        $stats = wpforge_get_performance_stats();
    } else {
        $stats = array();
    }

    return rest_ensure_response(array(
        'success' => true,
        'stats'   => $stats,
    ));
}

/**
 * Get all theme settings.
 *
 * @since 1.0.0
 * @return array All theme settings.
 */
function wpforge_get_all_theme_settings() {
    global $wp_customize;

    $settings = array();

    // Get all theme mods.
    $theme_mods = get_theme_mods();

    foreach ($theme_mods as $key => $value) {
        // Only include WPForge settings.
        if (strpos($key, 'wpforge_') === 0) {
            $settings[$key] = $value;
        }
    }

    // Also include core WordPress settings that we use.
    $core_settings = array(
        'blogname',
        'blogdescription',
        'site_icon',
        'custom_logo',
    );

    foreach ($core_settings as $setting) {
        $settings[$setting] = get_theme_mod($setting);
    }

    return $settings;
}

/**
 * Update theme settings.
 *
 * @since 1.0.0
 * @param array $settings Settings to update.
 * @return bool Whether update was successful.
 */
function wpforge_update_theme_settings($settings) {
    if (!is_array($settings)) {
        return false;
    }

    foreach ($settings as $key => $value) {
        // Sanitize based on setting type.
        if (strpos($key, '_color') !== false) {
            $value = sanitize_hex_color($value);
        } elseif (strpos($key, '_enabled') !== false || strpos($key, '_show_') !== false) {
            $value = (bool) $value;
        } elseif (strpos($key, '_width') !== false || strpos($key, '_height') !== false || strpos($key, '_size') !== false || strpos($key, '_count') !== false) {
            $value = absint($value);
        } else {
            $value = sanitize_text_field($value);
        }

        set_theme_mod($key, $value);
    }

    return true;
}

/**
 * Get all presets.
 *
 * @since 1.0.0
 * @return array Presets data.
 */
function wpforge_get_all_presets() {
    $presets = array(
        'default' => array(
            'name'        => __('Default', 'wpforge-theme'),
            'description' => __('Clean, modern default style', 'wpforge-theme'),
            'colors' => array(
                'primary'   => '#2563eb',
                'secondary' => '#64748b',
                'accent'    => '#f97316',
                'text'      => '#1e293b',
                'background' => '#ffffff',
            ),
        ),
        'modern' => array(
            'name'        => __('Modern Blue', 'wpforge-theme'),
            'description' => __('Professional blue theme for business', 'wpforge-theme'),
            'colors' => array(
                'primary'   => '#3b82f6',
                'secondary' => '#1e40af',
                'accent'    => '#06b6d4',
                'text'      => '#1e293b',
                'background' => '#ffffff',
            ),
        ),
        'elegant' => array(
            'name'        => __('Elegant Purple', 'wpforge-theme'),
            'description' => __('Sophisticated purple theme', 'wpforge-theme'),
            'colors' => array(
                'primary'   => '#8b5cf6',
                'secondary' => '#7c3aed',
                'accent'    => '#ec4899',
                'text'      => '#1e1b4b',
                'background' => '#ffffff',
            ),
        ),
        'fresh' => array(
            'name'        => __('Fresh Green', 'wpforge-theme'),
            'description' => __('Natural green theme for eco/health', 'wpforge-theme'),
            'colors' => array(
                'primary'   => '#22c55e',
                'secondary' => '#16a34a',
                'accent'    => '#84cc16',
                'text'      => '#14532d',
                'background' => '#ffffff',
            ),
        ),
        'warm' => array(
            'name'        => __('Warm Orange', 'wpforge-theme'),
            'description' => __('Warm orange theme for creative', 'wpforge-theme'),
            'colors' => array(
                'primary'   => '#f97316',
                'secondary' => '#ea580c',
                'accent'    => '#eab308',
                'text'      => '#431407',
                'background' => '#fffbeb',
            ),
        ),
        'dark' => array(
            'name'        => __('Dark Mode', 'wpforge-theme'),
            'description' => __('Sleek dark mode theme', 'wpforge-theme'),
            'colors' => array(
                'primary'   => '#60a5fa',
                'secondary' => '#94a3b8',
                'accent'    => '#f472b6',
                'text'      => '#f1f5f9',
                'background' => '#0f172a',
            ),
        ),
        'minimal' => array(
            'name'        => __('Minimal Black', 'wpforge-theme'),
            'description' => __('Minimalist black and white', 'wpforge-theme'),
            'colors' => array(
                'primary'   => '#000000',
                'secondary' => '#666666',
                'accent'    => '#333333',
                'text'      => '#111111',
                'background' => '#ffffff',
            ),
        ),
        'ecommerce' => array(
            'name'        => __('E-Commerce', 'wpforge-theme'),
            'description' => __('Optimized for online stores', 'wpforge-theme'),
            'colors' => array(
                'primary'   => '#ef4444',
                'secondary' => '#dc2626',
                'accent'    => '#f59e0b',
                'text'      => '#1f2937',
                'background' => '#ffffff',
            ),
        ),
        'blog' => array(
            'name'        => __('Blog Style', 'wpforge-theme'),
            'description' => __('Perfect for content blogs', 'wpforge-theme'),
            'colors' => array(
                'primary'   => '#0ea5e9',
                'secondary' => '#0284c7',
                'accent'    => '#f43f5e',
                'text'      => '#1e293b',
                'background' => '#f8fafc',
            ),
        ),
        'corporate' => array(
            'name'        => __('Corporate', 'wpforge-theme'),
            'description' => __('Professional corporate style', 'wpforge-theme'),
            'colors' => array(
                'primary'   => '#1e40af',
                'secondary' => '#1e3a8a',
                'accent'    => '#0891b2',
                'text'      => '#0f172a',
                'background' => '#ffffff',
            ),
        ),
    );

    return apply_filters('wpforge_theme_presets', $presets);
}

/**
 * Apply a preset.
 *
 * @since 1.0.0
 * @param string $preset Preset name.
 * @return bool|WP_Error True on success, WP_Error on failure.
 */
function wpforge_apply_preset($preset) {
    $presets = wpforge_get_all_presets();

    if (!isset($presets[$preset])) {
        return new WP_Error('invalid_preset', __('Invalid preset', 'wpforge-theme'), array('status' => 400));
    }

    $preset_data = $presets[$preset];

    // Apply colors.
    if (isset($preset_data['colors'])) {
        $colors = $preset_data['colors'];

        if (isset($colors['primary'])) {
            set_theme_mod('wpforge_primary_color', $colors['primary']);
        }
        if (isset($colors['secondary'])) {
            set_theme_mod('wpforge_secondary_color', $colors['secondary']);
        }
        if (isset($colors['accent'])) {
            set_theme_mod('wpforge_accent_color', $colors['accent']);
        }
        if (isset($colors['text'])) {
            set_theme_mod('wpforge_text_color', $colors['text']);
        }
        if (isset($colors['background'])) {
            set_theme_mod('wpforge_background_color', $colors['background']);
        }
    }

    // Save active preset.
    set_theme_mod('wpforge_active_preset', $preset);

    do_action('wpforge_preset_applied', $preset, $preset_data);

    return true;
}

/**
 * Export theme config.
 *
 * @since 1.0.0
 * @return array Exported config.
 */
function wpforge_export_theme_config() {
    $config = array(
        'version'  => WPFORGE_THEME_VERSION,
        'exported' => current_time('mysql'),
        'settings' => wpforge_get_all_theme_settings(),
        'preset'   => get_theme_mod('wpforge_active_preset', 'default'),
    );

    return apply_filters('wpforge_export_config', $config);
}

/**
 * Import theme config.
 *
 * @since 1.0.0
 * @param array $config Config to import.
 * @return bool|WP_Error True on success, WP_Error on failure.
 */
function wpforge_import_theme_config($config) {
    if (!is_array($config)) {
        return new WP_Error('invalid_config', __('Invalid config format', 'wpforge-theme'), array('status' => 400));
    }

    if (!isset($config['settings']) || !is_array($config['settings'])) {
        return new WP_Error('missing_settings', __('Config missing settings', 'wpforge-theme'), array('status' => 400));
    }

    // Import settings.
    wpforge_update_theme_settings($config['settings']);

    // Apply preset if specified.
    if (isset($config['preset'])) {
        wpforge_apply_preset($config['preset']);
    }

    do_action('wpforge_config_imported', $config);

    return true;
}

/**
 * Add WPForge admin menu.
 *
 * @since 1.0.0
 */
function wpforge_add_admin_menu() {
    add_theme_page(
        __('WPForge Theme', 'wpforge-theme'),
        __('WPForge Theme', 'wpforge-theme'),
        'edit_theme_options',
        'wpforge-theme',
        'wpforge_render_admin_page'
    );
}

/**
 * Render WPForge admin page.
 *
 * @since 1.0.0
 */
function wpforge_render_admin_page() {
    ?>
    <div class="wrap">
        <h1><?php esc_html_e('WPForge Theme', 'wpforge-theme'); ?></h1>

        <div class="wpforge-theme-admin">
            <div class="wpforge-theme-info">
                <h2><?php esc_html_e('Theme Info', 'wpforge-theme'); ?></h2>
                <p><strong><?php esc_html_e('Version:', 'wpforge-theme'); ?></strong> <?php echo esc_html(WPFORGE_THEME_VERSION); ?></p>
                <p><?php esc_html_e('AI-Driven Ultra-Lightweight WordPress Theme', 'wpforge-theme'); ?></p>
            </div>

            <div class="wpforge-theme-actions">
                <h2><?php esc_html_e('Quick Actions', 'wpforge-theme'); ?></h2>

                <p>
                    <a href="<?php echo esc_url(admin_url('customize.php')); ?>" class="button button-primary">
                        <?php esc_html_e('Customize Theme', 'wpforge-theme'); ?>
                    </a>
                </p>

                <form method="post" action="">
                    <?php wp_nonce_field('wpforge_export_config', 'wpforge_export_nonce'); ?>
                    <input type="hidden" name="wpforge_action" value="export_config">
                    <button type="submit" class="button">
                        <?php esc_html_e('Export Config', 'wpforge-theme'); ?>
                    </button>
                </form>

                <form method="post" action="" enctype="multipart/form-data">
                    <?php wp_nonce_field('wpforge_import_config', 'wpforge_import_nonce'); ?>
                    <input type="hidden" name="wpforge_action" value="import_config">
                    <p>
                        <input type="file" name="wpforge_config_file" accept=".json">
                    </p>
                    <button type="submit" class="button">
                        <?php esc_html_e('Import Config', 'wpforge-theme'); ?>
                    </button>
                </form>
            </div>

            <div class="wpforge-theme-presets">
                <h2><?php esc_html_e('Presets', 'wpforge-theme'); ?></h2>
                <form method="post" action="">
                    <?php wp_nonce_field('wpforge_apply_preset', 'wpforge_preset_nonce'); ?>
                    <input type="hidden" name="wpforge_action" value="apply_preset">
                    <select name="wpforge_preset">
                        <?php
                        $presets = wpforge_get_all_presets();
                        foreach ($presets as $key => $preset) {
                            echo '<option value="' . esc_attr($key) . '">' . esc_html($preset['name']) . '</option>';
                        }
                        ?>
                    </select>
                    <button type="submit" class="button">
                        <?php esc_html_e('Apply Preset', 'wpforge-theme'); ?>
                    </button>
                </form>
            </div>
        </div>
    </div>
    <?php
}

/**
 * Add admin bar menu.
 *
 * @since 1.0.0
 * @param WP_Admin_Bar $wp_admin_bar Admin bar object.
 */
function wpforge_add_admin_bar_menu($wp_admin_bar) {
    if (!current_user_can('edit_theme_options')) {
        return;
    }

    $wp_admin_bar->add_node(array(
        'id'    => 'wpforge-theme',
        'title' => __('WPForge Theme', 'wpforge-theme'),
        'href'  => admin_url('themes.php?page=wpforge-theme'),
    ));

    $wp_admin_bar->add_node(array(
        'id'     => 'wpforge-customize',
        'parent' => 'wpforge-theme',
        'title'  => __('Customize', 'wpforge-theme'),
        'href'   => admin_url('customize.php'),
    ));

    $wp_admin_bar->add_node(array(
        'id'     => 'wpforge-settings',
        'parent' => 'wpforge-theme',
        'title'  => __('Settings', 'wpforge-theme'),
        'href'   => admin_url('themes.php?page=wpforge-theme'),
    ));
}

/**
 * Handle preset import from admin.
 *
 * @since 1.0.0
 */
function wpforge_handle_preset_import() {
    if (!isset($_POST['wpforge_action']) || 'apply_preset' !== $_POST['wpforge_action']) {
        return;
    }

    if (!current_user_can('edit_theme_options')) {
        return;
    }

    if (!isset($_POST['wpforge_preset_nonce']) || !wp_verify_nonce($_POST['wpforge_preset_nonce'], 'wpforge_apply_preset')) {
        return;
    }

    $preset = sanitize_text_field($_POST['wpforge_preset']);
    $result = wpforge_apply_preset($preset);

    if ($result) {
        add_settings_error('wpforge-theme', 'preset_applied', sprintf(__('Preset "%s" applied successfully', 'wpforge-theme'), $preset), 'updated');
    }
}

/**
 * Handle config export from admin.
 *
 * @since 1.0.0
 */
function wpforge_handle_config_export() {
    if (!isset($_POST['wpforge_action']) || 'export_config' !== $_POST['wpforge_action']) {
        return;
    }

    if (!current_user_can('edit_theme_options')) {
        return;
    }

    if (!isset($_POST['wpforge_export_nonce']) || !wp_verify_nonce($_POST['wpforge_export_nonce'], 'wpforge_export_config')) {
        return;
    }

    $config = wpforge_export_theme_config();

    header('Content-Type: application/json');
    header('Content-Disposition: attachment; filename="wpforge-theme-config.json"');
    header('Cache-Control: no-cache, must-revalidate');
    header('Expires: Mon, 26 Jul 1997 05:00:00 GMT');

    echo wp_json_encode($config, JSON_PRETTY_PRINT);
    exit;
}

/**
 * Handle config import from admin.
 *
 * @since 1.0.0
 */
function wpforge_handle_config_import() {
    if (!isset($_POST['wpforge_action']) || 'import_config' !== $_POST['wpforge_action']) {
        return;
    }

    if (!current_user_can('edit_theme_options')) {
        return;
    }

    if (!isset($_POST['wpforge_import_nonce']) || !wp_verify_nonce($_POST['wpforge_import_nonce'], 'wpforge_import_config')) {
        return;
    }

    if (isset($_FILES['wpforge_config_file']) && UPLOAD_ERR_OK === $_FILES['wpforge_config_file']['error']) {
        $file = $_FILES['wpforge_config_file'];

        // Read file content.
        $config_json = file_get_contents($file['tmp_name']);
        $config = json_decode($config_json, true);

        if ($config) {
            $result = wpforge_import_theme_config($config);

            if ($result) {
                add_settings_error('wpforge-theme', 'config_imported', __('Config imported successfully', 'wpforge-theme'), 'updated');
            } else {
                add_settings_error('wpforge-theme', 'import_failed', __('Failed to import config', 'wpforge-theme'), 'error');
            }
        } else {
            add_settings_error('wpforge-theme', 'invalid_json', __('Invalid JSON file', 'wpforge-theme'), 'error');
        }
    }
}

/**
 * Check if WPForge plugin is active.
 *
 * @since 1.0.0
 * @return bool Whether WPForge plugin is active.
 */
function wpforge_is_plugin_active() {
    return class_exists('WPForge\\Plugin');
}

/**
 * Get WPForge integration status.
 *
 * @since 1.0.0
 * @return array Integration status.
 */
function wpforge_get_integration_status() {
    return array(
        'plugin_active'    => wpforge_is_plugin_active(),
        'theme_version'    => WPFORGE_THEME_VERSION,
        'rest_api_enabled' => true,
        'presets_count'    => count(wpforge_get_all_presets()),
        'settings_count'   => count(wpforge_get_all_theme_settings()),
    );
}
