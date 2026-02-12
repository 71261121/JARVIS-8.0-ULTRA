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
        params = IRTParameters(a=1.2, b=0.0, c=0.25)
        
        for theta in theta_values:
            prob = probability_correct(theta, params)
            assert 0 <= prob <= 1.0, f"Probability {prob} out of bounds for theta {theta}"
    
    def test_probability_correct_guessing(self):
        """Test that minimum probability is guessing parameter."""
        c = 0.25  # 4-option MCQ
        params = IRTParameters(a=1.0, b=2.0, c=c)  # Very hard question
        
        prob = probability_correct(-3.0, params)  # Very low ability
        assert prob >= c, f"Probability {prob} should be at least {c}"
    
    def test_probability_correct_increases_with_ability(self):
        """Test that probability increases with theta."""
        params = IRTParameters(a=1.0, b=0.0, c=0.25)
        
        probs = [probability_correct(theta, params) for theta in [-2, -1, 0, 1, 2]]
        
        # Verify monotonic increase
        for i in range(len(probs) - 1):
            assert probs[i] < probs[i+1], "Probability should increase with ability"
    
    def test_probability_at_difficulty(self):
        """Test that at theta=b, probability = (1+c)/2."""
        c = 0.25
        params = IRTParameters(a=1.0, b=0.5, c=c)
        
        prob = probability_correct(0.5, params)
        expected = (1 + c) / 2  # Should be 0.625
        
        assert abs(prob - expected) < 0.01, f"Expected ~{expected}, got {prob}"
    
    def test_fisher_information_positive(self):
        """Test that Fisher information is always positive."""
        theta_values = [-2.0, 0.0, 2.0]
        params = IRTParameters(a=1.5, b=0.0, c=0.25)
        
        for theta in theta_values:
            info = fisher_information(theta, params)
            assert info > 0, f"Fisher information should be positive, got {info}"
    
    def test_fisher_information_maximum_at_difficulty(self):
        """Test that Fisher information peaks near b parameter."""
        params = IRTParameters(a=1.5, b=0.0, c=0.25)
        
        # Calculate information at various thetas
        thetas = [-2.0, -1.0, 0.0, 1.0, 2.0]
        infos = [fisher_information(theta, params) for theta in thetas]
        
        # Maximum should be near theta=0 (the b parameter)
        max_idx = infos.index(max(infos))
        assert max_idx == 2, "Maximum information should be at theta close to b"


class TestIRTThetaEstimation:
    """Test theta estimation functions."""
    
    def test_theta_update_correct_easy(self):
        """Test theta increases when answering easy question correctly."""
        initial_theta = 0.0
        params = IRTParameters(a=1.0, b=-1.0, c=0.25)  # Easy question
        
        new_theta = update_theta(initial_theta, params, is_correct=True)
        
        assert new_theta > initial_theta, "Theta should increase after correct answer"
    
    def test_theta_update_incorrect_hard(self):
        """Test theta decreases when answering hard question incorrectly."""
        initial_theta = 0.0
        params = IRTParameters(a=1.0, b=1.0, c=0.25)  # Hard question
        
        new_theta = update_theta(initial_theta, params, is_correct=False)
        
        assert new_theta < initial_theta, "Theta should decrease after incorrect answer"
    
    def test_theta_bounds(self):
        """Test theta stays within bounds."""
        initial_theta = 0.0
        params = IRTParameters(a=1.0, b=0.0, c=0.25)
        
        # Apply many updates
        theta = initial_theta
        for _ in range(100):
            theta = update_theta(theta, params, is_correct=True)
            assert THETA_MIN <= theta <= THETA_MAX
        
        theta = initial_theta
        for _ in range(100):
            theta = update_theta(theta, params, is_correct=False)
            assert THETA_MIN <= theta <= THETA_MAX
    
    def test_mle_estimation(self):
        """Test MLE theta estimation from responses."""
        # Create responses where student got easy questions right
        # and hard questions wrong
        questions = [
            (IRTParameters(a=1.0, b=-1.0, c=0.25), True),   # Easy, correct
            (IRTParameters(a=1.0, b=-0.5, c=0.25), True),   # Medium-easy, correct
            (IRTParameters(a=1.0, b=0.5, c=0.25), False),   # Medium-hard, wrong
            (IRTParameters(a=1.0, b=1.0, c=0.25), False),   # Hard, wrong
        ]
        
        theta = estimate_theta_mle([(q, r) for q, r in questions])
        
        # Should be around 0 (between easy correct and hard wrong)
        assert -1.0 < theta < 1.0


