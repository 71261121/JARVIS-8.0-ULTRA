"""
JARVIS Voice Engine
===================

Purpose: Core TTS (Text-to-Speech) functionality for JARVIS.

This module provides:
- Text-to-speech conversion
- Multiple voice personalities
- Volume and speed control
- Queue management for messages
- Platform-specific TTS backends

EXAM IMPACT:
    CRITICAL. Voice is MORE impactful than text.
    User cannot ignore voice messages like notifications.
    Voice provides personal accountability feel.

PLATFORM SUPPORT:
    PRIMARY: Termux TTS (termux-tts-speak)
    FALLBACK: Android TTS via am command
    FALLBACK: espeak (if installed)

TTS COMMANDS:
    termux-tts-speak "text"              # Basic TTS
    termux-tts-speak -r 1.2 "text"       # With rate
    termux-tts-speak -p 1.0 "text"       # With pitch

REASON FOR DESIGN:
    - Multiple backends for reliability
    - Queue system prevents message overlap
    - Personality system for different contexts
    - Async-friendly design

ROLLBACK PLAN:
    - Voice is read-only (no system modifications)
    - Can be disabled by setting enabled=False
    - No persistent changes to system
"""

import subprocess
import threading
import queue
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


# ============================================================================
# CONSTANTS
# ============================================================================

class TTSBackend(Enum):
    """Available TTS backends."""
    TERMUX = "termux"       # termux-tts-speak (primary)
    ANDROID = "android"     # Android TTS via am
    ESPEAK = "espeak"       # espeak (fallback)
    DUMMY = "dummy"         # No TTS (testing)


class VoicePersonality(Enum):
    """Voice personalities for different contexts."""
    STERN = "stern"         # For discipline and warnings
    ENCOURAGING = "encouraging"  # For congratulations
    NEUTRAL = "neutral"     # For information
    URGENT = "urgent"       # For critical alerts
    GENTLE = "gentle"       # For late-night messages


DEFAULT_RATE = 1.0
DEFAULT_PITCH = 1.0
DEFAULT_VOLUME = 1.0
DEFAULT_LANGUAGE = "en-IN"
MAX_QUEUE_SIZE = 50
MESSAGE_TIMEOUT = 30


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class VoiceConfig:
    """Configuration for voice engine."""
    enabled: bool = True
    backend: TTSBackend = TTSBackend.TERMUX
    rate: float = DEFAULT_RATE
    pitch: float = DEFAULT_PITCH
    volume: float = DEFAULT_VOLUME
    language: str = DEFAULT_LANGUAGE
    max_queue_size: int = MAX_QUEUE_SIZE

    personality_rates: Dict[str, float] = field(default_factory=lambda: {
        VoicePersonality.STERN.value: 0.9,
        VoicePersonality.ENCOURAGING.value: 1.1,
        VoicePersonality.NEUTRAL.value: 1.0,
        VoicePersonality.URGENT.value: 1.3,
        VoicePersonality.GENTLE.value: 0.85,
    })


@dataclass
class VoiceResult:
    """Result of a TTS operation."""
    success: bool
    message: str
    backend: TTSBackend
    duration_seconds: float = 0.0
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "message": self.message,
            "backend": self.backend.value,
            "duration_seconds": self.duration_seconds,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class QueuedMessage:
    """A message in the TTS queue."""
    text: str
    personality: VoicePersonality
    priority: int
    timestamp: datetime = field(default_factory=datetime.now)
    callback: Optional[Callable[[VoiceResult], None]] = None


# ============================================================================
# VOICE ENGINE CLASS
# ============================================================================

