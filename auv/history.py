# -*- coding: utf-8 -*-
"""
History Management Module for AUV
Provides operation logging, timeline management, and rollback functionality
"""

import json
import os
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from .i18n import _


@dataclass
class HistoryEntry:
    """Single history entry representing one operation"""
    timeline_id: str  # Unique timeline identifier
    timestamp: float  # Unix timestamp
    operation_type: str  # Type of operation (organize, config_change, etc.)
    operation_data: Dict[str, Any]  # Operation-specific data
    files_moved: List[Dict[str, str]]  # List of file movements {source, target}
    config_changes: Dict[str, Any]  # Configuration changes made
    reversible: bool  # Whether this operation can be reversed
    description: str  # Human-readable description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoryEntry':
        """Create from dictionary"""
        return cls(**data)
    
    def get_formatted_time(self) -> str:
        """Get formatted timestamp"""
        dt = datetime.fromtimestamp(self.timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")


class HistoryManager:
    """Manages operation history and provides rollback functionality"""
    
    def __init__(self, config_dir: str = None):
        """Initialize history manager"""
        if config_dir is None:
            config_dir = os.path.expanduser("~/.auv")
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.history_file = self.config_dir / "history.json"
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Load existing history
        self._history: List[HistoryEntry] = self._load_history()
        self._timeline_counter = self._get_next_timeline_id()
    
    def _load_history(self) -> List[HistoryEntry]:
        """Load history from file"""
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [HistoryEntry.from_dict(entry) for entry in data]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Warning: Could not load history file: {e}")
            return []
    
    def _save_history(self):
        """Save history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([entry.to_dict() for entry in self._history], f, 
                         indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def _get_next_timeline_id(self) -> int:
        """Get next timeline ID"""
        if not self._history:
            return 1
        
        max_id = 0
        for entry in self._history:
            try:
                timeline_id = int(entry.timeline_id.split('T')[1])
                max_id = max(max_id, timeline_id)
            except (ValueError, IndexError):
                continue
        
        return max_id + 1
    
    def create_timeline_id(self) -> str:
        """Create new timeline ID"""
        timeline_id = f"T{self._timeline_counter}"
        self._timeline_counter += 1
        return timeline_id
    
    def record_operation(self, 
                        operation_type: str,
                        description: str,
                        operation_data: Dict[str, Any] = None,
                        files_moved: List[Dict[str, str]] = None,
                        config_changes: Dict[str, Any] = None,
                        reversible: bool = True) -> str:
        """Record a new operation in history"""
        
        timeline_id = self.create_timeline_id()
        
        entry = HistoryEntry(
            timeline_id=timeline_id,
            timestamp=time.time(),
            operation_type=operation_type,
            operation_data=operation_data or {},
            files_moved=files_moved or [],
            config_changes=config_changes or {},
            reversible=reversible,
            description=description
        )
        
        self._history.append(entry)
        self._save_history()
        
        return timeline_id
    
    def get_history(self, limit: int = None) -> List[HistoryEntry]:
        """Get operation history"""
        history = sorted(self._history, key=lambda x: x.timestamp, reverse=True)
        if limit:
            return history[:limit]
        return history
    
    def get_entry_by_timeline(self, timeline_id: str) -> Optional[HistoryEntry]:
        """Get specific entry by timeline ID"""
        for entry in self._history:
            if entry.timeline_id == timeline_id:
                return entry
        return None
    
    def get_last_entry(self) -> Optional[HistoryEntry]:
        """Get the most recent entry"""
        if not self._history:
            return None
        return max(self._history, key=lambda x: x.timestamp)
    
    def can_rollback_to(self, timeline_id: str) -> Tuple[bool, str]:
        """Check if we can rollback to specific timeline"""
        entry = self.get_entry_by_timeline(timeline_id)
        if not entry:
            return False, f"Timeline {timeline_id} not found"
        
        if not entry.reversible:
            return False, f"Operation {timeline_id} is not reversible"
        
        # Check if all subsequent operations are also reversible
        later_entries = [e for e in self._history if e.timestamp > entry.timestamp]
        for later_entry in later_entries:
            if not later_entry.reversible:
                return False, f"Cannot rollback past non-reversible operation {later_entry.timeline_id}"
        
        return True, ""
    
    def rollback_to_timeline(self, timeline_id: str) -> Tuple[bool, str]:
        """Rollback to specific timeline"""
        can_rollback, reason = self.can_rollback_to(timeline_id)
        if not can_rollback:
            return False, reason
        
        target_entry = self.get_entry_by_timeline(timeline_id)
        if not target_entry:
            return False, f"Timeline {timeline_id} not found"
        
        # Get all entries after the target
        entries_to_reverse = sorted(
            [e for e in self._history if e.timestamp > target_entry.timestamp],
            key=lambda x: x.timestamp,
            reverse=True  # Reverse in reverse chronological order
        )
        
        # Perform rollback operations
        rollback_success = True
        rollback_errors = []
        
        for entry in entries_to_reverse:
            try:
                self._reverse_operation(entry)
            except Exception as e:
                rollback_success = False
                rollback_errors.append(f"Failed to reverse {entry.timeline_id}: {e}")
        
        if rollback_success:
            # Remove reversed entries from history
            self._history = [e for e in self._history if e.timestamp <= target_entry.timestamp]
            self._save_history()
            
            # Record the rollback operation
            self.record_operation(
                operation_type="rollback",
                description=f"Rolled back to timeline {timeline_id}",
                operation_data={"target_timeline": timeline_id},
                reversible=False  # Rollbacks themselves are not reversible
            )
            
            return True, f"Successfully rolled back to timeline {timeline_id}"
        else:
            return False, f"Rollback failed: {'; '.join(rollback_errors)}"
    
    def rollback_last_operation(self) -> Tuple[bool, str]:
        """Rollback the last operation"""
        last_entry = self.get_last_entry()
        if not last_entry:
            return False, "No operations to rollback"
        
        if not last_entry.reversible:
            return False, f"Last operation ({last_entry.timeline_id}) is not reversible"
        
        try:
            self._reverse_operation(last_entry)
            self._history.remove(last_entry)
            self._save_history()
            
            return True, f"Successfully rolled back operation {last_entry.timeline_id}"
        except Exception as e:
            return False, f"Failed to rollback: {e}"
    
    def _reverse_operation(self, entry: HistoryEntry):
        """Reverse a specific operation"""
        if entry.operation_type == "organize_files":
            self._reverse_file_moves(entry.files_moved)
        elif entry.operation_type == "config_change":
            self._reverse_config_changes(entry.config_changes)
        elif entry.operation_type == "custom_organize":
            self._reverse_file_moves(entry.files_moved)
        else:
            raise ValueError(f"Unknown operation type: {entry.operation_type}")
    
    def _reverse_file_moves(self, files_moved: List[Dict[str, str]]):
        """Reverse file movements"""
        for file_move in reversed(files_moved):  # Reverse in reverse order
            source = file_move.get("source")
            target = file_move.get("target")
            
            if not source or not target:
                continue
            
            target_path = Path(target)
            source_path = Path(source)
            
            # Only move back if target file exists and source directory exists
            if target_path.exists():
                # Ensure source directory exists
                source_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file back
                shutil.move(str(target_path), str(source_path))
    
    def _reverse_config_changes(self, config_changes: Dict[str, Any]):
        """Reverse configuration changes"""
        # This would require integration with config manager
        # For now, we'll just log that config changes cannot be automatically reversed
        raise NotImplementedError("Config change reversal requires manual intervention")
    
    def display_history(self, limit: int = 20) -> str:
        """Generate formatted history display"""
        history = self.get_history(limit)
        if not history:
            return _("no_history_found")
        
        output = [_("operation_history")]
        output.append("=" * 50)
        
        for entry in history:
            status = "✓" if entry.reversible else "✗"
            output.append(f"{status} {entry.timeline_id} | {entry.get_formatted_time()}")
            output.append(f"   Type: {entry.operation_type}")
            output.append(f"   Description: {entry.description}")
            
            if entry.files_moved:
                output.append(f"   Files moved: {len(entry.files_moved)}")
            
            if entry.config_changes:
                output.append(f"   Config changes: {len(entry.config_changes)}")
            
            output.append("")
        
        output.append(f"Showing {len(history)} recent operations")
        output.append("Use 'auv return <timeline_id>' to rollback to specific point")
        output.append("Use 'auv return' to rollback last operation")
        
        return "\n".join(output)
    
    def cleanup_old_history(self, days: int = 30):
        """Remove history entries older than specified days"""
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        original_count = len(self._history)
        
        self._history = [entry for entry in self._history if entry.timestamp > cutoff_time]
        
        if len(self._history) < original_count:
            self._save_history()
            return original_count - len(self._history)
        
        return 0


# Global history manager instance
_history_manager = None


def get_history_manager() -> HistoryManager:
    """Get global history manager instance"""
    global _history_manager
    if _history_manager is None:
        _history_manager = HistoryManager()
    return _history_manager