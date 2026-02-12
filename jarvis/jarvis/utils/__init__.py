"""
JARVIS Utils Module
===================

Purpose: Utility functions used across JARVIS.

Components:
- Time/date helpers
- File operations
- Data formatting
- Validation functions
- Constants

Reason for separation:
- Keep code DRY (Don't Repeat Yourself)
- Common functions in one place
- Easy testing
"""

from .time_utils import format_duration, get_time_greeting, calculate_days_remaining
from .file_utils import ensure_dir, backup_file, restore_backup
from .formatting import format_xp, format_theta, format_percentage
from .validation import validate_answer, validate_date

__all__ = [
    "format_duration",
    "get_time_greeting",
    "calculate_days_remaining",
    "ensure_dir",
    "backup_file",
    "restore_backup",
    "format_xp",
    "format_theta",
    "format_percentage",
    "validate_answer",
    "validate_date",
]
