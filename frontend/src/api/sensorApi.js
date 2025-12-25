import axios from 'axios'

// API base URL
const API_BASE = 'http://localhost:5003/api'

/**
 * 获取传感器数据
 * @returns {Promise<Object>} 传感器数据
 */
export const fetchSensorData = async () => {
  try {
    const response = await axios.get('/api/sensor-data')
    return response.data
  } catch (error) {
    console.error('获取传感器数据失败:', error)
    throw error
  }
}

/**
 * 测试API连接
 * @returns {Promise<Object>} 健康检查结果
 */
export const testApiConnection = async () => {
  try {
    const response = await axios.get('/api/health')
    return response.data
  } catch (error) {
    console.error('API连接测试失败:', error)
    throw error
  }
}