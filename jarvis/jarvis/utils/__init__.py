"""
JARVIS Utils Module
===================

Utility functions and error handling for JARVIS.
"""

from .time_utils import get_time_greeting, calculate_days_remaining, get_current_phase, get_phase_name
from .validation import validate_email, validate_phone, sanitize_input
from .formatting import format_duration, format_number, format_percentage
from .file_utils import ensure_directory, safe_write_file, safe_read_file
from .error_handling import (
    JarvisError,
    CoreError,
    DatabaseError,
    ConfigError,
    StudyError,
    IRTError,
    SM2Error,
    QuestionBankError,
    FocusError,
    RootAccessError,
    PornBlockerError,
    VoiceError,
    TTSError,
    PsychologyError,
    ContentError,
    RetryConfig,
    retry_on_failure,
    CircuitBreaker,
    CircuitState,
    DegradationManager,
    DegradationLevel,
    HealthChecker,
    HealthStatus,
    safe_call,
    degradation_manager,
    health_checker,
)

__all__ = [
    # Time utilities
    "get_time_greeting",
    "calculate_days_remaining",
    "get_current_phase",
    "get_phase_name",
    
    # Validation
    "validate_email",
    "validate_phone",
    "sanitize_input",
    
    # Formatting
    "format_duration",
    "format_number",
    "format_percentage",
    
    # File utilities
    "ensure_directory",
    "safe_write_file",
    "safe_read_file",
    
    # Exceptions
    "JarvisError",
    "CoreError",
    "DatabaseError",
    "ConfigError",
    "StudyError",
    "IRTError",
    "SM2Error",
    "QuestionBankError",
    "FocusError",
    "RootAccessError",
    "PornBlockerError",
    "VoiceError",
    "TTSError",
    "PsychologyError",
    "ContentError",
    
    # Retry mechanism
    "RetryConfig",
    "retry_on_failure",
    
    # Circuit breaker
    "CircuitBreaker",
    "CircuitState",
    
    # Degradation
    "DegradationManager",
    "DegradationLevel",
    
    # Health check
    "HealthChecker",
    "HealthStatus",
    
    # Utilities
    "safe_call",
    "degradation_manager",
    "health_checker",
]
