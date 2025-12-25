# MQTT Python Client for EMQ X

这是一个使用 Python 连接到 EMQ X Broker 的示例项目，基于 Eclipse Paho MQTT 官方文档中的示例。

## 项目说明

本项目演示如何使用 [Paho MQTT](https://pypi.org/project/paho-mqtt/) 库连接到 EMQ X Broker，并进行消息的发布和订阅。

## 功能特性

- 支持标准 MQTT 连接
- 支持 TLS/SSL 加密连接
- 支持 Will 消息（遗嘱消息）
- 提供多种运行模式（标准、回调API、异步API）
- 包含详细的错误处理和调试信息

## 安装依赖

```bash
pip install paho-mqtt
```

## 使用方法

1. 确保已安装 EMQ X Broker 并启动服务
2. 复制 `config_example.py` 为 `config.py`，并修改连接参数
3. 运行客户端程序

```bash
python main.py
```

运行时会提示选择模式：
- 1. 标准模式（默认）
- 2. 回调API模式
- 3. 异步API模式

## 配置

在 `config.py` 文件中可以配置连接参数，如服务器地址、端口、用户名和密码等。

### 基本配置项
- `server`: MQTT 服务器地址
- `port`: 端口号（非加密连接通常为1883，TLS连接为8883）
- `username`: 用户名
- `password`: 密码
- `client_id`: 客户端ID（可选，留空则自动生成）
- `keepalive`: 心跳间隔（秒）

### 高级配置项
- `use_tls`: 是否使用TLS加密连接
- `ca_certs`, `certfile`, `keyfile`: TLS证书配置
- `will_topic`, `will_payload`, `will_qos`: Will消息配置

## MQTT连接错误代码说明

- 0: 连接成功
- 1: 连接被拒绝 - 不正确的协议版本
- 2: 连接被拒绝 - 无效的客户端标识符
- 3: 连接被拒绝 - 服务器不可用
- 4: 连接被拒绝 - 用户名或密码错误
- 5: 连接被拒绝 - 未授权

## Vue3 前端监控面板

项目还包括一个基于 Vue3 的前端监控面板，用于实时展示从 MQTT 接收的传感器数据。

### 后端服务

首先启动后端 Flask 服务：

```bash
pip install flask
python backend.py
```

### MQTT 数据桥接

使用 `mqtt_bridge.py` 连接到 MQTT 代理并解析传感器数据：

```bash
python mqtt_bridge.py
```

### 前端界面

进入前端目录并启动：

```bash
cd frontend
npm install
npm run dev
```

前端应用将在 http://localhost:3000 上运行，自动从后端获取数据并展示。

## 故障排除

如果遇到"连接超时"错误，请检查以下几点：

1. **服务器地址和端口**：
   - 确认 EMQX 服务器正在运行
   - 确认服务器 IP 地址是否正确
   - 确认端口是否正确（1883 用于普通连接，8883 用于 SSL 连接）

2. **网络连接**：
   - 使用 `ping` 命令测试与服务器的连通性
   - 检查防火墙设置是否阻止了连接
   - 确认网络连接是否正常

3. **认证信息**：
   - 检查用户名和密码是否正确
   - 确认用户是否有连接权限

4. **EMQX 配置**：
   - 检查 EMQX 是否允许客户端连接
   - 查看 EMQX 日志以获取更多信息

## 许可证

MIT# mqtt
# mqtt
# mqtt
