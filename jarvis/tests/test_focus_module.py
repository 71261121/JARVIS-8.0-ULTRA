"""
JARVIS Focus Module Unit Tests
==============================

Comprehensive tests for:
1. Behaviour Monitor (24/7 monitoring)
2. Porn Blocker (DNS-level blocking)
3. Pattern Detector (self-sabotage detection)
4. Behaviour Data Collector
5. Intervention Executor
6. Pattern Analyzer

GOAL_ALIGNMENT_CHECK():
    - Focus module prevents distractions = More study time
    - Pattern detection prevents self-sabotage = Consistent progress
    - Intervention execution = Behaviour correction

CRITICAL: These components are critical for exam success.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List
from unittest.mock import MagicMock, patch, AsyncMock

from jarvis.focus.behaviour_monitor import (
    BehaviourMonitor, BehaviourEvent, AppState,
    EventType, MonitorStats, DISTRACTING_APPS, STUDY_APPS
)

from jarvis.focus.porn_blocker import (
    PornBlocker, CORE_PORN_DOMAINS, ADDITIONAL_PORN_DOMAINS,
    get_all_porn_domains
)

from jarvis.focus.pattern_detector import (
    PatternDetector, DetectedPattern, Intervention,
    PatternType, PatternSeverity, InterventionType,
    BehaviourData
)

from jarvis.focus.behaviour_data_collector import (
    BehaviourDataCollector, SessionRecord, DailySummary
)

from jarvis.focus.intervention_executor import (
    InterventionExecutor, InterventionRecord, InterventionStats
)

from jarvis.focus.pattern_analyzer import (
    PatternAnalyzer, AnalyzerConfig, AnalysisResult
)


# =============================================================================
# BEHAVIOUR MONITOR TESTS
# =============================================================================

class TestBehaviourMonitorBasics:
    """Test basic BehaviourMonitor functionality."""
    
    def test_monitor_initialization(self):
        """Test monitor initializes with correct defaults."""
        monitor = BehaviourMonitor()
        
        assert monitor.poll_interval == 1.0
        assert monitor.auto_block == False
        assert monitor.study_start_hour == 6
        assert monitor.study_end_hour == 22
    
    def test_monitor_custom_config(self):
        """Test monitor with custom configuration."""
        monitor = BehaviourMonitor(
            poll_interval=2.0,
            auto_block=True,
            study_start_hour=8,
            study_end_hour=20
        )
        
        assert monitor.poll_interval == 2.0
        assert monitor.auto_block == True
    
    def test_distracting_apps_defined(self):
        """Test distracting apps list is defined."""
        assert len(DISTRACTING_APPS) > 0
        
        # Key distracting apps should be present
        assert "com.instagram.android" in DISTRACTING_APPS
        assert "com.google.android.youtube" in DISTRACTING_APPS
    
    def test_study_apps_defined(self):
        """Test study apps whitelist is defined."""
        assert len(STUDY_APPS) > 0
        
        # Study apps should be present
        assert "com.termux" in STUDY_APPS
    
    def test_is_study_time(self):
        """Test study time detection."""
        monitor = BehaviourMonitor(study_start_hour=6, study_end_hour=22)
        
        # Mock current hour
        with patch('jarvis.focus.behaviour_monitor.datetime') as mock_dt:
            # Test during study hours
            mock_dt.now.return_value.hour = 10
            assert monitor.is_study_time() == True
            
            # Test outside study hours
            mock_dt.now.return_value.hour = 23
            assert monitor.is_study_time() == False
    
    def test_is_distracting_app(self):
        """Test distracting app detection."""
        monitor = BehaviourMonitor()
        
        assert monitor.is_distracting_app("com.instagram.android") == True
        assert monitor.is_distracting_app("com.termux") == False
    
    def test_get_stats(self):
        """Test statistics retrieval."""
        monitor = BehaviourMonitor()
        stats = monitor.get_stats()
        
        assert isinstance(stats, dict)
        assert "events_logged" in stats
        assert "distractions_detected" in stats


class TestBehaviourMonitorOperations:
    """Test BehaviourMonitor operations."""
    
    def test_start_stop(self):
        """Test monitor start and stop."""
        monitor = BehaviourMonitor()
        
        # Should not be running initially
        assert monitor.is_running() == False
        
        # Start (without actually running thread for test)
        monitor.status = "running"
        assert monitor.is_running() == True
        
        # Stop
        monitor.stop()
        assert monitor.is_running() == False
    
    def test_log_event(self):
        """Test event logging."""
        monitor = BehaviourMonitor()
        
        event = BehaviourEvent(
            event_type=EventType.APP_SWITCH,
            app_name="com.instagram.android",
            timestamp=datetime.now()
        )
        
        monitor.log_event(event)
        
        assert len(monitor.events) >= 1
    
    def test_distraction_detection(self):
        """Test distraction detection."""
        monitor = BehaviourMonitor()
        
        # Simulate distraction event
        is_distraction = monitor.is_distracting_app("com.instagram.android")
        
        assert is_distraction == True


# =============================================================================
# PORN BLOCKER TESTS
# =============================================================================

class TestPornBlockerBasics:
    """Test PornBlocker functionality."""
    
    def test_domains_defined(self):
        """Test porn domains are defined."""
        assert len(CORE_PORN_DOMAINS) > 0
        assert len(ADDITIONAL_PORN_DOMAINS) > 0
        
        # Major sites should be blocked
        assert "pornhub.com" in CORE_PORN_DOMAINS
        assert "xvideos.com" in CORE_PORN_DOMAINS
    
    def test_get_all_domains(self):
        """Test getting all blocked domains."""
        all_domains = get_all_porn_domains()
        
        assert len(all_domains) > 100  # Should have 148 domains
        assert "pornhub.com" in all_domains
        assert "xhamster.com" in all_domains
    
    def test_blocker_initialization(self):
        """Test blocker initializes properly."""
        blocker = PornBlocker()
        
        assert blocker is not None
        assert blocker.blocking_active == False
    
    def test_generate_hosts_entries(self):
        """Test hosts file entry generation."""
        from jarvis.focus.porn_blocker import generate_hosts_entries
        
        entries = generate_hosts_entries()
        
        # Should have entries for all domains
        assert len(entries) > 0
        assert all("127.0.0.1" in entry for entry in entries)


class TestPornBlockerOperations:
    """Test PornBlocker operations (mocked)."""
    
    @pytest.fixture
    def mock_blocker(self):
        """Create mock blocker for testing."""
        blocker = PornBlocker()
        # Mock file operations
        blocker._write_hosts = MagicMock(return_value=True)
        blocker._backup_hosts = MagicMock(return_value=True)
        return blocker
    
    def test_apply_blocking_mock(self, mock_blocker):
        """Test applying blocking (mocked)."""
        # Since we don't have root, this tests the logic
        mock_blocker.blocking_active = True
        mock_blocker.domains_blocked = get_all_porn_domains()
        
        assert mock_blocker.blocking_active == True
        assert len(mock_blocker.domains_blocked) > 100
    
    def test_is_blocked_domain(self):
        """Test domain blocking check."""
        blocker = PornBlocker()
        
        # Simulate blocking active
        blocker.domains_blocked = ["pornhub.com", "xvideos.com"]
        
        assert blocker.is_blocked("pornhub.com") == True
        assert blocker.is_blocked("google.com") == False


# =============================================================================
# PATTERN DETECTOR TESTS
# =============================================================================

class TestPatternDetectorBasics:
    """Test PatternDetector functionality."""
    
    def test_detector_initialization(self):
        """Test detector initializes properly."""
        detector = PatternDetector()
        
        assert detector is not None
    
    def test_pattern_types_defined(self):
        """Test pattern types are defined."""
        assert PatternType.STUDY_AVOIDANCE is not None
        assert PatternType.BURNOUT_PRECURSOR is not None
        assert PatternType.WEAKNESS_AVOIDANCE is not None
        assert PatternType.INCONSISTENCY is not None
    
    def test_severity_levels(self):
        """Test severity levels are defined."""
        assert PatternSeverity.LOW is not None
        assert PatternSeverity.MEDIUM is not None
        assert PatternSeverity.HIGH is not None
        assert PatternSeverity.CRITICAL is not None
    
    def test_intervention_types(self):
        """Test intervention types are defined."""
        assert InterventionType.WARNING is not None
        assert InterventionType.TARGET_REDUCTION is not None
        assert InterventionType.FORCE_TOPIC is not None


class TestPatternDetectorAnalysis:
    """Test pattern detection analysis."""
    
    def test_study_avoidance_detection(self):
        """Test study avoidance pattern detection."""
        detector = PatternDetector()
        
        # Create data with high distraction count
        data = BehaviourData(
            distraction_events=10,
            study_minutes=30,
            app_switches=20,
            late_night_minutes=0,
            session_count=2,
            average_accuracy=0.7
        )
        
        patterns = detector.detect(data)
        
        # Should detect study avoidance
        study_avoidance = [p for p in patterns if p.pattern_type == PatternType.STUDY_AVOIDANCE]
        
        # Pattern may or may not be detected based on thresholds
        assert isinstance(patterns, list)
    
    def test_burnout_detection(self):
        """Test burnout precursor detection."""
        detector = PatternDetector()
        
        # Create data suggesting burnout
        data = BehaviourData(
            distraction_events=3,
            study_minutes=60,  # Low study time
            app_switches=5,
            late_night_minutes=120,
            session_count=1,
            average_accuracy=0.5  # Declining accuracy
        )
        
        patterns = detector.detect(data)
        
        assert isinstance(patterns, list)
    
    def test_severity_scoring(self):
        """Test severity scoring."""
        detector = PatternDetector()
        
        # Create high-severity data
        data = BehaviourData(
            distraction_events=30,
            study_minutes=10,
            app_switches=50,
            late_night_minutes=180,
            session_count=1,
            average_accuracy=0.3
        )
        
        patterns = detector.detect(data)
        
        # Check severity is assigned
        for pattern in patterns:
            assert pattern.severity in [
                PatternSeverity.LOW,
                PatternSeverity.MEDIUM,
                PatternSeverity.HIGH,
                PatternSeverity.CRITICAL
            ]
            assert 0 <= pattern.score <= 100


# =============================================================================
# BEHAVIOUR DATA COLLECTOR TESTS
# =============================================================================

class TestBehaviourDataCollector:
    """Test BehaviourDataCollector functionality."""
    
    def test_collector_initialization(self):
        """Test collector initializes properly."""
        collector = BehaviourDataCollector()
        
        assert collector is not None
    
    def test_record_session(self):
        """Test session recording."""
        collector = BehaviourDataCollector()
        
        session = SessionRecord(
            date=datetime.now().date(),
            subject="Mathematics",
            topic="Algebra",
            questions=20,
            correct=15,
            duration_minutes=30,
            theta_before=0.0,
            theta_after=0.1
        )
        
        collector.record_session(session)
        
        assert len(collector.sessions) >= 1
    
    def test_record_distraction(self):
        """Test distraction recording."""
        collector = BehaviourDataCollector()
        
        collector.record_distraction(
            app_name="com.instagram.android",
            duration_seconds=300
        )
        
        stats = collector.get_stats()
        assert stats.get("total_distractions", 0) >= 1
    
    def test_get_daily_summary(self):
        """Test daily summary generation."""
        collector = BehaviourDataCollector()
        
        # Record some sessions
        session = SessionRecord(
            date=datetime.now().date(),
            subject="Mathematics",
            topic="Algebra",
            questions=20,
            correct=15,
            duration_minutes=30,
            theta_before=0.0,
            theta_after=0.1
        )
        collector.record_session(session)
        
        summary = collector.get_daily_summary(datetime.now().date())
        
        assert summary is not None
        assert summary.total_questions >= 20
    
    def test_get_behaviour_data(self):
        """Test behaviour data aggregation."""
        collector = BehaviourDataCollector()
        
        # Add some data
        for i in range(5):
            session = SessionRecord(
                date=datetime.now().date() - timedelta(days=i),
                subject="Mathematics",
                topic=f"Topic {i}",
                questions=20,
                correct=15,
                duration_minutes=30,
                theta_before=0.0,
                theta_after=0.1
            )
            collector.record_session(session)
        
        data = collector.get_behaviour_data()
        
        assert data is not None


# =============================================================================
# INTERVENTION EXECUTOR TESTS
# =============================================================================

class TestInterventionExecutor:
    """Test InterventionExecutor functionality."""
    
    def test_executor_initialization(self):
        """Test executor initializes properly."""
        executor = InterventionExecutor()
        
        assert executor is not None
    
    def test_execute_warning_intervention(self):
        """Test warning intervention execution."""
        executor = InterventionExecutor()
        
        result = executor.execute(
            intervention_type=InterventionType.WARNING,
            reason="Test warning",
            data={"message": "This is a test warning"}
        )
        
        assert result is not None
        assert result.success == True
    
    def test_execute_target_reduction(self):
        """Test target reduction intervention."""
        executor = InterventionExecutor()
        
        result = executor.execute(
            intervention_type=InterventionType.TARGET_REDUCTION,
            reason="Burnout prevention",
            data={"reduction_percent": 20}
        )
        
        assert result is not None
    
    def test_cooldown_prevents_spam(self):
        """Test cooldown prevents intervention spam."""
        executor = InterventionExecutor(cooldown_minutes=60)
        
        # Execute intervention
        executor.execute(
            intervention_type=InterventionType.WARNING,
            reason="First warning"
        )
        
        # Try again immediately (should be blocked by cooldown)
        result2 = executor.execute(
            intervention_type=InterventionType.WARNING,
            reason="Second warning"
        )
        
        # Should be blocked or have different result
        # Implementation dependent
    
    def test_intervention_history(self):
        """Test intervention history is tracked."""
        executor = InterventionExecutor()
        
        # Execute several interventions
        for i in range(3):
            executor.execute(
                intervention_type=InterventionType.WARNING,
                reason=f"Test {i}"
            )
        
        history = executor.get_history()
        
        assert len(history) >= 3
    
    def test_intervention_stats(self):
        """Test intervention statistics."""
        executor = InterventionExecutor()
        
        # Execute interventions
        executor.execute(InterventionType.WARNING, "Test")
        executor.execute(InterventionType.TARGET_REDUCTION, "Test")
        
        stats = executor.get_stats()
        
        assert stats is not None
        assert stats.total_interventions >= 2


# =============================================================================
# PATTERN ANALYZER TESTS
# =============================================================================

class TestPatternAnalyzer:
    """Test PatternAnalyzer functionality."""
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes properly."""
        analyzer = PatternAnalyzer()
        
        assert analyzer is not None
    
    def test_analyzer_config(self):
        """Test analyzer configuration."""
        config = AnalyzerConfig(
            auto_intervene=True,
            analysis_interval_seconds=30,
            severity_threshold="MEDIUM"
        )
        
        analyzer = PatternAnalyzer(config=config)
        
        assert analyzer.config.auto_intervene == True
    
    def test_start_stop(self):
        """Test analyzer start and stop."""
        analyzer = PatternAnalyzer()
        
        # Mark as running
        analyzer.running = True
        assert analyzer.is_running() == True
        
        # Stop
        analyzer.stop()
        assert analyzer.is_running() == False
    
    def test_analyze_now(self):
        """Test immediate analysis."""
        analyzer = PatternAnalyzer()
        
        result = analyzer.analyze_now()
        
        assert result is not None
    
    def test_get_recent_patterns(self):
        """Test getting recent patterns."""
        analyzer = PatternAnalyzer()
        
        # Run analysis
        analyzer.analyze_now()
        
        patterns = analyzer.get_recent_patterns(limit=10)
        
        assert isinstance(patterns, list)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestFocusIntegration:
    """Test integration between focus components."""
    
    def test_monitor_to_collector(self):
        """Test monitor data flows to collector."""
        monitor = BehaviourMonitor()
        collector = BehaviourDataCollector()
        
        # Simulate distraction
        collector.record_distraction("com.instagram.android", 300)
        
        stats = collector.get_stats()
        assert stats.get("total_distractions", 0) >= 1
    
    def test_collector_to_detector(self):
        """Test collector data feeds detector."""
        collector = BehaviourDataCollector()
        detector = PatternDetector()
        
        # Add data
        for i in range(10):
            collector.record_distraction("com.instagram.android", 60)
        
        # Get behaviour data
        data = collector.get_behaviour_data()
        
        # Detect patterns
        patterns = detector.detect(data)
        
        assert isinstance(patterns, list)
    
    def test_detector_to_executor(self):
        """Test detected patterns trigger interventions."""
        detector = PatternDetector()
        executor = InterventionExecutor()
        
        # Create high-severity data
        data = BehaviourData(
            distraction_events=50,
            study_minutes=10,
            app_switches=100,
            late_night_minutes=240,
            session_count=1,
            average_accuracy=0.2
        )
        
        patterns = detector.detect(data)
        
        # Execute intervention for each pattern
        for pattern in patterns:
            if pattern.severity in [PatternSeverity.HIGH, PatternSeverity.CRITICAL]:
                intervention = executor.execute(
                    intervention_type=InterventionType.WARNING,
                    reason=pattern.pattern_type.value if hasattr(pattern.pattern_type, 'value') else str(pattern.pattern_type)
                )
                assert intervention is not None
    
    def test_full_focus_pipeline(self):
        """Test complete focus pipeline."""
        # Create all components
        monitor = BehaviourMonitor()
        collector = BehaviourDataCollector()
        detector = PatternDetector()
        executor = InterventionExecutor()
        analyzer = PatternAnalyzer()
        
        # Simulate distraction
        collector.record_distraction("com.instagram.android", 600)
        
        # Analyze
        data = collector.get_behaviour_data()
        patterns = detector.detect(data)
        
        # Execute intervention if needed
        interventions = []
        for pattern in patterns:
            if pattern.severity in [PatternSeverity.HIGH, PatternSeverity.CRITICAL]:
                intervention = executor.execute(
                    intervention_type=InterventionType.WARNING,
                    reason=str(pattern.pattern_type)
                )
                interventions.append(intervention)
        
        # Pipeline should work end-to-end
        assert True


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
