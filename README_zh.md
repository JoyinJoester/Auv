# AUV - 智能文件整理工具 📁

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

一个功能强大的命令行文件整理工具，支持自动分类和整理各种文件类型，具有灵活的路径配置和智能整理模式。

[中文文档](README_zh.md) | [English](README.md)

## ✨ 核心特性

- 🗂️ **智能文件整理**: 根据文件类型自动分类，支持自定义规则
- 🎯 **自定义命令**: 创建个性化文件整理命令（如 `-py` 整理Python文件）
- 📜 **操作历史**: 追踪所有操作，支持基于时间线的回退功能
- 🔧 **灵活配置**: 启用/禁用文件类型，自定义目标路径
- 🏃 **守护进程模式**: 后台监控，自动整理新文件
- 🌍 **跨平台支持**: 支持 Windows、macOS 和 Linux
- 🔒 **安全操作**: 自动备份和回退功能

## 🚀 快速开始

### 安装

```bash
# 安装依赖
pip install watchdog psutil click

# 安装 AUV
pip install --user -e .

# 验证安装
auv --help
```

### 基本用法

```bash
# 整理当前目录文件
auv -pdf                    # 整理PDF文件
auv -img                    # 整理图片文件
auv -py                     # 整理Python文件（自定义命令）

# 指定整理路径
auv -pdf here               # 在当前目录创建PDF文件夹
auv -pdf ./Documents        # 移动PDF到Documents文件夹

# 查看配置和历史
auv status                  # 显示当前配置
auv history                 # 查看操作历史
auv return                  # 回退上一个操作
```

## 📚 核心命令

### 文件整理
```bash
auv -pdf                    # 整理PDF文件
auv -img                    # 整理图片文件
auv -doc                    # 整理文档文件
auv -video                  # 整理视频文件
auv -audio                  # 整理音频文件
```

### 配置管理
```bash
auv set enable archive     # 启用压缩包文件支持
auv set path pdf ~/PDFs     # 设置PDF默认目标路径
auv set custom add py .py .pyw --path ~/Python  # 创建自定义命令
```

### 历史记录与回退
```bash
auv history                 # 查看操作历史
auv history --limit 10      # 显示最近10个操作
auv return                  # 回退上一个操作
auv return T15              # 回退到时间线T15
```

### 守护进程模式
```bash
auv agent                   # 启动后台监控
auv agent --stop            # 停止守护进程
```

## 🎯 支持的文件类型

### 基本类型（始终可用）
- **PDF**: `.pdf`
- **图片**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`
- **文档**: `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`
- **视频**: `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`
- **音频**: `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`

### 扩展类型（按需启用）
- **安装包**: `.exe`, `.msi`, `.dmg`, `.deb`, `.rpm`
- **压缩包**: `.zip`, `.rar`, `.7z`, `.tar.gz`, `.iso`
- **代码文件**: `.py`, `.js`, `.html`, `.css`, `.java`, `.cpp`
- **字体文件**: `.ttf`, `.otf`, `.woff`, `.woff2`
- **电子书**: `.epub`, `.mobi`, `.azw`

### 自定义类型
为任何文件扩展名创建无限制的自定义命令。

## 📖 配置

配置文件位置：
- **Windows**: `%APPDATA%\auv\config.json`
- **macOS/Linux**: `~/.config/auv/config.json`

配置示例：
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

## 🔧 高级用法

### 自定义命令
为你的工作流程创建专用命令：

```bash
# 为开发创建命令
auv set custom add frontend .html .css .js .vue
auv set custom add backend .py .sql .yaml
auv set custom add mobile .java .swift .dart

# 启用并使用
auv set enable frontend backend mobile
auv -frontend              # 整理前端文件
auv -backend               # 整理后端文件
```

### 批量操作
```bash
# 一次整理多种文件类型
auv -pdf -img -doc         # 整理多种类型

# 不同工作目录
auv -d -pdf                # 整理下载文件夹
auv here -img Pictures     # 在本地创建Pictures文件夹
```

### 智能路径处理
```bash
auv -pdf ./documents       # 相对路径
auv -pdf ~/Documents       # 主目录
auv -pdf /absolute/path    # 绝对路径
```

## 📜 历史系统

AUV使用基于时间线的系统追踪所有操作：

```
操作历史记录
==================================================
✓ T15 | 2025-09-21 14:30:25
   Type: organize_files
   Description: 整理了5个PDF文件
   Files moved: 5

✓ T14 | 2025-09-21 14:25:10  
   Type: custom_organize
   Description: 整理了Python文件
   Files moved: 3
```

- ✓ = 可回退的操作
- ✗ = 不可回退的操作

## 🛠️ 开发

### 项目结构
```
auv/
├── auv/                    # 主包
│   ├── cli.py             # 命令行界面
│   ├── core_v2.py         # 文件整理逻辑
│   ├── config.py          # 配置管理
│   ├── history.py         # 历史记录追踪
│   └── daemon.py          # 后台监控
├── tests/                 # 测试文件
└── setup.py               # 包配置
```

### 贡献指南
1. Fork 仓库
2. 创建功能分支
3. 进行更改
4. 添加测试（如适用）
5. 提交拉取请求

## 📋 系统要求

- **Python**: 3.7 或更高版本
- **依赖**: watchdog, psutil, click
- **操作系统**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 支持

- 🐛 [报告问题](https://github.com/JoyinJoester/Auv/issues)
- 💡 [功能请求](https://github.com/JoyinJoester/Auv/issues)
- 📖 [英文文档](README.md)

---

**让文件整理变得简单高效！** 🎉