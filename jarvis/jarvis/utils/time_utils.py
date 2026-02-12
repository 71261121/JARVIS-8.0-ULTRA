"""
Time/Date Utilities
===================

Purpose: Time and date related helper functions.

Reason: Common time operations centralized for consistency.
"""

from datetime import datetime, date, timedelta
from typing import Optional


def format_duration(seconds: int) -> str:
    """
    Format seconds into human-readable duration.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string like "1h 30m" or "45m"
    
    Examples:
        format_duration(3600) -> "1h"
        format_duration(5400) -> "1h 30m"
        format_duration(2700) -> "45m"
    """
    if seconds < 0:
        return "0m"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0 and minutes > 0:
        return f"{hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{minutes}m"


def get_time_greeting() -> str:
    """
    Get greeting based on current time.
    
    Returns:
        Greeting like "Good morning", "Good afternoon", etc.
    
    Reason:
        Personalized greetings improve user experience.
    """
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 21:
        return "Good evening"
    else:
        return "Good night"


def calculate_days_remaining(target_date: str) -> int:
    """
    Calculate days remaining until target date.
    
    Args:
        target_date: Target date in YYYY-MM-DD format
    
    Returns:
        Number of days remaining (negative if passed)
    
    Reason:
        Used for countdown display and urgency.
    """
    try:
        target = datetime.strptime(target_date, "%Y-%m-%d").date()
        today = date.today()
        delta = target - today
        return delta.days
    except ValueError:
        return 0


def get_current_phase(day_number: int) -> int:
    """
    Get current phase based on day number.
    
    Args:
        day_number: Current day (1-75)
    
    Returns:
        Phase number (1-4)
    
    Phase breakdown:
        Phase 1: Days 1-25 (Foundation Rush)
        Phase 2: Days 26-50 (Intensive Practice)
        Phase 3: Days 51-70 (Mock Marathon)
        Phase 4: Days 71-75 (Final Revision)
    """
    if day_number <= 25:
        return 1
    elif day_number <= 50:
        return 2
    elif day_number <= 70:
        return 3
    else:
        return 4


def get_phase_name(phase: int) -> str:
    """Get phase name from phase number."""
    names = {
        1: "Foundation Rush",
        2: "Intensive Practice",
        3: "Mock Marathon",
        4: "Final Revision"
    }
    return names.get(phase, "Unknown")


def is_study_time() -> bool:
    """
    Check if current time is within study hours.
    
    Returns:
        True if between 8:00 and 22:00
    
    Reason:
        Used for focus mode auto-activation.
    """
    hour = datetime.now().hour
    return 8 <= hour < 22


def get_next_break_time(study_minutes: int) -> datetime:
    """
    Calculate next break time based on Pomodoro.
    
    Args:
        study_minutes: Minutes studied so far
    
    Returns:
        Datetime of next break
    """
    # Pomodoro: 25 min study + 5 min break
    # After 4 cycles: 15-20 min break
    cycle = (study_minutes // 25) % 4
    
    if cycle == 3:
        # Long break after 4th cycle
        break_minutes = 20
    else:
        break_minutes = 5
    
    return datetime.now() + timedelta(minutes=break_minutes)


def format_date_for_display(date_str: str) -> str:
    """
    Format date string for display.
    
    Args:
        date_str: Date in YYYY-MM-DD format
    
    Returns:
        Formatted date like "Monday, Jan 15"
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%A, %b %d")
    except ValueError:
        return date_str


def get_study_week(day_number: int) -> int:
    """
    Get study week number.
    
    Args:
        day_number: Current day (1-75)
    
    Returns:
        Week number (1-11)
    """
    return ((day_number - 1) // 7) + 1
