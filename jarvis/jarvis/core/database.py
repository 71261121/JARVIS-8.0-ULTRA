"""
JARVIS Database Module
======================

Purpose: SQLite database management for JARVIS.

Reason for SQLite:
    - Built into Python, no extra dependency
    - Single file, easy backup
    - WAL mode for concurrent access
    - Perfect for mobile/local app

Rollback:
    - Database file can be deleted and recreated
    - Backup in data/backup/ folder

Schema Version: 1.0
Last Updated: 2025-02-12
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

try:
    import aiosqlite
    ASYNC_AVAILABLE = True
except ImportError:
    import sqlite3
    ASYNC_AVAILABLE = False

from .config import Config


# ============================================================================
# SCHEMA DEFINITION
# ============================================================================

SCHEMA_VERSION = 1

SCHEMA_SQL = """
-- ============================================
-- JARVIS DATABASE SCHEMA v1.0
-- ============================================
-- Reason: Each table serves a specific purpose
-- No redundant tables, no missing tables
-- ============================================

-- User Profile Table
-- Reason: Store user info, track progress
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL DEFAULT 'Student',
    background TEXT DEFAULT 'biology_stream',
    exam TEXT DEFAULT 'Loyola Academy B.Sc CS',
    exam_date TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Current progress
    current_day INTEGER DEFAULT 1,
    current_phase INTEGER DEFAULT 1,
    
    -- IRT Theta values per subject
    maths_theta REAL DEFAULT 0.0,
    physics_theta REAL DEFAULT 0.0,
    chemistry_theta REAL DEFAULT 0.0,
    english_theta REAL DEFAULT 0.0,
    
    -- Psychological stats
    total_xp INTEGER DEFAULT 0,
    current_level INTEGER DEFAULT 1,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_study_date TEXT,
    streak_freezes_available INTEGER DEFAULT 3
);

-- Subjects Table
-- Reason: Define subjects with weightage
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    weightage INTEGER NOT NULL,
    priority INTEGER DEFAULT 99,
    description TEXT
);

-- Topics Table
-- Reason: Hierarchical topic structure
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    parent_id INTEGER,  -- For sub-topics, NULL if top-level
    difficulty REAL DEFAULT 0.0,  -- IRT difficulty parameter
    
    -- For biology background students
    foundation_required INTEGER DEFAULT 0,
    foundation_days INTEGER DEFAULT 0,
    
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (parent_id) REFERENCES topics(id)
);

-- Questions Table
-- Reason: Store all questions with IRT parameters
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_option TEXT NOT NULL,  -- 'A', 'B', 'C', or 'D'
    explanation TEXT,
    
    -- IRT Parameters
    difficulty REAL DEFAULT 0.0,      -- b parameter
    discrimination REAL DEFAULT 1.0,   -- a parameter
    guessing REAL DEFAULT 0.25,        -- c parameter (4 options = 0.25)
    
    -- Metadata
    source TEXT,  -- 'ai_generated', 'previous_year', 'manual'
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    times_asked INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

-- Study Sessions Table
-- Reason: Track each study session
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject_id INTEGER,
    session_type TEXT NOT NULL,  -- 'practice', 'revision', 'mock_test'
    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TEXT,
    duration_minutes INTEGER,
    
    -- Stats
    questions_attempted INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    xp_earned INTEGER DEFAULT 0,
    
    -- IRT
    theta_before REAL,
    theta_after REAL,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

-- Question Responses Table
-- Reason: Track every answer for IRT calculations
CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    session_id INTEGER NOT NULL,
    
    -- Response
    user_answer TEXT NOT NULL,  -- 'A', 'B', 'C', 'D'
    is_correct INTEGER NOT NULL,  -- 0 or 1
    time_taken_seconds INTEGER,
    
    -- IRT
    theta_before REAL,
    theta_after REAL,
    fisher_information REAL,
    
    answered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (question_id) REFERENCES questions(id),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- Spaced Repetition Table
-- Reason: SM-2 algorithm tracking
CREATE TABLE IF NOT EXISTS spaced_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    
    -- SM-2 Parameters
    ease_factor REAL DEFAULT 2.5,
    interval_days INTEGER DEFAULT 1,
    repetitions INTEGER DEFAULT 0,  -- Consecutive correct count
    
    -- Scheduling
    last_review_date TEXT,
    next_review_date TEXT NOT NULL,
    
    -- Stats
    total_reviews INTEGER DEFAULT 0,
    average_quality REAL DEFAULT 0.0,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

