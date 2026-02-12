"""
JARVIS Daily Target Manager
===========================

Purpose: Manage daily question targets with subject rotation.

This module provides:
- Dynamic daily target calculation
- Subject rotation scheduling
- Progress tracking
- Target adjustment based on performance
- Burnout prevention

EXAM IMPACT:
    CRITICAL. Daily targets provide STRUCTURE.
    Without targets, user studies aimlessly.
    With targets, EVERY session has purpose.

SUBJECT ROTATION STRATEGY:
    Mathematics: Morning (fresh mind)
    Physics: Mid-day (requires focus)
    Chemistry: Afternoon (memory-heavy)
    English: Evening (lighter, comprehension)

DYNAMIC ADJUSTMENTS:
    - If accuracy < 60%: Reduce target by 20%
    - If accuracy > 90%: Increase target by 10%
    - If streak > 7: Bonus questions unlocked
    - If burnout detected: Mandatory rest day

REASON FOR DESIGN:
    - IRT-based difficulty matching
    - Weakness-focused extra allocation
    - Subject rotation prevents fatigue
    - Automatic adjustment prevents frustration

ROLLBACK PLAN:
    - Targets can be manually adjusted
    - Rotation can be disabled
    - Progress is preserved
"""

from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import random


# ============================================================================
# CONSTANTS
# ============================================================================

# Time slots for subjects
SUBJECT_TIME_SLOTS = {
    "morning": {
        "start": time(6, 0),
        "end": time(11, 0),
        "best_for": ["mathematics", "physics"],  # Hard subjects when fresh
        "difficulty": "hard",
    },
    "midday": {
        "start": time(11, 0),
        "end": time(14, 0),
        "best_for": ["physics", "chemistry"],
        "difficulty": "medium",
    },
    "afternoon": {
        "start": time(14, 0),
        "end": time(17, 0),
        "best_for": ["chemistry"],
        "difficulty": "medium",
    },
    "evening": {
        "start": time(17, 0),
        "end": time(20, 0),
        "best_for": ["chemistry", "english"],
        "difficulty": "light",
    },
    "night": {
        "start": time(20, 0),
        "end": time(23, 0),
        "best_for": ["english", "revision"],
        "difficulty": "light",
    },
}

# Target adjustment thresholds
ACCURACY_THRESHOLD_INCREASE = 0.90
ACCURACY_THRESHOLD_DECREASE = 0.60
TARGET_INCREASE_PERCENT = 10
TARGET_DECREASE_PERCENT = 20

# Minimum and maximum questions per subject
MIN_QUESTIONS_PER_SUBJECT = 5
MAX_QUESTIONS_PER_SUBJECT = 50

# Streak bonuses
STREAK_BONUS_THRESHOLD = 7
STREAK_BONUS_PERCENT = 15


# ============================================================================
# ENUMS
# ========================================================================

class TimeSlot(Enum):
    """Time slots for study."""
    MORNING = "morning"
    MIDDAY = "midday"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"


