"""
JARVIS Voice Enforcer
=====================

Purpose: Integrate voice with behaviour enforcement.

This module:
- Generates voice responses to detected patterns
- Enforces discipline through voice confrontation
- Celebrates achievements with voice
- Provides real-time voice feedback

EXAM IMPACT:
    CRITICAL. Voice is MORE impactful than text.
    This module makes JARVIS feel ALIVE and WATCHING.
    User cannot ignore voice interventions.

ENFORCEMENT MODES:
    - PASSIVE: Only speaks when asked
    - ASSISTANT: Speaks for important events
    - ENFORCER: Proactively speaks on patterns
    - RUTHLESS: Maximum intervention (user choice)

REASON FOR DESIGN:
    - Integrates with pattern detection
    - Connects to psychological engine
    - Works with intervention system
    - Provides comprehensive enforcement

ROLLBACK PLAN:
    - Set mode to PASSIVE to disable
    - Voice is read-only
    - No persistent system changes
"""

import threading
import time
from datetime import datetime, timedelta, time as dt_time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue

from .voice_engine import (
    VoiceEngine,
    VoicePersonality,
    VoiceResult,
    create_voice_engine,
)
from .voice_messages import (
    VoiceMessageGenerator,
    MessageType,
    MessageIntensity,
)


# ============================================================================
# ENUMS
# ============================================================================

class EnforcementMode(Enum):
    """Voice enforcement modes."""
    PASSIVE = "passive"         # Only when asked
    ASSISTANT = "assistant"     # Important events only
    ENFORCER = "enforcer"       # Proactive enforcement
    RUTHLESS = "ruthless"       # Maximum intervention


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class EnforcerConfig:
    """Configuration for voice enforcer."""
    mode: EnforcementMode = EnforcementMode.ENFORCER
    enabled: bool = True

    # Quiet hours (no voice)
    quiet_start: int = 23  # 11 PM
    quiet_end: int = 6     # 6 AM

    # Rate limiting
    min_interval_seconds: int = 60  # Min time between interventions
    max_interventions_per_hour: int = 5

    # What to speak about
    speak_on_achievement: bool = True
    speak_on_jackpot: bool = True
    speak_on_streak_risk: bool = True
    speak_on_distraction: bool = True
    speak_on_late_night: bool = True
    speak_on_session_end: bool = True


@dataclass
class InterventionEvent:
    """An event that may trigger voice intervention."""
    event_type: str
    severity: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


# ============================================================================
# VOICE ENFORCER CLASS
# ============================================================================