-- Daily Plans Table
-- Reason: 75-day plan tracking
CREATE TABLE IF NOT EXISTS daily_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    day_number INTEGER NOT NULL,
    phase INTEGER NOT NULL,
    
    -- Plan
    topics_to_cover TEXT,  -- JSON array of topic IDs
    questions_target INTEGER DEFAULT 0,
    mock_test INTEGER DEFAULT 0,  -- 0 or 1
    
    -- Actual
    questions_completed INTEGER DEFAULT 0,
    mock_score REAL,
    
    -- Status
    is_completed INTEGER DEFAULT 0,
    completed_at TEXT,
    
    date TEXT NOT NULL,  -- The actual date
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, day_number)
);

-- Mock Tests Table
-- Reason: Full mock test tracking
CREATE TABLE IF NOT EXISTS mock_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id INTEGER,
    
    -- Scores
    maths_score INTEGER DEFAULT 0,
    physics_score INTEGER DEFAULT 0,
    chemistry_score INTEGER DEFAULT 0,
    english_score INTEGER DEFAULT 0,
    total_score INTEGER DEFAULT 0,
    
    -- Time
    time_taken_seconds INTEGER,
    
    -- Analysis
    weak_topics TEXT,  -- JSON array
    
    taken_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- Achievements Table
-- Reason: Achievement definitions
CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    xp_reward INTEGER DEFAULT 0,
    icon TEXT,
    category TEXT  -- 'milestone', 'skill', 'streak', 'special'
);

-- User Achievements Table
-- Reason: Track unlocked achievements
CREATE TABLE IF NOT EXISTS user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    unlocked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (achievement_id) REFERENCES achievements(id),
    UNIQUE(user_id, achievement_id)
);

-- Distraction Events Table
-- Reason: Track distraction attempts
CREATE TABLE IF NOT EXISTS distraction_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    app_name TEXT NOT NULL,
    event_type TEXT NOT NULL,  -- 'blocked', 'warning', 'opened'
    occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    xp_penalty INTEGER DEFAULT 0,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- XP History Table
-- Reason: Track all XP changes
CREATE TABLE IF NOT EXISTS xp_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    xp_change INTEGER NOT NULL,  -- Can be negative
    reason TEXT NOT NULL,
    session_id INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- AI Response Cache Table
-- Reason: Cache AI responses for speed
CREATE TABLE IF NOT EXISTS ai_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_hash TEXT NOT NULL UNIQUE,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT,
    hit_count INTEGER DEFAULT 0
);

-- Schema Version Table
-- Reason: Track migrations
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES
-- ============================================
-- Reason: Speed up common queries

CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions(topic_id);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);

CREATE INDEX IF NOT EXISTS idx_responses_user ON responses(user_id);
CREATE INDEX IF NOT EXISTS idx_responses_question ON responses(question_id);
CREATE INDEX IF NOT EXISTS idx_responses_session ON responses(session_id);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(started_at);

CREATE INDEX IF NOT EXISTS idx_spaced_reviews_user ON spaced_reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_spaced_reviews_date ON spaced_reviews(next_review_date);

CREATE INDEX IF NOT EXISTS idx_daily_plans_user_day ON daily_plans(user_id, day_number);

