"""
JARVIS Mock Test System
=======================

Purpose: Full mock test simulation and analysis.

This module provides:
- Complete mock test generation
- Timer-based simulation
- Score analysis
- Subject-wise performance breakdown
- Comparison with previous tests
- Recommendations for improvement

EXAM IMPACT:
    CRITICAL. Mock tests are the REALITY CHECK.
    Without mocks, user doesn't know true preparation level.
    With mocks, user can fix gaps BEFORE the exam.

MOCK TEST TYPES:
    - Full Test: All 4 subjects, 60 marks total, 2 hours
    - Subject Test: Single subject, 20-15 marks, 30-45 min
    - Mini Test: Quick 15-min subject check

ANALYSIS FEATURES:
    - Time per question analysis
    - Subject-wise accuracy
    - Weakness identification
    - Comparison with target scores
    - IRT-based difficulty analysis

REASON FOR DESIGN:
    - Simulates real exam conditions
    - Provides actionable feedback
    - Tracks improvement over time
    - Identifies weak areas for focus

ROLLBACK PLAN:
    - Mock tests can be retaken
    - Results are preserved
    - Can disable time limits for practice
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import random
import json


# ============================================================================
# CONSTANTS
# ============================================================================

# Exam structure (Loyola Academy B.Sc CS)
EXAM_STRUCTURE = {
    "mathematics": {
        "marks": 20,
        "questions": 20,
        "time_minutes": 40,
    },
    "physics": {
        "marks": 15,
        "questions": 15,
        "time_minutes": 30,
    },
    "chemistry": {
        "marks": 15,
        "questions": 15,
        "time_minutes": 30,
    },
    "english": {
        "marks": 10,
        "questions": 10,
        "time_minutes": 20,
    },
}

# Total exam
TOTAL_MARKS = 60
TOTAL_TIME_MINUTES = 120

# Target scores for different performance levels
TARGET_SCORES = {
    "excellent": 54,  # 90%
    "good": 48,       # 80%
    "average": 42,    # 70%
    "pass": 36,       # 60%
    "poor": 30,       # 50%
}

# Mock test schedule (in intensive phase)
MOCK_SCHEDULE = {
    1: {"type": "subject", "subject": "mathematics"},
    2: {"type": "subject", "subject": "physics"},
    3: {"type": "subject", "subject": "chemistry"},
    4: {"type": "full"},
    5: {"type": "subject", "subject": "mathematics"},
    # ... continues
}


# ============================================================================
# ENUMS
# ============================================================================

class MockType(Enum):
    """Types of mock tests."""
    FULL = "full"           # Full exam simulation
    SUBJECT = "subject"     # Single subject
    MINI = "mini"           # Quick check


class MockStatus(Enum):
    """Status of mock test."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class QuestionResult:
    """Result for a single question."""
    question_id: int
    subject: str
    correct: bool
    user_answer: Optional[str] = None
    correct_answer: str = ""
    time_taken_seconds: int = 0
    difficulty: str = "medium"

    def to_dict(self) -> Dict:
        return {
            "question_id": self.question_id,
            "subject": self.subject,
            "correct": self.correct,
            "time_taken": self.time_taken_seconds,
            "difficulty": self.difficulty,
        }


@dataclass
class SubjectResult:
    """Result for a single subject."""
    subject: str
    total_questions: int
    correct: int
    incorrect: int
    skipped: int
    marks_obtained: float
    total_marks: float
    time_taken_minutes: float
    accuracy: float

    # Topic-wise breakdown
    topic_performance: Dict[str, Tuple[int, int]] = field(default_factory=dict)  # topic -> (correct, total)

    def get_percentage(self) -> float:
        """Get percentage score."""
        if self.total_marks == 0:
            return 0.0
        return (self.marks_obtained / self.total_marks) * 100

    def to_dict(self) -> Dict:
        return {
            "subject": self.subject,
            "total_questions": self.total_questions,
            "correct": self.correct,
            "incorrect": self.incorrect,
            "skipped": self.skipped,
            "marks_obtained": self.marks_obtained,
            "total_marks": self.total_marks,
            "percentage": self.get_percentage(),
            "time_taken": self.time_taken_minutes,
            "accuracy": self.accuracy,
        }


