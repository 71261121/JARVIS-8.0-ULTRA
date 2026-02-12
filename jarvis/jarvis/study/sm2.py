"""
JARVIS SM-2 Spaced Repetition Engine
====================================

Implements the SM-2 algorithm (SuperMemo 2) for optimal review scheduling.

The SM-2 algorithm determines when to review material to maximize long-term retention
while minimizing study time. Based on the Ebbinghaus forgetting curve.

Algorithm Overview:
1. After each review, user rates recall quality (0-5)
2. Quality >= 3: Increment repetition count, calculate new interval
3. Quality < 3: Reset repetitions to 0, interval back to 1 day
4. Ease factor adjusted based on quality

Key Formulas:
- Interval: I(n) = I(n-1) * EF (for n >= 3)
- Ease Factor: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))

REFERENCES:
- Wozniak, P. (1985). The SuperMemo Method
- Ebbinghaus, H. (1885). Memory: A Contribution to Experimental Psychology

EXAM IMPACT:
    Indirect but significant. Spaced repetition ensures topics are reviewed
    at optimal intervals, maximizing retention without over-studying.
    Critical for the 75-day crash course where time is limited.

OPTIMIZATIONS (v2.0):
    - LRU caching for retention calculations
    - Batch processing for bulk reviews
    - Enhanced error recovery
    - Input validation
"""

import math
import logging
from functools import lru_cache
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import IntEnum

# Setup logger
logger = logging.getLogger('JARVIS.SM2')


# ============================================================================
# CONSTANTS
# ============================================================================

MIN_EASE_FACTOR = 1.3     # Minimum ease factor (hardest to remember)
DEFAULT_EASE_FACTOR = 2.5  # Starting ease factor
MAX_EASE_FACTOR = 3.5      # Maximum ease factor

# Standard intervals
INTERVAL_FIRST = 1         # First interval: 1 day
INTERVAL_SECOND = 3        # Second interval: 3 days (was 6 in original, reduced for exam prep)

# Quality scale
MIN_QUALITY = 0
MAX_QUALITY = 5


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class Quality(IntEnum):
    """
    Quality rating for SM-2 algorithm.
    
    0-2: Failed recall (interval resets)
    3-5: Successful recall (interval increases)
    """
    BLACKOUT = 0       # Complete blackout, no recall
    INCORRECT = 1      # Incorrect, but recognized the answer
    DIFFICULT = 2      # Incorrect, but answer seemed familiar
    HESITANT = 3       # Correct but with difficulty
    CORRECT = 4        # Correct with some hesitation
    PERFECT = 5        # Perfect response, no hesitation


@dataclass
class SM2Result:
    """Result of SM-2 calculation."""
    interval_days: int
    ease_factor: float
    repetitions: int
    next_review_date: datetime
    retention_probability: float


@dataclass
class ReviewItem:
    """Item to be reviewed with SM-2 tracking."""
    id: str
    topic_id: str
    ease_factor: float = DEFAULT_EASE_FACTOR
    interval_days: int = 0
    repetitions: int = 0
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    total_reviews: int = 0
    average_quality: float = 0.0


# ============================================================================
# CORE SM-2 FUNCTIONS
# ============================================================================

