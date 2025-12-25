<template>
  <div id="app">
    <header class="header">
      <h1>MQTT 传感器数据监控面板</h1>
    </header>
    
    <main class="main-content">
      <div class="sensor-cards">
        <div 
          v-for="(sensor, sensorId) in sensorData" 
          :key="sensorId"
          class="card"
        >
          <h3>{{ sensorId }} - 传感器数据</h3>
          
          <div class="data-grid">
            <!-- 传感器1板块 -->
            <div class="data-section sensor1-section">
              <h4>🌡️ 传感器1</h4>
              <p class="value">
                <span :class="{'temp-value': true, 'zero-data': sensor.current_data?.temperature1 === 0 && sensor.current_data?.timestamp && isDataFresh(sensor.current_data?.timestamp)}">
                  温度: {{ sensor.current_data?.temperature1 || 0 }}°C
                </span>
              </p>
              <p class="value">
                <span :class="{'humid-value': true, 'zero-data': sensor.current_data?.humidity1 === 0 && sensor.current_data?.timestamp && isDataFresh(sensor.current_data?.timestamp)}">
                  湿度: {{ sensor.current_data?.humidity1 || 0 }}%
                </span>
              </p>
            </div>
            
            <!-- 传感器2板块 -->
            <div class="data-section sensor2-section">
              <h4>🌡️ 传感器2</h4>
              <p class="value">
                <span :class="{'temp-value': true, 'zero-data': sensor.current_data?.temperature2 === 0 && sensor.current_data?.timestamp && isDataFresh(sensor.current_data?.timestamp)}">
                  温度: {{ sensor.current_data?.temperature2 || 0 }}°C
                </span>
              </p>
              <p class="value">
                <span :class="{'humid-value': true, 'zero-data': sensor.current_data?.humidity2 === 0 && sensor.current_data?.timestamp && isDataFresh(sensor.current_data?.timestamp)}">
                  湿度: {{ sensor.current_data?.humidity2 || 0 }}%
                </span>
              </p>
            </div>
            
            <!-- 继电器和PB8电平板块 -->
            <div class="data-section device-status">
              <h4>⚙️ 设备状态</h4>
              <div class="status-row">
                <p>继电器: 
                  <span :class="sensor.current_data?.relay_status ? 'status-on' : (sensor.current_data?.relay_status === 0 && sensor.current_data?.timestamp && isDataFresh(sensor.current_data?.timestamp) ? 'status-off-zero' : 'status-off')">
                    {{ sensor.current_data?.relay_status ? '开启' : '关闭' }}
                  </span>
                </p>
              </div>
              <div class="status-row">
                <p>PB8: 
                  <span :class="sensor.current_data?.pb8_level ? 'status-on' : (sensor.current_data?.pb8_level === 0 && sensor.current_data?.timestamp && isDataFresh(sensor.current_data?.timestamp) ? 'status-off-zero' : 'status-off')">
                    {{ sensor.current_data?.pb8_level ? '高' : '低' }}
                  </span>
                </p>
              </div>
            </div>
          </div>
          
          <p class="update-time">最后更新: {{ sensor.current_data?.timestamp ? new Date(sensor.current_data.timestamp).toLocaleString() : '等待数据...' }}</p>
        </div>
      </div>
      
      <div class="last-update">
        <p>最后更新: {{ lastUpdateTime ? new Date(lastUpdateTime).toLocaleString() : '等待数据...' }}</p>
      </div>
      
      <!-- 报警信息显示 -->
      <div v-if="!isDeviceOnline" class="alert-banner">
        <div class="alert-content">
          <span class="alert-icon">⚠️</span>
          <span class="alert-text">传感器离线或故障，请检查设备</span>
          <span class="alert-time">数据已过期 {{ offlineDuration }} 秒</span>
        </div>
      </div>
      
      <div class="chart-container">
        <h3>传感器数据图表</h3>
        <div ref="chartRef" class="chart"></div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

// API base URL - 使用正确的后端端口
const API_BASE = 'http://localhost:5002/api'

/**
 * 获取传感器数据
 * @returns {Promise<Object>} 传感器数据
 */
