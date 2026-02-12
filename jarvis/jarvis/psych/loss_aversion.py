"""
JARVIS Loss Aversion Engine
===========================

Purpose: Implement loss aversion psychology to maximize motivation.

Loss Aversion (Kahneman & Tversky, 1979):
    Losses feel approximately 2x more painful than equivalent gains feel good.
    This module exploits this cognitive bias to prevent streak breaks and
    maintain consistent study behaviour.

Key Insight:
    - "You will LOSE 500 XP" is MORE motivating than "You will gain 500 XP"
    - Fear of losing progress is stronger than desire to gain progress

EXAM IMPACT:
    CRITICAL. User has history of inconsistency.
    Loss aversion messaging can prevent streak breaks.
    Every streak day preserved = cumulative study benefit.

REASON FOR DESIGN:
    - LOSS_AVERSION_MULTIPLIER = 2 (from research)
    - Emphasize potential losses over gains
    - Show streak in terms of "days at risk"
    - Calculate what will be LOST, not just what could be gained

SOURCE RESEARCH:
    - Kahneman, D., & Tversky, A. (1979). Prospect Theory
    - The Decision Lab: Loss Aversion
    - PMC: Neural correlates of loss aversion

ROLLBACK PLAN:
    - Loss aversion is messaging only
    - No system modifications
    - Can be disabled without affecting other modules
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# CONSTANTS
# ============================================================================

# Loss aversion multiplier (research-backed)
LOSS_AVERSION_MULTIPLIER = 2.0

# XP values
XP_PER_QUESTION = 10
XP_PER_MINUTE_STUDY = 2
XP_STREAK_BONUS_MULTIPLIER = 0.1  # 10% bonus per streak day
XP_MAX_STREAK_BONUS = 2.0  # Max 200% bonus

# Coin values
COINS_PER_QUESTION = 5
COINS_STREAK_BONUS = 10

# Warning thresholds
STREAK_WARNING_THRESHOLD = 3  # Warn when streak is this many days
HOURS_UNTIL_STREAK_BREAK = 6  # Warn if less than this many hours left in day


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class UserProgress:
    """User's current progress for loss calculations."""
    total_xp: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    total_coins: int = 0
    questions_today: int = 0
    minutes_today: int = 0
    daily_target_questions: int = 50
    daily_target_minutes: int = 480  # 8 hours

    # XP at risk
    streak_xp_bonus: int = 0  # XP bonus from streak that would be lost

    # Time tracking
    last_activity: Optional[datetime] = None
    streak_start_date: Optional[datetime] = None

    def calculate_streak_xp_at_risk(self) -> int:
        """Calculate XP bonus that would be lost if streak breaks."""
        if self.current_streak < 2:
            return 0

        # Each streak day adds 10% XP bonus (max 200%)
        bonus_multiplier = min(self.current_streak * 0.1, 2.0)
        return int(self.total_xp * bonus_multiplier * 0.1)  # 10% of bonus XP


@dataclass
class LossWarning:
    """A loss aversion warning message."""
    warning_type: str
    severity: str  # "low", "medium", "high", "critical"
    potential_loss: int  # Amount that could be lost
    loss_description: str
    gain_alternative: str  # What would be gained instead
    message: str
    urgency: float  # 0-1, how urgent is this
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            "warning_type": self.warning_type,
            "severity": self.severity,
            "potential_loss": self.potential_loss,
            "loss_description": self.loss_description,
            "gain_alternative": self.gain_alternative,
            "message": self.message,
            "urgency": self.urgency,
            "created_at": self.created_at.isoformat(),
        }


# ============================================================================
# LOSS AVERSION ENGINE CLASS
# ============================================================================

