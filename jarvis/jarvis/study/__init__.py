"""
JARVIS Study Module
===================

Purpose: Core study functionality - IRT, SM-2, question bank, sessions.

Components:
- IRT (Item Response Theory) engine for adaptive testing
- SM-2 algorithm for spaced repetition
- Question bank management
- Study session tracking

This is the HEART of JARVIS.

Mathematical Foundation:
- IRT 3PL Model: P(θ) = c + (1-c) / (1 + exp(-Da(θ-b)))
- SM-2 Algorithm: Interval = previous × ease_factor

Reason for these algorithms:
- IRT: Adaptive questions match student ability
- SM-2: Optimal timing for memory retention

EXAM IMPACT:
    Direct. These algorithms ensure:
    - Questions match student ability (no wasted time)
    - Reviews happen at optimal intervals
    - Weaknesses are targeted systematically
"""

# IRT Engine
from .irt import (
    # Core classes
    IRTEngine,
    IRTParameters,
    IRTResult,
    QuestionIRT,
    AbilityLevel,
    
    # Core functions
    probability_correct,
    fisher_information,
    update_theta,
    
    # CAT functions
    select_optimal_question,
    calculate_standard_error,
    should_stop_cat,
    
    # Conversion utilities
    theta_to_percentage,
    theta_to_percentile,
    percentage_to_theta,
    get_ability_level,
    calculate_expected_score,
    estimate_theta_mle,
    
    # Constants
    THETA_MIN,
    THETA_MAX,
    GUESSING_DEFAULT,
    D_SCALING,
    SE_TARGET,
)

# SM-2 Engine
from .sm2 import (
    # Core classes
    SM2Engine,
    SM2Result,
    ReviewItem,
    Quality,
    
    # Core functions
    calculate_next_review,
    calculate_ease_factor,
    calculate_retention_probability,
    calculate_optimal_review_delay,
    
    # Review management
    get_due_reviews,
    get_overdue_reviews,
    calculate_review_urgency,
    sort_by_urgency,
    predict_retention_rate,
    
    # Constants
    MIN_EASE_FACTOR,
    DEFAULT_EASE_FACTOR,
    MAX_EASE_FACTOR,
    INTERVAL_FIRST,
    INTERVAL_SECOND,
)

# Question Bank
from .question_bank import (
    # Classes
    QuestionBank,
    Question,
    Topic,
    Subject,
    
    # Default data
    DEFAULT_SUBJECTS,
    FOUNDATION_TOPICS_MATHS,
    FOUNDATION_TOPICS_PHYSICS,
)

# Session Manager
from .session import (
    # Classes
    SessionManager,
    MockTestManager,
    Session,
    SessionConfig,
    SessionStats,
    SessionStatus,
    SessionType,
    QuestionResponse,
)

__all__ = [
    # IRT
    "IRTEngine",
    "IRTParameters",
    "IRTResult",
    "QuestionIRT",
    "AbilityLevel",
    "probability_correct",
    "fisher_information",
    "update_theta",
    "select_optimal_question",
    "calculate_standard_error",
    "should_stop_cat",
    "theta_to_percentage",
    "theta_to_percentile",
    "percentage_to_theta",
    "get_ability_level",
    "calculate_expected_score",
    "estimate_theta_mle",
    "THETA_MIN",
    "THETA_MAX",
    "GUESSING_DEFAULT",
    "D_SCALING",
    "SE_TARGET",
    
    # SM-2
    "SM2Engine",
    "SM2Result",
    "ReviewItem",
    "Quality",
    "calculate_next_review",
    "calculate_ease_factor",
    "calculate_retention_probability",
    "calculate_optimal_review_delay",
    "get_due_reviews",
    "get_overdue_reviews",
    "calculate_review_urgency",
    "sort_by_urgency",
    "predict_retention_rate",
    "MIN_EASE_FACTOR",
    "DEFAULT_EASE_FACTOR",
    "MAX_EASE_FACTOR",
    "INTERVAL_FIRST",
    "INTERVAL_SECOND",
    
    # Question Bank
    "QuestionBank",
    "Question",
    "Topic",
    "Subject",
    "DEFAULT_SUBJECTS",
    "FOUNDATION_TOPICS_MATHS",
    "FOUNDATION_TOPICS_PHYSICS",
    
    # Session Manager
    "SessionManager",
    "MockTestManager",
    "Session",
    "SessionConfig",
    "SessionStats",
    "SessionStatus",
    "SessionType",
    "QuestionResponse",
]
