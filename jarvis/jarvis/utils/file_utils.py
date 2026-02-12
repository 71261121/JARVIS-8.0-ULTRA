"""
File Utilities
==============

Purpose: File operation helpers.

Reason: Centralized file operations for safety and consistency.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional


def ensure_dir(path: str) -> Path:
    """
    Ensure directory exists, create if not.
    
    Args:
        path: Directory path
    
    Returns:
        Path object
    
    Reason:
        Prevents "directory not found" errors.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def backup_file(source: str, backup_dir: str = "data/backup/") -> str:
    """
    Create backup of a file.
    
    Args:
        source: Path to source file
        backup_dir: Directory for backups
    
    Returns:
        Path to backup file
    
    Raises:
        FileNotFoundError: If source file doesn't exist
    
    Reason:
        Data loss prevention - critical for user progress.
    """
    source_path = Path(source)
    
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source}")
    
    # Ensure backup directory exists
    backup_path = ensure_dir(backup_dir)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
    backup_file = backup_path / backup_name
    
    # Copy file
    shutil.copy2(source_path, backup_file)
    
    return str(backup_file)


def restore_backup(backup_file: str, target: str) -> bool:
    """
    Restore file from backup.
    
    Args:
        backup_file: Path to backup file
        target: Path to restore to
    
    Returns:
        True if successful
    
    Reason:
        Recovery from data corruption or accidental deletion.
    """
    backup_path = Path(backup_file)
    target_path = Path(target)
    
    if not backup_path.exists():
        return False
    
    # Ensure target directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy backup to target
    shutil.copy2(backup_path, target_path)
    
    return True


def get_file_size(path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        path: File path
    
    Returns:
        Size in bytes, 0 if not found
    """
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


def format_file_size(bytes_size: int) -> str:
    """
    Format file size for display.
    
    Args:
        bytes_size: Size in bytes
    
    Returns:
        Formatted string like "1.5 MB"
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def clean_old_backups(backup_dir: str, keep_count: int = 10) -> int:
    """
    Remove old backups, keeping only most recent.
    
    Args:
        backup_dir: Directory containing backups
        keep_count: Number of backups to keep
    
    Returns:
        Number of files removed
    
    Reason:
        Prevent disk space issues from accumulating backups.
    """
    backup_path = Path(backup_dir)
    
    if not backup_path.exists():
        return 0
    
    # Get all backup files sorted by modification time (newest first)
    files = sorted(
        backup_path.iterdir(),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    
    # Remove old files
    removed = 0
    for file in files[keep_count:]:
        file.unlink()
        removed += 1
    
    return removed


def write_json(path: str, data: dict) -> bool:
    """
    Write data to JSON file.
    
    Args:
        path: File path
        data: Dictionary to write
    
    Returns:
        True if successful
    """
    try:
        import json
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return True
    except Exception:
        return False


def read_json(path: str) -> Optional[dict]:
    """
    Read data from JSON file.
    
    Args:
        path: File path
    
    Returns:
        Dictionary or None if failed
    """
    try:
        import json
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return None
