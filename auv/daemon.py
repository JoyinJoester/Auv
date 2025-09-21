"""
Daemon mode functionality for AUV.
"""

import os
import sys
import time
import signal
import psutil
from pathlib import Path
from typing import Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .config import ConfigManager
from .core import FileOrganizer
from .i18n import _


class FileHandler(FileSystemEventHandler):
    """File system event handler for monitoring Downloads folder."""
    
    def __init__(self, organizer: FileOrganizer):
        self.organizer = organizer
        super().__init__()
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            print(_('File detected: {}').format(file_path.name))
            
            # Wait a bit to ensure file is fully written
            time.sleep(1)
            
            # Try to organize the file
            if self.organizer.organize_single_file(file_path):
                print(_('Organized: {} -> {}').format(
                    file_path.name,
                    self.organizer._get_target_path(file_path)
                ))
            else:
                print(_('Skipped: {}').format(file_path.name))


class DaemonManager:
    """Manages daemon mode for AUV."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.pid_file = self._get_pid_file()
        self.observer = None
    
    def _get_pid_file(self) -> Path:
        """Get PID file path."""
        if os.name == 'nt':  # Windows
            pid_dir = Path(os.environ.get('TEMP', ''))
        else:  # Unix-like
            pid_dir = Path('/tmp')
        
        return pid_dir / 'auv_daemon.pid'
    
    def is_running(self) -> bool:
        """Check if daemon is already running."""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is still running
            return psutil.pid_exists(pid)
        except (ValueError, IOError):
            # Invalid PID file
            self._remove_pid_file()
            return False
    
    def start(self) -> None:
        """Start daemon mode."""
        if self.is_running():
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            print(_('AUV daemon is already running (PID: {})').format(pid))
            return
        
        try:
            if os.name != 'nt':  # Unix-like systems
                self._daemonize()
            
            self._run_daemon()
        except Exception as e:
            print(_('Failed to start daemon: {}').format(e))
            sys.exit(1)
    
    def stop(self) -> None:
        """Stop daemon mode."""
        if not self.is_running():
            print(_('AUV daemon is not running'))
            return
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Send termination signal
            if os.name == 'nt':  # Windows
                import subprocess
                subprocess.run(['taskkill', '/PID', str(pid), '/F'], check=True)
            else:  # Unix-like
                os.kill(pid, signal.SIGTERM)
            
            self._remove_pid_file()
            print(_('AUV daemon stopped'))
        except Exception as e:
            print(_('Failed to stop daemon: {}').format(e))
    
    def _daemonize(self) -> None:
        """Daemonize the process (Unix-like systems only)."""
        try:
            # First fork
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # Exit parent
        except OSError as e:
            print(f'Fork failed: {e}')
            sys.exit(1)
        
        # Decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)
        
        # Second fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # Exit second parent
        except OSError as e:
            print(f'Fork failed: {e}')
            sys.exit(1)
        
        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        
        with open(os.devnull, 'r') as si:
            os.dup2(si.fileno(), sys.stdin.fileno())
        with open(os.devnull, 'w') as so:
            os.dup2(so.fileno(), sys.stdout.fileno())
        with open(os.devnull, 'w') as se:
            os.dup2(se.fileno(), sys.stderr.fileno())
    
    def _run_daemon(self) -> None:
        """Run the daemon."""
        # Write PID file
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        print(_('AUV daemon started with PID: {}').format(os.getpid()))
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Create file organizer and handler
        organizer = FileOrganizer(self.config)
        handler = FileHandler(organizer)
        
        # Set up file system observer
        self.observer = Observer()
        watch_path = self.config.get_source_path()
        recursive = self.config.should_watch_subdirs()
        
        self.observer.schedule(handler, watch_path, recursive=recursive)
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self._cleanup()
    
    def _signal_handler(self, signum, frame):
        """Handle termination signals."""
        self._cleanup()
        sys.exit(0)
    
    def _cleanup(self) -> None:
        """Clean up daemon resources."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        self._remove_pid_file()
    
    def _remove_pid_file(self) -> None:
        """Remove PID file."""
        if self.pid_file.exists():
            try:
                self.pid_file.unlink()
            except IOError:
                pass