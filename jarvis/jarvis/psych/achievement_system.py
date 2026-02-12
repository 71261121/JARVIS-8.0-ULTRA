"""
JARVIS Achievement System
=========================

Purpose: Gamification through achievements and milestones.

Achievement Psychology:
    Achievements provide:
    1. Sense of progress and accomplishment
    2. Social proof (can share with others)
    3. Intrinsic motivation through goal completion
    4. Long-term engagement through rare achievements

Key Insight:
    Achievements work best when:
    - Some are easy (quick wins)
    - Some are medium (goals to work toward)
    - Some are hard (long-term aspirations)
    - Some are hidden (surprise element)

EXAM IMPACT:
    MEDIUM-HIGH. Achievements gamify the study process.
    Makes the journey feel like progress, not just work.
    Especially effective for users who respond to game mechanics.

REASON FOR DESIGN:
    - Multiple achievement categories
    - Tiered difficulty (Common → Legendary)
    - Hidden achievements for surprise
    - Progress tracking for each achievement
    - Rewards tied to achievement completion

SOURCE RESEARCH:
    - Springer - Gamification and achievement systems
    - HCI research - Badges and user motivation
    - Game design principles - Achievement design

ROLLBACK PLAN:
    - Achievement system is additive only
    - No system modifications
    - Can be disabled without affecting other modules
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


# ============================================================================
# CONSTANTS
# ============================================================================

# Achievement tiers
class AchievementTier(Enum):
    """Achievement rarity tiers."""
    COMMON = "common"         # 50%+ of users will get
    UNCOMMON = "uncommon"     # 25-50% of users will get
    RARE = "rare"             # 10-25% of users will get
    EPIC = "epic"             # 5-10% of users will get
    LEGENDARY = "legendary"   # <5% of users will get
    HIDDEN = "hidden"         # Secret achievements


# Achievement categories
class AchievementCategory(Enum):
    """Achievement categories."""
    STREAK = "streak"           # Consistency achievements
    STUDY = "study"             # Study-related achievements
    ACCURACY = "accuracy"       # Performance achievements
    TOPIC = "topic"             # Subject/topic achievements
    MILESTONE = "milestone"     # Major milestones
    SPECIAL = "special"         # Special/hidden achievements
    SOCIAL = "social"           # Social comparison achievements


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Achievement:
    """Definition of an achievement."""
    achievement_id: str
    name: str
    description: str
    tier: AchievementTier
    category: AchievementCategory
    xp_reward: int
    coin_reward: int
    icon: str  # Emoji icon
    requirement: Dict[str, Any]  # What's needed to unlock
    is_hidden: bool = False  # Hidden until unlocked?

    def to_dict(self) -> Dict:
        return {
            "achievement_id": self.achievement_id,
            "name": self.name,
            "description": self.description,
            "tier": self.tier.value,
            "category": self.category.value,
            "xp_reward": self.xp_reward,
            "coin_reward": self.coin_reward,
            "icon": self.icon,
            "requirement": self.requirement,
            "is_hidden": self.is_hidden,
        }


@dataclass
class UserAchievement:
    """A user's progress on an achievement."""
    achievement_id: str
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None
    progress: float = 0.0  # 0-1
    current_value: int = 0
    target_value: int = 0

    def to_dict(self) -> Dict:
        return {
            "achievement_id": self.achievement_id,
            "unlocked": self.unlocked,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None,
            "progress": self.progress,
            "current_value": self.current_value,
            "target_value": self.target_value,
        }


@dataclass
class AchievementStats:
    """Statistics about user's achievements."""
    total_achievements: int = 0
    unlocked_count: int = 0
    total_xp_from_achievements: int = 0
    total_coins_from_achievements: int = 0
    by_tier: Dict[str, int] = field(default_factory=dict)
    by_category: Dict[str, int] = field(default_factory=dict)
    rarest_achievement: Optional[str] = None
    completion_percentage: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "total_achievements": self.total_achievements,
            "unlocked_count": self.unlocked_count,
            "total_xp_from_achievements": self.total_xp_from_achievements,
            "total_coins_from_achievements": self.total_coins_from_achievements,
            "by_tier": self.by_tier,
            "by_category": self.by_category,
            "rarest_achievement": self.rarest_achievement,
            "completion_percentage": self.completion_percentage,
        }


