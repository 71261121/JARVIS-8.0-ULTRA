"""
JARVIS Psychological Engine Module
==================================

Purpose: Motivation through gamification and behavioral psychology.

Components:
- Loss Aversion Engine (Kahneman & Tversky, 1979)
- Variable Reward System (Slot machine psychology)
- Achievement System (Gamification)
- Psychological Engine (Integration)

Psychological Foundation:
1. Loss Aversion (Kahneman & Tversky, 1979)
   - Losses feel 2x more painful than equivalent gains
   - Used in streak protection and messaging
   - LOSS_AVERSION_MULTIPLIER = 2.0

2. Variable Reward System
   - Unpredictable rewards trigger more dopamine
   - Slot machine psychology (variable ratio schedule)
   - Jackpots, bonuses, mystery boxes

3. Achievement System
   - Gamification through badges and milestones
   - Tiered difficulty (Common → Legendary)
   - Hidden achievements for surprise

4. Social Comparison
   - Leaderboards and ranking
   - Competition as motivation

EXAM IMPACT:
    CRITICAL. User has history of inconsistency.
    These techniques are PROVEN to increase engagement.
    Psychology is what makes the system WORK.

Customization for User:
- No guilt-based messaging (user requested)
- Forward-looking motivation
- Factual, not emotional

Messaging Style:
❌ "You're useless! Study kar nahi sakte?"
✓ "Maths score is 6/20. Let's work on Quadratic equations."
"""

# New comprehensive modules
from .loss_aversion import (
    LossAversionEngine,
    UserProgress,
    LossWarning,
    LOSS_AVERSION_MULTIPLIER,
)

from .reward_system import (
    RewardSystem,
    Reward,
    MysteryBox,
    RewardType,
    RewardTier,
    RewardStats,
    JACKPOT_CHANCE,
)

from .achievement_system import (
    AchievementSystem as NewAchievementSystem,
    Achievement,
    UserAchievement,
    AchievementTier,
    AchievementCategory,
    AchievementStats,
    ACHIEVEMENTS,
)

from .psychological_engine import (
    PsychologicalEngine,
    SessionResult,
    DailyMotivation,
    PsychologicalStats,
    create_psychological_engine,
)

# Legacy modules (for backward compatibility)
try:
    from .xp import XPSystem, calculate_level
    from .streak import StreakManager
    from .achievements import AchievementSystem
    from .motivation import MotivationEngine
    LEGACY_AVAILABLE = True
except ImportError:
    LEGACY_AVAILABLE = False
    XPSystem = None
    calculate_level = None
    StreakManager = None
    AchievementSystem = None
    MotivationEngine = None


__all__ = [
    # New modules (recommended)
    "LossAversionEngine",
    "UserProgress",
    "LossWarning",
    "LOSS_AVERSION_MULTIPLIER",

    "RewardSystem",
    "Reward",
    "MysteryBox",
    "RewardType",
    "RewardTier",
    "RewardStats",
    "JACKPOT_CHANCE",

    "NewAchievementSystem",
    "Achievement",
    "UserAchievement",
    "AchievementTier",
    "AchievementCategory",
    "AchievementStats",
    "ACHIEVEMENTS",

    "PsychologicalEngine",
    "SessionResult",
    "DailyMotivation",
    "PsychologicalStats",
    "create_psychological_engine",

    # Legacy modules (backward compatibility)
    "XPSystem",
    "calculate_level",
    "StreakManager",
    "AchievementSystem",
    "MotivationEngine",
    "LEGACY_AVAILABLE",
]