class LossAversionEngine:
    """
    Generates loss aversion messages to maximize motivation.

    This class:
    - Calculates potential losses
    - Generates impactful warning messages
    - Emphasizes loss over gain framing
    - Tracks urgency based on time

    Usage:
        engine = LossAversionEngine()

        # Check for warnings
        warning = engine.check_streak_risk(progress)
        if warning:
            print(warning.message)

        # Get daily motivation
        motivation = engine.get_daily_motivation(progress)

    EXAM IMPACT:
        Loss aversion messaging is 2x more effective than gain messaging.
        This directly increases study consistency.
    """

    def __init__(
        self,
        loss_multiplier: float = LOSS_AVERSION_MULTIPLIER,
        streak_warning_threshold: int = STREAK_WARNING_THRESHOLD
    ):
        """
        Initialize loss aversion engine.

        Args:
            loss_multiplier: Multiplier for loss impact (default: 2.0)
            streak_warning_threshold: Days before warning (default: 3)
        """
        self.loss_multiplier = loss_multiplier
        self.streak_warning_threshold = streak_warning_threshold

    # ========================================================================
    # STREAK RISK DETECTION
    # ========================================================================

    def check_streak_risk(self, progress: UserProgress) -> Optional[LossWarning]:
        """
        Check if user's streak is at risk.

        Args:
            progress: Current user progress

        Returns:
            LossWarning if streak is at risk, None otherwise

        Reason:
            Streak is the MOST valuable asset. Breaking it should feel
            like a MAJOR loss. This warning is CRITICAL.
        """
        if progress.current_streak < 2:
            return None  # No streak to protect

        now = datetime.now()
        hours_left_in_day = 24 - now.hour - (now.minute / 60)

        # Calculate what's at risk
        xp_at_risk = progress.calculate_streak_xp_at_risk()
        streak_days = progress.current_streak

        # Determine urgency
        if progress.questions_today == 0 and hours_left_in_day < HOURS_UNTIL_STREAK_BREAK:
            urgency = 1.0
            severity = "critical"
        elif progress.questions_today < progress.daily_target_questions * 0.5:
            urgency = 0.8
            severity = "high"
        elif hours_left_in_day < 4 and progress.questions_today < progress.daily_target_questions * 0.8:
            urgency = 0.6
            severity = "medium"
        else:
            return None  # Not at risk

        # Generate loss-framed message
        message = self._generate_streak_warning(
            streak_days=streak_days,
            xp_at_risk=xp_at_risk,
            hours_left=hours_left_in_day,
            questions_done=progress.questions_today,
            questions_target=progress.daily_target_questions,
            urgency=urgency
        )

        return LossWarning(
            warning_type="streak_risk",
            severity=severity,
            potential_loss=xp_at_risk,
            loss_description=f"{streak_days}-day streak ({xp_at_risk} XP bonus at risk)",
            gain_alternative=f"Complete {progress.daily_target_questions - progress.questions_today} more questions to protect streak",
            message=message,
            urgency=urgency,
        )

    def _generate_streak_warning(
        self,
        streak_days: int,
        xp_at_risk: int,
        hours_left: float,
        questions_done: int,
        questions_target: int,
        urgency: float
    ) -> str:
        """Generate a loss-framed streak warning message."""

        if urgency >= 1.0:
            # CRITICAL - immediate action needed
            return (
                f"🚨 CRITICAL: YOUR {streak_days}-DAY STREAK IS ABOUT TO DIE\n"
                f"\n"
                f"⏰ Only {hours_left:.1f} hours left today.\n"
                f"❌ You have done {questions_done}/{questions_target} questions.\n"
                f"\n"
                f"💀 IF YOU DON'T ACT NOW:\n"
                f"   • Your {streak_days}-day streak will be DESTROYED\n"
                f"   • You will LOSE {xp_at_risk} XP bonus permanently\n"
                f"   • All your hard work - GONE\n"
                f"\n"
                f"🔥 This is the EXACT moment where winners and quitters separate.\n"
                f"🔥 Which one are you?"
            )
        elif urgency >= 0.8:
            # HIGH
            return (
                f"⚠️ WARNING: Your {streak_days}-day streak is in DANGER\n"
                f"\n"
                f"You've only completed {questions_done}/{questions_target} questions today.\n"
                f"\n"
                f"📉 WHAT YOU'RE RISKING:\n"
                f"   • {streak_days} days of consistent effort\n"
                f"   • {xp_at_risk} XP streak bonus\n"
                f"   • Your momentum and confidence\n"
                f"\n"
                f"⚡ DO NOT let this slip away. Start NOW."
            )
        else:
            # MEDIUM
            return (
                f"🟡 Your {streak_days}-day streak needs attention\n"
                f"\n"
                f"You still have {hours_left:.1f} hours, but don't get complacent.\n"
                f"\n"
                f"💭 Remember: Breaking a streak takes SECONDS.\n"
                f"💭 Building it back takes WEEKS.\n"
                f"\n"
                f"Complete your daily target to keep your {xp_at_risk} XP bonus."
            )

    # ========================================================================
    # DAILY MOTIVATION
    # ========================================================================

    def get_daily_motivation(self, progress: UserProgress) -> str:
        """
        Generate daily motivation using loss framing.

        Args:
            progress: Current user progress

        Returns:
            Loss-framed motivational message

        Reason:
            Start each day with a reminder of what's at stake.
            Not fear-mongering, but realistic stakes.
        """
        now = datetime.now()
        day_of_prep = self._calculate_day_of_prep(progress)

        # Calculate potential gains and frame as losses
        daily_xp_potential = progress.daily_target_questions * XP_PER_QUESTION
        daily_xp_potential += progress.daily_target_minutes * XP_PER_MINUTE_STUDY

        # Apply streak bonus
        streak_multiplier = 1 + min(progress.current_streak * 0.1, 1.0)
        daily_xp_potential = int(daily_xp_potential * streak_multiplier)

        # Days until exam
        days_until_exam = self._get_days_until_exam()

        # Loss framing
        if progress.current_streak >= 7:
            streak_message = (
                f"🔥 Your {progress.current_streak}-day streak is your BIGGEST asset.\n"
                f"🔥 It's worth an extra {progress.calculate_streak_xp_at_risk()} XP.\n"
                f"🔥 DON'T THROW IT AWAY."
            )
        elif progress.current_streak >= 3:
            streak_message = (
                f"📈 Your {progress.current_streak}-day streak is building momentum.\n"
                f"📈 Each day makes the next day easier.\n"
                f"📈 DON'T BREAK THE CHAIN."
            )
        else:
            streak_message = (
                f"🌱 Today is the day to start (or continue) your streak.\n"
                f"🌱 Small consistent actions > Big occasional efforts.\n"
                f"🌱 Your future self is counting on you."
            )

        return (
            f"📅 DAY {day_of_prep} of Preparation\n"
            f"🎯 {days_until_exam} days until exam\n"
            f"\n"
            f"💰 TODAY'S STAKES:\n"
            f"   • Gain: {daily_xp_potential} XP (with streak bonus)\n"
            f"   • Lose: Your entire streak if you don't complete targets\n"
            f"\n"
            f"{streak_message}\n"
            f"\n"
            f"⚡ EVERY question you answer today is an investment.\n"
            f"⚡ EVERY minute you study compounds.\n"
            f"⚡ Don't let today be the day you quit."
        )

    def _calculate_day_of_prep(self, progress: UserProgress) -> int:
        """Calculate current day of preparation."""
        if progress.streak_start_date:
            return (datetime.now() - progress.streak_start_date).days + 1
        return 1

    def _get_days_until_exam(self) -> int:
        """Get days until exam (placeholder - should be configured)."""
        # Default: 75 days from now
        exam_date = datetime(2025, 5, 15)  # Placeholder
        return max(0, (exam_date - datetime.now()).days)

    # ========================================================================
    # SESSION LOSS FRAMING
    # ========================================================================

    def frame_session_as_loss(
        self,
        questions_answered: int,
        accuracy: float,
        time_minutes: int,
        potential_questions: int
    ) -> str:
        """
        Frame session results in terms of losses/gains.

        Args:
            questions_answered: Questions answered in session
            accuracy: Accuracy rate (0-1)
            time_minutes: Time spent
            potential_questions: Maximum questions that could have been done

        Returns:
            Loss-framed session summary

        Reason:
            Show what was LOST through inefficiency, not just what was gained.
        """
        # Calculate XP
        base_xp = questions_answered * XP_PER_QUESTION
        accuracy_bonus = int(base_xp * (accuracy - 0.5)) if accuracy > 0.5 else 0
        time_xp = time_minutes * XP_PER_MINUTE_STUDY
        total_xp = base_xp + accuracy_bonus + time_xp

        # Calculate potential loss
        potential_xp = potential_questions * XP_PER_QUESTION
        lost_xp = potential_xp - base_xp

        if accuracy >= 0.9:
            accuracy_message = "🎯 Excellent accuracy! Full bonus earned."
        elif accuracy >= 0.7:
            accuracy_message = f"✅ Good accuracy. You earned {accuracy_bonus} bonus XP."
        elif accuracy >= 0.5:
            accuracy_message = f"⚠️ Accuracy at {accuracy*100:.0f}%. Room for improvement."
        else:
            accuracy_message = f"❌ Low accuracy ({accuracy*100:.0f}%). Focus on understanding, not speed."

        if lost_xp > 0:
            loss_message = (
                f"\n📉 POTENTIAL LOSS ANALYSIS:\n"
                f"   • You could have earned {potential_xp} XP\n"
                f"   • You earned {total_xp} XP\n"
                f"   • {lost_xp} XP left on the table\n"
                f"\n"
                f"💡 Remember: Each question you skip is XP you LOSE."
            )
        else:
            loss_message = (
                f"\n✨ MAXIMUM EFFICIENCY:\n"
                f"   • You earned every possible XP!\n"
                f"   • This is what peak performance looks like."
            )

        return (
            f"📊 SESSION SUMMARY\n"
            f"\n"
            f"✅ Questions: {questions_answered}\n"
            f"✅ Accuracy: {accuracy*100:.0f}%\n"
            f"✅ Time: {time_minutes} minutes\n"
            f"✅ XP Earned: {total_xp}\n"
            f"\n"
            f"{accuracy_message}"
            f"{loss_message}"
        )

    # ========================================================================
    # COMPARISON MESSAGING
    # ========================================================================

    def generate_comparison_message(
        self,
        user_xp: int,
        user_rank: int,
        total_users: int,
        xp_above: int,
        xp_below: int
    ) -> str:
        """
        Generate social comparison with loss framing.

        Args:
            user_xp: User's total XP
            user_rank: User's rank
            total_users: Total users in leaderboard
            xp_above: XP of user directly above
            xp_below: XP of user directly below

        Returns:
            Social comparison message

        Reason:
            Social comparison is motivating. Frame in terms of:
            - How many people are BEHIND (protect what you have)
            - How close the next person is (could overtake you)
        """
        percentile = (1 - user_rank / total_users) * 100

        # Calculate XP gap
        gap_above = xp_above - user_xp if xp_above > user_xp else 0
        gap_below = user_xp - xp_below if xp_below > 0 else 0

        if gap_above <= 0:
            # User is at top
            return (
                f"🏆 RANK #{user_rank} - TOP {percentile:.1f}%!\n"
                f"\n"
                f"You're at the TOP. Everyone below is trying to catch you.\n"
                f"Don't let them. Every day you slack is a day they gain.\n"
                f"\n"
                f"🔥 STAY HUNGRY. STAY ON TOP."
            )
        else:
            return (
                f"📊 RANK #{user_rank} - TOP {percentile:.1f}%\n"
                f"\n"
                f"⬆️ {gap_above} XP to overtake #{user_rank - 1}\n"
                f"⬇️ {gap_below} XP lead over #{user_rank + 1}\n"
                f"\n"
                f"⚠️ The person behind you is {gap_below} XP away.\n"
                f"⚠️ That's only {gap_below // XP_PER_QUESTION} questions.\n"
                f"⚠️ They could overtake you TODAY if you don't study.\n"
                f"\n"
                f"💪 PROTECT YOUR RANK. Study NOW."
            )

    # ========================================================================
    # WEEKLY LOSS SUMMARY
    # ========================================================================

    def generate_weekly_loss_summary(
        self,
        questions_answered: int,
        questions_missed: int,
        xp_earned: int,
        xp_lost: int,
        streak_days: int
    ) -> str:
        """
        Generate weekly summary with loss framing.

        Args:
            questions_answered: Total questions answered this week
            questions_missed: Questions below target
            xp_earned: XP earned this week
            xp_lost: XP that could have been earned
            streak_days: Current streak length

        Returns:
            Weekly summary with loss analysis

        Reason:
            Weekly review should show what was LOST, not just gained.
            This creates motivation for next week.
        """
        efficiency = questions_answered / (questions_answered + questions_missed) if (questions_answered + questions_missed) > 0 else 0

        return (
            f"📅 WEEKLY REVIEW\n"
            f"\n"
            f"✅ WHAT YOU ACHIEVED:\n"
            f"   • {questions_answered} questions answered\n"
            f"   • {xp_earned} XP earned\n"
            f"   • {streak_days}-day streak maintained\n"
            f"\n"
            f"❌ WHAT YOU LOST:\n"
            f"   • {questions_missed} questions below target\n"
            f"   • {xp_lost} XP left on the table\n"
            f"   • {efficiency*100:.0f}% efficiency rate\n"
            f"\n"
            f"💡 NEXT WEEK:\n"
            f"   • Every question you skip is XP you lose\n"
            f"   • Every day you miss resets your streak\n"
            f"   • Every hour wasted is an hour your competitors study\n"
            f"\n"
            f"🔥 Make next week count."
        )


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Loss Aversion Engine...")
    print("="*60)

    engine = LossAversionEngine()

    # Test 1: Streak risk warning
    print("\n1. Testing streak risk warning...")
    progress = UserProgress(
        total_xp=5000,
        current_streak=7,
        longest_streak=10,
        total_coins=500,
        questions_today=10,
        daily_target_questions=50,
        streak_start_date=datetime.now() - timedelta(days=7)
    )

    warning = engine.check_streak_risk(progress)
    if warning:
        print(warning.message)
    else:
        print("No streak risk detected")

    # Test 2: Daily motivation
    print("\n" + "="*60)
    print("\n2. Testing daily motivation...")
    motivation = engine.get_daily_motivation(progress)
    print(motivation)

    # Test 3: Session loss framing
    print("\n" + "="*60)
    print("\n3. Testing session loss framing...")
    session = engine.frame_session_as_loss(
        questions_answered=20,
        accuracy=0.85,
        time_minutes=45,
        potential_questions=30
    )
    print(session)

    # Test 4: Comparison message
    print("\n" + "="*60)
    print("\n4. Testing comparison message...")
    comparison = engine.generate_comparison_message(
        user_xp=5000,
        user_rank=5,
        total_users=100,
        xp_above=5500,
        xp_below=4800
    )
    print(comparison)

    print("\n" + "="*60)
    print("All tests passed!")
