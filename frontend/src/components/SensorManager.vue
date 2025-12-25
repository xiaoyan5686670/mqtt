<template>
  <div class="sensor-manager">
    <h2>传感器配置管理</h2>
    
    <div class="controls">
      <button @click="addNewSensor" class="btn btn-primary">添加传感器</button>
      <button @click="loadConfigs" class="btn btn-secondary">刷新列表</button>
    </div>
    
    <div class="sensor-list">
      <div v-for="config in sensorConfigs" :key="config.id" class="sensor-card">
        <div class="sensor-header">
          <h3>{{ config.name }}</h3>
          <div class="sensor-id">ID: {{ config.id }}</div>
        </div>
        
        <div class="sensor-details">
          <div class="location-info">
            <h4>位置信息</h4>
            <div class="form-group">
              <label>楼宇:</label>
              <input 
                type="text" 
                v-model="config.location.building" 
                :disabled="!config.editing"
                class="form-control"
              />
            </div>
            <div class="form-group">
              <label>楼层:</label>
              <input 
                type="text" 
                v-model="config.location.floor" 
                :disabled="!config.editing"
                class="form-control"
              />
            </div>
            <div class="form-group">
              <label>房间:</label>
              <input 
                type="text" 
                v-model="config.location.room" 
                :disabled="!config.editing"
                class="form-control"
              />
            </div>
            <div class="form-group">
              <label>具体位置:</label>
              <input 
                type="text" 
                v-model="config.location.position" 
                :disabled="!config.editing"
                class="form-control"
              />
            </div>
          </div>
          
          <div class="sensor-info">
            <h4>传感器信息</h4>
            <div class="form-group">
              <label>名称:</label>
              <input 
                type="text" 
                v-model="config.name" 
                :disabled="!config.editing"
                class="form-control"
              />
            </div>
            <div class="form-group">
              <label>描述:</label>
              <textarea 
                v-model="config.description" 
                :disabled="!config.editing"
                class="form-control"
              ></textarea>
            </div>
          </div>
        </div>
        
        <div class="sensor-actions">
          <button 
            v-if="!config.editing" 
            @click="startEditing(config)" 
            class="btn btn-edit"
          >
            编辑
          </button>
          <button 
            v-if="config.editing" 
            @click="saveConfig(config)" 
            class="btn btn-save"
          >
            保存
          </button>
          <button 
            v-if="config.editing" 
            @click="cancelEditing(config)" 
            class="btn btn-cancel"
          >
            取消
          </button>
          <button 
            @click="deleteConfig(config)" 
            class="btn btn-delete"
          >
            删除
          </button>
        </div>
      </div>
    </div>
    
    <!-- 添加新传感器的表单 -->
    <div v-if="showAddForm" class="add-sensor-form">
      <h3>添加新传感器</h3>
      <div class="form-group">
        <label>传感器ID:</label>
        <input 
          type="text" 
          v-model="newSensor.id" 
          placeholder="例如: sensor_003"
          class="form-control"
        />
      </div>
      <div class="form-group">
        <label>传感器名称:</label>
        <input 
          type="text" 
          v-model="newSensor.name" 
          placeholder="例如: A栋-机房301-温湿度传感器"
          class="form-control"
        />
      </div>
      <div class="form-group">
        <label>楼宇:</label>
        <input 
          type="text" 
          v-model="newSensor.location.building" 
          placeholder="例如: A栋"
          class="form-control"
        />
      </div>
      <div class="form-group">
        <label>楼层:</label>
        <input 
          type="text" 
          v-model="newSensor.location.floor" 
          placeholder="例如: 3"
          class="form-control"
        />
      </div>
      <div class="form-group">
        <label>房间:</label>
        <input 
          type="text" 
          v-model="newSensor.location.room" 
          placeholder="例如: 机房301"
          class="form-control"
        />
      </div>
      <div class="form-group">
        <label>具体位置:</label>
        <input 
          type="text" 
          v-model="newSensor.location.position" 
          placeholder="例如: 服务器架右侧"
          class="form-control"
        />
      </div>
      <div class="form-group">
        <label>描述:</label>
        <textarea 
          v-model="newSensor.description" 
          placeholder="传感器功能描述"
          class="form-control"
        ></textarea>
      </div>
      <div class="form-actions">
        <button @click="createSensor" class="btn btn-save">创建</button>
        <button @click="cancelAdd" class="btn btn-cancel">取消</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

// 从API获取和更新传感器配置的函数
const apiBase = '/api'

