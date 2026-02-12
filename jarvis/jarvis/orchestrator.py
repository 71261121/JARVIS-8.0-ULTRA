"""
JARVIS System Orchestrator
==========================

Central orchestration class that:
1. Initializes ALL modules in correct order
2. Coordinates inter-module communication
3. Manages system lifecycle (startup/shutdown)
4. Provides unified API for external use
5. Handles errors gracefully

GOAL_ALIGNMENT_CHECK():
    - Orchestrator ensures system works as ONE UNIT
    - Proper initialization order prevents failures
    - Unified API simplifies external integration
    - Error handling prevents system crashes

ROLLBACK PLAN:
    - orchestrator.stop() shuts down all components
    - Each component has individual stop method
    - Graceful shutdown preserves data

EXAM IMPACT:
    CRITICAL. Without orchestrator, modules cannot work together.
    Single point of control for entire system.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import all modules
from jarvis.study.irt import IRTEngine
from jarvis.study.sm2 import SM2Engine
from jarvis.study.question_bank import QuestionBank
from jarvis.study.session import SessionManager

from jarvis.focus.behaviour_monitor import BehaviourMonitor
from jarvis.focus.porn_blocker import PornBlocker
from jarvis.focus.pattern_detector import PatternDetector
from jarvis.focus.behaviour_data_collector import BehaviourDataCollector
from jarvis.focus.intervention_executor import InterventionExecutor
from jarvis.focus.pattern_analyzer import PatternAnalyzer

from jarvis.psych.loss_aversion import LossAversionEngine
from jarvis.psych.reward_system import RewardSystem
from jarvis.psych.achievement_system import AchievementSystem
from jarvis.psych.psychological_engine import PsychologicalEngine

from jarvis.voice.voice_engine import VoiceEngine, TTSBackend
from jarvis.voice.voice_messages import VoiceMessageGenerator
from jarvis.voice.voice_enforcer import VoiceEnforcer, EnforcementMode
from jarvis.voice.voice_scheduler import VoiceScheduler

from jarvis.content.study_plan import StudyPlanGenerator
from jarvis.content.daily_target import DailyTargetManager
from jarvis.content.mock_test import MockTestSystem, MockType
from jarvis.content.milestone_tracker import MilestoneTracker


class SystemState(Enum):
    """System operational states."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class OrchestratorConfig:
    """Configuration for JARVIS orchestrator."""
    
    # Study settings
    initial_theta: float = 0.0
    target_exam_date: str = "2025-05-01"
    
    # Focus settings
    enable_monitoring: bool = True
    enable_porn_blocking: bool = False  # Requires root
    study_start_hour: int = 6
    study_end_hour: int = 22
    
    # Psychology settings
    loss_aversion_multiplier: float = 2.0
    
    # Voice settings
    enable_voice: bool = True
    voice_mode: str = "ENFORCER"  # PASSIVE, ASSISTANT, ENFORCER, RUTHLESS
    quiet_hours_start: int = 23
    quiet_hours_end: int = 7
    
    # Content settings
    plan_start_date: Optional[str] = None
    daily_target_questions: int = 100
    
    # Data paths
    data_dir: str = "/sdcard/jarvis_data"
    log_dir: str = "/sdcard/jarvis_data/logs"
    
    # Debug
    debug_mode: bool = False


@dataclass
class SystemStatus:
    """System status report."""
    state: SystemState
    modules_loaded: List[str]
    active_components: List[str]
    errors: List[str]
    uptime_seconds: float
    last_activity: datetime
    
    def to_dict(self) -> Dict:
        return {
            "state": self.state.value,
            "modules_loaded": self.modules_loaded,
            "active_components": self.active_components,
            "errors": self.errors,
            "uptime_seconds": self.uptime_seconds,
            "last_activity": self.last_activity.isoformat()
        }


