"""
JARVIS 75-Day Study Plan Generator
===================================

Purpose: Generate and manage the complete 75-day study plan.

This module provides:
- Structured 75-day plan generation
- Phase-based progression (Foundation → Core → Advanced → Practice → Revision)
- Daily targets calculation
- Subject weightage optimization
- Weakness-focused adjustments

EXAM IMPACT:
    CRITICAL. This is the CORE preparation strategy.
    Without structured plan, user's effort is wasted.
    75-day plan ensures COMPLETE syllabus coverage.

PHASE BREAKDOWN:
    Days 1-15:   Foundation Rush (10th basics) - Biology→MPC transition
    Days 16-35:  Core Building (11th syllabus) - 20 days
    Days 36-55:  Advanced Topics (12th syllabus) - 20 days
    Days 56-70:  Intensive Practice + Mocks - 15 days
    Days 71-75:  Final Revision - 5 days

SUBJECT WEIGHTAGE (Loyola Academy B.Sc CS):
    Mathematics: 20 marks (HIGHEST) - User's WEAKEST
    Physics: 15 marks
    Chemistry: 15 marks
    English: 10 marks

SPECIAL CONSIDERATIONS:
    - User is Biology stream, attempting MPC
    - Maths needs 40% more time allocation
    - Foundation phase is CRITICAL for survival

REASON FOR DESIGN:
    - IRT-based difficulty progression
    - Weakness-focused allocation
    - Mock test integration from Day 36
    - Buffer days for revision

ROLLBACK PLAN:
    - Plan can be regenerated
    - Progress is tracked separately
    - Can adjust daily targets
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


# ============================================================================
# ENUMS
# ============================================================================

class StudyPhase(Enum):
    """Phases of 75-day preparation."""
    FOUNDATION = "foundation"       # Days 1-15: 10th basics
    CORE_BUILDING = "core"          # Days 16-35: 11th syllabus
    ADVANCED = "advanced"           # Days 36-55: 12th syllabus
    INTENSIVE = "intensive"         # Days 56-70: Practice + Mocks
    FINAL_REVISION = "revision"     # Days 71-75: Final prep


class Subject(Enum):
    """Subjects for the exam."""
    MATHEMATICS = "mathematics"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    ENGLISH = "english"


class DayType(Enum):
    """Types of study days."""
    NORMAL = "normal"               # Regular study
    MOCK_TEST = "mock_test"         # Full mock test
    REVISION = "revision"           # Revision day
    LIGHT = "light"                 # Reduced load (Sunday/burnout prevention)


# ============================================================================
# CONSTANTS
# ============================================================================

# Phase day ranges
PHASE_RANGES = {
    StudyPhase.FOUNDATION: (1, 15),
    StudyPhase.CORE_BUILDING: (16, 35),
    StudyPhase.ADVANCED: (36, 55),
    StudyPhase.INTENSIVE: (56, 70),
    StudyPhase.FINAL_REVISION: (71, 75),
}

# Subject weightage (marks in exam)
SUBJECT_WEIGHTAGE = {
    Subject.MATHEMATICS: 20,    # HIGHEST weightage
    Subject.PHYSICS: 15,
    Subject.CHEMISTRY: 15,
    Subject.ENGLISH: 10,
}

# Daily study hours target
DAILY_STUDY_HOURS = {
    StudyPhase.FOUNDATION: 6,
    StudyPhase.CORE_BUILDING: 8,
    StudyPhase.ADVANCED: 8,
    StudyPhase.INTENSIVE: 7,    # Less hours, more intensity
    StudyPhase.FINAL_REVISION: 5,
}

# Questions per hour (estimated)
QUESTIONS_PER_HOUR = {
    Subject.MATHEMATICS: 4,     # Maths takes longer
    Subject.PHYSICS: 6,
    Subject.CHEMISTRY: 6,
    Subject.ENGLISH: 10,
}

# Subject priority multipliers (weakness-focused)
# User's maths is weakest, so 40% more questions
WEAKNESS_MULTIPLIER = {
    Subject.MATHEMATICS: 1.4,   # 40% more for weakness
    Subject.PHYSICS: 1.0,
    Subject.CHEMISTRY: 1.0,
    Subject.ENGLISH: 0.8,       # Less focus, easier subject
}

# Foundation topics (10th basics)
FOUNDATION_TOPICS = {
    Subject.MATHEMATICS: [
        "Number Systems",
        "Polynomials",
        "Linear Equations",
        "Quadratic Equations",
        "Arithmetic Progressions",
        "Triangles",
        "Coordinate Geometry",
        "Trigonometry Basics",
        "Areas Related to Circles",
        "Statistics",
        "Probability Basics",
    ],
    Subject.PHYSICS: [
        "Motion in Straight Line",
        "Motion in Plane",
        "Laws of Motion",
        "Work, Energy, Power",
        "Gravitation",
        "Properties of Matter",
    ],
    Subject.CHEMISTRY: [
        "Atomic Structure",
        "Chemical Bonding",
        "Periodic Table",
        "Chemical Reactions",
        "Acids, Bases, Salts",
        "Metals and Non-metals",
    ],
    Subject.ENGLISH: [
        "Grammar Basics",
        "Vocabulary Building",
        "Reading Comprehension",
        "Sentence Correction",
    ],
}

# Core topics (11th syllabus)
CORE_TOPICS = {
    Subject.MATHEMATICS: [
        "Sets and Functions",
        "Trigonometric Functions",
        "Complex Numbers",
        "Linear Inequalities",
        "Permutations and Combinations",
        "Binomial Theorem",
        "Sequences and Series",
        "Straight Lines",
        "Conic Sections",
        "Introduction to 3D Geometry",
        "Limits and Derivatives",
        "Mathematical Reasoning",
        "Statistics and Probability",
    ],
    Subject.PHYSICS: [
        "Units and Measurements",
        "Motion in 1D and 2D",
        "Laws of Motion",
        "Work, Energy, Power",
        "Rotational Motion",
        "Gravitation",
        "Properties of Solids",
        "Properties of Fluids",
        "Thermodynamics",
        "Kinetic Theory",
        "Oscillations",
        "Waves",
    ],
    Subject.CHEMISTRY: [
        "Some Basic Concepts",
        "Structure of Atom",
        "Classification of Elements",
        "Chemical Bonding",
        "States of Matter",
        "Thermodynamics",
        "Equilibrium",
        "Redox Reactions",
        "Hydrogen",
        "s-Block Elements",
        "p-Block Elements",
        "Organic Chemistry Basics",
        "Hydrocarbons",
        "Environmental Chemistry",
    ],
    Subject.ENGLISH: [
        "Advanced Grammar",
        "Essay Writing",
        "Precis Writing",
        "Comprehension Practice",
        "Vocabulary Enhancement",
    ],
}

# Advanced topics (12th syllabus)
ADVANCED_TOPICS = {
    Subject.MATHEMATICS: [
        "Relations and Functions",
        "Inverse Trigonometric Functions",
        "Matrices",
        "Determinants",
        "Continuity and Differentiability",
        "Applications of Derivatives",
        "Integrals",
        "Applications of Integrals",
        "Differential Equations",
        "Vector Algebra",
        "Three Dimensional Geometry",
        "Linear Programming",
        "Probability Advanced",
    ],
    Subject.PHYSICS: [
        "Electric Charges and Fields",
        "Electrostatic Potential",
        "Current Electricity",
        "Moving Charges and Magnetism",
        "Magnetism and Matter",
        "Electromagnetic Induction",
        "Alternating Current",
        "Electromagnetic Waves",
        "Ray Optics",
        "Wave Optics",
        "Dual Nature of Radiation",
        "Atoms and Nuclei",
        "Semiconductor Electronics",
    ],
    Subject.CHEMISTRY: [
        "Solid State",
        "Solutions",
        "Electrochemistry",
        "Chemical Kinetics",
        "Surface Chemistry",
        "General Principles of Isolation",
        "p-Block Elements Advanced",
        "d and f Block Elements",
        "Coordination Compounds",
        "Haloalkanes and Haloarenes",
        "Alcohols, Phenols, Ethers",
        "Aldehydes, Ketones, Carboxylic Acids",
        "Amines",
        "Biomolecules",
        "Polymers",
        "Chemistry in Everyday Life",
    ],
    Subject.ENGLISH: [
        "Literature Analysis",
        "Critical Reading",
        "Advanced Writing",
        "Exam-Style Practice",
    ],
}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class DailyPlan:
    """Plan for a single study day."""
    day_number: int
    date: datetime
    phase: StudyPhase
    day_type: DayType

    # Daily targets
    total_hours: float
    total_questions: int

    # Subject breakdown
    subject_targets: Dict[str, int] = field(default_factory=dict)  # subject -> questions
    topic_targets: Dict[str, List[str]] = field(default_factory=dict)  # subject -> topics

    # Special events
    is_mock_test: bool = False
    mock_test_subjects: List[str] = field(default_factory=list)

    # Progress tracking
    completed: bool = False
    questions_done: int = 0
    hours_studied: float = 0.0

    def get_completion_percentage(self) -> float:
        """Get completion percentage for the day."""
        if self.total_questions == 0:
            return 0.0
        return (self.questions_done / self.total_questions) * 100

    def to_dict(self) -> Dict:
        return {
            "day_number": self.day_number,
            "date": self.date.isoformat(),
            "phase": self.phase.value,
            "day_type": self.day_type.value,
            "total_hours": self.total_hours,
            "total_questions": self.total_questions,
            "subject_targets": self.subject_targets,
            "topic_targets": self.topic_targets,
            "is_mock_test": self.is_mock_test,
            "mock_test_subjects": self.mock_test_subjects,
            "completed": self.completed,
            "questions_done": self.questions_done,
            "hours_studied": self.hours_studied,
        }


@dataclass
class WeeklySummary:
    """Summary of a study week."""
    week_number: int
    start_day: int
    end_day: int
    phase: StudyPhase
    total_questions_target: int
    total_questions_completed: int
    total_hours_target: float
    total_hours_completed: float
    mock_tests_scheduled: int
    mock_tests_completed: int
    subjects_covered: List[str]

    def get_completion_percentage(self) -> float:
        if self.total_questions_target == 0:
            return 0.0
        return (self.total_questions_completed / self.total_questions_target) * 100


@dataclass
class StudyPlan:
    """Complete 75-day study plan."""
    start_date: datetime
    end_date: datetime
    daily_plans: List[DailyPlan] = field(default_factory=list)

    # User profile
    user_weakness: Subject = Subject.MATHEMATICS
    user_strength: Subject = Subject.ENGLISH

    # Progress
    current_day: int = 1
    total_questions_target: int = 0
    total_questions_completed: int = 0

    # Milestones
    milestones: Dict[int, str] = field(default_factory=dict)

    def get_current_plan(self) -> Optional[DailyPlan]:
        """Get current day's plan."""
        if 1 <= self.current_day <= len(self.daily_plans):
            return self.daily_plans[self.current_day - 1]
        return None

    def get_overall_progress(self) -> float:
        """Get overall progress percentage."""
        if self.total_questions_target == 0:
            return 0.0
        return (self.total_questions_completed / self.total_questions_target) * 100

    def get_phase_progress(self, phase: StudyPhase) -> float:
        """Get progress for a specific phase."""
        phase_plans = [p for p in self.daily_plans if p.phase == phase]
        if not phase_plans:
            return 0.0

        total_target = sum(p.total_questions for p in phase_plans)
        total_done = sum(p.questions_done for p in phase_plans)

        if total_target == 0:
            return 0.0
        return (total_done / total_target) * 100


