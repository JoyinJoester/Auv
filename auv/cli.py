#!/usr/bin/env python3
"""
AUV - Automatic file organization Utilities
Command line interface for file organization in Downloads folder.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

from .core import FileOrganizer
from .config import ConfigManager
from .daemon import DaemonManager
from .i18n import _
from .history import get_history_manager


def create_dynamic_parser(config_manager) -> argparse.ArgumentParser:
    """Create argument parser with dynamic custom commands."""
    parser = argparse.ArgumentParser(
        prog='auv',
        description=_('智能文件整理工具'),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_('''
使用示例:
  auv                           # 整理当前文件夹的所有文件
  auv -pdf                      # 整理当前文件夹的 PDF 文件到默认路径
  auv -d -pdf                   # 整理下载文件夹的 PDF 文件
  auv here -pdf                 # 在当前目录创建 PDF 文件夹并整理
  auv here -pdf mypdf           # 在当前目录创建 mypdf 文件夹并整理
  auv -pdf ./documents          # 整理 PDF 到相对路径
  auv -pdf D:\\MyDocs           # 整理 PDF 到绝对路径
  auv set path pdf ~/Documents/PDFs  # 设置 PDF 默认目标路径
  auv -py                       # 使用自定义 py 命令整理 Python 文件 (如果已配置)
        ''')
    )
    
    # 工作目录选项
    parser.add_argument('-d', '--downloads', action='store_true',
                       help=_('操作下载文件夹而不是当前文件夹'))
    
    # 基本文件类型过滤器
    basic_file_types = ['pdf', 'image', 'document', 'video', 'audio']
    extended_file_types = ['installer', 'archive', 'code', 'font', 'ebook']
    
    for file_type in basic_file_types:
        enabled = config_manager.is_file_type_enabled(file_type)
        if file_type == 'image':
            help_text = _('处理图片文件，可选指定目标路径')
            short_arg = '-img'
        else:
            help_text = _('处理 {} 文件，可选指定目标路径').format(file_type.upper())
            short_arg = f'-{file_type}'
        
        if not enabled:
            help_text += _(' (已禁用)')
            
        parser.add_argument(short_arg, f'--{file_type}', nargs='?', const='__default__',
                           help=help_text)
    
    # 扩展文件类型过滤器
    for file_type in extended_file_types:
        enabled = config_manager.is_file_type_enabled(file_type)
        help_text = _('处理 {} 文件 {}，可选指定目标路径').format(
            file_type, 
            _('(需要启用)') if not enabled else ''
        )
        
        parser.add_argument(f'-{file_type}', f'--{file_type}', nargs='?', const='__default__',
                           help=help_text)
    
    # 动态添加自定义命令参数
    custom_commands = config_manager.get_custom_commands()
    for cmd_name, cmd_config in custom_commands.items():
        enabled = cmd_config.get('enabled', False)
        extensions = cmd_config.get('extensions', [])
        help_text = _('处理 {} 文件 ({}) {}，可选指定目标路径').format(
            cmd_name,
            ', '.join(extensions),
            _('(已禁用)') if not enabled else ''
        )
        
        parser.add_argument(f'-{cmd_name}', f'--{cmd_name}', nargs='?', const='__default__',
                           help=help_text)
    
    # 版本信息
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    return parser


def create_subcommand_parser(config_manager) -> argparse.ArgumentParser:
    """Create argument parser for subcommands."""
    parser = argparse.ArgumentParser(
        prog='auv',
        description=_('智能文件整理工具'),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 版本信息
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help=_('可用命令'))
    
    # Set command - 设置默认路径和文件类型管理
    set_parser = subparsers.add_parser('set', help=_('设置路径和文件类型管理'))
    set_subparsers = set_parser.add_subparsers(dest='set_type', help=_('设置类型'))
    
    # 路径设置
    path_parser = set_subparsers.add_parser('path', help=_('设置文件类型路径'))
    all_file_types = ['downloads', 'pdf', 'image', 'document', 'video', 'audio', 
                      'installer', 'archive', 'code', 'font', 'ebook']
    # 添加自定义命令到路径设置选项
    custom_commands = config_manager.get_custom_commands()
    all_file_types.extend(list(custom_commands.keys()))
    
    path_parser.add_argument('type', choices=all_file_types,
                           help=_('要设置的路径类型'))
    path_parser.add_argument('path', help=_('目标路径'))
    
    # 文件类型启用/禁用
    enable_parser = set_subparsers.add_parser('enable', help=_('启用文件类型'))
    enable_types = ['pdf', 'image', 'document', 'video', 'audio',
                   'installer', 'archive', 'code', 'font', 'ebook']
    enable_types.extend(list(custom_commands.keys()))
    enable_parser.add_argument('type', choices=enable_types,
                             help=_('要启用的文件类型'))
    
    disable_parser = set_subparsers.add_parser('disable', help=_('禁用文件类型'))
    disable_parser.add_argument('type', choices=enable_types,
                               help=_('要禁用的文件类型'))
    
    # 自定义命令管理
    custom_parser = set_subparsers.add_parser('custom', help=_('管理自定义命令'))
    custom_subparsers = custom_parser.add_subparsers(dest='custom_action', help=_('自定义命令操作'))
    
    # 添加自定义命令
    add_parser = custom_subparsers.add_parser('add', help=_('添加自定义命令'))
    add_parser.add_argument('name', help=_('命令名称 (如: py, js, css)'))
    add_parser.add_argument('extensions', nargs='+', help=_('文件扩展名 (如: .py .pyw)'))
    add_parser.add_argument('--path', help=_('目标路径 (可选)'))
    
    # 删除自定义命令
    remove_parser = custom_subparsers.add_parser('remove', help=_('删除自定义命令'))
    if custom_commands:
        remove_parser.add_argument('name', choices=list(custom_commands.keys()),
                                 help=_('要删除的命令名称'))
    else:
        remove_parser.add_argument('name', help=_('要删除的命令名称'))
    
    # 列出自定义命令
    custom_subparsers.add_parser('list', help=_('列出所有自定义命令'))
    
    # Agent command
    agent_parser = subparsers.add_parser('agent', help=_('守护进程模式'))
    agent_parser.add_argument('--stop', action='store_true', help=_('停止守护进程'))
    
    # Status command
    subparsers.add_parser('status', help=_('显示当前配置和状态'))
    
    # History command
    history_parser = subparsers.add_parser('history', help=_('查看操作历史'))
    history_parser.add_argument('--limit', type=int, default=20, help=_('显示最近的历史记录数量'))
    
    # Return command
    return_parser = subparsers.add_parser('return', help=_('回退操作'))
    return_parser.add_argument('timeline', nargs='?', help=_('时间线ID (留空则回退上一操作)'))
    
    return parser


def handle_file_organization_mode(parser, config_manager, args_list):
    """Handle file organization mode with dynamic parsing."""
    # 手动解析 here 参数
    here_or_path = None
    if 'here' in args_list:
        here_index = args_list.index('here')
        args_list.pop(here_index)  # 移除 'here'
        here_or_path = 'here'
        
        # 检查是否有自定义文件夹名
        if here_index < len(args_list) and not args_list[here_index].startswith('-'):
            here_or_path = args_list.pop(here_index)
    
    args = parser.parse_args(args_list)
    args.here_or_path = here_or_path
    
    # 处理文件整理
    handle_organize_command_new(args, config_manager)


def main():
    """Main entry point for AUV CLI."""
    # 首先创建配置管理器以获取自定义命令
    config_manager = ConfigManager()
    
    # 检查是否为简单的file组织模式（没有子命令）
    args_list = sys.argv[1:]
    if not args_list or not any(arg in ['set', 'agent', 'status', 'history', 'return'] for arg in args_list):
        # 文件整理模式，使用动态解析器
        parser = create_dynamic_parser(config_manager)
        handle_file_organization_mode(parser, config_manager, args_list)
        return
    
    # 子命令模式
    parser = create_subcommand_parser(config_manager)
    args = parser.parse_args()
    
    try:
        if args.command == 'set':
            handle_set_command_new(args, config_manager)
        elif args.command == 'agent':
            handle_agent_command(args, config_manager)
        elif args.command == 'status':
            handle_status_command(config_manager)
        elif args.command == 'history':
            handle_history_command(args, config_manager)
        elif args.command == 'return':
            handle_return_command(args, config_manager)
        else:
            print(_('未知命令，请使用 --help 查看帮助'))
            
    except KeyboardInterrupt:
        print(_('\nOperation cancelled by user.'))
        sys.exit(1)
    except Exception as e:
        print(f"{_('Error')}: {e}")
        sys.exit(1)


def handle_set_command(args, config_manager: ConfigManager):
    """Handle the 'set' command for configuring paths."""
    updated = False
    
    if args.pdf:
        config_manager.set_target_path('pdf', args.pdf)
        print(_('PDF target path set to: {}').format(args.pdf))
        updated = True
    
    if args.image:
        config_manager.set_target_path('image', args.image)
        print(_('Image target path set to: {}').format(args.image))
        updated = True
    
    if args.document:
        config_manager.set_target_path('document', args.document)
        print(_('Document target path set to: {}').format(args.document))
        updated = True
    
    if args.video:
        config_manager.set_target_path('video', args.video)
        print(_('Video target path set to: {}').format(args.video))
        updated = True
    
    if args.audio:
        config_manager.set_target_path('audio', args.audio)
        print(_('Audio target path set to: {}').format(args.audio))
        updated = True
    
    if not updated:
        print(_('No target paths specified. Use --help for usage information.'))


def handle_agent_command(args, config_manager: ConfigManager):
    """Handle the 'agent' command for daemon mode."""
    daemon_manager = DaemonManager(config_manager)
    
    if args.stop:
        daemon_manager.stop()
        print(_('Daemon stopped.'))
    else:
        print(_('Starting daemon mode...'))
        daemon_manager.start()


def handle_status_command(config_manager: ConfigManager):
    """Handle the 'status' command."""
    print(_('AUV Configuration Status'))
    print('=' * 50)
    
    # Show source path
    source_path = config_manager.get_source_path()
    print(_('源路径: {}').format(source_path))
    
    # Show all file types status
    print(_('\n文件类型状态:'))
    file_types_status = config_manager.get_file_types_status()
    
    # 基本文件类型
    basic_types = ['pdf', 'image', 'document', 'video', 'audio']
    print(_('  基本文件类型:'))
    for file_type in basic_types:
        enabled = file_types_status.get(file_type, True)
        status = _('启用') if enabled else _('禁用')
        target_path = config_manager.get_target_path(file_type) if enabled else _('未设置')
        print(f'    {file_type}: {status} -> {target_path}')
    
    # 扩展文件类型
    extended_types = ['installer', 'archive', 'code', 'font', 'ebook']
    print(_('  扩展文件类型:'))
    for file_type in extended_types:
        enabled = file_types_status.get(file_type, False)
        status = _('启用') if enabled else _('禁用')
        target_path = config_manager.get_target_path(file_type) if enabled else _('未设置')
        print(f'    {file_type}: {status} -> {target_path}')
    
    # 自定义命令
    custom_commands = config_manager.get_custom_commands()
    if custom_commands:
        print(_('\n自定义命令:'))
        for cmd_name, cmd_config in custom_commands.items():
            enabled = cmd_config.get('enabled', False)
            extensions = cmd_config.get('extensions', [])
            target_path = cmd_config.get('target_path', _('未设置'))
            status = _('启用') if enabled else _('禁用')
            print(f'  {cmd_name}: {status} ({", ".join(extensions)}) -> {target_path}')
    else:
        print(_('\n自定义命令: 无'))
    
    # Show daemon status
    daemon_manager = DaemonManager(config_manager)
    if daemon_manager.is_running():
        print(_('\n守护进程状态: 运行中'))
    else:
        print(_('\n守护进程状态: 已停止'))
    
    # Show history status
    history_enabled = config_manager.is_history_enabled()
    print(_('\n历史记录状态: {}').format(_('启用') if history_enabled else _('禁用')))
    
    if history_enabled:
        history_manager = get_history_manager()
        history = history_manager.get_history(limit=5)
        if history:
            print(_('  最近操作:'))
            for entry in history:
                print(f'    {entry.timeline_id}: {entry.description[:50]}...' if len(entry.description) > 50 else f'    {entry.timeline_id}: {entry.description}')
        else:
            print(_('  暂无操作历史'))
    
    print()  # Empty line at the end


def handle_organize_command(args, config_manager: ConfigManager):
    """Handle file organization commands."""
    organizer = FileOrganizer(config_manager)
    
    # 所有文件类型列表
    all_file_types = ['pdf', 'image', 'document', 'video', 'audio', 'installer', 'archive', 'code', 'font', 'ebook']
    
    # Determine which file types to process
    file_types = []
    for file_type in all_file_types:
        # 处理 image 参数映射
        attr_name = 'image' if file_type == 'image' else file_type
        if hasattr(args, attr_name) and getattr(args, attr_name):
            # 检查扩展文件类型是否启用
            extended_types = ['installer', 'archive', 'code', 'font', 'ebook']
            if file_type in extended_types and not config_manager.is_extended_type_enabled(file_type):
                print(_('扩展文件类型 "{}" 未启用，使用 "auv set enable {}" 启用').format(file_type, file_type))
                continue
            file_types.append(file_type)
    
    # If no specific type specified, process all enabled types
    if not file_types:
        file_types = None
    
    print(_('Organizing files...'))
    moved_count = organizer.organize_files(file_types)
    
    if moved_count > 0:
        print(_('Successfully organized {} files.').format(moved_count))
    else:
        print(_('No files to organize.'))


def handle_set_command_new(args, config_manager: ConfigManager):
    """Handle the new 'set' command for setting default paths and extended features."""
    
    # 处理子命令结构
    if hasattr(args, 'set_type') and args.set_type:
        if args.set_type == 'path':
            # 路径设置
            path_type = args.type
            target_path = args.path
            
            if path_type == 'downloads':
                config_manager.set_downloads_path(target_path)
                print(_('下载文件夹路径设置为: {}').format(target_path))
            elif path_type in config_manager.get_custom_commands():
                # 自定义命令路径设置
                config_manager.set_custom_command_target_path(path_type, target_path)
                print(_('自定义命令 {} 路径设置为: {}').format(path_type, target_path))
            else:
                # 标准文件类型路径设置
                config_manager.set_target_path(path_type, target_path)
                print(_('{} 默认路径设置为: {}').format(path_type.upper(), target_path))
                
        elif args.set_type == 'enable':
            # 启用文件类型或自定义命令
            file_type = args.type
            if file_type in config_manager.get_custom_commands():
                config_manager.set_custom_command_enabled(file_type, True)
                print(_('已启用自定义命令: {}').format(file_type))
            else:
                config_manager.set_file_type_enabled(file_type, True)
                print(_('已启用文件类型: {}').format(file_type))
            
        elif args.set_type == 'disable':
            # 禁用文件类型或自定义命令
            file_type = args.type
            if file_type in config_manager.get_custom_commands():
                config_manager.set_custom_command_enabled(file_type, False)
                print(_('已禁用自定义命令: {}').format(file_type))
            else:
                config_manager.set_file_type_enabled(file_type, False)
                print(_('已禁用文件类型: {}').format(file_type))
                
        elif args.set_type == 'custom':
            # 自定义命令管理
            if hasattr(args, 'custom_action') and args.custom_action:
                if args.custom_action == 'add':
                    # 添加自定义命令
                    cmd_name = args.name
                    extensions = args.extensions
                    target_path = getattr(args, 'path', None)
                    
                    config_manager.add_custom_command(cmd_name, extensions, target_path)
                    print(_('已添加自定义命令: {} (扩展名: {})').format(cmd_name, ', '.join(extensions)))
                    
                elif args.custom_action == 'remove':
                    # 删除自定义命令
                    cmd_name = args.name
                    config_manager.remove_custom_command(cmd_name)
                    print(_('已删除自定义命令: {}').format(cmd_name))
                    
                elif args.custom_action == 'list':
                    # 列出自定义命令
                    custom_commands = config_manager.get_custom_commands()
                    if custom_commands:
                        print(_('自定义命令列表:'))
                        for cmd_name, cmd_config in custom_commands.items():
                            enabled = cmd_config.get('enabled', False)
                            extensions = cmd_config.get('extensions', [])
                            target_path = cmd_config.get('target_path', '')
                            status = _('启用') if enabled else _('禁用')
                            print(f'  {cmd_name}: {status} - {", ".join(extensions)} -> {target_path}')
                    else:
                        print(_('没有配置自定义命令'))
            else:
                print(_('请指定自定义命令操作，使用 "auv set custom --help" 查看帮助'))
    else:
        print(_('请指定要设置的参数，使用 "auv set --help" 查看帮助'))


def handle_organize_command_new(args, config_manager: ConfigManager):
    """Handle the new flexible organize command."""
    from .core_v2 import FlexibleFileOrganizer
    
    # 确定工作目录
    if hasattr(args, 'downloads') and args.downloads:
        source_path = Path(config_manager.get_downloads_path())
        print(_('整理下载文件夹: {}').format(source_path))
    else:
        source_path = Path.cwd()
        print(_('整理当前文件夹: {}').format(source_path))
    
    if not source_path.exists():
        print(_('源路径不存在: {}').format(source_path))
        return
    
    organizer = FlexibleFileOrganizer(config_manager)
    
    # 收集文件类型和目标路径
    file_operations = []
    
    # 检查基本文件类型参数
    basic_file_types = ['pdf', 'image', 'document', 'video', 'audio']
    extended_file_types = ['installer', 'archive', 'code', 'font', 'ebook']
    all_standard_types = basic_file_types + extended_file_types
    
    for file_type in all_standard_types:
        # 处理 image 参数映射
        attr_name = 'image' if file_type == 'image' else file_type
        type_value = getattr(args, attr_name, None)
        if type_value is not None:
            # 检查文件类型是否启用
            if not config_manager.is_file_type_enabled(file_type):
                print(_('文件类型 "{}" 未启用，使用 "auv set enable {}" 启用').format(file_type, file_type))
                continue
                
            target_path = determine_target_path(
                file_type, type_value, getattr(args, 'here_or_path', None), config_manager, source_path
            )
            file_operations.append((file_type, target_path))
    
    # 检查自定义命令参数
    custom_commands = config_manager.get_custom_commands()
    for cmd_name, cmd_config in custom_commands.items():
        type_value = getattr(args, cmd_name, None)
        if type_value is not None:
            # 检查自定义命令是否启用
            if not config_manager.is_custom_command_enabled(cmd_name):
                print(_('自定义命令 "{}" 未启用，使用 "auv set enable {}" 启用').format(cmd_name, cmd_name))
                continue
            
            # 获取自定义命令的目标路径
            if type_value != '__default__':
                # 用户指定了路径
                target_path = Path(type_value).resolve()
            else:
                # 使用配置的默认路径
                default_path = config_manager.get_custom_command_target_path(cmd_name)
                if default_path:
                    target_path = Path(default_path).resolve()
                else:
                    target_path = source_path / f"{cmd_name.title()}Files"
            
            file_operations.append((cmd_name, target_path))
    
    # 如果没有指定任何文件类型，处理所有启用的类型
    if not file_operations:
        print(_('没有指定文件类型，整理所有启用的文件类型...'))
        # 处理所有启用的标准文件类型
        for file_type in all_standard_types:
            if config_manager.is_file_type_enabled(file_type):
                target_path = Path(config_manager.get_target_path(file_type)).resolve()
                file_operations.append((file_type, target_path))
        
        # 处理所有启用的自定义命令
        for cmd_name, cmd_config in custom_commands.items():
            if config_manager.is_custom_command_enabled(cmd_name):
                default_path = config_manager.get_custom_command_target_path(cmd_name)
                if default_path:
                    target_path = Path(default_path).resolve()
                else:
                    target_path = source_path / f"{cmd_name.title()}Files"
                file_operations.append((cmd_name, target_path))
    
    # 执行文件整理
    total_moved = 0
    for file_type_or_cmd, target_path in file_operations:
        if file_type_or_cmd in custom_commands:
            # 处理自定义命令
            extensions = custom_commands[file_type_or_cmd]['extensions']
            moved = organizer.organize_files_by_extensions(source_path, extensions, target_path)
            print(_('已移动 {} 个 {} 文件到 {}').format(moved, file_type_or_cmd, target_path))
        else:
            # 处理标准文件类型
            moved = organizer.organize_files_by_type(source_path, file_type_or_cmd, target_path)
            print(_('已移动 {} 个 {} 文件到 {}').format(moved, file_type_or_cmd, target_path))
        total_moved += moved
    
    if total_moved > 0:
        print(_('成功整理了 {} 个文件').format(total_moved))
    else:
        print(_('没有找到需要整理的文件'))


def determine_target_path(file_type: str, type_value: str, here_or_path: Optional[str], 
                         config_manager: ConfigManager, source_path: Path) -> Optional[Path]:
    """确定目标路径的逻辑"""
    
    # 如果有 here_or_path 参数
    if here_or_path:
        if here_or_path == 'here':
            # 在当前目录创建文件夹
            if type_value and type_value != '__default__':
                # 使用自定义文件夹名
                return source_path / type_value
            else:
                # 使用默认文件夹名
                folder_names = {
                    'pdf': 'PDF',
                    'image': 'Images', 
                    'document': 'Documents',
                    'video': 'Videos',
                    'audio': 'Audio'
                }
                return source_path / folder_names.get(file_type, file_type.upper())
        else:
            # here_or_path 是路径
            return Path(here_or_path).resolve()
    
    # 如果文件类型参数指定了路径
    if type_value and type_value != '__default__':
        return Path(type_value).resolve()
    
    # 使用默认配置
    default_path = config_manager.get_target_path(file_type)
    return Path(default_path).resolve() if default_path else None


def handle_history_command(args, config_manager: ConfigManager):
    """Handle the 'history' command."""
    if not config_manager.is_history_enabled():
        print(_('历史记录功能已禁用'))
        return
    
    history_manager = get_history_manager()
    history_output = history_manager.display_history(limit=args.limit)
    print(history_output)


def handle_return_command(args, config_manager: ConfigManager):
    """Handle the 'return' command for rollback operations."""
    if not config_manager.is_history_enabled():
        print(_('历史记录功能已禁用'))
        return
    
    history_manager = get_history_manager()
    
    if args.timeline:
        # 回退到指定时间线
        success, message = history_manager.rollback_to_timeline(args.timeline)
        if success:
            print(_('✓ {}').format(message))
        else:
            print(_('✗ {}').format(message))
    else:
        # 回退上一个操作
        success, message = history_manager.rollback_last_operation()
        if success:
            print(_('✓ {}').format(message))
        else:
            print(_('✗ {}').format(message))


if __name__ == '__main__':
    main()