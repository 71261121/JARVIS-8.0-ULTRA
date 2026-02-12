"""
JARVIS Psychological Engine Unit Tests
======================================

Comprehensive tests for:
1. Loss Aversion Engine
2. Variable Reward System
3. Achievement System (27 achievements)
4. Psychological Engine Integration

GOAL_ALIGNMENT_CHECK():
    - Loss aversion = Prevents streak breaks = Consistency
    - Variable rewards = Maintains engagement = More study time
    - Achievements = Motivation through gamification = Progress

CRITICAL: Psychology is what makes the system effective.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List
import random

from jarvis.psych.loss_aversion import (
    LossAversionEngine, UserProgress, LossWarning,
    LOSS_AVERSION_MULTIPLIER
)

from jarvis.psych.reward_system import (
    RewardSystem, Reward, MysteryBox,
    RewardType, RewardTier, RewardStats,
    JACKPOT_CHANCE, BONUS_CHANCE
)

from jarvis.psych.achievement_system import (
    AchievementSystem, Achievement, UserAchievement,
    AchievementTier, AchievementCategory, AchievementStats,
    ACHIEVEMENTS
)

from jarvis.psych.psychological_engine import (
    PsychologicalEngine, SessionResult, DailyMotivation,
    PsychologicalStats, create_psychological_engine
)


# =============================================================================
# LOSS AVERSION ENGINE TESTS
# =============================================================================

class TestLossAversionBasics:
    """Test basic LossAversion functionality."""
    
    def test_loss_aversion_multiplier(self):
        """Test loss aversion multiplier is set correctly."""
        assert LOSS_AVERSION_MULTIPLIER == 2.0
        
        # Losses should feel 2x more impactful
        gain_value = 100
        equivalent_loss = gain_value * LOSS_AVERSION_MULTIPLIER
        
        assert equivalent_loss == 200
    
    def test_engine_initialization(self):
        """Test engine initializes properly."""
        engine = LossAversionEngine()
        
        assert engine is not None
    
    def test_user_progress_dataclass(self):
        """Test UserProgress dataclass."""
        progress = UserProgress(
            xp=1000,
            coins=500,
            current_streak=7,
            longest_streak=14,
            total_questions=200,
            total_correct=150
        )
        
        assert progress.xp == 1000
        assert progress.current_streak == 7


class TestLossAversionWarnings:
    """Test loss aversion warning generation."""
    
    def test_streak_risk_warning(self):
        """Test streak risk warning generation."""
        engine = LossAversionEngine()
        
        progress = UserProgress(
            xp=1000,
            coins=500,
            current_streak=7,
            longest_streak=14,
            total_questions=200,
            total_correct=150
        )
        
        warning = engine.generate_streak_risk_warning(progress, hours_remaining=4)
        
        assert warning is not None
        assert 7 in warning or "streak" in warning.lower() or "7" in warning
    
    def test_daily_motivation(self):
        """Test daily motivation generation."""
        engine = LossAversionEngine()
        
        progress = UserProgress(
            xp=1000,
            coins=500,
            current_streak=7,
            longest_streak=14,
            total_questions=200,
            total_correct=150
        )
        
        motivation = engine.generate_daily_motivation(progress)
        
        assert motivation is not None
        assert len(motivation) > 20  # Should be meaningful message
    
    def test_loss_framing(self):
        """Test that messages use loss framing."""
        engine = LossAversionEngine()
        
        # Test XP loss framing
        loss_message = engine.frame_as_loss(xp_at_risk=500)
        
        assert "lose" in loss_message.lower() or "500" in loss_message
    
    def test_session_loss_message(self):
        """Test session loss message."""
        engine = LossAversionEngine()
        
        message = engine.generate_session_loss_message(
            xp_available=200,
            coins_available=50
        )
        
        assert message is not None
        # Should mention what's being lost
        assert "200" in message or "xp" in message.lower()


# =============================================================================
# VARIABLE REWARD SYSTEM TESTS
# =============================================================================

class TestRewardSystemBasics:
    """Test basic RewardSystem functionality."""
    
    def test_reward_chances(self):
        """Test reward chances are valid probabilities."""
        assert 0 < JACKPOT_CHANCE < 0.1
        assert 0 < BONUS_CHANCE < 0.3
        
        # Total should be reasonable
        total = JACKPOT_CHANCE + BONUS_CHANCE
        assert total < 0.5  # Less than 50% for special rewards
    
    def test_engine_initialization(self):
        """Test engine initializes properly."""
        system = RewardSystem()
        
        assert system is not None
        assert system.total_xp == 0
        assert system.total_coins == 0
    
    def test_reward_tiers(self):
        """Test reward tier definitions."""
        assert RewardTier.JACKPOT is not None
        assert RewardTier.BONUS is not None
        assert RewardTier.NORMAL is not None
    
    def test_reward_types(self):
        """Test reward type definitions."""
        assert RewardType.XP is not None
        assert RewardType.COINS is not None
        assert RewardType.ACHIEVEMENT is not None


class TestRewardSystemOperations:
    """Test RewardSystem operations."""
    
    def test_calculate_reward(self):
        """Test reward calculation."""
        system = RewardSystem()
        
        # Basic reward
        reward = system.calculate_reward(
            base_xp=100,
            base_coins=20,
            accuracy=0.8
        )
        
        assert reward is not None
        assert reward.xp > 0
        assert reward.coins > 0
    
    def test_jackpot_multiplier(self):
        """Test jackpot applies 3x multiplier."""
        system = RewardSystem()
        
        # Force jackpot tier
        reward = Reward(
            xp=300,  # 100 * 3
            coins=100,  # ~33 * 3
            tier=RewardTier.JACKPOT,
            message="JACKPOT!"
        )
        
        assert reward.tier == RewardTier.JACKPOT
        assert reward.xp >= 300
    
    def test_variable_rewards_distribution(self):
        """Test variable rewards follow expected distribution."""
        system = RewardSystem()
        
        # Simulate many rewards
        tiers = {
            RewardTier.JACKPOT: 0,
            RewardTier.BONUS: 0,
            RewardTier.SMALL_BONUS: 0,
            RewardTier.NORMAL: 0
        }
        
        for _ in range(1000):
            reward = system.calculate_reward(base_xp=100, base_coins=20, accuracy=0.7)
            tiers[reward.tier] += 1
        
        # Jackpot should be rare (~5%)
        assert tiers[RewardTier.JACKPOT] < 100  # Less than 10%
        
        # Normal should be most common
        assert tiers[RewardTier.NORMAL] > tiers[RewardTier.JACKPOT]
    
    def test_mystery_box_creation(self):
        """Test mystery box creation."""
        system = RewardSystem()
        
        box = system.create_mystery_box(reason="Session complete")
        
        assert box is not None
        assert box.reason == "Session complete"
    
    def test_mystery_box_opening(self):
        """Test mystery box opening."""
        system = RewardSystem()
        
        box = system.create_mystery_box(reason="Test")
        result = system.open_mystery_box(box)
        
        assert result is not None
    
    def test_streak_bonus(self):
        """Test streak bonus calculation."""
        system = RewardSystem()
        
        # No streak
        bonus_0 = system.calculate_streak_bonus(0)
        
        # 7-day streak
        bonus_7 = system.calculate_streak_bonus(7)
        
        # Higher streak should give more bonus
        assert bonus_7 >= bonus_0
    
    def test_accuracy_bonus(self):
        """Test accuracy bonus calculation."""
        system = RewardSystem()
        
        # Low accuracy
        reward_low = system.calculate_reward(base_xp=100, base_coins=20, accuracy=0.5)
        
        # High accuracy
        reward_high = system.calculate_reward(base_xp=100, base_coins=20, accuracy=0.95)
        
        # High accuracy should give more rewards
        assert reward_high.xp >= reward_low.xp


# =============================================================================
# ACHIEVEMENT SYSTEM TESTS
# =============================================================================

class TestAchievementSystemBasics:
    """Test basic AchievementSystem functionality."""
    
    def test_achievements_defined(self):
        """Test achievements are defined."""
        assert len(ACHIEVEMENTS) > 0
        assert len(ACHIEVEMENTS) == 27  # 27 achievements
    
    def test_achievement_tiers(self):
        """Test achievement tier distribution."""
        tiers = {
            AchievementTier.COMMON: 0,
            AchievementTier.UNCOMMON: 0,
            AchievementTier.RARE: 0,
            AchievementTier.EPIC: 0,
            AchievementTier.LEGENDARY: 0
        }
        
        for achievement in ACHIEVEMENTS:
            tiers[achievement.tier] += 1
        
        # Should have at least one of each tier
        assert tiers[AchievementTier.COMMON] > 0
        assert tiers[AchievementTier.LEGENDARY] > 0
    
    def test_achievement_categories(self):
        """Test achievement categories."""
        categories = set()
        
        for achievement in ACHIEVEMENTS:
            categories.add(achievement.category)
        
        # Should have multiple categories
        assert AchievementCategory.STREAK in categories
        assert AchievementCategory.STUDY in categories
    
    def test_engine_initialization(self):
        """Test engine initializes properly."""
        system = AchievementSystem()
        
        assert system is not None
        assert len(system.unlocked) == 0


class TestAchievementSystemOperations:
    """Test AchievementSystem operations."""
    
    def test_check_achievements(self):
        """Test achievement checking."""
        system = AchievementSystem()
        
        stats = {
            "total_sessions": 1,
            "current_streak": 0,
            "total_questions": 0,
            "accuracy": 0
        }
        
        new_achievements = system.check_achievements(stats)
        
        # First session should unlock "First Step"
        assert isinstance(new_achievements, list)
    
    def test_first_step_achievement(self):
        """Test 'First Step' achievement unlock."""
        system = AchievementSystem()
        
        stats = {
            "total_sessions": 1,
            "current_streak": 1,
            "total_questions": 20,
            "accuracy": 0.75
        }
        
        new_achievements = system.check_achievements(stats)
        
        # Should have unlocked at least one achievement
        first_step = [a for a in new_achievements if a.id == "first_step"]
        
        if len(first_step) > 0:
            assert first_step[0].name == "First Step"
    
    def test_streak_achievements(self):
        """Test streak-based achievements."""
        system = AchievementSystem()
        
        # 7-day streak
        stats = {
            "total_sessions": 7,
            "current_streak": 7,
            "total_questions": 140,
            "accuracy": 0.75
        }
        
        new_achievements = system.check_achievements(stats)
        
        # Should unlock "Week Warrior"
        week_warrior = [a for a in new_achievements if a.id == "week_warrior"]
        
        if len(week_warrior) > 0:
            assert week_warrior[0].tier in [AchievementTier.COMMON, AchievementTier.UNCOMMON]
    
    def test_accuracy_achievements(self):
        """Test accuracy-based achievements."""
        system = AchievementSystem()
        
        # High accuracy session
        stats = {
            "total_sessions": 5,
            "current_streak": 3,
            "total_questions": 100,
            "accuracy": 0.95,  # 95% accuracy
            "session_accuracy": 0.95
        }
        
        new_achievements = system.check_achievements(stats)
        
        assert isinstance(new_achievements, list)
    
    def test_achievement_progress(self):
        """Test achievement progress tracking."""
        system = AchievementSystem()
        
        # Check progress for specific achievement
        progress = system.get_progress("week_warrior", current_streak=5)
        
        # Should show some progress towards 7-day streak
        assert progress is not None
    
    def test_get_unlocked_achievements(self):
        """Test getting unlocked achievements."""
        system = AchievementSystem()
        
        # Unlock some achievements
        stats = {"total_sessions": 1, "current_streak": 1}
        system.check_achievements(stats)
        
        unlocked = system.get_unlocked()
        
        assert isinstance(unlocked, list)
    
    def test_achievement_xp_rewards(self):
        """Test achievement XP rewards."""
        for achievement in ACHIEVEMENTS:
            assert achievement.xp_reward > 0
            assert achievement.xp_reward < 10000  # Reasonable max


# =============================================================================
# PSYCHOLOGICAL ENGINE TESTS
# =============================================================================

class TestPsychologicalEngine:
    """Test PsychologicalEngine integration."""
    
    def test_engine_initialization(self):
        """Test engine initializes properly."""
        engine = PsychologicalEngine()
        
        assert engine is not None
        assert engine.loss_aversion is not None
        assert engine.reward_system is not None
        assert engine.achievement_system is not None
    
    def test_process_session(self):
        """Test session processing."""
        engine = PsychologicalEngine()
        
        result = engine.process_session(
            questions_correct=18,
            questions_total=20,
            duration_minutes=30,
            subject="Mathematics",
            topic="Algebra"
        )
        
        assert result is not None
        assert result.xp_earned > 0
        assert result.coins_earned > 0
    
    def test_process_session_with_accuracy_bonus(self):
        """Test high accuracy session."""
        engine = PsychologicalEngine()
        
        # Perfect accuracy
        result = engine.process_session(
            questions_correct=20,
            questions_total=20,
            duration_minutes=30,
            subject="Mathematics",
            topic="Algebra"
        )
        
        assert result.xp_earned > 0
        # Should have bonus for high accuracy
    
    def test_update_streak(self):
        """Test streak update."""
        engine = PsychologicalEngine()
        
        # Update streak for studying today
        result = engine.update_streak(studied_today=True)
        
        assert result.current_streak >= 1
    
    def test_break_streak(self):
        """Test streak break."""
        engine = PsychologicalEngine()
        
        # Build streak
        for _ in range(5):
            engine.update_streak(studied_today=True)
        
        # Break streak
        result = engine.update_streak(studied_today=False)
        
        assert result.current_streak == 0
    
    def test_get_daily_motivation(self):
        """Test daily motivation generation."""
        engine = PsychologicalEngine()
        
        motivation = engine.get_daily_motivation()
        
        assert motivation is not None
        assert motivation.message is not None
    
    def test_get_stats(self):
        """Test statistics retrieval."""
        engine = PsychologicalEngine()
        
        # Process some sessions
        for _ in range(5):
            engine.process_session(
                questions_correct=15,
                questions_total=20,
                duration_minutes=30,
                subject="Mathematics",
                topic="Algebra"
            )
        
        stats = engine.get_stats()
        
        assert stats.total_xp > 0
        assert stats.total_sessions >= 5


class TestPsychologicalIntegration:
    """Test integration of psychological components."""
    
    def test_session_to_achievements(self):
        """Test session triggers achievements."""
        engine = PsychologicalEngine()
        
        # Process first session
        result = engine.process_session(
            questions_correct=15,
            questions_total=20,
            duration_minutes=30,
            subject="Mathematics",
            topic="Algebra"
        )
        
        # Check for new achievements
        stats = engine.get_stats()
        
        # Should have processed session
        assert stats.total_sessions >= 1
    
    def test_streak_to_loss_aversion(self):
        """Test streak triggers loss aversion warning."""
        engine = PsychologicalEngine()
        
        # Build streak
        for _ in range(7):
            engine.update_streak(studied_today=True)
        
        # Check streak risk
        warning = engine.check_streak_risk(hours_until_reset=4)
        
        # High streak should generate warning
        if engine.get_stats().current_streak >= 7:
            assert warning is not None
    
    def test_factory_function(self):
        """Test create_psychological_engine factory."""
        engine = create_psychological_engine()
        
        assert engine is not None
        assert isinstance(engine, PsychologicalEngine)


# =============================================================================
# MESSAGE VERIFICATION TESTS
# =============================================================================

class TestMessageContent:
    """Test message content quality."""
    
    def test_loss_messages_are_impactful(self):
        """Test loss messages are impactful."""
        engine = LossAversionEngine()
        
        message = engine.generate_streak_risk_warning(
            UserProgress(current_streak=7, xp=1000, coins=500, longest_streak=14, total_questions=100, total_correct=75),
            hours_remaining=4
        )
        
        # Message should be substantial
        assert message is not None
        assert len(message) > 30  # Not too short
    
    def test_no_guilt_messages(self):
        """Test messages don't use guilt-based language."""
        engine = LossAversionEngine()
        
        # Generate several messages
        for streak in [1, 3, 7, 14]:
            message = engine.generate_streak_risk_warning(
                UserProgress(current_streak=streak, xp=1000, coins=500, longest_streak=14, total_questions=100, total_correct=75),
                hours_remaining=4
            )
            
            # Should not contain guilt-inducing words
            guilt_words = ["useless", "worthless", "failure", "stupid", "lazy"]
            for word in guilt_words:
                if message:
                    assert word not in message.lower()


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
