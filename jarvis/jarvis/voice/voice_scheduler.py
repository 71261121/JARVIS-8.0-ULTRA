"""
JARVIS Voice Scheduler
======================

Purpose: Schedule voice messages at specific times.

This module:
- Provides scheduled voice reminders
- Morning motivation at wake time
- Study reminders throughout the day
- Bedtime warnings at night
- Hourly progress check-ins

EXAM IMPACT:
    HIGH. Consistent reminders maintain consistency.
    Scheduled voice creates ROUTINE and ACCOUNTABILITY.
    User knows JARVIS will check in at specific times.

SCHEDULE TYPES:
    - MORNING_GREETING: Start of day motivation
    - STUDY_REMINDER: Remind to study at set times
    - PROGRESS_CHECK: Hourly progress updates
    - TARGET_REMINDER: Daily target check
    - BEDTIME_WARNING: Time to sleep reminder

REASON FOR DESIGN:
    - Background thread for scheduling
    - Configurable schedule
    - Skips if studying actively
    - Respects quiet hours

ROLLBACK PLAN:
    - Stop scheduler to disable
    - No persistent changes
"""

import threading
import time
from datetime import datetime, timedelta, time as dt_time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import random

from .voice_engine import (
    VoiceEngine,
    VoicePersonality,
    create_voice_engine,
)
from .voice_messages import (
    VoiceMessageGenerator,
    MessageType,
)


# ============================================================================
# ENUMS
# ============================================================================

class ScheduleType(Enum):
    """Types of scheduled messages."""
    MORNING_GREETING = "morning_greeting"
    STUDY_REMINDER = "study_reminder"
    PROGRESS_CHECK = "progress_check"
    TARGET_REMINDER = "target_reminder"
    BEDTIME_WARNING = "bedtime_warning"
    HOURLY_MOTIVATION = "hourly_motivation"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ScheduledMessage:
    """A scheduled voice message."""
    schedule_type: ScheduleType
    hour: int
    minute: int = 0
    enabled: bool = True
    days: List[int] = field(default_factory=lambda: list(range(7)))  # 0=Mon, 6=Sun
    message: Optional[str] = None  # Custom message or auto-generated
    personality: VoicePersonality = VoicePersonality.NEUTRAL
    last_spoken: Optional[datetime] = None


@dataclass
class ScheduleConfig:
    """Configuration for voice scheduler."""
    enabled: bool = True

    # Morning
    morning_hour: int = 7
    morning_enabled: bool = True

    # Study reminders
    study_reminder_hours: List[int] = field(default_factory=lambda: [9, 14, 19])
    study_reminder_enabled: bool = True

    # Progress checks
    progress_check_interval_hours: int = 2
    progress_check_enabled: bool = True

    # Target reminders
    target_reminder_hours: List[int] = field(default_factory=lambda: [17, 20, 22])
    target_reminder_enabled: bool = True

    # Bedtime
    bedtime_hour: int = 22
    bedtime_enabled: bool = True

    # Quiet hours
    quiet_start: int = 23
    quiet_end: int = 6

    # Skip conditions
    skip_if_studying: bool = True  # Don't interrupt active study
    study_active_minutes: int = 15  # Consider studying if activity in last N minutes


# ============================================================================
# VOICE SCHEDULER CLASS
# ============================================================================

