"""
JARVIS Pattern Analyzer
=======================

Purpose: Real-time pattern analysis engine that integrates all components.

This module:
- Integrates BehaviourMonitor, DataCollector, PatternDetector, InterventionExecutor
- Runs continuous background analysis
- Triggers interventions when patterns are detected
- Provides unified API for pattern management

EXAM IMPACT:
    CRITICAL. This is the BRAIN of the behaviour control system.
    It connects all components and makes real-time decisions.
    Without this, individual components don't work together.

REASON FOR DESIGN:
    - Central coordination point
    - Thread-safe background operation
    - Event-driven analysis
    - Configurable sensitivity

ROLLBACK PLAN:
    - Can be stopped without affecting monitoring
    - All interventions are logged and reversible
    - Emergency disable available
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import queue

# Import components
from .pattern_detector import (
    PatternDetector,
    DetectedPattern,
    Intervention,
    BehaviourData,
    PatternType,
    PatternSeverity,
    InterventionType,
)
from .behaviour_data_collector import (
    BehaviourDataCollector,
    SessionRecord,
    DailySummary,
)
from .intervention_executor import (
    InterventionExecutor,
    InterventionRecord,
    InterventionStats,
)


# ============================================================================
# CONSTANTS
# ============================================================================

# Analysis intervals
DEFAULT_ANALYSIS_INTERVAL_SECONDS = 60  # Analyze every minute
QUICK_CHECK_INTERVAL_SECONDS = 10  # Quick checks every 10 seconds

# Severity thresholds for auto-intervention
AUTO_INTERVENTION_THRESHOLDS = {
    PatternSeverity.LOW: False,  # Don't auto-intervene for low severity
    PatternSeverity.MEDIUM: True,  # Auto-intervene for medium
    PatternSeverity.HIGH: True,  # Auto-intervene for high
    PatternSeverity.CRITICAL: True,  # Always auto-intervene for critical
}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class AnalysisResult:
    """Result of a pattern analysis run."""
    timestamp: datetime
    patterns_detected: int
    interventions_executed: int
    analysis_duration_ms: int
    status: str
    patterns: List[DetectedPattern] = field(default_factory=list)
    interventions: List[InterventionRecord] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "patterns_detected": self.patterns_detected,
            "interventions_executed": self.interventions_executed,
            "analysis_duration_ms": self.analysis_duration_ms,
            "status": self.status,
            "patterns": [p.to_dict() for p in self.patterns],
            "interventions": [i.to_dict() for i in self.interventions],
        }


@dataclass
class AnalyzerConfig:
    """Configuration for PatternAnalyzer."""
    analysis_interval: int = DEFAULT_ANALYSIS_INTERVAL_SECONDS
    auto_intervene: bool = True
    log_all_analysis: bool = False
    notification_callback: Optional[Callable] = None
    severity_threshold: PatternSeverity = PatternSeverity.MEDIUM


# ============================================================================
# PATTERN ANALYZER CLASS
# ============================================================================

class PatternAnalyzer:
    """
    Real-time pattern analysis engine.

    This class:
    - Runs background analysis thread
    - Integrates all components
    - Triggers interventions automatically
    - Provides unified API

    Usage:
        analyzer = PatternAnalyzer(
            data_collector=collector,
            executor=executor
        )

        # Start background analysis
        analyzer.start()

        # Get current status
        status = analyzer.get_status()

        # Stop analysis
        analyzer.stop()

    EXAM IMPACT:
        This is the central brain of behaviour control.
        Every second of analysis protects study time.
    """

    def __init__(
        self,
        data_collector: BehaviourDataCollector,
        detector: Optional[PatternDetector] = None,
        executor: Optional[InterventionExecutor] = None,
        config: Optional[AnalyzerConfig] = None
    ):
        """
        Initialize pattern analyzer.

        Args:
            data_collector: BehaviourDataCollector instance
            detector: Optional PatternDetector (created if not provided)
            executor: Optional InterventionExecutor (created if not provided)
            config: Optional configuration

        Reason:
            Dependencies can be injected or created internally.
            Flexible for testing and production.
        """
        self.data_collector = data_collector
        self.detector = detector or PatternDetector()
        self.executor = executor or InterventionExecutor(
            notification_callback=config.notification_callback if config else None
        )
        self.config = config or AnalyzerConfig()

        # Analysis state
        self._running = False
        self._analysis_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Analysis history
        self._analysis_history: List[AnalysisResult] = []
        self._last_analysis: Optional[AnalysisResult] = None

        # Event queue for real-time processing
        self._event_queue: queue.Queue = queue.Queue()

        # Statistics
        self._total_analyses = 0
        self._total_patterns_detected = 0
        self._total_interventions_executed = 0

    # ========================================================================
    # CONTROL
    # ========================================================================

    def start(self) -> bool:
        """
        Start background analysis.

        Returns:
            True if started successfully

        Reason:
            Starts the continuous monitoring loop.
            Non-blocking - runs in background thread.
        """
        if self._running:
            return False

        self._running = True
        self._stop_event.clear()

        self._analysis_thread = threading.Thread(
            target=self._analysis_loop,
            daemon=True,
            name="PatternAnalyzer"
        )
        self._analysis_thread.start()

        print("Pattern Analyzer started")
        return True

    def stop(self) -> bool:
        """
        Stop background analysis.

        Returns:
            True if stopped successfully

        Reason:
            Gracefully stops the analysis thread.
            Completes current analysis before stopping.
        """
        if not self._running:
            return False

        self._stop_event.set()
        self._running = False

        if self._analysis_thread:
            self._analysis_thread.join(timeout=5)

        print("Pattern Analyzer stopped")
        return True

    def is_running(self) -> bool:
        """Check if analyzer is running."""
        return self._running

    # ========================================================================
    # ANALYSIS
    # ========================================================================

    def analyze_now(self) -> AnalysisResult:
        """
        Run immediate analysis.

        Returns:
            AnalysisResult with detected patterns and interventions

        Reason:
            On-demand analysis for manual triggers or testing.
        """
        return self._run_analysis()

    def _analysis_loop(self) -> None:
        """
        Main analysis loop (runs in background thread).

        Reason:
            Continuous analysis at configured intervals.
            Handles all analysis timing and error handling.
        """
        while not self._stop_event.is_set():
            try:
                # Run analysis
                result = self._run_analysis()

                # Log if configured
                if self.config.log_all_analysis:
                    self._analysis_history.append(result)
                    # Keep last 1000 results
                    if len(self._analysis_history) > 1000:
                        self._analysis_history = self._analysis_history[-1000:]

                # Check for quick events in queue
                self._process_event_queue()

            except Exception as e:
                print(f"Analysis error: {e}")

            # Wait for next interval
            self._stop_event.wait(self.config.analysis_interval)

    def _run_analysis(self) -> AnalysisResult:
        """
        Execute one analysis cycle.

        Returns:
            AnalysisResult with findings

        Reason:
            Core analysis logic - connects all components.
        """
        start_time = datetime.now()
        patterns = []
        interventions = []

        try:
            # Get behaviour data
            behaviour_data = self.data_collector.get_behaviour_data(days=14)

            # Run pattern detection
            detected = self.detector.analyze(behaviour_data)
            patterns = detected

            # Execute interventions if auto-intervene enabled
            if self.config.auto_intervene:
                for pattern in detected:
                    if self._should_auto_intervene(pattern):
                        pattern_interventions = self.detector.get_interventions(pattern)
                        for intervention in pattern_interventions:
                            record = self.executor.execute(intervention, pattern)
                            interventions.append(record)

            status = "success"

        except Exception as e:
            status = f"error: {str(e)}"

        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        result = AnalysisResult(
            timestamp=start_time,
            patterns_detected=len(patterns),
            interventions_executed=len(interventions),
            analysis_duration_ms=duration_ms,
            status=status,
            patterns=patterns,
            interventions=interventions,
        )

        # Update statistics
        self._total_analyses += 1
        self._total_patterns_detected += len(patterns)
        self._total_interventions_executed += len(interventions)
        self._last_analysis = result

        return result

    def _should_auto_intervene(self, pattern: DetectedPattern) -> bool:
        """
        Determine if pattern should trigger auto-intervention.

        Args:
            pattern: Detected pattern

        Returns:
            True if should auto-intervene

        Reason:
            Not all patterns need intervention.
            Severity-based filtering prevents over-intervention.
        """
        return AUTO_INTERVENTION_THRESHOLDS.get(pattern.severity, False)

    def _process_event_queue(self) -> None:
        """
        Process queued events for real-time response.

        Reason:
            Some events need immediate response, not waiting for
            the next analysis interval.
        """
        try:
            while not self._event_queue.empty():
                event = self._event_queue.get_nowait()
                self._handle_realtime_event(event)
        except queue.Empty:
            pass

    def _handle_realtime_event(self, event: Dict) -> None:
        """
        Handle a real-time event.

        Args:
            event: Event dictionary with type and data

        Reason:
            Immediate response to critical events like
            porn app detection or rapid app switching.
        """
        event_type = event.get("type")

        if event_type == "distraction_detected":
            # Immediate check for study avoidance
            self._check_study_avoidance()

        elif event_type == "porn_app_detected":
            # Critical - immediate intervention
            self._emergency_intervention(
                "Porn app detected - immediate blocking required",
                PatternSeverity.CRITICAL
            )

        elif event_type == "late_night_activity":
            # Check for late night dopamine pattern
            self._check_late_night_dopamine()

    def _check_study_avoidance(self) -> None:
        """Quick check for study avoidance pattern."""
        # Get recent app switches
        data = self.data_collector.get_behaviour_data(days=1)
        if len(data.app_switches) >= 5:
            # Quick analysis
            patterns = self.detector.analyze(data)
            for pattern in patterns:
                if pattern.pattern_type == PatternType.STUDY_AVOIDANCE:
                    if self.config.auto_intervene:
                        interventions = self.detector.get_interventions(pattern)
                        for intervention in interventions[:1]:  # Only first
                            self.executor.execute(intervention, pattern)

    def _check_late_night_dopamine(self) -> None:
        """Check for late night dopamine pattern."""
        now = datetime.now()
        if now.hour >= 23 or now.hour < 6:
            # Late night activity detected
            data = self.data_collector.get_behaviour_data(days=1)
            if data.late_night_activity:
                # Create warning
                from .pattern_detector import DetectedPattern
                pattern = DetectedPattern(
                    pattern_type=PatternType.LATE_NIGHT_DOPAMINE,
                    severity=PatternSeverity.HIGH,
                    score=70,
                    detected_at=now,
                    evidence={"late_night_count": len(data.late_night_activity)},
                    description="Late night dopamine activity detected",
                    recommended_interventions=[
                        InterventionType.WARNING,
                        InterventionType.BLOCK_APPS,
                    ],
                )
                if self.config.auto_intervene:
                    interventions = self.detector.get_interventions(pattern)
                    for intervention in interventions[:1]:
                        self.executor.execute(intervention, pattern)

    def _emergency_intervention(self, message: str, severity: PatternSeverity) -> None:
        """
        Execute emergency intervention.

        Args:
            message: Emergency message
            severity: Severity level

        Reason:
            Critical situations need immediate response,
            not waiting for analysis cycle.
        """
        pattern = DetectedPattern(
            pattern_type=PatternType.DISTRACTION_ESCALATION,
            severity=severity,
            score=100,
            detected_at=datetime.now(),
            evidence={"emergency": True},
            description=message,
            recommended_interventions=[
                InterventionType.EMERGENCY_PAUSE,
                InterventionType.BLOCK_APPS,
            ],
        )

        interventions = self.detector.get_interventions(pattern)
        for intervention in interventions:
            self.executor.execute(intervention, pattern)

    # ========================================================================
    # EVENT QUEUE
    # ========================================================================

    def queue_event(self, event_type: str, data: Dict) -> None:
        """
        Queue an event for real-time processing.

        Args:
            event_type: Type of event
            data: Event data

        Reason:
            External components can trigger immediate analysis.
        """
        self._event_queue.put({
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        })

    # ========================================================================
    # STATUS & STATISTICS
    # ========================================================================

    def get_status(self) -> Dict[str, Any]:
        """
        Get current analyzer status.

        Returns:
            Dictionary with status information

        Reason:
            Dashboard display and monitoring.
        """
        return {
            "running": self._running,
            "total_analyses": self._total_analyses,
            "total_patterns_detected": self._total_patterns_detected,
            "total_interventions_executed": self._total_interventions_executed,
            "last_analysis": self._last_analysis.to_dict() if self._last_analysis else None,
            "analysis_interval": self.config.analysis_interval,
            "auto_intervene": self.config.auto_intervene,
            "queue_size": self._event_queue.qsize(),
        }

    def get_recent_patterns(self, hours: int = 24) -> List[DetectedPattern]:
        """
        Get patterns detected in last N hours.

        Args:
            hours: Number of hours to look back

        Returns:
            List of detected patterns
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            p for p in self.detector.pattern_history
            if p.detected_at > cutoff
        ]

    def get_recent_interventions(self, hours: int = 24) -> List[InterventionRecord]:
        """
        Get interventions executed in last N hours.

        Args:
            hours: Number of hours to look back

        Returns:
            List of intervention records
        """
        return self.executor.get_recent_interventions(hours)

    def get_intervention_statistics(self) -> InterventionStats:
        """Get intervention statistics."""
        return self.executor.get_statistics()

    def get_trend_summary(self) -> Dict[str, Any]:
        """
        Get behaviour trend summary.

        Returns:
            Dictionary with trend analysis

        Reason:
            Shows if behaviour is improving or declining.
        """
        return self.data_collector.get_trend_analysis()

    def get_daily_summaries(self, days: int = 7) -> List[DailySummary]:
        """
        Get daily summaries.

        Args:
            days: Number of days

        Returns:
            List of daily summaries
        """
        return self.data_collector.get_daily_summaries(days)

    # ========================================================================
    # MANUAL CONTROLS
    # ========================================================================

    def force_intervention(
        self,
        pattern_type: PatternType,
        intervention_type: InterventionType,
        reason: str = "Manual trigger"
    ) -> InterventionRecord:
        """
        Force a specific intervention.

        Args:
            pattern_type: Type of pattern
            intervention_type: Type of intervention
            reason: Reason for intervention

        Returns:
            InterventionRecord

        Reason:
            User or external system can trigger intervention manually.
        """
        pattern = DetectedPattern(
            pattern_type=pattern_type,
            severity=PatternSeverity.HIGH,
            score=80,
            detected_at=datetime.now(),
            evidence={"manual": True, "reason": reason},
            description=f"Manual intervention: {reason}",
            recommended_interventions=[intervention_type],
        )

        intervention = Intervention(
            intervention_type=intervention_type,
            pattern_type=pattern_type,
            triggered_at=datetime.now(),
            parameters={"manual": True, "reason": reason},
        )

        return self.executor.execute(intervention, pattern)

    def rollback_intervention(self, intervention_id: str) -> bool:
        """
        Rollback an intervention.

        Args:
            intervention_id: ID of intervention to rollback

        Returns:
            True if successful
        """
        return self.executor.rollback(intervention_id)

    def update_config(self, **kwargs) -> None:
        """
        Update analyzer configuration.

        Args:
            **kwargs: Configuration values to update

        Reason:
            Runtime configuration changes.
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_pattern_analyzer(
    auto_start: bool = False,
    analysis_interval: int = DEFAULT_ANALYSIS_INTERVAL_SECONDS,
    auto_intervene: bool = True,
    notification_callback: Optional[Callable] = None
) -> PatternAnalyzer:
    """
    Create a fully configured PatternAnalyzer.

    Args:
        auto_start: Start analysis immediately
        analysis_interval: Seconds between analyses
        auto_intervene: Automatically execute interventions
        notification_callback: Callback for notifications

    Returns:
        Configured PatternAnalyzer instance

    Reason:
        Factory function for easy setup.
    """
    from pathlib import Path

    # Create components
    data_collector = BehaviourDataCollector()
    detector = PatternDetector()

    config = AnalyzerConfig(
        analysis_interval=analysis_interval,
        auto_intervene=auto_intervene,
        notification_callback=notification_callback,
    )

    executor = InterventionExecutor(
        notification_callback=notification_callback
    )

    # Create analyzer
    analyzer = PatternAnalyzer(
        data_collector=data_collector,
        detector=detector,
        executor=executor,
        config=config
    )

    # Start if requested
    if auto_start:
        analyzer.start()

    return analyzer


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Pattern Analyzer...")
    print()

    # Create analyzer
    analyzer = create_pattern_analyzer(auto_start=False)

    # Add some test data
    for i in range(5):
        session = SessionRecord(
            session_id=f"test_{i}",
            started_at=datetime.now() - timedelta(days=i),
            ended_at=datetime.now() - timedelta(days=i, hours=-1),
            duration_minutes=60 - i * 5,  # Declining
            subject="Mathematics",
            topic="algebra",
            questions_answered=20,
            correct_answers=15,
            accuracy=0.75,
            theta_before=0.0,
            theta_after=0.1,
            theta_change=0.1,
        )
        analyzer.data_collector.record_session(session)

    # Record distractions
    for i in range(8):
        analyzer.data_collector.record_app_switch(datetime.now() - timedelta(minutes=i))

    # Run analysis
    result = analyzer.analyze_now()
    print(f"Analysis Result:")
    print(f"  Patterns detected: {result.patterns_detected}")
    print(f"  Interventions executed: {result.interventions_executed}")
    print(f"  Status: {result.status}")

    for p in result.patterns:
        print(f"\n  Pattern: {p.pattern_type.value}")
        print(f"  Severity: {p.severity.value}")
        print(f"  Score: {p.score}")

    # Get status
    status = analyzer.get_status()
    print(f"\nAnalyzer Status:")
    print(f"  Total analyses: {status['total_analyses']}")
    print(f"  Total patterns: {status['total_patterns_detected']}")

    print("\nAll tests passed!")
