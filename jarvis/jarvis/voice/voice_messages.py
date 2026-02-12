"""
JARVIS Voice Messages
=====================

Purpose: Predefined voice messages for different scenarios.

This module provides:
- Categorized voice messages
- Dynamic message generation
- Context-aware messaging
- Multiple intensity levels

EXAM IMPACT:
    CRITICAL. Right words at right time = behaviour change.
    Messages are crafted to be IMPACTFUL, not nagging.

MESSAGE PHILOSOPHY:
    - Direct, not vague
    - Actionable, not preachy
    - Personal, not generic
    - Urgent when needed, calm when appropriate

CATEGORIES:
    1. DISCIPLINE - Pattern detection warnings
    2. MOTIVATION - Daily motivation, encouragement
    3. ACHIEVEMENT - Celebration messages
    4. STUDY - Session guidance
    5. SCHEDULE - Time-based reminders
    6. SOCIAL - Comparison, accountability

REASON FOR DESIGN:
    - Predefined for consistency
    - Multiple options for variety
    - Intensity levels for severity
    - Dynamic generation for personalization

ROLLBACK PLAN:
    - Messages are read-only
    - No system modifications
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import random


# ============================================================================
# ENUMS
# ============================================================================

class MessageType(Enum):
    """Types of voice messages."""
    # Discipline
    DISTRACTION_WARNING = "distraction_warning"
    STREAK_RISK = "streak_risk"
    PORN_DETECTED = "porn_detected"
    LATE_NIGHT = "late_night"
    STUDY_AVOIDANCE = "study_avoidance"
    BURNOUT_WARNING = "burnout_warning"

    # Motivation
    DAILY_START = "daily_start"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    STREAK_CELEBRATION = "streak_celebration"
    TARGET_REMINDER = "target_reminder"

    # Achievement
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    JACKPOT = "jackpot"
    MILESTONE = "milestone"
    LEVEL_UP = "level_up"

    # Study
    QUESTION_PROMPT = "question_prompt"
    BREAK_REMINDER = "break_reminder"
    FOCUS_LOST = "focus_lost"
    WEAK_TOPIC = "weak_topic"

    # Schedule
    MORNING_GREETING = "morning_greeting"
    EVENING_SUMMARY = "evening_summary"
    BEDTIME_WARNING = "bedtime_warning"

    # Social
    LEADERBOARD_UPDATE = "leaderboard_update"
    COMPETITOR_AHEAD = "competitor_ahead"


class MessageCategory(Enum):
    """Categories of messages."""
    DISCIPLINE = "discipline"
    MOTIVATION = "motivation"
    ACHIEVEMENT = "achievement"
    STUDY = "study"
    SCHEDULE = "schedule"
    SOCIAL = "social"


class MessageIntensity(Enum):
    """Intensity levels for messages."""
    GENTLE = "gentle"       # Calm, non-threatening
    NORMAL = "normal"       # Standard tone
    FIRM = "firm"           # Clear, direct
    URGENT = "urgent"       # Time-sensitive
    CRITICAL = "critical"   # Emergency level


# ============================================================================
# PREDEFINED MESSAGES
# ============================================================================

PREDEFINED_MESSAGES: Dict[MessageType, Dict[MessageIntensity, List[str]]] = {
    # ========================================
    # DISCIPLINE MESSAGES
    # ========================================
    MessageType.DISTRACTION_WARNING: {
        MessageIntensity.GENTLE: [
            "I noticed you switched apps. Let's get back to studying.",
            "Focus check. Your study session is still active.",
        ],
        MessageIntensity.NORMAL: [
            "You've opened a distracting app. Close it and return to your session.",
            "Distraction detected. Your exam success depends on focus. Get back to work.",
        ],
        MessageIntensity.FIRM: [
            "You're being distracted. Close the app NOW. Your seat depends on every minute.",
            "This is the third distraction. Each one costs you marks. Focus!",
        ],
        MessageIntensity.URGENT: [
            "Stop. Close that app immediately. You're wasting precious preparation time.",
            "Distraction alert. You have {hours_left} hours left today. Don't waste them.",
        ],
        MessageIntensity.CRITICAL: [
            "EMERGENCY. You've been distracted for {minutes} minutes. This is EXACTLY what derails preparation. STOP NOW.",
            "CRITICAL. Your streak is at risk because of distractions. Close the app or lose everything you've built.",
        ],
    },

    MessageType.STREAK_RISK: {
        MessageIntensity.GENTLE: [
            "Your streak is counting on you today. A few more questions will keep it alive.",
            "Don't forget to complete your daily target. Your streak is precious.",
        ],
        MessageIntensity.NORMAL: [
            "Your {streak}-day streak needs attention today. Don't let it break.",
            "You have {hours_left} hours to protect your streak. Complete your target.",
        ],
        MessageIntensity.FIRM: [
            "WARNING. Your {streak}-day streak is at risk. {questions_left} questions needed to save it.",
            "Your streak of {streak} days will DIE today if you don't study. Is that what you want?",
        ],
        MessageIntensity.URGENT: [
            "URGENT. Only {hours_left} hours left and you have {questions_done} questions done. Your streak is dying.",
            "Your {streak}-day streak is about to end. {xp_at_risk} XP will be lost. ACT NOW.",
        ],
        MessageIntensity.CRITICAL: [
            "CRITICAL. Your {streak}-day streak will be DESTROYED in {hours_left} hours. This is the moment where champions and quitters separate. Which are you?",
        ],
    },

    MessageType.PORN_DETECTED: {
        MessageIntensity.FIRM: [
            "I detected access to inappropriate content. This will destroy your preparation. Close it immediately.",
            "Adult content detected. This is exactly what derails students. Stop now.",
        ],
        MessageIntensity.URGENT: [
            "STOP. Pornography will destroy your focus, your motivation, and your exam results. Close it NOW.",
            "This content is banned for a reason. Every second on it is a second stolen from your future.",
        ],
        MessageIntensity.CRITICAL: [
            "EMERGENCY. Pornography access detected. This is a PATTERN that has derailed you before. You have a choice right now: your addiction or your seat. Choose wisely.",
        ],
    },

    MessageType.LATE_NIGHT: {
        MessageIntensity.GENTLE: [
            "It's late. Your brain needs rest to consolidate what you learned today.",
            "Past midnight. Consider wrapping up so tomorrow you're fresh.",
        ],
        MessageIntensity.NORMAL: [
            "It's {hour} PM. Late night screen time hurts tomorrow's focus. Time to sleep.",
            "Your sleep is important for memory consolidation. Consider stopping for today.",
        ],
        MessageIntensity.FIRM: [
            "It's {hour} AM. Late night dopamine seeking is a pattern that leads to burnout. Put the phone down.",
            "You're still awake at {hour}. This will destroy your tomorrow's productivity. Sleep NOW.",
        ],
        MessageIntensity.URGENT: [
            "LATE NIGHT ALERT. It's {hour} AM. Your brain needs sleep to process what you learned. If you stay up, you're sabotaging your own preparation.",
        ],
        MessageIntensity.CRITICAL: [
            "CRITICAL. {hour} AM and still active. This is a DANGEROUS pattern. Every hour of missed sleep reduces your cognitive performance by 10%. Is this content worth LOSING YOUR SEAT?",
        ],
    },

    MessageType.STUDY_AVOIDANCE: {
        MessageIntensity.NORMAL: [
            "I notice you've been avoiding studying. What's stopping you?",
            "Your study session was supposed to start. Let's begin, shall we?",
        ],
        MessageIntensity.FIRM: [
            "You've switched apps {count} times in the last {minutes} minutes. This is avoidance behavior. Your exam won't wait.",
            "Study avoidance detected. You're running from the hard work that will get you that seat.",
        ],
        MessageIntensity.URGENT: [
            "STOP AVOIDING. You've delayed studying for {hours} hours. Every delay is a mark lost. Start NOW.",
        ],
        MessageIntensity.CRITICAL: [
            "CRITICAL AVOIDANCE PATTERN. You've spent today avoiding the very thing that will get you your seat. This is how dreams die - one delayed session at a time. START STUDYING RIGHT NOW.",
        ],
    },

    MessageType.BURNOUT_WARNING: {
        MessageIntensity.GENTLE: [
            "You've been studying hard. Consider taking a short break.",
            "Your session lengths are getting shorter. Maybe you need some rest?",
        ],
        MessageIntensity.NORMAL: [
            "I notice your sessions are declining. This could be early burnout. Let's adjust your targets.",
            "Your accuracy has dropped {percent} percent this week. Your brain might need recovery time.",
        ],
        MessageIntensity.FIRM: [
            "BURNOUT ALERT. Your performance is declining. I'm reducing your daily targets by 20 percent. This is not weakness, it's strategy.",
            "You're showing signs of burnout: shorter sessions, lower accuracy, more distractions. Take a rest day. It's mandatory.",
        ],
        MessageIntensity.URGENT: [
            "SERIOUS BURNOUT DETECTED. Your last {days} days show declining metrics. STOP. Take tomorrow OFF. Your seat requires you to be fresh, not exhausted.",
        ],
    },

    # ========================================
    # MOTIVATION MESSAGES
    # ========================================
    MessageType.DAILY_START: {
        MessageIntensity.GENTLE: [
            "Good morning. A new day of preparation begins. Ready to make progress?",
            "Rise and shine. Your exam prep waits for no one. Let's get started.",
        ],
        MessageIntensity.NORMAL: [
            "Day {day_number}. {days_left} days until your exam. Every question you answer today brings you closer to that seat.",
            "Good morning. You have {target} questions to complete today. Your {streak}-day streak is counting on you.",
        ],
        MessageIntensity.FIRM: [
            "Day {day_number} of 75. No more excuses. No more delays. Today you will complete your full target. Your seat depends on it.",
        ],
    },

    MessageType.SESSION_START: {
        MessageIntensity.GENTLE: [
            "Starting your {subject} session. Focus on quality over speed.",
            "Let's work on {subject} today. Take your time with each question.",
        ],
        MessageIntensity.NORMAL: [
            "Session starting. {questions} questions ahead. Your jackpot chance is 5 percent. Let's go.",
            "Beginning {subject} practice. Your current accuracy is {accuracy} percent. Let's improve it.",
        ],
        MessageIntensity.FIRM: [
            "SESSION START. {subject}. {questions} questions. No phone. No distractions. Full focus. This is how you win.",
        ],
    },

    MessageType.SESSION_END: {
        MessageIntensity.GENTLE: [
            "Session complete. Good effort today. Take a short break.",
            "Well done! You answered {questions} questions with {accuracy} percent accuracy.",
        ],
        MessageIntensity.NORMAL: [
            "Session complete! {xp} XP earned. {coins} coins collected. Your streak is now {streak} days strong.",
            "Great session! You earned {xp} XP. Your accuracy was {accuracy} percent. Keep this momentum going.",
        ],
        MessageIntensity.FIRM: [
            "SESSION COMPLETE. {questions} questions. {accuracy} percent accuracy. {xp} XP. This is the work of a champion. Now rest, then do it again.",
        ],
    },

    MessageType.STREAK_CELEBRATION: {
        MessageIntensity.NORMAL: [
            "{streak} days strong! Your consistency is building. Keep going.",
            "Streak milestone: {streak} days! Each day makes the next easier.",
        ],
        MessageIntensity.FIRM: [
            "{streak} DAY STREAK! You are proving your commitment. {streak} days of showing up. This is how seats are won.",
            "AMAZING. {streak} days of consistency. Most people quit by now. You didn't. That's the difference.",
        ],
    },

    MessageType.TARGET_REMINDER: {
        MessageIntensity.GENTLE: [
            "You have {questions_left} questions left today. Plenty of time.",
            "Daily target: {done} of {total} complete. Keep going when you're ready.",
        ],
        MessageIntensity.NORMAL: [
            "{questions_left} questions remaining. {hours_left} hours left today. Stay on track.",
            "Target reminder: {percent} percent complete. Push through to finish strong.",
        ],
        MessageIntensity.FIRM: [
            "TARGET ALERT. Only {questions_done} of {target} done. {hours_left} hours remaining. Accelerate NOW.",
        ],
    },

    # ========================================
    # ACHIEVEMENT MESSAGES
    # ========================================
    MessageType.ACHIEVEMENT_UNLOCK: {
        MessageIntensity.NORMAL: [
            "Achievement unlocked: {name}. Well earned.",
            "You've earned the {name} achievement. {xp} bonus XP awarded.",
        ],
        MessageIntensity.FIRM: [
            "ACHIEVEMENT UNLOCKED: {name}! {description}. This is proof of your dedication. {xp} XP awarded.",
            "CONGRATULATIONS. You've earned {name}. This is what consistency looks like. {xp} XP added to your total.",
        ],
    },

    MessageType.JACKPOT: {
        MessageIntensity.NORMAL: [
            "JACKPOT! You hit the big one! {xp} XP awarded!",
            "Incredible! Jackpot on this session! {xp} XP and {coins} coins!",
        ],
        MessageIntensity.FIRM: [
            "JACKPOT! {xp} XP! This is the biggest reward possible! Your dedication paid off! {coins} bonus coins!",
            "WOW! JACKPOT HIT! {xp} XP earned in one session! This is rare and well deserved! Keep this momentum!",
        ],
    },

    MessageType.MILESTONE: {
        MessageIntensity.NORMAL: [
            "Milestone reached: {milestone}. You're making real progress.",
            "{milestone} achieved. This is a significant step toward your goal.",
        ],
        MessageIntensity.FIRM: [
            "MILESTONE: {milestone}! This is a major achievement in your preparation journey. {message}",
            "INCREDIBLE MILESTONE: {milestone}! You've proven your commitment. This is how seats are confirmed. {message}",
        ],
    },

    # ========================================
    # STUDY MESSAGES
    # ========================================
    MessageType.QUESTION_PROMPT: {
        MessageIntensity.NORMAL: [
            "Next question. Take your time and think carefully.",
            "Question {number}. Read carefully before answering.",
        ],
    },

    MessageType.BREAK_REMINDER: {
        MessageIntensity.GENTLE: [
            "You've been studying for an hour. Consider a 5 minute break.",
            "Time for a short break. Stand up, stretch, hydrate.",
        ],
        MessageIntensity.NORMAL: [
            "Break time. You've studied {minutes} minutes. Take 5 minutes to refresh.",
            "Your brain needs a reset. Take a short break, then come back strong.",
        ],
    },

    MessageType.FOCUS_LOST: {
        MessageIntensity.NORMAL: [
            "I notice your focus dropping. Take a breath and refocus.",
            "Your response times are slowing. Are you still focused?",
        ],
        MessageIntensity.FIRM: [
            "FOCUS CHECK. Your performance is declining. Either commit fully or take a proper break.",
        ],
    },

    MessageType.WEAK_TOPIC: {
        MessageIntensity.NORMAL: [
            "This topic needs more practice. Let's focus on {topic}.",
            "{topic} is a weak area. I'm adding extra questions for it.",
        ],
        MessageIntensity.FIRM: [
            "WEAK TOPIC ALERT. {topic} has low accuracy. You MUST practice this. Avoiding it will cost you marks in the exam.",
            "Your {subject} theta is low. This is your weakest subject and highest weightage. No more avoidance. We practice this NOW.",
        ],
    },

    # ========================================
    # SCHEDULE MESSAGES
    # ========================================
    MessageType.MORNING_GREETING: {
        MessageIntensity.NORMAL: [
            "Good morning. Day {day} of preparation. {days_left} days until exam. Let's make progress.",
            "Rise and shine. Your {streak}-day streak continues. Today's target: {questions} questions.",
        ],
        MessageIntensity.FIRM: [
            "Good morning. Day {day}. No shortcuts today. No excuses. Full target completion. Your seat waits for no one.",
        ],
    },

    MessageType.EVENING_SUMMARY: {
        MessageIntensity.NORMAL: [
            "Evening summary. You completed {questions} questions with {accuracy} percent accuracy. {xp} XP earned today.",
            "End of day report: {questions} questions, {accuracy} accuracy, {streak} day streak. Tomorrow, do better.",
        ],
        MessageIntensity.FIRM: [
            "DAILY REPORT: {questions} questions. Target was {target}. {percent} percent complete. {message}",
        ],
    },

    MessageType.BEDTIME_WARNING: {
        MessageIntensity.GENTLE: [
            "It's getting late. Your brain needs rest for tomorrow's session.",
            "Time to wind down. Good sleep means better learning tomorrow.",
        ],
        MessageIntensity.NORMAL: [
            "It's {hour} PM. Recommended bedtime is approaching. Start wrapping up.",
            "Late night reminder: Quality sleep is essential for memory consolidation.",
        ],
        MessageIntensity.FIRM: [
            "BEDTIME. It's {hour}. Your brain processes memories during sleep. Every hour of missed sleep costs you tomorrow.",
        ],
    },

    # ========================================
    # SOCIAL MESSAGES
    # ========================================
    MessageType.LEADERBOARD_UPDATE: {
        MessageIntensity.NORMAL: [
            "Leaderboard update: You're now rank {rank}. {people_behind} people behind you.",
            "Position check: Rank {rank}. You're in the top {percent} percent.",
        ],
        MessageIntensity.FIRM: [
            "LEADERBOARD: Rank {rank}. Only {xp_gap} XP behind the person above you. That's just {questions} questions. Take their spot.",
        ],
    },

    MessageType.COMPETITOR_AHEAD: {
        MessageIntensity.NORMAL: [
            "Someone just overtook you on the leaderboard. Time to fight back.",
            "You dropped one rank. Show them what you've got.",
        ],
        MessageIntensity.FIRM: [
            "ALERT. You've been overtaken. Rank {new_rank}. The person ahead has only {xp_gap} XP more. Take back your position NOW.",
        ],
    },
}


# ============================================================================
# MESSAGE GENERATOR CLASS
# ============================================================================

class VoiceMessageGenerator:
    """
    Generates voice messages for different scenarios.

    This class:
    - Provides predefined messages
    - Generates dynamic messages
    - Personalizes messages with user data
    - Selects appropriate intensity

    Usage:
        generator = VoiceMessageGenerator()

        # Get message for distraction
        message = generator.get_message(
            MessageType.DISTRACTION_WARNING,
            MessageIntensity.NORMAL,
            app_name="Instagram"
        )

        # Get streak risk message
        message = generator.get_streak_risk_message(
            streak=7,
            hours_left=4,
            questions_done=10
        )

    EXAM IMPACT:
        Right message at right time = behaviour change.
        Messages are crafted to be IMPACTFUL.
    """

    def __init__(
        self,
        messages: Optional[Dict[MessageType, Dict[MessageIntensity, List[str]]]] = None
    ):
        """
        Initialize message generator.

        Args:
            messages: Custom messages (default: PREDEFINED_MESSAGES)
        """
        self.messages = messages or PREDEFINED_MESSAGES

    def get_message(
        self,
        message_type: MessageType,
        intensity: MessageIntensity = MessageIntensity.NORMAL,
        **kwargs
    ) -> str:
        """
        Get a message for the given type and intensity.

        Args:
            message_type: Type of message
            intensity: Intensity level
            **kwargs: Variables to substitute

        Returns:
            Formatted message
        """
        # Get messages for this type
        type_messages = self.messages.get(message_type, {})
        intensity_messages = type_messages.get(intensity, [])

        if not intensity_messages:
            # Fallback to normal intensity
            intensity_messages = type_messages.get(MessageIntensity.NORMAL, [])

        if not intensity_messages:
            return "JARVIS message."

        # Select random message from options
        message = random.choice(intensity_messages)

        # Substitute variables
        return message.format(**kwargs) if kwargs else message

    # ========================================================================
    # CONVENIENCE METHODS
    # ========================================================================

    def get_distraction_warning(
        self,
        app_name: str,
        minutes_distracted: int = 0,
        intensity: MessageIntensity = MessageIntensity.NORMAL
    ) -> str:
        """Get distraction warning message."""
        return self.get_message(
            MessageType.DISTRACTION_WARNING,
            intensity,
            app_name=app_name,
            minutes=minutes_distracted
        )

    def get_streak_risk_message(
        self,
        streak: int,
        hours_left: float,
        questions_done: int,
        questions_left: int = 0,
        xp_at_risk: int = 0,
        intensity: MessageIntensity = MessageIntensity.NORMAL
    ) -> str:
        """Get streak risk message."""
        return self.get_message(
            MessageType.STREAK_RISK,
            intensity,
            streak=streak,
            hours_left=int(hours_left),
            questions_done=questions_done,
            questions_left=questions_left,
            xp_at_risk=xp_at_risk
        )

    def get_late_night_message(
        self,
        hour: int,
        intensity: MessageIntensity = MessageIntensity.NORMAL
    ) -> str:
        """Get late night warning message."""
        return self.get_message(
            MessageType.LATE_NIGHT,
            intensity,
            hour=hour
        )

    def get_session_start_message(
        self,
        subject: str,
        questions: int,
        accuracy: float = 0.0,
        intensity: MessageIntensity = MessageIntensity.NORMAL
    ) -> str:
        """Get session start message."""
        return self.get_message(
            MessageType.SESSION_START,
            intensity,
            subject=subject,
            questions=questions,
            accuracy=int(accuracy * 100)
        )

    def get_session_end_message(
        self,
        questions: int,
        accuracy: float,
        xp: int,
        coins: int,
        streak: int,
        intensity: MessageIntensity = MessageIntensity.NORMAL
    ) -> str:
        """Get session end message."""
        return self.get_message(
            MessageType.SESSION_END,
            intensity,
            questions=questions,
            accuracy=int(accuracy * 100),
            xp=xp,
            coins=coins,
            streak=streak
        )

    def get_achievement_message(
        self,
        name: str,
        description: str,
        xp: int,
        intensity: MessageIntensity = MessageIntensity.NORMAL
    ) -> str:
        """Get achievement unlock message."""
        return self.get_message(
            MessageType.ACHIEVEMENT_UNLOCK,
            intensity,
            name=name,
            description=description,
            xp=xp
        )

    def get_jackpot_message(
        self,
        xp: int,
        coins: int,
        intensity: MessageIntensity = MessageIntensity.FIRM
    ) -> str:
        """Get jackpot celebration message."""
        return self.get_message(
            MessageType.JACKPOT,
            intensity,
            xp=xp,
            coins=coins
        )

    def get_daily_motivation(
        self,
        day: int,
        days_left: int,
        streak: int,
        target: int
    ) -> str:
        """Get daily motivation message."""
        messages = [
            f"Day {day} of your preparation. {days_left} days until your exam. Your {streak}-day streak is proof of your commitment. Today, complete {target} questions. Every one brings you closer to your seat.",
            f"Good morning. Day {day}. You've shown up for {streak} days in a row. Today is no different. {target} questions. Full focus. No excuses. Your seat is waiting.",
            f"Day {day}. Each question you answer is an investment in your future. Your {streak}-day streak shows you understand this. {target} more investments today. Let's go.",
        ]
        return random.choice(messages)

    def get_bedtime_warning(
        self,
        hour: int,
        intensity: MessageIntensity = MessageIntensity.NORMAL
    ) -> str:
        """Get bedtime warning."""
        return self.get_message(
            MessageType.BEDTIME_WARNING,
            intensity,
            hour=hour
        )

    def get_leaderboard_message(
        self,
        rank: int,
        total: int,
        xp_gap: int,
        intensity: MessageIntensity = MessageIntensity.NORMAL
    ) -> str:
        """Get leaderboard update message."""
        percent = (1 - rank / total) * 100 if total > 0 else 0
        questions = xp_gap // 10

        return self.get_message(
            MessageType.LEADERBOARD_UPDATE,
            intensity,
            rank=rank,
            percent=int(percent),
            xp_gap=xp_gap,
            questions=questions
        )


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Voice Messages...")
    print("="*60)

    generator = VoiceMessageGenerator()

    # Test 1: Distraction warnings
    print("\n1. Distraction Warnings:")
    for intensity in [MessageIntensity.GENTLE, MessageIntensity.NORMAL, MessageIntensity.FIRM]:
        msg = generator.get_distraction_warning("Instagram", intensity=intensity)
        print(f"   [{intensity.value}]: {msg[:60]}...")

    # Test 2: Streak risk
    print("\n2. Streak Risk Messages:")
    msg = generator.get_streak_risk_message(
        streak=7,
        hours_left=4,
        questions_done=15,
        intensity=MessageIntensity.FIRM
    )
    print(f"   {msg}")

    # Test 3: Session messages
    print("\n3. Session Messages:")
    print(f"   Start: {generator.get_session_start_message('Mathematics', 30)}")
    print(f"   End: {generator.get_session_end_message(30, 0.85, 450, 150, 7)}")

    # Test 4: Achievements
    print("\n4. Achievement Messages:")
    print(f"   {generator.get_achievement_message('Week Warrior', '7-day streak', 300)}")
    print(f"   Jackpot: {generator.get_jackpot_message(500, 200)}")

    # Test 5: Daily motivation
    print("\n5. Daily Motivation:")
    print(f"   {generator.get_daily_motivation(day=30, days_left=45, streak=30, target=50)}")

    print("\n" + "="*60)
    print("All tests passed!")
