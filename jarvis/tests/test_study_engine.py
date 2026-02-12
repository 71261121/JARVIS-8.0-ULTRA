"""
JARVIS Study Engine Tests
=========================

Comprehensive tests for IRT and SM-2 engines.

Tests are aligned with implementation parameter names:
- difficulty (b parameter)
- discrimination (a parameter)
- guessing (c parameter)
"""

import pytest
import math
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from jarvis.study.irt import (
    IRTParameters,
    IRTResult,
    QuestionIRT,
    IRTEngine,
    probability_correct,
    fisher_information,
    update_theta,
    select_optimal_question,
    calculate_standard_error,
    should_stop_cat,
    theta_to_percentile,
    theta_to_percentage,
    get_ability_level,
    estimate_theta_mle,
    THETA_MIN,
    THETA_MAX,
    GUESSING_DEFAULT,
    SE_TARGET,
)

from jarvis.study.sm2 import (
    Quality,
    SM2Result,
    ReviewItem,
    SM2Engine,
    calculate_next_review,
    calculate_ease_factor,
    calculate_retention_probability,
    calculate_optimal_review_delay,
    get_due_reviews,
    sort_by_urgency,
    MIN_EASE_FACTOR,
    DEFAULT_EASE_FACTOR,
    MAX_EASE_FACTOR,
    INTERVAL_FIRST,
    INTERVAL_SECOND,
)


# ============================================================================
# IRT ENGINE TESTS
# ============================================================================

class TestIRTBasics:
    """Basic IRT functionality tests."""
    
    def test_irt_parameters_creation(self):
        """Test IRTParameters creation with valid values."""
        params = IRTParameters(
            difficulty=0.0,
            discrimination=1.0,
            guessing=0.25
        )
        assert params.difficulty == 0.0
        assert params.discrimination == 1.0
        assert params.guessing == 0.25
    
    def test_irt_parameters_clamping(self):
        """Test parameter clamping to valid ranges."""
        # Test out of range values
        params = IRTParameters(
            difficulty=10.0,  # Out of range
            discrimination=5.0,  # Out of range
            guessing=1.0  # Out of range
        )
        assert params.difficulty == THETA_MAX  # Clamped to 3.0
        assert params.discrimination == 2.5  # Clamped to max
        assert params.guessing == 0.5  # Clamped to max
    
    def test_probability_correct_bounds(self):
        """Test that probability is always between guessing and 1."""
        params = IRTParameters(difficulty=0.0, discrimination=1.0, guessing=0.25)
        
        for theta in [-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0]:
            prob = probability_correct(theta, params)
            assert 0.25 <= prob <= 1.0, f"Probability {prob} out of bounds for theta {theta}"
    
    def test_probability_correct_guessing(self):
        """Test that minimum probability is guessing parameter."""
        params = IRTParameters(difficulty=3.0, discrimination=1.0, guessing=0.25)
        
        # Very low ability on hard question
        prob = probability_correct(-3.0, params)
        assert prob >= 0.25  # Should be at least guessing
        assert prob < 0.35   # But not much higher
    
    def test_probability_correct_increases_with_ability(self):
        """Test that probability increases with ability."""
        params = IRTParameters(difficulty=0.0, discrimination=1.0, guessing=0.25)
        
        probs = [probability_correct(theta, params) for theta in [-2, -1, 0, 1, 2]]
        
        # Verify monotonic increase
        for i in range(len(probs) - 1):
            assert probs[i] < probs[i + 1], "Probability should increase with ability"
    
    def test_probability_at_difficulty(self):
        """Test probability at theta = difficulty."""
        params = IRTParameters(difficulty=0.0, discrimination=1.0, guessing=0.25)
        
        prob = probability_correct(0.0, params)
        
        # At theta = difficulty, probability should be approximately (1 + guessing) / 2
        expected = (1.0 + 0.25) / 2
        assert abs(prob - expected) < 0.01
    
    def test_fisher_information_positive(self):
        """Test that Fisher information is non-negative."""
        params = IRTParameters(difficulty=0.0, discrimination=1.0, guessing=0.25)
        
        for theta in [-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0]:
            info = fisher_information(theta, params)
            assert info >= 0, f"Negative information at theta {theta}"
    
    def test_fisher_information_maximum_at_difficulty(self):
        """Test that information is maximized near difficulty."""
        params = IRTParameters(difficulty=0.0, discrimination=1.5, guessing=0.25)
        
        # Calculate information at various theta values
        info_values = {theta: fisher_information(theta, params) for theta in [-2, -1, 0, 1, 2]}
        
        # Maximum should be near difficulty (theta = 0)
        max_theta = max(info_values.keys(), key=lambda t: info_values[t])
        assert abs(max_theta) <= 1, f"Max info at {max_theta}, expected near 0"