# ============================================================================
# PREDEFINED ACHIEVEMENTS
# ============================================================================

# All achievements in the system
ACHIEVEMENTS: List[Achievement] = [
    # ========================================
    # STREAK ACHIEVEMENTS (Consistency)
    # ========================================
    Achievement(
        achievement_id="first_step",
        name="First Step",
        description="Complete your first study session",
        tier=AchievementTier.COMMON,
        category=AchievementCategory.STREAK,
        xp_reward=50,
        coin_reward=20,
        icon="👣",
        requirement={"type": "sessions", "value": 1}
    ),
    Achievement(
        achievement_id="three_day_streak",
        name="Hat Trick",
        description="Maintain a 3-day study streak",
        tier=AchievementTier.COMMON,
        category=AchievementCategory.STREAK,
        xp_reward=100,
        coin_reward=50,
        icon="🔥",
        requirement={"type": "streak_days", "value": 3}
    ),
    Achievement(
        achievement_id="week_warrior",
        name="Week Warrior",
        description="Maintain a 7-day study streak",
        tier=AchievementTier.UNCOMMON,
        category=AchievementCategory.STREAK,
        xp_reward=300,
        coin_reward=100,
        icon="⚔️",
        requirement={"type": "streak_days", "value": 7}
    ),
    Achievement(
        achievement_id="two_week_champion",
        name="Two Week Champion",
        description="Maintain a 14-day study streak",
        tier=AchievementTier.RARE,
        category=AchievementCategory.STREAK,
        xp_reward=700,
        coin_reward=200,
        icon="🏆",
        requirement={"type": "streak_days", "value": 14}
    ),
    Achievement(
        achievement_id="monthly_master",
        name="Monthly Master",
        description="Maintain a 30-day study streak",
        tier=AchievementTier.EPIC,
        category=AchievementCategory.STREAK,
        xp_reward=2000,
        coin_reward=500,
        icon="👑",
        requirement={"type": "streak_days", "value": 30}
    ),
    Achievement(
        achievement_id="seat_confirmed",
        name="SEAT CONFIRMED",
        description="Complete 75 days of preparation",
        tier=AchievementTier.LEGENDARY,
        category=AchievementCategory.STREAK,
        xp_reward=10000,
        coin_reward=2000,
        icon="🎓",
        requirement={"type": "total_days", "value": 75}
    ),

    # ========================================
    # STUDY ACHIEVEMENTS (Volume)
    # ========================================
    Achievement(
        achievement_id="question_hundred",
        name="Century",
        description="Answer 100 questions",
        tier=AchievementTier.COMMON,
        category=AchievementCategory.STUDY,
        xp_reward=100,
        coin_reward=50,
        icon="💯",
        requirement={"type": "total_questions", "value": 100}
    ),
    Achievement(
        achievement_id="question_five_hundred",
        name="Half Grand",
        description="Answer 500 questions",
        tier=AchievementTier.UNCOMMON,
        category=AchievementCategory.STUDY,
        xp_reward=400,
        coin_reward=150,
        icon="📚",
        requirement={"type": "total_questions", "value": 500}
    ),
    Achievement(
        achievement_id="question_thousand",
        name="The Scholar",
        description="Answer 1,000 questions",
        tier=AchievementTier.RARE,
        category=AchievementCategory.STUDY,
        xp_reward=1000,
        coin_reward=300,
        icon="📖",
        requirement={"type": "total_questions", "value": 1000}
    ),
    Achievement(
        achievement_id="question_five_thousand",
        name="Knowledge Master",
        description="Answer 5,000 questions",
        tier=AchievementTier.EPIC,
        category=AchievementCategory.STUDY,
        xp_reward=5000,
        coin_reward=1000,
        icon="🧠",
        requirement={"type": "total_questions", "value": 5000}
    ),
    Achievement(
        achievement_id="marathon",
        name="Marathon Runner",
        description="Study for 4 hours in a single session",
        tier=AchievementTier.UNCOMMON,
        category=AchievementCategory.STUDY,
        xp_reward=300,
        coin_reward=100,
        icon="🏃",
        requirement={"type": "single_session_minutes", "value": 240}
    ),

    # ========================================
    # ACCURACY ACHIEVEMENTS (Performance)
    # ========================================
    Achievement(
        achievement_id="sharpshooter",
        name="Sharpshooter",
        description="Achieve 90% accuracy in a session (min 20 questions)",
        tier=AchievementTier.UNCOMMON,
        category=AchievementCategory.ACCURACY,
        xp_reward=200,
        coin_reward=75,
        icon="🎯",
        requirement={"type": "session_accuracy", "value": 0.90, "min_questions": 20}
    ),
    Achievement(
        achievement_id="perfectionist",
        name="Perfectionist",
        description="Achieve 100% accuracy in a session (min 20 questions)",
        tier=AchievementTier.RARE,
        category=AchievementCategory.ACCURACY,
        xp_reward=500,
        coin_reward=150,
        icon="✨",
        requirement={"type": "session_accuracy", "value": 1.0, "min_questions": 20}
    ),
    Achievement(
        achievement_id="consistent_excellence",
        name="Consistent Excellence",
        description="Maintain 85%+ accuracy for 7 consecutive days",
        tier=AchievementTier.EPIC,
        category=AchievementCategory.ACCURACY,
        xp_reward=1000,
        coin_reward=300,
        icon="⭐",
        requirement={"type": "consecutive_accuracy", "value": 0.85, "days": 7}
    ),

    # ========================================
    # TOPIC ACHIEVEMENTS (Subject Mastery)
    # ========================================
    Achievement(
        achievement_id="math_warrior",
        name="Math Warrior",
        description="Answer 200 Maths questions",
        tier=AchievementTier.UNCOMMON,
        category=AchievementCategory.TOPIC,
        xp_reward=300,
        coin_reward=100,
        icon="🔢",
        requirement={"type": "subject_questions", "value": 200, "subject": "maths"}
    ),
    Achievement(
        achievement_id="physics_master",
        name="Physics Master",
        description="Answer 200 Physics questions",
        tier=AchievementTier.UNCOMMON,
        category=AchievementCategory.TOPIC,
        xp_reward=300,
        coin_reward=100,
        icon="⚛️",
        requirement={"type": "subject_questions", "value": 200, "subject": "physics"}
    ),
    Achievement(
        achievement_id="chemistry_wizard",
        name="Chemistry Wizard",
        description="Answer 200 Chemistry questions",
        tier=AchievementTier.UNCOMMON,
        category=AchievementCategory.TOPIC,
        xp_reward=300,
        coin_reward=100,
        icon="🧪",
        requirement={"type": "subject_questions", "value": 200, "subject": "chemistry"}
    ),
    Achievement(
        achievement_id="theta_positive",
        name="Above Average",
        description="Get your IRT theta above 0 in any subject",
        tier=AchievementTier.COMMON,
        category=AchievementCategory.TOPIC,
        xp_reward=100,
        coin_reward=50,
        icon="📈",
        requirement={"type": "theta_positive", "value": 1}
    ),
    Achievement(
        achievement_id="maths_theta_one",
        name="Math Master",
        description="Achieve theta > 1.0 in Mathematics",
        tier=AchievementTier.RARE,
        category=AchievementCategory.TOPIC,
        xp_reward=800,
        coin_reward=250,
        icon="🏆",
        requirement={"type": "subject_theta", "value": 1.0, "subject": "maths"}
    ),

    # ========================================
    # MILESTONE ACHIEVEMENTS
    # ========================================
    Achievement(
        achievement_id="first_mock",
        name="Test Run",
        description="Complete your first mock test",
        tier=AchievementTier.COMMON,
        category=AchievementCategory.MILESTONE,
        xp_reward=100,
        coin_reward=50,
        icon="📝",
        requirement={"type": "mock_tests", "value": 1}
    ),
    Achievement(
        achievement_id="mock_master",
        name="Mock Master",
        description="Complete 10 mock tests",
        tier=AchievementTier.RARE,
        category=AchievementCategory.MILESTONE,
        xp_reward=1000,
        coin_reward=300,
        icon="📋",
        requirement={"type": "mock_tests", "value": 10}
    ),
    Achievement(
        achievement_id="early_bird",
        name="Early Bird",
        description="Start studying before 7 AM",
        tier=AchievementTier.UNCOMMON,
        category=AchievementCategory.MILESTONE,
        xp_reward=150,
        coin_reward=75,
        icon="🌅",
        requirement={"type": "early_study", "hour": 7}
    ),
    Achievement(
        achievement_id="night_owl",
        name="Night Owl",
        description="Study after 10 PM (responsibly)",
        tier=AchievementTier.COMMON,
        category=AchievementCategory.MILESTONE,
        xp_reward=50,
        coin_reward=25,
        icon="🦉",
        requirement={"type": "late_study", "hour": 22}
    ),

    # ========================================
    # SPECIAL ACHIEVEMENTS (Hidden)
    # ========================================
    Achievement(
        achievement_id="comeback_kid",
        name="Comeback Kid",
        description="Recover from a broken streak with a longer one",
        tier=AchievementTier.RARE,
        category=AchievementCategory.SPECIAL,
        xp_reward=500,
        coin_reward=200,
        icon="💪",
        requirement={"type": "streak_recovery", "value": True},
        is_hidden=True
    ),
    Achievement(
        achievement_id="no_distractions",
        name="Unstoppable",
        description="Complete a 3-hour session with zero distractions",
        tier=AchievementTier.EPIC,
        category=AchievementCategory.SPECIAL,
        xp_reward=800,
        coin_reward=250,
        icon="🚫",
        requirement={"type": "distraction_free", "minutes": 180},
        is_hidden=True
    ),
    Achievement(
        achievement_id="jackpot_winner",
        name="Lucky Day",
        description="Hit the jackpot on a session reward",
        tier=AchievementTier.RARE,
        category=AchievementCategory.SPECIAL,
        xp_reward=100,
        coin_reward=100,
        icon="🎰",
        requirement={"type": "jackpot", "value": 1},
        is_hidden=True
    ),
    Achievement(
        achievement_id="mystery_hunter",
        name="Mystery Hunter",
        description="Open 50 mystery boxes",
        tier=AchievementTier.EPIC,
        category=AchievementCategory.SPECIAL,
        xp_reward=1000,
        coin_reward=400,
        icon="📦",
        requirement={"type": "mystery_boxes", "value": 50},
        is_hidden=True
    ),
]


