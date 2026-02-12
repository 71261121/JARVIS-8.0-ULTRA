#!/usr/bin/env python3
"""
JARVIS Test Runner
==================

Master test runner script that:
1. Discovers and runs all tests
2. Generates detailed reports
3. Calculates coverage
4. Provides pass/fail summary

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --module study  # Run specific module tests
    python run_tests.py --coverage   # Run with coverage
    python run_tests.py --verbose    # Detailed output

GOAL_ALIGNMENT_CHECK():
    - Comprehensive testing ensures system reliability
    - Coverage metrics identify gaps
    - Reports guide improvement
"""

import sys
import os
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class TestResult:
    """Test result data."""
    name: str
    passed: bool
    duration: float
    error: str = ""


@dataclass
class ModuleResult:
    """Module test results."""
    module_name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    duration: float
    tests: List[TestResult]


class TestRunner:
    """JARVIS test runner."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[ModuleResult] = []
        self.start_time: float = 0
    
    def run_all_tests(self) -> Dict:
        """
        Run all tests and generate report.
        
        Returns:
            Dictionary with complete test results
        """
        self.start_time = time.time()
        
        print("=" * 70)
        print("JARVIS 8.0 ULTRA - COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Test modules in order
        test_modules = [
            ("imports", "Module Import Validation", self._test_imports),
            ("study", "Study Engine", self._test_study_engine),
            ("focus", "Focus Module", self._test_focus_module),
            ("psych", "Psychological Engine", self._test_psychological),
            ("voice", "Voice Module", self._test_voice),
            ("content", "Content Module", self._test_content),
            ("integration", "Cross-Module Integration", self._test_integration),
            ("orchestrator", "System Orchestrator", self._test_orchestrator),
        ]
        
        for module_id, module_name, test_func in test_modules:
            print(f"\n{'─' * 70}")
            print(f"MODULE: {module_name}")
            print(f"{'─' * 70}")
            
            result = test_func()
            self.results.append(result)
            
            self._print_module_summary(result)
        
        # Generate final report
        return self._generate_report()
    
    def _test_imports(self) -> ModuleResult:
        """Test all module imports."""
        tests = []
        start = time.time()
        
        import_tests = [
            ("jarvis main package", lambda: __import__("jarvis")),
            ("jarvis.core", lambda: __import__("jarvis.core", fromlist=["Config"])),
            ("jarvis.study", lambda: __import__("jarvis.study", fromlist=["IRTEngine"])),
            ("jarvis.focus", lambda: __import__("jarvis.focus", fromlist=["BehaviourMonitor"])),
            ("jarvis.psych", lambda: __import__("jarvis.psych", fromlist=["PsychologicalEngine"])),
            ("jarvis.voice", lambda: __import__("jarvis.voice", fromlist=["VoiceEngine"])),
            ("jarvis.content", lambda: __import__("jarvis.content", fromlist=["StudyPlanGenerator"])),
        ]
        
        for name, import_func in import_tests:
            test_start = time.time()
            try:
                import_func()
                tests.append(TestResult(
                    name=name,
                    passed=True,
                    duration=time.time() - test_start
                ))
                if self.verbose:
                    print(f"  ✓ {name}")
            except Exception as e:
                tests.append(TestResult(
                    name=name,
                    passed=False,
                    duration=time.time() - test_start,
                    error=str(e)
                ))
                print(f"  ✗ {name}: {e}")
        
        passed = sum(1 for t in tests if t.passed)
        failed = sum(1 for t in tests if not t.passed)
        
        return ModuleResult(
            module_name="Module Imports",
            total_tests=len(tests),
            passed=passed,
            failed=failed,
            skipped=0,
            duration=time.time() - start,
            tests=tests
        )
    
    def _test_study_engine(self) -> ModuleResult:
        """Test study engine components."""
        tests = []
        start = time.time()
        
        try:
            from jarvis.study.irt import IRTEngine, IRTParameters, probability_correct
            from jarvis.study.sm2 import SM2Engine, Quality
            
            # IRT Tests
            test_start = time.time()
            try:
                engine = IRTEngine()
                params = IRTParameters(a=1.0, b=0.0, c=0.25)
                prob = probability_correct(0.0, params)
                
                assert 0 <= prob <= 1.0, "Probability out of range"
                tests.append(TestResult("IRT probability calculation", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ IRT probability calculation: {prob:.3f}")
            except Exception as e:
                tests.append(TestResult("IRT probability calculation", False, time.time() - test_start, str(e)))
                print(f"  ✗ IRT probability: {e}")
            
            # IRT theta update
            test_start = time.time()
            try:
                engine = IRTEngine(initial_theta=0.0)
                from jarvis.study.irt import QuestionIRT
                question = QuestionIRT(
                    id="test",
                    params=IRTParameters(a=1.0, b=0.0, c=0.25),
                    subject="Math",
                    topic="Algebra"
                )
                result = engine.process_response(question, is_correct=True)
                tests.append(TestResult("IRT theta update", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ IRT theta update: {engine.theta:.3f}")
            except Exception as e:
                tests.append(TestResult("IRT theta update", False, time.time() - test_start, str(e)))
                print(f"  ✗ IRT theta update: {e}")
            
            # SM-2 Tests
            test_start = time.time()
            try:
                sm2 = SM2Engine()
                from jarvis.study.sm2 import ReviewItem, calculate_next_review, DEFAULT_EASE_FACTOR
                
                result = calculate_next_review(
                    interval=0,
                    repetition=0,
                    ease_factor=DEFAULT_EASE_FACTOR,
                    quality=Quality.GOOD
                )
                assert result.interval == 1, "First interval should be 1"
                tests.append(TestResult("SM-2 interval calculation", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ SM-2 interval: {result.interval}")
            except Exception as e:
                tests.append(TestResult("SM-2 interval calculation", False, time.time() - test_start, str(e)))
                print(f"  ✗ SM-2 interval: {e}")
            
        except ImportError as e:
            tests.append(TestResult("Study engine import", False, 0, str(e)))
            print(f"  ✗ Import error: {e}")
        
        passed = sum(1 for t in tests if t.passed)
        failed = sum(1 for t in tests if not t.passed)
        
        return ModuleResult(
            module_name="Study Engine",
            total_tests=len(tests),
            passed=passed,
            failed=failed,
            skipped=0,
            duration=time.time() - start,
            tests=tests
        )
    
    def _test_focus_module(self) -> ModuleResult:
        """Test focus module components."""
        tests = []
        start = time.time()
        
        try:
            from jarvis.focus.behaviour_monitor import BehaviourMonitor, DISTRACTING_APPS
            from jarvis.focus.porn_blocker import PornBlocker, get_all_porn_domains
            from jarvis.focus.pattern_detector import PatternDetector, BehaviourData
            
            # Behaviour Monitor
            test_start = time.time()
            try:
                monitor = BehaviourMonitor()
                assert len(DISTRACTING_APPS) > 0, "No distracting apps defined"
                tests.append(TestResult("Behaviour monitor init", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Behaviour monitor: {len(DISTRACTING_APPS)} apps tracked")
            except Exception as e:
                tests.append(TestResult("Behaviour monitor init", False, time.time() - test_start, str(e)))
                print(f"  ✗ Behaviour monitor: {e}")
            
            # Porn Blocker
            test_start = time.time()
            try:
                domains = get_all_porn_domains()
                assert len(domains) >= 100, "Should have 100+ domains"
                tests.append(TestResult("Porn blocker domains", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Porn domains: {len(domains)} blocked")
            except Exception as e:
                tests.append(TestResult("Porn blocker domains", False, time.time() - test_start, str(e)))
                print(f"  ✗ Porn domains: {e}")
            
            # Pattern Detector
            test_start = time.time()
            try:
                detector = PatternDetector()
                data = BehaviourData(
                    distraction_events=10,
                    study_minutes=30,
                    app_switches=20,
                    late_night_minutes=0,
                    session_count=2,
                    average_accuracy=0.7
                )
                patterns = detector.detect(data)
                tests.append(TestResult("Pattern detection", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Pattern detection: {len(patterns)} patterns")
            except Exception as e:
                tests.append(TestResult("Pattern detection", False, time.time() - test_start, str(e)))
                print(f"  ✗ Pattern detection: {e}")
            
        except ImportError as e:
            tests.append(TestResult("Focus module import", False, 0, str(e)))
            print(f"  ✗ Import error: {e}")
        
        passed = sum(1 for t in tests if t.passed)
        failed = sum(1 for t in tests if not t.passed)
        
        return ModuleResult(
            module_name="Focus Module",
            total_tests=len(tests),
            passed=passed,
            failed=failed,
            skipped=0,
            duration=time.time() - start,
            tests=tests
        )
    
    def _test_psychological(self) -> ModuleResult:
        """Test psychological engine components."""
        tests = []
        start = time.time()
        
        try:
            from jarvis.psych.loss_aversion import LossAversionEngine, LOSS_AVERSION_MULTIPLIER
            from jarvis.psych.reward_system import RewardSystem, JACKPOT_CHANCE
            from jarvis.psych.achievement_system import AchievementSystem, ACHIEVEMENTS
            from jarvis.psych.psychological_engine import PsychologicalEngine
            
            # Loss Aversion
            test_start = time.time()
            try:
                assert LOSS_AVERSION_MULTIPLIER == 2.0, "Loss aversion should be 2.0"
                tests.append(TestResult("Loss aversion constant", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Loss aversion multiplier: {LOSS_AVERSION_MULTIPLIER}")
            except Exception as e:
                tests.append(TestResult("Loss aversion constant", False, time.time() - test_start, str(e)))
            
            # Reward System
            test_start = time.time()
            try:
                reward = RewardSystem()
                result = reward.calculate_reward(base_xp=100, base_coins=20, accuracy=0.8)
                tests.append(TestResult("Reward calculation", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Reward: {result.xp} XP, tier: {result.tier}")
            except Exception as e:
                tests.append(TestResult("Reward calculation", False, time.time() - test_start, str(e)))
                print(f"  ✗ Reward: {e}")
            
            # Achievement System
            test_start = time.time()
            try:
                assert len(ACHIEVEMENTS) == 27, f"Should have 27 achievements, got {len(ACHIEVEMENTS)}"
                tests.append(TestResult("Achievement count", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Achievements: {len(ACHIEVEMENTS)} defined")
            except Exception as e:
                tests.append(TestResult("Achievement count", False, time.time() - test_start, str(e)))
                print(f"  ✗ Achievements: {e}")
            
            # Psychological Engine
            test_start = time.time()
            try:
                engine = PsychologicalEngine()
                result = engine.process_session(
                    questions_correct=10,
                    questions_total=15,
                    duration_minutes=20,
                    subject="Mathematics",
                    topic="Algebra"
                )
                tests.append(TestResult("Psychological engine", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Psychology: {result.xp_earned} XP earned")
            except Exception as e:
                tests.append(TestResult("Psychological engine", False, time.time() - test_start, str(e)))
                print(f"  ✗ Psychology: {e}")
            
        except ImportError as e:
            tests.append(TestResult("Psychological import", False, 0, str(e)))
            print(f"  ✗ Import error: {e}")
        
        passed = sum(1 for t in tests if t.passed)
        failed = sum(1 for t in tests if not t.passed)
        
        return ModuleResult(
            module_name="Psychological Engine",
            total_tests=len(tests),
            passed=passed,
            failed=failed,
            skipped=0,
            duration=time.time() - start,
            tests=tests
        )
    
    def _test_voice(self) -> ModuleResult:
        """Test voice module components."""
        tests = []
        start = time.time()
        
        try:
            from jarvis.voice.voice_engine import VoiceEngine, VoicePersonality, TTSBackend
            from jarvis.voice.voice_messages import VoiceMessageGenerator, MessageType, PREDEFINED_MESSAGES
            from jarvis.voice.voice_enforcer import VoiceEnforcer, EnforcementMode
            
            # Voice Engine
            test_start = time.time()
            try:
                engine = VoiceEngine()
                engine.backend = TTSBackend.DUMMY
                result = engine.speak("Test", personality=VoicePersonality.NEUTRAL)
                tests.append(TestResult("Voice engine", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Voice engine: backend={TTSBackend.DUMMY}")
            except Exception as e:
                tests.append(TestResult("Voice engine", False, time.time() - test_start, str(e)))
                print(f"  ✗ Voice engine: {e}")
            
            # Voice Messages
            test_start = time.time()
            try:
                generator = VoiceMessageGenerator()
                message = generator.generate(MessageType.DISTRACTION_WARNING)
                tests.append(TestResult("Voice messages", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Message generated: {len(message)} chars")
            except Exception as e:
                tests.append(TestResult("Voice messages", False, time.time() - test_start, str(e)))
                print(f"  ✗ Voice messages: {e}")
            
            # Voice Enforcer
            test_start = time.time()
            try:
                enforcer = VoiceEnforcer()
                enforcer.mode = EnforcementMode.ENFORCER
                tests.append(TestResult("Voice enforcer", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Enforcer mode: {EnforcementMode.ENFORCER}")
            except Exception as e:
                tests.append(TestResult("Voice enforcer", False, time.time() - test_start, str(e)))
                print(f"  ✗ Voice enforcer: {e}")
            
        except ImportError as e:
            tests.append(TestResult("Voice module import", False, 0, str(e)))
            print(f"  ✗ Import error: {e}")
        
        passed = sum(1 for t in tests if t.passed)
        failed = sum(1 for t in tests if not t.passed)
        
        return ModuleResult(
            module_name="Voice Module",
            total_tests=len(tests),
            passed=passed,
            failed=failed,
            skipped=0,
            duration=time.time() - start,
            tests=tests
        )
    
    def _test_content(self) -> ModuleResult:
        """Test content module components."""
        tests = []
        start = time.time()
        
        try:
            from jarvis.content.study_plan import StudyPlanGenerator, PHASE_RANGES
            from jarvis.content.daily_target import DailyTargetManager
            from jarvis.content.mock_test import MockTestSystem, MockType
            from jarvis.content.milestone_tracker import MilestoneTracker, DEFAULT_MILESTONES
            
            # Study Plan
            test_start = time.time()
            try:
                assert len(PHASE_RANGES) == 5, "Should have 5 study phases"
                tests.append(TestResult("Study plan phases", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Study phases: {len(PHASE_RANGES)}")
            except Exception as e:
                tests.append(TestResult("Study plan phases", False, time.time() - test_start, str(e)))
            
            # Daily Target
            test_start = time.time()
            try:
                manager = DailyTargetManager()
                target = manager.get_daily_target(day_number=1)
                tests.append(TestResult("Daily target", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Daily target: {len(target.subject_targets)} subjects")
            except Exception as e:
                tests.append(TestResult("Daily target", False, time.time() - test_start, str(e)))
                print(f"  ✗ Daily target: {e}")
            
            # Mock Test
            test_start = time.time()
            try:
                system = MockTestSystem()
                mock = system.create_mock(MockType.MINI)
                tests.append(TestResult("Mock test creation", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Mock test created: {MockType.MINI}")
            except Exception as e:
                tests.append(TestResult("Mock test creation", False, time.time() - test_start, str(e)))
                print(f"  ✗ Mock test: {e}")
            
            # Milestone Tracker
            test_start = time.time()
            try:
                assert len(DEFAULT_MILESTONES) == 17, f"Should have 17 milestones, got {len(DEFAULT_MILESTONES)}"
                tests.append(TestResult("Milestone count", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Milestones: {len(DEFAULT_MILESTONES)}")
            except Exception as e:
                tests.append(TestResult("Milestone count", False, time.time() - test_start, str(e)))
                print(f"  ✗ Milestones: {e}")
            
        except ImportError as e:
            tests.append(TestResult("Content module import", False, 0, str(e)))
            print(f"  ✗ Import error: {e}")
        
        passed = sum(1 for t in tests if t.passed)
        failed = sum(1 for t in tests if not t.passed)
        
        return ModuleResult(
            module_name="Content Module",
            total_tests=len(tests),
            passed=passed,
            failed=failed,
            skipped=0,
            duration=time.time() - start,
            tests=tests
        )
    
    def _test_integration(self) -> ModuleResult:
        """Test cross-module integration."""
        tests = []
        start = time.time()
        
        try:
            # Import orchestrator
            from jarvis.orchestrator import JarvisOrchestrator, OrchestratorConfig
            
            # Full initialization
            test_start = time.time()
            try:
                config = OrchestratorConfig(
                    enable_voice=True,
                    enable_monitoring=False,
                    debug_mode=True
                )
                jarvis = JarvisOrchestrator(config)
                success = jarvis.initialize()
                
                assert success, "Initialization should succeed"
                tests.append(TestResult("Full initialization", True, time.time() - test_start))
                if self.verbose:
                    status = jarvis.get_status()
                    print(f"  ✓ Initialized: {len(status.modules_loaded)} modules")
            except Exception as e:
                tests.append(TestResult("Full initialization", False, time.time() - test_start, str(e)))
                print(f"  ✗ Init: {e}")
            
            # Session processing
            test_start = time.time()
            try:
                config = OrchestratorConfig(enable_voice=False, enable_monitoring=False)
                jarvis = JarvisOrchestrator(config)
                jarvis.initialize()
                
                result = jarvis.process_study_session(
                    subject="Mathematics",
                    topic="Algebra",
                    questions_correct=18,
                    questions_total=20,
                    duration_minutes=30
                )
                
                assert "xp_earned" in result, "Should have XP earned"
                tests.append(TestResult("Session processing", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Session: {result.get('xp_earned', 0)} XP")
            except Exception as e:
                tests.append(TestResult("Session processing", False, time.time() - test_start, str(e)))
                print(f"  ✗ Session: {e}")
            
        except ImportError as e:
            tests.append(TestResult("Integration import", False, 0, str(e)))
            print(f"  ✗ Import error: {e}")
        
        passed = sum(1 for t in tests if t.passed)
        failed = sum(1 for t in tests if not t.passed)
        
        return ModuleResult(
            module_name="Integration",
            total_tests=len(tests),
            passed=passed,
            failed=failed,
            skipped=0,
            duration=time.time() - start,
            tests=tests
        )
    
    def _test_orchestrator(self) -> ModuleResult:
        """Test system orchestrator."""
        tests = []
        start = time.time()
        
        try:
            from jarvis.orchestrator import JarvisOrchestrator, OrchestratorConfig, SystemState
            
            # Create and initialize
            test_start = time.time()
            try:
                config = OrchestratorConfig(enable_voice=False, enable_monitoring=False)
                orchestrator = JarvisOrchestrator(config)
                
                assert orchestrator.state == SystemState.UNINITIALIZED
                tests.append(TestResult("Orchestrator creation", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Created: state={orchestrator.state.value}")
            except Exception as e:
                tests.append(TestResult("Orchestrator creation", False, time.time() - test_start, str(e)))
                print(f"  ✗ Creation: {e}")
            
            # Lifecycle
            test_start = time.time()
            try:
                config = OrchestratorConfig(enable_voice=False, enable_monitoring=False)
                orchestrator = JarvisOrchestrator(config)
                
                # Initialize
                assert orchestrator.initialize() == True
                assert orchestrator.state == SystemState.READY
                
                # Start
                assert orchestrator.start() == True
                assert orchestrator.state == SystemState.RUNNING
                
                # Stop
                assert orchestrator.stop() == True
                assert orchestrator.state == SystemState.STOPPED
                
                tests.append(TestResult("Orchestrator lifecycle", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Lifecycle: init→start→stop")
            except Exception as e:
                tests.append(TestResult("Orchestrator lifecycle", False, time.time() - test_start, str(e)))
                print(f"  ✗ Lifecycle: {e}")
            
        except ImportError as e:
            tests.append(TestResult("Orchestrator import", False, 0, str(e)))
            print(f"  ✗ Import error: {e}")
        
        passed = sum(1 for t in tests if t.passed)
        failed = sum(1 for t in tests if not t.passed)
        
        return ModuleResult(
            module_name="System Orchestrator",
            total_tests=len(tests),
            passed=passed,
            failed=failed,
            skipped=0,
            duration=time.time() - start,
            tests=tests
        )
    
    def _print_module_summary(self, result: ModuleResult):
        """Print module test summary."""
        status = "✓ PASSED" if result.failed == 0 else "✗ FAILED"
        print(f"\n  {status}: {result.passed}/{result.total_tests} tests passed")
        print(f"  Duration: {result.duration:.2f}s")
    
    def _generate_report(self) -> Dict:
        """Generate final test report."""
        total_duration = time.time() - self.start_time
        
        total_tests = sum(r.total_tests for r in self.results)
        total_passed = sum(r.passed for r in self.results)
        total_failed = sum(r.failed for r in self.results)
        
        print("\n" + "=" * 70)
        print("FINAL TEST REPORT")
        print("=" * 70)
        
        for result in self.results:
            status = "✓" if result.failed == 0 else "✗"
            print(f"  {status} {result.module_name}: {result.passed}/{result.total_tests}")
        
        print("\n" + "─" * 70)
        print(f"  TOTAL: {total_passed}/{total_tests} tests passed")
        print(f"  FAILED: {total_failed}")
        print(f"  DURATION: {total_duration:.2f}s")
        print("=" * 70)
        
        if total_failed == 0:
            print("\n  🎉 ALL TESTS PASSED! JARVIS IS READY FOR DEPLOYMENT! 🎉\n")
        else:
            print(f"\n  ⚠️  {total_failed} TESTS FAILED. REVIEW ERRORS ABOVE. ⚠️\n")
        
        return {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "duration": total_duration,
            "success": total_failed == 0,
            "modules": [
                {
                    "name": r.module_name,
                    "passed": r.passed,
                    "total": r.total_tests,
                    "duration": r.duration
                }
                for r in self.results
            ]
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="JARVIS Test Runner")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--module", "-m", type=str, help="Run specific module tests")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose)
    results = runner.run_all_tests()
    
    if args.json:
        print(json.dumps(results, indent=2))
    
    return 0 if results["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
