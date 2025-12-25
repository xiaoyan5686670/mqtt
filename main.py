import paho.mqtt.client as mqtt
import time
import json
import uuid
from config import MQTT_CONFIG, SUB_TOPICS, PUB_TOPIC


# 连接回调函数
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ 连接成功")
        # 连接成功后订阅主题
        for topic in SUB_TOPICS:
            client.subscribe(topic, qos=1)
            print(f"📡 订阅主题: {topic}")
    else:
        print(f"❌ 连接失败，错误代码: {rc}")


# 断开连接回调函数
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("⚠️ 意外断开连接")
    else:
        print("🔗 已断开连接")


# 消息接收回调函数
def on_message(client, userdata, msg):
    print(f"📥 收到消息: 主题={msg.topic}, 载荷={msg.payload.decode('utf-8')}")


# 消息发布回调函数
def on_publish(client, userdata, mid):
    print(f"📤 消息发布成功，消息ID: {mid}")


# 订阅确认回调函数
def on_subscribe(client, userdata, mid, granted_qos):
    print(f"✅ 订阅确认，消息ID: {mid}, QoS: {granted_qos}")


def run_client():
    """
    运行 MQTT 客户端，使用官方推荐的连接方式
    """
    # 创建客户端实例，使用随机生成的客户端ID
    client_id = MQTT_CONFIG['client_id'] or f"python_mqtt_client_{uuid.uuid4().hex[:8]}"
    client = mqtt.Client(client_id=client_id)
    
    # 设置回调函数
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    
    # 设置用户名和密码（如果提供）
    if MQTT_CONFIG['username'] and MQTT_CONFIG['password']:
        client.username_pw_set(MQTT_CONFIG['username'], MQTT_CONFIG['password'])
    
    # 设置TLS（如果需要）
    if MQTT_CONFIG.get('use_tls', False):
        client.tls_set(
            ca_certs=MQTT_CONFIG.get('ca_certs'),
            certfile=MQTT_CONFIG.get('certfile'),
            keyfile=MQTT_CONFIG.get('keyfile')
        )
    
    # 设置Will消息（如果需要）
    if MQTT_CONFIG.get('will_topic'):
        client.will_set(
            MQTT_CONFIG['will_topic'],
            MQTT_CONFIG.get('will_payload', 'Client is offline'),
            qos=MQTT_CONFIG.get('will_qos', 1)
        )
    
    try:
        print(f"🔌 正在连接到 {MQTT_CONFIG['server']}:{MQTT_CONFIG['port']}")
        
        # 连接到MQTT代理
        client.connect(MQTT_CONFIG['server'], MQTT_CONFIG['port'], keepalive=MQTT_CONFIG['keepalive'])
        
        # 启动网络循环
        client.loop_start()
        
        # 等待连接建立
        time.sleep(1)
        
        # 发送几条测试消息
        for i in range(10):
            message = {
                'message_id': i+1,
                'content': f'这是第 {i+1} 条测试消息',
                'timestamp': time.time(),
                'client_id': client_id
            }
            result, mid = client.publish(PUB_TOPIC, json.dumps(message), qos=1)
            if result == mqtt.MQTT_ERR_SUCCESS:
                print(f"⏳ 发布消息: {json.dumps(message)}")
            else:
                print(f"❌ 消息发布失败，错误代码: {result}")
            time.sleep(2)  # 等待 2 秒
        
        # 保持连接一段时间以接收消息
        print("⏳ 等待接收消息...")
        time.sleep(20)
        
        # 停止网络循环
        client.loop_stop()
        client.disconnect()
        print("👋 客户端已断开连接")
        
    except TimeoutError:
        print(f"❌ 连接超时，请检查服务器地址 {MQTT_CONFIG['server']}:{MQTT_CONFIG['port']} 是否正确，以及服务器是否正常运行")
    except ConnectionRefusedError:
        print(f"❌ 连接被拒绝，请检查服务器是否运行在 {MQTT_CONFIG['server']}:{MQTT_CONFIG['port']}")
    except OSError as e:
        print(f"❌ 网络错误: {e}")
        print("💡 请检查:")
        print(f"  - 网络连接是否正常")
        print(f"  - 服务器 {MQTT_CONFIG['server']} 是否可达")
        print(f"  - 端口 {MQTT_CONFIG['port']} 是否开放")
        print(f"  - 防火墙设置是否允许连接")
    except Exception as e:
        print(f"❌ 发生错误: {e}")


