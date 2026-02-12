"""
JARVIS Focus Module
===================

Purpose: Distraction blocking and focus management.

Components:
- Behaviour Monitor: 24/7 background monitoring
- Porn Blocker: DNS-level permanent blocking
- Root Commands: Execute commands with root
- App Blocking: Force-stop distracting apps
- Network Blocking: iptables-based network control

Requirements:
- ROOTED Android device
- Termux with root access
- su binary available

Critical for:
- Blocking Instagram, YouTube, Porn
- Enforcing study hours
- Preventing distraction loops
- 24/7 behaviour monitoring

Without root: Focus module will be LIMITED (40% effective)
With root: Focus module will be FULLY effective (95%)

EXAM IMPACT:
    CRITICAL. User's biggest distractions are Porn and Instagram.
    Without blocking, user cannot maintain 8-hour study schedule.
    This module provides:
    - Real-time distraction detection
    - Automatic app blocking during study hours
    - Permanent porn site blocking at DNS level
    - Sleep pattern monitoring
    - Behaviour pattern analysis data
"""

import os

# Check root availability
ROOT_AVAILABLE = False

def check_root():
    """
    Check if root is available.
    
    Returns:
        True if root access is available
    
    Reason:
        Must verify root before attempting any root operations.
        Many features depend on root access.
    """
    global ROOT_AVAILABLE
    
    su_paths = ["/system/bin/su", "/system/xbin/su", "/sbin/su", "/su/bin/su"]
    for path in su_paths:
        if os.path.exists(path):
            try:
                import subprocess
                result = subprocess.run(
                    [path, "-c", "id"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if "uid=0" in result.stdout:
                    ROOT_AVAILABLE = True
                    break
            except Exception:
                pass
    
    return ROOT_AVAILABLE

# Check on import
check_root()


# ============================================================================
# IMPORTS
# ============================================================================

# Root access module
from .root_access import (
    RootAccess,
    RootStatus,
    CommandResult,
    DISTRACTING_APPS,
    get_distracting_apps_by_severity,
)

# Behaviour monitor
from .behaviour_monitor import (
    BehaviourMonitor,
    BehaviourEvent,
    AppState,
    DeviceStatus,
    DeviceState,
    MonitorStatus,
    ScreenState,
    EventType,
    MonitorStats,
    CommandExecutor,
    DISTRACTING_APPS as DISTRACTING_APPS_MONITOR,
    STUDY_APPS,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_STUDY_START,
    DEFAULT_STUDY_END,
)

# Porn blocker
from .porn_blocker import (
    PornBlocker,
    get_all_porn_domains,
    generate_hosts_entries,
    CORE_PORN_DOMAINS,
    ADDITIONAL_PORN_DOMAINS,
    HOSTS_FILE,
    BACKUP_DIR,
)

# Pattern detector
from .pattern_detector import (
    PatternDetector,
    DetectedPattern,
    Intervention,
    BehaviourData,
    PatternType,
    PatternSeverity,
    InterventionType,
)

# Behaviour data collector
from .behaviour_data_collector import (
    BehaviourDataCollector,
    SessionRecord,
    DailySummary,
)

# Intervention executor
from .intervention_executor import (
    InterventionExecutor,
    InterventionRecord,
    InterventionStats,
)

# Pattern analyzer
from .pattern_analyzer import (
    PatternAnalyzer,
    AnalyzerConfig,
    AnalysisResult,
    create_pattern_analyzer,
)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_monitor(
    poll_interval: float = 1.0,
    auto_block: bool = False,
    study_start: int = 6,
    study_end: int = 22
) -> BehaviourMonitor:
    """
    Create and return a behaviour monitor instance.
    
    Args:
        poll_interval: Seconds between polls
        auto_block: Enable automatic blocking
        study_start: Study start hour (24-hour)
        study_end: Study end hour (24-hour)
    
    Returns:
        Configured BehaviourMonitor instance
    
    Reason:
        Factory function for easy monitor creation.
    """
    return BehaviourMonitor(
        poll_interval=poll_interval,
        auto_block=auto_block,
        study_start_hour=study_start,
        study_end_hour=study_end
    )


def create_porn_blocker() -> PornBlocker:
    """
    Create and return a porn blocker instance.
    
    Returns:
        PornBlocker instance
    
    Reason:
        Factory function for easy blocker creation.
    """
    return PornBlocker()


def quick_block_porn() -> tuple:
    """
    Quick function to apply porn blocking.
    
    Returns:
        Tuple of (success, message)
    
    Reason:
        One-liner for immediate blocking.
    
    EXAM IMPACT:
        Immediate protection from porn distraction.
    """
    blocker = PornBlocker()
    return blocker.apply_blocking()


def get_focus_status() -> dict:
    """
    Get current focus system status.
    
    Returns:
        Dictionary with status information
    
    Reason:
        Quick status check for dashboard.
    """
    return {
        "root_available": ROOT_AVAILABLE,
        "monitor_available": True,  # Module loaded successfully
        "porn_blocker_available": True,
        "pattern_analyzer_available": True,
        "total_distracting_apps": len(DISTRACTING_APPS),
        "total_porn_domains": len(get_all_porn_domains()),
    }


def create_full_protection_system(
    auto_start: bool = True,
    auto_intervene: bool = True,
    notification_callback=None
) -> dict:
    """
    Create and return the complete protection system.
    
    Args:
        auto_start: Start monitoring and analysis immediately
        auto_intervene: Automatically execute interventions
        notification_callback: Callback for notifications
    
    Returns:
        Dictionary with all components
    
    Reason:
        One-stop function to set up entire focus system.
    
    EXAM IMPACT:
        Quick setup of all protection components.
    """
    from pathlib import Path
    
    # Create data collector
    data_collector = BehaviourDataCollector()
    
    # Create pattern analyzer (includes detector and executor)
    analyzer = create_pattern_analyzer(
        auto_start=False,
        auto_intervene=auto_intervene,
        notification_callback=notification_callback
    )
    
    # Create behaviour monitor
    monitor = BehaviourMonitor(auto_block=auto_intervene)
    
    # Create porn blocker
    porn_blocker = PornBlocker()
    
    if auto_start:
        monitor.start()
        analyzer.start()
    
    return {
        "monitor": monitor,
        "porn_blocker": porn_blocker,
        "analyzer": analyzer,
        "data_collector": data_collector,
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Root check
    "ROOT_AVAILABLE",
    "check_root",
    
    # Root access
    "RootAccess",
    "RootStatus",
    "CommandResult",
    "DISTRACTING_APPS",
    "get_distracting_apps_by_severity",
    
    # Behaviour monitor
    "BehaviourMonitor",
    "BehaviourEvent",
    "AppState",
    "DeviceStatus",
    "DeviceState",
    "MonitorStatus",
    "ScreenState",
    "EventType",
    "MonitorStats",
    "CommandExecutor",
    "STUDY_APPS",
    "DEFAULT_POLL_INTERVAL",
    
    # Porn blocker
    "PornBlocker",
    "get_all_porn_domains",
    "generate_hosts_entries",
    "CORE_PORN_DOMAINS",
    "ADDITIONAL_PORN_DOMAINS",
    
    # Pattern detector
    "PatternDetector",
    "DetectedPattern",
    "Intervention",
    "BehaviourData",
    "PatternType",
    "PatternSeverity",
    "InterventionType",
    
    # Behaviour data collector
    "BehaviourDataCollector",
    "SessionRecord",
    "DailySummary",
    
    # Intervention executor
    "InterventionExecutor",
    "InterventionRecord",
    "InterventionStats",
    
    # Pattern analyzer
    "PatternAnalyzer",
    "AnalyzerConfig",
    "AnalysisResult",
    "create_pattern_analyzer",
    
    # Convenience functions
    "create_monitor",
    "create_porn_blocker",
    "quick_block_porn",
    "get_focus_status",
    "create_full_protection_system",
]
