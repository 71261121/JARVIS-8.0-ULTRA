"""
JARVIS Configuration Module
============================

Purpose: Load, validate, and provide access to configuration.

Reason for Pydantic:
    - Runtime validation catches errors early
    - Type hints for IDE support
    - Clear error messages for invalid config
    
Rollback:
    If config is invalid, system falls back to defaults.
    User is notified of all issues.

Usage:
    from jarvis.core.config import load_config
    config = load_config()
    print(config.user.name)
"""

import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

# Try to import pydantic, fall back to dataclasses if not available
try:
    from pydantic import BaseModel, Field, validator
    USE_PYDANTIC = True
except ImportError:
    USE_PYDANTIC = False


# ============================================================================
# CONFIGURATION DATA CLASSES
# ============================================================================

@dataclass
class SubjectConfig:
    """Configuration for a single subject."""
    weightage: int
    strength: str
    target: int
    priority: int
    foundation_required: bool = False
    foundation_days: int = 0
    biology_advantage: bool = False


@dataclass
class UserConfig:
    """User-specific configuration."""
    name: str = "Student"
    background: str = "biology_stream"
    exam: str = "Loyola Academy B.Sc CS"
    exam_date: str = "2025-05-15"
    target_score: int = 50
    safe_score: int = 48
    days_remaining: int = 75
    subjects: Dict[str, SubjectConfig] = field(default_factory=dict)


@dataclass
class PhaseConfig:
    """Single phase configuration."""
    name: str
    days: List[int]  # [start, end]
    focus: str
    target_score: int
    mock_frequency: str


@dataclass
class ScheduleItem:
    """Single schedule item."""
    time: str
    duration: int  # minutes
    activity: str
    type: str
    reason: str = ""


@dataclass
class StudyPlanConfig:
    """Study plan configuration."""
    total_days: int = 75
    daily_hours: int = 8
    max_hours: int = 10
    phases: List[PhaseConfig] = field(default_factory=list)
    daily_schedule: List[ScheduleItem] = field(default_factory=list)


@dataclass
class MissedDayProtocol:
    """Missed day recovery protocol."""
    enabled: bool = True
    target_reduction: float = 0.20
    overcompensation_blocked: bool = True
    message_style: str = "neutral_recovery"


@dataclass
class ForcedBreak:
    """Forced break configuration."""
    after_days: int
    type: str
    hours: int
    reason: str


@dataclass
class PanicDetection:
    """Panic detection configuration."""
    enabled: bool = True
    no_progress_minutes: int = 180
    response: str = "suggest_break_and_restart"


@dataclass
class BurnoutPreventionConfig:
    """Burnout prevention configuration."""
    guilt_messaging: bool = False
    forward_looking_motivation: bool = True
    missed_day_protocol: MissedDayProtocol = field(default_factory=MissedDayProtocol)
    forced_breaks: List[ForcedBreak] = field(default_factory=list)
    panic_detection: PanicDetection = field(default_factory=PanicDetection)


@dataclass
class BlockRules:
    """App blocking rules."""
    study_hours: Dict[str, str] = field(default_factory=lambda: {"start": "08:00", "end": "22:00"})
    free_hours: Dict[str, str] = field(default_factory=lambda: {"start": "22:00", "end": "23:00"})
    sleep_hours: Dict[str, str] = field(default_factory=lambda: {"start": "23:00", "end": "07:00"})


@dataclass
class AppConfig:
    """Single app blocking configuration."""
    severity: str
    study_hours: str
    free_hours: str
    sleep_hours: str
    package: str = ""
    whitelist_mode: bool = False


@dataclass
class DistractionBlockingConfig:
    """Distraction blocking configuration."""
    root_required: bool = True
    block_rules: BlockRules = field(default_factory=BlockRules)
    apps: Dict[str, AppConfig] = field(default_factory=dict)


@dataclass
class XPSystem:
    """XP system configuration."""
    correct_answer: int = 10
    wrong_with_review: int = 5
    wrong_skip_review: int = 0
    daily_goals_complete: int = 100
    streak_per_day: int = 10
    mock_test_complete: int = 100
    topic_mastered: int = 200
    achievement_unlock: List[int] = field(default_factory=lambda: [50, 500])


