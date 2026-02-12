"""
JARVIS Module Import Validation Tests
======================================

This test module validates that ALL JARVIS modules can be imported
without errors. It checks:
1. Main package imports
2. Submodule imports
3. Class exports
4. Function exports

GOAL_ALIGNMENT_CHECK():
    - Import errors = System cannot start = Exam failure
    - All modules must import cleanly
    - Missing dependencies must be documented

CRITICAL: If any import fails, the system cannot function.
"""

import pytest
import sys
from pathlib import Path
from typing import List, Tuple

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestModuleImports:
    """Test that all modules can be imported."""
    
    def test_main_package_import(self):
        """Test main jarvis package import."""
        import jarvis
        assert hasattr(jarvis, '__version__')
        assert hasattr(jarvis, '__author__')
        assert hasattr(jarvis, '__target_exam__')
        assert jarvis.__version__ == "1.0.0"
    
    def test_check_dependencies_function(self):
        """Test dependency checking function."""
        import jarvis
        deps = jarvis.check_dependencies()
        assert isinstance(deps, dict)
        assert "python_version" in deps
        assert deps["python_version"] is True  # We're running Python 3.8+
    
    def test_check_root_access_function(self):
        """Test root access checking function."""
        import jarvis
        result = jarvis.check_root_access()
        assert isinstance(result, bool)
        # In dev environment, should be False
        # In Termux with root, should be True


class TestCoreModuleImports:
    """Test core module imports."""
    
    def test_core_package_import(self):
        """Test core package import."""
        from jarvis import core
        assert core is not None
    
    def test_config_import(self):
        """Test config module import."""
        from jarvis.core import config
        assert hasattr(config, 'Config')
        assert hasattr(config, 'load_config')
    
    def test_database_import(self):
        """Test database module import."""
        from jarvis.core import database
        assert hasattr(database, 'Database')
        assert hasattr(database, 'init_database')
    
    def test_logging_import(self):
        """Test logging module import."""
        from jarvis.core import logging_setup
        assert hasattr(logging_setup, 'setup_logging')
        assert hasattr(logging_setup, 'get_logger')
    
    def test_core_exports(self):
        """Test core __init__ exports."""
        from jarvis.core import Config, load_config, Database, init_database
        from jarvis.core import setup_logging, get_logger
        assert Config is not None
        assert load_config is not None
        assert Database is not None
        assert init_database is not None


class TestStudyModuleImports:
    """Test study module imports."""
    
    def test_study_package_import(self):
        """Test study package import."""
        from jarvis import study
        assert study is not None
    
    def test_irt_import(self):
        """Test IRT module import."""
        from jarvis.study import irt
        assert hasattr(irt, 'IRTEngine')
        assert hasattr(irt, 'probability_correct')
        assert hasattr(irt, 'update_theta')
        assert hasattr(irt, 'select_optimal_question')
    
    def test_sm2_import(self):
        """Test SM-2 module import."""
        from jarvis.study import sm2
        assert hasattr(sm2, 'SM2Engine')
        assert hasattr(sm2, 'calculate_next_review')
        assert hasattr(sm2, 'calculate_ease_factor')
    
    def test_question_bank_import(self):
        """Test question bank module import."""
        from jarvis.study import question_bank
        assert hasattr(question_bank, 'QuestionBank')
        assert hasattr(question_bank, 'Question')
        assert hasattr(question_bank, 'Topic')
    
    def test_session_import(self):
        """Test session module import."""
        from jarvis.study import session
        assert hasattr(session, 'SessionManager')
        assert hasattr(session, 'Session')
        assert hasattr(session, 'SessionConfig')
    
    def test_study_exports(self):
        """Test study __init__ exports."""
        from jarvis.study import (
            IRTEngine, SM2Engine, QuestionBank, SessionManager,
            THETA_MIN, THETA_MAX, MIN_EASE_FACTOR, DEFAULT_EASE_FACTOR
        )
        assert IRTEngine is not None
        assert SM2Engine is not None
        assert QuestionBank is not None
        assert SessionManager is not None


