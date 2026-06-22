<?php
/**
 * WebSocket客户端类
 * 
 * 负责与中转服务器建立WebSocket连接，处理消息收发
 */

// 防止直接访问
if (!defined('ABSPATH')) {
    exit;
}

class WPForge_Relay_WebSocket_Client {

    /**
     * 服务器URL
     */
    private $server_url = '';

    /**
     * 站点ID
     */
    private $site_id = '';

    /**
     * 站点Token
     */
    private $site_token = '';

    /**
     * 连接状态
     */
    private $connected = false;

    /**
     * 消息队列实例
     */
    private $message_queue = null;

    /**
     * 重连尝试次数
     */
    private $reconnect_attempts = 0;

    /**
     * 最大重连次数
     */
    private $max_reconnect_attempts = 5;

    /**
     * 构造函数
     */
    public function __construct($message_queue) {
        $this->message_queue = $message_queue;
        $this->server_url = get_option('wpforge_relay_server_url', '');
        $this->site_id = get_option('wpforge_relay_site_id', '');
        $this->site_token = get_option('wpforge_relay_site_token', '');
    }

    /**
     * 连接到服务器
     */
    public function connect() {
        if (empty($this->server_url) || empty($this->site_id) || empty($this->site_token)) {
            error_log('WPForge Relay: Server URL, Site ID or Token not configured');
            return false;
        }

        try {
            // 这里使用PHP的stream_socket_client建立WebSocket连接
            // 实际生产环境建议使用更成熟的WebSocket客户端库
            
            $parsed_url = parse_url($this->server_url);
            $host = $parsed_url['host'];
            $port = isset($parsed_url['port']) ? $parsed_url['port'] : 80;
            $path = isset($parsed_url['path']) ? $parsed_url['path'] : '/socket.io/?EIO=4&transport=websocket';
            
            // 构建WebSocket握手请求
            $key = base64_encode(openssl_random_pseudo_bytes(16));
            
            $headers = array(
                'GET ' . $path . ' HTTP/1.1',
                'Host: ' . $host,
                'Upgrade: websocket',
                'Connection: Upgrade',
                'Sec-WebSocket-Key: ' . $key,
                'Sec-WebSocket-Version: 13',
                'User-Agent: WPForge-Relay-Plugin/' . WPFORGE_RELAY_VERSION,
            );

            // 添加认证信息
            $auth_data = json_encode(array(
                'clientType' => 'plugin',
                'credentials' => array(
                    'siteId' => $this->site_id,
                    'token' => $this->site_token
                )
            ));
            
            $headers[] = 'Authorization: Bearer ' . base64_encode($auth_data);

            // 建立连接
            $context = stream_context_create();
            $socket = stream_socket_client(
                'tcp://' . $host . ':' . $port,
                $errno,
                $errstr,
                30,
                STREAM_CLIENT_CONNECT,
                $context
            );

            if (!$socket) {
                error_log('WPForge Relay: Failed to connect - ' . $errstr);
                return false;
            }

            // 发送握手请求
            fwrite($socket, implode("\r\n", $headers) . "\r\n\r\n");
            
            // 读取响应
            $response = fread($socket, 1024);
            
            if (strpos($response, '101 Switching Protocols') === false) {
                error_log('WPForge Relay: WebSocket handshake failed');
                fclose($socket);
                return false;
            }

            $this->connected = true;
            $this->reconnect_attempts = 0;
            
            // 发送连接认证消息（Socket.io格式）
            $this->send_message('40' . json_encode(array(
                'token' => $this->site_token,
                'siteId' => $this->site_id
            )));

            // 启动消息监听
            $this->start_listening($socket);

            return true;

        } catch (Exception $e) {
            error_log('WPForge Relay: Connection error - ' . $e->getMessage());
            $this->connected = false;
            return false;
        }
    }

