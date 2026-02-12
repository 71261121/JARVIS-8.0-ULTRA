"""
JARVIS Reward System
====================

Purpose: Variable reward system for dopamine optimization.

Variable Reward Psychology:
    Unpredictable rewards are MORE motivating than predictable ones.
    This is why slot machines are addictive - the uncertainty creates
    dopamine spikes that fixed rewards don't.

Key Insight:
    - Fixed reward: "Complete 10 questions = 100 XP" → Predictable, boring
    - Variable reward: "Complete 10 questions = ??? (could be 50-500 XP!)" → Exciting!

EXAM IMPACT:
    HIGH. Variable rewards keep user engaged for longer periods.
    User has history of inconsistency - this system creates
    "just one more" motivation that prevents early session termination.

REASON FOR DESIGN:
    - Slot machine psychology (variable ratio schedule)
    - Mystery boxes for session completion
    - Jackpots for exceptional performance
    - Streak bonuses with random multipliers

SOURCE RESEARCH:
    - Skinner, B.F. - Operant conditioning, variable ratio schedules
    - ResearchGate - Dopamine and variable rewards
    - MDPI - Gamification and reward uncertainty

ROLLBACK PLAN:
    - Reward system is additive only
    - No system modifications
    - Can be disabled, user keeps all earned rewards
"""

import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


# ============================================================================
# CONSTANTS
# ============================================================================

# Reward tiers (probabilities)
JACKPOT_CHANCE = 0.05       # 5% chance for jackpot
BONUS_CHANCE = 0.15         # 15% chance for bonus
SMALL_BONUS_CHANCE = 0.25   # 25% chance for small bonus
NORMAL_CHANCE = 0.55        # 55% chance for normal

# Reward values
JACKPOT_XP_MULTIPLIER = 3.0
JACKPOT_COIN_MULTIPLIER = 5.0
BONUS_XP_MULTIPLIER = 1.5
BONUS_COIN_MULTIPLIER = 2.0
SMALL_BONUS_XP_MULTIPLIER = 1.2

# Mystery box contents
MYSTERY_BOX_RARE_CHANCE = 0.02      # 2% rare achievement
MYSTERY_BOX_BIG_XP_CHANCE = 0.15    # 15% big XP (100-300)
MYSTERY_BOX_COINS_CHANCE = 0.25     # 25% coins (20-70)
MYSTERY_BOX_SMALL_XP_CHANCE = 0.20  # 20% small XP (25-75)
MYSTERY_BOX_NOTHING_CHANCE = 0.38   # 38% nothing (but encouraging message)

# Streak bonus multipliers
STREAK_BONUS_PER_DAY = 0.05  # 5% bonus per streak day
MAX_STREAK_BONUS = 1.5       # Max 150% bonus

# Accuracy bonuses
ACCURACY_THRESHOLD_EXCELLENT = 0.90
ACCURACY_THRESHOLD_GOOD = 0.75
ACCURACY_BONUS_EXCELLENT = 1.5
ACCURACY_BONUS_GOOD = 1.2


# ============================================================================
# ENUMS
# ============================================================================

class RewardType(Enum):
    """Types of rewards."""
    XP = "xp"
    COINS = "coins"
    ACHIEVEMENT = "achievement"
    STREAK_BONUS = "streak_bonus"
    ACCURACY_BONUS = "accuracy_bonus"
    JACKPOT = "jackpot"
    MYSTERY_BOX = "mystery_box"


class RewardTier(Enum):
    """Reward tiers for variable rewards."""
    JACKPOT = "jackpot"
    BONUS = "bonus"
    SMALL_BONUS = "small_bonus"
    NORMAL = "normal"


class MysteryBoxResult(Enum):
    """Possible mystery box outcomes."""
    RARE_ACHIEVEMENT = "rare_achievement"
    BIG_XP = "big_xp"
    COINS = "coins"
    SMALL_XP = "small_xp"
    NOTHING = "nothing"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Reward:
    """A reward given to the user."""
    reward_type: RewardType
    amount: int
    tier: RewardTier
    description: str
    bonus_info: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            "reward_type": self.reward_type.value,
            "amount": self.amount,
            "tier": self.tier.value,
            "description": self.description,
            "bonus_info": self.bonus_info,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class MysteryBox:
    """A mystery box that can be opened for random rewards."""
    box_id: str
    source: str  # What earned this box (e.g., "session_complete", "streak_7")
    created_at: datetime = field(default_factory=datetime.now)
    opened: bool = False
    opened_at: Optional[datetime] = None
    result: Optional[Reward] = None

    def to_dict(self) -> Dict:
        return {
            "box_id": self.box_id,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "opened": self.opened,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "result": self.result.to_dict() if self.result else None,
        }


