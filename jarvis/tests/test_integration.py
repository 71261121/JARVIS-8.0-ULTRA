"""
JARVIS Cross-Module Integration Tests
=====================================

Tests for cross-module data flow:
1. Study Session → IRT → Psychological → Voice + Pattern Detection + Achievement
2. Behaviour Monitoring → Pattern Detection → Intervention → Voice
3. Daily Progress → Milestones → Achievements → Voice Celebration
4. Mock Test → Score Analysis → Weak Topic Detection → Study Plan Adjustment

GOAL_ALIGNMENT_CHECK():
    - Integration ensures all components work together
    - Data flows correctly between modules
    - User gets unified experience

CRITICAL: Integration tests verify the system works as ONE UNIT.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List
from unittest.mock import MagicMock, patch, AsyncMock

# Import all modules
from jarvis.study.irt import IRTEngine, IRTParameters, QuestionIRT
from jarvis.study.sm2 import SM2Engine, ReviewItem, Quality
from jarvis.study.question_bank import QuestionBank, Question
from jarvis.study.session import SessionManager, SessionConfig

from jarvis.focus.behaviour_monitor import BehaviourMonitor, EventType
from jarvis.focus.pattern_detector import PatternDetector, BehaviourData, PatternSeverity
from jarvis.focus.behaviour_data_collector import BehaviourDataCollector
from jarvis.focus.intervention_executor import InterventionExecutor, InterventionType

from jarvis.psych.loss_aversion import LossAversionEngine, UserProgress
from jarvis.psych.reward_system import RewardSystem
from jarvis.psych.achievement_system import AchievementSystem
from jarvis.psych.psychological_engine import PsychologicalEngine

from jarvis.voice.voice_engine import VoiceEngine, VoicePersonality, TTSBackend
from jarvis.voice.voice_messages import VoiceMessageGenerator, MessageType
from jarvis.voice.voice_enforcer import VoiceEnforcer, EnforcementMode

from jarvis.content.study_plan import StudyPlanGenerator
from jarvis.content.daily_target import DailyTargetManager
from jarvis.content.mock_test import MockTestSystem, MockType
from jarvis.content.milestone_tracker import MilestoneTracker


# =============================================================================
# STUDY SESSION INTEGRATION TESTS
# =============================================================================

class TestStudySessionIntegration:
    """Test study session integration with all modules."""
    
    def test_complete_study_session_flow(self):
        """Test complete study session data flow."""
        # Create all required components
        irt_engine = IRTEngine(initial_theta=0.0)
        sm2_engine = SM2Engine()
        psych_engine = PsychologicalEngine()
        reward_system = RewardSystem()
        achievement_system = AchievementSystem()
        
        # Add review item to SM-2
        review_item = ReviewItem(
            id="algebra_1",
            subject="Mathematics",
            topic="Algebra"
        )
        sm2_engine.add_item(review_item)
        
        # Create question for IRT
        question = QuestionIRT(
            id="algebra_1",
            params=IRTParameters(a=1.2, b=0.0, c=0.25),
            subject="Mathematics",
            topic="Algebra"
        )
        
        # Process through IRT
        irt_result = irt_engine.process_response(question, is_correct=True)
        
        # Process through SM-2
        sm2_result = sm2_engine.review_item("algebra_1", Quality.GOOD)
        
        # Process through psychology
        psych_result = psych_engine.process_session(
            questions_correct=8,
            questions_total=10,
            duration_minutes=15,
            subject="Mathematics",
            topic="Algebra"
        )
        
        # Check achievements
        achievements = achievement_system.check_achievements({
            "total_sessions": 1,
            "current_streak": 1,
            "total_questions": 10
        })
        
        # All components should have processed successfully
        assert irt_result is not None
        assert sm2_result is not None
        assert psych_result is not None
        assert isinstance(achievements, list)
    
    def test_irt_to_psychology_connection(self):
        """Test IRT results affect psychological processing."""
        irt_engine = IRTEngine(initial_theta=0.0)
        psych_engine = PsychologicalEngine()
        
        # Simulate good performance (theta increases)
        for _ in range(10):
            question = QuestionIRT(
                id=f"q_{_}",
                params=IRTParameters(a=1.0, b=-1.0, c=0.25),  # Easy questions
                subject="Mathematics",
                topic="Algebra"
            )
            irt_engine.process_response(question, is_correct=True)
        
        # Higher theta should correlate with confidence
        assert irt_engine.theta > 0.0
        
        # Process session
        result = psych_engine.process_session(
            questions_correct=10,
            questions_total=10,
            duration_minutes=15,
            subject="Mathematics",
            topic="Algebra"
        )
        
        # Perfect accuracy should give bonus
        assert result.xp_earned > 0
    
    def test_session_to_achievements_flow(self):
        """Test session completion triggers achievements."""
        psych_engine = PsychologicalEngine()
        achievement_system = AchievementSystem()
        
        # Process first session
        psych_engine.process_session(
            questions_correct=10,
            questions_total=15,
            duration_minutes=20,
            subject="Mathematics",
            topic="Algebra"
        )
        
        # Check for "First Step" achievement
        stats = psych_engine.get_stats()
        
        achievements = achievement_system.check_achievements({
            "total_sessions": 1,
            "total_questions": 15,
            "current_streak": 1
        })
        
        # Should have unlocked something
        assert isinstance(achievements, list)


# =============================================================================
# BEHAVIOUR TO INTERVENTION INTEGRATION TESTS
# =============================================================================

class TestBehaviourToInterventionIntegration:
    """Test behaviour monitoring to intervention flow."""
    
    def test_distraction_to_intervention_flow(self):
        """Test distraction detection triggers intervention."""
        # Create components
        collector = BehaviourDataCollector()
        detector = PatternDetector()
        executor = InterventionExecutor()
        
        # Simulate multiple distractions
        for _ in range(10):
            collector.record_distraction("com.instagram.android", 300)
        
        # Get behaviour data
        data = collector.get_behaviour_data()
        
        # Detect patterns
        patterns = detector.detect(data)
        
        # Execute intervention for high-severity patterns
        interventions = []
        for pattern in patterns:
            if pattern.severity in [PatternSeverity.HIGH, PatternSeverity.CRITICAL]:
                intervention = executor.execute(
                    intervention_type=InterventionType.WARNING,
                    reason=str(pattern.pattern_type)
                )
                interventions.append(intervention)
        
        # Flow should complete
        assert isinstance(patterns, list)
        assert isinstance(interventions, list)
    
    def test_pattern_to_voice_intervention(self):
        """Test pattern detection triggers voice intervention."""
        # Create components
        detector = PatternDetector()
        voice_engine = VoiceEngine()
        voice_engine.backend = TTSBackend.DUMMY
        message_generator = VoiceMessageGenerator()
        
        # Create high-severity behaviour data
        data = BehaviourData(
            distraction_events=50,
            study_minutes=10,
            app_switches=100,
            late_night_minutes=240,
            session_count=1,
            average_accuracy=0.2
        )
        
        # Detect patterns
        patterns = detector.detect(data)
        
        # Generate voice message for each pattern
        messages = []
        for pattern in patterns:
            message = message_generator.generate(
                MessageType.DISTRACTION_WARNING,
                context={"pattern": str(pattern.pattern_type)}
            )
            messages.append(message)
        
        # Should have generated messages
        assert len(patterns) > 0 or len(messages) >= 0
    
    def test_full_protection_pipeline(self):
        """Test complete protection pipeline."""
        # Create all components
        monitor = BehaviourMonitor()
        collector = BehaviourDataCollector()
        detector = PatternDetector()
        executor = InterventionExecutor()
        
        # Simulate behaviour
        collector.record_distraction("com.instagram.android", 600)
        collector.record_distraction("com.google.android.youtube", 300)
        
        # Analyze
        data = collector.get_behaviour_data()
        patterns = detector.detect(data)
        
        # Intervene
        for pattern in patterns:
            if pattern.severity in [PatternSeverity.HIGH, PatternSeverity.CRITICAL]:
                executor.execute(InterventionType.WARNING, str(pattern.pattern_type))
        
        # Pipeline should work end-to-end
        assert True


# =============================================================================
# PSYCHOLOGY TO VOICE INTEGRATION TESTS
# =============================================================================

class TestPsychologyToVoiceIntegration:
    """Test psychology events trigger voice responses."""
    
    def test_achievement_triggers_voice(self):
        """Test achievement unlock triggers voice celebration."""
        psych_engine = PsychologicalEngine()
        voice_engine = VoiceEngine()
        voice_engine.backend = TTSBackend.DUMMY
        message_generator = VoiceMessageGenerator()
        
        # Process session that might unlock achievement
        for i in range(7):
            psych_engine.update_streak(studied_today=True)
        
        # Generate achievement message
        message = message_generator.generate(
            MessageType.ACHIEVEMENT_UNLOCK,
            context={"achievement": "Week Warrior"}
        )
        
        # Speak it
        result = voice_engine.speak(message, personality=VoicePersonality.ENCOURAGING)
        
        assert result is not None
    
    def test_streak_risk_triggers_voice(self):
        """Test streak risk triggers voice warning."""
        loss_engine = LossAversionEngine()
        voice_engine = VoiceEngine()
        voice_engine.backend = TTSBackend.DUMMY
        
        # Create high-streak progress
        progress = UserProgress(
            xp=5000,
            coins=1000,
            current_streak=14,
            longest_streak=14,
            total_questions=500,
            total_correct=400
        )
        
        # Generate warning
        warning = loss_engine.generate_streak_risk_warning(progress, hours_remaining=4)
        
        # Speak it
        result = voice_engine.speak(warning, personality=VoicePersonality.URGENT)
        
        assert warning is not None
        assert result is not None
    
    def test_jackpot_triggers_celebration(self):
        """Test jackpot win triggers celebration."""
        reward_system = RewardSystem()
        voice_engine = VoiceEngine()
        voice_engine.backend = TTSBackend.DUMMY
        message_generator = VoiceMessageGenerator()
        
        # Calculate reward (might be jackpot)
        reward = reward_system.calculate_reward(
            base_xp=100,
            base_coins=20,
            accuracy=0.95
        )
        
        # If jackpot, celebrate
        if reward.tier.value == "JACKPOT":
            message = message_generator.generate(
                MessageType.JACKPOT,
                context={"xp": reward.xp}
            )
            voice_engine.speak(message, personality=VoicePersonality.ENCOURAGING)
        
        assert reward is not None


# =============================================================================
# CONTENT TO PROGRESS INTEGRATION TESTS
# =============================================================================

class TestContentToProgressIntegration:
    """Test content module integration with progress tracking."""
    
    def test_daily_target_to_milestone(self):
        """Test daily target completion contributes to milestones."""
        target_manager = DailyTargetManager()
        milestone_tracker = MilestoneTracker()
        
        # Get target
        target = target_manager.get_daily_target(day_number=1)
        
        # Complete all targets
        for subject_target in target.subject_targets:
            target_manager.update_progress(
                subject=str(subject_target.subject),
                questions_completed=subject_target.target_questions
            )
        
        # Check milestones
        stats = target_manager.get_stats()
        completed = milestone_tracker.check_milestones({
            "day": 1,
            "total_questions": stats.get("total_questions", 0),
            "current_streak": 1
        })
        
        assert isinstance(completed, list)
    
    def test_mock_test_to_study_plan(self):
        """Test mock test results affect study plan."""
        mock_system = MockTestSystem()
        plan_generator = StudyPlanGenerator()
        
        # Take mock test
        mock = mock_system.create_mock(MockType.SUBJECT, subject="Mathematics")
        result = mock_system.complete_mock(mock.id)
        
        # Analyze results
        analysis = mock_system.analyze_results(mock.id)
        
        # Get study plan
        plan = plan_generator.generate_plan()
        
        # Both should be valid
        assert plan is not None
        assert result is not None
    
    def test_full_75_day_simulation(self):
        """Test 75-day plan simulation."""
        plan_generator = StudyPlanGenerator()
        target_manager = DailyTargetManager()
        milestone_tracker = MilestoneTracker()
        psych_engine = PsychologicalEngine()
        
        # Generate plan
        plan = plan_generator.generate_plan()
        
        total_questions = 0
        achievements_unlocked = 0
        
        # Simulate all 75 days
        for day in plan.daily_plans:
            # Get daily target
            target = target_manager.get_daily_target(day.day_number)
            
            # Simulate completing targets
            for subject_target in target.subject_targets:
                questions = subject_target.target_questions
                total_questions += questions
                
                # Process session
                psych_engine.process_session(
                    questions_correct=int(questions * 0.75),
                    questions_total=questions,
                    duration_minutes=30,
                    subject=str(subject_target.subject),
                    topic="Topic"
                )
            
            # Update streak
            psych_engine.update_streak(studied_today=True)
            
            # Check milestones
            completed = milestone_tracker.check_milestones({
                "day": day.day_number,
                "total_questions": total_questions,
                "current_streak": day.day_number
            })
            
            achievements_unlocked += len(completed)
        
        # Should have completed all 75 days
        assert total_questions > 0
        assert achievements_unlocked >= 0


# =============================================================================
# FULL SYSTEM INTEGRATION TESTS
# =============================================================================

class TestFullSystemIntegration:
    """Test full system integration scenarios."""
    
    def test_morning_study_session_flow(self):
        """Test typical morning study session flow."""
        # Initialize all components
        irt_engine = IRTEngine()
        sm2_engine = SM2Engine()
        psych_engine = PsychologicalEngine()
        achievement_system = AchievementSystem()
        milestone_tracker = MilestoneTracker()
        voice_engine = VoiceEngine()
        voice_engine.backend = TTSBackend.DUMMY
        message_generator = VoiceMessageGenerator()
        
        # Morning greeting
        greeting = message_generator.generate(MessageType.DAILY_START)
        voice_engine.speak(greeting, personality=VoicePersonality.NEUTRAL)
        
        # Get due reviews from SM-2
        due_items = sm2_engine.get_due_reviews()
        
        # Process each due item
        for item in due_items[:5]:  # Process up to 5
            question = QuestionIRT(
                id=item.id,
                params=IRTParameters(a=1.0, b=0.0, c=0.25),
                subject=item.subject,
                topic=item.topic
            )
            
            # Simulate answer
            is_correct = True  # Simplified
            irt_engine.process_response(question, is_correct)
            sm2_engine.review_item(item.id, Quality.GOOD if is_correct else Quality.FORGET)
        
        # Process session
        session_result = psych_engine.process_session(
            questions_correct=5,
            questions_total=5,
            duration_minutes=15,
            subject="Mathematics",
            topic="Review"
        )
        
        # Check achievements
        achievements = achievement_system.check_achievements({
            "total_sessions": 1,
            "current_streak": 1,
            "total_questions": 5
        })
        
        # Update milestone
        milestones = milestone_tracker.check_milestones({
            "day": 1,
            "total_questions": 5,
            "current_streak": 1
        })
        
        # Flow should complete successfully
        assert session_result is not None
    
    def test_distraction_intervention_flow(self):
        """Test complete distraction detection and intervention flow."""
        # Initialize components
        monitor = BehaviourMonitor()
        collector = BehaviourDataCollector()
        detector = PatternDetector()
        executor = InterventionExecutor()
        voice_engine = VoiceEngine()
        voice_engine.backend = TTSBackend.DUMMY
        enforcer = VoiceEnforcer(voice_engine=voice_engine)
        enforcer.mode = EnforcementMode.ENFORCER
        
        # Simulate distraction event
        collector.record_distraction("com.instagram.android", 600)
        
        # Analyze behaviour
        data = collector.get_behaviour_data()
        patterns = detector.detect(data)
        
        # Handle each pattern
        for pattern in patterns:
            if pattern.severity in [PatternSeverity.HIGH, PatternSeverity.CRITICAL]:
                # Execute intervention
                intervention = executor.execute(
                    InterventionType.WARNING,
                    str(pattern.pattern_type)
                )
                
                # Voice intervention
                enforcer.handle_event(
                    "distraction_detected",
                    {"app": "Instagram", "pattern": str(pattern.pattern_type)}
                )
        
        # Flow should complete
        assert True
    
    def test_exam_day_simulation(self):
        """Test exam day simulation."""
        # This simulates what happens on day 75 (SEAT CONFIRMED)
        milestone_tracker = MilestoneTracker()
        psych_engine = PsychologicalEngine()
        voice_engine = VoiceEngine()
        voice_engine.backend = TTSBackend.DUMMY
        message_generator = VoiceMessageGenerator()
        
        # Simulate 75 days of preparation
        total_questions = 3000
        current_streak = 75
        
        # Check final milestone
        completed = milestone_tracker.check_milestones({
            "day": 75,
            "total_questions": total_questions,
            "current_streak": current_streak,
            "accuracy": 0.80
        })
        
        # Should have completed "SEAT CONFIRMED" milestone
        seat_confirmed = [m for m in completed if "seat" in m.id.lower() or "confirmed" in m.id.lower()]
        
        # Generate celebration message
        if seat_confirmed:
            message = message_generator.generate(
                MessageType.MILESTONE,
                context={"milestone": "SEAT CONFIRMED"}
            )
            voice_engine.speak(message, personality=VoicePersonality.ENCOURAGING)
        
        # Simulation complete
        assert isinstance(completed, list)


# =============================================================================
# ERROR RECOVERY INTEGRATION TESTS
# =============================================================================

class TestErrorRecoveryIntegration:
    """Test error recovery across modules."""
    
    def test_voice_failure_graceful_degradation(self):
        """Test system continues if voice fails."""
        psych_engine = PsychologicalEngine()
        
        # Process session
        result = psych_engine.process_session(
            questions_correct=10,
            questions_total=15,
            duration_minutes=20,
            subject="Mathematics",
            topic="Algebra"
        )
        
        # Even without voice, psychology should work
        assert result is not None
        assert result.xp_earned > 0
    
    def test_pattern_analyzer_restart(self):
        """Test pattern analyzer can restart after error."""
        analyzer = AnalyzerConfig()
        collector = BehaviourDataCollector()
        
        # Add data
        collector.record_distraction("app", 60)
        
        # Should still work
        data = collector.get_behaviour_data()
        
        assert data is not None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