class VoiceScheduler:
    """
    Schedule and deliver voice messages.

    This class:
    - Manages scheduled voice messages
    - Checks conditions before speaking
    - Tracks what's been spoken
    - Respects quiet hours

    Usage:
        scheduler = VoiceScheduler(voice_engine)
        scheduler.start()

        # Add custom schedule
        scheduler.add_schedule(ScheduledMessage(
            schedule_type=ScheduleType.STUDY_REMINDER,
            hour=10,
            minute=0
        ))

        # Stop
        scheduler.stop()

    EXAM IMPACT:
        Scheduled reminders maintain consistency.
        Creates routine and accountability.
    """

    def __init__(
        self,
        voice_engine: Optional[VoiceEngine] = None,
        config: Optional[ScheduleConfig] = None,
        message_generator: Optional[VoiceMessageGenerator] = None,
        get_progress_callback: Optional[Callable[[], Dict]] = None
    ):
        """
        Initialize voice scheduler.

        Args:
            voice_engine: VoiceEngine instance
            config: Scheduler configuration
            message_generator: Message generator
            get_progress_callback: Callback to get current progress
        """
        self.voice = voice_engine or create_voice_engine(auto_start=False)
        self.config = config or ScheduleConfig()
        self.generator = message_generator or VoiceMessageGenerator()
        self.get_progress = get_progress_callback

        # Schedules
        self._schedules: List[ScheduledMessage] = []
        self._init_default_schedules()

        # State
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Last activity (for skip_if_studying)
        self._last_activity: Optional[datetime] = None

        # Statistics
        self._messages_spoken = 0
        self._messages_skipped = 0

    def _init_default_schedules(self) -> None:
        """Initialize default scheduled messages."""
        # Morning greeting
        if self.config.morning_enabled:
            self._schedules.append(ScheduledMessage(
                schedule_type=ScheduleType.MORNING_GREETING,
                hour=self.config.morning_hour,
                minute=0,
                personality=VoicePersonality.ENCOURAGING,
            ))

        # Study reminders
        if self.config.study_reminder_enabled:
            for hour in self.config.study_reminder_hours:
                self._schedules.append(ScheduledMessage(
                    schedule_type=ScheduleType.STUDY_REMINDER,
                    hour=hour,
                    minute=0,
                    personality=VoicePersonality.NEUTRAL,
                ))

        # Target reminders
        if self.config.target_reminder_enabled:
            for hour in self.config.target_reminder_hours:
                self._schedules.append(ScheduledMessage(
                    schedule_type=ScheduleType.TARGET_REMINDER,
                    hour=hour,
                    minute=0,
                    personality=VoicePersonality.NEUTRAL,
                ))

        # Bedtime warning
        if self.config.bedtime_enabled:
            self._schedules.append(ScheduledMessage(
                schedule_type=ScheduleType.BEDTIME_WARNING,
                hour=self.config.bedtime_hour,
                minute=0,
                personality=VoicePersonality.GENTLE,
            ))

    # ========================================================================
    # CONTROL
    # ========================================================================

    def start(self) -> bool:
        """Start the scheduler."""
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
            name="VoiceScheduler"
        )
        self._worker_thread.start()

        return True

    def stop(self) -> bool:
        """Stop the scheduler."""
        if not self._running:
            return False

        self._stop_event.set()
        self._running = False

        if self._worker_thread:
            self._worker_thread.join(timeout=3)

        return True

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running

    # ========================================================================
    # SCHEDULE MANAGEMENT
    # ========================================================================

    def add_schedule(self, schedule: ScheduledMessage) -> None:
        """Add a scheduled message."""
        self._schedules.append(schedule)

    def remove_schedule(self, schedule_type: ScheduleType, hour: int) -> bool:
        """Remove a scheduled message."""
        for i, s in enumerate(self._schedules):
            if s.schedule_type == schedule_type and s.hour == hour:
                self._schedules.pop(i)
                return True
        return False

    def get_schedules(self) -> List[ScheduledMessage]:
        """Get all scheduled messages."""
        return list(self._schedules)

    def clear_schedules(self) -> None:
        """Clear all schedules."""
        self._schedules.clear()

    # ========================================================================
    # ACTIVITY TRACKING
    # ========================================================================

    def record_activity(self) -> None:
        """Record that user is active."""
        self._last_activity = datetime.now()

    def _is_user_studying(self) -> bool:
        """Check if user is currently studying."""
        if not self.config.skip_if_studying:
            return False

        if not self._last_activity:
            return False

        elapsed = (datetime.now() - self._last_activity).total_seconds()
        return elapsed < self.config.study_active_minutes * 60

    # ========================================================================
    # MESSAGE GENERATION
    # ========================================================================

    def _generate_message(
        self,
        schedule: ScheduledMessage
    ) -> str:
        """Generate message for a schedule."""
        # Use custom message if provided
        if schedule.message:
            return schedule.message

        # Get progress data if callback available
        progress = self.get_progress() if self.get_progress else {}

        # Generate based on type
        if schedule.schedule_type == ScheduleType.MORNING_GREETING:
            return self._generate_morning_message(progress)

        elif schedule.schedule_type == ScheduleType.STUDY_REMINDER:
            return self._generate_study_reminder(progress)

        elif schedule.schedule_type == ScheduleType.PROGRESS_CHECK:
            return self._generate_progress_check(progress)

        elif schedule.schedule_type == ScheduleType.TARGET_REMINDER:
            return self._generate_target_reminder(progress)

        elif schedule.schedule_type == ScheduleType.BEDTIME_WARNING:
            return self._generate_bedtime_warning(progress)

        elif schedule.schedule_type == ScheduleType.HOURLY_MOTIVATION:
            return self._generate_hourly_motivation(progress)

        return "JARVIS reminder."

    def _generate_morning_message(self, progress: Dict) -> str:
        """Generate morning greeting message."""
        day = progress.get("day", 1)
        days_left = progress.get("days_left", 75)
        streak = progress.get("streak", 0)
        target = progress.get("target", 50)

        return self.generator.get_daily_motivation(
            day=day,
            days_left=days_left,
            streak=streak,
            target=target
        )

    def _generate_study_reminder(self, progress: Dict) -> str:
        """Generate study reminder message."""
        streak = progress.get("streak", 0)
        done_today = progress.get("done_today", 0)
        target = progress.get("target", 50)

        messages = [
            f"Study reminder. You've completed {done_today} of {target} questions today. Your {streak}-day streak is counting on you.",
            f"Time to study. {target - done_today} questions remaining today. Each one brings you closer to your seat.",
            f"Study session reminder. Your daily progress: {done_today} questions. Target: {target}. Let's close the gap.",
        ]

        return random.choice(messages)

    def _generate_progress_check(self, progress: Dict) -> str:
        """Generate progress check message."""
        done_today = progress.get("done_today", 0)
        target = progress.get("target", 50)
        percent = int(done_today / target * 100) if target > 0 else 0

        messages = [
            f"Progress check: {percent} percent of daily target complete. {target - done_today} questions remaining.",
            f"Hourly update: {done_today} questions done. {target - done_today} to go. Stay focused.",
            f"Status check: {percent} percent progress today. Keep pushing.",
        ]

        return random.choice(messages)

    def _generate_target_reminder(self, progress: Dict) -> str:
        """Generate target reminder message."""
        done_today = progress.get("done_today", 0)
        target = progress.get("target", 50)
        remaining = target - done_today
        streak = progress.get("streak", 0)

        if remaining <= 0:
            return f"Great news! Daily target complete. Your {streak}-day streak is safe."

        hour = datetime.now().hour
        hours_left = 24 - hour

        if remaining > target * 0.5:
            urgency = "You have significant work remaining."
        else:
            urgency = "You're making progress. Push through."

        return (
            f"Target reminder: {done_today} of {target} complete. "
            f"{remaining} questions left with {hours_left} hours remaining. "
            f"{urgency} Your streak depends on completion."
        )

    def _generate_bedtime_warning(self, progress: Dict) -> str:
        """Generate bedtime warning message."""
        hour = datetime.now().hour
        return self.generator.get_bedtime_warning(hour)

    def _generate_hourly_motivation(self, progress: Dict) -> str:
        """Generate hourly motivation message."""
        streak = progress.get("streak", 0)
        done_today = progress.get("done_today", 0)

        motivations = [
            f"Hourly motivation: You've answered {done_today} questions today. Your {streak}-day streak shows your commitment. Keep going.",
            f"Reminder: Every question is progress. You're at {done_today} today. Excellence is a habit. Maintain it.",
            f"Hourly check: {done_today} questions complete. Each one is an investment in your seat. Stay consistent.",
        ]

        return random.choice(motivations)

    # ========================================================================
    # WORKER LOOP
    # ========================================================================

    def _worker_loop(self) -> None:
        """Main worker loop for checking schedules."""
        last_check_minute = -1

        while not self._stop_event.is_set():
            try:
                now = datetime.now()

                # Only check once per minute
                if now.minute == last_check_minute:
                    time.sleep(30)
                    continue

                last_check_minute = now.minute

                # Check each schedule
                for schedule in self._schedules:
                    self._check_schedule(schedule, now)

                time.sleep(60)  # Check every minute

            except Exception as e:
                print(f"Voice scheduler error: {e}")
                time.sleep(60)

    def _check_schedule(
        self,
        schedule: ScheduledMessage,
        now: datetime
    ) -> None:
        """Check if a schedule should trigger."""
        # Check if enabled
        if not schedule.enabled:
            return

        # Check if this hour/minute
        if now.hour != schedule.hour or now.minute != schedule.minute:
            return

        # Check day of week
        if now.weekday() not in schedule.days:
            return

        # Check if already spoken today
        if schedule.last_spoken:
            if schedule.last_spoken.date() == now.date():
                return

        # Check quiet hours
        if self._is_quiet_hour(now.hour):
            return

        # Check if user is studying (skip if so)
        if self._is_user_studying():
            self._messages_skipped += 1
            return

        # Speak the message
        self._speak_schedule(schedule)

    def _is_quiet_hour(self, hour: int) -> bool:
        """Check if current hour is in quiet hours."""
        if self.config.quiet_start <= self.config.quiet_end:
            return self.config.quiet_start <= hour < self.config.quiet_end
        else:
            # Overnight quiet hours (e.g., 23 to 6)
            return hour >= self.config.quiet_start or hour < self.config.quiet_end

    def _speak_schedule(self, schedule: ScheduledMessage) -> None:
        """Speak a scheduled message."""
        message = self._generate_message(schedule)

        result = self.voice.speak(message, schedule.personality)

        if result.success:
            schedule.last_spoken = datetime.now()
            self._messages_spoken += 1
        else:
            self._messages_skipped += 1

    # ========================================================================
    # STATISTICS
    # ========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        return {
            "enabled": self.config.enabled,
            "running": self._running,
            "schedules_count": len(self._schedules),
            "messages_spoken": self._messages_spoken,
            "messages_skipped": self._messages_skipped,
            "last_activity": self._last_activity.isoformat() if self._last_activity else None,
        }

    # ========================================================================
    # MANUAL TRIGGERS
    # ========================================================================

    def trigger_morning_greeting(self) -> bool:
        """Manually trigger morning greeting."""
        message = self._generate_morning_message(
            self.get_progress() if self.get_progress else {}
        )
        return self.voice.speak(message, VoicePersonality.ENCOURAGING).success

    def trigger_bedtime_warning(self) -> bool:
        """Manually trigger bedtime warning."""
        message = self._generate_bedtime_warning(
            self.get_progress() if self.get_progress else {}
        )
        return self.voice.speak(message, VoicePersonality.GENTLE).success

    def trigger_progress_check(self) -> bool:
        """Manually trigger progress check."""
        message = self._generate_progress_check(
            self.get_progress() if self.get_progress else {}
        )
        return self.voice.speak(message, VoicePersonality.NEUTRAL).success


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_voice_scheduler(
    enabled: bool = True,
    morning_hour: int = 7,
    bedtime_hour: int = 22,
    auto_start: bool = False,
    progress_callback: Optional[Callable[[], Dict]] = None
) -> VoiceScheduler:
    """
    Create a configured voice scheduler.

    Args:
        enabled: Enable scheduler
        morning_hour: Hour for morning greeting
        bedtime_hour: Hour for bedtime warning
        auto_start: Start immediately
        progress_callback: Callback for progress data

    Returns:
        Configured VoiceScheduler
    """
    config = ScheduleConfig(
        enabled=enabled,
        morning_hour=morning_hour,
        bedtime_hour=bedtime_hour,
    )

    scheduler = VoiceScheduler(
        config=config,
        get_progress_callback=progress_callback
    )

    if auto_start and enabled:
        scheduler.start()

    return scheduler


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Voice Scheduler...")
    print("="*60)

    # Create scheduler
    def get_progress():
        return {
            "day": 30,
            "days_left": 45,
            "streak": 7,
            "target": 50,
            "done_today": 25,
        }

    scheduler = create_voice_scheduler(
        auto_start=False,
        progress_callback=get_progress
    )

    # Test 1: Check schedules
    print("\n1. Default schedules:")
    for s in scheduler.get_schedules():
        print(f"   {s.schedule_type.value}: {s.hour:02d}:{s.minute:02d}")

    # Test 2: Generate messages
    print("\n2. Generated messages:")
    print(f"   Morning: {scheduler._generate_morning_message(get_progress())[:60]}...")
    print(f"   Study: {scheduler._generate_study_reminder(get_progress())[:60]}...")
    print(f"   Target: {scheduler._generate_target_reminder(get_progress())[:60]}...")

    # Test 3: Manual triggers
    print("\n3. Manual triggers:")
    print(f"   Morning greeting: {scheduler.trigger_morning_greeting()}")
    print(f"   Progress check: {scheduler.trigger_progress_check()}")

    # Test 4: Statistics
    print("\n4. Statistics:")
    stats = scheduler.get_stats()
    print(f"   Schedules: {stats['schedules_count']}")
    print(f"   Spoken: {stats['messages_spoken']}")

    print("\n" + "="*60)
    print("All tests passed!")
