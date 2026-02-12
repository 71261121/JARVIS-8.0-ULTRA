#!/usr/bin/env python3
"""
JARVIS Test Runner - Fixed Version
===================================

Master test runner with correct API usage.
"""

import sys
import os
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class TestResult:
    name: str
    passed: bool
    duration: float
    error: str = ""


@dataclass
class ModuleResult:
    module_name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    duration: float
    tests: List[TestResult]


class TestRunner:
    """JARVIS test runner with correct API usage."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[ModuleResult] = []
        self.start_time: float = 0
    
    def run_all_tests(self) -> Dict:
        """Run all tests and generate report."""
        self.start_time = time.time()
        
        print("=" * 70)
        print("JARVIS 8.0 ULTRA - COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        test_modules = [
            ("imports", "Module Import Validation", self._test_imports),
            ("study", "Study Engine", self._test_study_engine),
            ("focus", "Focus Module", self._test_focus_module),
            ("psych", "Psychological Engine", self._test_psychological),
            ("voice", "Voice Module", self._test_voice),
            ("content", "Content Module", self._test_content),
            ("orchestrator", "System Orchestrator", self._test_orchestrator),
        ]
        
        for module_id, module_name, test_func in test_modules:
            print(f"\n{'─' * 70}")
            print(f"MODULE: {module_name}")
            print(f"{'─' * 70}")
            
            result = test_func()
            self.results.append(result)
            self._print_module_summary(result)
        
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
                tests.append(TestResult(name=name, passed=True, duration=time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ {name}")
            except Exception as e:
                tests.append(TestResult(name=name, passed=False, duration=time.time() - test_start, error=str(e)))
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
        """Test study engine with correct API."""
        tests = []
        start = time.time()
        
        try:
            from jarvis.study.irt import IRTEngine, IRTParameters, probability_correct
            from jarvis.study.sm2 import SM2Engine, Quality, calculate_next_review, DEFAULT_EASE_FACTOR
            
            # IRT probability test (correct API)
            test_start = time.time()
            try:
                params = IRTParameters(difficulty=0.0, discrimination=1.0, guessing=0.25)
                prob = probability_correct(0.0, params)
                assert 0 <= prob <= 1.0
                tests.append(TestResult("IRT probability calculation", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ IRT probability: {prob:.3f}")
            except Exception as e:
                tests.append(TestResult("IRT probability calculation", False, time.time() - test_start, str(e)))
                print(f"  ✗ IRT probability: {e}")
            
            # IRT theta update (correct API)
            test_start = time.time()
            try:
                from jarvis.study.irt import update_theta
                params = IRTParameters(difficulty=0.0, discrimination=1.0, guessing=0.25)
                result = update_theta(0.0, params, is_correct=True)
                tests.append(TestResult("IRT theta update", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ IRT theta update: {result.theta_after:.3f}")
            except Exception as e:
                tests.append(TestResult("IRT theta update", False, time.time() - test_start, str(e)))
                print(f"  ✗ IRT theta update: {e}")
            
            # SM-2 interval test (correct API)
            test_start = time.time()
            try:
                interval, ef, reps = calculate_next_review(
                    quality=4,  # Quality enum value
                    ease_factor=DEFAULT_EASE_FACTOR,
                    interval=0,
                    repetitions=0
                )
                assert interval == 1
                tests.append(TestResult("SM-2 interval calculation", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ SM-2 interval: {interval}")
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
        """Test focus module."""
        tests = []
        start = time.time()
        
        try:
            from jarvis.focus.behaviour_monitor import BehaviourMonitor, DISTRACTING_APPS
            from jarvis.focus.porn_blocker import get_all_porn_domains
            from jarvis.focus.pattern_detector import PatternDetector
            
            # Behaviour monitor
            test_start = time.time()
            try:
                monitor = BehaviourMonitor()
                assert len(DISTRACTING_APPS) > 0
                tests.append(TestResult("Behaviour monitor init", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Behaviour monitor: {len(DISTRACTING_APPS)} apps")
            except Exception as e:
                tests.append(TestResult("Behaviour monitor init", False, time.time() - test_start, str(e)))
                print(f"  ✗ Behaviour monitor: {e}")
            
            # Porn blocker
            test_start = time.time()
            try:
                domains = get_all_porn_domains()
                assert len(domains) >= 100
                tests.append(TestResult("Porn blocker domains", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Porn domains: {len(domains)} blocked")
            except Exception as e:
                tests.append(TestResult("Porn blocker domains", False, time.time() - test_start, str(e)))
                print(f"  ✗ Porn domains: {e}")
            
            # Pattern detector
            test_start = time.time()
            try:
                detector = PatternDetector()
                tests.append(TestResult("Pattern detector init", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Pattern detector initialized")
            except Exception as e:
                tests.append(TestResult("Pattern detector init", False, time.time() - test_start, str(e)))
                print(f"  ✗ Pattern detector: {e}")
            
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
        """Test psychological engine with correct API."""
        tests = []
        start = time.time()
        
        try:
            from jarvis.psych.loss_aversion import LOSS_AVERSION_MULTIPLIER
            from jarvis.psych.reward_system import RewardSystem, JACKPOT_CHANCE
            from jarvis.psych.achievement_system import ACHIEVEMENTS
            from jarvis.psych.psychological_engine import PsychologicalEngine
            
            # Loss aversion constant
            test_start = time.time()
            try:
                assert LOSS_AVERSION_MULTIPLIER == 2.0
                tests.append(TestResult("Loss aversion constant", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Loss aversion multiplier: {LOSS_AVERSION_MULTIPLIER}")
            except Exception as e:
                tests.append(TestResult("Loss aversion constant", False, time.time() - test_start, str(e)))
            
            # Reward system (correct API)
            test_start = time.time()
            try:
                reward = RewardSystem()
                result = reward.calculate_session_reward(
                    questions_answered=20,
                    accuracy=0.8,
                    time_minutes=30,
                    streak_days=5
                )
                tests.append(TestResult("Reward calculation", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Reward: {result.amount} XP, tier: {result.tier.value}")
            except Exception as e:
                tests.append(TestResult("Reward calculation", False, time.time() - test_start, str(e)))
                print(f"  ✗ Reward: {e}")
            
            # Achievement count
            test_start = time.time()
            try:
                assert len(ACHIEVEMENTS) == 27
                tests.append(TestResult("Achievement count", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Achievements: {len(ACHIEVEMENTS)}")
            except Exception as e:
                tests.append(TestResult("Achievement count", False, time.time() - test_start, str(e)))
                print(f"  ✗ Achievements: {e}")
            
            # Psychological engine
            test_start = time.time()
            try:
                engine = PsychologicalEngine()
                tests.append(TestResult("Psychological engine init", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Psychology engine initialized")
            except Exception as e:
                tests.append(TestResult("Psychological engine init", False, time.time() - test_start, str(e)))
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
        """Test voice module."""
        tests = []
        start = time.time()
        
        try:
            from jarvis.voice.voice_engine import VoiceEngine, TTSBackend
            from jarvis.voice.voice_enforcer import VoiceEnforcer, EnforcementMode
            
            # Voice engine
            test_start = time.time()
            try:
                engine = VoiceEngine()
                tests.append(TestResult("Voice engine init", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Voice engine initialized")
            except Exception as e:
                tests.append(TestResult("Voice engine init", False, time.time() - test_start, str(e)))
                print(f"  ✗ Voice engine: {e}")
            
            # Voice enforcer
            test_start = time.time()
            try:
                enforcer = VoiceEnforcer()
                enforcer.mode = EnforcementMode.ENFORCER
                tests.append(TestResult("Voice enforcer init", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Enforcer mode: {EnforcementMode.ENFORCER}")
            except Exception as e:
                tests.append(TestResult("Voice enforcer init", False, time.time() - test_start, str(e)))
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
        """Test content module."""
        tests = []
        start = time.time()
        
        try:
            from jarvis.content.study_plan import PHASE_RANGES
            from jarvis.content.daily_target import DailyTargetManager
            from jarvis.content.milestone_tracker import DEFAULT_MILESTONES
            
            # Study phases
            test_start = time.time()
            try:
                assert len(PHASE_RANGES) == 5
                tests.append(TestResult("Study plan phases", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Study phases: {len(PHASE_RANGES)}")
            except Exception as e:
                tests.append(TestResult("Study plan phases", False, time.time() - test_start, str(e)))
            
            # Daily target
            test_start = time.time()
            try:
                manager = DailyTargetManager()
                target = manager.get_daily_target(day_number=1)
                tests.append(TestResult("Daily target init", True, time.time() - test_start))
                if self.verbose:
                    print(f"  ✓ Daily target: {len(target.subject_targets)} subjects")
            except Exception as e:
                tests.append(TestResult("Daily target init", False, time.time() - test_start, str(e)))
                print(f"  ✗ Daily target: {e}")
            
            # Milestone count
            test_start = time.time()
            try:
                assert len(DEFAULT_MILESTONES) == 17
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
    
    def _test_orchestrator(self) -> ModuleResult:
        """Test orchestrator."""
        tests = []
        start = time.time()
        
        try:
            from jarvis.orchestrator import JarvisOrchestrator, OrchestratorConfig, SystemState
            
            # Creation
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
            
            # Initialization
            test_start = time.time()
            try:
                config = OrchestratorConfig(enable_voice=False, enable_monitoring=False)
                orchestrator = JarvisOrchestrator(config)
                success = orchestrator.initialize()
                
                if success:
                    tests.append(TestResult("Orchestrator initialization", True, time.time() - test_start))
                    if self.verbose:
                        status = orchestrator.get_status()
                        print(f"  ✓ Initialized: {len(status.modules_loaded)} modules")
                else:
                    tests.append(TestResult("Orchestrator initialization", False, time.time() - test_start, "Init returned False"))
            except Exception as e:
                tests.append(TestResult("Orchestrator initialization", False, time.time() - test_start, str(e)))
                print(f"  ✗ Init: {e}")
            
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
        """Print module summary."""
        status = "✓ PASSED" if result.failed == 0 else "✗ FAILED"
        print(f"\n  {status}: {result.passed}/{result.total_tests} tests passed")
        print(f"  Duration: {result.duration:.2f}s")
    
    def _generate_report(self) -> Dict:
        """Generate final report."""
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
            print(f"\n  ⚠️  {total_failed} TESTS NEED ATTENTION. ⚠️\n")
        
        return {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "duration": total_duration,
            "success": total_failed == 0,
            "modules": [
                {"name": r.module_name, "passed": r.passed, "total": r.total_tests, "duration": r.duration}
                for r in self.results
            ]
        }


def main():
    parser = argparse.ArgumentParser(description="JARVIS Test Runner")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose)
    results = runner.run_all_tests()
    
    if args.json:
        print(json.dumps(results, indent=2))
    
    return 0 if results["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