class TestFocusModuleImports:
    """Test focus module imports."""
    
    def test_focus_package_import(self):
        """Test focus package import."""
        from jarvis import focus
        assert focus is not None
    
    def test_root_access_import(self):
        """Test root access module import."""
        from jarvis.focus import root_access
        assert hasattr(root_access, 'RootAccess')
        assert hasattr(root_access, 'DISTRACTING_APPS')
    
    def test_behaviour_monitor_import(self):
        """Test behaviour monitor import."""
        from jarvis.focus import behaviour_monitor
        assert hasattr(behaviour_monitor, 'BehaviourMonitor')
        assert hasattr(behaviour_monitor, 'DISTRACTING_APPS_MONITOR')
        assert hasattr(behaviour_monitor, 'STUDY_APPS')
    
    def test_porn_blocker_import(self):
        """Test porn blocker import."""
        from jarvis.focus import porn_blocker
        assert hasattr(porn_blocker, 'PornBlocker')
        assert hasattr(porn_blocker, 'CORE_PORN_DOMAINS')
        assert hasattr(porn_blocker, 'ADDITIONAL_PORN_DOMAINS')
    
    def test_pattern_detector_import(self):
        """Test pattern detector import."""
        from jarvis.focus import pattern_detector
        assert hasattr(pattern_detector, 'PatternDetector')
        assert hasattr(pattern_detector, 'PatternType')
        assert hasattr(pattern_detector, 'PatternSeverity')
    
    def test_behaviour_data_collector_import(self):
        """Test behaviour data collector import."""
        from jarvis.focus import behaviour_data_collector
        assert hasattr(behaviour_data_collector, 'BehaviourDataCollector')
        assert hasattr(behaviour_data_collector, 'SessionRecord')
        assert hasattr(behaviour_data_collector, 'DailySummary')
    
    def test_intervention_executor_import(self):
        """Test intervention executor import."""
        from jarvis.focus import intervention_executor
        assert hasattr(intervention_executor, 'InterventionExecutor')
        assert hasattr(intervention_executor, 'InterventionRecord')
        assert hasattr(intervention_executor, 'InterventionStats')
    
    def test_pattern_analyzer_import(self):
        """Test pattern analyzer import."""
        from jarvis.focus import pattern_analyzer
        assert hasattr(pattern_analyzer, 'PatternAnalyzer')
        assert hasattr(pattern_analyzer, 'create_pattern_analyzer')
    
    def test_focus_exports(self):
        """Test focus __init__ exports."""
        from jarvis.focus import (
            ROOT_AVAILABLE, check_root,
            RootAccess, BehaviourMonitor, PornBlocker,
            PatternDetector, InterventionExecutor, PatternAnalyzer,
            create_monitor, create_porn_blocker, create_full_protection_system
        )
        assert BehaviourMonitor is not None
        assert PornBlocker is not None
        assert PatternAnalyzer is not None


class TestPsychModuleImports:
    """Test psychological module imports."""
    
    def test_psych_package_import(self):
        """Test psych package import."""
        from jarvis import psych
        assert psych is not None
    
    def test_loss_aversion_import(self):
        """Test loss aversion module import."""
        from jarvis.psych import loss_aversion
        assert hasattr(loss_aversion, 'LossAversionEngine')
        assert hasattr(loss_aversion, 'LOSS_AVERSION_MULTIPLIER')
    
    def test_reward_system_import(self):
        """Test reward system import."""
        from jarvis.psych import reward_system
        assert hasattr(reward_system, 'RewardSystem')
        assert hasattr(reward_system, 'JACKPOT_CHANCE')
    
    def test_achievement_system_import(self):
        """Test achievement system import."""
        from jarvis.psych import achievement_system
        assert hasattr(achievement_system, 'AchievementSystem')
        assert hasattr(achievement_system, 'AchievementTier')
        assert hasattr(achievement_system, 'ACHIEVEMENTS')
    
    def test_psychological_engine_import(self):
        """Test psychological engine import."""
        from jarvis.psych import psychological_engine
        assert hasattr(psychological_engine, 'PsychologicalEngine')
        assert hasattr(psychological_engine, 'create_psychological_engine')
    
    def test_psych_exports(self):
        """Test psych __init__ exports."""
        from jarvis.psych import (
            LossAversionEngine, RewardSystem, AchievementSystem,
            PsychologicalEngine, LOSS_AVERSION_MULTIPLIER, JACKPOT_CHANCE
        )
        assert LossAversionEngine is not None
        assert RewardSystem is not None
        assert AchievementSystem is not None
        assert PsychologicalEngine is not None


