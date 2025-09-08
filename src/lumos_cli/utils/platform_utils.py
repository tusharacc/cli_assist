"""
Cross-platform utilities for Windows/macOS/Linux compatibility
"""

import os
import sys
import platform
from pathlib import Path
from typing import List, Optional, Dict

def get_platform() -> str:
    """Get the current platform"""
    return platform.system().lower()

def is_windows() -> bool:
    """Check if running on Windows"""
    return get_platform() == 'windows'

def is_macos() -> bool:
    """Check if running on macOS"""
    return get_platform() == 'darwin'

def is_linux() -> bool:
    """Check if running on Linux"""
    return get_platform() == 'linux'

def get_home_directory() -> Path:
    """Get user home directory in a cross-platform way"""
    return Path.home()

def get_config_directory() -> Path:
    """Get application config directory - standardized across all platforms"""
    # Standardized path: ~/.lumos/.config/ for all operating systems
    config_dir = Path.home() / ".lumos" / ".config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def get_logs_directory() -> Path:
    """Get logs directory following platform conventions"""
    if is_windows():
        # Windows: %LOCALAPPDATA%/Lumos/Logs
        localappdata = os.getenv('LOCALAPPDATA')
        if localappdata:
            return Path(localappdata) / "Lumos" / "Logs"
        else:
            return get_config_directory() / "logs"
    elif is_macos():
        # macOS: ~/Library/Logs/Lumos
        return Path.home() / "Library" / "Logs" / "Lumos"
    else:
        # Linux: ~/.local/share/lumos/logs or ~/.lumos/logs
        xdg_data = os.getenv('XDG_DATA_HOME')
        if xdg_data:
            return Path(xdg_data) / "lumos" / "logs"
        else:
            return Path.home() / ".local" / "share" / "lumos" / "logs"

def get_cache_directory() -> Path:
    """Get cache directory following platform conventions"""
    if is_windows():
        # Windows: %LOCALAPPDATA%/Lumos/Cache
        localappdata = os.getenv('LOCALAPPDATA')
        if localappdata:
            return Path(localappdata) / "Lumos" / "Cache"
        else:
            return get_config_directory() / "cache"
    elif is_macos():
        # macOS: ~/Library/Caches/Lumos
        return Path.home() / "Library" / "Caches" / "Lumos"
    else:
        # Linux: ~/.cache/lumos
        xdg_cache = os.getenv('XDG_CACHE_HOME')
        if xdg_cache:
            return Path(xdg_cache) / "lumos"
        else:
            return Path.home() / ".cache" / "lumos"

def get_env_file_locations() -> List[Path]:
    """Get potential .env file locations in search order"""
    locations = [
        Path(".env"),
        Path(".env.local"),
    ]
    
    # Add home directory .env (different locations per platform)
    if is_windows():
        # Windows users typically don't use ~/.env, but support it
        locations.extend([
            Path.home() / ".env",
            Path.home() / "Documents" / ".env"
        ])
    else:
        # Unix-like systems
        locations.append(Path.home() / ".env")
    
    return locations

def get_ollama_executable_locations() -> List[str]:
    """Get potential Ollama executable locations per platform"""
    if is_windows():
        return [
            "ollama.exe",  # In PATH
            str(Path.home() / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe"),
            "C:\\Program Files\\Ollama\\ollama.exe",
            "C:\\Program Files (x86)\\Ollama\\ollama.exe"
        ]
    elif is_macos():
        return [
            "ollama",  # In PATH
            "/usr/local/bin/ollama",
            "/opt/homebrew/bin/ollama",
            "/Applications/Ollama.app/Contents/MacOS/ollama"
        ]
    else:  # Linux
        return [
            "ollama",  # In PATH  
            "/usr/local/bin/ollama",
            "/usr/bin/ollama",
            str(Path.home() / ".local" / "bin" / "ollama")
        ]

def check_ollama_installed() -> bool:
    """Check if Ollama is installed on the system"""
    import shutil
    
    # First check if it's in PATH
    if shutil.which("ollama" + (".exe" if is_windows() else "")):
        return True
    
    # Then check platform-specific locations
    for location in get_ollama_executable_locations():
        if Path(location).exists():
            return True
    
    return False

def get_default_ollama_url() -> str:
    """Get default Ollama URL (same across platforms)"""
    return "http://localhost:11434"

def get_shell_command_for_platform() -> List[str]:
    """Get the appropriate shell command for the platform"""
    if is_windows():
        return ["cmd", "/c"]  # Or ["powershell", "-Command"] for PowerShell
    else:
        return ["sh", "-c"]

def normalize_path_separators(path: str) -> str:
    """Normalize path separators for the current platform"""
    return str(Path(path))

def get_python_executable() -> str:
    """Get the Python executable path"""
    return sys.executable

def create_directory_if_not_exists(directory: Path) -> bool:
    """Create directory if it doesn't exist, return True if successful"""
    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError):
        return False

def get_platform_info() -> Dict[str, str]:
    """Get comprehensive platform information"""
    return {
        "platform": get_platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": sys.version.split()[0],
        "home_dir": str(get_home_directory()),
        "config_dir": str(get_config_directory()),
        "logs_dir": str(get_logs_directory()),
        "cache_dir": str(get_cache_directory()),
        "is_windows": str(is_windows()),
        "is_macos": str(is_macos()),
        "is_linux": str(is_linux()),
    }