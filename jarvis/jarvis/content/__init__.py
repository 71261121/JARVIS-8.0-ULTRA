"""
JARVIS Content Module
=====================

Purpose: 75-day study content and planning.

Components:
- Study Plan Generator: Complete 75-day plan
- Daily Target Manager: Daily question targets with rotation
- Mock Test System: Full mock test simulation
- Milestone Tracker: Progress checkpoints

EXAM IMPACT:
    CRITICAL. This is the CORE preparation strategy.
    Structured 75-day plan ensures COMPLETE syllabus coverage.
    Every day has clear objectives and targets.

75-DAY BREAKDOWN:
    Days 1-15:   Foundation Rush (10th basics)
    Days 16-35:  Core Building (11th syllabus)
    Days 36-55:  Advanced Topics (12th syllabus)
    Days 56-70:  Intensive Practice + Mocks
    Days 71-75:  Final Revision

SUBJECT ALLOCATION:
    Mathematics: 40% more time (weakness, highest weightage)
    Physics: Standard allocation
    Chemistry: Standard allocation
    English: 20% less (strength, lower weightage)

ROLLBACK PLAN:
    - Plans can be regenerated
    - Targets can be manually adjusted
    - Progress is tracked separately
"""

from .study_plan import (
    StudyPlanGenerator,
    StudyPlan,
    DailyPlan,
    WeeklySummary,
    StudyPhase,
    Subject,
    DayType,
    PHASE_RANGES,
    SUBJECT_WEIGHTAGE,
    create_study_plan,
    get_day_info,
)

from .daily_target import (
    DailyTargetManager,
    DailyTarget,
    SubjectTarget,
    TimeSlot,
    TargetStatus,
    create_daily_target_manager,
)

from .mock_test import (
    MockTestSystem,
    MockTestResult,
    SubjectResult,
    QuestionResult,
    MockType,
    MockStatus,
    EXAM_STRUCTURE,
    TARGET_SCORES,
    create_mock_test_system,
)

from .milestone_tracker import (
    MilestoneTracker,
    Milestone,
    MilestoneStatus,
    MilestoneType,
    DEFAULT_MILESTONES,
    create_milestone_tracker,
)


__all__ = [
    # Study Plan
    "StudyPlanGenerator",
    "StudyPlan",
    "DailyPlan",
    "WeeklySummary",
    "StudyPhase",
    "Subject",
    "DayType",
    "PHASE_RANGES",
    "SUBJECT_WEIGHTAGE",
    "create_study_plan",
    "get_day_info",

    # Daily Target
    "DailyTargetManager",
    "DailyTarget",
    "SubjectTarget",
    "TimeSlot",
    "TargetStatus",
    "create_daily_target_manager",

    # Mock Test
    "MockTestSystem",
    "MockTestResult",
    "SubjectResult",
    "QuestionResult",
    "MockType",
    "MockStatus",
    "EXAM_STRUCTURE",
    "TARGET_SCORES",
    "create_mock_test_system",

    # Milestone Tracker
    "MilestoneTracker",
    "Milestone",
    "MilestoneStatus",
    "MilestoneType",
    "DEFAULT_MILESTONES",
    "create_milestone_tracker",
]
