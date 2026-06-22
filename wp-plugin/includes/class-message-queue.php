<?php
/**
 * 消息队列类
 * 
 * 处理离线消息的本地缓存和补发
 */

// 防止直接访问
if (!defined('ABSPATH')) {
    exit;
}

class WPForge_Relay_Message_Queue {

    /**
     * 数据库表名
     */
    private $table_name = '';

    /**
     * 构造函数
     */
    public function __construct() {
        global $wpdb;
        $this->table_name = $wpdb->prefix . 'wpforge_relay_queue';
    }

    /**
     * 创建数据库表
     */
    public function create_table() {
        global $wpdb;
        $charset_collate = $wpdb->get_charset_collate();

        $sql = "CREATE TABLE IF NOT EXISTS {$this->table_name} (
            id bigint(20) NOT NULL AUTO_INCREMENT,
            message_id varchar(100) NOT NULL,
            message_type varchar(50) NOT NULL DEFAULT 'event',
            message_data longtext NOT NULL,
            status varchar(20) NOT NULL DEFAULT 'pending',
            priority int(11) NOT NULL DEFAULT 0,
            retry_count int(11) NOT NULL DEFAULT 0,
            max_retries int(11) NOT NULL DEFAULT 5,
            error_message text DEFAULT NULL,
            created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY message_id (message_id),
            KEY status (status),
            KEY priority (priority),
            KEY created_at (created_at)
        ) $charset_collate;";

        require_once ABSPATH . 'wp-admin/includes/upgrade.php';
        dbDelta($sql);
    }

    /**
     * 消息入队
     */
    public function enqueue($message_data, $message_type = 'event', $priority = 0) {
        global $wpdb;

        $message_id = $this->generate_message_id();

        $result = $wpdb->insert(
            $this->table_name,
            array(
                'message_id' => $message_id,
                'message_type' => $message_type,
                'message_data' => maybe_serialize($message_data),
                'status' => 'pending',
                'priority' => $priority,
                'max_retries' => 5,
            ),
            array(
                '%s',
                '%s',
                '%s',
                '%s',
                '%d',
                '%d',
            )
        );

        if ($result === false) {
            error_log('WPForge Relay: Failed to enqueue message - ' . $wpdb->last_error);
            return false;
        }

        return $message_id;
    }

    /**
     * 消息出队
     */
    public function dequeue($limit = 10) {
        global $wpdb;

        // 获取待处理消息
        $messages = $wpdb->get_results(
            $wpdb->prepare(
                "SELECT * FROM {$this->table_name} 
                 WHERE status = %s 
                 AND retry_count < max_retries
                 ORDER BY priority DESC, created_at ASC 
                 LIMIT %d",
                'pending',
                $limit
            )
        );

        if (empty($messages)) {
            return array();
        }

        // 标记为处理中
        $ids = wp_list_pluck($messages, 'id');
        $ids_placeholder = implode(',', array_fill(0, count($ids), '%d'));

        $wpdb->query(
            $wpdb->prepare(
                "UPDATE {$this->table_name} SET status = %s WHERE id IN ($ids_placeholder)",
                'processing',
                ...$ids
            )
        );

        // 反序列化消息数据
        foreach ($messages as &$message) {
            $message->message_data = maybe_unserialize($message->message_data);
        }

        return $messages;
    }

    /**
     * 标记消息成功
     */
    public function mark_success($message_id) {
        global $wpdb;

        return $wpdb->update(
            $this->table_name,
            array('status' => 'completed'),
            array('message_id' => $message_id),
            array('%s'),
            array('%s')
        );
    }

    /**
     * 标记消息失败
     */
    public function mark_failed($message_id, $error_message = '') {
        global $wpdb;

        // 获取当前重试次数
        $message = $wpdb->get_row(
            $wpdb->prepare(
                "SELECT * FROM {$this->table_name} WHERE message_id = %s",
                $message_id
            )
        );

        if (!$message) {
            return false;
        }

        $new_retry_count = $message->retry_count + 1;
        $new_status = ($new_retry_count >= $message->max_retries) ? 'failed' : 'pending';

        return $wpdb->update(
            $this->table_name,
            array(
                'status' => $new_status,
                'retry_count' => $new_retry_count,
                'error_message' => $error_message,
            ),
            array('message_id' => $message_id),
            array('%s', '%d', '%s'),
            array('%s')
        );
    }

    /**
     * 处理待处理消息
     */
    public function process_pending_messages() {
        $messages = $this->dequeue(20);

        if (empty($messages)) {
            return 0;
        }

        $processed = 0;
        $websocket_client = wpforge_relay()->get_websocket_client();

        foreach ($messages as $message) {
            try {
                $success = false;

                // 根据消息类型处理
                if ($message->message_type === 'event') {
                    $event_data = $message->message_data;
                    $event_type = isset($event_data['event']) ? $event_data['event'] : 'unknown';
                    $event_data = isset($event_data['data']) ? $event_data['data'] : array();

                    $success = $websocket_client->send_event($event_type, $event_data);
                }

                if ($success) {
                    $this->mark_success($message->message_id);
                    $processed++;
                } else {
                    $this->mark_failed($message->message_id, 'Send failed');
                }

            } catch (Exception $e) {
                $this->mark_failed($message->message_id, $e->getMessage());
            }
        }

        return $processed;
    }

    /**
     * 获取队列统计
     */
    public function get_stats() {
        global $wpdb;

        $stats = array(
            'pending' => 0,
            'processing' => 0,
            'completed' => 0,
            'failed' => 0,
            'total' => 0,
        );

        $results = $wpdb->get_results(
            "SELECT status, COUNT(*) as count FROM {$this->table_name} GROUP BY status"
        );

        foreach ($results as $row) {
            if (isset($stats[$row->status])) {
                $stats[$row->status] = intval($row->count);
            }
            $stats['total'] += intval($row->count);
        }

        return $stats;
    }

    /**
     * 清理已完成的消息
     */
    public function cleanup_completed($days = 7) {
        global $wpdb;

        $wpdb->query(
            $wpdb->prepare(
                "DELETE FROM {$this->table_name} 
                 WHERE status = %s 
                 AND updated_at < DATE_SUB(NOW(), INTERVAL %d DAY)",
                'completed',
                $days
            )
        );
    }

    /**
     * 清理失败的消息
     */
    public function cleanup_failed($days = 30) {
        global $wpdb;

        $wpdb->query(
            $wpdb->prepare(
                "DELETE FROM {$this->table_name} 
                 WHERE status = %s 
                 AND updated_at < DATE_SUB(NOW(), INTERVAL %d DAY)",
                'failed',
                $days
            )
        );
    }

    /**
     * 生成消息ID
     */
    private function generate_message_id() {
        return 'msg_' . time() . '_' . wp_generate_password(12, false);
    }

    /**
     * 获取队列中的消息数量
     */
    public function get_pending_count() {
        global $wpdb;

        return intval($wpdb->get_var(
            $wpdb->prepare(
                "SELECT COUNT(*) FROM {$this->table_name} WHERE status = %s",
                'pending'
            )
        ));
    }
}
