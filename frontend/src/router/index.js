import { createRouter, createWebHashHistory } from 'vue-router'
import RealTimeMonitor from '../components/RealTimeMonitor.vue'
import SensorManager from '../components/SensorManager.vue'

const routes = [
  {
    path: '/',
    name: 'RealTimeMonitor',
    component: RealTimeMonitor
  },
  {
    path: '/manage',
    name: 'SensorManager',
    component: SensorManager
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router