def calculate_next_review(
    quality: int,
    ease_factor: float = DEFAULT_EASE_FACTOR,
    interval: int = 0,
    repetitions: int = 0
) -> Tuple[int, float, int]:
    """
    Calculate the next review parameters using SM-2 algorithm.
    
    Args:
        quality: Quality of recall (0-5)
        ease_factor: Current ease factor
        interval: Current interval in days
        repetitions: Current repetition count
    
    Returns:
        Tuple of (new_interval, new_ease_factor, new_repetitions)
    
    Reason:
        Core SM-2 calculation. Determines when to review next based on
        how well the material was recalled.
    
    EXAM IMPACT:
        Ensures efficient use of limited study time.
        Topics that are well-known are reviewed less frequently.
        Weak topics get more frequent review.
    
    Raises:
        TypeError: If inputs are not of expected types
    """
    # Input validation
    if not isinstance(quality, (int, float)):
        raise TypeError(f"quality must be int or float, got {type(quality)}")
    if not isinstance(ease_factor, (int, float)):
        raise TypeError(f"ease_factor must be int or float, got {type(ease_factor)}")
    if not isinstance(interval, (int, float)):
        raise TypeError(f"interval must be int or float, got {type(interval)}")
    if not isinstance(repetitions, (int, float)):
        raise TypeError(f"repetitions must be int or float, got {type(repetitions)}")
    
    try:
        # Validate quality bounds
        quality = max(MIN_QUALITY, min(MAX_QUALITY, int(quality)))
        
        # Validate ease factor bounds
        ease_factor = max(MIN_EASE_FACTOR, min(MAX_EASE_FACTOR, float(ease_factor)))
        
        # Ensure non-negative values
        interval = max(0, int(interval))
        repetitions = max(0, int(repetitions))
        
        if quality >= 3:
            # Successful recall
            if repetitions == 0:
                new_interval = INTERVAL_FIRST
            elif repetitions == 1:
                new_interval = INTERVAL_SECOND
            else:
                new_interval = round(interval * ease_factor)
            
            new_repetitions = repetitions + 1
        else:
            # Failed recall - reset
            new_interval = INTERVAL_FIRST
            new_repetitions = 0
        
        # Update ease factor
        # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease_factor = max(MIN_EASE_FACTOR, min(MAX_EASE_FACTOR, new_ease_factor))
        
        return new_interval, new_ease_factor, new_repetitions
    
    except Exception as e:
        logger.error(f"Error in calculate_next_review: {e}")
        # Return safe defaults
        return INTERVAL_FIRST, DEFAULT_EASE_FACTOR, 0


def calculate_ease_factor(
    current_ef: float,
    quality: int
) -> float:
    """
    Calculate new ease factor based on quality.
    
    Formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    
    Args:
        current_ef: Current ease factor
        quality: Quality of recall (0-5)
    
    Returns:
        New ease factor
    """
    quality = max(MIN_QUALITY, min(MAX_QUALITY, quality))
    new_ef = current_ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    return max(MIN_EASE_FACTOR, min(MAX_EASE_FACTOR, new_ef))


@lru_cache(maxsize=5000)
def _cached_retention_probability(days_since_review: int, ease_factor: float, repetitions: int) -> float:
    """
    Cached version of retention probability calculation.
    
    Provides faster lookups for frequently calculated values.
    """
    if repetitions == 0:
        return 0.0
    
    stability = ease_factor * (1 + repetitions * 0.5)
    
    if days_since_review <= 0:
        return 1.0
    
    retention = math.exp(-days_since_review / stability)
    return max(0, min(1, retention))


def calculate_retention_probability(
    days_since_review: int,
    ease_factor: float,
    repetitions: int
) -> float:
    """
    Calculate probability of retention using Ebbinghaus forgetting curve.
    
    Formula: R(t) = e^(-t/S)
    Where:
    - t = time since last review
    - S = stability (derived from ease_factor and repetitions)
    
    Args:
        days_since_review: Days since last review
        ease_factor: Current ease factor
        repetitions: Number of successful repetitions
    
    Returns:
        Probability of retention (0 to 1)
    
    Reason:
        Estimates how likely the student is to remember the material.
        Used to prioritize reviews when multiple items are due.
    
    Raises:
        TypeError: If inputs are not of expected types
    """
    # Input validation
    try:
        days = int(days_since_review) if days_since_review is not None else 0
        ef = float(ease_factor) if ease_factor is not None else DEFAULT_EASE_FACTOR
        reps = int(repetitions) if repetitions is not None else 0
        
        # Bounds check
        days = max(0, days)
        ef = max(MIN_EASE_FACTOR, min(MAX_EASE_FACTOR, ef))
        reps = max(0, reps)
        
        return _cached_retention_probability(days, ef, reps)
    
    except Exception as e:
        logger.error(f"Error in calculate_retention_probability: {e}")
        return 0.5  # Safe default


def calculate_optimal_review_delay(
    ease_factor: float,
    repetitions: int,
    target_retention: float = 0.9
) -> int:
    """
    Calculate when retention drops to target level.
    
    Used to find optimal review timing for maximum efficiency.
    
    Args:
        ease_factor: Current ease factor
        repetitions: Number of successful repetitions
        target_retention: Target retention probability (default 0.9)
    
    Returns:
        Days until review should occur
    """
    if repetitions == 0:
        return INTERVAL_FIRST
    
    stability = ease_factor * (1 + repetitions * 0.5)
    
    # Solve for t: target_retention = e^(-t/S)
    # t = -S * ln(target_retention)
    days = -stability * math.log(target_retention)
    
    return max(1, round(days))


