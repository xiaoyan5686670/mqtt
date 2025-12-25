from flask import Flask, jsonify, request
import json
import threading
import time
from datetime import datetime, timedelta
import uuid
from flask_cors import CORS  # 添加CORS支持

app = Flask(__name__)
CORS(app)  # 启用CORS

# 设备存储
devices = {}

# 传感器数据存储
sensor_data = {}

# 记录最后接收数据的时间
last_data_received_time = {}

# 数据过期时间（30秒）
DATA_EXPIRATION_SECONDS = 30

# 设备模型类
class Device:
    def __init__(self, device_id: str, name: str, protocol: str, 
                 location: dict = None, properties: dict = None):
        self.id = device_id
        self.name = name
        self.protocol = protocol
        self.location = location or {
            'building': '未知楼宇',
            'floor': '未知楼层', 
            'room': '未知房间',
            'position': '未知位置'
        }
        self.properties = properties or {}
        self.created_time = datetime.now().isoformat()
        self.last_active_time = None
        self.status = "offline"
        self.config = {}

def create_device(device_id, name, protocol, location=None, properties=None):
    """创建设备"""
    if device_id in devices:
        return False, "Device already exists"
    
    device = Device(device_id, name, protocol, location, properties)
    devices[device_id] = device
    sensor_data[device_id] = {
        'temperature1': 0.0,
        'humidity1': 0.0,
        'temperature2': 0.0,
        'humidity2': 0.0,
        'relay_status': 0,
        'pb8_level': 0,
        'timestamp': None
    }
    return True, "Device created successfully"

def update_device_status(device_id, status):
    """更新设备状态"""
    if device_id in devices:
        devices[device_id].status = status
        devices[device_id].last_active_time = datetime.now().isoformat()

# 解析从MQTT接收到的数据
def parse_sensor_data(payload_str):
    """
    解析传感器数据字符串
    格式示例: "stm32/1 Temperature1: 22.10 C, Humidity1: 16.10 %\r\nTemperature2: 21.80 C, Humidity2: 23.40 %\r\nRelay Status: 1\r\nPB8 Level: 1\r\n"
    """
    global sensor_data, last_data_received_time
    
    try:
        # 从payload中解析传感器ID，格式为 "stm32/1 Temperature1:..."
        payload_lines = payload_str.split('\r\n')
        first_line = payload_lines[0]
        
        # 提取传感器ID，假设格式为 "topic_name Temperature1:..."
        topic_and_data = first_line.split(' ', 1)
        if len(topic_and_data) > 1:
            device_id = topic_and_data[0].replace('/', '_')  # 将 "stm32/1" 转换为 "stm32_1"
        else:
            device_id = 'default'
        
        # 重新构建数据部分（去掉传感器ID部分）
        data_lines = [first_line[len(topic_and_data[0])+1:]] + payload_lines[1:]  # 去掉第一个单词和空格
        
        # 如果设备不存在，自动注册
        if device_id not in devices:
            create_device(
                device_id=device_id,
                name=f"自动注册设备-{device_id}",
                protocol="mqtt",
                location={'building': f'未知楼宇({device_id})', 'floor': '未知楼层', 'room': '未知房间', 'position': '未知位置'}
            )
            print(f"✅ 自动注册新设备: {device_id}")
        
        # 更新设备状态为在线
        update_device_status(device_id, "online")
        
        # 解析数据行
        for line in data_lines:
            line = line.strip()
            if line:
                # 对每行再按逗号分割
                parts = line.split(', ')
                for part in parts:
                    part = part.strip()
                    if part.startswith('Temperature1:'):
                        # 提取温度1
                        sub_parts = part.split()
                        sensor_data[device_id]['temperature1'] = float(sub_parts[1])
                    elif part.startswith('Humidity1:'):
                        # 提取湿度1
                        sub_parts = part.split()
                        sensor_data[device_id]['humidity1'] = float(sub_parts[1])
                    elif part.startswith('Temperature2:'):
                        # 提取温度2
                        sub_parts = part.split()
                        sensor_data[device_id]['temperature2'] = float(sub_parts[1])
                    elif part.startswith('Humidity2:'):
                        # 提取湿度2
                        sub_parts = part.split()
                        sensor_data[device_id]['humidity2'] = float(sub_parts[1])
                    elif part.startswith('Relay Status:'):
                        # 提取继电器状态
                        sub_parts = part.split()
                        sensor_data[device_id]['relay_status'] = int(sub_parts[2])
                    elif part.startswith('PB8 Level:'):
                        # 提取PB8电平
                        sub_parts = part.split()
                        sensor_data[device_id]['pb8_level'] = int(sub_parts[2])
        
        sensor_data[device_id]['timestamp'] = datetime.now().isoformat()
        last_data_received_time[device_id] = datetime.now()
        print(f"✅ Updated sensor data for {device_id}: {sensor_data[device_id]}")
        
    except Exception as e:
        print(f"解析传感器数据时出错: {e}")

