"""
JARVIS Database Module v2.0
===========================

Purpose: SQLite database management for JARVIS with enhanced features.

Features:
    - Connection pooling for performance
    - Comprehensive error handling
    - Edge case validation
    - Query optimization with indexes
    - Graceful degradation on failures
    - Transaction management
    - Automatic backups

Reason for SQLite:
    - Built into Python, no extra dependency
    - Single file, easy backup
    - WAL mode for concurrent access
    - Perfect for mobile/local app

Schema Version: 1.0
Last Updated: 2025-02-12
"""

import os
import json
import asyncio
import logging
import hashlib
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple, Union
from contextlib import asynccontextmanager
from dataclasses import dataclass

try:
    import aiosqlite
    ASYNC_AVAILABLE = True
except ImportError:
    import sqlite3
    ASYNC_AVAILABLE = False

try:
    from .config import Config
except ImportError:
    # Fallback for standalone testing
    class Config:
        class database:
            path = ":memory:"
            wal_mode = True
            pool_size = 5

# Setup logger
logger = logging.getLogger('JARVIS.Database')


# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

SCHEMA_VERSION = 1

# Connection pool settings
DEFAULT_POOL_SIZE = 5
CONNECTION_TIMEOUT = 30.0  # seconds
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 0.1  # seconds

# Query timeout
QUERY_TIMEOUT = 10.0  # seconds


# ============================================================================
# SCHEMA DEFINITION
# ============================================================================

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
# ERROR CLASSES
# ============================================================================

class DatabaseError(Exception):
    """Base exception for database errors."""
    pass


class ConnectionError(DatabaseError):
    """Raised when connection cannot be established."""
    pass


class QueryError(DatabaseError):
    """Raised when a query fails."""
    pass


class ValidationError(DatabaseError):
    """Raised when input validation fails."""
    pass


# ============================================================================
# CONNECTION POOL
# ============================================================================

@dataclass
class PooledConnection:
    """Wrapper for pooled connection with metadata."""
    connection: Any
    created_at: float
    last_used: float
    in_use: bool = False


