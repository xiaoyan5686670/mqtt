<template>
  <div id="app">
    <header class="header">
      <h1>MQTT 传感器数据监控面板</h1>
    </header>
    
    <main class="main-content">
      <div class="controls">
        <button @click="refreshDevices" class="btn-refresh">刷新设备列表</button>
        <button @click="showAddDeviceModal = true" class="btn-add">添加设备</button>
        <p class="last-refresh">最后刷新: {{ lastRefreshTime ? new Date(lastRefreshTime).toLocaleString() : '从未刷新' }}</p>
      </div>
      
      <div class="device-cards">
        <div 
          v-for="device in devices" 
          :key="device.id"
          :class="['card', { 'offline': device.status !== 'online' }]"
        >
          <div class="device-header">
            <h3>{{ device.name }} ({{ device.id }})</h3>
            <span :class="['status-badge', device.status]">{{ device.status }}</span>
          </div>
          
          <div class="device-location">
            <p><strong>位置:</strong> {{ device.location.building }} - {{ device.location.floor }}楼 - {{ device.location.room }} - {{ device.location.position }}</p>
          </div>
          
          <div class="sensor-values">
            <p>温度1: <span :class="{'value': true, 'zero-data': device.current_data.temperature1 === 0 && device.current_data.timestamp && isDataFresh(device.current_data.timestamp)}">{{ device.current_data.temperature1 }}°C</span></p>
            <p>湿度1: <span :class="{'value': true, 'zero-data': device.current_data.humidity1 === 0 && device.current_data.timestamp && isDataFresh(device.current_data.timestamp)}">{{ device.current_data.humidity1 }}%</span></p>
            <p>温度2: <span :class="{'value': true, 'zero-data': device.current_data.temperature2 === 0 && device.current_data.timestamp && isDataFresh(device.current_data.timestamp)}">{{ device.current_data.temperature2 }}°C</span></p>
            <p>湿度2: <span :class="{'value': true, 'zero-data': device.current_data.humidity2 === 0 && device.current_data.timestamp && isDataFresh(device.current_data.timestamp)}">{{ device.current_data.humidity2 }}%</span></p>
            <p>继电器状态: 
              <span :class="device.current_data.relay_status ? 'status-on' : (device.current_data.relay_status === 0 && device.current_data.timestamp && isDataFresh(device.current_data.timestamp) ? 'status-off-zero' : 'status-off')">
                {{ device.current_data.relay_status ? '开启' : '关闭' }}
              </span>
            </p>
            <p>PB8 电平: 
              <span :class="device.current_data.pb8_level ? 'status-on' : (device.current_data.pb8_level === 0 && device.current_data.timestamp && isDataFresh(device.current_data.timestamp) ? 'status-off-zero' : 'status-off')">
                {{ device.current_data.pb8_level ? '高电平' : '低电平' }}
              </span>
            </p>
          </div>
          
          <div class="device-meta">
            <p><strong>协议:</strong> {{ device.protocol }}</p>
            <p><strong>最后活动:</strong> {{ device.last_active_time ? new Date(device.last_active_time).toLocaleString() : '从未活动' }}</p>
            <p><strong>创建时间:</strong> {{ new Date(device.created_time).toLocaleString() }}</p>
          </div>
          
          <div class="device-actions">
            <button @click="editDevice(device)" class="btn-edit">编辑</button>
            <button @click="deleteDevice(device.id)" class="btn-delete">删除</button>
          </div>
        </div>
      </div>
      
      <!-- 添加/编辑设备模态框 -->
      <div v-if="showAddDeviceModal" class="modal">
        <div class="modal-content">
          <h3>{{ editingDevice ? '编辑设备' : '添加设备' }}</h3>
          
          <div class="form-group">
            <label>设备ID:</label>
            <input 
              v-model="currentDevice.id" 
              :disabled="!!editingDevice"
              type="text" 
              placeholder="设备唯一标识"
              class="form-control"
            />
          </div>
          
          <div class="form-group">
            <label>设备名称:</label>
            <input 
              v-model="currentDevice.name" 
              type="text" 
              placeholder="设备名称"
              class="form-control"
            />
          </div>
          
          <div class="form-group">
            <label>协议类型:</label>
            <select v-model="currentDevice.protocol" class="form-control">
              <option value="mqtt">MQTT</option>
              <option value="coap">CoAP</option>
              <option value="tcp">TCP</option>
            </select>
          </div>
          
          <h4>位置信息</h4>
          <div class="form-row">
            <div class="form-group">
              <label>楼宇:</label>
              <input 
                v-model="currentDevice.location.building" 
                type="text" 
                placeholder="楼宇"
                class="form-control"
              />
            </div>
            
            <div class="form-group">
              <label>楼层:</label>
              <input 
                v-model="currentDevice.location.floor" 
                type="text" 
                placeholder="楼层"
                class="form-control"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>房间:</label>
              <input 
                v-model="currentDevice.location.room" 
                type="text" 
                placeholder="房间"
                class="form-control"
              />
            </div>
            
            <div class="form-group">
              <label>具体位置:</label>
              <input 
                v-model="currentDevice.location.position" 
                type="text" 
                placeholder="具体位置"
                class="form-control"
              />
            </div>
          </div>
          
          <div class="modal-actions">
            <button @click="saveDevice" class="btn-save">{{ editingDevice ? '更新' : '添加' }}</button>
            <button @click="closeModal" class="btn-cancel">取消</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
// 从API获取和更新传感器配置的函数
const apiBase = 'http://localhost:5002/api'  // 确保与后端端口一致

