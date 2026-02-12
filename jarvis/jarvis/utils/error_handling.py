"""
JARVIS Error Handling Module
============================

Purpose: Centralized error handling and recovery for JARVIS.

Features:
    - Custom exception hierarchy
    - Error logging and tracking
    - Graceful degradation
    - Recovery strategies
    - Error statistics

EXAM IMPACT:
    CRITICAL. Without proper error handling, the system can crash
    during important study sessions.
"""

import logging
import traceback
import time
from datetime import datetime
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps

# Setup logger
logger = logging.getLogger('JARVIS.Errors')


# ============================================================================
# ERROR SEVERITY
# ============================================================================

class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"           # Minor issue, doesn't affect functionality
    MEDIUM = "medium"     # Affects some functionality
    HIGH = "high"         # Major functionality affected
    CRITICAL = "critical" # System unusable
    FATAL = "fatal"       # System crash


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class JarvisError(Exception):
    """Base exception for all JARVIS errors."""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 recovery_hint: str = None, context: Dict = None):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.recovery_hint = recovery_hint
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "severity": self.severity.value,
            "recovery_hint": self.recovery_hint,
            "context": self.context,
            "timestamp": self.timestamp.isoformat()
        }


class IRTEngineError(JarvisError):
    """Error in IRT calculations."""
    pass


class SM2EngineError(JarvisError):
    """Error in SM-2 calculations."""
    pass


class DatabaseError(JarvisError):
    """Error in database operations."""
    pass


class VoiceEngineError(JarvisError):
    """Error in voice system."""
    pass


class FocusMonitorError(JarvisError):
    """Error in focus monitoring."""
    pass


class PsychologyEngineError(JarvisError):
    """Error in psychological engine."""
    pass


class ConfigurationError(JarvisError):
    """Error in configuration."""
    pass


class ValidationError(JarvisError):
    """Error in input validation."""
    pass


class SessionError(JarvisError):
    """Error in study session."""
    pass


class QuestionBankError(JarvisError):
    """Error in question bank."""
    pass


# ============================================================================
# ERROR TRACKER
# ============================================================================

@dataclass
class ErrorRecord:
    """Record of an error occurrence."""
    error_type: str
    message: str
    severity: str
    traceback_str: str
    timestamp: datetime
    context: Dict = field(default_factory=dict)
    recovered: bool = False
    recovery_method: str = None


class ErrorTracker:
    """
    Tracks and analyzes errors in the system.
    
    Features:
        - Error history
        - Error frequency analysis
        - Recovery tracking
        - Statistics
    """
    
    def __init__(self, max_records: int = 1000):
        """
        Initialize error tracker.
        
        Args:
            max_records: Maximum number of errors to track
        """
        self.max_records = max_records
        self._errors: List[ErrorRecord] = []
        self._error_counts: Dict[str, int] = {}
        self._recovery_success: Dict[str, int] = {}
        self._recovery_failure: Dict[str, int] = {}
    
    def record_error(self, error: Exception, context: Dict = None,
                     recovered: bool = False, recovery_method: str = None) -> ErrorRecord:
        """
        Record an error occurrence.
        
        Args:
            error: The exception
            context: Additional context
            recovered: Whether recovery was successful
            recovery_method: Method used for recovery
        
        Returns:
            ErrorRecord
        """
        record = ErrorRecord(
            error_type=error.__class__.__name__,
            message=str(error),
            severity=getattr(error, 'severity', ErrorSeverity.MEDIUM).value,
            traceback_str=traceback.format_exc(),
            timestamp=datetime.now(),
            context=context or {},
            recovered=recovered,
            recovery_method=recovery_method
        )
        
        self._errors.append(record)
        
        # Update counts
        self._error_counts[record.error_type] = self._error_counts.get(record.error_type, 0) + 1
        
        if recovered:
            self._recovery_success[record.error_type] = self._recovery_success.get(record.error_type, 0) + 1
        else:
            self._recovery_failure[record.error_type] = self._recovery_failure.get(record.error_type, 0) + 1
        
        # Trim old records
        if len(self._errors) > self.max_records:
            self._errors = self._errors[-self.max_records:]
        
        return record
    
    def get_recent_errors(self, count: int = 10) -> List[ErrorRecord]:
        """Get most recent errors."""
        return self._errors[-count:]
    
    def get_error_frequency(self) -> Dict[str, int]:
        """Get error frequency by type."""
        return dict(self._error_counts)
    
    def get_recovery_rate(self) -> Dict[str, float]:
        """Get recovery success rate by error type."""
        rates = {}
        for error_type in self._error_counts:
            success = self._recovery_success.get(error_type, 0)
            failure = self._recovery_failure.get(error_type, 0)
            total = success + failure
            if total > 0:
                rates[error_type] = success / total
        return rates
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        return {
            "total_errors": len(self._errors),
            "error_types": len(self._error_counts),
            "error_frequency": self.get_error_frequency(),
            "recovery_rates": self.get_recovery_rate(),
            "recent_errors": [
                {
                    "type": e.error_type,
                    "message": e.message[:100],
                    "severity": e.severity,
                    "recovered": e.recovered
                }
                for e in self.get_recent_errors(5)
            ]
        }
    
    def clear(self) -> None:
        """Clear all error records."""
        self._errors.clear()
        self._error_counts.clear()
        self._recovery_success.clear()
        self._recovery_failure.clear()