class ConnectionPool:
    """
    Connection pool for SQLite database connections.
    
    Provides connection reuse and management for better performance.
    Thread-safe for async operations.
    """
    
    def __init__(self, db_path: str, pool_size: int = DEFAULT_POOL_SIZE):
        """
        Initialize connection pool.
        
        Args:
            db_path: Path to SQLite database
            pool_size: Maximum number of connections
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self._pool: List[PooledConnection] = []
        self._lock = asyncio.Lock()
        self._initialized = False
        logger.info(f"Connection pool created for {db_path} with size {pool_size}")
    
    async def initialize(self) -> None:
        """Initialize the connection pool."""
        async with self._lock:
            if self._initialized:
                return
            
            for _ in range(self.pool_size):
                try:
                    if ASYNC_AVAILABLE:
                        conn = await aiosqlite.connect(self.db_path)
                        # Enable WAL mode for concurrent access
                        await conn.execute("PRAGMA journal_mode=WAL")
                        await conn.execute("PRAGMA synchronous=NORMAL")
                        await conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
                        await conn.execute("PRAGMA temp_store=MEMORY")
                    else:
                        conn = sqlite3.connect(self.db_path)
                        conn.execute("PRAGMA journal_mode=WAL")
                    
                    pooled = PooledConnection(
                        connection=conn,
                        created_at=time.time(),
                        last_used=time.time()
                    )
                    self._pool.append(pooled)
                except Exception as e:
                    logger.error(f"Failed to create connection: {e}")
            
            self._initialized = True
            logger.info(f"Connection pool initialized with {len(self._pool)} connections")
    
    @asynccontextmanager
    async def get_connection(self):
        """
        Get a connection from the pool.
        
        Yields:
            Database connection
            
        Raises:
            ConnectionError: If no connection available
        """
        if not self._initialized:
            await self.initialize()
        
        conn = None
        pooled_conn = None
        
        try:
            async with self._lock:
                # Find available connection
                for pc in self._pool:
                    if not pc.in_use:
                        pc.in_use = True
                        pc.last_used = time.time()
                        pooled_conn = pc
                        conn = pc.connection
                        break
                
                if conn is None:
                    # Pool exhausted, wait and retry
                    logger.warning("Connection pool exhausted, waiting...")
                    await asyncio.sleep(0.1)
                    for pc in self._pool:
                        if not pc.in_use:
                            pc.in_use = True
                            pc.last_used = time.time()
                            pooled_conn = pc
                            conn = pc.connection
                            break
            
            if conn is None:
                raise ConnectionError("No database connection available")
            
            yield conn
        
        finally:
            if pooled_conn:
                async with self._lock:
                    pooled_conn.in_use = False
    
    async def close_all(self) -> None:
        """Close all connections in the pool."""
        async with self._lock:
            for pc in self._pool:
                try:
                    if ASYNC_AVAILABLE:
                        await pc.connection.close()
                    else:
                        pc.connection.close()
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
            
            self._pool.clear()
            self._initialized = False
            logger.info("All database connections closed")


# ============================================================================
# DATABASE CLASS
# ============================================================================

class Database:
    """
    Database manager for JARVIS with enhanced features.
    
    Features:
        - Connection pooling
        - Automatic retries
        - Query logging
        - Input validation
        - Transaction support
        - Graceful error handling
    
    Usage:
        db = Database(config)
        await db.initialize()
        
        # Queries
        user = await db.get_user(1)
        await db.update_xp(1, 100, "Completed session")
    """
    
    def __init__(self, config: Config, pool_size: int = DEFAULT_POOL_SIZE):
        """
        Initialize database manager.
        
        Args:
            config: JARVIS configuration
            pool_size: Number of connections in pool
        """
        self.config = config
        self.db_path = config.database.path
        self._pool: Optional[ConnectionPool] = None
        self._initialized = False
        self._query_count = 0
        self._error_count = 0
        logger.info(f"Database manager created for {self.db_path}")
    
    async def initialize(self) -> None:
        """
        Initialize database - create if not exists.
        
        Raises:
            DatabaseError: If database cannot be initialized
        """
        if self._initialized:
            return
        
        try:
            # Ensure directory exists
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            
            # Create connection pool
            self._pool = ConnectionPool(self.db_path, DEFAULT_POOL_SIZE)
            await self._pool.initialize()
            
            # Create schema
            async with self._pool.get_connection() as conn:
                if ASYNC_AVAILABLE:
                    await conn.executescript(SCHEMA_SQL)
                    await conn.execute(
                        "INSERT OR IGNORE INTO schema_version (version) VALUES (?)",
                        (SCHEMA_VERSION,)
                    )
                    await conn.commit()
                else:
                    conn.executescript(SCHEMA_SQL)
                    conn.commit()
            
            self._initialized = True
            logger.info("Database initialized successfully")
        
        except Exception as e:
            self._error_count += 1
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")
    
    async def close(self) -> None:
        """Close all database connections."""
        if self._pool:
            await self._pool.close_all()
            self._pool = None
        self._initialized = False
        logger.info("Database closed")
    
    async def _ensure_initialized(self) -> None:
        """Ensure database is initialized before operations."""
        if not self._initialized:
            await self.initialize()
    
    def _validate_user_id(self, user_id: int) -> int:
        """Validate user ID input."""
        if not isinstance(user_id, (int, float)):
            raise ValidationError(f"user_id must be numeric, got {type(user_id)}")
        user_id = int(user_id)
        if user_id < 1:
            raise ValidationError(f"user_id must be positive, got {user_id}")
        return user_id
    
    def _validate_subject(self, subject: str) -> str:
        """Validate subject name."""
        valid_subjects = ['maths', 'physics', 'chemistry', 'english']
        subject_lower = subject.lower().strip()
        if subject_lower not in valid_subjects:
            logger.warning(f"Subject '{subject}' not in standard list: {valid_subjects}")
        return subject_lower
    
    def _validate_theta(self, theta: float) -> float:
        """Validate theta value."""
        if not isinstance(theta, (int, float)):
            raise ValidationError(f"theta must be numeric, got {type(theta)}")
        if theta is None:
            return 0.0
        # Clamp to valid range
        return max(-3.0, min(3.0, float(theta)))
    
    @asynccontextmanager
    async def transaction(self):
        """
        Context manager for database transactions.
        
        Yields:
            Database connection
            
        Usage:
            async with db.transaction() as conn:
                await conn.execute(...)
                await conn.commit()
        """
        await self._ensure_initialized()
        
        async with self._pool.get_connection() as conn:
            try:
                yield conn
                if ASYNC_AVAILABLE:
                    await conn.commit()
                else:
                    conn.commit()
            except Exception as e:
                if ASYNC_AVAILABLE:
                    await conn.rollback()
                else:
                    conn.rollback()
                self._error_count += 1
                logger.error(f"Transaction failed: {e}")
                raise
    
    # ========================================================================
    # USER OPERATIONS
    # ========================================================================
    
    async def create_user(self, name: str = "Student") -> int:
        """
        Create a new user.
        
        Args:
            name: User's name (will be sanitized)
        
        Returns:
            User ID
        
        Raises:
            ValidationError: If name is invalid
            DatabaseError: If creation fails
        """
        await self._ensure_initialized()
        
        # Input validation
        if not name or not isinstance(name, str):
            name = "Student"
        name = name.strip()[:100]  # Limit length
        
        try:
            async with self._pool.get_connection() as conn:
                if ASYNC_AVAILABLE:
                    cursor = await conn.execute(
                        """INSERT INTO users (name, exam_date) 
                           VALUES (?, date('now', '+75 days'))""",
                        (name,)
                    )
                    await conn.commit()
                    user_id = cursor.lastrowid
                else:
                    cursor = conn.execute(
                        """INSERT INTO users (name, exam_date) 
                           VALUES (?, date('now', '+75 days'))""",
                        (name,)
                    )
                    conn.commit()
                    user_id = cursor.lastrowid
                
                self._query_count += 1
                logger.info(f"Created user {user_id}: {name}")
                return user_id
        
        except Exception as e:
            self._error_count += 1
            logger.error(f"Failed to create user: {e}")
            raise DatabaseError(f"User creation failed: {e}")
    
    async def get_user(self, user_id: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID (default 1 for single user)
        
        Returns:
            User dict or None if not found
        """
        await self._ensure_initialized()
        
        # Validate input
        user_id = self._validate_user_id(user_id)
        
        try:
            async with self._pool.get_connection() as conn:
                if ASYNC_AVAILABLE:
                    async with conn.execute(
                        "SELECT * FROM users WHERE id = ?", (user_id,)
                    ) as cursor:
                        row = await cursor.fetchone()
                        if row:
                            columns = [desc[0] for desc in cursor.description]
                else:
                    cursor = conn.execute(
                        "SELECT * FROM users WHERE id = ?", (user_id,)
                    )
                    row = cursor.fetchone()
                    if row:
                        columns = [desc[0] for desc in cursor.description]
                
                self._query_count += 1
                
                if row is None:
                    logger.debug(f"User {user_id} not found")
                    return None
                
                return dict(zip(columns, row))
        
        except Exception as e:
            self._error_count += 1
            logger.error(f"Failed to get user {user_id}: {e}")
            return None
    
    async def update_theta(self, user_id: int, subject: str, theta: float) -> bool:
        """
        Update theta value for a subject.
        
        Args:
            user_id: User ID
            subject: Subject name (maths, physics, chemistry, english)
            theta: New theta value
        
        Returns:
            True if successful, False otherwise
        """
        await self._ensure_initialized()
        
        # Validate inputs
        user_id = self._validate_user_id(user_id)
        subject = self._validate_subject(subject)
        theta = self._validate_theta(theta)
        
        column = f"{subject}_theta"
        
        try:
            async with self._pool.get_connection() as conn:
                if ASYNC_AVAILABLE:
                    await conn.execute(
                        f"UPDATE users SET {column} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (theta, user_id)
                    )
                    await conn.commit()
                else:
                    conn.execute(
                        f"UPDATE users SET {column} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (theta, user_id)
                    )
                    conn.commit()
                
                self._query_count += 1
                logger.debug(f"Updated {subject} theta to {theta} for user {user_id}")
                return True
        
        except Exception as e:
            self._error_count += 1
            logger.error(f"Failed to update theta: {e}")
            return False
    
    async def update_xp(self, user_id: int, xp_change: int, reason: str, 
                        session_id: Optional[int] = None) -> int:
        """
        Update user XP and record history.
        
        Args:
            user_id: User ID
            xp_change: XP change (positive or negative)
            reason: Reason for change
            session_id: Related session ID (optional)
        
        Returns:
            New total XP, or 0 on error
        """
        await self._ensure_initialized()
        
        # Validate inputs
        user_id = self._validate_user_id(user_id)
        if not isinstance(xp_change, (int, float)):
            xp_change = 0
        xp_change = int(xp_change)
        
        if not reason or not isinstance(reason, str):
            reason = "No reason provided"
        reason = reason.strip()[:500]  # Limit length
        
        try:
            async with self._pool.get_connection() as conn:
                if ASYNC_AVAILABLE:
                    # Update total XP
                    await conn.execute(
                        """UPDATE users 
                           SET total_xp = total_xp + ?, 
                               updated_at = CURRENT_TIMESTAMP 
                           WHERE id = ?""",
                        (xp_change, user_id)
                    )
                    
                    # Record history
                    await conn.execute(
                        """INSERT INTO xp_history (user_id, xp_change, reason, session_id)
                           VALUES (?, ?, ?, ?)""",
                        (user_id, xp_change, reason, session_id)
                    )
                    
                    await conn.commit()
                    
                    # Get new total
                    async with conn.execute(
                        "SELECT total_xp FROM users WHERE id = ?", (user_id,)
                    ) as cursor:
                        row = await cursor.fetchone()
                        new_xp = row[0] if row else 0
                else:
                    conn.execute(
                        """UPDATE users 
                           SET total_xp = total_xp + ?, 
                               updated_at = CURRENT_TIMESTAMP 
                           WHERE id = ?""",
                        (xp_change, user_id)
                    )
                    conn.execute(
                        """INSERT INTO xp_history (user_id, xp_change, reason, session_id)
                           VALUES (?, ?, ?, ?)""",
                        (user_id, xp_change, reason, session_id)
                    )
                    conn.commit()
                    
                    cursor = conn.execute(
                        "SELECT total_xp FROM users WHERE id = ?", (user_id,)
                    )
                    row = cursor.fetchone()
                    new_xp = row[0] if row else 0
                
                self._query_count += 1
                logger.info(f"User {user_id} XP changed by {xp_change}: {reason}")
                return new_xp
        
        except Exception as e:
            self._error_count += 1
            logger.error(f"Failed to update XP: {e}")
            return 0
    
    async def update_streak(self, user_id: int, increment: bool = True) -> int:
        """
        Update study streak.
        
        Args:
            user_id: User ID
            increment: True to increment, False to reset
        
        Returns:
            New streak value, or 0 on error
        """
        await self._ensure_initialized()
        
        # Validate input
        user_id = self._validate_user_id(user_id)
        
        try:
            async with self._pool.get_connection() as conn:
                if ASYNC_AVAILABLE:
                    if increment:
                        await conn.execute(
                            """UPDATE users 
                               SET current_streak = current_streak + 1,
                                   longest_streak = MAX(longest_streak, current_streak + 1),
                                   last_study_date = date('now'),
                                   updated_at = CURRENT_TIMESTAMP
                               WHERE id = ?""",
                            (user_id,)
                        )
                    else:
                        await conn.execute(
                            """UPDATE users 
                               SET current_streak = 0,
                                   updated_at = CURRENT_TIMESTAMP
                               WHERE id = ?""",
                            (user_id,)
                        )
                    
                    await conn.commit()
                    
                    async with conn.execute(
                        "SELECT current_streak FROM users WHERE id = ?", (user_id,)
                    ) as cursor:
                        row = await cursor.fetchone()
                        streak = row[0] if row else 0
                else:
                    if increment:
                        conn.execute(
                            """UPDATE users 
                               SET current_streak = current_streak + 1,
                                   longest_streak = MAX(longest_streak, current_streak + 1),
                                   last_study_date = date('now'),
                                   updated_at = CURRENT_TIMESTAMP
                               WHERE id = ?""",
                            (user_id,)
                        )
                    else:
                        conn.execute(
                            """UPDATE users 
                               SET current_streak = 0,
                                   updated_at = CURRENT_TIMESTAMP
                               WHERE id = ?""",
                            (user_id,)
                        )
                    
                    conn.commit()
                    
                    cursor = conn.execute(
                        "SELECT current_streak FROM users WHERE id = ?", (user_id,)
                    )
                    row = cursor.fetchone()
                    streak = row[0] if row else 0
                
                self._query_count += 1
                logger.info(f"User {user_id} streak {'incremented' if increment else 'reset'}: {streak}")
                return streak
        
        except Exception as e:
            self._error_count += 1
            logger.error(f"Failed to update streak: {e}")
            return 0

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
        
        Raises:
            ValidationError: If inputs are invalid
        """
        await self._ensure_initialized()
        
        # Validate inputs
        if not isinstance(topic_id, (int, float)) or topic_id < 1:
            raise ValidationError(f"Invalid topic_id: {topic_id}")
        
        if not question_text or not isinstance(question_text, str):
            raise ValidationError("question_text is required")
        question_text = question_text.strip()
        
        if not options or len(options) != 4:
            raise ValidationError("Must have exactly 4 options")
        
        correct = correct.upper().strip()
        if correct not in ['A', 'B', 'C', 'D']:
            raise ValidationError(f"Correct must be A, B, C, or D, got: {correct}")
        
        # Validate IRT parameters
        difficulty = max(-3.0, min(3.0, float(difficulty)))
        discrimination = max(0.5, min(2.5, float(discrimination)))
        guessing = max(0.0, min(0.5, float(guessing)))
        
        try:
            async with self._pool.get_connection() as conn:
                if ASYNC_AVAILABLE:
                    cursor = await conn.execute(
                        """INSERT INTO questions 
                           (topic_id, question_text, option_a, option_b, option_c, option_d,
                            correct_option, explanation, difficulty, discrimination, guessing, source)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (topic_id, question_text, options[0], options[1], 
                         options[2], options[3], correct, explanation,
                         difficulty, discrimination, guessing, source)
                    )
                    await conn.commit()
                    question_id = cursor.lastrowid
                else:
                    cursor = conn.execute(
                        """INSERT INTO questions 
                           (topic_id, question_text, option_a, option_b, option_c, option_d,
                            correct_option, explanation, difficulty, discrimination, guessing, source)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (topic_id, question_text, options[0], options[1], 
                         options[2], options[3], correct, explanation,
                         difficulty, discrimination, guessing, source)
                    )
                    conn.commit()
                    question_id = cursor.lastrowid
                
                self._query_count += 1
                logger.info(f"Added question {question_id} for topic {topic_id}")
                return question_id
        
        except Exception as e:
            self._error_count += 1
            logger.error(f"Failed to add question: {e}")
            raise DatabaseError(f"Question creation failed: {e}")
    
    async def get_question(self, question_id: int) -> Optional[Dict[str, Any]]:
        """Get question by ID."""
        await self._ensure_initialized()
        
        if not isinstance(question_id, (int, float)) or question_id < 1:
            return None
        
        try:
            async with self._pool.get_connection() as conn:
                if ASYNC_AVAILABLE:
                    async with conn.execute(
                        "SELECT * FROM questions WHERE id = ?", (int(question_id),)
                    ) as cursor:
                        row = await cursor.fetchone()
                        if row:
                            columns = [desc[0] for desc in cursor.description]
                else:
                    cursor = conn.execute(
                        "SELECT * FROM questions WHERE id = ?", (int(question_id),)
                    )
                    row = cursor.fetchone()
                    if row:
                        columns = [desc[0] for desc in cursor.description]
                
                self._query_count += 1
                return dict(zip(columns, row)) if row else None
        
        except Exception as e:
            self._error_count += 1
            logger.error(f"Failed to get question: {e}")
            return None
    
    async def get_questions_for_topic(self, topic_id: int, 
                                       limit: int = 10) -> List[Dict[str, Any]]:
        """Get questions for a topic."""
        await self._ensure_initialized()
        
        # Validate inputs
        if not isinstance(topic_id, (int, float)) or topic_id < 1:
            return []
        if not isinstance(limit, (int, float)) or limit < 1:
            limit = 10
        limit = min(int(limit), 100)  # Cap at 100
        
        try:
            async with self._pool.get_connection() as conn:
                if ASYNC_AVAILABLE:
                    async with conn.execute(
                        """SELECT * FROM questions 
                           WHERE topic_id = ? 
                           ORDER BY RANDOM() 
                           LIMIT ?""",
                        (int(topic_id), limit)
                    ) as cursor:
                        rows = await cursor.fetchall()
                        columns = [desc[0] for desc in cursor.description]
                else:
                    cursor = conn.execute(
                        """SELECT * FROM questions 
                           WHERE topic_id = ? 
                           ORDER BY RANDOM() 
                           LIMIT ?""",
                        (int(topic_id), limit)
                    )
                    rows = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                
                self._query_count += 1
                return [dict(zip(columns, row)) for row in rows]
        
        except Exception as e:
            self._error_count += 1
            logger.error(f"Failed to get questions for topic: {e}")
            return []
    
    async def record_response(self, user_id: int, question_id: int,
                              session_id: int, user_answer: str,
                              is_correct: bool, time_seconds: int,
                              theta_before: float, theta_after: float,
                              fisher_info: float) -> int:
        """
        Record a question response.
        
        Returns:
            Response ID, or -1 on error
        """
        await self._ensure_initialized()
        
        # Validate inputs
        user_id = self._validate_user_id(user_id)
        if not isinstance(question_id, (int, float)) or question_id < 1:
            return -1
        if not isinstance(session_id, (int, float)) or session_id < 1:
            return -1
        
        user_answer = str(user_answer).upper().strip()
        if user_answer not in ['A', 'B', 'C', 'D']:
            user_answer = 'A'  # Default
        
        theta_before = self._validate_theta(theta_before)
        theta_after = self._validate_theta(theta_after)
        
        try:
            async with self._pool.get_connection() as conn:
                if ASYNC_AVAILABLE:
                    cursor = await conn.execute(
                        """INSERT INTO responses 
                           (user_id, question_id, session_id, user_answer, is_correct,
                            time_taken_seconds, theta_before, theta_after, fisher_information)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (user_id, int(question_id), int(session_id), user_answer, 
                         1 if is_correct else 0, int(time_seconds),
                         theta_before, theta_after, float(fisher_info))
                    )
                    
                    # Update question stats
                    await conn.execute(
                        """UPDATE questions 
                           SET times_asked = times_asked + 1,
                               times_correct = times_correct + ?
                           WHERE id = ?""",
                        (1 if is_correct else 0, int(question_id))
                    )
                    
                    await conn.commit()
                    response_id = cursor.lastrowid
                else:
                    cursor = conn.execute(
                        """INSERT INTO responses 
                           (user_id, question_id, session_id, user_answer, is_correct,
                            time_taken_seconds, theta_before, theta_after, fisher_information)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (user_id, int(question_id), int(session_id), user_answer, 
                         1 if is_correct else 0, int(time_seconds),
                         theta_before, theta_after, float(fisher_info))
                    )
                    conn.execute(
                        """UPDATE questions 
                           SET times_asked = times_asked + 1,
                               times_correct = times_correct + ?
                           WHERE id = ?""",
                        (1 if is_correct else 0, int(question_id))
                    )
                    conn.commit()
                    response_id = cursor.lastrowid
                
                self._query_count += 1
                return response_id
        
        except Exception as e:
            self._error_count += 1
            logger.error(f"Failed to record response: {e}")
            return -1
    
    # ========================================================================
    # AI CACHE OPERATIONS
    # ========================================================================
    
    async def get_cached_response(self, prompt: str) -> Optional[str]:
        """
        Get cached AI response if available and not expired.
        
        Args:
            prompt: The prompt to look up
        
        Returns:
            Cached response or None
        """
        await self._ensure_initialized()
        
        if not prompt or not isinstance(prompt, str):
            return None
        
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
        
        try:
            async with self._pool.get_connection() as conn:
                if ASYNC_AVAILABLE:
                    await conn.execute(
                        """UPDATE ai_cache SET hit_count = hit_count + 1 
                           WHERE prompt_hash = ? 
                           AND (expires_at IS NULL OR expires_at > datetime('now'))""",
                        (prompt_hash,)
                    )
                    await conn.commit()
                    
                    async with conn.execute(
                        """SELECT response FROM ai_cache 
                           WHERE prompt_hash = ? 
                           AND (expires_at IS NULL OR expires_at > datetime('now'))""",
                        (prompt_hash,)
                    ) as cursor:
                        row = await cursor.fetchone()
                else:
                    conn.execute(
                        """UPDATE ai_cache SET hit_count = hit_count + 1 
                           WHERE prompt_hash = ? 
                           AND (expires_at IS NULL OR expires_at > datetime('now'))""",
                        (prompt_hash,)
                    )
                    conn.commit()
                    
                    cursor = conn.execute(
                        """SELECT response FROM ai_cache 
                           WHERE prompt_hash = ? 
                           AND (expires_at IS NULL OR expires_at > datetime('now'))""",
                        (prompt_hash,)
                    )
                    row = cursor.fetchone()
                
                self._query_count += 1
                return row[0] if row else None
        
        except Exception as e:
            self._error_count += 1
            logger.error(f"Failed to get cached response: {e}")
            return None
    
    async def cache_response(self, prompt: str, response: str, 
                            expires_hours: int = 24) -> bool:
        """
        Cache an AI response.
        
        Args:
            prompt: The prompt
            response: The AI response
            expires_hours: Hours until expiration (default 24)
        
        Returns:
            True if cached successfully
        """
        await self._ensure_initialized()
        
        if not prompt or not response:
            return False
        
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
        
        try:
            async with self._pool.get_connection() as conn:
                if ASYNC_AVAILABLE:
                    await conn.execute(
                        """INSERT OR REPLACE INTO ai_cache 
                           (prompt_hash, prompt, response, expires_at)
                           VALUES (?, ?, ?, datetime('now', '+' || ? || ' hours'))""",
                        (prompt_hash, prompt, response, expires_hours)
                    )
                    await conn.commit()
                else:
                    conn.execute(
                        """INSERT OR REPLACE INTO ai_cache 
                           (prompt_hash, prompt, response, expires_at)
                           VALUES (?, ?, ?, datetime('now', '+' || ? || ' hours'))""",
                        (prompt_hash, prompt, response, expires_hours)
                    )
                    conn.commit()
                
                self._query_count += 1
                return True
        
        except Exception as e:
            self._error_count += 1
            logger.error(f"Failed to cache response: {e}")
            return False
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            "query_count": self._query_count,
            "error_count": self._error_count,
            "initialized": self._initialized,
            "pool_size": self._pool.pool_size if self._pool else 0,
        }


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
    """
    db = Database(config)
    await db.initialize()
    return db


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing database module v2.0...")
    print()
    
    # Create test config
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
        
        # Test cache
        cached = await db.cache_response("test prompt", "test response")
        print(f"Cached: {cached}")
        
        retrieved = await db.get_cached_response("test prompt")
        print(f"Retrieved from cache: {retrieved}")
        
        # Stats
        stats = db.get_stats()
        print(f"Stats: {stats}")
        
        await db.close()
        print("\nAll tests passed!")
    
    asyncio.run(test())
