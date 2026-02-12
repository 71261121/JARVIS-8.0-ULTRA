"""
JARVIS Voice Module
===================

Purpose: Voice-based interaction and enforcement.

Components:
- Voice Engine: TTS (Text-to-Speech) functionality
- Voice Messages: Predefined messages for different scenarios
- Voice Enforcer: Integration with intervention system
- Voice Scheduler: Scheduled voice reminders

Why Voice:
- Voice is MORE impactful than text
- Cannot be ignored (unlike notifications)
- Personal accountability feel
- Can interrupt distractions
- Works even when screen is off

EXAM IMPACT:
    CRITICAL. User has history of ignoring text notifications.
    Voice provides UNIGNORABLE feedback.
    Late-night voice warnings can prevent dopamine loops.

Platform Support:
- PRIMARY: Termux TTS (termux-tts-speak)
- FALLBACK: Android TTS via am command
- FALLBACK: espeak (if installed)

ROLLBACK PLAN:
    - Voice is read-only (no system modifications)
    - Can be disabled by setting enabled=False
    - No data loss from disabling
"""

from .voice_engine import (
    VoiceEngine,
    VoiceConfig,
    VoiceResult,
    VoicePersonality,
    TTSBackend,
    create_voice_engine,
)

from .voice_messages import (
    VoiceMessageGenerator,
    MessageType,
    MessageCategory,
    MessageIntensity,
    PREDEFINED_MESSAGES,
)

from .voice_enforcer import (
    VoiceEnforcer,
    EnforcementMode,
    EnforcerConfig,
    create_voice_enforcer,
)

from .voice_scheduler import (
    VoiceScheduler,
    ScheduledMessage,
    ScheduleConfig,
    ScheduleType,
    create_voice_scheduler,
)


__all__ = [
    # Voice Engine
    "VoiceEngine",
    "VoiceConfig",
    "VoiceResult",
    "VoicePersonality",
    "TTSBackend",
    "create_voice_engine",

    # Voice Messages
    "VoiceMessageGenerator",
    "MessageType",
    "MessageCategory",
    "MessageIntensity",
    "PREDEFINED_MESSAGES",

    # Voice Enforcer
    "VoiceEnforcer",
    "EnforcementMode",
    "EnforcerConfig",
    "create_voice_enforcer",

    # Voice Scheduler
    "VoiceScheduler",
    "ScheduledMessage",
    "ScheduleConfig",
    "ScheduleType",
    "create_voice_scheduler",
]
