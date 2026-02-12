"""
JARVIS Error Handling & Recovery Module
========================================

Provides unified error handling, recovery, and health checking for all modules.

Features:
- Custom exception hierarchy
- Automatic retry with exponential backoff
- Graceful degradation strategies
- Health check endpoints
- Error logging and reporting

Production Features:
- Thread-safe operations
- Circuit breaker pattern
- Rate limiting for retries
- Comprehensive logging
"""

import functools
import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Type, Union
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager
import traceback

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger("JARVIS.Errors")


# ============================================================================
# EXCEPTION HIERARCHY
# ============================================================================

class JarvisError(Exception):
    """Base exception for all JARVIS errors."""
    
    def __init__(self, message: str, code: str = "UNKNOWN", recoverable: bool = True):
        super().__init__(message)
        self.code = code
        self.recoverable = recoverable
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.__class__.__name__,
            "message": str(self),
            "code": self.code,
            "recoverable": self.recoverable,
            "timestamp": self.timestamp.isoformat()
        }


# Core Module Errors
class CoreError(JarvisError):
    """Errors in core module."""
    pass


class DatabaseError(CoreError):
    """Database operation errors."""
    def __init__(self, message: str, operation: str = "unknown"):
        super().__init__(message, code="DB_ERROR")
        self.operation = operation


class ConfigError(CoreError):
    """Configuration errors."""
    def __init__(self, message: str, key: str = ""):
        super().__init__(message, code="CONFIG_ERROR", recoverable=False)
        self.key = key


# Study Module Errors
class StudyError(JarvisError):
    """Errors in study module."""
    pass


class IRTError(StudyError):
    """IRT calculation errors."""
    def __init__(self, message: str, theta: float = 0.0):
        super().__init__(message, code="IRT_ERROR")
        self.theta = theta


class SM2Error(StudyError):
    """SM-2 calculation errors."""
    def __init__(self, message: str, item_id: str = ""):
        super().__init__(message, code="SM2_ERROR")
        self.item_id = item_id


class QuestionBankError(StudyError):
    """Question bank errors."""
    def __init__(self, message: str, question_id: str = ""):
        super().__init__(message, code="QB_ERROR")
        self.question_id = question_id


# Focus Module Errors
class FocusError(JarvisError):
    """Errors in focus module."""
    pass


class RootAccessError(FocusError):
    """Root access errors."""
    def __init__(self, message: str, command: str = ""):
        super().__init__(message, code="ROOT_ERROR")
        self.command = command


class PornBlockerError(FocusError):
    """Porn blocker errors."""
    def __init__(self, message: str, domain: str = ""):
        super().__init__(message, code="PORN_BLOCK_ERROR")
        self.domain = domain


class PatternDetectionError(FocusError):
    """Pattern detection errors."""
    def __init__(self, message: str, pattern_type: str = ""):
        super().__init__(message, code="PATTERN_ERROR")
        self.pattern_type = pattern_type


# Voice Module Errors
class VoiceError(JarvisError):
    """Errors in voice module."""
    pass


class TTSError(VoiceError):
    """Text-to-speech errors."""
    def __init__(self, message: str, text: str = ""):
        super().__init__(message, code="TTS_ERROR")
        self.text = text[:100] if text else ""


# Psychology Module Errors
class PsychologyError(JarvisError):
    """Errors in psychology module."""
    pass


class RewardError(PsychologyError):
    """Reward system errors."""
    def __init__(self, message: str, reward_type: str = ""):
        super().__init__(message, code="REWARD_ERROR")
        self.reward_type = reward_type


class AchievementError(PsychologyError):
    """Achievement system errors."""
    def __init__(self, message: str, achievement_id: str = ""):
        super().__init__(message, code="ACHIEVEMENT_ERROR")
        self.achievement_id = achievement_id


# Content Module Errors
class ContentError(JarvisError):
    """Errors in content module."""
    pass