class TestVoiceModuleImports:
    """Test voice module imports."""
    
    def test_voice_package_import(self):
        """Test voice package import."""
        from jarvis import voice
        assert voice is not None
    
    def test_voice_engine_import(self):
        """Test voice engine import."""
        from jarvis.voice import voice_engine
        assert hasattr(voice_engine, 'VoiceEngine')
        assert hasattr(voice_engine, 'VoicePersonality')
        assert hasattr(voice_engine, 'TTSBackend')
    
    def test_voice_messages_import(self):
        """Test voice messages import."""
        from jarvis.voice import voice_messages
        assert hasattr(voice_messages, 'VoiceMessageGenerator')
        assert hasattr(voice_messages, 'MessageType')
        assert hasattr(voice_messages, 'MessageIntensity')
        assert hasattr(voice_messages, 'PREDEFINED_MESSAGES')
    
    def test_voice_enforcer_import(self):
        """Test voice enforcer import."""
        from jarvis.voice import voice_enforcer
        assert hasattr(voice_enforcer, 'VoiceEnforcer')
        assert hasattr(voice_enforcer, 'EnforcementMode')
    
    def test_voice_scheduler_import(self):
        """Test voice scheduler import."""
        from jarvis.voice import voice_scheduler
        assert hasattr(voice_scheduler, 'VoiceScheduler')
        assert hasattr(voice_scheduler, 'ScheduleType')
    
    def test_voice_exports(self):
        """Test voice __init__ exports."""
        from jarvis.voice import (
            VoiceEngine, VoiceMessageGenerator, VoiceEnforcer, VoiceScheduler,
            VoicePersonality, MessageType, EnforcementMode, create_voice_engine
        )
        assert VoiceEngine is not None
        assert VoiceMessageGenerator is not None
        assert VoiceEnforcer is not None
        assert VoiceScheduler is not None


class TestContentModuleImports:
    """Test content module imports."""
    
    def test_content_package_import(self):
        """Test content package import."""
        from jarvis import content
        assert content is not None
    
    def test_study_plan_import(self):
        """Test study plan import."""
        from jarvis.content import study_plan
        assert hasattr(study_plan, 'StudyPlanGenerator')
        assert hasattr(study_plan, 'StudyPhase')
        assert hasattr(study_plan, 'PHASE_RANGES')
    
    def test_daily_target_import(self):
        """Test daily target import."""
        from jarvis.content import daily_target
        assert hasattr(daily_target, 'DailyTargetManager')
        assert hasattr(daily_target, 'TimeSlot')
    
    def test_mock_test_import(self):
        """Test mock test import."""
        from jarvis.content import mock_test
        assert hasattr(mock_test, 'MockTestSystem')
        assert hasattr(mock_test, 'MockType')
        assert hasattr(mock_test, 'EXAM_STRUCTURE')
    
    def test_milestone_tracker_import(self):
        """Test milestone tracker import."""
        from jarvis.content import milestone_tracker
        assert hasattr(milestone_tracker, 'MilestoneTracker')
        assert hasattr(milestone_tracker, 'DEFAULT_MILESTONES')
    
    def test_content_exports(self):
        """Test content __init__ exports."""
        from jarvis.content import (
            StudyPlanGenerator, DailyTargetManager, MockTestSystem, MilestoneTracker,
            StudyPhase, MockType, DEFAULT_MILESTONES, create_study_plan
        )
        assert StudyPlanGenerator is not None
        assert DailyTargetManager is not None
        assert MockTestSystem is not None
        assert MilestoneTracker is not None


