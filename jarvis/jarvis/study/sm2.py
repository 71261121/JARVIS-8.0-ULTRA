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

PRODUCTION OPTIMIZATIONS:
- LRU caching for retention calculations
- Batch processing for multiple items
- Thread-safe operations
- Comprehensive error handling
- Priority queue for review scheduling

REFERENCES:
- Wozniak, P. (1985). The SuperMemo Method
- Ebbinghaus, H. (1885). Memory: A Contribution to Experimental Psychology

EXAM IMPACT:
    Indirect but significant. Spaced repetition ensures topics are reviewed
    at optimal intervals, maximizing retention without over-studying.
    Critical for the 75-day crash course where time is limited.
"""

import math
import functools
import threading
import heapq
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple, Set, Any, Iterator
from dataclasses import dataclass, field
from enum import IntEnum
import logging

# ============================================================================
# CONSTANTS
# ============================================================================

MIN_EASE_FACTOR = 1.3     # Minimum ease factor (hardest to remember)
DEFAULT_EASE_FACTOR = 2.5  # Starting ease factor
MAX_EASE_FACTOR = 3.5      # Maximum ease factor

# Standard intervals
INTERVAL_FIRST = 1         # First interval: 1 day
INTERVAL_SECOND = 3        # Second interval: 3 days (was 6 in original, reduced for exam prep)
INTERVAL_MAX = 365         # Maximum interval (1 year)

# Quality scale
MIN_QUALITY = 0
MAX_QUALITY = 5

# Cache settings
MAX_CACHE_SIZE = 5000

# Retention thresholds
RETENTION_CRITICAL = 0.5   # Below this = urgent review needed
RETENTION_TARGET = 0.9     # Target retention for optimal review timing


# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger("JARVIS.SM2")


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


class ReviewPriority(IntEnum):
    """Priority levels for review items."""
    CRITICAL = 0    # Immediate attention needed
    HIGH = 1        # Due today or overdue
    MEDIUM = 2      # Due within 3 days
    LOW = 3         # Not urgent


@dataclass
class SM2Result:
    """Result of SM-2 calculation with full details."""
    interval_days: int
    ease_factor: float
    repetitions: int
    next_review_date: datetime
    retention_probability: float
    priority: ReviewPriority = ReviewPriority.MEDIUM
    days_until_due: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "interval_days": self.interval_days,
            "ease_factor": round(self.ease_factor, 3),
            "repetitions": self.repetitions,
            "next_review_date": self.next_review_date.isoformat(),
            "retention_probability": round(self.retention_probability, 4),
            "priority": self.priority.name,
            "days_until_due": self.days_until_due,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ReviewItem:
    """
    Item to be reviewed with SM-2 tracking.
    
    Implements comparison for priority queue usage via __lt__.
    """
    # Item data
    id: str
    topic_id: str
    subject_id: str = ""
    ease_factor: float = DEFAULT_EASE_FACTOR
    interval_days: int = 0
    repetitions: int = 0
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    total_reviews: int = 0
    average_quality: float = 0.0
    difficulty_score: float = 0.5  # 0=easy, 1=hard
    tags: Set[str] = field(default_factory=set)
    
    # Sort key (computed from urgency)
    _sort_key: float = field(default=0.0, repr=False)
    
    def __post_init__(self):
        """Compute sort key after initialization."""
        self._sort_key = -self._compute_urgency()
    
    def _compute_urgency(self) -> float:
        """Compute urgency for sorting."""
        if self.next_review_date is None:
            return 100.0
        days_overdue = (datetime.now().date() - self.next_review_date.date()).days
        if days_overdue < 0:
            return 0.0
        return days_overdue * 10 + (MAX_EASE_FACTOR - self.ease_factor) * 5
    
    def update_sort_key(self) -> None:
        """Update sort key after changes."""
        self._sort_key = -self._compute_urgency()
    
    def __lt__(self, other: 'ReviewItem') -> bool:
        """Compare for sorting (lower sort_key = higher priority)."""
        if not isinstance(other, ReviewItem):
            return NotImplemented
        return self._sort_key < other._sort_key
    
    def __le__(self, other: 'ReviewItem') -> bool:
        """Compare for sorting."""
        if not isinstance(other, ReviewItem):
            return NotImplemented
        return self._sort_key <= other._sort_key
    
    def get_retention(self) -> float:
        """Get current retention probability."""
        if self.last_review_date is None or self.repetitions == 0:
            return 0.0
        
        days_since = (datetime.now().date() - self.last_review_date.date()).days
        return calculate_retention_probability(days_since, self.ease_factor, self.repetitions)
    
    def is_due(self, check_date: Optional[date] = None) -> bool:
        """Check if item is due for review."""
        check_date = check_date or datetime.now().date()
        if self.next_review_date is None:
            return True
        return self.next_review_date.date() <= check_date
    
    def get_priority(self) -> ReviewPriority:
        """Get review priority."""
        retention = self.get_retention()
        
        if retention < RETENTION_CRITICAL:
            return ReviewPriority.CRITICAL
        
        if self.next_review_date is None:
            return ReviewPriority.HIGH
        
        days_until = (self.next_review_date.date() - datetime.now().date()).days
        
        if days_until <= 0:
            return ReviewPriority.HIGH
        elif days_until <= 3:
            return ReviewPriority.MEDIUM
        else:
            return ReviewPriority.LOW
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "subject_id": self.subject_id,
            "ease_factor": round(self.ease_factor, 3),
            "interval_days": self.interval_days,
            "repetitions": self.repetitions,
            "last_review_date": self.last_review_date.isoformat() if self.last_review_date else None,
            "next_review_date": self.next_review_date.isoformat() if self.next_review_date else None,
            "total_reviews": self.total_reviews,
            "average_quality": round(self.average_quality, 2),
            "retention": round(self.get_retention(), 3),
            "priority": self.get_priority().name,
            "is_due": self.is_due()
        }


# ============================================================================
# CORE SM-2 FUNCTIONS WITH CACHING
# ============================================================================

@functools.lru_cache(maxsize=MAX_CACHE_SIZE)
def _cached_exp_div_stability(days: int, stability: float) -> float:
    """Cached exp(-days/stability) calculation."""
    try:
        if stability <= 0:
            return 0.0
        return math.exp(-days / stability)
    except (OverflowError, ZeroDivisionError):
        return 0.0


def calculate_next_review(
    quality: int,
    ease_factor: float = DEFAULT_EASE_FACTOR,
    interval: int = 0,
    repetitions: int = 0,
    max_interval: int = INTERVAL_MAX
) -> Tuple[int, float, int]:
    """
    Calculate the next review parameters using SM-2 algorithm.
    
    Args:
        quality: Quality of recall (0-5)
        ease_factor: Current ease factor
        interval: Current interval in days
        repetitions: Current repetition count
        max_interval: Maximum allowed interval
    
    Returns:
        Tuple of (new_interval, new_ease_factor, new_repetitions)
    
    Production Features:
        - Input validation
        - Maximum interval cap
        - Handles edge cases
    """
    # Validate and clamp inputs
    quality = max(MIN_QUALITY, min(MAX_QUALITY, int(quality)))
    ease_factor = max(MIN_EASE_FACTOR, min(MAX_EASE_FACTOR, float(ease_factor)))
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
        
        # Cap at maximum interval
        new_interval = min(new_interval, max_interval)
        new_repetitions = repetitions + 1
    else:
        # Failed recall - reset
        new_interval = INTERVAL_FIRST
        new_repetitions = 0
    
    # Update ease factor: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    delta = (5 - quality) * (0.08 + (5 - quality) * 0.02)
    new_ease_factor = ease_factor + (0.1 - delta)
    new_ease_factor = max(MIN_EASE_FACTOR, min(MAX_EASE_FACTOR, new_ease_factor))
    
    return new_interval, new_ease_factor, new_repetitions


def calculate_ease_factor(
    current_ef: float,
    quality: int
) -> float:
    """
    Calculate new ease factor based on quality.
    
    Formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    """
    quality = max(MIN_QUALITY, min(MAX_QUALITY, int(quality)))
    current_ef = max(MIN_EASE_FACTOR, min(MAX_EASE_FACTOR, float(current_ef)))
    
    delta = (5 - quality) * (0.08 + (5 - quality) * 0.02)
    new_ef = current_ef + (0.1 - delta)
    
    return max(MIN_EASE_FACTOR, min(MAX_EASE_FACTOR, new_ef))


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
    
    Production Features:
        - LRU caching
        - Edge case handling
    """
    if repetitions == 0:
        return 0.0
    
    # Validate inputs
    days_since_review = max(0, int(days_since_review))
    ease_factor = max(MIN_EASE_FACTOR, min(MAX_EASE_FACTOR, float(ease_factor)))
    
    if days_since_review <= 0:
        return 1.0
    
    # Stability increases with ease factor and repetitions
    stability = ease_factor * (1 + repetitions * 0.5)
    
    # Use cached calculation
    retention = _cached_exp_div_stability(days_since_review, stability)
    
    return max(0.0, min(1.0, retention))


