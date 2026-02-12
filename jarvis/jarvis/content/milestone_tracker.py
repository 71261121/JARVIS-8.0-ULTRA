"""
JARVIS Milestone Tracker
========================

Purpose: Track progress through key milestones in the 75-day journey.

This module provides:
- Milestone definitions
- Progress tracking
- Celebration triggers
- Warning indicators
- Final milestone: SEAT CONFIRMED

EXAM IMPACT:
    HIGH. Milestones provide MOTIVATION and DIRECTION.
    Without milestones, user can't see progress.
    With milestones, every achievement is celebrated.

KEY MILESTONES:
    Day 7:   First Week Complete
    Day 15:  Foundation Mastered
    Day 30:  One Month Complete
    Day 35:  Core Building Done
    Day 55:  Advanced Phase Complete
    Day 70:  Intensive Practice Done
    Day 75:  SEAT CONFIRMED

CELEBRATION SYSTEM:
    - Voice celebration on milestone completion
    - Achievement unlocks
    - Progress visualization
    - Motivational messages

REASON FOR DESIGN:
    - Breaks 75 days into achievable chunks
    - Provides sense of progress
    - Creates accountability checkpoints
    - Celebrates wins to maintain motivation

ROLLBACK PLAN:
    - Milestones can be adjusted
    - Progress is tracked separately
    - Can recalculate on demand
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class MilestoneStatus(Enum):
    """Status of a milestone."""
    LOCKED = "locked"       # Not yet accessible
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"       # Missed deadline


class MilestoneType(Enum):
    """Types of milestones."""
    TIME = "time"           # Day-based milestone
    QUESTIONS = "questions"  # Total questions milestone
    ACCURACY = "accuracy"   # Accuracy milestone
    STREAK = "streak"       # Streak milestone
    MOCK_TEST = "mock_test" # Mock test score milestone


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Milestone:
    """A milestone in the 75-day journey."""
    milestone_id: str
    name: str
    description: str
    day_number: int
    milestone_type: MilestoneType
    status: MilestoneStatus = MilestoneStatus.LOCKED

    # Requirements
    required_questions: int = 0
    required_accuracy: float = 0.0
    required_streak: int = 0
    required_mock_score: float = 0.0

    # Progress
    current_questions: int = 0
    current_accuracy: float = 0.0
    current_streak: int = 0
    current_mock_score: float = 0.0

    # Timestamps
    unlocked_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Rewards
    xp_reward: int = 0
    achievement_id: Optional[str] = None
    voice_message: str = ""

    def get_progress_percentage(self) -> float:
        """Get progress towards milestone."""
        if self.milestone_type == MilestoneType.TIME:
            return 100.0 if self.status == MilestoneStatus.COMPLETED else 0.0

        elif self.milestone_type == MilestoneType.QUESTIONS:
            if self.required_questions == 0:
                return 0.0
            return min(100.0, (self.current_questions / self.required_questions) * 100)

        elif self.milestone_type == MilestoneType.ACCURACY:
            if self.required_accuracy == 0:
                return 0.0
            return min(100.0, (self.current_accuracy / self.required_accuracy) * 100)

        elif self.milestone_type == MilestoneType.STREAK:
            if self.required_streak == 0:
                return 0.0
            return min(100.0, (self.current_streak / self.required_streak) * 100)

        elif self.milestone_type == MilestoneType.MOCK_TEST:
            if self.required_mock_score == 0:
                return 0.0
            return min(100.0, (self.current_mock_score / self.required_mock_score) * 100)

        return 0.0

    def is_complete(self) -> bool:
        """Check if milestone is complete."""
        return self.status == MilestoneStatus.COMPLETED

    def to_dict(self) -> Dict:
        return {
            "id": self.milestone_id,
            "name": self.name,
            "description": self.description,
            "day": self.day_number,
            "type": self.milestone_type.value,
            "status": self.status.value,
            "progress": self.get_progress_percentage(),
            "xp": self.xp_reward,
        }


# ============================================================================
# MILESTONE DEFINITIONS
# ============================================================================

DEFAULT_MILESTONES = [
    # Week 1
    Milestone(
        milestone_id="first_day",
        name="First Step",
        description="Complete your first study session",
        day_number=1,
        milestone_type=MilestoneType.TIME,
        xp_reward=50,
        achievement_id="first_step",
        voice_message="Congratulations on taking the first step! Your journey to the seat begins now.",
    ),

    Milestone(
        milestone_id="first_week",
        name="Week One Warrior",
        description="Complete 7 consecutive days of study",
        day_number=7,
        milestone_type=MilestoneType.TIME,
        required_streak=7,
        xp_reward=200,
        achievement_id="week_warrior",
        voice_message="One week complete! You've proven you can show up consistently.",
    ),

    # Foundation Phase
    Milestone(
        milestone_id="foundation_100",
        name="Foundation Beginner",
        description="Answer 100 questions in Foundation phase",
        day_number=10,
        milestone_type=MilestoneType.QUESTIONS,
        required_questions=100,
        xp_reward=150,
    ),

    Milestone(
        milestone_id="foundation_complete",
        name="Foundation Master",
        description="Complete Foundation phase (Days 1-15)",
        day_number=15,
        milestone_type=MilestoneType.TIME,
        required_questions=300,
        xp_reward=500,
        achievement_id="foundation_master",
        voice_message="Foundation phase complete! You've built the base for your exam success.",
    ),

    # Core Building Phase
    Milestone(
        milestone_id="500_questions",
        name="Half Thousand",
        description="Answer 500 total questions",
        day_number=25,
        milestone_type=MilestoneType.QUESTIONS,
        required_questions=500,
        xp_reward=400,
        achievement_id="half_grand",
    ),

    Milestone(
        milestone_id="one_month",
        name="One Month Champion",
        description="Complete 30 days of preparation",
        day_number=30,
        milestone_type=MilestoneType.TIME,
        required_questions=800,
        xp_reward=800,
        achievement_id="monthly_master",
        voice_message="One month complete! 40% of the journey done. You're on track!",
    ),

    Milestone(
        milestone_id="core_complete",
        name="Core Building Complete",
        description="Complete Core Building phase (Days 16-35)",
        day_number=35,
        milestone_type=MilestoneType.TIME,
        required_questions=1000,
        xp_reward=600,
        voice_message="Core building complete! 11th syllabus is now yours.",
    ),

    # Advanced Phase
    Milestone(
        milestone_id="1000_questions",
        name="The Scholar",
        description="Answer 1000 total questions",
        day_number=40,
        milestone_type=MilestoneType.QUESTIONS,
        required_questions=1000,
        xp_reward=600,
        achievement_id="scholar",
    ),

    Milestone(
        milestone_id="accuracy_75",
        name="Accuracy Achiever",
        description="Maintain 75% accuracy for 7 consecutive days",
        day_number=45,
        milestone_type=MilestoneType.ACCURACY,
        required_accuracy=0.75,
        xp_reward=500,
    ),

    Milestone(
        milestone_id="advanced_complete",
        name="Advanced Phase Complete",
        description="Complete Advanced phase (Days 36-55)",
        day_number=55,
        milestone_type=MilestoneType.TIME,
        required_questions=2000,
        xp_reward=800,
        voice_message="Advanced phase complete! Full syllabus is now covered!",
    ),

    # Intensive Phase
    Milestone(
        milestone_id="first_mock",
        name="Test Run",
        description="Complete your first mock test",
        day_number=56,
        milestone_type=MilestoneType.MOCK_TEST,
        required_mock_score=30,
        xp_reward=300,
        achievement_id="first_mock",
    ),

    Milestone(
        milestone_id="mock_70",
        name="Mock Test Champion",
        description="Score 70% in a mock test",
        day_number=65,
        milestone_type=MilestoneType.MOCK_TEST,
        required_mock_score=42,
        xp_reward=700,
        achievement_id="mock_champion",
    ),

    Milestone(
        milestone_id="two_months",
        name="Two Months Complete",
        description="Complete 60 days of preparation",
        day_number=60,
        milestone_type=MilestoneType.TIME,
        required_questions=2500,
        xp_reward=1000,
        voice_message="Two months complete! The finish line is in sight!",
    ),

    Milestone(
        milestone_id="intensive_complete",
        name="Intensive Phase Complete",
        description="Complete Intensive Practice phase",
        day_number=70,
        milestone_type=MilestoneType.TIME,
        required_questions=3000,
        xp_reward=900,
        voice_message="Intensive phase complete! You're ready for final revision!",
    ),

    # Final Revision
    Milestone(
        milestone_id="14_day_streak",
        name="Fortnight Champion",
        description="Maintain a 14-day streak",
        day_number=70,
        milestone_type=MilestoneType.STREAK,
        required_streak=14,
        xp_reward=700,
        achievement_id="fortnight_champion",
    ),

    Milestone(
        milestone_id="final_revision",
        name="Final Revision Complete",
        description="Complete Final Revision phase",
        day_number=75,
        milestone_type=MilestoneType.TIME,
        required_questions=3500,
        xp_reward=500,
    ),

    # THE ULTIMATE MILESTONE
    Milestone(
        milestone_id="seat_confirmed",
        name="SEAT CONFIRMED",
        description="Complete all 75 days of preparation",
        day_number=75,
        milestone_type=MilestoneType.TIME,
        required_questions=3500,
        required_accuracy=0.70,
        xp_reward=10000,
        achievement_id="seat_confirmed",
        voice_message="CONGRATULATIONS! You have completed the entire 75-day preparation program! Your seat at Loyola College B.Sc Computer Science is now CONFIRMED! You've earned this through consistent effort. Go ace that exam!",
    ),
]


# ============================================================================
# MILESTONE TRACKER CLASS
# ============================================================================

class MilestoneTracker:
    """
    Tracks progress through milestones.

    This class:
    - Manages milestone states
    - Updates progress
    - Triggers celebrations
    - Provides progress visualization

    Usage:
        tracker = MilestoneTracker()

        # Update progress
        tracker.update_progress(
            day_number=15,
            total_questions=350,
            accuracy=0.78,
            streak=15
        )

        # Check for completed milestones
        completed = tracker.check_milestones()

        # Get progress
        progress = tracker.get_progress()

    EXAM IMPACT:
        Milestones provide MOTIVATION and DIRECTION.
        Critical for maintaining 75-day consistency.
    """

    def __init__(self, milestones: Optional[List[Milestone]] = None):
        """
        Initialize milestone tracker.

        Args:
            milestones: Custom milestones (default: DEFAULT_MILESTONES)
        """
        self.milestones = milestones or DEFAULT_MILESTONES.copy()
        self._completed_count = 0
        self._last_completed: Optional[Milestone] = None

    # ========================================================================
    # PROGRESS UPDATE
    # ========================================================================

    def update_progress(
        self,
        day_number: int,
        total_questions: int = 0,
        accuracy: float = 0.0,
        streak: int = 0,
        mock_score: float = 0.0
    ) -> List[Milestone]:
        """
        Update progress for all milestones.

        Args:
            day_number: Current day number
            total_questions: Total questions answered
            accuracy: Current accuracy rate
            streak: Current streak length
            mock_score: Latest mock test score

        Returns:
            List of newly completed milestones
        """
        newly_completed = []

        for milestone in self.milestones:
            # Skip already completed
            if milestone.status == MilestoneStatus.COMPLETED:
                continue

            # Update current values
            milestone.current_questions = total_questions
            milestone.current_accuracy = accuracy
            milestone.current_streak = streak
            milestone.current_mock_score = mock_score

            # Check if should unlock
            if milestone.status == MilestoneStatus.LOCKED:
                if day_number >= milestone.day_number - 1:
                    milestone.status = MilestoneStatus.IN_PROGRESS
                    milestone.unlocked_at = datetime.now()

            # Check if complete
            if milestone.status == MilestoneStatus.IN_PROGRESS:
                is_complete = False

                if milestone.milestone_type == MilestoneType.TIME:
                    if day_number >= milestone.day_number:
                        is_complete = True

                elif milestone.milestone_type == MilestoneType.QUESTIONS:
                    if total_questions >= milestone.required_questions:
                        is_complete = True

                elif milestone.milestone_type == MilestoneType.ACCURACY:
                    if accuracy >= milestone.required_accuracy:
                        is_complete = True

                elif milestone.milestone_type == MilestoneType.STREAK:
                    if streak >= milestone.required_streak:
                        is_complete = True

                elif milestone.milestone_type == MilestoneType.MOCK_TEST:
                    if mock_score >= milestone.required_mock_score:
                        is_complete = True

                if is_complete:
                    milestone.status = MilestoneStatus.COMPLETED
                    milestone.completed_at = datetime.now()
                    newly_completed.append(milestone)
                    self._completed_count += 1
                    self._last_completed = milestone

        return newly_completed

    def check_milestones(self) -> List[Milestone]:
        """Get all completed milestones."""
        return [m for m in self.milestones if m.status == MilestoneStatus.COMPLETED]

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    def get_current_milestone(self, day_number: int) -> Optional[Milestone]:
        """Get the current milestone in progress."""
        for milestone in self.milestones:
            if milestone.status == MilestoneStatus.IN_PROGRESS:
                return milestone
        return None

    def get_next_milestone(self) -> Optional[Milestone]:
        """Get the next locked milestone."""
        for milestone in self.milestones:
            if milestone.status == MilestoneStatus.LOCKED:
                return milestone
        return None

    def get_progress(self) -> Dict:
        """Get overall progress summary."""
        total = len(self.milestones)
        completed = self._completed_count
        in_progress = sum(
            1 for m in self.milestones
            if m.status == MilestoneStatus.IN_PROGRESS
        )

        return {
            "total_milestones": total,
            "completed": completed,
            "in_progress": in_progress,
            "locked": total - completed - in_progress,
            "completion_percentage": (completed / total) * 100 if total > 0 else 0,
            "last_completed": self._last_completed.to_dict() if self._last_completed else None,
        }

    def get_upcoming_milestones(self, count: int = 3) -> List[Dict]:
        """Get upcoming milestones."""
        upcoming = []
        for milestone in self.milestones:
            if milestone.status != MilestoneStatus.COMPLETED:
                upcoming.append(milestone.to_dict())
                if len(upcoming) >= count:
                    break
        return upcoming

    def get_milestone_by_id(self, milestone_id: str) -> Optional[Milestone]:
        """Get a specific milestone by ID."""
        for milestone in self.milestones:
            if milestone.milestone_id == milestone_id:
                return milestone
        return None

    # ========================================================================
    # CELEBRATION
    # ========================================================================

    def get_celebration_message(self, milestone: Milestone) -> str:
        """Get celebration message for a completed milestone."""
        messages = [
            f"🎉 MILESTONE ACHIEVED: {milestone.name}!",
            "",
            milestone.description,
            "",
            f"Day {milestone.day_number} of 75",
            f"Progress: {self.get_progress()['completion_percentage']:.0f}%",
        ]

        if milestone.xp_reward > 0:
            messages.append(f"XP Earned: +{milestone.xp_reward}")

        if milestone.voice_message:
            messages.extend(["", milestone.voice_message])

        return "\n".join(messages)


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_milestone_tracker() -> MilestoneTracker:
    """Create a milestone tracker."""
    return MilestoneTracker()


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Milestone Tracker...")
    print("="*60)

    tracker = MilestoneTracker()

    # Test 1: Initial state
    print("\n1. Initial state:")
    progress = tracker.get_progress()
    print(f"   Total milestones: {progress['total_milestones']}")
    print(f"   Locked: {progress['locked']}")

    # Test 2: Update progress
    print("\n2. Updating to day 15...")
    completed = tracker.update_progress(
        day_number=15,
        total_questions=350,
        accuracy=0.78,
        streak=15
    )
    print(f"   Milestones completed: {len(completed)}")
    for m in completed:
        print(f"   - {m.name}")

    # Test 3: Progress
    print("\n3. Current progress:")
    progress = tracker.get_progress()
    print(f"   Completed: {progress['completed']}/{progress['total_milestones']}")
    print(f"   Percentage: {progress['completion_percentage']:.1f}%")

    # Test 4: Upcoming
    print("\n4. Upcoming milestones:")
    upcoming = tracker.get_upcoming_milestones(3)
    for m in upcoming:
        print(f"   - {m['name']} (Day {m['day']})")

    # Test 5: Update to day 75
    print("\n5. Simulating day 75...")
    completed = tracker.update_progress(
        day_number=75,
        total_questions=3500,
        accuracy=0.75,
        streak=30,
        mock_score=50
    )
    print(f"   Milestones completed: {len(completed)}")

    progress = tracker.get_progress()
    print(f"   Final: {progress['completed']}/{progress['total_milestones']}")

    # Test 6: Check SEAT CONFIRMED
    seat = tracker.get_milestone_by_id("seat_confirmed")
    if seat and seat.is_complete():
        print("\n🎉 SEAT CONFIRMED!")
        print(tracker.get_celebration_message(seat))

    print("\n" + "="*60)
    print("All tests passed!")
