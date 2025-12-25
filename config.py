"""
EMQ X 连接配置文件
"""

# MQTT 服务器配置
MQTT_CONFIG = {
    'server': '172.16.208.176',  # EMQ X 服务器地址
    'port': 18883,               # MQTT 端口，注意：测试文件中使用的是18883，不是1883
    'username': 'qxy1',         # 用户名 - 从测试文件推测应该是admin
    'password': '5686670',        # 密码 - 从测试文件推测应该是public
    'client_id': 'python_client',  # 客户端 ID，留空则自动生成
    'keepalive': 60,             # 心跳间隔（秒）
    'timeout': 10,               # 连接超时时间（秒）
    
    # 高级选项
    'use_tls': False,            # 是否使用TLS加密 - 根据端口18883，可能需要启用
    'ca_certs': None,            # CA证书路径
    'certfile': None,            # 客户端证书路径
    'keyfile': None,             # 客户端密钥路径
    
    # Will消息选项
    'will_topic': 'clients/python_client_status',  # Will消息主题
    'will_payload': 'Client is offline',           # Will消息载荷
    'will_qos': 1,               # Will消息QoS等级
}

# 订阅主题配置
SUB_TOPICS = [
    'stm32/1',
    'pc/1',
]

# 发布主题配置
PUB_TOPIC = 'pc/1'