# Global error tracker
_error_tracker = ErrorTracker()


def get_error_tracker() -> ErrorTracker:
    """Get the global error tracker."""
    return _error_tracker


# ============================================================================
# RECOVERY STRATEGIES
# ============================================================================

class RecoveryStrategy:
    """Base class for recovery strategies."""
    
    def can_recover(self, error: Exception) -> bool:
        """Check if this strategy can recover from the error."""
        raise NotImplementedError
    
    def recover(self, error: Exception, context: Dict = None) -> bool:
        """Attempt to recover from the error."""
        raise NotImplementedError


class DefaultValueRecovery(RecoveryStrategy):
    """Recovery by returning a default value."""
    
    def __init__(self, default_value: Any):
        self.default_value = default_value
    
    def can_recover(self, error: Exception) -> bool:
        return True
    
    def recover(self, error: Exception, context: Dict = None) -> bool:
        logger.info(f"Using default value for recovery: {self.default_value}")
        return True


class RetryRecovery(RecoveryStrategy):
    """Recovery by retrying the operation."""
    
    def __init__(self, max_retries: int = 3, delay: float = 0.1):
        self.max_retries = max_retries
        self.delay = delay
    
    def can_recover(self, error: Exception) -> bool:
        # Retry for transient errors
        transient_errors = (ConnectionError, TimeoutError, OSError)
        return isinstance(error, transient_errors)
    
    def recover(self, error: Exception, context: Dict = None) -> bool:
        func = context.get('function') if context else None
        args = context.get('args', ()) if context else ()
        kwargs = context.get('kwargs', {}) if context else {}
        
        if not func:
            return False
        
        for attempt in range(self.max_retries):
            try:
                time.sleep(self.delay * (attempt + 1))
                func(*args, **kwargs)
                return True
            except Exception as e:
                logger.warning(f"Retry {attempt + 1} failed: {e}")
        
        return False


# ============================================================================
# ERROR HANDLER DECORATOR
# ============================================================================