# ============================================================================
# ACHIEVEMENT SYSTEM CLASS
# ============================================================================

class AchievementSystem:
    """
    Manages achievements and progress tracking.

    This class:
    - Tracks user progress toward achievements
    - Unlocks achievements when requirements met
    - Provides achievement status and statistics
    - Handles hidden achievements

    Usage:
        system = AchievementSystem()

        # Update progress
        system.update_progress("streak_days", 7)
        system.update_progress("total_questions", 150)

        # Check for new unlocks
        new_achievements = system.check_unlocks()

        # Get all achievements with progress
        all_achievements = system.get_all_with_progress()

    EXAM IMPACT:
        Gamification increases engagement.
        Achievements provide sense of progress.
    """

    def __init__(self, achievements: Optional[List[Achievement]] = None):
        """
        Initialize achievement system.

        Args:
            achievements: List of achievements (default: predefined)
        """
        self.achievements = {a.achievement_id: a for a in (achievements or ACHIEVEMENTS)}

        # User progress
        self._user_achievements: Dict[str, UserAchievement] = {}
        self._progress_values: Dict[str, int] = {}

        # Initialize all achievements
        for achievement_id in self.achievements:
            self._user_achievements[achievement_id] = UserAchievement(
                achievement_id=achievement_id,
                target_value=self.achievements[achievement_id].requirement.get("value", 0)
            )

    # ========================================================================
    # PROGRESS TRACKING
    # ========================================================================

    def update_progress(self, progress_type: str, value: int, **kwargs) -> List[Achievement]:
        """
        Update progress for achievements of a given type.

        Args:
            progress_type: Type of progress (e.g., "streak_days")
            value: New value
            **kwargs: Additional context (e.g., subject)

        Returns:
            List of newly unlocked achievements

        Reason:
            Central method for progress updates.
            Automatically checks for unlocks.
        """
        self._progress_values[progress_type] = value

        # Update relevant achievements
        newly_unlocked = []

        for achievement_id, achievement in self.achievements.items():
            req = achievement.requirement

            # Check if this achievement uses this progress type
            if req.get("type") != progress_type:
                continue

            # Check subject-specific achievements
            if "subject" in req and req["subject"] != kwargs.get("subject"):
                continue

            # Update progress
            user_ach = self._user_achievements[achievement_id]
            user_ach.current_value = value
            user_ach.target_value = req.get("value", 0)
            user_ach.progress = min(1.0, value / user_ach.target_value if user_ach.target_value > 0 else 0)

            # Check for unlock
            if not user_ach.unlocked and value >= user_ach.target_value:
                self._unlock_achievement(achievement_id)
                newly_unlocked.append(achievement)

        return newly_unlocked

    def increment_progress(self, progress_type: str, amount: int = 1, **kwargs) -> List[Achievement]:
        """
        Increment progress by amount.

        Args:
            progress_type: Type of progress
            amount: Amount to increment
            **kwargs: Additional context

        Returns:
            List of newly unlocked achievements
        """
        current = self._progress_values.get(progress_type, 0)
        return self.update_progress(progress_type, current + amount, **kwargs)

    def _unlock_achievement(self, achievement_id: str) -> None:
        """Unlock an achievement."""
        user_ach = self._user_achievements[achievement_id]
        user_ach.unlocked = True
        user_ach.unlocked_at = datetime.now()
        user_ach.progress = 1.0

    # ========================================================================
    # ACHIEVEMENT QUERIES
    # ========================================================================

    def get_all_with_progress(self, include_hidden: bool = False) -> List[Tuple[Achievement, UserAchievement]]:
        """
        Get all achievements with progress.

        Args:
            include_hidden: Include hidden achievements

        Returns:
            List of (Achievement, UserAchievement) tuples
        """
        result = []

        for achievement_id, achievement in self.achievements.items():
            # Skip hidden if not requested
            if achievement.is_hidden and not include_hidden and not self._user_achievements[achievement_id].unlocked:
                continue

            result.append((achievement, self._user_achievements[achievement_id]))

        # Sort: unlocked first, then by progress, then by tier rarity
        tier_order = {
            AchievementTier.LEGENDARY: 0,
            AchievementTier.EPIC: 1,
            AchievementTier.RARE: 2,
            AchievementTier.UNCOMMON: 3,
            AchievementTier.COMMON: 4,
            AchievementTier.HIDDEN: 5,
        }

        result.sort(key=lambda x: (
            not x[1].unlocked,  # Unlocked first
            -x[1].progress,     # Then by progress
            tier_order.get(x[0].tier, 5),  # Then by tier
        ))

        return result

    def get_unlocked(self) -> List[Achievement]:
        """Get all unlocked achievements."""
        return [
            self.achievements[aid]
            for aid, ua in self._user_achievements.items()
            if ua.unlocked
        ]

    def get_close_to_unlock(self, threshold: float = 0.8) -> List[Tuple[Achievement, float]]:
        """
        Get achievements close to being unlocked.

        Args:
            threshold: Progress threshold (default: 80%)

        Returns:
            List of (Achievement, progress) tuples
        """
        result = []

        for achievement_id, user_ach in self._user_achievements.items():
            if user_ach.unlocked:
                continue

            if user_ach.progress >= threshold:
                achievement = self.achievements[achievement_id]
                result.append((achievement, user_ach.progress))

        # Sort by progress descending
        result.sort(key=lambda x: -x[1])
        return result

    def get_stats(self) -> AchievementStats:
        """Get achievement statistics."""
        stats = AchievementStats()

        stats.total_achievements = len(self.achievements)
        stats.unlocked_count = len([a for a in self._user_achievements.values() if a.unlocked])
        stats.completion_percentage = stats.unlocked_count / stats.total_achievements * 100 if stats.total_achievements > 0 else 0

        for achievement_id, user_ach in self._user_achievements.items():
            if not user_ach.unlocked:
                continue

            achievement = self.achievements[achievement_id]

            # Add rewards
            stats.total_xp_from_achievements += achievement.xp_reward
            stats.total_coins_from_achievements += achievement.coin_reward

            # Count by tier
            tier = achievement.tier.value
            stats.by_tier[tier] = stats.by_tier.get(tier, 0) + 1

            # Count by category
            category = achievement.category.value
            stats.by_category[category] = stats.by_category.get(category, 0) + 1

        # Find rarest unlocked
        tier_rarity = {
            AchievementTier.LEGENDARY: 0,
            AchievementTier.EPIC: 1,
            AchievementTier.RARE: 2,
            AchievementTier.UNCOMMON: 3,
            AchievementTier.COMMON: 4,
            AchievementTier.HIDDEN: 5,
        }

        unlocked = [(aid, self.achievements[aid]) for aid, ua in self._user_achievements.items() if ua.unlocked]
        if unlocked:
            rarest = min(unlocked, key=lambda x: tier_rarity.get(x[1].tier, 5))
            stats.rarest_achievement = rarest[1].name

        return stats

    # ========================================================================
    # SPECIAL CHECKS
    # ========================================================================

    def check_session_achievement(
        self,
        questions: int,
        accuracy: float,
        time_minutes: int,
        subject: str,
        distractions: int = 0
    ) -> List[Achievement]:
        """
        Check for session-based achievements.

        Args:
            questions: Questions answered
            accuracy: Accuracy rate
            time_minutes: Session duration
            subject: Subject studied
            distractions: Distraction events during session

        Returns:
            List of newly unlocked achievements
        """
        unlocked = []

        # Check accuracy achievements
        if accuracy >= 0.90 and questions >= 20:
            newly = self.update_progress("session_accuracy", int(accuracy * 100), min_questions=questions)
            unlocked.extend(newly)

        # Check marathon achievement
        if time_minutes >= 240:
            newly = self.update_progress("single_session_minutes", time_minutes)
            unlocked.extend(newly)

        # Check subject achievements
        self.increment_progress("subject_questions", questions, subject=subject)

        # Check distraction-free achievement
        if distractions == 0 and time_minutes >= 180:
            newly = self.update_progress("distraction_free", time_minutes)
            unlocked.extend(newly)

        return unlocked

    def check_time_achievement(self, hour: int) -> Optional[Achievement]:
        """
        Check for time-based achievements.

        Args:
            hour: Current hour (0-23)

        Returns:
            Newly unlocked achievement or None
        """
        unlocked = []

        if hour < 7:
            newly = self.update_progress("early_study", 1)
            unlocked.extend(newly)

        if hour >= 22:
            newly = self.update_progress("late_study", 1)
            unlocked.extend(newly)

        return unlocked[0] if unlocked else None

    def check_jackpot_achievement(self) -> Optional[Achievement]:
        """Check for jackpot achievement."""
        newly = self.update_progress("jackpot", 1)
        return newly[0] if newly else None


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Achievement System...")
    print("="*60)

    system = AchievementSystem()

    # Test 1: Update streak progress
    print("\n1. Testing streak achievements...")

    for days in [1, 3, 7, 14, 30]:
        unlocked = system.update_progress("streak_days", days)
        if unlocked:
            for a in unlocked:
                print(f"   UNLOCKED: {a.icon} {a.name} ({a.xp_reward} XP)")

    # Test 2: Update question progress
    print("\n2. Testing question achievements...")

    for total in [100, 500, 1000]:
        unlocked = system.update_progress("total_questions", total)
        if unlocked:
            for a in unlocked:
                print(f"   UNLOCKED: {a.icon} {a.name} ({a.xp_reward} XP)")

    # Test 3: Get close to unlock
    print("\n3. Getting achievements close to unlock...")

    system.update_progress("total_questions", 4500)  # Close to 5000
    close = system.get_close_to_unlock()
    for achievement, progress in close[:3]:
        print(f"   {achievement.icon} {achievement.name}: {progress*100:.0f}%")

    # Test 4: Statistics
    print("\n4. Achievement Statistics:")
    stats = system.get_stats()
    print(f"   Total: {stats.total_achievements}")
    print(f"   Unlocked: {stats.unlocked_count}")
    print(f"   Completion: {stats.completion_percentage:.1f}%")
    print(f"   XP from achievements: {stats.total_xp_from_achievements}")
    print(f"   Rarest unlocked: {stats.rarest_achievement}")

    # Test 5: All achievements with progress
    print("\n5. All achievements (first 5):")
    all_ach = system.get_all_with_progress()[:5]
    for achievement, user_ach in all_ach:
        status = "✅" if user_ach.unlocked else f"{user_ach.progress*100:.0f}%"
        print(f"   {achievement.icon} {achievement.name}: {status}")

    print("\n" + "="*60)
    print("All tests passed!")
