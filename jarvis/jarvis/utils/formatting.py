"""
Formatting Utilities
====================

Purpose: Data formatting for display.

Reason: Consistent formatting across the application.
"""

from typing import Optional


def format_xp(xp: int) -> str:
    """
    Format XP value for display.
    
    Args:
        xp: XP value
    
    Returns:
        Formatted string like "1,250 XP" or "12,500 XP"
    
    Examples:
        format_xp(1250) -> "1,250 XP"
        format_xp(-100) -> "-100 XP"
    """
    sign = "+" if xp > 0 else ""
    return f"{sign}{xp:,} XP"


def format_theta(theta: float) -> str:
    """
    Format IRT theta value for display.
    
    Args:
        theta: Theta value (-3 to +3)
    
    Returns:
        Formatted string like "+0.52" or "-1.35"
    
    Reason:
        Theta is the core ability metric in IRT.
    """
    sign = "+" if theta >= 0 else ""
    return f"{sign}{theta:.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format value as percentage.
    
    Args:
        value: Value between 0 and 1 (or 0 to 100)
        decimals: Number of decimal places
    
    Returns:
        Formatted string like "85.5%"
    
    Reason:
        Used for accuracy and progress display.
    """
    # Handle both 0-1 and 0-100 ranges
    if value <= 1:
        value *= 100
    
    return f"{value:.{decimals}f}%"


def format_score(correct: int, total: int) -> str:
    """
    Format score as fraction and percentage.
    
    Args:
        correct: Number correct
        total: Total questions
    
    Returns:
        Formatted string like "17/20 (85%)"
    """
    if total == 0:
        return "0/0 (0%)"
    
    percentage = (correct / total) * 100
    return f"{correct}/{total} ({percentage:.0f}%)"


def format_level(level: int, title: str = "") -> str:
    """
    Format level for display.
    
    Args:
        level: Level number
        title: Level title (optional)
    
    Returns:
        Formatted string like "Level 5: Learner"
    """
    if title:
        return f"Level {level}: {title}"
    return f"Level {level}"


def format_streak(days: int) -> str:
    """
    Format streak for display.
    
    Args:
        days: Number of days
    
    Returns:
        Formatted string like "12 days 🔥"
    """
    if days >= 30:
        return f"{days} days 🔥🔥🔥"
    elif days >= 14:
        return f"{days} days 🔥🔥"
    elif days >= 7:
        return f"{days} days 🔥"
    elif days > 0:
        return f"{days} days"
    else:
        return "0 days"


def format_ability_level(theta: float) -> str:
    """
    Convert theta to ability level description.
    
    Args:
        theta: IRT theta value
    
    Returns:
        Ability level like "Above Average", "Excellent", etc.
    
    Mapping:
        θ >= 2.0: Excellent
        θ >= 1.0: Above Average
        θ >= 0.0: Average
        θ >= -1.0: Below Average
        θ < -1.0: Needs Work
    """
    if theta >= 2.0:
        return "Excellent"
    elif theta >= 1.0:
        return "Above Average"
    elif theta >= 0.0:
        return "Average"
    elif theta >= -1.0:
        return "Below Average"
    else:
        return "Needs Work"


def format_time_ago(timestamp: str) -> str:
    """
    Format timestamp as relative time.
    
    Args:
        timestamp: ISO format timestamp
    
    Returns:
        String like "2 hours ago", "yesterday", etc.
    """
    from datetime import datetime, timedelta
    
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt
        
        if diff.days > 365:
            return f"{diff.days // 365} year{'s' if diff.days // 365 > 1 else ''} ago"
        elif diff.days > 30:
            return f"{diff.days // 30} month{'s' if diff.days // 30 > 1 else ''} ago"
        elif diff.days > 0:
            if diff.days == 1:
                return "yesterday"
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"
    except Exception:
        return timestamp


def format_progress_bar(current: int, total: int, width: int = 20) -> str:
    """
    Create text progress bar.
    
    Args:
        current: Current progress
        total: Maximum value
        width: Bar width in characters
    
    Returns:
        Progress bar string like "████████░░░░ 65%"
    """
    if total == 0:
        return "░" * width + " 0%"
    
    percentage = min(100, (current / total) * 100)
    filled = int((percentage / 100) * width)
    empty = width - filled
    
    bar = "█" * filled + "░" * empty
    return f"{bar} {percentage:.0f}%"
