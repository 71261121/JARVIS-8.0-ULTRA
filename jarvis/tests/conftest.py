"""
JARVIS Test Configuration and Fixtures
=======================================

This module provides:
1. Shared fixtures for all tests
2. Mock implementations for external dependencies
3. Test data generators
4. Database fixtures
5. Configuration fixtures

GOAL_ALIGNMENT_CHECK():
    - Tests ensure system reliability → Exam success
    - Mocks prevent external dependency failures → Stable testing
    - Fixtures ensure consistent test data → Reproducible results

ROLLBACK PLAN:
    - All fixtures use isolated test databases
    - No production data is touched
    - Each test gets fresh state
"""

import pytest
import asyncio
import tempfile
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from unittest.mock import MagicMock, patch, AsyncMock

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# EVENT LOOP FIXTURE
# =============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# DATABASE FIXTURES
# =============================================================================

@pytest.fixture
def temp_db_path():
    """Provide temporary database path."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    yield path
    # Cleanup
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
async def test_database(temp_db_path):
    """Provide test database instance."""
    # Import here to avoid import errors if aiosqlite not installed
    try:
        import aiosqlite
        
        db = await aiosqlite.connect(temp_db_path)
        
        # Create tables
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subject TEXT,
                topic TEXT,
                questions_attempted INTEGER,
                questions_correct INTEGER,
                duration_minutes INTEGER,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            
            CREATE TABLE IF NOT EXISTS question_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                question_id TEXT,
                subject TEXT,
                topic TEXT,
                is_correct INTEGER,
                time_taken_seconds INTEGER,
                theta_before REAL,
                theta_after REAL,
                answered_at TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES study_sessions(id)
            );
            
            CREATE TABLE IF NOT EXISTS behaviour_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                app_name TEXT,
                timestamp TIMESTAMP,
                duration_seconds INTEGER,
                intervention_triggered INTEGER DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                achievement_id TEXT UNIQUE,
                name TEXT,
                description TEXT,
                tier TEXT,
                xp_reward INTEGER,
                unlocked_at TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                coins INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                total_questions INTEGER DEFAULT 0,
                total_correct INTEGER DEFAULT 0,
                last_study_date DATE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            
            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                milestone_id TEXT UNIQUE,
                name TEXT,
                description TEXT,
                target_value INTEGER,
                current_value INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                completed_at TIMESTAMP
            );
            
            INSERT OR IGNORE INTO users (id, name) VALUES (1, 'Test User');
            INSERT OR IGNORE INTO user_progress (user_id, xp, coins) VALUES (1, 0, 0);
        """)
        
        await db.commit()
        
        yield db
        
        await db.close()
        
    except ImportError:
        pytest.skip("aiosqlite not installed")


# =============================================================================
# MOCK IMPLEMENTATIONS
# =============================================================================

class MockRootAccess:
    """Mock root access for testing without actual root."""
    
    def __init__(self):
        self.available = False
        self.commands_executed = []
    
    def is_available(self) -> bool:
        return False
    
    def execute(self, command: str, timeout: int = 10) -> Dict:
        """Simulate command execution."""
        self.commands_executed.append(command)
        return {
            "success": False,
            "stdout": "",
            "stderr": "Root not available (mock)",
            "return_code": 1
        }
    
    def force_stop_app(self, package: str) -> bool:
        self.commands_executed.append(f"force-stop {package}")
        return False
    
    def get_foreground_app(self) -> Optional[str]:
        return "com.termux"


class MockVoiceEngine:
    """Mock voice engine for testing without TTS."""
    
    def __init__(self):
        self.messages_spoken = []
        self.enabled = True
    
    async def speak(self, text: str, personality: str = "NEUTRAL") -> bool:
        """Simulate voice output."""
        self.messages_spoken.append({
            "text": text,
            "personality": personality,
            "timestamp": datetime.now()
        })
        return True
    
    def clear_queue(self):
        self.messages_spoken.clear()
    
    def is_available(self) -> bool:
        return True