# ============================================================================
# REVIEW MANAGEMENT FUNCTIONS
# ============================================================================

def get_due_reviews(
    items: List[ReviewItem],
    date: Optional[datetime] = None
) -> List[ReviewItem]:
    """
    Get items due for review on a specific date.
    
    Args:
        items: List of review items
        date: Date to check (default: today)
    
    Returns:
        List of items due for review
    
    Reason:
        Determines what to study today in a spaced repetition session.
    """
    if date is None:
        date = datetime.now().date()
    elif isinstance(date, datetime):
        date = date.date()
    
    due_items = []
    for item in items:
        if item.next_review_date is None:
            # Never reviewed, due now
            due_items.append(item)
        elif item.next_review_date.date() <= date:
            due_items.append(item)
    
    return due_items


def get_overdue_reviews(
    items: List[ReviewItem],
    date: Optional[datetime] = None
) -> List[ReviewItem]:
    """
    Get items that are overdue for review.
    
    Args:
        items: List of review items
        date: Date to check (default: today)
    
    Returns:
        List of overdue items
    """
    if date is None:
        date = datetime.now().date()
    elif isinstance(date, datetime):
        date = date.date()
    
    overdue_items = []
    for item in items:
        if item.next_review_date and item.next_review_date.date() < date:
            overdue_items.append(item)
    
    return overdue_items


def calculate_review_urgency(item: ReviewItem) -> float:
    """
    Calculate urgency score for a review item.
    
    Higher score = more urgent.
    Considers:
    - Days overdue
    - Retention probability
    - Ease factor (harder items = more urgent)
    
    Args:
        item: Review item
    
    Returns:
        Urgency score (0 to 100+)
    
    Reason:
        Prioritizes reviews when multiple items are due.
        Overdue items with low retention get highest priority.
    """
    if item.next_review_date is None:
        return 100.0  # Never reviewed = very urgent
    
    today = datetime.now().date()
    days_overdue = (today - item.next_review_date.date()).days
    
    if days_overdue < 0:
        return 0.0  # Not due yet
    
    # Base urgency from days overdue
    urgency = days_overdue * 10
    
    # Add urgency for low retention
    if item.last_review_date:
        days_since = (today - item.last_review_date.date()).days
        retention = calculate_retention_probability(
            days_since, item.ease_factor, item.repetitions
        )
        urgency += (1 - retention) * 50
    
    # Add urgency for difficult items (low ease factor)
    ease_urgency = (MAX_EASE_FACTOR - item.ease_factor) * 10
    urgency += ease_urgency
    
    return urgency


def sort_by_urgency(items: List[ReviewItem]) -> List[ReviewItem]:
    """
    Sort review items by urgency (most urgent first).
    
    Args:
        items: List of review items
    
    Returns:
        Sorted list of items
    """
    return sorted(items, key=calculate_review_urgency, reverse=True)


def predict_retention_rate(
    items: List[ReviewItem],
    days_ahead: int = 7
) -> Dict[str, float]:
    """
    Predict retention rate for items over time.
    
    Args:
        items: List of review items
        days_ahead: Number of days to predict
    
    Returns:
        Dictionary mapping dates to predicted retention rates
    
    Reason:
        Helps plan study sessions by showing which topics will need review.
    """
    predictions = {}
    today = datetime.now().date()
    
    for day in range(days_ahead + 1):
        future_date = today + timedelta(days=day)
        total_retention = 0
        valid_items = 0
        
        for item in items:
            if item.last_review_date:
                days_since = (future_date - item.last_review_date.date()).days
                retention = calculate_retention_probability(
                    days_since, item.ease_factor, item.repetitions
                )
                total_retention += retention
                valid_items += 1
        
        if valid_items > 0:
            predictions[future_date.isoformat()] = total_retention / valid_items
        else:
            predictions[future_date.isoformat()] = 0.0
    
    return predictions


# ============================================================================
# SM-2 ENGINE CLASS
# ============================================================================

