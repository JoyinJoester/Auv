"""
Configuration management for AUV.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, List

from .i18n import _


class ConfigManager:
    """Manages configuration settings for AUV."""
    
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / 'config.json'
        self.config = self._load_config()
    
    def _get_config_dir(self) -> Path:
        """Get the configuration directory path."""
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', '')) / 'auv'
        else:  # Unix-like (Linux, macOS)
            config_dir = Path.home() / '.config' / 'auv'
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def _load_config(self) -> Dict:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(_('Warning: Failed to load config file, using defaults: {}').format(e))
        
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration."""
        downloads_path = self._get_default_downloads_path()
        
        return {
            'downloads_path': str(downloads_path),
            'target_paths': {
                'pdf': str(Path.home() / 'Documents' / 'PDFs'),
                'image': str(Path.home() / 'Pictures'),
                'document': str(Path.home() / 'Documents'),
                'video': str(Path.home() / 'Videos'),
                'audio': str(Path.home() / 'Music'),
                # Extended file types (with default paths)
                'installer': str(Path.home() / 'Downloads' / 'Installers'),
                'archive': str(Path.home() / 'Downloads' / 'Archives'),
                'code': str(Path.home() / 'Documents' / 'Code'),
                'font': str(Path.home() / 'Downloads' / 'Fonts'),
                'ebook': str(Path.home() / 'Documents' / 'eBooks')
            },
            'daemon': {
                'enabled': False,
                'watch_subdirs': False
            },
            'file_types': {
                # Basic file types (enabled by default)
                'pdf': True,
                'image': True,
                'document': True,
                'video': True,
                'audio': True,
                # Extended file types (disabled by default)
                'installer': False,
                'archive': False,
                'code': False,
                'font': False,
                'ebook': False
            },
            'custom_commands': {
                # Custom command examples:
                # 'py': {
                #     'extensions': ['.py'],
                #     'target_path': 'Documents/PythonFiles',
                #     'enabled': True
                # }
            },
            'history': {
                'enabled': True,
                'max_entries': 1000,
                'auto_cleanup_days': 30
            },
            'language': 'auto'
        }
    
    def _get_default_downloads_path(self) -> Path:
        """Get the default Downloads folder path."""
        if os.name == 'nt':  # Windows
            downloads_path = Path.home() / 'Downloads'
        else:  # Unix-like
            downloads_path = Path.home() / 'Downloads'
        
        return downloads_path
    
    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise Exception(_('Failed to save config: {}').format(e))
    
    def get_downloads_path(self) -> str:
        """Get the downloads folder path."""
        return self.config.get('downloads_path', self._get_default_downloads_path())
    
    def set_downloads_path(self, path: str) -> None:
        """Set the downloads folder path."""
        self.config['downloads_path'] = str(Path(path).resolve())
        self.save_config()
    
    def get_source_path(self) -> str:
        """Get the source path (Downloads folder) - for backward compatibility."""
        return self.get_downloads_path()
    
    def set_source_path(self, path: str) -> None:
        """Set the source path - for backward compatibility."""
        self.set_downloads_path(path)
    
    def get_target_path(self, file_type: str) -> Optional[str]:
        """Get target path for a file type."""
        return self.config['target_paths'].get(file_type)
    
    def set_target_path(self, file_type: str, path: str) -> None:
        """Set target path for a file type."""
        # Resolve path (handle relative paths)
        resolved_path = Path(path).resolve()
        self.config['target_paths'][file_type] = str(resolved_path)
        self.save_config()
    
    def get_all_target_paths(self) -> Dict[str, str]:
        """Get all target paths."""
        return self.config['target_paths'].copy()
    
    def is_file_type_enabled(self, file_type: str) -> bool:
        """Check if a file type is enabled."""
        return self.config.get('file_types', {}).get(file_type, True)
    
    def set_file_type_enabled(self, file_type: str, enabled: bool) -> None:
        """Enable or disable a file type."""
        if 'file_types' not in self.config:
            self.config['file_types'] = {}
        self.config['file_types'][file_type] = enabled
        self.save_config()
    
    def get_file_types_status(self) -> Dict[str, bool]:
        """Get the status of all file types."""
        default_status = {
            'pdf': True, 'image': True, 'document': True, 'video': True, 'audio': True,
            'installer': False, 'archive': False, 'code': False, 'font': False, 'ebook': False
        }
        user_status = self.config.get('file_types', {})
        default_status.update(user_status)
        return default_status
    
    def get_enabled_file_types(self) -> List[str]:
        """Get list of enabled file types."""
        return [ft for ft, enabled in self.get_file_types_status().items() if enabled]
    
    # Custom commands management
    def add_custom_command(self, command_name: str, extensions: List[str], 
                          target_path: str = None, enabled: bool = True) -> None:
        """Add a custom command configuration."""
        if 'custom_commands' not in self.config:
            self.config['custom_commands'] = {}
        
        self.config['custom_commands'][command_name] = {
            'extensions': extensions,
            'target_path': target_path or f'Documents/{command_name.title()}Files',
            'enabled': enabled
        }
        self.save_config()
    
    def remove_custom_command(self, command_name: str) -> None:
        """Remove a custom command configuration."""
        if 'custom_commands' in self.config and command_name in self.config['custom_commands']:
            del self.config['custom_commands'][command_name]
            self.save_config()
    
    def get_custom_commands(self) -> Dict[str, Dict]:
        """Get all custom commands."""
        return self.config.get('custom_commands', {}).copy()
    
    def is_custom_command_enabled(self, command_name: str) -> bool:
        """Check if a custom command is enabled."""
        custom_commands = self.config.get('custom_commands', {})
        return custom_commands.get(command_name, {}).get('enabled', False)
    
    def set_custom_command_enabled(self, command_name: str, enabled: bool) -> None:
        """Enable or disable a custom command."""
        if 'custom_commands' not in self.config:
            self.config['custom_commands'] = {}
        if command_name not in self.config['custom_commands']:
            return
        
        self.config['custom_commands'][command_name]['enabled'] = enabled
        self.save_config()
    
    def get_custom_command_target_path(self, command_name: str) -> Optional[str]:
        """Get target path for a custom command."""
        custom_commands = self.config.get('custom_commands', {})
        command_config = custom_commands.get(command_name, {})
        return command_config.get('target_path')
    
    def set_custom_command_target_path(self, command_name: str, target_path: str) -> None:
        """Set target path for a custom command."""
        if 'custom_commands' not in self.config:
            self.config['custom_commands'] = {}
        if command_name not in self.config['custom_commands']:
            return
            
        self.config['custom_commands'][command_name]['target_path'] = target_path
        self.save_config()
    
    # Legacy support for extended_types (will be migrated)
    def is_extended_type_enabled(self, file_type: str) -> bool:
        """Check if an extended file type is enabled (legacy support)."""
        # First check new file_types structure
        if 'file_types' in self.config:
            return self.config['file_types'].get(file_type, False)
        # Fallback to old extended_types structure
        return self.config.get('extended_types', {}).get(file_type, False)
    
    def set_extended_type_enabled(self, file_type: str, enabled: bool) -> None:
        """Enable or disable an extended file type (legacy support)."""
        # Use new file_types structure
        self.set_file_type_enabled(file_type, enabled)
    
    def is_daemon_enabled(self) -> bool:
        """Check if daemon mode is enabled."""
        return self.config['daemon']['enabled']
    
    def set_daemon_enabled(self, enabled: bool) -> None:
        """Enable or disable daemon mode."""
        self.config['daemon']['enabled'] = enabled
        self.save_config()
    
    def should_watch_subdirs(self) -> bool:
        """Check if subdirectories should be watched."""
        return self.config['daemon']['watch_subdirs']
    
    def set_watch_subdirs(self, watch: bool) -> None:
        """Set whether to watch subdirectories."""
        self.config['daemon']['watch_subdirs'] = watch
        self.save_config()
    
    def get_language(self) -> str:
        """Get the configured language."""
        return self.config.get('language', 'auto')
    
    def set_language(self, language: str) -> None:
        """Set the language."""
        self.config['language'] = language
        self.save_config()
    
    # History management methods
    def is_history_enabled(self) -> bool:
        """Check if history tracking is enabled."""
        return self.config.get('history', {}).get('enabled', True)
    
    def set_history_enabled(self, enabled: bool) -> None:
        """Enable or disable history tracking."""
        if 'history' not in self.config:
            self.config['history'] = {}
        self.config['history']['enabled'] = enabled
        self.save_config()
    
    def get_history_max_entries(self) -> int:
        """Get maximum number of history entries to keep."""
        return self.config.get('history', {}).get('max_entries', 1000)
    
    def set_history_max_entries(self, max_entries: int) -> None:
        """Set maximum number of history entries."""
        if 'history' not in self.config:
            self.config['history'] = {}
        self.config['history']['max_entries'] = max_entries
        self.save_config()
    
    def get_history_auto_cleanup_days(self) -> int:
        """Get number of days after which old history entries are cleaned up."""
        return self.config.get('history', {}).get('auto_cleanup_days', 30)
    
    def set_history_auto_cleanup_days(self, days: int) -> None:
        """Set auto cleanup days for history entries."""
        if 'history' not in self.config:
            self.config['history'] = {}
        self.config['history']['auto_cleanup_days'] = days
        self.save_config()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self.config = self._get_default_config()
        self.save_config()