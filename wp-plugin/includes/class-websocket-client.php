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
     * 当前socket连接资源
     */
    private $socket = null;

    /**
     * 心跳间隔（秒，从Engine.IO open包获取）
     */
    private $ping_interval = 25;

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
            // 使用PHP的stream_socket_client建立WebSocket连接
            $parsed_url = parse_url($this->server_url);
            $host = $parsed_url['host'];
            $is_secure = isset($parsed_url['scheme']) && $parsed_url['scheme'] === 'https';
            $port = isset($parsed_url['port']) ? $parsed_url['port'] : ($is_secure ? 443 : 80);
            $path = isset($parsed_url['path']) ? $parsed_url['path'] : '/socket.io/';
            // Engine.IO v4，使用websocket传输
            $path .= (strpos($path, '?') !== false ? '&' : '?') . 'EIO=4&transport=websocket';

            // 构建WebSocket握手请求
            $key = base64_encode(openssl_random_pseudo_bytes(16));

            $headers = array(
                'GET ' . $path . ' HTTP/1.1',
                'Host: ' . $host . ($port == 80 || $port == 443 ? '' : ':' . $port),
                'Upgrade: websocket',
                'Connection: Upgrade',
                'Sec-WebSocket-Key: ' . $key,
                'Sec-WebSocket-Version: 13',
                'User-Agent: WPForge-Relay-Plugin/' . WPFORGE_RELAY_VERSION,
            );

            // 建立连接（支持wss/https）
            $context = stream_context_create();
            $remote = ($is_secure ? 'ssl://' : 'tcp://') . $host . ':' . $port;
            $socket = stream_socket_client(
                $remote,
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

            // 读取HTTP握手响应（直到遇到\r\n\r\n结束）
            $response = '';
            while (!feof($socket) && strpos($response, "\r\n\r\n") === false) {
                $chunk = fread($socket, 1024);
                if ($chunk === false || $chunk === '') {
                    break;
                }
                $response .= $chunk;
            }

            if (strpos($response, '101 Switching Protocols') === false) {
                error_log('WPForge Relay: WebSocket handshake failed');
                fclose($socket);
                return false;
            }

            // 保存socket资源
            $this->socket = $socket;
            $this->connected = true;
            $this->reconnect_attempts = 0;

            // 读取Engine.IO open握手包（包含sid等信息）
            $this->read_engineio_open();

            // 发送Socket.IO CONNECT包，携带认证信息
            // relay-server 的 AuthManager 期望 handshake.auth 包含 clientType 和 credentials
            $connect_payload = json_encode(array(
                'clientType' => 'plugin',
                'credentials' => array(
                    'siteId' => $this->site_id,
                    'token' => $this->site_token,
                ),
            ));
            $this->send_message('40' . $connect_payload);

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
     * 读取Engine.IO open握手包
     */
    private function read_engineio_open() {
        if (!$this->socket) {
            return;
        }

        $payload = $this->read_websocket_frame();
        if ($payload === null) {
            return;
        }

        // Engine.IO open 包以 "0" 开头，后接JSON
        if (substr($payload, 0, 1) === '0') {
            $data = json_decode(substr($payload, 1), true);
            if (isset($data['pingInterval'])) {
                $this->ping_interval = intval($data['pingInterval']) / 1000;
            }
        }
    }

    /**
     * 发送消息
     *
     * @param string $data 要发送的原始数据（Engine.IO/Socket.IO 协议字符串）
     * @return bool
     */
    public function send_message($data) {
        if (!$this->connected || !$this->socket || !is_resource($this->socket)) {
            return false;
        }

        try {
            // 构建WebSocket帧
            $frame = $this->build_websocket_frame($data);

            // 真正通过socket发送数据
            $written = 0;
            $length = strlen($frame);
            while ($written < $length) {
                $bytes = fwrite($this->socket, substr($frame, $written));
                if ($bytes === false || $bytes === 0) {
                    error_log('WPForge Relay: Failed to write to socket');
                    $this->connected = false;
                    return false;
                }
                $written += $bytes;
            }

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
     *
     * 由于PHP是同步阻塞模型，这里采用非阻塞读取方式处理已到达的消息。
     * 长连接场景下应通过WP-Cron或常驻进程反复调用 process_messages()。
     *
     * @param resource $socket
     */
    private function start_listening($socket) {
        if (!$socket || !is_resource($socket)) {
            return;
        }

        // 切换为非阻塞模式，避免 fread 卡住请求
        stream_set_blocking($socket, false);
        stream_set_timeout($socket, 1);

        // 注册shutdown函数来处理连接关闭
        register_shutdown_function(function() {
            $this->disconnect();
        });

        // 立即处理一次已到达的消息（如CONNECT确认）
        $this->process_messages();
    }

    /**
     * 处理一次可读的消息（非阻塞）
     *
     * 读取所有当前可用的WebSocket帧，按Engine.IO/Socket.IO协议解析并分发。
     * 包含ping/pong心跳处理。
     *
     * @return int 处理的消息数量
     */
    public function process_messages() {
        if (!$this->connected || !$this->socket || !is_resource($this->socket)) {
            return 0;
        }

        $processed = 0;
        // 限制单次处理的消息数量，避免长时间占用PHP进程
        $max_per_call = 50;

        while ($processed < $max_per_call) {
            $payload = $this->read_websocket_frame();
            if ($payload === null) {
                break;
            }

            $processed++;
            $this->handle_engineio_packet($payload);
        }

        return $processed;
    }

    /**
     * 处理Engine.IO/Socket.IO数据包
     *
     * @param string $payload 解码后的WebSocket负载数据
     */
    private function handle_engineio_packet($payload) {
        if ($payload === '') {
            return;
        }

        $engineio_type = substr($payload, 0, 1);
        $rest = substr($payload, 1);

        switch ($engineio_type) {
            case '0': // Engine.IO open
                // 已在握手阶段处理，这里忽略
                break;
            case '1': // Engine.IO close
                $this->connected = false;
                break;
            case '2': // Engine.IO ping，需回复pong
                $this->send_message('3');
                break;
            case '3': // Engine.IO pong
                break;
            case '4': // Engine.IO message，承载Socket.IO数据包
                $this->handle_socketio_packet($rest);
                break;
            default:
                break;
        }
    }

    /**
     * 处理Socket.IO数据包
     *
     * @param string $data Socket.IO数据包内容（去掉Engine.IO前缀后的部分）
     */
    private function handle_socketio_packet($data) {
        if ($data === '') {
            return;
        }

        $sio_type = substr($data, 0, 1);
        $payload = substr($data, 1);

        switch ($sio_type) {
            case '0': // CONNECT
                // 连接确认，无需处理
                break;
            case '1': // DISCONNECT
                $this->connected = false;
                break;
            case '2': // EVENT，格式 2["event_name",{...}]
                $decoded = $this->decode_socketio_event($payload);
                if ($decoded !== null) {
                    $message = array(
                        'type' => isset($decoded['event']) ? $decoded['event'] : 'event',
                        'data' => isset($decoded['args']) ? $decoded['args'] : array(),
                        'timestamp' => current_time('timestamp'),
                    );
                    // 兼容已有的事件处理：command/broadcast/heartbeat
                    if (isset($decoded['event'])) {
                        switch ($decoded['event']) {
                            case 'command':
                                do_action('wpforge_relay_command_received', $decoded);
                                break;
                            case 'broadcast':
                                do_action('wpforge_relay_broadcast_received', $decoded);
                                break;
                            case 'heartbeat':
                                $this->send_heartbeat();
                                break;
                            default:
                                do_action('wpforge_relay_message_received', $message);
                                break;
                        }
                    }
                    $this->handle_message(json_encode($message));
                }
                break;
            case '3': // ACK
                break;
            case '4': // ERROR
                error_log('WPForge Relay: Socket.IO error - ' . $payload);
                break;
            default:
                break;
        }
    }

    /**
     * 解码Socket.IO事件包
     *
     * Socket.IO事件格式为 JSON 数组：["event_name", arg1, arg2, ...]
     *
     * @param string $payload
     * @return array|null
     */
    private function decode_socketio_event($payload) {
        if ($payload === '') {
            return null;
        }
        $decoded = json_decode($payload, true);
        if (!is_array($decoded) || empty($decoded)) {
            return null;
        }
        $event = array_shift($decoded);
        return array(
            'event' => $event,
            'args' => $decoded,
        );
    }

    /**
     * 读取并解码一个WebSocket帧
     *
     * @return string|null 解码后的负载数据，无数据可读时返回null
     */
    private function read_websocket_frame() {
        if (!$this->socket || !is_resource($this->socket)) {
            return null;
        }

        // 读取帧头前2字节
        $header = $this->read_bytes(2);
        if ($header === null || strlen($header) < 2) {
            return null;
        }

        $b0 = ord($header[0]);
        $b1 = ord($header[1]);

        $fin = ($b0 & 0x80) !== 0;
        $opcode = $b0 & 0x0F;
        $masked = ($b1 & 0x80) !== 0;
        $length = $b1 & 0x7F;

        // 连接关闭帧
        if ($opcode === 0x08) {
            $this->connected = false;
            return null;
        }

        // ping帧，回复pong
        if ($opcode === 0x09) {
            $payload = '';
            if ($length > 0) {
                $payload = $this->read_bytes($length);
                $payload = $payload !== null ? $payload : '';
            }
            if ($masked && $payload !== '') {
                $mask = $this->read_bytes(4);
                if ($mask !== null) {
                    $payload = $this->apply_mask($payload, $mask);
                }
            }
            $this->send_pong($payload);
            return null;
        }

        // 仅处理文本帧(0x01)和二进制帧(0x02)及延续帧(0x00)
        if ($opcode !== 0x01 && $opcode !== 0x02 && $opcode !== 0x00) {
            return null;
        }

        // 读取扩展长度
        if ($length === 126) {
            $ext = $this->read_bytes(2);
            if ($ext === null) {
                return null;
            }
            $length = unpack('n', $ext)[1];
        } elseif ($length === 127) {
            $ext = $this->read_bytes(8);
            if ($ext === null) {
                return null;
            }
            $length = unpack('J', $ext)[1];
        }

        if ($length <= 0) {
            return '';
        }

        // 读取掩码（服务端发送的帧通常不带掩码，但兼容处理）
        $mask = null;
        if ($masked) {
            $mask = $this->read_bytes(4);
            if ($mask === null) {
                return null;
            }
        }

        // 读取负载数据
        $payload = $this->read_bytes($length);
        if ($payload === null) {
            return null;
        }

        if ($masked && $mask !== null) {
            $payload = $this->apply_mask($payload, $mask);
        }

        return $payload;
    }

    /**
     * 从socket读取指定字节数（非阻塞，无数据时返回null）
     *
     * @param int $len
     * @return string|null
     */
    private function read_bytes($len) {
        if (!$this->socket || !is_resource($this->socket)) {
            return null;
        }

        $data = '';
        while (strlen($data) < $len) {
            $chunk = fread($this->socket, $len - strlen($data));
            if ($chunk === false) {
                return null;
            }
            if ($chunk === '') {
                // 非阻塞模式下无数据可读
                if (feof($this->socket)) {
                    $this->connected = false;
                    return null;
                }
                // 数据尚未到达，返回已读取的部分（不足则返回null）
                if (strlen($data) === 0) {
                    return null;
                }
                break;
            }
            $data .= $chunk;
        }

        return $data;
    }

    /**
     * 应用/解除WebSocket掩码
     *
     * @param string $data
     * @param string $mask 4字节掩码
     * @return string
     */
    private function apply_mask($data, $mask) {
        $masked = '';
        $len = strlen($data);
        for ($i = 0; $i < $len; $i++) {
            $masked .= $data[$i] ^ $mask[$i % 4];
        }
        return $masked;
    }

    /**
     * 发送pong帧（响应ping）
     *
     * @param string $data
     */
    private function send_pong($data = '') {
        if (!$this->socket || !is_resource($this->socket)) {
            return;
        }
        $frame = $this->build_websocket_frame($data, 'pong');
        fwrite($this->socket, $frame);
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
        if ($this->socket && is_resource($this->socket)) {
            // 发送WebSocket关闭帧（opcode 0x08）
            $close_frame = chr(0x88) . chr(0x00);
            @fwrite($this->socket, $close_frame);
            fclose($this->socket);
        }
        $this->socket = null;
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
     *
     * @param string $data 负载数据
     * @param string $type 帧类型：text/binary/pong
     * @return string
     */
    private function build_websocket_frame($data, $type = 'text') {
        $length = strlen($data);
        $frame = '';

        // 第一个字节：FIN + opcode
        $opcode = 0x01; // 默认文本帧
        if ($type === 'binary') {
            $opcode = 0x02;
        } elseif ($type === 'pong') {
            $opcode = 0x0A;
        }
        $frame .= chr(0x80 | $opcode); // FIN + opcode

        // 客户端发送的帧必须带掩码（按RFC 6455规范）
        $mask_bit = 0x80;

        // 长度
        if ($length <= 125) {
            $frame .= chr($mask_bit | $length);
        } elseif ($length <= 65535) {
            $frame .= chr($mask_bit | 126);
            $frame .= pack('n', $length);
        } else {
            $frame .= chr($mask_bit | 127);
            $frame .= pack('J', $length);
        }

        // 生成4字节掩码并应用到数据
        $mask = openssl_random_pseudo_bytes(4);
        $frame .= $mask;

        // 掩码数据
        $masked = '';
        for ($i = 0; $i < $length; $i++) {
            $masked .= $data[$i] ^ $mask[$i % 4];
        }
        $frame .= $masked;

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