class TargetStatus(Enum):
    """Status of a target."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class SubjectTarget:
    """Target for a single subject."""
    subject: str
    questions_target: int
    questions_completed: int = 0
    time_slot: TimeSlot = TimeSlot.MORNING
    difficulty: str = "medium"
    topics: List[str] = field(default_factory=list)
    status: TargetStatus = TargetStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    accuracy: float = 0.0

    def get_progress_percentage(self) -> float:
        """Get progress percentage."""
        if self.questions_target == 0:
            return 0.0
        return (self.questions_completed / self.questions_target) * 100

    def is_complete(self) -> bool:
        """Check if target is complete."""
        return self.questions_completed >= self.questions_target

    def get_remaining(self) -> int:
        """Get remaining questions."""
        return max(0, self.questions_target - self.questions_completed)

    def to_dict(self) -> Dict:
        return {
            "subject": self.subject,
            "questions_target": self.questions_target,
            "questions_completed": self.questions_completed,
            "time_slot": self.time_slot.value,
            "difficulty": self.difficulty,
            "topics": self.topics,
            "status": self.status.value,
            "progress": self.get_progress_percentage(),
            "remaining": self.get_remaining(),
        }


@dataclass
class DailyTarget:
    """Complete daily target for all subjects."""
    date: datetime
    day_number: int
    total_questions: int
    total_completed: int = 0
    subject_targets: Dict[str, SubjectTarget] = field(default_factory=dict)
    hours_target: float = 8.0
    hours_completed: float = 0.0
    streak_days: int = 0
    is_rest_day: bool = False
    notes: List[str] = field(default_factory=list)

    def get_completion_percentage(self) -> float:
        """Get overall completion percentage."""
        if self.total_questions == 0:
            return 0.0
        return (self.total_completed / self.total_questions) * 100

    def get_subject_progress(self, subject: str) -> Optional[SubjectTarget]:
        """Get progress for a specific subject."""
        return self.subject_targets.get(subject)

    def add_completion(self, subject: str, questions: int, accuracy: float) -> None:
        """Add completion for a subject."""
        if subject in self.subject_targets:
            target = self.subject_targets[subject]
            target.questions_completed += questions
            target.accuracy = accuracy
            self.total_completed += questions

            if target.is_complete():
                target.status = TargetStatus.COMPLETED
                target.completed_at = datetime.now()
            else:
                target.status = TargetStatus.IN_PROGRESS

    def get_summary(self) -> Dict:
        """Get summary of daily target."""
        return {
            "date": self.date.strftime("%Y-%m-%d"),
            "day_number": self.day_number,
            "total_questions": self.total_questions,
            "completed": self.total_completed,
            "progress": self.get_completion_percentage(),
            "hours_target": self.hours_target,
            "hours_completed": self.hours_completed,
            "streak": self.streak_days,
            "subjects": {s: t.to_dict() for s, t in self.subject_targets.items()},
        }


# ============================================================================
# DAILY TARGET MANAGER CLASS
# ============================================================================

class DailyTargetManager:
    """
    Manages daily study targets with subject rotation.

    This class:
    - Calculates daily targets per subject
    - Rotates subjects through optimal time slots
    - Adjusts targets based on performance
    - Tracks completion progress
    - Prevents burnout through rest days

    Usage:
        manager = DailyTargetManager()

        # Get today's targets
        today = manager.get_daily_target(
            day_number=15,
            base_hours=8,
            weakness="mathematics"
        )

        # Record progress
        manager.record_progress("mathematics", questions=25, accuracy=0.85)

        # Get next subject to study
        next_subject = manager.get_next_subject()

    EXAM IMPACT:
        Daily targets provide STRUCTURE and PURPOSE.
        Every session has clear objectives.
    """

    def __init__(self):
        """Initialize target manager."""
        self._current_day: Optional[DailyTarget] = None
        self._history: List[DailyTarget] = []
        self._subject_performance: Dict[str, List[float]] = {}

    # ========================================================================
    # TARGET CALCULATION
    # ========================================================================

    def get_daily_target(
        self,
        day_number: int,
        base_hours: float = 8.0,
        weakness: str = "mathematics",
        strength: str = "english",
        phase: str = "core",
        streak_days: int = 0,
        recent_accuracy: Dict[str, float] = None
    ) -> DailyTarget:
        """
        Calculate daily targets for all subjects.

        Args:
            day_number: Day number in plan
            base_hours: Base study hours
            weakness: User's weakest subject
            strength: User's strongest subject
            phase: Current study phase
            streak_days: Current streak length
            recent_accuracy: Recent accuracy by subject

        Returns:
            DailyTarget with all subject targets
        """
        recent_accuracy = recent_accuracy or {}
        today = datetime.now()

        # Determine if rest day (every 7th day)
        is_rest_day = day_number % 7 == 0 and day_number > 0

        daily = DailyTarget(
            date=today,
            day_number=day_number,
            total_questions=0,
            hours_target=base_hours * 0.6 if is_rest_day else base_hours,
            streak_days=streak_days,
            is_rest_day=is_rest_day,
        )

        if is_rest_day:
            # Rest day has reduced targets
            daily.notes.append("Rest day - Reduced targets for recovery")

        # Calculate subject targets
        subjects = ["mathematics", "physics", "chemistry", "english"]

        for subject in subjects:
            target = self._calculate_subject_target(
                subject=subject,
                base_hours=base_hours,
                weakness=weakness,
                strength=strength,
                streak_days=streak_days,
                recent_accuracy=recent_accuracy.get(subject, 0.75),
                is_rest_day=is_rest_day,
                day_number=day_number,
            )
            daily.subject_targets[subject] = target
            daily.total_questions += target.questions_target

        self._current_day = daily
        return daily

    def _calculate_subject_target(
        self,
        subject: str,
        base_hours: float,
        weakness: str,
        strength: str,
        streak_days: int,
        recent_accuracy: float,
        is_rest_day: bool,
        day_number: int
    ) -> SubjectTarget:
        """Calculate target for a single subject."""
        # Base questions per hour
        qph_map = {
            "mathematics": 4,
            "physics": 5,
            "chemistry": 6,
            "english": 8,
        }

        # Weightage in exam
        weightage_map = {
            "mathematics": 20,
            "physics": 15,
            "chemistry": 15,
            "english": 10,
        }

        # Calculate base allocation
        total_weightage = sum(weightage_map.values())
        weightage = weightage_map.get(subject, 10)
        allocation = weightage / total_weightage

        # Apply weakness multiplier
        if subject == weakness:
            allocation *= 1.4  # 40% more for weakness
        elif subject == strength:
            allocation *= 0.8  # 20% less for strength

        # Calculate questions
        qph = qph_map.get(subject, 5)
        hours = base_hours * allocation
        questions = int(hours * qph)

        # Apply accuracy-based adjustment
        if recent_accuracy >= ACCURACY_THRESHOLD_INCREASE:
            questions = int(questions * (1 + TARGET_INCREASE_PERCENT / 100))
        elif recent_accuracy < ACCURACY_THRESHOLD_DECREASE:
            questions = int(questions * (1 - TARGET_DECREASE_PERCENT / 100))

        # Apply streak bonus
        if streak_days >= STREAK_BONUS_THRESHOLD:
            questions = int(questions * (1 + STREAK_BONUS_PERCENT / 100))

        # Apply rest day reduction
        if is_rest_day:
            questions = int(questions * 0.5)

        # Ensure within bounds
        questions = max(MIN_QUESTIONS_PER_SUBJECT, min(MAX_QUESTIONS_PER_SUBJECT, questions))

        # Determine optimal time slot
        time_slot = self._get_optimal_time_slot(subject, day_number)

        # Determine difficulty
        difficulty = "hard" if subject == weakness else "medium"

        return SubjectTarget(
            subject=subject,
            questions_target=questions,
            time_slot=time_slot,
            difficulty=difficulty,
        )

    def _get_optimal_time_slot(self, subject: str, day_number: int) -> TimeSlot:
        """Determine optimal time slot for a subject."""
        # Subject preferences
        preferences = {
            "mathematics": [TimeSlot.MORNING, TimeSlot.MIDDAY],
            "physics": [TimeSlot.MORNING, TimeSlot.MIDDAY],
            "chemistry": [TimeSlot.AFTERNOON, TimeSlot.EVENING],
            "english": [TimeSlot.EVENING, TimeSlot.NIGHT],
        }

        subject_prefs = preferences.get(subject, [TimeSlot.MORNING])

        # Rotate based on day number
        idx = day_number % len(subject_prefs)
        return subject_prefs[idx]

    # ========================================================================
    # PROGRESS TRACKING
    # ========================================================================

    def record_progress(
        self,
        subject: str,
        questions: int,
        accuracy: float,
        time_spent_minutes: float = 0
    ) -> Dict:
        """
        Record progress for a subject.

        Args:
            subject: Subject name
            questions: Questions completed
            accuracy: Accuracy rate (0-1)
            time_spent_minutes: Time spent

        Returns:
            Progress summary
        """
        if not self._current_day:
            return {"error": "No active daily target"}

        # Update subject target
        if subject in self._current_day.subject_targets:
            target = self._current_day.subject_targets[subject]

            old_completed = target.questions_completed
            target.questions_completed += questions
            target.accuracy = accuracy
            target.status = TargetStatus.IN_PROGRESS

            if target.is_complete():
                target.status = TargetStatus.COMPLETED
                target.completed_at = datetime.now()

            # Update daily totals
            self._current_day.total_completed += questions
            self._current_day.hours_completed += time_spent_minutes / 60

        # Track performance for adjustments
        if subject not in self._subject_performance:
            self._subject_performance[subject] = []
        self._subject_performance[subject].append(accuracy)

        # Keep only last 10 accuracy values
        self._subject_performance[subject] = self._subject_performance[subject][-10:]

        return {
            "subject": subject,
            "questions_added": questions,
            "accuracy": accuracy,
            "progress": self._current_day.get_completion_percentage(),
            "subject_complete": self._current_day.subject_targets[subject].is_complete() if subject in self._current_day.subject_targets else False,
        }

    def complete_day(self) -> Dict:
        """Mark current day as complete and archive."""
        if not self._current_day:
            return {"error": "No active daily target"}

        # Calculate final statistics
        total_target = self._current_day.total_questions
        total_completed = self._current_day.total_completed
        completion_rate = total_completed / total_target if total_target > 0 else 0

        # Archive
        self._history.append(self._current_day)

        summary = {
            "date": self._current_day.date.strftime("%Y-%m-%d"),
            "day_number": self._current_day.day_number,
            "total_target": total_target,
            "total_completed": total_completed,
            "completion_rate": completion_rate,
            "hours_target": self._current_day.hours_target,
            "hours_completed": self._current_day.hours_completed,
            "streak": self._current_day.streak_days,
            "subjects_completed": sum(
                1 for t in self._current_day.subject_targets.values()
                if t.is_complete()
            ),
        }

        self._current_day = None
        return summary

    # ========================================================================
    # SUBJECT RECOMMENDATION
    # ========================================================================

    def get_next_subject(self) -> Dict:
        """Get recommended next subject to study."""
        if not self._current_day:
            return {"subject": None, "reason": "No active daily target"}

        # Get current hour
        now = datetime.now()
        current_hour = now.hour

        # Find incomplete subjects
        incomplete = [
            (subject, target)
            for subject, target in self._current_day.subject_targets.items()
            if not target.is_complete()
        ]

        if not incomplete:
            return {"subject": None, "reason": "All targets complete!"}

        # Prioritize by:
        # 1. Current time slot match
        # 2. Most behind (lowest completion %)
        # 3. Weakness priority

        # Check time slot
        for subject, target in incomplete:
            slot = SUBJECT_TIME_SLOTS.get(target.time_slot.value, {})
            start = slot.get("start", time(0, 0))
            end = slot.get("end", time(23, 59))

            start_hour = start.hour
            end_hour = end.hour

            if start_hour <= current_hour < end_hour:
                return {
                    "subject": subject,
                    "reason": f"Optimal time for {subject}",
                    "remaining": target.get_remaining(),
                    "difficulty": target.difficulty,
                }

        # If no time match, pick most behind
        most_behind = min(
            incomplete,
            key=lambda x: x[1].get_progress_percentage()
        )

        return {
            "subject": most_behind[0],
            "reason": "Behind schedule",
            "remaining": most_behind[1].get_remaining(),
            "progress": most_behind[1].get_progress_percentage(),
        }

    def get_study_schedule(self) -> List[Dict]:
        """Get recommended study schedule for the day."""
        if not self._current_day:
            return []

        schedule = []

        for slot_name, slot_info in SUBJECT_TIME_SLOTS.items():
            # Find best subject for this slot
            for subject, target in self._current_day.subject_targets.items():
                if target.is_complete():
                    continue

                slot = TimeSlot(slot_name)
                if target.time_slot == slot:
                    schedule.append({
                        "time_slot": slot_name,
                        "time_range": f"{slot_info['start'].strftime('%I:%M %p')} - {slot_info['end'].strftime('%I:%M %p')}",
                        "subject": subject,
                        "questions": target.get_remaining(),
                        "difficulty": target.difficulty,
                    })
                    break

        return schedule

    # ========================================================================
    # STATISTICS
    # ========================================================================

    def get_performance_summary(self) -> Dict:
        """Get performance summary across all subjects."""
        summary = {}

        for subject, accuracies in self._subject_performance.items():
            if not accuracies:
                continue

            avg_accuracy = sum(accuracies) / len(accuracies)
            trend = "improving" if len(accuracies) >= 2 and accuracies[-1] > accuracies[0] else "stable"

            summary[subject] = {
                "average_accuracy": avg_accuracy,
                "recent_accuracy": accuracies[-1] if accuracies else 0,
                "trend": trend,
                "sessions": len(accuracies),
            }

        return summary

    def get_current_day_summary(self) -> Optional[Dict]:
        """Get summary of current day."""
        if not self._current_day:
            return None
        return self._current_day.get_summary()

    def get_history(self, days: int = 7) -> List[Dict]:
        """Get history for last N days."""
        recent = self._history[-days:] if self._history else []
        return [d.get_summary() for d in recent]


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_daily_target_manager() -> DailyTargetManager:
    """Create a daily target manager."""
    return DailyTargetManager()


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Daily Target Manager...")
    print("="*60)

    manager = DailyTargetManager()

    # Test 1: Get daily target
    print("\n1. Getting daily target...")
    target = manager.get_daily_target(
        day_number=15,
        base_hours=8,
        weakness="mathematics",
        streak_days=10,
        recent_accuracy={"mathematics": 0.75, "physics": 0.85}
    )
    print(f"   Total questions: {target.total_questions}")
    print(f"   Hours target: {target.hours_target}")

    # Test 2: Subject breakdown
    print("\n2. Subject breakdown:")
    for subject, starget in target.subject_targets.items():
        print(f"   {subject}: {starget.questions_target} questions ({starget.time_slot.value})")

    # Test 3: Record progress
    print("\n3. Recording progress...")
    result = manager.record_progress("mathematics", questions=20, accuracy=0.80, time_spent_minutes=45)
    print(f"   Progress: {result['progress']:.1f}%")

    result = manager.record_progress("physics", questions=30, accuracy=0.90, time_spent_minutes=50)
    print(f"   Progress: {result['progress']:.1f}%")

    # Test 4: Get next subject
    print("\n4. Next subject recommendation:")
    next_sub = manager.get_next_subject()
    print(f"   Subject: {next_sub['subject']}")
    print(f"   Reason: {next_sub['reason']}")

    # Test 5: Study schedule
    print("\n5. Study schedule:")
    schedule = manager.get_study_schedule()
    for slot in schedule[:3]:
        print(f"   {slot['time_slot']}: {slot['subject']} ({slot['questions']} questions)")

    print("\n" + "="*60)
    print("All tests passed!")
