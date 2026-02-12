"""
JARVIS Behaviour Data Collector
================================

Purpose: Collect and aggregate behaviour data from BehaviourMonitor
         for pattern detection analysis.

This module:
- Interfaces with BehaviourMonitor for real-time data
- Aggregates data for pattern analysis
- Provides BehaviourData objects for PatternDetector
- Maintains historical data for trend analysis

EXAM IMPACT:
    HIGH. Pattern detection requires quality data.
    Without proper data collection, patterns cannot be detected.
    This module bridges the gap between monitoring and analysis.

REASON FOR DESIGN:
    - Decouples monitoring from analysis
    - Provides clean data interface
    - Maintains data history
    - Efficient data aggregation

ROLLBACK PLAN:
    - Data collector is read-only
    - No system modifications
    - Can be disabled without affecting monitoring
"""

import json
import math
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from pathlib import Path

# Import pattern detector types
from .pattern_detector import (
    BehaviourData,
    PatternType,
    PatternSeverity,
)


# ============================================================================
# CONSTANTS
# ============================================================================

# Data storage paths
DATA_DIR = Path("/sdcard/jarvis_data")
BEHAVIOUR_DATA_FILE = DATA_DIR / "behaviour_history.json"
SESSION_DATA_FILE = DATA_DIR / "session_history.json"

# Data retention
MAX_HISTORY_DAYS = 90  # Keep 90 days of data (exam prep duration)
MAX_EVENTS_IN_MEMORY = 10000  # Limit in-memory events

# Aggregation windows
HOURLY_AGGREGATION = True
DAILY_AGGREGATION = True


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class SessionRecord:
    """A study session record."""
    session_id: str
    started_at: datetime
    ended_at: Optional[datetime]
    duration_minutes: int
    subject: str
    topic: str
    questions_answered: int
    correct_answers: int
    accuracy: float
    theta_before: float
    theta_after: float
    theta_change: float

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_minutes": self.duration_minutes,
            "subject": self.subject,
            "topic": self.topic,
            "questions_answered": self.questions_answered,
            "correct_answers": self.correct_answers,
            "accuracy": self.accuracy,
            "theta_before": self.theta_before,
            "theta_after": self.theta_after,
            "theta_change": self.theta_change,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'SessionRecord':
        return cls(
            session_id=data["session_id"],
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else datetime.now(),
            ended_at=datetime.fromisoformat(data["ended_at"]) if data.get("ended_at") else None,
            duration_minutes=data["duration_minutes"],
            subject=data["subject"],
            topic=data["topic"],
            questions_answered=data["questions_answered"],
            correct_answers=data["correct_answers"],
            accuracy=data["accuracy"],
            theta_before=data["theta_before"],
            theta_after=data["theta_after"],
            theta_change=data["theta_change"],
        )


@dataclass
class DailySummary:
    """Daily behaviour summary."""
    date: datetime
    total_study_minutes: int
    total_distraction_events: int
    total_distraction_seconds: int
    sessions_completed: int
    questions_answered: int
    overall_accuracy: float
    avg_session_duration: float
    streak_days: int
    late_night_activity: bool
    weak_topics_practiced: List[str]
    weak_topics_avoided: List[str]

    def to_dict(self) -> Dict:
        return {
            "date": self.date.isoformat() if self.date else None,
            "total_study_minutes": self.total_study_minutes,
            "total_distraction_events": self.total_distraction_events,
            "total_distraction_seconds": self.total_distraction_seconds,
            "sessions_completed": self.sessions_completed,
            "questions_answered": self.questions_answered,
            "overall_accuracy": self.overall_accuracy,
            "avg_session_duration": self.avg_session_duration,
            "streak_days": self.streak_days,
            "late_night_activity": self.late_night_activity,
            "weak_topics_practiced": self.weak_topics_practiced,
            "weak_topics_avoided": self.weak_topics_avoided,
        }


# ============================================================================
# BEHAVIOUR DATA COLLECTOR CLASS
# ============================================================================