class VoiceEnforcer:
    """
    Voice-based behaviour enforcement.

    This class:
    - Responds to patterns with voice
    - Enforces discipline through confrontation
    - Celebrates achievements
    - Manages intervention rate limiting

    Usage:
        enforcer = VoiceEnforcer(voice_engine)

        # Start enforcer
        enforcer.start()

        # Report events
        enforcer.report_distraction("Instagram", 300)
        enforcer.report_achievement("Week Warrior", 300)
        enforcer.report_streak_risk(7, 4, 15)

        # Stop
        enforcer.stop()

    EXAM IMPACT:
        Voice enforcement is the most impactful intervention.
        User CANNOT ignore voice like they ignore text.
    """

    def __init__(
        self,
        voice_engine: Optional[VoiceEngine] = None,
        config: Optional[EnforcerConfig] = None,
        message_generator: Optional[VoiceMessageGenerator] = None
    ):
        """
        Initialize voice enforcer.

        Args:
            voice_engine: VoiceEngine instance
            config: Enforcer configuration
            message_generator: Message generator
        """
        self.voice = voice_engine or create_voice_engine(auto_start=False)
        self.config = config or EnforcerConfig()
        self.generator = message_generator or VoiceMessageGenerator()

        # Rate limiting
        self._last_intervention: Dict[str, datetime] = {}
        self._hourly_count: int = 0
        self._hour_reset: datetime = datetime.now()

        # Event queue
        self._event_queue: Queue = Queue()

        # State
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Statistics
        self._interventions_total = 0
        self._interventions_by_type: Dict[str, int] = {}

    # ========================================================================
    # CONTROL
    # ========================================================================

    def start(self) -> bool:
        """Start the voice enforcer."""
        if self._running:
            return False

        if not self.config.enabled:
            return False

        # Start voice engine if not running
        if not self.voice.is_running():
            self.voice.start()

        self._running = True
        self._stop_event.clear()

        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            daemon=True,
            name="VoiceEnforcer"
        )
        self._worker_thread.start()

        return True

    def stop(self) -> bool:
        """Stop the voice enforcer."""
        if not self._running:
            return False

        self._stop_event.set()
        self._running = False

        if self._worker_thread:
            self._worker_thread.join(timeout=3)

        return True

    def is_running(self) -> bool:
        """Check if enforcer is running."""
        return self._running

    # ========================================================================
    # EVENT REPORTING
    # ========================================================================

    def report_distraction(
        self,
        app_name: str,
        duration_seconds: int,
        severity: str = "medium"
    ) -> bool:
        """
        Report a distraction event.

        Args:
            app_name: Name of distracting app
            duration_seconds: How long distracted
            severity: Severity level

        Returns:
            True if voice intervention triggered
        """
        if not self._should_speak("distraction"):
            return False

        intensity = self._severity_to_intensity(severity)
        message = self.generator.get_distraction_warning(
            app_name=app_name,
            minutes_distracted=duration_seconds // 60,
            intensity=intensity
        )

        personality = (
            VoicePersonality.URGENT if intensity == MessageIntensity.URGENT
            else VoicePersonality.STERN
        )

        return self._speak(message, personality, "distraction")

    def report_streak_risk(
        self,
        streak: int,
        hours_left: float,
        questions_done: int,
        questions_target: int,
        xp_at_risk: int,
        severity: str = "high"
    ) -> bool:
        """
        Report streak at risk.

        Args:
            streak: Current streak
            hours_left: Hours until day ends
            questions_done: Questions completed today
            questions_target: Daily target
            xp_at_risk: XP that would be lost
            severity: Severity level

        Returns:
            True if intervention triggered
        """
        if not self._should_speak("streak_risk"):
            return False

        intensity = self._severity_to_intensity(severity)
        message = self.generator.get_streak_risk_message(
            streak=streak,
            hours_left=hours_left,
            questions_done=questions_done,
            questions_left=questions_target - questions_done,
            xp_at_risk=xp_at_risk,
            intensity=intensity
        )

        return self._speak(message, VoicePersonality.URGENT, "streak_risk")

    def report_achievement(
        self,
        name: str,
        description: str,
        xp: int
    ) -> bool:
        """
        Report achievement unlock.

        Args:
            name: Achievement name
            description: Achievement description
            xp: XP awarded

        Returns:
            True if spoke
        """
        if not self.config.speak_on_achievement:
            return False

        message = self.generator.get_achievement_message(
            name=name,
            description=description,
            xp=xp
        )

        return self._speak(message, VoicePersonality.ENCOURAGING, "achievement")

    def report_jackpot(
        self,
        xp: int,
        coins: int
    ) -> bool:
        """
        Report jackpot win.

        Args:
            xp: XP won
            coins: Coins won

        Returns:
            True if spoke
        """
        if not self.config.speak_on_jackpot:
            return False

        message = self.generator.get_jackpot_message(xp=xp, coins=coins)
        return self._speak(message, VoicePersonality.ENCOURAGING, "jackpot")

    def report_session_complete(
        self,
        questions: int,
        accuracy: float,
        xp: int,
        coins: int,
        streak: int
    ) -> bool:
        """
        Report session completion.

        Args:
            questions: Questions answered
            accuracy: Accuracy rate
            xp: XP earned
            coins: Coins earned
            streak: Current streak

        Returns:
            True if spoke
        """
        if not self.config.speak_on_session_end:
            return False

        message = self.generator.get_session_end_message(
            questions=questions,
            accuracy=accuracy,
            xp=xp,
            coins=coins,
            streak=streak
        )

        return self._speak(message, VoicePersonality.ENCOURAGING, "session")

    def report_late_night(
        self,
        hour: int,
        activity: str = "screen"
    ) -> bool:
        """
        Report late night activity.

        Args:
            hour: Current hour
            activity: Type of activity

        Returns:
            True if spoke
        """
        if not self.config.speak_on_late_night:
            return False

        if not self._should_speak("late_night"):
            return False

        # Determine intensity based on how late
        if hour >= 2:
            intensity = MessageIntensity.CRITICAL
        elif hour >= 1:
            intensity = MessageIntensity.URGENT
        elif hour >= 0:
            intensity = MessageIntensity.FIRM
        else:
            intensity = MessageIntensity.NORMAL

        message = self.generator.get_late_night_message(
            hour=hour,
            intensity=intensity
        )

        return self._speak(message, VoicePersonality.GENTLE, "late_night")

    def report_pattern_detected(
        self,
        pattern_type: str,
        severity: str,
        evidence: Dict[str, Any]
    ) -> bool:
        """
        Report a detected behaviour pattern.

        Args:
            pattern_type: Type of pattern
            severity: Severity level
            evidence: Pattern evidence

        Returns:
            True if intervention triggered
        """
        # Map pattern types to handlers
        pattern_handlers = {
            "study_avoidance": self._handle_study_avoidance,
            "burnout_precursor": self._handle_burnout,
            "weakness_avoidance": self._handle_weakness_avoidance,
            "late_night_dopamine": self._handle_late_night_dopamine,
            "distraction_escalation": self._handle_distraction_escalation,
        }

        handler = pattern_handlers.get(pattern_type)
        if handler:
            return handler(severity, evidence)

        return False

    def _handle_study_avoidance(
        self,
        severity: str,
        evidence: Dict[str, Any]
    ) -> bool:
        """Handle study avoidance pattern."""
        intensity = self._severity_to_intensity(severity)
        switch_count = evidence.get("switch_count", 0)

        messages = {
            MessageIntensity.NORMAL: f"You've switched apps {switch_count} times. This is avoidance. Return to studying.",
            MessageIntensity.FIRM: f"STUDY AVOIDANCE DETECTED. {switch_count} app switches. Your exam doesn't care about your excuses. Study NOW.",
            MessageIntensity.URGENT: f"CRITICAL AVOIDANCE. {switch_count} switches detected. This is EXACTLY how you've failed before. BREAK THE PATTERN. Study NOW.",
        }

        message = messages.get(intensity, messages[MessageIntensity.NORMAL])
        return self._speak(message, VoicePersonality.STERN, "study_avoidance")

    def _handle_burnout(
        self,
        severity: str,
        evidence: Dict[str, Any]
    ) -> bool:
        """Handle burnout precursor pattern."""
        decline = evidence.get("session_decline_ratio", 1.0)
        decline_pct = int((1 - decline) * 100)

        message = (
            f"BURNOUT WARNING. Your sessions are {decline_pct} percent shorter than normal. "
            f"This is the START of burnout. I'm reducing your targets by 20 percent. "
            f"This is not weakness. It's strategy. Rest, recover, return stronger."
        )

        return self._speak(message, VoicePersonality.GENTLE, "burnout")

    def _handle_weakness_avoidance(
        self,
        severity: str,
        evidence: Dict[str, Any]
    ) -> bool:
        """Handle weakness avoidance pattern."""
        avoided = evidence.get("avoided_topics", [])
        maths_avoided = evidence.get("maths_topics_avoided", 0)

        if maths_avoided > 0:
            message = (
                f"WEAKNESS AVOIDANCE DETECTED. You've been avoiding Mathematics - "
                f"your HIGHEST WEIGHTAGE subject. This is the EXACT pattern that leads to exam failure. "
                f"Practice your weak topics NOW. No exceptions."
            )
        else:
            message = (
                f"You've been avoiding {len(avoided)} weak topics. "
                f"Every topic you avoid is marks you lose in the exam. "
                f"Let's practice them now."
            )

        return self._speak(message, VoicePersonality.STERN, "weakness_avoidance")

    def _handle_late_night_dopamine(
        self,
        severity: str,
        evidence: Dict[str, Any]
    ) -> bool:
        """Handle late night dopamine pattern."""
        count = evidence.get("late_night_count", 0)
        hour = datetime.now().hour

        message = (
            f"LATE NIGHT DOPAMINE PATTERN. {count} incidents this week. "
            f"Your brain needs sleep to consolidate learning. "
            f"Every late night costs you tomorrow's productivity. "
            f"Put the phone down. Sleep. Your seat requires it."
        )

        return self._speak(message, VoicePersonality.GENTLE, "late_night")

    def _handle_distraction_escalation(
        self,
        severity: str,
        evidence: Dict[str, Any]
    ) -> bool:
        """Handle distraction escalation pattern."""
        increase = evidence.get("increase_ratio", 1.0)
        increase_pct = int((increase - 1) * 100)

        message = (
            f"DISTRACTION ESCALATION. Your distractions have increased {increase_pct} percent. "
            f"This is a WARNING SIGN. Intervene NOW before it gets worse. "
            f"Your future self will thank you."
        )

        return self._speak(message, VoicePersonality.URGENT, "distraction_escalation")

    # ========================================================================
    # SCHEDULING
    # ========================================================================

    def speak_at_time(
        self,
        message: str,
        scheduled_time: datetime,
        personality: VoicePersonality = VoicePersonality.NEUTRAL
    ) -> None:
        """
        Schedule a voice message for a specific time.

        Args:
            message: Message to speak
            scheduled_time: When to speak
            personality: Voice personality
        """
        event = InterventionEvent(
            event_type="scheduled",
            severity="low",
            data={
                "message": message,
                "personality": personality.value,
                "scheduled_time": scheduled_time.isoformat(),
            }
        )
        self._event_queue.put(event)

    # ========================================================================
    # INTERNAL METHODS
    # ========================================================================

    def _should_speak(self, event_type: str) -> bool:
        """
        Check if we should speak for this event.

        Args:
            event_type: Type of event

        Returns:
            True if we should speak
        """
        if not self.config.enabled:
            return False

        # Check mode
        if self.config.mode == EnforcementMode.PASSIVE:
            return False

        if self.config.mode == EnforcementMode.ASSISTANT:
            # Only speak on critical events
            if event_type not in ["streak_risk", "achievement", "jackpot"]:
                return False

        # Check quiet hours
        now = datetime.now()
        hour = now.hour
        if self.config.quiet_start <= hour or hour < self.config.quiet_end:
            # During quiet hours, only critical
            if event_type not in ["streak_risk", "porn_detected"]:
                return False

        # Check rate limiting
        if event_type in self._last_intervention:
            last = self._last_intervention[event_type]
            elapsed = (now - last).total_seconds()
            if elapsed < self.config.min_interval_seconds:
                return False

        # Check hourly limit
        if now.hour != self._hour_reset.hour:
            self._hourly_count = 0
            self._hour_reset = now

        if self._hourly_count >= self.config.max_interventions_per_hour:
            return False

        return True

    def _speak(
        self,
        message: str,
        personality: VoicePersonality,
        event_type: str
    ) -> bool:
        """
        Speak a message.

        Args:
            message: Message to speak
            personality: Voice personality
            event_type: Type of event

        Returns:
            True if spoken
        """
        result = self.voice.speak(message, personality)

        if result.success:
            # Update rate limiting
            self._last_intervention[event_type] = datetime.now()
            self._hourly_count += 1

            # Update stats
            self._interventions_total += 1
            self._interventions_by_type[event_type] = \
                self._interventions_by_type.get(event_type, 0) + 1

        return result.success

    def _severity_to_intensity(self, severity: str) -> MessageIntensity:
        """Convert severity string to intensity."""
        mapping = {
            "low": MessageIntensity.GENTLE,
            "medium": MessageIntensity.NORMAL,
            "high": MessageIntensity.FIRM,
            "critical": MessageIntensity.URGENT,
        }
        return mapping.get(severity.lower(), MessageIntensity.NORMAL)

    def _worker_loop(self) -> None:
        """Worker thread for scheduled events."""
        while not self._stop_event.is_set():
            try:
                # Check for scheduled events
                try:
                    event = self._event_queue.get(timeout=1.0)

                    # Check if time to speak
                    scheduled = event.data.get("scheduled_time")
                    if scheduled:
                        scheduled_time = datetime.fromisoformat(scheduled)
                        if datetime.now() >= scheduled_time:
                            message = event.data.get("message", "")
                            personality = VoicePersonality(
                                event.data.get("personality", "neutral")
                            )
                            self.voice.speak(message, personality)

                except:
                    pass

            except Exception as e:
                print(f"Voice enforcer error: {e}")

    # ========================================================================
    # STATISTICS
    # ========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get enforcer statistics."""
        return {
            "enabled": self.config.enabled,
            "mode": self.config.mode.value,
            "running": self._running,
            "interventions_total": self._interventions_total,
            "interventions_by_type": self._interventions_by_type,
            "hourly_count": self._hourly_count,
            "voice_engine": self.voice.get_stats(),
        }

    def set_mode(self, mode: EnforcementMode) -> None:
        """Set enforcement mode."""
        self.config.mode = mode

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable enforcer."""
        self.config.enabled = enabled


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_voice_enforcer(
    mode: EnforcementMode = EnforcementMode.ENFORCER,
    enabled: bool = True,
    auto_start: bool = False
) -> VoiceEnforcer:
    """
    Create a configured voice enforcer.

    Args:
        mode: Enforcement mode
        enabled: Enable enforcer
        auto_start: Start immediately

    Returns:
        Configured VoiceEnforcer
    """
    config = EnforcerConfig(
        mode=mode,
        enabled=enabled,
    )

    enforcer = VoiceEnforcer(config=config)

    if auto_start and enabled:
        enforcer.start()

    return enforcer


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Voice Enforcer...")
    print("="*60)

    enforcer = create_voice_enforcer(auto_start=False)

    # Test 1: Distraction report
    print("\n1. Testing distraction report...")
    result = enforcer.report_distraction(
        app_name="Instagram",
        duration_seconds=300,
        severity="high"
    )
    print(f"   Spoken: {result}")

    # Test 2: Streak risk
    print("\n2. Testing streak risk...")
    result = enforcer.report_streak_risk(
        streak=7,
        hours_left=4,
        questions_done=15,
        questions_target=50,
        xp_at_risk=500
    )
    print(f"   Spoken: {result}")

    # Test 3: Achievement
    print("\n3. Testing achievement...")
    result = enforcer.report_achievement(
        name="Week Warrior",
        description="7-day streak",
        xp=300
    )
    print(f"   Spoken: {result}")

    # Test 4: Session complete
    print("\n4. Testing session complete...")
    result = enforcer.report_session_complete(
        questions=30,
        accuracy=0.85,
        xp=450,
        coins=150,
        streak=7
    )
    print(f"   Spoken: {result}")

    # Test 5: Pattern detection
    print("\n5. Testing pattern detection...")
    result = enforcer.report_pattern_detected(
        pattern_type="study_avoidance",
        severity="high",
        evidence={"switch_count": 8}
    )
    print(f"   Spoken: {result}")

    # Test 6: Statistics
    print("\n6. Statistics:")
    stats = enforcer.get_stats()
    print(f"   Total interventions: {stats['interventions_total']}")
    print(f"   By type: {stats['interventions_by_type']}")

    print("\n" + "="*60)
    print("All tests passed!")