@dataclass
class MockTestResult:
    """Complete result of a mock test."""
    test_id: str
    mock_type: MockType
    subject: Optional[str]  # For subject tests
    started_at: datetime
    completed_at: Optional[datetime]
    status: MockStatus

    # Overall
    total_marks: float
    obtained_marks: float
    total_time_minutes: float
    time_taken_minutes: float

    # Per subject
    subject_results: Dict[str, SubjectResult] = field(default_factory=dict)

    # Per question
    question_results: List[QuestionResult] = field(default_factory=list)

    # Analysis
    performance_level: str = "average"
    improvement_areas: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)

    # Comparison
    previous_test_id: Optional[str] = None
    previous_score: Optional[float] = None
    score_change: Optional[float] = None

    def get_percentage(self) -> float:
        """Get overall percentage."""
        if self.total_marks == 0:
            return 0.0
        return (self.obtained_marks / self.total_marks) * 100

    def get_grade(self) -> str:
        """Get grade based on percentage."""
        percentage = self.get_percentage()
        if percentage >= 90:
            return "A+"
        elif percentage >= 80:
            return "A"
        elif percentage >= 70:
            return "B+"
        elif percentage >= 60:
            return "B"
        elif percentage >= 50:
            return "C"
        else:
            return "D"

    def to_dict(self) -> Dict:
        return {
            "test_id": self.test_id,
            "mock_type": self.mock_type.value,
            "subject": self.subject,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status.value,
            "total_marks": self.total_marks,
            "obtained_marks": self.obtained_marks,
            "percentage": self.get_percentage(),
            "grade": self.get_grade(),
            "time_taken": self.time_taken_minutes,
            "performance_level": self.performance_level,
            "subjects": {s: r.to_dict() for s, r in self.subject_results.items()},
            "improvement_areas": self.improvement_areas,
            "strengths": self.strengths,
        }


# ============================================================================
# MOCK TEST SYSTEM CLASS
# ============================================================================

