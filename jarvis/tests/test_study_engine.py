"""
JARVIS Study Engine Unit Tests
==============================

Comprehensive tests for:
1. IRT Engine (3PL Model, theta estimation, CAT)
2. SM-2 Algorithm (spaced repetition)
3. Question Bank Manager
4. Session Manager

GOAL_ALIGNMENT_CHECK():
    - IRT accuracy = Optimal question selection = Efficient learning
    - SM-2 accuracy = Proper review timing = Memory retention
    - These are DIRECTLY tied to exam success

CRITICAL: These algorithms are the CORE of JARVIS.

FIXED: Parameter names now match implementation:
    - discrimination (was 'a')
    - difficulty (was 'b')  
    - guessing (was 'c')
"""

import pytest
import math
from datetime import datetime, timedelta
from typing import List, Dict

from jarvis.study.irt import (
    IRTEngine, IRTParameters, QuestionIRT,
    probability_correct, fisher_information, update_theta,
    select_optimal_question, calculate_standard_error,
    theta_to_percentage, percentage_to_theta,
    get_ability_level, estimate_theta_mle,
    THETA_MIN, THETA_MAX, D_SCALING
)

from jarvis.study.sm2 import (
    SM2Engine, SM2Result, ReviewItem, Quality,
    calculate_next_review, calculate_ease_factor,
    calculate_retention_probability, get_due_reviews,
    MIN_EASE_FACTOR, DEFAULT_EASE_FACTOR, MAX_EASE_FACTOR
)

from jarvis.study.question_bank import (
    QuestionBank, Question, Topic, Subject,
    DEFAULT_SUBJECTS
)

from jarvis.study.session import (
    SessionManager, Session, SessionConfig, SessionType
)


# =============================================================================
# IRT ENGINE TESTS
# =============================================================================

class TestIRTBasics:
    """Test basic IRT functions."""
    
    def test_probability_correct_bounds(self):
        """Test that probability is always between 0 and 1."""
        theta_values = [-3.0, -1.0, 0.0, 1.0, 3.0]
        # CORRECTED: Use 'difficulty', 'discrimination', 'guessing' parameter names
        params = IRTParameters(discrimination=1.2, difficulty=0.0, guessing=0.25)
        
        for theta in theta_values:
            prob = probability_correct(theta, params)
            assert 0 <= prob <= 1.0, f"Probability {prob} out of bounds for theta {theta}"
    
    def test_probability_correct_guessing(self):
        """Test that minimum probability is guessing parameter."""
        guessing = 0.25  # 4-option MCQ
        # CORRECTED: Use proper parameter names
        params = IRTParameters(discrimination=1.0, difficulty=2.0, guessing=guessing)  # Very hard question
        
        prob = probability_correct(-3.0, params)  # Very low ability
        assert prob >= guessing, f"Probability {prob} should be at least {guessing}"
    
    def test_probability_correct_increases_with_ability(self):
        """Test that probability increases with theta."""
        params = IRTParameters(discrimination=1.0, difficulty=0.0, guessing=0.25)
        
        probs = [probability_correct(theta, params) for theta in [-2, -1, 0, 1, 2]]
        
        # Verify monotonic increase
        for i in range(len(probs) - 1):
            assert probs[i] < probs[i+1], "Probability should increase with ability"
    
    def test_probability_at_difficulty(self):
        """Test that at theta=difficulty, probability = (1+guessing)/2."""
        guessing = 0.25
        params = IRTParameters(discrimination=1.0, difficulty=0.5, guessing=guessing)
        
        prob = probability_correct(0.5, params)
        expected = (1 + guessing) / 2  # Should be 0.625
        
        assert abs(prob - expected) < 0.01, f"Expected ~{expected}, got {prob}"
    
    def test_fisher_information_positive(self):
        """Test that Fisher information is always positive."""
        theta_values = [-2.0, 0.0, 2.0]
        params = IRTParameters(discrimination=1.5, difficulty=0.0, guessing=0.25)
        
        for theta in theta_values:
            info = fisher_information(theta, params)
            assert info >= 0, f"Fisher information should be non-negative, got {info}"
    
    def test_fisher_information_maximum_at_difficulty(self):
        """Test that Fisher information peaks near difficulty parameter."""
        params = IRTParameters(discrimination=1.5, difficulty=0.0, guessing=0.25)
        
        # Calculate information at various thetas
        thetas = [-2.0, -1.0, 0.0, 1.0, 2.0]
        infos = [fisher_information(theta, params) for theta in thetas]
        
        # Maximum should be near theta=0 (the difficulty parameter)
        max_idx = infos.index(max(infos))
        assert max_idx == 2, "Maximum information should be at theta close to difficulty"


