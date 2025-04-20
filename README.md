# MCServerRadar (我的世界服务器雷达)

一个强大的 Minecraft 服务器扫描、监控和可视化工具。

<div align="center">
    <img src="docs/images/logo.svg" alt="MCServerRadar Logo" width="200"/>
    <p>
        中文 | <a href="README_EN.md">English</a>
    </p>
    <p>
        <img src="https://img.shields.io/github/license/MoTeam-org/MCServerRadar" alt="License"/>
        <img src="https://img.shields.io/github/stars/MoTeam-org/MCServerRadar" alt="Stars"/>
        <img src="https://img.shields.io/github/forks/MoTeam-org/MCServerRadar" alt="Forks"/>
        <img src="https://img.shields.io/github/issues/MoTeam-org/MCServerRadar" alt="Issues"/>
    </p>
    <p>
        🌍 在线演示：<a href="https://mc-scan.pages.dev" target="_blank">https://mc-scan.pages.dev</a> (目前待启动)
    </p>
</div>

## 📖 项目介绍

MCServerRadar 是一个专门为 Minecraft 服务器设计的扫描和监控工具。它能够：

- 自动发现和扫描全球范围内的 Minecraft 服务器
- 实时监控服务器状态和玩家数量
- 提供美观的 Web 界面展示服务器信息
- 支持按国家/地区筛选服务器
- 提供服务器地理位置分布可视化

## ✨ 功能特点

- 🔍 全球范围的 Minecraft 服务器扫描
- 🌍 基于 GeoIP 的服务器地理位置识别
- 📊 美观的 Web 界面展示
- 📈 实时服务器状态监控
- 🗺 按国家/地区分类展示
- 📱 响应式设计，支持移动端访问
- 🚀 高性能异步扫描
- 🔒 注重隐私（排除私有IP范围）
- 📝 详细的服务器信息
- 🌐 多语言支持

## 🌟 在线演示

访问我们的演示站点：[https://mc-scan.pages.dev](https://mc-scan.pages.dev) (目前待启动)

在演示站点，你可以：
- 查看全球 Minecraft 服务器分布
- 实时监控服务器状态
- 按国家/地区筛选服务器
- 体验所有核心功能

## 🚀 快速开始

### 环境要求

- Python 3.8+
- GeoLite2 国家数据库
- 网络连接

### 安装步骤

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

### 使用方法

1. 扫描服务器：
```bash
# 扫描特定国家的服务器
python scan.py --country china

# 随机全球扫描
python scan.py --mode random

# 扫描特定IP范围
python scan.py --mode range --start-ip 1.1.1.1 --end-ip 1.1.1.255

# 扫描指定服务器列表
## 方法1：使用文本文件（每行一个服务器地址）
echo "mc.hypixel.net
2b2t.org
play.pixelmonrealms.com" > servers.txt
python scan.py --mode multiple --hosts-file servers.txt

## 方法2：直接在代码中使用
from mc_scanner import MinecraftServerScanner
import asyncio

async def main():
    servers_to_scan = [
        "mc.hypixel.net",
        "2b2t.org",
        "play.pixelmonrealms.com"
    ]
    scanner = MinecraftServerScanner()
    await scanner.scan_multiple_servers(servers_to_scan)
    scanner.save_results()

if __name__ == "__main__":
    asyncio.run(main())

2. 启动 Web 界面：
```bash
python web.py
```

3. 访问仪表盘：
- 打开浏览器访问 `http://localhost:5000`

## 📊 功能详情

### 扫描模式

- **国家扫描**：扫描特定国家的服务器
- **随机全球**：随机采样全球IP
- **IP范围**：扫描特定IP范围
- **单主机**：扫描单个主机的所有端口
- **多服务器**：扫描已知服务器列表
- **完整IPv4**：扫描整个IPv4空间（谨慎使用）

### 服务器信息

- 服务器版本
- 在线/最大玩家数
- 服务器公告（MOTD）
- 延迟
- 在线玩家列表（如果可用）
- 地理位置
- 最后更新时间

### Web界面

- 实时统计数据
- 按国家分组
- 服务器状态指示
- 响应式设计
- 搜索和筛选功能
- 交互式地图（即将推出）

## 🛠 技术栈

- **后端**
  - Python 3.x
  - Flask (Web框架)
  - MCStatus (服务器查询)
  - GeoIP2 (位置检测)
  - Async IO (高性能扫描)

- **前端**
  - Bootstrap 5
  - Flag Icons
  - 自定义CSS动画
  - 响应式设计

## 💡 最佳实践

### 扫描建议

1. **合理使用**
   - 建议先使用小范围扫描测试
   - 避免频繁扫描同一IP段
   - 遵守目标服务器的使用政策

2. **性能优化**
   - 适当调整批处理大小
   - 根据网络状况调整超时设置
   - 使用国家扫描模式提高效率

3. **数据处理**
   - 定期清理过期数据
   - 备份重要的扫描结果
   - 适当设置保存间隔

### 部署建议

1. **系统要求**
   - 推荐使用 Linux 系统
   - 确保足够的网络带宽
   - 建议使用 SSD 存储

2. **网络配置**
   - 配置合适的防火墙规则
   - 使用代理服务器分散请求
   - 避免触发 IP 封禁

3. **监控维护**
   - 设置日志记录
   - 监控系统资源使用
   - 定期检查更新

## 🤝 贡献指南

我们欢迎各种形式的贡献！以下是参与方式：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m '添加一些很棒的特性'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 📝 许可证

本项目采用 Apache License 2.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [MCStatus](https://github.com/Dinnerbone/mcstatus) - Minecraft服务器查询库
- [MaxMind](https://www.maxmind.com) - GeoIP2数据库
- [Bootstrap](https://getbootstrap.com) - 前端框架
- 所有帮助这个项目成长的贡献者

## 📞 联系方式

- GitHub Issues: [创建issue](https://github.com/MoTeam-org/MCServerRadar/issues)
- 邮箱: [moteam.org@gmail.com]

## 🔮 开发路线

- [ ] 添加服务器历史记录追踪
- [ ] 实现实时更新
- [ ] 添加交互式世界地图
- [ ] 支持基岩版服务器
- [ ] 添加更多扫描模式
- [ ] 提升扫描性能
- [ ] 添加API文档
- [ ] 添加Docker支持

## ❓ 常见问题

1. **为什么扫描速度较慢？**
   - 检查网络连接状况
   - 调整并发连接数
   - 考虑使用代理服务器

2. **如何提高扫描准确率？**
   - 适当增加超时时间
   - 多次扫描验证结果
   - 使用可靠的IP数据源

3. **如何处理扫描错误？**
   - 查看详细错误日志
   - 检查网络连接
   - 验证目标服务器状态

## 📚 相关资源

- [Minecraft 官网](https://www.minecraft.net/)
- [MCStatus 文档](https://github.com/Dinnerbone/mcstatus)
- [GeoIP2 文档](https://dev.maxmind.com/geoip) 