class MockBehaviourMonitor:
    """Mock behaviour monitor for testing."""
    
    def __init__(self):
        self.running = False
        self.events_logged = []
        self.distractions_detected = []
    
    def start(self):
        self.running = True
    
    def stop(self):
        self.running = False
    
    def is_running(self) -> bool:
        return self.running
    
    def log_event(self, event_type: str, app_name: str, duration: int = 0):
        self.events_logged.append({
            "type": event_type,
            "app": app_name,
            "duration": duration,
            "timestamp": datetime.now()
        })
    
    def detect_distraction(self, app_name: str) -> bool:
        distracting_apps = [
            "com.instagram.android",
            "com.google.android.youtube",
            "com.zhiliaoapp.musically",
            "com.pornhub.android"
        ]
        is_distraction = app_name in distracting_apps
        if is_distraction:
            self.distractions_detected.append(app_name)
        return is_distraction
    
    def get_current_app(self) -> str:
        return "com.termux"


class MockPornBlocker:
    """Mock porn blocker for testing."""
    
    def __init__(self):
        self.blocking_active = False
        self.domains_blocked = []
    
    def apply_blocking(self) -> tuple:
        """Simulate applying porn blocking."""
        self.blocking_active = True
        self.domains_blocked = ["pornhub.com", "xvideos.com", "xhamster.com"]
        return (True, "Blocking applied (mock)")
    
    def remove_blocking(self) -> tuple:
        """Simulate removing porn blocking."""
        self.blocking_active = False
        self.domains_blocked.clear()
        return (True, "Blocking removed (mock)")
    
    def is_blocked(self, domain: str) -> bool:
        return domain in self.domains_blocked
    
    def get_blocked_domains(self) -> List[str]:
        return self.domains_blocked.copy()


class MockPatternAnalyzer:
    """Mock pattern analyzer for testing."""
    
    def __init__(self):
        self.patterns_detected = []
        self.interventions_executed = []
        self.running = False
    
    def start(self):
        self.running = True
    
    def stop(self):
        self.running = False
    
    def analyze(self, data: Dict) -> List[Dict]:
        """Simulate pattern analysis."""
        patterns = []
        
        # Check for study avoidance
        if data.get("distraction_count", 0) > 5:
            patterns.append({
                "type": "STUDY_AVOIDANCE",
                "severity": "HIGH",
                "score": 75,
                "description": "High distraction count detected"
            })
        
        # Check for burnout precursor
        if data.get("session_decline", False):
            patterns.append({
                "type": "BURNOUT_PRECURSOR",
                "severity": "MEDIUM",
                "score": 60,
                "description": "Declining session times observed"
            })
        
        self.patterns_detected.extend(patterns)
        return patterns
    
    def execute_intervention(self, pattern_type: str) -> Dict:
        """Simulate intervention execution."""
        intervention = {
            "type": pattern_type,
            "executed_at": datetime.now(),
            "success": True,
            "message": f"Intervention for {pattern_type} executed (mock)"
        }
        self.interventions_executed.append(intervention)
        return intervention


class MockPsychologicalEngine:
    """Mock psychological engine for testing."""
    
    def __init__(self):
        self.xp = 0
        self.coins = 0
        self.streak = 0
        self.achievements_unlocked = []
        self.mystery_boxes = []
    
    def process_session(self, session_data: Dict) -> Dict:
        """Simulate session processing."""
        questions_correct = session_data.get("correct", 0)
        questions_total = session_data.get("total", 1)
        accuracy = questions_correct / questions_total if questions_total > 0 else 0
        
        # Calculate XP
        base_xp = questions_correct * 10
        xp_earned = base_xp
        
        # Check for bonus
        if accuracy >= 0.9:
            xp_earned = int(base_xp * 1.5)
        
        self.xp += xp_earned
        self.coins += questions_correct * 2
        
        return {
            "xp_earned": xp_earned,
            "coins_earned": questions_correct * 2,
            "accuracy": accuracy,
            "reward_tier": "BONUS" if accuracy >= 0.9 else "NORMAL"
        }
    
    def update_streak(self, studied_today: bool) -> Dict:
        """Simulate streak update."""
        if studied_today:
            self.streak += 1
        else:
            self.streak = 0
        
        return {
            "current_streak": self.streak,
            "streak_maintained": studied_today
        }
    
    def check_achievements(self, user_stats: Dict) -> List[Dict]:
        """Simulate achievement checking."""
        new_achievements = []
        
        # First session achievement
        if user_stats.get("total_sessions", 0) == 1:
            new_achievements.append({
                "id": "first_step",
                "name": "First Step",
                "tier": "COMMON",
                "xp_reward": 50
            })
        
        # 7-day streak
        if self.streak >= 7 and "week_warrior" not in [a["id"] for a in self.achievements_unlocked]:
            new_achievements.append({
                "id": "week_warrior",
                "name": "Week Warrior",
                "tier": "UNCOMMON",
                "xp_reward": 200
            })
        
        self.achievements_unlocked.extend(new_achievements)
        return new_achievements
    
    def get_progress(self) -> Dict:
        """Get current progress."""
        return {
            "xp": self.xp,
            "coins": self.coins,
            "streak": self.streak,
            "achievements": len(self.achievements_unlocked)
        }