class TestIRTThetaEstimation:
    """Theta estimation tests."""
    
    def test_theta_update_correct_easy(self):
        """Test theta update after correct answer on easy question."""
        params = IRTParameters(difficulty=-1.0, discrimination=1.0, guessing=0.25)
        
        result = update_theta(0.0, params, is_correct=True)
        
        # Correct on easy question should increase theta
        assert result.theta_after > result.theta_before
        assert result.theta_change > 0
    
    def test_theta_update_incorrect_hard(self):
        """Test theta update after incorrect answer on hard question."""
        params = IRTParameters(difficulty=1.0, discrimination=1.0, guessing=0.25)
        
        result = update_theta(0.0, params, is_correct=False)
        
        # Incorrect on hard question should decrease theta slightly
        assert result.theta_after < result.theta_before
    
    def test_theta_bounds(self):
        """Test that theta stays within bounds."""
        params = IRTParameters(difficulty=0.0, discrimination=1.0, guessing=0.25)
        
        # Start at maximum
        theta = THETA_MAX
        
        # Correct answer should not exceed max
        result = update_theta(theta, params, is_correct=True)
        assert result.theta_after <= THETA_MAX
        
        # Start at minimum
        theta = THETA_MIN
        
        # Incorrect answer should not go below min
        result = update_theta(theta, params, is_correct=False)
        assert result.theta_after >= THETA_MIN
    
    def test_mle_estimation(self):
        """Test MLE theta estimation."""
        # Create items with known parameters
        items = [
            IRTParameters(difficulty=-1.0, discrimination=1.0, guessing=0.25),
            IRTParameters(difficulty=0.0, discrimination=1.0, guessing=0.25),
            IRTParameters(difficulty=1.0, discrimination=1.0, guessing=0.25),
        ]
        
        # Correct on easy, incorrect on hard
        responses = [1, 0, 0]
        
        theta = estimate_theta_mle(responses, items)
        
        # Should be in valid range
        assert THETA_MIN <= theta <= THETA_MAX
    
    def test_mle_all_correct(self):
        """Test MLE with all correct responses."""
        items = [
            IRTParameters(difficulty=0.0, discrimination=1.0, guessing=0.25),
            IRTParameters(difficulty=0.0, discrimination=1.0, guessing=0.25),
        ]
        
        responses = [1, 1]
        theta = estimate_theta_mle(responses, items)
        
        # All correct should give maximum theta
        assert theta == THETA_MAX
    
    def test_mle_all_incorrect(self):
        """Test MLE with all incorrect responses."""
        items = [
            IRTParameters(difficulty=0.0, discrimination=1.0, guessing=0.25),
            IRTParameters(difficulty=0.0, discrimination=1.0, guessing=0.25),
        ]
        
        responses = [0, 0]
        theta = estimate_theta_mle(responses, items)
        
        # All incorrect should give minimum theta
        assert theta == THETA_MIN