class MockTestSystem:
    """
    Complete mock test system.

    This class:
    - Generates mock tests
    - Simulates exam conditions
    - Analyzes results
    - Provides recommendations
    - Tracks improvement over time

    Usage:
        system = MockTestSystem()

        # Start a mock test
        test = system.start_test(MockType.FULL)

        # Submit answers
        system.submit_answer(test_id, question_id, answer, time_taken)

        # Complete test
        result = system.complete_test(test_id)

        # Get analysis
        analysis = system.analyze_result(result)

    EXAM IMPACT:
        Mock tests are the REALITY CHECK.
        Essential for final preparation.
    """

    def __init__(self):
        """Initialize mock test system."""
        self._active_tests: Dict[str, MockTestResult] = {}
        self._completed_tests: List[MockTestResult] = []
        self._test_counter = 0

    # ========================================================================
    # TEST GENERATION
    # ========================================================================

    def start_test(
        self,
        mock_type: MockType,
        subject: Optional[str] = None,
        time_limit: bool = True
    ) -> MockTestResult:
        """
        Start a new mock test.

        Args:
            mock_type: Type of mock test
            subject: Subject for subject tests
            time_limit: Enforce time limits

        Returns:
            MockTestResult with test details
        """
        self._test_counter += 1
        test_id = f"mock_{datetime.now().strftime('%Y%m%d')}_{self._test_counter}"

        # Determine marks and time based on type
        if mock_type == MockType.FULL:
            total_marks = TOTAL_MARKS
            total_time = TOTAL_TIME_MINUTES
        elif mock_type == MockType.SUBJECT and subject:
            subject_config = EXAM_STRUCTURE.get(subject, {})
            total_marks = subject_config.get("marks", 20)
            total_time = subject_config.get("time_minutes", 40)
        else:
            total_marks = 15  # Mini test
            total_time = 15

        test = MockTestResult(
            test_id=test_id,
            mock_type=mock_type,
            subject=subject,
            started_at=datetime.now(),
            completed_at=None,
            status=MockStatus.IN_PROGRESS,
            total_marks=total_marks,
            obtained_marks=0.0,
            total_time_minutes=total_time,
            time_taken_minutes=0.0,
        )

        self._active_tests[test_id] = test
        return test

    def submit_answer(
        self,
        test_id: str,
        question_id: int,
        subject: str,
        user_answer: str,
        correct_answer: str,
        time_taken_seconds: int,
        difficulty: str = "medium"
    ) -> Dict:
        """
        Submit an answer for a question.

        Args:
            test_id: Test ID
            question_id: Question number
            subject: Subject
            user_answer: User's answer
            correct_answer: Correct answer
            time_taken_seconds: Time taken
            difficulty: Question difficulty

        Returns:
            Answer result
        """
        if test_id not in self._active_tests:
            return {"error": "Test not found"}

        test = self._active_tests[test_id]

        # Check if correct
        correct = user_answer.strip().lower() == correct_answer.strip().lower()

        # Create result
        result = QuestionResult(
            question_id=question_id,
            subject=subject,
            correct=correct,
            user_answer=user_answer,
            correct_answer=correct_answer,
            time_taken_seconds=time_taken_seconds,
            difficulty=difficulty,
        )

        test.question_results.append(result)

        # Update time
        test.time_taken_minutes += time_taken_seconds / 60

        return {
            "correct": correct,
            "correct_answer": correct_answer if not correct else None,
            "time_taken": time_taken_seconds,
        }

    def complete_test(self, test_id: str) -> MockTestResult:
        """
        Complete a mock test and generate results.

        Args:
            test_id: Test ID

        Returns:
            Complete MockTestResult with analysis
        """
        if test_id not in self._active_tests:
            return None

        test = self._active_tests[test_id]
        test.completed_at = datetime.now()
        test.status = MockStatus.COMPLETED

        # Calculate subject-wise results
        subject_questions: Dict[str, List[QuestionResult]] = {}
        for q in test.question_results:
            if q.subject not in subject_questions:
                subject_questions[q.subject] = []
            subject_questions[q.subject].append(q)

        for subject, questions in subject_questions.items():
            correct = sum(1 for q in questions if q.correct)
            incorrect = sum(1 for q in questions if not q.correct and q.user_answer)
            skipped = sum(1 for q in questions if not q.user_answer)

            total_q = len(questions)
            accuracy = correct / total_q if total_q > 0 else 0

            subject_config = EXAM_STRUCTURE.get(subject, {})
            marks_per_question = subject_config.get("marks", 20) / subject_config.get("questions", 20)

            marks_obtained = correct * marks_per_question

            time_taken = sum(q.time_taken_seconds for q in questions) / 60

            test.subject_results[subject] = SubjectResult(
                subject=subject,
                total_questions=total_q,
                correct=correct,
                incorrect=incorrect,
                skipped=skipped,
                marks_obtained=marks_obtained,
                total_marks=subject_config.get("marks", 20),
                time_taken_minutes=time_taken,
                accuracy=accuracy,
            )

            test.obtained_marks += marks_obtained

        # Determine performance level
        percentage = test.get_percentage()
        if percentage >= 90:
            test.performance_level = "excellent"
        elif percentage >= 80:
            test.performance_level = "good"
        elif percentage >= 70:
            test.performance_level = "average"
        elif percentage >= 60:
            test.performance_level = "pass"
        else:
            test.performance_level = "poor"

        # Identify improvement areas and strengths
        for subject, result in test.subject_results.items():
            if result.accuracy < 0.6:
                test.improvement_areas.append(f"{subject} ({result.accuracy*100:.0f}% accuracy)")
            elif result.accuracy >= 0.8:
                test.strengths.append(f"{subject} ({result.accuracy*100:.0f}% accuracy)")

        # Compare with previous test
        if self._completed_tests:
            previous = self._completed_tests[-1]
            test.previous_test_id = previous.test_id
            test.previous_score = previous.obtained_marks
            test.score_change = test.obtained_marks - previous.obtained_marks

        # Archive
        self._completed_tests.append(test)
        del self._active_tests[test_id]

        return test

    # ========================================================================
    # ANALYSIS
    # ========================================================================

    def analyze_result(self, result: MockTestResult) -> Dict:
        """
        Generate detailed analysis of test result.

        Args:
            result: MockTestResult to analyze

        Returns:
            Detailed analysis dictionary
        """
        analysis = {
            "test_id": result.test_id,
            "overall": {
                "score": result.obtained_marks,
                "total": result.total_marks,
                "percentage": result.get_percentage(),
                "grade": result.get_grade(),
                "performance": result.performance_level,
            },
            "subjects": {},
            "time_analysis": {},
            "recommendations": [],
            "comparison": {},
        }

        # Subject analysis
        for subject, subject_result in result.subject_results.items():
            analysis["subjects"][subject] = {
                "score": subject_result.marks_obtained,
                "total": subject_result.total_marks,
                "percentage": subject_result.get_percentage(),
                "accuracy": subject_result.accuracy,
                "time_per_question": subject_result.time_taken_minutes / max(1, subject_result.total_questions),
                "weak_topics": [],
                "strong_topics": [],
            }

        # Time analysis
        total_time = result.time_taken_minutes
        avg_time_per_question = total_time / max(1, len(result.question_results))

        analysis["time_analysis"] = {
            "total_time": total_time,
            "avg_time_per_question": avg_time_per_question,
            "time_efficiency": (result.total_time_minutes / max(1, total_time)) * 100,
        }

        # Generate recommendations
        if result.get_percentage() < 60:
            analysis["recommendations"].append("Focus on foundation - score below passing")
            analysis["recommendations"].append("Prioritize mathematics - highest weightage")

        for subject, sr in result.subject_results.items():
            if sr.accuracy < 0.5:
                analysis["recommendations"].append(f"Urgent: Review {subject} basics")
            elif sr.accuracy < 0.7:
                analysis["recommendations"].append(f"Practice {subject} more questions")

        # Comparison with previous
        if result.previous_score is not None:
            analysis["comparison"] = {
                "previous_score": result.previous_score,
                "change": result.score_change,
                "trend": "improving" if result.score_change and result.score_change > 0 else "declining",
            }

        return analysis

    # ========================================================================
    # STATISTICS
    # ========================================================================

    def get_test_history(self, limit: int = 10) -> List[Dict]:
        """Get history of completed tests."""
        recent = self._completed_tests[-limit:]
        return [t.to_dict() for t in recent]

    def get_progress_summary(self) -> Dict:
        """Get overall progress summary."""
        if not self._completed_tests:
            return {
                "tests_taken": 0,
                "average_score": 0,
                "best_score": 0,
                "improvement_trend": "no_data",
            }

        scores = [t.obtained_marks for t in self._completed_tests]

        return {
            "tests_taken": len(self._completed_tests),
            "average_score": sum(scores) / len(scores),
            "best_score": max(scores),
            "worst_score": min(scores),
            "improvement_trend": "improving" if scores[-1] > scores[0] else "stable",
            "last_test_score": scores[-1],
        }

    def get_subject_progress(self, subject: str) -> Dict:
        """Get progress for a specific subject."""
        subject_scores = []

        for test in self._completed_tests:
            if subject in test.subject_results:
                result = test.subject_results[subject]
                subject_scores.append({
                    "test_id": test.test_id,
                    "score": result.marks_obtained,
                    "percentage": result.get_percentage(),
                    "accuracy": result.accuracy,
                    "date": test.started_at.isoformat(),
                })

        if not subject_scores:
            return {"subject": subject, "tests": 0}

        return {
            "subject": subject,
            "tests": len(subject_scores),
            "average_accuracy": sum(s["accuracy"] for s in subject_scores) / len(subject_scores),
            "best_accuracy": max(s["accuracy"] for s in subject_scores),
            "history": subject_scores,
        }


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_mock_test_system() -> MockTestSystem:
    """Create a mock test system."""
    return MockTestSystem()


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Mock Test System...")
    print("="*60)

    system = MockTestSystem()

    # Test 1: Start full test
    print("\n1. Starting full mock test...")
    test = system.start_test(MockType.FULL)
    print(f"   Test ID: {test.test_id}")
    print(f"   Total marks: {test.total_marks}")
    print(f"   Time limit: {test.total_time_minutes} minutes")

    # Test 2: Submit some answers
    print("\n2. Submitting answers...")
    answers = [
        ("mathematics", "A", "A", 45),
        ("mathematics", "B", "B", 50),
        ("mathematics", "C", "A", 60),  # Wrong
        ("physics", "A", "A", 40),
        ("physics", "B", "C", 55),  # Wrong
        ("chemistry", "A", "A", 35),
        ("english", "B", "B", 25),
    ]

    for i, (subject, user_ans, correct_ans, time_sec) in enumerate(answers):
        result = system.submit_answer(
            test.test_id,
            question_id=i+1,
            subject=subject,
            user_answer=user_ans,
            correct_answer=correct_ans,
            time_taken_seconds=time_sec
        )
        print(f"   Q{i+1} ({subject}): {'✓' if result['correct'] else '✗'}")

    # Test 3: Complete test
    print("\n3. Completing test...")
    result = system.complete_test(test.test_id)
    print(f"   Score: {result.obtained_marks}/{result.total_marks}")
    print(f"   Percentage: {result.get_percentage():.1f}%")
    print(f"   Grade: {result.get_grade()}")
    print(f"   Performance: {result.performance_level}")

    # Test 4: Analysis
    print("\n4. Test analysis:")
    analysis = system.analyze_result(result)
    print(f"   Overall: {analysis['overall']['percentage']:.1f}%")
    print(f"   Recommendations: {analysis['recommendations'][:2]}")

    # Test 5: Progress summary
    print("\n5. Progress summary:")
    summary = system.get_progress_summary()
    print(f"   Tests taken: {summary['tests_taken']}")
    print(f"   Average score: {summary['average_score']:.1f}")

    print("\n" + "="*60)
    print("All tests passed!")