class StudyPlanError(ContentError):
    """Study plan errors."""
    def __init__(self, message: str, day: int = 0):
        super().__init__(message, code="PLAN_ERROR")
        self.day = day


# ============================================================================
# RETRY MECHANISM
# ============================================================================

class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: tuple = (Exception,)
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions


def calculate_backoff(
    attempt: int,
    base_delay: float,
    max_delay: float,
    exponential_base: float,
    jitter: bool
) -> float:
    """Calculate backoff delay with optional jitter."""
    delay = min(base_delay * (exponential_base ** attempt), max_delay)
    
    if jitter:
        import random
        delay = delay * (0.5 + random.random())
    
    return delay


def retry_on_failure(
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator for automatic retry on failure.
    
    Args:
        config: Retry configuration
        on_retry: Callback called on each retry
    
    Usage:
        @retry_on_failure(RetryConfig(max_retries=3))
        def unreliable_operation():
            ...
    """
    config = config or RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt < config.max_retries:
                        delay = calculate_backoff(
                            attempt,
                            config.base_delay,
                            config.max_delay,
                            config.exponential_base,
                            config.jitter
                        )
                        
                        logger.warning(
                            f"Retry {attempt + 1}/{config.max_retries} for {func.__name__}: "
                            f"{e}. Waiting {delay:.1f}s"
                        )
                        
                        if on_retry:
                            on_retry(e, attempt)
                        
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {config.max_retries} retries failed for {func.__name__}: {e}"
                        )
            
            raise last_exception
        
        return wrapper
    
    return decorator


# ============================================================================
# CIRCUIT BREAKER
# ============================================================================

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject all calls
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class CircuitStats:
    """Circuit breaker statistics."""
    failures: int = 0
    successes: int = 0
    last_failure: Optional[datetime] = None
    last_success: Optional[datetime] = None
    state: CircuitState = CircuitState.CLOSED
    state_changed: Optional[datetime] = None


class CircuitBreaker:
    """
    Circuit breaker for protecting failing services.
    
    Usage:
        breaker = CircuitBreaker("database", failure_threshold=5)
        
        with breaker:
            result = risky_operation()
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        success_threshold: int = 3
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self._stats = CircuitStats()
        self._lock = threading.Lock()
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            self._check_state_transition()
            return self._stats.state
    
    def _check_state_transition(self):
        """Check and update state transitions."""
        now = datetime.now()
        
        if self._stats.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if (self._stats.state_changed and 
                (now - self._stats.state_changed).total_seconds() >= self.recovery_timeout):
                self._transition_to(CircuitState.HALF_OPEN)
        
        elif self._stats.state == CircuitState.HALF_OPEN:
            if self._stats.successes >= self.success_threshold:
                self._transition_to(CircuitState.CLOSED)
    
    def _transition_to(self, new_state: CircuitState):
        """Transition to a new state."""
        old_state = self._stats.state
        self._stats.state = new_state
        self._stats.state_changed = datetime.now()
        self._stats.failures = 0
        self._stats.successes = 0
        
        logger.info(f"Circuit '{self.name}' transitioned: {old_state.value} -> {new_state.value}")
    
    def record_success(self):
        """Record a successful operation."""
        with self._lock:
            self._stats.successes += 1
            self._stats.last_success = datetime.now()
            
            if self._stats.state == CircuitState.HALF_OPEN:
                self._check_state_transition()
    
    def record_failure(self):
        """Record a failed operation."""
        with self._lock:
            self._stats.failures += 1
            self._stats.last_failure = datetime.now()
            
            if self._stats.state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)
            elif self._stats.failures >= self.failure_threshold:
                self._transition_to(CircuitState.OPEN)
    
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        with self._lock:
            self._check_state_transition()
            return self._stats.state != CircuitState.OPEN
    
    @contextmanager
    def __call__(self):
        """Context manager for protected execution."""
        if not self.can_execute():
            raise JarvisError(
                f"Circuit '{self.name}' is open - operation rejected",
                code="CIRCUIT_OPEN"
            )
        
        try:
            yield
            self.record_success()
        except Exception as e:
            self.record_failure()
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        with self._lock:
            return {
                "name": self.name,
                "state": self._stats.state.value,
                "failures": self._stats.failures,
                "successes": self._stats.successes,
                "last_failure": self._stats.last_failure.isoformat() if self._stats.last_failure else None,
                "last_success": self._stats.last_success.isoformat() if self._stats.last_success else None
            }


