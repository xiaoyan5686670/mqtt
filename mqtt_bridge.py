import paho.mqtt.client as mqtt
import sys
import os
import requests

# 指定后端API地址
BACKEND_API_URL = 'http://localhost:5003/api/update-sensor-data'

# 连接成功回调
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('✅ Connected successfully with result code 0')
        client.subscribe('testtopic/#')
        # 也订阅测试文件中使用的主题
        client.subscribe("stm32/1")
    else:
        print(f'❌ Connection failed with result code {rc}')
        if rc == 1:
            print("❌ Connection refused - incorrect protocol version")
        elif rc == 2:
            print("❌ Connection refused - invalid client identifier")
        elif rc == 3:
            print("❌ Connection refused - server unavailable")
        elif rc == 4:
            print("❌ Connection refused - bad username or password")
        elif rc == 5:
            print("❌ Connection refused - not authorised")

# 消息接收回调
def on_message(client, userdata, msg):
    payload_str = msg.payload.decode('utf-8')
    print(f"📥 {msg.topic} {payload_str}")
    
    # 通过HTTP请求将数据发送到后端API
    try:
        response = requests.post(BACKEND_API_URL, data=payload_str, headers={'Content-Type': 'text/plain'})
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Data sent to backend: {result['message']}")
        else:
            print(f"❌ Failed to send data to backend: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"❌ Error sending data to backend: {e}")

# 创建客户端
client = mqtt.Client()

# 指定回调函数
client.on_connect = on_connect
client.on_message = on_message

# 设置用户名和密码
client.username_pw_set("qxy1", "5686670")

# 建立连接 - 使用测试文件中的端口
try:
    client.connect('172.16.208.176', 18883, 60)
    print("🔌 Attempting to connect to 172.16.208.176:18883")
    
    # 开始网络循环
    client.loop_forever()
    
except Exception as e:
    print(f"❌ Exception occurred: {e}")