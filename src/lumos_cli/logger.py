"""
Persistent logging system for Lumos CLI debugging
"""

import os
import time
from pathlib import Path
from datetime import datetime
from typing import Optional
import threading
from .platform_utils import get_logs_directory, create_directory_if_not_exists

# Global logger instance
_logger_instance: Optional['LumosLogger'] = None
_logger_lock = threading.Lock()

class LumosLogger:
    """Thread-safe persistent logger for Lumos CLI"""
    
    def __init__(self, log_dir: Optional[str] = None):
        # Use platform-appropriate logs directory
        self.log_dir = Path(log_dir) if log_dir else get_logs_directory()
        
        # Ensure logs directory exists with proper error handling
        if not create_directory_if_not_exists(self.log_dir):
            # Fallback to home directory if logs directory can't be created
            self.log_dir = Path.home() / ".lumos" / "logs"
            create_directory_if_not_exists(self.log_dir)
        
        # Create daily log file
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"lumos-{today}.log"
        self.debug_file = self.log_dir / f"lumos-debug-{today}.log"
        
        # Ensure files exist
        self.log_file.touch()
        self.debug_file.touch()
        
        # Write startup marker
        self._write_log("INFO", "=== Lumos CLI Session Started ===", to_debug=True)
    
    def _write_log(self, level: str, message: str, to_debug: bool = False):
        """Write log entry with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        try:
            # Write to main log
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            # Also write to debug log if requested
            if to_debug:
                with open(self.debug_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                    
        except Exception as e:
            # Fail silently to avoid breaking the CLI
            pass
    
    def debug(self, message: str):
        """Log debug message"""
        self._write_log("DEBUG", message, to_debug=True)
    
    def info(self, message: str):
        """Log info message"""  
        self._write_log("INFO", message)
    
    def warning(self, message: str):
        """Log warning message"""
        self._write_log("WARNING", message, to_debug=True)
    
    def error(self, message: str):
        """Log error message"""
        self._write_log("ERROR", message, to_debug=True)
    
    def get_log_files(self) -> dict:
        """Get paths to current log files"""
        return {
            "main_log": str(self.log_file),
            "debug_log": str(self.debug_file),
            "log_dir": str(self.log_dir)
        }
    
    def get_recent_logs(self, lines: int = 50, debug_only: bool = False) -> str:
        """Get recent log entries"""
        log_file = self.debug_file if debug_only else self.log_file
        
        try:
            if not log_file.exists():
                return "No logs available"
                
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return ''.join(recent_lines)
                
        except Exception as e:
            return f"Error reading logs: {e}"

def get_logger() -> LumosLogger:
    """Get or create global logger instance"""
    global _logger_instance
    
    with _logger_lock:
        if _logger_instance is None:
            _logger_instance = LumosLogger()
        return _logger_instance

def log_debug(message: str):
    """Quick debug logging function"""
    logger = get_logger()
    logger.debug(message)

def log_info(message: str):
    """Quick info logging function"""
    logger = get_logger()
    logger.info(message)

def log_warning(message: str):
    """Quick warning logging function"""
    logger = get_logger()
    logger.warning(message)

def log_error(message: str):
    """Quick error logging function"""
    logger = get_logger()
    logger.error(message)

def show_log_info():
    """Show information about log files"""
    logger = get_logger()
    files = logger.get_log_files()
    
    print("📋 Lumos CLI Log Files:")
    print(f"   Main Log: {files['main_log']}")
    print(f"   Debug Log: {files['debug_log']}")
    print(f"   Log Directory: {files['log_dir']}")
    
    # Show recent debug entries
    recent = logger.get_recent_logs(lines=10, debug_only=True)
    if recent.strip():
        print(f"\n🔍 Recent Debug Entries:")
        for line in recent.strip().split('\n'):
            print(f"   {line}")
    else:
        print(f"\n🔍 No recent debug entries")

def cleanup_old_logs(days: int = 7):
    """Clean up log files older than specified days"""
    logger = get_logger()
    log_dir = Path(logger.log_dir)
    
    cutoff_time = time.time() - (days * 24 * 60 * 60)
    cleaned = 0
    
    try:
        for log_file in log_dir.glob("lumos-*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                cleaned += 1
        
        if cleaned > 0:
            log_info(f"Cleaned up {cleaned} old log files")
            
    except Exception as e:
        log_error(f"Error cleaning up logs: {e}")