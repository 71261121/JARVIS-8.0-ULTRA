"""
JARVIS Psychological Engine
===========================

Purpose: Central integration of all psychological techniques.

This engine combines:
1. Loss Aversion - Fear of losing progress
2. Variable Rewards - Dopamine from unpredictability
3. Achievements - Gamification and milestones
4. Social Comparison - Leaderboard motivation

Key Insight:
    The COMBINATION of these techniques is more powerful than any single one.
    They work together to create:
    - Immediate motivation (variable rewards)
    - Sustained motivation (achievements)
    - Protective motivation (loss aversion)
    - Social motivation (comparison)

EXAM IMPACT:
    CRITICAL. Psychology is what makes the system effective.
    Without psychology, it's just a question tracker.
    WITH psychology, it's a behaviour modification system.

REASON FOR DESIGN:
    - Unified API for all psychological features
    - Event-driven progress tracking
    - Integrated reward calculation
    - Comprehensive statistics

SOURCE RESEARCH:
    - Kahneman & Tversky - Prospect Theory (Loss Aversion)
    - Skinner - Operant Conditioning (Variable Rewards)
    - Deterding - Gamification (Achievements)
    - Festinger - Social Comparison Theory

ROLLBACK PLAN:
    - All modules are independent
    - Can disable any component
    - No system modifications
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path

# Import components
from .loss_aversion import (
    LossAversionEngine,
    UserProgress,
    LossWarning,
)
from .reward_system import (
    RewardSystem,
    Reward,
    MysteryBox,
    RewardTier,
    RewardStats,
)
from .achievement_system import (
    AchievementSystem,
    Achievement,
    UserAchievement,
    AchievementStats,
    AchievementTier,
)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class SessionResult:
    """Result of a study session with psychological analysis."""
    # Core metrics
    questions_answered: int
    accuracy: float
    time_minutes: int
    subject: str

    # Rewards
    xp_earned: int
    coins_earned: int
    reward_tier: str
    reward_description: str

    # Achievements
    achievements_unlocked: List[str] = field(default_factory=list)

    # Loss warnings
    streak_warning: Optional[str] = None

    # Mystery boxes
    mystery_box_awarded: bool = False
    mystery_box_result: Optional[str] = None

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            "questions_answered": self.questions_answered,
            "accuracy": self.accuracy,
            "time_minutes": self.time_minutes,
            "subject": self.subject,
            "xp_earned": self.xp_earned,
            "coins_earned": self.coins_earned,
            "reward_tier": self.reward_tier,
            "reward_description": self.reward_description,
            "achievements_unlocked": self.achievements_unlocked,
            "streak_warning": self.streak_warning,
            "mystery_box_awarded": self.mystery_box_awarded,
            "mystery_box_result": self.mystery_box_result,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class DailyMotivation:
    """Daily motivational content."""
    loss_message: str
    reward_preview: str
    close_achievements: List[str]
    streak_status: str
    leaderboard_position: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "loss_message": self.loss_message,
            "reward_preview": self.reward_preview,
            "close_achievements": self.close_achievements,
            "streak_status": self.streak_status,
            "leaderboard_position": self.leaderboard_position,
        }


@dataclass
class PsychologicalStats:
    """Comprehensive psychological statistics."""
    # User progress
    total_xp: int = 0
    total_coins: int = 0
    current_streak: int = 0
    longest_streak: int = 0

    # Rewards
    jackpots_won: int = 0
    bonuses_won: int = 0
    mystery_boxes_opened: int = 0

    # Achievements
    achievements_unlocked: int = 0
    achievements_total: int = 0
    rarest_achievement: Optional[str] = None

    # Loss aversion
    times_warned: int = 0
    streaks_saved: int = 0

    def to_dict(self) -> Dict:
        return {
            "total_xp": self.total_xp,
            "total_coins": self.total_coins,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "jackpots_won": self.jackpots_won,
            "bonuses_won": self.bonuses_won,
            "mystery_boxes_opened": self.mystery_boxes_opened,
            "achievements_unlocked": self.achievements_unlocked,
            "achievements_total": self.achievements_total,
            "rarest_achievement": self.rarest_achievement,
            "times_warned": self.times_warned,
            "streaks_saved": self.streaks_saved,
        }


# ============================================================================
# PSYCHOLOGICAL ENGINE CLASS
# ============================================================================

class PsychologicalEngine:
    """
    Central integration of all psychological techniques.

    This class:
    - Coordinates all psychological components
    - Provides unified API
    - Tracks comprehensive statistics
    - Generates motivational content

    Usage:
        engine = PsychologicalEngine()

        # Process session
        result = engine.process_session(
            questions_answered=20,
            accuracy=0.85,
            time_minutes=45,
            subject="maths"
        )

        # Get daily motivation
        motivation = engine.get_daily_motivation()

        # Get statistics
        stats = engine.get_stats()

    EXAM IMPACT:
        This is the BRAIN of the motivational system.
        All techniques work together to maximize consistency.
    """

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        notification_callback: Optional[Callable] = None
    ):
        """
        Initialize psychological engine.

        Args:
            data_dir: Directory to store data
            notification_callback: Callback for notifications
        """
        self.data_dir = data_dir or Path("/sdcard/jarvis_data")
        self.notification_callback = notification_callback

        # Initialize components
        self.loss_engine = LossAversionEngine()
        self.reward_system = RewardSystem(data_dir=self.data_dir)
        self.achievement_system = AchievementSystem()

        # User progress
        self.progress = UserProgress()

        # Statistics
        self._stats = PsychologicalStats()
        self._stats.achievements_total = len(self.achievement_system.achievements)

        # Pending mystery boxes
        self._pending_boxes: List[MysteryBox] = []

    # ========================================================================
    # SESSION PROCESSING
    # ========================================================================

    def process_session(
        self,
        questions_answered: int,
        accuracy: float,
        time_minutes: int,
        subject: str,
        distractions: int = 0
    ) -> SessionResult:
        """
        Process a study session with all psychological effects.

        Args:
            questions_answered: Questions answered
            accuracy: Accuracy rate (0-1)
            time_minutes: Time spent
            subject: Subject studied
            distractions: Distraction events

        Returns:
            SessionResult with all psychological effects

        Reason:
            Main entry point for session processing.
            Applies all psychological techniques.
        """
        result = SessionResult(
            questions_answered=questions_answered,
            accuracy=accuracy,
            time_minutes=time_minutes,
            subject=subject,
            xp_earned=0,
            coins_earned=0,
            reward_tier="normal",
            reward_description="",
        )

        # 1. Calculate variable reward
        reward = self.reward_system.calculate_session_reward(
            questions_answered=questions_answered,
            accuracy=accuracy,
            time_minutes=time_minutes,
            streak_days=self.progress.current_streak,
            subject=subject
        )

        result.xp_earned = reward.amount
        result.coins_earned = reward.bonus_info.get("coins", 0)
        result.reward_tier = reward.tier.value
        result.reward_description = reward.description

        # Update progress
        self.progress.total_xp += reward.amount
        self.progress.total_coins += result.coins_earned
        self.progress.questions_today += questions_answered
        self.progress.minutes_today += time_minutes
        self.progress.last_activity = datetime.now()

        # 2. Check achievements
        unlocked = self.achievement_system.check_session_achievement(
            questions=questions_answered,
            accuracy=accuracy,
            time_minutes=time_minutes,
            subject=subject,
            distractions=distractions
        )

        result.achievements_unlocked = [a.name for a in unlocked]

        for achievement in unlocked:
            self.progress.total_xp += achievement.xp_reward
            self.progress.total_coins += achievement.coin_reward
            self._stats.achievements_unlocked += 1

            if self.notification_callback:
                self.notification_callback(
                    title=f"🏆 Achievement Unlocked: {achievement.name}",
                    message=achievement.description,
                    severity="success"
                )

        # 3. Award mystery box for good sessions
        if accuracy >= 0.8 and questions_answered >= 20:
            box = self.reward_system.create_mystery_box("session_complete")
            self._pending_boxes.append(box)
            result.mystery_box_awarded = True

        # 4. Check for jackpot achievement
        if reward.tier == RewardTier.JACKPOT:
            self.achievement_system.check_jackpot_achievement()
            self._stats.jackpots_won += 1

            if self.notification_callback:
                self.notification_callback(
                    title="🎰 JACKPOT!",
                    message=f"You hit the jackpot! {reward.amount} XP!",
                    severity="success"
                )

        # 5. Check time achievements
        hour = datetime.now().hour
        time_achievement = self.achievement_system.check_time_achievement(hour)
        if time_achievement:
            result.achievements_unlocked.append(time_achievement.name)

        # 6. Update question progress
        self.achievement_system.increment_progress("total_questions", questions_answered)

        # Update stats
        self._stats.total_xp = self.progress.total_xp
        self._stats.total_coins = self.progress.total_coins

        return result

    def open_mystery_box(self) -> Optional[Reward]:
        """
        Open the next pending mystery box.

        Returns:
            Reward from mystery box, or None if no boxes
        """
        if not self._pending_boxes:
            return None

        box = self._pending_boxes.pop(0)
        result = self.reward_system.open_mystery_box(box)

        # Add to progress
        if result.reward_type.value == "xp":
            self.progress.total_xp += result.amount
        elif result.reward_type.value == "coins":
            self.progress.total_coins += result.amount

        self._stats.mystery_boxes_opened += 1

        if self.notification_callback:
            self.notification_callback(
                title="📦 Mystery Box Opened!",
                message=result.description,
                severity="info"
            )

        return result

    # ========================================================================
    # STREAK MANAGEMENT
    # ========================================================================

    def update_streak(self, completed_today: bool) -> Tuple[int, bool]:
        """
        Update streak based on daily completion.

        Args:
            completed_today: Whether user completed daily target

        Returns:
            Tuple of (current_streak, streak_broken)

        Reason:
            Streak management is CRITICAL for consistency.
            Loss aversion applies here.
        """
        streak_broken = False

        if completed_today:
            if self.progress.last_activity:
                last_date = self.progress.last_activity.date()
                today = datetime.now().date()

                if last_date == today:
                    pass  # Same day, no change
                elif last_date == today - timedelta(days=1):
                    self.progress.current_streak += 1
                else:
                    # Streak broken
                    streak_broken = True
                    self.progress.current_streak = 1
            else:
                self.progress.current_streak = 1

            self.progress.longest_streak = max(
                self.progress.longest_streak,
                self.progress.current_streak
            )

            # Update achievement progress
            self.achievement_system.update_progress("streak_days", self.progress.current_streak)

        self._stats.current_streak = self.progress.current_streak
        self._stats.longest_streak = self.progress.longest_streak

        return self.progress.current_streak, streak_broken

    def check_streak_risk(self) -> Optional[LossWarning]:
        """
        Check if streak is at risk.

        Returns:
            LossWarning if at risk, None otherwise
        """
        warning = self.loss_engine.check_streak_risk(self.progress)

        if warning:
            self._stats.times_warned += 1

            if self.notification_callback:
                self.notification_callback(
                    title="⚠️ Streak at Risk!",
                    message=warning.message[:200],
                    severity="warning"
                )

        return warning

    # ========================================================================
    # MOTIVATION GENERATION
    # ========================================================================

    def get_daily_motivation(self) -> DailyMotivation:
        """
        Generate daily motivational content.

        Returns:
            DailyMotivation with all motivational elements
        """
        # Loss-framed motivation
        loss_message = self.loss_engine.get_daily_motivation(self.progress)

        # Reward preview
        reward_preview = self.reward_system.get_next_reward_preview(self.progress.current_streak)

        # Close achievements
        close_achievements = self.achievement_system.get_close_to_unlock(threshold=0.7)
        close_names = [f"{a.icon} {a.name} ({p*100:.0f}%)" for a, p in close_achievements[:3]]

        # Streak status
        if self.progress.current_streak >= 7:
            streak_status = f"🔥 {self.progress.current_streak}-day streak! Keep it burning!"
        elif self.progress.current_streak >= 3:
            streak_status = f"📈 {self.progress.current_streak}-day streak! Building momentum!"
        elif self.progress.current_streak >= 1:
            streak_status = f"🌱 {self.progress.current_streak}-day streak. Every day counts!"
        else:
            streak_status = "🎯 Start your streak today!"

        return DailyMotivation(
            loss_message=loss_message,
            reward_preview=reward_preview,
            close_achievements=close_names,
            streak_status=streak_status,
        )

    def get_session_motivation(self) -> str:
        """
        Get motivation before a session.

        Returns:
            Motivational message
        """
        lines = []

        # Reward preview
        lines.append("🎯 THIS SESSION'S POTENTIAL:")
        lines.append(self.reward_system.get_jackpot_probability())
        lines.append("")

        # Stakes
        if self.progress.current_streak > 0:
            lines.append(f"🔥 Your {self.progress.current_streak}-day streak is on the line.")
            lines.append(f"💰 {self.progress.calculate_streak_xp_at_risk()} XP bonus at risk.")
            lines.append("")

        # Close achievements
        close = self.achievement_system.get_close_to_unlock(threshold=0.8)
        if close:
            achievement, progress = close[0]
            lines.append(f"📊 Almost there: {achievement.name} ({progress*100:.0f}%)")
            lines.append("")

        lines.append("💪 Let's go! Every question counts.")

        return "\n".join(lines)

    # ========================================================================
    # STATISTICS
    # ========================================================================

    def get_stats(self) -> PsychologicalStats:
        """Get comprehensive statistics."""
        # Update from components
        reward_stats = self.reward_system.get_stats()
        achievement_stats = self.achievement_system.get_stats()

        self._stats.total_xp = self.progress.total_xp
        self._stats.total_coins = self.progress.total_coins
        self._stats.current_streak = self.progress.current_streak
        self._stats.longest_streak = self.progress.longest_streak
        self._stats.jackpots_won = reward_stats.jackpots_won
        self._stats.mystery_boxes_opened = reward_stats.mystery_boxes_opened
        self._stats.achievements_unlocked = achievement_stats.unlocked_count
        self._stats.rarest_achievement = achievement_stats.rarest_achievement

        return self._stats

    def get_progress(self) -> UserProgress:
        """Get current user progress."""
        return self.progress

    def get_achievements(self) -> List[Tuple[Achievement, UserAchievement]]:
        """Get all achievements with progress."""
        return self.achievement_system.get_all_with_progress()

    def get_pending_boxes_count(self) -> int:
        """Get count of pending mystery boxes."""
        return len(self._pending_boxes)

    # ========================================================================
    # COMPARISON
    # ========================================================================

    def generate_comparison(
        self,
        user_rank: int,
        total_users: int,
        xp_above: int,
        xp_below: int
    ) -> str:
        """
        Generate social comparison message.

        Args:
            user_rank: User's rank
            total_users: Total users
            xp_above: XP of user above
            xp_below: XP of user below

        Returns:
            Comparison message
        """
        return self.loss_engine.generate_comparison_message(
            user_xp=self.progress.total_xp,
            user_rank=user_rank,
            total_users=total_users,
            xp_above=xp_above,
            xp_below=xp_below
        )


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_psychological_engine(
    data_dir: Optional[Path] = None,
    notification_callback: Optional[Callable] = None
) -> PsychologicalEngine:
    """
    Create a fully configured psychological engine.

    Args:
        data_dir: Directory for data storage
        notification_callback: Callback for notifications

    Returns:
        Configured PsychologicalEngine
    """
    return PsychologicalEngine(
        data_dir=data_dir,
        notification_callback=notification_callback
    )


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Psychological Engine...")
    print("="*60)

    engine = create_psychological_engine()

    # Test 1: Process session
    print("\n1. Processing session...")
    result = engine.process_session(
        questions_answered=25,
        accuracy=0.88,
        time_minutes=45,
        subject="maths"
    )
    print(f"   XP: {result.xp_earned}")
    print(f"   Coins: {result.coins_earned}")
    print(f"   Tier: {result.reward_tier}")
    print(f"   Achievements: {result.achievements_unlocked}")

    # Test 2: Update streak
    print("\n2. Updating streak...")
    streak, broken = engine.update_streak(completed_today=True)
    print(f"   Current streak: {streak}")
    print(f"   Broken: {broken}")

    # Test 3: Daily motivation
    print("\n3. Daily motivation:")
    motivation = engine.get_daily_motivation()
    print(f"   Streak status: {motivation.streak_status}")
    print(f"   Close achievements: {motivation.close_achievements}")

    # Test 4: Open mystery box
    print("\n4. Mystery boxes...")
    print(f"   Pending boxes: {engine.get_pending_boxes_count()}")

    if engine.get_pending_boxes_count() > 0:
        reward = engine.open_mystery_box()
        print(f"   Opened: {reward.description[:50] if reward else 'None'}...")

    # Test 5: Statistics
    print("\n5. Statistics:")
    stats = engine.get_stats()
    print(f"   Total XP: {stats.total_xp}")
    print(f"   Total Coins: {stats.total_coins}")
    print(f"   Current Streak: {stats.current_streak}")
    print(f"   Achievements: {stats.achievements_unlocked}/{stats.achievements_total}")

    print("\n" + "="*60)
    print("All tests passed!")