async function fetchSensorData() {
  try {
    const response = await fetch(`${API_BASE}/devices`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    return data
  } catch (error) {
    console.error('获取传感器数据失败:', error)
    throw error
  }
}

export default {
  name: 'App',
  setup() {
    const sensorData = ref({})
    const chartRef = ref(null)
    let chartInstance = null
    let updateInterval = null
    const isDeviceOnline = ref(true)
    const lastUpdateTime = ref(Date.now())
    const offlineDuration = ref(0)
    let offlineTimer = null
    
    // 数据历史记录，用于时间轴图表
    const dataHistory = ref({
      time: [],
      temperature1: [],
      humidity1: [],
      temperature2: [],
      humidity2: []
    })
    
    // 检查数据是否新鲜（在30秒内）
    const isDataFresh = (timestamp) => {
      if (!timestamp) return false;
      const dataTimestamp = new Date(timestamp).getTime();
      const now = Date.now();
      const timeDiff = now - dataTimestamp;
      return timeDiff < 30000;
    }
    
    // 添加数据到历史记录
    const addDataToHistory = (data) => {
      const now = new Date()
      // 格式化时间为小时:分钟:秒格式，例如 "14:30:25"
      const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
      
      // 添加时间点
      dataHistory.value.time.push(timeStr)
      
      // 从所有传感器中取第一个传感器的数据用于图表（或聚合数据）
      const sensorIds = Object.keys(data)
      if (sensorIds.length > 0) {
        const firstSensorId = sensorIds[0]
        const firstSensor = data[firstSensorId]
        // 添加数据点
        dataHistory.value.temperature1.push(firstSensor.current_data?.temperature1 || 0)
        dataHistory.value.humidity1.push(firstSensor.current_data?.humidity1 || 0)
        dataHistory.value.temperature2.push(firstSensor.current_data?.temperature2 || 0)
        dataHistory.value.humidity2.push(firstSensor.current_data?.humidity2 || 0)
      } else {
        // 如果没有传感器数据，添加0值
        dataHistory.value.temperature1.push(0)
        dataHistory.value.humidity1.push(0)
        dataHistory.value.temperature2.push(0)
        dataHistory.value.humidity2.push(0)
      }
      
      // 限制历史数据点数量，避免过多数据影响性能
      if (dataHistory.value.time.length > 60) {
        dataHistory.value.time.shift()
        dataHistory.value.temperature1.shift()
        dataHistory.value.humidity1.shift()
        dataHistory.value.temperature2.shift()
        dataHistory.value.humidity2.shift()
      }
    }
    
    // 检查设备是否在线
    const checkDeviceStatus = () => {
      // 检查是否有任何传感器数据
      const sensorIds = Object.keys(sensorData.value);
      if (sensorIds.length === 0) {
        // 如果没有传感器数据，认为设备离线
        isDeviceOnline.value = false;
        offlineDuration.value = Math.floor((Date.now() - lastUpdateTime.value) / 1000);
        return;
      }
      
      // 检查所有传感器中是否有新鲜数据
      let hasFreshData = false;
      for (const sensorId of sensorIds) {
        const sensor = sensorData.value[sensorId];
        const timestamp = sensor.current_data?.timestamp;
        if (timestamp) {
          const dataTimestamp = new Date(timestamp).getTime();
          const now = Date.now();
          const timeDiff = now - dataTimestamp;
          if (timeDiff < 30000) {
            hasFreshData = true;
            break;
          }
        }
      }
      
      isDeviceOnline.value = hasFreshData;
      
      // 计算离线时间（使用最新的时间戳）
      let latestTimestamp = 0;
      for (const sensorId of sensorIds) {
        const sensor = sensorData.value[sensorId];
        const timestamp = sensor.current_data?.timestamp;
        if (timestamp) {
          const ts = new Date(timestamp).getTime();
          if (ts > latestTimestamp) {
            latestTimestamp = ts;
          }
        }
      }
      
      if (latestTimestamp > 0) {
        offlineDuration.value = Math.floor((Date.now() - latestTimestamp) / 1000);
      } else {
        offlineDuration.value = Math.floor((Date.now() - lastUpdateTime.value) / 1000);
      }
    }
    
    // 获取传感器数据
    const fetchSensorData = async () => {
      try {
        const response = await fetch(`${API_BASE}/devices`)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const jsonData = await response.json()
        sensorData.value = jsonData
        // 更新最后更新时间
        lastUpdateTime.value = Date.now()
        addDataToHistory(jsonData)
        updateChart()
      } catch (error) {
        console.error('获取传感器数据失败:', error)
      }
    }
    
    // 初始化图表
    const initChart = () => {
      if (chartRef.value) {
        chartInstance = echarts.init(chartRef.value)
        
        const option = {
          tooltip: {
            trigger: 'axis'
          },
          legend: {
            data: ['温度1', '湿度1', '温度2', '湿度2']
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            containLabel: true
          },
          toolbox: {
            feature: {
              saveAsImage: {}
            }
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: dataHistory.value.time,
            // 配置x轴标签的显示格式，以更好地展示小时级时间
            axisLabel: {
              interval: 5, // 每隔5个标签显示一个，避免标签过于密集
              rotate: 45  // 标签旋转45度，节省空间
            }
          },
          yAxis: [
            {
              type: 'value',
              name: '温度 (°C)',
              position: 'left',
              min: 0,
              max: 50,
              axisLine: {
                lineStyle: {
                  color: '#91cc75'
                }
              }
            },
            {
              type: 'value',
              name: '湿度 (%)',
              position: 'right',
              min: 0,
              max: 100,
              axisLine: {
                lineStyle: {
                  color: '#73c0de'
                }
              }
            }
          ],
          series: [
            {
              name: '温度1',
              type: 'line',
              yAxisIndex: 0,
              data: dataHistory.value.temperature1,
              itemStyle: { color: '#91cc75' },
              smooth: true
            },
            {
              name: '湿度1',
              type: 'line',
              yAxisIndex: 1,
              data: dataHistory.value.humidity1,
              itemStyle: { color: '#73c0de' },
              smooth: true
            },
            {
              name: '温度2',
              type: 'line',
              yAxisIndex: 0,
              data: dataHistory.value.temperature2,
              itemStyle: { color: '#fac858' },
              smooth: true
            },
            {
              name: '湿度2',
              type: 'line',
              yAxisIndex: 1,
              data: dataHistory.value.humidity2,
              itemStyle: { color: '#ee6666' },
              smooth: true
            }
          ]
        }
        
        chartInstance.setOption(option)
      }
    }
    
    // 更新图表数据
    const updateChart = () => {
      if (chartInstance) {
        chartInstance.setOption({
          xAxis: {
            data: dataHistory.value.time
          },
          series: [
            {
              name: '温度1',
              data: dataHistory.value.temperature1
            },
            {
              name: '湿度1',
              data: dataHistory.value.humidity1
            },
            {
              name: '温度2',
              data: dataHistory.value.temperature2
            },
            {
              name: '湿度2',
              data: dataHistory.value.humidity2
            }
          ]
        })
      }
    }
    
    onMounted(() => {
      // 初始获取数据
      fetchSensorData()
      
      // 设置定时更新 - 每2秒更新一次
      updateInterval = setInterval(fetchSensorData, 2000)
      
      // 每秒检查一次设备状态
      offlineTimer = setInterval(checkDeviceStatus, 1000)
      
      // 初始化图表
      initChart()
    })
    
    onUnmounted(() => {
      if (updateInterval) {
        clearInterval(updateInterval)
      }
      if (offlineTimer) {
        clearInterval(offlineTimer)
      }
      if (chartInstance) {
        chartInstance.dispose()
      }
    })
    
    return {
      sensorData,
      chartRef,
      isDeviceOnline,
      offlineDuration,
      lastUpdateTime,
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

.sensor-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card h3 {
  margin-top: 0;
  color: #34495e;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.8rem;
  margin: 1rem 0;
}

.data-section {
  margin: 0;
  padding: 0.8rem;
  background-color: #f9f9f9;
  border-radius: 6px;
  border-left: 4px solid #3498db;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sensor1-section {
  border-left: 4px solid #91cc75;
}

.sensor2-section {
  border-left: 4px solid #fac858;
}

.data-section h4 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.temp-value, .humid-value {
  font-weight: bold;
  font-size: 1.1rem;
  color: #3498db;
  display: block;
  margin: 0.3rem 0;
}

/* 为零的数据值使用红色字体 */
.temp-value.zero-data, .humid-value.zero-data {
  color: #e74c3c;
}

.status-on {
  color: #2ecc71;
  font-weight: bold;
  font-size: 1.1rem;
}

.status-off {
  color: #e74c3c;
  font-weight: bold;
  font-size: 1.1rem;
}

/* 为零的设备状态使用红色字体 */
.status-off-zero {
  color: #e74c3c;
  font-weight: bold;
  font-size: 1.1rem;
}

.device-status {
  border-left: 4px solid #9b59b6;
}

.status-row {
  margin: 0.5rem 0;
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.update-time {
  font-style: italic;
  color: #7f8c8d;
  margin: 0;
  padding-top: 0.5rem;
  border-top: 1px solid #eee;
}

.last-update {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* 新增的报警横幅样式 */
.alert-banner {
  background-color: #e74c3c;
  color: white;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  animation: alert-pulse 2s infinite;
}

@keyframes alert-pulse {
  0% { background-color: #e74c3c; }
  50% { background-color: #c0392b; }
  100% { background-color: #e74c3c; }
}

.alert-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-icon {
  font-size: 1.5rem;
}

.alert-text {
  font-weight: bold;
  font-size: 1.2rem;
}

.alert-time {
  font-style: italic;
}

.chart-container {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.chart {
  height: 400px;
  margin-top: 1rem;
}
</style>