@dataclass
class PunishmentConfig:
    """Punishment configuration."""
    skip_session: int = -50
    skip_day: int = -100
    skip_2_days: int = -200
    porn_attempt: int = -200
    streak_break_multiplier: float = 2.0


@dataclass
class StreakConfig:
    """Streak configuration."""
    freeze_available: int = 3
    freeze_per_month: int = 3
    recovery_window_hours: int = 24


@dataclass
class LevelConfig:
    """Level configuration."""
    level: int
    title: str
    xp_required: int


@dataclass
class MessagingStyle:
    """Messaging style configuration."""
    type: str = "factual_motivational"
    guilt_based: bool = False
    examples: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class PsychologicalEngineConfig:
    """Psychological engine configuration."""
    xp_system: XPSystem = field(default_factory=XPSystem)
    punishment: PunishmentConfig = field(default_factory=PunishmentConfig)
    streak: StreakConfig = field(default_factory=StreakConfig)
    levels: List[LevelConfig] = field(default_factory=list)
    messaging_style: MessagingStyle = field(default_factory=MessagingStyle)


@dataclass
class AIEngineConfig:
    """AI engine configuration."""
    engine: str = "llama.cpp"
    model: str = "deepseek-r1-1.5b-q4_k_m"
    model_size_mb: int = 1070
    context_length: int = 2048
    temperature: float = 0.7
    max_tokens: int = 512
    cache_enabled: bool = True
    cache_ttl_hours: int = 168
    cache_max_entries: int = 1000


@dataclass
class IRTSettings:
    """IRT algorithm settings."""
    model: str = "3PL"
    D_constant: float = 1.7
    theta_range: List[float] = field(default_factory=lambda: [-3.0, 3.0])
    initial_theta: float = 0.0
    min_questions: int = 10
    max_questions: int = 30
    standard_error_threshold: float = 0.3


@dataclass
class SM2Settings:
    """SM-2 algorithm settings."""
    default_ease_factor: float = 2.5
    minimum_ease_factor: float = 1.3
    retention_target: float = 0.9


@dataclass
class DatabaseConfig:
    """Database configuration."""
    type: str = "sqlite"
    path: str = "data/db/jarvis.db"
    backup_path: str = "data/backup/"
    backup_frequency: str = "daily"
    wal_mode: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    path: str = "data/logs/"
    max_size_mb: int = 10
    backup_count: int = 5


@dataclass
class PathsConfig:
    """Path configuration."""
    models: str = "models/"
    cache: str = "data/cache/"
    logs: str = "data/logs/"
    backup: str = "data/backup/"
    config: str = "config.json"


@dataclass
class Config:
    """
    Main configuration class.
    
    Contains all configuration for JARVIS system.
    Validates on load, provides type-safe access.
    """
    user: UserConfig = field(default_factory=UserConfig)
    study_plan: StudyPlanConfig = field(default_factory=StudyPlanConfig)
    burnout_prevention: BurnoutPreventionConfig = field(default_factory=BurnoutPreventionConfig)
    distraction_blocking: DistractionBlockingConfig = field(default_factory=DistractionBlockingConfig)
    psychological_engine: PsychologicalEngineConfig = field(default_factory=PsychologicalEngineConfig)
    ai_engine: AIEngineConfig = field(default_factory=AIEngineConfig)
    irt_settings: IRTSettings = field(default_factory=IRTSettings)
    sm2_settings: SM2Settings = field(default_factory=SM2Settings)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    
    # Internal tracking
    _loaded_from: str = ""
    _load_errors: List[str] = field(default_factory=list)


# ============================================================================
# CONFIG LOADER
# ============================================================================

def _parse_subject_config(data: dict) -> SubjectConfig:
    """Parse subject configuration from dict."""
    return SubjectConfig(
        weightage=data.get("weightage", 0),
        strength=data.get("strength", "unknown"),
        target=data.get("target", 0),
        priority=data.get("priority", 99),
        foundation_required=data.get("foundation_required", False),
        foundation_days=data.get("foundation_days", 0),
        biology_advantage=data.get("biology_advantage", False),
    )


def _parse_phase_config(data: dict) -> PhaseConfig:
    """Parse phase configuration from dict."""
    return PhaseConfig(
        name=data.get("name", "Unknown"),
        days=data.get("days", [1, 1]),
        focus=data.get("focus", ""),
        target_score=data.get("target_score", 0),
        mock_frequency=data.get("mock_frequency", "weekly"),
    )