class TestIRTEngine:
    """Test IRTEngine class."""
    
    def test_engine_initialization(self):
        """Test engine initializes with default theta."""
        engine = IRTEngine()
        assert engine.theta == 0.0
        assert engine.standard_error > 0
    
    def test_engine_custom_initial_theta(self):
        """Test engine can start with custom theta."""
        engine = IRTEngine(initial_theta=1.5)
        assert engine.theta == 1.5
    
    def test_engine_process_response(self):
        """Test processing a response updates theta."""
        engine = IRTEngine()
        initial_theta = engine.theta
        
        question = QuestionIRT(
            id="test_1",
            params=IRTParameters(a=1.0, b=0.0, c=0.25),
            subject="Mathematics",
            topic="Algebra"
        )
        
        result = engine.process_response(question, is_correct=True)
        
        assert engine.theta != initial_theta
        assert "theta" in result
        assert "standard_error" in result
    
    def test_engine_select_question(self):
        """Test question selection based on theta."""
        engine = IRTEngine(initial_theta=0.5)
        
        questions = [
            QuestionIRT(
                id=f"q_{i}",
                params=IRTParameters(a=1.0, b=b, c=0.25),
                subject="Mathematics",
                topic="Algebra"
            )
            for i, b in enumerate([-2, -1, 0, 1, 2])
        ]
        
        selected = select_optimal_question(questions, engine.theta)
        
        # Should select question near current theta
        assert selected is not None
        assert abs(selected.params.b - engine.theta) < 2.0
    
    def test_engine_standard_error_decreases(self):
        """Test that SE decreases with more responses."""
        engine = IRTEngine()
        initial_se = engine.standard_error
        
        # Process 10 responses
        for i in range(10):
            question = QuestionIRT(
                id=f"q_{i}",
                params=IRTParameters(a=1.2, b=0.0, c=0.25),
                subject="Mathematics",
                topic="Algebra"
            )
            engine.process_response(question, is_correct=True)
        
        assert engine.standard_error < initial_se
    
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
        level = get_ability_level(-2.5)
        assert level in ["BEGINNER", "NOVICE", "BELOW_AVERAGE"]
    
    def test_average_level(self):
        """Test average classification."""
        level = get_ability_level(0.0)
        assert level in ["AVERAGE", "INTERMEDIATE"]
    
    def test_expert_level(self):
        """Test expert classification."""
        level = get_ability_level(2.5)
        assert level in ["ADVANCED", "EXPERT", "MASTER"]


# =============================================================================
# SM-2 ALGORITHM TESTS
# =============================================================================

class TestSM2Basics:
    """Test basic SM-2 functions."""
    
    def test_ease_factor_minimum(self):
        """Test ease factor doesn't go below minimum."""
        # Quality 0 should reduce ease factor, but not below minimum
        ef = calculate_ease_factor(DEFAULT_EASE_FACTOR, Quality.FORGET)
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
        ef = calculate_ease_factor(DEFAULT_EASE_FACTOR, Quality.FORGET)
        assert ef < DEFAULT_EASE_FACTOR
    
    def test_interval_first_review(self):
        """Test first review interval."""
        result = calculate_next_review(
            interval=0,
            repetition=0,
            ease_factor=DEFAULT_EASE_FACTOR,
            quality=Quality.GOOD
        )
        assert result.interval == 1  # First interval is 1 day
    
    def test_interval_second_review(self):
        """Test second review interval."""
        result = calculate_next_review(
            interval=1,
            repetition=1,
            ease_factor=DEFAULT_EASE_FACTOR,
            quality=Quality.GOOD
        )
        assert result.interval == 6  # Second interval is 6 days
    
    def test_interval_multiplication(self):
        """Test interval multiplies by ease factor."""
        ef = 2.5
        result = calculate_next_review(
            interval=6,
            repetition=2,
            ease_factor=ef,
            quality=Quality.GOOD
        )
        # Interval should be approximately 6 * ef = 15
        assert result.interval >= 12  # At least 6 * 2.0
        assert result.interval <= 18  # At most 6 * 3.0
    
    def test_reset_on_failure(self):
        """Test interval resets on failure."""
        result = calculate_next_review(
            interval=30,
            repetition=5,
            ease_factor=DEFAULT_EASE_FACTOR,
            quality=Quality.FORGET
        )
        assert result.interval == 1
        assert result.repetition == 0