// 获取所有设备
async function fetchAllDevices() {
  try {
    const response = await fetch(`${apiBase}/devices`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    return data
  } catch (error) {
    console.error('获取设备列表失败:', error)
    throw error
  }
}

// 注册设备
async function registerDevice(device) {
  try {
    const response = await fetch(`${apiBase}/devices`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(device)
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('注册设备失败:', error)
    throw error
  }
}

// 更新设备
async function updateDevice(deviceId, device) {
  try {
    const response = await fetch(`${apiBase}/devices/${deviceId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(device)
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('更新设备失败:', error)
    throw error
  }
}

// 删除设备
async function deleteDeviceAPI(deviceId) {
  try {
    const response = await fetch(`${apiBase}/devices/${deviceId}`, {
      method: 'DELETE'
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('删除设备失败:', error)
    throw error
  }
}

import { ref, onMounted } from 'vue'

export default {
  name: 'App',
  setup() {
    const devices = ref([])
    const lastRefreshTime = ref(null)
    const showAddDeviceModal = ref(false)
    const editingDevice = ref(null)
    
    // 当前正在编辑或添加的设备
    const currentDevice = ref({
      id: '',
      name: '',
      protocol: 'mqtt',
      location: {
        building: '',
        floor: '',
        room: '',
        position: ''
      }
    })
    
    // 检查数据是否新鲜（在30秒内）
    const isDataFresh = (timestamp) => {
      if (!timestamp) return false
      const dataTimestamp = new Date(timestamp).getTime()
      const now = Date.now()
      const timeDiff = now - dataTimestamp
      return timeDiff < 30000
    }
    
    // 刷新设备列表
    const refreshDevices = async () => {
      try {
        const data = await fetchAllDevices()
        devices.value = data
        lastRefreshTime.value = Date.now()
      } catch (error) {
        console.error('刷新设备列表失败:', error)
      }
    }
    
    // 添加新设备
    const addDevice = () => {
      editingDevice.value = null
      currentDevice.value = {
        id: '',
        name: '',
        protocol: 'mqtt',
        location: {
          building: '',
          floor: '',
          room: '',
          position: ''
        }
      }
      showAddDeviceModal.value = true
    }
    
    // 编辑设备
    const editDevice = (device) => {
      editingDevice.value = device
      currentDevice.value = {
        id: device.id,
        name: device.name,
        protocol: device.protocol,
        location: { ...device.location }
      }
      showAddDeviceModal.value = true
    }
    
    // 保存设备（新增或更新）
    const saveDevice = async () => {
      try {
        if (editingDevice.value) {
          // 更新设备
          await updateDevice(currentDevice.value.id, currentDevice.value)
        } else {
          // 添加设备
          await registerDevice(currentDevice.value)
        }
        showAddDeviceModal.value = false
        await refreshDevices() // 刷新列表
      } catch (error) {
        console.error('保存设备失败:', error)
      }
    }
    
    // 删除设备
    const deleteDevice = async (deviceId) => {
      if (confirm(`确定要删除设备 "${deviceId}" 吗？`)) {
        try {
          await deleteDeviceAPI(deviceId)
          await refreshDevices() // 刷新列表
        } catch (error) {
          console.error('删除设备失败:', error)
        }
      }
    }
    
    // 关闭模态框
    const closeModal = () => {
      showAddDeviceModal.value = false
    }
    
    onMounted(async () => {
      await refreshDevices()
    })
    
    return {
      devices,
      lastRefreshTime,
      showAddDeviceModal,
      editingDevice,
      currentDevice,
      refreshDevices,
      addDevice,
      editDevice,
      saveDevice,
      deleteDevice,
      closeModal,
      isDataFresh
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  background-color: #34495e;
  color: white;
  padding: 1rem;
  text-align: center;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.btn-refresh, .btn-add {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  margin-right: 10px;
}

.btn-refresh {
  background-color: #3498db;
  color: white;
}

.btn-add {
  background-color: #2ecc71;
  color: white;
}

.btn-refresh:hover, .btn-add:hover {
  opacity: 0.9;
}

.last-refresh {
  margin: 0;
  color: #7f8c8d;
}

.device-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: border 0.3s;
  position: relative;
}

.card.offline {
  border: 2px solid #e74c3c;
  opacity: 0.8;
}

.device-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.device-header h3 {
  margin: 0;
  color: #34495e;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.status-badge.online {
  background-color: #2ecc71;
  color: white;
}

.status-badge.offline {
  background-color: #e74c3c;
  color: white;
}

.device-location {
  margin: 1rem 0;
  padding: 0.5rem;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.sensor-values {
  margin: 1rem 0;
  padding: 0.5rem 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
}

.value {
  font-weight: bold;
  color: #3498db;
  font-size: 1.1rem;
}

/* 为零的数据值使用红色字体 */
.value.zero-data {
  color: #e74c3c;
}

.status-on {
  color: #2ecc71;
  font-weight: bold;
}

.status-off {
  color: #e74c3c;
  font-weight: bold;
}

/* 为零的设备状态使用红色字体 */
.status-off-zero {
  color: #e74c3c;
  font-weight: bold;
}

.device-meta {
  margin: 1rem 0;
  font-size: 0.9rem;
  color: #7f8c8d;
}

.device-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.btn-edit, .btn-delete {
  padding: 0.3rem 0.8rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-edit {
  background-color: #f39c12;
  color: white;
}

.btn-delete {
  background-color: #e74c3c;
  color: white;
}

/* 模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 1rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-row .form-group {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 0.3rem;
  font-weight: bold;
  color: #2c3e50;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-save, .btn-cancel {
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-save {
  background-color: #3498db;
  color: white;
}

.btn-cancel {
  background-color: #95a5a6;
  color: white;
}
</style>