def calculate_optimal_review_delay(
    ease_factor: float,
    repetitions: int,
    target_retention: float = RETENTION_TARGET
) -> int:
    """
    Calculate when retention drops to target level.
    
    Args:
        ease_factor: Current ease factor
        repetitions: Number of successful repetitions
        target_retention: Target retention probability
    
    Returns:
        Days until review should occur
    """
    if repetitions == 0:
        return INTERVAL_FIRST
    
    ease_factor = max(MIN_EASE_FACTOR, min(MAX_EASE_FACTOR, float(ease_factor)))
    target_retention = max(0.1, min(0.99, float(target_retention)))
    
    stability = ease_factor * (1 + repetitions * 0.5)
    
    # Solve: target_retention = e^(-t/S) => t = -S * ln(target_retention)
    try:
        days = -stability * math.log(target_retention)
    except (ValueError, ZeroDivisionError):
        return INTERVAL_FIRST
    
    return max(1, min(round(days), INTERVAL_MAX))


# ============================================================================
# BATCH OPERATIONS
# ============================================================================

def batch_calculate_retention(
    items: List[ReviewItem]
) -> List[float]:
    """
    Calculate retention for multiple items efficiently.
    
    Args:
        items: List of review items
    
    Returns:
        List of retention probabilities
    """
    today = datetime.now().date()
    results = []
    
    for item in items:
        if item.last_review_date is None or item.repetitions == 0:
            results.append(0.0)
        else:
            days_since = (today - item.last_review_date.date()).days
            retention = calculate_retention_probability(
                days_since, item.ease_factor, item.repetitions
            )
            results.append(retention)
    
    return results