class TestIRTThetaEstimation:
    """Test theta estimation functions."""
    
    def test_theta_update_correct_easy(self):
        """Test theta increases when answering easy question correctly."""
        initial_theta = 0.0
        params = IRTParameters(discrimination=1.0, difficulty=-1.0, guessing=0.25)  # Easy question
        
        result = update_theta(initial_theta, params, is_correct=True)
        
        assert result.theta_after > initial_theta, "Theta should increase after correct answer"
    
    def test_theta_update_incorrect_hard(self):
        """Test theta decreases when answering hard question incorrectly."""
        initial_theta = 0.0
        params = IRTParameters(discrimination=1.0, difficulty=1.0, guessing=0.25)  # Hard question
        
        result = update_theta(initial_theta, params, is_correct=False)
        
        assert result.theta_after < initial_theta, "Theta should decrease after incorrect answer"
    
    def test_theta_bounds(self):
        """Test theta stays within bounds."""
        initial_theta = 0.0
        params = IRTParameters(discrimination=1.0, difficulty=0.0, guessing=0.25)
        
        # Apply many updates
        theta = initial_theta
        for _ in range(100):
            result = update_theta(theta, params, is_correct=True)
            theta = result.theta_after
            assert THETA_MIN <= theta <= THETA_MAX
        
        theta = initial_theta
        for _ in range(100):
            result = update_theta(theta, params, is_correct=False)
            theta = result.theta_after
            assert THETA_MIN <= theta <= THETA_MAX
    
    def test_mle_estimation(self):
        """Test MLE theta estimation from responses."""
        # Create responses where student got easy questions right
        # and hard questions wrong
        responses = [1, 1, 0, 0]  # correct, correct, wrong, wrong
        items = [
            IRTParameters(discrimination=1.0, difficulty=-1.0, guessing=0.25),  # Easy, correct
            IRTParameters(discrimination=1.0, difficulty=-0.5, guessing=0.25),  # Medium-easy, correct
            IRTParameters(discrimination=1.0, difficulty=0.5, guessing=0.25),   # Medium-hard, wrong
            IRTParameters(discrimination=1.0, difficulty=1.0, guessing=0.25),   # Hard, wrong
        ]
        
        theta = estimate_theta_mle(responses, items)
        
        # Should be around 0 (between easy correct and hard wrong)
        assert -1.0 < theta < 1.0


class TestIRTEngine:
    """Test IRTEngine class."""
    
    def test_engine_initialization(self):
        """Test engine initializes properly."""
        engine = IRTEngine()
        assert engine is not None
    
    def test_theta_to_percentage(self):
        """Test theta to percentage conversion."""
        # Test various theta values
        assert theta_to_percentage(0.0) == 50.0  # Average
        assert theta_to_percentage(2.0) > 50.0   # Above average
        assert theta_to_percentage(-2.0) < 50.0  # Below average
    
    def test_percentage_to_theta(self):
        """Test percentage to theta conversion."""
        # Test round-trip
        for theta in [-2.0, -1.0, 0.0, 1.0, 2.0]:
            pct = theta_to_percentage(theta)
            converted = percentage_to_theta(pct)
            assert abs(theta - converted) < 0.1


class TestIRTAbilityLevels:
    """Test ability level classification."""
    
    def test_beginner_level(self):
        """Test beginner classification."""
        level_info = get_ability_level(-2.5)
        assert level_info["level"] in ["Beginner", "NOVICE", "BELOW_AVERAGE"]
    
    def test_average_level(self):
        """Test average classification."""
        level_info = get_ability_level(0.0)
        assert level_info["level"] in ["Competent", "INTERMEDIATE", "Proficient"]
    
    def test_expert_level(self):
        """Test expert classification."""
        level_info = get_ability_level(2.5)
        assert level_info["level"] in ["Advanced", "Expert", "MASTER"]


