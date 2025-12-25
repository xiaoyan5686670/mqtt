import paho.mqtt.client as mqtt

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
    print(f"📥 {msg.topic} {str(msg.payload)}")

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