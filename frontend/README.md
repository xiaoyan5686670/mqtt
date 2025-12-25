# MQTT Vue Frontend

基于 Vue3 的 MQTT 传感器数据监控前端界面

## 项目介绍

这是一个使用 Vue3 开发的前端应用，用于实时展示从 MQTT 接收的传感器数据。该应用包括：

- 传感器数据显示卡片
- 实时更新的图表
- 设备状态监控

## 技术栈

- Vue 3
- Vue Router
- Axios
- ECharts
- Vite

## 安装和运行

### 前提条件

- Node.js >= 14.0
- 后端服务 (Flask) 运行在 http://localhost:5000

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:3000 上运行，Vite 会自动代理 `/api` 请求到后端服务。

### 构建生产版本

```bash
npm run build
```

## 项目结构

```
src/
├── App.vue          # 主应用组件
├── main.js          # 应用入口文件
```

## 功能说明

- 自动每2秒从后端获取最新传感器数据
- 实时图表展示温度和湿度数据
- 直观显示设备状态（继电器、PB8电平）
- 响应式布局，适配不同屏幕尺寸

## 后端集成

前端通过 `/api/sensor-data` 接口获取传感器数据，该接口由配套的 Flask 后端提供。