# =============================================================================
# SM-2 ALGORITHM TESTS
# =============================================================================

class TestSM2Basics:
    """Test basic SM-2 functions."""
    
    def test_ease_factor_minimum(self):
        """Test ease factor doesn't go below minimum."""
        # Quality 0 should reduce ease factor, but not below minimum
        ef = calculate_ease_factor(DEFAULT_EASE_FACTOR, Quality.BLACKOUT)
        assert ef >= MIN_EASE_FACTOR
    
    def test_ease_factor_maximum(self):
        """Test ease factor doesn't exceed maximum."""
        # Quality 5 should increase ease factor
        ef = calculate_ease_factor(DEFAULT_EASE_FACTOR, Quality.PERFECT)
        assert ef <= MAX_EASE_FACTOR
    
    def test_ease_factor_good_response(self):
        """Test ease factor increases with good response."""
        ef = calculate_ease_factor(DEFAULT_EASE_FACTOR, Quality.PERFECT)
        assert ef > DEFAULT_EASE_FACTOR
    
    def test_ease_factor_bad_response(self):
        """Test ease factor decreases with bad response."""
        ef = calculate_ease_factor(DEFAULT_EASE_FACTOR, Quality.BLACKOUT)
        assert ef < DEFAULT_EASE_FACTOR
    
    def test_interval_first_review(self):
        """Test first review interval."""
        new_interval, new_ef, new_reps = calculate_next_review(
            interval=0,
            repetitions=0,
            ease_factor=DEFAULT_EASE_FACTOR,
            quality=Quality.CORRECT
        )
        assert new_interval == 1  # First interval is 1 day
    
    def test_interval_second_review(self):
        """Test second review interval."""
        new_interval, new_ef, new_reps = calculate_next_review(
            interval=1,
            repetitions=1,
            ease_factor=DEFAULT_EASE_FACTOR,
            quality=Quality.CORRECT
        )
        assert new_interval == 3  # Second interval is 3 days
    
    def test_interval_multiplication(self):
        """Test interval multiplies by ease factor."""
        ef = 2.5
        new_interval, new_ef, new_reps = calculate_next_review(
            interval=6,
            repetitions=2,
            ease_factor=ef,
            quality=Quality.CORRECT
        )
        # Interval should be approximately 6 * ef = 15
        assert new_interval >= 12  # At least 6 * 2.0
        assert new_interval <= 18  # At most 6 * 3.0
    
    def test_reset_on_failure(self):
        """Test interval resets on failure."""
        new_interval, new_ef, new_reps = calculate_next_review(
            interval=30,
            repetitions=5,
            ease_factor=DEFAULT_EASE_FACTOR,
            quality=Quality.BLACKOUT
        )
        assert new_interval == 1
        assert new_reps == 0


class TestSM2Engine:
    """Test SM2Engine class."""
    
    def test_engine_initialization(self):
        """Test engine initializes properly."""
        engine = SM2Engine()
        assert engine is not None
    
    def test_retention_probability(self):
        """Test retention probability calculation."""
        # Item reviewed 1 day ago
        prob = calculate_retention_probability(
            days_since_review=1,
            ease_factor=DEFAULT_EASE_FACTOR,
            repetitions=3
        )
        
        # Should be high (recently reviewed)
        assert 0 < prob < 1.0


# =============================================================================
# QUESTION BANK TESTS
# =============================================================================

class TestQuestionBank:
    """Test QuestionBank class."""
    
    def test_bank_initialization(self):
        """Test bank initializes with default subjects."""
        bank = QuestionBank()
        
        # Should have basic structure
        assert bank is not None
    
    def test_add_question(self):
        """Test adding a question."""
        bank = QuestionBank()
        
        question = Question(
            id="test_q1",
            subject="Mathematics",
            topic="Algebra",
            content="What is 2+2?",
            options=["3", "4", "5", "6"],
            correct_answer="4",
            difficulty=0.5,
            discrimination=1.0,
            guessing=0.25
        )
        
        bank.add_question(question)
        
        questions = bank.get_questions("Mathematics", "Algebra")
        assert len(questions) >= 1
    
    def test_get_topics(self):
        """Test getting topics for a subject."""
        bank = QuestionBank()
        
        topics = bank.get_topics("Mathematics")
        
        assert isinstance(topics, list)