def run_client_with_callback_api():
    """
    使用回调API的示例 - 更接近官方文档的用法
    """
    # 创建客户端
    client_id = f"python_callback_client_{uuid.uuid4().hex[:8]}"
    client = mqtt.Client(client_id=client_id)
    
    # 设置认证
    if MQTT_CONFIG['username'] and MQTT_CONFIG['password']:
        client.username_pw_set(MQTT_CONFIG['username'], MQTT_CONFIG['password'])
    
    # 连接
    client.connect(MQTT_CONFIG['server'], MQTT_CONFIG['port'], keepalive=MQTT_CONFIG['keepalive'])
    
    # 订阅主题
    for topic in SUB_TOPICS:
        client.subscribe(topic, qos=1)
        print(f"📡 订阅主题: {topic}")
    
    # 定义消息处理函数
    def message_callback(client, userdata, message):
        print(f"📥 收到消息: 主题={message.topic}, 载荷={message.payload.decode('utf-8')}")
    
    # 为特定主题设置回调
    for topic in SUB_TOPICS:
        client.message_callback_add(topic, message_callback)
    
    # 启动网络循环
    client.loop_start()
    
    # 发布消息
    for i in range(5):
        message = {
            'message_id': i+1,
            'content': f'回调API测试消息 {i+1}',
            'timestamp': time.time(),
            'client_id': client_id
        }
        client.publish(PUB_TOPIC, json.dumps(message), qos=1)
        print(f"⏳ 发布消息: {json.dumps(message)}")
        time.sleep(1)
    
    # 保持运行
    time.sleep(10)
    
    # 停止循环
    client.loop_stop()
    client.disconnect()


def run_client_with_async_api():
    """
    使用异步API的示例 - 适用于异步应用
    """
    import asyncio
    
    async def async_main():
        # 创建客户端
        client_id = f"python_async_client_{uuid.uuid4().hex[:8]}"
        aclient = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        
        # 设置回调
        aclient.on_connect = on_connect
        aclient.on_message = on_message
        
        # 如果有认证信息则设置
        if MQTT_CONFIG['username'] and MQTT_CONFIG['password']:
            aclient.username_pw_set(MQTT_CONFIG['username'], MQTT_CONFIG['password'])
        
        # 异步连接
        await aclient.connect_async(MQTT_CONFIG['server'], MQTT_CONFIG['port'])
        
        # 启动异步循环
        aclient.loop_start()
        
        # 订阅主题
        for topic in SUB_TOPICS:
            aclient.subscribe(topic, qos=1)
        
        # 发布消息
        for i in range(3):
            message = {
                'message_id': i+1,
                'content': f'异步API测试消息 {i+1}',
                'timestamp': time.time(),
                'client_id': client_id
            }
            aclient.publish(PUB_TOPIC, json.dumps(message), qos=1)
            await asyncio.sleep(1)
        
        await asyncio.sleep(10)
        
        # 断开连接
        aclient.loop_stop()
        aclient.disconnect()
    
    # 运行异步函数
    asyncio.run(async_main())


if __name__ == '__main__':
    print("🚀 启动 MQTT Python 客户端...")
    print("💡 提示: 请确保 config.py 中的服务器地址、用户名和密码正确")
    
    # 可以选择运行不同版本的客户端
    print("\n选择运行模式:")
    print("1. 标准模式 (默认)")
    print("2. 回调API模式")
    print("3. 异步API模式")
    
    choice = input("请输入选择 (1/2/3, 默认为1): ").strip() or "1"
    
    if choice == "1":
        run_client()
    elif choice == "2":
        run_client_with_callback_api()
    elif choice == "3":
        run_client_with_async_api()
    else:
        print("无效选择，运行默认模式")
        run_client()