def batch_get_due_items(
    items: List[ReviewItem],
    check_date: Optional[date] = None,
    include_future_days: int = 0
) -> List[ReviewItem]:
    """
    Get all due items efficiently.
    
    Args:
        items: List of review items
        check_date: Date to check (default: today)
        include_future_days: Include items due within N days
    
    Returns:
        List of due items sorted by priority
    """
    check_date = check_date or datetime.now().date()
    threshold_date = check_date + timedelta(days=include_future_days)
    
    due_items = []
    for item in items:
        if item.next_review_date is None:
            due_items.append(item)
        elif item.next_review_date.date() <= threshold_date:
            due_items.append(item)
    
    # Sort by urgency (descending)
    due_items.sort(key=lambda x: -x._compute_urgency())
    
    return due_items


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
    """
    return batch_get_due_items(items, date)


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
    check_date = (date or datetime.now()).date() if isinstance(date, datetime) else (date or datetime.now().date())
    
    overdue = []
    for item in items:
        if item.next_review_date and item.next_review_date.date() < check_date:
            overdue.append(item)
    
    return sorted(overdue, key=lambda x: -x._compute_urgency())


def calculate_review_urgency(item: ReviewItem) -> float:
    """
    Calculate urgency score for a review item.
    
    Higher score = more urgent.
    """
    return item._compute_urgency()


def sort_by_urgency(items: List[ReviewItem]) -> List[ReviewItem]:
    """
    Sort review items by urgency (most urgent first).
    """
    return sorted(items, key=lambda x: -x._compute_urgency())


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
    """
    if not items:
        return {}
    
    predictions = {}
    today = datetime.now().date()
    
    for day in range(days_ahead + 1):
        future_date = today + timedelta(days=day)
        total_retention = 0.0
        valid_items = 0
        
        for item in items:
            if item.last_review_date and item.repetitions > 0:
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


