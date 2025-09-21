# AUV - Automatic file organization Utilities �

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

A powerful command-line file organization tool that automatically categorizes and organizes various file types with flexible path configuration and intelligent sorting modes.

[中文文档](README_zh.md) | [English](README.md)

## ✨ Features

- 🗂️ **Smart File Organization**: Automatically sort files by type with customizable rules
- 🎯 **Custom Commands**: Create personalized file sorting commands (e.g., `-py` for Python files)
- 📜 **Operation History**: Track all operations with timeline-based rollback functionality  
- 🔧 **Flexible Configuration**: Enable/disable file types and customize target paths
- 🏃 **Daemon Mode**: Background monitoring for automatic file organization
- 🌍 **Cross-Platform**: Supports Windows, macOS, and Linux
- 🔒 **Safe Operations**: Automatic backup and rollback capabilities

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install watchdog psutil click

# Install AUV
pip install --user -e .

# Verify installation
auv --help
```

### Basic Usage

```bash
# Organize files in current directory
auv -pdf                    # Organize PDF files
auv -img                    # Organize image files  
auv -py                     # Organize Python files (custom command)

# Organize with custom path
auv -pdf here               # Create PDF folder in current directory
auv -pdf ./Documents        # Move PDFs to Documents folder

# View configuration and history
auv status                  # Show current configuration
auv history                 # View operation history
auv return                  # Rollback last operation
```

## 📚 Core Commands

### File Organization
```bash
auv -pdf                    # Organize PDF files
auv -img                    # Organize images
auv -doc                    # Organize documents
auv -video                  # Organize videos
auv -audio                  # Organize audio files
```

### Configuration Management
```bash
auv set enable archive     # Enable archive file support
auv set path pdf ~/PDFs     # Set default PDF target path
auv set custom add py .py .pyw --path ~/Python  # Create custom command
```

### History & Rollback
```bash
auv history                 # View operation history
auv history --limit 10      # Show last 10 operations
auv return                  # Rollback last operation
auv return T15              # Rollback to timeline T15
```

### Daemon Mode
```bash
auv agent                   # Start background monitoring
auv agent --stop            # Stop daemon
```

## 🎯 Supported File Types

### Basic Types (Always Available)
- **PDF**: `.pdf`
- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`
- **Documents**: `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`
- **Videos**: `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`
- **Audio**: `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`

### Extended Types (Enable as needed)
- **Installers**: `.exe`, `.msi`, `.dmg`, `.deb`, `.rpm`
- **Archives**: `.zip`, `.rar`, `.7z`, `.tar.gz`, `.iso`
- **Code**: `.py`, `.js`, `.html`, `.css`, `.java`, `.cpp`
- **Fonts**: `.ttf`, `.otf`, `.woff`, `.woff2`
- **eBooks**: `.epub`, `.mobi`, `.azw`

### Custom Types
Create unlimited custom commands for any file extensions.

## 📖 Configuration

Configuration file location:
- **Windows**: `%APPDATA%\auv\config.json`
- **macOS/Linux**: `~/.config/auv/config.json`

Example configuration:
```json
{
    "downloads_path": "/Users/username/Downloads",
    "target_paths": {
        "pdf": "/Users/username/Documents/PDFs",
        "image": "/Users/username/Pictures"
    },
    "custom_commands": {
        "py": {
            "extensions": [".py", ".pyw"],
            "target_path": "/Users/username/Code/Python",
            "enabled": true
        }
    },
    "history": {
        "enabled": true,
        "max_entries": 1000,
        "auto_cleanup_days": 30
    }
}
```

## 🔧 Advanced Usage

### Custom Commands
Create specialized commands for your workflow:

```bash
# Create commands for development
auv set custom add frontend .html .css .js .vue
auv set custom add backend .py .sql .yaml
auv set custom add mobile .java .swift .dart

# Enable and use them
auv set enable frontend backend mobile
auv -frontend              # Organize frontend files
auv -backend               # Organize backend files
```

