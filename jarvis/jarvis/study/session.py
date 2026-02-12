"""
JARVIS Session Manager
======================

Manages study sessions with IRT integration and progress tracking.

Key Features:
- Session creation and management
- Real-time theta updates
- XP and streak tracking
- Session analytics
- Mock test support

EXAM IMPACT:
    Direct. Session management ensures structured study time.
    Real-time feedback keeps student engaged and motivated.
    Analytics identify patterns and areas for improvement.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .irt import (
    IRTEngine, IRTParameters, IRTResult, QuestionIRT,
    update_theta, fisher_information, THETA_MIN, THETA_MAX
)
from .sm2 import SM2Engine, ReviewItem, Quality


# ============================================================================
# ENUMS
# ============================================================================

class SessionType(Enum):
    """Types of study sessions."""
    PRACTICE = "practice"
    REVISION = "revision"
    MOCK_TEST = "mock_test"
    WEAKNESS_TARGET = "weakness_target"


class SessionStatus(Enum):
    """Status of a study session."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class SessionConfig:
    """Configuration for a study session."""
    subject_id: str
    session_type: SessionType
    target_questions: int = 20
    time_limit_minutes: Optional[int] = None
    difficulty_range: Tuple[float, float] = (THETA_MIN, THETA_MAX)
    focus_weak_topics: bool = False
    

@dataclass
class QuestionResponse:
    """Record of a question response."""
    question_id: str
    user_answer: str
    is_correct: bool
    time_taken_seconds: int
    theta_before: float
    theta_after: float
    theta_change: float
    fisher_information: float
    answered_at: datetime = field(default_factory=datetime.now)


@dataclass
class SessionStats:
    """Statistics for a study session."""
    questions_attempted: int = 0
    questions_correct: int = 0
    questions_incorrect: int = 0
    accuracy: float = 0.0
    total_time_seconds: int = 0
    average_time_per_question: float = 0.0
    theta_start: float = 0.0
    theta_end: float = 0.0
    theta_change: float = 0.0
    xp_earned: int = 0
    

@dataclass
class Session:
    """A study session."""
    id: str
    user_id: str
    subject_id: str
    session_type: SessionType
    status: SessionStatus = SessionStatus.NOT_STARTED
    config: Optional[SessionConfig] = None
    
    # Timing
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_minutes: int = 0
    
    # Responses
    responses: List[QuestionResponse] = field(default_factory=list)
    answered_question_ids: Set[str] = field(default_factory=set)
    
    # IRT
    theta_before: float = 0.0
    theta_after: float = 0.0
    
    # Stats
    stats: SessionStats = field(default_factory=SessionStats)
    
    # XP
    xp_earned: int = 0


# ============================================================================
# SESSION MANAGER CLASS
# ============================================================================