    /**
     * 发送消息
     */
    public function send_message($data) {
        if (!$this->connected) {
            return false;
        }

        try {
            // WebSocket帧封装
            $frame = $this->build_websocket_frame($data);
            
            // 这里简化处理，实际应该通过socket发送
            // 由于PHP的特性，实际生产中可能需要使用ReactPHP或Swoole
            error_log('WPForge Relay: Sending message - ' . substr($data, 0, 100));
            
            return true;

        } catch (Exception $e) {
            error_log('WPForge Relay: Send error - ' . $e->getMessage());
            $this->connected = false;
            return false;
        }
    }

    /**
     * 发送事件
     */
    public function send_event($event_type, $event_data) {
        $message = array(
            'type' => 'event',
            'event' => $event_type,
            'data' => $event_data,
            'timestamp' => current_time('timestamp')
        );

        if ($this->connected) {
            return $this->send_message(json_encode($message));
        } else {
            // 连接断开时加入队列
            $this->message_queue->enqueue($message);
            return false;
        }
    }

    /**
     * 发送指令响应
     */
    public function send_response($command_id, $success, $data = array(), $error = null) {
        $message = array(
            'type' => 'response',
            'responseTo' => $command_id,
            'success' => $success,
            'data' => $data,
            'error' => $error,
            'timestamp' => current_time('timestamp')
        );

        return $this->send_message(json_encode($message));
    }

    /**
     * 启动消息监听
     */
    private function start_listening($socket) {
        // 由于PHP的特性，这里简化处理
        // 实际生产中应该使用异步处理方式
        
        // 注册shutdown函数来处理连接关闭
        register_shutdown_function(function() use ($socket) {
            if (is_resource($socket)) {
                fclose($socket);
            }
            $this->connected = false;
        });
    }

    /**
     * 处理接收到的消息
     */
    public function handle_message($message) {
        try {
            $data = json_decode($message, true);
            
            if (!$data || !isset($data['type'])) {
                return;
            }

            switch ($data['type']) {
                case 'command':
                    // 处理指令
                    do_action('wpforge_relay_command_received', $data);
                    break;
                
                case 'broadcast':
                    // 处理广播
                    do_action('wpforge_relay_broadcast_received', $data);
                    break;
                
                case 'heartbeat':
                    // 响应心跳
                    $this->send_heartbeat();
                    break;
            }

        } catch (Exception $e) {
            error_log('WPForge Relay: Message handling error - ' . $e->getMessage());
        }
    }

    /**
     * 发送心跳
     */
    public function send_heartbeat() {
        $message = array(
            'type' => 'heartbeat',
            'timestamp' => current_time('timestamp')
        );

        return $this->send_message(json_encode($message));
    }

    /**
     * 断开连接
     */
    public function disconnect() {
        $this->connected = false;
        $this->reconnect_attempts = 0;
    }

    /**
     * 重连
     */
    public function reconnect() {
        if ($this->reconnect_attempts >= $this->max_reconnect_attempts) {
            error_log('WPForge Relay: Max reconnect attempts reached');
            return false;
        }

        $this->reconnect_attempts++;
        
        // 指数退避
        $delay = pow(2, $this->reconnect_attempts) * 1000;
        usleep($delay * 1000);

        return $this->connect();
    }

    /**
     * 检查连接状态
     */
    public function is_connected() {
        return $this->connected;
    }

    /**
     * 构建WebSocket帧
     */
    private function build_websocket_frame($data, $type = 'text') {
        // 简化的WebSocket帧构建
        // 实际生产中应该使用完整的WebSocket协议实现
        
        $length = strlen($data);
        $frame = '';

        // 第一个字节：FIN + opcode
        $frame .= chr(0x81); // 0x81 = FIN + text frame

        // 长度
        if ($length <= 125) {
            $frame .= chr($length);
        } elseif ($length <= 65535) {
            $frame .= chr(126);
            $frame .= pack('n', $length);
        } else {
            $frame .= chr(127);
            $frame .= pack('J', $length);
        }

        // 数据
        $frame .= $data;

        return $frame;
    }

    /**
     * 更新配置
     */
    public function update_config($server_url, $site_id, $site_token) {
        $this->server_url = $server_url;
        $this->site_id = $site_id;
        $this->site_token = $site_token;
        
        // 如果已连接，断开重连
        if ($this->connected) {
            $this->disconnect();
        }
    }
}