CREATE INDEX IF NOT EXISTS idx_ai_cache_hash ON ai_cache(prompt_hash);
"""


# ============================================================================
# DATABASE CLASS
# ============================================================================

class Database:
    """
    Database manager for JARVIS.
    
    Usage:
        db = Database(config)
        await db.initialize()
        
        # Queries
        user = await db.get_user(1)
        await db.update_xp(1, 100, "Completed session")
    
    Reason for design:
        - Async for Textual compatibility
        - Context manager for connection safety
        - All SQL in one place for maintainability
    """
    
    def __init__(self, config: Config):
        """
        Initialize database manager.
        
        Args:
            config: JARVIS configuration
        
        Reason:
            Store config reference for paths and settings.
        """
        self.config = config
        self.db_path = config.database.path
        self._connection = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """
        Initialize database - create if not exists.
        
        Raises:
            sqlite3.Error: If database cannot be created
        
        Reason:
            Lazy initialization allows config to be loaded first.
        """
        # Ensure directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        # Connect and create schema
        if ASYNC_AVAILABLE:
            self._connection = await aiosqlite.connect(self.db_path)
            
            # Enable WAL mode for concurrent access
            if self.config.database.wal_mode:
                await self._connection.execute("PRAGMA journal_mode=WAL")
            
            # Create schema
            await self._connection.executescript(SCHEMA_SQL)
            
            # Record schema version
            await self._connection.execute(
                "INSERT OR IGNORE INTO schema_version (version) VALUES (?)",
                (SCHEMA_VERSION,)
            )
            
            await self._connection.commit()
        else:
            # Fallback to sync sqlite3
            self._connection = sqlite3.connect(self.db_path)
            self._connection.executescript(SCHEMA_SQL)
            self._connection.commit()
        
        self._initialized = True
    
    async def close(self) -> None:
        """Close database connection."""
        if self._connection:
            if ASYNC_AVAILABLE:
                await self._connection.close()
            else:
                self._connection.close()
            self._connection = None
    
    async def _ensure_initialized(self) -> None:
        """Ensure database is initialized before operations."""
        if not self._initialized:
            await self.initialize()
    
    # ========================================================================
    # USER OPERATIONS
    # ========================================================================
    
    async def create_user(self, name: str = "Student") -> int:
        """
        Create a new user.
        
        Args:
            name: User's name
        
        Returns:
            User ID
        
        Reason:
            Single user system, but ID allows future multi-user support.
        """
        await self._ensure_initialized()
        
        if ASYNC_AVAILABLE:
            cursor = await self._connection.execute(
                """INSERT INTO users (name, exam_date) 
                   VALUES (?, date('now', '+75 days'))""",
                (name,)
            )
            await self._connection.commit()
            return cursor.lastrowid
        else:
            cursor = self._connection.execute(
                """INSERT INTO users (name, exam_date) 
                   VALUES (?, date('now', '+75 days'))""",
                (name,)
            )
            self._connection.commit()
            return cursor.lastrowid
    
    async def get_user(self, user_id: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID (default 1 for single user)
        
        Returns:
            User dict or None
        """
        await self._ensure_initialized()
        
        if ASYNC_AVAILABLE:
            async with self._connection.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
        else:
            cursor = self._connection.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            )
            row = cursor.fetchone()
        
        if row is None:
            return None
        
        # Convert to dict
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))
    
    async def update_theta(self, user_id: int, subject: str, theta: float) -> None:
        """
        Update theta value for a subject.
        
        Args:
            user_id: User ID
            subject: Subject name (maths, physics, chemistry, english)
            theta: New theta value
        
        Reason:
            Theta is updated after each question in IRT.
        """
        await self._ensure_initialized()
        
        column = f"{subject}_theta"
        if ASYNC_AVAILABLE:
            await self._connection.execute(
                f"UPDATE users SET {column} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (theta, user_id)
            )
            await self._connection.commit()
        else:
            self._connection.execute(
                f"UPDATE users SET {column} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (theta, user_id)
            )
            self._connection.commit()
    
    async def update_xp(self, user_id: int, xp_change: int, reason: str, 
                        session_id: Optional[int] = None) -> int:
        """
        Update user XP and record history.
        
        Args:
            user_id: User ID
            xp_change: XP change (positive or negative)
            reason: Reason for change
            session_id: Related session ID
        
        Returns:
            New total XP
        
        Reason:
            XP changes must be tracked for analytics.
        """
        await self._ensure_initialized()
        
        if ASYNC_AVAILABLE:
            # Update total XP
            await self._connection.execute(
                """UPDATE users 
                   SET total_xp = total_xp + ?, 
                       updated_at = CURRENT_TIMESTAMP 
                   WHERE id = ?""",
                (xp_change, user_id)
            )
            
            # Record history
            await self._connection.execute(
                """INSERT INTO xp_history (user_id, xp_change, reason, session_id)
                   VALUES (?, ?, ?, ?)""",
                (user_id, xp_change, reason, session_id)
            )
            
            await self._connection.commit()
            
            # Get new total
            async with self._connection.execute(
                "SELECT total_xp FROM users WHERE id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
        else:
            self._connection.execute(
                """UPDATE users 
                   SET total_xp = total_xp + ?, 
                       updated_at = CURRENT_TIMESTAMP 
                   WHERE id = ?""",
                (xp_change, user_id)
            )
            self._connection.execute(
                """INSERT INTO xp_history (user_id, xp_change, reason, session_id)
                   VALUES (?, ?, ?, ?)""",
                (user_id, xp_change, reason, session_id)
            )
            self._connection.commit()
            
            cursor = self._connection.execute(
                "SELECT total_xp FROM users WHERE id = ?", (user_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else 0
    
    async def update_streak(self, user_id: int, increment: bool = True) -> int:
        """
        Update study streak.
        
        Args:
            user_id: User ID
            increment: True to increment, False to reset
        
        Returns:
            New streak value
        
        Reason:
            Streak is a key motivator. Must be accurate.
        """
        await self._ensure_initialized()
        
        if ASYNC_AVAILABLE:
            if increment:
                await self._connection.execute(
                    """UPDATE users 
                       SET current_streak = current_streak + 1,
                           longest_streak = MAX(longest_streak, current_streak + 1),
                           last_study_date = date('now'),
                           updated_at = CURRENT_TIMESTAMP
                       WHERE id = ?""",
                    (user_id,)
                )
            else:
                await self._connection.execute(
                    """UPDATE users 
                       SET current_streak = 0,
                           updated_at = CURRENT_TIMESTAMP
                       WHERE id = ?""",
                    (user_id,)
                )
            
            await self._connection.commit()
            
            async with self._connection.execute(
                "SELECT current_streak FROM users WHERE id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
        else:
            if increment:
                self._connection.execute(
                    """UPDATE users 
                       SET current_streak = current_streak + 1,
                           longest_streak = MAX(longest_streak, current_streak + 1),
                           last_study_date = date('now'),
                           updated_at = CURRENT_TIMESTAMP
                       WHERE id = ?""",
                    (user_id,)
                )
            else:
                self._connection.execute(
                    """UPDATE users 
                       SET current_streak = 0,
                           updated_at = CURRENT_TIMESTAMP
                       WHERE id = ?""",
                    (user_id,)
                )
            
            self._connection.commit()
            
            cursor = self._connection.execute(
                "SELECT current_streak FROM users WHERE id = ?", (user_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else 0

    # ========================================================================
    # QUESTION OPERATIONS
    # ========================================================================
    
    async def add_question(self, topic_id: int, question_text: str,
                          options: List[str], correct: str,
                          explanation: str = "", 
                          difficulty: float = 0.0,
                          discrimination: float = 1.0,
                          guessing: float = 0.25,
                          source: str = "manual") -> int:
        """
        Add a new question.
        
        Args:
            topic_id: Topic ID
            question_text: Question text
            options: List of 4 options [A, B, C, D]
            correct: Correct option letter ('A', 'B', 'C', 'D')
            explanation: Explanation text
            difficulty: IRT difficulty (b parameter)
            discrimination: IRT discrimination (a parameter)
            guessing: IRT guessing (c parameter)
            source: Source of question
        
        Returns:
            Question ID
        
        Reason:
            Centralized question creation with validation.
        """
        await self._ensure_initialized()
        
        if len(options) != 4:
            raise ValueError("Must have exactly 4 options")
        
        if correct not in ['A', 'B', 'C', 'D']:
            raise ValueError("Correct must be A, B, C, or D")
        
        if ASYNC_AVAILABLE:
            cursor = await self._connection.execute(
                """INSERT INTO questions 
                   (topic_id, question_text, option_a, option_b, option_c, option_d,
                    correct_option, explanation, difficulty, discrimination, guessing, source)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (topic_id, question_text, options[0], options[1], 
                 options[2], options[3], correct, explanation,
                 difficulty, discrimination, guessing, source)
            )
            await self._connection.commit()
            return cursor.lastrowid
        else:
            cursor = self._connection.execute(
                """INSERT INTO questions 
                   (topic_id, question_text, option_a, option_b, option_c, option_d,
                    correct_option, explanation, difficulty, discrimination, guessing, source)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (topic_id, question_text, options[0], options[1], 
                 options[2], options[3], correct, explanation,
                 difficulty, discrimination, guessing, source)
            )
            self._connection.commit()
            return cursor.lastrowid
    
    async def get_question(self, question_id: int) -> Optional[Dict[str, Any]]:
        """Get question by ID."""
        await self._ensure_initialized()
        
        if ASYNC_AVAILABLE:
            async with self._connection.execute(
                "SELECT * FROM questions WHERE id = ?", (question_id,)
            ) as cursor:
                row = await cursor.fetchone()
        else:
            cursor = self._connection.execute(
                "SELECT * FROM questions WHERE id = ?", (question_id,)
            )
            row = cursor.fetchone()
        
        if row is None:
            return None
        
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))
    
    async def get_questions_for_topic(self, topic_id: int, 
                                       limit: int = 10) -> List[Dict[str, Any]]:
        """Get questions for a topic."""
        await self._ensure_initialized()
        
        if ASYNC_AVAILABLE:
            async with self._connection.execute(
                """SELECT * FROM questions 
                   WHERE topic_id = ? 
                   ORDER BY RANDOM() 
                   LIMIT ?""",
                (topic_id, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
        else:
            cursor = self._connection.execute(
                """SELECT * FROM questions 
                   WHERE topic_id = ? 
                   ORDER BY RANDOM() 
                   LIMIT ?""",
                (topic_id, limit)
            )
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        
        return [dict(zip(columns, row)) for row in rows]
    
    async def record_response(self, user_id: int, question_id: int,
                              session_id: int, user_answer: str,
                              is_correct: bool, time_seconds: int,
                              theta_before: float, theta_after: float,
                              fisher_info: float) -> int:
        """
        Record a question response.
        
        Returns:
            Response ID
        """
        await self._ensure_initialized()
        
        if ASYNC_AVAILABLE:
            cursor = await self._connection.execute(
                """INSERT INTO responses 
                   (user_id, question_id, session_id, user_answer, is_correct,
                    time_taken_seconds, theta_before, theta_after, fisher_information)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, question_id, session_id, user_answer, 
                 1 if is_correct else 0, time_seconds,
                 theta_before, theta_after, fisher_info)
            )
            
            # Update question stats
            await self._connection.execute(
                """UPDATE questions 
                   SET times_asked = times_asked + 1,
                       times_correct = times_correct + ?
                   WHERE id = ?""",
                (1 if is_correct else 0, question_id)
            )
            
            await self._connection.commit()
            return cursor.lastrowid
        else:
            cursor = self._connection.execute(
                """INSERT INTO responses 
                   (user_id, question_id, session_id, user_answer, is_correct,
                    time_taken_seconds, theta_before, theta_after, fisher_information)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, question_id, session_id, user_answer, 
                 1 if is_correct else 0, time_seconds,
                 theta_before, theta_after, fisher_info)
            )
            self._connection.execute(
                """UPDATE questions 
                   SET times_asked = times_asked + 1,
                       times_correct = times_correct + ?
                   WHERE id = ?""",
                (1 if is_correct else 0, question_id)
            )
            self._connection.commit()
            return cursor.lastrowid


# ============================================================================
# INITIALIZATION FUNCTION
# ============================================================================

async def init_database(config: Config) -> Database:
    """
    Initialize and return database.
    
    Args:
        config: JARVIS configuration
    
    Returns:
        Initialized Database instance
    
    Reason:
        Factory function for clean initialization.
    """
    db = Database(config)
    await db.initialize()
    return db


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("Testing database module...")
    print()
    
    # Create test config
    from .config import Config
    config = Config()
    config.database.path = ":memory:"  # In-memory for testing
    
    async def test():
        db = await init_database(config)
        
        # Test user creation
        user_id = await db.create_user("Test Student")
        print(f"Created user: {user_id}")
        
        # Get user
        user = await db.get_user(user_id)
        print(f"User data: {user}")
        
        # Update XP
        new_xp = await db.update_xp(user_id, 100, "Test reward")
        print(f"New XP: {new_xp}")
        
        # Update streak
        streak = await db.update_streak(user_id, True)
        print(f"Streak: {streak}")
        
        await db.close()
        print("\nAll tests passed!")
    
    asyncio.run(test())