# =============================================================================
# FIXTURE REGISTRATION
# =============================================================================

@pytest.fixture
def mock_root():
    """Provide mock root access."""
    return MockRootAccess()


@pytest.fixture
def mock_voice():
    """Provide mock voice engine."""
    return MockVoiceEngine()


@pytest.fixture
def mock_monitor():
    """Provide mock behaviour monitor."""
    return MockBehaviourMonitor()


@pytest.fixture
def mock_porn_blocker():
    """Provide mock porn blocker."""
    return MockPornBlocker()


@pytest.fixture
def mock_pattern_analyzer():
    """Provide mock pattern analyzer."""
    return MockPatternAnalyzer()


@pytest.fixture
def mock_psychological():
    """Provide mock psychological engine."""
    return MockPsychologicalEngine()


# =============================================================================
# TEST DATA GENERATORS
# =============================================================================

@dataclass
class TestDataGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def generate_questions(count: int, subject: str = "Mathematics") -> List[Dict]:
        """Generate test questions."""
        topics = {
            "Mathematics": ["Algebra", "Calculus", "Geometry", "Trigonometry"],
            "Physics": ["Mechanics", "Thermodynamics", "Optics", "Electromagnetism"],
            "Chemistry": ["Organic", "Inorganic", "Physical", "Biochemistry"],
            "English": ["Grammar", "Vocabulary", "Comprehension", "Writing"]
        }
        
        questions = []
        subject_topics = topics.get(subject, ["General"])
        
        for i in range(count):
            questions.append({
                "id": f"{subject.lower()}_{i+1}",
                "subject": subject,
                "topic": subject_topics[i % len(subject_topics)],
                "difficulty": 0.3 + (i % 10) * 0.07,  # 0.3 to 0.93
                "discrimination": 1.0 + (i % 5) * 0.2,  # 1.0 to 1.8
                "guessing": 0.25,
                "content": f"Test question {i+1} for {subject}",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A"
            })
        
        return questions
    
    @staticmethod
    def generate_study_sessions(count: int, user_id: int = 1) -> List[Dict]:
        """Generate study session records."""
        sessions = []
        base_time = datetime.now() - timedelta(days=count)
        
        for i in range(count):
            session_time = base_time + timedelta(days=i)
            questions = 20 + (i % 30)
            correct = int(questions * (0.6 + (i % 4) * 0.1))
            
            sessions.append({
                "id": i + 1,
                "user_id": user_id,
                "subject": ["Mathematics", "Physics", "Chemistry", "English"][i % 4],
                "topic": f"Topic {i+1}",
                "questions_attempted": questions,
                "questions_correct": correct,
                "duration_minutes": 30 + (i % 60),
                "started_at": session_time,
                "completed_at": session_time + timedelta(minutes=45),
                "accuracy": correct / questions
            })
        
        return sessions
    
    @staticmethod
    def generate_behaviour_events(count: int, include_distractions: bool = True) -> List[Dict]:
        """Generate behaviour events."""
        events = []
        base_time = datetime.now() - timedelta(hours=count)
        
        apps = ["com.termux", "com.android.chrome"]
        if include_distractions:
            apps.extend(["com.instagram.android", "com.google.android.youtube"])
        
        for i in range(count):
            event_time = base_time + timedelta(hours=i)
            app = apps[i % len(apps)]
            
            events.append({
                "event_type": "APP_SWITCH",
                "app_name": app,
                "timestamp": event_time,
                "duration_seconds": 60 + (i % 300),
                "is_distraction": app in ["com.instagram.android", "com.google.android.youtube"]
            })
        
        return events
    
    @staticmethod
    def generate_user_progress() -> Dict:
        """Generate user progress data."""
        return {
            "xp": 1250,
            "coins": 340,
            "current_streak": 7,
            "longest_streak": 14,
            "total_questions": 500,
            "total_correct": 380,
            "accuracy": 0.76,
            "last_study_date": datetime.now().date(),
            "achievements_unlocked": 5,
            "milestones_completed": 3
        }