### Batch Operations
```bash
# Multiple file types at once
auv -pdf -img -doc         # Organize multiple types

# Different working directories
auv -d -pdf                # Organize Downloads folder
auv here -img Pictures     # Create Pictures folder locally
```

### Smart Path Handling
```bash
auv -pdf ./documents       # Relative path
auv -pdf ~/Documents       # Home directory
auv -pdf /absolute/path    # Absolute path
```

## 📜 History System

AUV tracks all operations with a timeline-based system:

```
Operation History
==================================================
✓ T15 | 2025-09-21 14:30:25
   Type: organize_files
   Description: Organized 5 PDF files
   Files moved: 5

✓ T14 | 2025-09-21 14:25:10  
   Type: custom_organize
   Description: Organized Python files
   Files moved: 3
```

- ✓ = Reversible operation
- ✗ = Non-reversible operation

## �️ Development

### Project Structure
```
auv/
├── auv/                    # Main package
│   ├── cli.py             # Command-line interface
│   ├── core_v2.py         # File organization logic
│   ├── config.py          # Configuration management
│   ├── history.py         # History tracking
│   └── daemon.py          # Background monitoring
├── tests/                 # Test files
└── setup.py               # Package configuration
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📋 Requirements

- **Python**: 3.7 or higher
- **Dependencies**: watchdog, psutil, click
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- 🐛 [Report Issues](https://github.com/JoyinJoester/Auv/issues)
- 💡 [Feature Requests](https://github.com/JoyinJoester/Auv/issues)
- 📖 [Chinese Documentation](README_zh.md)

---

**Make file organization simple and efficient!** 🎉

# 基本文件整理
auv                            # 整理当前文件夹的所有启用类型文件
auv -pdf                       # 整理PDF文件到默认位置
auv -img                       # 整理图片文件到默认位置
auv -doc                       # 整理文档文件到默认位置
auv -video                     # 整理视频文件到默认位置
auv -audio                     # 整理音频文件到默认位置

# 扩展文件类型（需要先启用）
auv -installer                 # 整理安装包文件
auv -archive                   # 整理压缩包文件
auv -code                      # 整理代码文件
auv -font                      # 整理字体文件
auv -ebook                     # 整理电子书文件

# 自定义命令（需要先创建和启用）
auv -py                        # 整理Python文件
auv -js                        # 整理JavaScript文件
auv -web                       # 整理Web文件
```

### 高级用法

```bash
# 下载文件夹整理
auv -d -pdf                 # 整理下载文件夹的PDF文件
auv -d -img                 # 整理下载文件夹的图片文件
auv -d                      # 整理下载文件夹的所有文件

# 在当前目录创建子文件夹整理
auv here -pdf               # 在当前目录创建 PDF 文件夹
auv here -pdf MyPDFs        # 在当前目录创建 MyPDFs 文件夹
auv here -img Pictures      # 在当前目录创建 Pictures 文件夹

# 指定目标路径
auv -pdf ./documents        # 整理PDF到相对路径
auv -pdf D:\MyDocs          # 整理PDF到绝对路径 (Windows)
auv -pdf ~/Documents        # 整理PDF到用户目录 (macOS/Linux)
```

### 配置管理

#### 文件类型启用/禁用
```bash
# 启用文件类型
auv set enable pdf             # 启用PDF文件整理
auv set enable installer       # 启用安装包文件整理
auv set enable archive         # 启用压缩包文件整理
auv set enable code            # 启用代码文件整理

# 禁用文件类型  
auv set disable pdf           # 禁用PDF文件整理（不推荐）
auv set disable installer     # 禁用安装包文件整理

# 查看所有文件类型状态
auv status
```

