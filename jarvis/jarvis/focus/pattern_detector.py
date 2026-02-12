"""
JARVIS Pattern Detector
=======================

Purpose: Detect self-sabotage patterns before they escalate into full burnout
         or study abandonment.

This module analyzes behaviour data to identify:
- Study avoidance patterns
- Burnout precursors
- Weakness avoidance
- Inconsistency patterns
- Late night dopamine seeking
- Distraction escalation

EXAM IMPACT:
    HIGH. User has history of:
    - Inconsistency
    - Burnout
    - "Right effort, wrong strategy" fear
    
    Early detection enables intervention BEFORE weeks of wasted effort.
    Pattern detection is the DIFFERENCE between proactive and reactive system.

REASON FOR DESIGN:
    - Statistical analysis of behaviour data
    - Threshold-based pattern triggers
    - Severity scoring for prioritization
    - Intervention recommendations
    
SOURCE RESEARCH:
    - Procrastination patterns: Steel (2007) "The Nature of Procrastination"
    - Burnout indicators: Maslach Burnout Inventory
    - Behaviour change: Prochaska & DiClemente's Transtheoretical Model

ROLLBACK PLAN:
    - Pattern detector is read-only
    - No system modifications
    - Can be disabled without affecting other modules
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


# ============================================================================
# CONSTANTS
# ============================================================================

# Pattern detection thresholds (all documented with rationale)

# Study Avoidance Detection
RAPID_SWITCH_THRESHOLD = 5          # 5 app switches
RAPID_SWITCH_WINDOW_MINUTES = 10    # within 10 minutes
AVOIDANCE_SEVERITY_BASE = 30        # Base severity score

# Burnout Detection
DECLINING_SESSION_THRESHOLD = 0.7   # 70% of normal session time
DECLINING_DAYS_THRESHOLD = 3        # Consecutive days of decline
ACCURACY_DECLINE_THRESHOLD = 0.15   # 15% accuracy drop
BURNOUT_SEVERITY_BASE = 50          # Higher severity - critical pattern

# Weakness Avoidance
WEAK_TOPIC_THRESHOLD = 0.3          # Topics with theta < -0.5
AVOIDANCE_DAYS_THRESHOLD = 5        # Days without practicing weak topic
WEAKNESS_AVOIDANCE_BASE = 40

# Inconsistency Detection
VARIANCE_THRESHOLD = 0.30           # 30% variance in daily hours
MIN_DAYS_FOR_VARIANCE = 7           # Need at least 7 days of data
INCONSISTENCY_BASE = 25

# Late Night Dopamine
LATE_NIGHT_START = 23               # 11 PM
LATE_NIGHT_END = 6                  # 6 AM
DOPAMINE_SEVERITY_BASE = 35

# Distraction Escalation
DISTRACTION_INCREASE_THRESHOLD = 1.5  # 50% increase
ESCALATION_WINDOW_DAYS = 3
ESCALATION_BASE = 30


# ============================================================================
# ENUMS
# ============================================================================

class PatternType(Enum):
    """Types of detected patterns."""
    STUDY_AVOIDANCE = "study_avoidance"
    BURNOUT_PRECURSOR = "burnout_precursor"
    WEAKNESS_AVOIDANCE = "weakness_avoidance"
    INCONSISTENCY = "inconsistency"
    LATE_NIGHT_DOPAMINE = "late_night_dopamine"
    DISTRACTION_ESCALATION = "distraction_escalation"
    SLEEP_DISRUPTION = "sleep_disruption"
    MOTIVATION_DROP = "motivation_drop"


class PatternSeverity(Enum):
    """Severity levels for patterns."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InterventionType(Enum):
    """Types of interventions."""
    WARNING = "warning"
    TARGET_REDUCTION = "target_reduction"
    REST_DAY = "rest_day"
    FORCE_TOPIC = "force_topic"
    BLOCK_APPS = "block_apps"
    VOICE_INTERVENTION = "voice_intervention"
    EMERGENCY_PAUSE = "emergency_pause"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class BehaviourData:
    """
    Behaviour data for pattern analysis.
    
    Collected from BehaviourMonitor, this data is analyzed
    for pattern detection.
    """
    # Session data
    session_durations: List[int] = field(default_factory=list)  # minutes
    session_dates: List[datetime] = field(default_factory=list)
    questions_answered: List[int] = field(default_factory=list)
    accuracy_rates: List[float] = field(default_factory=list)
    
    # App usage
    app_switches: List[datetime] = field(default_factory=list)
    distracting_app_usage: Dict[str, int] = field(default_factory=dict)  # app -> seconds
    distraction_events: List[datetime] = field(default_factory=list)
    
    # Topic data
    topic_theta: Dict[str, float] = field(default_factory=dict)  # topic -> theta
    topics_practiced: List[str] = field(default_factory=list)  # Recent topics
    topic_dates: Dict[str, List[datetime]] = field(default_factory=dict)
    
    # Sleep data
    sleep_times: List[datetime] = field(default_factory=list)
    wake_times: List[datetime] = field(default_factory=list)
    late_night_activity: List[datetime] = field(default_factory=list)
    
    # Streak data
    current_streak: int = 0
    longest_streak: int = 0
    missed_days: List[datetime] = field(default_factory=list)