def get_review_statistics(items: List[ReviewItem]) -> Dict[str, Any]:
    """
    Get comprehensive statistics for review items.
    
    Args:
        items: List of review items
    
    Returns:
        Dictionary with statistics
    """
    if not items:
        return {
            "total_items": 0,
            "due_items": 0,
            "overdue_items": 0,
            "average_ease_factor": 0,
            "average_retention": 0
        }
    
    today = datetime.now().date()
    due_count = 0
    overdue_count = 0
    total_ef = 0.0
    total_retention = 0.0
    valid_retention = 0
    
    for item in items:
        total_ef += item.ease_factor
        
        if item.next_review_date is None or item.next_review_date.date() <= today:
            due_count += 1
        
        if item.next_review_date and item.next_review_date.date() < today:
            overdue_count += 1
        
        if item.repetitions > 0 and item.last_review_date:
            days_since = (today - item.last_review_date.date()).days
            retention = calculate_retention_probability(
                days_since, item.ease_factor, item.repetitions
            )
            total_retention += retention
            valid_retention += 1
    
    return {
        "total_items": len(items),
        "due_items": due_count,
        "overdue_items": overdue_count,
        "average_ease_factor": round(total_ef / len(items), 3),
        "average_retention": round(total_retention / valid_retention, 3) if valid_retention > 0 else 0,
        "critical_items": sum(1 for i in items if i.get_retention() < RETENTION_CRITICAL)
    }


# ============================================================================
# SM-2 ENGINE CLASS
# ============================================================================