#### 路径设置
```bash
# 设置默认路径
auv set path downloads ~/Downloads      # 设置下载文件夹路径
auv set path pdf ~/Documents/PDFs       # 设置PDF默认目标路径
auv set path image ~/Pictures           # 设置图片默认目标路径
auv set path document ~/Documents       # 设置文档默认目标路径
auv set path video ~/Videos             # 设置视频默认目标路径
auv set path audio ~/Music              # 设置音频默认目标路径

# 设置扩展文件类型路径
auv set path installer ~/Downloads/Installers  # 设置安装包路径
auv set path archive ~/Downloads/Archives      # 设置压缩包路径
auv set path code ~/Documents/Code             # 设置代码文件路径
```

#### 自定义命令管理

自定义命令功能允许您为特定的文件扩展名创建专用的整理命令，例如为 Python 文件创建 `-py` 命令。

```bash
# 添加自定义命令
auv set custom add py .py .pyw                    # 创建Python文件命令
auv set custom add js .js .ts .jsx .tsx           # 创建JavaScript/TypeScript命令
auv set custom add web .html .css .scss           # 创建Web文件命令
auv set custom add config .json .yaml .toml .ini  # 创建配置文件命令

# 为自定义命令指定路径
auv set custom add py .py .pyw --path ~/Documents/Python

# 启用/禁用自定义命令
auv set enable py              # 启用Python文件命令
auv set disable js             # 禁用JavaScript命令

# 设置自定义命令路径
auv set path py ~/Documents/PythonProjects
auv set path js ~/Documents/WebDev

# 列出所有自定义命令
auv set custom list

# 删除自定义命令
auv set custom remove py
```

#### 使用自定义命令
```bash
# 使用自定义命令整理文件
auv -py                        # 整理Python文件到默认位置
auv -js                        # 整理JavaScript文件到默认位置
auv -web                       # 整理Web文件到默认位置

# 指定自定义路径
auv -py ./my_python_project    # 整理Python文件到指定目录
auv -js here                   # 在当前目录创建子文件夹

# 组合使用
auv -py -js -web               # 同时整理多种自定义文件类型
auv -d -py                     # 整理下载文件夹中的Python文件
```

### 📜 操作历史与回退

AUV 会自动记录所有文件操作，支持查看历史和回退操作。

#### 查看操作历史
```bash
auv history                    # 查看最近20条操作记录
auv history --limit 50         # 查看最近50条操作记录
```

历史记录格式示例：
```
操作历史记录
==================================================
✓ T15 | 2025-09-21 14:30:25
   Type: organize_files
   Description: Organized 5 PDF files from Downloads to Documents/PDFs
   Files moved: 5

✓ T14 | 2025-09-21 14:25:10
   Type: custom_organize
   Description: Organized 3 files with extensions ['.py'] from Downloads to Documents/Python
   Files moved: 3

✗ T13 | 2025-09-21 14:20:05
   Type: config_change
   Description: Changed PDF target path
   Config changes: 1
```

图标说明：
- ✓ 可回退的操作
- ✗ 不可回退的操作

#### 操作回退
```bash
auv return                     # 回退到上一个操作
auv return T15                 # 回退到时间线T15
```

回退功能说明：
- 只能回退文件移动操作，配置更改无法自动回退
- 回退会将文件移动回原始位置
- 不能跳过不可回退的操作进行回退
- 回退操作本身不可再次回退

#### 历史记录管理
```bash
# 通过配置管理历史记录
auv set enable history         # 启用历史记录（默认启用）
auv set disable history        # 禁用历史记录
```

配置历史记录设置：
```json
{
    "history": {
        "enabled": true,        // 是否启用历史记录
        "max_entries": 1000,    // 最大记录条数
        "auto_cleanup_days": 30 // 自动清理天数
    }
}
```

### 守护进程模式

```bash
# 启动后台监控（自动整理下载文件夹）
auv agent

# 停止后台监控
auv agent --stop
```

### 实用场景示例

