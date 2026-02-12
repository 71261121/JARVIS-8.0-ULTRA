"""
Validation Utilities
====================

Purpose: Input validation helpers.

Reason: Prevent invalid data from entering the system.
"""

import re
from datetime import datetime
from typing import Optional, Tuple, List


def validate_answer(answer: str) -> Tuple[bool, Optional[str]]:
    """
    Validate MCQ answer.
    
    Args:
        answer: User's answer (A, B, C, D)
    
    Returns:
        Tuple of (is_valid, normalized_answer)
    
    Reason:
        Ensure answers are consistent (uppercase, single letter).
    """
    if not answer:
        return False, None
    
    # Normalize
    answer = answer.strip().upper()
    
    # Check valid options
    if answer in ['A', 'B', 'C', 'D']:
        return True, answer
    
    # Check numeric (1-4)
    if answer in ['1', '2', '3', '4']:
        mapping = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
        return True, mapping[answer]
    
    return False, None


def validate_date(date_str: str, format_str: str = "%Y-%m-%d") -> Tuple[bool, Optional[datetime]]:
    """
    Validate date string.
    
    Args:
        date_str: Date string
        format_str: Expected format
    
    Returns:
        Tuple of (is_valid, datetime_object)
    
    Reason:
        Ensure dates are parseable and valid.
    """
    try:
        dt = datetime.strptime(date_str, format_str)
        return True, dt
    except ValueError:
        return False, None


def validate_xp(xp: int) -> bool:
    """
    Validate XP value.
    
    Args:
        xp: XP value
    
    Returns:
        True if valid
    
    Reason:
        XP must be integer, any value allowed (positive or negative).
    """
    return isinstance(xp, int) and not isinstance(xp, bool)


def validate_theta(theta: float) -> bool:
    """
    Validate IRT theta value.
    
    Args:
        theta: Theta value
    
    Returns:
        True if within valid range (-3 to +3)
    
    Reason:
        Theta is bounded by IRT theory.
    """
    try:
        return -3.0 <= float(theta) <= 3.0
    except (TypeError, ValueError):
        return False


def validate_question_text(text: str) -> Tuple[bool, Optional[str]]:
    """
    Validate question text.
    
    Args:
        text: Question text
    
    Returns:
        Tuple of (is_valid, cleaned_text)
    
    Reason:
        Ensure questions are meaningful and not empty.
    """
    if not text:
        return False, None
    
    # Clean whitespace
    cleaned = text.strip()
    
    # Minimum length
    if len(cleaned) < 10:
        return False, None
    
    # Maximum length (prevent database issues)
    if len(cleaned) > 2000:
        return False, None
    
    return True, cleaned


def validate_options(options: List[str]) -> Tuple[bool, Optional[List[str]]]:
    """
    Validate MCQ options.
    
    Args:
        options: List of 4 options
    
    Returns:
        Tuple of (is_valid, cleaned_options)
    
    Reason:
        MCQ must have exactly 4 valid options.
    """
    if not options:
        return False, None
    
    if len(options) != 4:
        return False, None
    
    # Clean and validate each option
    cleaned = []
    for opt in options:
        if not opt or not isinstance(opt, str):
            return False, None
        
        opt_cleaned = opt.strip()
        if len(opt_cleaned) < 1:
            return False, None
        
        cleaned.append(opt_cleaned)
    
    return True, cleaned


def validate_irt_params(a: float, b: float, c: float) -> Tuple[bool, str]:
    """
    Validate IRT parameters.
    
    Args:
        a: Discrimination parameter
        b: Difficulty parameter
        c: Guessing parameter
    
    Returns:
        Tuple of (is_valid, error_message)
    
    Reason:
        IRT parameters have theoretical bounds.
    """
    # Discrimination (a): 0.5 to 2.5
    if not (0.5 <= a <= 2.5):
        return False, f"Discrimination (a) must be 0.5-2.5, got {a}"
    
    # Difficulty (b): -3.0 to 3.0
    if not (-3.0 <= b <= 3.0):
        return False, f"Difficulty (b) must be -3 to +3, got {b}"
    
    # Guessing (c): 0 to 0.5
    if not (0 <= c <= 0.5):
        return False, f"Guessing (c) must be 0-0.5, got {c}"
    
    return True, ""


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email string
    
    Returns:
        True if valid format
    
    Note:
        Not currently used, included for future use.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_positive_int(value: int, max_value: int = 10000) -> bool:
    """
    Validate positive integer.
    
    Args:
        value: Integer value
        max_value: Maximum allowed value
    
    Returns:
        True if valid
    """
    try:
        return 0 < int(value) <= max_value
    except (TypeError, ValueError):
        return False


def validate_hours(hours: int) -> bool:
    """
    Validate study hours (0-24).
    
    Args:
        hours: Hours value
    
    Returns:
        True if valid
    """
    try:
        return 0 <= int(hours) <= 24
    except (TypeError, ValueError):
        return False


def sanitize_string(text: str, max_length: int = 500) -> str:
    """
    Sanitize string for safe storage.
    
    Args:
        text: Input string
        max_length: Maximum length
    
    Returns:
        Sanitized string
    
    Reason:
        Prevent injection and database issues.
    """
    if not text:
        return ""
    
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f]', '', text)
    
    # Trim to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()