class JarvisOrchestrator:
    """
    JARVIS System Orchestrator.
    
    Central coordination for all JARVIS modules.
    
    Usage:
        orchestrator = JarvisOrchestrator()
        orchestrator.initialize()
        orchestrator.start()
        
        # Use the system
        result = orchestrator.process_study_session(...)
        
        # Shutdown
        orchestrator.stop()
    
    ROLLBACK PLAN:
        orchestrator.stop() shuts down all components gracefully.
        Data is saved before shutdown.
    """
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        """
        Initialize orchestrator with configuration.
        
        Args:
            config: Orchestrator configuration. Uses defaults if None.
        """
        self.config = config or OrchestratorConfig()
        self.state = SystemState.UNINITIALIZED
        self.start_time: Optional[datetime] = None
        self.last_activity: datetime = datetime.now()
        self.errors: List[str] = []
        
        # Module references
        self._modules: Dict[str, Any] = {}
        self._active_components: List[str] = []
        
        # Logger
        self.logger = logging.getLogger("JARVIS.Orchestrator")
        
    # =========================================================================
    # LIFECYCLE METHODS
    # =========================================================================
    
    def initialize(self) -> bool:
        """
        Initialize all JARVIS modules.
        
        Initialization order matters:
        1. Core utilities (logging, config)
        2. Study engine (IRT, SM-2, Question Bank)
        3. Psychological engine (Loss Aversion, Rewards, Achievements)
        4. Voice system (Engine, Messages, Enforcer)
        5. Content system (Study Plan, Targets, Mocks, Milestones)
        6. Focus system (Monitor, Blocker, Detector, Analyzer)
        
        Returns:
            True if initialization successful, False otherwise
        """
        self.state = SystemState.INITIALIZING
        self.logger.info("Initializing JARVIS...")
        
        try:
            # Phase 1: Study Engine
            self._init_study_engine()
            
            # Phase 2: Psychological Engine
            self._init_psychological_engine()
            
            # Phase 3: Voice System
            self._init_voice_system()
            
            # Phase 4: Content System
            self._init_content_system()
            
            # Phase 5: Focus System
            self._init_focus_system()
            
            self.state = SystemState.READY
            self.logger.info("JARVIS initialization complete")
            return True
            
        except Exception as e:
            self.state = SystemState.ERROR
            self.errors.append(f"Initialization failed: {str(e)}")
            self.logger.error(f"Initialization failed: {e}")
            return False
    
    def start(self) -> bool:
        """
        Start all active JARVIS components.
        
        Starts monitoring, voice scheduler, and other background tasks.
        
        Returns:
            True if start successful, False otherwise
        """
        if self.state != SystemState.READY:
            self.logger.error(f"Cannot start: system in {self.state.value} state")
            return False
        
        self.logger.info("Starting JARVIS...")
        
        try:
            # Start behaviour monitor
            if self.config.enable_monitoring and "monitor" in self._modules:
                self._modules["monitor"].start()
                self._active_components.append("monitor")
            
            # Start pattern analyzer
            if "pattern_analyzer" in self._modules:
                self._modules["pattern_analyzer"].start()
                self._active_components.append("pattern_analyzer")
            
            # Start voice scheduler
            if self.config.enable_voice and "voice_scheduler" in self._modules:
                self._modules["voice_scheduler"].start()
                self._active_components.append("voice_scheduler")
            
            self.state = SystemState.RUNNING
            self.start_time = datetime.now()
            self.logger.info("JARVIS started successfully")
            return True
            
        except Exception as e:
            self.state = SystemState.ERROR
            self.errors.append(f"Start failed: {str(e)}")
            self.logger.error(f"Start failed: {e}")
            return False
    
    def stop(self) -> bool:
        """
        Stop all JARVIS components gracefully.
        
        Saves data and shuts down all active components.
        
        Returns:
            True if stop successful, False otherwise
        """
        if self.state == SystemState.STOPPED:
            return True
        
        self.state = SystemState.STOPPING
        self.logger.info("Stopping JARVIS...")
        
        try:
            # Stop in reverse order
            # Stop voice scheduler
            if "voice_scheduler" in self._active_components:
                self._modules["voice_scheduler"].stop()
                self._active_components.remove("voice_scheduler")
            
            # Stop pattern analyzer
            if "pattern_analyzer" in self._active_components:
                self._modules["pattern_analyzer"].stop()
                self._active_components.remove("pattern_analyzer")
            
            # Stop behaviour monitor
            if "monitor" in self._active_components:
                self._modules["monitor"].stop()
                self._active_components.remove("monitor")
            
            # Remove porn blocking if active
            if "porn_blocker" in self._active_components:
                self._modules["porn_blocker"].remove_blocking()
                self._active_components.remove("porn_blocker")
            
            self.state = SystemState.STOPPED
            self.logger.info("JARVIS stopped successfully")
            return True
            
        except Exception as e:
            self.errors.append(f"Stop failed: {str(e)}")
            self.logger.error(f"Stop failed: {e}")
            return False
    
    def pause(self) -> bool:
        """Pause all active components."""
        if self.state != SystemState.RUNNING:
            return False
        
        # Pause monitoring and interventions
        if "monitor" in self._active_components:
            self._modules["monitor"].stop()
        
        self.state = SystemState.PAUSED
        return True
    
    def resume(self) -> bool:
        """Resume paused components."""
        if self.state != SystemState.PAUSED:
            return False
        
        if self.config.enable_monitoring and "monitor" in self._modules:
            self._modules["monitor"].start()
        
        self.state = SystemState.RUNNING
        return True
    
    # =========================================================================
    # INITIALIZATION HELPERS
    # =========================================================================
    
    def _init_study_engine(self):
        """Initialize study engine modules."""
        self.logger.info("Initializing Study Engine...")
        
        # IRT Engine (no constructor arguments)
        self._modules["irt_engine"] = IRTEngine()
        self._current_theta = self.config.initial_theta  # Track theta separately
        
        # SM-2 Engine
        self._modules["sm2_engine"] = SM2Engine()
        
        # Question Bank
        self._modules["question_bank"] = QuestionBank()
        
        # Session Manager
        self._modules["session_manager"] = SessionManager()
        
        self.logger.info("Study Engine initialized")
    
    def _init_psychological_engine(self):
        """Initialize psychological engine modules."""
        self.logger.info("Initializing Psychological Engine...")
        
        # Loss Aversion Engine
        self._modules["loss_aversion"] = LossAversionEngine()
        
        # Reward System - use local path in dev environment
        try:
            self._modules["reward_system"] = RewardSystem()
        except Exception:
            # Fallback for development environment
            self._modules["reward_system"] = RewardSystem(data_dir=Path("./jarvis_data"))
        
        # Achievement System
        self._modules["achievement_system"] = AchievementSystem()
        
        # Psychological Engine (integration)
        self._modules["psychological_engine"] = PsychologicalEngine()
        
        self.logger.info("Psychological Engine initialized")
    
    def _init_voice_system(self):
        """Initialize voice system modules."""
        self.logger.info("Initializing Voice System...")
        
        if not self.config.enable_voice:
            self.logger.info("Voice system disabled")
            return
        
        # Voice Engine
        voice_engine = VoiceEngine()
        voice_engine.backend = TTSBackend.DUMMY  # Use dummy for testing
        self._modules["voice_engine"] = voice_engine
        
        # Voice Message Generator
        self._modules["voice_messages"] = VoiceMessageGenerator()
        
        # Voice Enforcer
        enforcer = VoiceEnforcer(voice_engine=voice_engine)
        mode = EnforcementMode[self.config.voice_mode]
        enforcer.mode = mode
        self._modules["voice_enforcer"] = enforcer
        
        # Voice Scheduler
        scheduler = VoiceScheduler(voice_engine=voice_engine)
        self._modules["voice_scheduler"] = scheduler
        
        self.logger.info("Voice System initialized")
    
    def _init_content_system(self):
        """Initialize content system modules."""
        self.logger.info("Initializing Content System...")
        
        # Study Plan Generator
        self._modules["study_plan_generator"] = StudyPlanGenerator()
        
        # Daily Target Manager
        self._modules["daily_target_manager"] = DailyTargetManager()
        
        # Mock Test System
        self._modules["mock_test_system"] = MockTestSystem()
        
        # Milestone Tracker
        self._modules["milestone_tracker"] = MilestoneTracker()
        
        self.logger.info("Content System initialized")
    
    def _init_focus_system(self):
        """Initialize focus system modules."""
        self.logger.info("Initializing Focus System...")
        
        # Behaviour Data Collector - handle permission issues in dev environment
        try:
            data_collector = BehaviourDataCollector()
        except PermissionError:
            # Create with local path for development environment
            data_collector = BehaviourDataCollector(data_dir=Path("./jarvis_data"))
        self._modules["data_collector"] = data_collector
        
        # Behaviour Monitor
        monitor = BehaviourMonitor(
            study_start_hour=self.config.study_start_hour,
            study_end_hour=self.config.study_end_hour
        )
        self._modules["monitor"] = monitor
        
        # Porn Blocker
        self._modules["porn_blocker"] = PornBlocker()
        
        # Pattern Detector
        self._modules["pattern_detector"] = PatternDetector()
        
        # Intervention Executor
        self._modules["intervention_executor"] = InterventionExecutor()
        
        # Pattern Analyzer - requires data_collector
        analyzer = PatternAnalyzer(data_collector=data_collector)
        self._modules["pattern_analyzer"] = analyzer
        
        self.logger.info("Focus System initialized")
    
    # =========================================================================
    # PUBLIC API
    # =========================================================================
    
    def process_study_session(
        self,
        subject: str,
        topic: str,
        questions_correct: int,
        questions_total: int,
        duration_minutes: int
    ) -> Dict:
        """
        Process a complete study session.
        
        This is the main entry point for study sessions.
        It coordinates:
        1. IRT theta update
        2. SM-2 review scheduling
        3. Psychological processing (XP, rewards, achievements)
        4. Milestone checking
        5. Voice announcements
        
        Args:
            subject: Subject name
            topic: Topic name
            questions_correct: Number of correct answers
            questions_total: Total questions attempted
            duration_minutes: Session duration in minutes
        
        Returns:
            Dictionary with session results
        """
        self.last_activity = datetime.now()
        
        results = {
            "subject": subject,
            "topic": topic,
            "questions_correct": questions_correct,
            "questions_total": questions_total,
            "accuracy": questions_correct / questions_total if questions_total > 0 else 0,
            "duration_minutes": duration_minutes,
            "timestamp": self.last_activity.isoformat()
        }
        
        try:
            # 1. Process through psychological engine
            psych_result = self._modules["psychological_engine"].process_session(
                questions_correct=questions_correct,
                questions_total=questions_total,
                duration_minutes=duration_minutes,
                subject=subject,
                topic=topic
            )
            results["xp_earned"] = psych_result.xp_earned
            results["coins_earned"] = psych_result.coins_earned
            results["reward_tier"] = psych_result.reward_tier
            
            # 2. Check achievements
            stats = self._modules["psychological_engine"].get_stats()
            achievements = self._modules["achievement_system"].check_achievements({
                "total_sessions": stats.total_sessions,
                "total_questions": stats.total_questions,
                "current_streak": stats.current_streak,
                "accuracy": stats.total_correct / max(1, stats.total_questions)
            })
            results["new_achievements"] = len(achievements)
            
            # 3. Check milestones
            milestones = self._modules["milestone_tracker"].check_milestones({
                "day": 1,  # Would need to track actual day
                "total_questions": stats.total_questions,
                "current_streak": stats.current_streak
            })
            results["milestones_completed"] = len(milestones)
            
            # 4. Record in data collector
            self._modules["data_collector"].record_session({
                "subject": subject,
                "topic": topic,
                "questions": questions_total,
                "correct": questions_correct,
                "duration_minutes": duration_minutes
            })
            
            # 5. Voice announcement if achievements
            if achievements and self.config.enable_voice:
                for achievement in achievements:
                    message = self._modules["voice_messages"].generate(
                        "achievement_unlock",
                        context={"achievement": achievement.name}
                    )
                    self._modules["voice_engine"].speak(message)
            
        except Exception as e:
            self.errors.append(f"Session processing error: {str(e)}")
            self.logger.error(f"Session processing error: {e}")
            results["error"] = str(e)
        
        return results
    
    def get_daily_plan(self, day_number: int) -> Dict:
        """
        Get study plan for a specific day.
        
        Args:
            day_number: Day number (1-75)
        
        Returns:
            Dictionary with daily plan
        """
        target = self._modules["daily_target_manager"].get_daily_target(day_number)
        
        return {
            "day_number": day_number,
            "targets": [
                {
                    "subject": str(t.subject),
                    "questions": t.target_questions,
                    "time_slot": str(t.time_slot) if hasattr(t, 'time_slot') else "Any"
                }
                for t in target.subject_targets
            ]
        }
    
    def create_mock_test(self, mock_type: str = "MINI", subject: str = None) -> Dict:
        """
        Create a mock test.
        
        Args:
            mock_type: Type of mock (FULL, SUBJECT, MINI)
            subject: Subject for subject-specific mock
        
        Returns:
            Dictionary with mock test info
        """
        mock_type_enum = MockType[mock_type.upper()]
        mock = self._modules["mock_test_system"].create_mock(
            mock_type_enum,
            subject=subject
        )
        
        return {
            "mock_id": mock.id,
            "type": mock_type,
            "subject": subject,
            "questions": mock.total_questions
        }
    
    def get_status(self) -> SystemStatus:
        """
        Get current system status.
        
        Returns:
            SystemStatus with current state and info
        """
        uptime = 0.0
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        return SystemStatus(
            state=self.state,
            modules_loaded=list(self._modules.keys()),
            active_components=self._active_components.copy(),
            errors=self.errors.copy(),
            uptime_seconds=uptime,
            last_activity=self.last_activity
        )
    
    def get_progress(self) -> Dict:
        """
        Get overall user progress.
        
        Returns:
            Dictionary with progress information
        """
        psych_stats = self._modules["psychological_engine"].get_stats()
        
        return {
            "xp": psych_stats.total_xp,
            "coins": psych_stats.total_coins,
            "current_streak": psych_stats.current_streak,
            "longest_streak": psych_stats.longest_streak,
            "total_sessions": psych_stats.total_sessions,
            "total_questions": psych_stats.total_questions,
            "achievements_unlocked": len(self._modules["achievement_system"].get_unlocked()),
            "milestones_completed": len(self._modules["milestone_tracker"].get_completed())
        }
    
    # =========================================================================
    # MODULE ACCESS
    # =========================================================================
    
    def get_module(self, name: str) -> Optional[Any]:
        """
        Get a specific module by name.
        
        Args:
            name: Module name (e.g., "irt_engine", "voice_engine")
        
        Returns:
            Module instance or None if not found
        """
        return self._modules.get(name)
    
    def get_all_modules(self) -> Dict[str, Any]:
        """
        Get all loaded modules.
        
        Returns:
            Dictionary of module name to instance
        """
        return self._modules.copy()


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_jarvis(config: Optional[OrchestratorConfig] = None) -> JarvisOrchestrator:
    """
    Factory function to create and initialize JARVIS.
    
    Args:
        config: Optional configuration
    
    Returns:
        Initialized JarvisOrchestrator instance
    """
    orchestrator = JarvisOrchestrator(config)
    orchestrator.initialize()
    return orchestrator


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Test the orchestrator
    print("=" * 60)
    print("JARVIS ORCHESTRATOR TEST")
    print("=" * 60)
    
    # Create configuration
    config = OrchestratorConfig(
        enable_voice=True,
        enable_monitoring=False,  # Disable for testing
        debug_mode=True
    )
    
    # Create and initialize
    jarvis = create_jarvis(config)
    
    # Check status
    status = jarvis.get_status()
    print(f"\nState: {status.state.value}")
    print(f"Modules loaded: {len(status.modules_loaded)}")
    print(f"Errors: {len(status.errors)}")
    
    # Test session
    print("\n" + "=" * 60)
    print("TEST SESSION")
    print("=" * 60)
    
    result = jarvis.process_study_session(
        subject="Mathematics",
        topic="Algebra",
        questions_correct=18,
        questions_total=20,
        duration_minutes=30
    )
    
    print(f"\nSession result:")
    print(f"  XP earned: {result.get('xp_earned', 0)}")
    print(f"  Coins earned: {result.get('coins_earned', 0)}")
    print(f"  Accuracy: {result.get('accuracy', 0):.1%}")
    
    # Get progress
    progress = jarvis.get_progress()
    print(f"\nProgress:")
    print(f"  Total XP: {progress['xp']}")
    print(f"  Streak: {progress['current_streak']}")
    
    # Stop
    jarvis.stop()
    print("\n" + "=" * 60)
    print("JARVIS STOPPED")
    print("=" * 60)