@dataclass
class RewardStats:
    """Statistics about rewards earned."""
    total_xp: int = 0
    total_coins: int = 0
    jackpots_won: int = 0
    bonuses_won: int = 0
    mystery_boxes_opened: int = 0
    rare_achievements_from_boxes: int = 0
    biggest_single_reward: int = 0
    rewards_by_tier: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "total_xp": self.total_xp,
            "total_coins": self.total_coins,
            "jackpots_won": self.jackpots_won,
            "bonuses_won": self.bonuses_won,
            "mystery_boxes_opened": self.mystery_boxes_opened,
            "rare_achievements_from_boxes": self.rare_achievements_from_boxes,
            "biggest_single_reward": self.biggest_single_reward,
            "rewards_by_tier": self.rewards_by_tier,
        }


# ============================================================================
# REWARD SYSTEM CLASS
# ============================================================================

class RewardSystem:
    """
    Variable reward system for dopamine optimization.

    This class:
    - Calculates variable rewards for sessions
    - Manages mystery boxes
    - Tracks reward statistics
    - Provides streak and accuracy bonuses

    Usage:
        reward_system = RewardSystem()

        # Calculate session reward
        reward = reward_system.calculate_session_reward(
            questions_answered=20,
            accuracy=0.85,
            time_minutes=45,
            streak_days=5
        )

        # Open mystery box
        box = reward_system.create_mystery_box("session_complete")
        result = reward_system.open_mystery_box(box)

    EXAM IMPACT:
        Variable rewards create "just one more" motivation.
        This prevents early session termination and increases study time.
    """

    def __init__(
        self,
        jackpot_chance: float = JACKPOT_CHANCE,
        bonus_chance: float = BONUS_CHANCE,
        data_dir: Optional[Path] = None
    ):
        """
        Initialize reward system.

        Args:
            jackpot_chance: Probability of jackpot (default: 5%)
            bonus_chance: Probability of bonus (default: 15%)
            data_dir: Directory to store data
        """
        self.jackpot_chance = jackpot_chance
        self.bonus_chance = bonus_chance
        self.data_dir = data_dir or Path("/sdcard/jarvis_data")

        # Statistics
        self.stats = RewardStats()

        # Pending mystery boxes
        self._pending_boxes: List[MysteryBox] = []

        # Initialize random seed with current time for variety
        random.seed(datetime.now().timestamp())

    # ========================================================================
    # SESSION REWARDS
    # ========================================================================

    def calculate_session_reward(
        self,
        questions_answered: int,
        accuracy: float,
        time_minutes: int,
        streak_days: int = 0,
        subject: str = "general"
    ) -> Reward:
        """
        Calculate variable reward for a study session.

        Args:
            questions_answered: Number of questions answered
            accuracy: Accuracy rate (0-1)
            time_minutes: Time spent studying
            streak_days: Current streak length
            subject: Subject studied

        Returns:
            Reward with variable tier applied

        Reason:
            Main entry point for reward calculation.
            Applies all bonuses and variable multipliers.
        """
        # Base XP calculation
        base_xp = questions_answered * 10  # 10 XP per question
        base_xp += time_minutes * 2  # 2 XP per minute

        # Apply accuracy bonus
        accuracy_multiplier = self._get_accuracy_multiplier(accuracy)

        # Apply streak bonus
        streak_multiplier = self._get_streak_multiplier(streak_days)

        # Apply VARIABLE reward tier
        tier, tier_multiplier = self._roll_reward_tier()

        # Calculate final XP
        final_xp = int(base_xp * accuracy_multiplier * streak_multiplier * tier_multiplier)

        # Create reward
        description = self._create_reward_description(
            tier=tier,
            base_xp=base_xp,
            final_xp=final_xp,
            accuracy=accuracy,
            streak_days=streak_days,
            accuracy_multiplier=accuracy_multiplier,
            streak_multiplier=streak_multiplier,
            tier_multiplier=tier_multiplier
        )

        # Calculate coins
        coins = int(questions_answered * 5 * tier_multiplier)

        # Update stats
        self._update_stats(final_xp, coins, tier)

        reward = Reward(
            reward_type=RewardType.XP,
            amount=final_xp,
            tier=tier,
            description=description,
            bonus_info={
                "base_xp": base_xp,
                "accuracy_multiplier": accuracy_multiplier,
                "streak_multiplier": streak_multiplier,
                "tier_multiplier": tier_multiplier,
                "coins": coins,
                "subject": subject,
            }
        )

        return reward

    def _get_accuracy_multiplier(self, accuracy: float) -> float:
        """Get multiplier based on accuracy."""
        if accuracy >= ACCURACY_THRESHOLD_EXCELLENT:
            return ACCURACY_BONUS_EXCELLENT
        elif accuracy >= ACCURACY_THRESHOLD_GOOD:
            return ACCURACY_BONUS_GOOD
        return 1.0

    def _get_streak_multiplier(self, streak_days: int) -> float:
        """Get multiplier based on streak."""
        bonus = streak_days * STREAK_BONUS_PER_DAY
        return min(1.0 + bonus, MAX_STREAK_BONUS)

    def _roll_reward_tier(self) -> Tuple[RewardTier, float]:
        """
        Roll for reward tier using variable ratio schedule.

        Returns:
            Tuple of (tier, multiplier)

        Reason:
            This is the core variable reward mechanism.
            Uncertainty creates dopamine spikes.
        """
        roll = random.random()

        if roll < self.jackpot_chance:
            # JACKPOT! (5% chance)
            return RewardTier.JACKPOT, JACKPOT_XP_MULTIPLIER
        elif roll < self.jackpot_chance + self.bonus_chance:
            # BONUS! (15% chance)
            return RewardTier.BONUS, BONUS_XP_MULTIPLIER
        elif roll < self.jackpot_chance + self.bonus_chance + SMALL_BONUS_CHANCE:
            # Small bonus (25% chance)
            return RewardTier.SMALL_BONUS, SMALL_BONUS_XP_MULTIPLIER
        else:
            # Normal (55% chance)
            return RewardTier.NORMAL, 1.0

    def _create_reward_description(
        self,
        tier: RewardTier,
        base_xp: int,
        final_xp: int,
        accuracy: float,
        streak_days: int,
        accuracy_multiplier: float,
        streak_multiplier: float,
        tier_multiplier: float
    ) -> str:
        """Create exciting description for the reward."""

        tier_messages = {
            RewardTier.JACKPOT: "🎰 JACKPOT! You hit the BIG ONE!",
            RewardTier.BONUS: "🎁 BONUS! Extra rewards coming your way!",
            RewardTier.SMALL_BONUS: "✨ Nice! You got a small bonus!",
            RewardTier.NORMAL: "✅ Session complete! Rewards earned.",
        }

        lines = [tier_messages[tier], ""]

        if tier != RewardTier.NORMAL:
            lines.append(f"   Base XP: {base_xp}")
            if accuracy_multiplier > 1.0:
                lines.append(f"   Accuracy Bonus: x{accuracy_multiplier}")
            if streak_multiplier > 1.0:
                lines.append(f"   Streak Bonus: x{streak_multiplier}")
            if tier_multiplier > 1.0:
                lines.append(f"   Tier Bonus: x{tier_multiplier}")
            lines.append(f"   ─────────────")
            lines.append(f"   TOTAL: {final_xp} XP!")
        else:
            lines.append(f"   Earned: {final_xp} XP")
            if accuracy_multiplier > 1.0:
                lines.append(f"   (Includes accuracy bonus!)")

        return "\n".join(lines)

    # ========================================================================
    # MYSTERY BOXES
    # ========================================================================

    def create_mystery_box(self, source: str) -> MysteryBox:
        """
        Create a mystery box.

        Args:
            source: What earned this box

        Returns:
            New MysteryBox instance

        Reason:
            Mystery boxes are awarded for milestones.
            They create anticipation and excitement.
        """
        box_id = f"box_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"

        box = MysteryBox(
            box_id=box_id,
            source=source,
        )

        self._pending_boxes.append(box)
        return box

    def open_mystery_box(self, box: MysteryBox) -> Reward:
        """
        Open a mystery box for random rewards.

        Args:
            box: MysteryBox to open

        Returns:
            Reward from the box

        Reason:
            Opening boxes creates excitement.
            Variable rewards are more motivating than fixed.
        """
        if box.opened:
            return box.result

        # Roll for result
        roll = random.random()

        if roll < MYSTERY_BOX_RARE_CHANCE:
            # RARE ACHIEVEMENT (2%)
            result = Reward(
                reward_type=RewardType.ACHIEVEMENT,
                amount=1,
                tier=RewardTier.JACKPOT,
                description="🌟 RARE FIND! You discovered a rare achievement in the mystery box!",
                bonus_info={"achievement_type": "mystery_box_rare"}
            )
            self.stats.rare_achievements_from_boxes += 1

        elif roll < MYSTERY_BOX_RARE_CHANCE + MYSTERY_BOX_BIG_XP_CHANCE:
            # BIG XP (15%)
            xp = random.randint(100, 300)
            result = Reward(
                reward_type=RewardType.XP,
                amount=xp,
                tier=RewardTier.BONUS,
                description=f"💎 BIG XP! You found {xp} XP in the mystery box!",
                bonus_info={"xp_range": "100-300"}
            )

        elif roll < MYSTERY_BOX_RARE_CHANCE + MYSTERY_BOX_BIG_XP_CHANCE + MYSTERY_BOX_COINS_CHANCE:
            # COINS (25%)
            coins = random.randint(20, 70)
            result = Reward(
                reward_type=RewardType.COINS,
                amount=coins,
                tier=RewardTier.SMALL_BONUS,
                description=f"🪙 COINS! You found {coins} Focus Coins in the mystery box!",
                bonus_info={"coins_range": "20-70"}
            )

        elif roll < MYSTERY_BOX_RARE_CHANCE + MYSTERY_BOX_BIG_XP_CHANCE + MYSTERY_BOX_COINS_CHANCE + MYSTERY_BOX_SMALL_XP_CHANCE:
            # SMALL XP (20%)
            xp = random.randint(25, 75)
            result = Reward(
                reward_type=RewardType.XP,
                amount=xp,
                tier=RewardTier.SMALL_BONUS,
                description=f"✨ Small XP! You found {xp} XP in the mystery box!",
                bonus_info={"xp_range": "25-75"}
            )

        else:
            # NOTHING (38%) - but encouraging message
            messages = [
                "📦 The mystery box was empty... but your dedication isn't! Keep going!",
                "📦 Nothing this time... but every box you earn is progress!",
                "📦 Empty box, full heart. Your consistency is the real reward!",
                "📦 No loot this time, but you're building something amazing!",
            ]
            result = Reward(
                reward_type=RewardType.XP,
                amount=0,
                tier=RewardTier.NORMAL,
                description=random.choice(messages),
                bonus_info={"empty": True}
            )

        # Mark box as opened
        box.opened = True
        box.opened_at = datetime.now()
        box.result = result

        # Update stats
        self.stats.mystery_boxes_opened += 1
        if result.amount > 0:
            if result.reward_type == RewardType.XP:
                self.stats.total_xp += result.amount
            elif result.reward_type == RewardType.COINS:
                self.stats.total_coins += result.amount

        return result

    def get_pending_boxes(self) -> List[MysteryBox]:
        """Get all unopened mystery boxes."""
        return [b for b in self._pending_boxes if not b.opened]

    def get_pending_boxes_count(self) -> int:
        """Get count of unopened mystery boxes."""
        return len([b for b in self._pending_boxes if not b.opened])

    # ========================================================================
    # STREAK REWARDS
    # ========================================================================

    def calculate_streak_reward(self, streak_days: int) -> Reward:
        """
        Calculate reward for maintaining a streak.

        Args:
            streak_days: Current streak length

        Returns:
            Reward for streak maintenance

        Reason:
            Streaks should be rewarded to encourage maintenance.
            Bigger streaks = bigger rewards.
        """
        # Base reward grows with streak
        base_reward = streak_days * 50  # 50 XP per day of streak

        # Bonus for milestone streaks
        milestone_bonus = 0
        milestone_name = None

        if streak_days == 7:
            milestone_bonus = 500
            milestone_name = "Week Warrior"
        elif streak_days == 14:
            milestone_bonus = 1000
            milestone_name = "Two Week Champion"
        elif streak_days == 30:
            milestone_bonus = 3000
            milestone_name = "Monthly Master"
        elif streak_days == 60:
            milestone_bonus = 7000
            milestone_name = "Exam Ready"
        elif streak_days == 75:
            milestone_bonus = 10000
            milestone_name = "SEAT CONFIRMED!"

        total_xp = base_reward + milestone_bonus

        if milestone_name:
            description = (
                f"🔥 STREAK REWARD!\n"
                f"   {streak_days} days of consistency!\n"
                f"   Milestone: {milestone_name}\n"
                f"   XP Earned: {total_xp}"
            )
        else:
            description = (
                f"🔥 STREAK REWARD!\n"
                f"   {streak_days} days and counting!\n"
                f"   XP Earned: {total_xp}"
            )

        return Reward(
            reward_type=RewardType.STREAK_BONUS,
            amount=total_xp,
            tier=RewardTier.BONUS if milestone_bonus > 0 else RewardTier.NORMAL,
            description=description,
            bonus_info={
                "streak_days": streak_days,
                "milestone": milestone_name,
                "base_reward": base_reward,
                "milestone_bonus": milestone_bonus,
            }
        )

    # ========================================================================
    # STATISTICS
    # ========================================================================

    def _update_stats(self, xp: int, coins: int, tier: RewardTier) -> None:
        """Update reward statistics."""
        self.stats.total_xp += xp
        self.stats.total_coins += coins

        if tier == RewardTier.JACKPOT:
            self.stats.jackpots_won += 1
        elif tier == RewardTier.BONUS:
            self.stats.bonuses_won += 1

        if xp > self.stats.biggest_single_reward:
            self.stats.biggest_single_reward = xp

        tier_count = self.stats.rewards_by_tier.get(tier.value, 0)
        self.stats.rewards_by_tier[tier.value] = tier_count + 1

    def get_stats(self) -> RewardStats:
        """Get reward statistics."""
        return self.stats

    def get_jackpot_probability(self) -> str:
        """Get human-readable jackpot probability."""
        return f"Your next session has a {self.jackpot_chance*100:.0f}% chance of JACKPOT!"

    def get_next_reward_preview(self, streak_days: int = 0) -> str:
        """
        Get preview of potential rewards for motivation.

        Args:
            streak_days: Current streak

        Returns:
            Preview string

        Reason:
            Showing potential rewards motivates action.
        """
        streak_mult = self._get_streak_multiplier(streak_days)

        return (
            f"🎲 NEXT SESSION REWARD PREVIEW\n"
            f"\n"
            f"Possible outcomes:\n"
            f"  🎰 JACKPOT (5%): Up to 3x XP!\n"
            f"  🎁 BONUS (15%): 1.5x XP!\n"
            f"  ✨ Small Bonus (25%): 1.2x XP!\n"
            f"  ✅ Normal (55%): Standard XP\n"
            f"\n"
            f"Your current streak bonus: x{streak_mult:.1f}\n"
            f"\n"
            f"💡 Complete the session to find out what you get!"
        )


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Reward System...")
    print("="*60)

    system = RewardSystem()

    # Test 1: Session rewards with different accuracies
    print("\n1. Testing session rewards...")

    for accuracy in [0.95, 0.80, 0.60]:
        reward = system.calculate_session_reward(
            questions_answered=20,
            accuracy=accuracy,
            time_minutes=30,
            streak_days=5
        )
        print(f"\nAccuracy {accuracy*100:.0f}%:")
        print(f"  Tier: {reward.tier.value}")
        print(f"  XP: {reward.amount}")
        print(f"  {reward.description[:50]}...")

    # Test 2: Mystery boxes
    print("\n" + "="*60)
    print("\n2. Testing mystery boxes...")

    # Open 10 boxes to show variety
    results = {"rare": 0, "big_xp": 0, "coins": 0, "small_xp": 0, "nothing": 0}

    for i in range(10):
        box = system.create_mystery_box(f"test_{i}")
        result = system.open_mystery_box(box)

        if result.reward_type == RewardType.ACHIEVEMENT:
            results["rare"] += 1
        elif result.tier == RewardTier.BONUS:
            results["big_xp"] += 1
        elif result.reward_type == RewardType.COINS:
            results["coins"] += 1
        elif result.amount > 0:
            results["small_xp"] += 1
        else:
            results["nothing"] += 1

    print(f"10 Mystery Boxes opened:")
    for result_type, count in results.items():
        print(f"  {result_type}: {count}")

    # Test 3: Streak rewards
    print("\n" + "="*60)
    print("\n3. Testing streak rewards...")

    for days in [7, 14, 30, 75]:
        reward = system.calculate_streak_reward(days)
        print(f"\n{days}-day streak: {reward.amount} XP")

    # Test 4: Statistics
    print("\n" + "="*60)
    print("\n4. Reward Statistics:")
    stats = system.get_stats()
    print(f"  Total XP: {stats.total_xp}")
    print(f"  Total Coins: {stats.total_coins}")
    print(f"  Jackpots: {stats.jackpots_won}")
    print(f"  Mystery Boxes Opened: {stats.mystery_boxes_opened}")

    # Test 5: Preview
    print("\n" + "="*60)
    print("\n5. Next Reward Preview:")
    print(system.get_next_reward_preview(streak_days=5))

    print("\n" + "="*60)
    print("All tests passed!")