# 定期检查数据是否过期
def check_data_expiration():
    global sensor_data, last_data_received_time
    while True:
        time.sleep(5)  # 每5秒检查一次
        now = datetime.now()
        
        # 遍历所有传感器，检查是否过期
        for device_id in list(last_data_received_time.keys()):
            if device_id in last_data_received_time:
                if now - last_data_received_time[device_id] > timedelta(seconds=DATA_EXPIRATION_SECONDS):
                    # 数据已过期，重置为默认值
                    print(f"⚠️ Device {device_id} data expired, marking as offline")
                    if device_id in sensor_data:
                        sensor_data[device_id].update({
                            'temperature1': 0.0,
                            'humidity1': 0.0,
                            'temperature2': 0.0,
                            'humidity2': 0.0,
                            'relay_status': 0,
                            'pb8_level': 0,
                            'timestamp': now.isoformat()
                        })
                    # 更新设备状态为离线
                    update_device_status(device_id, "offline")

# 启动数据过期检查线程
def start_expiration_checker():
    thread = threading.Thread(target=check_data_expiration, daemon=True)
    thread.start()

# 获取所有设备信息
@app.route('/api/devices', methods=['GET'])
def get_devices():
    """获取所有设备列表"""
    result = []
    for device_id, device in devices.items():
        # 获取设备最新数据
        data = sensor_data.get(device_id, {})
        device_info = {
            'id': device.id,
            'name': device.name,
            'protocol': device.protocol,
            'location': device.location,
            'properties': device.properties,
            'status': device.status,
            'last_active_time': device.last_active_time,
            'created_time': device.created_time,
            'current_data': data
        }
        result.append(device_info)
    
    return jsonify(result)

# 获取单个设备信息
@app.route('/api/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    """获取单个设备信息"""
    if device_id not in devices:
        return jsonify({'error': 'Device not found'}), 404
    
    device = devices[device_id]
    data = sensor_data.get(device_id, {})
    
    device_info = {
        'id': device.id,
        'name': device.name,
        'protocol': device.protocol,
        'location': device.location,
        'properties': device.properties,
        'status': device.status,
        'last_active_time': device.last_active_time,
        'created_time': device.created_time,
        'current_data': data
    }
    
    return jsonify(device_info)

# 注册新设备
@app.route('/api/devices', methods=['POST'])
def register_device():
    """注册新设备"""
    try:
        data = request.json
        device_id = data.get('id') or str(uuid.uuid4())
        name = data.get('name', f'设备-{device_id}')
        protocol = data.get('protocol', 'mqtt')
        location = data.get('location')
        properties = data.get('properties')
        
        success, message = create_device(device_id, name, protocol, location, properties)
        if success:
            return jsonify({'status': 'success', 'message': message, 'device_id': device_id})
        else:
            return jsonify({'status': 'error', 'message': message}), 400
    except Exception as e:
        print(f"注册设备时出错: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 更新设备信息
@app.route('/api/devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    """更新设备信息"""
    if device_id not in devices:
        return jsonify({'error': 'Device not found'}), 404
    
    try:
        data = request.json
        device = devices[device_id]
        
        # 更新可修改的字段
        if 'name' in data:
            device.name = data['name']
        if 'location' in data:
            device.location = data['location']
        if 'properties' in data:
            device.properties = data['properties']
        
        return jsonify({'status': 'success', 'message': 'Device updated successfully'})
    except Exception as e:
        print(f"更新设备时出错: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 删除设备
@app.route('/api/devices/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    """删除设备"""
    if device_id not in devices:
        return jsonify({'error': 'Device not found'}), 404
    
    # 从所有存储中删除设备
    del devices[device_id]
    if device_id in sensor_data:
        del sensor_data[device_id]
    if device_id in last_data_received_time:
        del last_data_received_time[device_id]
    
    return jsonify({'status': 'success', 'message': 'Device deleted successfully'})

# 新增API端点：接收MQTT桥接程序发送的数据
@app.route('/api/update-sensor-data', methods=['POST'])
def update_sensor_data():
    """接收MQTT数据并更新传感器数据"""
    try:
        payload_str = request.data.decode('utf-8')
        parse_sensor_data(payload_str)
        return jsonify({'status': 'success', 'message': 'Sensor data updated successfully'})
    except Exception as e:
        print(f"更新传感器数据时出错: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({'status': 'OK'})

if __name__ == '__main__':
    # 启动数据过期检查器
    start_expiration_checker()
    # 使用不同的端口以避免与macOS AirPlay Receiver冲突
    # 绑定到所有网络接口，确保可以从其他地址访问
    app.run(debug=True, host='0.0.0.0', port=5003)