```bash
# 场景1: 清理混乱的下载文件夹
auv -d                      # 整理所有下载的文件

# 场景2: 整理项目文件夹
cd /path/to/project
auv here -pdf Documents     # 在项目中创建Documents文件夹整理PDF
auv here -img Assets        # 在项目中创建Assets文件夹整理图片

# 场景3: 批量整理多种文件类型
auv -pdf -img -doc          # 同时整理PDF、图片和文档

# 场景4: 开发者文件整理
auv -py -js -web            # 整理Python、JavaScript和Web文件
auv -code -config           # 整理代码文件和配置文件

# 场景5: 设置完整的开发环境整理
auv set custom add py .py .pyw --path ~/Documents/Python
auv set custom add js .js .ts .jsx .tsx --path ~/Documents/WebDev
auv set custom add config .json .yaml .toml .ini --path ~/Documents/Configs
auv set enable py js config
auv -py -js -config         # 使用自定义命令整理开发文件

# 场景6: 自动监控新下载的文件
auv agent                   # 启动后台监控，自动整理新文件
```

### 高级配置示例

```bash
# 为特定项目类型创建自定义命令
auv set custom add frontend .html .css .js .scss .vue --path ~/Projects/Frontend
auv set custom add backend .py .sql .yaml .dockerfile --path ~/Projects/Backend
auv set custom add mobile .java .kt .swift .dart --path ~/Projects/Mobile

# 启用所有项目类型
auv set enable frontend backend mobile

# 按项目类型整理文件
auv -frontend               # 整理前端开发文件
auv -backend                # 整理后端开发文件
auv -mobile                 # 整理移动开发文件
```

## 🎯 支持的文件类型