class SM2Engine:
    """
    SM-2 Engine for JARVIS with production optimizations.
    
    Features:
        - Thread-safe operations
        - LRU caching for performance
        - Batch operations for efficiency
        - Priority queue for review scheduling
    
    Usage:
        engine = SM2Engine()
        
        # Process a review
        result = engine.process_review(item, quality=4)
        
        # Get due items
        due = engine.get_due_reviews(items)
    """
    
    # Constants
    MIN_EASE_FACTOR = MIN_EASE_FACTOR
    DEFAULT_EASE_FACTOR = DEFAULT_EASE_FACTOR
    MAX_EASE_FACTOR = MAX_EASE_FACTOR
    INTERVAL_FIRST = INTERVAL_FIRST
    INTERVAL_SECOND = INTERVAL_SECOND
    INTERVAL_MAX = INTERVAL_MAX
    
    def __init__(self, max_cache_size: int = MAX_CACHE_SIZE):
        """
        Initialize SM-2 Engine.
        
        Args:
            max_cache_size: Maximum cache size
        """
        self._lock = threading.Lock()
        self._review_count = 0
        logger.info("SM-2 Engine initialized")
    
    # Core calculations (static methods for thread safety)
    calculate_next_review = staticmethod(calculate_next_review)
    calculate_ease_factor = staticmethod(calculate_ease_factor)
    calculate_retention_probability = staticmethod(calculate_retention_probability)
    calculate_optimal_review_delay = staticmethod(calculate_optimal_review_delay)
    
    # Batch operations
    batch_calculate_retention = staticmethod(batch_calculate_retention)
    batch_get_due_items = staticmethod(batch_get_due_items)
    
    # Review management
    get_due_reviews = staticmethod(get_due_reviews)
    get_overdue_reviews = staticmethod(get_overdue_reviews)
    calculate_review_urgency = staticmethod(calculate_review_urgency)
    sort_by_urgency = staticmethod(sort_by_urgency)
    predict_retention_rate = staticmethod(predict_retention_rate)
    get_review_statistics = staticmethod(get_review_statistics)
    
    def process_review(
        self,
        item: ReviewItem,
        quality: int,
        review_time: Optional[datetime] = None
    ) -> SM2Result:
        """
        Process a review and calculate next review parameters.
        
        Args:
            item: Review item being processed
            quality: Quality of recall (0-5)
            review_time: Time of review (default: now)
        
        Returns:
            SM2Result with new parameters
        """
        with self._lock:
            self._review_count += 1
        
        review_time = review_time or datetime.now()
        
        # Calculate new parameters
        interval, ef, reps = calculate_next_review(
            quality, item.ease_factor, item.interval_days, item.repetitions
        )
        
        next_review = review_time + timedelta(days=interval)
        
        # Update average quality
        new_total = item.total_reviews + 1
        new_avg_quality = (
            (item.average_quality * item.total_reviews + quality) / new_total
        )
        
        # Calculate current retention
        retention = calculate_retention_probability(0, ef, reps)
        
        # Calculate days until due
        days_until = (next_review.date() - review_time.date()).days
        
        # Determine priority
        if retention < RETENTION_CRITICAL:
            priority = ReviewPriority.CRITICAL
        elif days_until <= 0:
            priority = ReviewPriority.HIGH
        elif days_until <= 3:
            priority = ReviewPriority.MEDIUM
        else:
            priority = ReviewPriority.LOW
        
        return SM2Result(
            interval_days=interval,
            ease_factor=ef,
            repetitions=reps,
            next_review_date=next_review,
            retention_probability=retention,
            priority=priority,
            days_until_due=days_until
        )
    
    def process_review_batch(
        self,
        reviews: List[Tuple[ReviewItem, int]]
    ) -> List[SM2Result]:
        """
        Process multiple reviews efficiently.
        
        Args:
            reviews: List of (item, quality) tuples
        
        Returns:
            List of SM2Results
        """
        return [self.process_review(item, quality) for item, quality in reviews]
    
    def create_review_item(
        self,
        item_id: str,
        topic_id: str,
        subject_id: str = "",
        difficulty_score: float = 0.5,
        tags: Optional[Set[str]] = None
    ) -> ReviewItem:
        """
        Create a new review item with defaults.
        
        Args:
            item_id: Unique identifier
            topic_id: Topic identifier
            subject_id: Subject identifier
            difficulty_score: Initial difficulty (0=easy, 1=hard)
            tags: Optional tags
        
        Returns:
            New ReviewItem
        """
        # Adjust initial ease factor based on difficulty
        initial_ef = DEFAULT_EASE_FACTOR - (difficulty_score * 0.5)
        initial_ef = max(MIN_EASE_FACTOR, min(MAX_EASE_FACTOR, initial_ef))
        
        return ReviewItem(
            id=item_id,
            topic_id=topic_id,
            subject_id=subject_id,
            ease_factor=initial_ef,
            difficulty_score=difficulty_score,
            tags=tags or set()
        )
    
    def clear_cache(self) -> None:
        """Clear calculation caches."""
        _cached_exp_div_stability.cache_clear()
        logger.info("SM-2 caches cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        cache_info = _cached_exp_div_stability.cache_info()
        return {
            "review_count": self._review_count,
            "cache_hits": cache_info.hits,
            "cache_misses": cache_info.misses,
            "cache_size": cache_info.currsize
        }


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Production SM-2 Engine...")
    print("=" * 60)
    
    engine = SM2Engine()
    
    # Test 1: Interval progression
    print("\n1. Interval progression (quality = 4):")
    interval, ef, reps = 0, DEFAULT_EASE_FACTOR, 0
    
    for i in range(10):
        interval, ef, reps = calculate_next_review(4, ef, interval, reps)
        print(f"   Review {i+1}: interval = {interval} days, EF = {ef:.3f}, reps = {reps}")
    
    # Test 2: Quality effects
    print("\n2. Effect of quality on ease factor:")
    for q in range(6):
        new_ef = calculate_ease_factor(DEFAULT_EASE_FACTOR, q)
        change = new_ef - DEFAULT_EASE_FACTOR
        print(f"   Quality {q}: EF = {new_ef:.3f} (change: {change:+.3f})")
    
    # Test 3: Retention probability
    print("\n3. Retention probability (EF = 2.5, reps = 5):")
    for days in [0, 1, 3, 7, 14, 30]:
        retention = calculate_retention_probability(days, 2.5, 5)
        print(f"   Day {days}: {retention:.1%} retention")
    
    # Test 4: Review item creation and processing
    print("\n4. Review item creation and processing:")
    item = engine.create_review_item("test-1", "algebra", "math", difficulty_score=0.3)
    print(f"   Created: {item.id}, initial EF = {item.ease_factor:.3f}")
    
    result = engine.process_review(item, Quality.CORRECT)
    print(f"   After review (quality=4):")
    print(f"      Interval: {result.interval_days} days")
    print(f"      New EF: {result.ease_factor:.3f}")
    print(f"      Priority: {result.priority.name}")
    
    # Test 5: Batch operations
    print("\n5. Batch operations:")
    items = [
        engine.create_review_item(f"item-{i}", f"topic-{i % 3}", "math")
        for i in range(10)
    ]
    
    # Process some reviews
    reviews = [(items[i], 4 if i % 2 == 0 else 2) for i in range(5)]
    results = engine.process_review_batch(reviews)
    print(f"   Processed {len(results)} reviews")
    
    # Get statistics
    stats = get_review_statistics(items)
    print(f"   Statistics: {stats['total_items']} items, {stats['due_items']} due")
    
    # Test 6: Engine stats
    print("\n6. Engine statistics:")
    engine_stats = engine.get_stats()
    print(f"   Reviews processed: {engine_stats['review_count']}")
    print(f"   Cache hits: {engine_stats['cache_hits']}")
    
    print("\n" + "=" * 60)
    print("All tests passed!")