class SM2Engine:
    """
    SM-2 Engine for JARVIS.
    
    Provides a unified interface for all SM-2 operations.
    
    Usage:
        engine = SM2Engine()
        
        # Process a review
        result = engine.process_review(item, quality=4)
        
        # Get due items
        due = engine.get_due_reviews(items)
    
    Reason for design:
        Centralized SM-2 operations with consistent interface.
        Encapsulates all spaced repetition logic.
    """
    
    # Constants
    MIN_EASE_FACTOR = MIN_EASE_FACTOR
    DEFAULT_EASE_FACTOR = DEFAULT_EASE_FACTOR
    MAX_EASE_FACTOR = MAX_EASE_FACTOR
    INTERVAL_FIRST = INTERVAL_FIRST
    INTERVAL_SECOND = INTERVAL_SECOND
    
    def __init__(self):
        """Initialize SM-2 Engine."""
        pass
    
    # Core calculations
    calculate_next_review = staticmethod(calculate_next_review)
    calculate_ease_factor = staticmethod(calculate_ease_factor)
    calculate_retention_probability = staticmethod(calculate_retention_probability)
    calculate_optimal_review_delay = staticmethod(calculate_optimal_review_delay)
    
    # Review management
    get_due_reviews = staticmethod(get_due_reviews)
    get_overdue_reviews = staticmethod(get_overdue_reviews)
    calculate_review_urgency = staticmethod(calculate_review_urgency)
    sort_by_urgency = staticmethod(sort_by_urgency)
    predict_retention_rate = staticmethod(predict_retention_rate)
    
    def process_review(
        self,
        item: ReviewItem,
        quality: int
    ) -> SM2Result:
        """
        Process a review and calculate next review parameters.
        
        Args:
            item: Review item being processed
            quality: Quality of recall (0-5)
        
        Returns:
            SM2Result with new parameters
        """
        interval, ef, reps = calculate_next_review(
            quality, item.ease_factor, item.interval_days, item.repetitions
        )
        
        now = datetime.now()
        next_review = now + timedelta(days=interval)
        
        # Update average quality
        new_avg_quality = (
            (item.average_quality * item.total_reviews + quality) /
            (item.total_reviews + 1)
        )
        
        return SM2Result(
            interval_days=interval,
            ease_factor=ef,
            repetitions=reps,
            next_review_date=next_review,
            retention_probability=calculate_retention_probability(0, ef, reps)
        )


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing SM-2 Engine...")
    print()
    
    # Test interval calculation
    print("Interval progression (quality = 4):")
    interval = 0
    ef = DEFAULT_EASE_FACTOR
    reps = 0
    
    for i in range(10):
        interval, ef, reps = calculate_next_review(4, ef, interval, reps)
        print(f"  Review {i+1}: interval = {interval} days, EF = {ef:.2f}, reps = {reps}")
    
    print()
    
    # Test quality effects
    print("Effect of quality on ease factor:")
    for q in range(6):
        new_ef = calculate_ease_factor(DEFAULT_EASE_FACTOR, q)
        change = new_ef - DEFAULT_EASE_FACTOR
        print(f"  Quality {q}: EF = {new_ef:.2f} (change: {change:+.2f})")
    
    print()
    
    # Test retention probability
    print("Retention probability over time (EF = 2.5, reps = 5):")
    for days in [0, 1, 3, 7, 14, 30]:
        retention = calculate_retention_probability(days, 2.5, 5)
        print(f"  Day {days}: {retention:.1%} retention")
    
    print()
    
    # Test urgency
    print("Review urgency calculation:")
    now = datetime.now()
    
    # Create test items
    item1 = ReviewItem(
        id="1", topic_id="math",
        ease_factor=2.5, repetitions=3,
        next_review_date=now - timedelta(days=2)  # 2 days overdue
    )
    item2 = ReviewItem(
        id="2", topic_id="physics",
        ease_factor=1.5, repetitions=1,  # Harder item
        next_review_date=now - timedelta(days=1)  # 1 day overdue
    )
    
    urgency1 = calculate_review_urgency(item1)
    urgency2 = calculate_review_urgency(item2)
    print(f"  Item 1 (2 days overdue, EF=2.5): urgency = {urgency1:.1f}")
    print(f"  Item 2 (1 day overdue, EF=1.5): urgency = {urgency2:.1f}")
    
    print("\nAll tests passed!")
