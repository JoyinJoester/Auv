"""
Core file organization functionality.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict
import mimetypes
import re

from .config import ConfigManager
from .i18n import _


class FileOrganizer:
    """Main file organization engine."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        
        # Basic file type mappings (always enabled)
        self.basic_file_type_mappings = {
            'pdf': ['.pdf'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'],
            'document': ['.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
            'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a']
        }
        
        # Extended file type mappings (configurable)
        from .core_v2 import extended_file_type_mappings
        self.extended_file_type_mappings = extended_file_type_mappings
        
        # Special filename patterns
        self.special_patterns = {
            'screenshot': r'screenshot.*\.(png|jpg|jpeg)',
            'download': r'download.*',
        }
    
    def organize_files(self, file_types: Optional[List[str]] = None) -> int:
        """
        Organize files in the downloads folder.
        
        Args:
            file_types: List of file types to process. If None, process all types.
            
        Returns:
            Number of files moved.
        """
        source_path = Path(self.config.get_source_path())
        
        if not source_path.exists():
            raise FileNotFoundError(_('Source path does not exist: {}').format(source_path))
        
        moved_count = 0
        
        for file_path in source_path.iterdir():
            if file_path.is_file():
                target_path = self._get_target_path(file_path, file_types)
                if target_path:
                    try:
                        self._move_file(file_path, target_path)
                        moved_count += 1
                        print(_('Moved: {} -> {}').format(file_path.name, target_path))
                    except Exception as e:
                        print(_('Failed to move {}: {}').format(file_path.name, e))
        
        return moved_count
    
    def organize_single_file(self, file_path: Path) -> bool:
        """
        Organize a single file.
        
        Args:
            file_path: Path to the file to organize.
            
        Returns:
            True if file was moved, False otherwise.
        """
        if not file_path.exists() or not file_path.is_file():
            return False
        
        target_path = self._get_target_path(file_path)
        if target_path:
            try:
                self._move_file(file_path, target_path)
                print(_('Moved: {} -> {}').format(file_path.name, target_path))
                return True
            except Exception as e:
                print(_('Failed to move {}: {}').format(file_path.name, e))
        
        return False
    
    def _get_target_path(self, file_path: Path, allowed_types: Optional[List[str]] = None) -> Optional[Path]:
        """
        Determine the target path for a file.
        
        Args:
            file_path: Source file path.
            allowed_types: List of allowed file types. If None, all types are allowed.
            
        Returns:
            Target path or None if no rule matches.
        """
        file_extension = file_path.suffix.lower()
        filename = file_path.name.lower()
        
        # Check special patterns first
        if self._matches_special_pattern(filename, 'screenshot'):
            file_type = 'image'
        else:
            # Determine file type by extension
            file_type = self._get_file_type(file_extension)
        
        if not file_type:
            return None
        
        # Check if this file type is allowed
        if allowed_types and file_type not in allowed_types:
            return None
        
        # Get target directory for this file type
        target_dir = self.config.get_target_path(file_type)
        if not target_dir:
            return None
        
        target_dir = Path(target_dir)
        
        # Create target directory if it doesn't exist
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Handle filename conflicts
        target_file = target_dir / file_path.name
        counter = 1
        while target_file.exists():
            name_parts = file_path.stem, counter, file_path.suffix
            target_file = target_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
            counter += 1
        
        return target_file
    
    def _get_file_type(self, extension: str) -> Optional[str]:
        """Get file type category for an extension."""
        # Check basic file types first (always enabled)
        for file_type, extensions in self.basic_file_type_mappings.items():
            if extension in extensions:
                return file_type
        
        # Check extended file types (only if enabled)
        for file_type, extensions in self.extended_file_type_mappings.items():
            if extension in extensions and self.config.is_extended_type_enabled(file_type):
                return file_type
                
        return None
    
    def _matches_special_pattern(self, filename: str, pattern_name: str) -> bool:
        """Check if filename matches a special pattern."""
        if pattern_name in self.special_patterns:
            pattern = self.special_patterns[pattern_name]
            return bool(re.match(pattern, filename, re.IGNORECASE))
        return False
    
    def _move_file(self, source: Path, target: Path) -> None:
        """
        Move a file from source to target.
        
        Args:
            source: Source file path.
            target: Target file path.
        """
        try:
            shutil.move(str(source), str(target))
        except Exception as e:
            raise Exception(_('Cannot move file: {}').format(e))
    
    def get_supported_file_types(self) -> Dict[str, List[str]]:
        """Get dictionary of supported file types and their extensions."""
        result = self.basic_file_type_mappings.copy()
        
        # Add enabled extended file types
        for file_type, extensions in self.extended_file_type_mappings.items():
            if self.config.is_extended_type_enabled(file_type):
                result[file_type] = extensions
                
        return result