class TestIRTEngine:
    """IRTEngine class tests."""
    
    def test_engine_initialization(self):
        """Test engine creation."""
        engine = IRTEngine()
        assert engine is not None
        assert engine.THETA_MIN == THETA_MIN
        assert engine.THETA_MAX == THETA_MAX
    
    def test_engine_process_response(self):
        """Test engine processing a response."""
        engine = IRTEngine()
        params = IRTParameters(difficulty=0.0, discrimination=1.0, guessing=0.25)
        
        result = engine.update_theta(0.0, params, is_correct=True)
        
        assert isinstance(result, IRTResult)
        assert result.theta_after > result.theta_before
    
    def test_engine_select_question(self):
        """Test question selection."""
        engine = IRTEngine()
        
        questions = [
            QuestionIRT(id="q1", subject_id="math", topic_id="algebra",
                       difficulty=-1.0, discrimination=1.0),
            QuestionIRT(id="q2", subject_id="math", topic_id="algebra",
                       difficulty=0.0, discrimination=1.0),
            QuestionIRT(id="q3", subject_id="math", topic_id="algebra",
                       difficulty=1.0, discrimination=1.0),
        ]
        
        # At theta = 0, should prefer question with difficulty near 0
        selected = select_optimal_question(0.0, questions, set())
        
        assert selected is not None
        assert selected.id in ["q1", "q2", "q3"]
    
    def test_engine_standard_error_decreases(self):
        """Test that SE decreases with more questions."""
        params = IRTParameters(difficulty=0.0, discrimination=1.0, guessing=0.25)
        
        se_1 = calculate_standard_error(0.0, [params])
        se_5 = calculate_standard_error(0.0, [params] * 5)
        se_10 = calculate_standard_error(0.0, [params] * 10)
        
        # SE should decrease with more information
        assert se_1 > se_5 > se_10


class TestIRTAbilityLevels:
    """Ability level categorization tests."""
    
    def test_beginner_level(self):
        """Test beginner ability level."""
        level = get_ability_level(-2.5)
        assert level["level"] == "Beginner"
        assert "Foundation" in level["description"]
    
    def test_average_level(self):
        """Test average ability level."""
        level = get_ability_level(0.0)
        assert level["level"] in ["Competent", "Proficient"]
    
    def test_expert_level(self):
        """Test expert ability level."""
        level = get_ability_level(2.5)
        assert level["level"] == "Expert"
    
    def test_ability_level_colors(self):
        """Test that all levels have valid colors."""
        for theta in [-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0]:
            level = get_ability_level(theta)
            assert level["color"].startswith("#")


# ============================================================================
# SM-2 ENGINE TESTS
# ============================================================================

class TestSM2Basics:
    """Basic SM-2 functionality tests."""
    
    def test_ease_factor_minimum(self):
        """Test minimum ease factor."""
        # Perfect response should increase EF
        new_ef = calculate_ease_factor(DEFAULT_EASE_FACTOR, Quality.PERFECT)
        assert new_ef > DEFAULT_EASE_FACTOR
        
        # But even worst response shouldn't go below minimum
        new_ef = calculate_ease_factor(MIN_EASE_FACTOR, Quality.BLACKOUT)
        assert new_ef >= MIN_EASE_FACTOR
    
    def test_ease_factor_bad_response(self):
        """Test ease factor decrease on bad response."""
        # Blackout response should decrease EF
        new_ef = calculate_ease_factor(DEFAULT_EASE_FACTOR, Quality.BLACKOUT)
        assert new_ef < DEFAULT_EASE_FACTOR
    
    def test_interval_first_review(self):
        """Test first review interval."""
        interval, ef, reps = calculate_next_review(
            quality=Quality.CORRECT,
            ease_factor=DEFAULT_EASE_FACTOR,
            interval=0,
            repetitions=0
        )
        assert interval == INTERVAL_FIRST
        assert reps == 1
    
    def test_interval_second_review(self):
        """Test second review interval."""
        interval, ef, reps = calculate_next_review(
            quality=Quality.CORRECT,
            ease_factor=DEFAULT_EASE_FACTOR,
            interval=INTERVAL_FIRST,
            repetitions=1
        )
        assert interval == INTERVAL_SECOND
        assert reps == 2
    
    def test_interval_multiplication(self):
        """Test interval multiplication after second review."""
        interval, ef, reps = calculate_next_review(
            quality=Quality.CORRECT,
            ease_factor=2.0,
            interval=INTERVAL_SECOND,
            repetitions=2
        )
        assert interval == round(INTERVAL_SECOND * 2.0)
        assert reps == 3
    
    def test_reset_on_failure(self):
        """Test reset on failed recall."""
        interval, ef, reps = calculate_next_review(
            quality=Quality.DIFFICULT,  # < 3, failed
            ease_factor=DEFAULT_EASE_FACTOR,
            interval=10,
            repetitions=5
        )
        assert interval == INTERVAL_FIRST
        assert reps == 0