// 获取所有传感器配置
const fetchSensorConfigs = async () => {
  try {
    const response = await fetch(`${apiBase}/sensor-configs`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('获取传感器配置失败:', error)
    throw error
  }
}

// 更新传感器配置
const updateSensorConfig = async (sensorId, config) => {
  try {
    const response = await fetch(`${apiBase}/sensor-configs/${sensorId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(config)
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('更新传感器配置失败:', error)
    throw error
  }
}

// 删除传感器配置
const deleteSensorConfig = async (sensorId) => {
  try {
    const response = await fetch(`${apiBase}/sensor-configs/${sensorId}`, {
      method: 'DELETE'
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('删除传感器配置失败:', error)
    throw error
  }
}

// 创建传感器配置
const createSensorConfig = async (config) => {
  try {
    const response = await fetch(`${apiBase}/sensor-configs/${config.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(config)
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('创建传感器配置失败:', error)
    throw error
  }
}

export default {
  name: 'SensorManager',
  setup() {
    const sensorConfigs = ref([])
    const showAddForm = ref(false)
    const originalConfigs = ref({}) // 保存原始配置用于取消编辑
    
    const newSensor = ref({
      id: '',
      name: '',
      location: {
        building: '',
        floor: '',
        room: '',
        position: ''
      },
      description: ''
    })
    
    // 加载传感器配置
    const loadConfigs = async () => {
      try {
        const configs = await fetchSensorConfigs()
        // 为每个配置添加editing属性
        sensorConfigs.value = configs.map(config => ({
          ...config,
          editing: false,
          original: { ...JSON.parse(JSON.stringify(config)) } // 深拷贝原始配置
        }))
      } catch (error) {
        console.error('加载传感器配置失败:', error)
      }
    }
    
    // 开始编辑传感器配置
    const startEditing = (config) => {
      config.editing = true
      // 保存原始配置用于取消编辑
      config.original = JSON.parse(JSON.stringify({
        name: config.name,
        location: config.location,
        description: config.description
      }))
    }
    
    // 保存传感器配置
    const saveConfig = async (config) => {
      try {
        await updateSensorConfig(config.id, config)
        config.editing = false
        console.log('传感器配置保存成功')
      } catch (error) {
        console.error('保存传感器配置失败:', error)
      }
    }
    
    // 取消编辑，恢复原始配置
    const cancelEditing = (config) => {
      config.name = config.original.name
      config.location = config.original.location
      config.description = config.original.description
      config.editing = false
    }
    
    // 删除传感器配置
    const deleteConfig = async (config) => {
      if (confirm(`确定要删除传感器 "${config.name}" 吗？`)) {
        try {
          await deleteSensorConfig(config.id)
          sensorConfigs.value = sensorConfigs.value.filter(c => c.id !== config.id)
          console.log('传感器配置删除成功')
        } catch (error) {
          console.error('删除传感器配置失败:', error)
        }
      }
    }
    
    // 显示添加传感器表单
    const addNewSensor = () => {
      showAddForm.value = true
      // 重置新传感器数据
      newSensor.value = {
        id: '',
        name: '',
        location: {
          building: '',
          floor: '',
          room: '',
          position: ''
        },
        description: ''
      }
    }
    
    // 创建新传感器
    const createSensor = async () => {
      if (!newSensor.value.id) {
        alert('请输入传感器ID')
        return
      }
      
      try {
        await createSensorConfig(newSensor.value)
        showAddForm.value = false
        loadConfigs() // 重新加载列表
        console.log('传感器创建成功')
      } catch (error) {
        console.error('创建传感器失败:', error)
      }
    }
    
    // 取消添加
    const cancelAdd = () => {
      showAddForm.value = false
    }
    
    onMounted(() => {
      loadConfigs()
    })
    
    return {
      sensorConfigs,
      showAddForm,
      newSensor,
      loadConfigs,
      startEditing,
      saveConfig,
      cancelEditing,
      deleteConfig,
      addNewSensor,
      createSensor,
      cancelAdd
    }
  }
}
</script>

<style scoped>
.sensor-manager {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.controls {
  margin-bottom: 20px;
}

.btn {
  padding: 8px 16px;
  margin-right: 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-edit {
  background-color: #f39c12;
  color: white;
}

.btn-save {
  background-color: #2ecc71;
  color: white;
}

.btn-cancel {
  background-color: #95a5a6;
  color: white;
}

.btn-delete {
  background-color: #e74c3c;
  color: white;
}

.sensor-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.sensor-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.sensor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.sensor-id {
  color: #7f8c8d;
  font-size: 12px;
}

.sensor-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  margin-bottom: 12px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: bold;
  color: #2c3e50;
}

.form-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-control:disabled {
  background-color: #f5f5f5;
  color: #777;
}

.sensor-actions {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 8px;
}

.add-sensor-form {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.add-sensor-form .form-group {
  margin-bottom: 16px;
}

.add-sensor-form .form-control {
  width: 100%;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}
</style>