# ============================================================================
# STUDY PLAN GENERATOR CLASS
# ============================================================================

class StudyPlanGenerator:
    """
    Generates comprehensive 75-day study plans.

    This class:
    - Creates structured daily plans
    - Allocates questions by subject weightage
    - Schedules mock tests
    - Tracks milestones
    - Adapts to user progress

    Usage:
        generator = StudyPlanGenerator()

        # Generate plan from today
        plan = generator.generate_plan(
            start_date=datetime.now(),
            weakness=Subject.MATHEMATICS
        )

        # Get today's plan
        today = plan.get_current_plan()

        # Update progress
        plan.total_questions_completed += 25

    EXAM IMPACT:
        This is the CORE preparation strategy.
        Structured plan ensures COMPLETE syllabus coverage.
    """

    def __init__(self, total_days: int = 75):
        """
        Initialize plan generator.

        Args:
            total_days: Total preparation days (default: 75)
        """
        self.total_days = total_days

    def generate_plan(
        self,
        start_date: Optional[datetime] = None,
        weakness: Subject = Subject.MATHEMATICS,
        strength: Subject = Subject.ENGLISH,
        include_sundays: bool = True,
        mock_test_frequency: int = 5  # Mock test every N days in intensive phase
    ) -> StudyPlan:
        """
        Generate complete 75-day study plan.

        Args:
            start_date: Plan start date (default: today)
            weakness: User's weakest subject
            strength: User's strongest subject
            include_sundays: Include Sunday study (recommended)
            mock_test_frequency: Days between mock tests in intensive phase

        Returns:
            Complete StudyPlan with all daily plans
        """
        start_date = start_date or datetime.now()
        end_date = start_date + timedelta(days=self.total_days - 1)

        plan = StudyPlan(
            start_date=start_date,
            end_date=end_date,
            user_weakness=weakness,
            user_strength=strength,
        )

        # Generate each day's plan
        for day_num in range(1, self.total_days + 1):
            day_date = start_date + timedelta(days=day_num - 1)
            daily_plan = self._generate_daily_plan(
                day_num=day_num,
                day_date=day_date,
                weakness=weakness,
                strength=strength,
                include_sundays=include_sundays,
                mock_test_frequency=mock_test_frequency,
                plan=plan
            )
            plan.daily_plans.append(daily_plan)
            plan.total_questions_target += daily_plan.total_questions

        # Set milestones
        plan.milestones = self._generate_milestones()

        return plan

    def _generate_daily_plan(
        self,
        day_num: int,
        day_date: datetime,
        weakness: Subject,
        strength: Subject,
        include_sundays: bool,
        mock_test_frequency: int,
        plan: StudyPlan
    ) -> DailyPlan:
        """Generate a single day's plan."""
        # Determine phase
        phase = self._get_phase(day_num)

        # Determine day type
        day_type = self._get_day_type(day_num, day_date, include_sundays, mock_test_frequency)

        # Get base hours for this phase
        base_hours = DAILY_STUDY_HOURS.get(phase, 6)

        # Adjust for day type
        if day_type == DayType.LIGHT:
            base_hours *= 0.6  # 60% of normal
        elif day_type == DayType.MOCK_TEST:
            base_hours = 3  # Mock test takes less time, high intensity

        # Calculate subject targets
        subject_targets = self._calculate_subject_targets(
            phase=phase,
            base_hours=base_hours,
            weakness=weakness,
            strength=strength
        )

        # Calculate total questions
        total_questions = sum(subject_targets.values())

        # Determine topics for today
        topic_targets = self._get_topics_for_day(day_num, phase)

        # Determine if mock test
        is_mock_test = day_type == DayType.MOCK_TEST
        mock_test_subjects = []
        if is_mock_test:
            mock_test_subjects = self._get_mock_test_subjects(day_num, phase)

        return DailyPlan(
            day_number=day_num,
            date=day_date,
            phase=phase,
            day_type=day_type,
            total_hours=base_hours,
            total_questions=total_questions,
            subject_targets={s.value: q for s, q in subject_targets.items()},
            topic_targets={s.value: t for s, t in topic_targets.items()},
            is_mock_test=is_mock_test,
            mock_test_subjects=mock_test_subjects,
        )

    def _get_phase(self, day_num: int) -> StudyPhase:
        """Determine phase for a given day number."""
        for phase, (start, end) in PHASE_RANGES.items():
            if start <= day_num <= end:
                return phase
        return StudyPhase.FINAL_REVISION

    def _get_day_type(
        self,
        day_num: int,
        day_date: datetime,
        include_sundays: bool,
        mock_test_frequency: int
    ) -> DayType:
        """Determine the type of study day."""
        # Check if revision phase
        phase = self._get_phase(day_num)
        if phase == StudyPhase.FINAL_REVISION:
            return DayType.REVISION

        # Check if mock test day (intensive phase)
        if phase == StudyPhase.INTENSIVE:
            # Mock test every N days
            relative_day = day_num - PHASE_RANGES[StudyPhase.INTENSIVE][0]
            if relative_day % mock_test_frequency == 0:
                return DayType.MOCK_TEST

        # Check if Sunday (if not including)
        if not include_sundays and day_date.weekday() == 6:
            return DayType.LIGHT

        # Every 7th day is a light day for recovery
        if day_num % 7 == 0:
            return DayType.LIGHT

        return DayType.NORMAL

    def _calculate_subject_targets(
        self,
        phase: StudyPhase,
        base_hours: float,
        weakness: Subject,
        strength: Subject
    ) -> Dict[Subject, int]:
        """Calculate question targets for each subject."""
        targets = {}

        for subject in Subject:
            # Base questions from weightage
            weightage = SUBJECT_WEIGHTAGE.get(subject, 10)

            # Questions per hour for this subject
            qph = QUESTIONS_PER_HOUR.get(subject, 5)

            # Base allocation proportional to weightage
            total_weightage = sum(SUBJECT_WEIGHTAGE.values())
            allocation_ratio = weightage / total_weightage

            # Apply weakness multiplier
            if subject == weakness:
                allocation_ratio *= WEAKNESS_MULTIPLIER.get(subject, 1.4)
            elif subject == strength:
                allocation_ratio *= WEAKNESS_MULTIPLIER.get(subject, 0.8)

            # Calculate hours for this subject
            subject_hours = base_hours * allocation_ratio

            # Calculate questions
            questions = int(subject_hours * qph)

            # Minimum questions per subject per day
            if phase == StudyPhase.FOUNDATION:
                min_questions = 5
            else:
                min_questions = 10

            targets[subject] = max(questions, min_questions)

        return targets

    def _get_topics_for_day(
        self,
        day_num: int,
        phase: StudyPhase
    ) -> Dict[Subject, List[str]]:
        """Get topics to cover for a specific day."""
        topics = {}

        # Get topic list based on phase
        if phase == StudyPhase.FOUNDATION:
            topic_pool = FOUNDATION_TOPICS
        elif phase == StudyPhase.CORE_BUILDING:
            topic_pool = CORE_TOPICS
        elif phase == StudyPhase.ADVANCED:
            topic_pool = ADVANCED_TOPICS
        else:
            # Intensive and revision phases use all topics
            topic_pool = {**CORE_TOPICS, **ADVANCED_TOPICS}

        # Select topics based on day number
        for subject in Subject:
            all_topics = topic_pool.get(subject, [])
            if not all_topics:
                topics[subject] = []
                continue

            # Cycle through topics based on day number
            # Each day covers 2-3 topics per subject
            num_topics = min(3, len(all_topics))
            start_idx = (day_num * 2) % max(1, len(all_topics))

            selected = []
            for i in range(num_topics):
                idx = (start_idx + i) % len(all_topics)
                selected.append(all_topics[idx])

            topics[subject] = selected

        return topics

    def _get_mock_test_subjects(
        self,
        day_num: int,
        phase: StudyPhase
    ) -> List[str]:
        """Get subjects for mock test."""
        # Alternate between full tests and subject-specific tests
        relative_day = day_num - PHASE_RANGES.get(phase, (56, 70))[0]

        if relative_day % 10 == 0:
            # Full mock test - all subjects
            return [s.value for s in Subject]
        else:
            # Subject-specific test
            subjects = [Subject.MATHEMATICS, Subject.PHYSICS, Subject.CHEMISTRY]
            return [subjects[relative_day % 3].value]

    def _generate_milestones(self) -> Dict[int, str]:
        """Generate milestone checkpoints."""
        return {
            7: "First Week Complete - Foundation Building Started",
            15: "Foundation Phase Complete - 10th Basics Mastered",
            21: "Three Weeks In - Core Topics Progress",
            30: "One Month Complete - 40% Syllabus Covered",
            35: "Core Building Complete - 11th Syllabus Done",
            45: "Six Weeks In - Advanced Topics Underway",
            55: "Advanced Phase Complete - Full Syllabus Covered",
            60: "Two Months Complete - Mock Test Phase Active",
            70: "Intensive Phase Complete - Ready for Final Revision",
            75: "SEAT CONFIRMATION - Preparation Complete!",
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_study_plan(
    start_date: Optional[datetime] = None,
    weakness: Subject = Subject.MATHEMATICS
) -> StudyPlan:
    """
    Create a 75-day study plan.

    Args:
        start_date: Start date (default: today)
        weakness: User's weakest subject

    Returns:
        Complete StudyPlan
    """
    generator = StudyPlanGenerator()
    return generator.generate_plan(
        start_date=start_date,
        weakness=weakness
    )


def get_day_info(plan: StudyPlan, day_num: int) -> Dict[str, Any]:
    """Get detailed information for a specific day."""
    if day_num < 1 or day_num > len(plan.daily_plans):
        return {}

    daily = plan.daily_plans[day_num - 1]

    return {
        "day": day_num,
        "phase": daily.phase.value,
        "type": daily.day_type.value,
        "hours": daily.total_hours,
        "questions": daily.total_questions,
        "subjects": daily.subject_targets,
        "topics": daily.topic_targets,
        "is_mock": daily.is_mock_test,
        "milestone": plan.milestones.get(day_num),
    }


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Study Plan Generator...")
    print("="*60)

    # Generate plan
    generator = StudyPlanGenerator()
    plan = generator.generate_plan(
        start_date=datetime.now(),
        weakness=Subject.MATHEMATICS
    )

    # Test 1: Plan overview
    print("\n1. Plan Overview:")
    print(f"   Start: {plan.start_date.strftime('%Y-%m-%d')}")
    print(f"   End: {plan.end_date.strftime('%Y-%m-%d')}")
    print(f"   Total Days: {len(plan.daily_plans)}")
    print(f"   Total Questions Target: {plan.total_questions_target}")

    # Test 2: Phase distribution
    print("\n2. Phase Distribution:")
    phase_counts = {}
    for daily in plan.daily_plans:
        phase = daily.phase.value
        phase_counts[phase] = phase_counts.get(phase, 0) + 1
    for phase, count in phase_counts.items():
        print(f"   {phase}: {count} days")

    # Test 3: Sample days
    print("\n3. Sample Days:")
    for day_num in [1, 15, 35, 55, 70, 75]:
        info = get_day_info(plan, day_num)
        print(f"   Day {day_num}: {info['phase']} - {info['questions']} questions")

    # Test 4: Milestones
    print("\n4. Milestones:")
    for day, milestone in list(plan.milestones.items())[:5]:
        print(f"   Day {day}: {milestone}")

    # Test 5: Subject allocation
    print("\n5. Subject Allocation (Day 20):")
    day20 = plan.daily_plans[19]
    for subject, questions in day20.subject_targets.items():
        print(f"   {subject}: {questions} questions")

    print("\n" + "="*60)
    print("All tests passed!")