def handle_errors(default_return: Any = None, 
                  raise_on_error: bool = False,
                  log_errors: bool = True):
    """
    Decorator for handling errors in functions.
    
    Args:
        default_return: Value to return on error
        raise_on_error: Whether to re-raise the error
        log_errors: Whether to log errors
    
    Usage:
        @handle_errors(default_return=0)
        def risky_function():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"Error in {func.__name__}: {e}")
                
                _error_tracker.record_error(e, context={
                    "function": func.__name__,
                    "args": str(args)[:200],
                    "kwargs": str(kwargs)[:200]
                })
                
                if raise_on_error:
                    raise
                
                return default_return
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"Error in {func.__name__}: {e}")
                
                _error_tracker.record_error(e, context={
                    "function": func.__name__,
                    "args": str(args)[:200],
                    "kwargs": str(kwargs)[:200]
                })
                
                if raise_on_error:
                    raise
                
                return default_return
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator


# ============================================================================
# INPUT VALIDATION
# ============================================================================

class InputValidator:
    """Centralized input validation."""
    
    @staticmethod
    def validate_type(value: Any, expected_type: type, name: str = "value") -> Any:
        """Validate that value is of expected type."""
        if value is None:
            return None
        
        if not isinstance(value, expected_type):
            try:
                return expected_type(value)
            except (ValueError, TypeError):
                raise ValidationError(
                    f"{name} must be {expected_type.__name__}, got {type(value).__name__}",
                    severity=ErrorSeverity.LOW
                )
        return value
    
    @staticmethod
    def validate_range(value: float, min_val: float, max_val: float, 
                       name: str = "value") -> float:
        """Validate that value is within range."""
        if value is None:
            return min_val
        
        if not isinstance(value, (int, float)):
            raise ValidationError(
                f"{name} must be numeric",
                severity=ErrorSeverity.LOW
            )
        
        if value < min_val:
            logger.warning(f"{name} {value} below minimum, using {min_val}")
            return min_val
        if value > max_val:
            logger.warning(f"{name} {value} above maximum, using {max_val}")
            return max_val
        
        return value
    
    @staticmethod
    def validate_string(value: str, max_length: int = 1000, 
                        name: str = "value", allow_empty: bool = True) -> str:
        """Validate string input."""
        if value is None:
            return "" if allow_empty else None
        
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip()
        
        if not allow_empty and not value:
            raise ValidationError(
                f"{name} cannot be empty",
                severity=ErrorSeverity.LOW
            )
        
        if len(value) > max_length:
            logger.warning(f"{name} truncated to {max_length} characters")
            value = value[:max_length]
        
        return value
    
    @staticmethod
    def validate_list(value: List, min_length: int = 0, max_length: int = 1000,
                      name: str = "list") -> List:
        """Validate list input."""
        if value is None:
            return []
        
        if not isinstance(value, (list, tuple)):
            raise ValidationError(
                f"{name} must be a list",
                severity=ErrorSeverity.LOW
            )
        
        if len(value) < min_length:
            raise ValidationError(
                f"{name} must have at least {min_length} items",
                severity=ErrorSeverity.LOW
            )
        
        if len(value) > max_length:
            logger.warning(f"{name} truncated to {max_length} items")
            value = list(value[:max_length])
        
        return list(value)
    
    @staticmethod
    def validate_option(value: str, options: List[str], 
                        name: str = "value", case_sensitive: bool = False) -> str:
        """Validate that value is one of the allowed options."""
        if value is None:
            return options[0] if options else None
        
        check_value = value if case_sensitive else str(value).lower()
        check_options = options if case_sensitive else [o.lower() for o in options]
        
        if check_value not in check_options:
            logger.warning(f"{name} '{value}' not in options, using {options[0]}")
            return options[0]
        
        # Return original case version
        idx = check_options.index(check_value)
        return options[idx]


# ============================================================================
# GRACEFUL DEGRADATION
# ============================================================================

class GracefulDegradation:
    """
    Manages graceful degradation when features fail.
    
    Allows the system to continue with reduced functionality
    when non-critical features fail.
    """
    
    def __init__(self):
        self._feature_status: Dict[str, bool] = {}
        self._feature_fallbacks: Dict[str, Callable] = {}
    
    def register_feature(self, name: str, fallback: Callable = None) -> None:
        """
        Register a feature with optional fallback.
        
        Args:
            name: Feature name
            fallback: Fallback function when feature fails
        """
        self._feature_status[name] = True
        self._feature_fallbacks[name] = fallback
        logger.info(f"Registered feature: {name}")
    
    def disable_feature(self, name: str, reason: str = None) -> None:
        """
        Disable a feature.
        
        Args:
            name: Feature name
            reason: Reason for disabling
        """
        if name in self._feature_status:
            self._feature_status[name] = False
            logger.warning(f"Feature '{name}' disabled: {reason or 'Unknown reason'}")
    
    def enable_feature(self, name: str) -> None:
        """Re-enable a feature."""
        if name in self._feature_status:
            self._feature_status[name] = True
            logger.info(f"Feature '{name}' re-enabled")
    
    def is_available(self, name: str) -> bool:
        """Check if a feature is available."""
        return self._feature_status.get(name, False)
    
    def get_fallback(self, name: str) -> Optional[Callable]:
        """Get fallback for a disabled feature."""
        return self._feature_fallbacks.get(name)
    
    def execute_with_fallback(self, name: str, primary_func: Callable, 
                              *args, **kwargs) -> Any:
        """
        Execute a function with automatic fallback.
        
        Args:
            name: Feature name
            primary_func: Primary function to execute
            *args: Arguments
            **kwargs: Keyword arguments
        
        Returns:
            Result from primary or fallback
        """
        if not self.is_available(name):
            fallback = self.get_fallback(name)
            if fallback:
                logger.info(f"Using fallback for feature '{name}'")
                return fallback(*args, **kwargs)
            return None
        
        try:
            return primary_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Feature '{name}' failed: {e}")
            _error_tracker.record_error(e, context={"feature": name})
            
            self.disable_feature(name, str(e))
            
            fallback = self.get_fallback(name)
            if fallback:
                return fallback(*args, **kwargs)
            
            return None
    
    def get_status(self) -> Dict[str, bool]:
        """Get status of all features."""
        return dict(self._feature_status)


# Global degradation manager
_degradation_manager = GracefulDegradation()


def get_degradation_manager() -> GracefulDegradation:
    """Get the global degradation manager."""
    return _degradation_manager


# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_error_handling():
    """Initialize error handling system."""
    # Register default features
    _degradation_manager.register_feature("voice_engine")
    _degradation_manager.register_feature("focus_monitor")
    _degradation_manager.register_feature("psychology_engine")
    _degradation_manager.register_feature("ai_cache")
    
    logger.info("Error handling system initialized")


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing error handling module...")
    print()
    
    # Initialize
    initialize_error_handling()
    
    # Test error tracking
    tracker = get_error_tracker()
    
    try:
        raise IRTEngineError("Test IRT error", 
                            severity=ErrorSeverity.HIGH,
                            recovery_hint="Check theta bounds")
    except Exception as e:
        tracker.record_error(e, recovered=True, recovery_method="default_value")
    
    # Test validation
    validator = InputValidator()
    
    # Range validation
    result = validator.validate_range(5.0, 0.0, 3.0, "theta")
    print(f"Validated theta: {result}")
    
    # String validation
    result = validator.validate_string("  test  ", max_length=3)
    print(f"Validated string: '{result}'")
    
    # Option validation
    result = validator.validate_option("MATHS", ["maths", "physics", "chemistry"])
    print(f"Validated option: {result}")
    
    # Test decorator
    @handle_errors(default_return=-1)
    def risky_function(x):
        return 10 / x
    
    print(f"risky_function(2) = {risky_function(2)}")
    print(f"risky_function(0) = {risky_function(0)}")  # Should return -1
    
    # Get stats
    stats = tracker.get_stats()
    print(f"\nError stats: {stats}")
    
    # Get degradation status
    degradation = get_degradation_manager()
    print(f"\nFeature status: {degradation.get_status()}")
    
    print("\nAll tests passed!")