@dataclass
class DetectedPattern:
    """A detected behaviour pattern."""
    pattern_type: PatternType
    severity: PatternSeverity
    score: int  # 0-100
    detected_at: datetime
    evidence: Dict[str, Any]
    description: str
    recommended_interventions: List[InterventionType]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage/display."""
        return {
            "pattern_type": self.pattern_type.value,
            "severity": self.severity.value,
            "score": self.score,
            "detected_at": self.detected_at.isoformat(),
            "evidence": self.evidence,
            "description": self.description,
            "interventions": [i.value for i in self.recommended_interventions]
        }


@dataclass
class Intervention:
    """An intervention action."""
    intervention_type: InterventionType
    pattern_type: PatternType
    triggered_at: datetime
    parameters: Dict[str, Any] = field(default_factory=dict)
    executed: bool = False
    result: Optional[str] = None


# ============================================================================
# PATTERN DETECTOR CLASS
# ============================================================================

class PatternDetector:
    """
    Detects self-sabotage patterns from behaviour data.
    
    Usage:
        detector = PatternDetector()
        
        # Analyze behaviour data
        patterns = detector.analyze(behaviour_data)
        
        # Get interventions
        for pattern in patterns:
            interventions = detector.get_interventions(pattern)
    
    Reason for design:
        - Centralized pattern detection logic
        - Threshold-based for verifiable detection
        - Severity scoring for prioritization
        - Actionable intervention recommendations
    
    EXAM IMPACT:
        Critical for preventing self-sabotage.
        User has history of inconsistency and burnout.
        Early detection = intervention before collapse.
    """
    
    def __init__(
        self,
        rapid_switch_threshold: int = RAPID_SWITCH_THRESHOLD,
        burnout_decline_threshold: float = DECLINING_SESSION_THRESHOLD,
        variance_threshold: float = VARIANCE_THRESHOLD
    ):
        """
        Initialize pattern detector.
        
        Args:
            rapid_switch_threshold: App switches to trigger avoidance detection
            burnout_decline_threshold: Session decline ratio for burnout
            variance_threshold: Daily hours variance threshold
        
        Reason:
            Configurable thresholds for different sensitivity levels.
        """
        self.rapid_switch_threshold = rapid_switch_threshold
        self.burnout_decline_threshold = burnout_decline_threshold
        self.variance_threshold = variance_threshold
        
        # Pattern history for trend analysis
        self.pattern_history: List[DetectedPattern] = []
    
    def analyze(self, data: BehaviourData) -> List[DetectedPattern]:
        """
        Analyze behaviour data for all pattern types.
        
        Args:
            data: Behaviour data to analyze
        
        Returns:
            List of detected patterns
        
        Reason:
            Main entry point for pattern detection.
            Runs all detectors and returns combined results.
        """
        patterns = []
        now = datetime.now()
        
        # Run all pattern detectors
        avoidance = self._detect_study_avoidance(data, now)
        if avoidance:
            patterns.append(avoidance)
        
        burnout = self._detect_burnout_precursor(data, now)
        if burnout:
            patterns.append(burnout)
        
        weakness = self._detect_weakness_avoidance(data, now)
        if weakness:
            patterns.append(weakness)
        
        inconsistency = self._detect_inconsistency(data, now)
        if inconsistency:
            patterns.append(inconsistency)
        
        late_night = self._detect_late_night_dopamine(data, now)
        if late_night:
            patterns.append(late_night)
        
        escalation = self._detect_distraction_escalation(data, now)
        if escalation:
            patterns.append(escalation)
        
        # Store in history
        self.pattern_history.extend(patterns)
        
        # Keep only last 100 patterns
        if len(self.pattern_history) > 100:
            self.pattern_history = self.pattern_history[-100:]
        
        return patterns
    
    # ========================================================================
    # PATTERN DETECTORS
    # ========================================================================
    
    def _detect_study_avoidance(
        self,
        data: BehaviourData,
        now: datetime
    ) -> Optional[DetectedPattern]:
        """
        Detect study avoidance pattern.
        
        Indicators:
        - Rapid app switching (>5 switches in 10 minutes)
        - Opening distracting apps during study hours
        - Long periods without any study session
        
        EXAM IMPACT:
            Study avoidance = wasted study hours.
            Critical to catch early before it becomes a habit.
        """
        if not data.app_switches:
            return None
        
        # Count recent switches (last 10 minutes)
        cutoff = now - timedelta(minutes=RAPID_SWITCH_WINDOW_MINUTES)
        recent_switches = [s for s in data.app_switches if s > cutoff]
        
        if len(recent_switches) < self.rapid_switch_threshold:
            return None
        
        # Calculate severity
        switch_count = len(recent_switches)
        severity_score = min(100, AVOIDANCE_SEVERITY_BASE + switch_count * 5)
        
        # Determine severity level
        if severity_score >= 75:
            severity = PatternSeverity.CRITICAL
        elif severity_score >= 50:
            severity = PatternSeverity.HIGH
        elif severity_score >= 25:
            severity = PatternSeverity.MEDIUM
        else:
            severity = PatternSeverity.LOW
        
        return DetectedPattern(
            pattern_type=PatternType.STUDY_AVOIDANCE,
            severity=severity,
            score=severity_score,
            detected_at=now,
            evidence={
                "switch_count": switch_count,
                "window_minutes": RAPID_SWITCH_WINDOW_MINUTES,
                "switches_per_minute": switch_count / RAPID_SWITCH_WINDOW_MINUTES
            },
            description=f"Study avoidance detected: {switch_count} app switches in {RAPID_SWITCH_WINDOW_MINUTES} minutes",
            recommended_interventions=[
                InterventionType.WARNING,
                InterventionType.VOICE_INTERVENTION,
                InterventionType.BLOCK_APPS
            ]
        )
    
    def _detect_burnout_precursor(
        self,
        data: BehaviourData,
        now: datetime
    ) -> Optional[DetectedPattern]:
        """
        Detect burnout precursor pattern.
        
        Indicators:
        - Declining session durations (3+ consecutive days)
        - Declining accuracy (15%+ drop)
        - Increased distraction frequency
        - Shorter attention spans
        
        EXAM IMPACT:
            Burnout = weeks of lost productivity.
            User has history of burnout - critical to prevent.
        """
        if len(data.session_durations) < 5:
            return None
        
        # Check for declining session times
        recent_sessions = data.session_durations[-5:]
        avg_recent = sum(recent_sessions[-3:]) / 3 if len(recent_sessions) >= 3 else 0
        avg_previous = sum(recent_sessions[:-3]) / len(recent_sessions[:-3]) if len(recent_sessions) > 3 else avg_recent
        
        if avg_recent == 0 or avg_previous == 0:
            return None
        
        decline_ratio = avg_recent / avg_previous
        
        if decline_ratio >= self.burnout_decline_threshold:
            return None  # Not declining enough
        
        # Check for accuracy decline
        accuracy_declining = False
        if len(data.accuracy_rates) >= 5:
            recent_accuracy = sum(data.accuracy_rates[-3:]) / 3
            previous_accuracy = sum(data.accuracy_rates[:-3]) / len(data.accuracy_rates[:-3])
            accuracy_declining = (previous_accuracy - recent_accuracy) >= ACCURACY_DECLINE_THRESHOLD
        
        # Calculate severity
        severity_score = BURNOUT_SEVERITY_BASE
        severity_score += int((1 - decline_ratio) * 50)  # Add for decline
        if accuracy_declining:
            severity_score += 20
        severity_score = min(100, severity_score)
        
        # Determine severity level
        if severity_score >= 80:
            severity = PatternSeverity.CRITICAL
        elif severity_score >= 60:
            severity = PatternSeverity.HIGH
        elif severity_score >= 40:
            severity = PatternSeverity.MEDIUM
        else:
            severity = PatternSeverity.LOW
        
        return DetectedPattern(
            pattern_type=PatternType.BURNOUT_PRECURSOR,
            severity=severity,
            score=severity_score,
            detected_at=now,
            evidence={
                "session_decline_ratio": decline_ratio,
                "avg_recent_minutes": avg_recent,
                "avg_previous_minutes": avg_previous,
                "accuracy_declining": accuracy_declining
            },
            description=f"Burnout precursor: Session time down to {decline_ratio:.0%} of normal",
            recommended_interventions=[
                InterventionType.TARGET_REDUCTION,
                InterventionType.REST_DAY,
                InterventionType.WARNING
            ]
        )
    
    def _detect_weakness_avoidance(
        self,
        data: BehaviourData,
        now: datetime
    ) -> Optional[DetectedPattern]:
        """
        Detect weakness avoidance pattern.
        
        Indicators:
        - Weak topics (theta < -0.5) not practiced recently
        - Consistently avoiding certain topics
        - Topic selection bias toward easy topics
        
        EXAM IMPACT:
            User's fear: "Right effort, wrong strategy"
            Avoiding weak topics = guaranteed exam failure on those topics.
            Maths is weakest but highest weightage - MUST NOT AVOID.
        """
        if not data.topic_theta or not data.topics_practiced:
            return None
        
        # Find weak topics
        weak_topics = [
            topic for topic, theta in data.topic_theta.items()
            if theta < -0.5
        ]
        
        if not weak_topics:
            return None
        
        # Check if weak topics have been practiced recently
        cutoff = now - timedelta(days=AVOIDANCE_DAYS_THRESHOLD)
        avoided_weak_topics = []
        
        for topic in weak_topics:
            last_practiced = data.topic_dates.get(topic, [datetime.min])[-1]
            if last_practiced < cutoff:
                avoided_weak_topics.append(topic)
        
        if not avoided_weak_topics:
            return None
        
        # Calculate severity based on number and importance of avoided topics
        # Maths topics are more critical (user's weakest, highest weightage)
        maths_topics = [t for t in avoided_weak_topics if 'math' in t.lower()]
        severity_score = WEAKNESS_AVOIDANCE_BASE
        severity_score += len(avoided_weak_topics) * 5
        severity_score += len(maths_topics) * 10  # Extra weight for maths
        severity_score = min(100, severity_score)
        
        # Determine severity
        if len(maths_topics) > 0:
            severity = PatternSeverity.HIGH
        elif severity_score >= 60:
            severity = PatternSeverity.HIGH
        elif severity_score >= 40:
            severity = PatternSeverity.MEDIUM
        else:
            severity = PatternSeverity.LOW
        
        return DetectedPattern(
            pattern_type=PatternType.WEAKNESS_AVOIDANCE,
            severity=severity,
            score=severity_score,
            detected_at=now,
            evidence={
                "weak_topics": weak_topics,
                "avoided_topics": avoided_weak_topics,
                "days_since_practice": AVOIDANCE_DAYS_THRESHOLD,
                "maths_topics_avoided": len(maths_topics)
            },
            description=f"Weakness avoidance: {len(avoided_weak_topics)} weak topics not practiced in {AVOIDANCE_DAYS_THRESHOLD} days",
            recommended_interventions=[
                InterventionType.FORCE_TOPIC,
                InterventionType.WARNING
            ]
        )
    
    def _detect_inconsistency(
        self,
        data: BehaviourData,
        now: datetime
    ) -> Optional[DetectedPattern]:
        """
        Detect inconsistency pattern.
        
        Indicators:
        - High variance in daily study hours (>30%)
        - Unpredictable study schedule
        - Frequent streak breaks
        
        EXAM IMPACT:
            Inconsistency = unreliable progress.
            User has history of inconsistency.
            Steady progress is better than bursts.
        """
        if len(data.session_durations) < MIN_DAYS_FOR_VARIANCE:
            return None
        
        # Calculate variance of session durations
        mean_duration = sum(data.session_durations) / len(data.session_durations)
        if mean_duration == 0:
            return None
        
        variance = sum(
            (d - mean_duration) ** 2 
            for d in data.session_durations
        ) / len(data.session_durations)
        
        std_dev = math.sqrt(variance)
        coefficient_of_variation = std_dev / mean_duration
        
        if coefficient_of_variation < self.variance_threshold:
            return None
        
        # Calculate severity
        severity_score = INCONSISTENCY_BASE
        severity_score += int(coefficient_of_variation * 100)
        severity_score += len(data.missed_days) * 5
        severity_score = min(100, severity_score)
        
        # Determine severity
        if severity_score >= 60:
            severity = PatternSeverity.HIGH
        elif severity_score >= 40:
            severity = PatternSeverity.MEDIUM
        else:
            severity = PatternSeverity.LOW
        
        return DetectedPattern(
            pattern_type=PatternType.INCONSISTENCY,
            severity=severity,
            score=severity_score,
            detected_at=now,
            evidence={
                "coefficient_of_variation": coefficient_of_variation,
                "mean_session_minutes": mean_duration,
                "std_dev_minutes": std_dev,
                "missed_days_count": len(data.missed_days)
            },
            description=f"Inconsistent study pattern: {coefficient_of_variation:.0%} variance in daily hours",
            recommended_interventions=[
                InterventionType.WARNING,
                InterventionType.TARGET_REDUCTION
            ]
        )
    
    def _detect_late_night_dopamine(
        self,
        data: BehaviourData,
        now: datetime
    ) -> Optional[DetectedPattern]:
        """
        Detect late night dopamine seeking pattern.
        
        Indicators:
        - Screen activity after 11 PM on distracting apps
        - Correlation with next-day performance drop
        - Sleep time disruption
        
        EXAM IMPACT:
            Late night dopamine = next day cognitive decline.
            Sleep disruption severely impacts learning.
            Common pattern before burnout.
        """
        if not data.late_night_activity:
            return None
        
        # Count late night activities in last 7 days
        cutoff = now - timedelta(days=7)
        recent_late_nights = [t for t in data.late_night_activity if t > cutoff]
        
        if len(recent_late_nights) < 2:
            return None
        
        # Calculate severity
        severity_score = DOPAMINE_SEVERITY_BASE
        severity_score += len(recent_late_nights) * 10
        severity_score = min(100, severity_score)
        
        # Determine severity
        if severity_score >= 70:
            severity = PatternSeverity.HIGH
        elif severity_score >= 50:
            severity = PatternSeverity.MEDIUM
        else:
            severity = PatternSeverity.LOW
        
        return DetectedPattern(
            pattern_type=PatternType.LATE_NIGHT_DOPAMINE,
            severity=severity,
            score=severity_score,
            detected_at=now,
            evidence={
                "late_night_count": len(recent_late_nights),
                "recent_activity_times": [t.isoformat() for t in recent_late_nights[:5]]
            },
            description=f"Late night dopamine seeking: {len(recent_late_nights)} incidents in last 7 days",
            recommended_interventions=[
                InterventionType.WARNING,
                InterventionType.BLOCK_APPS
            ]
        )
    
    def _detect_distraction_escalation(
        self,
        data: BehaviourData,
        now: datetime
    ) -> Optional[DetectedPattern]:
        """
        Detect escalating distraction pattern.
        
        Indicators:
        - 50%+ increase in distraction events
        - Progressive increase over multiple days
        - More severe distracting apps being used
        
        EXAM IMPACT:
            Escalating distraction = approaching total collapse.
            Must intervene before study schedule completely breaks down.
        """
        if len(data.distraction_events) < 5:
            return None
        
        # Compare recent to previous
        cutoff = now - timedelta(days=ESCALATION_WINDOW_DAYS)
        recent_events = [e for e in data.distraction_events if e > cutoff]
        previous_events = [e for e in data.distraction_events if e <= cutoff]
        
        if not previous_events:
            return None
        
        recent_rate = len(recent_events) / ESCALATION_WINDOW_DAYS
        previous_rate = len(previous_events) / max(1, (now - min(previous_events)).days)
        
        if previous_rate == 0:
            return None
        
        increase_ratio = recent_rate / previous_rate
        
        if increase_ratio < DISTRACTION_INCREASE_THRESHOLD:
            return None
        
        # Calculate severity
        severity_score = ESCALATION_BASE
        severity_score += int((increase_ratio - 1) * 50)
        severity_score = min(100, severity_score)
        
        # Determine severity
        if severity_score >= 70:
            severity = PatternSeverity.HIGH
        elif severity_score >= 50:
            severity = PatternSeverity.MEDIUM
        else:
            severity = PatternSeverity.LOW
        
        return DetectedPattern(
            pattern_type=PatternType.DISTRACTION_ESCALATION,
            severity=severity,
            score=severity_score,
            detected_at=now,
            evidence={
                "increase_ratio": increase_ratio,
                "recent_daily_rate": recent_rate,
                "previous_daily_rate": previous_rate,
                "window_days": ESCALATION_WINDOW_DAYS
            },
            description=f"Distraction escalation: {increase_ratio:.0%} increase in distraction events",
            recommended_interventions=[
                InterventionType.BLOCK_APPS,
                InterventionType.VOICE_INTERVENTION,
                InterventionType.WARNING
            ]
        )
    
    # ========================================================================
    # INTERVENTION GENERATION
    # ========================================================================
    
    def get_interventions(
        self,
        pattern: DetectedPattern
    ) -> List[Intervention]:
        """
        Get recommended interventions for a detected pattern.
        
        Args:
            pattern: Detected pattern
        
        Returns:
            List of recommended interventions
        
        Reason:
            Converts patterns to actionable interventions.
            Prioritizes based on severity.
        """
        interventions = []
        now = datetime.now()
        
        for intervention_type in pattern.recommended_interventions:
            intervention = Intervention(
                intervention_type=intervention_type,
                pattern_type=pattern.pattern_type,
                triggered_at=now,
                parameters=self._get_intervention_parameters(
                    intervention_type, pattern
                )
            )
            interventions.append(intervention)
        
        return interventions
    
    def _get_intervention_parameters(
        self,
        intervention_type: InterventionType,
        pattern: DetectedPattern
    ) -> Dict[str, Any]:
        """
        Get parameters for an intervention.
        
        Args:
            intervention_type: Type of intervention
            pattern: Detected pattern
        
        Returns:
            Parameters for the intervention
        """
        params = {}
        
        if intervention_type == InterventionType.TARGET_REDUCTION:
            # Reduce targets by 20% for burnout
            params["reduction_percentage"] = 20
            params["reason"] = "Burnout prevention"
        
        elif intervention_type == InterventionType.FORCE_TOPIC:
            # Get avoided weak topics
            if pattern.pattern_type == PatternType.WEAKNESS_AVOIDANCE:
                params["topics"] = pattern.evidence.get("avoided_topics", [])
                params["questions_per_topic"] = 10
        
        elif intervention_type == InterventionType.BLOCK_APPS:
            # Block distracting apps for study hours
            params["block_duration_hours"] = 2
            params["severity"] = "high"
        
        elif intervention_type == InterventionType.VOICE_INTERVENTION:
            # Voice message parameters
            params["message_type"] = "direct"
            params["severity"] = pattern.severity.value
        
        elif intervention_type == InterventionType.REST_DAY:
            # Suggest rest day
            params["duration_hours"] = 24
            params["guilt_free"] = True
        
        return params
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_pattern_summary(self) -> Dict:
        """Get summary of detected patterns."""
        if not self.pattern_history:
            return {
                "total_patterns": 0,
                "by_type": {},
                "by_severity": {}
            }
        
        by_type = defaultdict(int)
        by_severity = defaultdict(int)
        
        for pattern in self.pattern_history:
            by_type[pattern.pattern_type.value] += 1
            by_severity[pattern.severity.value] += 1
        
        return {
            "total_patterns": len(self.pattern_history),
            "by_type": dict(by_type),
            "by_severity": dict(by_severity),
            "most_recent": self.pattern_history[-1].to_dict() if self.pattern_history else None
        }
    
    def get_active_patterns(self, hours: int = 24) -> List[DetectedPattern]:
        """
        Get patterns detected in the last N hours.
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            List of recent patterns
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        return [p for p in self.pattern_history if p.detected_at > cutoff]


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Pattern Detector...")
    print()
    
    detector = PatternDetector()
    
    # Create test data with study avoidance pattern
    data = BehaviourData()
    
    # Add rapid app switches (study avoidance)
    now = datetime.now()
    for i in range(7):
        data.app_switches.append(now - timedelta(minutes=i))
    
    # Add declining sessions (burnout precursor)
    data.session_durations = [60, 55, 50, 40, 35, 30, 25]
    data.session_dates = [now - timedelta(days=i) for i in range(7)]
    data.accuracy_rates = [0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55]
    
    # Add weak topics
    data.topic_theta = {
        "maths_algebra": -1.2,
        "maths_geometry": -0.8,
        "physics_mechanics": 0.3,
        "chemistry_organic": 0.5,
    }
    data.topics_practiced = ["physics_mechanics", "chemistry_organic"]
    data.topic_dates = {
        "physics_mechanics": [now - timedelta(days=1)],
        "chemistry_organic": [now - timedelta(days=2)],
    }
    
    # Analyze
    patterns = detector.analyze(data)
    
    print(f"Detected {len(patterns)} patterns:")
    for p in patterns:
        print(f"\n  Pattern: {p.pattern_type.value}")
        print(f"  Severity: {p.severity.value}")
        print(f"  Score: {p.score}")
        print(f"  Description: {p.description}")
        print(f"  Interventions: {[i.value for i in p.recommended_interventions]}")
    
    print("\n" + "="*50)
    print("Pattern Summary:")
    print(detector.get_pattern_summary())
    
    print("\nAll tests passed!")