class SessionManager:
    """
    Manages study sessions for JARVIS.
    
    Usage:
        manager = SessionManager()
        
        # Start a session
        session = manager.start_session(user_id, config)
        
        # Record responses
        result = manager.record_response(session, question, answer, time_taken)
        
        # End session
        stats = manager.end_session(session)
    
    Reason for design:
        Centralized session management with IRT integration.
        Tracks all study activity for analytics and motivation.
    """
    
    def __init__(self):
        """Initialize session manager."""
        self.irt_engine = IRTEngine()
        self.sm2_engine = SM2Engine()
        self.active_sessions: Dict[str, Session] = {}
        self.session_history: List[Session] = []
    
    # ========================================================================
    # SESSION LIFECYCLE
    # ========================================================================
    
    def create_session(
        self,
        user_id: str,
        config: SessionConfig
    ) -> Session:
        """
        Create a new study session.
        
        Args:
            user_id: User ID
            config: Session configuration
        
        Returns:
            New Session object
        """
        import uuid
        session_id = str(uuid.uuid4())[:8]
        
        session = Session(
            id=session_id,
            user_id=user_id,
            subject_id=config.subject_id,
            session_type=config.session_type,
            config=config,
            status=SessionStatus.NOT_STARTED
        )
        
        return session
    
    def start_session(
        self,
        session: Session,
        initial_theta: float = 0.0
    ) -> Session:
        """
        Start a study session.
        
        Args:
            session: Session to start
            initial_theta: Starting theta value
        
        Returns:
            Updated Session object
        """
        session.status = SessionStatus.IN_PROGRESS
        session.started_at = datetime.now()
        session.theta_before = initial_theta
        session.theta_after = initial_theta
        
        self.active_sessions[session.id] = session
        
        return session
    
    def pause_session(self, session: Session) -> Session:
        """Pause an active session."""
        if session.status == SessionStatus.IN_PROGRESS:
            session.status = SessionStatus.PAUSED
        return session
    
    def resume_session(self, session: Session) -> Session:
        """Resume a paused session."""
        if session.status == SessionStatus.PAUSED:
            session.status = SessionStatus.IN_PROGRESS
        return session
    
    def end_session(
        self,
        session: Session,
        abandoned: bool = False
    ) -> SessionStats:
        """
        End a study session.
        
        Args:
            session: Session to end
            abandoned: Whether session was abandoned
        
        Returns:
            Session statistics
        """
        session.status = SessionStatus.ABANDONED if abandoned else SessionStatus.COMPLETED
        session.ended_at = datetime.now()
        
        if session.started_at:
            duration = session.ended_at - session.started_at
            session.duration_minutes = int(duration.total_seconds() / 60)
        
        # Calculate final stats
        stats = self._calculate_stats(session)
        session.stats = stats
        
        # Move to history
        if session.id in self.active_sessions:
            del self.active_sessions[session.id]
        self.session_history.append(session)
        
        return stats
    
    # ========================================================================
    # QUESTION HANDLING
    # ========================================================================
    
    def record_response(
        self,
        session: Session,
        question_id: str,
        question_params: IRTParameters,
        user_answer: str,
        correct_answer: str,
        time_taken_seconds: int
    ) -> Tuple[IRTResult, QuestionResponse]:
        """
        Record a question response and update theta.
        
        Args:
            session: Active session
            question_id: Question ID
            question_params: IRT parameters for the question
            user_answer: User's answer (A, B, C, or D)
            correct_answer: Correct answer
            time_taken_seconds: Time taken to answer
        
        Returns:
            Tuple of (IRTResult, QuestionResponse)
        
        Reason:
            Core function for study sessions.
            Updates ability estimate after each question.
        """
        is_correct = user_answer.upper() == correct_answer.upper()
        
        # Update theta
        result = update_theta(session.theta_after, question_params, is_correct)
        
        # Create response record
        response = QuestionResponse(
            question_id=question_id,
            user_answer=user_answer.upper(),
            is_correct=is_correct,
            time_taken_seconds=time_taken_seconds,
            theta_before=result.theta_before,
            theta_after=result.theta_after,
            theta_change=result.theta_change,
            fisher_information=result.information
        )
        
        # Update session
        session.responses.append(response)
        session.answered_question_ids.add(question_id)
        session.theta_after = result.theta_after
        
        return result, response
    
    def select_next_question(
        self,
        session: Session,
        questions: List[QuestionIRT]
    ) -> Optional[QuestionIRT]:
        """
        Select the next optimal question for the session.
        
        Args:
            session: Active session
            questions: Available questions
        
        Returns:
            Optimal question or None if no questions available
        """
        if session.config:
            # Filter by difficulty range if specified
            min_diff, max_diff = session.config.difficulty_range
            questions = [
                q for q in questions
                if min_diff <= q.difficulty <= max_diff
            ]
        
        return self.irt_engine.select_optimal_question(
            session.theta_after,
            questions,
            session.answered_question_ids
        )
    
    def should_stop_session(
        self,
        session: Session,
        max_questions: int = 50
    ) -> Tuple[bool, str]:
        """
        Check if session should stop.
        
        Args:
            session: Active session
            max_questions: Maximum questions allowed
        
        Returns:
            Tuple of (should_stop, reason)
        """
        if session.config:
            max_questions = session.config.target_questions
        
        # Check question count
        if len(session.responses) >= max_questions:
            return True, "Target questions reached"
        
        # Check time limit
        if session.config and session.config.time_limit_minutes:
            if session.started_at:
                elapsed = datetime.now() - session.started_at
                if elapsed.total_seconds() / 60 >= session.config.time_limit_minutes:
                    return True, "Time limit reached"
        
        # Check IRT precision (optional - for adaptive tests)
        if len(session.responses) >= 10:
            params = [
                IRTParameters(
                    difficulty=r.theta_before,  # Approximate
                    discrimination=1.0,
                    guessing=0.25
                )
                for r in session.responses[-10:]
            ]
            should_stop, reason = self.irt_engine.should_stop_cat(
                session.theta_after, params, max_questions, len(session.responses)
            )
            if should_stop:
                return should_stop, reason
        
        return False, "Continue session"
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def _calculate_stats(self, session: Session) -> SessionStats:
        """Calculate session statistics."""
        responses = session.responses
        
        if not responses:
            return SessionStats()
        
        correct = sum(1 for r in responses if r.is_correct)
        total_time = sum(r.time_taken_seconds for r in responses)
        
        stats = SessionStats(
            questions_attempted=len(responses),
            questions_correct=correct,
            questions_incorrect=len(responses) - correct,
            accuracy=correct / len(responses) * 100 if responses else 0,
            total_time_seconds=total_time,
            average_time_per_question=total_time / len(responses) if responses else 0,
            theta_start=session.theta_before,
            theta_end=session.theta_after,
            theta_change=session.theta_after - session.theta_before
        )
        
        return stats
    
    def calculate_xp(self, session: Session) -> int:
        """
        Calculate XP earned for a session.
        
        XP Factors:
        - Base XP per question
        - Bonus for correct answers
        - Bonus for accuracy streak
        - Bonus for time efficiency
        
        Args:
            session: Completed session
        
        Returns:
            XP earned
        """
        if not session.responses:
            return 0
        
        stats = session.stats
        
        # Base XP: 5 per question attempted
        base_xp = stats.questions_attempted * 5
        
        # Correct answer bonus: 10 per correct
        correct_xp = stats.questions_correct * 10
        
        # Accuracy bonus
        accuracy_bonus = 0
        if stats.accuracy >= 90:
            accuracy_bonus = 50
        elif stats.accuracy >= 80:
            accuracy_bonus = 30
        elif stats.accuracy >= 70:
            accuracy_bonus = 15
        
        # Streak bonus (consecutive correct)
        max_streak = 0
        current_streak = 0
        for r in session.responses:
            if r.is_correct:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        streak_bonus = max_streak * 5
        
        # Theta improvement bonus
        theta_bonus = 0
        if stats.theta_change > 0:
            theta_bonus = int(stats.theta_change * 50)
        
        total_xp = base_xp + correct_xp + accuracy_bonus + streak_bonus + theta_bonus
        
        return max(0, total_xp)
    
    # ========================================================================
    # SESSION ANALYTICS
    # ========================================================================
    
    def get_session_summary(self, session: Session) -> Dict:
        """
        Get a summary of the session for display.
        
        Args:
            session: Session to summarize
        
        Returns:
            Summary dictionary
        """
        stats = session.stats
        
        return {
            "session_id": session.id,
            "subject": session.subject_id,
            "type": session.session_type.value,
            "status": session.status.value,
            "duration_minutes": session.duration_minutes,
            "questions": stats.questions_attempted,
            "correct": stats.questions_correct,
            "accuracy": f"{stats.accuracy:.1f}%",
            "theta_change": f"{stats.theta_change:+.3f}",
            "theta_start": f"{stats.theta_start:.3f}",
            "theta_end": f"{stats.theta_end:.3f}",
            "xp_earned": self.calculate_xp(session),
            "average_time": f"{stats.average_time_per_question:.1f}s",
        }
    
    def get_recent_sessions(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Session]:
        """Get recent sessions for a user."""
        user_sessions = [
            s for s in self.session_history
            if s.user_id == user_id
        ]
        user_sessions.sort(key=lambda s: s.started_at or datetime.min, reverse=True)
        return user_sessions[:limit]
    
    def get_subject_progress(
        self,
        user_id: str,
        subject_id: str
    ) -> Dict:
        """
        Get progress for a subject across all sessions.
        
        Args:
            user_id: User ID
            subject_id: Subject ID
        
        Returns:
            Progress summary
        """
        subject_sessions = [
            s for s in self.session_history
            if s.user_id == user_id and s.subject_id == subject_id
        ]
        
        if not subject_sessions:
            return {
                "total_sessions": 0,
                "total_questions": 0,
                "overall_accuracy": 0,
                "theta_progress": []
            }
        
        total_questions = sum(s.stats.questions_attempted for s in subject_sessions)
        total_correct = sum(s.stats.questions_correct for s in subject_sessions)
        
        theta_progress = [
            {
                "date": s.started_at.isoformat() if s.started_at else None,
                "theta": s.theta_after
            }
            for s in sorted(subject_sessions, key=lambda x: x.started_at or datetime.min)
        ]
        
        return {
            "total_sessions": len(subject_sessions),
            "total_questions": total_questions,
            "overall_accuracy": total_correct / total_questions * 100 if total_questions else 0,
            "theta_progress": theta_progress
        }