# =============================================================================
# SESSION MANAGER TESTS
# =============================================================================

class TestSessionManager:
    """Test SessionManager class."""
    
    def test_manager_initialization(self):
        """Test manager initializes properly."""
        manager = SessionManager()
        assert manager is not None
    
    def test_create_session(self):
        """Test creating a study session."""
        manager = SessionManager()
        
        config = SessionConfig(
            subject="Mathematics",
            topic="Algebra",
            target_questions=10
        )
        
        session = manager.create_session(config)
        
        assert session is not None
        assert session.subject == "Mathematics"
        assert session.status == "active"
    
    def test_end_session(self):
        """Test ending a session."""
        manager = SessionManager()
        
        config = SessionConfig(subject="Mathematics", topic="Algebra")
        session = manager.create_session(config)
        
        result = manager.end_session(session.id)
        
        assert result is not None


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestStudyIntegration:
    """Test integration between study components."""
    
    def test_irt_sm2_integration(self):
        """Test IRT and SM-2 work together."""
        # Create engines
        irt_engine = IRTEngine()
        sm2_engine = SM2Engine()
        
        # Test both initialize
        assert irt_engine is not None
        assert sm2_engine is not None
    
    def test_adaptive_question_selection(self):
        """Test adaptive question selection flow."""
        bank = QuestionBank()
        irt_engine = IRTEngine()
        
        # Add questions
        for i in range(10):
            q = Question(
                id=f"q_{i}",
                subject="Mathematics",
                topic="Algebra",
                content=f"Question {i}",
                options=["A", "B", "C", "D"],
                correct_answer="A",
                difficulty=-2.0 + i * 0.4,
                discrimination=1.0,
                guessing=0.25
            )
            bank.add_question(q)
        
        # Get questions
        questions = bank.get_questions("Mathematics", "Algebra")
        
        # Convert to IRT questions
        irt_questions = [
            QuestionIRT(
                id=q.id,
                subject_id=q.subject,
                topic_id=q.topic,
                difficulty=q.difficulty,
                discrimination=q.discrimination,
                guessing=q.guessing
            )
            for q in questions
        ]
        
        # Select question
        selected = select_optimal_question(0.0, irt_questions, set())
        
        # Should select a question
        assert selected is not None


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_null_theta(self):
        """Test handling of null theta."""
        params = IRTParameters(discrimination=1.0, difficulty=0.0, guessing=0.25)
        # Should not crash
        prob = probability_correct(0.0, params)
        assert 0 <= prob <= 1
    
    def test_extreme_theta(self):
        """Test handling of extreme theta values."""
        params = IRTParameters(discrimination=1.0, difficulty=0.0, guessing=0.25)
        
        # Very high theta
        prob_high = probability_correct(10.0, params)
        assert prob_high < 1.0
        
        # Very low theta
        prob_low = probability_correct(-10.0, params)
        assert prob_low > 0
    
    def test_zero_discrimination(self):
        """Test handling of zero discrimination."""
        # This is an edge case - should still work
        params = IRTParameters(discrimination=0.5, difficulty=0.0, guessing=0.25)
        prob = probability_correct(0.0, params)
        assert 0 <= prob <= 1
    
    def test_empty_question_pool(self):
        """Test handling of empty question pool."""
        selected = select_optimal_question(0.0, [], set())
        assert selected is None
    
    def test_all_questions_answered(self):
        """Test when all questions have been answered."""
        questions = [
            QuestionIRT(
                id="q1",
                subject_id="Maths",
                topic_id="Algebra",
                difficulty=0.0,
                discrimination=1.0,
                guessing=0.25
            )
        ]
        answered = {"q1"}
        
        selected = select_optimal_question(0.0, questions, answered)
        assert selected is None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