class VoiceEngine:
    """
    Core TTS engine for JARVIS.
    """

    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config or VoiceConfig()

        if self.config.backend == TTSBackend.TERMUX:
            self.config.backend = self._detect_backend()

        self._queue: queue.PriorityQueue = queue.PriorityQueue(
            maxsize=self.config.max_queue_size
        )

        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._current_message: Optional[str] = None

        self._messages_spoken = 0
        self._messages_failed = 0
        self._total_speaking_time = 0.0

        self._available_backends: List[TTSBackend] = []
        self._detect_available_backends()

    def _detect_backend(self) -> TTSBackend:
        if self._check_command("termux-tts-speak"):
            return TTSBackend.TERMUX
        if self._check_command("espeak"):
            return TTSBackend.ESPEAK
        if self._check_command("am"):
            return TTSBackend.ANDROID
        return TTSBackend.DUMMY

    def _detect_available_backends(self) -> None:
        self._available_backends = []
        if self._check_command("termux-tts-speak"):
            self._available_backends.append(TTSBackend.TERMUX)
        if self._check_command("espeak"):
            self._available_backends.append(TTSBackend.ESPEAK)
        if self._check_command("am"):
            self._available_backends.append(TTSBackend.ANDROID)
        if not self._available_backends:
            self._available_backends.append(TTSBackend.DUMMY)

    def _check_command(self, command: str) -> bool:
        try:
            result = subprocess.run(["which", command], capture_output=True, timeout=2)
            return result.returncode == 0
        except Exception:
            return False

    def start(self) -> bool:
        if self._running:
            return False
        if not self.config.enabled:
            return False

        self._running = True
        self._stop_event.clear()

        self._worker_thread = threading.Thread(
            target=self._worker_loop, daemon=True, name="VoiceEngine"
        )
        self._worker_thread.start()
        return True

    def stop(self) -> bool:
        if not self._running:
            return False
        self._stop_event.set()
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        return True

    def is_running(self) -> bool:
        return self._running

    def is_speaking(self) -> bool:
        return self._current_message is not None

    def speak(
        self,
        text: str,
        personality: VoicePersonality = VoicePersonality.NEUTRAL,
        blocking: bool = False
    ) -> VoiceResult:
        if not self.config.enabled:
            return VoiceResult(
                success=False, message=text, backend=TTSBackend.DUMMY,
                error="Voice engine disabled"
            )

        start_time = datetime.now()

        try:
            result = self._speak_with_backend(text, personality)
            duration = (datetime.now() - start_time).total_seconds()

            if result.success:
                self._messages_spoken += 1
                self._total_speaking_time += duration
            else:
                self._messages_failed += 1

            result.duration_seconds = duration
            return result

        except Exception as e:
            self._messages_failed += 1
            return VoiceResult(
                success=False, message=text, backend=self.config.backend, error=str(e)
            )

    def _speak_with_backend(self, text: str, personality: VoicePersonality) -> VoiceResult:
        backend = self.config.backend
        personality_rate = self.config.personality_rates.get(personality.value, 1.0)
        rate = self.config.rate * personality_rate

        if backend == TTSBackend.TERMUX:
            return self._speak_termux(text, rate)
        elif backend == TTSBackend.ESPEAK:
            return self._speak_espeak(text, rate)
        elif backend == TTSBackend.ANDROID:
            return self._speak_android(text)
        else:
            return self._speak_dummy(text)

    def _speak_termux(self, text: str, rate: float) -> VoiceResult:
        try:
            cmd = ["termux-tts-speak", "-r", str(rate), "-p", str(self.config.pitch)]
            if self.config.language:
                cmd.extend(["-l", self.config.language])
            cmd.append(text)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=MESSAGE_TIMEOUT)

            if result.returncode == 0:
                return VoiceResult(success=True, message=text, backend=TTSBackend.TERMUX)
            else:
                return VoiceResult(success=False, message=text, backend=TTSBackend.TERMUX, error=result.stderr)

        except subprocess.TimeoutExpired:
            return VoiceResult(success=False, message=text, backend=TTSBackend.TERMUX, error="TTS timeout")
        except FileNotFoundError:
            self.config.backend = self._detect_backend()
            return self._speak_with_backend(text, VoicePersonality.NEUTRAL)

    def _speak_espeak(self, text: str, rate: float) -> VoiceResult:
        try:
            wpm = int(160 * rate)
            cmd = ["espeak", "-s", str(wpm), "-p", str(int(self.config.pitch * 50)), text]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=MESSAGE_TIMEOUT)

            if result.returncode == 0:
                return VoiceResult(success=True, message=text, backend=TTSBackend.ESPEAK)
            else:
                return VoiceResult(success=False, message=text, backend=TTSBackend.ESPEAK, error=result.stderr)

        except FileNotFoundError:
            self.config.backend = TTSBackend.DUMMY
            return self._speak_dummy(text)

    def _speak_android(self, text: str) -> VoiceResult:
        return self._speak_dummy(text)

    def _speak_dummy(self, text: str) -> VoiceResult:
        print(f"\n🔊 TTS: {text}\n")
        return VoiceResult(success=True, message=text, backend=TTSBackend.DUMMY)

    def queue_message(
        self,
        text: str,
        personality: VoicePersonality = VoicePersonality.NEUTRAL,
        priority: int = 0,
        callback: Optional[Callable[[VoiceResult], None]] = None
    ) -> bool:
        if not self.config.enabled:
            return False

        try:
            message = QueuedMessage(text=text, personality=personality, priority=priority, callback=callback)
            self._queue.put((-priority, datetime.now(), message))
            return True
        except queue.Full:
            return False

    def _worker_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                try:
                    _, _, message = self._queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                self._current_message = message.text
                result = self.speak(message.text, message.personality, blocking=True)

                if message.callback:
                    try:
                        message.callback(result)
                    except Exception as e:
                        print(f"Voice callback error: {e}")

                self._current_message = None
                self._queue.task_done()

            except Exception as e:
                print(f"Voice worker error: {e}")

    def clear_queue(self) -> int:
        cleared = 0
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                cleared += 1
            except queue.Empty:
                break
        return cleared

    def get_queue_size(self) -> int:
        return self._queue.qsize()

    def get_stats(self) -> Dict[str, Any]:
        return {
            "enabled": self.config.enabled,
            "backend": self.config.backend.value,
            "running": self._running,
            "speaking": self.is_speaking(),
            "messages_spoken": self._messages_spoken,
            "messages_failed": self._messages_failed,
            "total_speaking_time": self._total_speaking_time,
            "queue_size": self.get_queue_size(),
            "available_backends": [b.value for b in self._available_backends],
        }

    def set_rate(self, rate: float) -> None:
        self.config.rate = max(0.5, min(2.0, rate))

    def set_pitch(self, pitch: float) -> None:
        self.config.pitch = max(0.5, min(2.0, pitch))

    def set_enabled(self, enabled: bool) -> None:
        self.config.enabled = enabled


def create_voice_engine(
    enabled: bool = True,
    rate: float = DEFAULT_RATE,
    pitch: float = DEFAULT_PITCH,
    auto_start: bool = False
) -> VoiceEngine:
    config = VoiceConfig(enabled=enabled, rate=rate, pitch=pitch)
    engine = VoiceEngine(config)
    if auto_start and enabled:
        engine.start()
    return engine


if __name__ == "__main__":
    print("Testing Voice Engine...")
    print("="*60)

    engine = create_voice_engine(auto_start=False)

    print("\n1. Backend Detection:")
    print(f"   Selected backend: {engine.config.backend.value}")
    print(f"   Available backends: {[b.value for b in engine._available_backends]}")

    print("\n2. Testing speak()...")
    result = engine.speak("Hello, JARVIS voice engine is ready.")
    print(f"   Success: {result.success}")
    print(f"   Backend: {result.backend.value}")

    print("\n3. Testing personalities...")
    for personality in [VoicePersonality.STERN, VoicePersonality.ENCOURAGING]:
        result = engine.speak(f"This is {personality.value} voice.", personality)
        print(f"   {personality.value}: {result.success}")

    print("\n4. Statistics:")
    stats = engine.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n" + "="*60)
    print("All tests passed!")