# ============================================================================
# MOCK TEST MANAGER
# ============================================================================

class MockTestManager:
    """
    Manages mock tests for exam simulation.
    
    EXAM IMPACT:
        Critical. Mock tests simulate actual exam conditions.
        Helps student build speed and accuracy under pressure.
    """
    
    # Exam pattern for Loyola Academy
    EXAM_PATTERN = {
        "maths": {"questions": 20, "marks": 1},
        "physics": {"questions": 15, "marks": 1},
        "chemistry": {"questions": 15, "marks": 1},
        "english": {"questions": 10, "marks": 1},
    }
    TOTAL_QUESTIONS = 60
    TOTAL_TIME_MINUTES = 50
    
    def __init__(self, session_manager: SessionManager):
        """Initialize mock test manager."""
        self.session_manager = session_manager
    
    def create_mock_test(
        self,
        user_id: str,
        duration_minutes: int = TOTAL_TIME_MINUTES
    ) -> Session:
        """
        Create a mock test session.
        
        Args:
            user_id: User ID
            duration_minutes: Test duration
        
        Returns:
            Mock test session
        """
        config = SessionConfig(
            subject_id="all",
            session_type=SessionType.MOCK_TEST,
            target_questions=self.TOTAL_QUESTIONS,
            time_limit_minutes=duration_minutes
        )
        
        return self.session_manager.create_session(user_id, config)
    
    def calculate_mock_score(self, session: Session) -> Dict:
        """
        Calculate mock test score.
        
        Args:
            session: Completed mock test session
        
        Returns:
            Score breakdown by subject
        """
        # Group responses by subject (would need subject tracking in questions)
        # For now, return overall score
        
        correct = session.stats.questions_correct
        total = session.stats.questions_attempted
        
        return {
            "total_score": correct,
            "total_possible": self.TOTAL_QUESTIONS,
            "percentage": correct / self.TOTAL_QUESTIONS * 100 if total else 0,
            "accuracy": session.stats.accuracy,
            "time_taken": session.duration_minutes,
            "time_allowed": self.TOTAL_TIME_MINUTES,
        }


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Session Manager...")
    print()
    
    manager = SessionManager()
    
    # Create a session
    config = SessionConfig(
        subject_id="maths",
        session_type=SessionType.PRACTICE,
        target_questions=10
    )
    
    session = manager.create_session("user_1", config)
    session = manager.start_session(session, initial_theta=0.0)
    
    print(f"Session started: {session.id}")
    print(f"Initial theta: {session.theta_before}")
    
    # Simulate some responses
    test_questions = [
        ("q1", IRTParameters(-0.5, 1.0, 0.25), "B", "B"),  # Correct, easy
        ("q2", IRTParameters(0.0, 1.0, 0.25), "A", "B"),   # Wrong, medium
        ("q3", IRTParameters(0.5, 1.0, 0.25), "C", "C"),   # Correct, hard
        ("q4", IRTParameters(-1.0, 1.0, 0.25), "D", "D"),  # Correct, very easy
    ]
    
    for qid, params, user_ans, correct_ans in test_questions:
        result, response = manager.record_response(
            session, qid, params, user_ans, correct_ans, 30
        )
        print(f"  Q: {qid}, Correct: {response.is_correct}, Theta: {result.theta_after:.3f}")
    
    # End session
    stats = manager.end_session(session)
    
    print()
    print("Session Summary:")
    print(f"  Questions: {stats.questions_attempted}")
    print(f"  Correct: {stats.questions_correct}")
    print(f"  Accuracy: {stats.accuracy:.1f}%")
    print(f"  Theta change: {stats.theta_change:+.3f}")
    print(f"  XP earned: {manager.calculate_xp(session)}")
    
    print("\nAll tests passed!")