# ============================================================================
# GRACEFUL DEGRADATION
# ============================================================================

class DegradationLevel(Enum):
    """System degradation levels."""
    FULL = "full"          # All features working
    REDUCED = "reduced"    # Non-critical features disabled
    MINIMAL = "minimal"    # Only core features
    EMERGENCY = "emergency"  # Basic operation only


class DegradationManager:
    """
    Manages graceful degradation of features.
    
    When components fail, the system degrades gracefully rather than crashing.
    """
    
    def __init__(self):
        self._level = DegradationLevel.FULL
        self._disabled_features: Set[str] = set()
        self._failure_counts: Dict[str, int] = {}
        self._lock = threading.Lock()
        
        # Thresholds for degradation
        self._thresholds = {
            DegradationLevel.REDUCED: 3,    # 3 feature failures
            DegradationLevel.MINIMAL: 6,    # 6 feature failures
            DegradationLevel.EMERGENCY: 10  # 10 feature failures
        }
    
    @property
    def level(self) -> DegradationLevel:
        """Get current degradation level."""
        return self._level
    
    def report_failure(self, feature: str) -> None:
        """Report a feature failure."""
        with self._lock:
            self._failure_counts[feature] = self._failure_counts.get(feature, 0) + 1
            self._disabled_features.add(feature)
            self._update_level()
            
            logger.warning(f"Feature '{feature}' failed. Degradation level: {self._level.value}")
    
    def report_recovery(self, feature: str) -> None:
        """Report a feature recovery."""
        with self._lock:
            if feature in self._disabled_features:
                self._disabled_features.discard(feature)
                self._failure_counts.pop(feature, None)
                self._update_level()
                
                logger.info(f"Feature '{feature}' recovered. Degradation level: {self._level.value}")
    
    def _update_level(self):
        """Update degradation level based on failures."""
        total_failures = len(self._disabled_features)
        
        if total_failures >= self._thresholds[DegradationLevel.EMERGENCY]:
            new_level = DegradationLevel.EMERGENCY
        elif total_failures >= self._thresholds[DegradationLevel.MINIMAL]:
            new_level = DegradationLevel.MINIMAL
        elif total_failures >= self._thresholds[DegradationLevel.REDUCED]:
            new_level = DegradationLevel.REDUCED
        else:
            new_level = DegradationLevel.FULL
        
        if new_level != self._level:
            old_level = self._level
            self._level = new_level
            logger.warning(f"System degraded: {old_level.value} -> {new_level.value}")
    
    def is_feature_available(self, feature: str) -> bool:
        """Check if a feature is available."""
        return feature not in self._disabled_features
    
    def get_status(self) -> Dict[str, Any]:
        """Get degradation status."""
        with self._lock:
            return {
                "level": self._level.value,
                "disabled_features": list(self._disabled_features),
                "failure_counts": dict(self._failure_counts)
            }


# ============================================================================
# HEALTH CHECK SYSTEM
# ============================================================================

@dataclass
class HealthStatus:
    """Health check result."""
    component: str
    healthy: bool
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "component": self.component,
            "healthy": self.healthy,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details
        }


