# AutoJS 控制台

AutoJS 控制台是一个用于管理和控制Android设备上AutoJS脚本的桌面应用程序。它提供了设备管理、脚本管理、屏幕镜像等功能，让您可以方便地在PC上管理和执行AutoJS脚本。

## 功能特性

### 设备管理
- **自动检测设备**: 自动检测并显示已连接的Android设备
- **多设备支持**: 支持同时连接多个设备，可随时切换控制设备
- **设备信息显示**: 
  - 显示设备型号
  - 显示设备ID
  - 显示Android系统版本
- **自动安装**: 首次连接设备时自动安装AutoJS应用

### 脚本管理
- **脚本库管理**:
  - 添加本地JavaScript脚本到脚本库
  - 删除已添加的脚本
  - 查看脚本基本信息
- **脚本执行**:
  - 一键运行脚本到选中设备
  - 实时显示脚本执行状态(运行中/成功/失败)
  - 查看详细执行日志
- **日志系统**:
  - 记录每次脚本执行的状态
  - 保存执行日志到数据库
  - 支持查看历史执行记录

### 屏幕镜像
- **实时显示**:
  - 高性能实时显示设备屏幕
  - 自适应窗口大小
  - 保持设备原始宽高比
- **导航控制**:
  - HOME键：返回主屏幕
  - BACK键：返回上一页
  - RECENT键：显示最近任务
- **镜像优化**:
  - 支持高帧率显示
  - 低延迟传输
  - 自动调整分辨率以获得最佳显示效果

### 其他特性
- **界面美观**: 现代化界面设计，操作直观
- **稳定可靠**: 可靠的设备连接和脚本执行机制
- **数据持久化**: 使用SQLite数据库保存脚本和日志信息
- **即插即用**: 支持设备热插拔，随时连接使用

## 系统要求

### 基本要求
- Windows 10/11 操作系统 (64位)
- Python 3.8 或更高版本
- USB 2.0/3.0 接口
- 至少 4GB 内存
- 500MB 可用磁盘空间

### Android设备要求
- Android 5.0 或更高版本
- 已启用USB调试
- 已安装或允许安装AutoJS应用
- USB数据线正常工作

### 必需的第三方软件
- ADB (Android Debug Bridge)
- Scrcpy (用于屏幕镜像)

## 安装说明

### 1. 安装必需的软件

#### 安装 Python
1. 从 [Python官网](https://www.python.org/downloads/) 下载并安装Python 3.8+
2. 安装时勾选"Add Python to PATH"
3. 验证安装: `python --version`

#### 安装 Scrcpy
- Windows (使用scoop):
```bash
scoop install scrcpy
```
- 或从 [Scrcpy Releases](https://github.com/Genymobile/scrcpy/releases) 下载

#### 安装 ADB
- Windows (使用scoop):
```bash
scoop install adb
```
- 或从 [Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools) 下载

### 2. 安装程序依赖

```bash
# 克隆仓库
git clone https://github.com/your-username/autox-console.git
cd autox-console

# 创建虚拟环境(推荐)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置Android设备

1. 启用开发者选项:
   - 设置 -> 关于手机 -> 版本号(点击7次)
2. 启用USB调试:
   - 设置 -> 开发者选项 -> USB调试
3. 连接设备到电脑:
   - 使用USB数据线连接
   - 在设备上允许USB调试授权

## 运行程序

```bash
# 激活虚拟环境(如果使用)
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 运行程序
python main.py
```

## 使用指南

### 首次使用
1. 启动程序后会自动检测已连接的设备
2. 首次连接设备时会自动安装AutoJS
3. 需要在设备上确认安装并授权AutoJS

### 添加脚本
1. 点击"添加脚本"按钮
2. 输入脚本名称
3. 选择本地的.js文件
4. 确认添加

### 执行脚本
1. 在设备列表中选择目标设备
2. 在脚本列表中找到要执行的脚本
3. 点击"运行"按钮
4. 通过日志按钮查看执行状态

### 屏幕镜像
1. 选择设备后自动开启屏幕镜像
2. 使用右侧按钮进行导航控制
3. 窗口大小可自适应调整

## 常见问题

### 设备连接问题
- 确保USB调试已启用
- 检查USB数据线是否正常
- 重新插拔USB连接
- 检查设备是否信任当前电脑

### 脚本执行问题
- 确保AutoJS已正确安装并授权
- 检查脚本语法是否正确
- 查看执行日志了解详细错误信息

### 屏幕镜像问题
- 确保Scrcpy已正确安装
- 尝试重新连接设备
- 检查设备分辨率设置

## 目录结构

```
autox-console/
├── main.py              # 程序入口
├── requirements.txt     # 依赖项
├── README.md           # 说明文档
├── src/                # 源代码
│   ├── ui/            # 用户界面
│   │   ├── main_window.py
│   │   ├── device_list.py
│   │   ├── script_list.py
│   │   └── screen_view.py
│   ├── core/          # 核心功能
│   │   ├── device_manager.py
│   │   ├── script_manager.py
│   │   ├── autojs_manager.py
│   │   └── scrcpy_manager.py
│   └── database/      # 数据库
│       └── db_manager.py
└── resources/         # 资源文件
    └── autojs.apk     # AutoJS安装包
```

## 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## 贡献指南

欢迎提交Issue和Pull Request。在提交PR之前，请确保：
1. 代码符合Python代码规范
2. 添加了必要的注释和文档
3. 所有测试通过

## 更新日志

### v1.0.0 (2024-03-xx)
- 初始版本发布
- 实现基本功能：设备管理、脚本管理、屏幕镜像
