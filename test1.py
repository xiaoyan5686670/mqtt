import paho.mqtt.client as mqtt

# 连接成功回调
def on_connect(client, userdata, flags, rc):
    print('Connected with result code '+str(rc))
    client.subscribe('testtopic/#')

# 消息接收回调
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()

# 指定回调函数
client.on_connect = on_connect
client.on_message = on_message
client.user_data_set([])

# 建立连接
client.connect('172.16.208.176', 18883, 60)
# 发布消息
#client.publish('emqtt',payload='Hello World',qos=0)
client.subscribe("stm32/1")

client.loop_forever()
print(f"Received the following message: {client.user_data_get()}")
