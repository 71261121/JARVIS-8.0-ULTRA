"""
JARVIS Logging Module
=====================

Purpose: Centralized logging for JARVIS.

Reason for custom logging:
    - Structured logs for debugging
    - File rotation to prevent disk fill
    - Different levels for different environments

Log Format:
    [TIMESTAMP] [LEVEL] [MODULE] Message

Log Files:
    - jarvis.log: Main log
    - error.log: Errors only
    - study.log: Study session logs
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path
from typing import Optional


# ============================================================================
# LOG FORMAT
# ============================================================================

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ============================================================================
# LOGGER CLASS
# ============================================================================

class JarvisLogger:
    """
    Centralized logger for JARVIS.
    
    Usage:
        from jarvis.core.logging_setup import get_logger
        logger = get_logger(__name__)
        logger.info("Starting session")
    
    Reason for design:
        - Single point of configuration
        - Consistent format across modules
        - File rotation built-in
    """
    
    _instance: Optional['JarvisLogger'] = None
    _initialized: bool = False
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern - one logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, log_path: str = "data/logs/", 
                 level: str = "INFO",
                 max_size_mb: int = 10,
                 backup_count: int = 5):
        """
        Initialize logger.
        
        Args:
            log_path: Directory for log files
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_size_mb: Max size per log file
            backup_count: Number of backup files to keep
        """
        if self._initialized:
            return
        
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.max_bytes = max_size_mb * 1024 * 1024
        self.backup_count = backup_count
        
        # Create root logger
        self.root_logger = logging.getLogger("jarvis")
        self.root_logger.setLevel(self.level)
        
        # Clear existing handlers
        self.root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        self.root_logger.addHandler(console_handler)
        
        # File handlers
        self._setup_file_handlers()
        
        self._initialized = True
    
    def _setup_file_handlers(self):
        """Setup rotating file handlers."""
        # Main log file
        main_log = self.log_path / "jarvis.log"
        main_handler = RotatingFileHandler(
            main_log,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        main_handler.setLevel(self.level)
        main_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        self.root_logger.addHandler(main_handler)
        
        # Error log file (errors only)
        error_log = self.log_path / "error.log"
        error_handler = RotatingFileHandler(
            error_log,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        self.root_logger.addHandler(error_handler)
        
        # Study log file (for study sessions)
        study_log = self.log_path / "study.log"
        study_handler = RotatingFileHandler(
            study_log,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        study_handler.setLevel(logging.INFO)
        study_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        
        # Only log study-related messages
        study_filter = StudyLogFilter()
        study_handler.addFilter(study_filter)
        self.root_logger.addHandler(study_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger for a module.
        
        Args:
            name: Module name (usually __name__)
        
        Returns:
            Logger instance
        """
        if not self._initialized:
            self.__init__()
        
        # Return child logger
        if not name.startswith("jarvis."):
            name = f"jarvis.{name}"
        
        return logging.getLogger(name)


class StudyLogFilter(logging.Filter):
    """Filter for study-related log messages."""
    
    STUDY_KEYWORDS = [
        "session", "question", "answer", "theta", "xp", "streak",
        "topic", "subject", "mock", "revision", "correct", "wrong"
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Return True if message is study-related."""
        message = record.getMessage().lower()
        return any(keyword in message for keyword in self.STUDY_KEYWORDS)


# ============================================================================
# GLOBAL FUNCTIONS
# ============================================================================

_jarvis_logger: Optional[JarvisLogger] = None


def setup_logging(log_path: str = "data/logs/",
                  level: str = "INFO",
                  max_size_mb: int = 10,
                  backup_count: int = 5) -> JarvisLogger:
    """
    Setup logging for JARVIS.
    
    Args:
        log_path: Directory for log files
        level: Log level
        max_size_mb: Max size per log file
        backup_count: Number of backup files
    
    Returns:
        JarvisLogger instance
    
    Reason:
        Must be called once at application start.
    """
    global _jarvis_logger
    _jarvis_logger = JarvisLogger(log_path, level, max_size_mb, backup_count)
    return _jarvis_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a module.
    
    Args:
        name: Module name (usually __name__)
    
    Returns:
        Logger instance
    
    Usage:
        logger = get_logger(__name__)
        logger.info("Message")
    """
    global _jarvis_logger
    
    if _jarvis_logger is None:
        # Auto-initialize with defaults
        _jarvis_logger = JarvisLogger()
    
    return _jarvis_logger.get_logger(name)


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing logging module...")
    print()
    
    # Setup logging
    setup_logging(level="DEBUG")
    
    # Get logger
    logger = get_logger("test")
    
    # Test all levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test study log
    study_logger = get_logger("study")
    study_logger.info("Session started - question 1")
    study_logger.info("Answer correct - XP +10")
    study_logger.info("This won't appear in study.log")
    
    print()
    print("Check data/logs/ for log files")
