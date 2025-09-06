"""
Debug logging configuration for Lumos CLI integrations
"""

import os
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

class DebugLogger:
    """Centralized debug logging for integrations"""
    
    def __init__(self, name: str = "lumos_debug"):
        self.name = name
        self.logger = None
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup the debug logger with file and console output"""
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler (only for errors and warnings)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler - use the same directory as existing logger
        log_file = self._get_log_file_path()
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Log startup
        self.logger.info(f"Debug logging initialized. Log file: {log_file}")
    
    def _get_log_file_path(self) -> str:
        """Get the log file path for the current platform"""
        # Use the same logging directory as the existing logger system
        from .platform_utils import get_logs_directory, create_directory_if_not_exists
        
        log_dir = get_logs_directory()
        
        # Create directory if it doesn't exist
        if not create_directory_if_not_exists(log_dir):
            # Fallback to home directory if logs directory can't be created
            log_dir = Path.home() / '.lumos' / 'logs'
            log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file with daily format (same as existing logger)
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = log_dir / f'lumos-debug-{today}.log'
        
        return str(log_file)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        if self.logger:
            self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        if self.logger:
            self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        if self.logger:
            self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        if self.logger:
            self.logger.error(message, extra=kwargs)
    
    def log_function_call(self, func_name: str, args: dict = None, kwargs: dict = None):
        """Log function call with parameters"""
        args_str = f"args={args}" if args else ""
        kwargs_str = f"kwargs={kwargs}" if kwargs else ""
        params = ", ".join(filter(None, [args_str, kwargs_str]))
        self.debug(f"🔍 CALL: {func_name}({params})")
    
    def log_function_return(self, func_name: str, result: any = None):
        """Log function return value"""
        if result is not None:
            self.debug(f"🔍 RETURN: {func_name} -> {result}")
        else:
            self.debug(f"🔍 RETURN: {func_name} -> None")
    
    def log_url_construction(self, base_url: str, endpoint: str, params: dict = None):
        """Log URL construction details"""
        full_url = f"{base_url}{endpoint}"
        if params:
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url += f"?{param_str}"
        
        self.debug(f"🌐 URL CONSTRUCTION:")
        self.debug(f"   Base URL: {base_url}")
        self.debug(f"   Endpoint: {endpoint}")
        if params:
            self.debug(f"   Params: {params}")
        self.debug(f"   Full URL: {full_url}")

# Global debug logger instance
debug_logger = DebugLogger()

def get_debug_logger() -> DebugLogger:
    """Get the global debug logger instance"""
    return debug_logger