### 基本文件类型（默认启用）
- **PDF**: `.pdf`
- **图片**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`
- **文档**: `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`
- **视频**: `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`, `.flv`
- **音频**: `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`

### 扩展文件类型（默认禁用，可启用）
- **安装包**: `.exe`, `.msi`, `.dmg`, `.deb`, `.rpm`, `.snap`, `.appimage`
- **压缩包**: `.zip`, `.rar`, `.7z`, `.tar.gz`, `.iso`, `.img`
- **代码文件**: `.py`, `.js`, `.html`, `.css`, `.java`, `.cpp`, `.json`, `.xml`
- **字体文件**: `.ttf`, `.otf`, `.woff`, `.woff2`
- **电子书**: `.epub`, `.mobi`, `.azw`, `.pdf`

### 自定义文件类型
通过自定义命令功能，您可以为任何文件扩展名创建专用的整理命令。

## 🛠️ 功能特性

- ✅ **多种整理模式**：当前文件夹、下载文件夹、自定义路径
- ✅ **灵活路径配置**：支持相对路径、绝对路径、here参数
- ✅ **智能文件分类**：根据扩展名自动识别文件类型
- ✅ **可配置文件类型**：所有文件类型均可启用/禁用
- ✅ **自定义命令**：为特定扩展名创建专用整理命令
- ✅ **扩展文件类型**：支持安装包、压缩包、代码文件等
- ✅ **安全移动**：自动创建目标目录，避免文件覆盖
- ✅ **操作历史**：记录所有操作，支持时间线回退
- ✅ **中文界面**：完整的中文用户界面
- ✅ **守护进程**：后台自动监控和整理
- ✅ **跨平台**：支持 Windows、macOS、Linux

## 📝 配置文件

配置文件位置：
- Windows: `%APPDATA%\auv\config.json`
- macOS/Linux: `~/.config/auv/config.json`

示例配置：
```json
{
    "downloads_path": "C:\\Users\\Username\\Downloads",
    "target_paths": {
        "pdf": "C:\\Users\\Username\\Documents\\PDFs",
        "image": "C:\\Users\\Username\\Pictures",
        "document": "C:\\Users\\Username\\Documents",
        "video": "C:\\Users\\Username\\Videos",
        "audio": "C:\\Users\\Username\\Music",
        "installer": "C:\\Users\\Username\\Downloads\\Installers",
        "archive": "C:\\Users\\Username\\Downloads\\Archives",
        "code": "C:\\Users\\Username\\Documents\\Code"
    },
    "file_types": {
        "pdf": true,
        "image": true,
        "document": true,
        "video": true,
        "audio": true,
        "installer": false,
        "archive": false,
        "code": false,
        "font": false,
        "ebook": false
    },
    "custom_commands": {
        "py": {
            "extensions": [".py", ".pyw"],
            "target_path": "C:\\Users\\Username\\Documents\\Python",
            "enabled": true
        },
        "js": {
            "extensions": [".js", ".ts", ".jsx", ".tsx"],
            "target_path": "C:\\Users\\Username\\Documents\\WebDev",
            "enabled": true
        },
        "config": {
            "extensions": [".json", ".yaml", ".toml", ".ini"],
            "target_path": "C:\\Users\\Username\\Documents\\Configs",
            "enabled": false
        }
    },
    "history": {
        "enabled": true,
        "max_entries": 1000,
        "auto_cleanup_days": 30
    }
}
```

### 自定义命令配置说明

在配置文件中，您可以手动添加自定义命令：

```json
"custom_commands": {
    "命令名": {
        "extensions": ["扩展名列表"],
        "target_path": "目标路径",
        "enabled": true/false
    }
}
```

**配置示例**：
- `py`: 处理 Python 文件（.py, .pyw）
- `js`: 处理 JavaScript/TypeScript 文件（.js, .ts, .jsx, .tsx）
- `web`: 处理 Web 文件（.html, .css, .scss, .sass）
- `config`: 处理配置文件（.json, .yaml, .toml, .ini）
- `data`: 处理数据文件（.csv, .xlsx, .sql, .db）

## 🔧 开发

### 项目结构
```
auv/
├── auv/                    # 主包目录
│   ├── __init__.py
│   ├── cli.py             # 命令行界面
│   ├── core_v2.py         # 核心整理逻辑
│   ├── config.py          # 配置管理
│   ├── daemon.py          # 守护进程
│   └── i18n.py            # 国际化
├── tests/                 # 测试文件
├── locales/               # 语言文件
├── setup.py               # 打包配置
└── requirements.txt       # 依赖列表
```

### 依赖要求
- **Python**: 3.7+ (推荐 3.8+)
- **watchdog**: >= 2.1.0 (文件监控)
- **psutil**: >= 5.8.0 (进程管理)  
- **click**: >= 8.0.0 (命令行界面)

### 安装方式对比

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **本地安装** | 直接使用 `auv` 命令，无需激活环境 | 可能与其他项目依赖冲突 | **推荐用户使用** |
| 虚拟环境 | 依赖隔离，无冲突 | 每次需激活环境 | 开发测试使用 |

### 故障排除

#### 1. 命令找不到 (`auv: command not found`)

**Windows**:
```cmd
# 检查 PATH 是否包含 Python Scripts 目录
echo %PATH% | findstr Scripts
# 如果没有，运行 setup_path.bat 或手动添加
```

**macOS/Linux**:
```bash
# 检查 PATH
echo $PATH | grep -E "(local/bin|Library/Python)"
# 重新加载 shell 配置
source ~/.bashrc  # Linux
source ~/.zshrc   # macOS
```

#### 2. 依赖安装失败

```bash
# 升级 pip
python -m pip install --upgrade pip

# 清除缓存重新安装
pip cache purge
pip install --user --force-reinstall watchdog psutil click
```

#### 3. 权限错误

**Windows**: 以管理员身份运行命令提示符
**macOS/Linux**: 使用 `--user` 参数避免权限问题

### 卸载

```bash
# 卸载 AUV
pip uninstall auv

# 清理配置文件
# Windows: 删除 %APPDATA%\auv 文件夹
# macOS/Linux: 删除 ~/.config/auv 文件夹
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issues 和 Pull Requests！

---

**让文件整理变得简单高效！** 🎉