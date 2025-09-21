"""
Enhanced flexible file organization functionality.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict
import mimetypes
import re

from .config import ConfigManager
from .i18n import _
from .history import get_history_manager


# Extended file type mappings (exported for use in other modules)
extended_file_type_mappings = {
    'installer': [
        # Windows
        '.exe', '.msi', '.msix', '.appx', '.appxbundle',
        # macOS
        '.dmg', '.pkg', '.mpkg',
        # Linux
        '.deb', '.rpm', '.snap', '.flatpak', '.appimage',
        # Cross-platform
        '.jar', '.app'
    ],
    'archive': [
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz',
        '.tar.gz', '.tar.bz2', '.tar.xz', '.tgz', '.tbz2',
        '.iso', '.img', '.cab', '.ace', '.lz', '.lzma'
    ],
    'code': [
        # Web development
        '.html', '.htm', '.css', '.js', '.ts', '.jsx', '.tsx',
        '.php', '.asp', '.aspx', '.jsp',
        # Programming languages
        '.py', '.java', '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp',
        '.cs', '.vb', '.go', '.rs', '.swift', '.kt',
        '.rb', '.pl', '.lua', '.r', '.m', '.scala',
        # Data and config
        '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg',
        '.sql', '.db', '.sqlite', '.sqlite3',
        # Shell and scripts
        '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
        # Build and project files
        '.makefile', '.cmake', '.gradle', '.maven', '.sbt'
    ],
    'font': [
        '.ttf', '.otf', '.woff', '.woff2', '.eot',
        '.pfb', '.pfm', '.afm', '.bdf', '.pcf'
    ],
    'ebook': [
        '.epub', '.mobi', '.azw', '.azw3', '.fb2', '.lit',
        '.pdb', '.prc', '.djvu', '.chm'
    ]
}


class FlexibleFileOrganizer:
    """Enhanced file organization engine with flexible path handling."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        
        # Basic file type mappings (always enabled)
        self.file_type_mappings = {
            'pdf': ['.pdf'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'],
            'document': ['.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
            'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a']
        }
        
        # Extended file type mappings (optional, disabled by default)
        self.extended_file_type_mappings = extended_file_type_mappings
        
        # Special filename patterns
        self.special_patterns = {
            'screenshot': r'screenshot.*\.(png|jpg|jpeg)',
            'download': r'download.*',
        }
    
    def get_enabled_file_types(self) -> Dict[str, List[str]]:
        """Get currently enabled file type mappings."""
        enabled_mappings = self.file_type_mappings.copy()
        
        # Check which extended types are enabled
        for extended_type, extensions in self.extended_file_type_mappings.items():
            if self.config.is_extended_type_enabled(extended_type):
                enabled_mappings[extended_type] = extensions
                
        return enabled_mappings
    
    def organize_files_by_type(self, source_path: Path, file_type: str, target_path: Path) -> int:
        """
        Organize files of specific type from source to target path.
        
        Args:
            source_path: Source directory path
            file_type: Type of files to organize (pdf, image, etc.)
            target_path: Target directory path
            
        Returns:
            Number of files moved
        """
        if not source_path.exists():
            raise FileNotFoundError(_('源路径不存在: {}').format(source_path))
        
        moved_count = 0
        files_moved = []  # Track moved files for history
        
        # Get enabled file type mappings
        enabled_mappings = self.get_enabled_file_types()
        extensions = enabled_mappings.get(file_type, [])
        
        if not extensions:
            print(_('不支持的文件类型: {}').format(file_type))
            return 0
        
        # Create target directory if it doesn't exist
        target_path.mkdir(parents=True, exist_ok=True)
        
        for file_path in source_path.iterdir():
            if file_path.is_file():
                if self._should_process_file(file_path, file_type, extensions):
                    try:
                        target_file = self._get_unique_target_path(target_path, file_path.name)
                        
                        # Record file movement for history
                        file_move_record = {
                            "source": str(file_path),
                            "target": str(target_file)
                        }
                        
                        self._move_file(file_path, target_file)
                        files_moved.append(file_move_record)
                        print(_('已移动: {} -> {}').format(file_path.name, target_file))
                        moved_count += 1
                    except Exception as e:
                        print(_('移动失败 {}: {}').format(file_path.name, e))
        
        # Record operation in history if any files were moved
        if files_moved and self.config.is_history_enabled():
            history_manager = get_history_manager()
            history_manager.record_operation(
                operation_type="organize_files",
                description=f"Organized {moved_count} {file_type} files from {source_path} to {target_path}",
                operation_data={
                    "source_path": str(source_path),
                    "target_path": str(target_path),
                    "file_type": file_type,
                    "file_count": moved_count
                },
                files_moved=files_moved,
                reversible=True
            )
        
        return moved_count
    
    def organize_files_by_extensions(self, source_path: Path, extensions: List[str], target_path: Path) -> int:
        """Organize files by specific extensions (for custom commands)."""
        moved_count = 0
        files_moved = []  # Track moved files for history
        
        if not source_path.exists():
            print(_('源路径不存在: {}').format(source_path))
            return 0
        
        # 确保目标目录存在
        target_path.mkdir(parents=True, exist_ok=True)
        
        for file_path in source_path.iterdir():
            if file_path.is_file():
                file_extension = file_path.suffix.lower()
                # 检查复合扩展名
                full_suffix = self._get_full_suffix(file_path)
                
                if file_extension in extensions or full_suffix in extensions:
                    try:
                        target_file = self._get_unique_target_path(target_path, file_path.name)
                        
                        # Record file movement for history
                        file_move_record = {
                            "source": str(file_path),
                            "target": str(target_file)
                        }
                        
                        self._move_file(file_path, target_file)
                        files_moved.append(file_move_record)
                        moved_count += 1
                    except Exception as e:
                        print(_('移动失败 {}: {}').format(file_path.name, e))
        
        # Record operation in history if any files were moved
        if files_moved and self.config.is_history_enabled():
            history_manager = get_history_manager()
            history_manager.record_operation(
                operation_type="custom_organize",
                description=f"Organized {moved_count} files with extensions {extensions} from {source_path} to {target_path}",
                operation_data={
                    "source_path": str(source_path),
                    "target_path": str(target_path),
                    "extensions": extensions,
                    "file_count": moved_count
                },
                files_moved=files_moved,
                reversible=True
            )
        
        return moved_count
    
    def _should_process_file(self, file_path: Path, file_type: str, extensions: List[str]) -> bool:
        """Check if file should be processed based on type and patterns."""
        file_extension = file_path.suffix.lower()
        filename = file_path.name.lower()
        
        # Check special patterns first
        if file_type == 'image' and self._matches_special_pattern(filename, 'screenshot'):
            return True
        
        # Check for compound extensions like .tar.gz
        full_suffix = self._get_full_suffix(file_path)
        
        # Check by extension (both simple and compound)
        return file_extension in extensions or full_suffix in extensions
    
    def _get_full_suffix(self, file_path: Path) -> str:
        """Get the full suffix including compound extensions like .tar.gz."""
        name = file_path.name.lower()
        
        # Check for common compound extensions
        compound_extensions = [
            '.tar.gz', '.tar.bz2', '.tar.xz', '.tar.lzma',
            '.tar.Z', '.tar.lz', '.tar.lzo'
        ]
        
        for ext in compound_extensions:
            if name.endswith(ext):
                return ext
        
        return file_path.suffix.lower()
    
    def _matches_special_pattern(self, filename: str, pattern_name: str) -> bool:
        """Check if filename matches a special pattern."""
        if pattern_name in self.special_patterns:
            pattern = self.special_patterns[pattern_name]
            return bool(re.match(pattern, filename, re.IGNORECASE))
        return False
    
    def _get_unique_target_path(self, target_dir: Path, filename: str) -> Path:
        """Get unique target file path to avoid conflicts."""
        target_file = target_dir / filename
        counter = 1
        original_stem = Path(filename).stem
        original_suffix = Path(filename).suffix
        
        while target_file.exists():
            new_filename = f"{original_stem}_{counter}{original_suffix}"
            target_file = target_dir / new_filename
            counter += 1
        
        return target_file
    
    def _move_file(self, source: Path, target: Path) -> None:
        """
        Move a file from source to target.
        
        Args:
            source: Source file path
            target: Target file path
        """
        try:
            shutil.move(str(source), str(target))
        except Exception as e:
            raise Exception(_('无法移动文件: {}').format(e))
    
    def get_supported_file_types(self) -> Dict[str, List[str]]:
        """Get dictionary of supported file types and their extensions."""
        return self.file_type_mappings.copy()
    
    def organize_all_files(self, source_path: Path) -> int:
        """Organize all supported files from source path using default targets."""
        total_moved = 0
        
        for file_type in self.file_type_mappings.keys():
            default_target = self.config.get_target_path(file_type)
            if default_target:
                target_path = Path(default_target)
                moved = self.organize_files_by_type(source_path, file_type, target_path)
                total_moved += moved
        
        return total_moved