class BehaviourDataCollector:
    """
    Collects and aggregates behaviour data for pattern detection.

    This class:
    - Maintains history of behaviour events
    - Aggregates data for analysis
    - Provides BehaviourData for PatternDetector
    - Persists data to disk

    Usage:
        collector = BehaviourDataCollector()

        # Record session
        collector.record_session(session_record)

        # Record distraction
        collector.record_distraction(app_name, duration_seconds)

        # Get data for analysis
        behaviour_data = collector.get_behaviour_data()

        # Analyze patterns
        patterns = detector.analyze(behaviour_data)

    EXAM IMPACT:
        Pattern detection quality depends on data quality.
        This module ensures PatternDetector has the data it needs.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize data collector.

        Args:
            data_dir: Directory to store data (default: /sdcard/jarvis_data)

        Reason:
            Configurable data directory for testing flexibility.
        """
        self.data_dir = data_dir or DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # In-memory storage
        self._sessions: List[SessionRecord] = []
        self._distraction_events: List[Dict] = []
        self._app_switches: List[datetime] = []
        self._late_night_activity: List[datetime] = []
        self._topic_practice: Dict[str, List[datetime]] = defaultdict(list)
        self._topic_theta: Dict[str, float] = {}

        # Streak tracking
        self._current_streak: int = 0
        self._longest_streak: int = 0
        self._last_study_date: Optional[datetime] = None
        self._missed_days: List[datetime] = []

        # Load existing data
        self._load_data()

    # ========================================================================
    # DATA RECORDING
    # ========================================================================

    def record_session(self, session: SessionRecord) -> None:
        """
        Record a study session.

        Args:
            session: SessionRecord with session data

        Reason:
            Sessions are primary indicator of study behaviour.
            Used for burnout detection, inconsistency detection.
        """
        self._sessions.append(session)
        self._update_streak(session.started_at)

        # Update topic practice
        if session.topic:
            self._topic_practice[session.topic].append(session.started_at)

        # Update topic theta
        if session.topic and session.theta_after != 0:
            self._topic_theta[session.topic] = session.theta_after

        # Trim if too many sessions
        if len(self._sessions) > MAX_EVENTS_IN_MEMORY:
            self._sessions = self._sessions[-MAX_EVENTS_IN_MEMORY:]

        self._save_data()

    def record_distraction(
        self,
        app_name: str,
        duration_seconds: int,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Record a distraction event.

        Args:
            app_name: Name of distracting app
            duration_seconds: How long user was distracted
            timestamp: When it happened (default: now)

        Reason:
            Distraction events are used for:
            - Study avoidance detection
            - Distraction escalation detection
            - Late night dopamine detection
        """
        event = {
            "app_name": app_name,
            "duration_seconds": duration_seconds,
            "timestamp": (timestamp or datetime.now()).isoformat(),
        }
        self._distraction_events.append(event)

        # Check for late night
        ts = timestamp or datetime.now()
        if ts.hour >= 23 or ts.hour < 6:
            self._late_night_activity.append(ts)

        # Trim if too many events
        if len(self._distraction_events) > MAX_EVENTS_IN_MEMORY:
            self._distraction_events = self._distraction_events[-MAX_EVENTS_IN_MEMORY:]

        self._save_data()

    def record_app_switch(self, timestamp: Optional[datetime] = None) -> None:
        """
        Record an app switch event.

        Args:
            timestamp: When the switch happened (default: now)

        Reason:
            Rapid app switching indicates study avoidance.
            Used by PatternDetector for avoidance detection.
        """
        self._app_switches.append(timestamp or datetime.now())

        # Trim
        if len(self._app_switches) > MAX_EVENTS_IN_MEMORY:
            self._app_switches = self._app_switches[-MAX_EVENTS_IN_MEMORY:]

    def record_topic_theta(self, topic: str, theta: float) -> None:
        """
        Record topic ability (theta) score.

        Args:
            topic: Topic identifier
            theta: IRT theta score

        Reason:
            Weak topics are identified by low theta.
            Used for weakness avoidance detection.
        """
        self._topic_theta[topic] = theta

    def record_sleep_time(self, sleep_time: datetime) -> None:
        """
        Record sleep time.

        Args:
            sleep_time: When user went to sleep

        Reason:
            Sleep patterns affect learning.
            Irregular sleep indicates potential issues.
        """
        # Store in session metadata
        pass  # TODO: Implement with sleep tracking

    # ========================================================================
    # DATA RETRIEVAL
    # ========================================================================

    def get_behaviour_data(
        self,
        days: int = 14
    ) -> BehaviourData:
        """
        Get aggregated behaviour data for pattern analysis.

        Args:
            days: Number of days to include (default: 14)

        Returns:
            BehaviourData object ready for PatternDetector

        Reason:
            Main interface for pattern detection.
            Provides all data needed for analysis.
        """
        cutoff = datetime.now() - timedelta(days=days)

        # Filter recent sessions
        recent_sessions = [
            s for s in self._sessions
            if s.started_at > cutoff
        ]

        # Filter recent distractions
        recent_distractions = [
            e for e in self._distraction_events
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]

        # Filter recent switches
        recent_switches = [
            s for s in self._app_switches
            if s > cutoff
        ]

        # Filter recent late night activity
        recent_late_nights = [
            t for t in self._late_night_activity
            if t > cutoff
        ]

        # Build BehaviourData
        data = BehaviourData()

        # Session data
        data.session_durations = [s.duration_minutes for s in recent_sessions]
        data.session_dates = [s.started_at for s in recent_sessions]
        data.questions_answered = [s.questions_answered for s in recent_sessions]
        data.accuracy_rates = [s.accuracy for s in recent_sessions]

        # App usage
        data.app_switches = recent_switches
        data.distraction_events = [
            datetime.fromisoformat(e["timestamp"])
            for e in recent_distractions
        ]
        data.distracting_app_usage = self._aggregate_app_usage(recent_distractions)

        # Topic data
        data.topic_theta = dict(self._topic_theta)
        data.topics_practiced = list(self._topic_practice.keys())
        data.topic_dates = {
            k: [t for t in v if t > cutoff]
            for k, v in self._topic_practice.items()
        }

        # Late night activity
        data.late_night_activity = recent_late_nights

        # Streak data
        data.current_streak = self._current_streak
        data.longest_streak = self._longest_streak
        data.missed_days = self._missed_days

        return data

    def get_daily_summaries(self, days: int = 14) -> List[DailySummary]:
        """
        Get daily summaries for trend analysis.

        Args:
            days: Number of days to include

        Returns:
            List of DailySummary objects

        Reason:
            Daily summaries provide quick overview.
            Useful for dashboard display and trend analysis.
        """
        summaries = []
        cutoff = datetime.now() - timedelta(days=days)

        for i in range(days):
            day = (datetime.now() - timedelta(days=days-i-1)).date()
            day_start = datetime.combine(day, time.min)
            day_end = datetime.combine(day, time.max)

            # Filter sessions for this day
            day_sessions = [
                s for s in self._sessions
                if day_start <= s.started_at <= day_end
            ]

            # Filter distractions for this day
            day_distractions = [
                e for e in self._distraction_events
                if day_start <= datetime.fromisoformat(e["timestamp"]) <= day_end
            ]

            # Calculate metrics
            total_study = sum(s.duration_minutes for s in day_sessions)
            total_distraction_time = sum(
                e["duration_seconds"] for e in day_distractions
            )

            # Check for late night activity
            late_night = any(
                day_start <= t <= day_end
                for t in self._late_night_activity
            )

            # Find weak topics practiced/avoided
            weak_threshold = -0.5
            weak_topics = [
                t for t, theta in self._topic_theta.items()
                if theta < weak_threshold
            ]
            practiced_weak = []
            avoided_weak = []

            for topic in weak_topics:
                practices = [
                    t for t in self._topic_practice.get(topic, [])
                    if day_start <= t <= day_end
                ]
                if practices:
                    practiced_weak.append(topic)
                else:
                    avoided_weak.append(topic)

            summary = DailySummary(
                date=day_start,
                total_study_minutes=total_study,
                total_distraction_events=len(day_distractions),
                total_distraction_seconds=total_distraction_time,
                sessions_completed=len(day_sessions),
                questions_answered=sum(s.questions_answered for s in day_sessions),
                overall_accuracy=(
                    sum(s.accuracy for s in day_sessions) / len(day_sessions)
                    if day_sessions else 0
                ),
                avg_session_duration=(
                    total_study / len(day_sessions) if day_sessions else 0
                ),
                streak_days=self._current_streak,
                late_night_activity=late_night,
                weak_topics_practiced=practiced_weak,
                weak_topics_avoided=avoided_weak,
            )
            summaries.append(summary)

        return summaries

    def get_trend_analysis(self) -> Dict[str, Any]:
        """
        Analyze trends in behaviour data.

        Returns:
            Dictionary with trend analysis

        Reason:
            Trends provide early warning indicators.
            Helps identify if behaviour is improving or deteriorating.
        """
        # Get last 7 days vs previous 7 days
        last_7 = self.get_daily_summaries(7)
        previous_7 = self.get_daily_summaries(14)[:7]

        if not last_7 or not previous_7:
            return {"status": "insufficient_data"}

        # Calculate averages
        last_7_study = sum(s.total_study_minutes for s in last_7) / 7
        previous_7_study = sum(s.total_study_minutes for s in previous_7) / 7

        last_7_distraction = sum(s.total_distraction_events for s in last_7) / 7
        previous_7_distraction = sum(s.total_distraction_events for s in previous_7) / 7

        last_7_accuracy = sum(s.overall_accuracy for s in last_7 if s.overall_accuracy > 0) / max(1, sum(1 for s in last_7 if s.overall_accuracy > 0))
        previous_7_accuracy = sum(s.overall_accuracy for s in previous_7 if s.overall_accuracy > 0) / max(1, sum(1 for s in previous_7 if s.overall_accuracy > 0))

        # Calculate trends
        study_trend = "improving" if last_7_study > previous_7_study * 1.1 else (
            "declining" if last_7_study < previous_7_study * 0.9 else "stable"
        )
        distraction_trend = "improving" if last_7_distraction < previous_7_distraction * 0.9 else (
            "declining" if last_7_distraction > previous_7_distraction * 1.1 else "stable"
        )
        accuracy_trend = "improving" if last_7_accuracy > previous_7_accuracy * 1.05 else (
            "declining" if last_7_accuracy < previous_7_accuracy * 0.95 else "stable"
        )

        return {
            "study_time_trend": study_trend,
            "study_time_change_pct": (
                (last_7_study - previous_7_study) / previous_7_study * 100
                if previous_7_study > 0 else 0
            ),
            "distraction_trend": distraction_trend,
            "distraction_change_pct": (
                (last_7_distraction - previous_7_distraction) / previous_7_distraction * 100
                if previous_7_distraction > 0 else 0
            ),
            "accuracy_trend": accuracy_trend,
            "accuracy_change_pct": (
                (last_7_accuracy - previous_7_accuracy) / previous_7_accuracy * 100
                if previous_7_accuracy > 0 else 0
            ),
            "current_streak": self._current_streak,
            "longest_streak": self._longest_streak,
            "late_night_incidents_7d": len([
                t for t in self._late_night_activity
                if t > datetime.now() - timedelta(days=7)
            ]),
        }

    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================

    def _aggregate_app_usage(
        self,
        distractions: List[Dict]
    ) -> Dict[str, int]:
        """Aggregate distraction time by app."""
        usage = defaultdict(int)
        for event in distractions:
            usage[event["app_name"]] += event["duration_seconds"]
        return dict(usage)

    def _update_streak(self, session_date: datetime) -> None:
        """Update streak tracking."""
        session_day = session_date.date()
        today = datetime.now().date()

        if self._last_study_date is None:
            self._current_streak = 1
        else:
            last_day = self._last_study_date.date()
            if session_day == last_day:
                pass  # Same day, no change
            elif session_day == last_day + timedelta(days=1):
                self._current_streak += 1
            else:
                # Streak broken
                self._missed_days.append(session_date)
                self._current_streak = 1

        self._last_study_date = session_date
        self._longest_streak = max(self._longest_streak, self._current_streak)

    def _save_data(self) -> None:
        """Save data to disk."""
        try:
            data = {
                "sessions": [s.to_dict() for s in self._sessions],
                "distraction_events": self._distraction_events,
                "app_switches": [s.isoformat() for s in self._app_switches],
                "late_night_activity": [t.isoformat() for t in self._late_night_activity],
                "topic_practice": {
                    k: [t.isoformat() for t in v]
                    for k, v in self._topic_practice.items()
                },
                "topic_theta": self._topic_theta,
                "current_streak": self._current_streak,
                "longest_streak": self._longest_streak,
                "last_study_date": self._last_study_date.isoformat() if self._last_study_date else None,
                "missed_days": [d.isoformat() for d in self._missed_days],
            }

            with open(BEHAVIOUR_DATA_FILE, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Warning: Could not save behaviour data: {e}")

    def _load_data(self) -> None:
        """Load data from disk."""
        try:
            if not BEHAVIOUR_DATA_FILE.exists():
                return

            with open(BEHAVIOUR_DATA_FILE, 'r') as f:
                data = json.load(f)

            # Load sessions
            self._sessions = [
                SessionRecord.from_dict(s)
                for s in data.get("sessions", [])
            ]

            # Load distraction events
            self._distraction_events = data.get("distraction_events", [])

            # Load app switches
            self._app_switches = [
                datetime.fromisoformat(s)
                for s in data.get("app_switches", [])
            ]

            # Load late night activity
            self._late_night_activity = [
                datetime.fromisoformat(t)
                for t in data.get("late_night_activity", [])
            ]

            # Load topic practice
            self._topic_practice = defaultdict(list)
            for topic, times in data.get("topic_practice", {}).items():
                self._topic_practice[topic] = [
                    datetime.fromisoformat(t) for t in times
                ]

            # Load topic theta
            self._topic_theta = data.get("topic_theta", {})

            # Load streak data
            self._current_streak = data.get("current_streak", 0)
            self._longest_streak = data.get("longest_streak", 0)
            self._last_study_date = (
                datetime.fromisoformat(data["last_study_date"])
                if data.get("last_study_date") else None
            )
            self._missed_days = [
                datetime.fromisoformat(d)
                for d in data.get("missed_days", [])
            ]

        except Exception as e:
            print(f"Warning: Could not load behaviour data: {e}")

    def clear_old_data(self, days: int = MAX_HISTORY_DAYS) -> int:
        """
        Clear data older than specified days.

        Args:
            days: Number of days to keep

        Returns:
            Number of records cleared

        Reason:
            Prevent unlimited data growth.
            Keep only relevant history.
        """
        cutoff = datetime.now() - timedelta(days=days)
        cleared = 0

        # Clear old sessions
        old_count = len(self._sessions)
        self._sessions = [s for s in self._sessions if s.started_at > cutoff]
        cleared += old_count - len(self._sessions)

        # Clear old distractions
        old_count = len(self._distraction_events)
        self._distraction_events = [
            e for e in self._distraction_events
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]
        cleared += old_count - len(self._distraction_events)

        # Clear old switches
        old_count = len(self._app_switches)
        self._app_switches = [s for s in self._app_switches if s > cutoff]
        cleared += old_count - len(self._app_switches)

        # Clear old late night activity
        old_count = len(self._late_night_activity)
        self._late_night_activity = [t for t in self._late_night_activity if t > cutoff]
        cleared += old_count - len(self._late_night_activity)

        self._save_data()
        return cleared


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Behaviour Data Collector...")
    print()

    # Create collector with temp directory
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        collector = BehaviourDataCollector(Path(tmpdir))

        # Record some test sessions
        for i in range(5):
            session = SessionRecord(
                session_id=f"test_{i}",
                started_at=datetime.now() - timedelta(days=i),
                ended_at=datetime.now() - timedelta(days=i, hours=-1),
                duration_minutes=60 - i * 5,
                subject="Mathematics",
                topic=f"maths_topic_{i % 2}",
                questions_answered=20,
                correct_answers=15 + i,
                accuracy=0.75 + i * 0.02,
                theta_before=0.0,
                theta_after=0.1 * i,
                theta_change=0.1 * i,
            )
            collector.record_session(session)

        # Record some distractions
        for i in range(3):
            collector.record_distraction(
                "instagram",
                300 + i * 60,
                datetime.now() - timedelta(hours=i)
            )

        # Get behaviour data
        data = collector.get_behaviour_data(days=7)
        print(f"BehaviourData:")
        print(f"  Sessions: {len(data.session_durations)}")
        print(f"  Distractions: {len(data.distraction_events)}")
        print(f"  Current streak: {data.current_streak}")

        # Get daily summaries
        summaries = collector.get_daily_summaries(7)
        print(f"\nDaily summaries: {len(summaries)}")

        # Get trend analysis
        trends = collector.get_trend_analysis()
        print(f"\nTrend Analysis:")
        for key, value in trends.items():
            print(f"  {key}: {value}")

    print("\nAll tests passed!")