class TestSM2Engine:
    """SM2Engine class tests."""
    
    def test_engine_initialization(self):
        """Test engine creation."""
        engine = SM2Engine()
        assert engine is not None
        assert engine.DEFAULT_EASE_FACTOR == DEFAULT_EASE_FACTOR
    
    def test_process_review(self):
        """Test review processing."""
        engine = SM2Engine()
        
        item = ReviewItem(
            id="test-1",
            topic_id="math-algebra",
            ease_factor=DEFAULT_EASE_FACTOR,
            interval_days=0,
            repetitions=0
        )
        
        result = engine.process_review(item, quality=Quality.CORRECT)
        
        assert isinstance(result, SM2Result)
        assert result.interval_days == INTERVAL_FIRST
        assert result.repetitions == 1
    
    def test_get_due_reviews(self):
        """Test getting due reviews."""
        engine = SM2Engine()
        
        now = datetime.now()
        
        # Create items with different due dates
        items = [
            ReviewItem(id="due-now", topic_id="test", next_review_date=now - timedelta(days=1)),
            ReviewItem(id="due-tomorrow", topic_id="test", next_review_date=now + timedelta(days=1)),
            ReviewItem(id="never-reviewed", topic_id="test", next_review_date=None),
        ]
        
        due = get_due_reviews(items)
        
        # Should include due-now and never-reviewed
        assert len(due) >= 2
        due_ids = [item.id for item in due]
        assert "due-now" in due_ids
        assert "never-reviewed" in due_ids
    
    def test_retention_probability(self):
        """Test retention probability calculation."""
        # Just reviewed = high retention
        retention = calculate_retention_probability(
            days_since_review=0,
            ease_factor=2.5,
            repetitions=5
        )
        assert retention == 1.0
        
        # Long time = low retention
        retention = calculate_retention_probability(
            days_since_review=30,
            ease_factor=1.3,  # Hard item
            repetitions=1
        )
        assert retention < 0.5


class TestSM2ReviewManagement:
    """Review management tests."""
    
    def test_sort_by_urgency(self):
        """Test sorting by urgency."""
        now = datetime.now()
        
        items = [
            ReviewItem(
                id="overdue-hard",
                topic_id="test",
                ease_factor=1.3,
                next_review_date=now - timedelta(days=3)
            ),
            ReviewItem(
                id="overdue-easy",
                topic_id="test",
                ease_factor=2.5,
                next_review_date=now - timedelta(days=1)
            ),
            ReviewItem(
                id="not-due",
                topic_id="test",
                next_review_date=now + timedelta(days=3)
            ),
        ]
        
        sorted_items = sort_by_urgency(items)
        
        # Overdue items should come first
        assert sorted_items[0].id in ["overdue-hard", "overdue-easy"]
        assert sorted_items[-1].id == "not-due"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIRTSM2Integration:
    """Integration tests for IRT and SM-2."""
    
    def test_irt_sm2_workflow(self):
        """Test combined IRT-SM-2 workflow."""
        irt_engine = IRTEngine()
        sm2_engine = SM2Engine()
        
        # Create a question
        question = QuestionIRT(
            id="q1",
            subject_id="math",
            topic_id="algebra",
            difficulty=0.0,
            discrimination=1.0,
            guessing=0.25
        )
        
        # Create a review item
        item = ReviewItem(
            id="topic-algebra",
            topic_id="algebra"
        )
        
        # Process through IRT
        theta = 0.0
        params = question.get_params()
        result = irt_engine.update_theta(theta, params, is_correct=True)
        
        # Process through SM-2
        sm2_result = sm2_engine.process_review(item, quality=Quality.CORRECT)
        
        # Both should have completed successfully
        assert result.theta_after > theta
        assert sm2_result.interval_days > 0


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