class TestUIModuleImports:
    """Test UI module imports."""
    
    def test_ui_package_import(self):
        """Test UI package import."""
        from jarvis import ui
        assert ui is not None
    
    def test_app_import(self):
        """Test app module import."""
        from jarvis.ui import app
        assert hasattr(app, 'JarvisApp')
    
    def test_screens_import(self):
        """Test screens module import."""
        from jarvis.ui import screens
        assert hasattr(screens, 'DashboardScreen')
        assert hasattr(screens, 'StudyScreen')
        assert hasattr(screens, 'ProgressScreen')
    
    def test_focus_screen_import(self):
        """Test focus screen import."""
        from jarvis.ui import focus_screen
        assert hasattr(focus_screen, 'FocusScreen')
    
    def test_pattern_screen_import(self):
        """Test pattern screen import."""
        from jarvis.ui import pattern_screen
        assert hasattr(pattern_screen, 'PatternScreen')
    
    def test_ui_exports(self):
        """Test UI __init__ exports."""
        from jarvis.ui import (
            JarvisApp, DashboardScreen, StudyScreen,
            ProgressScreen, FocusScreen, PatternScreen
        )
        assert JarvisApp is not None


class TestUtilsModuleImports:
    """Test utilities module imports."""
    
    def test_utils_package_import(self):
        """Test utils package import."""
        from jarvis import utils
        assert utils is not None
    
    def test_time_utils_import(self):
        """Test time utilities import."""
        from jarvis.utils import time_utils
        assert time_utils is not None
    
    def test_validation_import(self):
        """Test validation utilities import."""
        from jarvis.utils import validation
        assert validation is not None
    
    def test_formatting_import(self):
        """Test formatting utilities import."""
        from jarvis.utils import formatting
        assert formatting is not None
    
    def test_file_utils_import(self):
        """Test file utilities import."""
        from jarvis.utils import file_utils
        assert file_utils is not None


class TestConstantsValidation:
    """Test that all constants are properly defined."""
    
    def test_irt_constants(self):
        """Test IRT constants are valid."""
        from jarvis.study.irt import THETA_MIN, THETA_MAX, D_SCALING, SE_TARGET
        
        assert THETA_MIN == -4.0
        assert THETA_MAX == 4.0
        assert D_SCALING == 1.7
        assert 0 < SE_TARGET < 1.0
    
    def test_sm2_constants(self):
        """Test SM-2 constants are valid."""
        from jarvis.study.sm2 import (
            MIN_EASE_FACTOR, DEFAULT_EASE_FACTOR, MAX_EASE_FACTOR,
            INTERVAL_FIRST, INTERVAL_SECOND
        )
        
        assert MIN_EASE_FACTOR == 1.3
        assert DEFAULT_EASE_FACTOR == 2.5
        assert MAX_EASE_FACTOR == 3.0
        assert INTERVAL_FIRST == 1
        assert INTERVAL_SECOND == 6
    
    def test_psychology_constants(self):
        """Test psychology constants are valid."""
        from jarvis.psych.loss_aversion import LOSS_AVERSION_MULTIPLIER
        from jarvis.psych.reward_system import JACKPOT_CHANCE, BONUS_CHANCE
        
        assert LOSS_AVERSION_MULTIPLIER == 2.0
        assert 0 < JACKPOT_CHANCE < 0.1
        assert 0 < BONUS_CHANCE < 0.3
    
    def test_focus_constants(self):
        """Test focus constants are valid."""
        from jarvis.focus.behaviour_monitor import (
            DEFAULT_POLL_INTERVAL, DEFAULT_STUDY_START, DEFAULT_STUDY_END
        )
        
        assert DEFAULT_POLL_INTERVAL == 1.0
        assert DEFAULT_STUDY_START == 6
        assert DEFAULT_STUDY_END == 22
    
    def test_content_constants(self):
        """Test content constants are valid."""
        from jarvis.content.study_plan import PHASE_RANGES, SUBJECT_WEIGHTAGE
        
        assert len(PHASE_RANGES) == 5  # 5 phases
        assert "MATHEMATICS" in SUBJECT_WEIGHTAGE


