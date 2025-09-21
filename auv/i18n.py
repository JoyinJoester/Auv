"""
Internationalization support for AUV.
"""

import locale
import os
from pathlib import Path
from typing import Dict, Optional


class I18n:
    """Internationalization manager."""
    
    def __init__(self):
        self.current_language = self._detect_language()
        self.translations = self._load_translations()
    
    def _detect_language(self) -> str:
        """Detect system language."""
        try:
            # Get system locale
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                if system_locale.startswith('zh'):
                    return 'zh_CN'
                elif system_locale.startswith('en'):
                    return 'en_US'
        except:
            pass
        
        # Default to English
        return 'en_US'
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load translation dictionaries."""
        return {
            'en_US': {
                # CLI messages
                'Automatic file organization tool for Downloads folder': 'Automatic file organization tool for Downloads folder',
                'Process only PDF files': 'Process only PDF files',
                'Process only image files': 'Process only image files',
                'Process only document files': 'Process only document files',
                'Process only video files': 'Process only video files',
                'Process only audio files': 'Process only audio files',
                'Available commands': 'Available commands',
                'Configure file organization rules': 'Configure file organization rules',
                'Set target path for PDF files': 'Set target path for PDF files',
                'Set target path for image files': 'Set target path for image files',
                'Set target path for document files': 'Set target path for document files',
                'Set target path for video files': 'Set target path for video files',
                'Set target path for audio files': 'Set target path for audio files',
                'Start daemon mode': 'Start daemon mode',
                'Stop daemon mode': 'Stop daemon mode',
                'Show current configuration and status': 'Show current configuration and status',
                
                # Status messages
                'Operation cancelled by user.': 'Operation cancelled by user.',
                'Error': 'Error',
                'PDF target path set to: {}': 'PDF target path set to: {}',
                'Image target path set to: {}': 'Image target path set to: {}',
                'Document target path set to: {}': 'Document target path set to: {}',
                'Video target path set to: {}': 'Video target path set to: {}',
                'Audio target path set to: {}': 'Audio target path set to: {}',
                'No target paths specified. Use --help for usage information.': 'No target paths specified. Use --help for usage information.',
                'Starting daemon mode...': 'Starting daemon mode...',
                'Daemon stopped.': 'Daemon stopped.',
                'AUV Configuration Status': 'AUV Configuration Status',
                'Source path: {}': 'Source path: {}',
                'Target paths:': 'Target paths:',
                'Daemon status: Running': 'Daemon status: Running',
                'Daemon status: Stopped': 'Daemon status: Stopped',
                'Organizing files...': 'Organizing files...',
                'Successfully organized {} files.': 'Successfully organized {} files.',
                'No files to organize.': 'No files to organize.',
                
                # Core messages
                'Source path does not exist: {}': 'Source path does not exist: {}',
                'Moved: {} -> {}': 'Moved: {} -> {}',
                'Failed to move {}: {}': 'Failed to move {}: {}',
                'Cannot move file: {}': 'Cannot move file: {}',
                
                # Config messages
                'Warning: Failed to load config file, using defaults: {}': 'Warning: Failed to load config file, using defaults: {}',
                'Failed to save config: {}': 'Failed to save config: {}',
                
                # Daemon messages
                'AUV daemon is already running (PID: {})': 'AUV daemon is already running (PID: {})',
                'AUV daemon started with PID: {}': 'AUV daemon started with PID: {}',
                'Failed to start daemon: {}': 'Failed to start daemon: {}',
                'AUV daemon is not running': 'AUV daemon is not running',
                'AUV daemon stopped': 'AUV daemon stopped',
                'Failed to stop daemon: {}': 'Failed to stop daemon: {}',
                'File detected: {}': 'File detected: {}',
                'Organized: {} -> {}': 'Organized: {} -> {}',
                'Skipped: {}': 'Skipped: {}',
                
                # History messages
                'no_history_found': 'No operation history found',
                'operation_history': 'Operation History',
                'View operation history': 'View operation history',
                'Rollback to previous operation': 'Rollback to previous operation',
                'Rollback to specific timeline': 'Rollback to specific timeline',
                'History management enabled': 'History management enabled',
                'History management disabled': 'History management disabled',
            },
            'zh_CN': {
                # CLI messages
                'Automatic file organization tool for Downloads folder': '下载文件夹自动整理工具',
                'Process only PDF files': '仅处理PDF文件',
                'Process only image files': '仅处理图片文件',
                'Process only document files': '仅处理文档文件',
                'Process only video files': '仅处理视频文件',
                'Process only audio files': '仅处理音频文件',
                'Available commands': '可用命令',
                'Configure file organization rules': '配置文件整理规则',
                'Set target path for PDF files': '设置PDF文件目标路径',
                'Set target path for image files': '设置图片文件目标路径',
                'Set target path for document files': '设置文档文件目标路径',
                'Set target path for video files': '设置视频文件目标路径',
                'Set target path for audio files': '设置音频文件目标路径',
                'Start daemon mode': '启动守护进程模式',
                'Stop daemon mode': '停止守护进程模式',
                'Show current configuration and status': '显示当前配置和状态',
                
                # Status messages
                'Operation cancelled by user.': '操作被用户取消。',
                'Error': '错误',
                'PDF target path set to: {}': 'PDF目标路径设置为：{}',
                'Image target path set to: {}': '图片目标路径设置为：{}',
                'Document target path set to: {}': '文档目标路径设置为：{}',
                'Video target path set to: {}': '视频目标路径设置为：{}',
                'Audio target path set to: {}': '音频目标路径设置为：{}',
                'No target paths specified. Use --help for usage information.': '未指定目标路径。使用 --help 查看使用信息。',
                'Starting daemon mode...': '正在启动守护进程模式...',
                'Daemon stopped.': '守护进程已停止。',
                'AUV Configuration Status': 'AUV 配置状态',
                'Source path: {}': '源路径：{}',
                'Target paths:': '目标路径：',
                'Daemon status: Running': '守护进程状态：运行中',
                'Daemon status: Stopped': '守护进程状态：已停止',
                'Organizing files...': '正在整理文件...',
                'Successfully organized {} files.': '成功整理了 {} 个文件。',
                'No files to organize.': '没有需要整理的文件。',
                
                # Core messages
                'Source path does not exist: {}': '源路径不存在：{}',
                'Moved: {} -> {}': '已移动：{} -> {}',
                'Failed to move {}: {}': '移动失败 {}：{}',
                'Cannot move file: {}': '无法移动文件：{}',
                
                # Config messages
                'Warning: Failed to load config file, using defaults: {}': '警告：加载配置文件失败，使用默认配置：{}',
                'Failed to save config: {}': '保存配置失败：{}',
                
                # Daemon messages
                'AUV daemon is already running (PID: {})': 'AUV 守护进程已在运行（PID：{}）',
                'AUV daemon started with PID: {}': 'AUV 守护进程已启动，PID：{}',
                'Failed to start daemon: {}': '启动守护进程失败：{}',
                'AUV daemon is not running': 'AUV 守护进程未运行',
                'AUV daemon stopped': 'AUV 守护进程已停止',
                'Failed to stop daemon: {}': '停止守护进程失败：{}',
                'File detected: {}': '检测到文件：{}',
                'Organized: {} -> {}': '已整理：{} -> {}',
                'Skipped: {}': '已跳过：{}',
                
                # History messages
                'no_history_found': '未找到操作历史记录',
                'operation_history': '操作历史记录',
                'View operation history': '查看操作历史',
                'Rollback to previous operation': '回退到上一个操作',
                'Rollback to specific timeline': '回退到指定时间线',
                'History management enabled': '历史记录管理已启用',
                'History management disabled': '历史记录管理已禁用',
            }
        }
    
    def translate(self, text: str) -> str:
        """Translate text to current language."""
        if self.current_language in self.translations:
            return self.translations[self.current_language].get(text, text)
        return text
    
    def set_language(self, language: str) -> None:
        """Set current language."""
        if language in self.translations:
            self.current_language = language


# Global instance
_i18n = I18n()

# Translation function
def _(text: str) -> str:
    """Translation function."""
    return _i18n.translate(text)

# Language setter
def set_language(language: str) -> None:
    """Set current language."""
    _i18n.set_language(language)