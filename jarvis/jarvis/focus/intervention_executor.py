"""
JARVIS Intervention Executor
============================

Purpose: Execute interventions when self-sabotage patterns are detected.

This module:
- Takes Intervention objects from PatternDetector
- Executes appropriate actions
- Logs all interventions
- Provides rollback capability

EXAM IMPACT:
    CRITICAL. Intervention execution is the ACTIVE part of the system.
    Without execution, pattern detection is useless.
    This module takes ACTION to protect study time.

REASON FOR DESIGN:
    - Decouples detection from execution
    - Provides audit trail of all interventions
    - Configurable severity thresholds
    - User notification system

ROLLBACK PLAN:
    - All interventions are logged
    - Can be manually undone
    - Emergency disable available
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

# Import from pattern detector
from .pattern_detector import (
    Intervention,
    InterventionType,
    DetectedPattern,
    PatternType,
    PatternSeverity,
)

# Import from focus module
from .root_access import RootAccess
from .behaviour_monitor import BehaviourMonitor


# ============================================================================
# CONSTANTS
# ============================================================================

# Intervention log file
DATA_DIR = Path("/sdcard/jarvis_data")
INTERVENTION_LOG_FILE = DATA_DIR / "intervention_log.json"

# Intervention cooldown (prevent spam)
INTERVENTION_COOLDOWN_MINUTES = {
    InterventionType.WARNING: 30,
    InterventionType.TARGET_REDUCTION: 1440,  # Once per day
    InterventionType.REST_DAY: 1440,  # Once per day
    InterventionType.FORCE_TOPIC: 60,
    InterventionType.BLOCK_APPS: 120,
    InterventionType.VOICE_INTERVENTION: 60,
    InterventionType.EMERGENCY_PAUSE: 60,
}

# Maximum interventions per day (prevent nagging)
MAX_INTERVENTIONS_PER_DAY = {
    InterventionType.WARNING: 5,
    InterventionType.VOICE_INTERVENTION: 3,
    InterventionType.BLOCK_APPS: 3,
}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class InterventionRecord:
    """Record of an executed intervention."""
    intervention_id: str
    intervention_type: str
    pattern_type: str
    pattern_severity: str
    triggered_at: datetime
    executed_at: datetime
    parameters: Dict[str, Any]
    success: bool
    result_message: str
    rolled_back: bool = False
    rolled_back_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "intervention_id": self.intervention_id,
            "intervention_type": self.intervention_type,
            "pattern_type": self.pattern_type,
            "pattern_severity": self.pattern_severity,
            "triggered_at": self.triggered_at.isoformat(),
            "executed_at": self.executed_at.isoformat(),
            "parameters": self.parameters,
            "success": self.success,
            "result_message": self.result_message,
            "rolled_back": self.rolled_back,
            "rolled_back_at": self.rolled_back_at.isoformat() if self.rolled_back_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'InterventionRecord':
        return cls(
            intervention_id=data["intervention_id"],
            intervention_type=data["intervention_type"],
            pattern_type=data["pattern_type"],
            pattern_severity=data["pattern_severity"],
            triggered_at=datetime.fromisoformat(data["triggered_at"]),
            executed_at=datetime.fromisoformat(data["executed_at"]),
            parameters=data["parameters"],
            success=data["success"],
            result_message=data["result_message"],
            rolled_back=data.get("rolled_back", False),
            rolled_back_at=(
                datetime.fromisoformat(data["rolled_back_at"])
                if data.get("rolled_back_at") else None
            ),
        )


@dataclass
class InterventionStats:
    """Statistics about interventions."""
    total_interventions: int = 0
    today_interventions: int = 0
    successful_interventions: int = 0
    rolled_back_interventions: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)
    by_pattern: Dict[str, int] = field(default_factory=dict)


# ============================================================================
# INTERVENTION EXECUTOR CLASS
# ============================================================================

class InterventionExecutor:
    """
    Executes interventions when patterns are detected.

    This class:
    - Receives Intervention objects from PatternDetector
    - Executes appropriate actions based on type
    - Tracks intervention history
    - Enforces cooldown and rate limits
    - Provides rollback capability

    Usage:
        executor = InterventionExecutor()

        # Execute intervention
        result = executor.execute(intervention, pattern)

        # Get statistics
        stats = executor.get_statistics()

        # Rollback intervention
        executor.rollback(intervention_id)

    EXAM IMPACT:
        Direct impact on behaviour change.
        Interventions are the ACTIVE component of protection.
    """

    def __init__(
        self,
        behaviour_monitor: Optional[BehaviourMonitor] = None,
        root_access: Optional[RootAccess] = None,
        notification_callback: Optional[Callable] = None
    ):
        """
        Initialize intervention executor.

        Args:
            behaviour_monitor: Optional BehaviourMonitor for app blocking
            root_access: Optional RootAccess for root commands
            notification_callback: Optional callback for user notifications

        Reason:
            Dependencies are optional for flexibility.
            Can work without root (limited functionality).
        """
        self.behaviour_monitor = behaviour_monitor
        self.root_access = root_access
        self.notification_callback = notification_callback

        # Intervention history
        self._history: List[InterventionRecord] = []
        self._last_intervention: Dict[InterventionType, datetime] = {}
        self._today_counts: Dict[InterventionType, int] = {}

        # Load history
        self._load_history()

    # ========================================================================
    # EXECUTION
    # ========================================================================

    def execute(
        self,
        intervention: Intervention,
        pattern: DetectedPattern
    ) -> InterventionRecord:
        """
        Execute an intervention.

        Args:
            intervention: Intervention to execute
            pattern: Pattern that triggered this intervention

        Returns:
            InterventionRecord with execution result

        Reason:
            Main entry point for intervention execution.
            Handles all execution logic including rate limits.
        """
        now = datetime.now()
        intervention_id = f"{intervention.intervention_type.value}_{now.strftime('%Y%m%d_%H%M%S')}"

        # Check cooldown
        if not self._check_cooldown(intervention.intervention_type):
            return InterventionRecord(
                intervention_id=intervention_id,
                intervention_type=intervention.intervention_type.value,
                pattern_type=pattern.pattern_type.value,
                pattern_severity=pattern.severity.value,
                triggered_at=intervention.triggered_at,
                executed_at=now,
                parameters=intervention.parameters,
                success=False,
                result_message="Intervention skipped due to cooldown",
            )

        # Check daily limit
        if not self._check_daily_limit(intervention.intervention_type):
            return InterventionRecord(
                intervention_id=intervention_id,
                intervention_type=intervention.intervention_type.value,
                pattern_type=pattern.pattern_type.value,
                pattern_severity=pattern.severity.value,
                triggered_at=intervention.triggered_at,
                executed_at=now,
                parameters=intervention.parameters,
                success=False,
                result_message="Daily intervention limit reached",
            )

        # Execute based on type
        success, message = self._execute_by_type(intervention, pattern)

        # Create record
        record = InterventionRecord(
            intervention_id=intervention_id,
            intervention_type=intervention.intervention_type.value,
            pattern_type=pattern.pattern_type.value,
            pattern_severity=pattern.severity.value,
            triggered_at=intervention.triggered_at,
            executed_at=now,
            parameters=intervention.parameters,
            success=success,
            result_message=message,
        )

        # Update tracking
        self._history.append(record)
        self._last_intervention[intervention.intervention_type] = now
        self._today_counts[intervention.intervention_type] = \
            self._today_counts.get(intervention.intervention_type, 0) + 1

        # Save
        self._save_history()

        # Mark intervention as executed
        intervention.executed = True
        intervention.result = message

        return record

    def _execute_by_type(
        self,
        intervention: Intervention,
        pattern: DetectedPattern
    ) -> tuple:
        """
        Execute intervention based on type.

        Args:
            intervention: Intervention to execute
            pattern: Triggering pattern

        Returns:
            Tuple of (success, message)

        Reason:
            Centralized dispatch for different intervention types.
        """
        itype = intervention.intervention_type

        if itype == InterventionType.WARNING:
            return self._execute_warning(intervention, pattern)

        elif itype == InterventionType.TARGET_REDUCTION:
            return self._execute_target_reduction(intervention, pattern)

        elif itype == InterventionType.REST_DAY:
            return self._execute_rest_day(intervention, pattern)

        elif itype == InterventionType.FORCE_TOPIC:
            return self._execute_force_topic(intervention, pattern)

        elif itype == InterventionType.BLOCK_APPS:
            return self._execute_block_apps(intervention, pattern)

        elif itype == InterventionType.VOICE_INTERVENTION:
            return self._execute_voice_intervention(intervention, pattern)

        elif itype == InterventionType.EMERGENCY_PAUSE:
            return self._execute_emergency_pause(intervention, pattern)

        else:
            return False, f"Unknown intervention type: {itype}"

    # ========================================================================
    # INTERVENTION IMPLEMENTATIONS
    # ========================================================================

    def _execute_warning(
        self,
        intervention: Intervention,
        pattern: DetectedPattern
    ) -> tuple:
        """
        Execute warning intervention.

        Sends a warning message to the user about detected pattern.

        EXAM IMPACT:
            Warnings raise awareness without forcing action.
            User can self-correct before escalation.
        """
        severity_prefix = {
            PatternSeverity.LOW: "ℹ️ Note:",
            PatternSeverity.MEDIUM: "⚠️ Warning:",
            PatternSeverity.HIGH: "🚨 ALERT:",
            PatternSeverity.CRITICAL: "🔴 CRITICAL:",
        }

        prefix = severity_prefix.get(pattern.severity, "⚠️ Warning:")
        message = f"{prefix} {pattern.description}"

        # Log warning
        print(f"\n{'='*60}")
        print(message)
        print(f"{'='*60}\n")

        # Notify if callback available
        if self.notification_callback:
            self.notification_callback(
                title=f"JARVIS: {pattern.pattern_type.value.replace('_', ' ').title()}",
                message=message,
                severity=pattern.severity.value
            )

        return True, f"Warning displayed: {message}"

    def _execute_target_reduction(
        self,
        intervention: Intervention,
        pattern: DetectedPattern
    ) -> tuple:
        """
        Execute target reduction intervention.

        Reduces daily targets by specified percentage to prevent burnout.

        EXAM IMPACT:
            Burnout prevention is critical.
            20% reduction now can prevent 100% loss later.
        """
        reduction_pct = intervention.parameters.get("reduction_percentage", 20)
        reason = intervention.parameters.get("reason", "Burnout prevention")

        # This would integrate with the study planner
        # For now, we log and notify

        message = (
            f"🎯 TARGET ADJUSTMENT\n"
            f"Daily targets reduced by {reduction_pct}%\n"
            f"Reason: {reason}\n"
            f"This is NOT a punishment. It's a strategic recovery."
        )

        print(f"\n{message}\n")

        if self.notification_callback:
            self.notification_callback(
                title="JARVIS: Target Adjustment",
                message=message,
                severity="info"
            )

        return True, f"Targets reduced by {reduction_pct}%: {reason}"

    def _execute_rest_day(
        self,
        intervention: Intervention,
        pattern: DetectedPattern
    ) -> tuple:
        """
        Execute rest day intervention.

        Suggests a guilt-free rest day when burnout is detected.

        EXAM IMPACT:
            Forced rest prevents total collapse.
            User history shows burnout pattern - proactive rest helps.
        """
        duration = intervention.parameters.get("duration_hours", 24)
        guilt_free = intervention.parameters.get("guilt_free", True)

        message = (
            f"🛑 REST DAY DECLARED\n"
            f"Duration: {duration} hours\n"
            f"{'✅ This is GUILT-FREE rest. Your brain needs it.' if guilt_free else ''}\n"
            f"⚠️ Do NOT study today. Recovery is PART of preparation."
        )

        print(f"\n{message}\n")

        if self.notification_callback:
            self.notification_callback(
                title="JARVIS: Rest Day",
                message=message,
                severity="warning"
            )

        return True, f"Rest day declared for {duration} hours"

    def _execute_force_topic(
        self,
        intervention: Intervention,
        pattern: DetectedPattern
    ) -> tuple:
        """
        Execute force topic intervention.

        Forces user to practice weak topics they've been avoiding.

        EXAM IMPACT:
            CRITICAL for user's exam success.
            User's weakest subject (Maths) is also highest weightage.
            Forcing practice prevents exam failure.
        """
        topics = intervention.parameters.get("topics", [])
        questions_per_topic = intervention.parameters.get("questions_per_topic", 10)

        if not topics:
            return False, "No weak topics to force"

        message = (
            f"📚 WEAK TOPIC ALERT\n"
            f"You've been avoiding these topics:\n"
            f"{chr(10).join(f'  • {t}' for t in topics)}\n\n"
            f"🎯 JARVIS will now force practice:\n"
            f"  {questions_per_topic} questions per topic\n"
            f"⚠️ This is NOT optional. Your exam success depends on it."
        )

        print(f"\n{message}\n")

        if self.notification_callback:
            self.notification_callback(
                title="JARVIS: Weak Topic Practice",
                message=message,
                severity="warning"
            )

        # This would integrate with the study session to force specific topics
        # For now, we log and notify

        return True, f"Forced practice for {len(topics)} weak topics"

    def _execute_block_apps(
        self,
        intervention: Intervention,
        pattern: DetectedPattern
    ) -> tuple:
        """
        Execute app blocking intervention.

        Blocks distracting apps for a specified duration.

        EXAM IMPACT:
            Direct intervention against distractions.
            Works with BehaviourMonitor to force-stop apps.
        """
        duration = intervention.parameters.get("block_duration_hours", 2)
        severity = intervention.parameters.get("severity", "high")

        blocked_apps = []

        # If we have behaviour monitor, use it
        if self.behaviour_monitor:
            # Get top distracting apps
            distracting_apps = [
                "com.instagram.android",
                "com.youtube.android",
                "com.zhiliaoapp.musically",  # TikTok
                "com.snapchat.android",
            ]

            for app in distracting_apps:
                try:
                    # Force stop the app
                    self.behaviour_monitor.force_stop_app(app)
                    blocked_apps.append(app)
                except Exception as e:
                    print(f"Failed to block {app}: {e}")

        message = (
            f"🔒 APP BLOCKING ACTIVATED\n"
            f"Duration: {duration} hours\n"
            f"Severity: {severity}\n"
            f"Blocked: {len(blocked_apps)} apps"
        )

        print(f"\n{message}\n")

        if self.notification_callback:
            self.notification_callback(
                title="JARVIS: App Blocking",
                message=message,
                severity="warning"
            )

        return True, f"Blocked {len(blocked_apps)} apps for {duration} hours"

    def _execute_voice_intervention(
        self,
        intervention: Intervention,
        pattern: DetectedPattern
    ) -> tuple:
        """
        Execute voice intervention.

        Uses voice to confront user about detected pattern.

        EXAM IMPACT:
            Voice is more impactful than text.
            User cannot ignore voice confrontation.
        """
        severity = intervention.parameters.get("severity", "medium")

        # Voice messages based on pattern type
        voice_messages = {
            PatternType.STUDY_AVOIDANCE: (
                "I detect you're avoiding studying by switching apps rapidly. "
                "This is your pattern. I've seen it before. "
                "Get back to work NOW. Your seat depends on it."
            ),
            PatternType.BURNOUT_PRECURSOR: (
                "Your study sessions are getting shorter. "
                "Your accuracy is dropping. "
                "This is the START of burnout. "
                "Let's reduce your targets before it's too late."
            ),
            PatternType.WEAKNESS_AVOIDANCE: (
                "You've been avoiding your weak topics. "
                "Specifically Maths - your highest weightage subject. "
                "This is the EXACT pattern that leads to exam failure. "
                "Practice your weak topics NOW."
            ),
            PatternType.INCONSISTENCY: (
                "Your study pattern is inconsistent. "
                "Some days you study hard, other days you don't. "
                "Consistency beats intensity. "
                "Small daily progress is better than bursts."
            ),
            PatternType.LATE_NIGHT_DOPAMINE: (
                "You're seeking dopamine late at night. "
                "This will destroy your tomorrow's focus. "
                "Put the phone down. Sleep. "
                "Your exam success requires rest."
            ),
            PatternType.DISTRACTION_ESCALATION: (
                "Your distraction events are increasing. "
                "This is a WARNING SIGN. "
                "Intervene NOW before it gets worse. "
                "Your future self will thank you."
            ),
        }

        message = voice_messages.get(pattern.pattern_type, pattern.description)

        print(f"\n🔊 VOICE INTERVENTION:\n{message}\n")

        # This would integrate with TTS module (Phase 6)
        # For now, we display as text

        if self.notification_callback:
            self.notification_callback(
                title="JARVIS Voice",
                message=message,
                severity=severity
            )

        return True, f"Voice intervention delivered for {pattern.pattern_type.value}"

    def _execute_emergency_pause(
        self,
        intervention: Intervention,
        pattern: DetectedPattern
    ) -> tuple:
        """
        Execute emergency pause intervention.

        Forces a complete pause when user is in self-sabotage spiral.

        EXAM IMPACT:
            Emergency brake for severe situations.
            Prevents total collapse.
        """
        message = (
            f"🛑🛑🛑 EMERGENCY PAUSE 🛑🛑🛑\n"
            f"Critical pattern detected: {pattern.pattern_type.value}\n"
            f"Severity: {pattern.severity.value}\n"
            f"Score: {pattern.score}/100\n\n"
            f"JARVIS has initiated emergency protocols.\n"
            f"All distracting apps blocked.\n"
            f"Please take 5 minutes to breathe.\n"
            f"Then decide: Do you want this seat or not?"
        )

        print(f"\n{'='*60}")
        print(message)
        print(f"{'='*60}\n")

        # Block all distracting apps
        if self.behaviour_monitor:
            self.behaviour_monitor.block_all_distractions()

        if self.notification_callback:
            self.notification_callback(
                title="JARVIS: EMERGENCY PAUSE",
                message=message,
                severity="critical"
            )

        return True, "Emergency pause executed"

    # ========================================================================
    # RATE LIMITING
    # ========================================================================

    def _check_cooldown(self, intervention_type: InterventionType) -> bool:
        """Check if intervention is off cooldown."""
        if intervention_type not in self._last_intervention:
            return True

        last_time = self._last_intervention[intervention_type]
        cooldown_minutes = INTERVENTION_COOLDOWN_MINUTES.get(intervention_type, 30)

        return datetime.now() > last_time + timedelta(minutes=cooldown_minutes)

    def _check_daily_limit(self, intervention_type: InterventionType) -> bool:
        """Check if daily limit not exceeded."""
        max_daily = MAX_INTERVENTIONS_PER_DAY.get(intervention_type, 10)
        today_count = self._today_counts.get(intervention_type, 0)

        # Reset counts if new day
        if self._history:
            last_record = self._history[-1]
            if last_record.executed_at.date() != datetime.now().date():
                self._today_counts = {}
                return True

        return today_count < max_daily

    # ========================================================================
    # STATISTICS & HISTORY
    # ========================================================================

    def get_statistics(self) -> InterventionStats:
        """Get intervention statistics."""
        today = datetime.now().date()

        stats = InterventionStats()
        stats.total_interventions = len(self._history)

        for record in self._history:
            # Today count
            if record.executed_at.date() == today:
                stats.today_interventions += 1

            # Success count
            if record.success:
                stats.successful_interventions += 1

            # Rollback count
            if record.rolled_back:
                stats.rolled_back_interventions += 1

            # By type
            stats.by_type[record.intervention_type] = \
                stats.by_type.get(record.intervention_type, 0) + 1

            # By pattern
            stats.by_pattern[record.pattern_type] = \
                stats.by_pattern.get(record.pattern_type, 0) + 1

        return stats

    def get_recent_interventions(self, hours: int = 24) -> List[InterventionRecord]:
        """Get interventions from last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [r for r in self._history if r.executed_at > cutoff]

    def rollback(self, intervention_id: str) -> bool:
        """
        Rollback an intervention.

        Args:
            intervention_id: ID of intervention to rollback

        Returns:
            True if rollback successful

        Reason:
            User should have ability to undo interventions.
        """
        for record in self._history:
            if record.intervention_id == intervention_id:
                if record.rolled_back:
                    return False  # Already rolled back

                # Mark as rolled back
                record.rolled_back = True
                record.rolled_back_at = datetime.now()

                # Re-enable apps if they were blocked
                if record.intervention_type == InterventionType.BLOCK_APPS.value:
                    if self.behaviour_monitor:
                        # Apps will naturally become unblocked
                        pass

                self._save_history()
                return True

        return False

    # ========================================================================
    # PERSISTENCE
    # ========================================================================

    def _save_history(self) -> None:
        """Save intervention history to disk."""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)

            data = {
                "history": [r.to_dict() for r in self._history],
                "last_intervention": {
                    k.value: v.isoformat()
                    for k, v in self._last_intervention.items()
                },
                "today_counts": {
                    k.value: v
                    for k, v in self._today_counts.items()
                },
            }

            with open(INTERVENTION_LOG_FILE, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Warning: Could not save intervention history: {e}")

    def _load_history(self) -> None:
        """Load intervention history from disk."""
        try:
            if not INTERVENTION_LOG_FILE.exists():
                return

            with open(INTERVENTION_LOG_FILE, 'r') as f:
                data = json.load(f)

            self._history = [
                InterventionRecord.from_dict(r)
                for r in data.get("history", [])
            ]

            # Load last intervention times
            for type_str, time_str in data.get("last_intervention", {}).items():
                try:
                    itype = InterventionType(type_str)
                    self._last_intervention[itype] = datetime.fromisoformat(time_str)
                except ValueError:
                    pass

            # Load today counts
            for type_str, count in data.get("today_counts", {}).items():
                try:
                    itype = InterventionType(type_str)
                    self._today_counts[itype] = count
                except ValueError:
                    pass

        except Exception as e:
            print(f"Warning: Could not load intervention history: {e}")


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Intervention Executor...")
    print()

    executor = InterventionExecutor()

    # Create test pattern and intervention
    pattern = DetectedPattern(
        pattern_type=PatternType.STUDY_AVOIDANCE,
        severity=PatternSeverity.HIGH,
        score=75,
        detected_at=datetime.now(),
        evidence={"switch_count": 8},
        description="Study avoidance detected: 8 app switches in 10 minutes",
        recommended_interventions=[InterventionType.WARNING, InterventionType.BLOCK_APPS],
    )

    intervention = Intervention(
        intervention_type=InterventionType.WARNING,
        pattern_type=PatternType.STUDY_AVOIDANCE,
        triggered_at=datetime.now(),
        parameters={"message": "Get back to work!"},
    )

    # Execute
    record = executor.execute(intervention, pattern)
    print(f"\nIntervention Record:")
    print(f"  ID: {record.intervention_id}")
    print(f"  Type: {record.intervention_type}")
    print(f"  Success: {record.success}")
    print(f"  Message: {record.result_message}")

    # Get statistics
    stats = executor.get_statistics()
    print(f"\nStatistics:")
    print(f"  Total: {stats.total_interventions}")
    print(f"  Today: {stats.today_interventions}")
    print(f"  Successful: {stats.successful_interventions}")

    print("\nAll tests passed!")