class TestClassInstantiation:
    """Test that key classes can be instantiated."""
    
    def test_irt_engine_instantiation(self):
        """Test IRT engine can be created."""
        from jarvis.study.irt import IRTEngine
        engine = IRTEngine()
        assert engine is not None
    
    def test_sm2_engine_instantiation(self):
        """Test SM-2 engine can be created."""
        from jarvis.study.sm2 import SM2Engine
        engine = SM2Engine()
        assert engine is not None
    
    def test_question_bank_instantiation(self):
        """Test question bank can be created."""
        from jarvis.study.question_bank import QuestionBank
        bank = QuestionBank()
        assert bank is not None
    
    def test_loss_aversion_engine_instantiation(self):
        """Test loss aversion engine can be created."""
        from jarvis.psych.loss_aversion import LossAversionEngine
        engine = LossAversionEngine()
        assert engine is not None
    
    def test_reward_system_instantiation(self):
        """Test reward system can be created."""
        from jarvis.psych.reward_system import RewardSystem
        system = RewardSystem()
        assert system is not None
    
    def test_achievement_system_instantiation(self):
        """Test achievement system can be created."""
        from jarvis.psych.achievement_system import AchievementSystem
        system = AchievementSystem()
        assert system is not None
    
    def test_psychological_engine_instantiation(self):
        """Test psychological engine can be created."""
        from jarvis.psych.psychological_engine import PsychologicalEngine
        engine = PsychologicalEngine()
        assert engine is not None
    
    def test_voice_engine_instantiation(self):
        """Test voice engine can be created."""
        from jarvis.voice.voice_engine import VoiceEngine
        engine = VoiceEngine()
        assert engine is not None
    
    def test_voice_message_generator_instantiation(self):
        """Test voice message generator can be created."""
        from jarvis.voice.voice_messages import VoiceMessageGenerator
        generator = VoiceMessageGenerator()
        assert generator is not None
    
    def test_voice_enforcer_instantiation(self):
        """Test voice enforcer can be created."""
        from jarvis.voice.voice_enforcer import VoiceEnforcer
        enforcer = VoiceEnforcer()
        assert enforcer is not None
    
    def test_voice_scheduler_instantiation(self):
        """Test voice scheduler can be created."""
        from jarvis.voice.voice_scheduler import VoiceScheduler
        scheduler = VoiceScheduler()
        assert scheduler is not None
    
    def test_study_plan_generator_instantiation(self):
        """Test study plan generator can be created."""
        from jarvis.content.study_plan import StudyPlanGenerator
        generator = StudyPlanGenerator()
        assert generator is not None
    
    def test_daily_target_manager_instantiation(self):
        """Test daily target manager can be created."""
        from jarvis.content.daily_target import DailyTargetManager
        manager = DailyTargetManager()
        assert manager is not None
    
    def test_mock_test_system_instantiation(self):
        """Test mock test system can be created."""
        from jarvis.content.mock_test import MockTestSystem
        system = MockTestSystem()
        assert system is not None
    
    def test_milestone_tracker_instantiation(self):
        """Test milestone tracker can be created."""
        from jarvis.content.milestone_tracker import MilestoneTracker
        tracker = MilestoneTracker()
        assert tracker is not None


# Run import validation
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