@pytest.fixture
def test_data():
    """Provide test data generator."""
    return TestDataGenerator()


# =============================================================================
# ASSERTION HELPERS
# =============================================================================

class AssertionHelpers:
    """Helper assertions for JARVIS tests."""
    
    @staticmethod
    def assert_valid_theta(theta: float):
        """Assert theta is within valid IRT range."""
        assert -4.0 <= theta <= 4.0, f"Theta {theta} outside valid range [-4, 4]"
    
    @staticmethod
    def assert_valid_difficulty(difficulty: float):
        """Assert difficulty parameter is valid."""
        assert -3.0 <= difficulty <= 3.0, f"Difficulty {difficulty} outside valid range"
    
    @staticmethod
    def assert_valid_discrimination(discrimination: float):
        """Assert discrimination parameter is valid."""
        assert 0 < discrimination <= 3.0, f"Discrimination {discrimination} outside valid range"
    
    @staticmethod
    def assert_valid_probability(prob: float):
        """Assert probability is valid."""
        assert 0 <= prob <= 1.0, f"Probability {prob} outside [0, 1]"
    
    @staticmethod
    def assert_valid_sm2_interval(interval: int):
        """Assert SM-2 interval is valid."""
        assert interval >= 0, f"Interval {interval} must be non-negative"
    
    @staticmethod
    def assert_valid_ease_factor(ef: float):
        """Assert ease factor is valid."""
        assert 1.3 <= ef <= 3.0, f"Ease factor {ef} outside valid range [1.3, 3.0]"
    
    @staticmethod
    def assert_achievement_valid(achievement: Dict):
        """Assert achievement structure is valid."""
        required_keys = ["id", "name", "tier", "xp_reward"]
        for key in required_keys:
            assert key in achievement, f"Achievement missing key: {key}"
    
    @staticmethod
    def assert_pattern_valid(pattern: Dict):
        """Assert pattern structure is valid."""
        required_keys = ["type", "severity", "score"]
        for key in required_keys:
            assert key in pattern, f"Pattern missing key: {key}"


@pytest.fixture
def asserts():
    """Provide assertion helpers."""
    return AssertionHelpers()


# =============================================================================
# CONFIGURATION FIXTURES
# =============================================================================

@pytest.fixture
def test_config():
    """Provide test configuration."""
    return {
        "database": {
            "path": ":memory:",
            "echo": False
        },
        "study": {
            "irt": {
                "theta_initial": 0.0,
                "se_target": 0.3
            },
            "sm2": {
                "ease_factor_default": 2.5,
                "interval_first": 1,
                "interval_second": 6
            }
        },
        "focus": {
            "poll_interval": 1.0,
            "study_start_hour": 6,
            "study_end_hour": 22,
            "auto_block": False
        },
        "psychology": {
            "loss_aversion_multiplier": 2.0,
            "jackpot_chance": 0.05,
            "bonus_chance": 0.15
        },
        "voice": {
            "enabled": True,
            "default_personality": "NEUTRAL",
            "quiet_hours_start": 23,
            "quiet_hours_end": 7
        }
    }


@pytest.fixture
def sample_irt_params():
    """Provide sample IRT parameters for testing."""
    return {
        "easy": {"a": 1.0, "b": -1.5, "c": 0.2},
        "medium": {"a": 1.2, "b": 0.0, "c": 0.25},
        "hard": {"a": 1.5, "b": 1.5, "c": 0.15}
    }


@pytest.fixture
def sample_sm2_items():
    """Provide sample SM-2 review items for testing."""
    return [
        {
            "id": "item_1",
            "interval": 0,
            "repetition": 0,
            "ease_factor": 2.5,
            "next_review": datetime.now()
        },
        {
            "id": "item_2",
            "interval": 6,
            "repetition": 2,
            "ease_factor": 2.3,
            "next_review": datetime.now() - timedelta(days=1)  # Overdue
        }
    ]


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for cross-module functionality"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests for full system simulation"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer to run"
    )
    config.addinivalue_line(
        "markers", "requires_root: Tests that require root access"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers."""
    # Skip root-requiring tests if root not available
    skip_root = pytest.mark.skip(reason="Root access not available")
    
    for item in items:
        if "requires_root" in item.keywords:
            # Check if root is available
            su_paths = ["/system/bin/su", "/system/xbin/su", "/sbin/su"]
            root_available = any(os.path.exists(p) for p in su_paths)
            if not root_available:
                item.add_marker(skip_root)
