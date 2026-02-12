"""
JARVIS Question Bank Manager
============================

Manages the question database with IRT parameters and topic associations.

Key Features:
- Question storage and retrieval
- IRT-based question selection
- Topic coverage tracking
- Question difficulty distribution
- AI-generated question caching

EXAM IMPACT:
    Direct. Question bank is the core content for study sessions.
    Proper difficulty distribution ensures exam-level preparation.
    Topic coverage tracking prevents blind spots.
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path

from .irt import (
    IRTParameters, QuestionIRT, fisher_information,
    THETA_MIN, THETA_MAX, GUESSING_DEFAULT
)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Question:
    """A question with all metadata."""
    id: str
    topic_id: str
    subject_id: str
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str  # 'A', 'B', 'C', or 'D'
    explanation: str = ""
    
    # IRT Parameters
    difficulty: float = 0.0       # b parameter
    discrimination: float = 1.0   # a parameter
    guessing: float = GUESSING_DEFAULT
    
    # Metadata
    source: str = "manual"  # 'ai_generated', 'previous_year', 'manual'
    created_at: datetime = field(default_factory=datetime.now)
    times_asked: int = 0
    times_correct: int = 0
    
    def to_irt_question(self) -> QuestionIRT:
        """Convert to IRT question format."""
        return QuestionIRT(
            id=self.id,
            subject_id=self.subject_id,
            topic_id=self.topic_id,
            difficulty=self.difficulty,
            discrimination=self.discrimination,
            guessing=self.guessing
        )
    
    def get_difficulty_level(self) -> str:
        """Get difficulty level as string."""
        if self.difficulty < -1:
            return "Easy"
        elif self.difficulty < 0:
            return "Moderate"
        elif self.difficulty < 1:
            return "Medium"
        elif self.difficulty < 2:
            return "Hard"
        else:
            return "Very Hard"


@dataclass
class Topic:
    """A topic within a subject."""
    id: str
    subject_id: str
    name: str
    parent_id: Optional[str] = None  # For sub-topics
    difficulty: float = 0.0
    foundation_required: bool = False  # For Biology stream students
    foundation_days: int = 0
    question_count: int = 0


@dataclass
class Subject:
    """A subject in the exam."""
    id: str
    name: str
    weightage: int  # Marks in exam
    priority: int = 99
    description: str = ""


# ============================================================================
# BUILTIN SUBJECTS AND TOPICS
# ============================================================================

DEFAULT_SUBJECTS = [
    Subject(id="maths", name="Mathematics", weightage=20, priority=1,
            description="Highest weightage, user's weakest subject"),
    Subject(id="physics", name="Physics", weightage=15, priority=2,
            description="Second highest weightage, needs foundation"),
    Subject(id="chemistry", name="Chemistry", weightage=15, priority=3,
            description="Moderate difficulty for Biology students"),
    Subject(id="english", name="English", weightage=10, priority=4,
            description="Language skills, reading comprehension"),
]

# Foundation topics for Biology stream students (10th basics)
FOUNDATION_TOPICS_MATHS = [
    "Real Numbers", "Polynomials", "Linear Equations", "Quadratic Equations",
    "Arithmetic Progressions", "Triangles", "Coordinate Geometry",
    "Trigonometry Basics", "Applications of Trigonometry", "Circles",
    "Constructions", "Areas Related to Circles", "Surface Areas and Volumes",
    "Statistics", "Probability"
]

FOUNDATION_TOPICS_PHYSICS = [
    "Motion", "Force and Laws of Motion", "Gravitation", "Work and Energy",
    "Sound", "Light Reflection", "Light Refraction", "Electricity",
    "Magnetic Effects of Electric Current", "Sources of Energy"
]


# ============================================================================
# QUESTION BANK CLASS
# ============================================================================

class QuestionBank:
    """
    Question bank manager for JARVIS.
    
    Manages questions, topics, and subjects with IRT integration.
    
    Usage:
        bank = QuestionBank()
        
        # Add a question
        q = bank.add_question(topic_id="maths_algebra", ...)
        
        # Get questions for study
        questions = bank.get_questions_for_ability(theta=0.0, subject="maths")
    
    Reason for design:
        Centralized question management with IRT awareness.
        Enables efficient question selection based on student ability.
    """
    
    def __init__(self):
        """Initialize question bank."""
        self.questions: Dict[str, Question] = {}
        self.topics: Dict[str, Topic] = {}
        self.subjects: Dict[str, Subject] = {}
        
        # Initialize default subjects
        for subject in DEFAULT_SUBJECTS:
            self.subjects[subject.id] = subject
        
        # Topic coverage tracking
        self.topic_coverage: Dict[str, int] = {}  # topic_id -> question count
    
    # ========================================================================
    # QUESTION OPERATIONS
    # ========================================================================
    
    def add_question(
        self,
        topic_id: str,
        subject_id: str,
        question_text: str,
        options: List[str],
        correct: str,
        explanation: str = "",
        difficulty: float = 0.0,
        discrimination: float = 1.0,
        guessing: float = GUESSING_DEFAULT,
        source: str = "manual"
    ) -> Question:
        """
        Add a question to the bank.
        
        Args:
            topic_id: Topic ID
            subject_id: Subject ID
            question_text: The question text
            options: List of 4 options [A, B, C, D]
            correct: Correct option letter
            explanation: Explanation text
            difficulty: IRT difficulty (b parameter)
            discrimination: IRT discrimination (a parameter)
            guessing: IRT guessing (c parameter)
            source: Source of question
        
        Returns:
            The created Question object
        
        Raises:
            ValueError: If invalid options or correct option
        """
        if len(options) != 4:
            raise ValueError("Must have exactly 4 options")
        
        if correct not in ['A', 'B', 'C', 'D']:
            raise ValueError("Correct must be A, B, C, or D")
        
        # Generate ID based on content hash
        content = f"{topic_id}:{question_text}:{options[0]}"
        qid = hashlib.md5(content.encode()).hexdigest()[:8]
        
        question = Question(
            id=qid,
            topic_id=topic_id,
            subject_id=subject_id,
            question_text=question_text,
            option_a=options[0],
            option_b=options[1],
            option_c=options[2],
            option_d=options[3],
            correct_option=correct,
            explanation=explanation,
            difficulty=difficulty,
            discrimination=discrimination,
            guessing=guessing,
            source=source
        )
        
        self.questions[qid] = question
        
        # Update topic coverage
        if topic_id not in self.topic_coverage:
            self.topic_coverage[topic_id] = 0
        self.topic_coverage[topic_id] += 1
        
        return question
    
    def get_question(self, question_id: str) -> Optional[Question]:
        """Get a question by ID."""
        return self.questions.get(question_id)
    
    def get_questions_for_topic(
        self,
        topic_id: str,
        limit: int = 10
    ) -> List[Question]:
        """Get questions for a specific topic."""
        topic_questions = [
            q for q in self.questions.values()
            if q.topic_id == topic_id
        ]
        
        import random
        random.shuffle(topic_questions)
        return topic_questions[:limit]
    
    def get_questions_for_subject(
        self,
        subject_id: str,
        limit: int = 50
    ) -> List[Question]:
        """Get questions for a specific subject."""
        subject_questions = [
            q for q in self.questions.values()
            if q.subject_id == subject_id
        ]
        
        import random
        random.shuffle(subject_questions)
        return subject_questions[:limit]
    
    def get_questions_for_ability(
        self,
        theta: float,
        subject_id: Optional[str] = None,
        limit: int = 10,
        answered_ids: Optional[Set[str]] = None
    ) -> List[Question]:
        """
        Get questions optimized for a given ability level.
        
        Uses Fisher Information to select questions that provide
        the most information at the student's current ability.
        
        Args:
            theta: Student's ability estimate
            subject_id: Optional subject filter
            limit: Maximum questions to return
            answered_ids: Set of already answered question IDs
        
        Returns:
            List of optimal questions
        
        Reason:
            Efficient question selection for CAT.
            Maximizes learning by matching difficulty to ability.
        """
        answered_ids = answered_ids or set()
        
        # Filter questions
        candidates = []
        for q in self.questions.values():
            if q.id in answered_ids:
                continue
            if subject_id and q.subject_id != subject_id:
                continue
            candidates.append(q)
        
        if not candidates:
            return []
        
        # Calculate information for each question
        scored = []
        for q in candidates:
            params = IRTParameters(
                difficulty=q.difficulty,
                discrimination=q.discrimination,
                guessing=q.guessing
            )
            info = fisher_information(theta, params)
            scored.append((q, info))
        
        # Sort by information (descending)
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Return top questions with some randomness
        import random
        top_n = min(limit * 2, len(scored))
        top_questions = [q for q, _ in scored[:top_n]]
        random.shuffle(top_questions)
        
        return top_questions[:limit]
    
    # ========================================================================
    # TOPIC OPERATIONS
    # ========================================================================
    
    def add_topic(
        self,
        topic_id: str,
        subject_id: str,
        name: str,
        parent_id: Optional[str] = None,
        foundation_required: bool = False
    ) -> Topic:
        """Add a topic to the bank."""
        topic = Topic(
            id=topic_id,
            subject_id=subject_id,
            name=name,
            parent_id=parent_id,
            foundation_required=foundation_required
        )
        self.topics[topic_id] = topic
        return topic
    
    def get_topics_for_subject(self, subject_id: str) -> List[Topic]:
        """Get all topics for a subject."""
        return [
            t for t in self.topics.values()
            if t.subject_id == subject_id
        ]
    
    def get_weak_topics(
        self,
        theta_per_subject: Dict[str, float],
        threshold: float = -0.5
    ) -> List[Tuple[str, str, float]]:
        """
        Get topics where student is weak.
        
        Args:
            theta_per_subject: Theta values per subject
            threshold: Theta threshold for weakness
        
        Returns:
            List of (subject_id, topic_id, theta) tuples
        
        Reason:
            Identifies areas needing extra focus.
            Critical for Biology stream students in Maths.
        """
        weak_topics = []
        
        for subject_id, theta in theta_per_subject.items():
            if theta < threshold:
                topics = self.get_topics_for_subject(subject_id)
                for topic in topics:
                    weak_topics.append((subject_id, topic.id, theta))
        
        return weak_topics
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_difficulty_distribution(
        self,
        subject_id: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Get distribution of question difficulties.
        
        Args:
            subject_id: Optional subject filter
        
        Returns:
            Dictionary mapping difficulty levels to counts
        """
        distribution = {
            "Easy": 0,
            "Moderate": 0,
            "Medium": 0,
            "Hard": 0,
            "Very Hard": 0
        }
        
        for q in self.questions.values():
            if subject_id and q.subject_id != subject_id:
                continue
            level = q.get_difficulty_level()
            distribution[level] += 1
        
        return distribution
    
    def get_topic_coverage(self) -> Dict[str, float]:
        """
        Get coverage percentage for each topic.
        
        Returns:
            Dictionary mapping topic IDs to coverage percentages
        """
        total_questions = len(self.questions)
        if total_questions == 0:
            return {}
        
        coverage = {}
        for topic_id, count in self.topic_coverage.items():
            coverage[topic_id] = count / total_questions * 100
        
        return coverage
    
    def get_bank_stats(self) -> Dict:
        """Get overall bank statistics."""
        return {
            "total_questions": len(self.questions),
            "total_topics": len(self.topics),
            "total_subjects": len(self.subjects),
            "questions_by_subject": {
                subject_id: len([q for q in self.questions.values() 
                                if q.subject_id == subject_id])
                for subject_id in self.subjects
            },
            "difficulty_distribution": self.get_difficulty_distribution(),
        }
    
    # ========================================================================
    # IMPORT/EXPORT
    # ========================================================================
    
    def export_questions(self, filepath: str) -> None:
        """Export questions to JSON file."""
        data = {
            "questions": [
                {
                    "id": q.id,
                    "topic_id": q.topic_id,
                    "subject_id": q.subject_id,
                    "question_text": q.question_text,
                    "options": [q.option_a, q.option_b, q.option_c, q.option_d],
                    "correct_option": q.correct_option,
                    "explanation": q.explanation,
                    "difficulty": q.difficulty,
                    "discrimination": q.discrimination,
                    "guessing": q.guessing,
                    "source": q.source,
                }
                for q in self.questions.values()
            ],
            "exported_at": datetime.now().isoformat(),
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_questions(self, filepath: str) -> int:
        """
        Import questions from JSON file.
        
        Args:
            filepath: Path to JSON file
        
        Returns:
            Number of questions imported
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        count = 0
        for qdata in data.get("questions", []):
            try:
                self.add_question(
                    topic_id=qdata["topic_id"],
                    subject_id=qdata["subject_id"],
                    question_text=qdata["question_text"],
                    options=qdata["options"],
                    correct=qdata["correct_option"],
                    explanation=qdata.get("explanation", ""),
                    difficulty=qdata.get("difficulty", 0.0),
                    discrimination=qdata.get("discrimination", 1.0),
                    guessing=qdata.get("guessing", GUESSING_DEFAULT),
                    source=qdata.get("source", "imported"),
                )
                count += 1
            except Exception as e:
                print(f"Warning: Could not import question: {e}")
        
        return count


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Question Bank...")
    print()
    
    bank = QuestionBank()
    
    # Add some test questions
    bank.add_question(
        topic_id="algebra",
        subject_id="maths",
        question_text="What is the value of x if 2x + 5 = 13?",
        options=["x = 3", "x = 4", "x = 5", "x = 6"],
        correct="B",
        explanation="2x = 13 - 5 = 8, so x = 4",
        difficulty=-0.5,  # Easy
        source="test"
    )
    
    bank.add_question(
        topic_id="algebra",
        subject_id="maths",
        question_text="Solve: x² - 5x + 6 = 0",
        options=["x = 2, 3", "x = -2, -3", "x = 1, 6", "x = -1, -6"],
        correct="A",
        explanation="Factor: (x-2)(x-3) = 0, so x = 2 or 3",
        difficulty=0.0,  # Medium
        source="test"
    )
    
    # Print stats
    stats = bank.get_bank_stats()
    print("Bank Statistics:")
    print(f"  Total Questions: {stats['total_questions']}")
    print(f"  Difficulty Distribution: {stats['difficulty_distribution']}")
    
    # Get questions for ability
    print("\nQuestions for theta = 0.0:")
    questions = bank.get_questions_for_ability(theta=0.0, subject_id="maths")
    for q in questions:
        print(f"  - {q.question_text[:50]}... (difficulty: {q.difficulty})")
    
    print("\nAll tests passed!")