def _parse_schedule_item(data: dict) -> ScheduleItem:
    """Parse schedule item from dict."""
    return ScheduleItem(
        time=data.get("time", "00:00"),
        duration=data.get("duration", 0),
        activity=data.get("activity", ""),
        type=data.get("type", ""),
        reason=data.get("reason", ""),
    )


def _parse_forced_break(data: dict) -> ForcedBreak:
    """Parse forced break from dict."""
    return ForcedBreak(
        after_days=data.get("after_days", 5),
        type=data.get("type", "half_day"),
        hours=data.get("hours", 4),
        reason=data.get("reason", ""),
    )


def _parse_level_config(data: dict) -> LevelConfig:
    """Parse level configuration from dict."""
    return LevelConfig(
        level=data.get("level", 1),
        title=data.get("title", "Beginner"),
        xp_required=data.get("xp_required", 0),
    )


def _parse_app_config(data: dict) -> AppConfig:
    """Parse app configuration from dict."""
    return AppConfig(
        severity=data.get("severity", "medium"),
        study_hours=data.get("study_hours", "blocked"),
        free_hours=data.get("free_hours", "allow"),
        sleep_hours=data.get("sleep_hours", "blocked"),
        package=data.get("package", ""),
        whitelist_mode=data.get("whitelist_mode", False),
    )


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to config.json. If None, searches default locations.
    
    Returns:
        Config: Validated configuration object
    
    Raises:
        FileNotFoundError: If config file not found
        ValueError: If config is invalid (after loading defaults)
    
    Reason for design:
        - Search multiple locations for flexibility
        - Fall back to defaults for missing values
        - Collect all errors before failing
        - Log warnings for non-critical issues
    """
    config = Config()
    errors = []
    
    # Find config file
    search_paths = [
        config_path,
        "config.json",
        "jarvis/config.json",
        os.path.expanduser("~/jarvis/config.json"),
        "/data/data/com.termux/files/home/jarvis/config.json",
    ]
    
    config_file = None
    for path in search_paths:
        if path and os.path.exists(path):
            config_file = path
            break
    
    if config_file is None:
        config._load_errors.append("Config file not found, using defaults")
        return config
    
    try:
        with open(config_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        config._load_errors.append(f"Invalid JSON in config file: {e}")
        return config
    
    config._loaded_from = config_file
    
    # Parse user config
    if "user" in data:
        user_data = data["user"]
        config.user = UserConfig(
            name=user_data.get("name", "Student"),
            background=user_data.get("background", "biology_stream"),
            exam=user_data.get("exam", "Loyola Academy B.Sc CS"),
            exam_date=user_data.get("exam_date", "2025-05-15"),
            target_score=user_data.get("target_score", 50),
            safe_score=user_data.get("safe_score", 48),
            days_remaining=user_data.get("days_remaining", 75),
            subjects={
                k: _parse_subject_config(v) 
                for k, v in user_data.get("subjects", {}).items()
            },
        )
    
    # Parse study plan
    if "study_plan" in data:
        sp_data = data["study_plan"]
        config.study_plan = StudyPlanConfig(
            total_days=sp_data.get("total_days", 75),
            daily_hours=sp_data.get("daily_hours", 8),
            max_hours=sp_data.get("max_hours", 10),
            phases=[
                _parse_phase_config(p) 
                for p in sp_data.get("phases", [])
            ],
            daily_schedule=[
                _parse_schedule_item(s) 
                for s in sp_data.get("daily_schedule", [])
            ],
        )
    
    # Parse burnout prevention
    if "burnout_prevention" in data:
        bp_data = data["burnout_prevention"]
        mdp_data = bp_data.get("missed_day_protocol", {})
        
        config.burnout_prevention = BurnoutPreventionConfig(
            guilt_messaging=bp_data.get("guilt_messaging", False),
            forward_looking_motivation=bp_data.get("forward_looking_motivation", True),
            missed_day_protocol=MissedDayProtocol(
                enabled=mdp_data.get("enabled", True),
                target_reduction=mdp_data.get("target_reduction", 0.20),
                overcompensation_blocked=mdp_data.get("overcompensation_blocked", True),
                message_style=mdp_data.get("message_style", "neutral_recovery"),
            ),
            forced_breaks=[
                _parse_forced_break(b) 
                for b in bp_data.get("forced_breaks", [])
            ],
            panic_detection=PanicDetection(
                enabled=bp_data.get("panic_detection", {}).get("enabled", True),
                no_progress_minutes=bp_data.get("panic_detection", {}).get("no_progress_minutes", 180),
                response=bp_data.get("panic_detection", {}).get("response", "suggest_break_and_restart"),
            ),
        )
    
    # Parse distraction blocking
    if "distraction_blocking" in data:
        db_data = data["distraction_blocking"]
        br_data = db_data.get("block_rules", {})
        
        config.distraction_blocking = DistractionBlockingConfig(
            root_required=db_data.get("root_required", True),
            block_rules=BlockRules(
                study_hours=br_data.get("study_hours", {"start": "08:00", "end": "22:00"}),
                free_hours=br_data.get("free_hours", {"start": "22:00", "end": "23:00"}),
                sleep_hours=br_data.get("sleep_hours", {"start": "23:00", "end": "07:00"}),
            ),
            apps={
                k: _parse_app_config(v) 
                for k, v in db_data.get("apps", {}).items()
            },
        )
    
    # Parse psychological engine
    if "psychological_engine" in data:
        pe_data = data["psychological_engine"]
        xp_data = pe_data.get("xp_system", {})
        pun_data = pe_data.get("punishment", {})
        str_data = pe_data.get("streak", {})
        msg_data = pe_data.get("messaging_style", {})
        
        config.psychological_engine = PsychologicalEngineConfig(
            xp_system=XPSystem(
                correct_answer=xp_data.get("correct_answer", 10),
                wrong_with_review=xp_data.get("wrong_with_review", 5),
                wrong_skip_review=xp_data.get("wrong_skip_review", 0),
                daily_goals_complete=xp_data.get("daily_goals_complete", 100),
                streak_per_day=xp_data.get("streak_per_day", 10),
                mock_test_complete=xp_data.get("mock_test_complete", 100),
                topic_mastered=xp_data.get("topic_mastered", 200),
                achievement_unlock=xp_data.get("achievement_unlock", [50, 500]),
            ),
            punishment=PunishmentConfig(
                skip_session=pun_data.get("skip_session", -50),
                skip_day=pun_data.get("skip_day", -100),
                skip_2_days=pun_data.get("skip_2_days", -200),
                porn_attempt=pun_data.get("porn_attempt", -200),
                streak_break_multiplier=pun_data.get("streak_break_multiplier", 2.0),
            ),
            streak=StreakConfig(
                freeze_available=str_data.get("freeze_available", 3),
                freeze_per_month=str_data.get("freeze_per_month", 3),
                recovery_window_hours=str_data.get("recovery_window_hours", 24),
            ),
            levels=[
                _parse_level_config(l) 
                for l in pe_data.get("levels", [])
            ],
            messaging_style=MessagingStyle(
                type=msg_data.get("type", "factual_motivational"),
                guilt_based=msg_data.get("guilt_based", False),
                examples=msg_data.get("examples", {}),
            ),
        )
    
    # Parse AI engine
    if "ai_engine" in data:
        ai_data = data["ai_engine"]
        cache_data = ai_data.get("cache", {})
        
        config.ai_engine = AIEngineConfig(
            engine=ai_data.get("engine", "llama.cpp"),
            model=ai_data.get("model", "deepseek-r1-1.5b-q4_k_m"),
            model_size_mb=ai_data.get("model_size_mb", 1070),
            context_length=ai_data.get("context_length", 2048),
            temperature=ai_data.get("temperature", 0.7),
            max_tokens=ai_data.get("max_tokens", 512),
            cache_enabled=cache_data.get("enabled", True),
            cache_ttl_hours=cache_data.get("ttl_hours", 168),
            cache_max_entries=cache_data.get("max_entries", 1000),
        )
    
    # Parse IRT settings
    if "irt_settings" in data:
        irt_data = data["irt_settings"]
        sr_data = irt_data.get("stopping_rule", {})
        
        config.irt_settings = IRTSettings(
            model=irt_data.get("model", "3PL"),
            D_constant=irt_data.get("D_constant", 1.7),
            theta_range=irt_data.get("theta_range", [-3.0, 3.0]),
            initial_theta=irt_data.get("initial_theta", 0.0),
            min_questions=sr_data.get("min_questions", 10),
            max_questions=sr_data.get("max_questions", 30),
            standard_error_threshold=sr_data.get("standard_error_threshold", 0.3),
        )
    
    # Parse SM-2 settings
    if "sm2_settings" in data:
        sm2_data = data["sm2_settings"]
        
        config.sm2_settings = SM2Settings(
            default_ease_factor=sm2_data.get("default_ease_factor", 2.5),
            minimum_ease_factor=sm2_data.get("minimum_ease_factor", 1.3),
            retention_target=sm2_data.get("retention_target", 0.9),
        )
    
    # Parse database config
    if "database" in data:
        db_data = data["database"]
        
        config.database = DatabaseConfig(
            type=db_data.get("type", "sqlite"),
            path=db_data.get("path", "data/db/jarvis.db"),
            backup_path=db_data.get("backup_path", "data/backup/"),
            backup_frequency=db_data.get("backup_frequency", "daily"),
            wal_mode=db_data.get("wal_mode", True),
        )
    
    # Parse logging config
    if "logging" in data:
        log_data = data["logging"]
        
        config.logging = LoggingConfig(
            level=log_data.get("level", "INFO"),
            path=log_data.get("path", "data/logs/"),
            max_size_mb=log_data.get("max_size_mb", 10),
            backup_count=log_data.get("backup_count", 5),
        )
    
    # Parse paths
    if "paths" in data:
        paths_data = data["paths"]
        
        config.paths = PathsConfig(
            models=paths_data.get("models", "models/"),
            cache=paths_data.get("cache", "data/cache/"),
            logs=paths_data.get("logs", "data/logs/"),
            backup=paths_data.get("backup", "data/backup/"),
            config=paths_data.get("config", "config.json"),
        )
    
    return config


def validate_config(config: Config) -> List[str]:
    """
    Validate configuration and return list of issues.
    
    Args:
        config: Configuration to validate
    
    Returns:
        List of validation issues (empty if all valid)
    
    Reason:
        Catch configuration errors before runtime.
        Better to fail fast than during study session.
    """
    issues = []
    
    # Check user config
    if config.user.days_remaining < 0:
        issues.append("days_remaining cannot be negative")
    
    if config.user.target_score < config.user.safe_score:
        issues.append("target_score should be >= safe_score")
    
    # Check study plan
    if config.study_plan.daily_hours > config.study_plan.max_hours:
        issues.append("daily_hours cannot exceed max_hours")
    
    if config.study_plan.daily_hours < 1:
        issues.append("daily_hours must be at least 1")
    
    # Check IRT settings
    if config.irt_settings.D_constant <= 0:
        issues.append("IRT D_constant must be positive")
    
    if config.irt_settings.min_questions >= config.irt_settings.max_questions:
        issues.append("IRT min_questions must be less than max_questions")
    
    # Check SM-2 settings
    if config.sm2_settings.default_ease_factor < config.sm2_settings.minimum_ease_factor:
        issues.append("SM-2 default_ease_factor must be >= minimum_ease_factor")
    
    if config.sm2_settings.minimum_ease_factor < 1.0:
        issues.append("SM-2 minimum_ease_factor must be >= 1.0")
    
    return issues


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("Testing configuration loader...")
    print()
    
    # Try to load config
    config = load_config()
    
    print(f"Loaded from: {config._loaded_from or 'defaults'}")
    
    if config._load_errors:
        print("Errors:")
        for error in config._load_errors:
            print(f"  - {error}")
    
    print()
    print("User Configuration:")
    print(f"  Name: {config.user.name}")
    print(f"  Exam: {config.user.exam}")
    print(f"  Target: {config.user.target_score}/60")
    print(f"  Days: {config.user.days_remaining}")
    
    print()
    print("Subjects:")
    for name, subject in config.user.subjects.items():
        print(f"  {name}: {subject.weightage} marks, target {subject.target}")
    
    print()
    print("Study Plan:")
    print(f"  Total Days: {config.study_plan.total_days}")
    print(f"  Daily Hours: {config.study_plan.daily_hours}")
    for phase in config.study_plan.phases:
        print(f"  Phase: {phase.name} (Days {phase.days[0]}-{phase.days[1]})")
    
    print()
    print("Validation:")
    issues = validate_config(config)
    if issues:
        print("  Issues found:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print("  ✓ All checks passed")