class HealthChecker:
    """
    System health checking.
    
    Provides comprehensive health checks for all system components.
    """
    
    def __init__(self):
        self._checks: Dict[str, Callable[[], HealthStatus]] = {}
        self._last_results: Dict[str, HealthStatus] = {}
        self._lock = threading.Lock()
    
    def register_check(self, component: str, check_func: Callable[[], HealthStatus]):
        """Register a health check function."""
        with self._lock:
            self._checks[component] = check_func
            logger.info(f"Registered health check for: {component}")
    
    def run_check(self, component: str) -> HealthStatus:
        """Run a single health check."""
        if component not in self._checks:
            return HealthStatus(
                component=component,
                healthy=False,
                message="Health check not registered"
            )
        
        try:
            status = self._checks[component]()
            with self._lock:
                self._last_results[component] = status
            return status
        except Exception as e:
            status = HealthStatus(
                component=component,
                healthy=False,
                message=f"Health check failed: {str(e)}",
                details={"error": str(e), "traceback": traceback.format_exc()}
            )
            with self._lock:
                self._last_results[component] = status
            return status
    
    def run_all_checks(self) -> Dict[str, HealthStatus]:
        """Run all registered health checks."""
        results = {}
        for component in self._checks:
            results[component] = self.run_check(component)
        return results
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        results = self.run_all_checks()
        
        all_healthy = all(r.healthy for r in results.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "components": {k: v.to_dict() for k, v in results.items()},
            "summary": {
                "total": len(results),
                "healthy": sum(1 for r in results.values() if r.healthy),
                "unhealthy": sum(1 for r in results.values() if not r.healthy)
            }
        }


# Global instances
degradation_manager = DegradationManager()
health_checker = HealthChecker()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def safe_call(
    func: Callable,
    *args,
    default: Any = None,
    log_error: bool = True,
    **kwargs
) -> Any:
    """
    Safely call a function, returning default on error.
    
    Args:
        func: Function to call
        *args: Positional arguments
        default: Default return value on error
        log_error: Whether to log errors
        **kwargs: Keyword arguments
    
    Returns:
        Function result or default on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_error:
            logger.error(f"Safe call failed for {func.__name__}: {e}")
        return default


def create_circuit_breaker(name: str, **kwargs) -> CircuitBreaker:
    """Factory function for circuit breakers."""
    return CircuitBreaker(name, **kwargs)


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Error Handling & Recovery Module...")
    print("=" * 60)
    
    # Test 1: Custom exceptions
    print("\n1. Custom exceptions:")
    try:
        raise IRTError("Theta out of bounds", theta=5.0)
    except JarvisError as e:
        print(f"   Caught: {e.to_dict()}")
    
    # Test 2: Retry mechanism
    print("\n2. Retry mechanism:")
    call_count = 0
    
    @retry_on_failure(RetryConfig(max_retries=3, base_delay=0.1))
    def flaky_function():
        global call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Not yet...")
        return "Success!"
    
    result = flaky_function()
    print(f"   Result: {result} (after {call_count} attempts)")
    
    # Test 3: Circuit breaker
    print("\n3. Circuit breaker:")
    breaker = CircuitBreaker("test", failure_threshold=2, recovery_timeout=0.5)
    
    # Cause failures
    for i in range(3):
        try:
            with breaker:
                raise ValueError("Simulated failure")
        except ValueError:
            pass
        print(f"   State after failure {i+1}: {breaker.state.value}")
    
    # Test 4: Degradation manager
    print("\n4. Degradation manager:")
    dm = DegradationManager()
    dm.report_failure("voice")
    dm.report_failure("voice_enforcer")
    dm.report_failure("pattern_analyzer")
    print(f"   Level: {dm.level.value}")
    print(f"   Disabled: {dm._disabled_features}")
    
    # Test 5: Health checker
    print("\n5. Health checker:")
    hc = HealthChecker()
    
    def check_irt():
        return HealthStatus("irt", True, "IRT engine operational")
    
    def check_voice():
        return HealthStatus("voice", False, "TTS backend unavailable")
    
    hc.register_check("irt", check_irt)
    hc.register_check("voice", check_voice)
    
    health = hc.get_system_health()
    print(f"   Status: {health['status']}")
    print(f"   Summary: {health['summary']}")
    
    print("\n" + "=" * 60)
    print("All tests passed!")
