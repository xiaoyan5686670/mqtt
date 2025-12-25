"""
EMQ X 连接配置文件示例
复制此文件为 config.py 并修改相应参数
"""

# MQTT 服务器配置
MQTT_CONFIG = {
    'server': '172.16.208.176',  # EMQ X 服务器地址
    'port': 1883,                # MQTT 端口，非加密连接 (默认1883)，TLS/SSL连接使用8883
    'username': 'admin',         # 用户名，使用您自己的凭据
    'password': 'public',        # 密码，使用您自己的凭据
    'client_id': 'python_client_123',  # 客户端 ID，确保唯一性，留空则自动生成
    'keepalive': 60,             # 心跳间隔（秒），默认为60
    'timeout': 10,               # 连接超时时间（秒）
    
    # TLS/SSL 配置（如果需要安全连接）
    'use_tls': False,            # 是否使用TLS加密连接
    'ca_certs': '/path/to/ca.crt',      # CA证书路径
    'certfile': '/path/to/client.crt',  # 客户端证书路径
    'keyfile': '/path/to/client.key',   # 客户端密钥路径
    
    # Will 消息配置（遗嘱消息）
    'will_topic': 'clients/python_client_status',  # Will消息主题
    'will_payload': 'Client is offline',           # Will消息载荷
    'will_qos': 1,               # Will消息QoS等级
}

# 订阅主题配置
SUB_TOPICS = [
    'test/topic1',
    'test/topic2',
    'sensor/status',
]

# 发布主题配置
PUB_TOPIC = 'test/python_client'

"""
常见问题排查:

1. 服务器地址和端口:
   - 检查EMQX服务器是否正在运行
   - 确认服务器IP地址是否正确
   - 确认端口是否正确 (1883用于普通连接，8883用于SSL连接)

2. 认证信息:
   - 检查用户名和密码是否正确
   - 确认用户是否有连接权限

3. 网络问题:
   - 检查防火墙设置
   - 确认网络连接是否正常
   - 尝试ping服务器地址

4. EMQX配置:
   - 确认EMQX允许客户端连接
   - 检查EMQX日志以获取更多信息

5. TLS/SSL连接:
   - 如果启用TLS，确认证书路径是否正确
   - 确认证书是否有效
"""