class TestSM2Engine:
    """Test SM2Engine class."""
    
    def test_engine_initialization(self):
        """Test engine initializes properly."""
        engine = SM2Engine()
        assert engine is not None
    
    def test_add_item(self):
        """Test adding review item."""
        engine = SM2Engine()
        
        item = ReviewItem(
            id="test_item",
            subject="Mathematics",
            topic="Algebra"
        )
        
        engine.add_item(item)
        assert len(engine.items) == 1
    
    def test_review_item(self):
        """Test reviewing an item."""
        engine = SM2Engine()
        
        item = ReviewItem(
            id="test_item",
            subject="Mathematics",
            topic="Algebra",
            interval=0,
            repetition=0,
            ease_factor=DEFAULT_EASE_FACTOR
        )
        
        engine.add_item(item)
        result = engine.review_item("test_item", Quality.GOOD)
        
        assert result is not None
        assert result.interval == 1
        assert result.repetition == 1
    
    def test_get_due_reviews(self):
        """Test getting due reviews."""
        engine = SM2Engine()
        
        # Add item due now
        item_due = ReviewItem(
            id="due_item",
            subject="Mathematics",
            topic="Algebra",
            next_review=datetime.now() - timedelta(hours=1)
        )
        
        # Add item not due yet
        item_future = ReviewItem(
            id="future_item",
            subject="Mathematics",
            topic="Algebra",
            next_review=datetime.now() + timedelta(days=5)
        )
        
        engine.add_item(item_due)
        engine.add_item(item_future)
        
        due = engine.get_due_reviews()
        assert len(due) == 1
        assert due[0].id == "due_item"
    
    def test_retention_probability(self):
        """Test retention probability calculation."""
        # Item reviewed 1 day ago with 6-day interval
        last_review = datetime.now() - timedelta(days=1)
        
        prob = calculate_retention_probability(
            days_since_review=1,
            interval=6,
            ease_factor=DEFAULT_EASE_FACTOR
        )
        
        # Should be high (recently reviewed, within interval)
        assert 0.5 < prob < 1.0


# =============================================================================
# QUESTION BANK TESTS
# =============================================================================

class TestQuestionBank:
    """Test QuestionBank class."""
    
    def test_bank_initialization(self):
        """Test bank initializes with default subjects."""
        bank = QuestionBank()
        
        assert "Mathematics" in bank.subjects
        assert "Physics" in bank.subjects
        assert "Chemistry" in bank.subjects
    
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
    
    def test_get_questions_by_difficulty(self):
        """Test filtering questions by difficulty."""
        bank = QuestionBank()
        
        # Add questions with different difficulties
        for i in range(5):
            q = Question(
                id=f"q_{i}",
                subject="Mathematics",
                topic="Algebra",
                content=f"Question {i}",
                options=["A", "B", "C", "D"],
                correct_answer="A",
                difficulty=-1.0 + i * 0.5,  # -1.0 to 1.0
                discrimination=1.0,
                guessing=0.25
            )
            bank.add_question(q)
        
        # Get questions near difficulty 0
        questions = bank.get_questions_by_difficulty(
            "Mathematics", "Algebra", target_difficulty=0.0, tolerance=0.5
        )
        
        assert len(questions) > 0
    
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
        assert "duration" in result or "questions_answered" in result


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
        
        # Add item to SM-2
        item = ReviewItem(
            id="algebra_1",
            subject="Mathematics",
            topic="Algebra"
        )
        sm2_engine.add_item(item)
        
        # Process through IRT
        question = QuestionIRT(
            id="algebra_1",
            params=IRTParameters(a=1.0, b=0.0, c=0.25),
            subject="Mathematics",
            topic="Algebra"
        )
        
        irt_result = irt_engine.process_response(question, is_correct=True)
        sm2_result = sm2_engine.review_item("algebra_1", Quality.GOOD)
        
        # Both should have processed
        assert irt_result is not None
        assert sm2_result is not None
    
    def test_adaptive_question_selection(self):
        """Test adaptive question selection flow."""
        bank = QuestionBank()
        irt_engine = IRTEngine(initial_theta=0.5)
        
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
        
        # Select question based on theta
        questions = bank.get_questions("Mathematics", "Algebra")
        irt_questions = [
            QuestionIRT(
                id=q.id,
                params=IRTParameters(a=q.discrimination, b=q.difficulty, c=q.guessing),
                subject=q.subject,
                topic=q.topic
            )
            for q in questions
        ]
        
        selected = select_optimal_question(irt_questions, irt_engine.theta)
        
        # Should select question near current theta
        assert selected is not None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
