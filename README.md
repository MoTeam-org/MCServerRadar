# MCServerRadar (我的世界服务器雷达)

一个强大的 Minecraft 服务器扫描、监控和展示工具。

## 功能特点

- 🔍 全球范围的 Minecraft 服务器扫描
- 🌍 基于 GeoIP 的服务器地理位置识别
- 📊 美观的 Web 界面展示
- 📈 实时服务器状态监控
- 🗺 按国家/地区分类展示
- 📱 响应式设计，支持移动端访问

## 安装说明

1. 克隆仓库：
```bash
git clone https://github.com/MoTeam-org/MCServerRadar.git
cd MCServerRadar
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 下载 GeoLite2 数据库：
- 从 [MaxMind](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) 下载 GeoLite2-Country.mmdb
- 将文件放在项目根目录

## 使用方法

1. 扫描服务器：
```bash
python scan.py --country china  # 扫描特定国家
python scan.py --mode random   # 随机扫描
```

2. 启动 Web 界面：
```bash
python web.py
```

3. 访问 Web 界面：
- 打开浏览器访问 `http://localhost:5000`

## 技术栈

- Python 3.x
- Flask (Web 框架)
- Bootstrap 5 (前端框架)
- GeoIP2 (IP 地理位置识别)
- MCStatus (Minecraft 服务器状态查询)

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License 